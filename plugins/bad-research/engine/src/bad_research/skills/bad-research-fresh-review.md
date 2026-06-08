---
name: bad-research-fresh-review
user-invocable: false
description: >
  Step 14.5 of the Bad Research pipeline (full tier only) — ONE fresh-context
  reviewer pass over the patched report (single pass, not a loop) that catches
  whole-report issues the in-context critics miss. Produces
  research/temp/fresh-review.json for the patcher to apply.
---

# Step 14.5 — Fresh-context review (single pass)

**Tier gate:** SKIP for `fast`. Runs for `full` only, after
the patcher (step 14), before polish (step 15).

**Goal:** spend ONE fresh reviewer pass to catch what the in-context critics
missed. The step-12 critics watched the report grow over a long context; a
fresh reader with no dispatch history reads it cold and catches drift. This is
the Anthropic/Devin "fresh-context review before ship" pattern — explicitly a
single pass, **not a loop** (a loop is the excluded grader-ensemble cost).

## Recover state

This step spawns a fresh-context reviewer subagent. The reviewer is tool-locked
to `[Read]` — it reports findings; it does NOT edit. Read for the spawn:
- `research/query-<vault_tag>.md` — GOSPEL query
- `research/prompt-decomposition.json` — required_section_headings, sub_questions
- `research/notes/final_report_<vault_tag>.md` — the patched report

## Procedure

1. Spawn ONE `bad-research-fresh-reviewer` subagent (fresh Opus, `[Read]` lock,
   no pipeline context). Standard 3-piece spawn contract:
   ```
   subagent_type: bad-research-fresh-reviewer
   prompt: |
     RESEARCH QUERY (verbatim, gospel):
     > {{paste research/query-<vault_tag>.md body}}

     PIPELINE POSITION: You are step 14.5 of the Bad Research pipeline — a
     fresh-context final reviewer. The report has been drafted, synthesized,
     critiqued, and patched. You read it COLD, with no memory of how it was
     built, and report whole-report issues the in-context critics missed.
     You are tool-locked to [Read]. You do NOT edit. After you return, the
     orchestrator applies surgical Edits for your critical findings, then
     step 15 polishes.

     PRE-READ PRIOR GENERATION (keyless cross-model proxy):
     BEFORE reading the report, write your own 3-sentence direct answer to the
     research query from memory alone. Record it in your working context. This
     is the keyless substitute for a true cross-model review — your a-priori
     answer stands in for an independent second model. THEN read the report end
     to end and flag every claim where your a-priori answer and the report's
     position diverge — these divergences are the highest-priority verification
     targets and must become `critical` or `major` findings.

     YOUR INPUTS:
     - query_file_path: research/query-<vault_tag>.md
     - report_path: research/notes/final_report_<vault_tag>.md
     - decomposition_path: research/prompt-decomposition.json
     - output_path: research/temp/fresh-review.json
   ```
   The reviewer reads the report once, end to end (this is the single pass),
   and emits findings to `research/temp/fresh-review.json`:
   ```json
   {"findings": [
     {"severity": "critical|major|minor",
      "kind": "drift|unanswered-subq|thesis-contradiction|structural|redundancy",
      "where": "<H2 heading or line region>",
      "issue": "<what is wrong>",
      "fix_hint": "<minimal surgical fix>"}]}
   ```

2. **Apply ONLY critical/major findings**, surgically, via `Edit` on the report
   (PATCH NEVER REGENERATE — the post-step-11 invariant holds). Minor findings
   are left for polish (step 15) to absorb. Do NOT re-spawn the reviewer; this
   is a single pass, not a loop.

3. If a critical finding requires a structural rewrite (not a surgical Edit),
   record it in `research/temp/fresh-review.json` as `applied: false` and note
   it — do not regenerate.

## Exit criterion

- `research/temp/fresh-review.json` exists
- All critical/major surgically-applicable findings applied via Edit
- The report was NOT regenerated; the reviewer ran exactly once (single pass)

## Next step

Return to the entry skill (`bad-research`). Invoke step 15:
`Skill(skill: "bad-research-15-polish")`.
