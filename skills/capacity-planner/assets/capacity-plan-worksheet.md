# Capacity Plan Worksheet — <queue / team name>

> Fill this in from a real demand forecast, not a daily average. Plan at the
> interval level; a day that averages fine can still miss service level at the
> lunchtime peak.

## Service target (fix this FIRST)
- **Service level:** __% of contacts answered within __ seconds (e.g. 80/20)
- **Max occupancy:** __% (plan cap, typically 80-88%)
- **Channel:** <phone / chat / ticket / dispatch>
- **Why this target:** <cost of missing it; customer tolerance for waiting>

## Demand forecast (per interval)
| Interval | Contact volume | AHT (sec) | Offered load A | Notes |
|----------|----------------|-----------|----------------|-------|
| 09:00-09:30 |             |           |                |       |
| 09:30-10:00 |             |           |                |       |
| 12:00-12:30 (peak) |      |           |                |       |

## Agents on the floor (from erlang_c.py --required-agents)
| Interval | A | Required agents | Service level | Occupancy | ASA (sec) |
|----------|---|-----------------|---------------|-----------|-----------|
|          |   |                 |               |           |           |

## Queue dynamics check (from queue_metrics.py)
- Arrival rate λ: __  Service rate μ (per agent): __  Servers c: __
- Utilization ρ: __  (must be < 1)  Prob. of wait: __%
- Wq (time in queue): __  L (in system): __  Stable? __

## FTE requirement (from staffing_requirements.py)
- Contact volume (period): __  AHT: __  Paid hours/FTE: __
- Occupancy cap: __%  Shrinkage: __%
- Productive hours needed: __  Base FTE: __  **Required FTE: __ (round up: __)**

## Assumptions to re-check when demand moves
| Assumption | Current value | Source | Last validated |
|------------|---------------|--------|----------------|
| Volume forecast |          |        |                |
| AHT             |          |        |                |
| Shrinkage       |          |        |                |
| Occupancy cap   |          |        |                |

## Decision summary (hand to the owner)
- Plan delivers: __% service level at __% occupancy.
- Cost of +1 / -1 agent at the margin: <service-level delta>
- Recommended roster: __ FTE across __ shifts.
