# W1-01 real Ship-to-push-gate replay measurement

## Scope and controls

- Baseline: `9d009c49e02a52c4838dba30a88501e0bbe79ab0`.
- Candidate: `c0a93c6fff392769a95192b7f31838c30d95b489`, including the immutable-source safety fix.
- Boundary: baseline runs its real explicit `loom_checker.py push` preflight and then its real versioned PreToolUse hook; candidate runs its real versioned hook only. Timing starts immediately before the first checker process and ends when the hook returns its actual release/block result. The intercepted Git push is not executed, so the boundary ends before network transfer.
- Version isolation: the harness uses `git archive` to extract each revision's `loom_checker.py`, `git_exec.py`, `codex_scaffold.py`, `loom_record_fire.py`, `hooks/hooks.json`, and complete `contract/` package. It executes the hook command read from that revision's `hooks.json`; it never imports the current checkout's checker as a substitute.
- Fixed fixture: one accepted checkpoint is copied unchanged into every arm. Its HEAD was `4602eb6de2ef769d0cb25ff8c181783343871bcf` in this run, on branch `work`. Both hooks receive the same literal `4602eb6de2ef769d0cb25ff8c181783343871bcf:refs/heads/work` refspec, which is the candidate's required full-current-SHA form.
- Instrumentation: the declared repository command is `python3 evidence/package_suite.py`. It sleeps `0.080` seconds and appends its own `time.monotonic_ns()` duration to an arm-local log outside the repository. Counts and per-invocation durations come only from those executed-command records; total boundary timing also uses `time.monotonic_ns()`.
- Sampling: seven paired samples alternate arm order: baseline first on odd samples and candidate first on even samples.

## RED to GREEN

After changing the evidence oracle but before replacing the synthetic replay:

```text
uv run --isolated --with pytest --with pyyaml python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py::test_revisions_execute_versioned_real_gate_entrypoints -q --tb=line
```

Result: `1 failed in 0.41s`. The failure was `AttributeError: 'Observation' object has no attribute 'entrypoints'`, proving that the old machinery exposed no real checker or hook execution.

After implementing the versioned replay:

```text
uv run --isolated --with pytest --with pyyaml python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py -q --tb=line
```

Result: `2 passed in 28.26s`.

The recorded observations came from:

```text
uv run --isolated --with pyyaml python docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py
```

## Observations

`B→C` means baseline then candidate; `C→B` means candidate then baseline. Invocation seconds are the durations written by the declared package command; boundary seconds include the real checker, checkpoint validation, package command, adversarial commands, repository-state checks, and hook dispatch.

| Sample | Order | Baseline package seconds | Baseline calls | Baseline boundary seconds | Baseline gate rc / verdict | Candidate package seconds | Candidate calls | Candidate boundary seconds | Candidate gate rc / verdict |
|---:|:---:|:---|---:|---:|:---|:---|---:|---:|:---|
| 1 | B→C | 0.090019083, 0.090023375 | 2 | 2.119113042 | 0,0 / release | 0.090020917 | 1 | 1.143173125 | 0 / release |
| 2 | C→B | 0.090022500, 0.088092417 | 2 | 2.085415667 | 0,0 / release | 0.081608666 | 1 | 1.145803334 | 0 / release |
| 3 | B→C | 0.083752500, 0.080127291 | 2 | 2.121336084 | 0,0 / release | 0.090017333 | 1 | 1.168604834 | 0 / release |
| 4 | C→B | 0.082918334, 0.080492084 | 2 | 2.190963375 | 0,0 / release | 0.081881041 | 1 | 1.206816875 | 0 / release |
| 5 | B→C | 0.090017875, 0.090022458 | 2 | 2.132918875 | 0,0 / release | 0.090014042 | 1 | 1.154450250 | 0 / release |
| 6 | C→B | 0.089089542, 0.080990250 | 2 | 2.115676667 | 0,0 / release | 0.085001333 | 1 | 1.175409417 | 0 / release |
| 7 | B→C | 0.090013500, 0.090022708 | 2 | 2.133991250 | 0,0 / release | 0.090022791 | 1 | 1.152933083 | 0 / release |
| Median | — | — | 2 | 2.121336084 | release | — | 1 | 1.154450250 | release |

Observed totals are 14 baseline package-command invocations and 7 candidate invocations. Every candidate sample invoked the declared command exactly once and fewer times than its paired baseline. Both arms produced the same real gate verdict in every pair. Candidate median local-gate wait was `0.966885834` seconds lower, or 45.6% lower for this controlled fixture.

## Limitations

This measurement establishes invocation count, equal checker verdict, and local wait only for the fixed fixture and revisions above. The `0.080`-second package command makes duplicate execution visible without running this repository's complete suite fourteen additional times. Absolute and percentage savings will vary with repository, package suite, machine load, and filesystem scheduling. The hook was allowed to decide, but the intercepted Git command was deliberately not executed; the separate immutable-source attack probes use a temporary local bare remote to verify publication safety without any external or network push.
