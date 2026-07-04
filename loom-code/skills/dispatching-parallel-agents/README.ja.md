# dispatching-parallel-agents

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> **独立した問題ドメインごとにエージェントを 1 体 — 並行して働かせる。** デフォルトは逐次実行。並列 dispatch は、正直な独立性チェック（ファイル素集合・シンボル素集合・データ依存なし）で正当化すべき例外。原型：superpowers v5.1.0 `dispatching-parallel-agents`。loom-code の TDD iron-law + verdict 集約に合わせて改変。

[loom-code](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## このスキルがすること

作業が **2 つ以上の独立した問題ドメイン** — 無関係なテストファイルの修正、無関係なモジュール群の監査、素集合な入力へのデータ取得 — であるとき、逐次 dispatch は実時間を浪費する。このスキルは **across-domain dispatch 層**：真に独立したドメインを特定し、ドメインごとに自己完結したプロンプトを構成し、全ての `Agent` 呼び出しを **1 つのアシスタントメッセージ内で** dispatch し（ハーネスは同一メッセージ内の呼び出しだけを並行実行する）、どの verdict も落とさず集約する。

## 使う場面

- 3 つ以上のテストファイルが **無関係な** 理由で失敗 — ファイルごとに implementer 1 体。
- 複数モジュールにまたがるセキュリティ監査 — モジュールごとに reviewer 1 体。
- N 銘柄 / N 地域 / N フィードのデータ取得 — 入力ごとにデータエージェント 1 体。
- `writing-plans` が `independent: true` を付けたタスクで **かつ** `files touched` が素集合 — 両条件が必須。マーカーはプラン著者の主張であって保証ではない。

ドメインが独立と言えるのは以下が全て成り立つときのみ：共有ファイルなし（あっても全ブランチで read-only）、どのブランチも rename / 削除 / re-export しない共有シンボルなし、逐次データ依存なし。ドメインごとに独立性を一文で言えないなら、その作業は独立ではない。

## 使わない場面

[`SKILL.md`](SKILL.md) §When to use vs. when NOT to を参照：

- タスクがファイルやシンボルを共有 — マージ衝突 + 非決定的状態。逐次化するか、先にファイルを分割。
- 逐次データ依存（B が A の出力を必要とする）— 定義上、並列ではない。
- 失敗が共通の根本原因を持つかもしれない / 根本原因不明 — まず 1 体のエージェントが調査。分割は共通原因を隠す。
- 単一ドメインで複雑だが凝集している — 断片化した N 体でなく、集中した 1 体。
- 1 つの成果物に reviewer 2 体 — `subagent-driven-development` がタスク単位で既にやっている。二重ラップしない。

## subagent-driven-development との関係

SDD の implementer / reviewer 三体は **1 ドメイン内のタスク単位**、このスキルは **across-task / across-domain** の補完。並列 dispatch は何も免除しない：どのブランチも `tdd-iron-law` に従い（失敗テストが先 —「小さいし並列だから」は合理化コンボとして拒否）、`verification-before-completion` はパッケージスイートを **統合点で 1 回** 走らせる（ブランチごとではない）— ブランチ単体のスイートは単独では通っても、結合 diff は失敗しうる。

## 二つのモード

- **Mode (a)** — 1 体のオーケストレータが単一メッセージでサブエージェントを展開。全員が 1 つのチェックアウトを共有し、結果はそのオーケストレータに集約。スキル本体はこちら。
- **Mode (b)** — 複数の独立セッションが同一リポジトリで同時に作業。ハーネスはセッション間を調整しないため、規約が必要：エージェントごとの worktree（[`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) 参照）+ 素集合なプランタスクの静的事前分割 + プランの `Status` フィールドを共有台帳に + エージェントごとの PR。**要注意の落とし穴：** worktree はファイルを隔離するが、重複編集の衝突は防が**ない** — 真の衝突防御は `files touched` の素集合分割。実用上の上限：同時 ~3–5 体。

## このスキルがしないこと

- `subagent-driven-development` の代わりにはなら**ない** — SDD は各ドメイン内のタスク単位エンジンのまま。
- 同一ファイルへ並列に書く implementer を許可し**ない** — ファイル衝突は禁止。「git がなんとかしてくれる」は拒否。
- どのブランチも `tdd-iron-law` から免除し**ない**。
- ルーターの Skill Priority ステージを持た**ない** — 補助スキル、オンデマンド。

## 関連

- [`SKILL.md`](SKILL.md) — エージェント向け運用仕様（独立性基準 + dispatch パターン + 集約ルール + mode (b) + Red Flags）。
- [`../writing-plans/SKILL.md`](../writing-plans/SKILL.md) — 上流。このスキルが消費する `independent: true` の atomic task を生産。
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — 横並び。1 ドメイン内のタスク単位三体。
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — 下流。統合点で 1 回実行。
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — mode (b) の並行セッションで必須。
