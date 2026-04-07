# Planning Frameworks Reference

Lightweight guide for choosing frameworks during project planning.
Use the simplest framework that answers your current question.

## Always Use

### Jobs-to-be-Done (JTBD)

Understand WHY users need this product before defining WHAT to build.

Format: "When [situation], I want to [motivation], so I can [outcome]."

Example:
- When I finish a meeting with multilingual participants,
  I want to get an accurate transcript with speaker labels and emotions,
  so I can review key moments without re-watching the recording.

Use in: Phase 1 (Vision) of product-spec-writing protocol.

### Assumption Mapping

Identify the riskiest assumptions BEFORE investing in implementation.

Categories:
- **Desirability**: Do users actually want this? (biggest risk for new products)
- **Feasibility**: Can we build this with available technology?
- **Viability**: Does the business model work? (if applicable)
- **Usability**: Can users figure out how to use it?

Process:
1. List all assumptions (aim for 10-20)
2. Plot on Impact (high/low) × Evidence (strong/weak) matrix
3. Top-right quadrant (high impact, weak evidence) = validate first
4. Mark top 3 as [ASSUMPTION] in PRODUCT-SPEC.md

Use in: Phase 3 (Scope) of product-spec-writing protocol.

## Use When Applicable

### Lean Canvas

Quick one-page business model for products with commercial intent.

9 blocks: Problem, Solution, Key Metrics, Unique Value Proposition,
Unfair Advantage, Channels, Customer Segments, Cost Structure, Revenue Streams.

When to use: Product has revenue/monetization goals.
When to skip: Personal tools, internal utilities, hobby projects.

Use in: Phase 4 (Direction Setting > Business direction).

### 3C 分析（大前研一）

市場ポジショニングのための顧客・競合・自社の分析フレームワーク。

- **Customer（顧客）**: 誰か？ 現在何を使っているか？ 何が不足しているか？
- **Competitor（競合）**: 何が存在するか？ 強み・弱みは？ 価格帯は？
- **Company（自社）**: 自分の優位性は？ リソースは？ 制約は？

使用場面：既存ソリューションがある市場に参入する場合。
スキップ：競合が存在しない新規領域の場合。

Use in: Phase 1 (Vision) when market context matters.

### 5W2H

企画の網羅性を確認するための日本ビジネス慣習由来のチェックフレーム。

- **Why（なぜ）**: この企画の目的・背景
- **What（何を）**: 提供する製品・サービスの内容
- **Who（誰が・誰に）**: ターゲットユーザーと実行者
- **When（いつ）**: タイムライン、マイルストーン
- **Where（どこで）**: プラットフォーム、配布チャネル
- **How（どのように）**: 技術アプローチ、実現方法
- **How much（いくらで）**: コスト、リソース見積もり

使用場面：PRODUCT-SPEC.md の最終チェックとして。
抜け漏れがないか 7 項目で網羅的に確認する。

Use in: Phase 5 (Handoff) as a completeness cross-check.

## Rarely Needed (for reference)

- **Opportunity Solution Tree**: When problem space is large and you need to map
  outcome → opportunities → solutions systematically. Usually overkill for personal projects.
- **Value Proposition Canvas**: When you need precise differentiation against
  specific competitors. Extends JTBD with gain creators and pain relievers.
