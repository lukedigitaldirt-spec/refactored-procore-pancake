#!/usr/bin/env python3
"""Weighted vendor performance scorecard (stdlib-only).

Given a vendor and a set of weighted criteria (Quality, Delivery, Cost,
Service, Responsiveness, ...), each scored 1-5, this computes the weighted
total, a letter grade, a percentage, and flags any weak criteria.

- Each criterion is scored 1-5 with a weight. Weights are normalized to sum to
  1 if they do not already (and the result flags that it renormalized).
- weighted_total = sum(score * normalized_weight)  (on the 1-5 scale).
- pct = weighted_total / 5 * 100.
- Letter grade from weighted_total: A >= 4.5, B >= 3.5, C >= 2.5, D >= 1.5,
  else F.
- Any criterion scoring <= 2 is flagged as "at_risk" - a strong overall score
  can still hide a failing dimension that needs a corrective-action plan.

Importable as functions; runnable as a CLI.

Input JSON schema:
    {
      "vendor": "Acme",
      "criteria": [
        {"name": "Quality",        "score": 4, "weight": 0.30},
        {"name": "Delivery",       "score": 3, "weight": 0.25},
        {"name": "Cost",           "score": 5, "weight": 0.20},
        {"name": "Service",        "score": 4, "weight": 0.15},
        {"name": "Responsiveness", "score": 2, "weight": 0.10}
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import sys

AT_RISK_THRESHOLD = 2


def _grade(total: float) -> str:
    if total >= 4.5:
        return "A"
    if total >= 3.5:
        return "B"
    if total >= 2.5:
        return "C"
    if total >= 1.5:
        return "D"
    return "F"


def evaluate(spec) -> dict:
    """Return weighted total, grade, pct, per-criterion contributions."""
    if not isinstance(spec, dict):
        raise ValueError("input must be a JSON object")

    vendor = spec.get("vendor", "vendor")
    criteria = spec.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("'criteria' must be a non-empty list")

    parsed = []
    for i, crit in enumerate(criteria):
        label = crit.get("name", f"criterion_{i + 1}") \
            if isinstance(crit, dict) else f"criterion_{i + 1}"
        try:
            s = float(crit["score"])
            w = float(crit["weight"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"criterion '{label}' needs numeric 'score' and "
                "'weight'") from exc
        if not 1 <= s <= 5:
            raise ValueError(f"criterion '{label}' score must be in 1-5")
        if w < 0:
            raise ValueError(f"criterion '{label}' weight must be >= 0")
        parsed.append({"name": label, "score": s, "weight": w})

    weight_sum = sum(c["weight"] for c in parsed)
    if weight_sum <= 0:
        raise ValueError("weights must sum to a positive number")
    normalized = abs(weight_sum - 1.0) > 1e-9

    weighted_total = 0.0
    contributions = []
    at_risk = []
    for c in parsed:
        w = c["weight"] / weight_sum
        contrib = c["score"] * w
        weighted_total += contrib
        contributions.append({
            "name": c["name"],
            "score": c["score"],
            "weight": round(w, 6),
            "contribution": round(contrib, 6),
        })
        if c["score"] <= AT_RISK_THRESHOLD:
            at_risk.append(c["name"])

    pct = weighted_total / 5.0 * 100.0
    return {
        "vendor": vendor,
        "weighted_total": round(weighted_total, 4),
        "grade": _grade(weighted_total),
        "pct": round(pct, 2),
        "weights_normalized": normalized,
        "at_risk": at_risk,
        "contributions": contributions,
    }


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        f"Vendor Scorecard: {result['vendor']}",
        "=" * (18 + len(result["vendor"])),
        f"Weighted total: {result['weighted_total']} / 5   "
        f"({result['pct']}%)   Grade: {result['grade']}",
    ]
    if result["weights_normalized"]:
        lines.append("Note: weights did not sum to 1 and were normalized.")
    lines.append("")
    lines.append(f"{'Criterion':<18}{'Score':>7}{'Weight':>9}"
                 f"{'Contribution':>14}")
    for c in result["contributions"]:
        lines.append(f"{c['name']:<18}{c['score']:>7.1f}"
                     f"{c['weight']:>9.3f}{c['contribution']:>14.3f}")
    if result["at_risk"]:
        lines.append("")
        lines.append("AT RISK (score <= 2): " + ", ".join(result["at_risk"]))
        lines.append("Open a corrective-action plan for each before renewal.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("spec", help="path to scorecard JSON file, or '-'")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        spec = _load(args.spec)
        result = evaluate(spec)
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
