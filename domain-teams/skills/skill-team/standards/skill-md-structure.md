# SKILL.md Structure Convention

Defines the required structure of a `domain-team` SKILL.md file — the
top-level file that Claude discovers and that orchestrates everything
else in the skill directory.

## Primary Sources

- Anthropic Agent Skills spec: https://docs.anthropic.com/en/docs/claude-code/skills
- Anthropic Skills format reference: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- Repo convention SSOT: `/Users/kouko/GitHub/monkey-skills/CLAUDE.md` §"Skill Development Conventions"
- Observed precedent: `qa-team/SKILL.md` (v4.2.0), `docs-team/SKILL.md` (v4.3.0), `devops-team/SKILL.md` (v4.4.0)

## Frontmatter Schema

Every SKILL.md starts with YAML frontmatter in this exact shape:

```yaml
---
name: {team-name}
description: >-
  {One-paragraph description with trigger sentences.}
  Use when {explicit triggers — verbs + artifacts}.
  Do NOT use for {explicit non-triggers, link to the right team}.
  Delivers {list of output artifacts, comma-separated}.
  {Optional: 中文・日本語 keyword suffix for multilingual discovery}.
---
```

**Required fields**: `name`, `description`.

**`name`**: kebab-case, matches directory name exactly (e.g. `qa-team`).

**`description`**: 40–200 words. MUST contain:
- A one-sentence mission statement
- A "Use when" clause listing trigger verbs (write, audit, design, refactor …)
- A "Do NOT use for" clause with delegation targets (`code-team`, `planning-team`, …)
- A "Delivers" clause listing output artifact names

**Word count rule**. Count only the English prose body of the
description. **Exclude**:
- YAML tokens (`>-`, `|`, `|-`)
- CJK / bilingual keyword suffix lines (e.g. `テスト観点・品質計画。測試觀點・品質計畫。`)
- Punctuation characters (`·`, `—`, `・`, `。`, `、`, `「」`, `『』`, backticks)
- Markdown-style list bullets or block-quote markers

**Tokenization rule**. Hyphenated compounds (e.g. `code-team`,
`product-level`, `cross-domain`, `PRODUCT-SPEC.md`) count as **separate
word tokens**: `code-team` = 2 tokens, `cross-domain` = 2 tokens. Same
rule for slash-separated compounds (e.g. `UX/UI`, `investment/market`,
`SLIs/SLOs`) — each slash-separated segment is its own token. This
matches the reference counts used when the 40-word floor was
calibrated in v4.6.1 and ensures evaluator re-verification is
deterministic across readers regardless of whether they use natural
English `wc -w` (which treats hyphens as intra-word) or a
regex-tokenized counter. Without this rule, `research-team`'s
description would count as 38 words (strict) or 43 words
(token-split) depending on interpretation — a 5-word ambiguity that
straddles the 40-word floor.

Rationale for the 40-word floor: the floor is grounded in observed
precedent across qa-team (v4.2.0), docs-team (v4.3.0), devops-team
(v4.4.0), and code-team (v4.6.0). Measured counts stabilize around
44–127 words when the four mandatory clauses (mission / Use when /
Do NOT use for / Delivers) are kept concise and non-repetitive.
An earlier 80-word floor was aspirational and never matched observed
precedent — it was lowered to 40 in v4.6.1 so the standard matches
reality. See `CHK-SKL-001` in `checklists/skill-completeness-checklist.md`.

**Router-skill exemption**. A **router skill** — a skill whose sole
purpose is to route callers to other skills, containing no worker or
evaluator launch templates and no per-workflow protocols — is exempt
from the 40-word minimum. Current example: `using-domain-teams`
(~36 words). Router skills still MUST contain `Use when` / `Do NOT
use for` clauses but may omit the mission sentence and Delivers list
since they deliver routing decisions, not artifacts.

**Optional CJK keyword suffix**: one trailing line of Traditional Chinese /
日本語 keywords for multilingual router discovery, e.g.
`テスト観点・品質計画。測試觀點・品質計畫。`.

## Persona Block

Immediately after the frontmatter, write the persona opening
(~15–30 lines). The persona establishes voice and grounding.

Required elements:
- **Opening stance**: "You are a {role}." or a philosophical premise
- **Primary-source anchors**: list 2-5 authoritative sources the skill grounds on
- **Mission line**: `Mission: ensure it's {outcome}.` — single sentence
- **Delivers line**: `Delivers: {artifact list}.` — comma-separated
- **Done when line**: `Done when: {completion criterion}.` — usually "all triggered quality gates pass."

## Required Sections (in order)

1. **Persona** (the opening block above)
2. **When to Use** — bullet list of trigger scenarios
3. **When NOT to Use** — bullet list with arrow delegation (`→ code-team`)
4. **Language** — `Detect the user's language and pass it as output_language to all agent launch prompts.`
5. **Context Discovery** — 2-3 step numbered list for pre-work state assessment
6. **Quality Gates** — 4 sub-sections: SELF Check / MUST Gates / SHOULD Gates / MAY Gates (see rules below)
7. **Gate Protocol** — evaluator launch rules + verdict handling + guard rails
8. **Resource Manifest** — worker default resources + evaluator default resources
9. **Behavioral Rules** — worker vs evaluator role boundaries
10. **Agents** — table with agent name, role, model
11. **Agent Launch Protocol** — worker and evaluator launch templates (fenced code blocks)
12. **Workflows** — one sub-section per workflow, each with phase table
13. **Cross-Domain Awareness** — lightweight vs switch-to-other-team guidance
14. **Worker BLOCKED Handling** — what to do if worker returns BLOCKED

Additional sections are permitted (e.g. `Note on Global Context` in devops-team)
but MUST come between Persona and Quality Gates, or as a clearly marked appendix
after Worker BLOCKED Handling.

## Quality Gates Sub-Section Rules

The `## Quality Gates` section has exactly four sub-sections in this
order: `### SELF Check`, `### MUST Gates`, `### SHOULD Gates`, `### MAY Gates`.
**All four sub-sections are structurally required** — the presence of each
is a signal that the 4-tier system has been consciously evaluated for
this skill. See `gate-system.md` for what each tier means.

### SELF Check

Always present. Written as a numbered 4-step process, not a table.
SELF check is not a file; it lives inline in SKILL.md.

### MUST Gates

Required sub-section. Use a table with columns `Gate | Trigger | File`.
At least one MUST gate is required — every domain-team skill must have
at least one non-skippable quality check.

### SHOULD Gates

Required sub-section. Use a table with columns `Gate | Trigger | File`.
Same column shape as MUST. A skill may have zero SHOULD gates, in which
case write `None currently.` followed by an optional `Future candidates: …` line.

### MAY Gates — table format and empty case

Required sub-section. **Do NOT omit** this sub-section even when there
are no MAY gates currently defined — its presence is the structural
signal that MAY tier was considered.

**When there are one or more MAY gates**: use the SAME table shape as
MUST and SHOULD, i.e. `Gate | Trigger | File`. Do NOT use a 2-column
`Gate | File` table — missing the `Trigger` column is a convention
drift and makes the gate look like a standing rule rather than an
on-demand check.

**When there are no current MAY gates**: write `None currently.`
optionally followed by a `Future candidates: {list}` sentence
describing gates that might be added later. Example (from
`code-team/SKILL.md`):

```markdown
### MAY Gates

None currently. Future candidates: per-gate-file linting, TDD
discipline audit, code-review checklist if a code-review protocol
is added.
```

**Do NOT** simply omit the sub-section, and do NOT write only a header
with no content.

## Research Subdirectory Convention

Some skills have an **optional** fifth subdirectory, `research/`, that
holds primary-source grounding audit trails produced during grounding
refactors. See `file-conventions.md` §Directory Semantics for the full
definition. Key points for SKILL.md authors:

### SKILL.md and runtime files do NOT structurally depend on research/

The rule below is **about runtime dependencies**, not about whether the
letters `research/` are allowed to appear anywhere in SKILL.md. The
goal is to keep worker and evaluator agents from trying to Read
research files at runtime. Structural references cause runtime reads;
prose rationale references do not.

**Forbidden (structural — cause runtime reads):**

- Listing `research/*.md` in the Resource Manifest section.
- Including `research/*.md` in worker or evaluator launch template
  `standards` arrays, `protocol:` field, or `gate_file:` field.
- Cross-referencing research files from other standards, protocols, or
  gate files in a way that implies the worker/evaluator should read
  them (e.g. "see `research/grounding-v4.8.0.md` for the full SC list").
  Standards must cite primary sources directly in their own
  `## Primary Sources` section; the research note is the audit trail
  for *why those sources were chosen*, not a runtime dependency.

**Permitted (prose — maintainer-facing rationale):**

- Mentioning `research/grounding-v{X.Y.Z}.md` by name in SKILL.md body
  sections whose purpose is maintainer-facing rationale (e.g.
  `## Note on Global Context`, `## Appendix`, or CHANGELOG-adjacent
  prose), provided the reference is a pointer for human reviewers
  and does not appear in any field that an agent launch would
  interpret as a file path to Read.
- Referencing research notes in commit messages, PR descriptions, and
  repo-level documentation outside the skill directory.

The distinguishing test: "Would a worker or evaluator agent, following
its launch template literally, end up calling the Read tool on this
path?" If yes → structural reference → forbidden. If no → prose
reference → permitted.

### When research/ exists vs doesn't

- A skill may have zero or one `research/grounding-v{X.Y.Z}.md` file
  per grounded version.
- Pre-v4.7.0 grounded skills are **grandfathered without backfill** if
  their original research was not captured in an importable form. The
  absence of `research/` does NOT imply ungrounded — only that the
  research audit trail pre-dates the in-repo convention.
- `CHK-SKL-012` (directory structure) allows `research/` as an optional
  subdirectory; any OTHER unexpected subdirectory is still FATAL.

### Diátaxis exemption

`research/` files are **explicitly exempt** from the Diátaxis
single-quadrant rule that docs-team enforces (see
`docs-team/standards/diataxis-taxonomy.md`). Grounding research notes
are fundamentally mixed-mode (Explanation prose for overview +
Reference tables for source verification + ADR-style decision sections
for JP integration / tier choices). They are maintainer-facing raw
artifacts, not polished user-facing documentation, and forcing them
into a single Diátaxis quadrant would require splitting each note into
2-3 files — heavy overhead with no clear reader benefit.

If a user later wants a research note reformatted as a proper Nygard
ADR or Diátaxis Explanation, they can invoke docs-team **separately**
as an optional downstream consumer. docs-team is NOT a mandatory
pipeline stage for grounding research.

## Token Budget

- **Hard cap**: ~6,000 tokens / ~4,500 words (triggers Skill Coherence rubric 🔴)
- **Soft target**: ~3,000–4,500 tokens
- **Warning zone**: ~4,500–6,000 tokens (🟡 in coherence rubric)
- Use word/token count rather than line count — lines vary too much in density

Historical precedent:
- qa-team: 268 lines
- docs-team: 319 lines
- devops-team: 361 lines
- research-team: 283 lines

## Markdown Conventions

- **Phase tables**: `| Phase | Agent | Protocol | Input | Output | Notes |`
- **Gate tables**: `| Gate | Trigger | File |`
- **Launch templates**: fenced code blocks with `### Task` / `### Resource Paths` / `### Input` headers
- **Cross-skill references**: use team name only (`code-team`, `research-team`), never deep file paths
- **Internal file references**: relative from skill root (`standards/x.md`), never absolute paths

## Anti-Patterns

- ❌ Inlining gate criteria content into SKILL.md (SSOT is in the gate file)
- ❌ Embedding standard content into launch prompt (agents must Read paths themselves)
- ❌ Absolute paths like `/Users/kouko/GitHub/monkey-skills/domain-teams/skills/…`
- ❌ Nested subdirectories under `standards/`, `protocols/`, etc.
- ❌ Workflow phases marked with `--` as protocol (means the workflow is broken)
- ❌ "Required Reading" sections listing everything — use Resource Manifest instead
