---
id: NNNN
title: <kebab-case-title>
status: draft        # draft → accepted → implemented | abandoned | superseded
created: <YYYY-MM-DD>
supersedes:          # the change or ADR id this replaces, if any
routing: create      # amend | supersede | create  — the Step 1.5 verdict, and why
stale_docs:          # every existing doc this change makes wrong; each becomes a plan task
  - <path>: <what goes out of date>
---

# <Title>

> The **one** document this change is allowed to produce (T2 only). The consistency findings and
> the implementation plan are sections *of this file*, never siblings — see the artifact budget in
> SKILL.md Step 1.5.
>
> Prose, not bullet dumps: writing forces precision, and bullets are where the hard thinking gets
> skipped. Aim for about two pages. If it will not fit, the change is too broad — split it.
>
> Sections marked **(required)** must be present and non-empty; Step 2.5 pass 6 checks the literal
> section set. A project's own template overrides this required set. Every load-bearing number
> cites a source or is tagged `[ASSUMPTION]` (pass 8), and every goal pairs with a roll-back
> invalidator below (pass 7).

## Problem / Context (required)
What is broken or missing **right now**, anchored in observable evidence — a metric, a log line, a
user report, a failing case. One or two paragraphs, plus the background a cold reader needs.

## Goals & Non-Goals (required)
What this achieves, and **explicitly what it will not do**. The non-goals bound the scope and
pre-empt half the grill.

## The win, in the user's words (when relevant)
One paragraph describing the outcome as the person affected would read it — plain language, no
jargon, no internal architecture. Decouples "what is wanted" from "what we happen to build well."

## Proposed solution (required)
The approach and **the trade-offs you made** — not how to code it. How it fits the system that
exists today. Is the solution space wide (greenfield) or narrow (constrained by what is already
shipped)?

## Alternatives considered (required)
Each rejected option and why it loses. *A change with no rejected alternative was not designed.*

## Success criteria (required)
Which measurable thing moves, by how much, measured how — the n, the threshold, and the exact
query or command. Post-ship and checkable by someone who was not here.

## Cross-cutting concerns (when relevant)
Security · privacy · observability and telemetry · data and migration · cost and ops. Drop a line
only when it is genuinely not applicable.

## Drawbacks · risks · hypothesis-invalidators (required)
The honest costs, then **the observable conditions that mean "roll this back"**. At least one full
triple: *observable condition → how it is measured → that it means roll back*. The trigger must be
concrete — N production runs, a named real-world event, a data-volume threshold. **A calendar
deferral ("revisit in two weeks", "monitor for N days") is not a trigger and is rejected.**

## Wedge (required)
The narrowest first slice that delivers value, in one or two sentences. How much time is this
worth — appetite, not estimate.

## Open questions (when relevant)
What still needs a decision. Mark inline ambiguities `[NEEDS CLARIFICATION]`.

## Out of scope / accepted (when relevant)
Consciously deferred or accepted as-is — this is where the grill's "acknowledge" bucket lands.

---

## Consistency findings
<!-- Step 2.5 writes here. Severity · location · summary · fix. CRITICAL blocks the grill. -->

## Grill findings
<!-- Step 3 writes here, in three buckets: must-fix · open question · accepted. -->

## Implementation plan
<!-- Step 4 writes here: disjoint-file task partition, ordered phases with dependencies, the
     doc-sync tasks from `stale_docs` above, the test plan (exact commands), rollback, blast
     radius, grader scores. This is the artifact the human approves at the plan-gate. -->

## Decision log
<!-- One line per gate crossing: what was approved, when, and by whom. -->
