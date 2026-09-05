---
name: a-graduated-probe-that-clones-the-repo-asserts-the-subprocess-exit-code
description: A probe that shells out to a test run and then inspects its output for `FAILED` lines passes vacuously when that run never collected anything (an import error, a missing interpreter, pytest exit 5, a missing test path swallowed by xdist), so it asserts `returncode == 0` first with stdout and stderr in the message, and the rehearsal script it wraps refuses an empty default glob and never adds `-n auto`, because xdist hides the "file or directory not found" collection error
type: practice
origin: 2026-09-05-graduated-probes-independent-of-local-history — Codex reader fatal finding wave-end:1-02 and the W1-01 implementer's xdist measurement (2026-09-05/06)
---

Three ways a "zero FAILED lines" check goes green while nothing ran:

1. The inner pytest exits non-zero before collecting (import error,
   wrong interpreter) — no `FAILED` line, no `SKIPPED` line, the outer
   assertion on skip reasons finds nothing to object to.
2. `pytest-xdist` swallows the "file or directory not found" collection
   error for an explicit path that does not exist; worker start-up never
   surfaces it to captured output. The rehearsal script therefore never
   passes `-n auto`, whatever the plan said about "adding it when xdist
   imports" — a slower loud run beats a fast silent one.
3. The default glob matches nothing and pytest is invoked with no path,
   collecting the whole clone — every unrelated test, none of the
   intended ones.

The probe asserts `returncode == 0` with both streams in the failure
message before it reads a single skip line; the script fails naming the
glob when its default expansion is empty.

Related: [[pytest-skip-reasons-with-nodeids-come-from-junit-xml-not-from-rs]],
[[pre-branch-end-ci-rehearsal-uses-full-history-without-a-local-main]].
