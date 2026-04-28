# skill-team

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 用於建構與 refactor domain-team skill 的 meta-skill。錨定一手來源、4 階層 quality gate、3-commit Conventional Commits 紀律。

**所屬**: [monkey-skills](https://github.com/kouko/monkey-skills) → `domain-teams`
**呼叫方式**: 透過 `using-domain-teams` 路由，或用 `domain-teams:skill-team` 直接呼叫
**grounding**: Anthropic Agent Skills spec · Conventional Commits 1.0.0 · Semantic Versioning 2.0.0 · qa-team v4.2.0 / docs-team v4.3.0 / devops-team v4.4.0 三次 refactor 先例

## 目錄

- [背景](#背景)
- [安裝](#安裝)
- [使用方式](#使用方式)
- [架構](#架構)
- [quality gates](#quality-gates)
- [檔案配置](#檔案配置)
- [Visibility convention](#visibility-convention)
- [貢獻](#貢獻)
- [授權](#授權)

## 背景

skill-team 是 meta-skill。唯一的職責是建構與 refactor **domain-team skill** — 遵循 `standards/protocols/checklists/rubrics` 目錄配置、啟動 worker / evaluator agent、強制 4 階層 quality gate 的 skill。

skill-team codify 的慣例不是發明來的，是從 3 次 grounded-team refactor 蒸餾出來的：qa-team v4.2.0（ISTQB / VSTeP）、docs-team v4.3.0（Diátaxis / Google Style / JTAP）、devops-team v4.4.0（Google SRE / DORA / 12-Factor）。三次 refactor 累積的 tribal knowledge 收斂在本 skill 的 8 份 standards 檔案裡。

**範圍刻意收窄。** 一般 Claude skill 撰寫（非 domain-team 類）請改用 `superpowers:writing-skills` 或 Anthropic 的 `skill-creator`。Obsidian skill、philosophers-toolkit skill、plugin 層級的打包、utility script 都不在本 skill 範疇內。

**meta-circularity 註記**: skill-team 在它自己存在之前就被 bootstrap 了。第一次建立是手動完成的 — 因為當時還沒有 tool 能套用它要 codify 的慣例。後續所有 skill 建立與 refactor 都走 skill-team。

## 安裝

skill-team 隨 monkey-skills plugin 一起發佈，不需要另外安裝。plugin 啟用後 Claude 會自動 discover。

## 使用方式

skill-team 沒有 slash command。它是間接呼叫的：

- 透過 `using-domain-teams` 自動路由（意圖匹配時，例如「幫我建一個新的 team skill」、「重構 qa-team 的 grounding」）
- 透過 Skill tool 直接呼叫：`domain-teams:skill-team`

### workflow

| workflow | 適用場景 |
|----------|---------|
| **New Skill Creation** | 為尚未涵蓋的領域建立全新 domain-team skill（例如新增 `security-team`、`data-team`）|
| **Skill Redesign**（grounding refactor）⭐ 主要用途 | 既有 team 缺一手來源錨定 / workflow phase 壞掉 / 需要結構性改善 |

兩個 workflow 都產出 PR-ready 的 3-commit branch：

```
Commit 1: standards CREATE/MODIFY              （SSOT 規則）
Commit 2: protocols + gates CREATE/MODIFY      （workflow 食譜 + verdict 標準）
Commit 3: SKILL.md + router + version bump     （接線 + 出貨）
```

這個拆法不是裝飾。每個 commit 的 diff 對應 skill 的一層 — reviewer 可以獨立稽核每一層；遇到問題時 bisect 也才會有效。

## 架構

```
skill-team（checkpoint 編排器）
  ├── worker (sonnet)     ← protocols/ + standards/
  └── evaluator (opus)    ← checklists/ + rubrics/ + standards/
```

worker 執行 build / refactor protocol。evaluator 評分 gate。main agent 統籌、套用 verdict 規則。

如果建構需要一手來源 grounding research，skill-team 會委派給 `research-team`，自己不執行 research。research artifact 落在目標 skill 內的 `research/grounding-v{X.Y.Z}.md` 作為稽核軌跡（依 `file-conventions.md` §research/ 規則）。

## quality gates

依 `standards/gate-system.md` 採 4 階層系統。

| 階層 | 行為 | skill-team 中的範例 |
|------|------|--------------------|
| **SELF** | 每次交付都跑、必執行；main agent 自我稽核 | 全部 workflow |
| **MUST** | 自動 trigger、不可略過 | Skill Completeness、Commit Split Validity |
| **SHOULD** | 自動 trigger、可附理由略過 | Primary Source Grounding、Skill Coherence |
| **MAY** | 使用者請求或 workflow 特定 | 目前無。未來候選：gate 檔案 linting、workflow 相依圖分析 |

gate verdict: `PASS` / `PASS_WITH_NOTES`（自動修訂，最多 2 輪）/ `NEEDS_REVISION`（escalate 給使用者）。

Commit Split Validity gate 對 `main` 跑 `git log --stat`；評估對象是 branch 整體，不是單一檔案。

## 檔案配置

```
skill-team/
├── README.md                              # 人類向概觀（英文、預設）
├── README.ja.md                           # 日文翻譯
├── README.zh-TW.md                        # 繁體中文翻譯（本檔）
├── SKILL.md                               # LLM-discovery SSOT
├── standards/                             # 8 份 SSOT 規則 — 收斂後的 tribal knowledge
│   ├── skill-md-structure.md                 # SKILL.md 結構、必要段落、token 預算
│   ├── file-conventions.md                   # 4 子目錄配置、top-level 檔案、path 紀律
│   ├── gate-system.md                        # SELF / MUST / SHOULD / MAY 階層、verdict 語義
│   ├── grounding-principle.md                # 一手來源規則、JP 整合策略
│   ├── agent-interface.md                    # Resource Paths 輸入契約、behavioral 界線
│   ├── commit-convention.md                  # 3-commit 拆分、Conventional Commits、semver
│   ├── mermaid-usage-guidelines.md           # 何時用 Mermaid vs 散文、syntax 規約
│   └── user-terminal-handoff.md              # TTY 綁定指令必須 handoff 到 user terminal（auth、sudo、TUI）
├── protocols/                             # workflow SOP
│   ├── skill-brainstorming.md                # 模糊請求的範圍分解
│   ├── grounding-research.md                 # 一手來源 research workflow（委派給 research-team）
│   ├── new-skill-creation.md                 # 新 team 的 10-phase 建構
│   └── skill-redesign.md                     # 既有 team 的 6-phase refactor
├── checklists/                            # 二元 gate
│   ├── skill-completeness-checklist.md       # MUST — SKILL.md 結構合規
│   └── commit-split-checklist.md             # MUST — branch commit 歷史合規
└── rubrics/                               # 定性 gate
    ├── primary-source-grounding.md           # SHOULD — 新 standards 的引用品質
    └── skill-coherence.md                    # SHOULD — 完成 skill 的內部一致性
```

skill-team 沒有 `research/` 子目錄。它的規約直接 trace 到 Anthropic Agent Skills spec 與 qa/docs/devops refactor 先例 — 兩者都已經在 standards 檔案內直接引用。skill-team 沒有需要 research 的外部領域，所以不需要 in-repo grounding note。

## Visibility convention

skill-team v5.2.0+ 定義了 `TaskUpdate` 發送慣例，所有 workflow 型 domain-team skill（research-team、code-team、docs-team、devops-team、qa-team、planning-team、investing-team、copywriting-team、design-team）都必須遵守：

- **phase transition**：每個主要 phase 的起點與終點要 emit
- **milestone**：每個 section / deliverable / sub-step 完成時 emit
- **heartbeat**：靜默期不可超過 60 秒，即使在深度推理中也不行

這個慣例提供 **機率性保證** — 遵守程度取決於 agent 行為。如果是非常長時間（> 5 min）的 dispatch 需要嚴格結構保證，把任務拆成更短的子 dispatch（phase-split 架構）。

完整文字與 controller narration 慣例請看 SKILL.md §Visibility Convention。

## 貢獻

skill-team 是 monkey-skills plugin 的一部分。issue 與 PR 提交到上層 repo：<https://github.com/kouko/monkey-skills>。

提案變更時：

- 把 skill-team 套用到 skill-team 自己（dogfood）— 對 `standards/` 的任何修改都走 `skill-redesign.md` 的 Phase 4-6（3-commit 拆分）
- 為新慣例引用一手來源 — 詳見 `standards/grounding-principle.md`。tribal-knowledge 類主張可用 qa/docs/devops 先例當一手來源；其他主張需要引用外部標準（Anthropic、Conventional Commits、semver 等）
- 提交前對 branch 跑 `checklists/skill-completeness-checklist.md` 與 `checklists/commit-split-checklist.md`
- 把 `SKILL.md` 控制在 `standards/skill-md-structure.md` 定義的 6,000 token hard cap 內

## 授權

MIT © 2026 kouko。詳見 repo 根目錄的 [LICENSE](../../../LICENSE)。
