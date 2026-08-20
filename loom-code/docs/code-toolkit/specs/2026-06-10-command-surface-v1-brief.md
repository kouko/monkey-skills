# Brainstorming brief — Command Surface v1 (野心 A: command resolution)

> **Type**: brainstorming output (consumed by `writing-plans`)
> **Branch**: `feat/command-surface`
> **Parent spec**: `2026-06-10-command-surface-establishment.md` (§8.1 design-lock ratified 2026-06-10)
> **Scope lock**: v1 = 野心 A only. Bound by ratified §8.1 **Q1 / Q3 / Q6**. Q2/Q4/Q5/Q7 are 野心 B → out.

## Problem

(Axis 1 — JTBD) When `verification-before-completion` (vbc) runs to confirm a task/branch is "done", the green it reports must reflect **the command the project actually uses to test** — which a project author often declares (`AGENTS.md` commands, `make test`, `just test`). Today vbc obtains the command by **detection only** (`test-invocation-by-stack.md` signal→command table), and detection runs **unconditionally first**, ignoring any declared surface. A declared surface captures author intent detection cannot see (custom harness, required env, monorepo entry). When detection guesses wrong or incomplete, "verification" becomes theater — the exact failure vbc exists to prevent.

Job story: *When I finish a task and vbc checks it, I want the gate to run the project's own declared test verb (if it actually works), so the pass I see is the project's real test surface — not a per-language guess.*

The fix is **not** blunt "declaration always wins" — declarations rot and lie. Correct principle: **信任由執行決定，不由來源** — a declared verb wins only after it runs AND emits a parseable test count; else fall back to detection. Never hard-fail on a broken declaration.

## Users

(Axis 2) code-toolkit's own automated agents, running on **any consuming project repo**:
- **vbc gate** — end-of-task / end-of-branch; owns the resolution logic (§8.1 Q1: resolution is lazy, inside vbc).
- **implementer subagent** — during SDD's TDD loop; runs package-level tests and must use the resolved verb, not re-guess (③b consumer).
- **SDD orchestrator** — resolves once, caches **session-scoped** (Q6), passes the verb into implementer dispatch (③a producer).

Conditions: fresh session (cache empty → re-resolve); the consuming project may or may not declare a surface. Existing tool: the 24-row detection table (`test-invocation-by-stack.md`), where `Makefile`/`justfile` currently sit at the **bottom**, tagged "Generic" lowest-priority.

## Current State Evidence

- **Forward (what calls the resolution path)**: `verification-before-completion/SKILL.md:51` Process step 1 — *"**Detect** the package-level test command … see references/test-invocation-by-stack.md"*. This is the entry point that becomes "Resolve". `SKILL.md:53` step 3 already parses output (*"total test count > 0, all-pass summary line"*) — the "execution earns trust" machinery is **already present**; v1 only adds the declared-first consult ahead of it.
- **Reverse (SSOT ownership)**: `test-invocation-by-stack.md` is **code-toolkit-unique**, NOT a functional copy synced by `scripts/distribute.py` (confirmed: spec §5 SSOT note; the BEGIN/END `baseline-v1`/`rule-sheet-v1` managed blocks in `implementer.md:65,175` are the only distribute-owned regions, and they are NOT touched by v1). Editing ①②③ does **not** trip `verify-drift.py`.
- **Error (fallback/fail-loud path)**: `test-invocation-by-stack.md:44-57` "Detecting 0 tests ran" — the `N passed`/test-count signal logic. This is what a bundled `check` (interleaved lint+test output) would defeat → drives the §6 decision: vbc consumes **granular `test`**, never umbrella `check`.
- **Data (the table being reframed)**: `test-invocation-by-stack.md:7` *"Detect by signal files at project root"* (framing to amend); `:32` `Makefile with test:` → Generic; `:33` `justfile with test:` → Generic (both bottom-of-table, lowest priority — the inversion target).
- **Boundary (dispatch contract, producer/consumer)**: `subagent-driven-development/SKILL.md:93` step 1 dispatches implementer *"with the task description + context paths + resource paths"* (③a — add: pass resolved verb + session cache). `agents/implementer.md:218-239` Input contract `### Task / ### Context / ### Resource Paths (protocol / standards / repo / branch)` (③b — add: receive + use the resolved test verb).

Evidence paths appendix:
- `code-toolkit/skills/verification-before-completion/SKILL.md` (L51, L53)
- `code-toolkit/skills/verification-before-completion/references/test-invocation-by-stack.md` (L7, L32-33, L44-57)
- `code-toolkit/skills/subagent-driven-development/SKILL.md` (L93)
- `code-toolkit/agents/implementer.md` (L218-239; managed blocks L65, L175 = do-not-touch)
- `code-toolkit/tests/verification-before-completion-pressure/prompts/index.md` (pressure-prompt convention)
- `code-toolkit/tests/integration/test-rule-sheet-drift.sh` (executable grep-assertion convention)

## Decision

**Build**: weave a **declared-first consult → execution earns trust → else fallback-to-detection** resolution rule into the existing vbc resolution path, as prose. Concretely, **3 integration points = 4 edit targets + 1 deterministic structural assertion + 1 behavioral pressure prompt**:

- **① detection table** (`test-invocation-by-stack.md`) — add a **priority-0** step ahead of the signal table: *consult the project-declared surface first; a declared verb outranks detection ONLY if it runs and emits a test count, else fall back.* Reframe the `:7` "Detect by signal files" intro to "Resolve (declared-first, detect-fallback)"; note Makefile/justfile may now be consulted as declared surface (not only the Generic bottom fallback).
- **② vbc gate** (`verification-before-completion/SKILL.md:51`) — step 1 *"Detect the package-level test command"* → *"Resolve the test command (declared-first consult; the declaration wins only if it runs and emits a test count; else fall back to detection)."*
- **③a SDD dispatch** (`subagent-driven-development/SKILL.md:93`) — pass the **resolved verb** down in the implementer dispatch; resolve once, cache **session-scoped**, re-resolve across sessions (Q6).
- **③b implementer contract** (`agents/implementer.md` Input contract) — **receive** the resolved test verb and **use** it for package-level test runs instead of re-detecting (closes the producer/consumer contract; without ③b the field ③a sends spins empty).
- **Test (TDD RED→GREEN)**: a deterministic executable assertion (grep-based, in the style of `tests/integration/test-rule-sheet-drift.sh`) that asserts each required rule string is present in ①②③ — RED before edits, GREEN after. PLUS a **behavioral pressure prompt** in `tests/verification-before-completion-pressure/prompts/` (a declared-surface scenario: project declares `make test` AND is also pytest-detectable → gate must consult the declaration first, but fall back if it emits no test count) + its `index.md` MUST/MUST NOT row.

**Why**: highest leverage, near-zero risk; fixes vbc reliability at its root (wrong command = meaningless gate); edits only code-toolkit-unique files (no SSOT drift). The "execution earns trust" half already exists in vbc step 3 — v1 is purely the declared-first consult + the pass-down plumbing.

**Will NOT build**: 野心 B (seed / accrete / builder / managed AGENTS.md block / `@AGENTS.md` shim / backend scaffolding). No new declaration format. No `check`-as-gate. No change to standards/rubrics/checklists or distribute-managed blocks.

## Alternatives Considered

(Axis 4 — researched + ratified in parent spec, verified 2026-06; not re-run)
1. **aider `test-cmd` / `lint-cmd` + `auto-test` verify→fix loop** (aider docs) — the proven "consume a declared command" pattern. **Adopted as the model** for declared-first consult. Pro: config-declared, run-after-edit, industry-validated. Con: aider hard-declares; v1 adds the "execution earns trust, else fallback" guardrail on top (stronger).
2. **AGENTS.md governed standard** (Linux Foundation AAIF, 60k+ repos) — *where* to declare is standardized; verb vocabulary is not. **Adopted as the target** the consult reads. (Backend storage / shim = 野心 B.)
3. **Blunt "reverse to declaration-first"** — **rejected**: declarations rot/lie; trust must be earned by execution.
4. **`.agent-makefile.toml` new format** — **rejected**: fights AGENTS.md, violates baseline Rule 2.
5. **Bundled `check` as the vbc gate** — **rejected**: interleaved output kills the `N passed` signal (§6); `check` → `finishing-a-development-branch`.

Note (EN/JA): Superpowers (code-toolkit's upstream) has **no** command-discovery mechanism — vbc's detection table already goes one step beyond it; v1 extends that lead. No mainstream skillset auto-builds a surface (that's 野心 B frontier).

## What Becomes Obsolete

(Axis 5) — handle in the same change:
- The unconditional **"Detect by signal files at project root"** framing (`test-invocation-by-stack.md:7`) → reframed to declared-first resolution.
- The **Makefile/justfile = Generic, lowest-priority bottom-of-table** positioning (`:32-33`) → these are now first-class declared-surface candidates (consulted at priority-0), though detection rows remain as fallback.
- The verb **"Detect"** in vbc Process step 1 (`SKILL.md:51`) → "Resolve".
- Detection itself is **NOT** obsolete — it remains the explicit fallback. Nothing is deleted wholesale; this is a reframe + prepend, not a rewrite.

## Out of Scope

- 野心 B in all forms: seed preflight (writing-plans), accretion-in-SDD-DoD, the detect→verify→instantiate builder, managed `<!-- BEGIN/END command-surface -->` AGENTS.md block, `@AGENTS.md` Claude-Code shim, backend (`justfile`/`scripts/`) scaffolding.
- Any new command-declaration file format.
- Making `check` (umbrella lint+typecheck+test) the vbc gate.
- standards/ · rubrics/ · checklists/ (SSOT functional copies) and distribute-managed BEGIN/END blocks in agent files.
- Cross-session persistence of the resolved verb (Q6: session-scoped only).
- Wiki/vault sync of the command-surface page (handoff P3; not blocking).

## Open Questions

- **None blocking.** §8.1 ratified; Q1/Q3/Q6 bind v1 and are resolved. Minor implementation call deferred to `writing-plans`: whether the deterministic RED assertion lives as a new `tests/integration/*.sh` or as an inline grep block — both satisfy TDD; pick the lighter at plan time.
