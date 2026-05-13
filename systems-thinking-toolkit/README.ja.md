# Systems Thinking Toolkit

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Dennis Sherwood『Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking』(Nicholas Brealey, 2002) から蒸留した 9 つのシステム思考スキルを `systems-thinking-toolkit` プラグインとして monkey-skills 向けに同梱しています。

## 同梱スキル

| スキル | 用途 |
|---|---|
| `using-systems-thinking-toolkit` | 状況に応じて最適なメソッドへルーティング |
| `loop-and-link-primitives` | 基礎：R/B ループ診断 + S/O リンク符号付け (sk01+sk02) |
| `cld-craft` | ワークショップ規律での因果ループ図作成 — 12 ルール + ファジー変数の昇格 (sk03+sk04) |
| `limits-to-growth-take-the-brakes-off` | R ループが B ループでブレーキされる原型；エンジンを踏むのではなく制約を緩める (sk05) |
| `variance-target-action-template` | 汎用 B ループ制御テンプレート + 振動時の「何もしない」診断 (sk06) |
| `strategy-lever-and-cascade` | レバー対アウトカム再構成 + 3 時間軸カスケード + 3×N シナリオプランニング (sk07+sk08) |
| `stakeholder-and-team-thinking` | 複数視点 CLD オーバーレイ + メンタルモデル調和 (sk09+sk10) |
| `simulation-modeling` | ストック・フロー変換 + 「学習のためのモデル、答えのためのモデルではない」規律 (sk11+sk12) |
| `manager-personality-quadrant` ⚠ V1-weak | 経営者人格 2×2；**v0.6 で「ファシリテーション語彙のみ」境界強化**；DiSC / Big Five / Hogan がより強い代替案（人事用途には絶対不可） |

> v0.6 で `innovaction-martian-test` を `strategy-lever-and-cascade` の Step 5 (Martian-test 特徴摂動) に吸収。スキルとしては廃止済み。
> 注: 本 README の上記表は v0.4 以前のスキル名を残しています。v0.7 で完全な v0.6 同期 rewrite を予定。

## このプラグインの位置づけ

システム思考は単なる図ではなく、**イベント** ではなく **構造** を診断するための規律です。Sherwood の貢献は運用面にあります — 因果ループ図は 2 種類のループ（強化型 / バランス型）に還元でき、O の数で分類でき、virtuous 対 vicious の回転方向は同一の構造アイデンティティに駆動されます。本プラグインは彼の著作のマネージャー向け部分を 9 個のアトミックで組み合わせ可能なスキルへ蒸留したものです。

オリジナルの 14 スキル Stage-3 蒸留から Profile-B でマージ。5 個の compose-with ペアを単一スキルに統合（source-unit 引用トレイルを保持）、4 個はスタンドアロン（sk05/sk06 は認知フレームレベルで対比；sk13/sk14 は V1-weak を user override 経由で保持し v0.2 で再評価予定）。

## 使い方

1. どのスキルを使うべきか分からない場合は `/systems-thinking-toolkit:stt` で intent table 経由のルーティング。
2. 状況が分かっている場合は per-skill コマンドを使用（全リストは [`INDEX.md`](INDEX.md) 参照）。
3. 系統的に学習する場合は [`INDEX.md`](INDEX.md) の推奨学習順序に従う — `loop-and-link-primitives` から開始。

## 出典 & 制約

- `tsundoku:book-distill` RIA-TV++ パイプラインで蒸留（Adler → 5 並列抽出 → 三重検証 → RIA++ レンダリング → Zettelkasten リンク → 敵対的圧力テスト）
- オリジナル 14 Stage-3 スキルから Profile-B で 9 へ統合（compose-with ペア 5 + スタンドアロン 4）
- V1-weak スキルは 1 つ残存（`manager-personality-quadrant`）。v0.6 で「ファシリテーション語彙のみ」境界強化。`innovaction-martian-test` は v0.6 で `strategy-lever-and-cascade` Step 5 に吸収済み。人格関連のより強い先行技術: DiSC, Big Five (NEO-PI-R), Hogan, Situational Leadership.
- Stage-0 (`BOOK_OVERVIEW.md`) / Stage-1.5 (`VERIFIED.md`) / Stage-3 オリジナル (`INDEX-original.md`) の監査証跡は [`references/`](references/) を参照
- v0.7+ 候補（PR #271 audit の 6 件 body fix；CI desc ↔ skill folder drift check；stock-flow シミュレーション Python コンパニオン；Edmondson teaming-safety hand-off）は [`ROADMAP.md`](ROADMAP.md) を参照

## ライセンス

MIT
