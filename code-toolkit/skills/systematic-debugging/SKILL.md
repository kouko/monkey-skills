---
name: systematic-debugging
description: 'Use when a bug or production failure needs investigation — any time code is throwing exceptions, returning wrong output, failing intermittently, "doesn''t work" but the cause is non-obvious, or "works on my machine" but breaks elsewhere. Examples: production errors, exceptions you''re tempted to silence with try/except, batch jobs dropping items, regressions you cannot localize, intermittent CI failures, race conditions, heisenbugs, slow queries, memory leaks, encoding bugs (UnicodeDecodeError / mojibake / BOM issues), "this should work but doesn''t" mysteries. Enforces a HARD-GATE 4-phase discipline — REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY — analogous to tdd-iron-law''s "no implementing without a failing test." No fixing without reproducing. Grounded in Kernighan & Pike (1999) The Practice of Programming Ch.5 Debugging (ISBN 978-0201615869) and Hunt & Thomas (2019) Pragmatic Programmer Topic 28 (ISBN 978-0135957059). Refuses random-patching, fishing-without-hypothesis logging, try/except masking, and "works on my machine" dismissals. デバッグ・系統的・再現先行・本番エラー調査・例外処理・try/except 回避。除錯・系統化・先再現・production bug 調查・例外處理・追根究底。'
version: 0.5.1-draft
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / debugger), the parent orchestrator already decided to invoke this skill. **Do not** re-route through it; follow your dispatched prompt directly. The orchestrator handles 4-phase progression.
</SUBAGENT-STOP>

## The HARD-GATE

> **NO FIXING WITHOUT REPRODUCING.**

This is the debugging analogue of tdd-iron-law's *"no production code without a failing test."* You cannot fix what you cannot reproduce; what you "fix" without a repro is either decoration (the bug was already gone) or theater (the bug will re-emerge from a different angle). **Phase 1 — REPRODUCE — must produce a reliable trigger before Phase 2 starts.**

When REPRODUCE returns *"I can't reproduce"*, that is a discovery — usually one of: (a) the bug needs production-only conditions you haven't surfaced, (b) the bug is a race or heisenbug, (c) the reporter's description is inaccurate. Each is a different next move. **None of them is "fix anyway."**

## When NOT to use

Narrow, enumerated exemption list.

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **Failing test + obvious line** | `tdd-iron-law` §False-green diagnostic already produced a RED test; you can see the wrong line; the fix is one-edit obvious. | "I think I see the line" — that's a hypothesis, not a verified isolation. Use this skill. |
| **Trivial typo / config value** | A literal typo in a string; a config value that's wrong by inspection (no behavior chain to trace). | A symptom that *looks* like a typo but you haven't traced to first appearance. |
| **Working as designed** | The "bug" is the spec — code does what the spec says; the spec is wrong. | The code does something the spec doesn't say AND you're not sure if it's intended. Repro it to confirm. |
| **Already root-caused in a prior session** | You're picking up a known-cause bug and the fix is queued. | You think you remember the cause but haven't re-confirmed. The fix-of-record is the bug-of-record; verify before fixing. |

When uncertain, ask: *"If I made a change right now, could I prove it fixed the bug?"* If no (because you can't trigger the bug to test against), this skill is mandatory.

## The 4 phases

Each phase has a **gate** to the next. Skipping a gate is a violation.

### Phase 1 — REPRODUCE

**Goal**: a reliable trigger that fails reproducibly.

The repro is your equivalent of a RED test (tdd-iron-law). Ideally it IS a failing test in the test suite — that gives you regression protection for free. Worst-case it's a documented command + input + observation: *"run X with input Y, observe Z."*

| Repro quality | Description |
|---|---|
| 🟢 **Reliable** | Triggers every time. Move to Phase 2. |
| 🟡 **Intermittent** | Triggers some-of-the-time. Use [`references/condition-based-waiting.md`](references/condition-based-waiting.md) to bound the conditions; isolate the race / timing factor before Phase 2. |
| 🔴 **Cannot reproduce** | The bug has not been observed by you. Surface back to user: do you have a reliable trigger? If no, the bug is not actionable yet — instrument the production code to capture it next time. **Do NOT proceed to Phase 2.** |

**Gate to Phase 2**: repro is 🟢 or 🟡 with bounded conditions documented.

### Phase 2 — ISOLATE

**Goal**: narrow the bug surface to the smallest possible bisection.

| Bisection axis | When to use |
|---|---|
| **Git bisect** | The bug appeared after a known-good version. Binary-search through commits. |
| **Input bisect** | Bug appears with input X but not X'. Narrow which field / byte / character matters. (See [`references/character-encoding-debug.md`](references/character-encoding-debug.md) for encoding-specific bisection.) |
| **Dependency bisect** | Bug appears after a dependency upgrade. Pin known-good version → confirm fix → bisect package version. |
| **Component bisect** | Bug is "somewhere in the pipeline." Insert observation points at module boundaries; binary-search through stages. |
| **5-Whys** | Bug is non-code (process / data / human). [`references/root-cause-tracing.md`](references/root-cause-tracing.md). |

The output of ISOLATE is the smallest possible *"the bug lives in this {line / function / dependency / input field}."*

**Gate to Phase 3**: bug surface is narrowed to a single component / input field / line — you can point at it.

### Phase 3 — HYPOTHESIZE

**Goal**: a falsifiable hypothesis that predicts an observation you have not yet made.

A hypothesis is **not** *"I think it's X"*. A hypothesis is *"if it's X, then observing Y will happen when I do Z, and observing ¬Y will not happen when I do W."* The asymmetry is the whole point — the hypothesis predicts an experiment, and the experiment's outcome falsifies or confirms.

**Anti-pattern**: *"I think the cache isn't invalidating."* → not a hypothesis, no prediction. **Correct**: *"If the cache isn't invalidating on write, then setting `cache.set(k, v)` followed by `cache.get(k)` should return stale data ONLY when there's an intermediate `cache.get(k)` between them. Run this sequence; observe."*

The discipline: every fix attempt requires a hypothesis stated in advance. If you cannot articulate the prediction, you're not debugging — you're random-patching (Red Flag below).

**Gate to Phase 4**: hypothesis is falsifiable (states a specific observation that would prove it wrong).

### Phase 4 — VERIFY

**Goal**: run the experiment; the hypothesis is confirmed or falsified.

| Result | Next step |
|---|---|
| ✅ Hypothesis confirmed | Apply the fix. Write a regression test (the repro from Phase 1 becomes a permanent test). Consider [`references/defense-in-depth.md`](references/defense-in-depth.md) for whether additional defensive layers proportional to blast radius are warranted. |
| ❌ Hypothesis falsified | **Good** — the experiment did its job. Return to Phase 2 with the new information from the falsification. **Do NOT keep the failed-hypothesis fix in.** Revert any speculative changes made during VERIFY before re-isolating. |
| 🟡 Inconclusive | The experiment didn't bind the hypothesis. Tighten the prediction in Phase 3; rerun Phase 4. |

**Gate to "done"**: hypothesis confirmed + fix applied + regression test in place + (if appropriate) defensive layer added.

## Cross-skill contract

| Direction | Skill | Trigger |
|---|---|---|
| **Upstream invocation** | `tdd-iron-law` §False-green diagnostic | When the diagnostic returns *"the test passes on first run AND commenting out the production code does not fail it,"* the test isn't testing what you think. systematic-debugging takes over to isolate why. |
| **Upstream invocation** | SDD `implementer` returning `BLOCKED` with `unblock_step: "test will not go RED"` | The implementer cannot create a failing test for a real-world bug. systematic-debugging takes over from Phase 1 REPRODUCE. |
| **Downstream (post-VERIFY)** | `tdd-iron-law` | Once the hypothesis is confirmed, the regression test is written under tdd-iron-law's RED-GREEN-REFACTOR cycle. The repro IS the RED. |
| **Lateral delegate (optional)** | `dev-workflow:complexity-critique` | When ISOLATE reveals the bug is in a module that's too tangled to bisect cleanly, complexity-critique's deletion-first lens may surface refactor-before-fix as the better path. |
| **Lateral delegate (optional)** | `repo-wiki:query` / `dbt-wiki:query` | When ISOLATE needs to understand *"why was this code written this way"* — query the knowledge base before re-deriving. |

Delegation contract per CLAUDE.md: pass **paths + structured seed context**, not file content.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"I'll just try a few fixes and see what works."* | Random-patching. No hypothesis = no learning. Each failed patch leaves the code in a worse-understood state. | Refuse. Return to Phase 3; articulate a falsifiable hypothesis BEFORE any change. Kernighan & Pike (1999) Ch.5: *"Debugging requires thinking, not changing."* |
| *"It's probably X."* | *Probably* is not a hypothesis — it's a guess. A hypothesis predicts an observation. | Refuse. Restate as *"if it's X, then observing Y when I do Z will confirm; observing ¬Y will falsify."* |
| *"It works on my machine."* | Failure to bound the repro conditions. The bug isn't gone; the environment shifted. | Phase 1 returned 🟡 Intermittent. Use [`references/condition-based-waiting.md`](references/condition-based-waiting.md) to enumerate environment differences; bound the repro. |
| *"Let me add more logging and see what happens."* | Fishing without a hypothesis. Logging is observation, not investigation. | Refuse. Form a hypothesis first; add ONLY the logging that tests the hypothesis. Otherwise you produce a log soup nobody reads. |
| *"Just wrap it in try/except and move on."* | Masking the bug. The exception is the bug telling you what's wrong; suppressing it converts a known failure into a silent corruption. | Refuse. Find the root cause via Phase 2-3. After root cause, defense-in-depth may add a graceful-degradation layer — but that's a deliberate decision, not a panic move. |
| *"It's intermittent so let's move on."* | Heisenbug refusal. Intermittent = race condition / timing / leak. These compound silently in production. | Refuse. Phase 1 🟡 → Phase 2 with timing-axis bisection. If genuinely cannot bound after 1 hour of effort, surface to user as known-unknown with observability instrumentation. |
| *"The error message is clear, I'll just fix it."* | Symptom ≠ root cause. The error message is where the bug surfaced, not where it lives. | Phase 2 ISOLATE first; the line that throws is rarely the line that broke. |
| 「先試試看 / とりあえず直してみる」 | Same rationalization, localized. | Same refusal — hypothesis-first. |

## What this skill does NOT do

- Does **not** write features. Implementation flows through `brainstorming` → `writing-plans` → SDD → `tdd-iron-law`. systematic-debugging is reactive (something broke), not generative.
- Does **not** replace `tdd-iron-law` §False-green diagnostic. That diagnostic is the *entry condition* to this skill, not its substitute.
- Does **not** add defense-in-depth proactively. The defense layer is a Phase-4 *result* of finding the bug, not a Phase-0 *posture*. Adding defenses without understanding what they defend against is paranoia.
- Does **not** decide blast radius / priority. The user / orchestrator decides whether this bug is worth Phase-1-through-4 effort. The skill, once invoked, runs the 4 phases.

## See also

- [`references/root-cause-tracing.md`](references/root-cause-tracing.md) — Phase 2 ISOLATE sub-protocols (bisection axes + 5-Whys for non-code causes).
- [`references/condition-based-waiting.md`](references/condition-based-waiting.md) — Phase 1 🟡 + race-condition isolation.
- [`references/defense-in-depth.md`](references/defense-in-depth.md) — Phase 4 post-VERIFY defensive-layer placement (proportional to blast radius).
- [`references/character-encoding-debug.md`](references/character-encoding-debug.md) — encoding-specific bisection protocol (BOM / UTF mismatch / NFC-NFD / surrogate pairs); links to `domain-teams:code-team/standards/character-encoding-security.md` (徳丸本 Ch.6) for the security-grounded version.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — the discipline that invokes this skill via §False-green diagnostic; also the discipline that writes the regression test in Phase 4.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — the orchestrator that invokes this skill when implementer returns BLOCKED on test-cannot-go-RED.
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — router; this skill is Stage 5 (Repair, when stuck).
