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
| 8 | Branch close | `finishing-a-development-branch` → delegates `dev-workflow:git-memory` | ✅ shipped |

**Auxiliary** (on-demand, not part of the linear stage flow):

- `using-git-worktrees` — parallel branches / long-running experiments / design-then-build cycles with one repo, N checkouts.
- `dispatching-parallel-agents` — 2+ independent problem domains (multiple unrelated test failures, multiple modules to audit, N disjoint data fetches, atomic tasks the plan marks `Independent: true`). Across-task / across-domain dispatch via one assistant message with multiple `Agent` calls. Complements `subagent-driven-development`'s within-task reviewer parallelism.

**Auto-suggest hook** (Stage 3 → Auxiliary): When SDD is about to consume a plan that contains **≥2 tasks** marked `Independent: true` with **disjoint `Files touched`**, the router suggests `dispatching-parallel-agents` for those tasks (the implementer fan-out happens in one assistant message; the rest of the plan stays on SDD's per-task triad). The user can decline; SDD's sequential dispatch is always the fallback. This is the **only** time the toolkit dispatches multiple implementers within one plan — every other path keeps SDD's "one implementer at a time" floor.

## Continuous mode (opt-in): spec-frozen → PR auto-advance

By default the pipeline is **human-pumped**: between every stage the user says "go". **Continuous mode** is an **opt-in** convention that lets the orchestrator run stage→stage unattended — from a frozen spec all the way to a PR — **without losing the verification gates**. It adds a STOP rule, not a brain.

**Entry — at the SPEC, not the plan.** Continuous mode starts only when **both** hold:

1. The user **opts in** explicitly (e.g. "run continuous to PR" / "連續跑到 PR"). The default stays human-pumped.
2. A **human-approved, frozen spec** exists. Two entry artifacts are accepted (the user picks one — see freeze discrimination below):
   - **(a) the `brainstorming` hand-off brief** (`docs/loom/specs/<topic>.md`), the per-feature artifact that locks the *approach*; or
   - **(b) a human-approved loom-spec change-folder** (`docs/loom/<change-id>/`) as an **alternative** entry artifact alongside the brief — the upstream loom-spec output the user has signed off on.

   Either way this is **not** the repo-level PRODUCT-SPEC / TECH-SPEC. **Design + spec stay human-gated** (sign-off locks the *approach* via `brainstorming`'s Smallest-End-State / Alternatives axes, or via the user's approval of the change-folder). The plan is **not** a human checkpoint: it is the mechanical sequencing of an already-decided approach, so it is **auto-generated** by `writing-plans` and **gated** by the `plan-document-reviewer` evaluator subagent (a real writer≠judge **plan gate**, PASS / NEEDS_REVISION). The plan becomes one more auto-advance-with-gate stage.

**Freeze discrimination — declared, NOT content-shape sniffed (R6).** The freeze does **not** classify the entry artifact by sniffing its content shape. Instead, the **user declares** which artifact to run on (the brief, or a change-folder at a named path), and the freeze **confirms** the change-folder by two checkable signals — never a fuzzy content-shape classifier:
- **(a) named-artifact presence** — `specs/<capability>/spec.md` exists at the declared change-folder path; and
- **(b) validator exit 0** — `loom-spec/scripts/validate_spec_output.py <change-folder>` returns **exit 0** (the cross-plugin gate; loom-spec owns the format, loom-code reuses it — no new validator). A non-zero exit HALTS the freeze and escalates (the artifact is not validate-clean).

This follows the declaration-gate learning: don't fake a fuzzy objective detector — make the agent declare it, and gate the consequence on a checkable signal. Upstream stays human-gated; the STOP contract + never-auto-merge terminal below are **unchanged**.

**Auto-advance behavior.** Within continuous mode the orchestrator proceeds `writing-plans → plan gate → SDD per-task triad → whole-branch review → verification → finish→PR` without waiting for a human "go", **unless a stop condition fires**.

**Stop contract (halt-and-escalate).** The run halts and escalates when any row fires:

| # | Stop trigger | Notes |
|---|---|---|
| 0a | **plan critical-path depth >5** (`writing-plans` route-back) | scope too deep → escalate: **re-cut** the spec. Existing forcing function |
| 0b | **`plan-document-reviewer` = NEEDS_REVISION for 2 rounds** | plan can't be made schema-valid / atomic → escalate. Existing 2-round cap |
| 1 | implementer returns **BLOCKED** | agent self-declares it needs a human; safe direction |
| 2a | **review-revision loop**: 2 reviewer↔implementer round-trips still NEEDS_REVISION | spec/quality gap; no WebSearch — fix is human clarification, not research |
| 2b | **debug loop**: `systematic-debugging` exhausts (2 hypotheses → mandatory WebSearch → hypothesis #3 still falsified) | reuses the existing **anchored-thinking** guard; zero new logic |
| 3 | a **scope / decision the plan did not specify** arises (not in the spec) | don't let the agent invent scope unattended |
| 4 | the agent **self-declares an assumption** outside plan/spec coverage | honest self-declaration trigger, not a fuzzy confidence detector |
| 5 | **whole-branch review = NEEDS_REVISION** (cross-task) | direct stop; cross-task issues most need human eyes — do NOT auto-remediate |
| 6 | any **PASS_WITH_NOTES** (per-task or whole-branch) | **auto-advance**; accumulate the notes, surface them all at the PR |
| 7 | **PR-open reached** | terminal stop; human merges; **never auto-merge** (inherited from `finishing-a-development-branch`) |

**Crutch-vs-verification line (load-bearing).** Within a task the agent may re-attempt **inside the existing gate loops** up to the bounds above (retry-within-bounds = verification). It may **NOT re-plan, re-scope, or re-route** — those HALT and escalate, they are not autonomous decisions. WebSearch is allowed only as `systematic-debugging`'s hypothesis-#3 input, never as a general "research a workaround" escape hatch.

**Escalation surfacing (two-layer).**

- **(i) Stop-and-wait (baseline, always):** the run **halts** and emits a clear **"why I stopped + what I need from you"** message plus the accumulated PASS_WITH_NOTES. Zero infrastructure.
- **(ii) Proactive notification (layered, optional):** if the host supports it (push notification / proactive message), send the stop reason so the user gets it while away. **Degrades gracefully** to (i) when the host lacks the capability — never a hard dependency.

This mode is **composed over existing gates** — it references, and does not duplicate, `systematic-debugging` (the anchored-thinking / WebSearch guard for row 2b), `subagent-driven-development` (the per-task verdicts), and `finishing-a-development-branch` (the PR-stop / never-auto-merge terminal).

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
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — loom-code **delegates** to these at the right moments. Never duplicate their logic.
- **`obra/superpowers`** — overlapping skill names + dual SessionStart hook. To disable loom-code's hook injection: `export LOOM_CODE_MODE=off` in shell rc.

## What this router does NOT do

- Does **not** write or review code itself — it routes.
- Does **not** auto-invoke downstream skills — the harness invokes them when the user's next message + Skill Priority match. **Exception:** when the user explicitly opts into **continuous mode** (see §"Continuous mode"), the orchestrator auto-advances stage→stage until a stop condition fires.
- Does **not** enforce one workflow for every task — Flexible skills (§Skill types) cover tailoring.
- Does **not** replace `domain-teams:code-team` — both ship; pick by use-case (build vs audit).

## Reference

- `references/claude-code-tools.md` — Claude Code canonical tool names.
- `references/codex-tools.md` — Codex CLI tool mapping (Phase 2.5 ship target).
- `references/engineering-baselines.md` — 12-rule engineering baseline carried by every loom-code plugin-level agent (SSOT in `../../scripts/_baseline.md`; v0.5.2 / P15-12).
- `../../PRODUCT-SPEC.md` / `../../TECH-SPEC.md` / `../../ROADMAP.md` — design lock + phase plan.
