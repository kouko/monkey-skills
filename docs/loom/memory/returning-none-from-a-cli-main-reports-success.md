---
name: returning-none-from-a-cli-main-reports-success
description: Every CLI here ends `sys.exit(main())` and `sys.exit(None)` exits 0 — so an error path that stops returning its non-zero code does not lose a diagnostic, it reports SUCCESS to the shell; a sampled mutation pass found four such paths where `return 1`/`return 2` could become `return None` with 1363 tests green
type: gotcha
origin: 2026-07-27 sampled mutation pass over the US SEC lanes (PR #623)
---

`analysis-kpi`'s CLIs all end:

```python
if __name__ == "__main__":
    sys.exit(main())
```

`sys.exit(None)` sets exit status **0**. So a `main()` whose error branch
stops returning its documented code — `return 1` for a fail-loud guard,
`return 2` for malformed input — hands the shell a success. The command
still prints its error to stderr, so a human watching the terminal sees the
failure and a `&&` chain, a `$?` check, or CI does not.

Four such paths existed with no test at all: `kpi_break dismiss` and
`confirm`, `kpi_series apply`, `kpi_xbrl build`. Each module's own docstring
already stated the contract ("Every fail-loud guard is a ValueError -> exit
1"); nothing held it.

**Why:** the failure is invisible in exactly the way this repo's arcs keep
rediscovering — a short or absent answer presented as a completed one. It is
also invisible to the usual test shapes: a test that calls `main()` and
asserts on stdout, or that asserts merely `!= 0`, passes either way. Only
asserting the SPECIFIC code catches it, and `1` vs `2` are different
contracts to a caller (a guard failure vs unusable input).

**How to apply:** any `main()` whose error paths return codes needs at least
one test per code, asserting the exact value — not `!= 0`, which lets the
codes drift into each other. Pin the premise itself once
(`sys.exit(None)` exits 0) so a later reader cannot dismiss the tests as
folklore. Related: [[a-test-can-be-correct-and-still-unable-to-fail]] — the
tests that hold these codes pass on first run, so their evidence is the
mutant, not a red bar.
