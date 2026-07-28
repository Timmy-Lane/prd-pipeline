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
- Marketplace manifest was **invalid** and nothing new could install from it. `"source": {"source":
  "git", ...}` is not a legal plugin source — the legal object forms are `url` and `git-subdir`
  (see `~/.claude/plugins/marketplaces/claude-plugins-official`). compound-v switched to `url`;
  silver dropped, because its `master` still has no plugin manifest (that is silver#2, unmerged) so
  the entry advertised an install that 404s. evidence: `claude plugin validate .` -> "Validation
  passed" (was "Found 2 errors"), `bash tests/smoke.sh` -> 115/115, `bash tests/bundle-consistency.sh`
  -> "bundle consistent". Uncommitted — commit and push before step 2, the installer reads the
  pushed clone, not this tree.

## Next
1. Commit + push the marketplace fix, then `claude plugin marketplace update prd-pipeline`.
   Nothing below works until origin/main carries a manifest that validates.
2. `claude plugin install prd-pipeline@prd-pipeline` (installs 1.0.0), **then**
   `claude plugin update compound-v@prd-pipeline` (0.3.0 -> 0.5.0). That order, because the
   installed compound-v 0.3.0 still carries the folded `compound-v:prd-pipeline` skill; updating
   first leaves a window with no pipeline, installing first leaves a brief duplicate.
3. Merge the three PRs (no push rights to LeventySeven from this machine — see Do not):
   compound-v#9, silver#2, workflow-investigation#2. silver stays out of the marketplace until #2
   merges; founder-distribution and handoff stay local until #9 merges.
4. After 2 and 3: `~/.claude/skills/superdesign` is a byte-identical duplicate of
   `plugins/superdesign/skills/superdesign` (`diff -rq` -> empty) and can go once
   `superdesign@prd-pipeline` is installed. **Do not delete founder-distribution or handoff** —
   they ship in no plugin today; they arrive only with compound-v#9. Leave
   `~/.claude/skills/{silver,workflow-investigation}` alone; both stay non-plugin installs.

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
- Do not list a plugin whose source repo does not carry `.claude-plugin/plugin.json` on its default
  branch. A manifest that only exists on an open PR branch is not installable, and
  `claude plugin validate .` will not catch that — it checks the source *shape*, not that the
  target resolves. Check with `gh api repos/<owner>/<repo>/contents/.claude-plugin` first.
