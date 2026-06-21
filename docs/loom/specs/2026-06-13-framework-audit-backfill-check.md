# Brief — framework-audit verify-backfill check (① shared-blind-spot fix)

- **Date**: 2026-06-13
- **Skill**: `research-toolkit/skills/deep-deep-research/`
- **Branch**: `feat/deep-deep-research-vs-angle-selector` (continue)
- **Motivation**: Phase-2 eval RUN (vault note §三-B-2) found the "① execution gap" shared blind spot — a framework-audit gap angle *exists* (e.g. ASML "DCF + Comparables" → relative-valuation cell) but the downstream research never lands a confirmed finding for it (it fetched DCF, never peer multiples). The cell the audit flagged as important ends up still uncovered, silently.

## Problem

Lever ① proposes gap angles tagged `framework`+`cell`. Those get fed into the normal pipeline (search→fetch→verify). But nothing checks whether each flagged cell *actually produced a confirmed finding*. A gap angle can be generated, searched, and still yield zero confirmed evidence — and the report gives no signal that a deliberately-flagged structural dimension came up empty. Job: *after verify, tell me which audit-flagged cells did NOT land a confirmed finding, so I can re-search them within budget or honestly surface them as known gaps — instead of silently dropping them.*

## Users

The agent running the (opt-in) framework-audit pass. After Stage 5 verify, it wants a deterministic "which flagged cells are still empty?" check, so the audit's value (flagging structural dimensions) isn't lost to incomplete downstream research.

## Smallest End State

One new deterministic function + CLI subcommand in `framework_audit.py`, plus a short SKILL.md step:

- **`backfill_check(gap_angles, confirmed_labels)`** — `gap_angles` = the audit-prompt output (each `{label, query, framework, cell, ...}`, BEFORE `select` strips the tags); `confirmed_labels` = the set of angle labels that yielded ≥1 confirmed claim (the agent derives this from the verify output — Stage 2 fans out per-angle and the label tags everything downstream). Returns `{unlanded: [{label, framework, cell, query}], landed_count, unlanded_count}` — the gap angles whose label is absent from `confirmed_labels`. Match by case-folded label (mirror `_angle_keys` label normalization).
- **`backfill` CLI subcommand** — stdin `{gap_angles, confirmed_labels}` → stdout `{unlanded, landed_count, unlanded_count}` (mirror the `select` stdin/stdout idiom).
- **SKILL.md** — a short step in the framework-audit subsection: after the pipeline runs, derive `confirmed_labels`, run `backfill`, and for each unlanded gap either re-search that angle within remaining `MAX_FETCH` OR surface it in the report as an explicitly-flagged known gap ("dimension X was flagged important but no reliable evidence was found"). Degradation: empty `unlanded` → nothing to do.

## Current State Evidence

- `scripts/framework_audit.py:233` `select_gaps` + `:341` `select` CLI — the stdin/stdout + `_angle_keys` label-normalization idiom to mirror. `:203` `_angle_keys` (casefold label key). `:219` `_strip_angle` (drops framework/cell — confirming the tagged gap list must come from audit-prompt output, not select output).
- `scripts/framework_audit.py:276-345` `main()` argparse subparsers (`schema`/`classify-prompt`/`audit-prompt`/`select`) — add `backfill` here; `valid` is derived from `sub.choices` so it auto-updates.
- `SKILL.md` framework-audit subsection (`### Opt-in: Framework completeness-audit`) — append the backfill step; quick-ref table gets a `backfill` row.
- Label-flow: `SKILL.md` Stage 2 "the label tags everything downstream" + per-angle fan-out → the agent can collect the labels whose claims survived Stage-5 quorum. Decoupled contract: the script takes `confirmed_labels` as given; it does NOT parse the claim schema.
- **Do NOT touch** synced primitives (schemas/rank/prompts/dedup.py) or mode_route.py.

## Decision

Add a deterministic `backfill_check` + `backfill` CLI to `framework_audit.py` (lever ①'s own module — checking its gap angles landed is its concern), matched by case-folded label, plus a SKILL.md step + quick-ref row. Pure logic, stdlib-only, no schema coupling. TDD.

## Out of Scope

- Auto re-search orchestration (the agent decides re-search vs surface-as-gap; the script only *identifies* unlanded cells).
- Any change to `select_gaps` / the existing gap-generation flow.
- The ② library learning-loop and ③ completeness-critic lever (separate items).
- Coupling the check to the claim/finding schema (kept decoupled via the `confirmed_labels` contract).
- Synced primitives; mode_route.py.

## Alternatives Considered

- **Couple the check to the claim schema** (script parses confirmed claims to find their angle labels) — rejected: couples framework_audit.py to the extract/verify schema internals; the `confirmed_labels` set-contract is simpler and schema-agnostic.
- **Put the check in synthesis.py** — rejected: it's about framework-audit gap cells, so it belongs in framework_audit.py (cohesion); synthesis.py is also closer to the rank/synthesis primitives.
