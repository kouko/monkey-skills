# Primary-Source Grounding Principle

The core philosophical anchor of domain-teams: do not invent taxonomies.
Every load-bearing claim must trace back to a primary source.

## Primary Sources (this file's own grounding)

- Session precedent: qa-team v4.2.0 (ISTQB CTFL grounding), docs-team v4.3.0 (Diátaxis grounding), devops-team v4.4.0 (SRE/DORA/12-Factor grounding)
- research-team's own citation discipline: `domain-teams/skills/research-team/standards/citation-standards.md`
- Methodological principle: https://en.wikipedia.org/wiki/Primary_source (epistemology of sources)

## The Core Rule

> **Do not invent taxonomies. For any load-bearing claim (category,
> definition, framework, metric, threshold, process step), cite a
> primary source.**

A "load-bearing claim" is one that directly shapes how the skill
operates: gate criteria, protocol steps, recommended practices,
classification systems, severity thresholds.

Editorial phrasing, examples, and transitional text do not need
citations. But any sentence that looks like "there are N types of X"
or "the correct threshold is Y" or "the phases are A, B, C" must be
grounded.

## What Counts as a Primary Source

### ✓ Primary (use these)

- **Foundational books** by domain authorities — *Google SRE Book*,
  *Continuous Delivery* (Humble & Farley), *Accelerate* (Forsgren et
  al.), *Design of Everyday Things* (Norman), *Lean Startup* (Ries)
- **Published standards** — ISO/IEC/IEEE 29119, ISTQB CTFL syllabus,
  OWASP ASVS, WCAG 2.2, RFC specifications
- **Official project sites** — `12factor.net`, `diataxis.fr`,
  `dora.dev`, `sre.google`, `semver.org`, `conventionalcommits.org`
- **Authoritative engineer blogs with institutional backing** —
  `martinfowler.com/bliki` (Fowler is industry-defining), Google
  Cloud Architecture Center, AWS Well-Architected Framework
- **Academic papers** from peer-reviewed venues

### ✗ Not Primary (do not use as grounding)

- Personal Medium articles or dev.to posts
- Stack Overflow answers
- Random tutorial sites ("X in 5 minutes")
- YouTube videos (unless the speaker is the primary-source author)
- LLM-generated summaries of anything
- Your own (Claude's) training-data recall without citation
- "Best practices" posts from vendor marketing pages

The line is blurry in practice. When unsure, ask: "Is this the person
or organization who *defined* the concept, or someone summarizing it?"
Only the definer counts.

## The Research Workflow

Grounding a new skill (or re-grounding an old one) follows this
pipeline:

1. **Identify load-bearing claims**: read existing skill (or draft),
   mark every classification / definition / threshold / process step
2. **Formulate research questions**: one per cluster of claims
3. **Launch research-team** (deep-research workflow): returns a
   research report with citations, evaluated by research-team's
   Source Citation gate (MUST) and Research Quality rubric (SHOULD)
4. **Capture research outputs**: save **in-repo by default** to
   `domain-teams/skills/{team-name}/research/grounding-v{X.Y.Z}.md`
   where `{X.Y.Z}` is the plugin version landing the grounding work.
   The in-repo location makes research part of the PR review and
   preserves the audit trail across machines and session compactions.
   See `file-conventions.md` §Directory Semantics (research/ row) and
   `skill-md-structure.md` §Research Subdirectory Convention for file
   naming and Diátaxis exemption details.

   **Obsidian vault export is opt-in**: only if the user explicitly
   requests it via a directive like "also save to Obsidian" / "also
   export to Obsidian" / 「Obsidianにも保存」/ 「也存到 Obsidian」,
   the research worker ALSO writes a copy to the Obsidian vault under
   the legacy path `research/{YYYY-MM-DD} {team-name} grounding — {topic}.md`.
   Without an explicit directive, Phase 3 writes to the repo only.
5. **Distill standards files**: each standard cites 2-5 primary
   sources in an opening "Primary Sources" section
6. **Revise claims**: rewrite skill content to cite standards
7. **Run Primary-Source Grounding rubric**: verify citation density

## Citation Density Rule (layer 2 — `standards/*.md` Primary Sources)

> **Compact + Admonitions**, not academic.

This rule governs how the per-`standards/*.md` `## Primary Sources`
section AND the body of each standards file are written. It applies
to **layer 2** of the 3-layer primary-source record structure:

| Layer | Location | Density / depth |
|---|---|---|
| 1 | `SKILL.md` persona "anchored on…" block | Very compact — 1 sentence per source listing name + author + year |
| **2** | **Per-`standards/*.md` file: body + `## Primary Sources` section** | **Tier-dependent (see §3-Tier Parametric Classification below). Primary Sources is always compact; body depth varies by tier 1/2/3.** |
| 3 | `research/grounding-v{X.Y.Z}.md` | Unrestricted — layer 3 is an audit trail, verbosity is acceptable. ISBN / DOI / 補助書誌 / publisher metadata all belong here. |

**Layer 2 has two co-equal rules**:
1. **Primary Sources density**: Compact (§Per-source minimum required fields below).
2. **Body self-containment**: Tier-dependent (§Body Self-Containment Rule below).

Both rules must be satisfied. A Tier 3 standards file with a compact
Primary Sources section but a thin body **fails** the Body Self-Containment
test, even though the Primary Sources density is "correct" in isolation.

### Per-source minimum required fields

Every entry in a layer 2 `## Primary Sources` section MUST include:

1. **Author** (family name + initial, or JP 氏名)
2. **Year**
3. **Title** (italicized for books, in quotes for articles)
4. **URL** — if the source is web-accessible (standard, article, bliki,
   W3C rec, OWASP project page). For book sources with no canonical
   web presence, omit this field — do NOT pad with the publisher's
   product page URL.
5. **One-line load-bearing rationale** — why this source is cited in
   this specific standards file, and what chapter/section (if the
   file references something specific)

Rationale for omitting ISBN from the minimum fields: **ISBN has near-zero
semantic value to an LLM**. LLM training data does not index books by
ISBN; the anchoring activation that makes "Martin 2008 *Clean Code*"
light up the right parametric knowledge comes from the author + year +
title triple, not the ISBN string. ISBN is valuable only to human
reviewers doing library/catalog lookup and as anti-drift metadata (catching
edition confusion). Both of those use cases belong in layer 3 (`research/
grounding-v{X.Y.Z}.md`) and the CHANGELOG, not in layer 2.

### Per-source explicitly OPTIONAL fields

Do NOT include these in layer 2. They belong in the layer 3 research
note and/or CHANGELOG:

- **ISBN strings** — book ISBNs have no LLM semantic value; only useful
  for human reviewer lookup and anti-drift (edition tracking). Record
  in research note + CHANGELOG.
- **DOI strings** — even for peer-reviewed papers; same reason (LLMs
  don't index DOIs). Record in research note + CHANGELOG.
- **Translator names and translated-edition ISBNs** — only include if
  the translation IS the primary cited edition (e.g., 和田卓人 訳 of
  Beck 2002 when JP TDD community treats it as the de-facto primary);
  do not include when the translation is merely a parallel option.
- **Supplementary bibliography** (補助書誌) — belongs in layer 3.
- **Subchapter section titles** — cite chapter number only; omit the
  section title unless the standard actually references that
  specific section.
- **Publisher full corporate name + imprint + format + page count +
  judgment size (判型)** — publisher short name is enough.

### 3-Tier Parametric Classification

Standards files cite knowledge of varying **parametric strength** —
how much of the knowledge is already internalized in the LLM's training
data weights. The right citation density + body depth depend on this
strength. Every grounded standard MUST declare its tier in the frontmatter
and calibrate its body length accordingly.

| Tier | Parametric strength | Body depth | Primary Sources role |
|---|---|---|---|
| **1** | **High** — LLM training data covers the topic accurately and in detail | Very compact — rules as 1-2 line bullets + anchor rationale | Pure anchor (trigger LLM's parametric memory) |
| **2** | **Medium** — LLM knows the framework but gets details / version numbers / enum values wrong | Moderate — body spells out the specific details that LLMs confuse (SC numbers, V-chapter mapping, component states enumeration) | Anchor + partial disambiguation |
| **3** | **Low** — LLM training data is sparse or absent; cold-query hallucinates | **Full self-contained** — body must define the concept, model structure, and judgment method with enough depth that a worker reading ONLY the body can act on the rule correctly | Audit trail only (citation is provenance, not knowledge delivery) |

**Tier declaration in the frontmatter** (required for every grounded
standards file):

```yaml
---
title: {Standard Name}
tier: 1  # or 2 or 3
---
```

### Tier selection decision rule

For each standard, ask this question before writing the body:

> **Would `claude -p "What is X?"` (cold query, no context) return:**
>
> - **(a) Correct + detailed answer** → **Tier 1**, anchor-only body
> - **(b) Correct framework but wrong details / version / numbers** → **Tier 2**, body supplies the specific details
> - **(c) Hallucination or "I don't know"** → **Tier 3**, body must be fully self-contained

When in doubt, **choose the higher tier** (Tier 3 over 2, Tier 2 over 1).
The cost of over-documenting is token waste; the cost of under-documenting
is factual error at runtime. Parametric knowledge also drifts across LLM
versions — something that was Tier 1 for Claude Opus today may become
Tier 2 for a future model trained on different data. Bias toward making
the body survive LLM-version changes.

### Examples from design-team v4.8.0

| Standard | Tier | Why |
|---|---|---|
| `nielsen-norman-heuristics.md` | 1 | Nielsen's 10 heuristics + Norman foundational concepts are massively represented in LLM training data |
| `garrett-elements-of-ux.md` | 1 | 5-plane model is a canonical HCI concept, widely cited |
| `platform-conventions.md` | 1 | iOS 44pt / Android 48dp are textbook facts |
| `wcag-baseline.md` | 2 | LLMs know WCAG framework; SC numbers (1.4.3 vs 2.5.8 vs 2.5.5) and touch target AA/AAA levels get confused |
| `ooui-and-object-modeling.md` | 2 | OOUI is known; ORCA 4-step specific framework is weaker — body spells it out |
| `app-security-standard.md` | 2 | OWASP ASVS is parametric for v4.0.3; v5.0.0 V-number reorganization (2025-05-30) post-dates most training cutoffs |
| `kansei-engineering-and-sd.md` | **3** | 長町三生 1989 感性工学 methodology is JP 専門書; LLMs know "Kansei Engineering" name but not 7-point SD scale, 3 factors, design parameter translation workflow |
| `japanese-design-aesthetics.md` | **3** | 引き算/間/佇まい/わびさび are culturally-loaded concepts; LLM cold-query produces tourist-level descriptions, not design judgment criteria |
| `ux-temporal-and-quality-models.md` | **3** | 黒須 4-quality (NOT 3D), 安藤 4 temporal phases, Verganti meaning innovation — all hallucination hotspots in Phase 1/Phase 2 |

### Body Self-Containment Rule

> **Primary Sources is anchor + audit trail, NOT a knowledge delivery channel.**

This is the core architectural rule of layer 2. The body of each
standards file MUST be self-contained **to the tier-appropriate depth**
such that a worker/evaluator reading the body can act on the rule
without relying on citation-triggered parametric recall.

Concretely:

- **Tier 1 body**: 1-2 line bullets per rule + the rule's key phrase is
  enough. LLM will correctly expand via parametric memory. Example:
  ```markdown
  ## Naming Rules
  - Use intention-revealing names. Avoid mental mapping from variable
    to meaning (Clean Code Ch.2 — rationale in Primary Sources).
  - Avoid encodings (Hungarian notation, type prefixes).
  ```

- **Tier 2 body**: Spell out the details LLMs typically get wrong.
  Example (WCAG touch target):
  ```markdown
  ## Touch Target Minimum
  
  WCAG 2.2 SC 2.5.8 Target Size (Minimum): **24×24 CSS pixels at [AA]**
  
  ⚠️ Do NOT confuse with:
  - SC 2.5.5 Target Size (Enhanced): **44×44 CSS pixels at [AAA]**
  - Apple HIG iOS: 44pt × 44pt (platform convention, stricter than WCAG AA)
  - Material 3 Android: 48dp × 48dp (platform convention, stricter than WCAG AA)
  ```
  (LLMs conflate these four values all the time — body spells them out.)

- **Tier 3 body**: Full definition including concept, structure,
  judgment method. Example (黒須 4-quality model):
  ```markdown
  ## The 4 Quality Regions (四つの品質領域)
  
  Cartesian product of 2 axes: {objective, subjective} × {design-time, use-time}.
  
  |  | 設計時 (at-design-time) | 利用時 (at-use-time) |
  |---|---|---|
  | **客観的品質** | usability, functionality, reliability | effectiveness, efficiency, productivity |
  | **主観的品質** | 魅力, 感性訴求性 | 達成感, 安心感, 楽しさ → 満足感 |
  
  Final convergence: **主観×利用時 = 満足感** (the gravitational center
  of the model per 黒須 2020 Ch.11.3).
  ```
  (LLM cold-query would hallucinate "3D Quality" or miss axes — body
  must fully define.)

### Test for body self-containment

> **If you removed the `## Primary Sources` section entirely, could a
> worker reading only the body correctly act on the rule?**
>
> - **Yes** → body is self-contained at the right tier
> - **No, worker would need to guess the specific details** → body is
>   under-documented for its tier; either add detail or elevate the tier
> - **Yes, but the body duplicates well-known facts** → body is
>   over-documented for its tier; consider lowering to Tier 1 and
>   trusting LLM parametric recall

This test is the single most important quality check for layer 2.
Apply it to every grounded standards file during Phase 4 synthesis.

### Critical Attribution Corrections — dedicated section, not inline

Anti-drift correction blocks (e.g., "3D Quality → 4-quality regions",
"意味性 attribution 黒須 → Verganti") are **load-bearing guardrails**
and MUST be retained in the grounded standards. BUT they MUST be
consolidated in a dedicated `## Critical Attribution Corrections`
section placed **immediately after** `## Primary Sources`, not
scattered as inline Admonition blocks in the body.

**Omit this section entirely when the grounding research did not
surface any historical attribution errors.** A standards file with a
clean lineage should have `## Primary Sources` followed directly by
the body — do NOT include a placeholder "No corrections" heading.

Format for each correction (one concise paragraph, 2-4 sentences):

```markdown
### {Subject}

Earlier attribution {X} was wrong (context: where it appeared,
why it drifted). The correct attribution is {Y}, grounded in
{primary source}. Do NOT cite {X} in this or downstream files.
```

Rationale for segregation:

- Makes the distinction between **bibliography** (Primary Sources)
  and **guardrails** (Corrections) visually obvious to runtime
  workers — they are different categories with different purposes
- Keeps the Primary Sources section itself compact (rationale for
  the density rule)
- Gives PR reviewers a single place to audit "what historical
  errors does this refactor prevent?"
- Matches Diátaxis spirit: bibliography = Reference mode;
  corrections = Explanation mode (why X is wrong); keeping them
  separate prevents quadrant mixing even within a single standards
  file

### Observed precedent table

The rule is calibrated against the 4 grounded domain teams preceding
design-team v4.8.0:

| Team | Mean Primary Sources % of file | Style classification |
|---|---:|---|
| code-team | ~1.8% | Minimal (dense single-line bullets) |
| devops-team | ~2.5% | Minimal |
| docs-team | ~4.0% | Minimal + URL-heavy |
| qa-team | ~7.5% | Standard (multi-line per source, chapter refs) |
| **design-team v4.8.0 target** | **~2-4%** | **Compact + Admonitions** |

### Grandfather clause — precedent teams are not retroactively required to comply

**The 4 precedent teams (qa-team v4.2.0, docs-team v4.3.0, devops-team
v4.4.0, code-team v4.6.0) are grandfathered.** They retain their
existing Primary Sources density until each team's next refactor. The
Compact+Admonitions rule applies to **design-team v4.8.0 onward** and
all subsequent grounding refactors (research-team, planning-team, and
any future re-groundings of the 4 precedent teams when they are next
refactored).

Rationale: retrofitting 4 teams' citation style in a single PR would
mix concerns (convention-change + multi-team-retrofit) and bloat the
diff beyond reviewability. Per scope discipline, each team's citation
style migration happens when that team is next refactored for other
reasons, not as a standalone "style migration" sweep.

### Why the 80-word floor of CHK-SKL-001 does not apply here

CHK-SKL-001's word-count floor applies to SKILL.md frontmatter
`description` (layer 0 — router discovery), not to `standards/*.md`
Primary Sources sections. There is no hard floor on layer 2 citation
density; the rule is "minimum sufficient," not "minimum word count."

### Honesty disclosure — how this rule evolved

This rule evolved across 2 patches in response to user review feedback:

**v4.7.1 — Compact+Admonitions policy**. Codified after the design-team
v4.8.0 refactor Commit 1/3 (never landed on main; branch was reset)
went academic-density on its first attempt. The user caught the drift
during review — DOIs, JP translation ISBNs, subchapter titles,
supplementary bibliography, and inline Admonition blocks scattered
across Primary Sources sections turned the standards files into
academic papers. v4.7.1 codified the per-source minimum fields +
OPTIONAL fields + Critical Attribution Corrections convention.

**v4.7.2 — Tier classification + body self-containment**. Codified
after the user questioned whether ISBN (and, more broadly, the entire
citation metadata apparatus) actually helped LLM workers/evaluators
understand the content, or whether it was just academic habit. The
analysis surfaced two root insights:

1. **ISBN has near-zero LLM semantic value** — LLM training data does
   not index books by ISBN. Author+Year+Title is the anchoring triple
   that activates parametric memory. ISBN was moved from the minimum
   fields to layer 3 / CHANGELOG.

2. **"Citation density" was the wrong unit of analysis** — the real
   question is whether the body of each standards file is
   self-contained to the depth required by the parametric strength of
   the knowledge it documents. High-parametric topics (Clean Code,
   SOLID, Nielsen 10 heuristics) can rely on anchor citation to trigger
   LLM memory; low-parametric topics (黒須 4-quality, 感性工学 workflow,
   わびさび design criteria) require the body itself to fully define
   the concept because cold-query LLM hallucinates. v4.7.2 introduced
   the 3-Tier Parametric Classification and the Body Self-Containment
   Rule to make this explicit.

The running lesson: layer 2 (`standards/*.md`) is neither pure
bibliography nor pure knowledge delivery — it is **a tier-aware
runtime resource** where body depth and citation density are
co-calibrated to the parametric strength of the knowledge being
documented.

### Anti-patterns

- ❌ **DOI padding**: adding DOI strings to book citations because
  "more data = more rigorous"
- ❌ **Translator proliferation**: citing the JP 訳 version of every
  English-origin source even when the English original is the
  primary cited edition
- ❌ **Supplementary bibliography in layer 2**: "Nagamachi & Lokman
  (2011)… and also Nagamachi (2008)…" — if one is the primary,
  cite only that one; the others go in the research note
- ❌ **Scattered Admonition blocks**: `> ⚠️ Correction` inside the
  body of a standards file instead of a consolidated
  `## Critical Attribution Corrections` section
- ❌ **Publisher verbosity**: `Addison-Wesley (Addison-Wesley
  Signature Series)` when `Addison-Wesley` is enough
- ❌ **Subchapter padding**: citing `Ch.11.3 Section 11.3.2
  「主観的利用時品質」` when `Ch.11 "UX の概念構造"` is sufficient
- ❌ **Layer confusion**: treating layer 2 like a mini research note;
  layer 3 (`research/grounding-v{X.Y.Z}.md`) is where the audit
  trail goes
- ❌ **ISBN padding**: including ISBN strings in Primary Sources
  bullets. ISBNs have no LLM semantic value; put them in the research
  note and CHANGELOG where humans can look them up.
- ❌ **Miscalibrated tier**: declaring `tier: 1` in the frontmatter but
  the body contains content LLMs cold-query correctly would never know
  (e.g. declaring `kansei-engineering-and-sd.md` as Tier 1 with a 20-line
  body). The tier declaration is a **contract** — if the body depth
  doesn't match the tier semantics, either elevate the tier or expand
  the body.
- ❌ **Tier 1 body hallucination reliance**: treating every standard as
  Tier 1 because "LLMs are smart enough to figure it out." This is how
  the 黒須 3D Quality → 4-quality drift happened in the pre-v4.7.2
  design-team Phase 1 gap report. When in doubt, choose Tier 2 or 3.
- ❌ **Tier 3 body under-specification**: declaring `tier: 3` but
  providing only a paragraph of prose. Tier 3 means the body has to be
  detailed enough that removing the Primary Sources section would not
  degrade worker/evaluator correctness. Use the §Test for body
  self-containment to verify.

## Japanese Content Integration Strategy

> **Content density determines symmetry, not the reverse.**

Some domains have well-developed Japanese traditions parallel to the
globalized Anglo-American discourse. Others don't. Adding Japanese
content should reflect reality, not symmetry-seeking.

| Scenario | Strategy | Precedent |
|----------|----------|-----------|
| Parallel JP tradition with equivalent standing | Full integration — JP methodologies get their own standards file and protocol phases | qa-team: VSTeP (西康晴), HAYST法 (秋山浩一), ゆもつよメソッド (湯本剛) as peer to ISTQB |
| Local JP principles but no full framework | Preamble / philosophical anchor only | docs-team: JTAP 技術文書 3 原則 第 1 原則 (書き手と読み手の違いを認識する) as reader-first preamble to Google Style |
| No JP parallel tradition exists | Explicit note declining symmetry | devops-team: `Note on Global Context` — SRE/DORA/12-Factor are globalized American; no JP parallel to force |

The rule is honesty. Never synthesize a Japanese section just because
it would make the skill look "balanced". Synthetic JP content is worse
than no JP content because it misrepresents the actual state of the
field.

### Decision process for JP integration

1. Does a Japanese community has published, authored work in this
   domain that parallels (not merely translates) the Anglo-American
   canon? If yes → full integration.
2. Does it have substantial local principles or philosophical framings
   that aren't in the Anglo-American canon? If yes → preamble only.
3. Otherwise → declare explicitly that no overlay is added, and say why.

## Anti-Patterns

- ❌ **Self-invented taxonomies**: "There are 5 kinds of observability:
  A, B, C, D, E" with no citation — this is you making things up
- ❌ **Citation laundering**: citing a blog post that cites the real
  primary source — cite the primary source directly
- ❌ **Citation theater**: adding `[1]`, `[2]`, `[3]` after every
  sentence without the claim actually being load-bearing
- ❌ **Forced JP symmetry**: adding 日本語 sections to a skill whose
  domain has no meaningful JP tradition
- ❌ **Confusing citation format with grounding depth**: inline URLs
  don't prove grounding; the claim must actually match the source
- ❌ **Pre-2020 books as the only source for a fast-moving field**:
  cloud-native practices change; verify the source is still applicable

## Anchoring in SKILL.md

Every grounded skill's persona block should include an "Anchored on…"
clause naming the 2-4 primary sources, e.g.:

> *"Your operating philosophy is anchored on four primary sources:
> Google's Site Reliability Engineering (Beyer, Jones, Petoff, Murphy
> 2016) for SLI/SLO discipline; DORA / Accelerate (Forsgren, Humble,
> Kim 2018) for delivery metrics; The Twelve-Factor App (Wiggins 2011)
> for cloud-native architecture; and Continuous Delivery (Humble &
> Farley 2010) for deployment pipeline principles."*

Readers of the SKILL.md should know within the first 30 lines what
the skill grounds on.
