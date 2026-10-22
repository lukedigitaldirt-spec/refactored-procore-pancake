#!/usr/bin/env python3
"""Bottleneck detector using Theory of Constraints logic (stdlib-only).

Given process steps each with a throughput capacity (units per period), this
finds the constraint (lowest-capacity step), the process throughput (equal to
the constraint's capacity), and each step's utilization relative to demand.

The constraint governs the whole line: system throughput can never exceed the
slowest step. Steps upstream of the constraint that run faster only build
inventory; downstream steps starve.

Input JSON schema (list of steps):
    [
      {"name": "Intake",  "capacity": 100},
      {"name": "Review",  "capacity": 40},
      {"name": "Approve", "capacity": 80}
    ]
Capacity is in units per period (e.g. cases/hour). Optionally pass --demand to
compute utilization = demand / capacity per step.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional


def detect(steps, demand: Optional[float] = None) -> dict:
    """Return the constraint, throughput, and per-step utilization."""
    if not steps:
        raise ValueError("steps must be a non-empty list")

    parsed = []
    for i, step in enumerate(steps):
        name = step.get("name", f"step_{i + 1}")
        try:
            cap = float(step["capacity"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"step '{name}' needs numeric 'capacity'") from exc
        if cap <= 0:
            raise ValueError(f"step '{name}' capacity must be > 0")
        parsed.append({"name": name, "capacity": cap})

    constraint = min(parsed, key=lambda s: s["capacity"])
    throughput = constraint["capacity"]

    for s in parsed:
        # Utilization vs the pace set by demand (or by the constraint if no
        # demand given). Utilization > 1 means the step cannot keep up.
        pace = demand if demand is not None else throughput
        s["utilization"] = round(pace / s["capacity"], 4)
        s["is_constraint"] = s["name"] == constraint["name"]
        s["headroom"] = round(s["capacity"] - throughput, 4)

    result = {
        "constraint": constraint["name"],
        "throughput": round(throughput, 4),
        "steps": parsed,
    }
    if demand is not None:
        if demand <= 0:
            raise ValueError("demand must be > 0")
        result["demand"] = demand
        result["meets_demand"] = throughput >= demand
        result["throughput_gap"] = round(max(0.0, demand - throughput), 4)
    return result


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "Bottleneck Analysis (Theory of Constraints)",
        "===========================================",
        f"Constraint step: {result['constraint']}",
        f"System throughput: {result['throughput']} units/period",
        "",
        f"{'Step':<20}{'Capacity':>10}{'Util':>8}{'Constraint':>12}",
    ]
    for s in result["steps"]:
        flag = "<== HERE" if s["is_constraint"] else ""
        lines.append(f"{s['name']:<20}{s['capacity']:>10.1f}"
                     f"{s['utilization'] * 100:>7.0f}%{flag:>12}")
    if result.get("demand") is not None:
        lines.append("")
        if result["meets_demand"]:
            lines.append(f"Throughput meets demand ({result['demand']}).")
        else:
            lines.append(f"SHORTFALL: demand {result['demand']} exceeds "
                         f"throughput by {result['throughput_gap']} units/"
                         "period. Elevate the constraint before anything "
                         "else.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("steps", help="path to steps JSON file, or '-'")
    parser.add_argument("--demand", type=float, default=None,
                        help="required throughput (units/period)")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        steps = _load(args.steps)
        result = detect(steps, args.demand)
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
