#!/usr/bin/env python3
"""UNSPSC-aligned spend categorizer (stdlib-only).

Classifies free-text purchase line items into spend categories by matching
each item's description against a keyword map. This is the first move of any
spend-analysis engagement: you cannot analyze, benchmark, or consolidate spend
until every dollar is mapped to a category. Uncategorized spend is surfaced
separately because it is the usual hiding place for tail spend and off-contract
(maverick) buying.

Classification uses case-insensitive substring matching. Each line item is
assigned to the FIRST category (in map order) whose keyword list produces a
hit against the description; anything with no hit falls to "Uncategorized".

UNSPSC (the UN Standard Products and Services Code, governed by GS1 US) is a
four-level hierarchy:
    Segment (2-digit)  ->  Family (4-digit)  ->  Class (6-digit)  ->
    Commodity (8-digit)
The built-in default map is aligned to common UNSPSC Segments/Families (IT
hardware, software, office supplies, professional services, facilities, travel,
marketing, logistics). It is a pragmatic keyword proxy, not a certified UNSPSC
crosswalk; for audited coding, map to real 8-digit commodity codes.

Input JSON schema:
    {
      "line_items": [
        {"description": "Dell laptops", "supplier": "Dell", "amount": 45000}
      ],
      "category_map": {
        "IT Hardware":     ["laptop", "server", "monitor"],
        "Office Supplies": ["paper", "pen", "toner"]
      }
    }
``category_map`` is optional; when omitted the built-in default map is used.
``supplier`` is optional on each line item. ``amount`` must be numeric and
non-negative.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

# Default keyword map, ordered and aligned to common UNSPSC Segments/Families.
# Order matters: the first category with a keyword hit wins.
DEFAULT_CATEGORY_MAP = {
    "IT Hardware": ["laptop", "desktop", "server", "monitor", "keyboard",
                    "router", "switch", "printer", "workstation", "tablet"],
    "Software": ["software", "license", "subscription", "saas", "cloud",
                 "platform", "api", "seat"],
    "Office Supplies": ["paper", "pen", "pencil", "toner", "ink", "stapler",
                        "notebook", "folder", "envelope"],
    "Professional Services": ["consulting", "advisory", "legal", "audit",
                              "accounting", "staffing", "contractor",
                              "recruiting"],
    "Facilities": ["rent", "lease", "cleaning", "janitorial", "hvac",
                   "maintenance", "utilities", "electricity", "security"],
    "Travel": ["airfare", "flight", "hotel", "lodging", "rental car",
               "taxi", "rail", "mileage", "per diem"],
    "Marketing": ["advertising", "media", "campaign", "agency", "branding",
                  "events", "sponsorship", "print collateral", "seo"],
    "Logistics": ["freight", "shipping", "courier", "warehousing", "pallet",
                  "customs", "trucking", "parcel", "drayage"],
}

UNCATEGORIZED = "Uncategorized"


def _match_category(description: str, category_map: dict) -> Optional[str]:
    """Return the first category whose keyword appears in description."""
    desc = description.lower()
    for category, keywords in category_map.items():
        for kw in keywords:
            if kw and kw.lower() in desc:
                return category
    return None


def categorize(line_items, category_map: Optional[dict] = None) -> dict:
    """Categorize line items and summarize spend by category.

    Each line item needs a ``description`` and a numeric ``amount``.
    Returns per-category totals, the uncategorized total/percentage, the
    categorized percentage, and the list of uncategorized descriptions.
    """
    if not line_items:
        raise ValueError("line_items must be a non-empty list")

    cmap = category_map if category_map else DEFAULT_CATEGORY_MAP
    if not isinstance(cmap, dict) or not cmap:
        raise ValueError("category_map must be a non-empty object")

    spend_by_category: dict = {}
    uncategorized_descriptions = []
    uncategorized_total = 0.0
    total = 0.0

    for i, item in enumerate(line_items):
        if not isinstance(item, dict):
            raise ValueError(f"line item {i + 1} must be an object")
        desc = item.get("description")
        if not desc or not isinstance(desc, str):
            raise ValueError(
                f"line item {i + 1} needs a non-empty 'description'")
        try:
            amount = float(item["amount"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"line item '{desc}' needs a numeric 'amount'") from exc
        if amount < 0:
            raise ValueError(f"line item '{desc}' has negative amount")

        total += amount
        category = _match_category(desc, cmap) or UNCATEGORIZED
        bucket = spend_by_category.setdefault(
            category, {"total": 0.0, "count": 0})
        bucket["total"] = round(bucket["total"] + amount, 4)
        bucket["count"] += 1

        if category == UNCATEGORIZED:
            uncategorized_total += amount
            uncategorized_descriptions.append(desc)

    uncat_pct = (uncategorized_total / total * 100) if total > 0 else 0.0
    result = {
        "spend_by_category": spend_by_category,
        "total_spend": round(total, 4),
        "uncategorized_total": round(uncategorized_total, 4),
        "uncategorized_pct": round(uncat_pct, 2),
        "categorized_pct": round(100 - uncat_pct, 2),
        "uncategorized_descriptions": uncategorized_descriptions,
        "line_item_count": len(line_items),
    }
    return result


def _load(path: str):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _format_human(result: dict) -> str:
    lines = [
        "Spend Categorization (UNSPSC-aligned)",
        "=====================================",
        f"Line items:        {result['line_item_count']}",
        f"Total spend:       {result['total_spend']}",
        f"Categorized:       {result['categorized_pct']}%",
        f"Uncategorized:     {result['uncategorized_pct']}%",
        "",
        f"{'Category':<26}{'Spend':>14}{'Items':>8}",
    ]
    ordered = sorted(result["spend_by_category"].items(),
                     key=lambda kv: kv[1]["total"], reverse=True)
    for category, bucket in ordered:
        lines.append(
            f"{category:<26}{bucket['total']:>14.2f}{bucket['count']:>8}")
    if result["uncategorized_pct"] > 0:
        lines.append("")
        lines.append("WARNING: uncategorized spend is the usual home of tail "
                     "and maverick spend. Code it before analyzing.")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("items", help="path to input JSON file, or '-' for "
                        "stdin")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        data = _load(args.items)
        if isinstance(data, list):
            line_items = data
            category_map = None
        else:
            line_items = data.get("line_items")
            category_map = data.get("category_map")
        result = categorize(line_items, category_map)
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
