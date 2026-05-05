# assumption-surface

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 任意のテキストから隠れた前提を抽出し、議論が実際に依拠しているのはどれかを格付けする。

Atomic skill。`artifact-deconstruct` がフル 6-lens × 6 観点を、
`argument-deconstruct` がフル Toulmin + Burke を回すのに対し、
`assumption-surface` は単一の deliverable に絞る：**隠れた前提の表**。
フル脱構築より速く、memo / proposal / 主張に基づき行動するか判断する
前のストレステストとして設計されている。

## いつ使うか

トリガーフレーズ（言語不問）。EN・JP・ZH-TW を混ぜて OK：

- "find the hidden assumptions", "what is this *assuming*"
- "stress-test these claims before deciding", "surface the implicit world-model"
- 「揭露這份備忘錄的隱性假設」「這個策略在假設什麼」
- 「隠れた前提を出して」「この主張は何を前提にしている」

スキップする場合：

- 対象テキストが 100 語未満 — 浮上させる surface が足りない
- 仕上げられた argument-map deliverable が欲しい — これは検査表であり deliverable ではない

姉妹 skill を使うべき場合：

- 制作物のフル design teardown が必要 → `artifact-deconstruct`
- Toulmin warrant（論証根拠）の梯子を明示する議論構造分析 → `argument-deconstruct`
- 外部テキストではなく**自分自身**の前提を疑う → `philosophers-toolkit:descartes-methodical-doubt`
- コード → `sourceatlas`

## 方法

4 つの動き、レイヤー化されたスタックとして適用：

### 1. 逆 Toulmin

Toulmin の claim-grounds-warrant モデルを**逆向き**に走らせる：
テキストの主張から出発し、grounds が claim を支持するために著者が
信じていなければならない warrant に向かって遡る。暗黙の中核的信念
を浮上させる。[`protocols/reverse-toulmin.md`](protocols/reverse-toulmin.md) 参照。

### 2. 症候的読解（Althusser 影響下）

[`references/lens-symptomatic-reading.md`](references/lens-symptomatic-reading.md) に基づく —
テキストが**語っていない**ことを読む。不在は欠落ではなく、著者が
言うまでもないと考えた、または言うのが危険すぎると考えたものに
ついての構造的データである。Althusser & Balibar『資本論を読む』
（*Lire le Capital*, Maspero 1965; 1968 簡約版; Brewster 訳 NLB 1970）
より借用。

### 3. 反事実プローブ

浮上させた各前提について問う：「この前提が偽だったら、議論は
どう見えるか？」議論が崩壊するなら、その前提は**基盤的**。
変形した形で残るなら、**中核的だが基盤的ではない**。変わらなければ
**装飾的**。

### 4. フレーム審査

テキストが操作している概念フレームは何か？（Goffman / Lakoff の
意味で。）フレームを命名することで、フレーミング自体に焼き込まれた
前提が浮上する。

## 3 段階の強度分類

浮上させたすべての前提に 3 つの強度評価のいずれかを付ける：

| 段階 | 意味 | 取るべき行動 |
|---|---|---|
| **基盤的** | 偽なら議論が完全に崩壊 | falsifiability test 必須 |
| **中核的** | 偽なら議論は大幅な再フレーミングが必要 | falsifiability test 推奨 |
| **装飾的** | 偽でも議論は変わらず存続 | 記録のみ、先へ進む |

## 反証可能性テスト（基盤的段階）

すべての基盤的前提について、それを**偽証しうる**テストを設計する。
そのようなテストが存在しなければ、その前提は反証不可能 — それ自体
が浮上させる価値のある発見である。Popper に従えば、反証不可能な
前提からは議論できず、信じることしかできない。反証不可能な基盤的
前提は最も危険な種類であり、レポート内で明示的にフラグを立てなければ
ならない。

## 何が得られるか（output）

- **Source claims** — テキストが行うすべての distinct な主張の番号付きリスト
- **Assumption table**（5–15 行）— assumption | source claim(s) | 強度段階 | falsifiability test（基盤的のみ）
- **挑戦に値する基盤的前提** — 各基盤的行に対する反問
- **Bottom line** — 一文で：制作物は N 個の基盤的前提に依拠し、そのうち K 個が反証不可能；最も争いうるのは X

5–15 行が sweet spot。30+ は通常、主張を前提として列挙していること
を意味する。

## Worked example

同梱の sample fixture：

- [`assets/sample-company-strategy-memo.md`](assets/sample-company-strategy-memo.md)
- [`assets/sample-tweet-thread-productivity.md`](assets/sample-tweet-thread-productivity.md)

Eval ground-truth（must-find リスト）：

- `eval/cases/assumption-surface-01-strategy-memo.yaml`
- `eval/cases/assumption-surface-02-tweet-thread.yaml`

## See also

- [`SKILL.md`](SKILL.md) — フル正典（workflow、output template、anti-patterns）
- [`references/lens-symptomatic-reading.md`](references/lens-symptomatic-reading.md) — Althusser & Balibar source
- [`protocols/reverse-toulmin.md`](protocols/reverse-toulmin.md) — backward-Toulmin 法
- 姉妹 skill：[`artifact-deconstruct`](../artifact-deconstruct/)（フル 6-lens）| [`argument-deconstruct`](../argument-deconstruct/)（フル Toulmin）
- Plugin 全体像：[`../../README.md`](../../README.md)
