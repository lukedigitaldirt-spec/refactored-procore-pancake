---
name: vendor-management
description: >-
  Govern suppliers and third parties with evidence, not opinion. Use when
  someone needs to check whether a vendor met its SLA, compute an error budget
  or service credit, segment suppliers by risk, decide a sourcing strategy, or
  score and review vendor performance. Triggers: "SLA", "SLO", "uptime", "error
  budget", "service credit", "vendor risk", "supplier risk", "Kraljic",
  "strategic supplier", "single source", "vendor scorecard", "supplier
  performance", "QBR", "vendor review", "should we renew this vendor". Ships
  three stdlib-only tools (sla_calculator, vendor_risk_scorer, scorecard). NOT
  for the internal workflow itself (use process-mapper) or staffing math (use
  capacity-planner).
---

# Vendor Management

Turn "are we getting what we pay for, and how exposed are we?" into **hard
numbers, a sourcing strategy, and a defensible review**. Three lenses, three
tools:

| Lens | Question it answers | Tool |
|------|--------------------|------|
| **Reliability** | Did the vendor meet its SLA? How much error budget is left? | `scripts/sla_calculator.py` |
| **Risk** | How exposed are we, and how should we source this? | `scripts/vendor_risk_scorer.py` |
| **Performance** | How is this vendor actually doing, by weighted evidence? | `scripts/scorecard.py` |

## Method (measure → segment → govern)

1. **Nail the SLA math.** Pin down the target, the measurement period, and what
   counts as downtime, then run `sla_calculator.py`. Report PASS/BREACH, the
   error budget remaining, and any service credit owed. A breach is a signal to
   fix the system, not just to collect a credit.
2. **Segment by risk.** Run `vendor_risk_scorer.py` to place the vendor on the
   **Kraljic matrix** (supply risk x profit impact) and to compute a weighted,
   multi-dimensional risk band. The quadrant dictates the sourcing strategy and
   the band dictates the review cadence — you cannot manage every supplier the
   same way.
3. **Score performance.** Run `scorecard.py` with weighted criteria (Quality,
   Delivery, Cost, Service, Responsiveness, ...). The weighted total gives a
   grade and a percentage; any criterion scoring <=2 is flagged for a
   corrective-action plan even when the overall grade looks fine.
4. **Govern the loop.** Feed all three into a Quarterly Business Review (see the
   agenda in `assets/`). Share the numbers with the vendor *before* the meeting,
   close out prior actions, and end with a short, owned, dated action list.
5. **Re-measure on a cadence.** Risk and performance drift; strategic vendors
   get a quarterly loop, non-critical ones an annual check. Re-score on trigger
   events (breach, ownership change, adverse media) regardless of cadence.

## Using the tools

All tools are stdlib-only, take a JSON file (or `-` for stdin), and support
`--json` for machine output.

```bash
# SLA / SLO attainment, error budget, and tiered service credits
python scripts/sla_calculator.py sla-input.json
cat sla-input.json | python scripts/sla_calculator.py - --json

# Kraljic quadrant + weighted multi-dimensional risk band
python scripts/vendor_risk_scorer.py risk-input.json

# Weighted vendor performance scorecard (grade, pct, at-risk criteria)
python scripts/scorecard.py scorecard-input.json --json
```

See `assets/` for ready-to-fill input templates and a QBR agenda.

## Reference library

- `references/sla-slo-management.md` — SLIs/SLOs, the nines, error budgets, credits.
- `references/vendor-risk-management.md` — Kraljic matrix and weighted risk.
- `references/vendor-scorecards-and-qbr.md` — scorecard design and the QBR.
- `references/contracts-and-governance.md` — the clauses and cadence that make it real.

## Forcing-question library (grill-with-docs)

Do not score a vendor or declare a breach until these are answered. If the user
can't answer, that gap *is* the finding.

- **Measurement definition:** "What exactly counts as 'down', who measures it,
  over what period, and which maintenance windows are excluded?" An SLA number
  with no agreed measurement method is unenforceable.
- **SLO vs. SLA:** "Is this the internal objective or the contractual promise —
  and is there headroom between them?" An SLA set at the limit of what you can
  deliver has no error budget and will be breached.
- **Impact vs. risk, honestly:** "On a 1-5 scale, how hard is this to source
  *and* how much does the business suffer if it stops? What evidence backs each
  score?" Kraljic placement built on gut feel misroutes the strategy.
- **Concentration:** "How much of this category — or of a critical input — rides
  on this single vendor, and who are *their* critical suppliers?" Hidden
  single points of failure (including fourth parties) are the risk that bites.
- **Weighted on purpose:** "Do the scorecard weights reflect what actually
  matters for this category, or are they round numbers nobody argued about?"
  Equal weights are a decision not to decide.
- **The hidden failing dimension:** "Is any single criterion failing even if the
  overall grade is fine — and does that dimension have an owned corrective-action
  plan?" A good average can mask a Quality or Compliance score of 2.
- **Consequence:** "When this vendor breaches or scores badly, what actually
  happens — a corrective-action plan, an escalation, a credit, or nothing?"
  Numbers with no consequence attached train everyone to ignore them.
