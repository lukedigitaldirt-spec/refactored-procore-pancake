#!/usr/bin/env python3
"""5W2H completeness validator for process/knowledge capture (stdlib-only).

The 5W2H frame (Who, What, When, Where, Why, How, How much) is the Kipling
"six honest serving-men" plus the two quantifying questions Toyota added. A
piece of know-how that cannot answer all seven is not yet documentable: the
gaps are exactly the questions to put back to the author.

This tool scores completeness across the seven elements in either of two modes
and lists a forcing prompt for every gap it finds.

Mode A - structured JSON (default): an object keyed by element. An element is
present when its value is a non-empty string (after stripping):
    {
      "who": "AP clerk",
      "what": "process the vendor invoice",
      "when": "on receipt of a matched invoice",
      "where": "NetSuite AP module",
      "why": "pay vendors on terms and avoid late fees",
      "how": "three-way match, then post, then route for approval",
      "how_much": "invoices under the $5k auto-approve threshold"
    }

Mode B - free text (--text FILE): scan a markdown/plain-text document for
headers or labels whose wording matches each element's keyword set
(case-insensitive). Any element whose keywords never appear in a header or
label line is reported missing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

ELEMENTS = ["who", "what", "when", "where", "why", "how", "how_much"]

# Keyword sets used in --text mode to recognise an element from a header/label.
KEYWORDS = {
    "who": ["who", "owner", "responsible", "accountable", "role", "actor",
            "assignee", "raci"],
    "what": ["what", "task", "activity", "action", "deliverable", "output",
             "objective"],
    "when": ["when", "timing", "schedule", "frequency", "trigger", "deadline",
             "timeline", "cadence"],
    "where": ["where", "location", "system", "tool", "platform",
              "environment", "repository", "channel"],
    "why": ["why", "purpose", "rationale", "reason", "goal", "justification"],
    "how": ["how", "method", "procedure", "steps", "approach", "technique",
            "mechanism"],
    "how_much": ["how much", "how many", "cost", "budget", "quantity",
                 "resources", "volume", "threshold", "effort"],
}

PROMPTS = {
    "who": "Specify WHO owns this: which role/person is accountable?",
    "what": "Specify WHAT is done: the task or deliverable (verb + object).",
    "when": "Specify WHEN it happens: trigger, timing, frequency, or deadline.",
    "where": "Specify WHERE it happens: which system, tool, or location.",
    "why": "Specify WHY it matters: the purpose or outcome it serves.",
    "how": "Specify HOW it is done: the method or sequence of steps.",
    "how_much": "Specify HOW MUCH: cost, quantity, threshold, or resources.",
}


def _keyword_hit(label: str, element: str) -> bool:
    """True if any keyword for ``element`` appears as a word in ``label``."""
    for kw in KEYWORDS[element]:
        if element == "how" and kw == "how":
            if re.search(r"\bhow\b(?!\s+(?:much|many))", label):
                return True
            continue
        if re.search(r"\b" + re.escape(kw) + r"\b", label):
            return True
    return False


def _label_portions(text: str):
    """Yield the label portion of each header or label line in ``text``."""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            yield line.lstrip("#").strip().lower()
            continue
        if ":" in line:
            yield line.split(":", 1)[0].strip().lower()
        bold = re.match(r"\*\*(.+?)\*\*", line)
        if bold:
            yield bold.group(1).strip().lower()


def _present_from_text(text: str) -> set:
    present = set()
    for label in _label_portions(text):
        for element in ELEMENTS:
            if element not in present and _keyword_hit(label, element):
                present.add(element)
    return present


def _assemble(present: set) -> dict:
    missing = [
        {"element": e, "prompt": PROMPTS[e]}
        for e in ELEMENTS if e not in present
    ]
    score = len(present) / len(ELEMENTS)
    return {
        "valid": len(present) == len(ELEMENTS),
        "completeness_score": round(score, 4),
        "completeness_pct": round(score * 100, 2),
        "elements": {e: (e in present) for e in ELEMENTS},
        "present": [e for e in ELEMENTS if e in present],
        "missing": missing,
    }


def validate(data) -> dict:
    """Score a structured 5W2H object; return completeness + gap prompts."""
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object keyed by 5W2H element")
    present = set()
    for element in ELEMENTS:
        value = data.get(element)
        if value is not None and str(value).strip():
            present.add(element)
    return _assemble(present)


def validate_text(text: str) -> dict:
    """Score a free-text document for 5W2H coverage via header/label scan."""
    if not text or not text.strip():
        raise ValueError("text input is empty")
    return _assemble(_present_from_text(text))


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
    lines = [
        "5W2H Completeness Check",
        "=======================",
        f"Completeness: {result['completeness_pct']}% "
        f"({len(result['present'])}/{len(ELEMENTS)} elements)",
        f"Result: {'COMPLETE' if result['valid'] else 'INCOMPLETE'}",
        "",
        "Elements:",
    ]
    for element in ELEMENTS:
        mark = "present" if result["elements"][element] else "MISSING"
        lines.append(f"  {element:<9} {mark}")
    if result["missing"]:
        lines.append("")
        lines.append("Fill these gaps:")
        lines.extend(f"  - {m['prompt']}" for m in result["missing"])
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("source", help="path to 5W2H JSON (or text with "
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
