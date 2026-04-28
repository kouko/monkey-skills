# skill-team

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Meta-skill that builds and refactors domain-team skills with primary-source grounding, 4-tier gate hierarchy, and 3-commit Conventional Commits discipline.

**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) → `domain-teams`
**Invocation**: routed through `using-domain-teams`, or directly via `domain-teams:skill-team`
**Grounding**: Anthropic Agent Skills spec · Conventional Commits 1.0.0 · Semantic Versioning 2.0.0 · qa-team v4.2.0 / docs-team v4.3.0 / devops-team v4.4.0 refactor precedents

## Table of contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Architecture](#architecture)
- [Quality gates](#quality-gates)
- [File layout](#file-layout)
- [Visibility convention](#visibility-convention)
- [Contributing](#contributing)
- [License](#license)

## Background

skill-team is the meta-skill. Its only job is to build and refactor
**domain-team skills** — skills that follow the
`standards/protocols/checklists/rubrics` directory layout, launch
worker / evaluator agents, and enforce the 4-tier gate hierarchy.

The conventions skill-team codifies were not invented. They were
distilled from three prior grounded-team refactors — qa-team v4.2.0
(ISTQB / VSTeP), docs-team v4.3.0 (Diátaxis / Google Style / JTAP),
devops-team v4.4.0 (Google SRE / DORA / 12-Factor). The tribal
knowledge that accumulated across those refactors lives in this skill's
8 standards files.

**Scope is deliberately narrow.** For generic Claude skill authoring
(non-domain-team), use `superpowers:writing-skills` or Anthropic's
`skill-creator`. For obsidian skills, philosophers-toolkit skills,
plugin-level packaging, or utility scripts, this skill does not apply.

**Meta-circularity note**: skill-team was bootstrapped before it
existed. The first creation was manual because no tool could yet apply
the conventions it codifies. Subsequent skill creations and refactors
all run through skill-team.

## Install

skill-team ships with the monkey-skills plugin. There is no separate
install. The skill is discovered by Claude when the plugin is enabled.

## Usage

skill-team has no slash command. It is invoked indirectly:

- Through `using-domain-teams` when intent matches (e.g. "build a new
  team skill", "refactor qa-team grounding")
- Directly via the Skill tool: `domain-teams:skill-team`

### Workflows

| Workflow | When to use |
|----------|-------------|
| **New Skill Creation** | Building a brand-new domain-team skill for an uncovered domain (e.g. adding `security-team`, `data-team`) |
| **Skill Redesign** (grounding refactor) ⭐ primary | Existing team lacks primary-source grounding, has a broken workflow phase, or needs structural improvement |

Both workflows produce a 3-commit branch ready for PR:

```
Commit 1: standards CREATE/MODIFY              (the SSOT rules)
Commit 2: protocols + gates CREATE/MODIFY      (the workflow recipes + verdict criteria)
Commit 3: SKILL.md + router + version bump     (wire it up + ship)
```

The split is not cosmetic. Each commit has a focused diff that maps to
one layer of the skill — reviewers can audit each layer independently,
and bisecting works when something breaks.

## Architecture

```
skill-team (checkpoint orchestrator)
  ├── worker (sonnet)     ← protocols/ + standards/
  └── evaluator (opus)    ← checklists/ + rubrics/ + standards/
```

Worker executes the build / refactor protocol. Evaluator scores gates.
The main agent orchestrates and applies verdict rules.

When the build needs primary-source grounding research, skill-team
delegates to `research-team` rather than executing research itself.
Research artifacts land at `research/grounding-v{X.Y.Z}.md` inside the
target skill (audit trail), per `file-conventions.md` §research/ rules.

## Quality gates

Four-tier system per `standards/gate-system.md`.

| Tier | Behavior | Examples in skill-team |
|------|----------|------------------------|
| **SELF** | Every delivery, always — main agent self-audits | All workflows |
| **MUST** | Auto-trigger, non-skippable | Skill Completeness, Commit Split Validity |
| **SHOULD** | Auto-trigger, skippable with stated reason | Primary Source Grounding, Skill Coherence |
| **MAY** | User-requested or workflow-specific | None currently. Future: per-gate-file linting, workflow dependency graph analysis |

Gate verdicts: `PASS` / `PASS_WITH_NOTES` (auto-revise, max 2 rounds) /
`NEEDS_REVISION` (escalate to user).

The Commit Split Validity gate runs `git log --stat` against `main`;
the artifact under evaluation is the branch, not a single file.

## File layout

```
skill-team/
├── README.md                              # Human-facing overview (English, default)
├── README.ja.md                           # Japanese translation
├── README.zh-TW.md                        # Traditional Chinese translation
├── SKILL.md                               # LLM-discovery SSOT
├── standards/                             # 8 SSOT rules — the codified tribal knowledge
│   ├── skill-md-structure.md                 # SKILL.md structure, required sections, token budget
│   ├── file-conventions.md                   # 4-subdirectory layout, top-level files, path discipline
│   ├── gate-system.md                        # SELF / MUST / SHOULD / MAY tiers, verdict semantics
│   ├── grounding-principle.md                # Primary-source rule, JP integration strategy
│   ├── agent-interface.md                    # Resource Paths Input Contract, behavioral boundaries
│   ├── commit-convention.md                  # 3-commit split, Conventional Commits, semver
│   ├── mermaid-usage-guidelines.md           # When to use Mermaid vs prose, syntax conventions
│   └── user-terminal-handoff.md              # TTY-bound commands MUST be handed off (auth, sudo, TUIs)
├── protocols/                             # Workflow SOPs
│   ├── skill-brainstorming.md                # Scope decomposition for ambiguous requests
│   ├── grounding-research.md                 # Primary-source research workflow (delegates to research-team)
│   ├── new-skill-creation.md                 # 10-phase build for a new team
│   └── skill-redesign.md                     # 6-phase refactor for an existing team
├── checklists/                            # Binary gates
│   ├── skill-completeness-checklist.md       # MUST — SKILL.md structural compliance
│   └── commit-split-checklist.md             # MUST — branch commit-history validity
└── rubrics/                               # Qualitative gates
    ├── primary-source-grounding.md           # SHOULD — citation quality of new standards
    └── skill-coherence.md                    # SHOULD — internal consistency of completed skill
```

skill-team has no `research/` subdirectory. Its conventions trace to
the Anthropic Agent Skills spec and the qa/docs/devops refactor
precedents — both already cited inline in the standards files. No
in-repo grounding note is required because skill-team has no external
domain to research.

## Visibility convention

skill-team v5.2.0+ defines a `TaskUpdate` emission convention that all
workflow-type domain-team skills (research-team, code-team, docs-team,
devops-team, qa-team, planning-team, investing-team, copywriting-team,
design-team) must follow:

- **Phase transition**: emit at start and end of each major phase
- **Milestone**: emit at each section / deliverable / sub-step completed
- **Heartbeat**: silent period MUST NOT exceed 60 seconds, even during
  extended reasoning

The convention provides a **probabilistic guarantee** — compliance
depends on agent behavior. For strict structural guarantee on
very-long-running dispatches, decompose the task into shorter
sub-dispatches (phase-split architecture).

See SKILL.md §Visibility Convention for full text and the controller
narration convention.

## Contributing

skill-team is part of the monkey-skills plugin. Issues and PRs go to
the parent repository: <https://github.com/kouko/monkey-skills>.

When proposing changes:

- Apply skill-team to itself (dogfood) — any modification to
  `standards/` runs through `skill-redesign.md` Phases 4-6 with the
  3-commit split
- Cite primary sources for new conventions — see
  `standards/grounding-principle.md`. The qa/docs/devops precedents
  count as primary for tribal-knowledge claims; external standards
  (Anthropic, Conventional Commits, semver) count for everything else
- Run `checklists/skill-completeness-checklist.md` and
  `checklists/commit-split-checklist.md` against your branch before
  submitting
- Keep `SKILL.md` within the 6,000-token hard cap defined in
  `standards/skill-md-structure.md`

## License

MIT © 2026 kouko. See [LICENSE](../../../LICENSE) at the repo root.
