# Visual Design Protocol

感性工学（長町三生）、引き算のデザイン、わびさびに基づくビジュアル設計プロトコル。
`rubrics/visual-gate.md`（evaluator gate）と対になるプロトコル。

## Primary Sources

This protocol targets Garrett's Surface plane
(`standards/garrett-elements-of-ux.md` §Gate Scope Partition) and
grounds its Kansei, subtractive-design, and aesthetic steps in two
tier-classified standards:

- **Step 1 Kansei targets + Step 7 SD 法 coherence check** →
  `standards/kansei-engineering-and-sd.md` (長町三生 1989 『感性工学』
  海文堂出版; Nagamachi 1995 *IJIE* 15(1):3-11; Osgood, Suci &
  Tannenbaum 1957 *The Measurement of Meaning*). The SD method is a
  **7-point bipolar** scale and decomposes into Osgood's 3 factors
  (Evaluation / Potency / Activity); never 5-point, never unipolar.
  See that standard's §Critical Attribution Corrections for the
  Osgood 1957 primary replacing earlier J-SEMS / J-STAGE / AIIT
  citations.
- **Step 2 引き算 / Step 3 余白 (Ma) / Step 6 佇まい / わびさび** →
  `standards/japanese-design-aesthetics.md` §1 引き算のデザイン
  (原研哉 2003), §2 白 / 余白 (原研哉 2008 『白』 Ch.3), §3 間 ma
  (磯崎新 2003 『建築における「日本的なもの」』), §4 佇まい
  (原研哉 2003 Ch.6 「日本にいる私」), §5 わびさび (Koren 1994).
- **Surface plane scope (no overreach into Structure / Skeleton)** →
  `standards/garrett-elements-of-ux.md`.

## Protocol

1. **Establish Kansei targets**: デザインが喚起すべき感情を定める。
   3〜5 個の目標感性語をリストする（例：洗練された、親しみやすい、先進的）。
   感性語抽出が済んでいれば `protocols/design-brainstorming.md` Phase 1 を参照
2. **Define visual hierarchy**: 閲覧者が最初、次、その次に何を見るべきか？
   ビジュアル処理を選ぶ前に情報の優先順位を確定する
3. **Select color palette**:
   - 色を感性ターゲットにマッピングする（例：暖色系 → 親しみやすい）
   - WCAG AA コントラストを検証（`standards/wcag-baseline.md`）
   - 色だけが情報伝達の唯一の手段にならないよう確保する
4. **Choose typography**:
   - 見出し・本文・キャプションの階層を視覚的に明確に区別する
   - フォントの組み合わせはスタイルとウェイトの相性を重視
   - 対象媒体の閲覧距離で可読性を担保する
5. **Compose layout**:
   - グリッドシステムを意図的な余白で適用する
   - 余白を**間（Ma）**として扱う — 何もない空白ではなく、意味を帯びた空隙
   - **引き算のデザイン**を徹底: 存在理由のない要素はすべて除去する
6. **Check craft quality**:
   - ピクセルレベルの整列と一貫性
   - 対象媒体に適した書き出し品質
   - **佇まい**: 品格が装飾ではなく内部設計から自然と滲み出ているか？
7. **Kansei coherence check**: 一歩引いて、全体の感情的印象を
   Step 1 のターゲットに照らして評価する。必要に応じて SD法の軸を使用:
   - 洗練された ←→ 野暮な
   - 高級感がある ←→ 安っぽい
   - 先進的な ←→ 古臭い
   - 親しみのある ←→ よそよそしい

## Rules

- 美的好みではなく感性ターゲットから出発する。
  「どう見えるべきか」の前に「どう感じるべきか」を問う
- **引き算のデザイン**: 迷ったら足すより引く
- 媒体に適応: App UI（プラットフォーム慣例、Dynamic Type）、
  印刷（CMYK、断ち切り）、ブランド（ファビコン〜ビルボードのスケーラビリティ）
- ダーク/ライトモード: 両方使う製品なら両方設計する
- ブランドガイドラインは個人的なスタイル選好に優先する
- ビジュアルアセットの制作は人間が行う — 明確な仕様と根拠を提示し、
  曖昧な指示は避ける

## Output Format

1. **Kansei Target Profile**: 目標感性語とビジュアルへのマッピング
2. **Visual Hierarchy**: 情報の優先順位
3. **Design Specifications**: 色、タイポグラフィ、レイアウト、余白の仕様
4. **Kansei Coherence Report**: 感情的印象とターゲットの照合結果
5. **Medium-Specific Notes**: 媒体別の適応要件
