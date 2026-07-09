# Claude Code — host tool reference for loom-discovery

This plugin's skills phrase host interaction in host-neutral prose
("delegate the research", "search the web for the missing evidence",
"read the prior evidence registry"). This file is the concrete Claude
Code call shape that prose resolves to, for both member skills reached
through this router.

> Grounding: skill/agent names below verified 2026-07-10 against shipped
> frontmatter (`loom-discovery/skills/*/SKILL.md`,
> `research-toolkit/skills/deep-deep-research/`,
> `domain-teams/skills/planning-team/`) — same evidence grain as the
> sibling `codex-tools.md`.

## Invoking the member skills

| Skill | Mechanism |
|---|---|
| `business-value` | `Skill(skill: "business-value")` |
| `user-insights` | `Skill(skill: "user-insights")` |

If the user types `/business-value` or `/user-insights`, that is an
explicit invocation — load it via the `Skill` tool directly, no routing
decision needed from this file.

## Research dispatch (user-insights)

- **Heavyweight** (more than 3 research questions, OR external/user
  evidence is needed): delegate via
  `Skill(skill: "research-toolkit:deep-deep-research")` — per the
  cross-plugin delegation contract, pass paths + a structured seed
  context; never inline the analysis inside user-insights itself.
- **Light inline scope** (≤3 questions, no external evidence needed):
  call the `WebSearch` tool directly, one call per research question,
  and write findings straight into
  `docs/loom/discovery/<date>-<slug>/research/<question-slug>.md`.

## Business-value delegation

`business-value` never analyzes market sizing, go-to-market, or revenue
inline — that delegates to `domain-teams:planning-team`. From Claude
Code, that is `Skill(skill: "domain-teams:planning-team")` with paths
passed, not file content (Cross-Plugin Delegation Contract, this repo's
CLAUDE.md).

## Reading prior evidence

Before starting a new discovery pass on an existing slug, `Read`
`docs/loom/discovery/<date>-<slug>/evidence.md` if it already exists —
the atomic-research model means evidence outlives any single report;
don't re-research a claim already logged there.
