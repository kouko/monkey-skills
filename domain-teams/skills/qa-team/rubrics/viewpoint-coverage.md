# Viewpoint Coverage Gate

## Scope Boundary

Review the _viewpoint list_ produced by `protocols/test-viewpoint-extraction.md`
or the viewpoint section of a TEST-PLAN.md. Do NOT review individual test cases,
test code, or execution details — those belong to other gates.

This gate draws its evaluation axes from ASTER テスト設計コンテスト U-30 審査基準,
the Japanese QA community's de-facto rubric for test design quality. See
`standards/test-viewpoints-ja.md` for methodology references.

## Flag Definitions

### Viewpoint Breadth

- 🔴 **Fatal**: Only one concern axis represented (e.g., all viewpoints are functional)
- 🟡 **Warning**: Two axes represented but a relevant third is clearly missing
  (e.g., a user-facing system has functional + non-functional but no accessibility)
- 🟢 **Clear**: At least three concern axes represented with rationale for inclusion

### Viewpoint Traceability

- 🔴 **Fatal**: Test cases reference no viewpoint IDs (viewpoints are decorative, not load-bearing)
- 🟡 **Warning**: Some test cases cite viewpoints but many do not, with no stated reason
- 🟢 **Clear**: Every non-trivial test case cites at least one V-NN ID from the viewpoint list

### Methodology Citation

- 🔴 **Fatal**: No methodology named (extraction appears ad-hoc with no reference to
  VSTeP/HAYST/ゆもつよ/mind-map/6W2H)
- 🟡 **Warning**: Methodology named but applied inconsistently (e.g., "VSTeP" stated
  but no NGT tree or MECE verification present)
- 🟢 **Clear**: Methodology cited from `standards/test-viewpoints-ja.md` and applied
  consistently; primary source (西康晴 / 秋山浩一 / 湯本剛 / 池田暁) referenced

### DR Readiness (設計レビュー可読性)

- 🔴 **Fatal**: Viewpoint list relies on author's tacit knowledge; non-authors cannot
  determine what each viewpoint covers from the document alone
- 🟡 **Warning**: Most viewpoints readable by non-authors but 1-2 require author
  clarification
- 🟢 **Clear**: A peer who did not participate in extraction can understand each
  viewpoint's scope and rationale from the document alone

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- This is a SHOULD gate. If the project genuinely has no need for viewpoint
  extraction (single-component bug fix, trivial scope), the gate can be skipped
  with an explicit rationale logged in the TEST-PLAN.md.
- Evaluate against the stated methodology's own completeness criteria — a
  HAYST法 orthogonal table is complete differently from a VSTeP NGT tree.
- When issuing NEEDS_REVISION for Breadth, name at least one concrete axis
  that is missing (e.g., "accessibility viewpoint absent for user-facing UI").
- Do not penalize methodology choice — VSTeP / HAYST / ゆもつよ / mind-map are
  all acceptable. Penalize only inconsistent application.

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: Specific location in the viewpoint list or TEST-PLAN.md with quote
3. **Suggested Addition** (for Breadth warnings): Concrete viewpoint axis to add
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

PASS_WITH_NOTES issues will be auto-revised without human review.
Be specific about what to add or clarify.

## Sources

- [ASTER テスト設計コンテスト U-30 審査基準](https://www.aster.or.jp/testcontest/u30.html) —
  审查基準 weighting detailed design (30 pts) and workflow consistency (10 pts)
- `standards/test-viewpoints-ja.md` — methodology reference
