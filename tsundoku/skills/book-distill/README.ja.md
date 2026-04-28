# book-distill

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 1 冊の本（[`book-extract`](../book-extract) によって章ごとに分割された
> Markdown 済み）を **RIA-TV++ pipeline** で実行可能な agent skill 群へと
> 蒸留する。

[tsundoku](../..) plugin の一部。Claude が実際に load する skill spec は
[`SKILL.md`](SKILL.md)。この README は人間向け。

> **ステータス（v0.9.0）**：pipeline 構造 + 出典に基づく三言語 glossary
> （EN / 日本語 / 繁體中文）。canonical な公式出版訳語を採用。
> 出典は `ATTRIBUTION.md` に記載。

## 何をする / 何をしない

- ✅ **蒸留**：方法論 / 意思決定 framework / checklist / 原則 / 概念体系 →
  atomic で再利用可能な agent skill
- ❌ **対象外**：本の要約 / 書評 / 著者ペルソナでのロールプレイ

## RIA-TV++ pipeline

```
Stage 0:    Adler analytical read           → BOOK_OVERVIEW.md
Stage 1:    5 つの parallel sub-agent extractor → candidates/
            （framework / principle / case / counter-example / glossary）
Stage 1.5:  Triple verification filter       → verified.md（30-50% が通過）
            V1 cross-domain / V2 predictive / V3 exclusivity
Stage 2:    RIA++ skill render               → <skill-slug>/SKILL.md
            R / I / A1 / A2 / E / B 6 フィールド
Stage 3:    Zettelkasten linking              → INDEX.md + cross-refs
Stage 4:    Adversarial pressure test         → test-prompts.json
```

蒸留そのものは **Claude-driven** — skill spec が Claude に各 stage で
sub-agent を spawn せよと指示する。一枚岩の Python orchestrator は無く、
唯一の shell script `book_distill_init.sh` は作業ディレクトリを
bootstrap するだけ。

## 前提条件

原典は事前に [`book-extract`](../book-extract) で処理されていること：

```bash
ls ~/.tsundoku/cache/markdown/<book-slug>-<id8>/
# 期待されるファイル：index.md / metadata.json / NN-chapter.md
```

これらが無い場合 `book_distill_init.sh` は中断し、`book-extract` へ
誘導する。

## Quick start

```bash
# 1. 抽出済み markdown から作業ディレクトリを bootstrap
bash scripts/book_distill_init.sh 一九八四-b9152ffe

# 出力：~/.tsundoku/cache/distilled/一九八四-b9152ffe/
#   ├── BOOK_OVERVIEW.md.draft
#   ├── metadata.snapshot.json
#   ├── chapters.list
#   ├── candidates/
#   ├── rejected/
#   └── .book-distill-state

# 2. その後、Claude にこの skill の SKILL.md を Stage 0 から実行させる。
#    Claude は章を読み、BOOK_OVERVIEW.md を埋め、5 つの parallel
#    extractor を spawn し、triple verification を回す、等々。
```

## 起動するタイミング

ユーザーが次のように言ったとき：
- "Distill *Poor Charlie's Almanack* into skills"
- 「把《思考的快與慢》蒸餾成 skill」
- 「この本の方法論を skill にして」

## 出力構造

```
~/.tsundoku/cache/distilled/<book-slug>/
├── BOOK_OVERVIEW.md            # Stage 0 — thesis / 骨格 / glossary / critique
├── INDEX.md                    # Stage 3 — skill 一覧 + 参照グラフ
├── candidates/                 # Stage 1 生候補プール（audit trail）
│   ├── frameworks.md
│   ├── principles.md
│   ├── cases.md
│   ├── counter-examples.md
│   └── glossary.md
├── rejected/                   # Stage 1.5 で除外した候補と理由（audit trail）
├── verified.md                 # Stage 1.5 残存組
└── <skill-slug-N>/             # 出荷 skill ごとに 1 ディレクトリ
    ├── SKILL.md                # RIA++ render：R / I / A1 / A2 / E / B
    └── test-prompts.json       # Stage 4 テストケース（≥3 trigger + ≥2 lure + ≥1 edge）
```

## Per-skill schema（RIA++ 6 フィールド）

| フィールド | 内容 |
|---|---|
| **R** Reading | 原典 verbatim 引用 ≤150 字 + 章 citation |
| **I** Interpretation | 自分の言葉で書く方法論の骨格、5-15 行 |
| **A1** Past Application | 著者が本文で記録した本方法論の事例 |
| **A2** Future Trigger ★ | ユーザーがこれを必要とする状況。frontmatter `description` になる |
| **E** Execution | 番号付き runtime 手順 + 完了基準 |
| **B** Boundary | 適用すべきでない状況。counter-example + critique を出典とする |

## 出力言語ルール

この skill は言語自動適応：

- **R 引用**：原典言語で VERBATIM。決して翻訳しない
- **I / A / E / B 本文**：原典の言語に揃える
- **YAML フィールド名 + slug**：英語（機械識別子）
- **frontmatter `description`**：原典言語（ユーザー query の trigger
  マッチングが自然になる）
- **Audit metadata**：英語

## このフォルダのファイル

| Path | 役割 |
|---|---|
| [`SKILL.md`](SKILL.md) | Claude が load するトップレベル orchestrator（約 270 行） |
| [`ATTRIBUTION.md`](ATTRIBUTION.md) | upstream credits（cangjie-skill、nuwa-skill、Adler、RIA、Zettelkasten）+ license |
| [`methodology/`](methodology) | 7 ファイル：設計思想 + 各 stage の詳細 |
| [`extractors/`](extractors) | 5 つの sub-agent prompt（framework / principle / case / counter-example / glossary） |
| [`templates/`](templates) | BOOK_OVERVIEW / SKILL / INDEX / test-prompts |
| [`scripts/book_distill_init.sh`](scripts/book_distill_init.sh) | `book-extract` 出力から作業ディレクトリを bootstrap |

## 系譜

[`kangarooking/cangjie-skill`](https://github.com/kangarooking/cangjie-skill)
（蒼頡-skill、MIT）から派生。完全な credits と upstream → tsundoku 変更点
リストは [`ATTRIBUTION.md`](ATTRIBUTION.md) を参照。

全体アーキは cangjie-skill 由来。tsundoku が加えた点：
1. 英語 canonical の指示文 + 出力言語の自動適応ルール
2. **三言語 glossary**（EN / 日本語 / 繁體中文）に canonical な公式出版訳語を採用
3. tsundoku 専用エントリ hook（`book_distill_init.sh`）により upstream 最大の
   摩擦点（「ユーザーが本と metadata を自分で用意する必要」）が消える

## なぜ "book-*" で "kobo-*" ではないのか

この skill は **format-agnostic**：入手元に関わらず、任意の章分割 Markdown を
入力として消費する。将来の `paper-distill`（学術論文）や `transcript-distill`
（podcast 書き起こし）も `book-*` / 処理層に加わる。`kobo-auth` と
`kobo-library` だけが Kobo プラットフォームに紐づく。

## 既知の制限

- **カバレッジの保証なし** — 蒸留が本書の最重要 framework を取りこぼす可能性
  がある。Roadmap：TOC reconstruction test（蒸留した skill だけで新規 agent が
  章立てを再構築できるか？）。

- **CJK 忠実度ベンチマーク無し** — 226 冊の zh-TW / 7 冊の ja のテスト library
  に対する定量検証は roadmap 項目。

- **自動 regression 無し** — `test-prompts.json` は darwin-skill 形式と互換だが
  実行する orchestrator は今のところ無く、将来の evolution skill か手動実行に
  委ねられている。

## 関連

- [`book-extract`](../book-extract) — この skill が消費する章分割 Markdown を
  生み出す
- [`tsundoku` README](../..) — pipeline 全体像
- [Cangjie 設計思想](https://github.com/kangarooking/cangjie-skill)
- [Nuwa Skill](https://github.com/alchaincyf/nuwa-skill) — 兄弟版 persona
  蒸留（スコープは違うが同じ Triple Verification primitive を採用）
