# Cycle-Time Metrics — lead time, PCE, takt, and Little's Law

The timing vocabulary of lean/BPM is small but people routinely conflate the
terms. Precise definitions, matched to `scripts/cycle_time_analyzer.py`.

## Core definitions
- **Process time (touch time):** time someone is actively working the item.
- **Wait time:** time the item sits in a queue or handoff, no one touching it.
- **Cycle time / lead time (elapsed):** total wall-clock from item entering a
  step (or the whole process) until it exits = process time + wait time.
  In lean usage "lead time" is often reserved for the whole value stream and
  "cycle time" for a single step; the analyzer reports the total either way.
- **Process Cycle Efficiency (PCE):** `process_time / lead_time`. The single
  most revealing office-process number. World-class knowledge work rarely
  exceeds 25%; many processes sit at 1-5%, i.e. 95-99% pure waiting.
- **Takt time:** `available_time / customer_demand`. The heartbeat — the pace
  at which you must complete one unit to meet demand. If cycle time > takt time,
  you cannot keep up without more capacity or a faster process.

## Little's Law
`WIP = throughput × lead_time` (equivalently `lead_time = WIP / throughput`).
The most important operational identity. Consequences:
- Cutting **work-in-progress** cuts lead time proportionally at fixed
  throughput — the cheapest lever, no new resources needed.
- You cannot cut lead time by "trying harder"; you must cut WIP or raise
  throughput.

## How to attack a slow process (in order)
1. **Wait time first.** If PCE < 25%, the problem is queues and handoffs, not
   worker speed. Reduce batch sizes, remove approval layers, co-locate handoffs.
2. **WIP limits.** Apply Little's Law — cap concurrent items to pull lead time
   down.
3. **Touch time last.** Only after waiting is minimized does shaving process
   time matter.

## Measurement discipline
- Time-stamp items at each step entry/exit; do not rely on recall.
- Separate value-add from non-value-add explicitly per step.
- Distinguish typical from tail: report median and P90, not just the mean —
  processes are usually right-skewed.

## Authoritative sources
1. James P. Womack & Daniel T. Jones, *Lean Thinking*, Free Press, 2003.
2. Mike Rother & John Shook, *Learning to See*, Lean Enterprise Institute,
   1999 (value-stream timing and PCE).
3. John D. C. Little, "A Proof for the Queuing Formula L = λW," *Operations
   Research*, 1961.
4. Donald G. Reinertsen, *The Principles of Product Development Flow*, Celeritas,
   2009 (queueing and WIP economics).
5. Taiichi Ohno, *Toyota Production System*, Productivity Press, 1988 (takt
   time origins).
6. Daniel T. Jones & James P. Womack, *Seeing the Whole Value Stream*, LEI,
   2011.
7. George Eckes, *The Six Sigma Revolution*, Wiley, 2001 (process cycle
   efficiency in DMAIC).
8. Michael L. George, *Lean Six Sigma*, McGraw-Hill, 2002 (PCE benchmarks).
