---
name: writing-prd
description: "Write or maintain a PRD — the product's stable, model-agnostic source of truth that a person or a fresh AI session reads first to get ~80% of the context in one pass: what the product is, what it does, and what it runs on. Use when asked for a PRD, a product doc, or a product spec, when bootstrapping `docs/` for a new product, when a fresh session keeps re-deriving the same product context, or when onboarding a human or agent to an existing product. Not for per-build decisions (that's writing-plans) or designing one feature (that's brainstorming)."
---

# Writing a PRD

A PRD is the product's **stable source of truth** — the durable record of what the product *is* and why it's shaped that way, captured once so neither a person nor a fresh AI session has to re-derive it. Its whole job is to be read *first* and hand over ~80% of the context in one pass. It is **not** a record of what you're building right now — that's the plan. If reading the PRD doesn't replace re-discovery, it isn't doing its job.

## When to use
- You're asked for a PRD, a product doc, a product spec, or "the doc that explains this product."
- You're bootstrapping `docs/` for a new product, or a fresh session keeps re-deriving the same product context.
- You're onboarding a human or an agent to an existing product.
- **Skip it** for one feature's design (that's **compound-v:brainstorming**), for per-build / how-to-build-it work (that's **compound-v:writing-plans**), and for a one-off script. Unsure of the effort? Route via **compound-v:using-compound-v**.

## The durable sections
Keep the whole thing to roughly two pages — if it doesn't fit, the scope is too broad, not the doc too short.

- **Problem & primitive** — the friction the product removes, anchored in something real, plus the one-sentence primitive the product is a consequence of ("the search result, from links to a cited answer"; "speculative editing"; "the sync engine"). Finding the primitive is **compound-v:startup-taste**'s job — record it here, don't re-derive it.
- **Goal** — what the product is, who it's for, and the one outcome it exists to deliver. Plain language, not a mission statement.
- **Core functions** — the handful of capabilities that define the product (the feature *spine*, not a backlog), one line each.
- **Non-goals** — what the product explicitly is *not* and won't do. Bounds scope, pre-empts the most common pushback, and survives a model upgrade because it encodes a human judgment a fresh model can't reconstruct. Include the **support boundary**: for inputs past the edge of scope, say what the product does — reject or escalate, not silently guess — because an unsure agent won't ask, it'll assume and proceed (a16z / Steinhardt).
- **Tech stack & architecture** — the languages, frameworks, and services it runs on, a one-sentence shape of the system, and the load-bearing design decisions. The slow-changing *what* and *why* — never the per-build *how*.

## What does NOT go here
Per-build content rots the stable doc on every feature — it stays in the **plan** (**compound-v:writing-plans**): the scope-cut for this build, the risks, the one verifiable ship signal, the approach, the task breakdown. Also keep out the **model name, exact prompts, and model-specific scaffolding** — those are the swappable execution layer the next model washes away (prompt sets are not PRDs). The test for any line: *would it still be true and useful against a clearly smarter model next year?* If an upgrade would force a rewrite, it doesn't belong here.

## Keep it the single source of truth
- **One PRD, edited in place.** Never a `prd-v2` or `PRD-final` fork — versioned forks are how the source of truth fragments. If the product is genuinely superseded, leave a one-line forward pointer instead of deleting.
- **Prune on a cadence.** A stale durable doc an agent trusts as fact is worse than no doc.
- **One fact, one home.** The PRD *links* to `AGENTS.md`, the plan, and the design spec rather than restating them (and they link back). See **compound-v:context-engineering** for the rot/maintenance mechanics — don't re-teach them here.
- **Entry point.** The PRD is read first for *product* context; `CLAUDE.md`/`AGENTS.md` points at it and holds *operating* context (build/test/run, code map, conventions); the plan holds the per-build decisions. No overlap means nothing goes stale by duplication.

## Writing discipline
Prose where precision matters — writing the sentence forces the thinking a bullet lets you skip. Cite or tag every load-bearing claim (`[ASSUMPTION]` when you're guessing); an unsourced magic number is a defect. Encode only what transfers across model generations. Keep it lean: if `CLAUDE.md` links it, you pay for it at every session start.
