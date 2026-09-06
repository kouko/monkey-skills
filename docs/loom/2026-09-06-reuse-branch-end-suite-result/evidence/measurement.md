# W1-01 real Ship-to-push-gate replay measurement

## Scope and controls

- Baseline: `9d009c49e02a52c4838dba30a88501e0bbe79ab0`.
- Candidate: `3ecac98e2b54282f88414481fae7ed8981b8d0e3`, including the immutable-source, shell-boundary, executable-shadow, and post-gate-hook hardening.
- Boundary: baseline runs its real explicit `loom_checker.py push` preflight and then its real versioned PreToolUse hook; candidate runs its real versioned hook only. Timing starts immediately before the first checker process and ends when the hook returns its actual release/block result. The intercepted Git push is not executed, so the boundary ends before network transfer.
- Version isolation: the harness uses `git archive` to extract each revision's `loom_checker.py`, `git_exec.py`, `codex_scaffold.py`, `loom_record_fire.py`, `hooks/hooks.json`, and complete `contract/` package. It executes the hook command read from that revision's `hooks.json`; it never imports the current checkout's checker as a substitute.
- Fixed fixture: one accepted checkpoint is copied unchanged into every arm. Its HEAD was `01ab28b22da425bfd220f117c24475ec8e611d52` in this run, on branch `work`.
- Canonical push input: every arm uses its sample repository's absolute path and generates the hook payload from these quote-all tokens: `'command' '/usr/bin/git' '-C' '<absolute-sample-repository>' 'push' '--no-follow-tags' '--recurse-submodules=no' '-u' '--no-verify' 'origin' '01ab28b22da425bfd220f117c24475ec8e611d52:refs/heads/work'`. The supported shell's standard `command` builtin is the trust root for bypassing aliases and functions; `/usr/bin/git` was the resolved trusted executable in this run. Every token is single-quoted, embedded single quotes use the standard `'"'"'` splice, and tokens are joined by one ASCII space.
- Instrumentation: the declared repository command is `python3 evidence/package_suite.py`. It sleeps `0.080` seconds and appends its own `time.monotonic_ns()` duration to an arm-local log outside the repository. Counts and per-invocation durations come only from those executed-command records; total boundary timing also uses `time.monotonic_ns()`.
- Sampling: seven paired samples alternate arm order: baseline first on odd samples and candidate first on even samples.

## RED to GREEN

After pointing the unchanged no-`command`-prefix harness at the final candidate:

```text
uv run --isolated --with pytest --with pyyaml python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py::test_revisions_execute_versioned_real_gate_entrypoints -q --tb=short
```

Result: `1 failed in 2.52s`. Candidate return code was `2`, with `BLOCK push.reviewed-sha: the Git push must begin with the standard command builtin`; candidate stdout was empty, so no package-command observation preceded the block.

After prepending quote-all `command` to the trusted absolute executable, absolute `-C` repository, fixed flags, literal remote, and full refspec:

```text
uv run --isolated --with pytest --with pyyaml python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py -q --tb=line
```

Result: `2 passed in 27.84s`.

The recorded observations came from:

```text
uv run --isolated --with pyyaml python docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py
```

## Observations

`B→C` means baseline then candidate; `C→B` means candidate then baseline. Invocation seconds are the durations written by the declared package command; boundary seconds include the real checker, checkpoint validation, package command, adversarial commands, repository-state checks, and hook dispatch.

| Sample | Order | Baseline package seconds | Baseline calls | Baseline boundary seconds | Baseline gate rc / verdict | Candidate package seconds | Candidate calls | Candidate boundary seconds | Candidate gate rc / verdict |
|---:|:---:|:---|---:|---:|:---|:---|---:|---:|:---|
| 1 | B→C | 0.083243125, 0.080380041 | 2 | 2.138496000 | 0,0 / release | 0.083067584 | 1 | 1.691297458 | 0 / release |
| 2 | C→B | 0.084977833, 0.081797083 | 2 | 3.449805708 | 0,0 / release | 0.081122167 | 1 | 1.968998583 | 0 / release |
| 3 | B→C | 0.080891625, 0.085051375 | 2 | 3.421059125 | 0,0 / release | 0.082499083 | 1 | 1.944297833 | 0 / release |
| 4 | C→B | 0.080795791, 0.084089250 | 2 | 3.572177750 | 0,0 / release | 0.081040708 | 1 | 1.935496583 | 0 / release |
| 5 | B→C | 0.082976583, 0.080931625 | 2 | 3.548430458 | 0,0 / release | 0.085025208 | 1 | 1.870498250 | 0 / release |
| 6 | C→B | 0.085046708, 0.085028959 | 2 | 3.491582625 | 0,0 / release | 0.085032208 | 1 | 1.920048584 | 0 / release |
| 7 | B→C | 0.080405375, 0.085239542 | 2 | 3.343056334 | 0,0 / release | 0.083065000 | 1 | 1.935328208 | 0 / release |
| Median | — | — | 2 | 3.449805708 | release | — | 1 | 1.935328208 | release |

Observed totals are 14 baseline package-command invocations and 7 candidate invocations. Every candidate sample invoked the declared command exactly once and fewer times than its paired baseline. Both arms produced the same real gate verdict in every pair. Candidate median local-gate wait was `1.514477500` seconds lower, or 43.9% lower for this controlled fixture.

## Guarantees and limitations

The candidate guarantee is narrow: the hook accepts only the canonical quote-all invocation measured above and rejects noncanonical spellings before running the package suite. Its trust chain begins with the supported shell's standard `command` builtin, which bypasses alias and function lookup before invoking the absolute Git executable. The fixed `--no-follow-tags`, `--recurse-submodules=no`, and `--no-verify` flags suppress configured implicit tag, submodule, and repository-hook publication; the full source SHA pins the explicit branch update. This does not claim that arbitrary shell syntax is safe, that every semantically equivalent Git command is accepted, or that post-hook processes cannot mutate local files.

This measurement establishes invocation count, equal checker verdict, and local wait only for the fixed fixture and revisions above. The `0.080`-second package command makes duplicate execution visible without running this repository's complete suite fourteen additional times. Absolute and percentage savings will vary with repository, package suite, machine load, and filesystem scheduling. The hook was allowed to decide, but the intercepted Git command was deliberately not executed; separate shell-boundary and immutable-source attack probes use temporary local bare remotes to verify publication safety without any external or network push.
