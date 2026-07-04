---
name: verification-before-completion
description: |
  Use BEFORE declaring 'done' — claiming complete without running the package-level test suite. Fires on 'I'm done', 'ready to ship', 'tests pass' (no invocation shown), 'merge'. Tests MUST run at package level (pytest / npm test), not a spot-check.
version: 0.9.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, your dispatcher already decided whether verification applies. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## The HARD-GATE

> **NO "DONE" WITHOUT PACKAGE-LEVEL TEST INVOCATION.**

"Done" without running the actual test suite at package level (`npm test` / `pytest` / `go test ./...` / `cargo test` / etc.) is the failure mode this skill exists to prevent. Single-file lint passes, individual test files passing, "the code looks right" — none of these are verification. The package-level invocation is the verification.

Three failure modes only the package-level run catches:

1. **Test interaction bugs**: Test A passes alone; Test B passes alone; A + B together fail (shared mutable state, database fixtures, port conflicts, env leakage).
2. **Orphan tests**: A test file exists but isn't included in the default suite (missing from `tests/` glob, excluded by config, wrong file extension) — a coverage hole the author, CI, and reality each assume someone else filled.
3. **Lint passes ≠ tests pass**: TypeScript compiles + ESLint clean + a runtime null dereference covered by no test. Static analysis is orthogonal to verification.

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **No tests exist yet** | Brand-new repo, no test infrastructure set up, this is the commit that adds the first test | "Tests exist but I didn't write any for this change" — that's Iron Law violation; not exempt |
| **Pure doc / config / generated regen** | Markdown change, version bump, regenerated protobuf stubs, `.gitignore` edit | Config that affects runtime behavior (retries: 3 → 5; feature flag flipped) — not exempt |
| **Test infrastructure broken** | The test runner itself crashes (not a test failure — the runner doesn't run); a dependency-install failure prevents even starting tests | "Tests are slow so I skipped them" — that's a Red Flag below |
| **Explicit user override + scoped** | User says "skip verification for this PR because it's only doc" AND the change matches exempt category 2 | "Just merge, I checked manually" — that's the rationalization |

When uncertain, ask: *"If this shipped and broke production, would I be able to point to the test run that should have caught it?"* If no, verification applies.

## Red Flags — refuse these rationalizations

Each maps to a failure mode in The HARD-GATE above.

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Tests pass."* (no invocation shown) | Unverified claim; their mental model of "passing" may not match what the runner actually says. | Run the suite; paste output; THEN you have evidence. |
| *"I ran the one test file, it passed."* | Misses interaction + orphan modes (1, 2). | Run package-level — single-file is necessary, not sufficient. |
| *"Lint passes / it compiles."* | Static ≠ runtime (mode 3). | Run tests; lint is orthogonal. |
| *"Tests are slow, I'll let CI catch it."* | CI catches it AFTER you push; this gate exists so you push only clean diffs. | Run locally first. If genuinely >10 min, see `systematic-debugging` slow-suite isolation. |
| *"It worked when I tested manually."* | Manual testing is exploration, not verification; it doesn't ratchet against the next regression. | Run the suite; add a test for what you checked by hand if it isn't covered. |
| *"Just a 1-line tweak after tests passed."* | The tweak might be the bug. | Re-run — 30 seconds now vs weeks recovering a 1-line prod regression. |
| *"Known-failing tests, just ignore them."* | "One more won't matter" is how 1 known-fail becomes 30. | Distinguish documented xfail / skip-with-ticket from new-fail; if your change is the new-fail, that's the bug. |
| 「テストはパスしてる / 測試 OK / 跑過了」 | Same rationalization, localized. | Same refusal — show the invocation. |

## Process

1. **Resolve the test command** for this project — declared-first consult (the project's declared commands: `AGENTS.md` commands section, `make`/`just` recipes, `package.json` scripts), falling back to detection if the declared verb does not run, emits no test count, or is signal-opaque (a bundled `check`/`test` that interleaves lint+tests — prefer the granular `test`, e.g. run a detectable `pytest` directly). See [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) for the priority-0 declared-surface consult and the per-stack detection table.
2. **Run it from project root.** Not from a subdirectory; not on a single file; not in IDE-watch-mode. The canonical CI-equivalent invocation.
3. **Read the exit code AND the output.** Exit 0 alone is not verification — *what was actually run*? Look for: total test count > 0, all-pass summary line, no `[skipped]` covering the touched modules. Exit 0 with 0 tests ran is a configuration bug, not a pass.
4. **If failures**, surface them. Do NOT mark "done." User decides remediation (route back to `tdd-iron-law` for the failing case; or `systematic-debugging` if the failure is non-obvious).
5. **If pass**, return verdict with evidence: the command run, the test count, the summary line — and mint the gate marker: `python3 <plugin-root>/scripts/loom_gate_markers.py verified --suite-line "<summary line>"` (`<plugin-root>` = `../..` from this skill's base dir). Writes `.git/loom/verified.json` bound to the current HEAD sha; the `hooks/git-guard.py` push gate requires it fresh, so in the branch-close flow run this AFTER the final commit — evidence must postdate the last content change (stale green lights are the failure mode this marker exists to kill).

## Boundaries & related skills

This skill runs the *existing* suite. It does **not** write tests (`tdd-iron-law`), judge code quality (`requesting-code-review` / SDD's per-task reviewer), decide which tests should exist, or replace CI — CI runs on push to remote; this skill runs *before* push so push carries only clean diffs. The rendered-UI half of verification (driving the real app through `ui-flows.md`'s states) is [`ui-verification`](../ui-verification/SKILL.md)'s job — a conditional sibling gate, not part of this one.

Invoked by `subagent-driven-development` (optional, end of each task triad — per-task for fast suites, deferred to end-of-plan for slow ones) and `finishing-a-development-branch` (Step 2, after `requesting-code-review`). On **PASS** the branch flow proceeds to git-memory + commit; on **FAIL** surface to the user, who routes to `tdd-iron-law` (failing case → RED → fix → GREEN) or `systematic-debugging` (failure non-obvious).

- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — canonical test commands + detection signals per stack.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) · [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) · [`../systematic-debugging/SKILL.md`](../systematic-debugging/SKILL.md) · [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) · [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — sibling gates + the orchestrator (this skill is Stage 7, Verification).
