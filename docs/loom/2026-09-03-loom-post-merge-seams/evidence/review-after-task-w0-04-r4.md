# after-task:W0-04 review round 4 — verdicts (HEAD f8da3b18)

## codex-review-w0-04-r4 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: code
reviewed_sha: 160658c2
sha: f8da3b184028e3a12649ac6fcaf68dee5f509b76
dimension_scores:
  security: FAIL
  architecture: PASS
  correctness: FAIL
  naming: PASS
  tests: FAIL
  refactoring: PASS
  cross-task-coherence: PASS
  external-surface-grounding: PASS
  principles-conformance: PASS
  deliberate-simplification: PASS
  deletion-first: PASS
findings:
  - severity: fatal
    disposition: BLOCKING
    dimension: correctness
    anchor: "loom-code/scripts/loom_checker.py:1863"
    text: "git_raw_text decodes blob bytes with surrogateescape, but regeneration re-encodes with strict UTF-8. An otherwise byte-preserving close commit whose unchanged content contains a non-UTF-8 byte raises UnicodeEncodeError instead of performing the required blob comparison, so the gate does not implement REQ-1's byte-equality condition for all blobs."
    fix: "Encode regenerated text with errors='surrogateescape', or perform regeneration directly on bytes; add a negative/positive regression covering an unchanged non-UTF-8 byte outside the status line."
  - severity: important
    disposition: BLOCKING
    dimension: correctness
    anchor: "loom-code/scripts/loom_checker.py:1979"
    text: "The malformed checkpoint-parent diagnostic discards check_review_only_head's computed detail and reports only 'touches something else'. It names the commit and expectation but not the actual paths, contrary to the required expected/got diagnostic."
    fix: "Preserve and include the underlying checkpoint failure detail or recompute the touched-path list, and strengthen test_a_close_commit_whose_parent_is_not_a_checkpoint_is_blocked to assert the actual got value."
notes:
  - "The requested pytest command could not start because the read-only sandbox provides no writable temporary directory; pytest raised FileNotFoundError before collection. The rule-count command ran and returned 27."
```

## sonnet-adversary-w0-04-r4 — NEEDS_REVISION (fatal: CRLF ending collapsed in regeneration → fixed 6f7a19a5; nit carry-forward: CRLF probes must pin core.autocrlf)

## sonnet-review-w0-04-r4 — PASS_WITH_NOTES (reviewed fcd5905e; independently reproduced and confirmed fixed the surrogateescape crash; carry-forward: check_close_commit_shape body ~66 lines > 50-line lens cap; probe 10 docstring stale)
