---
name: verification-before-completion
description: |
  Use BEFORE declaring 'done' — claiming complete without running the package-level test suite. Fires on 'I'm done', 'ready to ship', 'tests pass' (no invocation shown), 'merge'.
version: 0.9.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, your dispatcher already decided whether verification applies. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## The HARD-GATE

> **NO "DONE" WITHOUT PACKAGE-LEVEL TEST INVOCATION.**

Evidence predating current HEAD is invalid. A focused test is never package verification. Until the current package suite passes, do not enter finishing or close-out: run the current package suite first.

Run the actual package suite (`npm test`, `pytest`, `go test ./...`, `cargo test`, etc.). Single-file tests, lint, or inspection are not verification.

Three failure modes only the package-level run catches:

1. **Test interaction bugs** from shared state, fixtures, ports, or environment.
2. **Orphan tests** excluded by a glob, config, or filename.
3. **Lint passes ≠ tests pass**: static analysis is not runtime behavior.

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **No tests exist yet** | Brand-new repo, no test infrastructure set up, this is the commit that adds the first test | "Tests exist but I didn't write any for this change" — that's Iron Law violation; not exempt |
| **Test infrastructure broken** | The test runner itself crashes (not a test failure — the runner doesn't run); a dependency-install failure prevents even starting tests | "Tests are slow so I skipped them" — that's a Red Flag below |

**Pure doc / config / generated regen** and **Explicit user override + scoped**
are not exemptions when a runnable suite exists: prose and generated outputs can
still break links, contracts, or checked artifacts. Only **No tests exist yet**
can make those changes N/A.

If you cannot point to the run that should catch a production break, verify.

## Red Flags — refuse these rationalizations

Each maps to a failure mode in The HARD-GATE above.

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Tests pass."* (no invocation) | No evidence. | Run and show the suite. |
| *"One test file passed."* | Misses interaction/orphan modes. | Run package-level. |
| *"Lint passes / it compiles."* | Static ≠ runtime. | Run tests. |
| *"CI can catch slow tests."* | Too late: CI follows push. | Run locally; for >10 min use `systematic-debugging`. |
| *"Manual testing worked."* | Exploration is not regression evidence. | Run/add tests. |
| *"A 1-line tweak after tests."* | The tweak may be the bug. | Re-run. |
| *"Ignore known failures."* | New failure ≠ documented xfail. | Surface any new failure. |
| 「テストはパスしてる / 測試 OK / 跑過了」 | Same rationalization, localized. | Same refusal — show the invocation. |

## Process

1. **Resolve the test command** for this project — declared-first consult (the project's declared commands: `AGENTS.md` commands section, `make`/`just` recipes, `package.json` scripts), falling back to detection if the declared verb does not run, emits no test count, or is signal-opaque (a bundled `check`/`test` that interleaves lint+tests — prefer the granular `test`, e.g. run a detectable `pytest` directly). See [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) for the priority-0 declared-surface consult and the per-stack detection table.
2. **Run it from project root.** Not from a subdirectory; not on a single file; not in IDE-watch-mode. The canonical CI-equivalent invocation.
3. **Read the exit code AND the output.** Exit 0 alone is not verification — *what was actually run*? Look for: total test count > 0, all-pass summary line, no `[skipped]` covering the touched modules. Exit 0 with 0 tests ran is a configuration bug, not a pass.
4. **If failures**, surface them. Do NOT mark "done." User decides remediation (route back to `tdd-iron-law` for the failing case; or `systematic-debugging` if the failure is non-obvious).
5. **If pass**, return verdict with evidence: the command run, the test count, the summary line — and mint the gate marker by running the suite THROUGH it: `python3 <plugin-root>/scripts/loom_gate_markers.py verified --run "<test command>"` (`<plugin-root>` = `../..` from this skill's base dir; it executes the command, records the real exit code + output tail, and mints only on exit 0). Writes `.git/loom/verified.json` bound to the current HEAD sha; the `hooks/git-guard.py` push gate requires it fresh, so in the branch-close flow run this AFTER the final commit — evidence must postdate the last content change (stale green lights are the failure mode this marker exists to kill). The "done" announcement itself follows the plain-relay contract — lead with one conclusion-first line (what shipped + test result in one sentence), per `loom-code/hooks/plain-relay.md`.

## Boundaries & related skills

This runs the existing suite; it does not write tests (`tdd-iron-law`), judge quality (`requesting-code-review`), choose coverage, or replace CI. Rendered `ui-flows.md` states belong to [`ui-verification`](../ui-verification/SKILL.md).

Invoked by `subagent-driven-development` (optional, end of each task triad — per-task for fast suites, deferred to end-of-plan for slow ones) and `finishing-a-development-branch` (Step 2, after `requesting-code-review`). On **PASS** proceed to git-memory + commit. On **FAIL** surface to the user, routing to `tdd-iron-law` (RED → fix → GREEN) or `systematic-debugging` (non-obvious failure).

- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — canonical test commands + detection signals per stack.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) · [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) · [`../systematic-debugging/SKILL.md`](../systematic-debugging/SKILL.md) · [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) · [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — sibling gates + the orchestrator (this skill is Stage 7, Verification).
