# SOP Authoring — structure, style, and control

A Standard Operating Procedure is documented information that makes a task
repeatable by anyone with the stated prerequisites. It is the unit of
captured, reusable know-how. This guide maps the structure that
`scripts/sop_linter.py` enforces to the quality-management standards behind it.

## The mandatory sections
- **Title** — the task as `verb + object` ("Process a vendor invoice"), never
  a noun. The title is the retrieval key in a knowledge base.
- **Purpose** — why the SOP exists and the outcome it guarantees. ISO/TR 10013
  treats purpose as non-optional: documentation with no stated purpose is
  waste.
- **Scope** — what is covered and, explicitly, what is not. Unbounded scope is
  the most common reason an SOP rots: people apply it to cases it never meant
  to cover.
- **Roles & responsibilities** — who is accountable for each part. Tie to
  roles, not names, so the SOP survives staff turnover.
- **Procedure** — the ordered, imperative steps. This is the SOP.
- **Revision history** — version, date, author, change. An SOP with no version
  control cannot be trusted to be current.

## Writing the steps
- **Lead with a verb.** "Open the ticket", not "The ticket is opened" or "You
  should open the ticket." Imperative mood removes ambiguity about who acts.
  The linter flags steps that start with an article or pronoun.
- **One action per step.** If a step contains "and then", split it.
- **Keep steps short.** The linter warns past ~30 words; long steps hide
  branching that belongs in an explicit decision step.
- **Make decisions explicit.** "If amount > $5k, route to the manager"
  surfaces the branch instead of burying it in prose.
- **Write for the least-experienced reader** who meets the prerequisites.

## The two failure modes
1. **Under-specified** — missing purpose, scope, or real steps. The reader
   cannot execute. These are errors, not warnings.
2. **Over-specified** — a 40-step wall that no one reads. Collapse detail into
   referenced sub-procedures; keep the top level scannable.

## Document control
SOPs are controlled documents: owned, versioned, reviewed on a cadence, and
retired when superseded. Uncontrolled copies are how two teams end up following
different "current" procedures. Store the source of truth once and link to it.

## Relationship to the tools here
- `sop_linter.py` checks structure (purpose/scope/steps present), version
  control, and step writing discipline.
- `fivew2h_validator.py` confirms the underlying know-how is complete *before*
  you write the SOP — an SOP is only as good as the 5W2H behind it.

## Authoritative sources
1. ISO 9001:2015, *Quality management systems — Requirements* (clause 7.5,
   documented information).
2. ISO/TR 10013:2021, *Quality management systems — Guidance for documented
   information.*
3. ISO 9000:2015, *Quality management systems — Fundamentals and vocabulary.*
4. U.S. EPA, *Guidance for Preparing Standard Operating Procedures (SOPs)*,
   EPA QA/G-6, EPA/600/B-07/001, 2007.
5. U.S. FDA, *Guidance for Industry: Quality Systems Approach to
   Pharmaceutical CGMP Regulations*, 2006 (SOPs under the quality system).
6. U.S. FDA 21 CFR 211.100, *Written procedures; deviations.*
7. Microsoft, *Microsoft Writing Style Guide* (procedures and imperative
   instructions), Microsoft Press, accessed 2026.
8. *The Chicago Manual of Style*, 17th ed., University of Chicago Press, 2017
   (numbered lists and procedural text).
