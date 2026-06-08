---
name: finishing
description: Wrap up a completed branch — verify the full suite is green with fresh evidence, then present merge / PR / keep / discard options and execute the chosen one safely. Use when implementation is done and rechecked and you need to integrate or close out the work — phrases like "wrap this up", "merge it", "open a PR", "are we done here", "clean up the branch".
---

# Finishing

Confirm the work is actually green, then let the user choose how to land it — never auto-merge, never auto-discard.

## When to use

- All tasks are built and compound-v:recheck returned APPROVED.
- The user signals the work is done and asks how to integrate or close it out.
- Skip it when the work isn't finished or recheck hasn't returned APPROVED — finishing assumes a green, reviewed branch; route incomplete work back to compound-v:batched-implementation or compound-v:systematic-debugging instead.

## Step 1 — Verify green, fresh, yourself

Run the full suite this turn and read the exit code yourself — the **compound-v:verification-before-completion** gate, applied to integration: no merge/PR decision rides on "they passed earlier" or the implementer's word.

The finishing-specific rule: a red suite is **not** a finishing situation. **Stop**, surface the failure, and route back to **compound-v:systematic-debugging** — never present the finish menu on red, because every option below assumes a green branch.

## Step 2 — Present the options, let the user pick

Offer a small structured menu, not an open-ended "what now?":

1. **Merge locally** into the base branch.
2. **Push and open a PR.**
3. **Keep the branch as-is** (leave it for later).
4. **Discard** the work.

Pick the base branch deliberately (the branch this work forked from, usually `main`/`master`). State it so the user can correct it.

## Step 3 — Execute the choice safely

**Merge / PR:** run the merge (or push + `gh pr create`), then **re-run the suite on the merged result** — a clean merge can still produce a broken combination. If the merge hits a **conflict**, **stop and surface it** — resolve it deliberately (or hand it back), never `-X theirs`/`--force` your way through. The PR path needs the branch pushed first (`git push -u origin <branch>`) and `gh` authenticated; check both before `gh pr create` rather than after it fails. Green locally is not green in CI. After the PR is open, surface the remote check status (`gh pr checks --watch`) rather than declaring done at `gh pr create` — a merged-result suite you ran can still diverge from the repo's CI, and the branch isn't landable until those checks pass.

**The PR body is an artifact, not a title.** It carries: what changed and why; the **verification evidence** — the actual command you ran plus its result line (e.g. `pytest -q → 214 passed`), not "tests pass"; the recheck verdict (`APPROVED`); and any known follow-ups you deliberately deferred. A reviewer should be able to trust the branch from the body alone.

**Discard or any destructive cleanup:** require a **typed confirmation** ("type `discard` to confirm"). A yes/no is too easy to fire by reflex; destroying work needs a deliberate keystroke. Before destroying anything, show what's at risk: run `git status --short` and `git log --branches --not --remotes --oneline` (or `git log <base>..HEAD`) so the typed confirmation is *informed* — uncommitted changes, untracked files, and unpushed commits are the work that vanishes and cannot be recovered.

**Worktree cleanup order** (the footgun): merge → **`cd` out of the worktree** → remove the worktree → then delete the branch. Removing a worktree while you're inside it fails silently, and deleting the branch before removing its worktree errors. Only remove worktrees you created (under a gitignored `.worktrees/` or similar) — never one the harness owns.
