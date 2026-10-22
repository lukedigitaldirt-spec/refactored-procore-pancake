# 5W2H and the Discipline of Questioning

Before you can document know-how, you have to extract it completely. 5W2H is
the checklist that forces completeness: seven questions whose answers, taken
together, fully specify a task. This guide backs `scripts/fivew2h_validator.py`.

## The seven questions
| Element | Question | What a good answer pins down |
|---------|----------|------------------------------|
| **Who** | Who owns / performs it? | The accountable role (not a name) |
| **What** | What is done? | The task and its output, verb + object |
| **When** | When / how often? | Trigger, cadence, deadline |
| **Where** | Where does it happen? | System, tool, location, channel |
| **Why** | Why does it exist? | Purpose, outcome, risk it addresses |
| **How** | How is it done? | Method, the sequence of steps |
| **How much** | How much / how many? | Cost, quantity, threshold, resources |

The first six are Kipling's "six honest serving-men" ("I keep six honest
serving-men / They taught me all I knew; / Their names are What and Why and
When / And How and Where and Who"). Toyota and the quality movement added the
two quantifying questions — the "2H" — because a task you cannot measure is a
task you cannot improve.

## Why completeness matters
A missing element is not a cosmetic gap; it is where the documented procedure
will fail. No **Who** and the work has no owner. No **Why** and people cannot
make good exceptions when reality diverges from the steps. No **How much** and
you cannot set thresholds, size resources, or know when a different path
applies. The validator exists to make each gap visible as a forcing question.

## Questioning technique — grill with the frame open
- **Ask for the role, not the person.** "Which role owns this?" survives
  turnover; "Who, like, Priya?" does not.
- **Separate what should happen from what does.** Document reality first.
- **Push "Why" up the ladder.** Keep asking why until you reach the real
  outcome; stop one rung short and you document a ritual, not a purpose.
- **Make "How much" concrete.** Replace "a lot" / "sometimes" with a number or
  a threshold that changes behaviour.
- **Treat a blank as the finding.** An element the owner cannot answer is the
  most valuable output of the session — it names what nobody actually knows.

## Where 5W2H sits among its cousins
- **Ishikawa (fishbone)** uses the Ws to organise causes of a problem; 5W2H
  uses them to fully specify a task or countermeasure.
- **5 Whys** drills a single causal chain; 5W2H spans the whole task. Use 5
  Whys *inside* the "Why" answer when the purpose is murky.
- **The Kipling method** in creative problem-solving is the same six questions
  pointed at idea generation rather than capture.

## Relationship to the tools here
- `fivew2h_validator.py` scores a structured object or a free-text worksheet
  and returns a prompt per gap — run it before authoring an SOP or runbook.
- A complete 5W2H flows straight into `sop_linter.py` (How → procedure, Who →
  roles, Why → purpose) and `runbook_validator.py` (When → trigger, How →
  steps).

## Authoritative sources
1. Rudyard Kipling, "The Elephant's Child," in *Just So Stories*, Macmillan,
   1902 (the "six honest serving-men").
2. Kaoru Ishikawa, *Guide to Quality Control*, Asian Productivity
   Organization, 1976 (cause-and-effect diagram).
3. Kaoru Ishikawa, *What Is Total Quality Control? The Japanese Way*,
   Prentice-Hall, 1985.
4. Taiichi Ohno, *Toyota Production System: Beyond Large-Scale Production*,
   Productivity Press, 1988 (the Five Whys and quantified countermeasures).
5. Shigeo Shingo, *A Study of the Toyota Production System*, Productivity
   Press, 1989.
6. Michael Brassard & Diane Ritter, *The Memory Jogger II*, GOAL/QPC, 2010
   (5W2H and quality tools).
7. Bernard Dodge, "The 5W Model" and Kipling-method questioning in
   instructional design, San Diego State University, accessed 2026.
8. Arthur VanGundy, *Techniques of Structured Problem Solving*, 2nd ed., Van
   Nostrand Reinhold, 1988 (Kipling / 5W1H in problem framing).
