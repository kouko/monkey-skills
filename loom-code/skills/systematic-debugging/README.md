# systematic-debugging

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> **HARD-GATE — NO FIXING WITHOUT REPRODUCING.** 4-phase discipline: REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY. The debugging analogue of tdd-iron-law's *"no implementing without a failing test."* Grounded in Kernighan & Pike (1999) *The Practice of Programming* Ch.5 (ISBN 978-0201615869) and Hunt & Thomas (2019) *Pragmatic Programmer* Topic 28 (ISBN 978-0135957059). Refuses random-patching, fishing-without-hypothesis logging, try/except masking, and "works on my machine" dismissals.

Part of the [loom-code](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## The 4 phases

| Phase | Goal | Gate to next |
|---|---|---|
| 1 — **REPRODUCE** | Reliable trigger that fails reproducibly (your equivalent of a RED test) | 🟢 reproducible OR 🟡 with bounded conditions |
| 2 — **ISOLATE** | Bisect to the smallest possible bug locus (one line / function / dependency / input field) | Surface narrowed to a single component |
| 3 — **HYPOTHESIZE** | Falsifiable hypothesis predicting an observation you have NOT yet made | Hypothesis is falsifiable (states what would prove it wrong) |
| 4 — **VERIFY** | Run the experiment; confirm or falsify; if confirmed, fix + regression test + defense-in-depth proportional to blast radius | Hypothesis confirmed; fix applied; regression test in place |

If a phase fails its gate, you do NOT proceed — you return to the previous phase with new information.

## When to use

Auto-routed when:
- `tdd-iron-law` §False-green diagnostic returns *"the test passes on first run AND commenting out the production code does not fail it"* (the test isn't testing what you think).
- SDD `implementer` subagent returns `BLOCKED` with `unblock_step: "test will not go RED"` (cannot construct a failing test for a real-world bug).
- User says the code "doesn't work" but the cause is non-obvious — *"it's intermittent,"* *"works on my machine but not on CI,"* *"this should work but doesn't."*

## When NOT to use

Enumerated exemptions in [`SKILL.md`](SKILL.md) §When NOT to Use:

- A failing test already exists AND the wrong line is obvious (just fix it under tdd-iron-law)
- Trivial typo / config value bug (no behavior chain to trace)
- Code does what the spec says but the spec is wrong (revise the spec via brainstorming)
- Bug was already root-caused in a prior session

## What this skill ships

- [`SKILL.md`](SKILL.md) — 4-phase operational spec, Red Flags (8 rationalizations × ja + zh-TW variants), cross-skill contracts.
- [`references/root-cause-tracing.md`](references/root-cause-tracing.md) — Phase 2 ISOLATE sub-protocols. Bisection axis table (git / dependency / input / component / time / 5-Whys); cost-per-halving heuristics; anti-patterns.
- [`references/condition-based-waiting.md`](references/condition-based-waiting.md) — Phase 1 🟡 and Phase 2 time-axis bisection. Replaces `sleep(500)` anti-pattern with condition-polling. Library helpers per language.
- [`references/defense-in-depth.md`](references/defense-in-depth.md) — Phase 4 post-VERIFY layering. 6-layer ladder (regression test → input validation → invariant assertion → type-system → monitoring → architectural refactor) with proportionality rule (cost ≤ expected damage of next instance).
- [`references/character-encoding-debug.md`](references/character-encoding-debug.md) — encoding-specific bisection (BOM / UTF mismatch / NFC-NFD / surrogate pairs / stream decoder buffer boundaries). Links to `domain-teams:code-team/standards/character-encoding-security.md` for the security-grounded version (徳丸本 第 2 版 Ch.6).

## Cross-skill contract

- **Upstream**: invoked from `tdd-iron-law` (false-green diagnostic) or `subagent-driven-development` (implementer BLOCKED on test-cannot-go-RED).
- **Downstream**: Phase 4 VERIFY's fix triggers `tdd-iron-law` for the regression test (the repro IS the RED).
- **Lateral (optional)**: `dev-workflow:complexity-critique` for refactor-before-fix when ISOLATE reveals untanglable module; `repo-wiki:query` / `dbt-wiki:query` for *"why was this code written this way"* before re-deriving.

## What this skill does NOT do

- Does **not** write features (use brainstorming → writing-plans → SDD → tdd-iron-law).
- Does **not** replace `tdd-iron-law`'s false-green diagnostic — that's the entry condition, not a substitute.
- Does **not** add defense-in-depth proactively. Defense layers are a Phase-4 *result*, not a Phase-0 *posture*.
- Does **not** decide blast radius or priority — that's the user / orchestrator's call.

## See also

- [`SKILL.md`](SKILL.md) — operational spec.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — discipline that invokes this skill and consumes its output.
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — orchestrator that invokes this skill on implementer-BLOCKED.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is Stage 5 (Repair, when stuck).
