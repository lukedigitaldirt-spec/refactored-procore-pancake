# Orchestration and Plays — chaining skills into an engagement

A single skill answers one question. Real operational problems are rarely one
question; they are an **engagement** — a chain of analyses where each output
feeds the next. This runner implements that chain as a **named play**: a
predefined, ordered sequence of sub-skills, each run in an isolated forked
context, with a carry-forward packet between them.

## The pattern: orchestrator vs. pipeline
- An **orchestrator** classifies a request and dispatches it to the single best
  specialist. One in, one out.
- A **pipeline** composes specialists: the result of stage N becomes an input
  to stage N+1. It needs a **sequencing rule** (which order) and a **hand-off
  contract** (what passes between stages).

This mirrors well-established composition patterns in software: the pipes-and-
filters architecture, the chain-of-responsibility pattern, and the saga pattern
for multi-step workflows where each step must be able to halt the chain.

## Named plays (a playbook)
A "play" is the operational analogue of a runbook-of-runbooks: a reusable,
named response to a recurring situation. Naming the sequence does three things:
1. **Repeatability** — the same goal yields the same ordered steps every time.
2. **Teachability** — a team can learn "we run `fix-a-slow-process`" rather
   than re-deriving the order under pressure.
3. **Auditability** — the chosen play and its stages are an explicit record of
   how a conclusion was reached.

`scripts/play_selector.py` is the deterministic selector: name, keywords, or an
explicit skill set in; an ordered sequence with a per-step carry-forward
contract out.

## Context isolation (fork-and-carry-forward)
Each stage runs in a **forked context** so one sub-skill's working notes, tool
output, and intermediate reasoning do not pollute the others or the parent
thread. Only each stage's **conclusion** is written into the shared engagement
packet and carried forward. This keeps a six-stage engagement legible and
bounds the context each stage has to reason over — the same discipline as
map-reduce and sub-agent orchestration.

## Gating
A pipeline without gates propagates garbage. Each stage may **halt** the chain
if its premise fails (the saga "compensate/abort" idea): if `process-mapper`
finds the step times were never measured, the downstream stages must not run on
fabricated numbers. Report and re-plan instead.

## Authoritative sources
1. Frank Buschmann et al., *Pattern-Oriented Software Architecture, Vol. 1*,
   Wiley, 1996 (pipes-and-filters).
2. Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides, *Design Patterns*,
   Addison-Wesley, 1994 (chain-of-responsibility).
3. Hector Garcia-Molina & Kenneth Salem, "Sagas," *ACM SIGMOD*, 1987
   (multi-step workflow with per-step abort/compensation).
4. Gregor Hohpe & Bobby Woolf, *Enterprise Integration Patterns*, Addison-
   Wesley, 2003 (message routing, process manager).
5. Chris Richardson, *Microservices Patterns*, Manning, 2018 (saga and process
   orchestration).
6. Atlassian, *Incident Management Handbook* (runbooks and playbooks), 2019.
7. Betsy Beyer et al., *Site Reliability Engineering*, O'Reilly, 2016
   (playbooks as named, repeatable responses).
8. Jeff Dean & Sanjay Ghemawat, "MapReduce: Simplified Data Processing on Large
   Clusters," *OSDI*, 2004 (fan-out/fan-in with isolated workers).
