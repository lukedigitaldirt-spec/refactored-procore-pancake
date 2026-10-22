# Runbook Authoring — executable response under pressure

A runbook is an SOP for an operational event: a known condition, met with a
concrete, ordered response. Where an SOP documents routine work, a runbook is
read at 3am by a tired on-call engineer who needs to act, not think. This guide
maps the seven parts that `scripts/runbook_validator.py` checks to established
SRE and incident-response practice.

## The seven canonical parts
- **Title** — names the condition, not a product. "API latency incident
  response". Keep the word that your tooling classifies (e.g. "alert") out of
  the title so it is not mistaken for the trigger section.
- **Trigger** — the exact condition that starts the runbook: which alert fires,
  which monitor crosses which threshold, what symptom is reported. A runbook
  with a vague trigger is run at the wrong time or not at all.
- **Prerequisites** — access, tools, and credentials needed before acting.
  Discovering you lack prod access mid-incident is a preventable delay.
- **Procedure** — the ordered, imperative steps to resolve. Copy-pasteable
  commands beat prose. One action per step.
- **Verification** — the exact signal that proves recovery: metric, value, and
  duration ("p99 under 300ms for 10 minutes"). "Seems fine" is not
  verification.
- **Rollback** — how to safely undo the actions if they worsen the situation.
  If an action is irreversible, the runbook must say so before the step.
- **Escalation** — who to page, and when. A runbook that dead-ends when the
  steps fail is incomplete.

## Why these and not others
Google SRE frames the runbook (playbook) as the single biggest lever on mean
time to recovery: it turns tribal knowledge into a repeatable response and
roughly halves MTTR versus improvising. PagerDuty and Atlassian incident
guidance add the same spine — detect, diagnose, remediate, verify, escalate —
and insist on a defined rollback and named escalation path.

## Writing discipline
- **Deterministic steps.** Prefer exact commands and expected output over
  "investigate the issue". Automate what you can; link the automation.
- **Idempotent where possible.** A step that is safe to re-run survives the
  confusion of an incident.
- **No decisions without criteria.** "If error rate stays above 1%, roll back"
  — give the threshold, not a judgment call.
- **Test the runbook** in game days / chaos drills. An untested runbook is a
  hypothesis.

## SOP vs. runbook
| | SOP | Runbook |
|---|---|---|
| Cadence | Routine, planned work | Reactive, event-driven |
| Reader state | Calm, learning | Stressed, acting now |
| Must have | Purpose, scope | Trigger, verification, rollback, escalation |
| Success | Task done correctly | Condition resolved, verified, safe to leave |

## Relationship to the tools here
- `runbook_validator.py` checks all seven parts and scores completeness; it
  errors on a missing trigger, steps, verification, or escalation.
- `sop_linter.py` is its sibling for routine procedures.

## Authoritative sources
1. Betsy Beyer, Chris Jones, Jennifer Petoff & Niall Richard Murphy (eds.),
   *Site Reliability Engineering: How Google Runs Production Systems*,
   O'Reilly, 2016 (playbooks and on-call).
2. Betsy Beyer et al. (eds.), *The Site Reliability Workbook*, O'Reilly, 2018
   (practical runbook and incident chapters).
3. PagerDuty, *Incident Response Documentation* (ops guide / runbooks),
   response.pagerduty.com, accessed 2026.
4. Atlassian, *Incident Management Handbook* and runbook guidance,
   atlassian.com/incident-management, accessed 2026.
5. Paul Hammant, Steve Freeman et al., Google SRE *Enterprise Roadmap to SRE*,
   O'Reilly, 2020.
6. NIST SP 800-61 Rev. 2, *Computer Security Incident Handling Guide*, 2012
   (prepare / detect / respond / recover phases).
7. Microsoft, *Microsoft Writing Style Guide* (procedures, commands, and
   imperative instructions), accessed 2026.
8. John Allspaw & Paul Hammond, "10+ Deploys Per Day: Dev and Ops Cooperation
   at Flickr," Velocity, 2009 (operational readiness and rollback).
