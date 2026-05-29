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
> T1 (light) specs need only the **bold** sections.

## Problem / Context
**What is broken or missing right now**, anchored in observable evidence (a metric, a log,
a user report, a failing case). One or two paragraphs. Background facts a reader needs.

## Goals & Non-Goals
**What this achieves**, and **explicitly what it will NOT do** (the non-goals are as
important as the goals — they bound scope and pre-empt the grill).

## The win, in the user's words
One paragraph describing the outcome as the user/customer would read it — plain language,
no jargon, no internal architecture. (Working-backwards: decouples "what's wanted" from
"what we currently build.") Optional for T1.

## Proposed solution
The approach and the **trade-offs you made** — not how to code it. A system-context note
(how this fits the existing system) where relevant. Degree of constraint: greenfield (wide)
or constrained by legacy (narrow)?

## Alternatives considered
Each rejected option + why it loses. *A spec with no alternatives wasn't designed.*

## Metric delta / success criteria
**Which measurable thing moves, by how much, measured how** (n, threshold, the query/command).
Post-ship and checkable.

## Cross-cutting concerns
Security, privacy, observability/telemetry, data/migration, cost/ops. Skip a line only if
genuinely N/A.

## Drawbacks · risks · hypothesis-invalidators
Honest costs. **Observable conditions that mean "roll this back"** — each must name HOW it
gets measured (no invalidator without a measurement plan).

## Wedge
**The narrowest first slice that delivers value.** One or two sentences. (Appetite: how much
time is this worth?)

## Open questions
What still needs a decision. Mark inline ambiguities `[NEEDS CLARIFICATION]`.

## Out of scope / accepted
Things consciously deferred or accepted as-is (from the grill's "acknowledge" bucket).
