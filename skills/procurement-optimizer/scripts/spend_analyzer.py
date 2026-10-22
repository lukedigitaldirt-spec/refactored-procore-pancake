#!/usr/bin/env python3
"""Pareto / ABC spend analyzer (stdlib-only).

Given a flat list of spend entries (a supplier, a category, a commodity — any
named bucket with an amount), this ranks them by spend and applies the classic
ABC / Pareto segmentation used across procurement and inventory management:

- Sort entries by amount descending and compute each entry's share of total
  spend plus the running cumulative share.
- ABC classification by cumulative share:
    A  cumulative share up to and including the entry is <= 80%
    B  cumulative share is <= 95% (and not A)
    C  the remaining tail (> 95%)
  The first (largest) entry is always class A, even if it alone exceeds 80%.
- The Pareto statistic: what percentage of entries make up the first 80% of
  spend (the "vital few"). In most spend bases a small fraction of suppliers
  carry the overwhelming majority of spend.
- The tail is the C class: its count, spend, and share. Tail spend is where
  fragmentation, maverick buying, and low negotiating leverage concentrate.

The tool is bucket-agnostic: feed it suppliers to find your strategic vendors,
or categories to find where spend concentrates.

Input JSON schema:
    {
      "spend": [
        {"name": "Supplier A", "amount": 500000},
        {"name": "Supplier B", "amount": 120000}
      ]
    }
A bare list of ``{"name", "amount"}`` objects is also accepted. ``amount``
must be numeric and non-negative.
"""
from __future__ import annotations

import argparse
import json
import sys


def analyze(spend) -> dict:
    """Rank spend entries and apply ABC / Pareto segmentation."""
    if not spend:
        raise ValueError("spend must be a non-empty list")

    parsed = []
    for i, entry in enumerate(spend):
        if not isinstance(entry, dict):
            raise ValueError(f"entry {i + 1} must be an object")
        name = entry.get("name", f"entry_{i + 1}")
        try:
            amount = float(entry["amount"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"entry '{name}' needs a numeric 'amount'") from exc
        if amount < 0:
            raise ValueError(f"entry '{name}' has negative amount")
        parsed.append({"name": name, "amount": amount})

    total = sum(e["amount"] for e in parsed)
    if total <= 0:
        raise ValueError("total spend must be > 0")

    parsed.sort(key=lambda e: e["amount"], reverse=True)

    ranked = []
    cumulative = 0.0
    a_count = b_count = c_count = 0
    entries_within_80 = 0
    reached_80 = False
    for idx, e in enumerate(parsed):
        cumulative += e["amount"]
        pct = e["amount"] / total * 100
        cum_pct = cumulative / total * 100

        if idx == 0 or cum_pct <= 80:
            abc = "A"
            a_count += 1
        elif cum_pct <= 95:
            abc = "B"
            b_count += 1
        else:
            abc = "C"
            c_count += 1

        if not reached_80:
            entries_within_80 += 1
            if cum_pct >= 80:
                reached_80 = True

        ranked.append({
            "name": e["name"],
            "amount": round(e["amount"], 4),
            "pct": round(pct, 2),
            "cumulative_pct": round(cum_pct, 2),
            "abc_class": abc,
        })

    tail = [r for r in ranked if r["abc_class"] == "C"]
    tail_spend = round(sum(r["amount"] for r in tail), 4)
    pareto_pct = round(entries_within_80 / len(ranked) * 100, 2)

    summary = {
        "total": round(total, 4),
        "entry_count": len(ranked),
        "a_count": a_count,
        "b_count": b_count,
        "c_count": c_count,
        "pareto_suppliers_pct_for_80": pareto_pct,
        "tail_count": len(tail),
        "tail_spend": tail_spend,
        "tail_pct": round(tail_spend / total * 100, 2),
    }
    return {"ranked": ranked, "summary": summary}


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    s = result["summary"]
    lines = [
        "Spend Analysis (Pareto / ABC)",
        "=============================",
        f"Entries:            {s['entry_count']}",
        f"Total spend:        {s['total']}",
        f"A / B / C entries:  {s['a_count']} / {s['b_count']} / {s['c_count']}",
        f"Vital few:          {s['pareto_suppliers_pct_for_80']}% of entries "
        "carry 80% of spend",
        f"Tail (C class):     {s['tail_count']} entries, {s['tail_spend']} "
        f"({s['tail_pct']}% of spend)",
        "",
        f"{'Rank':<6}{'Name':<24}{'Spend':>14}{'%':>8}{'Cum%':>8}{'ABC':>5}",
    ]
    for rank, r in enumerate(result["ranked"], start=1):
        lines.append(
            f"{rank:<6}{r['name']:<24}{r['amount']:>14.2f}"
            f"{r['pct']:>8.1f}{r['cumulative_pct']:>8.1f}{r['abc_class']:>5}")
    if s["tail_pct"] > 0:
        lines.append("")
        lines.append("The C-class tail is your consolidation and "
                     "rationalization target.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("spend", help="path to spend JSON file, or '-' for "
                        "stdin")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.spend)
        entries = data if isinstance(data, list) else data.get("spend")
        result = analyze(entries)
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
