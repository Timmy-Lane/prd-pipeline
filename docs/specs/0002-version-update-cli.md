---
id: 0002
title: version-update-cli
status: draft        # draft → accepted → implemented | abandoned | superseded
author: durden
created: 2026-06-01
supersedes:
---

# Version-aware `prd` CLI + update notifications

> T2 full spec. The notify piece (a network check + a `settings.json` edit) breaks the
> README's current *"the only network operation is git clone/pull of this repo"* promise —
> a reputational one-way door — so the whole change is specced at T2 even though most
> sub-tasks are mechanically T1-simple.

## Problem / Context

`prd update` already exists (`git pull --ff-only` + reinstall), so the *mechanism* to pull
updates is solved. The gap is **awareness**: the CLI is version-blind.

Observable evidence in the current tree:

- `bin/prd` and `install.sh` contain **no version string** (`grep -i version bin/ install.sh`
  → nothing). `CHANGELOG.md` says `0.1.0`, but the running CLI cannot report it.
- **Zero git tags** (`git tag -l` → empty), yet `README.md` line 84 tells users to *"pin to a
  tagged release"* — a feature that does not exist.
- `prd doctor` reports install status but **not a version**, and cannot say whether a newer
  release exists.

So a user cannot answer "what version am I on?" or "is there an update?" without manually
running `prd update` and reading the diff. There is also no passive nudge: a user who
installed months ago has no signal that the skill they invoke every day is stale.

Two secondary defects this work must absorb because the new commands depend on them:

- **`REPO_ROOT` is not symlink-safe.** `bin/prd:12` computes
  `REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"`. Run through the installed
  symlink (`~/.local/bin/prd`), `BASH_SOURCE[0]` is the *symlink path*, not its target, so
  `REPO_ROOT` resolves to `~/.local` instead of the clone. Today this is masked because
  `install`/`update` are documented to run from the clone; the new commands (`version`,
  `update --check`, `notify`) are run through the symlink and **must** resolve the real clone.
- **"Version" has two referents.** The symlinked `prd` lives in the clone; the skill copied
  into `~/.claude/skills/prd-pipeline/` is a *separate* artifact that can be older. Without a
  drift check, `prd version` can report "latest" while the skill Claude actually loads is stale.

## Goals & Non-Goals

**Goals**

- A single source-of-truth `VERSION` file and a `prd version` command.
- `prd update --check` — an **active**, always-fresh check (`git ls-remote --tags`) that reports
  whether a newer release tag exists, without pulling.
- `prd doctor` reports **both** the clone version and the installed-skill version, and **warns on
  drift**.
- `prd new <topic>` and `prd list` — CLI ergonomics around specs, reusing the skill's existing
  `references/spec-template.md` as the single format source.
- `prd notify on|off` — **opt-in** passive update notification via a `SessionStart` hook.
- Release discipline: SemVer + annotated git tags (`vX.Y.Z`), starting at **0.2.0**.
- Symlink-safe path resolution so all of the above work when invoked through `~/.local/bin/prd`.

**Non-Goals**

- No package-registry publishing (Homebrew, npm, etc.). Distribution stays `git clone`/`git pull`.
- No auto-*apply* of updates — notification only nudges; the user still runs `prd update`.
- No telemetry, analytics, or any data **sent** anywhere. The only network call remains a read
  (`ls-remote`) against the user's own configured repo.
- No GitHub Releases API / third-party services (rejected below).
- Not changing the skill's pipeline/tier logic — this is CLI + packaging only.

## The win, in the user's words

> "I run `prd version` and see exactly what I have. When I open a Claude session, if a newer
> release is out, one line tells me — `update available: v0.2.0 → v0.3.0 (run: prd update)` —
> and nothing phones home unless I turned that on. `prd doctor` warns me if my installed skill
> drifted behind my clone. And `prd new auth-rate-limit` drops a correctly-formatted spec stub
> in `docs/specs/` so I'm not hand-copying the template."

## Proposed solution

**Versioning.** A `VERSION` file at the repo root (`0.2.0`) is the single source of truth.
`install` copies it into `~/.claude/skills/prd-pipeline/VERSION` alongside the skill. A release
is an annotated tag `vX.Y.Z` plus a `CHANGELOG.md` entry. `prd version` prints the clone's
`VERSION`. `prd doctor` reads clone `VERSION` *and* installed-skill `VERSION`, prints both, and
prints a drift warning when they differ (`installed skill v0.2.0 is behind clone v0.3.0 — run
prd install`).

**Symlink-safe paths.** Replace the `REPO_ROOT` computation with a portable symlink resolver
(loop over `readlink` until the target is not a symlink; no dependency on GNU `readlink -f`,
since macOS lacks it). All commands resolve the real clone whether invoked directly or via the
symlink. This is covered by a smoke-test case that invokes through a symlink.

**Active check — `prd update --check`.** Runs `git ls-remote --tags <repo-url>`, parses the
highest `vX.Y.Z` tag, compares against clone `VERSION` with a pure-bash SemVer compare. Always
fresh (the user explicitly asked). Prints `up to date (v0.2.0)` or `update available: v0.2.0 →
v0.3.0 (run: prd update)`. `--check` is a flag on `update` so the existing pull path is the
default and the check is the dry-run variant. Network failure degrades to a non-fatal
`could not check (offline?)` — never blocks.

**Passive notify — `prd notify on|off` + a `SessionStart` hook.** This is the sensitive part and
is built so the **default install touches `settings.json` zero times and makes zero network
calls.** Only an explicit `prd notify on` wires the hook.

- `prd notify on` inserts a `SessionStart` hook into `~/.claude/settings.json` whose command is
  the thin shim `prd notify --hook`. The edit is **marker-guarded and atomic** in spirit, but
  because `settings.json` is JSON (not line-oriented like `CLAUDE.md`), the merge is done by
  reading the file, splicing our hook entry into the `hooks.SessionStart` array, and writing
  atomically (temp file + `mv`). The exact `settings.json` hook schema will be **verified via the
  `update-config` skill before the JSON is written** — not reconstructed from memory. If the file
  is absent, create a minimal valid one. If it is present but unparseable, abort with a clear
  message rather than risk corrupting it.
- `prd notify off` removes only our hook entry (identified by the `prd notify --hook` command
  string), leaving every other hook intact.
- `prd notify --hook` is the runtime shim invoked by the hook at session start: it checks the
  opt-in flag, reads a disk cache (`~/.claude/.prd-update-cache`), and only if the cache is older
  than **24h** performs one `ls-remote` to the user's own repo, refreshes the cache, and prints at
  most one line. Cached/fresh → prints from cache with no network. Failure → silent (never breaks
  a session start).

**`prd new` / `prd list`.** `prd new <topic>` finds the next free `NNNN` in `docs/specs/`, copies
`references/spec-template.md`, fills `id`/`title`/`created`, and writes
`docs/specs/NNNN-<topic>.md`. It **reads the template from the installed/clone skill** — the CLI
never carries its own copy of the format. `prd list` scans `docs/specs/*.md` frontmatter and
prints `id · title · status`. Both operate on the current working repo's `docs/specs/`.

**Build partition (worktree mandate).** Every command lives in `bin/prd`, so the `bin/prd` edits
**cannot** be parallelized across worktrees — they are serialized in phase order
(version foundation + symlink-safe paths → `update --check` → `notify` → `new`/`list`). The
genuinely independent artifacts are parallelized in their own worktrees: `tests/` additions,
`README.md`+`CHANGELOG.md` doc edits, and the hook-template/`SKILL.md` note. Keeping `bin/prd` a
single self-contained file is a **conscious trade** against the "many small files" coding-style
norm — portability for `curl | bash` + a symlinked entry point outweighs splitting into sourced
libs (which adds symlink-relative `source` fragility).

## Alternatives considered

- **GitHub Releases API for the check.** Nicer payload (release notes), but it is an HTTP call to
  `api.github.com`, subject to rate limits and a third-party dependency — directly against the
  project's "only git over HTTPS to this repo" identity. Rejected.
- **`git fetch` + compare `HEAD` vs `origin/main` (no tags).** Simplest, but has no concept of a
  "release" — every commit reads as an update, so the notification would cry wolf on every WIP
  push. Rejected in favor of tags.
- **Opt-out (notify on by default).** Best convenience, but "network by default" contradicts the
  README promise and would surprise users. Rejected; chose **opt-in + 24h cache**.
- **Cache-only passive check (session never touches the network).** Maximum privacy, but the nudge
  only appears *after* some other command refreshed the cache — too lagging to be useful. Rejected
  in favor of opt-in network with a 24h cache.
- **Split `bin/prd` into sourced `bin/lib/*.sh` per command group** (to satisfy disjoint-file
  parallelism). Rejected: sourcing relative to a symlinked entry point is fragile and undercuts
  the single-file portability that makes `curl | bash` safe. Serialize the `bin/prd` edits instead.

## Metric delta / success criteria

- `prd version` prints the `VERSION` contents; **asserted in `tests/smoke.sh`** against a seeded
  `VERSION`.
- `prd update --check` against a **mocked** `ls-remote` (a local bare repo with a higher tag)
  prints `update available: … → …`; against an equal tag prints `up to date`. Both asserted.
- `prd doctor` prints two versions and emits the drift warning when the installed-skill `VERSION`
  is seeded behind the clone `VERSION`. Asserted on output content.
- `prd notify on` then `off` is **idempotent** and leaves `settings.json` **valid JSON** with no
  residual `prd` hook; a non-`prd` hook seeded beforehand survives untouched. Asserted (parse the
  JSON after each step).
- **Default `prd install` writes zero bytes to `settings.json` and makes zero network calls** —
  asserted (seed an absent/empty `settings.json`, run install, assert unchanged/absent).
- `prd new foo` creates `docs/specs/NNNN-foo.md` with a filled, template-matching frontmatter;
  `prd list` shows it. Asserted on a temp repo tree.
- A **symlink invocation** case: `prd version` invoked via `$PRD_BIN_DIR/prd` resolves the real
  clone and prints the version (guards the `REPO_ROOT` fix).
- CI green on **ubuntu + macos** (BSD vs GNU `awk`/`sed`/`readlink`/`mktemp` is the headline risk).

## Cross-cutting concerns

- **Privacy / "no phone-home" (load-bearing).** Default install: no `settings.json` edit, no
  network. Even with `notify on`, the only call is a read-only `ls-remote` to the user's own
  configured repo URL, capped at once/24h, sending no user data. The README Security/trust section
  **must** be rewritten from "the only network operation is git clone/pull" to state the opt-in
  `ls-remote`. This README edit is **in scope**, not polish (cross-artifact consistency gate must
  force it).
- **Settings.json safety.** JSON merge is riskier than the existing `CLAUDE.md` text-append: a bad
  merge corrupts user settings. Mitigations: verify schema first, parse-or-abort (never blind
  overwrite), atomic temp-file + `mv`, identify our hook by its command string for clean removal,
  and a smoke test asserting validity + non-`prd` hook survival.
- **Observability.** None added (no telemetry). The "signal" is the one-line stdout nudge only.
- **Cost/ops.** One `ls-remote` per day per opted-in user against their own repo. Negligible.
- **Supply chain.** No new dependencies; pure bash + git, consistent with the project.

## Drawbacks · risks · hypothesis-invalidators

- **`settings.json` corruption.** *Invalidator:* the smoke test parses `settings.json` after
  `notify on`/`off`; if it is ever invalid JSON or drops a pre-seeded foreign hook, STOP — do not
  ship the notify piece. The rest (version/check/new/list) can ship without it.
- **Network call breaks the README promise.** *Invalidator:* if any default-install path (no
  `notify on`) makes a network call or edits `settings.json`, that is a contract break — the
  zero-touch assertion above must stay green every run.
- **macOS vs Linux divergence** (no `readlink -f` on BSD; `awk`/`sed`/`mktemp` differences).
  *Invalidator:* green on one OS and red on the other in CI → not portable; fix before merge.
- **SemVer parsing in bash is fiddly.** *Invalidator:* a unit case feeds `v0.10.0` vs `v0.9.0`
  and asserts `0.10.0` is newer (string compare would get this wrong); if it fails, the compare is
  broken.
- **Rollback.** `version`/`new`/`list` are additive (new `case` arms + a `VERSION` file) — fully
  reversible. `notify` is isolated behind its own verb and removable via `notify off`; if it
  proves unsafe, drop the `notify` arms and the hook template without touching the rest.

## Wedge

**Phase 1 (the wedge): `VERSION` file + symlink-safe `REPO_ROOT` + `prd version` + `prd doctor`
drift report.** That alone closes "what version am I on?" and the latent symlink bug, is fully
additive, and unblocks everything else. Phases 2–4 (`update --check`, `notify on|off` + hook,
`new`/`list`) layer on top. Appetite: ship Phase 1 first; the notify phase gets the most scrutiny.

## Open questions

- Hook output channel: a `SessionStart` hook injects its stdout as session context. Confirm via
  the `update-config` skill that a one-line stdout nudge renders acceptably (vs. needing a
  specific JSON envelope). `[NEEDS CLARIFICATION — resolve during writing-plans via update-config]`
- Cache file location/format: `~/.claude/.prd-update-cache` as `last_check_epoch\tlatest_tag`.
  Confirm `~/.claude` is the right home vs. an XDG cache dir. (Lean: `~/.claude`, consistent with
  the rest of the tool.)

## Out of scope / accepted

- README CI/version badge — nice-to-have, deferred (consistent with 0001).
- Auto-applying updates, or prompting to update *within* a session — notify is read-only nudge.
- Multi-repo / fork awareness beyond the single configured `PRD_REPO_URL`.
- Windows support (the project is macOS + Linux today).
