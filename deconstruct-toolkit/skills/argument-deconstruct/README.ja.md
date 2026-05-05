# argument-deconstruct

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 長文の議論を深掘りする — 隠れた warrant（論証根拠）を表に出し、見落とされた rebuttal を名指し、動機の ratio を暴く。

議論に特化した深掘り skill。`artifact-deconstruct` がどんな制作物に対しても 6 lens × 6 次元のフル treatment を走らせるのに対し、`argument-deconstruct` は単一 artifact-class — 長文の議論 — に絞り込み、Toulmin + Burke をより高解像度で適用する。中核となる動作：**隠れた warrant を表に出す**。

## 使用タイミング

トリガーフレーズ（言語不問）：

- 「拆解這個論證」「這份提案論證哪裡弱」「找隱性 warrant」
- 「論証を脱構築して」「この社説の隠れた前提は？」
- "deconstruct this argument" / "find the warrant" / "where does this argument fail"
- "is this argument valid" / "what's the hidden assumption in this claim"

スキップすべきとき：

- 対象に議論的な背骨がない（記述的 / 物語的 / リファレンス文書） → `artifact-deconstruct` を使う
- 対象が 200 語未満 — 脱構築するには薄すぎる
- 対象がコード — `sourceatlas` を使う

兄弟 skill を代わりに使うべきとき：

- マルチ lens treatment（rhetoric + persuasion + frame + genre + UX + semiotic）→ [`artifact-deconstruct`](../artifact-deconstruct/)
- フル Toulmin treatment 不要のアトミックな前提抽出 → [`assumption-surface`](../assumption-surface/)

## 方法（artifact-deconstruct の lens-rhetoric との差分）

`artifact-deconstruct/references/lens-rhetoric-anglo.md` は Burke pentad + Toulmin を survey 解像度で 1 つの lens に統合する。`argument-deconstruct` はそれらを意図的に **分割** する — それぞれをより充実した treatment にしたものが [`references/lens-toulmin.md`](references/lens-toulmin.md) と [`references/lens-burke-pentad.md`](references/lens-burke-pentad.md)。ADR-0002 のとおり、この synthesis 分割は意図的：同じ primary source、異なる operationalization 深度。

### Toulmin model（6 構成要素のフル）

| 構成要素 | 問い |
|---|---|
| **Claim**（主張） | 結論は何か？ |
| **Grounds**（根拠） | それを支える証拠は何か？ |
| **Warrant** ⭐ | 根拠から主張に渡る暗黙の橋は何か？ |
| **Backing** | warrant を裏付ける権威は何か？ |
| **Rebuttal**（反駁） | どんな反論を受け入れているか？ |
| **Qualifier**（限定詞） | どんな条件で主張は成立するか？ |

warrant が **焦点となる動作**。多くの議論は warrant を隠している。議論を脱構築するということは、warrant を声に出して述べ、合理的な反対者がそれを受け入れるかを試すこと。

### 隠れた warrant の 8 パターン（カタログ化済）

warrant をうまく言語化できないとき、[`references/lens-toulmin.md`](references/lens-toulmin.md) の以下のパターンを確認する：

| パターン | こんな響き |
|---|---|
| 権威への訴え | 「X が言ったから真」 |
| 多数派への訴え | 「みんなやってるから正しい」 |
| アナロジー | 「あそこで効いたからここでも効く」 |
| トレンド外挿 | 「過去のトレンドが未来を予測する」 |
| 相関からの因果 | 「X 採用者は Y もやる、だから X が Y を引き起こす」 |
| 損失回避 | 「やらないと失う」 |
| 第一原理主張 | 「基本原理から X が導かれる」 |
| 自明性 | 「明らかに…」 |

### Burke pentad の ratio

5 要素（act / 行為、scene / 場、agent / 行為者、agency / 手段、purpose / 目的）に加えて **ratio** 分析：どの 2 要素が支配的かが動機構造を明らかにする。

| Ratio | 意味 |
|---|---|
| Scene-Act | 状況が行動を強いる |
| Agent-Act | 自分が何者かが行動を決める |
| Agent-Agency | アイデンティティが手段を決める |
| Act-Purpose | 行動それ自体が目的 |
| Agency-Purpose | 手段が目的を決める |
| Scene-Agent | 場が誰になるかを決める |

**主張された** ratio と **実際の** ratio の食い違いを表に出す — そのギャップこそが動機ロンダリングの居場所。

## 出力（得られるもの）

- **議論マップ**（mermaid 形式：claim / grounds / warrant / backing / rebuttal / qualifier を可視化、隠れた warrant は dotted edge で強調）
- **Warrant の明示化** — 暗黙の warrant をすべて「なぜなら…」で始まる完全な文として記述
- **欠落 rebuttal テーブル** — 著者が無視 / 先回り回避した反論
- **Burke pentad ratio 分析** — 主張 ratio vs 実際 ratio と動機解釈
- **倫理ポジション**（検出された説得メカニズムに対して 🟢/🟡/🔴/⚫）

## 実例

[`eval/cases/argument-deconstruct-01-op-ed.yaml`](../../eval/cases/argument-deconstruct-01-op-ed.yaml) と [`eval/cases/argument-deconstruct-02-vc-pitch.yaml`](../../eval/cases/argument-deconstruct-02-vc-pitch.yaml) に must_find の正解データあり。

## 関連

- [`SKILL.md`](SKILL.md) — フル canon
- [`references/lens-toulmin.md`](references/lens-toulmin.md) — フル Toulmin treatment（Toulmin 1958, Ch 3）
- [`references/lens-burke-pentad.md`](references/lens-burke-pentad.md) — フル Burke treatment（Burke 1945, Introduction）
- 兄弟 skill：[`artifact-deconstruct`](../artifact-deconstruct/) | [`assumption-surface`](../assumption-surface/)
- Plugin 概要：[`../../README.md`](../../README.md)
