# Historical replay comparison

## Verdict

**GRADEABLE.** Both flows applied the same committed plan and six fixed task
patches in the same order. Their final tree hashes are identical, all permanent
commands passed, and both independent branch-end reviewers found important or
fatal defects without seeing the historical oracle.

The candidate runtime is pinned to
`6bca3513bf6ff997419fb73a6a56ea8613db62ac`, the last implementation commit
before replay evidence was written. Before final release, its runtime-contract
bytes must still match the first branch-end-review parent; otherwise this replay
becomes **UNGRADABLE** rather than evidence for a speed claim.

## Structural time result

| Metric | Baseline | Candidate | Reduction |
|---|---:|---:|---:|
| Build-time formal-review dispatches | 2 | 0 | 2 (100%) |
| Checkpoint blocking time | 1,086 s | 0 s | 1,086 s (18m06s; 100%) |
| Defect-fix time | unavailable | 0 s | not claimed |

This is a structural wait-time result for the replayed build, not a claim that
every delivery becomes 18 minutes faster. The baseline review record has no
separate fix-implementer dispatch timestamp, so defect-fix time cannot be
derived and is not folded into the saving.

## Integrity and quality controls

- Baseline final tree: `e6201f8f13d18a36ccd5362204ee1c5d7d5aa2b7`.
- Candidate final tree: `e6201f8f13d18a36ccd5362204ee1c5d7d5aa2b7`.
- Both flows observed the intended adversary RED (`19 failed, 7 passed`) after
  W0-01 and GREEN (`26 passed`) after W0-02.
- Both flows ended with `1096 passed` in the permanent package suite.
- The candidate dispatched no `after-task:` or `wave-end:` formal review. It
  kept task tests and one complete branch-end checkpoint.
- Codex (`gpt-6`) and Claude (`claude-opus-5`) both returned
  `NEEDS_REVISION`, demonstrating that the retained endpoint checkpoint still
  detects consequential defects in this historical target.

## Hidden-oracle comparison

The oracle was opened only after both verdicts were recorded.

| Oracle root cause | Outcome at final target | Evidence |
|---|---|---|
| Dot-directories counted as plugins | Inapplicable after later replay task fixed it | `test_loom_checker_push.py:2355-2371` preserves the regression case. |
| Change-folder exclusion omitted `spec.md` | Inapplicable after later replay task fixed it | `loom_checker.py:2493-2501` explicitly includes `spec.md`; `test_loom_checker_push.py:2375-2384` exercises it. |
| Reviewer floor contradicted ratified principles | Rediscovered at the same policy boundary | Both reviewers found paths that could receive the small-lane floor despite belonging to full-lane categories. |
| Published verdict rule claimed a fixed two-reader floor | Inapplicable: the canonical replay target already carries the lane-aware wording | `loom-code/scripts/loom_checker.py:176` names one reviewer for small and two for full; the stale Codex mirror finding is a different publication defect and is not credited as rediscovery. |

The endpoint review therefore rediscovered the one oracle concern still
relevant to the completed target. The other three were already removed by
later fixed task patches or canonical wording, with executable or line-level
evidence present before branch-end review.

## Fixture corrections made before execution

- Used the actual `check_version_bump.py` signature with explicit `--base` and
  `--head`.
- Split manifest synchronization into one invocation per plugin.
- Removed a command naming `scripts/test_skill_word_caps.py`, which does not
  exist in the pinned replay target.

These corrections repair invalid harness commands only; they do not change the
fixed task patches, their order, the target source tree, or either flow's review
policy.
