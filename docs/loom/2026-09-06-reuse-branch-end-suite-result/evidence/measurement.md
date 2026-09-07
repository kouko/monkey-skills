# W1-01 real Ship-to-push-gate replay measurement

## Scope and controls

- Baseline: `2ec1e3b7c9cf307cec206c1a740ee6ba474e4b75`.
- Candidate: `839f1884a0d839475f9276c228db70b546c218a2`, including the immutable-source, shell-boundary, executable-shadow, and post-gate-hook hardening.
- Boundary: baseline runs its real explicit `loom_checker.py push` preflight and then its real versioned PreToolUse hook; candidate runs its real versioned hook only. Timing starts immediately before the first checker process and ends when the hook returns its actual release/block result. The intercepted Git push is not executed, so the boundary ends before network transfer.
- Version isolation: the harness uses `git archive` to extract each revision's `loom_checker.py`, `git_exec.py`, `codex_scaffold.py`, `loom_record_fire.py`, `hooks/hooks.json`, and complete `contract/` package. It executes the hook command read from that revision's `hooks.json`; it never imports the current checkout's checker as a substitute.
- Fixed fixture: one accepted checkpoint is copied unchanged into every arm. Its HEAD was `6efbb72fa04cb79aa82409300f02ac5474395261` in this run, on branch `work`.
- Canonical push input: every arm uses its sample repository's absolute path and generates the hook payload from these quote-all tokens: `'command' '/usr/bin/git' '-C' '<absolute-sample-repository>' 'push' '--no-follow-tags' '--recurse-submodules=no' '-u' '--no-verify' 'origin' '6efbb72fa04cb79aa82409300f02ac5474395261:refs/heads/work'`. The supported shell's standard `command` builtin is the trust root for bypassing aliases and functions; `/usr/bin/git` was the resolved trusted executable in this run. Every token is single-quoted, embedded single quotes use the standard `'"'"'` splice, and tokens are joined by one ASCII space.
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

Result: `2 passed in 27.37s` in a branch-only clone containing no backup refs.

The recorded observations came from:

```text
uv run --isolated --with pyyaml python docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py
```

## Observations

`B→C` means baseline then candidate; `C→B` means candidate then baseline. Invocation seconds are the durations written by the declared package command; boundary seconds include the real checker, checkpoint validation, package command, adversarial commands, repository-state checks, and hook dispatch.

| Sample | Order | Baseline package seconds | Baseline calls | Baseline boundary seconds | Baseline gate rc / verdict | Candidate package seconds | Candidate calls | Candidate boundary seconds | Candidate gate rc / verdict |
|---:|:---:|:---|---:|---:|:---|:---|---:|---:|:---|
| 1 | B→C | 0.082115250, 0.080648750 | 2 | 2.160431125 | 0,0 / release | 0.081194375 | 1 | 1.138371292 | 0 / release |
| 2 | C→B | 0.081334083, 0.085015792 | 2 | 2.099739708 | 0,0 / release | 0.080149166 | 1 | 1.152506500 | 0 / release |
| 3 | B→C | 0.081415084, 0.083182042 | 2 | 2.071124584 | 0,0 / release | 0.080214000 | 1 | 1.125506167 | 0 / release |
| 4 | C→B | 0.085013291, 0.085021500 | 2 | 2.152893708 | 0,0 / release | 0.080879292 | 1 | 1.198806875 | 0 / release |
| 5 | B→C | 0.085023875, 0.085034250 | 2 | 2.340308625 | 0,0 / release | 0.085015542 | 1 | 1.120538917 | 0 / release |
| 6 | C→B | 0.085021917, 0.085046333 | 2 | 2.092431959 | 0,0 / release | 0.085019042 | 1 | 1.219421375 | 0 / release |
| 7 | B→C | 0.080651791, 0.085018042 | 2 | 2.128029542 | 0,0 / release | 0.081739208 | 1 | 1.137820375 | 0 / release |
| Median | — | — | 2 | 2.128029542 | release | — | 1 | 1.138371292 | release |

Observed totals are 14 baseline package-command invocations and 7 candidate invocations. Every candidate sample invoked the declared command exactly once and fewer times than its paired baseline. Both arms produced the same real gate verdict in every pair. Candidate median local-gate wait was `0.989658250` seconds lower, or 46.5% lower for this controlled fixture.

## Guarantees and limitations

The candidate guarantee is narrow: the hook accepts only the canonical quote-all invocation measured above and rejects noncanonical spellings before running the package suite. Its trust chain begins with the supported shell's standard `command` builtin, which bypasses alias and function lookup before invoking the absolute Git executable. The fixed `--no-follow-tags`, `--recurse-submodules=no`, and `--no-verify` flags suppress configured implicit tag, submodule, and repository-hook publication; the full source SHA pins the explicit branch update. This does not claim that arbitrary shell syntax is safe, that every semantically equivalent Git command is accepted, or that post-hook processes cannot mutate local files.

This measurement establishes invocation count, equal checker verdict, and local wait only for the fixed fixture and revisions above. The `0.080`-second package command makes duplicate execution visible without running this repository's complete suite fourteen additional times. Absolute and percentage savings will vary with repository, package suite, machine load, and filesystem scheduling. The hook was allowed to decide, but the intercepted Git command was deliberately not executed; separate shell-boundary and immutable-source attack probes use temporary local bare remotes to verify publication safety without any external or network push.
