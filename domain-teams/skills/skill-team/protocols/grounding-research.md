# Protocol: Grounding Research

**When to use**: a skill needs primary-source grounding — either
because it's new or because gap assessment in `skill-redesign.md`
phase 1 surfaced load-bearing claims without citations.

**Output**: a list of standards files to draft, each with its
authoritative primary sources identified, plus a Japanese integration
decision.

Grounds on: `../standards/grounding-principle.md`.

## Phase 1: Define Research Questions

Translate the grounding gap into concrete questions research-team can
answer. Each question should target a specific claim cluster.

Good question shapes:
- "What is the authoritative taxonomy for {domain concept}?"
- "What are the primary sources that define {framework}?"
- "How does the {global / Anglo-American} canon treat {topic}?"
- "Are there parallel Japanese community traditions for {topic}?"

Bad question shapes:
- "What are best practices for X?" — too vague, no primary source
  anchor
- "What does Claude think about X?" — you're asking for hallucination
- "What do people on Stack Overflow say?" — not primary sources

Aim for 2–5 research questions per grounding task. More than 5 and
research-team will lose focus.

## Phase 2: Launch research-team

Use the `research-team` deep research workflow:

```
### Task
Ground {team-name} in primary sources for {topic area}.
Research questions: {list from phase 1}.

### Resource Paths
(research-team's own resources — skill-team doesn't pass them)

### Input
output_language: {user's language}
```

research-team produces a research report that passes:
- Source Citation gate (MUST) — every factual claim cited
- Research Quality rubric (SHOULD) — depth and source authority

If research-team returns `NEEDS_REVISION` or `BLOCKED`, do NOT
proceed — escalate to the user.

## Phase 2b: Multi-Cluster Parallel Research (optional — for multi-framework expansions, added v4.11.0)

If the grounding task spans **3 or more independent framework
clusters** (e.g., adding 5 new macro frameworks to an already-
grounded team), a single sequential research-team launch becomes
both slow AND prone to losing focus across clusters. Use multi-
cluster parallel grounding instead.

### When to use multi-cluster parallel

- Grounding task has **3+ independent framework clusters** (e.g.,
  research-team v4.11.0 added 5 frameworks: Hedgeye GIP, MMT, RAI,
  Taleb Barbell, Fama-French — one cluster per framework)
- Clusters are **loosely coupled** — each can be researched without
  depending on the findings of the others
- The refactor is a **post-grounding expansion** (see
  `skill-redesign.md §Phase 1 Variant: Post-Grounding Expansion
  Track`), not an initial grounding

### Parallel launch pattern

For each framework cluster:

1. **Scope narrowly** — one cluster = one worker launch. Do NOT
   give one worker multiple clusters to research "in parallel"
   internally.
2. **Launch as `general-purpose` or `research-team deep mode`** —
   each worker gets a focused research brief naming:
   - The specific framework (e.g., "Hedgeye GIP")
   - 4-6 concrete claims to verify (definition, lineage, attribution,
     variants, JP integration, anti-drift corrections)
   - Expected output structure (primary sources list, attribution
     corrections, body draft for the eventual standards file)
3. **Run all workers in parallel** via a single main-agent response
   with N tool calls — NOT sequential launches.
4. **Budget per cluster** — ~40-60k tokens for deep research; ~15-25k
   for quick triangulation. Total budget scales linearly with
   cluster count.
5. **Collect outputs** as N separate research summaries.

### Synthesis into a single research note

After all parallel workers complete:

1. **Merge outputs** into a single consolidated research note
   (`research/grounding-v{X.Y.Z}.md`) with one cluster per section
2. **De-duplicate cross-cluster attribution corrections** — some
   corrections surface in multiple clusters (e.g., "Shiller alone
   vs Campbell & Shiller 1998" might appear in both a macro
   cluster and a security cluster)
3. **Surface cross-cluster attribution drift** — parallel research
   often exposes contradictions between clusters that sequential
   single-task research misses (e.g., Cluster A cites X 2018;
   Cluster B cites X 2020 — which is canonical?)
4. **Run §Phase 4 Standards Synthesis** on the merged note as usual

### Precedent — research-team v4.11.0

5 parallel `general-purpose` grounding agents, one per framework
cluster, for the investment analysis L1/L2/L3/portfolio split:

| Cluster | Agent | Token budget | Corrections surfaced |
|---|---|---:|---:|
| Hedgeye GIP | general-purpose | ~40k | 7 |
| MMT | general-purpose | ~50k | 7 |
| RAI | general-purpose | ~45k | 10 |
| Taleb Barbell | general-purpose | ~30k | 7 |
| Fama-French | general-purpose | ~40k | 11 |
| **Total** | | **~205k** | **42 (11 unique misattributions prevented)** |

Synthesis phase produced `research/grounding-v4.11.0.md` (1364
lines) as a single consolidated audit trail with all 42 attribution
corrections, cross-referenced by layer for the 4 new standards
files.

### When NOT to use multi-cluster parallel

- **Initial skill grounding** (new team, no prior standards) — use
  the standard single-research-team Phase 2 launch; parallel works
  best for additive expansions, not initial state
- **Single-framework deep dive** (1-2 clusters) — parallel overhead
  exceeds savings
- **Tightly-coupled clusters** (e.g., "how do A, B, C interact?")
  — parallel research cannot surface interaction findings

## Phase 3: Research Note Capture

Save the research report **in-repo by default** under the skill's
optional `research/` subdirectory:

```
domain-teams/skills/{team-name}/research/grounding-v{X.Y.Z}.md
```

where `{X.Y.Z}` is the plugin version that will land the grounding
work (for example, `grounding-v4.8.0.md` for design-team's v4.8.0
refactor). See `file-conventions.md` §Directory Semantics (research/
row) and `skill-md-structure.md` §Research Subdirectory Convention
for the full rules:

- One file per grounding event; no dates in filename (dates are in
  git log and frontmatter)
- ASCII-only filename; CJK content goes in the file body
- File is maintainer-facing; NOT read by worker/evaluator at runtime
- Not listed in SKILL.md Resource Manifest or launch templates
- Exempt from Diátaxis single-quadrant rule (research notes are
  fundamentally mixed-mode)

The in-repo location makes research part of the PR review, ensures
the audit trail survives session compaction and machine changes, and
lets reviewers see the "why" behind primary-source choices alongside
the grounding changes themselves.

### File content

Preserve the full research artifact: cluster-by-cluster source
verification, research questions with cited answers, claim → source
mapping tables, JP integration decision with evidence, open
questions. Mirror the structure of prior grounded team research notes
(see `qa-team/research/grounding-v4.2.0.md`,
`docs-team/research/grounding-v4.3.0.md`,
`code-team/research/grounding-v4.6.0.md` for reference shapes).

Required frontmatter:

```yaml
---
title: {team-name} 再設計研究 — {topic}
date: {YYYY-MM-DD}
team: {team-name}
refactor_version: v{X.Y.Z}
tags: [research, domain-teams, {team-name}, grounding]
---
```

### Opt-in Obsidian export (user directive only)

Obsidian vault export is **opt-in**. If — and only if — the user's
skill-team invocation contains an explicit directive, ALSO write a
copy to the user's Obsidian vault under the legacy convention path
`research/{YYYY-MM-DD} {team-name} grounding — {topic}.md`.

**Directive trigger phrases** (multilingual, accept any):

- English: `also save to Obsidian`, `also export to Obsidian`,
  `and to Obsidian`, `Obsidian copy`
- 日本語: `Obsidianにも保存`, `Obsidianにもエクスポート`,
  `Obsidianにもコピー`
- 繁體中文: `也存到 Obsidian`, `也複製到 Obsidian`,
  `也輸出到 Obsidian`
- 简体中文: `也存到 Obsidian`, `也复制到 Obsidian`

If no Obsidian directive is present, write **only** the in-repo
file. Do not prompt the user to ask — silence means repo-only.

If an Obsidian directive IS present but the Obsidian vault location
is not discoverable (no `*.obsidian` vault found in expected paths),
log a note in Phase 6's grounding plan ("Obsidian export requested
but vault not found — in-repo copy only") and continue. Do not
block the refactor on Obsidian availability.

## Phase 4: Standards Synthesis

For each cluster of related findings, plan one standards file:

```
{authoritative-name}.md
Tier: {1 | 2 | 3 — see §Tier Selection below}
Purpose: {what claims this standard anchors}
Primary sources: {2–5 sources, formatted per §Citation Density Rule — NO ISBNs}
Critical attribution corrections: {any anti-drift corrections, if applicable}
Body outline: {tier-dependent — see §Body Self-Containment below}
Estimated length: {Tier 1: 60-90 lines; Tier 2: 100-150 lines; Tier 3: 150-250 lines}
Load-bearing claims covered: {list}
```

Standards should be single-topic. If findings span two topics, split
into two standards files.

Typical output from phase 4 is a plan listing 3–6 standards to write.

### Tier Selection (MUST run before writing each standard)

Before writing any standard, classify it into one of 3 tiers per
`../standards/grounding-principle.md` §3-Tier Parametric
Classification. Apply the **cold-query decision rule**:

> **Would `claude -p "What is X?"` (no context) return:**
>
> - **(a) Correct + detailed answer** → **Tier 1** (anchor-only body)
> - **(b) Correct framework but wrong details / version / numbers** → **Tier 2** (body supplies confused details)
> - **(c) Hallucination or "I don't know"** → **Tier 3** (body is fully self-contained)

**Mandatory test**: actually run the cold-query mentally (or literally
with `claude -p`) before committing to a tier. Do NOT default to Tier 1
because "LLMs are smart enough." When in doubt, choose the higher tier.

**Heuristics**:
- Non-Anglo canonical knowledge (JP 専門書, 中文 regulatory docs,
  domain-specific national standards) → usually Tier 3
- Post-2024 standards and their specific numbered requirements
  (ASVS v5, WCAG 3 drafts, new OWASP Top 10) → Tier 2
- Pre-2024 mainstream Anglo HCI/software engineering canon (Clean Code,
  SOLID, Nielsen 10, Norman, Fowler, Beck, Garrett, etc.) → usually Tier 1
- Internal company conventions that are not in any public training
  corpus → always Tier 3

**Tier drives body depth, not Primary Sources density.** Primary
Sources stays compact regardless of tier; the body is where tier
calibration lives.

### Citation style for each standards file

**Apply the Compact+Admonitions style** documented in
`../standards/grounding-principle.md` §Citation Density Rule. Each
standards file produced by this phase MUST contain:

1. **Frontmatter with `tier: {1|2|3}`** — declares the standard's
   parametric tier so downstream evaluators can verify body depth
   calibration.
2. **A `## Primary Sources` section** with one bullet per source, each
   containing ONLY the mandatory fields: **author / year / title / URL
   (if web-accessible) / one-line load-bearing rationale**. **No ISBN**
   (ISBN has no LLM semantic value; it goes in the research note + CHANGELOG).
3. **A body calibrated to the declared tier** (see §Body Self-Containment
   below).
4. (Optional but recommended for first-time-grounded topics) **A
   `## Critical Attribution Corrections` section** placed immediately
   after `## Primary Sources`, consolidating any anti-drift correction
   blocks as standalone paragraphs (not inline Admonitions in the body).

**Do NOT** include ISBNs, DOIs, translator names, supplementary
bibliographies, subchapter titles, or publisher verbosity in the
Primary Sources section — those details belong in the layer 3
research note (`research/grounding-v{X.Y.Z}.md`), which you already
produced in Phase 3.

### Minimal template for a Primary Sources section

```markdown
## Primary Sources

- **{Author} ({Year})** *{Title}*. {URL if web-accessible}. {One-line why this standard cites it — chapter reference if specific.}
- **{Author} ({Year})** *{Title}*. {One-line why.}
- {... 2 to 5 sources total ...}
```

Note: **no ISBN line, no publisher imprint, no DOI**. Book sources
omit the URL line entirely (don't pad with publisher product pages).

### Body Self-Containment by tier

The body of the standards file must be calibrated to the tier you
declared in the frontmatter. See
`../standards/grounding-principle.md` §Body Self-Containment Rule for
the full specification; the condensed per-tier checklist:

**Tier 1 body** (high parametric):
- Rules as 1-2 line bullets
- Each rule has a short anchor phrase (the name of the rule + the
  author/title cross-reference)
- Trust LLM to fill in via parametric memory
- Example target: `nielsen-norman-heuristics.md` — list the 10 by
  canonical name, one line each, + brief anchor to Nielsen NN/g URL

**Tier 2 body** (medium parametric):
- Everything Tier 1 has, PLUS
- Explicit spell-out of numbered details, enum values, version-specific
  mappings that LLMs typically confuse
- Use tables for matrix data (SC number × level, V-chapter × topic)
- Example target: `wcag-baseline.md` — SC numbers 1.4.3 / 2.5.5 / 2.5.8
  explicitly with their AA/AAA levels in a table

**Tier 3 body** (low parametric):
- Everything Tier 2 has, PLUS
- Full definitions of concepts the LLM would hallucinate on cold query
- Complete model structures (e.g. black's 4-quality 2×2 matrix spelled
  out with cell contents)
- Judgment criteria / decision rules that the evaluator gate needs to
  apply
- Example target: `ux-temporal-and-quality-models.md` — 4 temporal
  phases defined with JP + English names, 4-quality regions in a
  complete 2×2 table with cell contents, Verganti meaning innovation
  3-path framework defined

**Self-containment test** (run after writing each standard): mentally
remove the `## Primary Sources` section. Could a worker reading only
the body still correctly act on the rule? If yes at the declared tier
level, body is calibrated correctly. If no, either elevate the tier or
expand the body.

### Minimal template for a Critical Attribution Corrections section

Only add this section when the grounding research surfaced concrete
attribution errors from earlier ungrounded versions. Otherwise omit
entirely.

```markdown
## Critical Attribution Corrections

### {Subject of correction}

Earlier attribution {X} was wrong ({brief context — e.g. "appeared
in ux-strategy-gate.md L42 of the pre-grounding version"}). The
correct attribution is {Y}, grounded in {primary source from this
standard's Primary Sources section above}. Do NOT cite {X} in this
or downstream files.

### {Subject of next correction}
…
```

### Anti-patterns in Phase 4 output

- ❌ Producing a `## Primary Sources` section that reproduces the
  research note's full cluster-by-cluster citation table — layer 2
  is not an audit trail
- ❌ **Including ISBN strings** in Primary Sources bullets. ISBNs
  have no LLM semantic value; they belong in the research note and
  the CHANGELOG, not in layer 2.
- ❌ Scattering `> ⚠️ Correction` Admonitions in the body of the
  standards file instead of consolidating them in
  `## Critical Attribution Corrections`
- ❌ Padding with DOIs / translators / bibliographies / subchapter
  titles because "completeness seems safer"
- ❌ Failing to write any `## Critical Attribution Corrections`
  section when the research note explicitly surfaced attribution
  errors — those corrections are load-bearing guardrails and must
  be preserved SOMEWHERE in the standards layer
- ❌ **Missing tier declaration** in the standards file frontmatter.
  `tier: 1|2|3` is mandatory per `../standards/grounding-principle.md`
  §3-Tier Parametric Classification; downstream evaluators use it to
  check body depth calibration.
- ❌ **Tier-1-defaulting without cold-query test**. Assuming every
  standard is Tier 1 because "LLMs know everything" is how the
  黒須 3D Quality → 4-quality drift happened. Actually run the
  cold-query test (or think hard about whether LLM cold-query is
  likely to correctly answer "What is X from author Y?") before
  committing to Tier 1.
- ❌ **Tier 3 body too thin**. Declaring `tier: 3` but writing only
  a paragraph of prose. Tier 3 means the body must define the
  concept, model structure, and judgment criteria in full — run the
  self-containment test (mentally remove Primary Sources and ask if
  the body still suffices).

## Phase 5: Japanese Integration Decision

Apply the content-density rule from `../standards/grounding-principle.md`:

| Evidence | Strategy |
|----------|----------|
| Research surfaces a named Japanese tradition with published authors and methodologies parallel to the Anglo canon | Full integration — standards file in JP + protocol phases reference JP methodologies |
| Research surfaces JP principles or philosophical framings (not full framework) | Preamble only — JP quote or principle as ground anchor in persona |
| Research surfaces no JP parallel tradition | Explicit note — add a "Note on Global Context" section declaring no JP overlay |

Document the decision AND the evidence behind it. Future reviewers
should see why this call was made.

## Phase 6: Produce the Grounding Plan

Output a structured plan:

```markdown
## Grounding Plan for {team-name}

**Research source**: `domain-teams/skills/{team-name}/research/grounding-v{X.Y.Z}.md` (in-repo, default)
**Obsidian export**: {none | path to Obsidian copy if user requested opt-in export}

**Standards to create** (for commit 1 of skill-redesign / new-skill-creation):
1. {standard-name}.md — primary sources: {list}
2. ...

**JP integration decision**: {full | preamble | none}
**JP evidence**: {one-sentence justification}

**Load-bearing claims now grounded**:
- {claim 1} → {source 1}
- {claim 2} → {source 2}
- ...
```

This plan feeds directly into `new-skill-creation.md` phase 3 or
`skill-redesign.md` phase 4.

## Rules

- If research-team can't find primary sources for a claim, that claim
  should NOT become load-bearing in the new skill. Reword it out.
- Always prefer books and published standards over blog posts, even
  authoritative blogs.
- The JP integration decision must be backed by research evidence,
  not personal preference.
- One grounding-research run ≠ one skill refactor. The same research
  may support multiple skill updates over time.

## Anti-Patterns

- ❌ Skipping research-team and inventing "primary sources" from
  training data recall
- ❌ Citing blog posts that themselves cite the primary source
- ❌ Running research-team with no specific questions ("research
  testing best practices" — too vague)
- ❌ Using the research output without reading it — you must
  understand the sources before synthesizing standards
- ❌ Forcing JP integration because "it would look balanced"
