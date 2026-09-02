# Branch-end round 28 — re-review after the round-27 fixes (frozen tree a20db4e9)

## codex-review-docs-branch-end-r28 (openai, lens: docs) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: docs
reviewed_sha: c3c4d478
rereview_of:
  R27-C1: "closed — commit 5c9b1c8f pins LC_ALL=C to wc and records 5278/2639."
  R27-C2: "closed — commit 5afd3a7c corrects REQ-8; the recomputed spec blob is 8844407, matching @8844407."
  R27-C3: "closed — commit 5afd3a7c corrects the originally cited plan lines 13 and 146."
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: NEEDS_REVISION
  incorrect-fact: NEEDS_REVISION
  missing-population: PASS
findings:
  - severity: fatal
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-02-simple-loom-flow/spec.md:3"
    text: "The confirmed-behavior comment says kouko re-confirmed the revised REQ-8 text, but the review packet states that this user confirmation is still pending. The blob pin itself is correct: removing this line hashes to 8844407."
    fix: "Remove the false re-confirmation claim and represent the confirmation as pending without inventing a user decision; update the date/comment only after the user actually confirms."
  - severity: important
    dimension: inconsistency
    anchor: "docs/loom/2026-09-02-simple-loom-flow/plan.md:56"
    text: "The old-string sweep still finds operative plan instructions using the obsolete ≤2640 threshold at lines 56, 57, and 179. Unlike line 13, these are not identified as historical values measured by the old locale-dependent method; they contradict the corrected 5278 baseline and ≤2639 threshold."
    fix: "Change all three remaining operative ≤2640 references to ≤2639, or explicitly label them historical and state the old measurement method if preserving them as history."
notes:
  - "The requested pipeline `LC_ALL=C bash loom-code/hooks/session-start </dev/null | wc -w` reproduces 658 on this Mac because LC_ALL applies to bash, not wc. The documented corrected pipeline `bash loom-code/hooks/session-start </dev/null | LC_ALL=C wc -w` reproduces 655."
  - "`check_mechanisms.py --measure` could not be rerun in this read-only environment because Python found no usable temporary directory; the report's claimed exit code was therefore not independently confirmed."```

## opus-review-code-branch-end-r28 (anthropic, lens: code) — PASS_WITH_NOTES

```yaml
verdict: PASS_WITH_NOTES
lens: code
reviewed_sha: c3c4d478
rereview_of: {R27-C1: closed, R27-O1: closed, R27-O2: closed, R27-O3: closed (guard skips; on this Mac the real assertion ran)}
dimension_scores: {security: PASS, architecture: PASS, correctness: PASS, naming: PASS, tests: PASS, refactoring: PASS, cross-task-coherence: PASS_WITH_NOTES, external-surface-grounding: PASS, principles-conformance: PASS, deliberate-simplification: PASS, deletion-first: PASS}
findings:
  - {id: R28-O1, severity: important, dimension: cross-task-coherence, anchor: "docs/loom/2026-09-02-simple-loom-flow/plan.md:56", text: "plan lines 56/57/179 still prescribe ≤2640 as current.", fix: "≤2639 on all three."}
  - {id: R28-O2, severity: nit, dimension: tests, anchor: "loom-code/scripts/test_check_mechanisms.py:664", text: "The skip guard's probe subprocess.run lacks check=True; a missing wc would die with IndexError.", fix: "Pass check=True."}
notes:
  - "655 via `| LC_ALL=C wc -w` and via str.split(); --measure exit 0 (5278 matches); 1006 passed; --self-test exit 0."
  - "push gate at the last review-only head 5ada2a26: only push.reviewed-sha; 19 adversarial probes exit 0."
  - "confirmed-behavior @8844407 matches the blob; the user's re-confirmation is outside scope."
```

## Disposition

- R28-C1 (Codex, fatal): the confirmed-behavior comment claimed a re-confirmation the user had not given — the station's own wording error. Fixed in the docs commit after this frozen tree: the comment now says the re-confirmation is pending; the user is asked for it before the push.
- R28-C2 / R28-O1 (plan ≤2640 ×3): fixed in the same docs commit.
- R28-O2 (nit): accepted, not fixed — a test edit after the final blind run would reopen the records-only claim; carried to the first post-merge change together with R24-O2.
- Round 29: two docs-lens legs (Codex + sonnet) on the frozen tree; no code changed after 5c9b1c8f.
