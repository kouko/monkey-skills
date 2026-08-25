# Dogfood report — Command Surface (v1 resolution + v2 accretion)

- **Date**: 2026-06-10
- **Target**: doctrine delta across 4 working-tree files on `feat/command-surface`
  (`verification-before-completion/SKILL.md` + `references/test-invocation-by-stack.md`,
  `subagent-driven-development/SKILL.md`, `agents/implementer.md`)
- **Scope note (floor-not-ceiling)**: Probe A (claude -p activation harness) was **scoped out** — this change does not touch any skill's triggering (descriptions/trigger phrases unchanged); existing `tests/skill-triggering/` + the two new pressure prompts cover firing. Ran **Probe B** (behavioral execution) on both resolution + accretion, and **Probe C** (cold-reader). No pass stamped.

## Severity summary

| Severity | Count | Categories |
|---|---|---|
| Critical | 0 | — |
| High | 0 | — |
| Medium | 1 | Output-quality (doctrine ambiguity) |
| Low | 5 | Cold-start / Jargon-leak / Progressive-disclosure |

Behavioral verdict: both executors produced **correct** behavior overall (declared-first consult; verify-before-declare + managed-block accretion + shim check). The findings are clarity/edge-case refinements, not behavioral failures.

## Findings

### F-1 [Medium · Output-quality · Probe B resolution] "emits a test count" is ambiguous for an interleaved bundled verb
- **Probe**: acme-api declares `make test` whose recipe runs `ruff check . && pytest` (interleaved lint+test output); pytest also independently detectable.
- **Expected (doctrine intent, spec §6)**: a bundled verb mixing lint+test is *signal-opaque* → fall back to the granular `test` (bare `pytest`) for a clean `N passed` signal.
- **Actual**: executor kept `make test`, reasoning "the pytest summary line is still present in stdout, so it emits a test count" — the looser reading. Defensible but contrary to §6's intent.
- **Root cause**: the rule "wins only if it runs and emits a test count" does not say whether an *interleaved-but-present* count qualifies; the pressure prompt assumes it does NOT, the executor assumed it does.
- **Why static review missed it**: the grep harness checks the phrase is present, not how an agent resolves the interleaved edge case; skill-judge read the rule as coherent.
- **Location**: `references/test-invocation-by-stack.md` §Priority 0; `verification-before-completion/SKILL.md` Process step 1.
- **Suggested fix**: clarify that a verb whose output **interleaves** lint+test is treated as signal-opaque and does NOT qualify as the gate even if a count is technically present — prefer the granular `test` (here bare `pytest`). One clause.

### F-2 [Low · Jargon-leak · Probe C + skill-judge] "declared surface" / "command surface" undefined inline
- vbc SKILL.md step 1 uses "declared-first consult" / "declared surface" with no inline definition — a reader must load the reference to know *what* to consult. "command surface" is never defined as a concept (only shown by example) across all 4 files.
- **Location**: `verification-before-completion/SKILL.md:51`; `subagent-driven-development/SKILL.md` accretion section; `writing-plans/SKILL.md` note.
- **Suggested fix**: add a ~1-line enumeration at first use — "(the project's declared commands: `AGENTS.md` commands section, `make`/`just` `test` recipes, README)".

### F-3 [Low · Jargon-leak · Probe C] "shim pattern" is a dead cross-reference
- SDD accretion section's Mechanics line references "shim pattern" and points to `implementer.md`, but `implementer.md` never uses the word "shim" (it describes the `@AGENTS.md` CLAUDE.md import behaviorally).
- **Location**: `subagent-driven-development/SKILL.md` accretion Mechanics; `agents/implementer.md` accretion rule.
- **Suggested fix**: align wording — either call it "the `@AGENTS.md` import shim" in implementer.md, or reword SDD to "the `@AGENTS.md` CLAUDE.md import".

### F-4 [Low · Cold-start · Probe C + skill-judge] accretion trigger lacks a negative example; "runnable" undefined
- The "new runnable capability" trigger gives positive examples (test suite / build / lint / e2e / migrate) but no negative example and no principle for "runnable"; novel cases (a `seed`/`report` script; a helper function) are left to inference. Risk: over-zealous declaration.
- **Location**: `subagent-driven-development/SKILL.md` accretion section; `agents/implementer.md` accretion rule.
- **Suggested fix**: add one negative example — "a task that adds a helper function / internal class with no new top-level runnable verb does NOT trigger this".

### F-5 [Low · Progressive-disclosure · skill-judge + Probe C] SDD step-1 re-narrates resolution mechanics + "once" ambiguous + content-hash has no mechanism
- SDD step 1 re-states the trust-by-execution rule (DRY/drift risk vs vbc as SSOT); "resolves once" is ambiguous for parallel-dispatch waves; the optional content-hash invalidation names no mechanism.
- **Location**: `subagent-driven-development/SKILL.md` Process step 1.
- **Suggested fix**: trim the re-narration to a pointer to vbc's rule; clarify "once per session before the first dispatch (or before each parallel wave)"; drop or soften the content-hash line.

### F-6 [Low · Output-quality · skill-judge] vbc reference Priority-0 internal duplication; writing-plans note not reviewer-enforced
- vbc reference's Priority-0 bold paragraph + the numbered 3-step list state the same order twice. Separately, writing-plans' accretion note is plan-visible but the plan-document-reviewer check table has no row enforcing it, and there's no canonical example acceptance line.
- **Location**: `references/test-invocation-by-stack.md` §Priority 0; `writing-plans/SKILL.md` note + reviewer check table.
- **Suggested fix**: drop the redundant numbered list; optionally add a reviewer check row + a one-line example for the accretion acceptance.

## Raw outputs appendix
- Probe B resolution executor: chose `make test`; full reasoning trace shows declared-first consult + bundled-check recognition but the looser "count still present → trust it" call (F-1).
- Probe B accretion executor: ran `npx playwright test` first, extended the `AGENTS.md` managed block, checked CLAUDE.md `@AGENTS.md`, explicit-path commit, `status: DONE` with both suites PASS — correct accretion behavior.
- Probe C cold-reader: confirmed F-2 (undefined "declared/command surface"), F-3 (dead "shim" reference), F-4 ("runnable" boundary fuzzy), F-5 (content-hash no mechanism).
