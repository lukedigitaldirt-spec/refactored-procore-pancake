# Knowledge-Management Foundations

Documenting a process is one move in a larger system: turning what people know
into what the organisation knows, so it survives turnover and scales beyond the
expert. This guide gives knowledge-ops its theory — why SOPs, runbooks, and
5W2H capture are worth the effort, and how to keep a knowledge base alive.

## Data → Information → Knowledge → Wisdom
The DIKW hierarchy separates raw **data** (an invoice timestamp) from
**information** (the AP cycle took 9 days), from **knowledge** (how to run the
AP process), from **wisdom** (knowing which exceptions to make). Documentation
operates at the knowledge layer: it encodes the *how* and *why*, not just the
*what*. An SOP that lists facts without method is stuck at the information
layer and does not transfer capability.

## Tacit vs. explicit knowledge (SECI)
Nonaka and Takeuchi distinguish **tacit** knowledge (in people's heads, hard to
articulate) from **explicit** knowledge (written, transferable). Their SECI
model names four conversions:
- **Socialization** (tacit → tacit): apprenticeship, shadowing.
- **Externalization** (tacit → explicit): *this is the hard one* — writing the
  SOP, running the 5W2H interview. It is where knowledge-ops earns its keep.
- **Combination** (explicit → explicit): assembling SOPs into a knowledge base.
- **Internalization** (explicit → tacit): people read the runbook, practise,
  and it becomes second nature.
The point of good capture tools is to make externalization cheap and reliable,
because it is the conversion organisations are worst at.

## The knowledge base as a living system
- **Single source of truth.** One canonical document per procedure; everything
  else links to it. Duplicated "current" copies are how drift starts.
- **Ownership and review cadence.** Every document has an owner and a review
  date. Unowned docs rot; rotted docs are worse than none because they are
  trusted.
- **Findable, not just stored.** Title by `verb + object`, tag by process, and
  link related docs. A document nobody can find was never captured.
- **Lifecycle.** Draft → reviewed → published → reviewed-on-cadence → retired.
  Retire superseded docs loudly so no one follows a ghost.

## Why documentation fails (and the fix)
| Failure | Cause | Fix |
|---------|-------|-----|
| Nobody reads it | Written for the author, not the performer | Imperative steps, scannable structure |
| It goes stale | No owner, no review date | Assign both; tie to a cadence |
| It is incomplete | Tacit gaps never surfaced | 5W2H interview before authoring |
| Two versions exist | No single source of truth | One canonical doc, link the rest |
| It cannot be found | No naming/tagging discipline | `verb + object` titles, consistent tags |

## Onboarding as the acid test
New-hire onboarding is the clearest return on captured knowledge: a strong SOP
and runbook library turns weeks of over-the-shoulder learning into
self-service internalization. If a new hire cannot execute from the docs, the
externalization was incomplete — send it back through 5W2H.

## Relationship to the tools here
- `fivew2h_validator.py` drives externalization: it forces tacit gaps into the
  open before capture.
- `sop_linter.py` and `runbook_validator.py` keep explicit artifacts
  structurally sound so combination and internalization actually work.

## Authoritative sources
1. Ikujiro Nonaka & Hirotaka Takeuchi, *The Knowledge-Creating Company*,
   Oxford University Press, 1995 (the SECI model).
2. Ikujiro Nonaka, "A Dynamic Theory of Organizational Knowledge Creation,"
   *Organization Science*, 1994.
3. Russell L. Ackoff, "From Data to Wisdom," *Journal of Applied Systems
   Analysis*, 1989 (the DIKW hierarchy).
4. Jennifer Rowley, "The wisdom hierarchy: representations of the DIKW
   hierarchy," *Journal of Information Science*, 2007.
5. Michael Polanyi, *The Tacit Dimension*, University of Chicago Press, 1966
   ("we know more than we can tell").
6. Thomas H. Davenport & Laurence Prusak, *Working Knowledge: How
   Organizations Manage What They Know*, Harvard Business School Press, 1998.
7. Etienne Wenger, *Communities of Practice: Learning, Meaning, and Identity*,
   Cambridge University Press, 1998.
8. ISO 30401:2018, *Knowledge management systems — Requirements.*
