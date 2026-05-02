# monkey-skills

語言：[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 個人 Claude Code plugin marketplace — 9 個 plugin，涵蓋 domain-team workflow、skill 開發、哲學思考、Obsidian、投資、copywriting、slides、書籍 distillation、code repo 知識。

## Plugin 列表

| Plugin | 版本 | Skill 數 | Command 數 | 說明 |
|--------|------|---------:|-----------:|------|
| [`domain-teams`](domain-teams/) | 5.5.1 | 11 | 9 | Domain team skill — planning、code、design、research、copywriting，搭配 checkpoint 為基礎的 quality gate。 |
| [`dev-workflow`](dev-workflow/) | 2.0.0 | 7 | 4 | Skill 建立、skill 品質評分、git 為基底的 project memory、proposal triage、complexity critique、skill refactor、skill tuning。 |
| [`philosophers-toolkit`](philosophers-toolkit/) | 1.0.4 | 12 | 12 | 用於釐清問題與深化推理的哲學思考 framework。 |
| [`obsidian`](obsidian/) | 3.5.0 | 13 | 1 | Obsidian vault workflow — daily note、markdown、base file、diagram、canvas、file intel、vault 管理、dashboard 設計。 |
| [`investing-toolkit`](investing-toolkit/) | 1.16.5 | 15 | 5 | 投資研究 toolkit — macro regime 診斷（US/JP/TW/KR/CN）、DCF、screener、透過 primary source adapter 取得的 equity snapshot。 |
| [`copywriting-toolkit`](copywriting-toolkit/) | 1.14.0 | 14 | 1 | Pipeline 結構的 copywriting — intake、ideation、neta 投入、5 種 form 專屬 drafter、voice 定位、ethics + form gate、audit。 |
| [`slides-toolkit`](slides-toolkit/) | 0.1.0-mvp | 5 | 0 | Google Slides 產生 toolkit — 透過 `gws` 的 template 化 deck pipeline、backend 中立的 design 知識、Platform-Pivot 架構。 |
| [`tsundoku`](tsundoku/) | 0.11.0 | 4 | 5 | Tsundoku 積読 — 把 Kobo 上「買了沒讀」的 e-book，透過 RIA-TV++ distillation pipeline 變成可執行的 agent skill 集。 |
| [`repo-wiki`](repo-wiki/) | 1.0.0 | 3 | 3 | Code repo 版 LLM Wiki Pattern — 從 git 歷史 seed `.repo-wiki/` (init)、從變更/context/外部文件成長 (ingest, polymorphic)、用 `src/` 驗證的 query (Eager triggers + 分段輸出)。 |

**總計**：84 個 skill、40 個 slash command（橫跨 9 個 plugin）。

> 在自身 description 中標示 ⚠️ 的 plugin（`investing-toolkit`、`slides-toolkit`、`tsundoku`，以及 `obsidian` 中的 `defuddle` skill）必須在 Claude Code CLI 環境執行 — Cowork sandbox 會封鎖其對外網路或 subprocess 操作。

## 安裝

### Claude Code（marketplace）

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install <plugin-name>@monkey-skills
```

`<plugin-name>` 替換為上表中任一 plugin 名稱。

### Gemini CLI（extension）

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

Extension manifest 位於 [`gemini-extension.json`](gemini-extension.json)。

### Codex

Symlink 與 plugin 兩種安裝方式請見 [`.codex/INSTALL.md`](.codex/INSTALL.md)。

## Repository 結構

```
monkey-skills/
├── .claude-plugin/
│   └── marketplace.json          # plugin 註冊表（8 筆）
├── .codex/
│   └── INSTALL.md                # Codex 安裝指南
├── .github/workflows/
│   ├── skill-structure.yml       # CI：強制 skill 結構規範
│   └── scraper-deps-monthly.yml  # CI：每月相依套件更新
├── domain-teams/                 # plugin
├── dev-workflow/                 # plugin
├── philosophers-toolkit/         # plugin
├── obsidian/                     # plugin
├── investing-toolkit/            # plugin
├── copywriting-toolkit/          # plugin
├── slides-toolkit/               # plugin
├── tsundoku/                     # plugin
├── repo-wiki/                    # plugin
├── docs/                         # 橫切文件（i18n glossary 等）
├── scripts/                      # repo 等級的工具
├── CLAUDE.md                     # 給 Claude Code 的專案慣例
├── GEMINI.md                     # 給 Gemini CLI 的專案慣例
├── AGENTS.md                     # 通用 agent 慣例
├── ATTRIBUTION.md                # 第三方來源與授權
├── LICENSE                       # MIT
└── gemini-extension.json         # Gemini CLI extension manifest
```

## 貢獻

本 repository 屬個人 marketplace，但仍歡迎在
[GitHub repository](https://github.com/kouko/monkey-skills) 提交 issue 與 PR。
Skill 開發慣例（檔案路徑、Two-Layer Spec、quality gate、agent role、跨 plugin
delegation）請參閱 [`CLAUDE.md`](CLAUDE.md)。

## 授權

MIT — 詳細請見 [`LICENSE`](LICENSE)。

第三方來源元件（kepano / axtonliu 的 Obsidian skill、AllanYiin 的
`skill-creator-advance`、softaworks 的 `skill-judge` 等）皆為 MIT 授權，
出處列於 [`ATTRIBUTION.md`](ATTRIBUTION.md)。
