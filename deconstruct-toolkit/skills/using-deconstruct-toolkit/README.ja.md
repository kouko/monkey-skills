# using-deconstruct-toolkit

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 目の前の制作物に対して、適切な脱構築 skill と lens combination を選び出す。

router です。ユーザーが持ち込んだものと、明らかにしたい内容に応じて、
適切な脱構築 skill（`artifact-deconstruct` / `argument-deconstruct` /
`assumption-surface`）と適切な lens combination を選びます。
どの sibling skill を使うべきかまだ分からない場合に、この skill を使ってください。

## いつ使うか

トリガーフレーズ（任意の言語）：

- 「help me deconstruct this」/「拆解這份」/「脱構築したい」
- 「このコピー / ページ / playbook の裏側にある設計は何か」
- 「この argument は実際に何を主張しているのか」
- 「隠された前提を見つけて」/「この主張を stress-test して」
- 「制作物はあるが、どの skill を使えばいいか分からない」

スキップする場面：

- ユーザーがすでに sibling skill を指定済み（例：`/deconstruct-toolkit:artifact-deconstruct`）— その skill を直接 invoke
- 対象がソースコードまたは build artifact — `sourceatlas` を使う
- ユーザーが自分自身の問題について考えたい — `philosophers-toolkit` を使う
- ユーザーが新しいコピー / ドキュメント / デザインを **生み出したい** — `copywriting-toolkit` / `docs-team` / `design-team` / `slides-toolkit` を使う

## まず境界チェック

この toolkit に router を通す前に、誤って向けられたリクエストを
リダイレクトするため、3 つの境界チェックを実行します：

| 質問 | yes ならリダイレクト先 |
|---|---|
| 対象はソースコードか？ | `sourceatlas`（impact / flow / overview / pattern / deps） |
| 自己思考（外部の制作物ではなく自分の問題）か？ | `philosophers-toolkit` |
| 前向きの制作（新しいコピー / ドキュメント / デザインを書く）か？ | `copywriting-toolkit` / `docs-team` / `design-team` / `slides-toolkit` |

3 つすべてが「no」になって初めて routing が進みます。

## 二軸 routing

### 軸 1 — 制作物タイプ

| 制作物 | デフォルト skill | デフォルト lens combo |
|---|---|---|
| マーケティングコピー / LP / 広告 | `artifact-deconstruct` | persuasion + rhetoric |
| ドキュメントパック / playbook / SOP / オンボーディング | `artifact-deconstruct` | genre + 6-dim full |
| UI / アプリオンボーディング / website screen | `artifact-deconstruct` | ux + persuasion |
| 長文の argument / op-ed / 提案 / 政治的文書 | `argument-deconstruct` | Toulmin + Burke + warrant surface |
| 戦略メモ / 政策 brief / SNS thread（隠された前提を疑う場合）| `assumption-surface` | reverse-Toulmin + symptomatic reading |
| スピーチ / 政治演説 | `artifact-deconstruct` | rhetoric + frame |
| 文学 / 映画 / 広告ビジュアル | `artifact-deconstruct` | semiotic + frame |
| スライドデック / プレゼンテーション | `artifact-deconstruct` | rhetoric + genre |

### 軸 2 — ユーザー意図（軸 1 を上書き）

| ユーザーの言い方 | 上書き先 |
|---|---|
| 「deconstruct the design」/「為什麼這份寫得這麼好」 | `artifact-deconstruct`（full 6-lens × 6-dim） |
| 「find hidden assumptions」/「これは何を *仮定* しているのか」 | `assumption-surface`（atomic、高速）|
| 「find the warrant」/「この argument は妥当か」 | `argument-deconstruct`（Toulmin focus）|
| 「自分は何で操作されているのか」/「ダークパターンを見つけて」 | `artifact-deconstruct` with persuasion + ux |

制作物タイプとユーザー意図が食い違う場合、**ユーザー意図が勝つ**。

## dispatch 前の 3 つのフィルタ

| フィルタ | 意味 |
|---|---|
| 長さ | 200 語未満かつ構造化された argument でない → 設計が十分にない；ユーザーに伝え、dispatch しない |
| 情報専用 | 純粋な reference（Wikipedia / 辞書 / 生データ）→ 復元できる設計がない；ユーザーに伝え、dispatch しない |
| マルチモーダル | 画像中心 + 直接画像を検査できない → ユーザーにテキストの記述を依頼するか、OCR / defuddle で事前抽出 |

## 文化バリアント検出（v0.2.0+）

dispatch する前に、router は次を判定します：

1. **主言語** — 英語 / 日本語 / 中国語（繁体字 vs 簡体字）/ 混成 / その他
2. **文化レジスター** — 学術 / ビジネス / 文学 / 政治 / 消費者向けマーケティング
3. **翻訳由来** — これは翻訳か？

これらの signals は受け取り側の skill に渡され、
`artifact-deconstruct/protocols/lens-variant-selection.md` に従って、
`lens-rhetoric` / `lens-persuasion` / `lens-genre` / `lens-frame` の
正しい文化バリアントに routing できるようにします。

[ADR-0004](../../docs/adr/0004-cultural-lens-variants.md) により、
plugin scope は恒久的に EN / JA / ZH です。
他の言語は **明示的な注意書き付きで** `-anglo` fallback になり、
カバレッジを暗黙に保証するものではありません。

## 出力されるもの

1〜3 文の dispatch：

> 「`artifact-deconstruct` に dispatch します。
> `lens-persuasion + lens-rhetoric` を preselect、language=Japanese、
> register=consumer-marketing → variants `-ja`。今から実行します。」

その後、dispatch された sibling skill が実行されます。

## ルール

- この skill 内で脱構築を実行しない — routing のみ
- lens の中身を説明しない — dispatch された skill に任せる
- skill は 1 つだけ recommend する。複数ではない
- ユーザーがすでに skill を指定している場合、routing をスキップして直接 invoke
- どの skill も合わない場合は、正直にそう伝える — すべての制作物が脱構築に値するわけではない

## 関連項目

- [`SKILL.md`](SKILL.md) — full canon
- 姉妹 skill：[`artifact-deconstruct`](../artifact-deconstruct/) | [`argument-deconstruct`](../argument-deconstruct/) | [`assumption-surface`](../assumption-surface/)
- 文化バリアント routing：[`../artifact-deconstruct/protocols/lens-variant-selection.md`](../artifact-deconstruct/protocols/lens-variant-selection.md)
- Plugin overview：[`../../README.md`](../../README.md)
