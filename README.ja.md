# Monkey Skills

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

個人用 agent skills marketplace — **8 plugins** で
domain-team quality gate、Obsidian vault workflow、哲学的思考
framework、skill 作成ツール、investing research、pipeline 化
copywriting、Google Slides 自動生成、Kobo 書庫からの skill 蒸留
をカバー。

## Plugins

| Plugin | バージョン | Skills | Commands | 説明 |
|--------|--------:|-------:|---------:|-------------|
| [`domain-teams`](domain-teams/README.md) | 5.2.0 | 10 | 9 | checkpoint 式 quality gate を備えた 9 チームの skill スイート（planning / code / docs / qa / devops / design / research / investing / copywriting）+ skill-team meta-skill + router |
| [`obsidian`](obsidian/README.md) | 3.5.0 | 13 (+1 agent) | 1 | Obsidian vault workflow — daily note、diagram、dashboard、kepano と axtonliu のビジュアル skill を統合 |
| [`philosophers-toolkit`](philosophers-toolkit/README.md) | 1.0.4 | 12 | 12 | 問題の明確化と深い推論のための哲学的思考 framework |
| [`dev-workflow`](dev-workflow/README.md) | 1.0.4 | 1 | 1 | Skill の作成と評価 workflow（Anthropic → AllanYiin 系譜から派生） |
| [`investing-toolkit`](investing-toolkit/README.md) | 1.16.5 | 15 | 5 | Investing research — US/JP/TW/KR/CN macro regime 診断、DCF、stock screener、stock snapshot |
| [`copywriting-toolkit`](copywriting-toolkit/README.md) | 1.14.0 | 14 | 1 | Pipeline 化 copywriting — 9-phase pipeline、90 voice anchor のライブラリ、ethics + form gate。`domain-teams:copywriting-team` と A/B 共存 |
| [`slides-toolkit`](slides-toolkit/README.md) | 0.1.0-mvp | 5 | 0 | Google Slides 自動生成 — brief → deck URL pipeline を `gws` CLI で実現、backend-agnostic な design 知識（Minto / SCQA / chart-selection）、Platform-Pivot multi-backend architecture |
| [`tsundoku`](tsundoku/README.md) | 0.11.0 | 4 | 5 | Kobo 書庫検索 → DRM-free EPUB ダウンロード → chunked Markdown → 原子化 agent skill への蒸留、RIA-TV++ pipeline 経由（Adler 分析的読書 / 5 つの parallel extractor / triple verification / Zettelkasten） |

**合計**：74 skills、34 slash commands、8 plugins。

各 plugin には独自の `README.md` があり、完全な skill 一覧、
architecture、使用方法が記載されています。本ルート README は
plugin の index のみを提供します。

## Install

### Claude Code

```bash
claude plugin marketplace add kouko/monkey-skills
# 8 plugins すべてが利用可能になります：
#   domain-teams, obsidian, philosophers-toolkit, dev-workflow,
#   investing-toolkit, copywriting-toolkit, slides-toolkit, tsundoku
```

特定の plugin のみインストール：

```bash
claude plugin install domain-teams@kouko/monkey-skills
claude plugin install obsidian@kouko/monkey-skills
# ...以下同様
```

### Gemini CLI

```bash
gemini extensions install https://github.com/kouko/monkey-skills
```

### Codex

[`.codex/INSTALL.md`](.codex/INSTALL.md) を参照してください。

## Repository 構成

```
monkey-skills/
├── .claude-plugin/marketplace.json   ← 8 plugins を列挙
├── domain-teams/                     ← Plugin（domain-teams/README.md 参照）
├── obsidian/                         ← Plugin（obsidian/README.md 参照）
├── philosophers-toolkit/             ← Plugin（philosophers-toolkit/README.md 参照）
├── dev-workflow/                     ← Plugin（dev-workflow/README.md 参照）
├── investing-toolkit/                ← Plugin（investing-toolkit/README.md 参照）
├── copywriting-toolkit/              ← Plugin（copywriting-toolkit/README.md 参照）
├── slides-toolkit/                   ← Plugin（slides-toolkit/README.md 参照）
├── tsundoku/                         ← Plugin（tsundoku/README.md 参照）
│
├── LICENSE                           ← プロジェクト MIT（kouko）+ サードパーティ参照
├── ATTRIBUTION.md                    ← サードパーティ取り込みのまとめ
├── CLAUDE.md                         ← Claude Code context（skill 作成規約）
├── GEMINI.md                         ← Gemini CLI context
├── AGENTS.md                         ← Codex / Copilot CLI context
├── gemini-extension.json             ← Gemini CLI extension manifest
└── .github/workflows/
    └── skill-structure.yml           ← CI：SKILL.md 構造 + Conventional Commits チェック
```

## License

本プロジェクトは MIT License で配布されます — プロジェクトレベルの
表記と各コンポーネントのライセンスファイルへのポインタは
[LICENSE](LICENSE) を参照してください。

サードパーティ製コンポーネントは原著者の著作権を保持します
（Steph Ango、Axton Liu、AllanYiin / 尹相志、Anthropic）。
上流 URL、ライセンス、変更内容を含む完全な attribution は
[ATTRIBUTION.md](ATTRIBUTION.md) を参照してください。

ライセンスや attribution に関する問題は
https://github.com/kouko/monkey-skills/issues に issue を立ててください。
