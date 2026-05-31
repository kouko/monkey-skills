---
name: using-code-toolkit
description: Router for code-toolkit — invoke whenever the user wants to **build, change, debug, or review code** (features / bug fixes / refactors / migrations / reviews / dependency bumps). Drives a Superpowers-style flow — brainstorm → plan → subagent-driven development → TDD iron-law → systematic debugging → code review → finish branch — with each rule grounded in primary sources (Beck 2002 / Martin 2008 / Fowler 2018 / OWASP ASVS / 徳丸本 Ch.6). 程式碼開發・流程紀律・一級書目 grounding。コーディング・プロセス規律・原典 grounding.
version: 0.9.0
---

<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer), **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
**You have code-toolkit.** If the user is starting any coding work — feature / bug fix / refactor / review / migration — you **must** route through this skill before writing implementation code.

Five load-bearing rules:

1. **Brainstorm before implementing.** Explore intent + alternatives first. Call `brainstorming` — 5-axis framework (Problem / Users / Smallest End State / Alternatives / What Becomes Obsolete) → structured brief.
2. **TDD is the iron law.** No production code without a failing test first. Call `tdd-iron-law`. Beck (2002, ISBN 978-0321146533) Preface: *"Make it fail. Make it pass. Make it clean."* Floor, not aspiration.
3. **Split + dispatch (SDD).** Task >1 hour or >1 module → `subagent-driven-development`; atomic ≤5-min units; three subagents per task (implementer / spec-reviewer / code-quality-reviewer).
4. **Never push without review.** `git push` / `gh pr create` / `gh pr merge` without prior `requesting-code-review` PASS (or `finishing-a-development-branch` flow) = violation. Push commands trigger review, not bypass.
5. **Research before asking.** Non-trivial design / strategy / tech-stack question to user MUST cite WebSearch findings (2-4 industry approaches w/ sources). *"X or Y?"* without industry context = violation. Use `brainstorming` Axis 4 protocol for the research. This is gate ② of the full asking-the-user discipline — gate ① (whether to ask: do reversible/inferable steps without asking, always confirm outward/irreversible actions) and gate ③ (plain, jargon-free phrasing with a state anchor) are enforced in the downstream skills (`brainstorming` / `subagent-driven-development` / `requesting-code-review`).

**Skipping any of these = violation.** "I'll just quickly…" / "just push" / "just ask" / 「ちょっと試すだけ」 / 「先 push 再說」 / 「先問再說」 are rationalizations — refuse them.
</EXTREMELY-IMPORTANT>

## Instruction priority

When instructions conflict, follow this order:

1. User's `CLAUDE.md` / project conventions — local rules always win.
2. code-toolkit skills loaded into context — this router + invoked specialists.
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
| 8 | Branch close | `finishing-a-development-branch` → delegates `dev-workflow:git-memory` | ✅ shipped |

**Auxiliary** (on-demand, not part of the linear stage flow):

- `using-git-worktrees` — parallel branches / long-running experiments / design-then-build cycles with one repo, N checkouts.
- `dispatching-parallel-agents` — 2+ independent problem domains (multiple unrelated test failures, multiple modules to audit, N disjoint data fetches, atomic tasks the plan marks `Independent: true`). Across-task / across-domain dispatch via one assistant message with multiple `Agent` calls. Complements `subagent-driven-development`'s within-task reviewer parallelism.

**Auto-suggest hook** (Stage 3 → Auxiliary): When SDD is about to consume a plan that contains **≥2 tasks** marked `Independent: true` with **disjoint `Files touched`**, the router suggests `dispatching-parallel-agents` for those tasks (the implementer fan-out happens in one assistant message; the rest of the plan stays on SDD's per-task triad). The user can decline; SDD's sequential dispatch is always the fallback. This is the **only** time the toolkit dispatches multiple implementers within one plan — every other path keeps SDD's "one implementer at a time" floor.

## Red flags — agent rationalizations to refuse

| Agent says | Reality | Correct response |
|---|---|---|
| "I'll quickly fix this without a test." | Iron-Law violation. | Load `tdd-iron-law`, write the failing test first. |
| "This change is trivial, skip planning." | Trivial changes accumulate scope. | Ask 2-3 clarifying Qs. If still trivial after, proceed with TDD. |
| "I'll write all the code, tests last." | Test-after rationalization. | Refuse. Beck 2002 §Preface forbids. |
| "Subagents add overhead." | Context-window logic, not quality logic. | If task >1 hour or >1 module, SDD is mandatory. |
| "User said skip TDD." | Valid only if user is explicit *and* the work matches `tdd-iron-law/SKILL.md` §When NOT to Use (throwaway / generated / pure config). | Quote §When NOT to Use back; ask for explicit confirmation. |
| 「我先快速試一下 / ちょっと試すだけ」 | Same rationalization, localized. | Same refusal — load `tdd-iron-law`. |

## Skill types

- **Rigid** — `tdd-iron-law`, `subagent-driven-development`. Measure is non-negotiable; exception path is documented in-skill (§When NOT to Use). Do not invent new exceptions on the fly.
- **Flexible** — `brainstorming`, `writing-plans`, `systematic-debugging`. Adapt structure to the task; honor reasoned user override.

## Coexistence

- **`domain-teams:code-team`** — passive gate entry. Use it to audit existing artifacts; this toolkit is for building from scratch. The knowledge layer (`standards/`, `rubrics/`, `checklists/`) here is a byte-identical functional copy of `code-team/`; sync via `scripts/distribute.py`, drift-checked by `scripts/verify-drift.py`.
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — code-toolkit **delegates** to these at the right moments. Never duplicate their logic.
- **`obra/superpowers`** — overlapping skill names + dual SessionStart hook. To disable code-toolkit's hook injection: `export CODE_TOOLKIT_MODE=off` in shell rc.

## What this router does NOT do

- Does **not** write or review code itself — it routes.
- Does **not** auto-invoke downstream skills — the harness invokes them when the user's next message + Skill Priority match.
- Does **not** enforce one workflow for every task — Flexible skills (§Skill types) cover tailoring.
- Does **not** replace `domain-teams:code-team` — both ship; pick by use-case (build vs audit).

## Reference

- `references/claude-code-tools.md` — Claude Code canonical tool names.
- `references/codex-tools.md` — Codex CLI tool mapping (Phase 2.5 ship target).
- `references/engineering-baselines.md` — 12-rule engineering baseline carried by every code-toolkit plugin-level agent (SSOT in `../../scripts/_baseline.md`; v0.5.2 / P15-12).
- `../../PRODUCT-SPEC.md` / `../../TECH-SPEC.md` / `../../ROADMAP.md` — design lock + phase plan.
