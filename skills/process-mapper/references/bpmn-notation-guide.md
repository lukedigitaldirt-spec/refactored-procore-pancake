# BPMN 2.0 Notation — the elements you actually need

Business Process Model and Notation (BPMN) 2.0 is the ISO/OMG standard visual
language for business processes. You do not need all 100+ symbols. Roughly
20% of the notation covers 80% of real process maps. This guide is that 20%,
mapped to the JSON model consumed by `scripts/bpmn_validator.py`.

## Flow objects

### Events (circles)
- **Start event** (thin circle) — what triggers the process. Exactly one per
  process level. No incoming flow.
- **End event** (thick circle) — a terminal state. At least one; you may have
  several (e.g. "approved" and "rejected").
- **Intermediate events** (double circle) — timers, messages, signals that
  occur mid-flow. Model sparingly; they are the most-abused symbol.

### Activities (rounded rectangles)
- **Task** — an atomic unit of work. Name it `verb + object` ("Approve
  invoice"), never a noun ("Invoice").
- **Sub-process** — a collapsed task that hides a nested flow. Use to keep a
  map readable; over-nesting hides the real complexity.

### Gateways (diamonds) — control the flow, never do work
- **Exclusive (XOR, X)** — one path out based on a condition. The workhorse.
- **Parallel (AND, +)** — all paths fire simultaneously; must be re-joined by a
  matching parallel gateway.
- **Inclusive (OR, O)** — one or more paths. Powerful but easy to get wrong.

A gateway is a routing decision, not an activity. Common error: labeling a
gateway with a verb. Label it with the **question** ("Amount > $10k?").

## Connecting objects
- **Sequence flow** (solid arrow) — order of execution within one pool.
- **Message flow** (dashed arrow) — communication *between* pools.
- **Association** (dotted) — links artifacts/annotations to elements.

## Swimlanes
- **Pool** — a participant/organization (e.g. "Customer", "Our company").
- **Lane** — a role/department inside a pool (e.g. "AP Clerk", "Controller").
  Every task lives in exactly one lane; that is who is accountable for it.

## Structural rules the validator enforces
1. Exactly one start event; >=1 end event.
2. Start events have no incoming, one outgoing flow. End events have no
   outgoing, >=1 incoming.
3. Every node is reachable from start and can reach an end (no orphans, no dead
   ends).
4. Gateways split or merge (>=3 connections); a gateway with two connections is
   really just a task in disguise.
5. Sequence flows may only connect existing nodes.

## Common modeling smells
- **Implicit gateways** — two flows leaving a task with no gateway. Illegal;
  make the decision explicit.
- **Unbalanced parallel gateways** — an AND-split with no AND-join deadlocks.
- **Black-hole tasks** — a task with no outgoing flow. Work goes in, nothing
  comes out.
- **Naming drift** — mixing verb-object and noun labels makes the map
  ambiguous.

## Authoritative sources
1. Object Management Group, *Business Process Model and Notation (BPMN)
   Version 2.0.2*, OMG formal specification, 2013.
2. ISO/IEC 19510:2013, *Information technology — Object Management Group
   Business Process Model and Notation.*
3. Bruce Silver, *BPMN Method and Style*, 2nd ed., Cody-Cassidy Press, 2011.
4. Thomas Allweyer, *BPMN 2.0: Introduction to the Standard for Business
   Process Modeling*, 2nd ed., BoD, 2016.
5. Marlon Dumas, Marcello La Rosa, Jan Mendling, Hajo Reijers, *Fundamentals
   of Business Process Management*, 2nd ed., Springer, 2018.
6. Stephen White & Derek Miers, *BPMN Modeling and Reference Guide*, Future
   Strategies, 2008.
7. OMG BPMN specification issues & MIWG interoperability test suite,
   bpmn.org (accessed 2026).
8. Jakob Freund & Bernd Rücker, *Real-Life BPMN*, 4th ed., 2019.
