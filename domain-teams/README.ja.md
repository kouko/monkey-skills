# domain-teams

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**: 5.2.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

primary-source grounding と checkpoint-based quality gates を備えた domain team skills。9 つの team が単一の `worker`（sonnet）+ `evaluator`（opus）agent ペアを共有します。

## Architecture

```
Team Skill (checkpoint orchestrator)
  ├── worker (sonnet)    ← protocols/ + standards/
  └── evaluator (opus)   ← checklists/ + rubrics/ + standards/

Four-level quality gates:
  SELF    → Agent が各成果物を自己チェック
  MUST    → 自動発動・スキップ不可（例：security、a11y、citation）
  SHOULD  → 自動発動・理由付きでスキップ可（例：quality、UX）
  MAY     → ユーザー要求時のみ（例：QA、tech debt、visual）

Domain knowledge（各 team skill ディレクトリに同梱、open access）：
  protocols/   → 手順形式の SOP（実行ガイド）
  checklists/  → 二値 pass/fail 基準（gate 評価）
  rubrics/     → 定性的 flag 基準（gate 評価）
  standards/   → 基本ルール（共有 SSOT）
  research/    → Grounding audit trail（任意）
```

## Router

| Type | Name | Role |
|------|------|------|
| Skill | `using-domain-teams` | エントリーポイント — リクエストを適切な team へ振り分け |

## Teams

| Team | Slash cmd | Role | Notable grounding |
|------|-----------|------|-------------------|
| `planning-team` | `/planning` | 領域横断のプロジェクト planning（企画）；PRODUCT-SPEC.md を生成 | Business thesis + JTBD |
| `code-team` | `/code` | Code 開発；機能実装・bug 修正・TECH-SPEC.md 執筆 | Clean Code (Martin 2008) + Pragmatic Programmer + SOLID + Kent Beck；外部依存：`feature-dev:code-architect` |
| `docs-team` | `/docs` | Documentation + codebase 評価；README、API docs、tech debt audit | Diátaxis + Google Developer Style + JTAP |
| `qa-team` | `/qa` | Test strategy と計画；E2E、integration、performance | ISTQB + ISO/IEC/IEEE 29119 + VSTeP / HAYST / ゆもつよ |
| `devops-team` | `/devops` | code を安全に届ける；CI/CD、Dockerfiles、IaC、deployment、monitoring | Google SRE + DORA + 12-Factor + Continuous Delivery |
| `design-team` | `/design` | accessibility + quality review を伴う design；UI、wireframes、UX strategy | Norman / Nielsen / WCAG 2.2 + 原研哉 / 深澤 / 黒須 / 上野 |
| `research-team` | `/research` | Primary-source-grounded research；market / competitive / literature review | Systematic-review rigor + citation verification |
| `investing-team` | — | 個別銘柄の Buy/Hold/Sell verdicts、equity research memo、portfolio rebalancing、macro regime 診断 | IC regime + Dalio + CAPE + ISQ (Investment Signal Quality) |
| `copywriting-team` | `/copywriting` | 説得力のある marketing copy — landing page、キャッチコピー、email、voice guide、audit | 神田 PASONA + 谷山 + 今泉 + 川喜田 + Cialdini + Schwartz + McQuarrie & Mick + Lakoff + Thornton |
| `skill-team` | `/skill` | Meta-skill：規律ある慣例で domain-team skills を構築・改修 | Anthropic Agent Skills spec + Conventional Commits + Semver |

合計 10 skills（9 teams + router）。9 slash commands（`investing-team` は `investing-toolkit` plugin router 経由でアクセス）。

## Repository Structure

```
domain-teams/
├── .claude-plugin/plugin.json
├── CHANGELOG.md
├── agents/
│   ├── worker.md                ← sonnet, artifact を生成（verdict は出さない）
│   └── evaluator.md             ← opus, verdict を生成（artifact は変更しない）
├── commands/                    ← 9 個の slash command
└── skills/
    ├── using-domain-teams/      ← Router
    ├── planning-team/
    ├── code-team/
    ├── docs-team/
    ├── qa-team/
    ├── devops-team/
    ├── design-team/
    ├── research-team/
    ├── investing-team/
    ├── copywriting-team/
    └── skill-team/
```

各 team skill ディレクトリは `SKILL.md` + `protocols/` + `checklists/` + `rubrics/` + `standards/` + 任意の `research/`（grounding audit trail）を含む自己完結構成です。

## Agent Behavioral Rules

- **worker** — artifact を生成し、gate verdict は出さない
- **evaluator** — verdict を生成し、artifact は変更しない
- **Knowledge access is open** — skill は必要な protocol / standard / checklist を自由に読み取る；行動上の分離であり、読み取り制限ではない

## Cross-Plugin Delegation

`investing-team` は `investing-toolkit:investment-memo-writer` の委譲先です。Cross-plugin delegation はパスと構造化された seed context を渡し、委譲先の team が自前で standards を読み込み、自前で gates を実行し、verdict を返却します。詳細は repo root の `CLAUDE.md §Cross-Plugin Delegation Contract` を参照してください。

## License

MIT — repository root の [`LICENSE`](../LICENSE) を参照。
