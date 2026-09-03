# after-task:W0-05 review round 2 — verdicts (HEAD a7eca30c / 92a21fe9)

## codex-review-w0-05-r2 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: code
reviewed_sha: 7d055bb8
sha: a7eca30cca48db4d51bbf65e2e0630b640cc1baf
dimension_scores:
  security: NEEDS_REVISION
  architecture: PASS
  correctness: NEEDS_REVISION
  naming: PASS_WITH_NOTES
  tests: NEEDS_REVISION
  refactoring: PASS
  cross-task-coherence: PASS
  external-surface-grounding: PASS
  principles-conformance: NEEDS_REVISION
  deliberate-simplification: PASS
  deletion-first: PASS
findings:
  - severity: fatal
    disposition: BLOCKING — REQ-3 still permits exemption when the committed checker copy has a forbidden mode
    dimension: correctness
    anchor: "loom-code/scripts/loom_checker.py:2636"
    text: "_plumbing_stamp_reason retrieves but ignores the committed checker copy's mode. A checker-copy symlink whose link-target blob begins with the expected stamp, or a regular checker copy with the wrong executable mode, can satisfy the commit-wide stamp gate. A canonical git_exec.py or contract path in that commit is then exempted even though REQ-3 says any symlink or mode mismatch must disable exemption. The existing symlink probe changes the checker path itself, so its later per-path comparison catches the defect and does not cover this sibling-only bypass."
    fix: "Validate the checker-copy tree entry's expected regular-file mode inside _plumbing_stamp_reason before reading its stamp, return a mode or symlink rejection reason, and add a sibling-only test where canonical git_exec.py is the changed path while the committed checker copy is a symlink or has the wrong mode."
  - severity: important
    disposition: BLOCKING — round-1 function-length finding after-task:W0-05-05 is not closed under the stated lens
    dimension: naming
    anchor: "loom-code/scripts/loom_checker.py:2817"
    text: "check_dispatch_covers_tasks still spans 74 lines through line 2890, exceeding the code lens's 50-line hard limit. Extracting _collect_untrailered_commits reduced executable statements but left the function itself over the hard boundary."
    fix: "Shorten the function below 50 source lines, for example by moving its long explanatory contract to a nearby comment or extracting the dispatch-coverage comparison and diagnostic construction."
notes:
  - "Round-1 findings 02, 03, 04, 06, and 07 are closed: rejection reasons reach diagnostics, the mixed-commit assertion distinguishes code from gate, canonical comparison is shared, _plumbing_path_rejection is 47 lines, and the stamp-order docstring is accurate."
  - "Round-1 finding 01 is only partially closed: the stamp is computed once per commit before per-path comparison, and stale or absent-copy tests exist, but the checker-copy mode is not validated."
  - "The requested pytest command could not start because the read-only environment had no usable temporary directory; no passing test result is claimed."
  - "The rule-count command completed and returned 27."
  - "The Codex-copy execution path remains fail-closed: _plumbing_canonical_dir returns None before the unshipped codex_scaffold sibling is imported."
  - "The review skill's code-lens definitions controlled the severity thresholds, function-length check, and requirement for independently run test evidence."
```

## sonnet-review-w0-05-r2 (anthropic) — PASS_WITH_NOTES (carry-forward nit: check_dispatch_covers_tasks 74 lines; all round-1 findings confirmed closed by 7db8f9c1; 109 tests; --list-rules 27)
