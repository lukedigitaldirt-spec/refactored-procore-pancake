# BizOps Commercial Expansion Plan

> Implementation spec for the `business-operations-skills` plugin (v2.10.0).
> Build pattern: **Path B (direct conversion)** — the orchestrator skill uses
> `context: fork` to route an inquiry to ONE sub-skill; the pipeline runner
> uses `context: fork` to chain SEVERAL sub-skills as a named play.

## 1. Positioning

The `business-operations` suite covers the **internal operating system** of a
company: how work flows, how vendors are governed, how support/ops capacity is
staffed, how change is communicated, how institutional knowledge is captured,
and how spend is categorized and consolidated.

It is deliberately **distinct** from adjacent suites:

| Suite | Owns | Does NOT own |
|-------|------|--------------|
| `business-operations` (this) | Internal process, vendor governance, capacity, change comms, SOPs, procurement | External selling, executive strategy |
| `business-growth` | External sales motion: CSM, sales engineering, RevOps, contracts | Internal ops |
| `c-level-advisor` | Strategic executive judgment | Operational tactics |
| `engineering/slo-architect` | System reliability | Business-process reliability |

## 2. Skill roster

| Skill | Sprint | `context: fork` | Frameworks | Tools |
|-------|--------|-----------------|-----------|-------|
| `business-operations-skills` (orchestrator) | 1 | yes | Grill-with-docs routing to ONE skill | 0 |
| `business-operations-pipeline` (runner) | 3 | yes | Named plays; value-chain sequencing of MANY skills | 1 |
| `process-mapper` | 1 | no | BPMN 2.0, Theory of Constraints, cycle-time | 3 |
| `vendor-management` | 1 | no | SLA/SLO, Kraljic risk matrix, weighted scorecard | 3 |
| `capacity-planner` | 2 | no | Erlang-C queueing, occupancy, shrinkage | 3 |
| `internal-comms` | 2 | no | ADKAR, Kotter 8-step | 3 |
| `knowledge-ops` | 2 | yes | 5W2H, SOP + runbook authoring | 3 |
| `procurement-optimizer` | 2 | no | UNSPSC taxonomy, spend cube, consolidation | 3 |

Total: **19 stdlib-only Python tools**, **26+ reference docs** (each citing
>=7 authoritative sources), and **asset templates per skill**.

## 3. Non-negotiable build conventions

1. **stdlib-only Python.** No third-party imports in any `scripts/*.py`. Every
   tool is both importable (pure functions) and runnable as a CLI with
   `argparse` and `--help`. Each tool accepts `--json` for machine output.
2. **flake8-clean.** Passes `flake8 --select=E9,F63,F7,F82` (syntax +
   undefined names) with zero findings. Line length <=127.
3. **Tested.** Every tool has pytest coverage under `tests/` so CI stays green.
4. **Grill discipline.** Every `SKILL.md` ends with a **Forcing-question
   library** — the Matt Pocock "grill the user with the docs open" pattern.
5. **Citations.** Every reference doc lists >=7 authoritative sources.

## 4. Directory contract (per sub-skill)

```
skills/<name>/
  SKILL.md                 # frontmatter + methodology + tool usage + grill library
  scripts/*.py             # stdlib-only tools (importable + CLI)
  references/*.md           # >=1 reference doc, each with >=7 sources
  assets/*                 # copy-paste templates
```

## 5. Orchestrator vs. pipeline

- **Orchestrator (`business-operations-skills`)** classifies an inbound request
  into exactly ONE sub-skill and hands off. Routing analysis runs in a forked
  context; only the verdict returns.
- **Pipeline (`business-operations-pipeline`)** selects a **named play** — a
  predefined ordered sequence of sub-skills for a common goal (e.g.
  `fix-a-slow-process`) — and runs each sub-skill in turn via `context: fork`,
  carrying each step's conclusion forward in an engagement packet. If no named
  play matches, it derives a custom order from the operations value chain
  (diagnose → decide → govern → document → communicate).
