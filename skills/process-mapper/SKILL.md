---
name: process-mapper
description: >-
  Map and diagnose business processes. Use when someone needs to document a
  workflow, draw an as-is/to-be map, model a process in BPMN, find where work
  stalls, or compute cycle time, lead time, process cycle efficiency, or takt
  time. Triggers: "map this process", "workflow", "BPMN", "swimlane",
  "handoff", "bottleneck", "constraint", "cycle time", "lead time", "process
  efficiency", "why is this so slow". Ships three stdlib-only tools
  (cycle_time_analyzer, bottleneck_detector, bpmn_validator). NOT for staffing
  math (use capacity-planner) or documenting a finished process as an SOP (use
  knowledge-ops).
---

# Process Mapper

Turn a fuzzy "this process is painful" into a **structured map, a validated
model, and hard numbers** about where time and throughput are lost. Three
lenses, three tools:

| Lens | Question it answers | Tool |
|------|--------------------|------|
| **Flow correctness** | Is the process model actually well-formed? | `scripts/bpmn_validator.py` |
| **Time** | Where does elapsed time go? How efficient is the flow? | `scripts/cycle_time_analyzer.py` |
| **Throughput** | Which single step caps our output? | `scripts/bottleneck_detector.py` |

## Method (as-is → analyze → to-be)

1. **Capture the as-is.** List every step in order, who owns it, and — for each
   step — the **process time** (hands-on touch time) and the **wait time**
   (queue/handoff/idle before it starts). Vague memory is not data; if the user
   hasn't measured, say so and grill (below).
2. **Model it.** Express the flow as a BPMN-lite graph (start event → tasks →
   gateways → end event) and validate structure with `bpmn_validator.py`. A map
   that doesn't validate is a map you can't trust.
3. **Quantify time.** Run `cycle_time_analyzer.py` to get lead time, process
   time, and **Process Cycle Efficiency (PCE = process_time / lead_time)**. In
   most office processes PCE is under 25% — meaning >75% of elapsed time is
   pure waiting. That reframes the fix from "work faster" to "kill the queues."
4. **Find the constraint.** Run `bottleneck_detector.py` (Theory of
   Constraints). System throughput equals the slowest step's capacity — nothing
   upstream or downstream matters until you elevate that one step.
5. **Design the to-be.** Attack in order: remove wait/handoffs first (biggest
   PCE lever), then elevate the constraint, then eliminate non-value-add tasks.
   Re-run the tools on the proposed design to prove the gain numerically.

## Using the tools

All tools are stdlib-only, take a JSON file (or `-` for stdin), and support
`--json` for machine output.

```bash
# Time analysis (optionally takt time with --available-time / --demand)
python scripts/cycle_time_analyzer.py steps.json
python scripts/cycle_time_analyzer.py steps.json --available-time 480 --demand 60

# Throughput / constraint (optionally --demand to test if you meet it)
python scripts/bottleneck_detector.py capacities.json --demand 50

# Structural validation of a BPMN-lite model
python scripts/bpmn_validator.py model.json --strict
```

See `assets/` for ready-to-fill input templates and a swimlane worksheet.

## Reference library

- `references/bpmn-notation-guide.md` — BPMN 2.0 elements you actually need.
- `references/cycle-time-metrics.md` — lead time, PCE, takt, Little's Law.
- `references/theory-of-constraints.md` — the five focusing steps.
- `references/value-stream-mapping.md` — VSM symbols and the as-is/to-be loop.

## Forcing-question library (grill-with-docs)

Do not draw a map or run a number until these are answered. If the user can't
answer, that gap *is* the finding.

- **Boundaries:** "What is the exact trigger that *starts* this process, and
  what event marks it *done*?" A process without crisp start/end events cannot
  be mapped or measured.
- **Measured vs. guessed:** "Are your step times measured, or estimated? If
  estimated, by whom and how recently?" PCE built on guesses is theater.
- **Process vs. wait:** "For each step, how long is someone *actually working*
  versus how long it *sits waiting*?" Conflating the two hides the real problem
  — wait time is usually the villain.
- **The one constraint:** "If you could only speed up one step, which is it —
  and do you have the capacity numbers to prove that's the constraint, not just
  the loudest complaint?"
- **Demand:** "How many units per period must this process deliver?" Without
  demand you cannot say whether the constraint is even a problem.
- **Rework loops:** "Where does work bounce back? What percent fails inspection
  or gets kicked back?" Hidden rework loops destroy both PCE and throughput.
- **As-is honesty:** "Are we mapping how it *should* work or how it *actually*
  works today, including the workarounds?" Map reality first, always.
