# monkey-skills

言語: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 個人用 Claude Code plugin marketplace — domain-team workflow、skill 開発、哲学的思考、Obsidian、投資、copywriting、slides、書籍 distillation を網羅した 8 つの plugin。

## Plugin 一覧

| Plugin | Version | Skill 数 | Command 数 | 説明 |
|--------|---------|---------:|-----------:|------|
| [`domain-teams`](domain-teams/) | 5.5.1 | 11 | 9 | Domain team skill — planning、code、design、research、copywriting を checkpoint ベースの quality gate と共に提供。 |
| [`dev-workflow`](dev-workflow/) | 2.0.0 | 7 | 4 | Skill 作成、skill 品質評価、git ベースの project memory、proposal triage、complexity critique、skill refactor、skill tuning。 |
| [`philosophers-toolkit`](philosophers-toolkit/) | 1.0.4 | 12 | 12 | 問題の明確化と深い推論のための哲学的思考 framework。 |
| [`obsidian`](obsidian/) | 3.5.0 | 13 | 1 | Obsidian vault workflow — daily note、markdown、base file、diagram、canvas、file intel、vault 管理、dashboard 設計。 |
| [`investing-toolkit`](investing-toolkit/) | 1.16.5 | 15 | 5 | 投資調査 toolkit — macro regime 診断（US/JP/TW/KR/CN）、DCF、screener、primary source adapter 経由の equity snapshot。 |
| [`copywriting-toolkit`](copywriting-toolkit/) | 1.14.0 | 14 | 1 | Pipeline 構造の copywriting — intake、ideation、ネタ投入、5 種の form 別 drafter、voice 配置、ethics + form gate、audit。 |
| [`slides-toolkit`](slides-toolkit/) | 0.1.0-mvp | 5 | 0 | Google Slides 生成 toolkit — `gws` 経由の template ベース deck pipeline、backend 非依存の design 知識、Platform-Pivot 構成。 |
| [`tsundoku`](tsundoku/) | 0.11.0 | 4 | 5 | Tsundoku 積読 — Kobo の積読 e-book を RIA-TV++ distillation pipeline で実行可能な agent skill 群に変換。 |

**合計**：81 skill、37 slash command（8 plugin 横断）。

> 各 plugin の description で ⚠️ が付いているもの（`investing-toolkit`、`slides-toolkit`、`tsundoku`、および `obsidian` 内の `defuddle` skill）は Claude Code CLI 環境を要求します — Cowork sandbox は外部 network 通信や subprocess 実行を遮断します。

## インストール

### Claude Code（marketplace）

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install <plugin-name>@monkey-skills
```

`<plugin-name>` には上の表のいずれかを指定。

### Gemini CLI（extension）

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

Extension manifest は [`gemini-extension.json`](gemini-extension.json)。

### Codex

Symlink 方式と plugin 方式の手順は [`.codex/INSTALL.md`](.codex/INSTALL.md) を参照。

## Repository 構成

```
monkey-skills/
├── .claude-plugin/
│   └── marketplace.json          # plugin 登録（8 件）
├── .codex/
│   └── INSTALL.md                # Codex 用インストール手順
├── .github/workflows/
│   ├── skill-structure.yml       # CI：skill 規約を強制
│   └── scraper-deps-monthly.yml  # CI：月次の依存リフレッシュ
├── domain-teams/                 # plugin
├── dev-workflow/                 # plugin
├── philosophers-toolkit/         # plugin
├── obsidian/                     # plugin
├── investing-toolkit/            # plugin
├── copywriting-toolkit/          # plugin
├── slides-toolkit/               # plugin
├── tsundoku/                     # plugin
├── docs/                         # 横断 docs（i18n glossary など）
├── scripts/                      # repo レベル tooling
├── CLAUDE.md                     # Claude Code 向けプロジェクト規約
├── GEMINI.md                     # Gemini CLI 向けプロジェクト規約
├── AGENTS.md                     # 汎用 agent 規約
├── ATTRIBUTION.md                # 第三者 import とライセンス
├── LICENSE                       # MIT
└── gemini-extension.json         # Gemini CLI extension manifest
```

## 貢献

本 repository は個人用 marketplace ですが、issue / PR は
[GitHub repository](https://github.com/kouko/monkey-skills) で歓迎します。
Skill 開発規約（ファイルパス、Two-Layer Spec、quality gate、agent role、cross-plugin
delegation）は [`CLAUDE.md`](CLAUDE.md) を参照。

## ライセンス

MIT — 詳細は [`LICENSE`](LICENSE) を参照。

第三者由来のコンポーネント（kepano / axtonliu の Obsidian skill、AllanYiin
の `skill-creator-advance`、softaworks の `skill-judge` ほか）はすべて MIT
ライセンスで、[`ATTRIBUTION.md`](ATTRIBUTION.md) に出典を記載。
