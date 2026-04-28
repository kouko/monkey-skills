# obsidian

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**Version**：3.5.0
**Part of**：[monkey-skills](https://github.com/kouko/monkey-skills)

Obsidian vault workflow — daily note、視覺化工具、file intelligence、
dashboard 設計。結合本專案原創 skill 與 Obsidian 社群（kepano / axtonliu）
以 MIT 授權匯入的 skill。

## Router + Agent

| Type | Name | 角色 |
|------|------|------|
| Skill | `using-obsidian` | 入口 — 將 vault 任務 route 到對應 skill |
| Agent | `obsidian-vault-organizer` | Vault 清理與整理（haiku） |

## 本專案原創 skill

| Skill | Slash cmd | 角色 |
|-------|-----------|------|
| `obsidian-daily` | `/obsidian` | 開始一天 — daily note、優先事項 |
| `obsidian-vault-setup` | — | 互動式 vault 設定 |
| `obsidian-tldr` | — | 將對話摘要存入 vault |
| `obsidian-file-intel` | — | 將檔案內容（PDF/PPTX/XLSX/DOCX 等）擷取為 Obsidian 筆記 |
| `dashboard-design` | — | Dashboard 設計 workflow |

## 自 Steph Ango (kepano) 匯入 — MIT

Upstream：[`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills)

| Skill | 角色 |
|-------|------|
| `defuddle` | 從網頁擷取乾淨的 markdown（去除雜訊） |
| `obsidian-bases` | 建立與編輯 Obsidian Bases（.base 檔） |
| `obsidian-cli` | 透過 Obsidian CLI 與 vault 互動 |
| `obsidian-markdown` | Obsidian flavored Markdown（wikilink、embed、callout、properties） |

## 自 Axton Liu (axtonliu) 匯入 — MIT

Upstream：[`axtonliu/axton-obsidian-visual-skills`](https://github.com/axtonliu/axton-obsidian-visual-skills)

| Skill | 角色 |
|-------|------|
| `obsidian-canvas-creator` | 建立 Canvas 檔案（MindMap / freeform 佈局）— 結合 axtonliu 基底與 kepano 的 json-canvas |
| `obsidian-excalidraw-diagram` | 生成 Excalidraw 圖表（mind map、animated flowchart） |
| `obsidian-mermaid-visualizer` | 建立 Mermaid 圖表 — 17 種類型，涵蓋 flowchart、sequence / state / class / ER / C4 / git-branch、各式 chart、行程表、architecture / block diagram |

合計 13 個 skill + 1 個 agent + 1 個 slash command。

## Repository Structure

```
obsidian/
├── .claude-plugin/plugin.json
├── agents/
│   └── obsidian-vault-organizer.md  ← haiku
├── commands/
│   └── obsidian.md                  ← /obsidian
└── skills/
    ├── README.md                    ← Skill attribution 表
    ├── using-obsidian/              ← Router
    ├── obsidian-daily/
    ├── obsidian-vault-setup/
    ├── obsidian-tldr/
    ├── obsidian-file-intel/
    ├── dashboard-design/
    ├── defuddle/                    ← 第三方 (kepano, MIT)
    ├── obsidian-bases/              ← 第三方 (kepano, MIT)
    ├── obsidian-cli/                ← 第三方 (kepano, MIT)
    ├── obsidian-markdown/           ← 第三方 (kepano, MIT)
    ├── obsidian-canvas-creator/     ← 第三方 (axtonliu + kepano, MIT)
    ├── obsidian-excalidraw-diagram/ ← 第三方 (axtonliu, MIT)
    └── obsidian-mermaid-visualizer/ ← 第三方 (axtonliu, MIT)
```

各 skill 的 attribution 表：[`skills/README.md`](skills/README.md)。
Repo 全域 attribution（含 upstream URL 與修改摘要）：
[`../ATTRIBUTION.md`](../ATTRIBUTION.md)。

## License

MIT — 詳見 repository 根目錄 [`LICENSE`](../LICENSE)。第三方元件
保留其原始著作權聲明（Steph Ango、Axton Liu）。
