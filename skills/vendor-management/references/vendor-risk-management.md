# Vendor Risk Management — Kraljic segmentation and weighted risk

How to decide *which* suppliers deserve *which* kind of attention, and how to
score the risk they carry. This is the theory behind
`scripts/vendor_risk_scorer.py`.

## The Kraljic purchasing portfolio matrix
Peter Kraljic's 1983 *Harvard Business Review* article reframed purchasing from
a clerical function into strategic supply management. It segments spend on two
axes:

- **Profit impact / importance:** volume of spend, effect on product quality or
  the business if the item is unavailable.
- **Supply risk / market complexity:** scarcity, number of suppliers, pace of
  technology change, substitution difficulty, logistics.

Four quadrants, four strategies:

| | Low supply risk | High supply risk |
|---|---|---|
| **High profit impact** | **Leverage** — exploit buying power, tender competitively | **Strategic** — partner, co-invest, dual-source, protect the relationship |
| **Low profit impact** | **Non-critical** — standardize, automate, reduce cost-to-serve | **Bottleneck** — secure supply, hold stock, find or engineer alternatives |

The point is *differentiated* management: you cannot and should not treat every
supplier the same. Strategic suppliers get executive relationships and joint
roadmaps; non-critical ones get a catalog and a p-card.

## Weighted multi-dimensional risk
A single "risk: high/low" label is too blunt for governance. Score each vendor
across named dimensions and weight them to your context:

- **Financial** — solvency, credit rating, dependence on your spend.
- **Operational** — delivery reliability, quality, capacity, key-person risk.
- **Compliance / regulatory** — data protection, licensing, sanctions, ESG.
- **Concentration** — how much of a category or a critical input rides on this
  one vendor (single points of failure).
- **Geographic / geopolitical** — country risk, logistics, climate exposure.

Normalize the weights, multiply by the 1-5 scores, and band the result. The band
drives cadence: High-risk/High-impact vendors earn quarterly business reviews
and continuity plans; Low/Low vendors earn an annual check.

## Fourth-party and concentration risk
Your vendor's vendors are your risk too (the "nth party" problem). Map critical
subcontractors and shared dependencies — a single cloud region or a single
chip supplier behind "different" vendors is a hidden concentration.

## Continuous, not one-time
Risk is dynamic: a financially healthy vendor can deteriorate in a quarter.
Re-score on a cadence set by the band, and on trigger events (ownership change,
breach, missed SLA, adverse media).

## Authoritative sources
1. Peter Kraljic, "Purchasing Must Become Supply Management," *Harvard Business
   Review*, Sept-Oct 1983.
2. ISO 31000:2018, *Risk management — Guidelines*.
3. NIST SP 800-161 Rev. 1, *Cybersecurity Supply Chain Risk Management Practices
   for Systems and Organizations*, 2022.
4. ISO 28000:2022, *Security and resilience — Security management systems for
   the supply chain*.
5. ISO 22301:2019, *Security and resilience — Business continuity management
   systems — Requirements*.
6. ISO 37500:2014, *Guidance on outsourcing*.
7. Robert Monczka, Robert Handfield, Larry Giunipero & James Patterson,
   *Purchasing and Supply Chain Management*, 7th ed., Cengage, 2020.
8. OCC Bulletin 2013-29, *Third-Party Relationships: Risk Management Guidance*,
   U.S. Office of the Comptroller of the Currency.
9. CIPS (Chartered Institute of Procurement & Supply), *Supplier Segmentation
   and the Kraljic Matrix* practice guidance.
