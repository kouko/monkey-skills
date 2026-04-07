# Planning Brainstorming Protocol

模糊なアイデアから明確なプロダクト方向性を導き出す。
Checklist-driven の対話プロセス。完了するまで spec 作成に進まない。

## Hard Gate

Do NOT load `product-spec-writing.md`, write any spec, or take any
implementation action until this checklist is fully completed and
the user has approved the selected direction.

## Checklist

Complete each task in order. Each task requires user input before proceeding.
One question per message. Prefer multiple choice when possible.

### 1. Understand the spark

何を作りたいか、なぜ作りたいかを理解する。
「何かアイデアがあるんですが」レベルの曖昧さでも OK。

### 2. Identify who benefits

誰のためのプロダクトか？
- 自分用（personal tool）
- 特定ユーザー向け（known audience）
- 市場向け（commercial product）

この回答で後続の質問の深さが変わる。

### 3. Define the Job-to-be-Done

ユーザーの「ジョブ」を特定する。
「[状況]のとき、[動機]したい。そうすれば[成果]できるから。」

ユーザーと一緒に文を完成させる。一度で完成しなくて良い
— 何度か質問して磨く。
See `standards/planning-frameworks.md` for JTBD format.

ソクラテス式に深掘りする：
- 「なぜそう思いますか？」（仮定を問う）
- 「もしそうでなかったら？」（反例を探る）
- 「今はどう解決していますか？」（現実を確認する）
回答を額面通りに受け取らない — 本質的なジョブは表面の要望と異なることが多い。

### 4. Explore existing landscape

現在この問題はどう解決されているか？
- 既存ツール / 競合 / 代替手段
- 何が不満か / 何が足りないか

ソクラテス式に確認する：
- 「競合がないと言いましたが、本当にないですか？ ユーザーは今どんな代替手段を使っていますか？」
- 「なぜ現状を我慢できているのですか？」（切迫度の確認）

市場データが必要なら → ユーザーに `research-team` の利用を提案。

### 5. Generate 2-3 product directions

異なるアプローチを提案する。各方向について：
- 何を作るか（形式：CLI / App / API / Library / ...）
- コア体験（何が一番価値を生むか）
- 技術的実現性（ざっくり：可能 / 要調査 / 困難）
- 最大のリスク

### 6. Compare trade-offs

各方向を比較表で提示：
- Scope（どこまで作るか）
- Complexity（技術的難易度）
- Impact（ユーザーへの価値）
- Risk（最大のリスクは何か）

### 7. Surface critical assumptions

選択肢ごとに最も危険な仮定を 1 つずつ挙げる。
See `standards/planning-frameworks.md` for Assumption Mapping.

ソクラテス式に検証する：
- 「この仮定が正しいという証拠は何ですか？」（evidence を問う）
- 「もしこの仮定が間違っていたら、計画全体にどう影響しますか？」（implications を問う）

### 8. User selects direction

AI は推奨を提示し、理由を説明する。
人間が最終判断する。

### 9. Define scope boundary

選択した方向について：
- IN scope（この版で作るもの）
- OUT scope（明確に作らないもの）

### 10. Handoff to spec writing

確定した方向を構造化して output する。

## Handoff Output

```
## Planning Brainstorming Summary

### Selected Direction
[選択した方向の概要]

### JTBD
When [situation], I want to [motivation], so I can [outcome].

### Key Assumptions (to validate)
1. [ASSUMPTION] ...
2. [ASSUMPTION] ...

### Scope
- IN: ...
- OUT: ...

### Next Step
Load `product-spec-writing.md` to write PRODUCT-SPEC.md.
```

## Rules

- 一度に一つの質問。複数の質問を一つのメッセージにまとめない
- 選択肢があれば提示する（open-ended より multiple choice 優先）
- Task 1-4 を完了する前に方向を提案しない — 先にユーザーの意図を理解する
- 具体的に：「ツール」ではなく「macOS CLI で会議録音を文字起こしするツール」
- AI は選択肢を提示し推奨する。最終決定は人間
- 方向が既に明確な場合は task 1-4 を簡略化してよいが、完全にスキップしない
