# docs-team

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Diátaxis-grounded documentation skill with checkpoint quality gates and an opt-in 4× cost-saving quick mode.

**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) → `domain-teams`
**Slash command**: `/docs`
**Grounding**: Diátaxis · Google Style · Microsoft Style · Standard README · Nygard ADR · OpenAPI 3.2.0 · Write the Docs · JTAP · Software Engineering at Google Ch.10

## Table of contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Architecture](#architecture)
- [Quality gates](#quality-gates)
- [Cost (full vs quick mode)](#cost-full-vs-quick-mode)
- [File layout](#file-layout)
- [Contributing](#contributing)
- [License](#license)

## Background

Documentation rots faster than code. The four most common failures are
mode-mixing (a how-to that lectures, a tutorial that lists every option),
inconsistent reference, undocumented architecture decisions, and stale
content nobody trusts. docs-team prevents each one with a checkpoint:
single-quadrant Diátaxis discipline, OpenAPI-shaped reference, Nygard
ADRs with mandatory consequences, and freshness frontmatter that ages
visibly.

The skill grounds every rule in a primary source. None of the
conventions are invented — Diátaxis traces to Daniele Procida, the
style rules to Google and Microsoft, the README spec to RichardLitt,
the ADR template to Michael Nygard, and the docs-rot mitigation to
*Software Engineering at Google* Chapter 10.

## Install

docs-team ships with the monkey-skills plugin. To use it:

```bash
# In Claude Code with the monkey-skills plugin enabled:
/docs <your request>
```

No separate installation. The plugin's `domain-teams` directory contains
the SKILL.md that Claude discovers automatically.

## Usage

Invoke with `/docs` followed by the request, or let the
`using-domain-teams` router pick docs-team based on intent.

```
/docs write a README for this Go library
/docs document the payment service architecture
/docs write an ADR for our token-bucket rate limiter
/docs audit the docs/ directory for staleness
/docs draft a quick how-to for rotating API keys     ← quick mode
```

The skill detects the artifact type, picks the right Diátaxis quadrant
or composite template, and runs the gates that match.

### Workflows

| Workflow | Output | MUST gate | SHOULD gate |
|----------|--------|-----------|-------------|
| Write Tutorial | Learning-oriented walk-through | Mode Clarity | Style |
| Write How-to Guide | Task-oriented recipe | Mode Clarity | Style |
| Write Reference | API / CLI / config reference | Mode Clarity | Style |
| Write Explanation | Design rationale / concept | Mode Clarity | Style |
| Write README | Standard README spec | README Completeness + per-section Mode Clarity | Style |
| Write ADR | Architecture Decision Record | ADR Structure | Style |
| Write API Reference | OpenAPI-shaped reference | Mode Clarity | Style |
| Write Architecture | Overview / component spec / data flow | Architecture Doc Completeness | Style |
| Documentation Audit | Diátaxis + freshness audit report | — | Freshness |
| Codebase Assessment | Health report (code or doc mode) | — | — |
| Quick Write | Same artifacts, SELF check only | — (gates skipped) | — |

## Architecture

```
docs-team (checkpoint orchestrator)
  ├── worker (sonnet)     ← protocols/ + standards/
  └── evaluator (opus)    ← checklists/ + rubrics/ + standards/
```

Worker writes artifacts. Evaluator scores gates. The main agent
orchestrates, applies verdict rules, and auto-revises on
`PASS_WITH_NOTES` (max 2 rounds).

In quick mode, the main agent runs the protocol inline without
dispatching either subagent — sacrificing gate enforcement for ~4×
lower token cost.

## Quality gates

Four-tier system per `domain-teams:skill-team` gate-system standard.

| Tier | Behavior | Examples in docs-team |
|------|----------|-----------------------|
| **SELF** | Every delivery, always — main agent self-audits | All workflows |
| **MUST** | Auto-trigger, non-skippable | Mode Clarity, README Completeness, ADR Structure, Architecture Doc Completeness |
| **SHOULD** | Auto-trigger, skippable with stated reason | Style, Freshness |
| **MAY** | User-requested or workflow-specific | Tech Debt audit, Freshness opt-in for un-metadata-ed docs |

Verdicts: `PASS` / `PASS_WITH_NOTES` (auto-revise) / `NEEDS_REVISION`
(escalate to user) / `NEEDS_METADATA` (Freshness only — the gate
cannot apply, not a failure).

## Cost (full vs quick mode)

| Mode | Per task | What runs | When to use |
|------|---------:|-----------|-------------|
| **Full** (default) | ~46K tokens | Worker + evaluator × MUST/SHOULD gates + auto-revision | Production docs, ADRs, API references, public release READMEs |
| **Quick** (opt-in) | ~11K tokens | Main agent inline + SELF check only | Drafts, personal notes, low-stakes iteration |

Quick mode is **refused** for ADRs, API references, public-facing
release READMEs, and architecture documentation — the gate audit
trail is the artifact's value for these.

`/docs verify <artifact>` runs gates retroactively on a quick-mode
output (~25K), letting you defer the verification decision without
paying full mode up front.

## File layout

```
docs-team/
├── README.md                        # This file (human-facing overview)
├── SKILL.md                         # LLM-discovery SSOT (frontmatter + workflows + gate triggers)
├── standards/                       # Stable SSOT rules
│   ├── diataxis-taxonomy.md            # 4-quadrant vocabulary (Procida)
│   ├── style-conventions.md            # Google + Microsoft + JTAP
│   ├── docs-as-code.md                 # Write the Docs philosophy
│   ├── freshness-metadata.md           # Frontmatter convention (SWE@Google)
│   ├── api-reference-structure.md      # OpenAPI 3.2.0 fields
│   ├── pre-writing-checklist.md        # LLM-defensive reading rules
│   └── architecture-doc-structure.md   # L0–L4 hierarchy + Mermaid rules
├── protocols/                       # Workflow SOPs
│   ├── doc-writing-router.md           # Mode + quadrant routing
│   ├── quick-write.md                  # Cost-saving inline workflow
│   ├── write-tutorial.md
│   ├── write-how-to.md
│   ├── write-reference.md
│   ├── write-explanation.md
│   ├── write-readme.md                 # Standard README composite
│   ├── write-adr.md                    # Nygard + MADR
│   ├── write-api-reference.md          # OpenAPI specialization
│   ├── write-architecture.md           # System / component / data flow
│   └── codebase-assessment.md          # Code + doc health audit
├── checklists/                      # Binary gates
│   ├── readme-completeness.md          # Standard README spec
│   └── tech-debt-checklist.md          # Code health (MAY)
├── rubrics/                         # Qualitative gates
│   ├── diataxis-mode-clarity.md
│   ├── adr-structure.md
│   ├── architecture-doc-completeness.md
│   ├── style.md
│   └── freshness.md
└── research/
    └── grounding-v4.3.0.md             # Primary-source audit trail
```

## Contributing

docs-team is part of the monkey-skills plugin. Issues and PRs go to
the parent repository: <https://github.com/kouko/monkey-skills>.

When proposing changes:

- Run the existing gates against your new artifacts before submitting
- Cite primary sources for new rules — no self-invented taxonomies
- Match `domain-teams:skill-team`'s `file-conventions.md` naming rules
  (kebab-case, no nested subdirectories, deletion over deprecation)
- Keep `SKILL.md` within the 6,000-token hard cap; split standards if
  pressure continues

## License

MIT © 2026 kouko. See [LICENSE](../../../LICENSE) at the repo root.
