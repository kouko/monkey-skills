# Spec review round 11 (narrow: REQ-1 v12 regenerate-and-compare) — verdicts (blob e660c1d, HEAD c4a2dbee)

## codex-review-spec-11 — PASS_WITH_NOTES

```yaml
verdict: PASS_WITH_NOTES
lens: spec
reviewed_sha: 160658c2
dimension_scores:
  omission: PASS_WITH_NOTES
  ambiguity: PASS
  inconsistency: PASS
  incorrect-fact: PASS
  missing-population: PASS
  spec-conformance: PASS_WITH_NOTES
  design-conformance: "N/A — no DESIGN.md"
  principles-conformance: PASS
  user-judgment-leak: PASS
findings:
  - severity: important
    dimension: omission
    anchor: "docs/loom/2026-09-03-loom-post-merge-seams/spec.md:6"
    text: "Round-9 F2 remains only partially closed: the trigger's intent template still comes from an unasserted live manifest. If that bundled value drifts or is mistyped, no real intent path matches and push.review-only-head silently treats the commit as not touching an intent. Blob equality does not address this trigger-level fail-open."
    fix: "Before matching paths, fail closed if the manifest's intent template is absent or differs from the checker-supported canonical template; name push.review-only-head and the unexpected template in the diagnostic."
notes:
  - "spec-R29 is closed: requiring exactly one status: line in each blob and byte equality after replacing that line rejects the headingless duplicate-status last-status-wins construction."
  - "Round-9 F4 is closed: a body decoy cannot be changed while the real status remains untouched because the blobs must differ only at their sole status: line."
  - "Round-9 F1 and F3 remain closed by the 100644 endpoint-mode requirement and regenerate-and-compare equality; F5 remains closed by the explicit sequencing restriction. F2 remains open as the finding above."
  - "spec-R24 is closed by requiring mode 100644 on both sides."
  - "spec-R25 is closed as to source selection and single naming: the template comes from the running checker's contract package through one named constant; its separate silent-drift issue is the carried F2 finding."
  - "spec-R26 is closed: HEAD^ supplies one grammar-valid canonical closed status line, and byte equality rejects any additional changed or trailing bytes."
  - "spec-R27 is superseded and closed more strongly: blob regeneration removes dependency on headings or hunk-line boundary calculations."
  - "spec-R28 is closed: confirmation, maintain-created, and amendment commits are explicitly forbidden at HEAD^ before a review-only push and must occur earlier."
  - "The three conditions remain implementable: one matching path with regular-file mode at both endpoints; exact regenerated-blob equality using the sole status line and STATUS.fullmatch closed values; and a checkpoint at HEAD^^ tied to HEAD^^^."
  - "The structural trigger covers Acceptance #1's negative cases. Extra bytes in the close commit break blob equality; skipped review breaks the verdict-sha tie or checkpoint shape."
  - "The ee5e104e commit closing 2026-09-02-simple-loom-flow touched four paths, so it would fail if it were HEAD^ of a review-only push. Its immediate child was the current change's intent-confirmation commit, not a review-only commit; an attempted push there already had the wrong HEAD shape, and later checkpoints place ee5e104e earlier than HEAD^."
  - "The amendment tightens the existing push.review-only-head rule without adding a rule or waiver, preserves repository recomputation, introduces no user judgment, and does not contradict REQ-2, Design decision 1, or the rejected alternatives."
```

## sonnet-review-spec-11 — PASS_WITH_NOTES (important: same manifest-drift fail-open, untracked; nit: the exactly-one-status-line count must be a raw scan, not parse_document). Notes: v12 closes spec-R29 and round-10 F4; W1-04's commit touches four paths so it is never a legal HEAD^.
