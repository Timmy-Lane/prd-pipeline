# Compound V — Skill Format Constitution

The authoritative spec for writing a Compound V skill. Lean by construction: if a line gives <5%
lift, it does not belong. This file is itself the example — short, dense, every rule earns its place.

## Frontmatter (required)

```yaml
---
name: <kebab-case>            # ^[a-z0-9-]+$, ≤64 chars, matches the directory name
description: <Imperative WHAT it does, one clause>. Use when <concrete triggers / intents / phrasings>, even if <the user doesn't name it>.
---
```

- `name` and `description` are the only required keys. Optional, rarely needed: `license`,
  `allowed-tools`, `metadata`. Any other key fails validation.
- **Ruling A — description = WHAT + WHEN, never the workflow.** State what the skill does + when to
  reach for it + searchable keywords. Be slightly *pushy* ("…even if not asked") to fight
  under-triggering. **Never** summarize the steps/flow — a description that encodes the workflow makes
  the model follow the description and skip the body (superpowers' #1 tested failure). Third person.
  ≤1024 chars; aim for 1–2 sentences.

## Body structure (target ≤250 lines; hard ceiling 500)

```
# Skill Name
One-sentence core principle.

## When to use            ← bullets with concrete symptoms + a "skip it when" line
## <the substance>        ← the actual technique/gates/checklist (the bulk)
## Red flags (optional)   ← two-column table ONLY for discipline skills with real failure modes
```

- **Progressive disclosure.** Keep the body lean; push heavy reference (>100 lines) or reusable code
  into `references/` or `scripts/` and point to it with a one-line "read X when Y". Don't pre-load
  what's only sometimes needed — that is context-engineering applied to the skill itself.
- **One excellent example beats five mediocre ones.** Pick the most relevant language; make it real
  and runnable, not a fill-in-the-blank template.

## Authoring checklist (the rules the kit follows but rarely states)
- **Description = WHAT + WHEN, never the steps** — Ruling A above is the single most load-bearing
  authoring rule; encoding the flow makes the model follow the description and skip the body.
- **Refs one level deep.** A SKILL points to `references/x.md`; that file does not point to a third
  hop the model has to chase. Any reference material over ~100 lines lives outside the SKILL (see
  progressive disclosure) — a long doc in the body burns context on every load whether it's needed
  or not.
- **One default, not a menu.** Give the recommended path; mention an alternative only when the choice
  is real and the trade-off is named. A menu makes the model pick (often wrong); a default makes it act.
- **Consistent terminology.** Pick one term per concept and reuse it verbatim across the SKILL and
  its refs — synonyms read as distinct things and dilute retrieval.
- **Match specificity to fragility.** Rigid step-by-step gates only for documented failure modes
  (verification, design-before-code, root-cause-before-fix); everywhere else give the reasoning and
  trust judgment (Ruling C). Over-specifying a robust step is the same defect as overkill.
- **Mind validation.** `name`/`description` are the only required keys; any other top-level key fails
  validation. `name` must match `^[a-z0-9-]+$`, ≤64 chars, and equal the directory name.

## Ruling B — tier-routing is the anti-overkill law
Match effort to the task. A trivial change never triggers the full pipeline. The router
(`using-compound-v`) owns the tier table; every workflow skill respects it and routes *down* when
unsure. Overkill is a defect, not a safety margin.

## Ruling C — explain *why*, not all-caps MUSTs
Today's models have good theory-of-mind; a reason generalizes where a rigid rule overfits. Reserve
hard gates for documented failure modes (verification, design-before-code, root-cause-before-fix).
Everywhere else: give the reasoning and trust judgment. All-caps ALWAYS/NEVER is a yellow flag.

## Flowcharts — only when they earn it
Use a small graphviz `dot` flowchart ONLY for a non-obvious decision or a loop where the model might
stop too early. Conventions: `diamond` = question, `box` = verb-action, `octagon` = STOP,
`doublecircle` = entry/exit; label edges yes/no. **Never** put code, reference material, or linear
steps in a flowchart — use lists/tables/code blocks for those.

## Cross-referencing other skills
Refer by name with an explicit marker: `**REQUIRED:** Use compound-v:recheck`. Never use `@path`
links — they force-load the file and burn context before it's needed.

## The no-bullshit / no-overkill bar (apply to every skill before shipping)
- **Target is Opus 4.8.** Write for a model with strong theory-of-mind — do *not* pad for weaker
  ones. No Iron-Law liturgy, no rationalization tables, no all-caps reinforcement walls. And no
  mandatory pressure-test-before-every-edit gate: that ceremony would turn a one-line deepen into a
  multi-day exercise and break the kit's ship-in-hours discipline. Test a *new* skill or a risky
  change; don't gate every word.
- Every section answers: would a senior engineer be *worse off* without it? If not, cut it.
- No ceremony, no triple-reinforced rationalization walls, no dated "in session X we…" narratives,
  no motivational filler, no model cost-tiering (we run Opus 4.8).
- Estimate work in hours/days, never weeks/months — and never let a skill imply otherwise.
- Every claim of fact traces to a real source. The grounding map is `references/sources.md` — it
  maps each load-bearing numeric/factual claim to its public primary URL and marks the recipe-knob
  judgment calls that need none. If a number isn't in that map, add a row citing its primary source
  (a real URL) or cut it; if you can't ground it, mark it clearly as a judgment call.
