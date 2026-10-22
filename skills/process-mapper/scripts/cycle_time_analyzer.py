#!/usr/bin/env python3
"""Cycle-time analyzer for process maps (stdlib-only).

Given an ordered list of process steps, each with a value-add processing time
and a non-value-add wait time, this computes the core lean/BPM timing metrics:

- Lead time (total elapsed): sum(process + wait) across all steps.
- Process time (touch time): sum(process).
- Wait time: sum(wait).
- Process Cycle Efficiency (PCE): process_time / lead_time.
- Takt time: available_time / customer_demand (only if both provided).

All times are unit-agnostic (minutes, hours, days) as long as they are
consistent. Importable as functions; runnable as a CLI.

Input JSON schema (list of steps):
    [
      {"name": "Intake",   "process": 5,  "wait": 120},
      {"name": "Review",   "process": 15, "wait": 480}
    ]
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional


def analyze(steps, available_time: Optional[float] = None,
            demand: Optional[float] = None) -> dict:
    """Return cycle-time metrics for a list of step dicts.

    Each step must have numeric ``process`` and ``wait`` keys and a ``name``.
    ``available_time`` and ``demand`` are optional and only used for takt time.
    """
    if not steps:
        raise ValueError("steps must be a non-empty list")

    process_time = 0.0
    wait_time = 0.0
    per_step = []
    for i, step in enumerate(steps):
        name = step.get("name", f"step_{i + 1}")
        try:
            p = float(step["process"])
            w = float(step["wait"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"step '{name}' needs numeric 'process' and 'wait'") from exc
        if p < 0 or w < 0:
            raise ValueError(f"step '{name}' has negative time")
        process_time += p
        wait_time += w
        per_step.append({"name": name, "process": p, "wait": w,
                         "elapsed": p + w})

    lead_time = process_time + wait_time
    pce = (process_time / lead_time) if lead_time > 0 else 0.0

    result = {
        "lead_time": round(lead_time, 4),
        "process_time": round(process_time, 4),
        "wait_time": round(wait_time, 4),
        "process_cycle_efficiency": round(pce, 4),
        "process_cycle_efficiency_pct": round(pce * 100, 2),
        "step_count": len(steps),
        "steps": per_step,
    }

    if available_time is not None and demand:
        if demand <= 0:
            raise ValueError("demand must be > 0 for takt time")
        result["takt_time"] = round(available_time / demand, 4)

    return result


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "Cycle-Time Analysis",
        "===================",
        f"Steps analyzed:            {result['step_count']}",
        f"Lead time (elapsed):       {result['lead_time']}",
        f"Process time (touch):      {result['process_time']}",
        f"Wait time (non-value-add): {result['wait_time']}",
        f"Process Cycle Efficiency:  {result['process_cycle_efficiency_pct']}%",
    ]
    if "takt_time" in result:
        lines.append(f"Takt time:                 {result['takt_time']}")
    if result["process_cycle_efficiency"] < 0.25:
        lines.append("")
        lines.append("WARNING: PCE < 25% - wait time dominates. Attack "
                     "queues/handoffs before touch time.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("steps", help="path to steps JSON file, or '-' for "
                        "stdin")
    parser.add_argument("--available-time", type=float, default=None,
                        help="available working time (for takt time)")
    parser.add_argument("--demand", type=float, default=None,
                        help="customer demand in units (for takt time)")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        steps = _load(args.steps)
        result = analyze(steps, args.available_time, args.demand)
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
