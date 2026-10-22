---
name: knowledge-ops
description: >-
  Capture institutional know-how as durable, structured documentation. Use when
  someone needs to write or audit a standard operating procedure, build a
  runbook, "document this process", stand up or clean a knowledge base, produce
  onboarding docs, or complete a 5W2H intake before writing anything. Triggers:
  "SOP", "standard operating procedure", "runbook", "playbook", "document this
  process", "write it up", "knowledge base", "onboarding docs", "5W2H",
  "document control", "revision history". Ships three stdlib-only validators
  (fivew2h_validator, sop_linter, runbook_validator), each reading structured
  JSON or a markdown/plain-text doc. Runs with context: fork so bulky
  multi-document intake stays out of the parent context. NOT for mapping or
  diagnosing a live workflow (use process-mapper) or staffing math (use
  capacity-planner).
context: fork
---

# Knowledge Ops

Turn "someone just knows how to do this" into **documentation anyone can
execute** — a validated SOP, a runbook that holds up at 3am, and a 5W2H intake
that proves the know-how is complete before a word is written. Three lenses,
three tools:

| Lens | Question it answers | Tool |
|------|--------------------|------|
| **Completeness** | Is the know-how fully specified yet? | `scripts/fivew2h_validator.py` |
| **Routine procedure** | Is this SOP usable and controlled? | `scripts/sop_linter.py` |
| **Operational response** | Is this runbook safe to run? | `scripts/runbook_validator.py` |

This skill runs with `context: fork` on purpose. Knowledge capture is a
read-heavy job: you pull in interview notes, existing wikis, half-written
procedures, and several reference docs at once. All of that intake and the
validation chatter happen in a forked context; only the finished artifact and
its verdict return to the parent, keeping the main thread clean.

## Method (interview → externalize → validate → control)

1. **Interview with the frame open.** Run a 5W2H intake first (Who, What, When,
   Where, Why, How, How much). A blank element is not a cosmetic gap — it is
   where the finished doc will fail. Validate coverage with
   `fivew2h_validator.py`; every gap it returns is a question to put back to the
   owner.
2. **Pick the artifact.** Routine, planned work → an **SOP**. A reactive
   response to a known condition (an alert, an outage, a symptom) → a
   **runbook**. The two are siblings with different readers: the SOP reader is
   calm and learning; the runbook reader is stressed and acting now.
3. **Externalize.** Draft from the 5W2H answers: How → procedure, Who → roles,
   Why → purpose, When → trigger. Use the templates in `assets/`.
4. **Validate structure.** Run `sop_linter.py` or `runbook_validator.py`. They
   separate errors (the doc is not usable) from warnings (quality smells) the
   same way process-mapper's validators do. A doc that does not validate is a
   doc you cannot hand off.
5. **Put it under control.** One canonical source of truth, an owner, a review
   date, a `verb + object` title, and revision history. Uncontrolled docs rot,
   and a trusted-but-stale doc is worse than none.

## Using the tools

All three are stdlib-only, take a JSON file (or `-` for stdin), support
`--json` for machine output, and **also accept a markdown/plain-text document
via `--text`** — so you can validate a doc you are drafting, not just a
structured object.

```bash
# 5W2H completeness from a structured object...
python scripts/fivew2h_validator.py intake.json

# ...or score a markdown worksheet by scanning its headers/labels
python scripts/fivew2h_validator.py assets/5w2h-worksheet.md --text

# Lint an SOP (structured), machine-readable output
python scripts/sop_linter.py sop-input.json --json

# Lint an SOP you are writing, straight from the markdown
python scripts/sop_linter.py assets/sop.template.md --text

# Validate a runbook from stdin (pipe JSON in)
cat runbook.json | python scripts/runbook_validator.py -

# Validate a runbook draft in markdown (scores completeness over 7 parts)
python scripts/runbook_validator.py assets/runbook.template.md --text
```

See `assets/` for ready-to-fill templates: `sop.template.md`,
`runbook.template.md`, `5w2h-worksheet.md`, and `sop-input.template.json`.

## Reference library

- `references/sop-authoring.md` — SOP structure, imperative style, document
  control (ISO 9001 / ISO/TR 10013, EPA QA/G-6, FDA).
- `references/runbook-authoring.md` — the seven runbook parts and SRE/incident
  practice (Google SRE, PagerDuty, Atlassian).
- `references/5w2h-and-questioning.md` — the seven questions, Kipling and
  Ishikawa, and how to grill for completeness.
- `references/knowledge-management-foundations.md` — DIKW, Nonaka's SECI
  (tacit → explicit), and keeping a knowledge base alive.

## Forcing-question library (grill-with-docs)

Per the Matt Pocock "grill the user with the docs open" discipline, do not
write a line until these are answered. If the owner cannot answer one, that gap
*is* the finding — capture it and send it back.

- **Reader and situation:** "Who reads this, and in what state — calmly
  learning a routine (SOP), or acting under pressure on a live event
  (runbook)?" The answer picks the artifact and the voice.
- **Owner, not name:** "Which *role* owns this task? Name a role, not a person,
  so the doc outlives whoever does it today."
- **Purpose up the ladder:** "Why does this process exist — what outcome or
  risk does it serve? Keep asking why until we hit the real reason, not a
  ritual."
- **Reality vs. policy:** "Are we documenting how it *actually* works today,
  including the workarounds, or how it's *supposed* to? Capture reality first."
- **Thresholds and quantities (the 2H):** "How much, how many, what threshold
  changes the path? 'Sometimes' and 'a lot' can't be executed — give me a
  number."
- **Verification and undo (runbooks):** "How do we *prove* it's resolved — which
  metric, value, and for how long — and how do we safely roll back if the fix
  makes it worse?"
- **Control:** "Where will the single source of truth live, who owns it, and
  when is it reviewed? An unowned, unversioned doc is one we'll regret
  trusting."
