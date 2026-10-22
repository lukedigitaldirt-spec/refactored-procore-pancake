#!/usr/bin/env python3
"""Workload-to-FTE staffing calculator with shrinkage (stdlib-only).

Converts a period workload (contact volume x average handle time) into the
number of full-time equivalents (FTE) required, accounting for the two factors
that sink naive headcount math:

- Occupancy cap: you cannot run agents at 100% utilization; a realistic cap
  (typically 80-88%) leaves slack to absorb arrival variability.
- Shrinkage: the share of paid time agents are NOT available for the work --
  breaks, training, meetings, leave, sick time, admin. Commonly 30-35%.

Pipeline:
    productive_hours_needed = contact_volume * aht_seconds / 3600
    base_fte  = productive_hours_needed / (paid_hours_per_fte * occupancy_cap)
    required_fte = base_fte / (1 - shrinkage)

``base_fte`` is the on-the-phone requirement; ``required_fte`` grosses it up
for shrinkage so that enough bodies are rostered to still cover the work. See
references/workforce-management-and-shrinkage.md.

Input JSON schema (object):
    {
      "contact_volume": 5000,
      "aht_seconds": 300,
      "period_paid_hours_per_fte": 160,
      "shrinkage_pct": 30,
      "occupancy_cap_pct": 85
    }
"""
from __future__ import annotations

import argparse
import json
import math
import sys


def compute(data: dict) -> dict:
    """Return the FTE requirement for a workload input dict."""
    required = ("contact_volume", "aht_seconds", "period_paid_hours_per_fte")
    for key in required:
        if key not in data:
            raise ValueError(f"input missing required key '{key}'")

    contact_volume = float(data["contact_volume"])
    aht_seconds = float(data["aht_seconds"])
    paid_hours = float(data["period_paid_hours_per_fte"])
    shrinkage_pct = float(data.get("shrinkage_pct", 0))
    occupancy_cap_pct = float(data.get("occupancy_cap_pct", 100))

    if contact_volume < 0:
        raise ValueError("contact_volume must be >= 0")
    if aht_seconds <= 0:
        raise ValueError("aht_seconds must be > 0")
    if paid_hours <= 0:
        raise ValueError("period_paid_hours_per_fte must be > 0")
    if not 0 <= shrinkage_pct < 100:
        raise ValueError("shrinkage_pct must be in [0, 100)")
    if not 0 < occupancy_cap_pct <= 100:
        raise ValueError("occupancy_cap_pct must be in (0, 100]")

    occupancy_cap = occupancy_cap_pct / 100.0
    shrinkage = shrinkage_pct / 100.0

    productive_hours_needed = contact_volume * aht_seconds / 3600.0
    base_fte = productive_hours_needed / (paid_hours * occupancy_cap)
    required_fte = base_fte / (1 - shrinkage)
    effective_hours_per_fte = paid_hours * (1 - shrinkage)

    return {
        "productive_hours_needed": round(productive_hours_needed, 4),
        "base_fte": round(base_fte, 4),
        "required_fte": round(required_fte, 4),
        "required_fte_rounded": int(math.ceil(required_fte)),
        "effective_hours_per_fte": round(effective_hours_per_fte, 4),
        "occupancy_cap_pct": occupancy_cap_pct,
        "shrinkage_pct": shrinkage_pct,
    }


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    return "\n".join([
        "Staffing Requirement (workload -> FTE)",
        "======================================",
        f"Productive hours needed:   {result['productive_hours_needed']}",
        f"Occupancy cap:             {result['occupancy_cap_pct']}%",
        f"Shrinkage:                 {result['shrinkage_pct']}%",
        f"Effective hours per FTE:   {result['effective_hours_per_fte']}",
        f"Base FTE (on the work):    {result['base_fte']}",
        f"Required FTE (w/ shrink):  {result['required_fte']}",
        f"Required FTE (rounded up): {result['required_fte_rounded']}",
    ])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("input", help="path to input JSON file, or '-' for "
                        "stdin")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.input)
        result = compute(data)
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
