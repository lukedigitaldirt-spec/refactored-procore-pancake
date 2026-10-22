#!/usr/bin/env python3
"""Stakeholder power/interest matrix (stdlib-only).

Mendelow's power/interest grid places each stakeholder on two axes — how much
power they hold over the change, and how much interest they have in it — and
sorts them into four quadrants, each with a distinct engagement strategy:

- High power, high interest  -> Manage Closely
- High power, low interest   -> Keep Satisfied
- Low power,  high interest  -> Keep Informed
- Low power,  low interest   -> Monitor

Mis-targeting is the common waste: broadcasting to high-power/high-interest
players who need a 1:1, or over-managing a low/low stakeholder who needs a FAQ.
This tool classifies each stakeholder, recommends a cadence and channel for the
quadrant, and counts how many stakeholders fall in each.

Importable as functions; runnable as a CLI.

Input JSON schema (object):
    {
      "stakeholders": [
        {"name": "CFO", "power": 5, "interest": 2},
        {"name": "Support lead", "power": 2, "interest": 5}
      ]
    }
``power`` and ``interest`` are each an integer or float in 1-5. A value at or
above the high threshold (default 3) counts as high.
"""
from __future__ import annotations

import argparse
import json
import sys

QUADRANTS = {
    (True, True): {
        "quadrant": "Manage Closely",
        "recommendation": "Weekly 1:1s and a seat on the steering group; "
                          "co-create the plan and surface concerns early.",
    },
    (True, False): {
        "quadrant": "Keep Satisfied",
        "recommendation": "Biweekly executive briefing; keep it concise, "
                          "flag risks and decisions, do not overwhelm.",
    },
    (False, True): {
        "quadrant": "Keep Informed",
        "recommendation": "Regular newsletter and demos; give detail and a "
                          "channel to ask questions and give feedback.",
    },
    (False, False): {
        "quadrant": "Monitor",
        "recommendation": "Broadcast updates and a self-serve FAQ; low effort, "
                          "watch for rising power or interest.",
    },
}


def classify(stakeholders, threshold: float = 3.0) -> dict:
    """Return quadrant + recommendation per stakeholder and quadrant counts.

    Each stakeholder needs a ``name`` and numeric ``power`` and ``interest``
    in 1-5. ``threshold`` (default 3) is the cut between low and high.
    """
    if not isinstance(stakeholders, list) or not stakeholders:
        raise ValueError("stakeholders must be a non-empty list")

    rows = []
    counts = {q["quadrant"]: 0 for q in QUADRANTS.values()}
    for i, sh in enumerate(stakeholders):
        if not isinstance(sh, dict):
            raise ValueError("each stakeholder must be an object")
        name = sh.get("name", f"stakeholder_{i + 1}")
        try:
            power = float(sh["power"])
            interest = float(sh["interest"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"stakeholder '{name}' needs numeric 'power' and "
                "'interest'") from exc
        for axis, val in (("power", power), ("interest", interest)):
            if not 1 <= val <= 5:
                raise ValueError(
                    f"stakeholder '{name}' {axis} must be in 1-5, got {val}")

        high_power = power >= threshold
        high_interest = interest >= threshold
        quad = QUADRANTS[(high_power, high_interest)]
        counts[quad["quadrant"]] += 1
        rows.append({
            "name": name,
            "power": round(power, 4),
            "interest": round(interest, 4),
            "quadrant": quad["quadrant"],
            "recommendation": quad["recommendation"],
        })

    return {
        "threshold": round(float(threshold), 4),
        "stakeholder_count": len(rows),
        "counts": counts,
        "stakeholders": rows,
    }


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "Stakeholder Power/Interest Matrix",
        "=================================",
        f"Stakeholders: {result['stakeholder_count']}  "
        f"(high threshold >= {result['threshold']})",
        "",
        f"{'Name':<22}{'Pwr':>4}{'Int':>4}  {'Quadrant':<16}",
    ]
    for row in result["stakeholders"]:
        lines.append(f"{row['name']:<22}{row['power']:>4.0f}"
                     f"{row['interest']:>4.0f}  {row['quadrant']:<16}")
    lines.append("")
    lines.append("Counts by quadrant:")
    for quad, n in result["counts"].items():
        lines.append(f"  {quad:<16} {n}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("stakeholders", help="path to stakeholders JSON file, "
                        "or '-' for stdin")
    parser.add_argument("--threshold", type=float, default=3.0,
                        help="cut between low and high (default 3)")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.stakeholders)
        if isinstance(data, dict):
            items = data.get("stakeholders", [])
        else:
            items = data
        result = classify(items, args.threshold)
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
