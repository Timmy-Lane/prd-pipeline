# STATE — prd-pipeline — rewritten 2026-07-28

## Goal
prd-pipeline installed as a standalone plugin, three upstream PRs merged, and no skill
listed twice in the session.

## Done
- prd-pipeline 1.0.0 pushed (`95fb5f4`). Standalone plugin, doc-routing + one-document-per-change,
  run log for compaction recovery. Marketplace = 5 plugins (prd-pipeline, compound-v, bad-research,
  silver, superdesign); compound-v is pulled live, no longer vendored at a stale 0.3.0.
  evidence: `bash tests/smoke.sh` -> "All 115 assertions passed"; `bash tests/bundle-consistency.sh`
  -> "bundle consistent"
- Duplicate `~/.claude/commands/workflow-investigation.md` deleted, and the local skill copy no
  longer hardcodes `/Users/admin`. evidence: `grep -c /Users/admin ~/.claude/skills/workflow-investigation/SKILL.md` -> 0

## Next
1. Merge the three PRs (no push rights to LeventySeven from this machine — see Do not):
   compound-v#9, silver#2, workflow-investigation#2.
2. `/plugin marketplace update prd-pipeline` then `/plugin install prd-pipeline@prd-pipeline`.
   **Order matters:** the marketplace has `autoUpdate: true`, and compound-v no longer carries the
   prd-pipeline skill. If the auto-update lands before the install, there is a window with no
   pipeline at all.
3. Only after 2 succeeds: `rm -rf ~/.claude/skills/{silver,superdesign,founder-distribution,handoff}`
   — those five now ship inside plugins and would otherwise list twice. Leave
   `~/.claude/skills/workflow-investigation` alone; it stays an npx install by design.

## Open decisions
- workflow-investigation PR: the BAD_GUIDE sweep wording. The old repo copy said "two copies, read
  both", the installed copy said "only one on this machine". Shipped compromise: read `guidesfm/`,
  also read a standalone `BAD_GUIDE.md` if present, prefer `guidesfm/` on disagreement. Confirm or
  correct in the PR.

## Verify with
```bash
bash tests/smoke.sh && bash tests/bundle-consistency.sh
```

## Do not
- Do not try to `git push` to any `LeventySeven/*` repo: `gh` is authenticated as Timmy-Lane only
  and no SSH key is authorized -> 403. Use `gh repo fork` + `gh pr create -R LeventySeven/...`.
- Do not put workflow-investigation in a marketplace. Private, internal repo; npx only.
- Do not re-vendor compound-v. That is what pinned it at 0.3.0 while upstream reached 0.5.0.
