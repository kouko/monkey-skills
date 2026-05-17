# domain-teams

> 以 checkpoint 為基礎的 quality gate 領域 team skill 集 — planning（企画）、code、design、research、copywriting、investing 等。

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

**Version**：5.5.1
**Part of**：[monkey-skills](https://github.com/kouko/monkey-skills)

## Background

`domain-teams` 是一個 Claude Code plugin，將 10 個領域特化 skill 包在
統一的 agent + gate architecture 之下。每個 team 自行擁有 protocol、
standards、checklist 與 rubric — 全部 anchor 在 primary source（教科書、
RFC、學術論文、官方 docs）上，而非 LLM 自創的 heuristics。

兩個共用 agent 支撐所有 team：

- **`worker`** — 產出 artifact（code、docs、spec、copy、research
  報告）。讀取 dispatch 端 skill 傳入的 protocol 與 standards 檔案，
  執行 SOP 後輸出交付物。不自評。若任務需要 hallucination 才能完成，
  可 escalate 為 `BLOCKED`。
- **`evaluator`** — 以 checklist（每項 PASS / FAIL_FATAL /
  FAIL_FIXABLE）或 rubric（🔴 / 🟡 / 🟢 旗標）judge artifact。回傳
  `PASS`、`PASS_WITH_NOTES`（auto-revise loop）或 `NEEDS_REVISION`
  （escalate 給使用者）。不修改 artifact。

這個分離 — *worker 負責 produce、evaluator 負責 judge* — 是 plugin
最關鍵的 behavioral rule。

## Architecture：4-tier quality gate

每個 team 在四個 tier 上定義自己的 gate：

```
SELF check  （每次交付，worker 自我檢驗）
   │
   ▼
MUST gates  （auto-trigger，不可 skip）
   │   security / architecture / completeness
   ▼
SHOULD gates  （auto-trigger，需明示理由方可 skip）
   │   quality / spec consistency / mode clarity
   ▼
MAY gates  （opt-in，相關時才執行）
       各 team 任意 discipline
```

Gate verdict 流程：

```
worker artifact ──► evaluator ──► verdict
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
              PASS          PASS_WITH_NOTES         NEEDS_REVISION
           gate 通過         auto-revise loop       escalate 給使用者
                            （最多 3 round，每 round
                              都用 fresh evaluator）
```

`SELF` 由 worker 自行負責；`MUST` / `SHOULD` / `MAY` 一律 launch
`evaluator` agent，並明確指定 checklist 或 rubric 檔案。每個 gate
檔案的路徑都在該 team 的 SKILL.md `Quality Gates` 區塊宣告，verdict
僅由 evaluator emit — worker 不得自行合成。

## Router skill

`using-domain-teams` 是入口 router。當你開始任何領域任務但不確定該
找哪個 team 時使用。內容包含：

- *Available Teams* 表（各 team 的 mission + delivers）
- *Intent Routing* 表（具體 user intent → team）
- *Ambiguous Cases* 表（多 team 串接序列，例：
  `planning-team` → `code-team` → `qa-team` → `devops-team`）

如果已經知道該找哪個 team，可略過 router 直接 invoke 對應 team skill。

## Teams

每個 team skill 都能用 skill 名稱直接以自動產生的 slash command 呼叫（例如 `/code-team`、`/qa-team`）。

| Team | Slash command | 角色 | 主要 grounding |
|------|---------------|------|---------------|
| `code-team` | `/code-team` | 以 primary-source-grounded 的 quality gate develop code | Clean Code（Martin 2008）、Pragmatic Programmer（Hunt & Thomas 2019）、SOLID、TDD（Beck 2002）、Refactoring 第 2 版（Fowler 2018）、Working Effectively with Legacy Code（Feathers 2004）、OWASP ASVS v5.0.0、徳丸本 第 6 章 |
| `docs-team` | `/docs-team` | 以 Diátaxis discipline 撰寫 documentation 並 assess codebase | Diátaxis taxonomy、Standard README（RichardLitt）、Google + Microsoft style、Trong-Tra `documentation-specialist`（readme + architecture L0–L4） |
| `qa-team` | `/qa-team` | 規劃並驗證 unit 以上層級的 test | 品質は工程で作り込む — built-in 品質；E2E / integration / performance test 策略 |
| `devops-team` | `/devops-team` | 以 CI/CD、container、IaC 安全 ship code | Google SRE、DORA、12-Factor App primary source |
| `research-team` | `/research-team` | 以 citation 驗證執行 primary-source-grounded 的 research | systematic-review rigor、confidence calibration、operator 視角 market analysis |
| `design-team` | `/design-team` | 含 accessibility 與 quality review 的 design | 行為設計（behavioral design）、感性工学、無意識の設計；UI / UX / a11y |
| `planning-team` | `/planning-team` | 跨領域 project planning（企画） | JTBD、Lean Startup、OKR、4 Big Risks、Business Model Canvas / Lean Canvas |
| `copywriting-team` | `/copywriting-team` | 撰寫具說服力的 marketing copy | 日本廣告傳統（神田昌典 PASONA / 谷山 / 糸井）+ Anglo persuasion psychology（Cialdini、Schwartz Awareness Levels、Ogilvy） |
| `investing-team` | *（透過 delegation 呼叫）* | 以 primary-source framework 支撐可辯護的投資決策 | Investment Clock（regime）、Buy/Hold/Sell verdict、台股（三大法人 / 月營收 / 董監持股 / 融資融券） |
| `skill-team` | `/skill-team` | 以 convention discipline 建構或修改 domain-team skill | 4-tier gate 設計、primary-source grounding、3-commit split、dual-file（README + SKILL.md）、companion file pattern |
| `using-domain-teams` | `/using-domain-teams`（router） | 將 intent route 至對應 team | — |

`investing-team` 沒有 slash command 是因為它通常透過 Cross-Plugin
Delegation Contract 從 `investing-toolkit` plugin 呼叫（見下方）。

## Repository 結構

```
domain-teams/
├── .claude-plugin/
│   └── plugin.json              # plugin metadata（SSOT）
├── agents/
│   ├── worker.md                # 通用任務 executor（sonnet）
│   └── evaluator.md             # 通用 quality evaluator（opus）
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

每個 `skills/<team>/` 目錄都是自包含的：

```
<team>/
├── SKILL.md          # frontmatter + 本文，~6,000 token 預算
├── protocols/        # worker 遵循的 SOP
├── standards/        # artifact 必須符合的 baseline 規則
├── checklists/       # binary PASS/FAIL gate 檔
├── rubrics/          # qualitative 🔴/🟡/🟢 gate 檔
├── research/         # grounding 筆記 + citation 驗證（部分 team）
└── README.md         # 選用的 skill 內部 overview（部分 team）
```

`SKILL.md` 內的 bundled file 用相對路徑引用（例：
`checklists/security-checklist.md`），不使用絕對路徑。

## Agent behavioral rule

`worker` / `evaluator` 的分離不只是 workflow convention，更是強制的
behavioral rule：

- **`worker`** 產出 artifact，**不**產出 gate verdict。可讀取任何
  domain 檔案（rubric、checklist、standards）做 self-check，但不得
  emit `PASS` / `PASS_WITH_NOTES` / `NEEDS_REVISION` 的 verdict。
- **`evaluator`** 產出 verdict，**不**修改 artifact。回傳 worker 可
  action 的 feedback，但自己不編輯檔案。
- 知識存取開放 — 限制在 *behavior*，不在 *agent 可讀哪些檔案*。
- 每次 gate retry 都會 launch 一個 *fresh* evaluator，沒有累積
  context — 只有 original requirement + 目前 artifact + feedback。
- worker honor dispatcher launch prompt 中的 `output_language`；
  technical jargon 保留原文（不強制翻譯）。

兩個 agent 都支援 `BLOCKED` 緊急出口：當任務需要 hallucination 才能
完成時，agent 會 emit 結構化 `BLOCKED` status，而不是輸出有缺陷的
artifact。

## Cross-Plugin Delegation Contract

domain-teams 是其他 plugin delegate 過來的 analysis + gate authority。
首例為
`investing-toolkit:investment-memo-writer` → `domain-teams:investing-team`。

Contract：

1. **Delegation = 傳路徑 + 結構化 seed context。** 不傳檔案內容；不
   inline analysis 結果。
2. **Delegation target 收到 full authority。** 收件 skill 自行載入
   standards、自行執行 gate、自行 emit verdict。delegator 不干涉。
3. **Data layer 留在 toolkit、analysis layer 留在 domain-teams。**
   toolkit plugin 負責 data fetch + pipeline orchestration；
   domain-teams 負責 analysis、primary-source anchoring 與 gate
   enforcement。
4. **Gate verdict 回流。** verdict（`PASS` / `PASS_WITH_NOTES` /
   `NEEDS_REVISION`）會傳回 orchestrating skill — 不被吞掉。
5. **跨 plugin 的路徑解析使用 plugin 名 + skill path**（例：
   `domain-teams:investing-team`），不用 filesystem 絕對路徑。

禁止：在其他 plugin 內重新實作 domain-team 的 gate logic（gate
bypass）、把 domain-teams standards 複製到其他 plugin（drift）、讓
data-fetcher agent 做 analysis。

## Skill 內部 README convention

v5.5.1 起，`skill-team/standards/file-conventions.md` 正式定義：
**skill 內部 README（`skills/<name>/README.md` 與 i18n sibling）不需要
docs-team workflow**。直接以較輕的 discipline 撰寫：

- 頂部語言切換器
- 保留英文名詞（依 `docs/i18n/glossary-*.md`）
- 連結到 sibling SKILL.md
- 不得與 SKILL.md 矛盾（SKILL.md 是 SSOT，README 是 overview）
- 若 skill 為衍生品，需 upstream attribution

仍需 `docs-team` workflow 的情況：plugin-level README、repo-level
README、公開 release README、ADR、API reference、runbook、architecture
L0–L4 文件。

## License

MIT — 詳見 repository root 的 [LICENSE](../LICENSE)。
