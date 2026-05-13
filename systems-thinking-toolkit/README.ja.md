# Systems Thinking Toolkit

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> 散文 → CLD 翻訳器 (carry-1) + 6 個の下流コンシューマー スキル + 1 個の V1-weak 人格補助 + 1 個のルーター。Dennis Sherwood『Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking』(Nicholas Brealey, 2002) を基盤とし、`systems-thinking-toolkit` プラグインとして monkey-skills に同梱。

## 同梱スキル

| Slug | 役割 | 説明 |
|---|---|---|
| `cld-craft` | Carry-1 producer | 散文 → 完全注釈付き Mermaid CLD（12 hygiene rules + Rule 7 fuzzy variable elevation + S/O signing + R/B classification、すべて Step 11 に集約） |
| `cld-archetypes` | CLD consumer | limits-to-growth (R+B coupling) または V/T/A (delay 付き B-loop) アーキタイプ認識 + 対応する介入プレイブック（Branch L + Branch V） |
| `cld-overlay` | CLD consumer | 多ステークホルダー CLD overlay + straddle-policy 抽出（対外的なコンフリクト解消） |
| `team-mental-model` | CLD consumer | メンタルモデル調和 + 4 つの観測可能な leadership-energy proxy（cadence / active-listening / value-revisitation / symbol-narrative）— 対内的なチーム プロトコル |
| `simulation-modeling` | CLD extension | text-only CLD → stock-and-flow 変換 + 「予測ではなく学習のための」規律 |
| `strategy-lever-and-cascade` | Non-CLD strategy | lever 対 outcome の reframe + 3 時間軸 cascade + 3×N シナリオ テーブル（v0.6 で Martian-test perturbation を Step 5 にインライン吸収） |
| `manager-personality-quadrant` ⚠ V1-weak | Auxiliary | framing 対 analysis 分割 + Gods/Gamblers/Grinders/Guides の 2×2；**facilitation vocabulary 限定**（v0.6 で Boundary 強化）；人事関連のあらゆる用途には DiSC / Big Five / Hogan などのより強い代替案あり |
| `using-systems-thinking-toolkit` | Entry / router | 意図不明確時のルーティング |

## このプラグインの位置づけ

**Carry-1 thesis**: システム思考の価値の大半は上流の翻訳ステップ — 散らかった散文を構造化された causal loop diagram (CLD) に変換するステップに集中する。これは LLM が人間に対して最大のアドバンテージを持つステップ（混線した narrative を nodes / links / signed loops に数秒でパースする）。下流の応用（ワークショップ運営、シミュレーション、意思決定）は逆に LLM が比較的弱い領域。よって本プラグインは意図的に上流ステップに重みを置く設計。

Sherwood の運用的貢献は `cld-craft` に集約されている: 12 hygiene rules、Rule 7 の fuzzy variable elevation、S/O link signing、R/B loop classification — すべて Step 11 に統合。出力は完全注釈付きの Mermaid CLD で、読める・分類できる・任意の下流コンシューマー スキルにそのまま渡せる。

下流スキル（cld-archetypes / cld-overlay / team-mental-model / simulation-modeling）は `cld-craft` が生成する分類済み CLD を消費する。`strategy-lever-and-cascade` は唯一の非 CLD スキル — strategic reframe 系の動き（lever 対 outcome / cascade / scenarios）を扱い、v0.6 で吸収された Martian-test perturbation を含む。`manager-personality-quadrant` は facilitation vocabulary 限定として残置 — 本気の人事用途には Big Five / Hogan / DiSC / Hofstede 等に転送するのが正解。

## 使い方

1. どのスキルを使うべきか分からない場合は `/systems-thinking-toolkit:stt` で意図ルーティング。
2. 散文 / vicious cycle / death spiral 系の言い回しがある場合は `/systems-thinking-toolkit:cld-craft` を直接呼ぶ。
3. CLD が既にある場合は `/stt` の「I have a CLD — now what?」セクションで archetypes / overlay / simulation へルーティング。
4. 戦略 / チーム作業なら `/strategy-lever-and-cascade` または `/team-mental-model` を参照。
5. 体系的に学習する場合は [`INDEX.md`](INDEX.md) の順序に従う — `cld-craft` から開始。

## 出典 & 制約

- `tsundoku:book-distill` RIA-TV++ パイプラインで蒸留（Adler → 5 並列抽出 → 三重検証 → RIA++ レンダリング → Zettelkasten リンク → 敵対的圧力テスト）
- オリジナル 14 スキル Stage-3 蒸留を v0.4 R3 restructure + v0.6 sk13 吸収で 7 機能 + 1 router に統合（コンテンツ ロスはゼロ；元 14 スキルの body はすべて統合先から復元可能 — [`INDEX.md`](INDEX.md) のマッピング参照）
- V1-weak スキルは 1 つ残存: `manager-personality-quadrant`。v0.6 で「facilitation vocabulary 限定」の Boundary に強化済み；その "Graduate beyond" 表は人事関連のあらゆる用途について Big Five (NEO-PI-R) / Hogan / Heifetz / Edmondson / Klein / Hofstede / Tuckman / Lencioni へルーティング
- Stage-0 (`BOOK_OVERVIEW.md`) / Stage-1.5 (`VERIFIED.md`) / Stage-3 オリジナル (`INDEX-original.md`) の監査証跡は [`references/`](references/) を参照
- v0.7+ 候補は [`ROADMAP.md`](ROADMAP.md) を参照
- 原著に対するカバレッジ監査（方法論 ~85% + 例示資料 ~70%）は `docs/superpowers/audits/2026-05-13-systems-thinking-toolkit-vs-original-book.md` を参照

## ライセンス

MIT
