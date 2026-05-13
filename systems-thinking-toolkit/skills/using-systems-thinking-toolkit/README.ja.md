[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# using-systems-thinking-toolkit

エントリー / ルーター スキル — 「何をしようとしていますか？」と 1 つ質問するだけで、状況に最適なシステム思考メソッドを見つける。

## 使うべき場面

- システム思考メソッドが適用できそうだが、どれを呼ぶべきかわからない。
- ユーザーが曖昧なパターンを述べる（「どんどん悪くなる」「支出を倍にしても売上が伸びない」など）— 特定スキルへ手を伸ばす前にルーターに分類させる。

## 起動方法

`/systems-thinking-toolkit:stt`

（直接の "stt" スキルは存在しない — このスラッシュコマンドはこのルーター スキルを起動する。）

## 得られるもの

- 1 質問の意図テーブルで現在の 7 機能スキル（cld-craft / cld-archetypes / cld-overlay / team-mental-model / simulation-modeling / strategy-lever-and-cascade / manager-personality-quadrant）の 1 つへルーティング。v0.6 で `innovaction-martian-test` を strategy Step 5 に吸収；v0.4 で loop-and-link-primitives を cld-craft Step 11 に吸収。
- 「複数のメソッドを組み合わせない」という正直なルール + 不明確なケースは **`cld-craft`**（carry-1 prose→CLD プロデューサー）へ既定で振るフォールバック。

## 適用しない場面

- どのメソッドが欲しいか既にわかっているユーザーには不要 — 直接 per-skill コマンドを呼ぶ。
- メソッド自体の代替ではない — ルーターは推薦して引き継ぐが、メソッドの説明は行わない。
- すべての問題にシステム思考が要るわけではない — どれも該当しなければ、ルーターは正直にそう言う。

## 参照

- 全ルーター論理: [SKILL.md](SKILL.md)
- 全プラグイン マップ: [`../../INDEX.md`](../../INDEX.md)

## 出典

このエントリー スキルは monkey-skills 内部のもの（`using-philosophers-toolkit` パターンを踏襲）。ルーティング先の 9 スキルは Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002) からの蒸留。
