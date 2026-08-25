---
name: systematic-debugging
description: |
  Use when a bug/production failure needs investigation — exceptions, wrong output, intermittent/CI failures, race conditions, 'works on my machine'. Enforces a 4-phase gate REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY; no fixing without reproducing.
version: 0.9.1
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer), the parent orchestrator already decided to invoke this skill. **Do not** re-route through it; follow your dispatched prompt directly. The orchestrator handles 4-phase progression.
</SUBAGENT-STOP>

## The HARD-GATE

> **NO FIXING WITHOUT REPRODUCING.**

This is tdd-iron-law's debugging analogue. **Phase 1 — REPRODUCE — must produce a reliable trigger before Phase 2 starts.**

"Cannot reproduce" means production-only conditions, a race/heisenbug, or an inaccurate report remain unresolved — never "fix anyway."

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

Prefer a failing test; otherwise record command + input + observation: "run X with Y, observe Z."

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

Output: the smallest defensible line, function, dependency, or input field.

**Gate to Phase 3**: bug surface is narrowed to a single component / input field / line — you can point at it.

### Phase 3 — HYPOTHESIZE

**Goal**: a falsifiable hypothesis that predicts an observation you have not yet made.

A hypothesis predicts an experiment: "if X, doing Z yields Y; W yields ¬Y." "I think it's X" is not falsifiable.

The discipline: every fix attempt requires a hypothesis stated in advance. Log each experiment: hypothesis; one variable changed; command/input; observed result; confirmed/falsified.

**Gate to Phase 4**: hypothesis is falsifiable (states a specific observation that would prove it wrong).

### Phase 4 — VERIFY

**Goal**: run the experiment; the hypothesis is confirmed or falsified.

| Result | Next step |
|---|---|
| ✅ Hypothesis confirmed | Apply the fix. Write a regression test (the repro from Phase 1 becomes a permanent test). Consider [`references/defense-in-depth.md`](references/defense-in-depth.md) for whether additional defensive layers proportional to blast radius are warranted. |
| ❌ Hypothesis falsified (**round 1**) | **Good** — the experiment did its job. Return to Phase 2 with the new information from the falsification. **Do NOT keep the failed-hypothesis fix in.** Revert any speculative changes made during VERIFY before re-isolating. |
| ❌ Hypothesis falsified (**round 2+**) | **HARD-GATE: WebSearch mandatory** before forming Hypothesis #3. See §"Anchored-thinking guard" below. |
| 🟡 Inconclusive | The experiment didn't bind the hypothesis. Tighten the prediction in Phase 3; rerun Phase 4. |

**Gate to "done"**: hypothesis confirmed + fix applied + regression test in place + (if appropriate) defensive layer added.

#### Anchored-thinking guard (≥2 falsifications)

After two falsifications, the initial framing may be biasing every next hypothesis.

**Mandatory before forming Hypothesis #3+**: run **WebSearch** on the problem class using the same protocol as `brainstorming` Axis 4 (EN + JA at minimum, cite sources, document empty results explicitly).

Query the framework + symptom/component in English and Japanese; include vendor forums and issue trackers.

**Output**: 2-3 known patterns from the industry that match observed symptoms. Hypothesis #3 must explicitly reference one of them OR document why none apply.

External evidence breaks the failed mental-model loop. Refuse "one more intuition"; run WebSearch.

## Cross-skill contract

| Direction | Skill | Trigger |
|---|---|---|
| **Upstream invocation** | `tdd-iron-law` §False-green diagnostic | When the diagnostic returns *"the test passes on first run AND commenting out the production code does not fail it,"* the test isn't testing what you think. systematic-debugging takes over to isolate why. |
| **Upstream invocation** | SDD `implementer` returning `BLOCKED` with `unblock_step: "test will not go RED"` | The implementer cannot create a failing test for a real-world bug. systematic-debugging takes over from Phase 1 REPRODUCE. |
| **Downstream (post-VERIFY)** | `tdd-iron-law` | Once the hypothesis is confirmed, the regression test is written under tdd-iron-law's RED-GREEN-REFACTOR cycle. The repro IS the RED. |
| **Lateral delegate (optional)** | `loom-workflow:complexity-critique` | When ISOLATE reveals the bug is in a module that's too tangled to bisect cleanly, complexity-critique's deletion-first lens may surface refactor-before-fix as the better path. |
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
| *"Let me try a 3rd hypothesis on my intuition"* (after 2 falsifications) | Anchored thinking compounding — the initial mental model is now the bias source, not the code. | §Anchored-thinking guard: WebSearch mandatory before Hypothesis #3+. Internal intuition has been falsified twice; ground the next round in external industry knowledge. |
| 「先試試看 / とりあえず直してみる」 | Same rationalization, localized. | Same refusal — hypothesis-first. |

## What this skill does NOT do

- Does **not** write features; use `brainstorming` → `writing-plans` → SDD → `tdd-iron-law`.
- Does **not** replace `tdd-iron-law` §False-green diagnostic; that is an entry condition.
- Adds defense-in-depth only after Phase 4 establishes the root cause.
- The user/orchestrator decides priority; once invoked, this skill runs all four phases.

## See also

- [`references/root-cause-tracing.md`](references/root-cause-tracing.md) — Phase 2 bisection + 5-Whys.
- [`references/condition-based-waiting.md`](references/condition-based-waiting.md) — Phase 1 🟡 race isolation.
- [`references/defense-in-depth.md`](references/defense-in-depth.md) — proportional post-VERIFY defenses.
- [`references/character-encoding-debug.md`](references/character-encoding-debug.md) — encoding-specific bisection protocol (BOM / UTF mismatch / NFC-NFD / surrogate pairs); links to `domain-teams:code-team/standards/character-encoding-security.md` (徳丸本 Ch.6) for the security-grounded version.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — the discipline that invokes this skill via §False-green diagnostic; also the discipline that writes the regression test in Phase 4.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — the orchestrator that invokes this skill when implementer returns BLOCKED on test-cannot-go-RED.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 5 (Repair, when stuck).
