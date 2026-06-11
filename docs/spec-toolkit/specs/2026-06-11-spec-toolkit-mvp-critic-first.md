# Brief: spec-toolkit MVP — critic-first thin slice (v0.1)

> **Type**: brainstorming brief (input to `writing-plans`)
> **Date**: 2026-06-11
> **Status**: Brief drafted, awaiting sign-off → plan
> **Driver**: kouko — close the GENERATE gap (Station 1 of the 4-station "stably produce code" pipeline)
> **Grounding**: `docs/spec-toolkit/research/2026-06-11-spec-toolkit-openspec-research-synthesis.md` (research) + 5 vault notes + OpenSpec 2026-06 web check

> **Positioning (revised post-dogfood, 2026-06-11)**: The original bet — "the critic finds omissions a capable model misses" — was tested by a **7-seed A/B dogfood** (`spec-toolkit/examples/AB-SUMMARY.md`) and came back **weak + situational**: the recall edge appears only in object-deep, under-documented operational domains (inventory, workforce), never dramatically, and is ≈zero in textbook domains. The **reliable, domain-independent value is structural**: verification-ready `GIVEN/WHEN/THEN` acceptance criteria + enforced blind-spots/provenance that a free brainstorm does not produce. **spec-toolkit is therefore positioned as a "structured, verification-ready spec output" tool — NOT a "finds more than you would" tool.** The Problem/Smallest-End-State below are preserved as the original planning record; read them through this corrected lens. See `spec-toolkit/README.md` for the shipped positioning.

## Problem
(Axis 1 — JTBD)

When kouko (or a future coding session) starts a non-trivial coding task from a **sparse idea**, the AI builds happy-path-only "slop" — it silently picks its own definition of "done" and skips the paths / states / edge cases a complete spec would have named. The job: **systematically expand a sparse seed into a high-recall spec (paths + edge cases + candidate acceptance criteria) so the right + complete thing gets built on the first pass**, instead of being caught late by the VERIFY layer (or not at all). "Build spec-toolkit" is the means; the job is **filling the GENERATE gap that code-toolkit (VERIFY) and OpenSpec (DECLARE) both explicitly leave open**.

## Users
(Axis 2 — who, conditions)

kouko — solo, building/maintaining the **monkey-skills monorepo (~21 plugins)**; hosts = Claude Code / Codex / Cursor; potentially marketplace installers later. Job story: *When I start a non-trivial feature from a few lines of intent, I want the spec's path/edge coverage fanned out and its blind spots flagged, so I hand code-toolkit a complete spec instead of discovering gaps during review.* **Hard constraint (from research-toolkit prior):** runs **inside a host agent**, must be **agent-portable / key-free / no external runtime dependency** — the host supplies the LLM + tools; the skill supplies the method.

## Smallest End State
(Axis 3 — critic-first thin slice; user-selected 2026-06-11)

**Two skills, built on our own primitives, output = plain markdown in OpenSpec change-folder shape (no OpenSpec CLI dependency yet):**

1. **`spec-expansion`** — sparse seed → objects + CTAs → per-object state machines → `backbone × object × CTA × state` grid → path / edge matrix + candidate acceptance criteria. Multi-agent fan-out. Every item tagged `provenance: seeded | inferred | critic-found`.
2. **`completeness-critic`** — loop-until-dry over the expansion; multi-lens fixed interrogation (missing object/actor · state completeness · cross-object/system-layer failures · NFR · policy/legal); **must emit its own blind spots** ("aspects I cannot judge → needs human/field input"). This is the **defensible differentiator** (CoDD expands-only; Spec Kit clarifies-not-adversarial; VSDD critiques-code-not-spec).

**Output (hybrid format — confirmed 2026-06-11)**: a directory mirroring the OpenSpec change-folder shape — `proposal.md` + `specs/` delta. **OpenSpec delta format is the skeleton** (`## ADDED Requirements → ### Requirement → #### Scenario: GIVEN/WHEN/THEN`, RFC-2119) — the load-bearing contract joint to VERIFY, zero migration when OpenSpec CLI wires in (v0.2), `openspec validate`-clean (structure-only). **spec-toolkit's differentiating richness goes in additive markdown sections** that OpenSpec's structure-only validate tolerates: `## Provenance` (seeded/inferred/critic-found per item), `## Blind spots — needs human/field input` (the critic's load-bearing output), `## Path × edge matrix` (appendix). NOT a custom format, NOT vanilla OpenSpec. Plain markdown, writable without `openspec init`.

**DoD / dogfood**: expand one real sparse seed end-to-end → the output's scenarios feed straight into `code-toolkit:writing-plans` as RED/GREEN acceptance criteria. Proves the critic catches an omission a one-shot brainstorm would miss.

## Current State Evidence
(Greenfield plugin with three integration touch points — most sub-bullets N/A)

- **Forward (entry points)**: New plugin `spec-toolkit/` does not exist (`ls */` confirms — no `spec-toolkit/`). Skeleton model = `research-toolkit/`: `.claude-plugin/plugin.json` + `skills/<name>/SKILL.md` (+ optional `skills/<name>/scripts/`). **No README×3 and no SessionStart hook required** (`find research-toolkit -type f` → only plugin.json + skills/; lighter than the packaging note's "~6 files / hook router" estimate).
- **Reverse (downstream consumer / SSOT)**: The output is consumed by `code-toolkit:writing-plans`, which (per `code-toolkit/skills/writing-plans/SKILL.md`) turns acceptance criteria into atomic RED/GREEN tasks. The brainstorming default brief path is `docs/code-toolkit/specs/` — spec-toolkit's output is the spec layer *upstream* of that. **No SSOT conflict**: spec-toolkit owns GENERATE artifacts, code-toolkit owns VERIFY; OpenSpec change-folder is the (future) neutral contract.
- **Error**: N/A — greenfield; no existing error paths touched.
- **Data**: Output schema = OpenSpec delta-spec markdown (`## ADDED Requirements`/`#### Scenario: GIVEN/WHEN/THEN`, RFC-2119), confirmed current at OpenSpec v1.4.1 (docs/concepts.md, web check 2026-06-11).
- **Boundary**: Registration touch point = root `.claude-plugin/marketplace.json` (`plugins[]` array, each `{name, description, source}`) — one new entry `./spec-toolkit/`. This is the only existing tracked file the MVP must modify.

Evidence paths: `research-toolkit/.claude-plugin/plugin.json`, `research-toolkit/skills/*/SKILL.md`, `.claude-plugin/marketplace.json`, `code-toolkit/skills/writing-plans/SKILL.md`, research synthesis §2–§4b.

## Decision
(What we build / what we do NOT / why)

Build **`spec-toolkit` v0.1** as a new, agent-portable, key-free plugin with **two skills** (`spec-expansion` + `completeness-critic`) that turn a sparse seed into a high-recall, blind-spot-flagged spec draft written as **plain markdown in OpenSpec change-folder shape**. **Build our own** (do not adopt/wrap CoDD — it's an expand-only Python pip dep that doesn't do the critic we differentiate on; reimplementing the *pattern* on host primitives is cheaper and honors the agent-portable prior). **Defer** OpenSpec-CLI wiring, the `spec-discovery`/`spec-persist`/router skills, and the SSOT knowledge-layer share — those land once the differentiator (critic) is proven end-to-end and the OpenSpec DECLARE brief is implemented. The completeness-critic **critiques the SPEC for omissions only** — it never reviews code or runs TDD (that boundary belongs to code-toolkit / VSDD).

## Out of Scope
(v0.1)

- **OpenSpec CLI integration** (`openspec init` / `instructions` / `validate` / `archive`) — output is plain markdown in the change-folder *shape*; CLI gate slots in when DECLARE lands.
- **`spec-discovery` skill** (intent clarification) — the seed is assumed already articulated (e.g. from `code-toolkit:brainstorming`); discovery is v0.2.
- **`spec-persist` skill + `using-spec-toolkit` router** — v0.2; MVP skills are invoked directly.
- **Knowledge-layer SSOT share** (`distribute.py`-style functional copy of `spec-consistency.md`) — v0.2; MVP inlines what it needs.
- **Proportional-rigor tiering** (No-Spec/Lite/Full trigger logic) — v0.2 (lives in the router).
- **Codex/Cursor cross-host testing** — v0.1 validates on Claude Code; portable-by-construction, tested later.
- **Re-opening** spec-toolkit-vs-integrate or OpenSpec Q6=A (settled).

## Alternatives Considered
(Axis 4 — research-grounded; full evidence in synthesis §4b)

- **Adopt/wrap CoDD `codd-dev`** (shipped pip, spec→design-doc wave expansion) — *rejected*: external pip + Python-runtime dep for the *non*-differentiating half; expand-only (no critic); 16 stars. Borrow its patterns (wave/dependency ordering, validate gate, `@generated-from` traceability), not its code.
- **Full 5-skill pipeline now** — *rejected for v0.1*: large; binds on the unimplemented OpenSpec DECLARE brief; defers proof of the differentiator.
- **Static spec file vs live state object** — *resolved*: liveness (task state machine) is OpenSpec's job (`tasks.md` + `instructions apply --json`); spec-toolkit writes the static change-folder shape, liveness arrives via the DECLARE layer later.
- **Boundary vs VSDD** (shipped CC plugin: SDD+TDD+adversarial) — *resolved*: VSDD's adversary critiques code/impl; spec-toolkit's critic critiques the spec for omissions. Different targets; spec-toolkit stops at GENERATE.

## What Becomes Obsolete
(Axis 5)

- Manual edge-case enumeration inside `code-toolkit:brainstorming` / `writing-plans` for high-tier changes (spec-expansion systematizes it).
- The OpenSpec brief's "generation / completeness is out-of-scope" gap — spec-toolkit fills it (update the brief's framing when DECLARE lands).
- Nothing in code-toolkit is removed — different layer (additive across the boundary; not YAGNI because it fills a named, evidenced gap).

## Open Questions
- **Engine fan-out mechanism**: `code-toolkit:dispatching-parallel-agents` / Workflow for per-object parallel expansion — confirm fit within a skill (vs sequential) during planning.
- **Critic rubric source**: inline the multi-lens checklist for v0.1, or seed it from the QA notes (ISTQB state-transition / JSTQB テスト観点)? Lean inline for MVP.
- **Acceptance-criteria runnability**: harness-course L08 argues each criterion should carry a *runnable* verification command, not prose. v0.1 emits `#### Scenario: GIVEN/WHEN/THEN` (testable but not executable) — is that enough, or must MVP emit runnable checks? Lean: scenario-level for MVP; runnable-check is writing-plans/TDD's job.
- **Test strategy for the skills themselves**: spec-expansion/critic are prompt-driven; what's the RED test? (Likely a fixture seed → assert output contains required structural sections + ≥1 critic-found blind spot. Resolve in plan.)
