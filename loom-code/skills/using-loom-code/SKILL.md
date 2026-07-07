---
name: using-loom-code
description: |
  Router for loom-code — invoke when the user wants to build, change, debug, or review code (features / fixes / refactors / migrations / reviews). Drives brainstorm → plan → SDD → TDD → debugging → code review → finish branch.
version: 0.11.0
---

<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer), **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
**You have loom-code.** If the user is starting any coding work — feature / bug fix / refactor / review / migration — you **must** route through this skill before writing implementation code.

Five load-bearing rules:

1. **Brainstorm before implementing.** Explore intent + alternatives first. Call `brainstorming` — 5-axis framework ("5-axis" is the historical name; the walk starts at Axis 0) (Problem / Users / Smallest End State / Alternatives / What Becomes Obsolete) → structured brief.
2. **TDD is the iron law.** No production code without a failing test first. Call `tdd-iron-law`. Beck (2002, ISBN 978-0321146533) Preface: *"Write the test you wish you had. Make it fail. Make it pass. Make it clean."* Floor, not aspiration.
3. **Split + dispatch (SDD).** Task >1 hour or >1 module → `subagent-driven-development`; atomic one-failing-test units; three subagents per task (implementer / spec-reviewer / code-quality-reviewer).
4. **Never push without review — and a real close-out means `finishing-a-development-branch`, not review alone.** `git push` / `gh pr create` / `gh pr merge` without prior review PASS = violation. A `requesting-code-review` PASS is the floor, not the whole close-out: if the push is meant to finish/merge the branch (not just fetch a mid-work review opinion), route the whole thing through `finishing-a-development-branch` — it delegates to `requesting-code-review` as its own Step 1, so nothing is lost, and it additionally bundles verification-before-completion + same-branch memory-timing + the git-memory trailer decision, none of which a standalone review-then-manual-push gets you. Calling `requesting-code-review` directly and pushing by hand is the narrow exception (`finishing-a-development-branch`'s own §When to use names it: "review WITHOUT merging") — not the default path for a real close-out.
5. **Research before asking.** Non-trivial design / strategy / tech-stack question to user MUST cite WebSearch findings (2-4 industry approaches w/ sources). *"X or Y?"* without industry context = violation. Use `brainstorming` Axis 4 protocol for the research. This is gate ② of the full asking-the-user discipline — gate ① (whether to ask: do reversible/inferable steps without asking, always confirm outward/irreversible actions) and gate ③ (plain, jargon-free phrasing with a state anchor) are enforced in the downstream skills (`brainstorming` / `subagent-driven-development` / `requesting-code-review`).

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
| 8 | Branch close | `finishing-a-development-branch` → delegates `dev-workflow:git-memory` | ✅ shipped |

**Auxiliary** (on-demand, not part of the linear stage flow):

- `using-git-worktrees` — parallel branches / long-running experiments / design-then-build cycles with one repo, N checkouts.
- `dispatching-parallel-agents` — 2+ independent problem domains (multiple unrelated test failures, multiple modules to audit, N disjoint data fetches, atomic tasks the plan marks `Independent: true`). Across-task / across-domain dispatch via one assistant message with multiple `Agent` calls. Complements `subagent-driven-development`'s within-task reviewer parallelism.

**Auto-suggest hook** (Stage 3 → Auxiliary): When SDD is about to consume a plan that contains **≥2 tasks** marked `Independent: true` with **disjoint `Files touched`**, the router suggests `dispatching-parallel-agents` for those tasks (the implementer fan-out happens in one assistant message; the rest of the plan stays on SDD's per-task triad). The user can decline; SDD's sequential dispatch is always the fallback. This is the **only** time the toolkit dispatches multiple implementers within one plan — every other path keeps SDD's "one implementer at a time" floor.

## Continuous mode (opt-in): spec-frozen → PR auto-advance

**Continuous mode** is an **opt-in** convention that lets the orchestrator auto-advance stage→stage from a frozen spec to a PR without a human "go" between stages (the default stays human-pumped). **Entry precondition:** the user opts in explicitly **and** a **human-approved** frozen entry artifact exists — either the `brainstorming` brief or a validated loom-spec change-folder. It adds a STOP rule, not a brain; the full doctrine lives in the reference.

**MANDATORY:** when the user opts into continuous mode ("run continuous to PR" / "連續跑到 PR"), **READ `references/continuous-mode.md` IN FULL before auto-advancing.** The stub here is not enough to run safely.

**Invariant (one line):** **never auto-merge**; **HALT** and escalate on re-plan / re-scope / re-route (and every STOP-contract row); **PR-open is the terminal stop** — the human merges.

## Red flags — agent rationalizations to refuse

| Agent says | Reality | Correct response |
|---|---|---|
| "I'll quickly fix this without a test." | Iron-Law violation. | Load `tdd-iron-law`, write the failing test first. |
| "This change is trivial, skip planning." | Trivial changes accumulate scope. | Ask 2-3 clarifying Qs. If still trivial after, proceed with TDD. |
| "I'll write all the code, tests last." | Test-after rationalization. | Refuse. Beck 2002 §Preface forbids. |
| "Subagents add overhead." | Context-window logic, not quality logic. | If task >1 hour or >1 module, SDD is mandatory. |
| "User said skip TDD." | Valid only if user is explicit *and* the work matches `tdd-iron-law/SKILL.md` §When NOT to Use (throwaway / generated / pure config). | Quote §When NOT to Use back; ask for explicit confirmation. |
| 「我先快速試一下 / ちょっと試すだけ」 | Same rationalization, localized. | Same refusal — load `tdd-iron-law`. |
| "I'll skip straight to the brief." | Skipping `brainstorming`'s Axis 0 upstream check before writing a brief = violation — new product-shaped work may need `using-loom-product-principles` / `using-loom-interface-design` / `using-loom-spec` first. | Load `brainstorming`; Axis 0 checks the reception criteria before Axis 1. |

## Skill types

- **Rigid** — `tdd-iron-law`, `subagent-driven-development`. Measure is non-negotiable; exception path is documented in-skill (§When NOT to Use). Do not invent new exceptions on the fly.
- **Flexible** — `brainstorming`, `writing-plans`, `systematic-debugging`. Adapt structure to the task; honor reasoned user override.

## Coexistence

- **`domain-teams:code-team`** — passive gate entry. Use it to audit existing artifacts; this toolkit is for building from scratch. The knowledge layer (`standards/`, `rubrics/`, `checklists/`) here is a byte-identical functional copy of `code-team/`; sync via `scripts/distribute.py`, drift-checked by `scripts/verify-drift.py`.
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — loom-code **delegates** to these at the right moments. Never duplicate their logic.
- **`obra/superpowers`** — overlapping skill names + dual SessionStart hook. To disable loom-code's hook injection: `export LOOM_CODE_MODE=off` in shell rc.
- **loom family reception** — `loom-pipeline`'s SessionStart hook carries the family map (the five `using-loom-*` entries) + the on-ramp criteria table; `brainstorming`'s Axis 0 points to it rather than duplicating it here.

## What this router does NOT do

- Does **not** write or review code itself — it routes.
- Does **not** auto-invoke downstream skills — the harness invokes them when the user's next message + Skill Priority match. **Exception:** when the user explicitly opts into **continuous mode** (see §"Continuous mode"), the orchestrator auto-advances stage→stage until a stop condition fires.
- Does **not** enforce one workflow for every task — Flexible skills (§Skill types) cover tailoring.
- Does **not** replace `domain-teams:code-team` — both ship; pick by use-case (build vs audit).

## Reference

Load each file **only when its trigger fires** — do NOT speculatively load all of them.

- `references/continuous-mode.md` — full Continuous-mode doctrine (entry/freeze, STOP contract, never-auto-merge). **MANDATORY:** when the user opts into continuous mode, READ this **IN FULL** before auto-advancing (the §"Continuous mode" stub above is not enough to run safely).
- `references/claude-code-tools.md` — Claude Code canonical tool names. Read only when the host is **Claude Code**.
- `references/codex-tools.md` — Codex CLI tool mapping (Phase 2.5 ship target). Read only when the host is **Codex CLI**.
- `references/engineering-baselines.md` — 12-rule engineering baseline carried by every loom-code plugin-level agent (SSOT in `../../scripts/_baseline.md`; v0.5.2 / P15-12).
- `references/environment-gotchas.md` — consolidated orchestrator harness / dcg / Read-tool-precondition gotchas (cross-cutting; pointed at by SDD / tdd-iron-law / finishing-a-development-branch / using-git-worktrees). Read only when an orchestrator hits a harness friction (blocked git command, "File has not been read yet", rebase conflict).
- `../../PRODUCT-SPEC.md` / `../../TECH-SPEC.md` / `../../ROADMAP.md` — design lock + phase plan.

**Do NOT load** every reference file up front — `continuous-mode.md` only on opt-in, the host-tool files only under their matching host, `environment-gotchas.md` only on a harness-friction trigger. The router body alone routes the common (human-pumped) path.
