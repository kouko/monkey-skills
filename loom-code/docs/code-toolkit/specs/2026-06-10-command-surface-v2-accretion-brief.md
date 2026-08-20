# Brainstorming brief — Command Surface v2 (野心 B, accretion-discipline half only)

> **Type**: brainstorming output (consumed by `writing-plans`)
> **Branch**: `feat/command-surface` (continues after v1 / 野心 A on the same branch)
> **Parent spec**: `2026-06-10-command-surface-establishment.md` §4.2 beat ② (ACCRETE), §5 integration point ④ (accretion-DoD half), §8.1 Q1/Q4/Q7
> **Scope lock**: the **accretion DISCIPLINE** half of ④ only. Bound by ratified §8.1 **Q1 (accretion = SDD DoD, event-driven), Q4 (managed-block write), Q7 (@AGENTS.md shim)**.
> **Depends on**: v1 (declared-first resolution) already landed on this branch — accretion's CONSUME beat reuses it.

## Problem

(Axis 1 — JTBD) v1 made vbc *consume* a declared command surface. But a surface only stays trustworthy if it **grows with the project**: when a task adds a new runnable capability (a second test suite, a build step, a lint target, e2e, `migrate`…), that capability is invisible to the surface until someone declares its verb. If declaration is left to "later", the surface rots — the next session's vbc/implementer can't find the e2e suite and silently under-verifies. The job: *When a task introduces a new runnable capability, declare its verb in the command surface and prove it runs — in the same task — so the surface always reflects what the project can currently do.*

This is the **ACCRETE** beat (§4.2 ②): event-driven, bound into the SDD task Definition of Done — exactly as TDD couples "add behaviour" with "add a test". **Not** per-task polling, **not** a build-once bootstrap. No new capability → no surface change. "Complete" is a moving target relative to current capabilities — you never pre-declare a `deploy` verb before deployment exists.

## Users

(Axis 2) code-toolkit's own agents on any consuming project:
- **SDD orchestrator** — owns the per-task Definition of Done; must treat "declared the new verb + verified it" as part of a capability-adding task's completion.
- **implementer subagent** — the actor that, having just built a new runnable capability, declares its verb (writes the AGENTS.md managed block + `@AGENTS.md` shim if needed) and runs it before declaring (verify-before-declare, Rule 12 fail-loud).
- **writing-plans (optional)** — at plan time, marks tasks that add a runnable capability so their acceptance already names "verb declared + verified".

Condition: a task whose work genuinely adds a runnable entry the surface doesn't yet name. Most tasks add **no** new capability → the discipline is a no-op for them (event-driven).

## Current State Evidence

- **Forward (where the DoD clause attaches)**: `subagent-driven-development/SKILL.md` has **no explicit "Definition of Done" section**. Task completion is defined implicitly by the status taxonomy (`SKILL.md:134-139`, DONE / DONE_WITH_CONCERNS) and the verdict-resolution table (`SKILL.md:115-118`, both reviewers PASS → "Task DONE"). The accretion clause needs a small new home — a focused subsection near the per-task triad (`SKILL.md:89-97`) or status handling.
- **Reverse (SSOT ownership)**: `subagent-driven-development/SKILL.md` and `writing-plans/SKILL.md` are **code-toolkit-unique** (not functional copies — v1 edited the former and `verify-drift.py` stayed green). `agents/implementer.md` carries distribute-managed blocks — `<!-- BEGIN baseline-v1 -->` (`implementer.md:65`) and `<!-- BEGIN rule-sheet-v1 -->` (`implementer.md:175`) — which are **OFF-LIMITS**; the accretion obligation goes in the hand-authored role-contract region (`implementer.md:12-63`) or input/output region (L218+), outside both blocks. v1 confirmed this is safe.
- **Error (verify-before-declare / fail-loud)**: baseline **Rule 12 — Fail loud** (`implementer.md` baseline block) is the anchor: never declare a verb that has not been run and observed to work; on an unresolved gap, surface it, never fabricate a surface entry.
- **Data (the managed-block write convention)**: the BEGIN/END marker style already exists for distribute-owned blocks (`distribute.py:168` baseline, `distribute.py:209` rule-sheet; mirrored in `implementer.md:65,175`). The Q4 accretion block reuses this **style** — `<!-- BEGIN command-surface (managed) -->` / `<!-- END command-surface (managed) -->` in the project's `AGENTS.md` — but is **written by the implementer during accretion**, NOT owned by distribute.py (so it never trips `verify-drift.py`, which only checks code-toolkit's own agent files).
- **Boundary (Claude-Code compat / Q7)**: no `@AGENTS.md` import-shim convention exists in code-toolkit today — only `using-code-toolkit/references/codex-tools.md:93-97` notes CLAUDE.md≡AGENTS.md informally. Part 2 introduces the convention: when accreting in a repo with no `CLAUDE.md`, create a thin `CLAUDE.md` containing `@AGENTS.md` so Claude Code passively sees the surface.

Evidence paths appendix:
- `code-toolkit/skills/subagent-driven-development/SKILL.md` (L89-97 per-task triad; L111-120 verdict resolution; L134-139 status taxonomy)
- `code-toolkit/agents/implementer.md` (L12-63 role contract; L65 + L175 managed blocks = OFF-LIMITS; L218-289 I/O contract; baseline Rule 12)
- `code-toolkit/skills/writing-plans/SKILL.md` (L52-57 splitting framework / acceptance criterion) + `references/plan-format.md`
- `code-toolkit/scripts/distribute.py` (L168 / L209 — BEGIN/END marker style to mirror)
- `code-toolkit/skills/verification-before-completion/references/test-invocation-by-stack.md` (v1 priority-0 resolution that CONSUME reuses)
- `code-toolkit/tests/integration/test-command-surface-resolution.sh` (the v1 harness to extend with accretion checks)
- `code-toolkit/tests/verification-before-completion-pressure/prompts/index.md` (pressure-prompt convention)

## Decision

**Build** (pure prose, code-toolkit-unique files): the accretion DISCIPLINE as a contract addition — **3 prose edit targets + 2 tests**:

- **A) SDD Definition-of-Done accretion clause** (`subagent-driven-development/SKILL.md`) — add a focused subsection: a task that introduces a **new runnable capability** (new test suite / build step / lint / e2e / migrate / …) is not DONE until its verb is **declared in the command surface AND verified to run** — event-driven, bound into the task DoD like TDD couples behaviour+test. No new capability → no surface change. Never per-task polling, never build-once.
- **B) implementer accretion obligation** (`agents/implementer.md`, role-contract region, OUTSIDE managed blocks) — when the task adds a runnable capability, the implementer: (1) **verify-before-declare** — run the new verb, confirm it works (Rule 12 fail-loud; never declare an unrun verb); (2) declare it in the project `AGENTS.md` inside a `<!-- BEGIN command-surface (managed) -->` / `<!-- END command-surface (managed) -->` block, extending an existing `## Commands` section rather than duplicating, never clobbering human-authored prose (Q4); (3) if the repo has no `CLAUDE.md`, create a thin one containing `@AGENTS.md` (Q7 shim); (4) **reuse v1's declared-first resolution** to locate/extend the surface — do NOT auto-scan or build a surface from zero (that is ⑤ seed builder, out of scope).
- **C) writing-plans capability-task marker** (`writing-plans/SKILL.md`, optional but recommended) — at plan time, a task that adds a runnable capability gets an acceptance line naming "the new verb is declared in the command surface and verified to run", so accretion is visible upfront, not only caught at DoD.
- **Tests**: extend the v1 harness (`test-command-surface-resolution.sh`) with accretion CHECK groups asserting the new clause/obligation/marker phrases; add a behavioral **accretion pressure prompt** (a task adds an e2e suite → must declare `test-e2e` + verify it runs before DONE; must NOT pre-declare a non-existent capability; must NOT clobber human AGENTS.md sections).

**Why**: closes the seed→ACCRETE→consume→anti-drift loop's *accretion* beat at near-zero risk (prose only, code-toolkit-unique files), making v1's consumed surface a *living* artifact. The discipline rides existing machinery (SDD DoD + implementer contract + v1 resolution) — no new builder, no new format.

**Will NOT build**: ④'s **seed preflight** (establish a surface when absent), ⑤'s **seed builder** (detect→verify→instantiate a surface from zero), any auto-scan of an existing repo, any executable surface-writing tool. Those are frontier; gate on v1+v2 dogfood signal. No new declaration format. No touching standards/rubrics/checklists or distribute-managed blocks.

## Alternatives Considered

(Axis 4 — researched + ratified in parent spec, verified 2026-06; not re-run)
1. **aider `auto-test` verify→fix loop** (aider docs) — proven *consume* pattern; v2 extends the model to *grow* the declared surface as capabilities appear. Pro: builds on the same declared-command foundation. Con: aider does not accrete — human declares; v2's event-driven DoD coupling is the novel-but-low-risk delta.
2. **TDD behaviour+test coupling** (Beck 2002) — the structural analogue v2 mirrors: bind "declare the verb" to "add the capability" in one task, as TDD binds "add a test" to "add behaviour". Adopted as the discipline's mental model.
3. **Per-task sufficiency polling** (check the whole surface every task) — **rejected** (§4.2): noisy, treats a moving target as a fixed checklist.
4. **One-time bootstrap** (build the full surface upfront) — **rejected**: over-builds; pre-declares capabilities that don't exist yet (no `deploy` verb before deploy).
5. **Auto-build / seed builder now (⑤)** — **deferred**: no proven auto-build precedent; frontier; gate on dogfood.

Note (EN/JA): no mainstream skillset (Superpowers / OpenSpec / goose / spec-kit) auto-accretes a command surface — all are human-declared. v2's event-driven DoD coupling is a disciplined middle path (agent declares *as it builds*, verify-before-declare), not auto-build.

## What Becomes Obsolete

(Axis 5)
- The implicit assumption that a command surface, once consumed (v1), is **static** — replaced by the living-artifact model (accretes via DoD).
- Nothing is deleted. v1's resolution and detection-fallback stay intact; accretion only *adds* a completion obligation that fires when (and only when) a task adds a capability.
- If `writing-plans` (C) lands, the plan's acceptance schema gains an accretion case — additive, no existing field removed.

## Out of Scope

- ④ **seed preflight** (surface-absent establishment) and ⑤ **seed builder** (detect→verify→instantiate from zero) — frontier, deferred.
- Any executable/auto tool that writes AGENTS.md (the implementer writes the managed block by hand following the prose convention; no builder script this round).
- Auto-scanning an existing repo to infer its full surface.
- New command-declaration format; `check`-as-vbc-gate; standards/rubrics/checklists; distribute-managed BEGIN/END blocks.
- Cross-session persistence of accreted state beyond what already lives in the project's AGENTS.md.

## Open Questions

- **None blocking.** §8.1 Q1/Q4/Q7 ratified and bind v2. Two implementation calls deferred to `writing-plans`: (a) the exact home for the SDD DoD clause (new "## Definition of Done" section vs subsection under the per-task triad) — both are valid, pick the lighter; (b) whether the writing-plans marker (C) is a full task or folded as a note in the splitting framework — decide by atomicity at plan time.
