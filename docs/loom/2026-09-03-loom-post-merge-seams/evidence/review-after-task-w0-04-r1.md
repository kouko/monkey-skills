# after-task:W0-04 review round 1 — verdicts (HEAD e0df97e2)

## codex-review-w0-04 (openai) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: code
reviewed_sha: 160658c2
sha: e0df97e2c4e5ad6429ba9ab29e84d1b415555a93
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
    anchor: "loom-code/scripts/loom_checker.py:1766"
    text: "A rename can bypass the close-commit recompute. With --no-renames, renaming a confirmed intent to another matching intent path while changing it to closed yields a deleted path with no after_text and an added path with no before_text. The loop skips both, closing_path remains None, and push.review-only-head accepts the commit without enforcing the one-file, one-line, or checkpoint-parent conditions. This violates REQ-1 and the recomputation principle."
    fix: "Detect closed transitions across delete/add intent-path pairs, or fail closed whenever an intent path is added or deleted at HEAD^ and either side parses as closed. Add a real-git regression test that renames a confirmed intent, closes it, adds the final review-only commit, and expects push.review-only-head to block."
notes:
  - "HEAD^ being a root commit means there is no first-parent transition to inspect; an intent already closed in that root tree is not a non-closed-to-closed transition under REQ-1, so the fix correctly leaves it untouched."
  - "Condition (3) uses check_review_only_head on HEAD^^, reads review.json with git show from the HEAD^^ tree, and resolves its reviewed_sha against HEAD^^^."
  - "The parser safely ignores hunk headers and the no-newline marker; CRLF is stripped, and a second status line is rejected. A BOM prevents the value or key from parsing as a valid closed status rather than creating a valid hidden transition."
  - "--list-rules printed 27 rule IDs, and push.review-only-head describes the close-commit shape."
  - "The requested pytest files could not execute because the read-only environment provides no writable temporary directory; test source and assertions were reviewed directly."
```
