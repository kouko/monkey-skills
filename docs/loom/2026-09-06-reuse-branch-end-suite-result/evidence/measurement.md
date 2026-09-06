# W1-01 real Ship-to-push-gate replay measurement

## Scope and controls

- Baseline: `9d009c49e02a52c4838dba30a88501e0bbe79ab0`.
- Candidate: `b197c123fb1c0cc513fc56b3262f15aefd845b82`, including the immutable-source and shell-boundary hardening.
- Boundary: baseline runs its real explicit `loom_checker.py push` preflight and then its real versioned PreToolUse hook; candidate runs its real versioned hook only. Timing starts immediately before the first checker process and ends when the hook returns its actual release/block result. The intercepted Git push is not executed, so the boundary ends before network transfer.
- Version isolation: the harness uses `git archive` to extract each revision's `loom_checker.py`, `git_exec.py`, `codex_scaffold.py`, `loom_record_fire.py`, `hooks/hooks.json`, and complete `contract/` package. It executes the hook command read from that revision's `hooks.json`; it never imports the current checkout's checker as a substitute.
- Fixed fixture: one accepted checkpoint is copied unchanged into every arm. Its HEAD was `b659dfb42d80990630ef630b670a94b9cef7586e` in this run, on branch `work`.
- Canonical push input: every arm uses its sample repository's absolute path and generates the hook payload from these quote-all tokens: `'/usr/bin/git' '-C' '<absolute-sample-repository>' 'push' '--no-follow-tags' '--recurse-submodules=no' '-u' 'origin' 'b659dfb42d80990630ef630b670a94b9cef7586e:refs/heads/work'`. `/usr/bin/git` was the resolved trusted executable in this run. Every token is single-quoted, embedded single quotes use the standard `'"'"'` splice, and tokens are joined by one ASCII space.
- Instrumentation: the declared repository command is `python3 evidence/package_suite.py`. It sleeps `0.080` seconds and appends its own `time.monotonic_ns()` duration to an arm-local log outside the repository. Counts and per-invocation durations come only from those executed-command records; total boundary timing also uses `time.monotonic_ns()`.
- Sampling: seven paired samples alternate arm order: baseline first on odd samples and candidate first on even samples.

## RED to GREEN

After pointing the unchanged harness at the hardened candidate but before generating its canonical command:

```text
uv run --isolated --with pytest --with pyyaml python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py::test_revisions_execute_versioned_real_gate_entrypoints -q --tb=short
```

Result: `1 failed in 3.45s`. Candidate return code was `2`, with `BLOCK push.reviewed-sha: the entire Git push command must use canonical quote-all rendering`; candidate stdout was empty, so no package-command observation preceded the block.

After generating the trusted absolute executable, absolute `-C` repository, fixed flags, literal remote, and full refspec as quote-all tokens:

```text
uv run --isolated --with pytest --with pyyaml python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py -q --tb=line
```

Result: `2 passed in 25.53s`.

The recorded observations came from:

```text
uv run --isolated --with pyyaml python docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py
```

## Observations

`B→C` means baseline then candidate; `C→B` means candidate then baseline. Invocation seconds are the durations written by the declared package command; boundary seconds include the real checker, checkpoint validation, package command, adversarial commands, repository-state checks, and hook dispatch.

| Sample | Order | Baseline package seconds | Baseline calls | Baseline boundary seconds | Baseline gate rc / verdict | Candidate package seconds | Candidate calls | Candidate boundary seconds | Candidate gate rc / verdict |
|---:|:---:|:---|---:|---:|:---|:---|---:|---:|:---|
| 1 | B→C | 0.090017916, 0.090023625 | 2 | 1.944800250 | 0,0 / release | 0.090019625 | 1 | 1.133754750 | 0 / release |
| 2 | C→B | 0.090015125, 0.090018584 | 2 | 2.045600292 | 0,0 / release | 0.090045333 | 1 | 1.164990167 | 0 / release |
| 3 | B→C | 0.090022000, 0.080918291 | 2 | 1.925855541 | 0,0 / release | 0.090023416 | 1 | 1.043103375 | 0 / release |
| 4 | C→B | 0.090012792, 0.090020833 | 2 | 1.971355833 | 0,0 / release | 0.090012833 | 1 | 1.068153666 | 0 / release |
| 5 | B→C | 0.090018917, 0.090033792 | 2 | 2.149540166 | 0,0 / release | 0.090013916 | 1 | 1.115616500 | 0 / release |
| 6 | C→B | 0.080021209, 0.090025959 | 2 | 1.933655541 | 0,0 / release | 0.090020833 | 1 | 1.061397583 | 0 / release |
| 7 | B→C | 0.090016709, 0.090014417 | 2 | 1.911076833 | 0,0 / release | 0.080361542 | 1 | 1.045498625 | 0 / release |
| Median | — | — | 2 | 1.944800250 | release | — | 1 | 1.068153666 | release |

Observed totals are 14 baseline package-command invocations and 7 candidate invocations. Every candidate sample invoked the declared command exactly once and fewer times than its paired baseline. Both arms produced the same real gate verdict in every pair. Candidate median local-gate wait was `0.876646584` seconds lower, or 45.1% lower for this controlled fixture.

## Guarantees and limitations

The candidate guarantee is narrow: the hook accepts only the canonical quote-all invocation measured above and rejects noncanonical spellings before running the package suite. The fixed `--no-follow-tags` and `--recurse-submodules=no` flags suppress configured implicit tag and submodule publication; the full source SHA pins the explicit branch update. This does not claim that arbitrary shell syntax is safe, that every semantically equivalent Git command is accepted, or that post-hook processes cannot mutate local files.

This measurement establishes invocation count, equal checker verdict, and local wait only for the fixed fixture and revisions above. The `0.080`-second package command makes duplicate execution visible without running this repository's complete suite fourteen additional times. Absolute and percentage savings will vary with repository, package suite, machine load, and filesystem scheduling. The hook was allowed to decide, but the intercepted Git command was deliberately not executed; separate shell-boundary and immutable-source attack probes use temporary local bare remotes to verify publication safety without any external or network push.
