# Theory of Constraints — the five focusing steps

Theory of Constraints (TOC), from Eliyahu Goldratt's *The Goal*, states that
every system's output is limited by a single constraint (bottleneck). Improving
anything other than the constraint yields no system-level gain. This is the
logic behind `scripts/bottleneck_detector.py`.

## The core claim
System throughput = the constraint's capacity. A chain is only as strong as its
weakest link; strengthening other links adds weight, not strength. Upstream
steps faster than the constraint merely pile up inventory; downstream steps
starve.

## The five focusing steps
1. **Identify** the constraint — the step with the lowest effective capacity
   relative to demand.
2. **Exploit** it — wring maximum output from the constraint as-is: never let it
   idle, never feed it defects, offload non-essential work. (Free.)
3. **Subordinate** everything else to the constraint — pace the whole line to
   the constraint (drum-buffer-rope); stop over-producing upstream.
4. **Elevate** the constraint — only now spend money/resources: add capacity,
   parallelize, automate the bottleneck step.
5. **Repeat** — once elevated, the constraint moves. Go back to step 1. Do not
   let inertia become the new constraint.

## Why "balance flow, not capacity"
Local efficiency metrics (keep every worker 100% busy) actively harm the
system: they inflate WIP everywhere except the constraint and lengthen lead
time. Only the constraint should run near 100%; non-constraints *should* have
idle time — that slack is what protects flow.

## Buffers
Place a **time buffer** immediately before the constraint so it never starves
from upstream variability. Protecting the constraint's uptime is worth more
than any local optimization elsewhere.

## Applying it with the tool
- Feed per-step capacities (units/period). The detector returns the constraint,
  system throughput, and per-step utilization.
- Pass `--demand` to test whether the constraint can meet required output and to
  size the throughput gap you must elevate.
- After elevating, re-run: the constraint will have moved.

## Authoritative sources
1. Eliyahu M. Goldratt & Jeff Cox, *The Goal*, 3rd rev. ed., North River Press,
   2004.
2. Eliyahu M. Goldratt, *Theory of Constraints*, North River Press, 1990.
3. Eliyahu M. Goldratt, *It's Not Luck*, North River Press, 1994.
4. William Dettmer, *Goldratt's Theory of Constraints: A Systems Approach to
   Continuous Improvement*, ASQ Quality Press, 1997.
5. John Ricketts, *Reaching the Goal: How Managers Improve a Services Business
   Using Goldratt's Theory of Constraints*, IBM Press, 2007.
6. Mabin & Balderstone, "The performance of the theory of constraints
   methodology," *International Journal of Operations & Production Management*,
   2003.
7. James F. Cox & John Schleier (eds.), *Theory of Constraints Handbook*,
   McGraw-Hill, 2010.
8. Wallace J. Hopp & Mark L. Spearman, *Factory Physics*, 3rd ed., Waveland
   Press, 2011 (constraints and variability).
