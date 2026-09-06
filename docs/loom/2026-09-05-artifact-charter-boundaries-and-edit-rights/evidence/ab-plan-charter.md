# 淺木色與更深的窗內紙 — plan
intent: 2026-08-20-light-wood-and-darker-inside-paper@n/a
charter: 1.0

## Current State Evidence
- Spec: docs/loom/specs/2026-08-20-light-wood-and-darker-inside-paper.md — target hex pair and three acceptance thresholds.
- Constants: blender/materials.py `_WOOD_SRGB_HEX`, `_PAPER_INSIDE_SRGB_HEX`.
- Thresholds: tests/test_render_blender_smoke.py `_MATERIAL_CONTRAST_MIN`/`_PAPER_CONTRAST_MIN`/`_THUMBNAIL_CONTRAST_MIN` (15/15/24).
- Wood-anchor parser: docs/loom/design-log.md 「木色選擇」 row, read by `_design_log_wood_hex()`.
- Prior sweep: docs/loom/measurements/2026-08-20-paper-darkness-sweep.md.

## Task DAG

**T1 — design-log 的木色錨點與樹種名脫鉤**  after: none
- Files: tests/test_render_blender_smoke.py, docs/loom/design-log.md
- Test: new test asserting `_design_log_wood_hex()` resolves the shipped hex from a species-neutral `出貨色 ~#RRGGBB` marker fails today (regex requires 核桃木); GREEN repoints the helper, preserves both species names/verdicts, package suite green.
- Risk: agent-decided — shipped colour unchanged this task; anchor only.

**T2 — 出貨色對上線（木色＋窗內紙一起）**  after: T1, T11
- Files: blender/materials.py, src/kumiko/output/measurement.py, docs/loom/design-log.md
- Test: ship `_WOOD_SRGB_HEX=#D9B382` and `_PAPER_INSIDE_SRGB_HEX=#585148` together; update design-log 木色選擇/窗內底紙色 rows; round-trip and inside-paper-contrast tests pass, thresholds unchanged.
- Risk: agent-decided — two constants are one configuration (docs/loom/measurements/2026-08-20-paper-darkness-sweep.md: wood alone leaves 16px gap 15.46 < 24); row prose verdicts untouched (T4's subject).

**T3 — 用出貨組態重渲，記錄三條驗收線的實測值**  after: T2
- Files: docs/loom/measurements/2026-08-20-shipped-pair-verification.md
- Test: note records five measured values (wood L*, paper L*, three acceptance gaps) plus the render command; three thresholds confirmed unchanged at 15/15/24 by reading tests/test_render_blender_smoke.py; all three tests pass.
- Risk: agent-decided — T4/T5/T6/T7 must cite this note's values, never the pre-ship sweep or a recompute.

**T4 — design-log 三處記載就地更正**  after: T3
- Files: docs/loom/design-log.md
- Test: three claims (洗白風險 rejection, 40%-darker rule, `#8B6345` figure) each stay verbatim with a dated correction inside the same table cell citing T3's note; claim (a) also cites the 「組子的實物木材樹種」 row; verify-docs.sh's four design-log checks PASS; package suite green.
- Risk: agent-decided — annotate-don't-delete convention; read the whole cell before judging RED, not a grep miss.

**T5 — materials.py 的散文更正**  after: T3
- Files: blender/materials.py
- Test: every 核桃木/`#8B6345` hit in a docstring or comment carries a dated correction or the measured replacement figure; `git diff` shows no executable-line change; package suite green.
- Risk: agent-decided — read each full enclosing block before judging, not only the matched line.

**T6 — smoke test 裡的散文更正**  after: T3
- Files: tests/test_render_blender_smoke.py
- Test: every 核桃木/`#8B6345`/`#FFFFFF` hit, including the three named custom-wood-hex tests, carries a dated correction or replacement figure; no test input, assertion or threshold changes; package suite green.
- Risk: agent-decided — cited line numbers drift once earlier tasks land; re-anchor by content, not the coordinate list.

**T7 — params.md 的木色預設值更正**  after: T2
- Files: docs/loom/params.md, blender/build_mesh.py, src/kumiko/output/measurement.py
- Test: three 核桃木 hits in params.md corrected to name hinoki/`#D9B382`, each verified against the code's actual default, not assumed; verify-docs.sh's four design-log checks PASS.
- Risk: agent-decided — read the code's real default before writing the doc; do not copy the assigned hex blindly.

**T8 — decisions.md 的當日觀察加註**  after: T2
- Files: docs/loom/decisions.md
- Test: the 2026-08-10 entry's 核桃木色 phrase stays verbatim, annotated in place with a dated note that the colour has since changed; original sentence not rewritten.
- Risk: agent-decided — entry records a historical observation; annotate beside it, never rewrite to today's colour.

**T9 — backlog 條目結案**  after: T3
- Files: docs/loom/backlog/light-wood-colour.md, docs/loom/BACKLOG.md, docs/loom/DIRECTION.md
- Test: status flips COMMITTED-NEXT to SHIPPED; body names which of the three proposed paths was taken, citing this branch and the measurement notes; `backlog_index.py --validate` exits 0; regenerated indexes staged.
- Risk: agent-decided — original table and closing paragraph preserved, annotated not rewritten.

**T10 — 以「主張」為單位的收網掃描**  after: T4, T5, T6, T7, T8, T9
- Files: docs/loom/measurements/2026-08-20-claim-sweep-receipt.md, README.md, blender/build_mesh.py
- Test: receipt exists and accounts for all seven claims (see docs/loom/specs/2026-08-20-light-wood-and-darker-inside-paper.md), each with a correction or a stated reason it needs none; scope statement names full-read vs matched-line-only files; verify-docs.sh's four checks PASS; package suite green.
- Risk: agent-decided — search by meaning, not only literal string; a prior arc's sweep-by-file left defects between file boundaries (docs/loom/memory/slicing-a-sweep-by-file-leaves-the-defects-between-the-slices.md).

**T11 — 像素量測脫離木色綁定**  after: none
- Files: tests/test_render_blender_smoke.py
- Test: re-anchor `_SIDE_WALL_WOOD_BR_MAX` at 0.6685 (docs/loom/measurements/2026-08-22-cross-species-wood-discriminator.md) and re-sample the centre-pixel test on the inside annulus via `_region_pixels`; three named tests pass under hinoki and walnut; rewritten centre-pixel test fails on an occlusion-simulating render; thresholds unchanged; package suite green.
- Risk: agent-decided — (a)'s classifier is (b)'s filter, they ship as one change; splitting exceeds this plan's critical-path depth cap of 5.

**T12 — 重新武裝被本 arc 解除武裝的木格層回歸測試**  after: T6
- Files: tests/test_render_blender_smoke.py
- Test: `test_the_paper_renders_in_the_wood_layer_and_not_the_background` currently passes on a wood-only render (docs/loom/measurements/2026-08-20-shipped-pair-verification.md); add a blue/red-ratio assertion via `_hex_channels` (not `_blue_over_red` — signature mismatch) that fails on that render and passes on real hinoki and walnut renders; thresholds unchanged; package suite green.
- Risk: agent-decided — do not reuse `_blue_over_red`; its `red==0→1.0` convention has no meaning for a layer's dominant colour.

## Questions asked
① — what — N/A: two target hexes and the 40%-rule disposition were user-decided in the brief before this plan (docs/loom/specs/2026-08-20-light-wood-and-darker-inside-paper.md, Decision section); the three thresholds' pass/fail were already measured in docs/loom/measurements/2026-08-20-paper-darkness-sweep.md.

## Risks
1. user-decided — the three threshold constants (15/15/24) are the user's acceptance lines; no task may lower them — a task needing to is BLOCKED, not self-relaxed.
2. user-decided — verify-docs.sh's first two checks fail for a pre-existing, unrelated reason (hard-coded plugin path); every task's GREEN asserts only its four design-log checks PASS, never a full exit 0.
3. agent-decided — T4/T5/T7 must cite T3's measurement note for every rendered value; recomputing or reusing the pre-ship sweep is disallowed.
4. agent-decided — T11's re-anchored threshold (0.6685) carries its own re-sweep trigger in its docstring, not restated here.
5. agent-decided — T11 and T12 cover facts discovered during implementation, not named in the original brief; evidence lives in the cited measurement notes.
6. user-decided — the 40%-darker/L*≤60 rule is demoted, never deleted; a task treating it as still binding is BLOCKED, not decided unilaterally.
