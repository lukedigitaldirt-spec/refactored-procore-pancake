# Engagement Sequencing — the operations value chain

Why do the plays run in the order they do? Because operational improvement has
a natural dependency order. Each stage produces the input the next one needs;
invert the order and you do rework or build on sand.

## The backbone
```
diagnose ─▶ decide ─▶ govern ─▶ document ─▶ communicate
```

1. **Diagnose (process-mapper).** You cannot fix, staff, or document a process
   you have not mapped and measured. Diagnosis establishes the as-is: the flow,
   the cycle-time/PCE, and the constraint. Everything downstream references it.
2. **Decide (capacity-planner / procurement-optimizer).** With the diagnosis in
   hand, decide the intervention. Is the gap *demand vs. supply* (size staffing
   with queueing math) or *cost/fragmentation* (categorize and consolidate
   spend)? Deciding before diagnosing is guessing.
3. **Govern (vendor-management).** If third parties are in the loop, lock the
   SLAs, risk posture, and scorecard that will hold the new design accountable.
4. **Document (knowledge-ops).** Only a *settled* design is worth writing down.
   Documenting first means rewriting the SOP after every decision — waste.
5. **Communicate (internal-comms).** You announce a change that is designed,
   governed, and documented. Communicating a half-baked change manufactures
   resistance you then have to unwind.

## This is the Deming/PDCA and DMAIC logic
The ordering is not arbitrary; it tracks the canonical improvement cycles:
- **PDCA** (Plan-Do-Check-Act): diagnose and decide = Plan; document and roll
  out = Do; govern/scorecard = Check.
- **DMAIC** (Define-Measure-Analyze-Improve-Control): diagnose = Measure/
  Analyze; decide = Improve; govern + document = Control.
- **Service blueprinting** sequences front-stage/back-stage design before
  standardization and launch.

## When to skip stages
A play is a slice, not always the whole backbone. Skip a stage only when its
output already exists and is trusted:
- Numbers already measured → skip diagnose, start at decide.
- No third parties → skip govern.
- One-off, not recurring → documentation may be lightweight.
But never skip **communicate** for a change that affects how people work;
unadopted change is wasted work.

## Authoritative sources
1. W. Edwards Deming, *Out of the Crisis*, MIT Press, 1986 (PDCA/System of
   Profound Knowledge).
2. Walter A. Shewhart, *Statistical Method from the Viewpoint of Quality
   Control*, 1939 (the Shewhart cycle).
3. Michael L. George, *Lean Six Sigma*, McGraw-Hill, 2002 (DMAIC).
4. Thomas Pyzdek & Paul Keller, *The Six Sigma Handbook*, 4th ed., McGraw-Hill,
   2014.
5. G. Lynn Shostack, "Designing Services That Deliver," *Harvard Business
   Review*, 1984 (service blueprinting).
6. Mary Jo Bitner, Amy Ostrom, Felicia Morgan, "Service Blueprinting," *
   California Management Review*, 2008.
7. Marlon Dumas et al., *Fundamentals of Business Process Management*, 2nd ed.,
   Springer, 2018 (the BPM lifecycle: identify → model → analyze → redesign →
   implement → monitor).
8. H. James Harrington, *Business Process Improvement*, McGraw-Hill, 1991.
