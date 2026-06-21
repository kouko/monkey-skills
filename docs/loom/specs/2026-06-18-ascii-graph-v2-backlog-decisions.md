# ascii-graph v2 — backlog decisions (deletion-first gate)

> Records which v2 backlog items were **built** vs **deliberately not built**,
> with the reasoning, so a future session does not re-propose the declined ones.
> Decisions reached via `dev-workflow:complexity-critique` (deletion-first gate)
> on 2026-06-18.

## Outcome

| Item | Decision | One-line reason |
|---|---|---|
| **v2-A** layered-architecture `arch` generator | ✅ **built + merged** (PR #414, v0.2.0) | High-value, in the alignment envelope. |
| **v2-C** sequence-diagram `seq` generator | ✅ **built** (PR #415, v0.3.0) | High communication value, deterministic grid layout. |
| **v2-B** `align.py --fix` box-row auto-fix | ⛔ **declined** | YAGNI — see below. |
| **v2-D** external-engine integration | ⛔ **declined** | Breaks the zero-dep thesis — see below. |
| **v2-E** SSOT cleanup nits | ⏸ **deferred** | Premature abstraction — see below. |

## v2-B — `align.py --fix` (DECLINED)

Mindset: *Simplicity-vs-Easy* (Hickey). align.py has **one role** — a read-only
width **oracle**. `--fix` is the *easy* feature (feels like closing the loop), not
the *simple* one.

- **Q1 (smallest end state):** keep the oracle report-only. The shapes `--fix`
  could safely auto-fix (box/table, where a border defines target width) are
  *exactly* the shapes that already have by-construction generators
  (`gen_table`/`gen_arch`/`gen_flow`). For the thin remaining slice (hand-drawn
  box/table not regenerated), the existing report already gives line + col + exact
  width mismatch, and re-padding is space-only (1-cell) — reliable for the model.
- **Q2:** +80–100 lines of fragile box-boundary parsing (the same layout problem
  `checks_kink`/`checks_table` grapple with) + write-back + CLI + tests. After ≫ before.
- **Q3:** nothing deleted (report path stays for seam/kink/free-topology drift).
- **Complection:** braids a **DO** path into a pure **VERIFY** oracle — contradicts
  the skill thesis (align.py = checks *on* the model, not doing *for* it).
- **Verdict: REJECT.** Revisit only if real usage shows the model re-introduces
  drift when re-padding from the report (not observed; padding is spaces).

## v2-D — external-engine integration (DECLINED)

Mindset: *Design-Is-Taking-Apart* (Hickey, complect vs compose).

- **Q1:** the honest ceiling already emits **Mermaid source** for the uncovered
  types — a faithful, renderable, zero-dep artifact. The engine path *still* falls
  back to it, so Mermaid-source stays either way; the engine is pure addition.
- **Q2:** binary detect + subprocess shell-out + per-engine output parsing + a
  mandatory **CJK-width validation/post-processing** layer (because **no** off-the-
  shelf engine renders all Mermaid types CJK-display-width-correct — v1 survey:
  merman/mermaid-ascii/beautiful-mermaid each partial, different failure mode) +
  fallback + cross-platform/version handling + tests. Plus an external Rust/Go/Node
  **runtime** that breaks the load-bearing **zero external binary, pure-Python** thesis.
- **Q3:** nothing deleted — Mermaid-source fallback must remain.
- **Complection (permanent, not transitional):** since no engine is all-types-CJK-
  correct, the validation+fallback never pays itself off — the dependency braid is forever.
- **Verdict: REJECT.** The "contribute a CJK width fix upstream to beautiful-mermaid
  (has the width fn, unwired in its ASCII path)" idea is a *separate, different-repo*
  effort — not this plugin's v2. Revisit only if a single engine becomes
  all-types-CJK-correct (then it's a thin compose, not a permanent complect).

## v2-E — SSOT cleanup nits (DEFERRED, not declined)

Each is gated on a "3rd occurrence" trigger that has **not** fired:

- `_center` duplicated in `gen_flow.py` + `gen_arch.py` (+ `gen_seq.py` has its own
  centering) — extract to a shared helper (e.g. in `width.py`) **when a clear 3rd
  identical consumer appears**; today the copies are below Fowler's Rule-of-Three.
- `enumerate_columns()` shared walker between `checks_seam` / `checks_kink` — same
  "on the 3rd occurrence" rule; still at 2.
- `checks_table.py` light-frame literals vs importing `glyphs.py` — minor SSOT
  tightening; do OR soften the docstring, low priority.
- `render_seq` is ~144 lines (most complex generator) — extraction seam: lift the
  label-row / arrow-row builders out of the message loop into named helpers. Filed
  debt from the v2-C whole-branch review (🟡, non-blocking); fully test-covered.

Doing any of these now would be speculative abstraction (YAGNI). Pick them up when
their trigger genuinely fires.

## Net

v2 ships **two new generators** (`arch`, `seq`) and **deliberately declines** the
three items whose cost exceeds their end-state value under the skill's own
design thesis (script-is-the-oracle; zero-dep, pure-Python). "Finishing v2" =
informed build/decline of every backlog item, not building all of them.
