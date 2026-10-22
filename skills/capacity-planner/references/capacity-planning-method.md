# Capacity-Planning Method — from demand forecast to roster

A defensible staffing plan is a short pipeline, each stage feeding the next.
Skipping a stage is how teams end up either drowning or over-staffed. This note
ties the three tools together into one method.

## The pipeline
1. **Forecast demand per interval.** Capacity is planned at the interval level
   (typically 15 or 30 minutes), never as a daily average — a day that averages
   fine can still have a lunchtime peak that blows service level. Forecast
   volume *and* average handle time; both move.
2. **Size the queue per interval (Erlang-C).** For each interval, convert volume
   and AHT into offered load and find the agents needed to hit the service
   target. Run `erlang_c.py` with `--required-agents` against your target
   service level. The result is an **agents-on-the-floor** curve across the day.
3. **Model the queue dynamics (M/M/c).** Use `queue_metrics.py` to sanity-check
   wait time, work-in-progress, and utilization at the chosen staffing — and to
   confirm the system is stable (`rho < 1`). Little's Law (`L = λW`) links the
   numbers and catches arithmetic errors.
4. **Gross up to headcount (WFM).** Convert the floor requirement into FTE with
   `staffing_requirements.py`, applying the occupancy cap and shrinkage. This is
   the number you actually hire and roster.
5. **Schedule and reconcile.** Fit real shifts to the interval curve, then
   compare planned vs. actual service level and re-forecast. Capacity planning
   is a loop, not a one-shot calculation.

## Peak vs. average — the cardinal rule
Staff to the **peak intervals** that matter, not the daily mean. Because the
Erlang curve is non-linear, averaging demand across the day systematically
under-staffs the peaks and over-staffs the troughs. Plan each interval on its
own load, then build shifts that approximate the resulting curve.

## Variability is the enemy, not just volume
Two queues with identical average load behave very differently if one has
bursty arrivals or highly variable handle times. Higher variability means longer
queues at the same utilization (the core result of `Factory Physics`). Reduce
variability — smoother arrivals, consistent AHT, fewer skill silos — before
adding bodies.

## Pooling and skill design
Combine queues wherever skills allow: pooled servers hit the same service level
with fewer agents (economies of scale). Over-fragmented skill-based routing
recreates many tiny, inefficient queues. Design the fewest pools that the work
genuinely requires.

## What to hand the decision-maker
- The agents-on-the-floor curve by interval (Erlang-C).
- Required FTE with the occupancy cap and shrinkage stated explicitly (WFM).
- The service level and occupancy the plan delivers, and the cost of one agent
  more or fewer at the margin.
- The forecast assumptions, so the plan can be re-run when demand moves.

## Authoritative sources
1. Brad Cleveland, *Call Center Management on Fast Forward*, 3rd ed., ICMI
   Press, 2012.
2. Noah Gans, Ger Koole & Avishai Mandelbaum, "Telephone Call Centers: Tutorial,
   Review, and Research Prospects," *M&SOM*, 2003.
3. Wallace J. Hopp & Mark L. Spearman, *Factory Physics*, 3rd ed., Waveland
   Press, 2011 (variability and capacity).
4. Donald Gross, John Shortle, James Thompson & Carl Harris, *Fundamentals of
   Queueing Theory*, 4th ed., Wiley, 2008.
5. Sem Borst, Avishai Mandelbaum & Martin Reiman, "Dimensioning Large Call
   Centers," *Operations Research*, 2004.
6. Richard B. Chase & F. Robert Jacobs, *Operations and Supply Chain
   Management*, 15th ed., McGraw-Hill, 2017.
7. Ger Koole, *Call Center Optimization*, MG Books, 2013.
8. John D. C. Little, "A Proof for the Queuing Formula L = λW," *Operations
   Research*, 1961.
