# Service Level, ASA, and Occupancy — defining the target before you staff

You cannot compute a headcount until you have fixed the **service target**. The
number of agents is an *output* of the target, not an input. This note defines
the targets `scripts/erlang_c.py` optimizes against and the traps in setting
them.

## Service level (the two-part number)
Service level is always a pair: **X% of contacts answered within Y seconds**.
"80/20" (80% within 20 seconds) is the long-standing default, but it is a choice,
not a law — nothing about queueing theory makes 80/20 special. Set Y from what
the customer actually tolerates and X from the cost of missing it.

A single percentage with no time window is meaningless. "95% service level"
without a Y is not a target.

## Average speed of answer (ASA)
ASA is the mean wait across **all** contacts (including the zero-wait ones). It
is a weaker target than service level because an average hides the tail: a good
ASA can still mask a minority of callers waiting several minutes. Report service
level as the primary target and ASA as a secondary sanity check, never ASA
alone.

## Occupancy — the hidden constraint
Occupancy = offered load / agents = `A / N`. It is the pressure gauge:

- Below ~70%: comfortable, possibly over-staffed in small teams.
- 85-90%: efficient but near the cliff.
- Above ~90% sustained: service level becomes extremely sensitive to small load
  spikes, handle time inflates (tired agents), and attrition climbs.

Occupancy and service level trade off along the same curve. You cannot
simultaneously demand 95/10 service and 95% occupancy on a small team — the math
forbids it.

## The economies of scale (pooling)
Larger pools are dramatically more efficient per agent. A team handling 4x the
load needs far less than 4x the agents for the same service level, because
random peaks and troughs average out across more servers. This is the central
argument for **pooling queues** and against fragmenting staff into many small
skill silos. It also means small teams pay a steep "size penalty" — a 3-person
desk cannot hit the same service level as a 30-person one at equal occupancy.

## Why the last agent matters so much
Near the knee of the Erlang-C curve, each added agent yields an outsized jump in
service level (the 24 -> 25 agent example lifts SL from ~0.81 to ~0.88). This
non-linearity is why "just add one more" debates are worth having with the
actual curve in front of you, not intuition.

## Authoritative sources
1. Brad Cleveland, *Call Center Management on Fast Forward*, 3rd ed., ICMI
   Press, 2012.
2. Noah Gans, Ger Koole & Avishai Mandelbaum, "Telephone Call Centers: Tutorial,
   Review, and Research Prospects," *M&SOM*, 2003.
3. Ger Koole & Avishai Mandelbaum, "Queueing Models of Call Centers: An
   Introduction," *Annals of Operations Research*, 2002.
4. Sem Borst, Avishai Mandelbaum & Martin Reiman, "Dimensioning Large Call
   Centers," *Operations Research*, 2004 (square-root staffing).
5. Donald Gross, John Shortle, James Thompson & Carl Harris, *Fundamentals of
   Queueing Theory*, 4th ed., Wiley, 2008.
6. Leonard Kleinrock, *Queueing Systems, Volume 1: Theory*, Wiley, 1975.
7. Z. Aksin, M. Armony & V. Mehrotra, "The Modern Call Center," *Production and
   Operations Management*, 2007.
8. Ward Whitt, "Engineering Solution of a Basic Call-Center Model,"
   *Management Science*, 2005.
