# 2026-06-10 — Command Surface Establishment Capability

> **Type**: Capability spec (proposal / draft)
> **Status**: Draft — design-lock proposed (§8.1), awaiting kouko ratification; then brainstorm→plan→implement (v1 = 野心 A)
> **Origin**: Research notes (kouko vault) `2026-06-10 Agent Makefile…` + `2026-06-10 Command Surface 整合進 code-toolkit…`
> **Suggested branch**: `feat/command-surface`
> **Purpose**: Treat the command surface as a **living artifact** and give code-toolkit the ability to (a) **consume** a project-declared surface (execution earns trust), (b) **seed** one when absent, and (c) **accrete** it as the project grows — declaring a verb for each new runnable capability, bound into the SDD Definition of Done. Targets the `AGENTS.md` standard. A reliable surface is a precondition for `verification-before-completion` to mean anything.

---

## 1. Context & problem

`verification-before-completion` (vbc) is code-toolkit's execution-based verification gate — the load-bearing "is it actually done" check. Today vbc obtains the test command by **detection**: it reads signal files (`package.json`, `pyproject.toml`, `go.mod`, …) and maps them to a canonical command via [`skills/verification-before-completion/references/test-invocation-by-stack.md`](../../../skills/verification-before-completion/references/test-invocation-by-stack.md).

Two gaps follow:

1. **Detection outranks declaration, unconditionally.** In that table, `Makefile`/`justfile` sit at the **bottom**, tagged "Generic" (lowest-priority fallback). That is backwards for the common case — a declared surface (`AGENTS.md`, `make check`) captures author intent detection cannot see. But the fix is **not** a blunt "prefer declaration": declarations rot and can lie. The correct rule (see §4.1) is **consult declaration first, let execution decide trust** — a declared verb wins only once it actually runs and emits a parseable test count; otherwise fall back to detection.
2. **When no usable command surface exists, vbc has nothing solid to run.** It falls back to a guessed single command. If the guess is wrong or incomplete, "verification" becomes theater — the exact failure vbc exists to prevent.

> **Architectural framing**: a *sufficient command surface* is a **precondition** for the verification gate to mean anything. Ensuring it is therefore in-scope for a process-discipline toolkit, not an add-on.

### Industry standard (verified 2026-06)
- **`AGENTS.md` is the de-facto standard for declaring build/test/lint commands** — donated to the Linux Foundation's **Agentic AI Foundation (AAIF)** in 2025-12 (alongside MCP and goose), 60k+ repos, read natively by 30–60+ tools.
- **Caveat**: `AGENTS.md` standardizes the *file/location*, **not a machine-readable command schema**. Commands are free-form Markdown prose. So: *where to declare* is standardized; *verb vocabulary / structure* remains convention (`make help` / `--list` / standard verb names).
- **Implication**: the builder must target `AGENTS.md`. Do **not** invent a new format (e.g. `.agent-makefile.toml`) — that fights a governed standard and violates baseline Rule 2.

---

## 2. Goal & non-goals

### Goal
- **G1 (Layer A — foundation)**: invert detection priority — prefer a project-declared command surface over per-language detection, in vbc and the implementer path.
- **G2 (Layer B — the capability)**: treat the command surface as a **living artifact** — **seed** it when absent, **accrete** it as capabilities are added (a verb per new runnable capability, bound into the SDD Definition of Done), and **handle drift** by re-verifying via execution; a detect→verify→instantiate builder backs the seed step. All targeting `AGENTS.md`.

### Non-goals
- ❌ Inventing a new command-declaration format. Target `AGENTS.md`.
- ❌ Proactively patrolling / rewriting a repo's `AGENTS.md` outside an active task.
- ❌ Replacing per-language detection — it remains the fallback when no declared surface exists.
- ❌ A general "repo configurator". **Seed** only when the surface is absent; **accrete** only when a task introduces a new runnable capability — never proactive patrol/rewrite, never per-task polling.
- ❌ Standardizing a verb schema (no industry standard exists; honor convention, don't ratify one).

---

## 3. Definitions

### 3.1 Command surface
A set of stably-named, discoverable, deterministic verbs (`test`, `lint`, `build`, `check`, …) that an agent can invoke without guessing, declared so the agent finds them on a fresh session. Backends: `AGENTS.md` declaration + `make`/`just`/`npm scripts`/`Taskfile` recipes.

### 3.2 "Sufficient" — two tiers

| Tier | Criterion | Serves |
|---|---|---|
| **Minimum-sufficient** (seed bar) | Agent can discover and run a **`test` verb** without guessing (declared in `AGENTS.md`, or a `make`/`just` `test` recipe exists) | `verification-before-completion` works |
| **Fully-sufficient (relative)** | **Every runnable capability the project *currently* has** is declared as a verb (`test`, plus `lint`/`build`/`check`/`e2e`/`migrate`… *as they exist*) and verified to run | Whole brainstorm→…→finish-branch flow has stable entry points |

**Minimum-sufficient is the SEED bar** (unblocks the verification gate). **Fully-sufficient is NOT a fixed `test+lint+build+check` checklist forced upfront — it is a moving target relative to the project's current capabilities, reached by accretion** (§4.2 beat ②). You never pre-declare a `deploy` verb before deployment exists.

---

## 4. Capability design

### 4.1 Layer A — command resolution: declared-first consult, trust earned by execution (foundation, prose-only)

**Principle: trust is earned by execution, not granted by source.** Consult the project-declared surface first — it captures intent detection cannot see (custom harness, required env, monorepo entry, the umbrella `check`). But a declaration only *wins* after it has been run and produced a parseable result. Otherwise fall back to detection. Never blindly trust a declaration; never hard-fail on a broken one.

Resolution order for the test command:
1. **Consult declared surface first** — `AGENTS.md` commands section, `make`/`just` `test`/`check` recipes, README commands. Prefer a declared **granular `test` verb**.
2. **Earn trust by execution** — vbc runs whatever it picks and parses the output anyway; the declared verb only counts if it (a) actually runs (no command-not-found / nonzero-from-missing-target) AND (b) emits a parseable test-count signal (`N passed`, N>0).
3. **Fall back, don't fail** — if the declared verb fails to run, or its output is not parseable for a test count (e.g. a bundled `check` mixing lint+test), fall back to the signal-detection table. Do not hard-fail; do not use a signal-opaque declaration as the gate (§6).

Three guardrails:
- **Broken declaration → fall back to detection** (not a hard failure).
- **Signal-opaque declaration (bundled `check`) → not used as the vbc gate** — use granular `test`; the umbrella `check` belongs to `finishing-a-development-branch` (§6).
- **Re-verify, don't trust stale** — declarations rot; a verb is trusted only after being executed-and-parsed *this session*, not carried across sessions (§8 Q6).

Touch points:
- `test-invocation-by-stack.md` — add a priority-0 step before the signal table: "Consult the project-declared surface first; a declared verb outranks detection **only if it runs and emits a test count**, else fall back to the table below."
- `verification-before-completion/SKILL.md` Process step 1 — "Detect the package-level test command" → "Resolve the test command (declared-first consult; the declaration wins only if it runs and emits a test count; else fall back to detection)."
- implementer path (`agents/implementer.md` / SDD dispatch) — pass the resolved verb down; cache **within the session only** (Rule 6 token economy), re-resolve across sessions because declarations rot.

### 4.2 Layer B — the command surface as a living artifact: seed → accrete → consume → anti-drift (the capability)

A command surface is **neither built-once-and-frozen nor re-polled every task**. It is a living artifact that **accretes as the project grows** (add e2e tests → add `test-e2e`; add a DB → add `migrate`). Four beats:

```
① SEED        When no surface exists → establish the minimum: a runnable, declared `test` verb.
              Trigger: surface-absent preflight (ONCE), via writing-plans. Semi-automatic in v1
              (agent drafts, human confirms — this is frontier; no proven auto-build precedent).

② ACCRETE     Event-driven, NOT per-task polling. When a task introduces a NEW runnable capability,
              that SAME task declares its verb + verifies it runs. Bound into the SDD task
              Definition of Done — exactly as TDD couples "add behaviour" with "add a test".
              No new capability → no surface change.

③ CONSUME     Layer A (§4.1) reads whatever the CURRENT surface is, on every verify
              (declared-first consult → execution earns trust → else fallback).

④ ANTI-DRIFT  Because it accretes (and tooling changes), the surface drifts — so a verb must
              RE-EARN trust by execution; never trust stale across sessions (§8 Q6).
              On seed/accrete: verify-before-declare; on unresolved gap → Fail loud (Rule 12),
              do not fabricate a surface.
```

> **"Complete" is relative + moving.** Fully-sufficient = complete relative to the project's *current* capabilities (§3.2), reached by accretion — not a fixed `test+lint+build+check` checklist forced upfront. This dissolves the proportional-rigor tension: the surface grows to match what the project actually has, no over-building.

Three hard constraints:
1. **Target `AGENTS.md`** (standard), not a new format; add a `@AGENTS.md` shim for Claude Code (§8 Q7).
2. **Verify before declare** — never declare a verb that has not been run and observed to work.
3. **Seed + builder run through code-toolkit's own plan→implement; accretion rides the SDD Definition of Done** — neither is black-box generation.

---

## 5. Integration points

| # | Where | File (repo-relative) | Change | Layer |
|---|---|---|---|---|
| ① | Detection table | `skills/verification-before-completion/references/test-invocation-by-stack.md` | Add priority-0 "prefer declared surface" step | A |
| ② | Verify gate process | `skills/verification-before-completion/SKILL.md` (Process step 1) | "Detect" → "Resolve: declared-first, detect-fallback" | A |
| ③ | Implementer contract | `agents/implementer.md` + SDD dispatch in `skills/subagent-driven-development/SKILL.md` | Pass resolved verb down; session cache | A |
| ④ | Seed preflight + accretion DoD | preflight in `skills/writing-plans/SKILL.md` (seed when surface absent) + Definition-of-Done coupling in `skills/subagent-driven-development/SKILL.md` (declare a verb for each new runnable capability) | B |
| ⑤ | Seed builder | new skill (e.g. `establishing-command-surface`) or a planned-subtask template | detect→verify→instantiate the seed into `AGENTS.md` (+ `@AGENTS.md` shim) | B |

> **SSOT note**: `test-invocation-by-stack.md` is code-toolkit-unique (not a functional copy synced from `domain-teams:code-team`), so editing ①② does **not** trip `verify-drift.py`. Clean to edit.

---

## 6. The `check` vs `test` signal tension (must-resolve)

vbc detects the "0 tests ran" configuration bug by parsing the runner's `N passed` summary (`test-invocation-by-stack.md` §"Detecting 0 tests ran"). A project `check` that bundles lint+typecheck+test produces interleaved output → vbc cannot read a clean test-count signal → the "0 tests ran" defense is defeated. vbc also explicitly treats lint as orthogonal to verification (`SKILL.md` L21).

**Resolution** (matches the standard `test`/`check` verb split):
- **vbc consumes the granular `test` verb** (preferred over detection) — keeps the test-count signal.
- **The umbrella `check` (lint+typecheck+test) maps to `finishing-a-development-branch`** — which already sequences `requesting-code-review` + `verification-before-completion`. That is the umbrella's natural home.
- The builder, when instantiating, should expose **both** a granular `test` verb and (optionally) a `check` umbrella — not collapse them.

---

## 7. Alignment with baseline & PRODUCT-SPEC

- **Rule 2 (Simplicity First)** — no new format; reuse the detection table; prose-first.
- **Rule 4 (Goal-Driven)** — the minimum-sufficient seed bar is a concrete, testable success criterion; verify-before-declare makes each accreted verb goal-checked (declare only what runs).
- **Rule 11 (Match conventions)** — target `AGENTS.md`; honor existing skill/test/doc layout.
- **Rule 12 (Fail loud)** — verify-before-write; surface gaps rather than fabricating a surface.
- **PRODUCT-SPEC boundary** — builder triggers only when surface is insufficient *and* a verifying task needs it; no proactive repo rewriting (stay a builder, not a configurator).

---

## 8. Open questions to lock before build

1. **Placement of resolution / seed / accretion**: where does each beat live? Resolution at verify-time in `verification-before-completion`; seed as a one-off surface-absent preflight in `writing-plans`; accretion as an SDD Definition-of-Done item (verb-per-new-capability) rather than a per-task polling gate.
2. **Builder form**: a dedicated skill (`establishing-command-surface`) vs a reusable planned-subtask template consumed by `writing-plans`? Skill = discoverable + testable; template = lighter, no router entry.
3. **Trigger threshold**: default bar = minimum-sufficient. Should fully-sufficient ever be *required* (e.g. at `finishing-a-development-branch`)?
4. **`AGENTS.md` write policy**: create vs augment-in-place; how to avoid clobbering human-authored sections (append a managed block? respect existing commands?).
5. **Scope of backend creation**: only write `AGENTS.md`, or also scaffold a `justfile`/`Makefile` `check`? (Leaning: `AGENTS.md` only by default; backend recipe optional and opt-in.)
6. **Re-verify vs cache (declarations rot)**: a declared verb must earn trust by execution, not be trusted on sight. How long does a validated verb stay trusted — current session only (re-resolve next session) vs persisted across sessions? (Leaning: session-scoped cache for token economy per Rule 6; re-resolve across sessions, since `AGENTS.md` is among the fastest-drifting files in a repo.)
7. **Cross-tool compatibility (Claude Code does not read `AGENTS.md`)**: Claude Code reads only `CLAUDE.md` (issue #34235, no roadmap as of 2026-06); Codex/Cursor/Windsurf read `AGENTS.md`. Two distinct reads: **active resolution** (the implementer agent `Read`s `AGENTS.md` / runs `just --list` — unaffected by auto-loading) vs **passive injection** (session auto-loads only `CLAUDE.md`). Implications: (a) 1A resolution works regardless; (b) for the advisory declaration to be passively present in Claude Code, and for 1B-scaffolded surfaces to be visible, a compat shim is required. **Leaning: `@AGENTS.md` import** — keep `AGENTS.md` canonical, write a thin `CLAUDE.md` containing `@AGENTS.md` (+ optional Claude-specific notes). Alternatives: symlink `CLAUDE.md`→`AGENTS.md` (Windows-fragile), pre-commit copy. The 1B builder must create this shim when scaffolding a surface in a Claude-Code repo.

---

## 8.1 Design-lock draft — recommended answers to §8

> Status: **proposed defaults** (kouko to ratify). These resolve §8 so the spec can move Draft → buildable. Grounded in the research note + baseline rules + OpenSpec's proportional-rigor finding.

- **Q1 (placement) → not a per-task gate; split into resolution / seed / accretion.** *Command resolution* (which verb to run, 野心 A) = **lazy, inside vbc**. *Seed* (野心 B, when the surface is absent) = **one-off preflight in `writing-plans`** — becomes an explicit "seed the surface" task. *Accretion* = **event-driven, bound into the SDD task Definition of Done** (a task that adds a runnable capability declares its verb) — NOT a per-task polling gate. The surface is a living artifact, not a checkpoint.
- **Q2 (builder form) → planned-subtask template first, promote later.** Start as a reusable subtask template consumed by `writing-plans` (no SKILL.md, no router entry, no version bump, no Codex port). Promote to a dedicated `establishing-command-surface` skill **only if dogfooding shows repeated reuse**. Honors Rule 2 (no speculative abstraction).
- **Q3 (threshold) → minimum-sufficient seed; fully-sufficient is relative + grown by accretion, never forced.** The seed bar is a runnable `test` verb. "Complete" = relative to the project's *current* capabilities (§3.2), grown by accretion (§4.2 ②) — not an upfront `test+lint+build+check` checklist. Keep *verification* rigor proportional per task (routine = run `test`; higher-risk, e.g. at `finishing-a-development-branch` = run the umbrella `check`). Surface-completeness and per-task verification rigor are separate dials.
- **Q4 (AGENTS.md write policy) → augment-in-place with a managed block.** Wrap generated commands in `<!-- BEGIN command-surface (managed) -->` / `<!-- END -->` markers; never overwrite human-authored sections; if a `## Commands` section already exists, extend it, don't duplicate. Reuses the BEGIN/END-marker convention code-toolkit already uses in `distribute.py` baseline injection.
- **Q5 (backend creation scope) → AGENTS.md (+ shim) by default; backend recipe opt-in + current-aware.** Usually the project already has `npm`/`pytest`/etc., so the surface just **names** them in AGENTS.md — no backend file needed. Scaffold a backend recipe only when there is genuinely no runnable entry (detection also fails); then follow the project: extend an existing `justfile`/`script/`, else default to the leanest (`scripts/init.sh` or `justfile`), **never Make**. (See research note Appendix A.)
- **Q6 (re-verify vs cache) → session-scoped cache, re-resolve across sessions.** Rule 6 token economy within a session; AGENTS.md drifts, so don't trust stale across sessions. Cheap safety: invalidate the cache if the declaring file's content-hash changes mid-session.
- **Q7 (cross-tool compat) → `@AGENTS.md` import** (kouko preference). Canonical = AGENTS.md; thin `CLAUDE.md` containing `@AGENTS.md` (+ optional Claude-specific notes). 野心 A resolution is unaffected (agent actively `Read`s files); the 野心 B builder creates the `@import` shim when scaffolding in a Claude-Code repo. Alternatives (symlink / pre-commit copy) documented but not default.

**Net v1/v2 shape after lock:**
- **v1 (野心 A)** — edit 3 files (`test-invocation-by-stack.md`, `verification-before-completion/SKILL.md`, `implementer.md`/SDD dispatch): command resolution = declared-first consult → execution earns trust → fallback to detection; vbc consumes the granular `test` verb; session-scoped cache. Pure prose, near-zero risk.
- **v2 (野心 B)** — the surface as a living artifact: **seed** (one-off surface-absent preflight) + **accrete** (verb-per-new-capability bound into the SDD Definition of Done) + **anti-drift** (re-verify by execution). Seed builder writes an AGENTS.md managed block + `@AGENTS.md` shim; backend opt-in + current-aware; verify-before-declare; Fail-loud on unresolved gaps. Semi-automatic seed in v1 (frontier — no proven auto-build precedent).

## 9. Phased plan (dogfood code-toolkit's own workflow)

1. **Phase A — foundation (prose-only)**: integration points ①②③. Low risk; ships the priority inversion + signal-tension fix. Pressure-test under `tests/verification-before-completion-pressure/`.
2. **Phase B1 — seed preflight + accretion discipline**: point ④. Surface-absent preflight (seed, one-off) + couple "declare a verb for any new runnable capability" into the SDD task Definition of Done (accretion). Define the seed/min-sufficient bar as a testable assertion. No per-task polling gate.
3. **Phase B2 — seed builder**: point ⑤. The detect→verify→instantiate template/skill for the seed step; verify-before-declare; managed AGENTS.md block + `@AGENTS.md` shim; new pressure tests; router entry if a skill; version bump + tri-lingual README update.
4. Each phase via brainstorm → writing-plans → SDD (TDD iron law) → requesting-code-review → verification-before-completion → finishing-a-development-branch.

---

## 10. References

- Research (kouko vault): `2026-06-10 Agent Makefile（Agentic Makefile）概念與應用研究`, `2026-06-10 Command Surface 整合進 code-toolkit 研究`, `2026-05-27 Agent Harness 的 Stable Command Surface`, `2026-05-27 Build System vs Task Runner`.
- Standard: [agents.md](https://agents.md/) · [Linux Foundation AAIF announcement](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation).
- code-toolkit: `skills/verification-before-completion/SKILL.md` + `references/test-invocation-by-stack.md`, `scripts/_baseline.md`, `agents/implementer.md`, `skills/finishing-a-development-branch/SKILL.md`, `PRODUCT-SPEC.md`.
