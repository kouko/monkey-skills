# obsidian

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Obsidian vault workflow — daily note、markdown、Bases、図、Canvas、file intel、vault 管理、ダッシュボード設計を Claude Code plugin としてパッケージ化。

## ⚠️ Cowork 互換性

本 plugin の skill のほとんどは Cowork 互換だが、`defuddle` skill のみ例外。
[Defuddle CLI](https://github.com/kepano/defuddle) を subprocess で呼び出して
外部 URL を取得・整形するため、Cowork の sandbox URL allowlist に block される。
`defuddle` は Claude Code CLI で利用すること。同じ制約は
[`investing-toolkit/docs/mcp-setup.md`](../investing-toolkit/docs/mcp-setup.md)
で詳述されている — plugin から起動した subprocess は plugin MCP と同じ sandbox 内で
動くため、両 path とも Cowork では同様に block される。

| Skill | Cowork | Claude Code CLI |
|---|---|---|
| `defuddle` | block（URL fetch） | 動作 |
| その他すべての obsidian skill | 動作 | 動作 |

## Version

3.9.0 — [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) を参照。

## 所属

本 plugin は [`monkey-skills`](https://github.com/kouko/monkey-skills) marketplace の
一部。日々の knowledge work、investing、copywriting、skill 開発のための
Claude Code plugin 群。

## 背景

Obsidian は local-first な markdown knowledge base。日常の vault 作業は小さい
反復タスクの集合になる：今日の daily note を開く、inbox を整理する、
有効な Bases YAML を書く、note 内に Mermaid 図を描く、PDF フォルダを
要約 note としてインポートする、session 終了時に会話の要約を保存する。

本 plugin はそれらのタスクを skill としてパッケージ化し、Claude Code が
intent に応じて dispatch する。Original skill は daily workflow / file intel /
ダッシュボード設計 / vault setup / 会話要約をカバー。Import 済 skill は
Obsidian 固有の markdown / Bases / Obsidian CLI / Defuddle web 抽出 /
Canvas 作成 / Excalidraw 図 / Mermaid 図をカバー。

## Router と agent

### Router

`using-obsidian` が entry skill。ユーザーの依頼内容（daily note、vault setup、
file processing、図、cleanup など）に応じて適切な skill に routing する。

slash command は `/using-obsidian` で呼び出す。

### Agent

`obsidian-vault-organizer` は vault 保守用 agent。定期的な hygiene 作業
（`inbox/` の振り分け、broken wikilink の修復、frontmatter 正規化、
重複候補の検出、tag 名の統一）を担当する。**ファイルは削除しない** —
move か edit のみ。振り分け先が曖昧な場合は確認を取る。

## Skills

### Original skill（this project）

| Skill | 用途 |
|---|---|
| `using-obsidian` | Router — vault workflow の intent を適切な skill に routing |
| `obsidian-daily` | 今日の daily note を読み込み or 作成、`inbox/` を sweep、上位 3 priority を提示 |
| `obsidian-vault-setup` | 対話型 vault 初期設定 — 自由記述の回答から role と scope を推定 |
| `obsidian-tldr` | 会話の要約を vault に保存し、`memory.md` を更新 |
| `obsidian-file-intel` | PDF / PPTX / XLSX / DOCX / CSV / JSON を Gemini で抽出し、Obsidian-ready な要約を生成 |
| `dashboard-design` | デジタル庁ダッシュボード設計ガイドラインに基づき、要件整理から layout までを引導 |

### Wiki layer（LLM 知識蒸留、original）

[Karpathy の LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) と [`Ar9av/obsidian-wiki`](https://github.com/Ar9av/obsidian-wiki) からの着想を、6 カテゴリの「型態軸」（entities / concepts / synthesis / skills / journal / references）、tiered retrieval、SHA-256 delta tracking、bounded auto-research に再設計。各 skill は完全に self-contained — cross-skill / plugin-level 共有 reference は使用しない。

| Skill | 用途 |
|---|---|
| `wiki-setup` | `wiki/` 構造、`.env`、manifest、hot cache の初回 scaffold |
| `wiki-ingest` | source notes（references/、research/ 等）を SHA-256 delta tracking で wiki/ に蒸留。page format spec の所有者 |
| `wiki-query` | tiered retrieval（hot.md → frontmatter summary → full page）で wiki/ を検索 |
| `wiki-cross-linker` | 平文の言及を `[[wikilinks]]` に変換し、知識グラフを補強 |
| `wiki-lint` | 11 項目の health audit — structural / semantic / provenance。Read-only |
| `wiki-auto-research` | 手動 one-shot — Open Questions と ambiguous claim を scan、web search、`research/` にレビュー可能なノート出力 |

### kepano（Steph Ango）からの import

Upstream: [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills)
— MIT, Copyright (c) 2026 Steph Ango。

| Skill | 用途 |
|---|---|
| `obsidian-markdown` | Obsidian Flavored Markdown の作成 — wikilink、embed、callout、properties、コメント |
| `obsidian-bases` | `.base` ファイルの作成・編集 — view、filter、formula、summary |
| `obsidian-cli` | 起動中の Obsidian instance を公式 CLI で操作 — read、create、search、plugin / theme 開発 |
| `defuddle` | Defuddle CLI で web ページから clean markdown を抽出（WebFetch の token 節約版） |

### axtonliu（Axton Liu）からの import

Upstream: [`axtonliu/axton-obsidian-visual-skills`](https://github.com/axtonliu/axton-obsidian-visual-skills)
— MIT, Copyright (c) 2025 Axton Liu。

| Skill | 用途 |
|---|---|
| `obsidian-canvas-creator` | Obsidian Canvas ファイルを MindMap / freeform layout で作成（kepano の json-canvas integration を統合） |
| `obsidian-excalidraw-diagram` | Excalidraw 図を Obsidian / Standard / Animated 形式で生成 |
| `obsidian-mermaid-visualizer` | Mermaid 17 図種（flow / data-viz / structural / time）— Obsidian 11.4.1 最適化、GitHub / Notion / HackMD にも portable |

## Install

```bash
# Claude Code（CLI）内で
/plugin marketplace add kouko/monkey-skills
/plugin install obsidian
```

`defuddle` skill は Defuddle CLI が必要：

```bash
npm install -g defuddle
```

`obsidian-cli` skill は公式 Obsidian CLI と起動中の Obsidian instance が必要 —
[help.obsidian.md/cli](https://help.obsidian.md/cli) 参照。

`obsidian-file-intel` skill は同梱の `scripts/process_files_with_gemini.py` と、
vault に設定済の Gemini API key が必要。

## Usage

一日を始める：

```
/obsidian
> Start my day
```

`using-obsidian` が `obsidian-daily` に route。`daily/YYYY-MM-DD.md` を
読み込み or 作成し、`inbox/` の項目を列挙、上位 3 priority を提示する。

session 終了時に会話の要約を保存：

```
> Save a TLDR of this conversation
```

`using-obsidian` が `obsidian-tldr` に route。関連フォルダに markdown 要約を
書き込み、`memory.md` を更新する。

note 内に図を描く：

```
> OAuth device flow の Mermaid sequence 図を作って
```

`using-obsidian` が `obsidian-mermaid-visualizer` に route。sequence diagram type
を選択し、Obsidian 11.4.1 quirk を適用、` ```mermaid ` ブロックを出力する。

## Repository 構造

```
obsidian/
├── .claude-plugin/
│   └── plugin.json              # plugin metadata、version 3.9.0
├── agents/
│   └── obsidian-vault-organizer.md  # vault 保守 agent
├── commands/
│   └── obsidian.md              # /obsidian → using-obsidian
├── skills/
│   ├── README.md                # skill 別 attribution 表
│   ├── using-obsidian/          # router（original）
│   ├── obsidian-daily/          # daily workflow（original）
│   ├── obsidian-vault-setup/    # vault 初期設定（original）
│   ├── obsidian-tldr/           # 会話要約（original）
│   ├── obsidian-file-intel/     # ファイル → Obsidian 要約（original）
│   ├── dashboard-design/        # ダッシュボード設計（original）
│   ├── obsidian-markdown/       # kepano から import
│   ├── obsidian-bases/          # kepano から import
│   ├── obsidian-cli/            # kepano から import
│   ├── defuddle/                # kepano から import
│   ├── obsidian-canvas-creator/ # axtonliu から import
│   ├── obsidian-excalidraw-diagram/ # axtonliu から import
│   ├── obsidian-mermaid-visualizer/ # axtonliu から import
│   ├── wiki-setup/                # wiki layer 初期化（original）
│   ├── wiki-ingest/               # source → wiki 蒸留（original）
│   ├── wiki-query/                # tiered retrieval（original）
│   ├── wiki-cross-linker/         # 知識グラフ補強（original）
│   ├── wiki-lint/                 # health audit（original）
│   └── wiki-auto-research/        # web search で gap 補完（original）
├── README.md
├── README.ja.md
└── README.zh-TW.md
```

skill 別の attribution は [`skills/README.md`](skills/README.md)、
repo 全体の attribution は [`../ATTRIBUTION.md`](../ATTRIBUTION.md) を参照。

## 貢献

- bug 報告・機能要望：
  [github.com/kouko/monkey-skills/issues](https://github.com/kouko/monkey-skills/issues)
  に issue を開いてください。
- PR 歓迎。既存の skill 構造（frontmatter + workflow + reference ファイル）に
  合わせ、Conventional Commits を使うこと。
- import 済 skill については、kepano / axtonliu 上流からの変更が流れてくる。
  上流に該当する修正は upstream PR の検討も推奨。

## License

MIT — 詳細は repository root の [LICENSE](../LICENSE) を参照。

import 済 skill は各 skill の `LICENSE` ファイルに原著作権表示を保持：

- `defuddle`、`obsidian-bases`、`obsidian-cli`、`obsidian-markdown` — MIT,
  Copyright (c) 2026 Steph Ango。各 skill 配下の `LICENSE` 参照。
- `obsidian-canvas-creator`、`obsidian-excalidraw-diagram`、
  `obsidian-mermaid-visualizer` — MIT, Copyright (c) 2025 Axton Liu。
  各 skill 配下の `LICENSE` 参照。（`obsidian-canvas-creator` は kepano 由来の
  json-canvas integration も同梱。）

プロジェクト全体の license は [LICENSE](../LICENSE)、third-party コンポーネント
全体は [ATTRIBUTION.md](../ATTRIBUTION.md) を参照。
