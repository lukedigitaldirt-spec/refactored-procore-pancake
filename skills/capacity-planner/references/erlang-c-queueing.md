# Erlang-C Queueing — the staffing workhorse and its assumptions

Erlang-C is the standard model for sizing a queue where contacts *wait* rather
than get blocked: inbound phone, chat, ticket triage, dispatch. It answers "with
N agents and this load, what fraction of contacts wait, and for how long?" This
is the math behind `scripts/erlang_c.py`.

## Offered load (Erlangs)
The dimensionless quantity that drives everything:

```
A = (calls_per_interval * aht_seconds) / interval_seconds
```

One Erlang is one agent-hour of work arriving per hour. 100 calls per 30-minute
interval at 180s AHT is `100 * 180 / 1800 = 10` Erlangs — ten agents' worth of
continuous work. You must staff **more** than A agents, because arrivals are
random, not evenly spaced.

## The Erlang-B recursion (numerically stable)
The textbook Erlang-C closed form contains `A^N / N!`, which overflows for even
modest N. Compute the Erlang-B blocking probability with the stable recursion
instead, then convert:

```
b = 1.0
for k in 1..N:  b = (A * b) / (k + A * b)       # Erlang-B for N servers
C = (N * b) / (N - A * (1 - b))                 # Erlang-C, requires N > A
```

`C` is the probability an arriving contact must wait. If `N <= A` the system is
unstable (the queue grows without bound): `C = 1` and service level is 0.

## Service level, ASA, occupancy
Given `C`, average handle time `AHT`, and a target answer time `t`:

- **Service level** (fraction answered within `t`):
  `SL = 1 - C * exp(-(N - A) * t / AHT)`.
- **Average speed of answer** (mean wait over all contacts):
  `ASA = C * AHT / (N - A)`.
- **Occupancy** (agent utilization): `A / N`. Above ~90% sustained, service
  degrades sharply and burnout rises.

## Worked example
A = 20 Erlangs, AHT = 180s, target = 20s. With N = 24 agents, `C ≈ 0.298`,
`SL ≈ 0.81`. Add one agent (N = 25) and `SL` jumps to ≈ 0.88 — the classic
sharply nonlinear payoff of the last agent near the knee of the curve.

## Assumptions and where it breaks
Erlang-C assumes Poisson arrivals, exponential handle times, a single skill
pool, infinite patience (no abandonment), and no retrials. The infinite-patience
assumption makes it **conservative** — real callers abandon, which shortens
queues, so Erlang-C tends to slightly over-staff. For high-abandonment or
long-wait environments use Erlang-A (Garnett/Mandelbaum/Reiman), which models
patience explicitly.

## Authoritative sources
1. A. K. Erlang, "The Theory of Probabilities and Telephone Conversations,"
   *Nyt Tidsskrift for Matematik B*, 1909.
2. A. K. Erlang, "Solution of Some Problems in the Theory of Probabilities of
   Significance in Automatic Telephone Exchanges," *Elektroteknikeren*, 1917.
3. Donald Gross, John Shortle, James Thompson & Carl Harris, *Fundamentals of
   Queueing Theory*, 4th ed., Wiley, 2008.
4. Leonard Kleinrock, *Queueing Systems, Volume 1: Theory*, Wiley, 1975.
5. Noah Gans, Ger Koole & Avishai Mandelbaum, "Telephone Call Centers: Tutorial,
   Review, and Research Prospects," *Manufacturing & Service Operations
   Management*, 2003.
6. O. Garnett, A. Mandelbaum & M. Reiman, "Designing a Call Center with
   Impatient Customers," *M&SOM*, 2002 (Erlang-A).
7. Ger Koole, *Call Center Optimization*, MG Books, 2013.
8. Robert B. Cooper, *Introduction to Queueing Theory*, 2nd ed., North-Holland,
   1981.
