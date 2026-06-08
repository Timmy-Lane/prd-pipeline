---
name: searching-patterns
description: Look up the canonical pattern and its matching anti-pattern from primary sources before writing unfamiliar or security-sensitive code, then feed both forward into the plan and the review. Use when about to write an unfamiliar API, a non-obvious or security-sensitive pattern, or pick a library/API shape; when unsure how a framework wants something done; or to confirm a best practice during a code review. Skip it for trivial, well-known code.
---

# Searching Patterns

Before writing something you're not sure about, find how it's *actually* done now — then carry back both the canonical pattern and the anti-pattern it replaces. Models confidently generate plausible-but-wrong or outdated API usage; a 60-second lookup against primary sources prevents a class of bugs and a round of review churn.

## When to search (and when not)

Search when getting it wrong is likely or expensive:

- **Unfamiliar API or library** — you haven't used this exact version, or you're choosing between libraries and need to see the real API shape.
- **Non-obvious pattern** — concurrency, caching, auth flows, retries, framework lifecycle hooks: areas where the wrong-but-plausible version compiles and then misbehaves.
- **Security-sensitive surface** — anything touching authn/authz, secrets, deserialization, SSRF, path handling, SQL. The cost of the wrong pattern here is a vulnerability, not a nit.
- **Confirming a best practice** during review — when you flag "this isn't how X is done," verify it instead of asserting it.

Don't search for trivial, well-trodden code you'd write correctly from memory (a loop, a standard library call, basic string handling). The lookup is overhead; spend it only where it buys correctness. This is the same instinct as catching an agent's architectural dead end early rather than nitpicking lines.

## How: read the primary source

The default tools need zero setup. Reach for the heaviest one that fits, lightest first:

- **Check the local convention first.** If the repo already has an established shape for this — a house wrapper, an AGENTS.md/CLAUDE.md rule, a pattern in neighboring files — that overrides the external canonical one. Match the local shape; don't import a clashing "correct" pattern. Only reach outward when the repo has no precedent. (AGENTS.md spec; Codex/Cursor system prompts: preserve an existing design system's established patterns.)
- **`WebSearch`** — find the current canonical page when you don't have the URL ("`<lib> <version>` retry middleware docs").
- **`WebFetch`** — read one known page (a docs section, a guide). The common case.
- **`gh`** — read the upstream repo directly: `gh api` for file contents, releases, or the `CHANGELOG`; `gh search code` to see how the library itself uses a thing. This is how you reach the *real* source and private/authed pages.

Prefer the library's own repo and docs over blog posts and forum answers — primary sources outrank secondary ones. **Pin the version**: default docs often render an older major than you're on, so read the docs for the version in your lockfile and note which version the pattern applies to. And don't stop at the first hit — the top search result is often a stale major or an SEO blog, so run a second query with different wording and prefer the result that matches your lockfile version. (Cursor's agent prompt: "look past the first seemingly relevant result"; run multiple searches with different wording, and include version numbers in technical queries.)

When the thing you're implementing ships an **official conformance suite** — a protocol, a wire format, a standard's test vectors — that suite *is* the primary source: precise, executable, and it doesn't drift the way prose docs do. Point the implementer at it and write code until those tests pass (Simon Willison; e.g. WebAssembly's spec test suite).

### When you must navigate: drive a real browser

`WebFetch` reads one static URL; it can't drive a JS-rendered site, page through multi-section docs behind interaction, or operate a repo UI. For that, reach for whatever **browser-automation tool your environment provides** — prefer one that works through the accessibility tree (stable element refs) over pixel-scraping.

The loop is snapshot-driven and tool-agnostic: **open** the page → **snapshot** the interactive elements (each gets a fresh ref) → **act** on a ref from *this* snapshot → **re-snapshot after anything that navigates or re-renders**, because refs go stale the moment the page changes. A typical lookup: open the docs or the canonical example in the upstream repo, snapshot to orient, read the section, then page through multi-section docs by re-snapshotting after each navigation.

## What to extract: pattern + anti-pattern + why

Don't just copy the snippet. A lookup is only useful if it captures three things:

1. **The canonical pattern** — the current, idiomatic way the library/framework intends it, with the version it applies to. APIs drift across majors, and default docs often render an *older* major than you're on — pin the lookup to the version in your lockfile and record it, so the implementer doesn't code the v2 shape against a v4 dependency.
2. **The matching anti-pattern** — the wrong-but-tempting version it replaces, and how to recognize it. This is what stops the same mistake recurring; the canonical pattern alone doesn't inoculate against the trap.
3. **Why** — one line on what the right way buys (avoids a race, preserves the cache, closes an injection path). The reason generalizes to cases the example didn't cover.

Then *use* both:

- **Feed it into the plan.** Write the canonical pattern (with its source) into the implementation plan so the implementer codes from the real shape, not a guess.
- **Feed it into the review.** Hand the anti-pattern to compound-v:recheck as a *named, checkable* item, not a vibe. Worked end-to-end: you looked up SQL access in the **v4.2** docs (the version in your lockfile, not whatever default the docs rendered) → found the trap: a string-interpolated query is an injection hole, and v4.2's canonical form is a parameterized query → record both with the version → that becomes a concrete recheck assertion — "does the diff build any query by string interpolation?" — which turns a vague best-practice opinion into a test the review can actually run *against the right API*.

Designing your own tool's API (an MCP tool, a CLI an agent will call)? That's a different problem — see compound-v:designing-agents for the agent-computer-interface rules.
