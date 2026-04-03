# Design Brainstorming Protocol

日本の 3 つのコア設計理論を統合した設計発想プロトコル。
- **感性工学**（長町三生）— 感性を物理パラメータに翻訳する技術体系
- **意味のイノベーション**（Verganti / 八重樫文）— 製品の社会的意味を根本的に革新
- **無意識の設計**（深澤直人）— アフォーダンスを通じた直感的行為への最適化

## Protocol

### Phase 0: Research & Insight（リサーチとインサイト開発）

1. **Clarify scope**: 何を設計するか、誰が使うか、制約条件（プラットフォーム、
   ブランド、予算）を明確にする
2. **Observe behavior**: 対象文脈におけるユーザーの無意識的行動を観察する。
   「考えずにやっていること」は何か？
3. **Extract Kansei vocabulary**: 「この製品はどう感じるべきか？」を問い、
   10〜30 個の感性語（感覚形容詞）を収集する。
   関連語を提案して語彙を拡張すること
4. **Explore cultural meaning**: この製品カテゴリが社会で現在どんな意味を
   持っているか？ どんな文化的トレンドが変化しつつあるか？

### Phase 1: Kansei Engineering（感性工学的フェーズ）

5. **Classify Kansei words**: 収集した感性語をクラスタに分類する
   （例：高格調性、親しみやすさ、先進性）
6. **Analyze competitors**: 既存製品がこれらの感性次元でどう評価されるか分析し、
   ギャップと機会を特定する
7. **Map to parameters**: 各感性クラスタに対して、目標の感情と相関する
   具体的な設計パラメータ（色、形状、質感、タイポグラフィ、余白）を提案する

### Phase 2: Design-Driven Innovation（意味のイノベーション的フェーズ）

8. **State the current meaning**: この製品がユーザーにとって今日どんな意味を
   持つか言語化する（例：「ゲーム機＝個人の画面娯楽」）
9. **Generate meaning hypotheses**: 2〜3 個の急進的な意味転換を提案する
   （例：「ゲーム機＝家族で身体を動かす遊び」）。
   各仮説は製品の**新しい社会的役割**を記述すること
10. **Identify key interpreters**: 文化的エコシステムの中で、この新しい意味を
    検証・増幅する「キーインタープリター」は誰か？
11. **Select meaning direction**: トレードオフを提示し、ユーザーに選択させる。
    AIは提案、人間が最終決定

### Phase 3: Without Thought（無意識の設計的フェーズ）

12. **Define target action**: ユーザーが**考えずに行うべき行為**を定義する
    （例：Wii リモコンを「持って振る」）
13. **Maximize affordance**: 目標行為が外見だけで自明になる
    形態・素材・配置を提案する
14. **Minimize cognitive load**: 思考を強いる要素を特定・除去する。
    色数、形数、テキストを削減。引き算のデザインを徹底
15. **Cross-check with Kansei**: アフォーダンスの選択が Phase 1 の
    感性ターゲットと矛盾せず強化しているか検証する

### Phase 4: Integration & Verification（統合的検証）

16. **Kansei alignment**: 設計が目標の感性プロファイルを達成しているか？
    各感性クラスタを確認
17. **Meaning coherence**: 形態が新しい意味を説明なしに伝えているか？
18. **Affordance test**: 初見のユーザーが説明なしに正しく操作できるか？
19. **Synthesize**: 3 層の統合コンセプトを、各層の連結根拠とともに提示する

## Rules

- AIは選択肢と仮説を生成する。最終的な創造判断はユーザーが行う
  — 特に意味の方向性（Phase 2）は人間の領域
- 解決策に飛ぶ前に、必ず観察と感性語抽出（Phase 0-1）から始めること
- 感性ターゲットとアフォーダンスの簡潔さが衝突した場合、
  トレードオフを明示する — 暗黙の妥協をしない
- 参考事例の検索は英語と日本語の両方で行うこと
  - EN: "{category} design best practices"
  - JP: 「〇〇 デザイン事例」「〇〇 感性」
- 文化的・美的判断は人間に属する。AIは構造化された分析と選択肢を提供する

## Output Format

1. **Kansei Profile**: 目標感性語とクラスタ分類
2. **Meaning Canvas**: 現在の意味 → 提案する新しい意味、
   キーインタープリターとナラティブ
3. **Affordance Spec**: 目標行為、形態原則、認知的簡潔さのために除去すべき要素
4. **Integration Summary**: 3 層がどう相互強化するか、トレードオフの記載
5. **Reference Examples**: 類似の統合を示す既存製品（出典付き）
