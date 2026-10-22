#!/usr/bin/env python3
"""Validator for operational runbooks (stdlib-only).

A runbook is the SOP's operational cousin: a concrete, executable response to a
known condition. Google SRE, PagerDuty, and Atlassian incident practice all
converge on the same skeleton - a clear trigger, the prerequisites to act, the
ordered steps, how to verify the fix, how to roll back, and who to escalate to.
This tool checks a runbook against those seven canonical parts, separating
errors (the runbook is unsafe to run) from warnings (quality smells), like the
process-mapper validators.

Mode A - structured JSON (default):
    {
      "title": "API latency incident response",
      "trigger": "p99 latency alarm fires for 5 minutes",
      "prerequisites": ["prod kubectl access", "PagerDuty on-call"],
      "steps": ["Check the dashboard.", "Scale the deployment."],
      "verification": "p99 latency back under 300ms for 10 minutes",
      "rollback": "Revert the scale change; page the service owner",
      "escalation": ["platform on-call L2", "service owner"]
    }

Mode B - free text (--text FILE): parse a markdown runbook whose headers name
the parts (Title as the H1; Trigger/Alert; Prerequisites; Steps/Procedure;
Verification/Validation; Rollback/Recovery; Escalation/Contacts) into the same
shape, then apply the identical checks.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

CANONICAL = ["title", "trigger", "prerequisites", "steps", "verification",
             "rollback", "escalation"]
MIN_STEPS = 2


def validate(data) -> dict:
    """Validate a runbook object; return {valid, errors, warnings, ...}."""
    if not isinstance(data, dict):
        raise ValueError("runbook input must be a JSON object")

    errors = []
    warnings = []

    title = data.get("title")
    trigger = data.get("trigger")
    prerequisites = data.get("prerequisites") or []
    steps = data.get("steps")
    verification = data.get("verification")
    rollback = data.get("rollback")
    escalation = data.get("escalation") or []

    if steps is None:
        steps = []
    for field, value in (("steps", steps), ("prerequisites", prerequisites),
                         ("escalation", escalation)):
        if not isinstance(value, list):
            raise ValueError(f"'{field}' must be a list")

    if not (trigger and str(trigger).strip()):
        errors.append("missing required part: trigger")
    if not steps:
        errors.append("missing required part: steps")
    if not (verification and str(verification).strip()):
        errors.append("missing required part: verification")
    if not escalation:
        errors.append("missing required part: escalation")

    if not prerequisites:
        warnings.append("no prerequisites listed; state access/tools needed")
    if not (rollback and str(rollback).strip()):
        warnings.append("no rollback defined; state how to undo the action")
    if 0 < len(steps) < MIN_STEPS:
        warnings.append(f"only {len(steps)} step; a runbook usually needs "
                        f">={MIN_STEPS} ordered steps")

    present = {
        "title": bool(title and str(title).strip()),
        "trigger": bool(trigger and str(trigger).strip()),
        "prerequisites": bool(prerequisites),
        "steps": bool(steps),
        "verification": bool(verification and str(verification).strip()),
        "rollback": bool(rollback and str(rollback).strip()),
        "escalation": bool(escalation),
    }
    present_count = sum(1 for k in CANONICAL if present[k])
    score = present_count / len(CANONICAL)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "completeness_score": round(score, 4),
        "completeness_pct": round(score * 100, 2),
        "parts": present,
        "stats": {
            "step_count": len(steps),
            "part_count": present_count,
        },
    }


def _split_sections(text: str):
    title = ""
    sections = {}
    current = None
    for raw in text.splitlines():
        header = re.match(r"^(#{1,6})\s+(.*)$", raw.strip())
        if header:
            level, name = len(header.group(1)), header.group(2).strip()
            if level == 1 and not title:
                title = name
            current = name.lower()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(raw)
    return title, sections


def _list_items(body_lines):
    items = []
    for raw in body_lines:
        line = raw.strip()
        m = re.match(r"^(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if m and m.group(1).strip():
            items.append(m.group(1).strip())
    return items


def _joined_prose(body_lines) -> str:
    kept = []
    for raw in body_lines:
        line = raw.strip()
        if not line or line.startswith(("-", "*", "+", "#")):
            continue
        kept.append(line)
    return " ".join(kept).strip()


def _classify(header: str):
    if "trigger" in header or "alert" in header or "symptom" in header:
        return "trigger"
    if "prerequisite" in header or "precondition" in header or \
            "requirement" in header:
        return "prerequisites"
    if "verification" in header or "validation" in header or \
            "verify" in header or "confirm" in header:
        return "verification"
    if "rollback" in header or "recovery" in header or "revert" in header or \
            "undo" in header:
        return "rollback"
    if "escalation" in header or "contact" in header or "on-call" in header \
            or "oncall" in header:
        return "escalation"
    if "procedure" in header or "step" in header or "resolution" in header \
            or "remediation" in header:
        return "steps"
    return None


def runbook_from_text(text: str) -> dict:
    """Parse a markdown runbook into the structured shape ``validate`` wants."""
    if not text or not text.strip():
        raise ValueError("text input is empty")
    title, sections = _split_sections(text)
    data = {"title": title, "prerequisites": [], "steps": [],
            "escalation": []}
    for header, body in sections.items():
        canon = _classify(header)
        if canon in ("prerequisites", "steps", "escalation"):
            items = _list_items(body)
            if not items and _joined_prose(body):
                items = [_joined_prose(body)]
            data[canon] = items
        elif canon in ("trigger", "verification", "rollback"):
            data[canon] = _joined_prose(body)
    return data


def validate_text(text: str) -> dict:
    """Validate a runbook supplied as markdown/plain text."""
    return validate(runbook_from_text(text))


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _format_human(result: dict) -> str:
    st = result["stats"]
    lines = [
        "Runbook Validation",
        "==================",
        f"Completeness: {result['completeness_pct']}% "
        f"({st['part_count']}/7 parts)  Steps: {st['step_count']}",
        f"Result: {'VALID' if result['valid'] else 'INVALID'}",
    ]
    if result["errors"]:
        lines.append("")
        lines.append("Errors:")
        lines.extend(f"  - {e}" for e in result["errors"])
    if result["warnings"]:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"  - {w}" for w in result["warnings"])
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("source", help="path to runbook JSON (or markdown "
                        "with --text); '-' reads stdin")
    parser.add_argument("--text", action="store_true",
                        help="treat source as markdown/plain text, not JSON")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        if args.text:
            result = validate_text(_read_text(args.source))
        else:
            result = validate(_load(args.source))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human(result))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
