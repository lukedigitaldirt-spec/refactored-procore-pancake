# 5W2H Worksheet — <process or task name>

> Answer all seven before you write an SOP or runbook. A blank line here is a
> question to put back to the process owner, not a box to guess at. Run
> `fivew2h_validator.py --text` against this file to score coverage.

## Who — owner / responsible role
<Which role or person is accountable? Use a role, not a name, so the doc
survives staff changes. (RACI if more than one party is involved.)>

## What — task / deliverable
<What exactly is done, in verb + object form? What is the output?>

## When — timing / trigger / frequency
<What starts it? How often? Is there a deadline or cadence?>

## Where — system / location / channel
<Which system, tool, environment, or physical location does the work happen
in?>

## Why — purpose / rationale
<Why does this exist? What outcome or risk does it serve? If you cannot answer,
question whether the task should exist at all.>

## How — method / steps
<By what method is it done? Summarise the sequence; the full detail becomes the
SOP procedure.>

## How much — cost / quantity / threshold / resources
<What volume, cost, budget, threshold, or resource level is involved? What
quantity triggers a different path?>

## Coverage check
- [ ] All seven elements answered with real content (not placeholders)
- [ ] `fivew2h_validator.py --text 5w2h-worksheet.md` reports 100%
