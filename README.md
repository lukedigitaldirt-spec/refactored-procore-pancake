# business-operations-skills

A Claude Code plugin: **6 BizOps skills + an orchestrator + a pipeline runner**
for the internal operating system of a company — how work flows, how vendors
are governed, how ops capacity is staffed, how change is communicated, how
know-how is captured, and how spend is categorized and consolidated.

> Distinct from `business-growth` (external sales) and `c-level-advisor`
> (strategic executive judgment). This suite is **operational**.

## Skills

| Skill | What it does | Frameworks | Tools |
|-------|--------------|-----------|-------|
| **business-operations-skills** | Orchestrator — routes a request to the ONE right sub-skill (`context: fork`) | Grill-with-docs routing | — |
| **business-operations-pipeline** | Pipeline runner — chains SEVERAL sub-skills as a named "play" (`context: fork`) | Named plays, value-chain sequencing | 1 |
| **process-mapper** | Map & diagnose workflows; find bottlenecks; compute cycle time | BPMN 2.0, Theory of Constraints, cycle-time/PCE | 3 |
| **vendor-management** | Govern third parties: SLAs, risk, scorecards | SLA/SLO, Kraljic matrix, weighted scorecard | 3 |
| **capacity-planner** | Staff ops teams to meet demand | Erlang-C queueing, occupancy, shrinkage | 3 |
| **internal-comms** | Communicate & land change | ADKAR, Kotter 8-step | 3 |
| **knowledge-ops** | Author SOPs & runbooks (`context: fork`) | 5W2H, SOP/runbook standards | 3 |
| **procurement-optimizer** | Categorize & consolidate spend | UNSPSC taxonomy, spend cube, ABC/Pareto | 3 |

**19 stdlib-only Python tools · 26+ reference docs (each citing >=7 authoritative
sources) · asset templates per skill.**

## Orchestrator vs. pipeline

- Use **business-operations-skills** when a request maps to **one** specialist.
- Use **business-operations-pipeline** when a request needs **several**
  specialists run in order — it selects a named play (e.g. `fix-a-slow-process`,
  `onboard-a-vendor`, `cut-spend`, `full-ops-review`) and runs each sub-skill
  via `context: fork`, carrying each step's conclusion into the next along the
  value chain `diagnose → decide → govern → document → communicate`.

## Layout

```
.claude-plugin/plugin.json          # plugin manifest (v2.10.0)
documentation/implementation/       # build spec
skills/<name>/
  SKILL.md                          # methodology + tool usage + grill library
  scripts/*.py                      # stdlib-only tools (importable + CLI)
  references/*.md                   # cited reference docs
  assets/*                          # copy-paste templates
tests/                              # pytest coverage for every tool
```

## Using a tool

Every tool is stdlib-only, importable, and runnable as a CLI. It reads a JSON
file (or `-` for stdin) and supports `--json` for machine output:

```bash
python skills/process-mapper/scripts/cycle_time_analyzer.py \
  skills/process-mapper/assets/steps.template.json

python skills/business-operations-pipeline/scripts/play_selector.py --list
```

## Development

```bash
python -m pip install pytest flake8
python -m pytest -q                                          # all tool tests
flake8 skills --select=E9,F63,F7,F82 --max-line-length=127   # syntax gate
```

Design conventions live in
`documentation/implementation/bizops-commercial-expansion-plan.md`: stdlib-only
Python, flake8-clean, tested, every `SKILL.md` ends with a Forcing-question
library (Matt Pocock grill-with-docs discipline), and every reference doc cites
>=7 authoritative sources.

## License

MIT (c) Alireza Rezvani
