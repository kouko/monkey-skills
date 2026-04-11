# Research Quality Review Gate

## Primary Sources

- `standards/source-quality-and-evidence.md` — primary/secondary/tertiary taxonomy + Kovach "Discipline of Verification" for judging source quality and cross-verification rigor
- `standards/systematic-review-methodology.md` — Booth 5-element argument model (for reasoning quality) + PRISMA 2020 27-item checklist (for completeness)
- `standards/confidence-and-claim-language.md` — IPCC/Kent calibrated language + Fact / Analysis / Speculation taxonomy for judging calibration

## Prerequisites

This gate runs AFTER the source citation checklist passes.
Do not re-check citation presence — focus on depth and quality.

## Flag Definitions

### Source Quality & Cross-Verification

Grounded in `standards/source-quality-and-evidence.md`
§The Primary / Secondary / Tertiary Taxonomy and §Journalism of
Verification Discipline (Kovach & Rosenstiel 2021).

- 🔴 **Fatal**: Key conclusion relies on a single source with no cross-verification (violates Kovach cross-verification discipline)
- 🔴 **Fatal**: Primary sources available (official docs, filings, reports) but only secondary sources used
- 🟡 **Warning**: EN and JP sources not both consulted (missing language coverage)
- 🟡 **Warning**: Key factual claim is doubtful and external verification (web search, MCP tools) was attempted but could not confirm or deny it
- 🟢 **Clear**: Claims cross-verified across 2+ independent sources; primary sources preferred

### Reasoning & Logic

Grounded in `standards/systematic-review-methodology.md`
§Booth's 5-Element Argument Model (claim + reasons + evidence +
warrants + acknowledgments). A sound argument makes each element
explicit; missing warrants or missing acknowledgments of
counter-evidence are the typical failure modes.

- 🔴 **Fatal**: Obvious logical fallacy in the reasoning chain (correlation ≠ causation, survivorship bias, etc.)
- 🔴 **Fatal**: Conclusion contradicts evidence presented in the same report
- 🟡 **Warning**: Assumptions (warrants) are implicit — not stated explicitly
- 🟢 **Clear**: Reasoning chain is sound; all 5 Booth elements (claim, reasons, evidence, warrants, acknowledgments) are explicit

### Completeness

Grounded in `standards/systematic-review-methodology.md` §PRISMA
2020 — the 27-Item, 7-Section Checklist. For formal systematic
reviews the PRISMA checklist is the standard; for lightweight
research the spirit (explicit scope, search, screening,
exclusions) still applies.

- 🟡 **Warning**: Major aspect of the topic is not addressed (obvious gap)
- 🟡 **Warning**: Counter-arguments or risks are not discussed
- 🟢 **Clear**: All relevant aspects covered; counter-positions acknowledged

### Actionability

Grounded in `standards/source-quality-and-evidence.md` §Journalism
of Verification Discipline (Kovach & Rosenstiel 2021). Kovach's
discipline demands the report serve the reader's decision-making,
not the author's performance of knowledge.

- 🟡 **Warning**: Recommendations are vague ("consider improving X" without specifics)
- 🟡 **Warning**: No clear next steps or actionable items at the end
- 🟢 **Clear**: Recommendations are specific, prioritized, and actionable

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Special Rule for Research

PASS_WITH_NOTES auto-revision is limited to formatting, clarity, and
structural issues only. If the warning flag relates to factual gaps
or missing analysis, it must be escalated to the user (who may
re-dispatch worker with additional search instructions).

## Output Format

1. **Flags**: `[🔴 Dimension]` or `[🟡 Dimension]` with evidence
2. **Fix Instruction**: What the worker should change or research further
3. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

Never sugar-coat. Be direct and specific.
