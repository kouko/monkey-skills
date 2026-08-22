# Barred-contract arm 2 — sonnet, 2026-08-22

Second run of the contract carrying the no-op bar, dispatched in parallel with
arm 1 under identical blind framing. `standards_version` self-reported 0.94.0
— this arm read `plugin.json` after Task 3's bump landed mid-flight. Both arms
held the same contract text; only the version string they sampled differs.

## Verdict block (verbatim)

```
verdict: NEEDS_REVISION

dimension_scores:
  security: PASS
  architecture: PASS
  correctness: NEEDS_REVISION
  naming: PASS
  tests: PASS
  refactoring: PASS
  cross-task-coherence: PASS
  external-surface-grounding: PASS
  principles-conformance: N/A
  deliberate-simplification: PASS
  deletion-first: NEEDS_REVISION

findings:
  - severity: 🔴 fatal
    dimension: correctness
    where: mod.py:42-44
    note: >
      The `display_label` docstring claims "A record whose `label` disagrees
      with its filename really does surface here under the filename stem".
      This is false. `header.get("label", record.stem)` returns the stem ONLY
      when the `label` key is absent — a present-but-disagreeing label is
      returned as-is. Verified by execution: a record at `stemname.txt` with
      `label: totally-different-label` returns `"totally-different-label"`.
      A scheduler built to this doc's instruction would fail to match real
      disagreeing-label records.

  - severity: 🟡 should-fix
    dimension: correctness
    where: mod.py:51-53
    note: >
      "Negative values are rejected rather than clamped." Verified by
      execution: `_RETRY_RE` only captures `\d+`, so `retries: -3` never
      matches — `parse_header` drops the key and `retry_budget` silently
      returns `DEFAULT_RETRIES` (3). The reject branch is unreachable for the
      realistic malformed-input case the docstring's own rationale invokes.
      The practical fallback is benign rather than dangerous, hence 🟡.

  - severity: 🟡 should-fix
    dimension: deletion-first
    where: mod.py:26-27
    note: >
      "Keys absent from the text are absent from the result" is a mechanism
      clause the `parse_header` body already shows directly. Flag the
      mechanism clause; the reason clause that follows must survive the edit —
      it is the counterfactual reason, not a mechanism the code shows.

  - severity: 🟡 should-fix
    dimension: deletion-first
    where: mod.py:26-27
    note: >
      A naive fix to the prior finding would strand the reason clause. The fix
      must keep the reason attached to a shortened lead-in, not delete the
      sentence wholesale.
```

## Grading note

Deletion class 1/2 — caught the welded mechanism-and-reason sentence and named
the stranding risk, twice, but did not flag the pure restatement in
`display_label`'s first line. It scored the dimension NEEDS_REVISION rather
than declaring it a no-op, so the route this arc closed stayed closed here too.

Control clean: it left the module docstring's intent sentence alone, and named
`parse_header`'s "never validates … by design" as a kept absence claim rather
than passing over it silently.

The two barred arms therefore disagree on both edges — arm 1 caught one more
planted item AND drew the exercise's first control false-positive. That is one
sample of each, not a rate.
