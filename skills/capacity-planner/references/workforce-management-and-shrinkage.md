# Workforce Management — shrinkage, occupancy, and FTE math

Erlang-C tells you how many agents must be *on the floor* in a given interval.
Workforce management (WFM) translates that into how many people you must
**hire and roster**, because no one is productive every paid minute. This is the
logic behind `scripts/staffing_requirements.py`.

## The two grossing-up factors

### Occupancy cap
Occupancy is the share of logged-in time an agent spends handling contacts.
You cannot plan to 100% — that leaves zero slack for arrival variability, and
service collapses at the knee of the Erlang curve. Plan to a realistic cap,
typically **80-88%**. Occupancy that runs chronically high is a leading
indicator of attrition.

### Shrinkage
Shrinkage is the share of *paid* time agents are **not** available for the work:

- **Planned:** breaks, lunch, training, coaching, team meetings, holiday/leave.
- **Unplanned:** sick time, late starts, system downtime, off-phone admin.

Typical contact-center shrinkage is **30-35%**. Measure it; do not guess. The
cardinal error is applying shrinkage to the wrong base or omitting it entirely,
which under-staffs every interval.

## The FTE pipeline
```
productive_hours_needed = contact_volume * aht_seconds / 3600
base_fte      = productive_hours_needed / (paid_hours_per_fte * occupancy_cap)
required_fte  = base_fte / (1 - shrinkage)
effective_hours_per_fte = paid_hours_per_fte * (1 - shrinkage)
```
`base_fte` is the on-the-work requirement; `required_fte` grosses it up so that
enough bodies are rostered to still cover the work after shrinkage. Divide by
`(1 - shrinkage)` — never multiply by `(1 + shrinkage)`, which understates the
need (a common and expensive mistake).

## Worked example
5,000 contacts at 300s AHT = 416.7 productive hours. At 160 paid hours/FTE and
an 85% occupancy cap, `base_fte = 416.7 / (160 * 0.85) ≈ 3.06`. At 30%
shrinkage, `required_fte = 3.06 / 0.70 ≈ 4.38` -> roster **5** FTE.

## Occupancy vs. utilization vs. productivity
These three get conflated. Keep them distinct: **occupancy** is busy time over
logged-in time; **utilization** is logged-in (productive) time over paid time
(i.e. `1 - shrinkage`); **productivity** is output per unit input. A plan can
show healthy utilization and still have crushing occupancy, or vice versa.

## Authoritative sources
1. Brad Cleveland, *Call Center Management on Fast Forward*, 3rd ed., ICMI
   Press, 2012.
2. Penny Reynolds, *The Power of One: Understanding the Economic and Workforce
   Management Value of a Single Call Center Agent*, The Call Center School,
   2010.
3. Ger Koole, *Call Center Optimization*, MG Books, 2013.
4. Noah Gans, Ger Koole & Avishai Mandelbaum, "Telephone Call Centers: Tutorial,
   Review, and Research Prospects," *M&SOM*, 2003.
5. Donald Gross, John Shortle, James Thompson & Carl Harris, *Fundamentals of
   Queueing Theory*, 4th ed., Wiley, 2008.
6. Z. Aksin, M. Armony & V. Mehrotra, "The Modern Call Center: A Multi-
   Disciplinary Perspective on Operations Management Research," *Production and
   Operations Management*, 2007.
7. SWPP (Society of Workforce Planning Professionals), *Common Metrics and
   Definitions for the Contact Center*, industry reference, 2019.
8. Richard B. Chase & F. Robert Jacobs, *Operations and Supply Chain
   Management*, 15th ed., McGraw-Hill, 2017 (service capacity planning).
