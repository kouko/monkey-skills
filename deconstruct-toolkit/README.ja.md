# deconstruct-toolkit

> 制作物（コピー、ドキュメントパック、UI、論証、製品、組織）を逆向きに分解し、設計判断、借用フレームワーク、修辞メカニズム、意図的な省略を可視化するツールキット。

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**: 0.1.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT

## 背景

`sourceatlas` がコードを逆向きに、`philosophers-toolkit` が自分の思考を整理するのに対し、**`deconstruct-toolkit` は外部の精緻な非コード制作物を脱構築する** — マーケティングコピー、ドキュメントパック、UI フロー、長文論証、製品戦略、組織アーティファクト。目的は要約ではなく、**design archaeology（設計考古学）** — 制作者が何を決めたか、どのフレームワークを借用したか、何を意図的に省略したかを掘り起こすこと。

ツールキットは 3 つの知的伝統を統合する：

- **大陸哲学 + 批評** — Derrida（脱構築）、Barthes（5 codes / S/Z）、Goffman + Lakoff（フレーム分析）。二項対立、暗号、暗黙のフレーミングを露出する手法。
- **英米修辞学 + UX** — Burke（劇的五要素）、Toulmin（議論モデル）、Bhatia/Swales（ジャンル move 分析）、Nielsen-Norman（UX ヒューリスティック）。主張、warrant、デザインアフォーダンスを浮上させる手法。
- **行動説得科学** — Cialdini（影響力の 7 原則）、Brignull（12 ダークパターン / 欺瞞的デザイン）。説得メカニズムを検出し倫理的位置づけを行う手法。

日本語圏の読者に対しては、**BCG「バリュー・チェーンの脱構築」**（Evans & Wurster『Blown to Bits』2000）と **山口周『武器になる哲学』**（2018）の系譜にも紐付ける — 日本では「脱構築」は哲学の借用語ではなく、ビジネス戦略用語として定着している。本 plugin はその実務的射程を agent skill として実装する。

## 境界

本 plugin は**非コード制作物専用**。以下の場合は別ツールを使用：

| 用途 | 使うべきもの |
|---|---|
| コードベースの逆向き解析 | [`sourceatlas`](https://github.com/kouko/monkey-skills/tree/main/sourceatlas)（impact / flow / overview / pattern / deps）|
| 自己思考 / 問題明確化 | [`philosophers-toolkit`](https://github.com/kouko/monkey-skills/tree/main/philosophers-toolkit) — `自分 vs 自分の問題` を扱う |
| 開発成果物の批評（提案 / コミット / skill）| [`dev-workflow`](https://github.com/kouko/monkey-skills/tree/main/dev-workflow)（proposal-critique / complexity-critique / skill-judge）|
| 順方向のコピー / ドキュメント / デザイン**生産** | [`copywriting-toolkit`](https://github.com/kouko/monkey-skills/tree/main/copywriting-toolkit), [`docs-team`](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/docs-team), [`design-team`](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/design-team) |
| 投資 / 株式の逆向き解析 | [`investing-toolkit`](https://github.com/kouko/monkey-skills/tree/main/investing-toolkit) |

「deconstruct」「teardown」「reverse engineering」の 3 用語は混用しない：

| 用語 | 領域 | 意味の核 |
|---|---|---|
| **Reverse engineering**（リバースエンジニアリング）| 工学 / ハードウェア / コード | 分解して**複製する** |
| **Teardown** | 製品 / 消費者向けアプリ / ハードウェア | 分解して**戦略を理解する** |
| **Deconstruct**（脱構築）| 哲学 / デザイン批評 / BCG 戦略 | **隠れた構造と対立を露出する** |

本 plugin は 3 つ目のカテゴリ。

## インストール

本 plugin は `monkey-skills` marketplace に存在：

```bash
# Claude Code 内で
/plugin marketplace add kouko/monkey-skills
/plugin install deconstruct-toolkit
```

## 使い方

skill が決まっている場合は直接：

```
/deconstruct-toolkit:artifact-deconstruct
/deconstruct-toolkit:argument-deconstruct
/deconstruct-toolkit:assumption-surface
```

迷ったら router へ：

```
/deconstruct-toolkit:using-deconstruct-toolkit
```

router は一つだけ質問する — 「何の制作物を、何を浮上させたいか」 — そして適切な skill と lens の組み合わせに案内する。

## Skills（v0.1.0）

### 旗艦

#### `artifact-deconstruct`

| 項目 | 内容 |
|-------|-------|
| 対象 | あらゆる精緻な制作物（コピー / ドキュメントパック / UI / playbook / SOP / 広告 / 文学）|
| 手法 | 6-lens ライブラリ × 6 次元分析 × 倫理的位置づけ |
| Lens | semiotic (Barthes) · rhetoric (Burke + Toulmin) · frame (Goffman + Lakoff) · genre (Swales/Bhatia) · ux (Nielsen-Norman) · persuasion (Cialdini + Brignull) |
| 出力 | 6 セクション脱構築レポート：表層観察 → 設計判断 → 借用フレームワーク → 修辞メカニズム（倫理的位置づけ付き）→ 転用可能な学び → 弱点 |
| 使う場面 |「これを脱構築」「なぜこのコピーは効くのか」「この設計の裏側」 |
| コマンド | `/deconstruct-toolkit:artifact-deconstruct` |

### 論証専用

#### `argument-deconstruct`

| 項目 | 内容 |
|-------|-------|
| 対象 | 長文論証、社説、提案書、政治テキスト、論文 introduction |
| 手法 | Toulmin モデル（claim / grounds / warrant / backing / rebuttal / qualifier）+ Burke 五要素比 + ジャンル move 分析 |
| 中核動作 | 隠れた warrant を浮上させる — 多くの論証は warrant を隠す |
| 出力 | 議論マップ (mermaid) + warrant 明示化 + 欠如反駁テーブル + 倫理的位置づけ |
| 使う場面 |「この社説の論証を脱構築」「この提案のどこが弱いか」 |
| コマンド | `/deconstruct-toolkit:argument-deconstruct` |

### 原子的

#### `assumption-surface`

| 項目 | 内容 |
|-------|-------|
| 対象 | 隠れた前提を疑うあらゆるテキスト（戦略メモ、SNS スレッド、政策ブリーフ） |
| 手法 | 逆 Toulmin · 症候的読解（Althusser 風「不在を読む」）· 反実仮想プローブ · フレーム監査 |
| 出力 | 前提テーブル（5–15 行）+ 強度評価（基礎 / 支柱 / 装飾）+ 基礎前提ごとの反証可能性チェック |
| 使う場面 |「このメモの隠れた前提を露出」「この主張は何を *仮定* しているか」 |
| コマンド | `/deconstruct-toolkit:assumption-surface` |

### Router

#### `using-deconstruct-toolkit`

| 項目 | 内容 |
|-------|-------|
| skill | ユーザの意図を兄弟 skill に振り分ける |
| 手法 | 1 質問 → 制作物タイプ検出 → lens 事前選択 → 振り分け |
| 使う場面 | 何かを脱構築したいが、どの skill / lens を使うか分からない |
| コマンド | `/deconstruct-toolkit:using-deconstruct-toolkit` |

## 設計原則

ツールキット全 skill を貫く原則：

**Design archaeology であって summary ではない。** 各 skill は「何が*決められた*か」を露出する — 「何が*書かれた*か」ではない。書く順番と読む順番の差分が設計であり、それが回収対象。

**lens 群であって pipeline ではない。** 各制作物には**タイプに応じた lens 組み合わせ**を選ぶ。6-lens ライブラリは選択式であり順次実行ではない。LP は persuasion + rhetoric、playbook は genre + 6 次元、UI は ux + persuasion。

**ネガティブスペースが重要。** *意図的に省略された* もの（欠如した反駁、不在の move、語られていない前提）はデータであり、欠落ではない。全 skill にネガティブスペース・パスを含む。

**倫理的位置づけは必須。** persuasion または UX lens を適用する場合、検出した全メカニズムに 4 つの位置づけのいずれか必須：🟢 透明 · 🟡 グレーゾーン · 🔴 操作 · ⚫ ダークパターン。中立的記述は許可されない。

**Primary-source 忠実。** 各 lens は版・章・ページまで明示した原典引用を lens reference ファイル冒頭に置く。skill ごとに operationalization が異なってもよい — ただし全て同じ primary source に忠実であること。[ADR-0002](docs/adr/0002-strict-skill-self-containment.md) 参照。

**Skill 独立性。** Anthropic 公式 skill convention に従い、各 skill は完全に自己完結する。lens 内容が skill 間で重複してもよい — 意図的な重複である。[ADR-0002](docs/adr/0002-strict-skill-self-containment.md) 参照。

## ロードマップ

[docs/design-proposal.md](docs/design-proposal.md) §8 に v0.1 → v1.0 の道筋。

| バージョン | 追加内容 |
|---|---|
| **v0.1.0**（本リリース）| router + artifact-deconstruct + argument-deconstruct + assumption-surface |
| v0.2.0 | `product-deconstruct`, `pricing-decode`（ビジネス領域への拡張）|
| v0.3.0 | `frame-reveal`, `bias-audit`, `decision-archaeology`（原子的深化）|
| v1.0.0 | 20+ 実世界 eval ケース、fixture corpus、日本実例研究、OSS リリース |

## コントリビュート

歓迎。新 skill 提案は先に Issue を開いてください。本 plugin の各新 skill は 2 つのメンバーシップ gate を通過する必要あり（[ADR-0001](docs/adr/0001-convention-b-mixed-naming.md) 参照）：

1. **動詞 gate** — skill 動詞は脱構築ファミリ（`deconstruct / surface / reveal / audit / decode / expose / archaeology`）に属する
2. **対象 gate** — skill 対象は外部の精緻な非コード制作物

PR は [Conventional Commits](https://www.conventionalcommits.org/) に従う。

## ライセンス

MIT — repository root の [LICENSE](../LICENSE) を参照。
