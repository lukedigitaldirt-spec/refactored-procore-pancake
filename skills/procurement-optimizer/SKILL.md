---
name: procurement-optimizer
description: >-
  Analyze and optimize indirect spend. Use when someone needs to categorize
  spend, build a spend cube, run a Pareto/ABC analysis, find supplier
  fragmentation and consolidation opportunities, hunt tail or maverick spend,
  or prep a sourcing wave. Triggers: "spend analysis", "categorize spend",
  "UNSPSC", "spend cube", "supplier consolidation", "rationalize suppliers",
  "tail spend", "maverick spend", "sourcing", "where is our spend going",
  "too many vendors". Ships three stdlib-only tools (spend_categorizer,
  spend_analyzer, consolidation_advisor). NOT for ongoing vendor
  governance/SLAs (use vendor-management) or mapping the procure-to-pay
  workflow itself (use process-mapper).
---

# Procurement Optimizer

Turn a fuzzy "we spend too much with too many vendors" into a **classified
spend cube, a ranked concentration analysis, and a quantified consolidation
plan**. Three lenses, three tools:

| Lens | Question it answers | Tool |
|------|--------------------|------|
| **Classification** | Where does every dollar actually go? | `scripts/spend_categorizer.py` |
| **Concentration** | Which suppliers/categories carry the spend? Where's the tail? | `scripts/spend_analyzer.py` |
| **Consolidation** | Which categories are fragmented, and what's the prize? | `scripts/consolidation_advisor.py` |

## Method (classify → analyze → consolidate)

1. **Classify first.** You cannot analyze spend you cannot name. Code every
   line item to a category with `spend_categorizer.py` (UNSPSC-aligned keyword
   map). Watch the **classification rate** — below ~90% your analysis is built
   on sand, and the **Uncategorized** bucket is the usual hiding place for tail
   and maverick (off-contract) spend.
2. **Find the concentration.** Run `spend_analyzer.py` (Pareto / ABC). A small
   fraction of suppliers almost always carry 80% of spend. The **A class** is
   your strategic few (manage tightly); the **C-class tail** is many suppliers
   with little spend each — the rationalization target.
3. **Quantify consolidation.** Run `consolidation_advisor.py` to group spend by
   category, count distinct suppliers per category, flag the fragmented ones,
   and estimate savings. Rank by savings so sourcing effort follows the money.
4. **Position before you act.** Overlay the **Kraljic matrix** (profit impact ×
   supply risk). Consolidate *leverage* categories hard; *partner* on
   strategic; *secure* bottlenecks; *automate/aggregate* the routine tail. Never
   single-source a high-risk category just to book a small saving.
5. **Prove and track the saving.** Treat estimated savings as a negotiated-
   savings hypothesis. Agree a baseline with Finance, then track realized (not
   just negotiated) savings — compliance and maverick spend erode the gap.

## Using the tools

All tools are stdlib-only, take a JSON file (or `-` for stdin), and support
`--json` for machine output.

```bash
# Classify line items (built-in UNSPSC-aligned map if category_map omitted)
python scripts/spend_categorizer.py line-items.json
python scripts/spend_categorizer.py line-items.json --json

# Pareto / ABC on suppliers OR categories (any name/amount list)
python scripts/spend_analyzer.py spend.json

# Consolidation opportunities (override assumptions from the CLI if you like)
python scripts/consolidation_advisor.py consolidation-input.json
python scripts/consolidation_advisor.py consolidation-input.json \
    --savings-rate 10 --min-suppliers 3
```

See `assets/` for ready-to-fill input templates and a starter UNSPSC keyword
map (`assets/unspsc-keyword-map.json`).

## Reference library

- `references/unspsc-and-spend-taxonomy.md` — UNSPSC's four levels and the spend cube.
- `references/spend-analysis-and-abc.md` — Pareto, ABC classes, and tail spend.
- `references/supplier-consolidation-and-sourcing.md` — Kraljic, TCO, rationalization.
- `references/category-management.md` — the category loop, maverick spend, savings discipline.

## Forcing-question library (grill-with-docs)

Do not present a spend analysis or a consolidation recommendation until these
are answered. If the user can't answer, that gap *is* the finding.

- **Data completeness:** "Does this spend data cover *all* buying channels —
  POs, invoices, P-cards, expenses — or just the part you can see easily?"
  Analysis on partial data overstates concentration and hides the tail.
- **Classification rate:** "What share of spend is actually coded to a
  category? What's sitting in Uncategorized, and have you looked at it?"
  Uncoded spend is where tail and maverick buying hide.
- **Supplier identity:** "Have supplier names been normalized and deduped? Is
  'IBM', 'I.B.M.', and 'IBM Corp' one supplier or three in this file?" A dirty
  supplier axis makes every concentration number wrong.
- **Risk, not just spend:** "For each category you want to consolidate, how many
  capable suppliers exist and how hard is it to switch?" Consolidating a
  high-risk category can trade a small saving for a continuity failure (Kraljic).
- **Savings assumption:** "Where does the savings rate come from — a benchmark,
  a prior negotiation, a should-cost? Is it hard savings Finance will recognize,
  or cost avoidance?" An unsourced rate is a guess dressed as a plan.
- **Maverick spend:** "Where is spend going off-contract when a contract already
  exists, and who is doing it?" Consolidation is worthless if buyers route
  around the deal.
- **Realization:** "Who owns turning a negotiated saving into a realized one,
  and how will you measure leakage?" Savings on a term sheet are not savings.
