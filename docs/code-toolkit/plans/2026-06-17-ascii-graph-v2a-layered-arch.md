# Plan: ascii-graph v2-A — layered-architecture generator (`arch`)

Source brief: docs/code-toolkit/specs/2026-06-17-ascii-graph-v2a-layered-arch.md
Total tasks: 4
Critical-path depth: 3 (≤5)   ← T1 → T3 → T4; T2 runs parallel with T3
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-17, 14/14 checks)

All paths below are relative to
`ascii-graph-toolkit/skills/ascii-graph/`. Run pytest from the skill root with
`PYTHONDONTWRITEBYTECODE=1 … -p no:cacheprovider` (per the repo hook). CLIs
already set `sys.dont_write_bytecode = True`.

## Task 1 — `render_arch` core layout (ASCII labels)
- Description: Create `scripts/gen_arch.py` with `render_arch(layers)` where
  `layers` is `[{"name": str, "components": [str, ...]}, ...]`. Render each layer
  as an independent box: top border / centered layer-name line / `├┬┤` separator
  / one component-cell row (`│ c1 │ c2 │ …`) / bottom border. ALL layer boxes
  share ONE outer interior width (= max over layers of the natural component-row
  width and the name width); boxes are stacked directly (no connector). Cell and
  pad widths measured via `width.display_width` (import like `gen_table.py:14`).
- Module: `scripts/gen_arch.py`
- Files touched: scripts/gen_arch.py, tests/test_gen_arch.py
- Context paths:
  - scripts/gen_table.py   (cell/pad/border idiom to mirror)
  - scripts/gen_flow.py    (shared-interior-width idiom to mirror)
  - scripts/width.py        (display_width import path)
- Acceptance:
  - RED: `tests/test_gen_arch.py::test_two_layers_share_outer_width` asserts the
    exact multi-line string for a 2-layer ASCII-label input — both layer boxes
    have identical outer width, each box internally consistent.
  - GREEN: test passes; every line of the output has equal display width.
- Dependencies: none
- Independent: false
- Brief item covered: "a vertical stack of independent, equal-outer-width boxes,
  one per layer … `[top border]` / `[centered layer-name line]` / `[separator]` /
  `[one component row of cells]` / `[bottom border]`".

## Task 2 — CJK alignment, slack distribution, degenerate cases
- Description: Extend `render_arch` so (a) CJK component/name labels (中/英/日,
  2 cells) align — output stays rectangular; (b) when a layer's components are
  narrower than the shared outer width, slack is distributed deterministically
  (evenly across cells, remainder to the last cell); (c) single-component and
  single-layer inputs render a clean box. Assert the output is **`align.py`-clean**
  by calling `align.analyze(out)` and requiring zero issues.
- Module: `scripts/gen_arch.py`
- Files touched: scripts/gen_arch.py, tests/test_gen_arch.py
- Context paths:
  - scripts/align.py        (analyze() returns (report, issues); assert issues == [])
  - scripts/checks_kink.py  (nested-box seam expectations the output must satisfy)
- Acceptance:
  - RED: `tests/test_gen_arch.py::test_cjk_layers_align_and_pass_oracle` feeds a
    mixed 中/英/日 multi-layer input and asserts (1) all lines equal display
    width AND (2) `align.analyze(out)[1] == []`. A separate
    `test_single_layer_single_component` asserts the degenerate box.
  - GREEN: both tests pass; CJK layers align and the oracle reports no drift.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "component cells are sized by `display_width` so CJK labels
  align … slack distributed deterministically … output is aligned by construction
  and passes `align.py` (`✓ no drift`, exit 0)"; Open Questions 1 & 2.

## Task 3 — wire `arch` into the `generate.py` dispatch
- Description: Add `"arch"` to `_SHAPES` (`generate.py:26`), add an `arch` branch
  in `render()` (`generate.py:29-48`) calling `render_arch(payload["layers"])`,
  and include `arch` in the usage string. Import `render_arch` alongside the
  other `from gen_* import …` lines.
- Module: `scripts/generate.py`
- Files touched: scripts/generate.py, tests/test_generate_cli.py
- Context paths:
  - scripts/generate.py     (dispatch table + usage to extend)
  - tests/test_generate_cli.py  (existing per-shape CLI test idiom to mirror)
- Acceptance:
  - RED: `tests/test_generate_cli.py::test_arch_shape_routes` pipes a
    `{"layers":[…]}` payload through `main(["arch"])` / `render("arch", payload)`
    and asserts a non-empty aligned diagram + exit 0; an unknown-shape case still
    returns 2.
  - GREEN: test passes; `echo '{"layers":[…]}' | python scripts/generate.py arch`
    prints the aligned diagram and exits 0 (new verb verified runnable under the
    existing pytest suite — no new command-surface entry, `generate.py` is the
    declared CLI).
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "A fifth generator, `arch`, wired into the existing
  `generate.py` dispatch … Surfaces touched: `generate.py` (`_SHAPES` + `render()`
  + usage)".

## Task 4 — SKILL.md routing + docs update
- Description: In `SKILL.md`: (1) add an `arch` row to the routing table
  (`SKILL.md:22-30`) and move "layered architecture" off the hand-drawn
  verify-loop row onto the new generator row; (2) add one worked
  `echo '{"layers":[…]}' | python scripts/generate.py arch` example block in the
  Generators section; (3) update the Bundled-files table to list `gen_arch.py`.
  Keep the honest-ceiling section accurate (layered arch is now generated, not
  hand-drawn).
- Module: SKILL.md
- Files touched: SKILL.md
- Context paths:
  - SKILL.md                (routing table, generator examples, bundled-files)
- Acceptance:
  - RED (doc diagnostic): SKILL.md has no `arch` routing row / no `gen_arch.py`
    in bundled files / layered architecture still routed to verify-loop — grep
    for `generate.py arch` returns nothing.
  - GREEN: the worked `arch` example in SKILL.md, run verbatim, reproduces the
    documented output (doc-mirrors-code verified against the shipped generator);
    bundled-files table lists `gen_arch.py`; routing table has the `arch` row.
- Dependencies: Task 3 completes first   # doc documents the working CLI command
- Independent: false
- Brief item covered: "What Becomes Obsolete … move layered architecture from the
  verify-loop row to a `generate.py arch` row in the same PR, and trim the
  honest-ceiling/Bundled-files sections to list the new generator".

## Notes

- Parallelism: T2 and T3 both depend only on T1, touch disjoint files
  (gen_arch.py/test_gen_arch.py vs generate.py/test_generate_cli.py), and have no
  shared symbol (T3 imports `render_arch` from T1, not from T2's additions) — both
  marked `Independent: true`, dispatchable in one message. T1 and T4 are the
  sequential spine.
- The `align.py`-clean guarantee is asserted inside `test_gen_arch.py` (Task 2)
  rather than adding an `arch` case to the shared `test_e2e.py`; an e2e case is
  additive and can follow later without blocking this plan.
- No new external surface: `gen_arch.py` uses only `width.display_width`
  (internal SSOT, wraps the already-vendored `wcwidth`). Default light
  box-drawing glyphs only → no `glyphs.py` import needed.
