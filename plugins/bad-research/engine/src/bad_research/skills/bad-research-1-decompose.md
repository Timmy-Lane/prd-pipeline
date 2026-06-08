---
name: bad-research-1-decompose
user-invocable: false
description: >
  Step 1 of the Bad Research pipeline — decomposes the canonical query into
  atomic items, classifies pipeline_tier + response_format, and writes the
  coverage matrix to research/prompt-decomposition.json.
---

# Step 1 — Prompt decomposition

**Tier gate:** Runs for ALL tiers. This step also classifies the tier itself.

**Goal:** before any research happens, decompose the user's prompt into its atomic items. This artifact is read by the instruction-critic in step 11 and by the draft sub-orchestrators in step 10 to make sure the pipeline doesn't drift from what was actually asked.

**Why this step exists:** the single dimension where the pipeline has the widest variance is whether the draft structurally mirrors the prompt. When the prompt asks "for each significant character, describe techniques / arcs / fate" and the draft produces per-character sections with those three fields in order — that's a structural match, high instruction-following. When the prompt asks the same thing and the draft organizes around thematic analysis — that's a structural mismatch, even if every fact is in there. The decomposition makes the structural requirement explicit, in writing, BEFORE drafting.

---

## Recover state

The orchestrator's bootstrap step (in the entry skill) has already produced:
- `research/scaffold.md` — vault_tag, modality, wrapper requirements
- `research/query-<vault_tag>.md` — canonical research query (GOSPEL)

Read both before starting. The vault_tag is in the scaffold's "Run config" section.

---

## Delegation

The orchestrator delegates the JSON extraction in this step to a **work-tier subagent** —
structured JSON production does not require frontier reasoning, so running it orchestrator-inline
at Opus rate is wasted spend. This mirrors the spawn pattern the step-5 depth investigators use.
Spawn:

```
Task(
  prompt: "Execute bad-research-1-decompose steps 1–9 exactly. Read research/scaffold.md and
           research/query-<vault_tag>.md, produce research/prompt-decomposition.json plus
           research/temp/coverage-matrix.md, append the Tier rationale to research/scaffold.md,
           then stop.",
  tier: "work",
  tools_allowed: [Read, Write, Bash],
  stop_conditions: "research/prompt-decomposition.json written (valid JSON) AND research/temp/coverage-matrix.md has zero Gap?=YES rows"
)
```

Then read `research/prompt-decomposition.json` back into orchestrator context before returning to
the entry skill and invoking the query-router (step 1.5). The router still owns the authoritative
`route` / `query_shape` decision — the work-tier subagent only produces the decomposition signals.

---

## Procedure

1. **Re-read the canonical research query** end to end (`research/query-<vault_tag>.md`).

2. **Walk through it and extract every atomic item** — anything that's a discrete thing the prompt named. These fall into categories:
   - **Sub-questions** — explicit or implicit questions the draft must answer ("What cues influence this?" → atomic: "cues influencing X")
   - **Named entities / categories** — every character, product, company, concept, time period, etc. the prompt names by name
   - **Required formats** — "mind map", "ranked list", "FAQ", "tabular", "scenario matrix", etc.
   - **Required sections** — "include X section", "end with Y", "begin with Z"
   - **Time horizons** — forward-looking spans: "through 2027", "next 12 months", "historical through 2010-present"
   - **Time periods (historical, period-pinned)** — backward-looking specific reporting periods that have a primary-source filing somewhere: "Q3 2024", "FY 2023", "9 months ended September 30, 2024", "as of November 17, 2025", "March 2024 equity raise". Different from time_horizons. Extract every one — they drive period-targeted searches in step 2 and a primary-source-coverage check in step 8. **Failing to extract these is the #1 cause of "agent had the topic right but missed the rubric's exact figures"**: the answer lives in the period-pinned filing the agent never fetched (10-Q, 10-K, statutory accounts, regulatory disclosure).
   - **Scope conditions** — "for non-academic contexts", "under SIL-4 constraints"

3. **Produce `required_section_headings`.** This is the single highest-leverage field for instruction-following scores. Ordered array of literal H2 heading strings the draft MUST emit in order. **Never leave this array empty** — an empty heading contract means the drafter invents its own structure, which systematically scores lower on IF because it never matches the evaluator's structural expectations. Population rule:
   - If the prompt contains enumerated asks (regex `\b\d[.\)]` such as "1)", "1." or leading phrase "List X, Y, Z" / "cover the following:"), produce one entry per enumerated item, in prompt order, with the prompt's verbatim noun-phrase as the heading slug.
   - If the prompt names N entities in a list and asks to "discuss", "analyze", "describe", or "evaluate" each, produce one heading per entity.
   - **Otherwise (narrative prompts):** generate headings from the sub-questions you extracted in step 2. Each sub-question becomes one H2 heading, phrased as a declarative topic ("## 1. Historical Context and Evolution", "## 2. Key Mechanisms and Drivers", etc.). For open-ended prompts ("Write about X"), derive 4-7 headings from the topic's natural analytical structure: background/context → core analysis (1-3 sections mapped to sub-questions) → comparative analysis → implications/future outlook. The headings don't need to quote the prompt verbatim, but they MUST cover every sub-question from step 2.

   Example (prompt: "Your report should: 1) List major manufacturers... 2) Include images... 3) Analyze primary use cases... 4) Investigate market penetration..."):
   ```json
   "required_section_headings": [
     "## 1. Major Manufacturers, Device Models, and Configurations",
     "## 2. Images of Representative Devices",
     "## 3. Primary Use Cases and Deployment Scenarios",
     "## 4. Regional Market Analysis"
   ]
   ```

4. **Write `research/prompt-decomposition.json`:**

```json
{
  "sub_questions": [
    "What is the specific question this addresses?",
    "..."
  ],
  "scope_brief": "One paragraph: the core subject, what the report will and will not cover, and the boundary conditions. The fast-mode writer reads this as its framing.",
  "entities": [
    {"name": "Bronze Saints", "type": "category", "required_fields": ["techniques", "arcs", "fate"]}
  ],
  "required_formats": [
    "mind map of causal structure",
    "5-tier support/resistance table"
  ],
  "required_sections": [
    "## Opinionated Synthesis (if wrapper_contract demands it)"
  ],
  "required_section_headings": [
    "## 1. Major Manufacturers, Device Models, and Configurations",
    "## 2. Images of Representative Devices",
    "## 3. Primary Use Cases and Deployment Scenarios",
    "## 4. Regional Market Analysis"
  ],
  "time_horizons": ["2010-present", "12-month forward"],
  "time_periods": [
    {"period": "Q3 2024", "type": "fiscal-quarter", "primary_source": "10-Q for the quarter ended September 30, 2024", "issuer": "ClearPoint Neuro"},
    {"period": "FY 2023", "type": "fiscal-year", "primary_source": "10-K for fiscal year ended December 31, 2023", "issuer": "ClearPoint Neuro"},
    {"period": "March 2024", "type": "event-anchored", "primary_source": "8-K disclosure or press release for March 2024 equity raise", "issuer": "ClearPoint Neuro"}
  ],
  "scope_conditions": ["urban rail specifically, not mainline"],
  "recency_window": "current",
  "pipeline_tier": "full",
  "response_format": "argumentative",
  "query_shape": "depth_first",
  "citation_style": "wikilink"
}
```

   **Author the `scope_brief`.** Write one tight paragraph naming the core subject, what the report will and will not cover, and the boundary conditions. The fast-mode writer reads this as its framing (it never sees the planner trace), so it must stand alone.

5. **Omit nothing the prompt names explicitly.** List every numbered ask, every named entity, every format cue as a separate atomic item, even if they feel redundant. The instruction-critic catches false-positive atomic items cheaply; it cannot catch false-negatives.

6. **Do NOT include wrapper-contract requirements here** — those live in `research/wrapper_contract.json` separately. The decomposition is ONLY about what the user's actual prompt named.

7. **Classify `pipeline_tier` and `response_format`.**

   **`pipeline_tier` is an initial tier *signal*, not the final routing decision.** It records this step's read of how much pipeline the query wants (`light` vs `full`). The authoritative routing decision — the `route` field (`fast` / `full`) that the orchestrator actually sequences from — is made downstream by the query-router (step 1.5), which reads this `pipeline_tier` as input and never down-routes a justified `full`. Set `pipeline_tier` honestly here; let step 1.5 own `route`.

   **`pipeline_tier`** — how much pipeline to run:

   | Tier | When to use | Signal words / patterns |
   |------|-------------|------------------------|
   | `"light"` | Query has a clear, bounded answer. Factual lookup, definition, simple explanation, short how-to, list/catalog, quick comparison, landscape overview, multi-entity survey. | "What is...", "How do I...", "List the...", "Define...", "Overview of...", "Compare X and Y", short-to-moderate prompts, single clear question or 2–5 sub-questions |
   | `"full"` | Deep analysis, synthesis of conflicting evidence, defended thesis, literature review, forecast with evidence chains. | "Analyze the impact of...", "Evaluate whether...", multi-paragraph prompts, explicit request for depth/rigor, research-grade questions, contested topics |

   **Default is `"full"`.** When uncertain, tier up. Running the full pipeline on a simple query wastes money; running the light pipeline on a complex query produces a bad report.

   **Survey vs. deep — the discriminator is the WORK, not the wording.** A query is a shallow breadth **survey** (→ `light` / `structured`) only when the work is *enumerating a set of independent options/entities*, where each item is one thing to characterize — e.g. "best tech stacks for a startup", "top 10 PM tools", "list the major cloud providers" (≈17 independent options, each gets a row). A query is **deep** (→ `full`) when the work is *investigating multiple facets of ONE subject and justifying recommendations* — e.g. "best tRPC patterns", "best practices for Kubernetes security", "best architecture for a real-time chat system" — even when phrased "best/top X". Here "best" introduces ONE subject whose ~8 facets must each be investigated and traded off, not a list of options to enumerate. The discriminator is **independent-options-to-enumerate (wide → survey/light)** vs **facets-of-one-subject-to-investigate (deep → full)**, NOT the superlative wording. If a "best/top X" query has a single core subject, it is deep — tier it `full`.

   **`response_format`** — how the output is shaped:

   | Format | When to use | Characteristics |
   |--------|-------------|----------------|
   | `"short"` | Direct answer, not a report. | 500–2000 words. 1–5 paragraphs. Tables/lists as needed. No Opinionated Synthesis section. Thesis up front, evidence follows. |
   | `"structured"` | Coverage across entities/topics. Scannability matters more than argumentative density. | 2000–5000 words. Scannable subsections. Breadth-first. Tables, bullets, visual devices liberally. Survey-style coverage acceptable. |
   | `"argumentative"` | Defended thesis, deep analysis, evidence-chain reasoning. | 5000–10000 words. Dense thesis-driven prose. "ARGUE, DON'T JUST REPORT" fully active. Required Opinionated Synthesis with all subsections. |

   **The two dimensions are independent.** Most common pairings:
   - `light` + `short` — factual lookup, definition, simple how-to
   - `light` + `structured` — list/catalog, quick multi-entity comparison, landscape overview
   - `full` + `argumentative` — deep analysis, literature review, forecast (the current default)
   - `full` + `structured` — comprehensive survey where adversarial depth still matters

   **`citation_style`** — how the final report handles source attribution:

   | Style | When to use | Output |
   |-------|-------------|--------|
   | `"wikilink"` | **Default.** Personal use in a vault — every citation is a clickable wiki-link back to the raw source note in `research/notes/`. | `[[note-id]]` markers inline. No separate Sources section (each link self-resolves to the source note's frontmatter title + URL). |
   | `"inline"` | Public deliverable, benchmark wrappers, or verifiable research report for someone outside the vault. | `[N]` inline citations + a formatted `## Sources` list at the end. |
   | `"none"` | Polished expert-analysis with no visible citation apparatus. | No citation markers, no Sources section. |

   **Wrapper override:** if `research/wrapper_contract.json` exists and specifies `citation_style`, it overrides the default. The benchmark harness sets `"inline"` via wrapper_contract so RACE evaluators can read numbered references; everything else gets the wikilink default.

7b. **Classify `query_shape`.** This is the fan-out *SHAPE* — how downstream investigators are *arranged* — and it is **orthogonal to `pipeline_tier`/`route`**: the tier decides *how many* resources (light/full), the shape decides *how they're arranged*. `query_shape` ADDS a field; it does NOT change the route. (Verbatim Claude Research taxonomy, `research_lead_agent.md:12-29`.)

   | `query_shape` (verbatim Claude label) | Claude's verbatim definition | Examples | Fan-out arrangement |
   |---|---|---|---|
   | `"depth_first"` (**depth-first query**) | *"the problem requires multiple perspectives on the same issue, and calls for 'going deep' by analyzing a single topic from many angles… The core question remains singular but benefits from diverse approaches."* | *"What are the most effective treatments for depression?"*; *"What really caused the 2008 financial crisis?"* (economic, regulatory, behavioral, historical perspectives + steelmanning) | 2–4 **sequential** perspectives on one locus, each reading the prior's committed position |
   | `"breadth_first"` (**breadth-first query**) | *"the problem can be broken into distinct, independent sub-questions, and calls for 'going wide'… The query naturally divides into multiple parallel research streams."* | *"Compare the economic systems of three Nordic countries"*; *"What are the net worths and names of all the CEOs of all the Fortune 500 companies?"* | **parallel** investigators across independent sub-questions, importance-ordered, `K = min(n_subq, cap)` |
   | `"straightforward"` (**straightforward query**) | *"focused, well-defined, and can be effectively answered by a single focused investigation or fetching a single resource… Can be handled effectively by a single subagent."* | *"What is the current population of Tokyo?"*; *"Tell me about bananas"* | a **single** investigator |

   **Classifier (DESIGN):**
   - `"straightforward"` = 1–2 atomic items / a single entity, not contested, no curation breadth.
   - `"breadth_first"` = many independent sub-questions / multiple entities (≈ a `collect`/`compare`/`survey` modality).
   - `"depth_first"` = one contested topic, multiple perspectives (≈ a `synthesize`/`forecast` modality + high contestedness — contradiction terms, argumentative format, dispute phrasing).

   Set `query_shape` honestly here; the query-router (step 1.5) re-derives it deterministically via `bad route` and writes the authoritative `query_shape` field, exactly as it does for `route`. The two are independent — a `full` route can be any of the three shapes, and a contested `depth_first` thesis can be `full` while a `breadth_first` survey down-routes to `light`.

7c. **Classify `recency_window`.** This is the *freshness tier* the search layer enforces: it both **biases planning** (the fan-out injects a date filter — `after:YYYY-MM-DD` for the host WebSearch/ddgs/SearXNG providers, `from_publication_date:` / `from-pub-date:` / `submittedDate:[…]` for the OpenAlex/Crossref/arXiv verticals) and **gates results** (the funnel's recency gate drops sources older than the window, primaries exempt). It maps 1:1 onto the funnel's frozen `RECENCY_MAX_AGE_DAYS` tiers, so use exactly one of these literal labels:

   | `recency_window` | Max source age | When to use | Signal words |
   |---|---|---|---|
   | `"breaking"` | 7 days | The answer turns on the last week's events — live developments, "today/this week", just-announced, ongoing incident. | "latest", "breaking", "just announced", "this week", "right now", "current status of <unfolding event>" |
   | `"current"` | 180 days | The answer needs recent-but-not-live sources — current state of a fast-moving field, "as of 2026", "recent", "now". | "currently", "recent", "as of <this year>", "state of the art", "latest version" |
   | `"evergreen"` | none (no gate) | **Default.** Timeless or historical questions where a 2019 source is as valid as a 2026 one — definitions, foundational papers, historical analysis, period-pinned filings. | everything else; any backward-looking `time_periods` entry forces evergreen |

   **Default is `"evergreen"`** (no freshness gate — a recency filter on a timeless question silently drops valid old sources). Only tier up to `"current"`/`"breaking"` when the query's *time_horizon* is forward/now-anchored and the topic is genuinely time-sensitive. A query with period-pinned `time_periods` (a 10-Q, an FY filing) is `"evergreen"` even when phrased "recent", because its primary source is a fixed historical document the gate must NOT drop.

   This `recency_window` threads downstream: step 1.5 / step 2 map the label to its `RECENCY_MAX_AGE_DAYS` value and pass it as `recency_days` on each `SearchQuery` (planning bias) and as the funnel `gather(..., recency_max_age_days=...)` argument (result gate). Set it honestly here; an over-tight window starves the corpus, an absent one lets stale SEO pages survive.

8. **Coverage matrix self-audit.** (The coverage matrix is a table mapping each verbatim query phrase to the atomic item(s) that cover it — the audit that catches dropped or narrowed scope.) Re-read the verbatim query. Walk through it phrase by phrase and extract every **significant noun phrase, proper noun, technical term, and category name**. For each:
   - Does it map to at least one atomic item in the decomposition?
   - Is the decomposition's interpretation **as broad as the phrase's natural scope**? (e.g., "SaaS applications" must not be narrowed to "POS SaaS"; "rugged tablets" must not be collapsed into "payment terminals")
   - If the phrase has multiple plausible referents, does the decomposition cover BOTH readings?

   Write the matrix to `research/temp/coverage-matrix.md`:

   ```markdown
   ## Coverage Matrix — query phrase → atomic item mapping

   | Query phrase (verbatim) | Mapped atomic item(s) | Scope check | Gap? |
   |---|---|---|---|
   | "rugged tablets" | Entity: rugged tablets | OK — full scope | No |
   | "SaaS applications" | Sub-Q3: SaaS deployment | NARROWED — decomposition says "POS SaaS" but query says "SaaS applications" broadly | **YES** |
   | "Southeast Asia" | Sub-Q4: Regional market — SEA | OK | No |
   ```

   **If any row has `Gap? = YES`:** go back and fix the decomposition. Add the missing atomic items, broaden the narrowed scope_conditions, or add missing entities. Then re-run the matrix until every row passes. Do NOT proceed with known gaps — they cascade into missing searches, missing sources, and missing draft sections.

9. **Update the scaffold.** Append a "Tier rationale" subsection to `research/scaffold.md` with a 2-3 sentence justification for the tier classification.

---

## Exit criterion

- `research/prompt-decomposition.json` exists, is valid JSON, every atomic item traces to the research_query
- `pipeline_tier` + `response_format` + `query_shape` + `citation_style` + `recency_window` are all set
- `scope_brief` is a one-paragraph framing (subject + in/out-of-scope + boundary conditions) the fast-mode writer can read standalone
- `research/temp/coverage-matrix.md` exists with **zero `Gap? = YES` rows**
- `research/scaffold.md` includes a Tier rationale subsection

---

## Next step

Return to the entry skill (`bad-research`), then invoke the query-router (step 1.5) — NOT step 2 directly. Decompose feeds the router, which decides the `route` and then sequences step 2 per that route:

```
Skill(skill: "bad-research-query-router")
```

The router (step 1.5) writes the `route` into `research/prompt-decomposition.json` and then proceeds to step 2 for every route (step 2 runs for ALL tiers).
