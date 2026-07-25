---
id: NNNN
title: <kebab-case-title>
status: draft        # draft → accepted → implemented | abandoned | superseded
author: <name>
created: <YYYY-MM-DD>
supersedes:          # link the spec id this replaces, if any
---

# <Title>

> Default spec template (used when the project defines none). Prose, not bullet dumps —
> writing forces precision. Aim for ~2 pages; if it won't fit, it's too broad — split it.
> Sections tagged **(required)** must be present and non-empty — Step 2.5 pass 7 checks this
> literally; T1 specs may drop the **(when relevant)** ones. A project's own template overrides
> this required set.
> Every load-bearing number cites a source (research note / benchmark / ADR) or is tagged
> `[ASSUMPTION]`; every Goal pairs with a roll-back invalidator below — Step 2.5 passes 8–9 enforce both.

## Problem / Context (required)
**What is broken or missing right now**, anchored in observable evidence (a metric, a log,
a user report, a failing case). One or two paragraphs. Background facts a reader needs.

## Goals & Non-Goals (required)
**What this achieves**, and **explicitly what it will NOT do** (the non-goals are as
important as the goals — they bound scope and pre-empt the grill).

## The win, in the user's words (when relevant)
One paragraph describing the outcome as the user/customer would read it — plain language,
no jargon, no internal architecture. (Working-backwards: decouples "what's wanted" from
"what we currently build.") Optional for T1.

## Proposed solution (required)
The approach and the **trade-offs you made** — not how to code it. A system-context note
(how this fits the existing system) where relevant. Degree of constraint: greenfield (wide)
or constrained by legacy (narrow)?

## Alternatives considered (required for T2)
Each rejected option + why it loses. *A spec with no alternatives wasn't designed.*

## Metric delta / success criteria (required)
**Which measurable thing moves, by how much, measured how** (n, threshold, the query/command).
Post-ship and checkable.

## Cross-cutting concerns (when relevant)
Security, privacy, observability/telemetry, data/migration, cost/ops. Skip a line only if
genuinely N/A.

## Drawbacks · risks · hypothesis-invalidators (required)
Honest costs. **Observable conditions that mean "roll this back"** — each must name HOW it
gets measured (no invalidator without a measurement plan). At least one full triple:
*observable condition → how measured → that it means roll back* (Step 2.5 pass 8).

## Wedge (required)
**The narrowest first slice that delivers value.** One or two sentences. (Appetite: how much
time is this worth?)

## Open questions (when relevant)
What still needs a decision. Mark inline ambiguities `[NEEDS CLARIFICATION]`.

## Out of scope / accepted (when relevant)
Things consciously deferred or accepted as-is (from the grill's "acknowledge" bucket).
