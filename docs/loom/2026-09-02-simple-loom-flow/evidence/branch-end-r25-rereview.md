# Branch-end round 25 — re-review on the frozen tree 6089e62b

## codex-review-docs-branch-end-r25 (openai, lens: docs) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: docs
reviewed_sha: c3c4d478
rereview_of:
  R24-C1: "closed — the second addendum identifies 1639e337 as the final tested tree; git diff 1639e337..HEAD contains only blind-run-report.md and review.json, and the required non-record diff after e2a8df91 is empty."
  R24-C2: "closed — CHANGELOG now states 27 rules, identifies --list-rules as the source of truth, and the command currently returns 27."
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: PASS
  incorrect-fact: NEEDS_REVISION
  missing-population: PASS
findings:
  - severity: fatal
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-02-simple-loom-flow/evidence/branch-end-r24-rereview.md:60"
    text: "The disposition says the four prose adversarial entries were removed from review.json probes[], but the final tree still contains all four: spec-redteam-r5, w0-checkpoint-reviews, w2-checkpoint-reviews, and w3-checkpoint-reviews. The probe array is unchanged at 25 entries since e2a8df91."
    fix: "Remove those four entries from review.json probes[] as promised, update the report's affected probe totals from 25 to 21, and record the resulting records-only correction."
notes: []```

## sonnet-review-docs-branch-end-r25 (anthropic, lens: docs) — PASS

```yaml
verdict: PASS
lens: docs
reviewed_sha: c3c4d478
rereview_of: {R24-C1: closed (records-only claim reproduced: exactly three files changed 40442b1e..1639e337, all from f600c281), R24-C2: closed (CHANGELOG 27, --list-rules 27)}
dimension_scores: {omission: PASS, ambiguity: PASS, inconsistency: PASS, incorrect-fact: PASS, missing-population: PASS}
findings: []
notes:
  - "Every number in both addenda reproduced live: 1005 passed; 27 rules; check_mechanisms exit 0 (658/2640); --self-test passed, tree clean; push blocked on exactly reviewed-sha / probes-adversarial / second-vendor-honoured / frozen-store-untouched."
  - "R24-O2 verified as honestly left unfixed (docstring 'below'), carried post-merge."
  - "(Incorrect in this note, caught by the Codex leg:) claimed the four prose probes were already gone at the frozen tree; they were not — see R25-C1."
```

## Disposition

- R25-C1 (Codex): the round-24 disposition sentence read as already done while the removal was scheduled for the review-only commit. Fixed in the record-only commit that follows the frozen tree: the four entries are removed from `probes[]` now, the report's probe counts say 21 (and explain the later re-run adds 19), and the disposition sentence is reworded. No program/hook/skill file changed.
- The sonnet leg's note claiming the probes were already gone is wrong; the two-vendor pair caught it. Recorded as-is.
- Round 26: same two docs-lens legs on the frozen tree after this commit; the only delta is review.json probes[], the report's three count sentences, and the round-24/25 evidence files.
