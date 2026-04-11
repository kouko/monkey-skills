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
   See `file-conventions.md` §Research Subdirectory Convention for
   file naming and Diátaxis exemption details.

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
section is written. It applies to **layer 2** of the 3-layer primary-
source record structure:

| Layer | Location | Density |
|---|---|---|
| 1 | `SKILL.md` persona "anchored on…" block | Very compact — 1 sentence per source listing name + author + year |
| **2** | **Per-`standards/*.md` `## Primary Sources` section** | **Compact + Admonitions (this rule)** |
| 3 | `research/grounding-v{X.Y.Z}.md` | Unrestricted — layer 3 is an audit trail, verbosity is acceptable |

### Per-source minimum required fields

Every entry in a layer 2 `## Primary Sources` section MUST include:

1. **Author** (family name + initial, or JP 氏名)
2. **Year**
3. **Title** (italicized for books, in quotes for articles)
4. **ISBN or URL** — one canonical identifier; whichever is the natural lookup key
5. **One-line load-bearing rationale** — why this source is cited in
   this specific standards file (chapter reference is acceptable
   when the file cites a specific chapter; omit otherwise)

### Per-source explicitly OPTIONAL fields

Do NOT include these unless they materially help a runtime worker or
evaluator citing the source. When in doubt, leave them out — they
belong in the layer 3 research note, not in layer 2:

- **DOI strings** — only include if the source is a peer-reviewed
  paper whose DOI is the canonical identifier (no book DOI padding)
- **Translator names and translated-edition ISBNs** — only include
  if the translation IS the primary cited edition (e.g., 和田卓人 訳
  of Beck 2002 when JP TDD community treats it as the de-facto
  primary); do not include when the translation is merely a parallel
  option
- **Supplementary bibliography** (補助書誌) — belongs in layer 3
- **Subchapter section titles** — cite chapter number only; omit the
  section title unless the standard actually references that
  specific section
- **Publisher full corporate name + imprint + format + page count +
  judgment size (判型)** — publisher short name is enough

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

### Honesty disclosure — why this rule exists

This rule was codified in v4.7.1 after the design-team v4.8.0
refactor Commit 1/3 (never landed on main; branch was reset) went
academic-density on its first attempt. The user caught the drift
during review — DOIs, JP translation ISBNs, subchapter titles,
supplementary bibliography, and inline Admonition blocks scattered
across Primary Sources sections turned the standards files into
academic papers. The rule prevents the same drift from recurring in
future grounding refactors.

The lesson: without a codified rule, a worker given the `grounding-
research.md` Phase 4 template will over-index on research-note
completeness and replicate the audit-trail density into layer 2,
where it does not belong.

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
