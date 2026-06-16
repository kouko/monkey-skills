# Brief — purpose-fit relevance-floor lever (end-check, lever ③)

date: 2026-06-13
branch: feat/deep-deep-research-vs-angle-selector
skill: research-toolkit/skills/deep-deep-research
status: brief (brainstorming output → writing-plans)

## Problem

The framework-audit lever makes research **complete**, and the purpose-fit experiment proved completeness then **crowds out relevance**: the decision-bearing findings are only ~12–24% of the output and sit buried in a 360° dump. The job: *when a research run has a (stated or inferable) decision purpose, surface the few decision-bearing findings and honestly label the rest — without deleting anything — so the reader isn't left to re-rank a 360° list themselves.*

JTBD (Klement form): **When** I've run a completeness-audited research pass for a specific decision, **I want** the decisive few findings foregrounded for that decision (and anything that could settle it outright flagged loudly), **so I can** act without my decision drowning in balanced-but-irrelevant coverage.

This is the **end-check (Plan A)** placement — purpose ranks/organizes the *already-complete* confirmed claims at synthesis time. It does **not** steer what gets searched (front-end steering = Plan C, evaluated and deferred this session: it trades a recoverable mis-ranking for an unrecoverable failure-of-imagination, and its premise is unestablished — see Alternatives).

## Users

The deep-deep-research agent at Stage 6 (synthesis), and the human reading the report. Fires **only when opt-in** (like VS / framework-audit / meta-mode); default research stays 360°. The purpose is **inferred from context + stated as a visible assumption + confidence-gated** — the user is NOT required to type a purpose (per this session's design discussion). Output is consumed by the human reader and feeds the meta-mode synthesis-stance + base synthesis prompt.

## Smallest End State

A new opt-in pass, after Stage 5 (confirmed claims) and feeding Stage 6, that:
1. **Infers the decision purpose** from the question + context, states it as a visible assumption with a confidence level (does NOT require the user to state it).
2. **Classifies confirmed claims** into `decisive / contextual / not-relevant-for-this-purpose` — **never deleting** (not-relevant items are labeled, kept).
3. **Consolidate-when-confident**: rich/high-confidence purpose → foreground that one decision-frame's decisive set. **Multi-frame fallback**: thin/low-confidence → organize by the question-type's N common decision-frames (small N, kept separate), evenly.
4. **Moot-hoist** (the eval-critical fix): any finding that could *settle the decision outright* is hoisted to a top-level "this may decide it" callout **above all frames**, never dissolved into a single frame.
5. Emits a **purpose-fit block** that PREPENDS the base synthesis prompt (mirroring `mode_route.stance_block`), so synthesis foregrounds the decisive few. **Never edits synced `prompts.py`.**
6. Opt-in SKILL.md subsection + own tests + zero synced-primitive drift + English-only.

## Current State Evidence

- **Forward** — `SKILL.md`: the lever-integration pattern is established — `### Opt-in: Framework completeness-audit` (L151, a Stage-1 additive pass) and `### Opt-in: Meta-mode synthesis-stance routing` (L422, a Stage-6 additive wrap that PREPENDS a directive ahead of the byte-identical base synthesis prompt, L477–482). purpose-fit is a Stage-6-area pass like meta-mode: it operates on Stage-5 confirmed claims and prepends a block to synthesis. Quick-ref table at L522–548.
- **Reverse (SSOT/coupling)** — `../../scripts/sync-primitives.sh`: the **only** synced primitives are `schemas.py / rank.py / prompts.py / dedup.py` (deep-deep-research is SSOT, byte-identical-copied to siblings behind a CI MD5 gate). `framework_audit.py` and `mode_route.py` are **house code, NOT synced** — purpose-fit's new module is the same: **house code, do not touch the four primitives** (per `feedback_house_additions_in_new_module_not_synced_ssot`). The purpose-fit block prepends synthesis exactly as `mode_route.stance_block` does — base `prompts.py synthesis` stays byte-identical.
- **Pattern analog** — `scripts/mode_route.py` (~250 lines) is the near-exact template: `schema` / `classify-prompt` / `stance` (a directive builder) CLI subcommands; `MODE_VERDICT_SCHEMA`; `stance_block()` PREPENDs to synthesis; `main()` CLI dispatch. purpose_fit.py mirrors this: `schema` / `purpose-classify-prompt` / `block`.
- **Error/Boundary** — `test_mode_route.py` is the test analog (schema shape, prompt-content assertions, block-assembly, CLI round-trip). `test_module_source_is_english_only` CJK guard covers `scripts/` + `references/` → all new content English-only (the prototyped N-frame catalog is in Chinese eval notes → translate). Module name `purpose_fit.py` is safe (not a stdlib shadow — cf. `feedback_select_py_shadows_stdlib_select`).
- **Reference-file analog** — `references/framework-audit-library.md` (routing-by-question-type + cell-blocks) is the template for the new `references/purpose-frames.md` (decision-frame catalog by question type).

Evidence paths: `SKILL.md`, `scripts/mode_route.py`, `scripts/framework_audit.py`, `scripts/test_mode_route.py`, `../../scripts/sync-primitives.sh`, `references/framework-audit-library.md`. Design SSOT: the 3 purpose-fit/eval vault notes (experiment + multi-purpose eval + front-end prior-art) + the A/C evaluation.

## Decision

**Build the end-check purpose-fit lever as a new house-code module `scripts/purpose_fit.py` + `references/purpose-frames.md` + opt-in SKILL.md subsection + `test_purpose_fit.py`, mirroring `mode_route.py`.** Pipeline placement: operates on Stage-5 confirmed claims, emits a purpose-fit block that prepends the synthesis prompt, ordered **purpose-fit-block → meta-mode-stance-block → base synthesis prompt** (both additive prepends; base `prompts.py` untouched). Opt-in only.

Module shape (deterministic logic only; agent supplies the reasoning, per the executor model):
- `purpose_fit.py schema` → the purpose-fit verdict schema: `{inferred_purpose, confidence, mode: "consolidated"|"multi-frame", mooting_factors: [...], frames: [{frame, decisive:[claim ids], contextual:[...], not_relevant:[...]}]}`.
- `purpose_fit.py purpose-classify-prompt --question Q --confirmed-block CB [--frames-from references/purpose-frames.md]` → the agent prompt that (a) infers purpose + confidence from question/context, (b) decides consolidated vs multi-frame by confidence, (c) classifies confirmed claims decisive/contextual/not-relevant **without deleting**, (d) **flags mooting factors** ("would this settle the decision outright?").
- `purpose_fit.py block` → reads the agent's verdict JSON from stdin, emits `{purpose_fit_block: "<directive>"}` — a synthesis-prepend directive that (i) states the inferred purpose + confidence, (ii) **hoists mooting factors to a top-level callout**, (iii) foregrounds the decisive few (consolidated) or presents N frames (multi-frame), (iv) labels not-relevant honestly. Never deletes; never edits `prompts.py`.
- `references/purpose-frames.md` — decision-frame catalog by question type (start with **equity: entry / trim / income / position-size** and **software-adoption: velocity / scale / cost-burden / lock-in-reversibility**, + a generic fallback; English-only; expandable). Small N (≤4 per type) per the eval's anti-collapse guard.

The three eval-validated behaviors are all load-bearing and all in v1: **consolidate-when-confident** (rich case), **multi-frame fallback** (thin case), **moot-hoist** (the fix for the macOS/k8s/microservices failures). Dropping any re-opens a failure the eval already caught.

## Out of Scope

- **Front-end steering (Plan C / hybrid)** + its ε-floor eval — evaluated and deferred this session (unrecoverable failure-of-imagination risk; unestablished premise; revisit only if 360°+this-lever is later observed to miss deep decisive factors).
- Any change to synced primitives (`schemas/rank/prompts/dedup.py`), the default scope path, VS mode, default synthesis prose, framework-audit, the just-shipped blind-spots section.
- A large/exhaustive purpose-frame catalog — start with 2 question-type families + generic fallback; expand later.
- A standalone eval harness in-repo — the eval lives in the vault notes (the lever's value is already experiment-validated).
- Requiring the user to type a stated purpose (inference + confidence-gate is the contract).
- PR / push of this or the blind-spots commit (separate user decision).

## Alternatives Considered (research-grounded — 3 rounds + A/C eval this session)

- **Plan B (pure front-end steering)** — rejected: moves WYSIATI to the generation stage (unrecoverable — can't surface what was never searched). Prior-art: failure-of-imagination (9/11), unknown-unknowns.
- **Plan C (hybrid front-end VoI-weighted depth + ε floor)** — deferred: prior-art research showed VoI is a valuation tool not a search-router (category error), the exploration floor is not established doctrine, there's a counter-tradition (仮説思考), and the premise (360°+A misses deep factors) is unestablished. A is independently worth building first; C gates on later evidence.
- **Stated-purpose-required input** — rejected: too much friction; inference + visible-assumption + confidence-gate is lower-friction and the eval's multi-frame fallback handles the no-confident-purpose case.
- **Single-inferred-purpose (no multi-frame)** — rejected: confident wrong guess mis-ranks everything; multi-frame fallback + confidence-gate is safer (this session's design discussion).
- **Anchor on Kahneman-Lovallo-Sibony 2011** — rejected (Thread-B round 3): scope-mismatch; DQ appropriate-frame + JTBD + WYSIATI are the purpose-matched anchors.

## What Becomes Obsolete

Nothing removed (additive opt-in lever, like VS / framework-audit / meta-mode). Justified-additive, not YAGNI: experiment-validated value. The N-frame catalog supersedes the ad-hoc per-eval purpose lists (consolidate them into the reference file).

## Open Questions

- Exact purpose-fit verdict schema field names + whether infer-purpose and classify are one agent prompt or two (lean: one combined `purpose-classify-prompt`, like framework-audit's single audit-prompt) — pin in plan.
- Whether `block` ordering vs meta-mode is fixed (purpose-fit → meta-mode → base) or configurable — lean fixed in v1.
- `references/purpose-frames.md` exact catalog content (translate the prototyped equity/software frames from the eval notes) — author in an early task.
