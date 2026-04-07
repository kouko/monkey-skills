# UX Strategy Protocol

おもてなし — ユーザーが問題に遭遇する前に解決する。
`rubrics/ux-strategy-gate.md`（evaluator gate）と対になるプロトコル。

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
