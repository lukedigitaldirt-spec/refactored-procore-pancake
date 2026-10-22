---
name: internal-comms
description: >-
  Plan and run internal change communication. Use when someone needs to
  announce a change, build a rollout comms plan, manage resistance, assess
  change readiness, track a transformation, segment stakeholders, or script a
  town hall / all-hands message. Triggers: "announce", "rollout comms", "change
  management", "ADKAR", "Kotter", "resistance", "stakeholder message", "town
  hall", "all-hands", "communication plan", "how do I tell the team". Ships
  three stdlib-only tools (adkar_assessment, kotter_tracker,
  stakeholder_matrix). NOT for external/customer messaging (use business-growth)
  or documenting a finished process as an SOP (use knowledge-ops).
---

# Internal Comms

Turn "we need to tell people about this change" into a **diagnosed readiness
picture, a sequenced plan, and the right message to the right audience**. Three
lenses, three tools:

| Lens | Question it answers | Tool |
|------|--------------------|------|
| **Readiness** | Are people ready to change — and where is the gap? | `scripts/adkar_assessment.py` |
| **Progress** | How far through the transformation are we, and in order? | `scripts/kotter_tracker.py` |
| **Audience** | Who must we engage, how closely, and through what channel? | `scripts/stakeholder_matrix.py` |

## Method (diagnose → plan → communicate)

1. **Diagnose readiness (ADKAR).** Score the five individual building blocks —
   Awareness, Desire, Knowledge, Ability, Reinforcement — 1-5. The **first**
   block below threshold is the barrier point: the gap that blocks everything
   after it. A gorgeous all-hands cannot fix a Desire gap with training. Fix the
   barrier, then re-score.
2. **Locate the transformation (Kotter).** Track the 8 steps. The sequence is
   load-bearing — declaring short-term wins before the vision is communicated,
   or victory before acceleration, is the classic failure. The tracker warns
   when a later step has jumped ahead of an unstarted earlier one.
3. **Segment the audience (power/interest).** Not everyone gets the same
   message at the same cadence. Place each stakeholder on the power/interest
   grid to decide who you manage closely, keep satisfied, keep informed, or
   merely monitor. Mis-targeting — flooding a Monitor group, blindsiding a
   Manage-Closely sponsor — is the common waste.
4. **Write the plan.** Use `assets/change-comms-plan.md`. For each message pin
   down audience, ADKAR objective, the WIIFM-explicit message, the sender
   (sponsor for *why*, line manager for *what it means for me*), channel, and
   timing. Brief sponsors and managers **before** the broad announcement.
5. **Close the loop.** Announcements build Awareness, not Desire. Build feedback
   channels, treat resistance as data about an unmet ADKAR block, re-score, and
   measure reach/recall/adoption — not "we sent the email."

## Using the tools

All tools are stdlib-only, take a JSON file (or `-` for stdin), and support
`--json` for machine output.

```bash
# Change readiness — finds the barrier point and the fix-first action
python scripts/adkar_assessment.py assessment.json
python scripts/adkar_assessment.py assessment.json --threshold 4

# Transformation progress — percent complete + out-of-sequence warnings
python scripts/kotter_tracker.py progress.json

# Stakeholder segmentation — quadrant + cadence/channel per person
python scripts/stakeholder_matrix.py stakeholders.json --json
```

See `assets/` for ready-to-fill input templates and a change-comms plan
worksheet.

## Reference library

- `references/adkar-model.md` — the five individual building blocks and the
  barrier-point logic.
- `references/kotter-8-step.md` — the eight organizational steps and why order
  matters.
- `references/stakeholder-analysis.md` — the power/interest grid and the four
  engagement strategies.
- `references/change-communication-planning.md` — senders, sequencing,
  resistance, and measurement.

## Forcing-question library (grill-with-docs)

Do not draft an announcement or run a number until these are answered. If the
user can't answer, that gap *is* the finding.

- **The why, honestly:** "What is the real business reason for this change, and
  what is the risk of *not* doing it?" Without a why you cannot build Awareness,
  and every downstream message rings hollow.
- **WIIFM per audience:** "For each affected group, what is actually in it for
  them — or against them?" Desire is won on WIIFM, not on the org chart's
  enthusiasm.
- **Measured readiness vs. hope:** "Are your ADKAR scores from a survey or
  interviews, or are they wishful? If guessed, by whom?" A barrier point built
  on hope sends you fixing the wrong block.
- **Sender, not just channel:** "Who is delivering each message — and have the
  sponsor and the line managers been briefed *before* the all-hands?" The right
  message from the wrong sender, or after the grapevine, fails.
- **Stakeholder targeting:** "Who are the high-power/high-interest players, and
  are you engaging them 1:1 rather than by broadcast?" Name the people you'd be
  blindsiding if you got the cadence wrong.
- **Resistance, surfaced:** "Where is the resistance, and which ADKAR block does
  it trace to?" Resistance you can't locate is resistance going underground.
- **Outcome, not activity:** "How will you know this worked — what reach,
  sentiment, adoption, or re-scored ADKAR number — beyond 'we sent it'?" If the
  only measure is messages sent, you have no plan, just a mailing list.
