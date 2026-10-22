#!/usr/bin/env python3
"""Linter for Standard Operating Procedures (SOPs) (stdlib-only).

Checks an SOP for the structure and writing discipline that ISO/TR 10013 and
the EPA/FDA SOP guidance expect: a stated purpose and scope, an actual
procedure, version control, and steps written as imperative commands. It
reports errors (the SOP is not usable) separately from warnings (the SOP works
but has quality smells), mirroring the process-mapper validators.

Mode A - structured JSON (default):
    {
      "title": "Process a vendor invoice",
      "purpose": "Ensure invoices are paid accurately and on terms",
      "scope": "All non-PO invoices under $5k in NetSuite",
      "roles": ["AP clerk", "AP manager"],
      "steps": [
        "Open the invoice in NetSuite.",
        "Match it against the receiving record."
      ],
      "revision_history": [{"version": "1.0", "date": "2026-01-01"}]
    }

Mode B - free text (--text FILE): parse a markdown SOP whose headers name the
sections (Title as the H1; Purpose; Scope; Roles; Procedure or Steps;
Revision History) into the same shape, then apply the identical checks.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

NON_IMPERATIVE = {
    "the", "a", "an", "this", "that", "these", "those", "it", "its",
    "they", "he", "she", "we", "i", "you", "user", "users", "system",
}
MAX_STEP_WORDS = 30
CANONICAL = ["title", "purpose", "scope", "roles", "steps",
             "revision_history"]


def lint(data) -> dict:
    """Lint a structured SOP object; return {valid, errors, warnings, stats}."""
    if not isinstance(data, dict):
        raise ValueError("SOP input must be a JSON object")

    errors = []
    warnings = []

    title = data.get("title")
    purpose = data.get("purpose")
    scope = data.get("scope")
    roles = data.get("roles") or []
    steps = data.get("steps")
    revision = data.get("revision_history") or []

    if steps is None:
        steps = []
    if not isinstance(steps, list):
        raise ValueError("'steps' must be a list")
    if not isinstance(roles, list):
        raise ValueError("'roles' must be a list")

    if not (purpose and str(purpose).strip()):
        errors.append("missing required section: purpose")
    if not (scope and str(scope).strip()):
        errors.append("missing required section: scope")
    if not steps:
        errors.append("missing required section: steps (procedure)")

    if not (title and str(title).strip()):
        warnings.append("SOP has no title")
    if not revision:
        warnings.append("no revision history; an SOP must be version-"
                        "controlled")

    for i, step in enumerate(steps, 1):
        words = str(step).strip().split()
        if not words:
            warnings.append(f"step {i} is empty")
            continue
        first = words[0].lower().strip(".,:;")
        if first in NON_IMPERATIVE:
            warnings.append(f"step {i} is not imperative: starts with "
                            f"'{words[0]}' (lead with a verb)")
        if len(words) > MAX_STEP_WORDS:
            warnings.append(f"step {i} is {len(words)} words (>{MAX_STEP_WORDS}"
                            "); split it into smaller steps")

    present = {
        "title": bool(title and str(title).strip()),
        "purpose": bool(purpose and str(purpose).strip()),
        "scope": bool(scope and str(scope).strip()),
        "roles": bool(roles),
        "steps": bool(steps),
        "revision_history": bool(revision),
    }
    section_count = sum(1 for k in CANONICAL if present[k])

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "step_count": len(steps),
            "section_count": section_count,
        },
    }


def _split_sections(text: str):
    """Return (title, {header_lower: [body_lines]}) from markdown ``text``."""
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
    if "purpose" in header:
        return "purpose"
    if "scope" in header:
        return "scope"
    if "role" in header:
        return "roles"
    if "procedure" in header or "step" in header or "instruction" in header:
        return "steps"
    if "revision" in header or "change history" in header or \
            "version history" in header:
        return "revision_history"
    return None


def sop_from_text(text: str) -> dict:
    """Parse a markdown SOP into the structured shape ``lint`` expects."""
    if not text or not text.strip():
        raise ValueError("text input is empty")
    title, sections = _split_sections(text)
    data = {"title": title, "roles": [], "steps": [], "revision_history": []}
    for header, body in sections.items():
        canon = _classify(header)
        if canon == "roles":
            data["roles"] = _list_items(body) or (
                [_joined_prose(body)] if _joined_prose(body) else [])
        elif canon == "steps":
            data["steps"] = _list_items(body)
        elif canon == "revision_history":
            items = _list_items(body)
            data["revision_history"] = items if items else (
                [_joined_prose(body)] if _joined_prose(body) else [])
        elif canon in ("purpose", "scope"):
            data[canon] = _joined_prose(body)
    return data


def validate_text(text: str) -> dict:
    """Lint an SOP supplied as markdown/plain text."""
    return lint(sop_from_text(text))


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
        "SOP Lint",
        "========",
        f"Sections present: {st['section_count']}/6  "
        f"Steps: {st['step_count']}",
        f"Result: {'PASS' if result['valid'] else 'FAIL'}",
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
    parser.add_argument("source", help="path to SOP JSON (or markdown with "
                        "--text); '-' reads stdin")
    parser.add_argument("--text", action="store_true",
                        help="treat source as markdown/plain text, not JSON")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        if args.text:
            result = validate_text(_read_text(args.source))
        else:
            result = lint(_load(args.source))
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
