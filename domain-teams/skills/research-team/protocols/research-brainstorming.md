# Research Brainstorming Protocol

表面的研究テーマから、未知領域・隠れたリスク・見落とされた選択肢を
体系的に洗い出す。Lateral Exploration（横断的探索）によって
研究範囲を拡張し、優先順位をつける。

## Primary Sources

- `standards/source-quality-and-evidence.md` — scope-expansion discipline と primary/secondary/tertiary source taxonomy（どのソース型で何が分かるか）
- `standards/systematic-review-methodology.md` §Primary Sources — ACRL "Research as Inquiry" frame: research is an iterative, question-driven process, not a one-shot keyword dump

## Phase 0: Mode Detection and Budget Setup

**MUST run before Phase 1.** Read the `mode:` field from the worker
launch `### Input` section. If absent, default to `quick`.

| Mode | Default budget | Source cap | Search cap | Token cap |
|---|---|---|---|---|
| **quick** (default) | single-pass triangulation | 5 sources | 5 web searches | ~15k tokens |
| **deep** (opt-in) | full audit trail | 15 sources | 20 web searches | ~150k tokens |

User-overridable via `### Input` fields: `max_sources`, `max_web_searches`,
`max_tokens`. Reject budgets below quick floor (15k tokens / 5 sources)
with `BLOCKED: budget below minimum viable quick mode`.

In **quick mode**, this protocol runs in a stripped-down form per the
mode-specific exit rule defined in `standards/confidence-and-claim-language.md`
§Cost-Aware Early-Exit Rule:
- Skip cross-language (EN+JP) parallel search unless natural
- ≥1 primary source per key claim is sufficient (vs ≥2 for deep)
- Exit immediately when all key claims reach Medium confidence
  (medium evidence × medium agreement on the IPCC 3×3 grid)
- Skip MUST `source-citation-checklist` gate (SELF check applies)
- Quick-mode reduction: limit to 3 candidate angles (vs unlimited);
  skip exhaustive lateral exploration across all 5 facets — pick
  the 3 most likely to surface decision-impacting unknowns

In **deep mode**, run the protocol per the existing v4.9.0 grounding:
- Cross-language parallel search REQUIRED
- ≥2 sources per key claim REQUIRED
- Exit at Very high confidence (robust evidence × high agreement)
  per the early-exit rule
- All MUST and SHOULD gates trigger
- Retry on PASS_WITH_NOTES per gate-system.md
- Deep-mode rigor: full lateral + assumption + risk exploration
  (all 5 facets, ≥5 adjacent areas) per the existing Checklist

**Phase hook composition**: This protocol can also run as the
**Brainstorm phase hook** of any other workflow when
`scope_clarity=unclear` is passed in `### Input`. See SKILL.md
§Workflows for the phase-hook composition pattern. In that mode
the brainstorming output feeds directly into the host protocol's
Phase 1 (not a standalone deliverable).

**Budget enforcement**: track source count, search count, token
estimate. On overrun, finish current source verification (atomic),
then return BLOCKED with summary: `"budget overrun: collected N
sources, M searches, ~Tk tokens. Partial result attached. Reply
'expand budget to X' or 'accept partial'."`

See `standards/confidence-and-claim-language.md` §Cost-Aware
Early-Exit Rule for the mode-specific exit thresholds and the
per-claim (not per-deliverable) policy.

## Hard Gate

Do NOT start deep research or produce a report until the exploration
scope has been confirmed with the user.

## Checklist

**Mode discipline**: in quick mode, cap lateral exploration per
Phase 0 budget (3 candidate angles max); in deep mode, follow
existing exhaustive workflow.

Complete each task in order. Each task requires user input before proceeding.
One question per message. Prefer multiple choice when possible.

### 1. Understand the research question

何を調べたいか、なぜ調べたいかを理解する。
- この調査は何の意思決定に使われるか？
- 期限や制約はあるか？

### 2. Map known territory

ユーザーが既に知っていることを整理する。
- 現時点で分かっていることは？
- 既に検討・却下した選択肢は？
- 情報源として何を見たか？

### 3. Lateral exploration — surface adjacent areas

研究テーマに関連する面を横断的に洗い出す。
直接的な回答だけでなく、隣接する領域を探索する：

- **代替アプローチ**: 同じ問題を別の方法で解決している事例は？
- **隣接技術/分野**: 関連するが見落とされがちな技術や分野は？
- **前提条件**: この研究の前提として暗黙に仮定していることは？
- **リスク要因**: 調べずに進んだ場合、何が壊れる可能性があるか？
- **ステークホルダー視点**: 異なる立場（ユーザー、開発者、ビジネス）から見ると
  他に何が重要か？

### 4. Identify unknowns

洗い出した面を分類する：
- **Known unknowns**: 知らないと分かっていること（調べれば分かる）
- **Suspected unknowns**: 多分知らないこと（調べてみないと分からない）
- **Assumption risks**: 正しいと思い込んでいるが未検証のこと

### 5. Prioritize research scope

Impact（判断への影響度）× Uncertainty（不確実性）で優先順位をつける。
高 Impact × 高 Uncertainty = 最優先で調査。

ユーザーに提示して、どこまで調べるか確認する。

### 6. Handoff to research execution

確定した研究範囲を構造化して output する。

## Handoff Output

```
## Research Brainstorming Summary

### Research Question
[元の研究テーマ]

### Known Territory
[既に分かっていること]

### Expanded Scope
[横断探索で発見した追加調査項目]

### Priority Order
1. [最優先] ...
2. [高] ...
3. [中] ...

### Out of Scope (for now)
[今回は調べないと決めた項目]

### Next Step
Load the matching research protocol to start investigation.
```

## Rules

- 一度に一つの質問。複数の質問を一つのメッセージにまとめない
- 「他に何かありますか？」で終わらない — 具体的な隣接領域を提案する
- Phase 3 では最低 5 つの関連面を洗い出すこと
- ユーザーが「十分」と言うまで探索を続ける
- AI は関連面を提案する。調査の優先順位は人間が最終決定する
- 研究テーマが明確で scope 拡張が不要な場合はスキップ → 直接 research protocol へ
