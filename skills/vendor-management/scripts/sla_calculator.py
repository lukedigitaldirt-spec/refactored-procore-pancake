#!/usr/bin/env python3
"""SLA/SLO attainment and error-budget calculator (stdlib-only).

Given an availability target, a measurement period, and observed downtime, this
computes whether the service-level objective was met and how much error budget
is left. If service-credit tiers are supplied (as in an SLA contract), it also
returns the credit owed to the customer.

Definitions (all downtime is in minutes, all percentages 0-100):

- actual_uptime_pct = (period_minutes - downtime_minutes) / period_minutes * 100
- allowed_downtime_minutes = period_minutes * (1 - target_pct / 100)  (budget)
- error_budget_minutes_remaining = allowed_downtime_minutes - downtime_minutes
  (negative means the budget is overspent / the SLO is breached).
- breached = actual_uptime_pct < target_pct.
- service_credit_pct = the largest credit among the tiers whose ``below_pct``
  threshold is above the actual uptime (i.e. tiers the service fell below),
  else 0. Tiers are evaluated independently; the worst applicable one wins.

Importable as functions; runnable as a CLI.

Input JSON schema:
    {
      "target_pct": 99.9,
      "period_hours": 720,
      "downtime_minutes": 130,
      "credit_tiers": [
        {"below_pct": 99.9, "credit_pct": 10},
        {"below_pct": 99.0, "credit_pct": 25}
      ]
    }
``credit_tiers`` is optional.
"""
from __future__ import annotations

import argparse
import json
import sys


def calculate(spec) -> dict:
    """Return SLA attainment and error-budget metrics for a spec dict."""
    if not isinstance(spec, dict):
        raise ValueError("input must be a JSON object")

    try:
        target_pct = float(spec["target_pct"])
        period_hours = float(spec["period_hours"])
        downtime_minutes = float(spec["downtime_minutes"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "need numeric 'target_pct', 'period_hours', "
            "'downtime_minutes'") from exc

    if not 0 < target_pct <= 100:
        raise ValueError("target_pct must be in (0, 100]")
    if period_hours <= 0:
        raise ValueError("period_hours must be > 0")
    if downtime_minutes < 0:
        raise ValueError("downtime_minutes must be >= 0")

    period_minutes = period_hours * 60.0
    if downtime_minutes > period_minutes:
        raise ValueError("downtime_minutes cannot exceed the period")

    uptime_minutes = period_minutes - downtime_minutes
    actual_uptime_pct = uptime_minutes / period_minutes * 100.0
    allowed_downtime = period_minutes * (1.0 - target_pct / 100.0)
    budget_remaining = allowed_downtime - downtime_minutes
    breached = actual_uptime_pct < target_pct

    tiers = spec.get("credit_tiers") or []
    if not isinstance(tiers, list):
        raise ValueError("credit_tiers must be a list")
    credit_pct = 0.0
    applied_tier = None
    for i, tier in enumerate(tiers):
        try:
            below = float(tier["below_pct"])
            credit = float(tier["credit_pct"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"credit tier {i + 1} needs numeric 'below_pct' and "
                "'credit_pct'") from exc
        if credit < 0:
            raise ValueError(f"credit tier {i + 1} has negative credit_pct")
        if actual_uptime_pct < below and credit > credit_pct:
            credit_pct = credit
            applied_tier = below

    return {
        "target_pct": round(target_pct, 6),
        "period_minutes": round(period_minutes, 4),
        "downtime_minutes": round(downtime_minutes, 4),
        "actual_uptime_pct": round(actual_uptime_pct, 6),
        "allowed_downtime_minutes": round(allowed_downtime, 4),
        "error_budget_minutes_remaining": round(budget_remaining, 4),
        "breached": breached,
        "service_credit_pct": round(credit_pct, 4),
        "applied_tier_below_pct": applied_tier,
    }


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    verdict = "BREACH" if result["breached"] else "PASS"
    lines = [
        "SLA / SLO Attainment",
        "====================",
        f"Target uptime:             {result['target_pct']}%",
        f"Actual uptime:             {round(result['actual_uptime_pct'], 4)}%",
        f"Downtime (observed):       {result['downtime_minutes']} min",
        f"Allowed downtime (budget): {result['allowed_downtime_minutes']} min",
        f"Error budget remaining:    "
        f"{result['error_budget_minutes_remaining']} min",
        f"Result: {verdict}",
    ]
    if result["service_credit_pct"] > 0:
        lines.append("")
        lines.append(f"Service credit owed: {result['service_credit_pct']}% "
                     f"(fell below {result['applied_tier_below_pct']}%).")
    if result["breached"]:
        lines.append("")
        lines.append("WARNING: SLO breached - error budget is overspent. "
                     "Freeze risky changes and prioritize reliability work.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("spec", help="path to SLA JSON file, or '-' for stdin")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        spec = _load(args.spec)
        result = calculate(spec)
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
