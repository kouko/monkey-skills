# obsidian

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> ⚠️ **Cowork 互換性**：ほとんどの skill は全環境で動作する。`defuddle` skill は Claude Code CLI が必要 — Cowork sandbox が plugin subprocess からの外部 HTTP をブロックするため。他の skill（vault management、daily note、diagram、canvas、dashboard、file-intel）は Cowork 対応。詳細な retrospective は [`../investing-toolkit/docs/mcp-setup.md`](../investing-toolkit/docs/mcp-setup.md) を参照。

**Version**: 3.5.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)

Obsidian vault workflow — daily note、ビジュアルツール、file intelligence、
dashboard 設計。本プロジェクトのオリジナル skill と、Obsidian コミュニティ
（kepano / axtonliu）から MIT ライセンスで import した skill を組み合わせ。

## Router + Agent

| Type | Name | 役割 |
|------|------|------|
| Skill | `using-obsidian` | エントリーポイント — vault タスクを適切な skill に route |
| Agent | `obsidian-vault-organizer` | Vault のクリーンアップと整理（haiku） |

## 本プロジェクトのオリジナル skill

| Skill | Slash cmd | 役割 |
|-------|-----------|------|
| `obsidian-daily` | `/obsidian` | 一日の始まり — daily note、優先事項 |
| `obsidian-vault-setup` | — | 対話型 vault 設定 |
| `obsidian-tldr` | — | 会話のサマリーを vault に保存 |
| `obsidian-file-intel` | — | ファイル内容（PDF/PPTX/XLSX/DOCX 等）を Obsidian ノートに抽出 |
| `dashboard-design` | — | Dashboard 設計 workflow |

## Steph Ango (kepano) より import — MIT

Upstream: [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills)

| Skill | 役割 |
|-------|------|
| `defuddle` | Web ページからクリーンな markdown を抽出（ノイズ除去） |
| `obsidian-bases` | Obsidian Bases（.base ファイル）の作成・編集 |
| `obsidian-cli` | Obsidian CLI 経由で vault と対話 |
| `obsidian-markdown` | Obsidian flavored Markdown（wikilink、embed、callout、properties） |

## Axton Liu (axtonliu) より import — MIT

Upstream: [`axtonliu/axton-obsidian-visual-skills`](https://github.com/axtonliu/axton-obsidian-visual-skills)

| Skill | 役割 |
|-------|------|
| `obsidian-canvas-creator` | Canvas ファイルの作成（MindMap / freeform レイアウト）— axtonliu のベースと kepano の json-canvas を組み合わせ |
| `obsidian-excalidraw-diagram` | Excalidraw 図の生成（mind map、animated flowchart） |
| `obsidian-mermaid-visualizer` | Mermaid 図の作成 — 17 種類のタイプ、flowchart、sequence / state / class / ER / C4 / git-branch、各種 chart、スケジュール、architecture / block diagram に対応 |

合計 13 skill + 1 agent + 1 slash command。

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
    ├── defuddle/                    ← 3rd-party (kepano, MIT)
    ├── obsidian-bases/              ← 3rd-party (kepano, MIT)
    ├── obsidian-cli/                ← 3rd-party (kepano, MIT)
    ├── obsidian-markdown/           ← 3rd-party (kepano, MIT)
    ├── obsidian-canvas-creator/     ← 3rd-party (axtonliu + kepano, MIT)
    ├── obsidian-excalidraw-diagram/ ← 3rd-party (axtonliu, MIT)
    └── obsidian-mermaid-visualizer/ ← 3rd-party (axtonliu, MIT)
```

skill ごとの attribution 表: [`skills/README.md`](skills/README.md)。
Repo 全体の attribution（upstream URL + 改変サマリー）:
[`../ATTRIBUTION.md`](../ATTRIBUTION.md)。

## License

MIT — repository ルートの [`LICENSE`](../LICENSE) を参照。第三者
コンポーネントは元の著作権表示を保持（Steph Ango、Axton Liu）。
