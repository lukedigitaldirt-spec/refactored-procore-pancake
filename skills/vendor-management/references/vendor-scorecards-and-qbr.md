# Vendor Scorecards and the Quarterly Business Review

Measuring supplier performance so the conversation is about evidence, not
opinion. This is the theory behind `scripts/scorecard.py`.

## What a scorecard is for
A scorecard turns "they've been a bit flaky lately" into a weighted, trended
number both sides can see. Its jobs:
- make performance expectations explicit *before* they are measured;
- drive a fact-based QBR instead of a venting session;
- feed renewal, consolidation, and corrective-action decisions.

## Choosing criteria (and weighting them)
Pick 4-7 criteria that actually matter for *this* category, and weight them to
reflect priorities. Common dimensions:

- **Quality** — defect rate, returns, first-pass yield, conformance to spec.
- **Delivery** — on-time-in-full (OTIF), lead-time adherence, fill rate.
- **Cost** — total cost of ownership, price stability, cost-reduction ideas.
- **Service / support** — responsiveness, issue resolution, account management.
- **Responsiveness / agility** — flexibility to demand changes, escalation speed.
- **Compliance / risk** — audit findings, security posture, ESG commitments.
- **Innovation** — roadmap contribution, proactive improvement.

Weights are a statement of strategy: a safety-critical component weights Quality
heavily; a commodity weights Cost. Normalize the weights so the total is a clean
1-5 (and a percentage).

## Scoring discipline
- Anchor the 1-5 scale with written descriptors so "3" means the same thing to
  everyone and every quarter.
- Prefer measured KPIs (OTIF %, defect PPM, mean time to respond) over gut feel;
  reserve subjective scores for genuinely qualitative criteria.
- A strong weighted total can hide a failing dimension — always surface any
  criterion scoring at or below 2 for a corrective-action plan, regardless of
  the overall grade.

## The Quarterly Business Review (QBR)
The scorecard is the agenda's backbone, not the whole meeting. A good QBR:
1. Reviews the scorecard and the trend since last quarter.
2. Closes out prior action items (did the corrective-action plan work?).
3. Looks forward: roadmap, demand changes, risks, cost initiatives.
4. Ends with a short, owned, dated action list for *both* sides.
Cadence follows segment: strategic vendors quarterly, others semi-annually or
annually. Share the scorecard with the vendor ahead of time — surprises make
for defensiveness, not improvement.

## Balanced incentives
Measure what you want more of, not only what you want less of. A scorecard that
is all penalties trains vendors to hide problems; include collaboration,
innovation, and responsiveness so the relationship improves, not just complies.

## Authoritative sources
1. Robert S. Kaplan & David P. Norton, "The Balanced Scorecard — Measures That
   Drive Performance," *Harvard Business Review*, Jan-Feb 1992.
2. Robert Monczka, Robert Handfield, Larry Giunipero & James Patterson,
   *Purchasing and Supply Chain Management*, 7th ed., Cengage, 2020.
3. APQC, *Supply Chain Management Process and Performance Benchmarks* (SCOR-based
   supplier metrics).
4. APICS / ASCM, *SCOR (Supply Chain Operations Reference) Model*, version 12.0
   (Reliability/Responsiveness metrics, OTIF, perfect order).
5. ISO 9001:2015, *Quality management systems — Requirements* (clause 8.4,
   control of externally provided processes, products and services).
6. CIPS (Chartered Institute of Procurement & Supply), *Supplier Performance
   Management* practice guidance.
7. Stephen Guth, *The Vendor Management Office (VMO)*, 2007.
8. Jonathan O'Brien, *Supplier Relationship Management: Unlocking the Hidden
   Value in Your Supply Base*, Kogan Page, 2nd ed., 2018.
9. IACCM / World Commerce & Contracting, *Governance and Relationship Management*
   contracting-excellence guidance.
