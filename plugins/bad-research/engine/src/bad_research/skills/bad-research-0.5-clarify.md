---
name: bad-research-0.5-clarify
user-invocable: false
description: >
  Step 0.5 of the Bad Research pipeline — a triage-tier, default-proceed
  clarifier (≤3 questions) that runs before decompose and writes
  research/clarify.json (action + ≤3 questions + a distilled brief) — the brief
  sharpens the scaffold that step 1 decompose then reads.
---

# Step 0.5 — Clarify (triage tier, default-proceed)

**Tier gate:** Runs first on every interactive run. SKIP only when the run is
`--auto` or wrapped — i.e. when `research/wrapper_contract.json` exists or
`--auto` is set (the wrapper/GOSPEL query is binding and must not be
questioned). Note: the `route` (incl. `fast`) is not yet known here —
it is decided at step 1.5, *after* this clarifier — so 0.5 cannot key off the
route. On a clean interactive run it always runs first.

**Goal:** spend one cheap triage-tier (Haiku-class) decision to avoid a wasted
run on a misread query. Fire a clarification ONLY on genuine ambiguity;
otherwise proceed silently and distill a clean `brief`.

## Recover state

The orchestrator bootstrap has produced:
- `research/scaffold.md` — vault_tag, modality, wrapper requirements
- `research/query-<vault_tag>.md` — canonical research query (GOSPEL)

Read both. If `research/wrapper_contract.json` exists OR the run is `--auto`,
write `{"action":"proceed","skipped":"wrapper/auto"}` to `research/clarify.json`
and exit immediately — do NOT question a binding query.

## Procedure

1. Read the verbatim query end to end.

2. Decide `clarify | proceed` using this rule (a triage-tier judgement, ONE call):

   **Clarify (emit 1–3 questions) ONLY if the query has:**
   - ambiguous acronyms or names with multiple plausible referents (which "Mercury"? the planet, the element, the car, the Freddie?)
   - unbounded scope ("tell me about X" with no constraint, time window, or angle)
   - an undefined time window where the answer materially depends on it

   **DEFAULT TO PROCEED.** If you do not recognize a concept or name, assume it
   is a browsing request and proceed — do NOT ask the user to define it. Never
   ask more than **3** questions. When in doubt, proceed: a wrong clarification
   costs a round-trip; a missed one costs at most a slightly-wider search.

3. Distill the `brief` — a 1–3 paragraph paraphrase of the research question
   with scope + constraints made explicit. This is the clean handoff payload;
   it does NOT replace the GOSPEL query (the pipeline still cites the verbatim
   query everywhere), it sharpens the scaffold.

4. Write `research/clarify.json`:
   ```json
   {
     "action": "clarify" | "proceed",
     "questions": ["...", "..."],
     "brief": "<1-3 paragraph distilled research question with scope + constraints>"
   }
   ```
   `questions` is `[]` when `action == "proceed"`, and at most 3 entries otherwise.

5. If `action == "clarify"` AND the run is interactive: surface the questions to
   the user, collect answers, append them to `research/query-<vault_tag>.md`
   under a `## Clarifications` section (the answers become part of GOSPEL), then
   re-run this decision once. After one round, always proceed.

6. Append the `brief` to `research/scaffold.md` under a `## Brief` subsection.

## Exit criterion

- `research/clarify.json` exists with a valid `action`
- If `clarify`, at most 3 questions; if interactive, answers folded into the query file
- `research/scaffold.md` has a `## Brief` subsection

## Next step

Return to the entry skill (`bad-research`). Invoke step 1:
`Skill(skill: "bad-research-1-decompose")`.
