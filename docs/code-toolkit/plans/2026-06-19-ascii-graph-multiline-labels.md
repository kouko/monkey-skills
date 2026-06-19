# Plan: ascii-graph multi-line node labels (換行)

Source brief: docs/code-toolkit/specs/2026-06-19-ascii-graph-multiline-labels.md
Total tasks: 9
Critical-path depth: 3 (≤5)   ← T1 → {T2,T3,T4,T5} → T8
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-19, 14/14 checks)

Paths relative to `ascii-graph-toolkit/skills/ascii-graph/` unless noted. Run pytest
from the WORKTREE root: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest ascii-graph-toolkit/
-q -p no:cacheprovider`. Invariant target: NO generator silently corrupts on `\n` —
flow/tree/table/arch render it; seq/bar reject it loudly. Single-`\n`-free labels stay
byte-identical to today.

## Task 1 — `split_lines` primitive in width.py
- Description: Add `split_lines(label: str) -> list[str]` to `scripts/width.py`,
  returning `label.split("\n")` (always ≥1 element; `"a\n\nb"` → `["a","","b"]`).
  Pure helper, no behavior change to existing functions.
- Module: `scripts/width.py`
- Files touched: scripts/width.py, tests/test_width.py
- Context paths:
  - scripts/width.py   (display_width / char_width idiom)
  - tests/test_width.py
- Acceptance:
  - RED: `tests/test_width.py::test_split_lines` asserts single label → 1-element list;
    `"a\nb"` → `["a","b"]`; `"a\n\nb"` → `["a","","b"]`; `""` → `[""]`.
  - GREEN: test passes; existing width tests still pass.
- Dependencies: none
- Independent: true
- Brief item covered: "Shared helper (in `width.py`): `split_lines(label) -> list[str]`
  = `label.split(\"\\n\")` (≥1 element)".

## Task 2 — flow: multi-line boxes
- Description: In `scripts/gen_flow.py`, render a step whose label contains `\n` as one
  centered body line PER label line. Interior width = max display width over EVERY line
  of EVERY step (via `split_lines` + `display_width`). Box grows taller; the trunk `│`/`▼`
  column and inter-box join are unchanged. A `\n`-free label is the 1-line case (no change).
- Module: `scripts/gen_flow.py`
- Files touched: scripts/gen_flow.py, tests/test_gen_flow.py
- Context paths:
  - scripts/gen_flow.py   (the `_center` + interior-width + body-line logic to extend)
  - scripts/width.py      (split_lines, display_width)
- Acceptance:
  - RED: `tests/test_gen_flow.py::test_multiline_step` feeds a step with a CJK `\n` label
    (e.g. `"驗證使用者\n身份確認"`) and asserts (1) the box has the expected extra body
    line, (2) EVERY output line has equal display_width, (3) a single-line sibling step
    in the same diagram still renders one body line.
  - GREEN: test passes; existing flow tests still pass.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "flow — a step with `\n` renders one body line per label line,
  each centered to the shared interior; box grows taller".

## Task 3 — tree: multi-line node labels
- Description: In `scripts/gen_tree.py`, render a node label containing `\n` so the FIRST
  line carries the `├─ `/`└─ ` connector and each CONTINUATION line carries the sibling
  continuation prefix (`│  ` if the node has a following sibling, else `   `) + the
  prefix, aligning continuation text under the label. Children render after all label lines.
- Module: `scripts/gen_tree.py`
- Files touched: scripts/gen_tree.py, tests/test_gen_tree.py
- Context paths:
  - scripts/gen_tree.py   (the `_TEE`/`_ELBOW`/`_BAR`/`_GAP` + `_render_children` logic)
- Acceptance:
  - RED: `tests/test_gen_tree.py::test_multiline_node` feeds a tree where a NON-last child
    and a LAST child each have a CJK `\n` label, plus a child under the multi-line node;
    asserts continuation lines use `│  ` (non-last) vs `   ` (last) prefixes and align
    under the label, and the child still renders correctly below.
  - GREEN: test passes; existing tree tests still pass.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "tree — a node label with `\n`: first line carries the connector;
  each continuation line carries the sibling continuation prefix … so it aligns under the label".

## Task 4 — table: multi-line cells
- Description: In `scripts/gen_table.py`, a cell containing `\n` makes its row taller:
  row height = max line-count across the row's cells; render the row as that many physical
  lines, each showing every cell's i-th line (blank-padded when a cell has fewer lines —
  top-aligned). Column width = max line display-width in that column (header + all rows).
- Module: `scripts/gen_table.py`
- Files touched: scripts/gen_table.py, tests/test_gen_table.py
- Context paths:
  - scripts/gen_table.py   (`_pad`, `col_widths`, `data_line` to extend)
  - scripts/width.py       (split_lines, display_width)
- Acceptance:
  - RED: `tests/test_gen_table.py::test_multiline_cell` feeds a row with one CJK `\n` cell
    and a single-line neighbor; asserts the row spans the expected number of physical lines,
    the short cell is blank-padded (top-aligned), and EVERY line has equal display_width.
  - GREEN: test passes; existing table tests still pass.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "table — a cell with `\n` makes its row taller: row height = max
  line-count across the row's cells … column width = max line width in that column".

## Task 5 — arch: multi-line component cells + layer name
- Description: In `scripts/gen_arch.py`, the layer-name line and component cells accept `\n`:
  a band grows taller to fit its tallest cell (same row-height + top-align logic as the table),
  and a multi-line layer name renders as multiple centered name lines. Shared outer width
  still spans all bands; output stays rectangular.
- Module: `scripts/gen_arch.py`
- Files touched: scripts/gen_arch.py, tests/test_gen_arch.py
- Context paths:
  - scripts/gen_arch.py    (centered name line + component-cell row + slack logic)
  - scripts/width.py       (split_lines, display_width)
- Acceptance:
  - RED: `tests/test_gen_arch.py::test_multiline_component` feeds a layer with one CJK `\n`
    component (and a `\n` layer name) and asserts the band gains the expected extra rows,
    cells top-align, and EVERY line has equal display_width across all bands.
  - GREEN: test passes; existing arch tests still pass.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "arch — component cells and the layer-name line accept `\n`, same
  row-height logic as table".

## Task 6 — seq: reject `\n` loudly
- Description: In `scripts/gen_seq.py`, raise a clear `ValueError` if any participant name
  OR message label contains `\n` (multi-line seq is deferred — fail loud, never silently
  corrupt). Add the check before rendering.
- Module: `scripts/gen_seq.py`
- Files touched: scripts/gen_seq.py, tests/test_gen_seq.py
- Context paths:
  - scripts/gen_seq.py   (the existing self-message ValueError guard to mirror)
- Acceptance:
  - RED: `tests/test_gen_seq.py::test_newline_in_label_rejected` asserts a participant
    name with `\n` and a message label with `\n` each raise `ValueError`; a normal seq
    still renders.
  - GREEN: test passes; existing seq tests still pass.
- Dependencies: none
- Independent: true
- Brief item covered: "seq and bar raise a clear `ValueError` if any label contains `\n`".

## Task 7 — bar: reject `\n` loudly
- Description: In `scripts/gen_bar.py`, raise a clear `ValueError` if any bar label contains
  `\n` (a bar row is inherently one line). Add the check before rendering.
- Module: `scripts/gen_bar.py`
- Files touched: scripts/gen_bar.py, tests/test_gen_bar.py
- Context paths:
  - scripts/gen_bar.py
- Acceptance:
  - RED: `tests/test_gen_bar.py::test_newline_in_label_rejected` asserts a pair label with
    `\n` raises `ValueError`; a normal bar still renders.
  - GREEN: test passes; existing bar tests still pass.
- Dependencies: none
- Independent: true
- Brief item covered: "seq and bar raise a clear `ValueError` if any label contains `\n`".

## Task 8 — SKILL.md: multi-line note + worked example
- Description: In `SKILL.md`, add a short "Multi-line labels (換行)" note in the Generators
  section: explain a `\n` in a label renders multiple lines in flow/tree/table/arch, and is
  rejected (ValueError) for seq/bar. Add ONE worked example (e.g. a flow step with a CJK `\n`
  label) with VERBATIM generator output (generated by running the command). Surgical edits only.
- Module: SKILL.md
- Files touched: SKILL.md
- Context paths:
  - SKILL.md
  - scripts/generate.py   (confirm payloads)
- Acceptance:
  - RED (doc diagnostic): `grep -n "Multi-line" SKILL.md` returns nothing.
  - GREEN: SKILL.md has the multi-line note + a worked example whose command, run verbatim,
    reproduces the pasted output exactly (doc-mirrors-code); grep matches. Full suite green.
- Dependencies: Tasks 2, 3, 4, 5 complete first   # example needs render working
- Independent: false
- Brief item covered: "SKILL.md gains a short 'multi-line labels' note + one worked example".

## Task 9 — manifest: version bump 0.3.0 → 0.4.0
- Description: Bump `"version"` in `ascii-graph-toolkit/.claude-plugin/plugin.json` from
  `"0.3.0"` to `"0.4.0"` (additive feature = semver minor). The description's generator list
  is UNCHANGED (multi-line is a capability, not a new shape) — do not edit the description,
  so plugin.json/marketplace.json stay in sync without touching marketplace.json.
- Module: `ascii-graph-toolkit/.claude-plugin/plugin.json`
- Files touched: ascii-graph-toolkit/.claude-plugin/plugin.json
- Context paths:
  - ascii-graph-toolkit/.claude-plugin/plugin.json
- Acceptance:
  - RED (diagnostic): plugin.json version reads "0.3.0".
  - GREEN: plugin.json version reads "0.4.0", file remains valid JSON, description unchanged.
- Dependencies: none
- Independent: true
- Brief item covered: "the manifest description/version bumps (0.3.0 → 0.4.0, additive feature)".

## Notes

- Two parallel waves. **Wave 1** (no cross-deps, disjoint files → all `Independent: true`):
  T1 (width.py), T6 (gen_seq.py), T7 (gen_bar.py), T9 (plugin.json). **Wave 2** (all depend
  only on T1, disjoint files → all `Independent: true`): T2 (gen_flow), T3 (gen_tree),
  T4 (gen_table), T5 (gen_arch). **Then** T8 (SKILL.md) after T2–T5. Critical path T1→T2→T8 = 3.
- No new external surface: every task uses only `width.split_lines`/`display_width` (internal
  SSOT, wcwidth via width.py) + stdlib `str.split`. No third-party import.
- align.py is NOT touched — it already validates multi-line boxes (proven this session).
