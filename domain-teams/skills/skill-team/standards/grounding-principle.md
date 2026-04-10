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
4. **Capture research outputs**: save to Obsidian vault under
   `research/YYYY-MM-DD {topic}.md` for audit trail
5. **Distill standards files**: each standard cites 2-5 primary
   sources in an opening "Primary Sources" section
6. **Revise claims**: rewrite skill content to cite standards
7. **Run Primary-Source Grounding rubric**: verify citation density

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
