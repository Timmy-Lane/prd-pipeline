# Research synthesis — best-in-class PRD-driven, plan-confirmed, parallel-agent development

> Self-driven targeted research, 2026-05-30. Feeds the design of the `prd-pipeline` global skill + rules.
> Sources cited inline; full list at bottom. This is reference material, not the skill itself.

## 1. Synthesized spec/PRD skeleton (union of what the best processes converge on)

Drawn from Google Design Docs, Amazon PR-FAQ, Rust RFC, Oxide RFD, GitHub spec-kit, ADRs, and the project's own PRD template. **Bold = universal; the rest are include-when-relevant.**

| Section | Purpose | Origin |
|---|---|---|
| **Title + metadata** (id, status, author, date, supersedes) | Index + lifecycle tracking | Oxide RFD frontmatter, project PRD frontmatter |
| **Problem / Context & Scope** | What's broken/missing now, anchored in observable evidence. Background facts. | Google "Context and Scope"; project "Problem" |
| **Goals & Non-Goals** | What this achieves + explicitly what it won't | Google; near-universal |
| Customer/press-release framing (1 para) | Working-backwards: describe the win in plain user language, no jargon | Amazon PR-FAQ |
| **Proposed solution / design** | The approach + trade-offs made (not how-to-code) | Google "The Actual Design"; Rust "Guide-level explanation" |
| Metric delta / success criteria | Which measurable moves, by how much, measured how | project PRD; spec-kit acceptance criteria |
| Alternatives considered | Rejected options + why; shows the space was explored | Google; Rust "Rationale and alternatives"; ADR |
| Cross-cutting concerns | Security, privacy, observability, data, cost, ops | Google "Cross-cutting concerns" |
| **Drawbacks / risks / hypothesis-invalidators** | Honest costs; observable conditions that mean *roll back* | Rust "Drawbacks"; project "Hypothesis invalidators" |
| **Wedge / first slice** | Narrowest slice that delivers value | project PRD; Shape Up appetite |
| Open / unresolved questions | What still needs a decision | Rust "Unresolved questions"; spec-kit `[NEEDS CLARIFICATION]` |
| Degree of constraint | Greenfield (wide) vs legacy (narrow) solution space | Google |

**Rule of thumb on length:** Amazon PR-FAQ ≤ 1 page PR + 2-5 pages FAQ; project rule "two pages or split it." A spec that doesn't fit on ~2 pages is too broad or padded.

## 2. Lifecycle + gates (synthesized state machine)

```
draft ──(grill survives + plan confirmed)──▶ accepted ──(shipped)──▶ implemented
  └─(killed)─▶ abandoned          accepted ──(decision changed)──▶ superseded
```

- **draft** — being written; sections may be empty; NOT safe to implement (project; Oxide `ideation`/`discussion`).
- **accepted** — survived the grill, plan locked + human-confirmed; ready to implement (project; Rust FCP "merge").
- **implemented** — shipped; lives as the record of what was decided and why (Oxide `committed`).
- **superseded / abandoned** — decision changed or dropped; never deleted, header links forward (Oxide `abandoned`; project append-only).

**Who/what gates each transition:**
- draft → accepted: the **grill** (adversarial review) must surface no must-fix blockers, AND a human must **confirm the plan** (the irreversible gate).
- accepted → implemented: verification + code review pass.
- Discussion happens on the artifact (Oxide does it in the PR; Rust in PR + FCP). For a solo+AI flow, "discussion" = the grill critics + the human plan-gate.

## 3. Highest-leverage practices worth copying

1. **Narrative over slides / "writing forces precision"** — Amazon banned PowerPoint for 6-pager memos; bullet points let you skip the hard thinking. *The PRD is prose, not a checklist.* [Amazon]
2. **Working backwards / customer-first** — write the win as the user would read it BEFORE designing; decouples "what users want" from "what we're good at building." [Amazon]
3. **"Warranted when 3+ ambiguity questions are 'yes'"** — Google's explicit test for *when* a design doc earns its cost (unsure of design? senior input valuable? contentious? cross-cutting concerns forgotten? legacy undocumented?). This is the **tiering trigger**. [Google]
4. **Alternatives-considered is non-optional** — a spec with no rejected alternatives wasn't really designed. [Google, Rust, ADR]
5. **Pre-mortem before committing** — imagine the plan already failed a year out, list causes; +30% risk identification, 20-30 min. The cheapest, highest-yield grill lens. [Klein, HBR 2007]
6. **One-way vs two-way door decisions** — irreversible (one-way) choices get heavy scrutiny + the human gate; reversible (two-way) choices flow fast. Calibrates how hard to gate. [Bezos / Amazon]
7. **Disagree-and-commit** — once the plan is confirmed, stop re-arguing scope; commit fully. [Amazon; mirrors project eng-review "commit fully once scope agreed"]
8. **Appetite, not estimate** — ask "how much time is this worth?" not "how long will it take"; fixed time, variable scope. Shapes the wedge. [Shape Up]
9. **Specs as the durable artifact** — code is the expression; the spec is institutional memory of *why*. [spec-kit; Google "reference points for future engineers"]
10. **Pre-implementation gates** — before any code: Simplicity / Anti-Abstraction / Integration-First checks; tests written + confirmed-failing + user-approved first. [spec-kit Phase -1]

## 4. Plan: authoring rubric + adversarial GRILL protocol + confirmation gate

### 4a. "Good plan" rubric (what an implementation plan must have)
- **Disjoint-file task partition** — each parallel task touches a non-overlapping file set; cross-cutting edits (config, schema, shared types, docs) serialize AFTER the parallel block. *This is what makes worktree-parallel safe.* [project eng-review; uzi/spec-kit `[P]` markers]
- Ordered phases with dependencies named; test plan (commands the reviewer runs); rollback/reversibility; risks + blast radius; observability hooks; data-migration handling; complexity tracking. [Google SRE; spec-kit; project]
- Right-sized diff: smallest diff that cleanly expresses the change — but don't compress a necessary rewrite into a patch. [project eng-review]

### 4b. GRILL = adversarial fan-out (parallel critics, distinct lenses)
Borrow bad-research's 4-critic pattern + the project's 3-agent grill. Each critic is INDEPENDENT and takes ONE lens — redundancy hides failure modes, diversity surfaces them:
- **Architecture/conflict lens** — contradicts an existing decision (ADR)? duplicates shipped scope? inconsistent with how the system works today?
- **Edge-case/invalidator lens** — invalidators named but not measurable? success criteria with no measurement plan? empty/null/race/restart/partial-failure/rate-limit/cap-exhaustion?
- **Cost/ops/telemetry lens** — cost math shown? operator knobs in the right place? telemetry to query it later? backwards-compat for existing rows?
- **Pre-mortem lens** — "it's a year later and this failed: why?" [Klein]
Run them in PARALLEL (the whole point — Nx faster). They find problems, they do NOT propose fixes (that's the next phase).

**Triage findings into 3 buckets:** (1) must-fix before `accepted`, (2) open-question (record in the spec), (3) acknowledge-and-accept (record in anti-goals/out-of-scope). Exit criterion: bucket 1 empty.

### 4c. Plan-CONFIRMATION gate (the one human gate that matters)
Borrow bad-research's step-1.6 plan-gate + Claude Code plan mode: **emit the plan (sub-tasks + per-task file scope + risks + rough cost/effort), then PAUSE for approve / edit / proceed.** No code touches disk before approval. [Claude Code plan mode: "reads files and proposes a plan but makes no edits until you approve"]
- Gate HARD on one-way-door / cross-cutting / schema / public-API / verdict-moving changes.
- Let two-way-door, reversible, single-file changes flow with a one-line heads-up.
- Record the decision in the spec frontmatter / a one-line decision log.

### 4d. What AI coding agents get RIGHT/WRONG about plan-then-execute
- RIGHT: plan-then-execute + human gate dramatically cuts "coding rabbit holes pursuing goals the design won't achieve" [Google]; spec-as-truth keeps multi-agent waves aligned without restarts [spec-kit/Augment].
- WRONG / failure modes to guard against: **plan drift** (implementation silently diverges from confirmed plan — re-anchor to the spec); **over-planning** (heavy spec for a two-way-door change — tier it down); **skipping the approval gate** (the single most common + most damaging failure — the gate is mandatory for Tier 2).

## 5. Parallel agents + git worktrees — the mechanism

**The single most important technique = git worktrees.** They solve the file-conflict problem completely and make merging straightforward. [Nimbalyst; AddyOsmani]

**Claude Code does this NATIVELY — no external tool required:**
- Agent tool `isolation: "worktree"` (or the `--worktree` launch flag) spins up a fresh worktree + dedicated branch under `.claude/worktrees/`, runs the agent there, **auto-cleans if unchanged**.
- Plan mode, memory, hooks, permissions, and the transcript all attach to the **worktree, not the original repo** — so two agents each have their own plan and never see each other's edits. [Claude Code docs]
- **The user's main tree never moves.** Verified in this repo: native worktrees create `worktree-agent-<id>` branches, `.claude/worktrees/` is gitignored and the branches are `locked`. The orchestrator (on the user's current branch) merges each agent's disjoint-file branch back with `git merge` — no `git checkout` on the user's side, ever.
- **Concurrency ceiling: 4-8 worktrees per developer reliably; above that you're bottlenecked on review, not on Claude.** [Claude Code worktree guides]
- **Operational gotcha (verified here):** 25 leftover locked worktrees had accumulated. Merge-back MUST be followed by explicit cleanup (`git worktree remove` + delete merged branch), else they pile up.

**OSS landscape (managers layered on the same git-worktree primitive — adopt only if a GUI/queue is wanted):**
- **Conductor** (Mac, melty labs) — visual dashboard + diff-first review, many Claude Code/Codex agents in parallel, each its own worktree.
- **Crystal** (MIT) — same, full source transparency for proprietary codebases.
- **claude-squad** — terminal-native, tmux + git worktrees.
- **vibe-kanban** (BloopAI, now community OSS) — kanban board over agent tasks.
- **uzi** (devflowinc) — CLI to run *large* numbers of agents in parallel worktrees, each with isolated deps.
- **container-use** (Dagger) — container-level isolation beyond worktrees.
> Decision: encode the **native Claude Code mechanism** (zero dependency, matches decision "pure Skill+Agent+git"). Mention these as optional GUIs.

**Spec-driven OSS for the PRD/plan layer (borrow ideas, don't hard-depend):**
- **GitHub spec-kit** (`specify` — already installed here): `constitution → specify → (clarify) → plan → tasks ([P] parallel markers) → analyze → implement`; explicit human-approval + pre-implementation gates.
- **OpenSpec** (Fission-AI): single living spec as authoritative reference, evolves with the codebase.
- **BMAD-METHOD**: multi-persona agents across the SDLC, file-based context passing, strict role boundaries.
- **Kiro** (AWS): requirements → design → tasks.

## 6. Tiering (when heavy spec vs one-pager vs nothing)

Maps Google's "3+ ambiguity yeses" + Bezos doors + Shape Up appetite + bad-research's route table:

| Tier | Trigger | Process |
|---|---|---|
| **0 — no spec** | Bug fix, refactor (no behavior change), docs, dep bump, prompt tweak measured vs existing eval, devops/CI. Two-way door, obvious solution. | Just do it: TDD + code-review. Skill exits fast. |
| **1 — light spec** | Small feature, single subsystem, mostly-reversible. <8 files, ≤2 new components. | One-pager spec + single grill pass + plan-gate (approve) + implement (worktrees if ≥2 disjoint tasks) + verify + review. |
| **2 — full spec** | New pipeline behavior, new DB table/column, new public API, cross-cutting, one-way door, verdict/outcome-moving. | Full PRD + adversarial grill (3-4 parallel critics incl. pre-mortem) + eng-review architecture lock-in (disjoint-file partition) + plan-gate (approve/edit) + parallel worktree implementation + verify + review + ship. |

RESPECT THE TIER — don't add ceremony to a Tier-0 fix; don't skip the grill/gate on a Tier-2 one-way door.

## 7. Anti-patterns / failure modes these processes guard against
- Coding rabbit holes pursuing goals the design won't achieve [Google]
- Security/privacy/observability oversights from skipping cross-cutting concerns [Google]
- Bullet-point thinking that skips the hard parts [Amazon]
- Plan drift, over-planning, skipping the approval gate [AI-agent SDD]
- Parallel agents colliding on shared files (cured by disjoint-file partition + worktrees)
- Worktree sprawl (cured by merge-then-cleanup discipline)
- Non-trivial feature with no spec; spec with no alternatives; invalidators with no measurement plan [project grill]

## Sources
- Design Docs at Google — https://www.industrialempathy.com/posts/design-docs-at-google/
- Amazon Working Backwards PR/FAQ — https://workingbackwards.com/resources/working-backwards-pr-faq/ ; https://commoncog.com / Bryar & Carr "Working Backwards"
- Rust RFCs — https://github.com/rust-lang/rfcs
- Oxide RFD 1 — https://rfd.shared.oxide.computer/rfd/0001
- Basecamp Shape Up — https://basecamp.com/shapeup (Betting Table ch.8; Set Boundaries ch.3)
- Gary Klein Pre-mortem — https://hbr.org/2007/09/performing-a-project-premortem
- GitHub spec-kit — https://github.com/github/spec-kit ; spec-driven.md
- OpenSpec — https://github.com/Fission-AI/OpenSpec ; BMAD-METHOD — https://github.com/bmad-code-org/BMAD-METHOD ; uzi — https://github.com/devflowinc/uzi
- Claude Code worktrees/plan mode — https://code.claude.com/docs/en/common-workflows ; https://code.claude.com/docs/en/agent-teams ; Nimbalyst worktree guides
- ADR (Michael Nygard) — https://github.com/joelparkerhenderson/architecture-decision-record
