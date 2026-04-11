# UX Strategy Protocol

おもてなし — ユーザーが問題に遭遇する前に解決する。
`rubrics/ux-strategy-gate.md`（evaluator gate）と対になるプロトコル。

## Primary Sources

This protocol targets Garrett's Strategy + Scope planes
(`standards/garrett-elements-of-ux.md` §Gate Scope Partition) and
draws its temporal, quality, and meaning models from
`standards/ux-temporal-and-quality-models.md`.

- **Step 2 temporal journey (4 期間 UX)** → `standards/ux-temporal-and-quality-models.md`
  §The 4 Temporal UX Phases. Primary source: Roto, Law, Vermeeren &
  Hoonhout (2011) *User Experience White Paper*, Dagstuhl Seminar
  10373; introduced to the Japanese HCD community by 安藤昌也 (2016)
  『UX デザインの教科書』 §2.2.4. The 4 phases (予期的 / 一時的 /
  エピソード的 / 累積的 UX) are **not a sequence** — for a long-term
  user, all 4 are active simultaneously.
- **Step 3 strategy × scope (Garrett)** → `standards/garrett-elements-of-ux.md`
  §The 5 Planes. Strategy = user needs × business objectives;
  Scope = functional + content requirements. Both planes live inside
  the `ux-strategy-gate`.
- **Step 6 meaning coherence** → `standards/ux-temporal-and-quality-models.md`
  §Meaning Innovation. **意味のイノベーション is from Verganti 2009
  *Design-Driven Innovation*, not 黒須.** 黒須 2020 『UX 原論』
  Ch.11 §11.3 defines a 2×2 **4 Quality Regions** matrix (客観 / 主観
  × 設計時 / 利用時) — it has no dimension called 意味性. Any
  load-bearing 意味 claim must cite Verganti; see that standard's
  §Critical Attribution Corrections for the 3D-quality →
  4-quality-regions and 黒須 → Verganti attribution fixes.
- **HCD process baseline (all steps)** → `standards/ux-temporal-and-quality-models.md`
  §Human-Centred Design Process (ISO 9241-210:2019 / JIS Z 8530:2021,
  6 principles).

## Protocol

1. **Define user & business goals**: 主要ユーザーは誰か？ そのコアニーズは？
   ビジネス目標は何か？ それぞれ一文で記述する
2. **Map the temporal journey**（安藤昌也 UXの期間モデル）:
   - **予期的UX**（利用前）: ユーザーは使う前に何を期待しているか？
   - **一時的UX**（利用中）: コアとなる利用中の体験は何か？
   - **エピソード的UX**（利用後）: セッション後に何が起きるか？
   - **累積的UX**（利用期間全体）: 時間とともに価値がどう蓄積されるか？
3. **Align strategy × scope**（Garrett モデル）:
   - **戦略**: 各フェーズがユーザーニーズとビジネスの両方に貢献しているか？
   - **要件**: 機能・コンテンツの必須/推奨/可能/対象外を整理する
4. **Identify experience gaps**: 体験のどこが途切れているか？
   タッチポイントがないフェーズ、インセンティブの不整合をフラグする
5. **Design re-engagement hooks**: 利用後のタッチポイントを確保する。
   進捗追跡、フィードバックループ、価値の再確認手段のいずれか
6. **Validate meaning coherence**: 全フェーズを通じて一貫した製品の意味が
   伝わっているか？（意味が定義済みなら `protocols/design-brainstorming.md`
   Phase 2 を参照）

## Rules

- 4 つの時間的フェーズを必ず全てマッピングする。
  エピソード的UXと累積的UXが最も見落とされやすい
- ビジネス目標がユーザーの信頼を毀損してはならない。
  短期的な収奪 vs 長期的な価値は致命的な矛盾
- 機能の優先順位付けは MoSCoW を使用:
  Must / Should / Could / Won't
- ユーザーがターゲットペルソナを未定義の場合、先に最小限のペルソナ作成を支援する
- UXパターンの検索は英語と日本語の両方で行うこと
  - EN: "{category} UX best practices"
  - JP: 「〇〇 UX設計」「〇〇 ユーザー体験」

## Output Format

1. **User & Business Alignment**: 目標の記述、矛盾点の指摘
2. **Temporal Journey Map**: 4 フェーズのタッチポイント分解
3. **Feature Scope**: MoSCoW で優先順位付けした機能リスト
4. **Gap Analysis**: タッチポイントが欠落・不整合なフェーズ
5. **Recommendations**: ユーザーインパクト順の改善提案
