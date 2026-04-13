# Planning Brainstorming Protocol

模糊なアイデアから明確なプロダクト方向性を導き出す。
Checklist-driven の対話プロセス。完了するまで spec 作成に進まない。

## Primary Sources

- `standards/planning-frameworks.md` — JTBD + Job Story template (Adams 2016 Intercom), 4 Big Risks (Cagan 2017), Assumption Mapping (Bland & Osterwalder 2020), 3C 分析 (大前 1975)
- `standards/discovery-frameworks.md` — Customer Development (Blank 2005) for Task 4 existing landscape, Product Discovery (Cagan 2017) for the discovery vs delivery distinction
- `standards/spec-completeness-standards.md` — JP 企画 cultural anchors (ヤング 1988 idea-generation 5 steps for brainstorming framing)

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

この段階ではヤング (1988 日譯)『アイデアのつくり方』の **材料収集** 段階に
相当する — 判断せずに情報を吸収する。
See `standards/spec-completeness-standards.md` §JP 企画 genealogy.

### 2. Identify who benefits

誰のためのプロダクトか？
- 自分用（personal tool）
- 特定ユーザー向け（known audience）
- 市場向け（commercial product）

この回答で後続の質問の深さが変わる。

### 3. Define the Job-to-be-Done

ユーザーの「ジョブ」を特定する。

**Job Story テンプレート**（Adams 2016 Intercom、`standards/planning-frameworks.md`
§Job Story template を参照）:

「[状況]のとき、[動機]したい。そうすれば[成果]できるから。」

このテンプレートは Paul Adams が 2016 年に Intercom 社内で発明したもので、
Christensen の JTBD 理論とは別物だが相補的である。ユーザーと一緒に
文を完成させる。一度で完成しなくて良い — 何度か質問して磨く。

ソクラテス式に深掘りする：
- 「なぜそう思いますか？」（仮定を問う）
- 「もしそうでなかったら？」（反例を探る）
- 「今はどう解決していますか？」（現実を確認する）

回答を額面通りに受け取らない — 本質的なジョブは表面の要望と異なることが多い。
これは Christensen & Raynor (2003)『イノベーションへの解』Ch.3 の milkshake
case study の核心的教訓である（プロダクト category ではなく customer job が
本質）。

### 4. Explore existing landscape

現在この問題はどう解決されているか？
- 既存ツール / 競合 / 代替手段
- 何が不満か / 何が足りないか

これは Blank (2005)『The Four Steps to the Epiphany』の Customer
Discovery 段階に対応する —「顧客は実在するか」「現在何を使っているか」を
確認する `standards/discovery-frameworks.md` §Customer Development 参照。

ソクラテス式に確認する：
- 「競合がないと言いましたが、本当にないですか？ ユーザーは今どんな代替手段を使っていますか？」
- 「なぜ現状を我慢できているのですか？」（切迫度の確認）

**3C 分析** のうち Competitor の視点を仮置きする
（`standards/planning-frameworks.md` §3C 分析、大前研一 1975『企業参謀』）。

市場データが必要なら → ユーザーに `research-team` の利用を提案。

### 4b. Grill — challenge assumptions before generating directions

Task 1-4 で収集した情報を基に、ユーザーの意図と仮定を質問して
共通理解を構築する。一度に一つの質問。各質問に推奨回答を添える。

- **前提への挑戦**: 「Xとおっしゃいましたが、既存の競合がYの方法で
  解決しています — それでもXが必要ですか？」
  表面の要望と本質的なジョブの矛盾を指摘する。
- **依存関係の深掘り**: 「もしこのユーザー層が実在しなかったら、
  プロダクト全体にどう影響しますか？」
  決定ツリーの各分岐を辿り、依存関係を一つずつ解決する。
- **境界条件の確認**: 「MVP には何を含めて、何を含めないか？
  その線引きの根拠は？」
  暗黙の要件と期待を明示化する。
- コードベースや既存資料を読めば分かる質問は、ユーザーに聞かずに
  自分で調べる。

未解決の分岐がなくなるまで、またはユーザーが先に進みたいと言うまで
続ける。質問数の上限は設けない。

### 4c. Understanding Summary

方向生成（Task 5）に進む前に、理解の要約を提示してユーザーに確認を求める：

```
## Understanding Summary

### Intent
[何を作りたいか、なぜ作りたいか]

### Job Story
When [situation], I want to [motivation], so I can [outcome].

### Key Constraints
[技術的・ビジネス的・スコープの制約]

### Confirmed Assumptions
[grill で検証された仮定]

### Resolved Ambiguities
[曖昧だったが解決された問題]
```

方向が既に明確な場合は Task 4b-4c を簡略化してよいが、
完全にスキップしない。

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

**4 Big Risks** のどれに該当するかを分類する
（`standards/planning-frameworks.md` §The 4 Big Risks、Cagan 2017
*Inspired* 2nd ed Part III）:

- **Value risk** — ユーザーは本当に欲しがるか？
- **Usability risk** — 使い方がわかるか？
- **Feasibility risk** — 技術的に作れるか？
- **Business Viability risk** — 事業として成立するか？

**重要**: 以前の standards は "Desirability / Feasibility / Viability /
Usability" の 4 軸を Bland & Osterwalder 2020 に帰属させていたが、これは
誤り。Bland は 3 軸 (D/V/F) のみ。4 軸版本は Cagan 2017 の Four Big Risks
(Value / Usability / Feasibility / Business Viability) に由来する。
planning-team は **Cagan 4 軸 を正式採用** する。

ソクラテス式に検証する：
- 「この仮定が正しいという証拠は何ですか？」（evidence を問う）
- 「もしこの仮定が間違っていたら、計画全体にどう影響しますか？」（implications を問う）

上位 3 つを **Assumption Mapping** の Impact × Evidence 2×2 にプロット
（Bland & Osterwalder 2020、`standards/planning-frameworks.md`
§Assumption Mapping 参照）— 「高 Impact × 弱 Evidence」象限のものが
validate すべき対象。

### 8. User selects direction

AI は推奨を提示し、理由を説明する。
人間が最終判断する。

### 9. Define scope boundary

選択した方向について：
- IN scope（この版で作るもの）
- OUT scope（明確に作らないもの — Ubl 2020 Non-Goals convention、
  `standards/goals-and-metrics.md` §Goals/Non-Goals 参照）

Non-Goals には「検討されたが明示的に却下された plausible goals」を書く。
「明らかに対象外のもの」は書く必要はない。

### 10. Handoff to spec writing

確定した方向を構造化して output する。

## Handoff Output

```
## Planning Brainstorming Summary

### Selected Direction
[選択した方向の概要]

### Job Story
When [situation], I want to [motivation], so I can [outcome].
(Adams 2016 Intercom — NOT Christensen)

### Key Assumptions (to validate)
Mapped to 4 Big Risks (Cagan 2017):
1. [ASSUMPTION] (Value / Usability / Feasibility / Business Viability)
2. [ASSUMPTION] ...
3. [ASSUMPTION] ...

### Scope
- IN: ...
- OUT: ... (plausible rejected goals, Ubl 2020)

### Next Step
Load `product-spec-writing.md` to write PRODUCT-SPEC.md.
```

## Rules

- 一度に一つの質問。複数の質問を一つのメッセージにまとめない
- 選択肢があれば提示する（open-ended より multiple choice 優先）
- Task 1-4c を完了する前に方向を提案しない — 先にユーザーの意図を理解する
- Grill（Task 4b）では各質問に推奨回答を添える — 聞くだけでなく提案もする
- コードベースや既存資料を読めば分かる質問は、ユーザーに聞かずに自分で調べる
- Understanding Summary はユーザーの確認を得てから Task 5 に進む
- 具体的に：「ツール」ではなく「macOS CLI で会議録音を文字起こしするツール」
- AI は選択肢を提示し推奨する。最終決定は人間
- 方向が既に明確な場合は task 1-4 を簡略化してよいが、完全にスキップしない
- Job Story を書くときは Adams (2016) Intercom を cite、Christensen では
  ない。「As a user, I want..." は user story であり Job Story ではない。
- Assumption Mapping の 4 軸は Cagan (2017) Four Big Risks。Bland (2020)
  の 3 軸 (D/V/F) とは異なる — 混用しない。
