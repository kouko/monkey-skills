[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# Using Systems Thinking Toolkit (Router)

`systems-thinking-toolkit` プラグインの意図不明確時ルーター。

## 使うべき場面

以下のとき `/systems-thinking-toolkit:stt` を使う:

- どのメソッドが自分の状況に合うか分からない
- 何かが spiral / oscillate / 頭打ちしている
- vicious cycle / death spiral / boom-and-bust にハマっている
- 散らかった状況をマップしたいが、どのメソッドに手を伸ばせばよいか不明

特定メソッド（`cld-craft` / `cld-archetypes` / `cld-overlay` / `simulation-modeling` / `strategy-lever-and-cascade` / `team-mental-model` / `manager-personality-quadrant`）が既に決まっているならルーターは不要 — per-skill コマンドを直接呼ぶ。

## 得られるもの

- 1 質問の意図テーブルで 7 機能スキル（`cld-craft` / `cld-archetypes` / `cld-overlay` / `team-mental-model` / `simulation-modeling` / `strategy-lever-and-cascade` / `manager-personality-quadrant`）の 1 つへルーティング。
- 各行 EN + zh-TW + JA のトリガー フレーズ（v0.5 で追加）。
- 「I have a CLD」セクションの前提条件を明示（v0.4 パッチ）。
- 本当に不明確なケースには **`cld-craft`** へ既定で振る fallback。

## 適用しない場面

- どのメソッドが欲しいか既に分かっているユーザーには不要 — per-skill コマンドを直接呼ぶ。
- メソッド自体の代替ではない — ルーターは推薦して引き継ぐが、メソッドの説明は行わない。
- 複数メソッドを 1 つのワークフローで合体させるためのものではない — ひとつ選ぶ；次のメソッドが必要なら再度ルーターを呼ぶ。

## 既定 fallback

narrowing question を経ても意図がまだ不明確なら **`cld-craft`** に振る。`cld-craft` は carry-1 の prose → CLD 翻訳器で、下流スキルが消費する基盤；別の下流スキルが最終的に必要となる場合でも、先に diagram を作っておくのはまず間違いにならない。

## 関連

- 完全なルーティング表: [`SKILL.md`](SKILL.md)
- プラグイン概要: [`../../README.md`](../../README.md)
- 全スキル マップ: [`../../INDEX.md`](../../INDEX.md)

## 出典

このエントリー スキルは monkey-skills 内部のもの（`using-philosophers-toolkit` パターンを踏襲）。ルーティング先の 7 機能スキルは Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002) からの蒸留。
