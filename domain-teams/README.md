# domain-teams

> Domain team skills with checkpoint-based quality gates — planning (企画), code, design, research, copywriting, investing, and more.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 5.5.1
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

## Background

`domain-teams` is a Claude Code plugin that packages 10 domain-specialized
skills behind a uniform agent + gate architecture. Each team owns its own
protocols, standards, checklists, and rubrics — anchored on primary
sources (textbooks, RFCs, academic papers, official docs), not on
LLM-invented heuristics.

Two shared agents underpin every team:

- **`worker`** — produces artifacts (code, docs, specs, copy, research
  reports). Reads the protocol + standards files passed by the dispatching
  skill, executes the SOP, and emits the deliverable. Never judges its own
  output. May escalate `BLOCKED` if a task would require hallucinating.
- **`evaluator`** — judges artifacts against a checklist (PASS /
  FAIL_FATAL / FAIL_FIXABLE per item) or a rubric (🔴 / 🟡 / 🟢 flags).
  Returns `PASS`, `PASS_WITH_NOTES` (auto-revise loop), or `NEEDS_REVISION`
  (escalate to user). Never modifies the artifact.

This separation — *workers produce, evaluators judge* — is the load-bearing
behavioral rule of the plugin.

## Architecture: 4-tier quality gates

Every team defines its own gates across four tiers:

```
SELF check  (every delivery, worker self-verification)
   │
   ▼
MUST gates  (auto-trigger, non-skippable)
   │   security / architecture / completeness
   ▼
SHOULD gates  (auto-trigger, skippable with stated reason)
   │   quality / spec consistency / mode clarity
   ▼
MAY gates  (opt-in, run when relevant)
       per-team optional disciplines
```

Gate verdict flow:

```
worker artifact ──► evaluator ──► verdict
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
              PASS          PASS_WITH_NOTES         NEEDS_REVISION
           gate cleared      auto-revise loop       escalate to user
                            (max 3 rounds, fresh
                             evaluator per round)
```

`SELF` is owned by the worker; `MUST` / `SHOULD` / `MAY` always launch
the `evaluator` agent with an explicit checklist or rubric file. Each
gate file's path is declared in the team's SKILL.md `Quality Gates`
section, and each verdict is emitted by the evaluator alone — never
synthesized by the worker.

## Router skill

`using-domain-teams` is the entry-point router. Use it when starting any
domain task and you are unsure which team applies. It exposes:

- An *Available Teams* table (mission + delivers per team)
- An *Intent Routing* table (specific user intents → team)
- An *Ambiguous Cases* table (multi-team sequences, e.g.
  `planning-team` → `code-team` → `qa-team` → `devops-team`)

Skip the router when you already know the destination — invoke the team
skill directly.

## Teams

Each team skill is invocable by its name as an auto-generated slash command (e.g. `/code-team`, `/qa-team`).

| Team | Slash command | Role | Key grounding |
|------|---------------|------|---------------|
| `code-team` | `/code-team` | Develop code with primary-source-grounded quality gates | Clean Code (Martin 2008), Pragmatic Programmer (Hunt & Thomas 2019), SOLID, TDD (Beck 2002), Refactoring 2nd ed (Fowler 2018), Working Effectively with Legacy Code (Feathers 2004), OWASP ASVS v5.0.0, 徳丸本 Ch.6 |
| `docs-team` | `/docs-team` | Write documentation and assess codebases with Diátaxis discipline | Diátaxis taxonomy, Standard README (RichardLitt), Google + Microsoft style, Trong-Tra `documentation-specialist` (readme + architecture L0–L4) |
| `qa-team` | `/qa-team` | Plan and verify tests beyond unit level | 品質は工程で作り込む — built-in quality; E2E / integration / performance test strategy |
| `devops-team` | `/devops-team` | Ship code safely with CI/CD, containers, and IaC | Google SRE, DORA, 12-Factor App primary sources |
| `research-team` | `/research-team` | Conduct primary-source-grounded research with citation verification | Systematic-review rigor, confidence calibration, operator-perspective market analysis |
| `design-team` | `/design-team` | Design with accessibility and quality review | 行為設計 (behavioral design), 感性工学, 無意識の設計; UI / UX / a11y |
| `planning-team` | `/planning-team` | Cross-domain project planning (企画) | JTBD, Lean Startup, OKR, 4 Big Risks, Business Model Canvas / Lean Canvas |
| `copywriting-team` | `/copywriting-team` | Write persuasive marketing copy | Japanese advertising tradition (神田昌典 PASONA / 谷山 / 糸井) + Anglo persuasion psychology (Cialdini, Schwartz Awareness Levels, Ogilvy) |
| `investing-team` | *(invoked via delegation)* | Make defensible investment decisions backed by primary-source frameworks | Investment Clock (regime), Buy/Hold/Sell verdicts, Taiwan equity (三大法人 / 月營收 / 董監持股 / 融資融券) |
| `skill-team` | `/skill-team` | Build or modify domain-team skills with convention discipline | 4-tier gate design, primary-source grounding, 3-commit split, dual-file (README + SKILL.md), companion file pattern |
| `using-domain-teams` | `/using-domain-teams` (router) | Route intents to the right team | — |

`investing-team` ships without a slash command because it is normally
reached through the `investing-toolkit` plugin via the Cross-Plugin
Delegation Contract (see below).

## Repository structure

```
domain-teams/
├── .claude-plugin/
│   └── plugin.json              # plugin metadata (SSOT)
├── agents/
│   ├── worker.md                # generic task executor (sonnet)
│   └── evaluator.md             # generic quality evaluator (opus)
├── skills/
│   ├── using-domain-teams/      # router
│   ├── code-team/
│   ├── copywriting-team/
│   ├── design-team/
│   ├── devops-team/
│   ├── docs-team/
│   ├── investing-team/
│   ├── planning-team/
│   ├── qa-team/
│   ├── research-team/
│   └── skill-team/
├── CHANGELOG.md
├── README.md
├── README.ja.md
└── README.zh-TW.md
```

Each `skills/<team>/` directory is self-contained:

```
<team>/
├── SKILL.md          # frontmatter + body, ~6,000 token budget
├── protocols/        # SOPs the worker follows
├── standards/        # baseline rules the artifact must comply with
├── checklists/       # binary PASS/FAIL gate files
├── rubrics/          # qualitative 🔴/🟡/🟢 gate files
├── research/         # grounding notes + citation verification (some teams)
└── README.md         # optional skill-internal overview (some teams)
```

Bundled files in `SKILL.md` are referenced by relative paths
(e.g. `checklists/security-checklist.md`), not absolute paths.

## Agent behavioral rules

The `worker` / `evaluator` split is enforced as a behavioral rule, not
just a workflow convention:

- **`worker`** produces artifacts. Does NOT produce gate verdicts. May
  read any domain file (rubrics, checklists, standards) for self-check
  but cannot emit a `PASS` / `PASS_WITH_NOTES` / `NEEDS_REVISION` verdict.
- **`evaluator`** produces verdicts. Does NOT modify artifacts. Returns
  feedback the worker can act on, but never edits files itself.
- Knowledge access is open — the constraint is on *behavior*, not on
  *which files an agent may read*.
- Each gate retry launches a *fresh* evaluator with no accumulated
  context — only the original requirements + current artifact + feedback.
- Worker honors `output_language` from the dispatcher's launch prompt;
  technical jargon is preserved in its original language (no
  force-translation).

Both agents support a `BLOCKED` escape hatch: if a task would require
hallucinating facts, the agent emits a structured `BLOCKED` status
instead of producing a flawed artifact.

## Cross-Plugin Delegation Contract

domain-teams is the analysis + gate authority that other plugins
delegate to. The first such case was
`investing-toolkit:investment-memo-writer` → `domain-teams:investing-team`.

The contract:

1. **Delegation = pass paths + structured seed context.** Never pass
   file content; never inline analysis results.
2. **Delegation target receives full authority.** The receiving skill
   loads its own standards, runs its own gates, and emits its own
   verdict. The delegator does not interfere.
3. **Data layer stays in the toolkit; analysis layer stays in
   domain-teams.** Toolkit plugins handle data fetch + pipeline
   orchestration; domain-teams handles analysis, primary-source
   anchoring, and gate enforcement.
4. **Gate verdicts flow back.** Verdicts (`PASS` / `PASS_WITH_NOTES` /
   `NEEDS_REVISION`) propagate to the orchestrating skill — never
   swallowed.
5. **Cross-plugin path resolution uses plugin name + skill path**
   (e.g. `domain-teams:investing-team`), not filesystem absolute paths.

Forbidden: re-implementing a domain-team's gate logic inside another
plugin (gate bypass), copying domain-teams standards into other
plugins (drift), or letting a data-fetcher agent perform analysis.

## Skill-Internal README convention

As of v5.5.1, `skill-team/standards/file-conventions.md` formalizes
that **skill-internal READMEs (`skills/<name>/README.md` and i18n
siblings) do not require the docs-team workflow**. They are authored
directly under a lighter discipline:

- Language switcher at top
- English-noun preservation (per `docs/i18n/glossary-*.md`)
- Link to sibling SKILL.md
- No contradiction with SKILL.md (SKILL.md is the SSOT; README is an
  overview)
- Upstream attribution if the skill is derivative

`docs-team` workflow IS still required for: plugin-level READMEs,
repo-level READMEs, public release READMEs, ADRs, API references,
runbooks, and architecture L0–L4 documents.

## License

MIT — see [LICENSE](../LICENSE) at the repository root.
