#!/usr/bin/env python3
"""Supplier consolidation advisor (stdlib-only).

Given spend records tagged with a supplier and a category, this finds
categories served by many suppliers — the prime candidates for supplier
rationalization. Fragmented spend (the same category bought from several
vendors) forfeits volume leverage, multiplies transaction and management cost,
and is where maverick spend hides. Consolidating a fragmented category onto
fewer suppliers typically yields mid-single-digit to low-double-digit savings.

Logic:
- Group records by category; count distinct suppliers and sum spend per
  category.
- Flag any category whose distinct-supplier count is >= ``min_suppliers_to_flag``
  (default 2).
- For flagged categories only, estimate savings as
  ``category_spend * savings_rate_pct / 100``. The savings rate is a negotiated
  planning assumption, not a promise; validate it against category benchmarks.
- Rank opportunities by estimated savings descending so sourcing effort goes
  where the money is.

Input JSON schema:
    {
      "records": [
        {"supplier": "A", "category": "IT Hardware", "amount": 50000},
        {"supplier": "B", "category": "IT Hardware", "amount": 30000}
      ],
      "savings_rate_pct": 8,
      "min_suppliers_to_flag": 2
    }
``savings_rate_pct`` (default 8) must be in [0, 100]. ``min_suppliers_to_flag``
(default 2) must be an integer >= 1. ``amount`` must be numeric and
non-negative.
"""
from __future__ import annotations

import argparse
import json
import sys


def advise(records, savings_rate_pct: float = 8.0,
           min_suppliers_to_flag: int = 2) -> dict:
    """Group spend by category and surface consolidation opportunities."""
    if not records:
        raise ValueError("records must be a non-empty list")
    if not 0 <= savings_rate_pct <= 100:
        raise ValueError("savings_rate_pct must be between 0 and 100")
    if int(min_suppliers_to_flag) < 1:
        raise ValueError("min_suppliers_to_flag must be >= 1")
    min_suppliers_to_flag = int(min_suppliers_to_flag)

    by_category: dict = {}
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            raise ValueError(f"record {i + 1} must be an object")
        category = rec.get("category")
        supplier = rec.get("supplier")
        if not category or not isinstance(category, str):
            raise ValueError(f"record {i + 1} needs a 'category'")
        if not supplier or not isinstance(supplier, str):
            raise ValueError(f"record {i + 1} needs a 'supplier'")
        try:
            amount = float(rec["amount"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"record {i + 1} needs a numeric 'amount'") from exc
        if amount < 0:
            raise ValueError(f"record {i + 1} has negative amount")

        bucket = by_category.setdefault(
            category, {"suppliers": set(), "spend": 0.0})
        bucket["suppliers"].add(supplier)
        bucket["spend"] += amount

    categories: dict = {}
    opportunities = []
    total_savings = 0.0
    for category, bucket in by_category.items():
        supplier_count = len(bucket["suppliers"])
        spend = round(bucket["spend"], 4)
        flagged = supplier_count >= min_suppliers_to_flag
        est = round(spend * savings_rate_pct / 100, 4) if flagged else 0.0
        entry = {
            "suppliers": sorted(bucket["suppliers"]),
            "supplier_count": supplier_count,
            "spend": spend,
            "flagged": flagged,
            "estimated_savings": est,
        }
        categories[category] = entry
        if flagged:
            total_savings += est
            opportunities.append({
                "category": category,
                "supplier_count": supplier_count,
                "spend": spend,
                "estimated_savings": est,
            })

    opportunities.sort(key=lambda o: o["estimated_savings"], reverse=True)

    return {
        "savings_rate_pct": savings_rate_pct,
        "min_suppliers_to_flag": min_suppliers_to_flag,
        "categories": categories,
        "opportunities": opportunities,
        "total_estimated_savings": round(total_savings, 4),
    }


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "Supplier Consolidation Analysis",
        "===============================",
        f"Savings rate:            {result['savings_rate_pct']}%",
        f"Flag threshold:          >= {result['min_suppliers_to_flag']} "
        "suppliers / category",
        f"Total estimated savings: {result['total_estimated_savings']}",
        "",
        f"{'Category':<26}{'Suppliers':>10}{'Spend':>14}{'Est. savings':>16}",
    ]
    ordered = sorted(result["categories"].items(),
                     key=lambda kv: kv[1]["spend"], reverse=True)
    for category, entry in ordered:
        flag = " *" if entry["flagged"] else ""
        lines.append(
            f"{category:<26}{entry['supplier_count']:>10}"
            f"{entry['spend']:>14.2f}{entry['estimated_savings']:>16.2f}{flag}")
    if result["opportunities"]:
        lines.append("")
        lines.append("* = fragmented category flagged for consolidation. "
                     "Attack top-ranked opportunities first.")
    else:
        lines.append("")
        lines.append("No fragmented categories at this threshold.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("records", help="path to input JSON file, or '-' for "
                        "stdin")
    parser.add_argument("--savings-rate", type=float, default=None,
                        help="estimated savings rate percent (default 8)")
    parser.add_argument("--min-suppliers", type=int, default=None,
                        help="min distinct suppliers to flag (default 2)")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.records)
        if isinstance(data, list):
            records = data
            rate = 8.0
            min_sup = 2
        else:
            records = data.get("records")
            rate = data.get("savings_rate_pct", 8.0)
            min_sup = data.get("min_suppliers_to_flag", 2)
        if args.savings_rate is not None:
            rate = args.savings_rate
        if args.min_suppliers is not None:
            min_sup = args.min_suppliers
        result = advise(records, rate, min_sup)
    except (ValueError, OSError, json.JSONDecodeError, AttributeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
