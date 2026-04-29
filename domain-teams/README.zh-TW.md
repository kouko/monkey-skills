# domain-teams

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**Version**: 5.4.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

具備 primary-source grounding 與 checkpoint-based quality gates 的 domain team skills。9 個 team 共用一組 `worker`（sonnet）+ `evaluator`（opus）agent。

## Architecture

```
Team Skill (checkpoint orchestrator)
  ├── worker (sonnet)    ← protocols/ + standards/
  └── evaluator (opus)   ← checklists/ + rubrics/ + standards/

Four-level quality gates:
  SELF    → Agent 對每次交付執行自檢
  MUST    → 自動觸發、不可略過（例：security、a11y、citation）
  SHOULD  → 自動觸發、可附理由略過（例：quality、UX）
  MAY     → 僅由使用者要求時觸發（例：QA、tech debt、visual）

Domain knowledge（與各 team skill 目錄共置，open access）：
  protocols/   → 步驟式 SOP（執行指引）
  checklists/  → 二元 pass/fail 標準（gate 評估）
  rubrics/     → 質性 flag 標準（gate 評估）
  standards/   → 基礎規則（共用 SSOT）
  research/    → Grounding audit trail（選用）
```

## Router

| Type | Name | Role |
|------|------|------|
| Skill | `using-domain-teams` | 進入點 — 將請求路由到對應 team |

## Teams

| Team | Slash cmd | Role | Notable grounding |
|------|-----------|------|-------------------|
| `planning-team` | `/planning` | 跨領域專案 planning（企画）；產出 PRODUCT-SPEC.md | Business thesis + JTBD |
| `code-team` | `/code` | Code 開發；實作功能、修 bug、撰寫 TECH-SPEC.md | Clean Code (Martin 2008) + Pragmatic Programmer + SOLID + Kent Beck；外部依賴：`feature-dev:code-architect` |
| `docs-team` | `/docs` | Documentation + codebase 評估；README、API docs、tech debt audit | Diátaxis + Google Developer Style + JTAP |
| `qa-team` | `/qa` | Test strategy 與規劃；E2E、integration、performance | ISTQB + ISO/IEC/IEEE 29119 + VSTeP / HAYST / ゆもつよ |
| `devops-team` | `/devops` | 安全交付 code；CI/CD、Dockerfiles、IaC、deployment、monitoring | Google SRE + DORA + 12-Factor + Continuous Delivery |
| `design-team` | `/design` | 具備 accessibility + quality review 的 design；UI、wireframes、UX strategy | Norman / Nielsen / WCAG 2.2 + 原研哉 / 深澤 / 黒須 / 上野 |
| `research-team` | `/research` | Primary-source-grounded research；market / competitive / literature review | Systematic-review rigor + citation verification |
| `investing-team` | — | 個股 Buy/Hold/Sell verdicts、equity research memo、portfolio rebalancing、macro regime 診斷 | IC regime + Dalio + CAPE + ISQ (Investment Signal Quality) |
| `copywriting-team` | `/copywriting` | 具說服力的 marketing copy — landing page、キャッチコピー、email、voice guide、audit | 神田 PASONA + 谷山 + 今泉 + 川喜田 + Cialdini + Schwartz + McQuarrie & Mick + Lakoff + Thornton |
| `skill-team` | `/skill` | Meta-skill：以慣例紀律建立或修改 domain-team skills | Anthropic Agent Skills spec + Conventional Commits + Semver |

共 10 個 skill（9 個 team + router）。9 個 slash command（`investing-team` 透過 `investing-toolkit` plugin router 存取）。

## Repository Structure

```
domain-teams/
├── .claude-plugin/plugin.json
├── CHANGELOG.md
├── agents/
│   ├── worker.md                ← sonnet, 產出 artifact（不產出 verdict）
│   └── evaluator.md             ← opus, 產出 verdict（不修改 artifact）
├── commands/                    ← 9 個 slash command
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

每個 team skill 目錄皆為自包含結構，含 `SKILL.md` + `protocols/` + `checklists/` + `rubrics/` + `standards/` + 選用的 `research/`（grounding audit trail）。

## Agent Behavioral Rules

- **worker** — 產出 artifact，不產出 gate verdict
- **evaluator** — 產出 verdict，不修改 artifact
- **Knowledge access is open** — skill 可讀取所需的任何 protocol / standard / checklist；為行為層分工，非閱讀層管制

## Cross-Plugin Delegation

`investing-team` 為 `investing-toolkit:investment-memo-writer` 的委派目標。Cross-plugin delegation 傳遞路徑與結構化 seed context；被委派的 team 自行載入 standards、執行 gates，並回傳 verdict。詳見 repo root 的 `CLAUDE.md §Cross-Plugin Delegation Contract`。

## License

MIT — 見 repository root 的 [`LICENSE`](../LICENSE)。
