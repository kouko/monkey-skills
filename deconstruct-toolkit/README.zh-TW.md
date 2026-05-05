# deconstruct-toolkit

> 將外部作品（文案、文件包、UI、論證、產品、組織）進行逆向解構，揭露設計決策、借用框架、修辭機制、與刻意省略。

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

**Version**: 0.2.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT
**文化變體範疇**: EN / JA / ZH（見 [ADR-0004](docs/adr/0004-cultural-lens-variants.md)）

## 背景

如果說 `sourceatlas` 對程式碼做逆向、`philosophers-toolkit` 釐清自己的思考，那 **`deconstruct-toolkit` 是對外部、非程式碼作品做逆向解構** — 行銷文案、文件包、UI 流程、長文論證、產品策略、組織形態。目的不是摘要，是 **design archaeology（設計考古學）** — 挖出創作者**決定了什麼**、**借用了哪些框架**、**刻意省略了什麼**。

工具組整合 3 個學術傳統：

- **歐陸哲學 + 批評** — Derrida（解構）、Barthes（5 codes / S/Z）、Goffman + Lakoff（框架分析）。揭露二元對立、隱性符碼、隱藏框架的方法。
- **英美修辭學 + UX** — Burke（戲劇五元）、Toulmin（論證模型）、Bhatia/Swales（體裁 move 分析）、Nielsen-Norman（UX 啟發法）。浮現主張、warrant、設計 affordance 的方法。
- **行為說服科學** — Cialdini（影響力 7 原則）、Brignull（12 黑暗模式 / 欺騙性設計）。檢測說服機制並進行倫理位置判斷的方法。

對華語區讀者，本工具組亦承襲 BCG「**價值鏈解構**」（Evans & Wurster《Blown to Bits》2000，日譯「バリュー・チェーンの脱構築」）與山口周《武器になる哲学》(2018) 的脈絡 — 在日本，「脱構築」已是商業策略用語，不只是哲學借用詞。本 plugin 將這條實務脈絡落地為 agent skill。

### 文化變體範疇（v0.2.0+）

4 個文化敏感度高的 lens（rhetoric / persuasion / genre / frame）皆配置 **EN / JA / ZH** 三語變體。此為恒久範疇決定，依據 [ADR-0004](docs/adr/0004-cultural-lens-variants.md)。

| 變體 | 一手來源 |
|---|---|
| `-anglo` | Burke / Toulmin / Goffman / Lakoff / Swales/Bhatia / Cialdini / Brignull |
| `-ja` | Hinds / 起承転結 / 土居健郎 / 山本七平 / 木下是雄 / Markus & Kitayama |
| `-zh` | 劉勰《文心雕龍》六觀 / Hu Hsien-chin / 黃光國 / 行政院公文程式條例 / Peng & Nisbett |

韓文 / 越南文 / 泰文等其他語言作品**不在 plugin grounded scope 內**：以明示 caveat 的方式套用 `-anglo` fallback，不假裝有覆蓋。詳見 `protocols/lens-variant-selection.md`。

## 邊界

本 plugin **僅處理非程式碼作品**。其他情境用其他工具：

| 用途 | 應使用 |
|---|---|
| 程式碼逆向工程 | [`sourceatlas`](https://github.com/kouko/monkey-skills/tree/main/sourceatlas)（impact / flow / overview / pattern / deps）|
| 自我思考 / 問題釐清 | [`philosophers-toolkit`](https://github.com/kouko/monkey-skills/tree/main/philosophers-toolkit) — 處理「你 vs 你的問題」 |
| Dev 產出物 critique（提案 / commit / skill）| [`dev-workflow`](https://github.com/kouko/monkey-skills/tree/main/dev-workflow)（proposal-critique / complexity-critique / skill-judge）|
| 正向**生產**文案 / 文件 / 設計 | [`copywriting-toolkit`](https://github.com/kouko/monkey-skills/tree/main/copywriting-toolkit), [`docs-team`](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/docs-team), [`design-team`](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/design-team) |
| 投資 / 個股逆向 | [`investing-toolkit`](https://github.com/kouko/monkey-skills/tree/main/investing-toolkit) |

「deconstruct」「teardown」「reverse engineering」三者**不可混用**：

| 詞 | 領域 | 語意核心 |
|---|---|---|
| **Reverse engineering**（逆向工程）| 工程 / 硬體 / 程式 | 拆解以**複製** |
| **Teardown** | 產品 / 消費者 app / 硬體 | 拆解以**理解策略** |
| **Deconstruct**（解構）| 哲學 / 設計批評 / BCG 戰略 | 揭露**隱性結構與對立** |

本 plugin 屬第三類。

## 安裝

本 plugin 在 `monkey-skills` marketplace：

```bash
# 在 Claude Code 內
/plugin marketplace add kouko/monkey-skills
/plugin install deconstruct-toolkit
```

## 使用

知道要哪個 skill 時直接叫：

```
/deconstruct-toolkit:artifact-deconstruct
/deconstruct-toolkit:argument-deconstruct
/deconstruct-toolkit:assumption-surface
```

不確定就走 router：

```
/deconstruct-toolkit:using-deconstruct-toolkit
```

Router 只問一個問題 — 「什麼類型的作品，想揭露什麼」 — 然後派你到正確的 skill 並預選好 lens。

## Skills（v0.2.0）

### 旗艦

#### `artifact-deconstruct`

| 欄位 | 內容 |
|-------|-------|
| 對象 | 任何作品（文案 / 文件包 / UI / playbook / SOP / 廣告 / 文學）|
| 方法 | 6-lens 庫 × 6 維分析 × 倫理位置判斷 |
| Lens | semiotic (Barthes) · rhetoric (Burke + Toulmin) · frame (Goffman + Lakoff) · genre (Swales/Bhatia) · ux (Nielsen-Norman) · persuasion (Cialdini + Brignull) |
| 輸出 | 6 段解構報告：表層觀察 → 設計決策 → 借用框架 → 修辭機制（含倫理位置）→ 可借鏡 → 弱點 |
| 用時機 |「拆解這份」「為什麼這份寫得這麼好」「這個設計的裏側」|
| 指令 | `/deconstruct-toolkit:artifact-deconstruct` |

### 論證專用

#### `argument-deconstruct`

| 欄位 | 內容 |
|-------|-------|
| 對象 | 長文論證、社論、提案、政治文本、學術論文 introduction |
| 方法 | Toulmin 模型（claim / grounds / warrant / backing / rebuttal / qualifier）+ Burke 五元比 + 體裁 move 分析 |
| 核心動作 | 揭露隱性 warrant — 多數論證藏 warrant |
| 輸出 | 論證 map (mermaid) + warrant 顯化 + 缺失反駁表 + 倫理位置 |
| 用時機 |「拆解這篇社論的論證」「這份提案弱在哪」 |
| 指令 | `/deconstruct-toolkit:argument-deconstruct` |

### 原子

#### `assumption-surface`

| 欄位 | 內容 |
|-------|-------|
| 對象 | 任何疑有隱性假設的文本（策略備忘錄、社群推文串、政策簡報） |
| 方法 | 逆 Toulmin · 症狀式閱讀（Althusser 風「讀不在場」）· 反事實探針 · 框架審計 |
| 輸出 | 假設表（5–15 行）+ 強度評等（基礎 / 支柱 / 裝飾）+ 每條基礎假設的可證偽性檢查 |
| 用時機 |「揭露這份備忘錄的隱性假設」「這個主張在 *假設* 什麼」 |
| 指令 | `/deconstruct-toolkit:assumption-surface` |

### Router

#### `using-deconstruct-toolkit`

| 欄位 | 內容 |
|-------|-------|
| skill | 將使用者意圖路由到正確的 sibling skill |
| 方法 | 1 個問題 → 作品類型偵測 → lens 預選 → 派發 |
| 用時機 | 想解構某個東西但不確定要哪個 skill / 哪個 lens |
| 指令 | `/deconstruct-toolkit:using-deconstruct-toolkit` |

## 設計原則

貫穿所有 skill 的原則：

**Design archaeology，不是 summary。** 每個 skill 揭露的是「**決定了什麼**」，不是「**寫了什麼**」。寫作順序與閱讀順序的差，就是設計，那才是要回收的東西。

**Lens 是組合，不是 pipeline。** 每個作品配一組**為其類型挑選的 lens 組合**。6-lens 庫是可選擇的，不是順序執行。LP 用 persuasion + rhetoric；playbook 用 genre + 6 維；UI 用 ux + persuasion。

**Negative space 重要。** *刻意省略* 的東西（缺失的反駁、不存在的 move、未說的假設）是資料，不是缺口。每個 skill 都含 negative space 階段。

**倫理位置強制。** 套用 persuasion 或 UX lens 時，每個偵測到的機制必須打 4 種位置之一：🟢 透明 · 🟡 灰區 · 🔴 操縱 · ⚫ 黑暗模式。不允許中立描述。

**Primary-source 忠實。** 每個 lens 在 reference 檔開頭標明版本 + 章 + 頁的原典引用。不同 skill 對同一 lens 的 operationalization 可不同 — 但都必須對同一 primary source 忠實。見 [ADR-0002](docs/adr/0002-strict-skill-self-containment.md)。

**Skill 獨立性。** 遵守 Anthropic 官方 skill convention，每個 skill 完全自含。Lens 內容跨 skill 可重複，這是刻意的。見 [ADR-0002](docs/adr/0002-strict-skill-self-containment.md)。

## Roadmap

完整 v0.1 → v1.0 路徑見 [docs/design-proposal.md](docs/design-proposal.md) §8。

| 版本 | 增加內容 |
|---|---|
| v0.1.0 | router + artifact-deconstruct + argument-deconstruct + assumption-surface |
| **v0.2.0**（本次釋出）| 文化變體（EN/JA/ZH）：rhetoric / persuasion / genre / frame 4 lens × 3 變體 + 變體選擇 protocol + 8 個 JP/ZH fixture + ADR-0004 |
| v0.3.0 | `product-deconstruct`, `pricing-decode`（商業域擴展，文化變體 aware 起跳）|
| v0.4.0 | `frame-reveal`, `bias-audit`, `decision-archaeology`（原子深化）|
| v0.5.0 | `lens-semiotic` + `lens-ux` 文化變體（中度文化敏感，從 v0.2 延後）|
| v1.0.0 | 20+ 真實 eval case、fixture corpus、開源釋出 |

## 貢獻

歡迎。提案新 skill 前請先開 Issue。本 plugin 每個新 skill **必須**通過兩個 membership gate（見 [ADR-0001](docs/adr/0001-convention-b-mixed-naming.md)）：

1. **動詞 gate** — skill 動詞屬解構家族（`deconstruct / surface / reveal / audit / decode / expose / archaeology`）
2. **對象 gate** — skill 對象是外部、非程式碼作品

PR 遵循 [Conventional Commits](https://www.conventionalcommits.org/)。

## 授權

MIT — 見 repository root 的 [LICENSE](../LICENSE)。
