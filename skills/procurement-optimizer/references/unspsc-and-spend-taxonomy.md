# UNSPSC and spend taxonomy — getting every dollar coded

You cannot analyze, benchmark, or consolidate spend you cannot classify. A
spend taxonomy is the shared language that turns a pile of PO and AP line items
into categories you can reason about. This is the logic behind
`scripts/spend_categorizer.py`.

## UNSPSC in one screen
The **United Nations Standard Products and Services Code (UNSPSC)** is the de
facto global taxonomy for products and services, governed by GS1 US. It is a
strict four-level hierarchy, each level a two-digit pair of an eight-digit code:

1. **Segment** (XX000000) — the broadest grouping, e.g. *43 — IT and
   telecommunications*.
2. **Family** (XXXX0000) — a commodity group within a segment, e.g. *4321 —
   Computer equipment and accessories*.
3. **Class** (XXXXXX00) — a group of commodities with common characteristics,
   e.g. *432115 — Notebook computers*.
4. **Commodity** (XXXXXXXX) — the specific product or service, the level most
   buying actually happens at.

A fifth optional pair, the **Business Function** code, qualifies the role
(rental vs. purchase vs. maintenance). UNSPSC was originally the merger of the
UN's UNCCS and Dun & Bradstreet's SPSC codes; the UNDP uses it to classify
procurement worldwide.

## The spend cube
Classified spend is usually modeled as a **spend cube** — a multidimensional
view sliceable by at least three axes:

- **Category** (what was bought — the taxonomy above),
- **Supplier** (who it was bought from),
- **Business unit / cost center** (who bought it).

Common further dimensions: time period, geography, contract vs. off-contract,
and GL account. The cube is the substrate every downstream analysis (Pareto,
ABC, consolidation) runs on.

## Classification approaches
- **Rules / keyword** (what the tool ships) — fast, transparent, auditable; the
  first-match-wins keyword map is a pragmatic proxy for UNSPSC segments. Weak on
  ambiguous free text.
- **Supplier-based** — map each supplier to a dominant category. Fast but wrong
  whenever a supplier spans categories (e.g. Amazon, Grainger).
- **Machine-learning / auto-classification** — vendors score line items against
  a trained taxonomy. Powerful at scale, but needs governance and a human
  review loop.

Whatever the method, measure **classification rate**: the share of spend mapped
to a real category. Below ~90% your analysis is built on sand, and the
uncategorized remainder is exactly where tail and maverick spend hide.

## Taxonomy hygiene
- Keep categories **MECE** (mutually exclusive, collectively exhaustive) at each
  level — no line item should plausibly belong to two sibling categories.
- Normalize supplier names first (dedupe "IBM", "I.B.M.", "IBM Corp") or your
  supplier axis is noise.
- Freeze the taxonomy per analysis cycle; a moving taxonomy makes period-over-
  period comparison meaningless.
- Reconcile classified spend back to the general ledger so totals tie out.

## Authoritative sources
1. GS1 US, *UNSPSC Codeset and Guidelines* (official UNSPSC code owner and
   documentation), current release.
2. United Nations Development Programme, *UNSPSC — United Nations Standard
   Products and Services Code* reference and procurement usage guidance.
3. Robert A. Rudzki & Robert J. Trent, *Next Level Supply Management
   Excellence*, J. Ross Publishing, 2011 (spend taxonomy and spend cube).
4. Jason Busch et al., *Spend Analysis: The Window into Strategic Sourcing*
   (Pandit & Marmanis), J. Ross Publishing, 2008.
5. Robert J. Engel & Patricia M. Normandy, *Spend Analysis: The Window into
   Strategic Sourcing*, J. Ross Publishing, 2008.
6. CIPS (Chartered Institute of Procurement & Supply), *Spend Analysis* and
   *Category Taxonomy* knowledge resources.
7. P. Fraser Johnson, Michiel Leenders & Anna Flynn, *Purchasing and Supply
   Management*, 16th ed., McGraw-Hill, 2020 (spend classification).
8. Gartner / APQC, *Procurement Spend Classification and Category Taxonomy*
   benchmark research.
