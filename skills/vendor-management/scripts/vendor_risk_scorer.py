#!/usr/bin/env python3
"""Vendor risk scorer: Kraljic matrix + weighted risk index (stdlib-only).

Two complementary lenses on a single supplier:

1. Kraljic purchasing portfolio matrix (Peter Kraljic, HBR 1983). Position the
   vendor on two 1-5 axes - ``supply_risk`` (how hard the item is to source)
   and ``profit_impact`` (how much it matters to the business). A score of 3 or
   more on an axis is "high". The quadrant implies a sourcing strategy:

     - high impact + high risk  -> Strategic   (partner / deep collaboration)
     - high impact + low risk   -> Leverage    (competitive tendering, power)
     - low impact + high risk   -> Bottleneck  (secure supply, hold stock)
     - low impact + low risk    -> Non-critical (automate, standardize)

2. A weighted risk index over named dimensions (financial, operational,
   compliance, concentration, geographic, ...). Each dimension is scored 1-5
   and multiplied by its weight; the weights are normalized to sum to 1 if they
   do not already (and the result flags that it renormalized). The weighted
   score maps to a band: < 2 Low, < 3.5 Medium, else High.

Importable as functions; runnable as a CLI.

Input JSON schema:
    {
      "name": "Acme",
      "supply_risk": 4,
      "profit_impact": 2,
      "dimensions": {
        "financial": 3, "operational": 4, "compliance": 2,
        "concentration": 5, "geographic": 1
      },
      "weights": {
        "financial": 0.3, "operational": 0.25, "compliance": 0.2,
        "concentration": 0.15, "geographic": 0.1
      }
    }
"""
from __future__ import annotations

import argparse
import json
import sys

STRATEGY = {
    "Strategic": "Partner: joint roadmaps, dual-source where possible, "
                 "executive relationship, contingency plans.",
    "Leverage": "Use buying power: competitive tendering, consolidate volume, "
                "negotiate on price and terms.",
    "Bottleneck": "Secure supply: safety stock, backup suppliers, long-term "
                  "agreements, redesign to remove the dependency.",
    "Non-critical": "Simplify: standardize, automate ordering, reduce "
                    "transaction cost and supplier count.",
}


def _axis_high(value: float) -> bool:
    return value >= 3


def quadrant(supply_risk: float, profit_impact: float) -> str:
    """Return the Kraljic quadrant name for two 1-5 axis scores."""
    high_risk = _axis_high(supply_risk)
    high_impact = _axis_high(profit_impact)
    if high_impact and high_risk:
        return "Strategic"
    if high_impact and not high_risk:
        return "Leverage"
    if not high_impact and high_risk:
        return "Bottleneck"
    return "Non-critical"


def _band(score: float) -> str:
    if score < 2:
        return "Low"
    if score < 3.5:
        return "Medium"
    return "High"


def score(spec) -> dict:
    """Return Kraljic quadrant, strategy, weighted risk score, and band."""
    if not isinstance(spec, dict):
        raise ValueError("input must be a JSON object")

    name = spec.get("name", "vendor")
    try:
        supply_risk = float(spec["supply_risk"])
        profit_impact = float(spec["profit_impact"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "need numeric 'supply_risk' and 'profit_impact'") from exc
    for label, val in (("supply_risk", supply_risk),
                       ("profit_impact", profit_impact)):
        if not 1 <= val <= 5:
            raise ValueError(f"{label} must be in 1-5, got {val}")

    dims = spec.get("dimensions")
    weights = spec.get("weights")
    if not isinstance(dims, dict) or not dims:
        raise ValueError("'dimensions' must be a non-empty object")
    if not isinstance(weights, dict) or not weights:
        raise ValueError("'weights' must be a non-empty object")

    parsed_dims = {}
    for key, val in dims.items():
        try:
            v = float(val)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"dimension '{key}' must be numeric") from exc
        if not 1 <= v <= 5:
            raise ValueError(f"dimension '{key}' must be in 1-5, got {v}")
        parsed_dims[key] = v

    parsed_weights = {}
    for key in parsed_dims:
        if key not in weights:
            raise ValueError(f"dimension '{key}' has no matching weight")
        try:
            w = float(weights[key])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"weight '{key}' must be numeric") from exc
        if w < 0:
            raise ValueError(f"weight '{key}' must be >= 0")
        parsed_weights[key] = w

    weight_sum = sum(parsed_weights.values())
    if weight_sum <= 0:
        raise ValueError("weights must sum to a positive number")
    normalized = abs(weight_sum - 1.0) > 1e-9
    norm_weights = {k: w / weight_sum for k, w in parsed_weights.items()}

    contributions = []
    weighted_score = 0.0
    for key, v in parsed_dims.items():
        w = norm_weights[key]
        contrib = v * w
        weighted_score += contrib
        contributions.append({
            "dimension": key,
            "score": v,
            "weight": round(w, 6),
            "contribution": round(contrib, 6),
        })

    quad = quadrant(supply_risk, profit_impact)
    return {
        "name": name,
        "supply_risk": supply_risk,
        "profit_impact": profit_impact,
        "quadrant": quad,
        "recommended_strategy": STRATEGY[quad],
        "weighted_score": round(weighted_score, 4),
        "band": _band(weighted_score),
        "weights_normalized": normalized,
        "contributions": contributions,
    }


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        f"Vendor Risk Profile: {result['name']}",
        "=" * (21 + len(result["name"])),
        f"Kraljic axes:   supply_risk={result['supply_risk']}  "
        f"profit_impact={result['profit_impact']}",
        f"Quadrant:       {result['quadrant']}",
        f"Strategy:       {result['recommended_strategy']}",
        "",
        f"Weighted risk:  {result['weighted_score']}  "
        f"(band: {result['band']})",
    ]
    if result["weights_normalized"]:
        lines.append("Note: weights did not sum to 1 and were normalized.")
    lines.append("")
    lines.append(f"{'Dimension':<16}{'Score':>7}{'Weight':>9}"
                 f"{'Contribution':>14}")
    for c in result["contributions"]:
        lines.append(f"{c['dimension']:<16}{c['score']:>7.1f}"
                     f"{c['weight']:>9.3f}{c['contribution']:>14.3f}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("spec", help="path to vendor JSON file, or '-'")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        spec = _load(args.spec)
        result = score(spec)
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
