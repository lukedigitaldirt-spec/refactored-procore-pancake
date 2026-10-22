# SLA / SLO Management — targets, error budgets, and service credits

The contract-facing and engineering-facing views of reliability must line up.
This is the theory behind `scripts/sla_calculator.py`.

## The vocabulary (keep these distinct)
- **SLI (indicator):** a measured quantity — e.g. the fraction of successful
  requests, or minutes available in a month.
- **SLO (objective):** the internal target for an SLI — e.g. 99.9% availability.
  Set it *below* what you believe you can achieve, with headroom.
- **SLA (agreement):** the external, contractual promise, usually looser than
  the SLO, with financial consequences (service credits) when missed.
- **Error budget:** `1 - SLO`. At 99.9% monthly, the budget is ~43.2 minutes of
  allowed downtime. Spend it on change velocity; stop changing when it runs out.

## The "nines" and why the period matters
Availability percentages only mean something against a stated window. The same
99.9% target allows very different absolute downtime per period:

| Target | per 30-day month | per year |
|--------|------------------|----------|
| 99%    | ~7.2 hours       | ~3.65 days |
| 99.9%  | ~43.2 minutes    | ~8.77 hours |
| 99.95% | ~21.6 minutes    | ~4.38 hours |
| 99.99% | ~4.32 minutes    | ~52.6 minutes |

Always agree the measurement period, what counts as "down", and who measures it
*before* signing — ambiguity here is the single most common SLA dispute.

## Error-budget policy
The budget is a control loop, not a trophy:
- Budget remaining ⇒ ship features, take calculated risks.
- Budget exhausted ⇒ freeze risky changes, redirect effort to reliability until
  the service re-earns headroom.
This converts an adversarial "dev vs ops" argument into a shared number.

## Service credits
SLAs usually define tiered credits: the further below target the service falls,
the larger the credit (as a percentage of fees). Credits are a *floor* on
accountability, not real compensation for business impact — treat a breach as a
signal to fix the system, not a line item. The calculator applies the worst
(largest) tier the service fell below.

## Reporting discipline
- Measure from the customer's vantage point, not the server's uptime counter.
- Distinguish partial degradation from hard outage; decide up front whether
  "slow" counts against the SLO.
- Exclude only *contractually agreed* maintenance windows, and name them.
- Report the trend, not just the month: three green months after a red one is a
  different story from a service degrading each quarter.

## Authoritative sources
1. Betsy Beyer, Chris Jones, Jennifer Petoff & Niall Richard Murphy (eds.),
   *Site Reliability Engineering: How Google Runs Production Systems*, O'Reilly,
   2016 (SLIs/SLOs and error budgets).
2. Betsy Beyer et al., *The Site Reliability Workbook*, O'Reilly, 2018
   (implementing SLOs and error-budget policy).
3. Alex Hidalgo, *Implementing Service Level Objectives*, O'Reilly, 2020.
4. ISO/IEC 20000-1:2018, *Information technology — Service management — Part 1:
   Service management system requirements*.
5. AXELOS, *ITIL 4: Create, Deliver and Support* (service level management
   practice), 2019.
6. ITIL Foundation, *ITIL 4 Edition*, AXELOS, 2019 (service level management).
7. Naomi Karten, *Establishing Service Level Agreements*, 2004.
8. Uptime Institute, *Tier Classification System* (availability and downtime
   benchmarking), Uptime Institute LLC.
9. Google Cloud, *Compute Engine Service Level Agreement (SLA)* (worked example
   of tiered monthly service credits).
