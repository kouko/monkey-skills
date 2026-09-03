# after-task:W0-04 review round 2 — verdicts (HEAD bab6103b; round-1 sonnet leg also landed here)

## codex-review-w0-04-r2 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: code
reviewed_sha: 160658c2
sha: 70b280af7bc0baead482d06d26c14286de10e2ae
dimension_scores:
  security: PASS
  architecture: PASS
  correctness: NEEDS_REVISION
  naming: PASS
  tests: PASS_WITH_NOTES
  refactoring: PASS
  cross-task-coherence: PASS
  external-surface-grounding: PASS
  principles-conformance: NEEDS_REVISION
  deliberate-simplification: PASS
  deletion-first: PASS
findings:
  - severity: fatal
    dimension: correctness
    anchor: "loom-code/scripts/loom_checker.py:1797"
    text: "The recompute does not run only when HEAD^ introduces closed. The `(before_closed and after_text is None)` branch classifies deletion of an already-closed intent as a closing transition, so an ordinary commit deleting such a file is subjected to the close-commit shape and blocked. The added half already detects a rename ending in closed under --no-renames; treating the deleted half as a transition is unnecessary and contradicts REQ-1."
    fix: "Trigger only when the after-tree path parses as closed and the corresponding before-tree path does not. Keep added closed paths as transitions; let a rename be detected from its added path and fail condition (1). Add a real-git regression where HEAD^ only deletes an already-closed intent and assert push.review-only-head is absent."
  - severity: important
    dimension: correctness
    anchor: "loom-code/scripts/loom_checker.py:1806"
    text: "The close-shape failure messages identify the offending commit only symbolically as HEAD^ or HEAD^^; they do not name the actual offending commit hash required by REQ-1. The root-parent diagnostic also states no explicit expected value."
    fix: "Include close_sha or pre_close_sha in every close-shape diagnostic and state the concrete expected shape or parent value. Add assertions that each negative case's stderr contains the offending commit hash and expected value."
  - severity: important
    dimension: tests
    anchor: "loom-code/scripts/test_loom_checker_push.py:391"
    text: "The rename and newly-added regressions assert only that push.review-only-head appears. They do not prove that the close-shape recompute fired for the intended transition or that the diagnostic names the offending commit and expected value; another failure under the same reused rule id would satisfy them."
    fix: "Assert the specific close-shape diagnostic, including the close commit hash and expected one-path or checkpoint-parent value, for both regressions."
notes:
  - "788a8e1f closes the reported rename and newly-added-closed bypass in the transition search; source inspection confirms the added path detects a real --no-renames rename."
  - "A root HEAD^ containing an already-closed intent is an added closed transition against Git's empty tree and must fail condition (3); an ordinary root HEAD^ remains untouched."
  - "Condition (3) reuses check_review_only_head on HEAD^^, reads review.json from the HEAD^^ tree with git show, and resolves its reviewed_sha against HEAD^^^."
  - "The -U0 parser excludes file headers, ignores hunk and no-newline marker lines, strips CRLF, and rejects two changed status lines. A BOM on the status key prevents it from parsing as a closed transition."
  - "The requested pytest invocation could not start because the read-only environment has no usable temporary directory; test sources and RED-producing historical diffs were inspected instead."
  - "loom_checker.py --list-rules produced 27 ids, and push.review-only-head mentions the close-commit shape."
```

## sonnet-review-w0-04 (anthropic, round-1 leg, reviewed bab6103b) — NEEDS_REVISION

Findings: important — deletion of an already-closed intent classified as a transition (loom_checker.py:1797); important — diagnostics name HEAD^/HEAD^^ symbolically, not the sha (:1811, :1838, :1853, :1865); nit — no test for a root commit adding an already-closed intent; nit — check_close_commit_shape ~165 lines, extract condition (3). Notes: verified the round-1 rename fatal closed by 788a8e1f (RED/GREEN via git show into an isolated copy); the branch moved five times during the review, all checks re-run on an isolated git archive of bab6103b.

## sonnet-review-w0-04-r2 (anthropic) — NEEDS_REVISION

Findings: important — same deletion false-block (reproduced: git rm of a closed intent blocked with '5 removed / 0 added'); important — function length ~166 lines (naming dimension threshold 100), extract condition (3); nit — probe 5 docstring stale ('DEFECT ... fires today') while its assertion passes. Notes: RED/GREEN of 788a8e1f's two tests re-verified against efbd0198 in an isolated copy; 78/78 push tests and 6/6 probes at bab6103b; --list-rules 27.
