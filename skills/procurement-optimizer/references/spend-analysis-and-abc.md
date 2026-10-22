# Spend analysis — Pareto and ABC segmentation

Once spend is classified, the first question is always *where is the money?*
A small number of suppliers or categories almost always carry the overwhelming
majority of spend. Pareto and ABC analysis make that concentration explicit so
sourcing effort goes where it pays. This is the logic behind
`scripts/spend_analyzer.py`.

## The Pareto principle
Vilfredo Pareto observed that ~80% of effects come from ~20% of causes; Joseph
Juran generalized it into the **"vital few and trivial many."** In spend bases
the ratio is often more extreme — 5-15% of suppliers can carry 80% of spend.
The managerial point: you have finite sourcing capacity, so spend it on the
vital few, and manage the trivial many with low-touch mechanisms.

## ABC classification
ABC is Pareto applied as a three-way segmentation, borrowed from inventory
management (Dickie's ABC analysis at General Electric). Sort entries by spend
descending, compute the running cumulative share, and cut:

- **A items** — the top of the curve, cumulative share up to ~80%. Few in
  number, enormous in value. Strategic: tight management, formal contracts,
  deep relationships, frequent review.
- **B items** — the next band, ~80-95% cumulative. Moderate attention, lighter
  contracts, periodic review.
- **C items** — the long tail beyond ~95%. Many entries, little value each.
  Minimize transaction cost: catalogs, P-cards, aggregation, automation. Do not
  spend expensive negotiator hours here one supplier at a time.

The exact 80/95 cut points are conventions, not laws; tune them to your curve.
By convention the single largest entry is always class A even if it alone
exceeds the A threshold.

## Tail spend
The C class is **tail spend** — typically the last ~20% of spend spread across
~80% of suppliers. It is where fragmentation, off-contract (maverick) buying,
duplicate suppliers, and weak leverage concentrate. The tail is rarely worth
negotiating supplier-by-supplier; it is worth *aggregating* — catalogs,
marketplaces, a managed tail-spend program, or consolidation onto preferred
suppliers (see `supplier-consolidation-and-sourcing.md`).

## Reading the numbers
- **% of suppliers for 80% of spend** — the headline concentration stat. Low =
  highly concentrated (manage the few); high = fragmented (consolidation
  opportunity).
- **Tail count and tail %** — the size of the rationalization prize.
- Pair spend concentration with **supply risk** before acting; a tiny-spend
  supplier can still be a single point of failure (see Kraljic in
  `supplier-consolidation-and-sourcing.md`).

## Pitfalls
- ABC on **unclassified or un-deduplicated** data just ranks noise.
- Concentration is not the whole story — weigh risk, switching cost, and
  contract coverage alongside spend.
- A right-skewed distribution means the **mean** supplier is misleading; reason
  about the curve, not the average.

## Authoritative sources
1. Joseph M. Juran & A. Blanton Godfrey, *Juran's Quality Handbook*, 5th ed.,
   McGraw-Hill, 1999 (the "vital few," Pareto principle).
2. H. Ford Dickie, "ABC Inventory Analysis Shoots for Dollars, Not Pennies,"
   *Factory Management and Maintenance*, 1951.
3. Vilfredo Pareto, *Cours d'économie politique*, 1896 (original 80/20
   observation).
4. P. Fraser Johnson, Michiel Leenders & Anna Flynn, *Purchasing and Supply
   Management*, 16th ed., McGraw-Hill, 2020 (ABC and spend analysis).
5. Robert J. Engel & Patricia Normandy, *Spend Analysis: The Window into
   Strategic Sourcing*, J. Ross Publishing, 2008.
6. Lisa M. Ellram & Thomas Y. Choi, *Supply Management* (tail spend and
   supplier base rationalization), ISM publications.
7. CIPS, *Spend Analysis* and *Managing the Supply Base* knowledge resources.
8. A.T. Kearney / Kearney, *Assessment of Excellence in Procurement (AEP)*
   studies on spend concentration and tail spend.
