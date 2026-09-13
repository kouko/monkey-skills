# Normalize cross-model probe prose — plan
intent: 2026-09-12-normalize-cross-model-probe-prose@e9fbefeb0
charter: 1.0

## Current State Evidence
- Forward: `docs/loom/2026-09-12-host-aware-cross-model-review-language/evidence/probes/test_host_aware_cross_model_review.py` :: `require(text, fragment, source)` performs byte-exact matching for prose and layout alike.
- Reverse: `loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md` :: `one heading and one descriptive cell` is valid prose split by Markdown wrapping.
- Error: finalization reports `missing 'one heading and one descriptive cell'` after the package suite passes.
- Data: the first whitespace-normalized assertions advanced the same probe to the next wrapped prose assertion, isolating the remaining failure mode.
- Boundary: the fenced one-column table assertion must remain byte-exact because its blank lines and row shape are the behavior under test.

## Task DAG

### Wave 0 — finish the evidence boundary

**W0-01 Normalize every prose assertion without weakening layout evidence**  after: none  acceptance: 1, 2, 3
- Files: docs/loom/2026-09-12-host-aware-cross-model-review-language/evidence/probes/test_host_aware_cross_model_review.py
- Test: A1 positive: wrapped-prose-passes; negative: missing-prose-fails. A2 positive: exact-table-passes; boundary: changed-spacing-fails. A3 positive: finalization-generates-attestation; boundary: failed-probe-generates-none.
- Risk: A partial conversion would only move the failure to the next prose assertion; agent-decided — route every prose-presence check through one normalized view while leaving the raw table assertion unchanged.

## Questions asked

① — what — 你要的是：只修復 adversarial probe 對 Markdown 換行過度敏感的問題；一般文字忽略無意義的換行，但表格結構與前後空白仍逐字精確驗證，不改變任何使用者可見行為。回答「對」代表新的 Review 與發布檢查通過後，我可以自動 non-forced push 並建立 Ready PR；merge 仍會另外詢問。對嗎？

## Risks

1. The prior repair normalized only assertions inside one loop; every prose assertion in the program must use the same comparison rule or finalization can fail serially on harmless Markdown wrapping.
2. Normalizing the raw fenced-table assertion would erase the exact whitespace guarantee this evidence exists to protect.
