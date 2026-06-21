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

**`description`**: **≤250 characters** (house standard — target ~150;
see `docs/skill-mining/2026-06-19-skill-description-standard.md`), with a
**≥30 word-token floor** so a team description stays substantive. MUST contain:
- A one-sentence mission statement
- A "Use when" clause listing trigger verbs (write, audit, design, refactor …)
- A **positive delegation redirect** for adjacent work (e.g. "Docs → docs-team")
  — the house standard refutes "Do NOT use for X" behavioral negation, so use a
  short positive "→ sibling-team" pointer instead
- A "Delivers" clause (optional — keep if it fits the char budget)

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
reality, then to **30 in the 2026-06-20 house-description-standard
reconciliation**: the repo-wide lean ≤250-char standard caps descriptions
shorter than a 40-word floor allows for verb-heavy team skills (e.g.
investing-team / research-team), so the floor drops to 30 to keep a
substantive minimum while admitting the lean style. See `CHK-SKL-001` in
`checklists/skill-completeness-checklist.md`.

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
5. **Context Discovery** — 2-3 step numbered list for pre-work state assessment (agent-internal)
6. **Empty Invocation Fallback** — user-facing onboarding when input is empty or too sparse to proceed (see rules below)
7. **Quality Gates** — 4 sub-sections: SELF Check / MUST Gates / SHOULD Gates / MAY Gates (see rules below)
8. **Gate Protocol** — evaluator launch rules + verdict handling + guard rails
9. **Resource Manifest** — worker default resources + evaluator default resources
10. **Behavioral Rules** — worker vs evaluator role boundaries
11. **Agents** — table with agent name, role, model
12. **Agent Launch Protocol** — worker and evaluator launch templates (fenced code blocks)
13. **Workflows** — one sub-section per workflow, each with phase table
14. **Cross-Domain Awareness** — lightweight vs switch-to-other-team guidance
15. **Worker BLOCKED Handling** — what to do if worker returns BLOCKED

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

## Empty Invocation Fallback Rules

**Context Discovery** (§5) is agent-internal state mapping — what the
agent reads before starting work. **Empty Invocation Fallback** (§6)
is the user-facing behavior specification for when the user invokes
the skill with no prompt or a prompt too sparse to act on. These two
sections serve different purposes and MUST be kept separate.

### Required elements (3)

Every SKILL.md §Empty Invocation Fallback section MUST specify:

1. **Surface orientation**: synthesize a structured orientation at
   runtime per §Surface Orientation Format below. Draw from existing
   sections (frontmatter / When to Use / When NOT to Use / Workflows /
   intake protocol) — do NOT duplicate content as static prose. The
   goal is to orient the user with "what I do / how we work together /
   what to have ready", not a lecture.
2. **Route to intake**: if this skill has a brainstorming protocol
   (typically `protocols/{team}-brainstorming.md`), invoke it.
   Otherwise, ask 2-3 bootstrap questions that establish: (a) scope /
   artifact type, (b) inputs / constraints, (c) output expectation.
3. **Sufficient-context skip**: SKIP the fallback (proceed directly to
   Context Discovery) when ANY of the following provides an actionable
   brief:
   - (a) Current-turn prompt: ≥50 chars with a concrete ask
   - (b) Prior conversation turns already state scope / artifact /
     output expectation
   - (c) IDE context (`<ide_selection>`, opened files) identifies the
     target artifact
   - (d) Referenced plan (`.claude/plans/*.md`) / memory file encodes
     the brief
   - (e) Upstream skill handoff — the main agent provided a prior
     skill's output as this skill's input

   Intent: don't lecture users when context is already rich. The
   fallback is for **genuine cold starts only**. Checking only the
   current-turn prompt length is a common pitfall that creates
   friction for returning users.

### Hard-gate exception

Skills with mandatory intake protocols (`copywriting-team`,
`planning-team`) explicitly replace element 3 with "Never skip" plus
a short rationale. The intake protocol surfaces elements that context
alone cannot reliably provide — e.g., Schwartz awareness level, voice
reference, job story, risks. These skills trade off returning-user
friction for intake rigor; document the trade-off in the SKILL.md
section.

### Surface Orientation Format

When orientation fires (context-check yielded insufficient brief),
present the following markdown skeleton to the user, filled from the
existing SKILL.md sections cited in each slot:

```markdown
## {team-name} — {first sentence of frontmatter description}

**What I do:**
- {top 3 bullets from §When to Use}

**What I don't do** (use these teams):
- {top 2 bullets from §When NOT to Use, include → delegation arrows}

**How we'll work together:**
1. **Intake**: {1-line summary of intake style — e.g., "Q1-Q10
   structured brainstorming" or "2-3 bootstrap questions"}
2. **Workflow**: {phase names chained from first §Workflows entry}
3. **Delivery**: {from frontmatter "Delivers:" clause}

**To get the best result, have these ready:**
- {2-3 prerequisite bullets — optional; omit if skill is open-ended}

Let's start. {First question from the intake protocol's first phase}
```

All load-bearing slots map to already-required SKILL.md sections —
no new static content is mandated. Prerequisites are optional
per-skill; skills may include an inline prerequisites bullet list in
their §Empty Invocation Fallback body to guide the synthesis.

### Format

Keep the whole §Empty Invocation Fallback body to ~10-15 lines. Do
NOT duplicate the brainstorming protocol's phase table; just reference
the protocol by relative path. Example skeleton:

```markdown
## Empty Invocation Fallback

Triggers when user input is empty OR < 50 chars OR lacks an
actionable brief signal AND no prior context / IDE context /
plan-file / upstream handoff provides one.

1. **Surface orientation**: synthesize per `standards/skill-md-structure.md` §Surface Orientation Format — draw from frontmatter / When to Use / When NOT to Use / Workflows / intake protocol.
2. **Route to intake**: invoke `protocols/{team}-brainstorming.md` — the structured intake protocol that extracts brief via Q1-QN.
3. **Sufficient-context skip**: if any context source provides an actionable brief (current prompt ≥50 chars, prior conversation, IDE context, plan/memory file, upstream handoff), proceed directly to Context Discovery without orientation.

Prerequisites (inline hint for orientation synthesis):
- {prerequisite 1}
- {prerequisite 2}
```

### Router-skill exemption

**Router skills** (skills whose sole purpose is to route callers to
other skills — currently `using-domain-teams` and
`using-philosophers-toolkit`) are EXEMPT from §Empty Invocation
Fallback. Their entire SKILL.md body *is* a routing-on-empty-input
mechanism. Adding this section to a router would be redundant.

Document this exemption in the skill's frontmatter description or in
a brief comment at the top of the Context Discovery section if
present.

## AskUserQuestion Pattern (CHK-SKL-014)

When a SKILL.md has any user-input branching step (mid-execution choice
between 2-4 options), it MUST use Anthropic's `AskUserQuestion` tool with
the **hardened pattern** documented in
[`asking-user-questions.md`](asking-user-questions.md).

The four hardenings (all required):

1. **MUST verb** — `MUST call AskUserQuestion`, not `Use AskUserQuestion`
2. **Args-schema example** — fenced ```json``` block showing tool-call args, not prose Q&A template
3. **Fallback contract** — explicit clause for tool-unavailable environments (subagent / web / sandbox)
4. **(Recommended) marker** — first option's `label` includes `(Recommended)`

A copy-paste mandatory-gate template is provided in
[`asking-user-questions.md`](asking-user-questions.md) §Mandatory-gate template.

**Exemption**: skills with no user-input branching steps. Examples: pure
deterministic skills, single-shot generators, skills where input is
gathered upstream by another skill.

**Why this matters**: industry research and an empirical A/B test confirmed
that the soft-verb pattern fails in three modes (inline fallback, silent
default, tool-unavailable). The 4 hardenings close all three. See
[`asking-user-questions.md`](asking-user-questions.md) for full rationale.

CHK-SKL-014 in [`../checklists/skill-completeness-checklist.md`](../checklists/skill-completeness-checklist.md)
enforces compliance.

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
