---
id: 0003
title: prd-audit
status: implemented  # draft → accepted → implemented | abandoned | superseded
author: durden
created: 2026-06-04
supersedes:          # link the spec id this replaces, if any
---

# `prd audit` — spec-lifecycle consistency check + count summary

> **Implemented 2026-06-04** (dogfood run of `/prd-pipeline`). Shipped in `bin/prd`: a count-summary header + `--status` filter on `prd list`, and a new read-only `prd audit` (`--fix` for the single safe metadata fix, `--json`, `--stale-days N`). Smoke suite 84 → 115 assertions (CASE 17–23, incl. an isolated git fixture + a positive staleness case exercising the BSD/GNU date math). The wedge guard held: `prd audit` reports clean on the repo's own `implemented` specs (0001, 0002), confirming the git-check polarity is right.
>
> T1 one-pager. Produced by `/prd-pipeline` dogfooding itself. Extends `bin/prd`
> (one file) + `tests/smoke.sh`. Reversible, single subsystem.

## Problem / Context (required)
The repo now accumulates specs in `docs/specs/NNNN-<topic>.md` and the lifecycle
machinery in `skills/prd-pipeline/SKILL.md` reads each spec's `status:` frontmatter
(`draft → accepted → implemented | abandoned | superseded`) to drive recovery and the
Step 6 ship gate. Today there is **no way to see the shape of that corpus at a glance**
(`prd list` prints rows but no totals) and **nothing checks that a spec's declared
state is internally consistent or still true**. A spec can drift out of sync silently:
`status:` goes missing or unparseable (and the lifecycle machinery degrades to a manual
todo list — SKILL.md line 53-54 says so), an `id:` no longer matches its filename after a
manual copy, a `superseded` spec never links forward (violating the append-only rule at
SKILL.md:258-259), or an in-flight `feat/NNNN-*` branch ships while its spec stays
`draft`. These are caught today only by eyeballing — which won't survive more specs.

## Goals & Non-Goals (required)
**Goals**
- `prd list` gains a one-line **count summary** (total + per-status tally + `invalid`).
- New `prd audit` (read-only) flags lifecycle/consistency problems, grouped by severity,
  exiting non-zero on any ERROR (so CI and the existing smoke suite can gate on it).
- `prd audit --fix` applies the **one** genuinely safe metadata fix behind a `[y/N]`
  prompt; everything else prints a suggested manual action.
- `prd audit --json` emits machine-readable findings for hooks/CI.
- `prd list --status <s>` filters the listing to one status.

**Non-Goals**
- **No file deletion, ever.** Specs are append-only (SKILL.md:258-259). `audit` never
  `rm`s, never renames, never archives.
- No new config file (`.prdrc`). The single threshold is a CLI flag with a default const.
- No auto-mutation on a guess: `--fix` does not bump statuses, rename files, or invent
  `supersedes` targets.
- Not wired into `prd doctor` (doctor is about *install* health, not the spec corpus).

## Proposed solution (required)
Three additions to `bin/prd`, all reusing the frontmatter extraction already in
`cmd_list`/`cmd_new` (no third parser):

**A. Count summary** — folded into `cmd_list`'s existing per-spec loop as a header line:
`specs in docs/specs/ — total:N draft:n accepted:n implemented:n abandoned:n superseded:n invalid:n`,
where `invalid` = a spec whose `status` is missing or outside the vocabulary.

**B. `prd audit`** — read-only; iterates `docs/specs/*.md`, classifies findings:
- **ERROR — structure/dupes** (deterministic): missing/unparseable `status`; `status`
  not in `{draft,accepted,implemented,abandoned,superseded}`; missing `id` or `title`;
  duplicate `id` across files; `id` frontmatter ≠ the `NNNN` prefix in the filename.
- **ERROR — referential integrity**: `superseded` with no `supersedes:` value;
  `supersedes:` → an id with no matching file; a spec another spec's `supersedes:` points
  to that is itself not marked `superseded`.
- **WARN — git desync** (only the valid polarity; **skipped gracefully when not a git
  repo / git absent**): a `feat/NNNN-*` branch exists but the spec is still
  `draft`/`accepted` (forgotten status bump on in-flight work); `status: implemented` but
  the spec body has no `> **Implemented …**` marker (unverified claim — checked via the
  **body marker**, NOT branch existence, because the workflow deletes branches after merge
  so "implemented + no branch" is the success state, not an anomaly).
- **WARN — staleness**: `draft`/`accepted` older than `--stale-days N` (default 30, by
  `created:`) — a dangling unfinished PRD.

**C. `prd audit --fix`** — honest narrow set. The only auto-applicable fix, behind
`[y/N]`: a spec with frontmatter but no `status:` line → insert `status: draft` (the
documented initial state). Every other finding prints a **suggested manual action**
(rename the file / add the `supersedes` link / bump the status / pick up or abandon the
draft). Never mutates on a guess, never deletes.

Trade-off accepted: the `--fix` safe-set is deliberately tiny (one fix). "Safe auto-fix"
does not grow into status-bumping or file renaming, both of which need human judgment and
could corrupt the append-only record. The honest shape is *audit + one trivial fix +
actionable suggestions for the rest*.

## Metric delta / success criteria (required)
- `prd list` on a repo with specs prints exactly one summary header whose tallies sum to
  `total`; verified by a new smoke CASE asserting the header contents.
- `prd audit` on a fixture repo seeded with one spec of each finding type reports each
  finding and exits non-zero; on a clean fixture it prints "ok" and exits 0. Asserted by
  smoke CASES (read-only path + exit-code contract).
- `prd audit --fix` on a spec missing `status:` inserts `status: draft` after `y` and
  leaves the file otherwise byte-identical; declining (`N`) leaves it untouched. Asserted.
- `prd audit --json` emits parseable output (one object/line or an array) consumed in a
  smoke assert.
- `prd list --status draft` prints only `draft` rows.
- Full suite stays BSD+GNU green (`bash tests/smoke.sh` → exit 0), no banned primitives
  (`readlink -f`, `stat -f/-c`, `sed -i` without extension, `sha256sum`).

## Cross-cutting concerns (when relevant)
- **Portability:** git checks must degrade to "skipped (not a git repo)" when `.git` is
  absent or `git` is missing — same defensive posture as `latest_remote_tag`. Branch match
  anchors on the loose `NNNN` id (`feat/NNNN-*`), tolerating any slug suffix.
- **No network, no external state.** Pure local file + `git for-each-ref`/`branch` reads.
- **Test scaffolding:** the git-desync CASE needs an isolated `git init` + a `feat/NNNN-*`
  branch in a temp repo (the most setup of any case here — and now the most scoped-down).

## Drawbacks · risks · hypothesis-invalidators (required)
- Cost: ~120-180 lines added to a 14.9K bash file + new smoke CASES. Acceptable for T1.
- **Risk — false positives erode trust.** If `audit` cries wolf, people ignore it. The
  load-bearing guard is the git-desync *polarity*: we dropped "implemented but no branch"
  precisely because it would fire on every correctly-shipped spec.
  - *Invalidator → measured by → means roll back:* run `prd audit` against the current
    real `docs/specs/` (0001, 0002 — both `implemented`) → **if either implemented spec is
    flagged ERROR/WARN by a structural or git check** (measured: audit exit code + finding
    lines naming 0001/0002), the check set is wrong → revert that check before shipping.
- Risk — `--fix` over-reach. Mitigation: exactly one fix type, gated by `[y/N]`, asserted
  in tests that the file is otherwise byte-identical.

## Wedge (required)
Ship **A (count in `prd list`) + B (`prd audit` ERROR-class structural/referential checks
only)** first — that alone answers "how many PRDs and which are inconsistent" with zero
git dependency and the simplest tests. The git-desync WARN, staleness WARN, `--fix`,
`--json`, and `list --status` layer on after the wedge is green.

## Out of scope / accepted (when relevant)
- Wiring audit into `prd doctor`, `prd next` (next-action suggester), and a SessionStart
  stale-draft nudge — considered, deferred (YAGNI for this slice).
