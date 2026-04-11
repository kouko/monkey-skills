# UI & Interaction Design Protocol

無意識の設計（深澤直人）とオブジェクト指向UI（OOUI/OOUX）に基づく
UI・インタラクション設計プロトコル。
`rubrics/ui-interaction-gate.md`（evaluator gate）と対になるプロトコル。

## Primary Sources

This protocol targets Garrett's Structure + Skeleton planes
(`standards/garrett-elements-of-ux.md`) and draws on four further
tier-classified standards for its load-bearing concepts:

- **ORCA / OOUI (Step 1, 4 — noun-before-verb object modeling)** →
  `standards/ooui-and-object-modeling.md` (上野学・ソシオメディア・藤井幸多
  2020 『オブジェクト指向 UI デザイン』技術評論社; Sophia V. Prater 2015
  "Object-Oriented UX" *A List Apart* + ooux.com for the full ORCA
  4-step framework, which is **not** present in the 2015 / 2016 ALA
  articles).
- **Without Thought / affordance (Step 5)** →
  `standards/japanese-design-aesthetics.md` §6 (深澤直人 2005 『デザイン
  の輪郭』TOTO 出版) grounded in Gibson's affordance theory, plus
  `standards/nielsen-norman-heuristics.md` for Norman's signifier /
  affordance distinction and the gulfs of execution / evaluation.
- **Interaction feedback, error handling, component states (Steps 6–7)** →
  `standards/nielsen-norman-heuristics.md` (Nielsen heuristics #1
  Visibility of System Status, #5 Error Prevention, #9 Help Users
  Recognize / Diagnose / Recover from Errors).
- **Platform adaptation (Step 8) — 44pt / 48dp / 24×24** →
  `standards/platform-conventions.md` (Apple HIG 44 × 44 pt iOS;
  Material Design 3 48 × 48 dp Android; both stricter than the WCAG
  2.2 SC 2.5.8 24 × 24 CSS px AA baseline — these are additive
  obligations, not alternatives).

Structure + Skeleton plane scope partition is defined in
`standards/garrett-elements-of-ux.md` §Gate Scope Partition.

## Protocol

1. **Identify core objects**: ユーザーが扱うドメインオブジェクト（名詞）を
   列挙する。アクションを定義する前にオブジェクトを先に特定すること。
   ORCA レンズ: Objects → Relationships → CTAs → Attributes
2. **Map object relationships**: オブジェクト間の関係をマッピングする。
   関係性が UI 上で可視化され、記憶や追加ナビゲーションなしで把握できること
3. **Design object flows**: コレクション → 単一オブジェクト → 詳細 の
   自然なナビゲーションを設計する。深度は 3 階層以内に収める
4. **Define actions per object**: 各オブジェクトに対してユーザーが実行できる
   操作を定義する。CTAはオブジェクト自体に配置する
   （OOUI原則：名詞が先、動詞が後）
5. **Apply Without Thought principles**:
   - **目標行為**: ユーザーが考えずに行うべき操作は何か？
   - **アフォーダンス**: UI要素の形態がその機能を示唆しているか？
   - **認知負荷の削減**: 思考を強いるラベル、アイコン、選択肢を除去する。
     「良いUIは見えない」
6. **Define all interaction states**: すべてのインタラクティブ要素について:
   - Default, hover, active, disabled, loading, error, empty
   - すべての操作に対して可視的なフィードバックを返すこと
7. **Handle error states**: エラーは「何が起きたか」と「どう直すか」の
   両方を説明する。行き止まりを作らない
8. **Platform adaptation**:
   - iOS: タッチターゲット ≥ 44pt、iOS HIG 準拠
   - Android: タッチターゲット ≥ 48dp、Material Design 準拠
   - Web: レスポンシブブレークポイント、キーボードナビゲーション
9. **Affordance verification**: 主要ユーザーフローを頭の中で歩いてみる。
   各ステップで「ユーザーはここで迷うか？」と問う。
   迷うならアフォーダンスが不十分。簡潔化する

## Rules

- オブジェクトが先、アクションが後 — オブジェクトを特定する前に
  フォーム/ウィザードを設計しない
- OOUIをデフォルトとする。タスクベースUIは厳密に線形のフロー
  （ウィザード、チェックアウト）にのみ使用し、その選択を文書化する
- ナビゲーション深度 > 4 階層は常に誤り、3 階層はボーダーライン
- すべてのクリック/タップに即座の可視フィードバックを返す
- 無意識の設計の簡潔さと機能の網羅性が衝突した場合、
  トレードオフをフラグする — ユーザーが必要とする機能を隠さない
- デザインシステムのトークンと命名規則に一貫して従うこと

## Output Format

1. **Object Model**: コアオブジェクト、関係性、属性
2. **Navigation Map**: オブジェクトフローと深度レベル
3. **Interaction Spec**: コンポーネントごとの状態、フィードバックパターン
4. **Affordance Report**: ユーザーが迷う可能性のあるポイントと簡潔化の提案
5. **Platform Notes**: タッチターゲット、プラットフォーム慣例への準拠状況
