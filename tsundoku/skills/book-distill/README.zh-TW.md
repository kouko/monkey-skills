# book-distill

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 將一本書（已由 [`book-extract`](../book-extract) 轉為依章節切分的 Markdown）
> 透過 **RIA-TV++ pipeline** 蒸餾成一組連貫、可執行的 agent skill。

屬於 [tsundoku](../..) plugin。Claude 真正載入的 skill spec 是
[`SKILL.md`](SKILL.md)；本 README 給人類閱讀。

> **狀態（v0.9.0）**：pipeline 結構 + 經研究背書的三語 glossary
> （EN / 日本語 / 繁體中文），採用 canonical 的官方出版譯名。
> 出處在 `ATTRIBUTION.md`。

## 它做什麼（與不做什麼）

- ✅ **蒸餾**：方法論 / 決策 framework / checklist / 原則 / 概念體系 →
  原子化、可重用的 agent skill
- ❌ **跳過**：書籍摘要 / 書評 / 把作者當人格扮演

## RIA-TV++ pipeline

```
Stage 0:    Adler analytical read           → BOOK_OVERVIEW.md
Stage 1:    5 個 parallel sub-agent extractor → candidates/
            （framework / principle / case / counter-example / glossary）
Stage 1.5:  Triple verification filter       → verified.md（約 30-50% 通過）
            V1 cross-domain / V2 predictive / V3 exclusivity
Stage 2:    RIA++ skill render               → <skill-slug>/SKILL.md
            R / I / A1 / A2 / E / B 六個欄位
Stage 3:    Zettelkasten linking              → INDEX.md + cross-refs
Stage 4:    Adversarial pressure test         → test-prompts.json
```

蒸餾本身是 **Claude-driven** — skill spec 指示 Claude 在每個 stage spawn
sub-agent。沒有單一龐大的 Python orchestrator；唯一的 shell script 是
`book_distill_init.sh`，作用是 bootstrap 工作目錄。

## 前置條件

來源書必須先由 [`book-extract`](../book-extract) 處理過：

```bash
ls ~/.tsundoku/cache/markdown/<book-slug>-<id8>/
# 預期：index.md / metadata.json / NN-chapter.md 檔案
```

如果沒有這些，`book_distill_init.sh` 會中止並把你 route 到 `book-extract`。

## Quick start

```bash
# 1. 從 extracted markdown bootstrap 一個工作目錄
bash scripts/book_distill_init.sh 一九八四-b9152ffe

# 輸出：~/.tsundoku/cache/distilled/一九八四-b9152ffe/
#   ├── BOOK_OVERVIEW.md.draft
#   ├── metadata.snapshot.json
#   ├── chapters.list
#   ├── candidates/
#   ├── rejected/
#   └── .book-distill-state

# 2. 接著讓 Claude 從 Stage 0 起依本 skill 的 SKILL.md 走完。
#    Claude 會讀章節、填 BOOK_OVERVIEW.md、spawn 5 個 parallel
#    extractor、跑 triple verification 等等。
```

## 何時觸發

使用者說類似：
- "Distill *Poor Charlie's Almanack* into skills"
- 「把《思考的快與慢》蒸餾成 skill」
- 「この本の方法論を skill にして」

## 輸出結構

```
~/.tsundoku/cache/distilled/<book-slug>/
├── BOOK_OVERVIEW.md            # Stage 0 — thesis / 骨架 / glossary / critique
├── INDEX.md                    # Stage 3 — skill overview + 引用圖
├── candidates/                 # Stage 1 原始候選池（audit trail）
│   ├── frameworks.md
│   ├── principles.md
│   ├── cases.md
│   ├── counter-examples.md
│   └── glossary.md
├── rejected/                   # Stage 1.5 被剔除者 + 理由（audit trail）
├── verified.md                 # Stage 1.5 倖存者
└── <skill-slug-N>/             # 每個出貨 skill 一個目錄
    ├── SKILL.md                # RIA++ render：R / I / A1 / A2 / E / B
    └── test-prompts.json       # Stage 4 測試案例（≥3 trigger + ≥2 lure + ≥1 edge）
```

## Per-skill schema（RIA++ 六個欄位）

| 欄位 | 內容 |
|---|---|
| **R** Reading | 來源逐字引用 ≤150 字元 + 章節 citation |
| **I** Interpretation | 用自己的話寫出方法論骨架，5-15 行 |
| **A1** Past Application | 作者書中記錄過的此方法論案例 |
| **A2** Future Trigger ★ | 使用者何時會需要它；會成為 frontmatter `description` |
| **E** Execution | 編號的 runtime 步驟 + 完成判準 |
| **B** Boundary | 何時**不**該用，依據 counter-example + critique |

## 輸出語言規則

本 skill 的語言會自適應：

- **R 引用**：逐字採用來源語言；絕不翻譯
- **I / A / E / B 本文**：對齊來源書的語言
- **YAML 欄位名稱 + slug**：英文（機器識別子）
- **frontmatter `description`**：來源語言（讓使用者 query 觸發 trigger
  匹配時更自然）
- **Audit metadata**：英文

## 此資料夾的檔案

| Path | 角色 |
|---|---|
| [`SKILL.md`](SKILL.md) | Claude 載入的頂層 orchestrator（約 270 行） |
| [`ATTRIBUTION.md`](ATTRIBUTION.md) | upstream credits（cangjie-skill、nuwa-skill、Adler、RIA、Zettelkasten） + license |
| [`methodology/`](methodology) | 7 個檔案：設計理念 + 各 stage 細節 |
| [`extractors/`](extractors) | 5 個 sub-agent prompt（framework / principle / case / counter-example / glossary） |
| [`templates/`](templates) | BOOK_OVERVIEW / SKILL / INDEX / test-prompts |
| [`scripts/book_distill_init.sh`](scripts/book_distill_init.sh) | 從 `book-extract` 輸出 bootstrap 工作目錄 |

## 由來

改編自 [`kangarooking/cangjie-skill`](https://github.com/kangarooking/cangjie-skill)
（蒼頡-skill，MIT）。完整 credits 與 upstream → tsundoku 變更清單見
[`ATTRIBUTION.md`](ATTRIBUTION.md)。

整體架構承襲 cangjie-skill；tsundoku 的貢獻有：
1. 英文 canonical 指令 + 自適應輸出語言規則
2. **三語 glossary**（EN / 日本語 / 繁體中文）採用 canonical 的官方出版譯名
3. tsundoku 專屬入口 hook（`book_distill_init.sh`），讓 upstream 最大的
   摩擦點（「使用者必須提供書 + metadata」）消失

## 為什麼是 "book-*" 不是 "kobo-*"？

本 skill 是 **format-agnostic**：不論來源為何，都能消化任何依章節切分的
Markdown。未來的 `paper-distill`（學術論文）或 `transcript-distill`
（podcast 逐字稿）會加入 `book-*` / 處理層。只有 `kobo-auth` 與
`kobo-library` 與 Kobo 平台綁定。

## 已知限制

- **沒有覆蓋率證明** — 蒸餾可能漏掉書中最重要的 framework。Roadmap 項目：
  TOC reconstruction test（給定蒸餾出的 skill，新 agent 能否重建章節大綱？）。

- **沒有 CJK fidelity benchmark** — 對測試 library 中 226 本 zh-TW / 7 本 ja
  書的量化驗證是 roadmap 項目。

- **沒有自動 regression** — `test-prompts.json` 與 darwin-skill 格式相容，
  但目前沒有 orchestrator 拉它跑；留給未來的 evolution skill 或手動執行。

## 另見

- [`book-extract`](../book-extract) — 產出此 skill 消化的依章節切分 Markdown
- [`tsundoku` README](../..) — 完整 pipeline 概覽
- [Cangjie 設計理念](https://github.com/kangarooking/cangjie-skill)
- [Nuwa Skill](https://github.com/alchaincyf/nuwa-skill) — 兄弟 persona
  蒸餾（範圍不同，但採同一個 Triple Verification primitive）
