# obsidian

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Obsidian vault workflow — daily note、markdown、Bases、圖表、Canvas、file intel、vault 管理、dashboard 設計，封裝為 Claude Code plugin。

## ⚠️ Cowork 相容性

本 plugin 大部分 skill 都與 Cowork 相容，唯獨 `defuddle` skill 例外 ——
它透過 subprocess 呼叫 [Defuddle CLI](https://github.com/kepano/defuddle)
抓取與清理外部 URL，會被 Cowork 的 sandbox URL allowlist 阻擋。
請在 Claude Code CLI 使用 `defuddle`。相同限制亦記錄於
[`investing-toolkit/docs/mcp-setup.md`](../investing-toolkit/docs/mcp-setup.md)：
plugin 安裝的 subprocess 與 plugin MCP 在同一個 sandbox 內執行，因此
兩條路徑在 Cowork 都同樣會被擋。

| Skill | Cowork | Claude Code CLI |
|---|---|---|
| `defuddle` | 阻擋（URL 抓取） | 可運作 |
| 其他所有 obsidian skill | 可運作 | 可運作 |

## Version

3.7.0 — 參見 [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json)。

## 所屬

本 plugin 隸屬於 [`monkey-skills`](https://github.com/kouko/monkey-skills) marketplace —
一組面向日常 knowledge work、investing、copywriting 與 skill 開發的 Claude Code plugin。

## 背景

Obsidian 是 local-first 的 markdown 知識庫。日常 vault 工作充滿小而重複的任務：
打開今天的 daily note、整理 inbox、撰寫合法的 Bases YAML、在 note 內畫
Mermaid 圖、把一整個 PDF 資料夾匯入成摘要 note，以及在 session 結束時
保存對話摘要。

本 plugin 把這些任務封裝為 skill，讓 Claude Code 依 intent dispatch。
Original skill 涵蓋 daily workflow、file intel、dashboard 設計、vault setup、
對話摘要。Imported skill 則涵蓋 Obsidian 專屬 markdown、Bases、Obsidian CLI、
Defuddle 網頁萃取、Canvas 建立、Excalidraw 圖與 Mermaid 圖。

## Router 與 agent

### Router

`using-obsidian` 是入口 skill，依使用者意圖（daily note、vault setup、
file processing、圖表、清理 vault）將請求 routing 至正確的 skill。

slash command `/obsidian` 會呼叫 `using-obsidian`。

### Agent

`obsidian-vault-organizer` 是 vault 維運 agent，負責週期性的 hygiene 任務
（整理 `inbox/`、修復壞掉的 wikilink、正規化 frontmatter、標示重複候選、
統一 tag 命名）。**絕不刪檔** —— 僅 move 或 edit；目的地不明時會先確認。

## Skills

### Original skill（this project）

| Skill | 用途 |
|---|---|
| `using-obsidian` | Router —— 把 vault workflow 意圖 routing 至正確的 skill |
| `obsidian-daily` | 讀取或建立今日 daily note，整理 `inbox/`，列出今日 top 3 priority |
| `obsidian-vault-setup` | 互動式 vault 首次設定 —— 從自由文字回答推測 role 與 scope |
| `obsidian-tldr` | 把對話摘要寫入 vault，並更新 `memory.md` |
| `obsidian-file-intel` | 透過 Gemini 從 PDF / PPTX / XLSX / DOCX / CSV / JSON 萃取內容並產出 Obsidian-ready 摘要 |
| `dashboard-design` | 依日本數位廳 dashboard 設計指引，從需求釐清引導到 layout |

### Wiki 知識層（LLM 知識萃取，original）

靈感來自 [Karpathy 的 LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 與 [`Ar9av/obsidian-wiki`](https://github.com/Ar9av/obsidian-wiki)，以 6 類「型態軸」（entities / concepts / synthesis / skills / journal / references）、tiered retrieval、SHA-256 delta tracking、bounded auto-research 重新設計。每個 skill 完全 self-contained —— 不使用跨 skill 引用、亦不使用 plugin-level 共用 reference。

| Skill | 用途 |
|---|---|
| `wiki-setup` | 一次性建立 `wiki/` 結構、`.env`、manifest、hot cache |
| `wiki-ingest` | 把 source notes（references/、research/ 等）以 SHA-256 delta tracking 萃取至 wiki/。為頁面格式 spec 的擁有者 |
| `wiki-query` | 用 tiered retrieval（hot.md → frontmatter summary → 全頁）查詢 wiki/ |
| `wiki-cross-linker` | 把純文字提及轉為 `[[wikilinks]]`，補強知識圖譜 |
| `wiki-lint` | 11 項健康檢查 —— structural / semantic / provenance。Read-only |
| `wiki-auto-research` | 手動 one-shot —— 掃描 Open Questions 與低信心聲明，web search 後輸出可審閱的研究筆記到 `research/` |

### 引入自 kepano（Steph Ango）

Upstream：[`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills)
—— MIT, Copyright (c) 2026 Steph Ango。

| Skill | 用途 |
|---|---|
| `obsidian-markdown` | 撰寫 Obsidian Flavored Markdown —— wikilink、embed、callout、properties、註解 |
| `obsidian-bases` | 建立與編輯 `.base` 檔，含 view、filter、formula、summary |
| `obsidian-cli` | 透過官方 CLI 操作運行中的 Obsidian instance —— read / create / search / plugin 與 theme 開發 |
| `defuddle` | 透過 Defuddle CLI 從網頁萃取乾淨 markdown（節省 token，取代 WebFetch） |

### 引入自 axtonliu（Axton Liu）

Upstream：[`axtonliu/axton-obsidian-visual-skills`](https://github.com/axtonliu/axton-obsidian-visual-skills)
—— MIT, Copyright (c) 2025 Axton Liu。

| Skill | 用途 |
|---|---|
| `obsidian-canvas-creator` | 建立 Obsidian Canvas 檔，支援 MindMap 或 freeform layout（整合 kepano 的 json-canvas） |
| `obsidian-excalidraw-diagram` | 產生 Excalidraw 圖（Obsidian / Standard / Animated 三種格式） |
| `obsidian-mermaid-visualizer` | 17 種 Mermaid 圖（flow / data-viz / structural / time）—— 為 Obsidian 11.4.1 優化，可移植到 GitHub / Notion / HackMD |

## Install

```bash
# 在 Claude Code（CLI）內
/plugin marketplace add kouko/monkey-skills
/plugin install obsidian
```

`defuddle` skill 需要 Defuddle CLI：

```bash
npm install -g defuddle
```

`obsidian-cli` skill 需要官方 Obsidian CLI 與運行中的 Obsidian instance ——
參見 [help.obsidian.md/cli](https://help.obsidian.md/cli)。

`obsidian-file-intel` skill 需要內附的 `scripts/process_files_with_gemini.py`
與在 vault 中設定好的 Gemini API key。

## Usage

開始一天：

```
/obsidian
> Start my day
```

`using-obsidian` 會 routing 到 `obsidian-daily`，讀取或建立
`daily/YYYY-MM-DD.md`、列出 `inbox/` 內容，並提示 top 3 priority。

session 結束時保存對話摘要：

```
> Save a TLDR of this conversation
```

`using-obsidian` 會 routing 到 `obsidian-tldr`，把 markdown 摘要寫入
相關資料夾並更新 `memory.md`。

在 note 內畫圖：

```
> 幫我畫 OAuth device flow 的 Mermaid sequence diagram
```

`using-obsidian` 會 routing 到 `obsidian-mermaid-visualizer`，挑選
sequence diagram type、套用 Obsidian 11.4.1 的 quirk，輸出
` ```mermaid ` 區塊。

## Repository 結構

```
obsidian/
├── .claude-plugin/
│   └── plugin.json              # plugin metadata，version 3.7.0
├── agents/
│   └── obsidian-vault-organizer.md  # vault 維運 agent
├── commands/
│   └── obsidian.md              # /obsidian → using-obsidian
├── skills/
│   ├── README.md                # 各 skill attribution 表
│   ├── using-obsidian/          # router（original）
│   ├── obsidian-daily/          # daily workflow（original）
│   ├── obsidian-vault-setup/    # vault 設定（original）
│   ├── obsidian-tldr/           # 對話摘要（original）
│   ├── obsidian-file-intel/     # 檔案 → Obsidian 摘要（original）
│   ├── dashboard-design/        # dashboard 設計（original）
│   ├── obsidian-markdown/       # 引入自 kepano
│   ├── obsidian-bases/          # 引入自 kepano
│   ├── obsidian-cli/            # 引入自 kepano
│   ├── defuddle/                # 引入自 kepano
│   ├── obsidian-canvas-creator/ # 引入自 axtonliu
│   ├── obsidian-excalidraw-diagram/ # 引入自 axtonliu
│   ├── obsidian-mermaid-visualizer/ # 引入自 axtonliu
│   ├── wiki-setup/                # wiki layer 初始化（original）
│   ├── wiki-ingest/               # source → wiki 萃取（original）
│   ├── wiki-query/                # tiered retrieval（original）
│   ├── wiki-cross-linker/         # 知識圖譜補強（original）
│   ├── wiki-lint/                 # health audit（original）
│   └── wiki-auto-research/        # 用 web search 補完知識缺口（original）
├── README.md
├── README.ja.md
└── README.zh-TW.md
```

各 skill 的 attribution 詳見 [`skills/README.md`](skills/README.md)；
整個 repo 的 attribution 詳見 [`../ATTRIBUTION.md`](../ATTRIBUTION.md)。

## 貢獻

- Bug 回報與功能建議：請至
  [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
  開 issue。
- 歡迎 PR。請維持既有 skill 結構（frontmatter + workflow + reference 檔），
  並使用 Conventional Commits。
- 引入自上游的 skill：kepano / axtonliu 上游變更會持續流入；如修正屬於
  上游性質，建議同步開 upstream PR。

## License

MIT — 詳見 repository root 的 [LICENSE](../LICENSE)。

引入的 skill 在各 skill 的 `LICENSE` 檔保留原著作權聲明：

- `defuddle`、`obsidian-bases`、`obsidian-cli`、`obsidian-markdown` —— MIT,
  Copyright (c) 2026 Steph Ango。詳見各 skill 內的 `LICENSE`。
- `obsidian-canvas-creator`、`obsidian-excalidraw-diagram`、
  `obsidian-mermaid-visualizer` —— MIT, Copyright (c) 2025 Axton Liu。
  詳見各 skill 內的 `LICENSE`。（`obsidian-canvas-creator` 同時包含 kepano
  的 json-canvas integration。）

整個專案的 license 詳見 [LICENSE](../LICENSE)，
完整 third-party 元件對照表詳見 [ATTRIBUTION.md](../ATTRIBUTION.md)。
