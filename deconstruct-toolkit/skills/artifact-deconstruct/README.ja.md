# artifact-deconstruct

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 非コードの制作物の背後にある設計ブループリントを復元する — 何が決定され、何が借用され、何が意図的に語られなかったか。

`deconstruct-toolkit` の主力 skill。外部の非コード制作物（コピー / ドキュメントパック / SOP / playbook / プレゼン / UI スクリーンショット / 広告 / 文学）の設計ブループリントをリバースエンジニアリングする。目標は **設計考古学** — 制作者が下した決定、借用した framework、そして意図的に省いた要素を復元することにある。

## いつ使うか

トリガーフレーズ（任意の言語）：

- EN: "deconstruct this", "reverse engineer", "design behind this", "teardown", "why does this work"
- JP: 「この制作物を脱構築して」「なぜこれはこんなに刺さるのか」「設計を逆引きして」
- ZH-TW: 「拆解這份」「反推這個」「為什麼這份寫得這麼好」「這份是怎麼設計的」

スキップする場合：

- ユーザーが **要約** を求めているとき — 通常の読解で対応
- 制作物が 200 語未満で構造化された論証でない場合 — 復元すべき設計が不足
- 対象が純粋に情報的な reference（Wikipedia、辞書、生データ）
- 対象が source code → `sourceatlas` を使う
- 対象がユーザー自身の思考 → `philosophers-toolkit` を使う

## 仕組み（6 ステップ）

1. **type 検出** — marketing / playbook / SOP / deck / UI / article / speech / literature / UI screen
2. **lens 選択** — 6 lens ライブラリから 1〜3 個（決定木は [`protocols/lens-selection.md`](protocols/lens-selection.md)）
3. **6 観点（dimensions）の実行** — lens 選択に関わらず常時稼働するバックボーン
4. **lens の適用** — 4 つの文化感受性 lens について [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md) で variant を解決
5. **report 生成** — 倫理ポジション判定付きの 6 セクション脱構築
6. **self-check** — 納品前に [`checklists/anti-patterns.md`](checklists/anti-patterns.md) を実行

instruction 本体は [`SKILL.md`](SKILL.md)。

## lens ライブラリ

選択可能な組み合わせで適用される 6 lens（**6 つ全部**ではない — それは判断停止のサイン）：

| Lens | 出典 | 文化 variant |
|---|---|---|
| `lens-semiotic` | Barthes 1970 (S/Z, 5 codes) | （なし — v0.2.0 時点では Anglo grounded のみ） |
| `lens-rhetoric` ✱ | Burke 1945 + Toulmin 1958 (anglo) · Hinds 1983/1987 + Oh 2025 起承転結 (ja) · 劉勰《文心雕龍》六観 (zh) | -anglo / -ja / -zh |
| `lens-frame` ✱ | Goffman 1974 + Lakoff 1980 (anglo) · + Doi 1971 / Yamamoto 1977 / Markus & Kitayama 1991 (ja) · + Hu 1944 / Hwang 1987 / Peng & Nisbett 1999 (zh) | -anglo / -ja / -zh |
| `lens-genre` ✱ | Swales 1990 + Bhatia 1993 (anglo) · + 木下 1981 + Hinds 1987 (ja) · + 行政院公文程式條例 (zh) | -anglo / -ja / -zh |
| `lens-ux` | Nielsen 1994/2020 + Norman 1988/2013 | （なし） |
| `lens-persuasion` ✱ | Cialdini 2021 + Brignull 2024 (anglo) · + Doi 1971 + 異文化実証研究 (ja) · + Hwang 1987 面子/關係/人情 (zh) | -anglo / -ja / -zh |

（✱ = 言語 variant ルーティング対象；適用前に [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md) で variant を解決すること）

## 6 観点バックボーン

どの lens を組み合わせても、すべての制作物には 6 観点すべてが適用される：

1. **読み手ルーティング** — 誰がいつ何を読むか？
2. **生成シーケンス** — 読まれる順序 vs おそらく書かれた順序
3. **出典系譜** — どの既存 framework が借用されたか？
4. **修辞構造** — どう説得するか？
5. **設計パターン** — 反復するテクニックは何か？
6. **ネガティブ・スペース** — 何が意図的に省かれているか？

ネガティブ・スペース観点は必須 — 制作物が **語っていないこと** はギャップではなくデータである。

## 出力（フォーマット）

6 セクションの脱構築 report（template は [`assets/report-template.md`](assets/report-template.md)）：

```
1. 表層観察           (見えるもの)
2. 設計上の決定       (読み手 / シーケンス / 修辞)
3. 借用された framework (系譜)
4. 修辞メカニズム     (倫理ポジション 🟢/🟡/🔴/⚫ 付き)
5. 再現可能な学び     (具体的な takeaway 5 点)
6. 弱点 / 警告        (欠落した手 / 怪しい warrant / ダークパターンのリスク)
```

最後に 1 行の **bottom-line verdict** を添える。

検出された各説得メカニズムまたは UX メカニズムには、4 つの倫理ポジションのいずれかが付与される：

| ポジション | 意味 |
|---|---|
| 🟢 透明 | 原理を使用、ユーザーは認識し拒否できる |
| 🟡 グレーゾーン | 原理を使用、ユーザーは無自覚 |
| 🔴 操作 | 緊急感や誤った信念を作り出す |
| ⚫ ダークパターン | 能動的に欺瞞しユーザーを害する |

中立的な記述は許可されない。

## 文化 variant ルーティング（v0.2.0+）

文化感受性のある 4 lens（rhetoric / persuasion / genre / frame）について、variant は **制作物のレジスター** で選択され、著者やブランドの origin では選択されない。Toyota の英語 LP には `-ja`（日本ブランド）ではなく `-anglo`（英語制作物）を適用する。アルゴリズムは [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md)。

出力 report は適用された variant を MUST 明示する：

> "Applied lens-rhetoric-ja (kishōtenketsu mode, op-ed register) to artifact at [URL] in Japanese."

これによって分析は監査可能になる — variant 選択に異論のある読者は別 variant で再実行できる。

## worked example

Anglo:

- [`assets/sample-dropbox-landing-2024.md`](assets/sample-dropbox-landing-2024.md) — 2026-05-05 に実際 fetch した Dropbox LP（must-find ground truth は plugin root の `eval/cases/artifact-deconstruct-01-dropbox-landing.yaml`）
- [`assets/sample-notion-onboarding-pack.md`](assets/sample-notion-onboarding-pack.md)
- [`assets/sample-stripe-signup-flow.md`](assets/sample-stripe-signup-flow.md)

文化 variant fixture（JP + ZH 計 8 件）：

- JP: `sample-ja-op-ed.md` · `sample-ja-ec-lp.md` · `sample-ja-business-letter.md` · `sample-ja-political-speech.md`
- ZH: `sample-zh-op-ed.md` · `sample-zh-ec-lp.md` · `sample-zh-gongwen.md` · `sample-zh-political-speech.md`

11 ケース全件に対応する `must_find` ground-truth spec が plugin root の `eval/cases/` にある。

## この skill を使わないとき

- 論証中心の深掘り → `argument-deconstruct`（Toulmin + Burke pentad、隠れ warrant フォーカス）
- 単発の隠れ前提の表面化 → `assumption-surface`（reverse-Toulmin + Althusser symptomatic reading）
- code のリバースエンジニアリング → `sourceatlas`
- 自己思考 → `philosophers-toolkit`
- 200 語未満かつ構造化された論証でない — 設計が不足

## 関連項目

- [`SKILL.md`](SKILL.md) — full canon（本 README は GitHub ブラウザ向けフロント、SKILL.md は LLM 向け instruction 本体）
- [`protocols/six-dimensions.md`](protocols/six-dimensions.md)
- [`protocols/lens-selection.md`](protocols/lens-selection.md)
- [`protocols/lens-variant-selection.md`](protocols/lens-variant-selection.md)
- [`checklists/anti-patterns.md`](checklists/anti-patterns.md)
- plugin overview: [`../../README.md`](../../README.md)
