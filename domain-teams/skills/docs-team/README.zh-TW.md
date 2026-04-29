# docs-team

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Diátaxis 錨定的文件 skill，搭配 checkpoint quality gate 與可選的 4× 成本節省 quick mode。

**所屬**: [monkey-skills](https://github.com/kouko/monkey-skills) → `domain-teams`
**slash command**: `/docs`
**grounding**: Diátaxis · Google Style · Microsoft Style · Standard README · Nygard ADR · OpenAPI 3.2.0 · Write the Docs · JTAP · *Software Engineering at Google* 第 10 章

## 目錄

- [背景](#背景)
- [安裝](#安裝)
- [使用方式](#使用方式)
- [架構](#架構)
- [quality gates](#quality-gates)
- [成本（full mode 與 quick mode）](#成本full-mode-與-quick-mode)
- [檔案配置](#檔案配置)
- [貢獻](#貢獻)
- [授權](#授權)

## 背景

文件腐化的速度比程式碼還快。最常見的四種失敗：模式混雜（how-to 卻在講課、tutorial 卻列舉所有 option）、不一致的 reference、未記錄的 architecture decision、以及沒人信任的過期內容。docs-team 用 checkpoint 各別擋下：Diátaxis 單一 quadrant 紀律、OpenAPI 形狀的 reference、強制列出 consequences 的 Nygard ADR、可見地老化的 freshness frontmatter。

skill 的每條規則都錨定到一手來源。所有規則都不是發明出來的 — Diátaxis 出自 Daniele Procida、style 規則來自 Google 與 Microsoft、README spec 來自 RichardLitt、ADR template 來自 Michael Nygard、docs-rot 緩解策略則出自 *Software Engineering at Google* 第 10 章。

## 安裝

docs-team 隨 monkey-skills plugin 一起發佈。使用方式：

```bash
# 在啟用 monkey-skills plugin 的 Claude Code 中：
/docs <你的請求>
```

不需要另外安裝。Claude 會自動 discover plugin 的 `domain-teams` 目錄裡的 SKILL.md。

## 使用方式

用 `/docs` 加上請求，或讓 `using-domain-teams` router 依意圖選擇 docs-team。

```
/docs write a README for this Go library
/docs document the payment service architecture
/docs write an ADR for our token-bucket rate limiter
/docs audit the docs/ directory for staleness
/docs draft a quick how-to for rotating API keys     ← quick mode
```

skill 偵測 artifact 類型、選擇對應的 Diátaxis quadrant 或 composite template，並啟動對應的 gate。

### workflow

| workflow | 輸出 | MUST gate | SHOULD gate |
|----------|------|-----------|-------------|
| Write Tutorial | 學習導向的 walk-through | Mode Clarity | Style |
| Write How-to Guide | 任務導向的食譜 | Mode Clarity | Style |
| Write Reference | API / CLI / config reference | Mode Clarity | Style |
| Write Explanation | 設計理由 / 概念說明 | Mode Clarity | Style |
| Write README | Standard README spec | README Completeness + 逐段 Mode Clarity | Style |
| Write ADR | Architecture Decision Record | ADR Structure | Style |
| Write API Reference | OpenAPI 形狀的 reference | Mode Clarity | Style |
| Write Architecture | overview / component spec / data flow | Architecture Doc Completeness | Style |
| Documentation Audit | Diátaxis + freshness 稽核報告 | — | Freshness |
| Codebase Assessment | health 報告（code mode 或 doc mode）| — | — |
| Quick Write | 同樣的 artifact，僅 SELF check | —（gate 略過）| — |

## 架構

```
docs-team（checkpoint 編排器）
  ├── worker (sonnet)     ← protocols/ + standards/
  └── evaluator (opus)    ← checklists/ + rubrics/ + standards/
```

worker 寫 artifact，evaluator 評分 gate。main agent 統籌、套用 verdict 規則，並對 `PASS_WITH_NOTES` 自動修訂（最多 2 輪）。

quick mode 由 main agent inline 執行 protocol，不 dispatch subagent — 用 gate enforcement 換取 4× 的 token 成本節省。

## quality gates

依 `domain-teams:skill-team` 的 gate-system standard 採 4 階層系統。

| 階層 | 行為 | docs-team 中的範例 |
|------|------|-------------------|
| **SELF** | 每次交付都跑、必執行；main agent 自我稽核 | 全部 workflow |
| **MUST** | 自動 trigger、不可略過 | Mode Clarity、README Completeness、ADR Structure、Architecture Doc Completeness |
| **SHOULD** | 自動 trigger、可附理由略過 | Style、Freshness |
| **MAY** | 使用者請求或 workflow 特定 | Tech Debt 稽核、無 frontmatter 文件的 opt-in Freshness |

verdict: `PASS` / `PASS_WITH_NOTES`（自動修訂）/ `NEEDS_REVISION`（escalate 給使用者）/ `NEEDS_METADATA`（僅 Freshness — 表示 gate 不適用，非失敗）。

## 成本（full mode 與 quick mode）

| mode | 每任務 | 執行內容 | 適用場景 |
|------|------:|---------|---------|
| **Full**（預設）| 約 46K tokens | worker + evaluator × MUST/SHOULD gates + 自動修訂 | 正式文件、ADR、API reference、對外公開的 release README |
| **Quick**（opt-in）| 約 11K tokens | main agent inline + 僅 SELF check | 草稿、個人筆記、低風險的既有文件微調 |

quick mode 對 ADR、API reference、對外公開的 release README、architecture documentation 一律 **拒絕** — 這些 artifact 的價值就在於 gate audit trail。

`/docs verify <artifact>` 可對 quick mode 的輸出事後跑 gate（約 25K），讓你延後驗證決策，不必一開始就付 full mode 的成本。

## 檔案配置

```
docs-team/
├── README.md                        # 人類向概觀（英文，預設）
├── README.ja.md                     # 日文翻譯
├── README.zh-TW.md                  # 繁體中文翻譯（本檔）
├── SKILL.md                         # LLM-discovery SSOT（frontmatter + workflow + gate trigger）
├── standards/                       # 穩定的 SSOT 規則
│   ├── diataxis-taxonomy.md            # 4 quadrant 詞彙（Procida）
│   ├── style-conventions.md            # Google + Microsoft + JTAP
│   ├── docs-as-code.md                 # Write the Docs 運作哲學
│   ├── freshness-metadata.md           # frontmatter 慣例（SWE@Google）
│   ├── api-reference-structure.md      # OpenAPI 3.2.0 欄位
│   ├── pre-writing-checklist.md        # LLM 防禦性閱讀規則
│   └── architecture-doc-structure.md   # L0–L4 階層 + Mermaid 規則
├── protocols/                       # workflow SOP
│   ├── doc-writing-router.md           # mode + quadrant 路由
│   ├── quick-write.md                  # 成本節省的 inline workflow
│   ├── write-tutorial.md
│   ├── write-how-to.md
│   ├── write-reference.md
│   ├── write-explanation.md
│   ├── write-readme.md                 # Standard README composite
│   ├── write-adr.md                    # Nygard + MADR
│   ├── write-api-reference.md          # OpenAPI 特化
│   ├── write-architecture.md           # system / component / data flow
│   └── codebase-assessment.md          # code + 文件健康度稽核
├── checklists/                      # 二元 gate
│   ├── readme-completeness.md          # Standard README spec
│   └── tech-debt-checklist.md          # 程式碼健康度（MAY）
├── rubrics/                         # 定性 gate
│   ├── diataxis-mode-clarity.md
│   ├── adr-structure.md
│   ├── architecture-doc-completeness.md
│   ├── style.md
│   └── freshness.md
└── research/
    └── grounding-v4.3.0.md             # 一手來源稽核軌跡
```

## 貢獻

docs-team 是 monkey-skills plugin 的一部分。issue 與 PR 請提交到上層 repo：<https://github.com/kouko/monkey-skills>。

提案變更時：

- 提交前對你新增的 artifact 跑過既有 gate
- 為新規則引用一手來源 — 不接受自創 taxonomy
- 遵守 `domain-teams:skill-team` 的 `file-conventions.md` 命名規則（kebab-case、不可巢狀子目錄、刪除優於 deprecation）
- 把 `SKILL.md` 控制在 6,000 token hard cap 內；如果壓力持續，把 standards 拆分

## 授權

MIT © 2026 kouko。詳見 repo 根目錄的 [LICENSE](../../../LICENSE)。
