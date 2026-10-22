# Supplier consolidation and strategic sourcing

When one category is bought from many suppliers, spend is fragmented: volume
leverage is forfeited, transaction and management cost multiply, quality varies,
and maverick spend hides in the gaps. Consolidating a fragmented category onto
fewer, better-managed suppliers is one of the highest-return moves in
procurement. This is the logic behind `scripts/consolidation_advisor.py`.

## Why fragmentation costs money
- **Lost leverage.** Spend split across vendors means no single contract is big
  enough to command best pricing, rebates, or service tiers.
- **Transaction cost.** Every supplier is onboarding, POs, invoices, payments,
  risk reviews, and relationship overhead. The total cost of a supplier is far
  more than the price it charges.
- **Price variance.** The same item bought from five vendors is bought at five
  prices — almost never the lowest.
- **Maverick spend.** Fragmentation is both a symptom and a cause of
  off-contract buying.

## The consolidation lever
Group spend by category, count distinct suppliers, and flag categories above a
supplier-count threshold. Estimated savings is a planning assumption applied to
the consolidatable spend — commonly **mid-single-digit to low-double-digit
percent** of category spend, from a mix of better unit price, volume rebates,
and lower process cost. Treat the rate as a hypothesis to validate in
negotiation, never a promise. Rank opportunities by savings so effort follows
the money.

## Do not consolidate blindly — the Kraljic matrix
Peter Kraljic's portfolio model segments categories on two axes — **profit
impact** (spend, value) and **supply risk** (scarcity, number of suppliers,
switching difficulty):

- **Leverage** (high profit impact, low risk) — many capable suppliers.
  *Consolidate and compete* for price. The sweet spot for this tool.
- **Strategic** (high impact, high risk) — few suppliers, critical items.
  *Partner*, develop, dual-source; consolidation can be dangerous here.
- **Bottleneck** (low impact, high risk) — secure supply and continuity first;
  savings is not the goal.
- **Non-critical / routine** (low impact, low risk) — automate and aggregate
  (tail spend); minimize process cost, not unit price.

Reducing a strategic or bottleneck category to a single source can trade a small
saving for a large continuity risk. Always pair consolidation with a
single-point-of-failure and supplier-health check.

## Sourcing mechanics
- **Demand aggregation** across business units before going to market.
- **Competitive events** (RFx, reverse auctions) where the category is
  leverage.
- **Should-cost / clean-sheet** models to anchor negotiation on cost, not last
  price paid.
- **Total Cost of Ownership (TCO)** — acquisition, operating, switching, and
  end-of-life cost, not sticker price.
- **Supplier rationalization roadmap** — tier suppliers (preferred, approved,
  transactional), set contract coverage targets, migrate the tail.

## Authoritative sources
1. Peter Kraljic, "Purchasing Must Become Supply Management," *Harvard Business
   Review*, 1983 (the Kraljic portfolio matrix).
2. Robert M. Monczka, Robert B. Handfield, Larry C. Giunipero & James L.
   Patterson, *Purchasing and Supply Chain Management*, 7th ed., Cengage, 2020.
3. Paul D. Cousins, Richard Lamming, Benn Lawson & Brian Squire, *Strategic
   Supply Management: Principles, Theories and Practice*, FT Prentice Hall,
   2008.
4. Jonathan O'Brien, *Category Management in Purchasing*, 4th ed., Kogan Page,
   2019 (sourcing strategy and supplier consolidation).
5. Lisa M. Ellram, "Total Cost of Ownership," *International Journal of Physical
   Distribution & Logistics Management*, 1995.
6. A.T. Kearney / Kearney, *Purchasing Chessboard* (sourcing and leverage
   strategies), Springer.
7. CIPS, *Supplier Base Rationalisation* and *Strategic Sourcing* knowledge
   resources.
8. Institute for Supply Management (ISM), *ISM Glossary of Key Supply
   Management Terms* and strategic-sourcing standards.
