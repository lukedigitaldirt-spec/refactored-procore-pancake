---
name: business-operations-pipeline
description: >-
  Run an end-to-end operations engagement by chaining several business-
  operations sub-skills in sequence. Use when a request needs MORE THAN ONE of
  process-mapper, capacity-planner, procurement-optimizer, vendor-management,
  knowledge-ops, or internal-comms run in order - e.g. "map our onboarding,
  document it, and announce it", "we're drowning in tickets: figure out
  staffing, fix the flow, write the SOP and tell the team", "consolidate
  suppliers then renegotiate governance", or "do a full operations review".
  Selects a named play (a predefined ordered sequence) and runs each sub-skill
  via context: fork, carrying each step's output into the next. Runs with
  context: fork itself. For a request that needs only ONE sub-skill, use the
  business-operations-skills orchestrator instead. NOT for external sales
  (business-growth) or executive strategy (c-level-advisor).
context: fork
---

# Business Operations — Pipeline Runner

You chain the suite's sub-skills into **one end-to-end engagement**. Where the
`business-operations-skills` orchestrator picks exactly one skill, you run a
**named play**: an ordered sequence of sub-skills, each invoked via
`context: fork`, with each step's conclusion carried forward into the next.

Because this skill runs with `context: fork`, the per-step reasoning stays out
of the parent thread; only the consolidated engagement summary returns.

## Why order matters — the operations value chain

Every play is a slice of the same backbone. Running it out of order wastes work
(you document a process you haven't fixed; you announce a change you haven't
designed):

```
diagnose ─▶ decide ─▶ govern ─▶ document ─▶ communicate
(map the   (size      (SLAs,     (SOPs,      (ADKAR/
 flow,      staffing,  vendor     runbooks)   Kotter,
 find the   consolidate risk)                 stakeholders)
 constraint) spend)
```

| Stage | Skill(s) | Produces |
|-------|----------|----------|
| diagnose | `process-mapper` | process map, PCE, the constraint |
| decide — size | `capacity-planner` | staffing/FTE, service level |
| decide — source | `procurement-optimizer` | spend categorization, consolidation |
| govern | `vendor-management` | SLA/risk/scorecard |
| document | `knowledge-ops` | SOP / runbook |
| communicate | `internal-comms` | ADKAR/Kotter/stakeholder comms plan |

## Named plays

`scripts/play_selector.py` is the single source of truth for the sequences.
Run `--list` to see them. The catalog:

| Play | Sequence |
|------|----------|
| `fix-a-slow-process` | process-mapper → capacity-planner → knowledge-ops → internal-comms |
| `onboard-a-vendor` | vendor-management → process-mapper → knowledge-ops → internal-comms |
| `cut-spend` | procurement-optimizer → vendor-management → internal-comms |
| `scale-support` | capacity-planner → process-mapper → knowledge-ops → internal-comms |
| `standardize-operations` | process-mapper → knowledge-ops → internal-comms |
| `full-ops-review` | process-mapper → capacity-planner → procurement-optimizer → vendor-management → knowledge-ops → internal-comms |

If no named play fits, pass an explicit `skills` list — the selector orders it
along the value chain into a **custom** play.

## Procedure

1. **Select the play.** Feed the goal (a play name), free-text + keywords, or an
   explicit skill list to `play_selector.py`. It returns the ordered sequence,
   the per-step carry-forward contract, and a confidence level.
2. **Grill before running if confidence is low** (see below). A full engagement
   is expensive; do not fan out sub-skills on a vague ask.
3. **Run each step via `context: fork`.** Invoke the step's sub-skill, passing
   the **engagement packet** (the goal plus every prior step's conclusion). Let
   that sub-skill do its own grilling and tool runs; capture only its
   conclusion back into the packet.
4. **Gate between steps.** If a step surfaces a blocker (e.g. process-mapper
   finds times were never measured), stop and report rather than feeding
   fabricated inputs downstream. A broken early stage invalidates the rest.
5. **Return the consolidated summary** — one section per stage: what it
   concluded, the decision it drove, and the artifact it produced — plus the
   single recommended next action.

## Using the tool

```bash
# List the named plays
python scripts/play_selector.py --list

# Resolve a goal by name
python scripts/play_selector.py --goal fix-a-slow-process

# Resolve by free text + keywords
python scripts/play_selector.py --goal "we're drowning in tickets" --keyword staffing

# Build a custom play from an explicit skill set (ordered along the value chain)
python scripts/play_selector.py --skill internal-comms --skill process-mapper --json

# Or pass a JSON goal file / stdin
echo '{"goal":"consolidate suppliers then renegotiate"}' | python scripts/play_selector.py -
```

See `assets/engagement-packet.template.json` for the carry-forward schema and
`assets/plays-catalog.md` for the human-readable catalog.

## Reference library

- `references/orchestration-and-plays.md` — playbooks, pipeline composition,
  the fork-and-carry-forward pattern.
- `references/engagement-sequencing.md` — the operations value chain and why
  diagnose-before-communicate ordering is non-negotiable.

## Forcing-question library (grill-with-docs)

A pipeline multiplies the cost of a vague brief across every stage. Grill
before you fan out.

- **Scope of the engagement:** "Is this genuinely a multi-step engagement, or
  one question? If one, I'll route you to a single skill instead."
- **The decision at the end:** "When all stages are done, what decision or
  deliverable are you left holding? Name it now so each stage aims at it."
- **Entry stage:** "Do you already know the process/numbers (skip diagnose), or
  are we starting from 'something's wrong and we don't know what'?"
- **Stop conditions:** "If stage one finds the premise is wrong — e.g. the
  process is fine but demand doubled — do you want me to stop and re-plan, or
  push through the whole play?"
- **Inputs per stage:** "Do you have the inputs each stage needs (step times,
  spend data, SLA targets), or will some stages be running on guesses?"
- **Change readiness:** "Has the change already been decided, so the
  communicate stage is real, or are we still exploring and comms is premature?"
- **Ownership:** "Who owns the output of each stage? A play with no owner per
  stage produces artifacts nobody adopts."

Ask at most three, then select the play with a stated confidence level.
