# Category management and tail/maverick spend

Spend analysis tells you *where* the money is; category management is the
operating discipline that *does something about it*, category by category, as an
ongoing program rather than a one-off sourcing event. It is the organizing frame
that ties the three tools in this skill together.

## What category management is
Treat each spend category as a mini-business with a strategy of its own. The
canonical loop (Jonathan O'Brien's work, and CIPS practice):

1. **Initiation** — scope the category, pull the spend cube, classify spend
   (`spend_categorizer.py`).
2. **Insight** — analyze the category: spend concentration and ABC
   (`spend_analyzer.py`), supplier fragmentation
   (`consolidation_advisor.py`), market and supplier dynamics, Kraljic
   positioning, demand and specification analysis.
3. **Strategy** — choose the lever that fits the category's Kraljic quadrant:
   consolidate and compete (leverage), partner (strategic), secure (bottleneck),
   automate and aggregate (routine).
4. **Delivery** — run the sourcing event, negotiate, contract, implement.
5. **Improvement** — manage the category on an ongoing basis: track compliance,
   savings realization, supplier performance; re-run the loop.

## Maverick (off-contract) spend
**Maverick spend** is buying that bypasses negotiated contracts and preferred
suppliers — purchasing off-contract when a contract exists. It directly
destroys the value category management creates:

- Pays non-negotiated (higher) prices.
- Leaks volume away from contracts, weakening the next negotiation.
- Evades spend visibility, so it resurfaces as **Uncategorized** spend in the
  categorizer — the first place to go hunting for it.

Reduce it with low-friction compliant paths (catalogs, guided buying, P-cards
with category controls), clear policy, and visibility that names the leakers.
The goal is to make the compliant path the *easy* path.

## Tail spend
The long C-class tail (see `spend-analysis-and-abc.md`) is managed, not
negotiated one supplier at a time. Tactics:

- **Aggregate** onto preferred suppliers, catalogs, and marketplaces.
- **Automate** the transaction (P-cards, e-procurement, no-touch POs).
- **Rationalize** duplicate and dormant suppliers out of the base.
- Consider a **managed tail-spend** service for the genuinely long tail.

## Savings discipline
- Distinguish **hard savings** (unit-price reductions you can show in the GL)
  from **cost avoidance** and **soft savings**.
- **Realized vs. negotiated** — savings on a term sheet are not savings until
  compliance converts them; leakage and maverick buying erode them.
- Set a **baseline** (last price paid, budget, or should-cost) and tie savings
  back to it; agree the methodology with Finance up front.
- Treat the consolidation tool's `estimated_savings` as a *negotiated-savings
  hypothesis* to be validated and then tracked to realization.

## Authoritative sources
1. Jonathan O'Brien, *Category Management in Purchasing*, 4th ed., Kogan Page,
   2019.
2. Robert M. Monczka et al., *Purchasing and Supply Chain Management*, 7th ed.,
   Cengage, 2020 (category strategy and compliance).
3. Paul D. Cousins et al., *Strategic Supply Management*, FT Prentice Hall,
   2008.
4. Peter Kraljic, "Purchasing Must Become Supply Management," *Harvard Business
   Review*, 1983 (category portfolio strategy).
5. CIPS, *Category Management* and *Maverick Spend / P2P Compliance* knowledge
   resources and practice guidance.
6. Institute for Supply Management (ISM), *ISM Glossary of Key Supply
   Management Terms* (maverick spend, savings definitions).
7. Hackett Group / APQC, *Procurement Benchmark* research on spend under
   management, compliance, and tail spend.
8. Gerard Chick & Robert Handfield, *The Procurement Value Proposition*, Kogan
   Page, 2014 (category management and value delivery).
