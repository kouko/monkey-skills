[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# simulation-modeling

定性的な CLD を定量的なストック フロー配管図に翻訳し、得られたシミュレーションを学習のために使う — ポイント予測のためではない。

## 使うべき場面

- CLD が定量化準備完了 — 変数特定済み、S / O 符号検証済み — で、方向だけでなく数値の大きさが必要。
- 指数トラップ（小さなドリフトの複利化）を疑っており、線形外挿が危険なほど誤導的かを知るために、doubling-time 対 response-delay 診断が必要。
- モデルは構築済みだが、チームがその出力を予測として扱っており、モデルを学習ツールとして再フレーム化したい。

## 起動方法

`/systems-thinking-toolkit:simulation` またはルーター `/systems-thinking-toolkit:stt` から。

## 得られるもの

- 定性 CLD から導かれたストック フロー配管図 — 変数は time-freeze テストでストック / フローに分類され、uniflow / biflow が検出され、レバー → フロー / アウトカム → ストックのマッピングが完了。
- すべての R ループに doubling-time 対 response-delay 診断が明示され、シミュレーションが学習アーティファクトとして（予測アーティファクトとしてではなく）明示的にフレーミングされる。

## 適用しない場面

- ポイント予測には不向き — モデルは構造駆動の挙動を露わにする。その数値を予測としてコミットすれば外れる。
- 実シミュレーターの代替にはならない — v0.1.0 は翻訳の規律のみを出荷する。数値実行は Vensim / iThink / Stella / スプレッドシート / Python が必要（コンパニオン スクリプトは v0.2+ へ延期）。
- 一回限りのキャリブレーションには不向き — スナップショットよりも学習ループのほうが重要。データが洗練されたら再実行する。

## 参照

- スキル本体仕様: [SKILL.md](SKILL.md)

## 出典

Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002) — 第 11 章（stock-flow translation）と第 12 章（models for learning, not answers）。数値系統 dynamics の Forrester / Sterman / Meadows 系譜。
