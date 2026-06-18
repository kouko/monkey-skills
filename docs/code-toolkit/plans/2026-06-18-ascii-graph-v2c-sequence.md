# Plan: ascii-graph v2-C — sequence-diagram generator (`seq`)

Source brief: docs/code-toolkit/specs/2026-06-18-ascii-graph-v2c-sequence.md
Total tasks: 6
Critical-path depth: 4 (≤5)   ← T1→T2→T3→T5; T4 parallels T2, T6 parallels T5
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-18, 14/14 checks)

Paths relative to `ascii-graph-toolkit/skills/ascii-graph/` unless noted. Run
pytest from the WORKTREE root with `PYTHONDONTWRITEBYTECODE=1 … -p no:cacheprovider`.
Correctness contract for `seq`: aligned-by-construction + structural tests, NOT
`align.py` (horizontal-arrow / lifeline-crossing topology is outside align.py's
vertical-seam model — see brief §Decision).

## Task 1 — `render_seq` column layout: participant boxes + lifelines
- Description: Create `scripts/gen_seq.py` with `render_seq(participants, messages)`.
  In THIS task implement the participants-only skeleton: each participant rendered
  as a box across the top (`┌──┐ / │ name │ / └─┬┘` with the lifeline stub `┬`
  centered under each box), then vertical lifelines (`│`) dropping at each
  participant's fixed center display-column for a few rows. `messages` may be
  accepted but not yet rendered (T2). Column positions + spacing computed via
  `width.display_width` so CJK participant names align. Mirror the
  `gen_arch.py`/`gen_flow.py` import idiom.
- Module: `scripts/gen_seq.py`
- Files touched: scripts/gen_seq.py, tests/test_gen_seq.py
- Context paths:
  - scripts/gen_flow.py    (box + centered-trunk idiom)
  - scripts/gen_arch.py    (per-box width math, sys.path import idiom)
  - scripts/width.py        (display_width)
- Acceptance:
  - RED: `tests/test_gen_seq.py::test_participants_render_boxes_and_lifelines`
    feeds 3 participants (incl. a CJK name), asserts (1) each participant box
    appears, (2) every output line has equal display_width, (3) each lifeline `│`
    sits at its participant's fixed center column on the lifeline rows.
  - GREEN: test passes; the participant header + lifelines are column-aligned.
- Dependencies: none
- Independent: false
- Brief item covered: "each participant in a box across the top, a vertical
  lifeline (│) dropping from each box's center column … each participant column
  sits at a fixed display-column".

## Task 2 — message rows: label + directional arrow + crossing; reject self-message
- Description: Extend `render_seq` to render each message as TWO rows — a centered
  label row and an arrow row spanning from the source lifeline column to the target
  lifeline column, `────►` (left→right) or `◄────` (right→left), arrowhead landing
  exactly on the target lifeline column. Arrows spanning non-adjacent participants
  pass THROUGH intermediate lifeline columns on the arrow row. Reject `from == to`
  (self-message, deferred) with a clear `ValueError`.
- Module: `scripts/gen_seq.py`
- Files touched: scripts/gen_seq.py, tests/test_gen_seq.py
- Context paths:
  - scripts/gen_seq.py   (the T1 skeleton to extend)
  - scripts/glyphs.py    (ARROWS set — source the ► ◄ glyphs, don't hardcode)
- Acceptance:
  - RED: `tests/test_gen_seq.py::test_message_arrow_direction_and_landing` asserts a
    left→right message renders `────►` with the head on the target column and the
    centered label above; a right→left message renders `◄────`; a message across a
    non-adjacent pair crosses the middle lifeline on the arrow row. A separate
    `test_self_message_rejected` asserts `from == to` raises `ValueError`.
  - GREEN: both pass; arrows start/end on the correct lifeline columns, every line
    equal display width.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "each message renders as two rows — a centered label row and
  an arrow row (────► / ◄────) … arrowhead on the target side … pass through the
  intermediate lifeline columns"; Open Question 3 (reject self-message).

## Task 3 — width-correctness: column-widening for wide labels + CJK message labels
- Description: Extend `render_seq` so a message label WIDER than the default gap
  between its two lifelines widens that column gap deterministically (gap =
  max(default spacing, widest label needing that gap)); and CJK (2-cell) message
  labels keep the diagram rectangular. All measured via `width.display_width`.
- Module: `scripts/gen_seq.py`
- Files touched: scripts/gen_seq.py, tests/test_gen_seq.py
- Context paths:
  - scripts/gen_seq.py   (the T2 renderer to extend)
  - scripts/width.py
- Acceptance:
  - RED: `tests/test_gen_seq.py::test_long_cjk_label_widens_gap` feeds a message
    whose CJK label is wider than the default lifeline gap and asserts (1) the label
    fits within its arrow span, (2) every line has equal display_width, (3)
    lifelines remain at consistent columns across all rows.
  - GREEN: test passes; wide/CJK labels never overflow or break column alignment.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "column spacing = max(participant box widths, and the widest
  message label that must fit in each gap) … so CJK … message labels stay aligned";
  Open Question 2.

## Task 4 — wire `seq` into the generate.py dispatch
- Description: Add `"seq"` to `_SHAPES`, `from gen_seq import render_seq`, a `seq`
  branch in `render()` calling `render_seq(payload["participants"],
  payload["messages"])`, and `seq` in the usage string. Preserve unknown-shape
  behaviour.
- Module: `scripts/generate.py`
- Files touched: scripts/generate.py, tests/test_generate_cli.py
- Context paths:
  - scripts/generate.py        (dispatch table + usage)
  - tests/test_generate_cli.py (per-shape CLI test idiom)
  - scripts/gen_seq.py         (confirm render_seq signature)
- Acceptance:
  - RED: `tests/test_generate_cli.py::test_seq_shape_routes` routes a small
    `{"participants":[...],"messages":[...]}` payload through `render("seq",payload)`
    / `main(["seq"])`, asserts a non-empty aligned diagram + exit 0; unknown shape
    still returns 2.
  - GREEN: test passes; `echo '{…}' | python scripts/generate.py seq` prints the
    diagram, exit 0 (extends the existing generate.py CLI — no new command-surface
    verb).
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "A sixth generator, `seq`, wired into `generate.py` (`_SHAPES`
  + `render()` + import)".

## Task 5 — SKILL.md routing + worked example + honest-ceiling
- Description: In `SKILL.md`: add a routing-table row for `seq`; add a worked
  `echo '{…}' | python scripts/generate.py seq` example with VERBATIM generator
  output (mixed 中/英/日, generated by running the command); add `scripts/gen_seq.py`
  to bundled-files; update honest-ceiling to list sequence diagrams as a generator
  shape AND note seq's construction-based (not align.py) guarantee. Surgical edits only.
- Module: SKILL.md
- Files touched: SKILL.md
- Context paths:
  - SKILL.md
  - scripts/generate.py   (confirm the exact seq invocation/payload)
- Acceptance:
  - RED (doc diagnostic): `grep -n "generate.py seq" SKILL.md` returns nothing and
    no `gen_seq.py` row exists in bundled-files.
  - GREEN: the worked `seq` example, run verbatim, reproduces the pasted output
    exactly (doc-mirrors-code); routing-table + bundled-files + honest-ceiling all
    updated; grep now matches.
- Dependencies: Tasks 3, 4 complete first   # needs full generator output + working CLI
- Independent: false
- Brief item covered: "What Becomes Obsolete … sequence diagrams move to the
  `generate.py seq` row … update honest-ceiling so sequence is listed as a
  generator shape".

## Task 6 — manifest: advertise `seq` + version bump (synced pair)
- Description: Add `seq` to the generator list in BOTH
  `ascii-graph-toolkit/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
  descriptions (kept byte-identical), and bump plugin.json version 0.2.0 → 0.3.0.
- Module: manifest (plugin.json + marketplace.json synced pair)
- Files touched: ascii-graph-toolkit/.claude-plugin/plugin.json, .claude-plugin/marketplace.json
- Context paths:
  - ascii-graph-toolkit/.claude-plugin/plugin.json
  - .claude-plugin/marketplace.json
- Acceptance:
  - RED (diagnostic): both descriptions read "table/flow/tree/bar/arch" without
    `seq`; plugin.json version is 0.2.0.
  - GREEN: both descriptions advertise `seq` and are byte-identical (verified by a
    JSON load + equality check); plugin.json version is 0.3.0.
- Dependencies: Task 4 completes first   # seq shape must exist before advertising it
- Independent: true
- Brief item covered: "Surfaces touched: … the manifest description/version."

## Notes

- Parallelism: T4 (dispatch) depends only on T1 and touches files disjoint from the
  gen_seq spine (T2/T3) → `Independent: true`, dispatchable alongside T2. T6 (manifest)
  depends only on T4 and is disjoint from T5 (docs) → `Independent: true`, parallel
  with T5. The sequential spine is T1→T2→T3, with T5 the join point (needs T3+T4).
- `seq` correctness is asserted by gen_seq's own structural tests (equal line widths,
  fixed lifeline columns, arrowhead-on-target). It is deliberately NOT fed to
  `align.py` (different topology — brief §Decision); no align.py assertion in this plan.
- External surfaces: none new — `gen_seq.py` uses `width.display_width` + `glyphs.ARROWS`,
  both internal SSOT (wcwidth reached only via width.py).
