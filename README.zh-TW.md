# Monkey Skills

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

個人 agent skills marketplace — **8 個 plugin**，涵蓋 domain-team quality gate、
Obsidian vault workflow、哲學思考框架、skill 撰寫工具、investing research、
pipeline 化的 copywriting、Google Slides 自動生成、以及 Kobo 書庫 skill 蒸餾。

## Plugins

| Plugin | 版本 | Skills | Commands | 說明 |
|--------|--------:|-------:|---------:|-------------|
| [`domain-teams`](domain-teams/README.md) | 5.2.0 | 10 | 9 | 9 個團隊的 skill 套件，內建 checkpoint 式 quality gate（planning / code / docs / qa / devops / design / research / investing / copywriting）+ skill-team meta-skill + router |
| [`obsidian`](obsidian/README.md) | 3.5.0 | 13 (+1 agent) | 1 | Obsidian vault workflow — daily note、diagram、dashboard，整合 kepano 與 axtonliu 的視覺化 skill |
| [`philosophers-toolkit`](philosophers-toolkit/README.md) | 1.0.4 | 12 | 12 | 哲學思考框架，用於釐清問題與深化推論 |
| [`dev-workflow`](dev-workflow/README.md) | 1.0.4 | 1 | 1 | Skill 創建與評估流程（改編自 Anthropic → AllanYiin 鏈） |
| [`investing-toolkit`](investing-toolkit/README.md) | 1.16.5 | 15 | 5 | Investing research — US/JP/TW/KR/CN macro regime 診斷、DCF、stock screener、stock snapshot |
| [`copywriting-toolkit`](copywriting-toolkit/README.md) | 1.14.0 | 14 | 1 | Pipeline 化 copywriting — 9-phase pipeline、90 voice anchor 資料庫、ethics + form gate。與 `domain-teams:copywriting-team` A/B 並存 |
| [`slides-toolkit`](slides-toolkit/README.md) | 0.1.0-mvp | 5 | 0 | Google Slides 自動生成 — brief → deck URL pipeline 透過 `gws` CLI、backend-agnostic 設計知識（Minto / SCQA / chart-selection）、Platform-Pivot 多 backend 架構 |
| [`tsundoku`](tsundoku/README.md) | 0.11.0 | 4 | 5 | Kobo 書庫搜尋 → DRM-free EPUB 下載 → 分章 Markdown → 原子化 agent skill 蒸餾，透過 RIA-TV++ pipeline（Adler 解析閱讀 / 5 個 parallel extractor / triple verification / Zettelkasten） |

**合計**：74 skills、34 slash commands、8 個 plugin。

每個 plugin 都有自己的 `README.md`，內含完整 skill 清單、架構與用法說明。
本根目錄 README 僅作為 plugin 索引。

## Install

### Claude Code

```bash
claude plugin marketplace add kouko/monkey-skills
# 8 個 plugin 全部可用：
#   domain-teams, obsidian, philosophers-toolkit, dev-workflow,
#   investing-toolkit, copywriting-toolkit, slides-toolkit, tsundoku
```

只安裝特定 plugin：

```bash
claude plugin install domain-teams@kouko/monkey-skills
claude plugin install obsidian@kouko/monkey-skills
# ...其他依此類推
```

### Gemini CLI

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

### Codex

請見 [`.codex/INSTALL.md`](.codex/INSTALL.md)。

## Repository 結構

```
monkey-skills/
├── .claude-plugin/marketplace.json   ← 列出所有 8 個 plugin
├── domain-teams/                     ← Plugin（見 domain-teams/README.md）
├── obsidian/                         ← Plugin（見 obsidian/README.md）
├── philosophers-toolkit/             ← Plugin（見 philosophers-toolkit/README.md）
├── dev-workflow/                     ← Plugin（見 dev-workflow/README.md）
├── investing-toolkit/                ← Plugin（見 investing-toolkit/README.md）
├── copywriting-toolkit/              ← Plugin（見 copywriting-toolkit/README.md）
├── slides-toolkit/                   ← Plugin（見 slides-toolkit/README.md）
├── tsundoku/                         ← Plugin（見 tsundoku/README.md）
│
├── LICENSE                           ← 專案 MIT（kouko）+ 第三方授權指引
├── ATTRIBUTION.md                    ← 第三方匯入內容彙整
├── CLAUDE.md                         ← Claude Code context（skill 撰寫慣例）
├── GEMINI.md                         ← Gemini CLI context
├── AGENTS.md                         ← Codex / Copilot CLI context
├── gemini-extension.json             ← Gemini CLI extension manifest
└── .github/workflows/
    └── skill-structure.yml           ← CI：SKILL.md 結構 + Conventional Commits 檢查
```

## License

本專案採用 MIT License — 詳見 [LICENSE](LICENSE)，內含專案層級宣告與
各組件授權檔的指引。

第三方組件保留原作者著作權（Steph Ango、Axton Liu、AllanYiin / 尹相志、
Anthropic）。完整 attribution（含上游 URL、授權條款、修改摘要）請見
[ATTRIBUTION.md](ATTRIBUTION.md)。

如需回報授權或 attribution 問題，請至
https://github.com/kouko/monkey-skills/issues 開 issue。
