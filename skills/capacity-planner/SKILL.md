---
name: capacity-planner
description: >-
  Size staffing and queues from demand. Use when someone asks how many agents,
  reps, or FTE they need, how to hit a service level, why wait times or hold
  times are bad, or how occupancy and shrinkage change headcount. Triggers:
  "how many agents", "staffing", "headcount", "FTE", "queue", "wait time",
  "hold time", "Erlang", "Erlang-C", "occupancy", "shrinkage", "service level",
  "ASA", "ticket volume", "call volume", "contact center", "overstaffed",
  "understaffed". Ships three stdlib-only tools (erlang_c,
  staffing_requirements, queue_metrics). NOT for mapping the process itself
  (use process-mapper) or governing vendors (use vendor-management).
---

# Capacity Planner

Turn "we're drowning / we're overstaffed" into a **defensible headcount with the
service level it buys**. The number of agents is an *output* of a service
target, never a guess. Three lenses, three tools:

| Lens | Question it answers | Tool |
|------|--------------------|------|
| **Service** | With N agents, what fraction wait, and for how long? | `scripts/erlang_c.py` |
| **Dynamics** | How long is the queue and WIP at this load? Is it stable? | `scripts/queue_metrics.py` |
| **Headcount** | How many FTE must we hire once shrinkage is counted? | `scripts/staffing_requirements.py` |

## Method (target → size → gross up)

1. **Fix the service target first.** Service level is always a pair — X% of
   contacts answered within Y seconds (e.g. 80/20) — plus an occupancy cap. A
   bare percentage with no time window is not a target. The headcount falls out
   of this; it is not an input.
2. **Forecast demand per interval.** Volume *and* average handle time, at the
   15- or 30-minute level. Never a daily average — the Erlang curve is
   non-linear, so averaging under-staffs the peak and over-staffs the trough.
3. **Size the queue (Erlang-C).** Convert volume and AHT to offered load A and
   find the agents-on-the-floor needed to hit the target. The payoff of the last
   agent near the knee is large (24→25 agents can lift SL from ~81% to ~88%).
4. **Check the dynamics (M/M/c).** Confirm the system is stable (`rho < 1`) and
   that wait time and WIP are tolerable. Little's Law (`L = λW`) ties it
   together and catches arithmetic errors.
5. **Gross up to headcount (WFM).** Apply the occupancy cap and shrinkage to
   turn floor requirement into FTE to hire. Divide by `(1 - shrinkage)` — never
   multiply by `(1 + shrinkage)`. State every assumption so the plan re-runs
   when demand moves.

## Using the tools

All tools are stdlib-only, take a JSON file (or `-` for stdin), and support
`--json` for machine output.

```bash
# Erlang-C: metrics for a given team size
python scripts/erlang_c.py assets/erlang-input.template.json

# Erlang-C: smallest team meeting a target service level
python scripts/erlang_c.py assets/erlang-input.template.json --required-agents

# M/M/c queue dynamics (wait, WIP, utilization, stability)
python scripts/queue_metrics.py assets/queue-input.template.json

# Workload -> FTE with occupancy cap and shrinkage
python scripts/staffing_requirements.py assets/staffing-input.template.json
```

See `assets/` for ready-to-fill input templates and a capacity-plan worksheet.

## Reference library

- `references/erlang-c-queueing.md` — offered load, the stable Erlang-B/C
  recursion, service level, ASA, occupancy; assumptions and where they break.
- `references/workforce-management-and-shrinkage.md` — the FTE pipeline,
  occupancy cap, shrinkage, and the grossing-up traps.
- `references/service-level-and-occupancy.md` — defining the target, the
  occupancy trade-off, and economies of scale from pooling.
- `references/capacity-planning-method.md` — the full demand-to-roster pipeline
  and the peak-vs-average rule.

## Forcing-question library (grill-with-docs)

Do not quote a headcount until these are answered. If the user can't answer,
that gap *is* the finding.

- **The target:** "What is your service level — the percentage *and* the answer
  time (e.g. 80% within 20s) — and your occupancy cap?" Without a two-part
  target there is no number to compute toward.
- **Measured vs. guessed:** "Is your average handle time measured from real
  data, or estimated? AHT drives offered load linearly — a 20% AHT error is a
  20% staffing error."
- **Interval, not average:** "Do you have demand by 15- or 30-minute interval,
  or only a daily total? Staffing to the daily average will miss every peak."
- **Shrinkage:** "What is your shrinkage, and what's in it — breaks, training,
  leave, sick, admin? If you don't know it, your FTE number is fiction."
- **Occupancy reality:** "What occupancy are you running today? Above ~90%
  sustained, service collapses on any spike and agents quit — more bodies may be
  cheaper than the attrition."
- **Abandonment:** "Do callers abandon, and at what point? Erlang-C assumes
  infinite patience and over-staffs; heavy abandonment means you need Erlang-A."
- **Pooling:** "Are these one pool or several skill silos? Fragmented queues
  need far more agents for the same service level than one pooled queue would."
