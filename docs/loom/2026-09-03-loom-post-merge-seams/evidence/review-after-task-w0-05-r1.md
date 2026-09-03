# after-task:W0-05 review round 1 — verdicts (HEAD 26185d8e)

## codex-review-w0-05 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: code
reviewed_sha: 7d055bb8
sha: 26185d8ed87b9df7a602600a127ae0a04a071455
dimension_scores:
  security: PASS
  architecture: PASS_WITH_NOTES
  correctness: NEEDS_REVISION
  naming: PASS_WITH_NOTES
  tests: NEEDS_REVISION
  refactoring: PASS_WITH_NOTES
  cross-task-coherence: PASS
  external-surface-grounding: PASS
  principles-conformance: NEEDS_REVISION
  deliberate-simplification: PASS
  deletion-first: PASS
findings:
  - severity: fatal
    disposition: BLOCKING — violates REQ-3 and can exempt a plumbing path against the wrong scaffold version
    dimension: correctness
    anchor: "loom-code/scripts/loom_checker.py:2672"
    text: "Version equality is checked only when the changed path is loom_checker.py. A commit changing only git_exec.py or contract/<rel> can be exempt even when the committed checker copy is absent or stamped with an older version, because those branches compare their own blob and mode without first validating the checker copy's stamp. REQ-3 requires the copy's stamp to equal codex_scaffold.plugin_version() before any per-path blob comparison."
    fix: "Before filtering any plumbing path for a commit, read that commit's CHECKER_COPY entry, require regular-file mode, extract exactly one stamp, and require its version to equal plugin_version(); only then perform the selected path's blob-and-mode comparison. Add cases where an otherwise canonical sibling and contract file are changed while CHECKER_COPY is missing or stale."
  - severity: important
    disposition: BLOCKING — the requested failure diagnostics cannot distinguish corruption classes
    dimension: correctness
    anchor: "loom-code/scripts/loom_checker.py:2753"
    text: "A rejected plumbing path loses the comparison failure reason. Version, mode, blob, deletion, symlink, missing canonical, and no-canonical execution all collapse to the generic message that the commit touches gate work, so the diagnostic does not say which required check failed."
    fix: "Return a structured match result containing the path and failure reason, retain those results while filtering, and include them in push.dispatch-covers-tasks diagnostics for untrailered commits."
  - severity: important
    disposition: BLOCKING — the test passes before the behavior it claims to prove exists
    dimension: tests
    anchor: "loom-code/scripts/test_loom_checker_push.py:1816"
    text: "The mixed-commit test only asserts that the rule blocks and that stderr contains code. Before W0-05, the same commit already blocks with both code and gate kinds, so this test is GREEN without the exemption and does not prove that the plumbing path was removed per path."
    fix: "Expose path-level or kind-level diagnostics and assert that the ordinary code path remains trailer-bearing while the canonical plumbing path is specifically classified as exempt; preserve RED-before-GREEN evidence for that assertion."
  - severity: important
    disposition: BLOCKING — exceeds the code lens's 50-line hard function limit
    dimension: naming
    anchor: "loom-code/scripts/loom_checker.py:2625"
    text: "_plumbing_path_matches_canonical spans 63 lines and combines entry lookup, version parsing, mode policy, canonical routing, and four content-rendering strategies."
    fix: "Split canonical expectation construction and checker-stamp validation from the small per-path comparison, keeping each helper focused and making structured mismatch reasons straightforward."
notes:
  - "The requested pytest command could not start because the read-only environment had no usable temporary directory; no test result is claimed from this review."
  - "The 11 adversarial probes were committed before the implementation; the genuine-refresh case carried a strict xfail marker until W0-05."
  - "The Codex-copy path is fail-closed: _plumbing_canonical_dir returns None before the lazy codex_scaffold import, so the unshipped sibling module is not required."
  - "The rule-count command completed and returned 27."
```

## sonnet-review-w0-05 (anthropic) — NEEDS_REVISION (blocking: check_dispatch_covers_tasks 106 lines; _plumbing_path_matches_canonical repeats the compare pattern four times and is 51+ lines; carry-forward nit: docstring claims the version gates the blob read). Note: REQ-3 semantics traced correctly; 107 push+probe tests pass; --list-rules 27.
