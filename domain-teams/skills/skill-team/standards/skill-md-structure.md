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

**`description`**: 80–200 words. MUST contain:
- A one-sentence mission statement
- A "Use when" clause listing trigger verbs (write, audit, design, refactor …)
- A "Do NOT use for" clause with delegation targets (`code-team`, `planning-team`, …)
- A "Delivers" clause listing output artifact names

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
6. **Quality Gates** — 4 sub-sections: SELF Check / MUST Gates / SHOULD Gates / MAY Gates
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

## Line Budget

- **Hard cap**: 500 lines (triggers Skill Coherence rubric 🔴)
- **Soft target**: 300–380 lines
- **Warning zone**: 400–500 lines (🟡 in coherence rubric)

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
