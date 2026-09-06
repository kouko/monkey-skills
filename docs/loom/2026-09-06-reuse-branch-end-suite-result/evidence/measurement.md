# W1-01 Ship-to-push replay measurement

## Scope and revisions

- Observed baseline: `9d009c49e02a52c4838dba30a88501e0bbe79ab0`, the revision immediately before `708b6703` made the supported-host hook the sole package-suite owner.
- Candidate: `998ba231327580c2262f650e54661dc1cb1d6d17`, the dispatched W1-01 starting revision containing W0-01 and W0-02.
- Boundary: the start of Ship's `Push` step through the local gate's `release` or `block` decision, before any network push. No remote command runs.
- Fixed fixture: each observed package-suite site runs `[sys.executable, package_suite.py]`. That complete fixture suite appends one line to `calls.log` and sleeps `0.080` seconds. Both arms inherit the same process environment plus `PYTHONHASHSEED=0`, the arm-local `W1_CALL_LOG`, and the same `W1_WORK_SECONDS=0.080`.
- Ownership observation: `git show <revision>:loom-code/skills/ship/SKILL.md` determines whether Ship executes the explicit checker preflight; the supported-host hook is then replayed for both revisions. Counts are the lines actually appended by executed suite processes, not counts inferred from narrative text.

## Commands

RED, before this evidence file existed:

```text
uv run --isolated --with pytest python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py -q --tb=line
```

Result: `1 failed`; `test_measurement_evidence_exists` reported `W1-01 measurement evidence has not been written`.

GREEN and recorded measurement:

```text
uv run --isolated --with pytest python -m pytest docs/loom/2026-09-06-reuse-branch-end-suite-result/evidence/probes/test_single_owner_push_gate.py -q --tb=line
uv run --isolated python -c '<load test module; call measured_samples in a new temporary directory; print observations as JSON>'
```

Result: `2 passed in 2.81s`; the second command produced the observations below. Timing uses `time.monotonic_ns()` around every complete boundary replay. Seven paired samples alternate execution order to reduce warm-up and load-order bias.

## Observations

| Sample | Baseline calls | Baseline seconds | Baseline verdict | Candidate calls | Candidate seconds | Candidate verdict |
|---:|---:|---:|---|---:|---:|---|
| 1 | 2 | 0.234855667 | release | 1 | 0.139257792 | release |
| 2 | 2 | 0.233202542 | release | 1 | 0.138872000 | release |
| 3 | 2 | 0.240689416 | release | 1 | 0.140658167 | release |
| 4 | 2 | 0.245722958 | release | 1 | 0.139508709 | release |
| 5 | 2 | 0.250232667 | release | 1 | 0.130234000 | release |
| 6 | 2 | 0.241350250 | release | 1 | 0.134126375 | release |
| 7 | 2 | 0.237124417 | release | 1 | 0.127672958 | release |
| Median | 2 | 0.240689416 | release | 1 | 0.138872000 | release |

Observed totals are 14 baseline invocations and 7 candidate invocations. Every candidate sample executed exactly once, fewer than its baseline pair, and both arms returned the same `release` verdict. Candidate median local-gate wait was `0.101817416` seconds lower (42.3% lower) for this fixture.

## Limitations

This is a controlled local fixture for this repository and these two revisions. The `0.080`-second complete fixture suite makes duplicate execution visible without spending the full repository-suite runtime on every sample. Process startup, machine load, and filesystem scheduling remain in the elapsed values. The result establishes the invocation-count and wait reduction only for this fixed replay; it does not predict absolute or percentage savings for other repositories, machines, package suites, hosts, or network pushes.
