#!/usr/bin/env python3
"""ADKAR change-readiness assessment (stdlib-only).

Prosci's ADKAR model says an individual moves through five sequential building
blocks to make a change stick: Awareness, Desire, Knowledge, Ability, and
Reinforcement. The blocks are ordered: you cannot build Desire before Awareness,
or Ability before Knowledge. The first block that scores below threshold is the
"barrier point" — the gap that blocks everything after it, and therefore the one
to fix first. Scoring the remaining blocks higher does not help until the
barrier is cleared.

This tool takes a 1-5 score per dimension, finds the barrier point (the FIRST
dimension in A-D-K-A-R order below threshold), reports per-dimension pass/fail
and the overall average, and recommends the action matched to the barrier.

Importable as functions; runnable as a CLI.

Input JSON schema (object):
    {
      "change": "New CRM rollout",
      "scores": {
        "awareness": 4,
        "desire": 2,
        "knowledge": 3,
        "ability": 4,
        "reinforcement": 1
      },
      "threshold": 3
    }
``change`` is an optional label. ``scores`` must contain all five dimensions,
each an integer or float in 1-5. ``threshold`` is optional (default 3): a
dimension at or above threshold passes, below it fails.
"""
from __future__ import annotations

import argparse
import json
import sys

# Canonical ADKAR order — the sequence is load-bearing, not cosmetic.
DIMENSIONS = ["awareness", "desire", "knowledge", "ability", "reinforcement"]

ACTIONS = {
    "awareness": "Communicate the why: the business reason for the change and "
                 "the risk of not changing.",
    "desire": "Address WIIFM and secure visible sponsorship; surface and work "
              "the sources of resistance.",
    "knowledge": "Deliver training on how to change — new processes, tools, "
                 "roles, and behaviors.",
    "ability": "Provide coaching, hands-on practice, and time so people can "
               "apply the knowledge in the real job.",
    "reinforcement": "Reward and measure the new behavior; remove rewards for "
                     "the old way so the change holds.",
}


def assess(change, scores, threshold: float = 3.0) -> dict:
    """Return the ADKAR assessment for a dict of dimension scores.

    ``scores`` must have all five ADKAR dimensions, each in 1-5. ``threshold``
    is the pass mark (default 3). The barrier point is the first dimension in
    ADKAR order scoring below threshold, or None if all pass.
    """
    if not isinstance(scores, dict):
        raise ValueError("scores must be an object of dimension -> value")

    missing = [d for d in DIMENSIONS if d not in scores]
    if missing:
        raise ValueError(f"missing ADKAR dimension(s): {', '.join(missing)}")
    extra = [k for k in scores if k not in DIMENSIONS]
    if extra:
        raise ValueError(f"unknown dimension(s): {', '.join(extra)}")

    parsed = {}
    for dim in DIMENSIONS:
        try:
            val = float(scores[dim])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"dimension '{dim}' must be numeric") from exc
        if not 1 <= val <= 5:
            raise ValueError(f"dimension '{dim}' must be in 1-5, got {val}")
        parsed[dim] = val

    barrier = None
    per_dim = []
    for dim in DIMENSIONS:
        val = parsed[dim]
        passed = val >= threshold
        if not passed and barrier is None:
            barrier = dim
        per_dim.append({
            "dimension": dim,
            "score": round(val, 4),
            "passed": passed,
            "is_barrier": False,
        })

    for row in per_dim:
        row["is_barrier"] = row["dimension"] == barrier

    overall = sum(parsed.values()) / len(DIMENSIONS)

    result = {
        "change": change,
        "threshold": round(float(threshold), 4),
        "overall": round(overall, 4),
        "barrier_point": barrier,
        "recommended_action": ACTIONS[barrier] if barrier else None,
        "dimensions": per_dim,
    }
    return result


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    label = result.get("change") or "(unnamed change)"
    lines = [
        "ADKAR Change-Readiness Assessment",
        "=================================",
        f"Change:    {label}",
        f"Threshold: {result['threshold']}",
        f"Overall:   {result['overall']} / 5",
        "",
        f"{'Dimension':<16}{'Score':>7}{'Result':>9}",
    ]
    for row in result["dimensions"]:
        flag = "FAIL" if not row["passed"] else "pass"
        marker = " <== barrier" if row["is_barrier"] else ""
        lines.append(f"{row['dimension']:<16}{row['score']:>7.1f}"
                     f"{flag:>9}{marker}")
    lines.append("")
    if result["barrier_point"]:
        lines.append(f"Barrier point: {result['barrier_point'].upper()}")
        lines.append(f"Fix first: {result['recommended_action']}")
    else:
        lines.append("No barrier: all dimensions clear the threshold. "
                     "Focus on reinforcement to hold the gain.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("assessment", help="path to assessment JSON file, or "
                        "'-' for stdin")
    parser.add_argument("--threshold", type=float, default=None,
                        help="override pass threshold (default 3, or the "
                        "value in the JSON)")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.assessment)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        threshold = args.threshold
        if threshold is None:
            threshold = data.get("threshold", 3.0)
        result = assess(data.get("change"), data.get("scores"), threshold)
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
