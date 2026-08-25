---
name: using-loom-code
description: |
  Router for loom-code — invoke when the user wants to build, change, debug, or review code (features / fixes / refactors / migrations / reviews). Drives brainstorm → plan → SDD → TDD → debugging → code review → finish branch.
version: 0.12.0
---

<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer), **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
**You have loom-code.** If the user is starting any coding work — feature / bug fix / refactor / review / migration — you **must** route through this skill before writing implementation code.

Five load-bearing rules:

1. **Brainstorm before implementing.** Call `brainstorming`; the historical 5-axis walk starts at Axis 0, then Problem / Users / Smallest End State / Alternatives / What Becomes Obsolete produce the brief.
2. **TDD is the iron law.** Call `tdd-iron-law`: no production code without a failing test first.
3. **Split + dispatch (SDD).** Task >1 hour or >1 module → `subagent-driven-development`; atomic one-failing-test units; three subagents per task (implementer / spec-reviewer / code-quality-reviewer).
4. **Never push without review.** A real close-out routes through `finishing-a-development-branch`, which adds review, verification, memory timing, and git-memory; standalone `requesting-code-review` is only for review without merging. `git push` / `gh pr create` / `gh pr merge` without review PASS violates the gate.
5. **Research before asking.** Non-trivial design/strategy/stack questions cite 2–4 sourced industry approaches via `brainstorming` Axis 4. Follow the four-outcome policy in `references/continuous-mode.md`: auto-resolve approved checkable work, ask only for missing scope/decision, and halt for irreversible safety boundaries; downstream skills own plain phrasing.

**Skipping any of these = violation.** "I'll just quickly…" / "just push" / "just ask" / 「ちょっと試すだけ」 / 「先 push 再說」 / 「先問再說」 are rationalizations — refuse them.
</EXTREMELY-IMPORTANT>

## Instruction priority

When instructions conflict, follow this order:

1. User's `CLAUDE.md` / project conventions — local rules always win.
2. loom-code skills loaded into context — this router + invoked specialists.
3. Host default behavior — fallback only.

## How to access skills

| Harness | Mechanism |
|---|---|
| Claude Code | Use the `Skill` tool, e.g. `Skill(skill: "tdd-iron-law")`. See `references/claude-code-tools.md`. |
| Codex CLI | Use the `skill` tool (Codex shape). Full tool mapping ships Phase 2.5 — see `references/codex-tools.md`. |

If the user types `/skill-name`, that is an explicit invocation — load it via the Skill tool. Do not guess names that are not listed below.

## Skill priority — decision order for coding tasks

Walk through these stages in order. Skip a stage only when its precondition is already met (e.g. user already handed in a plan → skip planning).

| # | Stage | Skill (target) | Status |
|---|---|---|---|
| 1 | Discovery | `brainstorming` | ✅ shipped |
| 2 | Planning | `writing-plans` | ✅ shipped |
| 3 | Execution | `subagent-driven-development` | ✅ shipped |
| 4 | Discipline (during execution) | `tdd-iron-law` | ✅ shipped |
| 5 | Repair (when stuck) | `systematic-debugging` | ✅ shipped |
| 6 | Review | `requesting-code-review` | ✅ shipped |
| 7 | Verification | `verification-before-completion` | ✅ shipped |
| 7b | UI verification (conditional) | `ui-verification` — fires only when the branch touched UI and a `ui-flows.md` exists; N/A otherwise | ✅ shipped |
| 8 | Branch close | `finishing-a-development-branch` → delegates `loom-workflow:git-memory` | ✅ shipped |

**Auxiliary** (on-demand, not part of the linear stage flow):

- `using-git-worktrees` — parallel branches / long-running experiments / design-then-build cycles with one repo, N checkouts.
- `dispatching-parallel-agents` — 2+ independent problem domains (multiple unrelated test failures, multiple modules to audit, N disjoint data fetches, atomic tasks the plan marks `Independent: true`). Across-task / across-domain dispatch via one assistant message with multiple `Agent` calls. Complements `subagent-driven-development`'s within-task reviewer parallelism.

**Auto-suggest hook** (Stage 3 → Auxiliary): When SDD is about to consume a plan that contains **≥2 tasks** marked `Independent: true` with **disjoint `Files touched`**, the router suggests `dispatching-parallel-agents` for those tasks (the implementer fan-out happens in one assistant message; the rest of the plan stays on SDD's per-task triad). The user can decline; SDD's sequential dispatch is always the fallback. This is the **only** time the toolkit dispatches multiple implementers within one plan — every other path keeps SDD's "one implementer at a time" floor.

## Autonomous execution (default): approved scope → PR-ready

**Autonomy-by-default:** after a **human-approved**, frozen brief or validated
loom-design change-folder fixes scope, auto-advance stage→stage; 「一站一站來」
is the per-session human-pumped override.
The approved entry, not a request phrase, is the authority boundary: a named
publish endpoint may set the terminal, but is not required to start autonomous
execution. Downstream stations follow the shared four-outcome policy, not their own confirmation defaults.
**MANDATORY:** before auto-advancing, **READ references/continuous-mode.md IN FULL.**
**Never auto-merge; HALT** for privacy, merge, deploy, delete, failed safety gates,
or another STOP-contract row; PR-open is terminal.

## Red flags — agent rationalizations to refuse

| Agent says | Reality | Correct response |
|---|---|---|
| "I'll quickly fix this without a test." | Iron-Law violation. | Load `tdd-iron-law`; write RED first. |
| "This change is trivial, skip planning." | Scope still needs grounding. | Auto-resolve approved checkable work; ask only for missing scope/decision. |
| "I'll write all the code, tests last." | Tests-after. | Refuse. |
| "Subagents add overhead." | Not a quality argument. | SDD is mandatory above its threshold. |
| "User said skip TDD." | Valid only under `tdd-iron-law/SKILL.md` §When NOT to Use. | Quote it and confirm. |
| 「我先快速試一下 / ちょっと試すだけ」 | Same rationalization, localized. | Same refusal — load `tdd-iron-law`. |
| "I'll skip straight to the brief." | Skipping Axis 0 before a brief is a violation; it may route to `using-loom-design`. | Run Axis 0 first. |

## Skill types

- **Rigid** — `tdd-iron-law`, `subagent-driven-development`. Measure is non-negotiable; exception path is documented in-skill (§When NOT to Use). Do not invent new exceptions on the fly.
- **Flexible** — `brainstorming`, `writing-plans`, `systematic-debugging`. Adapt structure to the task; honor reasoned user override.

## Coexistence

- **`domain-teams:code-team`** audits existing artifacts; loom-code builds. Its knowledge copies sync via `scripts/distribute.py` and `scripts/verify-drift.py`.
- **`loom-workflow:{git-memory, complexity-critique, proposal-critique}`** — delegate; never duplicate.
- **`obra/superpowers`** overlaps names/hooks; disable loom-code injection with `LOOM_CODE_MODE=off`.
- **loom family reception** — SessionStart owns the family map/on-ramp; Axis 0 points to it.

## What this router does NOT do

- Does **not** write or review code itself — it routes.
- Does **not** auto-invoke downstream skills before an approved entry; afterward autonomy advances
  until an ask-policy outcome or safety stop.
- Does **not** enforce one workflow for every task — Flexible skills (§Skill types) cover tailoring.
- Does **not** replace `domain-teams:code-team` — both ship; pick by use-case (build vs audit).

## Reference

Load each file **only when its trigger fires** — do NOT speculatively load all of them.

- `references/continuous-mode.md` — full autonomy-by-default doctrine
  (entry/freeze, ask policy, STOP contract, never-auto-merge). **MANDATORY:**
  after an approved entry artifact, READ this **IN FULL** before auto-advancing
  (the §"Autonomous execution" stub above is not enough to run safely).
- `references/claude-code-tools.md` — Claude Code canonical tool names. Read only when the host is **Claude Code**.
- `references/codex-tools.md` — Codex CLI tool mapping (Phase 2.5 ship target). Read only when the host is **Codex CLI**.
- `references/engineering-baselines.md` — agent baseline (SSOT: `../../scripts/_baseline.md`).
- `references/environment-gotchas.md` — consolidated orchestrator harness / dcg / Read-tool-precondition gotchas (cross-cutting; pointed at by SDD / tdd-iron-law / finishing-a-development-branch / using-git-worktrees). Read only when an orchestrator hits a harness friction (blocked git command, "File has not been read yet", rebase conflict).
- `../../PRODUCT-SPEC.md` / `../../TECH-SPEC.md` / `../../ROADMAP.md` — design lock + phase plan.

**Do NOT load** every reference file up front — load `continuous-mode.md` when
an approved entry begins autonomous execution, the host-tool files only under
their matching host, and `environment-gotchas.md` only on a harness-friction
trigger. The router body alone routes pre-approval work.
