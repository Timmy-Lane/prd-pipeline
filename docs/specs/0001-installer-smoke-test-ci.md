---
id: 0001
title: installer-smoke-test-ci
status: implemented
author: durden
created: 2026-05-30
---

> **Implemented 2026-05-30** (dogfood run of `/prd-pipeline`). Shipped: `tests/smoke.sh` (48 assertions, isolated temp envs, BSD+GNU portable) + `.github/workflows/ci.yml` (ubuntu+macos matrix). **Scope addition beyond the plan:** the smoke test surfaced a `bin/prd` refresh idempotency bug (blank-line accumulation); fixed it (2-line awk trailing-blank strip) and the test now asserts whole-file steady state. `bash tests/smoke.sh` → exit 0.

# Installer smoke-test + CI

> T1 one-pager. Produced by `/prd-pipeline` dogfooding itself.

## Problem / Context
`bin/prd` and `install.sh` are run via `curl | bash` and edit a user's `~/.claude/CLAUDE.md`, symlink onto `PATH`, and copy a skill into `~/.claude`. They have **zero automated tests and no CI**. A regression in the awk managed-block edit (e.g. losing the missing-`:end` guard), the symlink, or the dependency check could silently break installs — or worse, truncate a user's `CLAUDE.md`. Manual smoke-testing is the only safety net today, and it won't survive future edits.

## Goals
- A POSIX-sh **smoke test** run against a **fully isolated environment** — `CLAUDE_HOME`, `PRD_BIN_DIR`, **and `PRD_HOME`** all pointed at `mktemp -d` and **exported** so even `install.sh`'s clone and every child process stay off the real dirs. It asserts invariants by **checking file CONTENTS, not just exit codes** (exit-0 can hide a duplicated/truncated block):
  - `install → doctor → uninstall` round-trip leaves **no residue** (skill dir, rule, symlink, CLAUDE.md block all gone).
  - CLAUDE.md managed-block **insert → refresh (idempotent: exactly one marker pair, surrounding content byte-identical) → remove**.
  - The **missing-`:end`-marker guard** leaves CLAUDE.md **unchanged** (asserted on content) rather than truncating.
  - **Manual-mention branch:** a CLAUDE.md pre-seeded with a bare `prd-pipeline` string (no markers) is left **untouched**.
  - **Symlink:** after re-install, `$PRD_BIN_DIR/prd` resolves to the repo's `bin/prd`.
  - `install --project DIR` writes only `DIR/.claude/skills/` (no global writes).
  - **`install.sh` local-checkout path** runs (`./install.sh` from a clone → execs `bin/prd install`); the clone path is covered by pointing `PRD_HOME` at a temp dir.
- A **GitHub Actions CI** workflow on push + PR. **The ubuntu + macos matrix is non-optional** — BSD-vs-GNU `awk`/`sed`/`ln`/`mktemp` divergence is the headline bug class; dropping macos defeats the purpose.

## Non-Goals
- Testing `SKILL.md` *behavior* (that's a Claude-runtime concern, not shell-testable here).
- Publishing to a package registry; testing against a live Claude install; coverage of the skill's pipeline logic.

## Wedge
One self-contained `tests/smoke.sh` (runs `prd` against `CLAUDE_HOME=$(mktemp -d)`, asserts each invariant, non-zero exit on first failure) + a minimal `.github/workflows/ci.yml` that runs it on a matrix of ubuntu + macos.

## Success criteria
- `tests/smoke.sh` exits 0 on a clean checkout, on **both** ubuntu and macos in CI.
- CI green on push/PR; red when the smoke test fails.
- **Automated mutation case** (not a one-time manual check): a case deliberately removes the `:end` marker from a seeded block and asserts `prd install` leaves CLAUDE.md unchanged — so the guard stays proven every run.

## Drawbacks / risks / hypothesis-invalidators
- **Must never touch the real environment.** Test exports `CLAUDE_HOME` + `PRD_BIN_DIR` + `PRD_HOME` to temp dirs so `install.sh`'s clone and every child process stay isolated. *Invalidator: if a run mutates the real `~/.claude/CLAUDE.md`, `~/.local/bin/prd`, or `~/.prd-pipeline`, STOP and roll back.*
- **macOS vs Linux divergence** (BSD vs GNU `awk`/`sed`/`ln`/`mktemp`) is the headline risk — both OSes in CI, non-optional. *Invalidator: green on one OS, red on the other → not portable; fix before merge.*
- Rollback: delete `tests/` + `.github/workflows/ci.yml` — fully reversible; touches no existing file (README CI badge deferred).

## Out of scope / accepted
- README CI badge — nice-to-have, deferred.
- **`uninstall`'s `[ -L ]` guard** (grill OPEN-Q): a pre-existing *plain file* at `$PRD_BIN_DIR/prd` is deliberately left — don't delete what we didn't create. Intentional safety; the test asserts our symlink is removed and documents this.
