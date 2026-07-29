# STATE — prd-pipeline — rewritten 2026-07-28

## Goal
Every skill on this machine either ships in a plugin or symlinks into a git clone, so nothing is a
hand-copy that rots. Three upstream PRs merged. No skill listed twice.

## Done
- Marketplace manifest fixed and pushed (`8e66c98`). `"source": {"source":"git"}` is not a legal
  plugin source — only `url` and `git-subdir` are. compound-v now uses `url`; silver is out until
  its manifest reaches `master` (silver#2). evidence: `claude plugin validate .` -> "Validation passed".
- Plugins now: prd-pipeline 1.0.0, compound-v 0.5.0, bad-research 0.1.1. The 0.3.0 -> 0.5.0 jump
  dropped the folded `compound-v:prd-pipeline`, so installing prd-pipeline closed the gap rather
  than duplicating it. evidence: a fresh `claude -p` skill listing shows `prd-pipeline:prd-pipeline`
  once and no `compound-v:prd-pipeline`.
- **All five loose skills are now symlinks into their source clones**, plus the four silver
  commands. Old copies moved to `~/.claude/backups/skills-pre-symlink-20260728-195748` (nothing
  deleted). Proof the copies were rotting: `~/.claude/skills/silver/skill-data/core/SKILL.md` was
  3 days behind its clone and missing the `silver.json` privilege-escalation fix.
  | link | target |
  |---|---|
  | silver | `~/Documents/GitHub/silver/silver` |
  | superdesign | `~/Documents/GitHub/prd-pipeline/plugins/superdesign/skills/superdesign` |
  | founder-distribution, handoff | `~/Documents/GitHub/compound-v/skills/*` |
  | workflow-investigation | `~/Documents/GitHub/workflow-investigation/skills/workflow-investigation` |
  evidence: a fresh `claude -p` session lists all five — symlinked skill dirs load fine.
- `~/.claude/scripts/update-skills.sh` — checks every symlink, pulls each source clone, updates the
  marketplaces, exits 1 on drift. evidence: run shows 9/9 links ok and names the two clones that
  cannot pull.
- Russian removed from everything the model reads: the `handoff` description and the CLAUDE.md
  config map. **Deliberately kept** in `hooks/verify-claim.sh` and `hooks/secrets-guard.sh` — those
  are grep, and grep does not translate; dropping the Russian alternatives blinds both guards.

- **founder-distribution is now grounded.** It was the only skill in compound-v dense with empirical
  claims and no `references/sources.md` entry, while its own honest-warrant section demanded three
  warrant tiers. A full-route bad-research run (10 parallel fetchers, 14 sub-questions, 164 sources,
  ~200 verbatim-grounded claims) produced a `## founder-distribution` section, appended to
  `~/Documents/GitHub/compound-v/references/sources.md` (+54 lines, uncommitted).
  **Three of its nine claims do not survive as written:** "several scaled to millions with no push
  feature at all" (no supporting instance exists), "almost every company got its first thousand from
  one channel" (Traction prescribes parallel testing first and addresses a later stage entirely), and
  the gate rule's non-transferability condition (Gmail, Clubhouse and Robinhood all violate it). Two
  more are contradicted outright: "the highest-friction users drown first" and "fix retention before
  optimizing acquisition" (Ehrenberg-Bass: the belief is held "without any evidence").
  Only `brainstorming` and `handoff` now lack a sources entry, and both are pure procedure.
- Engine bug found and worked around: `bad funnel-gather` exits 0 but its search fan-out ignores the
  plan and returns junk (Google login pages, an IELTS test). `bad fetch <url>` and `bad search` are
  separately unreliable — `search` reported 15 notes while `research/notes/` held 164 files. File the
  bug in `LeventySeven/badresearch`, not here.

## Next
1. `cd ~/Documents/GitHub/silver && git push -u origin feat/claude-code-plugin` — that branch tracks
   no remote, so the silver skill currently cannot be updated by anything.
2. `cd ~/Documents/GitHub/compound-v` — commit two things into PR #9: the `skills/handoff/SKILL.md`
   frontmatter edit (English trigger + `argument-hint`) and the new `references/sources.md` section.
   Until they are committed, update-skills.sh skips that clone. Then decide whether to apply the
   rewrites the section recommends to `skills/founder-distribution/SKILL.md` itself — the grounding
   is done, the edit to the skill body is not.
3. Merge the remaining two PRs (see Do not for which repos need a fork+PR):
   compound-v#9, silver#2, workflow-investigation#2.
4. **After compound-v#9 merges and compound-v updates**, delete the `founder-distribution` and
   `handoff` symlinks — the plugin will ship both and they would list twice.

## Open decisions
- workflow-investigation PR: the BAD_GUIDE sweep wording. The old repo copy said "two copies, read
  both", the installed copy said "only one on this machine". Shipped compromise: read `guidesfm/`,
  also read a standalone `BAD_GUIDE.md` if present, prefer `guidesfm/` on disagreement. Confirm or
  correct in the PR.

## Verify with
```bash
bash tests/smoke.sh && bash tests/bundle-consistency.sh && claude plugin validate .
~/.claude/scripts/update-skills.sh
```

## Do not
- Do not copy a skill into `~/.claude/skills/`. Symlink the clone. Every copy here has gone stale.
- Do not `git push` to `LeventySeven/compound-v` or `LeventySeven/silver`: Timmy-Lane has
  `push: false` on both. Use the existing `fork` remote + a PR. **`LeventySeven/workflow-investigation`
  is the exception — Timmy-Lane has `push: true, triage: true` there and can merge its own PRs.**
  Check with `gh api repos/<owner>/<repo> --jq .permissions` rather than assuming; the old blanket
  "no push to any LeventySeven repo" rule in this file was wrong and cost a round trip.
- Do not put workflow-investigation in a marketplace. Private, internal repo; npx only.
- Do not re-vendor compound-v. That is what pinned it at 0.3.0 while upstream reached 0.5.0.
- Do not list a plugin whose source repo lacks `.claude-plugin/plugin.json` on its **default
  branch**. A manifest that only exists on an open PR branch is not installable, and
  `claude plugin validate .` will not catch it — it checks the source shape, not that it resolves.
