#!/usr/bin/env python3
"""Kotter 8-step change-progress tracker (stdlib-only).

John Kotter's *Leading Change* lays out eight steps an organization works
through to transform. The steps are ordered on purpose: running a late step
before the earlier ones are in place is the classic failure mode (e.g.
declaring victory before short-term wins, or acting before the vision is
communicated). This tool tracks status per step, computes a weighted percent
complete, finds the current step, and warns when later steps have jumped ahead
of earlier ones that have not started.

Weighting: a complete step counts 1.0, an in-progress step 0.5, not-started
0.0; percent_complete is that sum over the 8 steps. The current step is the
lowest-numbered step that is not complete. next_action is the name of the
current step.

Importable as functions; runnable as a CLI.

Input JSON schema (object):
    {
      "steps": [
        {"step": 1, "status": "complete"},
        {"step": 2, "status": "in_progress"}
      ]
    }
Each entry has an integer ``step`` in 1-8 and a ``status`` in
{not_started, in_progress, complete}. Steps omitted default to not_started.
Duplicate step numbers are rejected.
"""
from __future__ import annotations

import argparse
import json
import sys

STEP_NAMES = {
    1: "Create a sense of urgency",
    2: "Build a guiding coalition",
    3: "Form a strategic vision",
    4: "Enlist volunteers / communicate the vision",
    5: "Enable action by removing barriers",
    6: "Generate short-term wins",
    7: "Sustain acceleration",
    8: "Institute change",
}

STATUSES = {"not_started", "in_progress", "complete"}
WEIGHTS = {"not_started": 0.0, "in_progress": 0.5, "complete": 1.0}


def track(steps) -> dict:
    """Return Kotter progress for a list of step-status dicts.

    Missing steps default to not_started. Status must be one of
    not_started/in_progress/complete; step numbers must be 1-8 with no
    duplicates.
    """
    if not isinstance(steps, list):
        raise ValueError("steps must be a list")

    status_by_step = {}
    for entry in steps:
        if not isinstance(entry, dict):
            raise ValueError("each step entry must be an object")
        try:
            num = int(entry["step"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("each step needs an integer 'step'") from exc
        if not 1 <= num <= 8:
            raise ValueError(f"step number must be in 1-8, got {num}")
        if num in status_by_step:
            raise ValueError(f"duplicate step number: {num}")
        status = entry.get("status", "not_started")
        if status not in STATUSES:
            raise ValueError(
                f"step {num} has invalid status '{status}'; expected one of "
                f"{sorted(STATUSES)}")
        status_by_step[num] = status

    per_step = []
    for num in range(1, 9):
        status = status_by_step.get(num, "not_started")
        per_step.append({
            "step": num,
            "name": STEP_NAMES[num],
            "status": status,
        })

    weighted = sum(WEIGHTS[s["status"]] for s in per_step)
    percent_complete = round(weighted / 8 * 100, 2)

    current = next((s for s in per_step if s["status"] != "complete"), None)
    if current is None:
        current_step = None
        next_action = None
    else:
        current_step = current["step"]
        next_action = current["name"]

    warnings = []
    for s in per_step:
        if s["status"] in ("complete", "in_progress"):
            earlier = [e for e in per_step
                       if e["step"] < s["step"]
                       and e["status"] == "not_started"]
            for e in earlier:
                warnings.append(
                    f"Step {s['step']} ({s['name']}) is {s['status']} while "
                    f"step {e['step']} ({e['name']}) has not started — "
                    "out of sequence.")

    return {
        "percent_complete": percent_complete,
        "current_step": current_step,
        "next_action": next_action,
        "steps": per_step,
        "warnings": warnings,
    }


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "Kotter 8-Step Progress",
        "======================",
        f"Percent complete: {result['percent_complete']}%",
    ]
    if result["current_step"] is None:
        lines.append("Current step:     all 8 steps complete")
    else:
        lines.append(f"Current step:     {result['current_step']} "
                     f"({result['next_action']})")
    lines.append("")
    for s in result["steps"]:
        lines.append(f"{s['step']}. {s['name']:<44}{s['status']}")
    if result["warnings"]:
        lines.append("")
        lines.append("WARNINGS (out-of-sequence execution):")
        for w in result["warnings"]:
            lines.append(f"  - {w}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("progress", help="path to progress JSON file, or '-' "
                        "for stdin")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.progress)
        if isinstance(data, dict):
            steps = data.get("steps", [])
        else:
            steps = data
        result = track(steps)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
