# Brief — spec-expansion v0.2.1: dogfood hardening (F-1 pairwise discipline + F-3 single-surface backbone)

> **Stage**: brief (discovery already done — the 2026-06-12 real-seed dogfood IS the discovery). Base: branch off `origin/main` (`8e3607e0`).
> **Source**: `docs/loom/dogfood/2026-06-12-pip-note-app/` findings F-1 + F-3; grounded in the shipped A/B (`…/design/2026-06-11-L2-ab-validation-results.md`).

## Problem

Running shipped v0.2 end-to-end on a real greenfield seed (PiP markdown note app) surfaced two prose gaps in `spec-expansion/SKILL.md`:

- **F-1 — executor bypasses `scripts/pairwise.py`.** On a ≥4-object (wide) stage, the SKILL.md says "instead call the generator … pipe to its stdin", but an LLM executor naturally reasons the combinations inline and skips the tool. The shipped A/B proved in-prompt enumeration **leaks** at ≥4 objects (`missed_by_both` up to 11) — so the bypass is a correctness/adoption gap, not a style nit. The instruction is too soft.
- **F-3 — the linear USM backbone is a forced fit for single-surface apps.** The PiP note app has no sequential wizard journey ("Edit & preview" is a persistent mode, not a stage you pass through); the L3 nav-graph fit better than the spine. The skill currently assumes a left-to-right sequential journey and offers no escape for floating/utility/single-surface apps.

## Users

The agent executing `spec-expansion` (any host). Secondary: kouko, whose real app types (floating utilities) hit F-3.

## Smallest End State

Two additive prose edits to `spec-expansion/SKILL.md` (+ a version bump) — no logic, no new files:

- **F-1**: strengthen the Phase ③b wide-stage instruction from "instead call" to an imperative **MUST run `scripts/pairwise.py` and show the invocation; do NOT enumerate a ≥4-object stage's combinations inline** (inline enumeration on wide stages is the validated leak). Keep ≤3-object in-prompt enumeration as-is.
- **F-3**: add a note to Phase ① that for a **single-surface / utility / floating app with no sequential journey**, the USM backbone may **collapse to ~1 stage node** and the **navigation graph (Phase ③c) carries the structure** — do NOT force a linear multi-stage spine where none exists (forcing one manufactures fiction, violating the seed-adequacy honesty rail).

## Current State Evidence

- **Forward / target:** `spec-toolkit/skills/spec-expansion/SKILL.md` — F-1 at the "Wide stages (≥4 co-active objects)" paragraph (~L197-205, "instead call the generator `scripts/pairwise.py`"); F-3 at Phase ① "USM — lay the user-journey backbone" + "Also build the backbone as a navigation graph" (~L84-101).
- **Reverse (SSOT):** the SKILL.md prose is the SSOT for executor behavior; `test_spec_expansion_skill.py` is the grep-structural guard (asserts load-bearing phrases). New behavior phrases → new assertions there.
- **Error/guardrail:** must preserve the existing honesty rails (ban-"complete", seed-adequacy gate, sparse-output fallback) and stay < 500 lines (currently 316).
- **Data/Boundary:** no output-contract change; `scripts/pairwise.py` already exists and is unchanged; consumer (`writing-plans`) unaffected.

Evidence paths: `spec-toolkit/skills/spec-expansion/SKILL.md`, `spec-toolkit/scripts/test_spec_expansion_skill.py`, `docs/loom/dogfood/2026-06-12-pip-note-app/proposal.md` (F-1/F-3 evidence).

## Decision

Harden the two prose gaps the real-seed dogfood exposed. F-1 = make the pairwise-tool invocation mandatory + ban inline enumeration on wide stages (the validated leak). F-3 = allow the backbone to collapse to a single node for single-surface apps, letting the nav-graph carry structure. Version → 0.2.1. NOT changing logic, output contract, the interaction-density gate, or the pairwise script.

## Out of Scope

- F-2 (Phase-② fan-out ceremony) and F-4 (completeness-critic didn't run) — both are execution-context observations, not SKILL.md defects; no change.
- pairwise CLI input-validation (the earlier 🟢 review nit) — separate next-touch.
- Any logic / script / output-format change.

## Open Questions

- None blocking. (F-1's exact wording: "MUST run + show invocation + do-not-inline-enumerate" — settled above.)
