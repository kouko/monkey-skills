# Citation & Output Standards (Shared Standard)

This file is the single source of truth for research output rules.
Both worker (when producing) and evaluator (when reviewing) reference this file.

## Search Protocol

- Always search in both English AND Japanese
  - EN: natural phrasing ("topic best practices")
  - JP: 「〇〇 使い方」「〇〇 ベストプラクティス」「〇〇 設定」
- Add search in the user's language for regional topics or on request
- Cross-verify claims across 2+ independent sources
- Prefer primary sources: official docs, SEC filings, central bank reports, peer-reviewed papers

## Data Freshness

- Flag sources older than 6 months for fast-moving topics
- Always note the data date for financial/economic data
- "Stale data kills analysis" — explicitly mark outdated figures

## Output Language

- All research output in the `output_language` specified in the launch prompt
- Preserve original language for proper nouns, technical terms, and direct quotes

## Confidence Levels

Tag key conclusions with:
- **高 (High)**: Multiple corroborating primary sources; consensus view
- **中 (Medium)**: 2+ sources agree but some ambiguity or limited data
- **低 (Low)**: Single source, contested, or speculative; clearly hedged

## Fact/Analysis/Speculation

Every claim must be categorized:
- **事實 (Fact)**: Cited, verifiable, attributed to a source
- **分析 (Analysis)**: Reasoned inference from facts; logic chain explicit
- **推測 (Speculation)**: Forward-looking or uncertain; hedged language required

## Structure

- End with actionable recommendations
- Recommendations must be specific and prioritized
- Include confidence levels on recommendations themselves
