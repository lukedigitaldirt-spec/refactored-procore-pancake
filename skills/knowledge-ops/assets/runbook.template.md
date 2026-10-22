# <Runbook title: the condition it responds to, e.g. "API latency incident response">

> A runbook is executed under pressure, often at 3am. Every part below is
> mandatory. If you cannot fill one, the runbook is not ready to hand off.

## Trigger
<The precise condition that starts this runbook: which alert or alarm fires,
what symptom a human reports, or what monitor crosses which threshold.
Be specific enough that the reader knows this is the right runbook.>

## Prerequisites
- <Access needed, e.g. "prod kubectl context", "PagerDuty on-call seat">
- <Tools, credentials, or dashboards required before acting>

## Procedure
1. <First ordered, imperative step. "Open the latency dashboard.">
2. <Next step. Keep each to one concrete action.>
3. <Continue until the condition is resolved.>

## Verification
<How to confirm the issue is actually resolved: the exact metric, value, and
duration that proves recovery, e.g. "p99 latency under 300ms for 10 minutes".>

## Rollback
<How to safely undo the actions above if they make things worse, step by step.
If an action is irreversible, say so explicitly.>

## Escalation
- <First escalation target and when to page them, e.g. "platform on-call L2
  after 15 minutes without recovery">
- <Secondary contact or service owner>
