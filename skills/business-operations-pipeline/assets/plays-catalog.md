# Plays Catalog — business-operations-pipeline

The canonical source is `scripts/play_selector.py` (`--list`). This is the
human-readable mirror. Each play is a slice of the value chain:
`diagnose → decide → govern → document → communicate`.

## fix-a-slow-process
**process-mapper → capacity-planner → knowledge-ops → internal-comms**
Diagnose the flow and the constraint, decide whether it is a staffing problem,
document the fix as an SOP, announce the change. Use when the complaint is
"this takes too long / we have a backlog."

## onboard-a-vendor
**vendor-management → process-mapper → knowledge-ops → internal-comms**
Risk-assess and scorecard the vendor, map the onboarding/integration process,
write the runbook, communicate go-live. Use when bringing on a new supplier.

## cut-spend
**procurement-optimizer → vendor-management → internal-comms**
Categorize and ABC the spend, find consolidation opportunities, govern the
surviving suppliers with SLAs and scorecards, communicate the sourcing change.
Use when the goal is "spend less across many suppliers."

## scale-support
**capacity-planner → process-mapper → knowledge-ops → internal-comms**
Size staffing for demand with queueing math, streamline the flow so capacity is
used well, document SOPs/runbooks, communicate the staffing/process change. Use
when "we're drowning in volume."

## standardize-operations
**process-mapper → knowledge-ops → internal-comms**
Map the as-is, author the SOP/runbook, roll out via ADKAR/Kotter comms. Use
when work is inconsistent and lives as tribal knowledge.

## full-ops-review
**process-mapper → capacity-planner → procurement-optimizer → vendor-management → knowledge-ops → internal-comms**
The full value chain. Use for an end-to-end operations overhaul. Expensive —
grill hard before running it.

## custom
Pass an explicit `skills` list; the selector orders it along the value chain.
Use when none of the named plays fit the engagement.
