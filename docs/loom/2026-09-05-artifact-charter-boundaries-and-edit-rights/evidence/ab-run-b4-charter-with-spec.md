# A/B run B4 — charter plan (941 words) plus the engineering spec (395 words), task T7, cold implementer (sonnet), read-only, git history off-limits

Scratch clone of the sample repo at c1d8cc7. Verbatim status report follows.

---

status: DONE_WITH_CONCERNS

RED found (verbatim, as I'd write it in the status report):

> RED: `docs/loom/params.md` carries three 核桃木 references that no longer match the shipped code. (1) Line 75, the `build_mesh.py --wood-hex` row's type/default column reads `` `str`／`#6B4A2F`（design-log 核桃木） `` — this is wrong on two independent axes: the species/hex is stale (shipped wood is 檜木 `#D9B382`, confirmed live in `blender/materials.py:29` `_WOOD_SRGB_HEX = "#D9B382"` and in `docs/loom/measurements/2026-08-20-shipped-pair-verification.md`), and the claim itself misdescribes the mechanism — `build_mesh.py`'s actual argparse default is `None` (confirmed at the `--wood-hex` argument definition, `default=None`), not a hex literal; the real default falls through at runtime to `materials.py`'s `_WOOD_SRGB_HEX`. (2) Line 89, the `build_scene(wood_hex)` row's description prose says "讓 `materials` 用自己的預設（design-log 核桃木）" — the type/default column itself (`str | None`／`None`) is already correct, but the species-name prose is stale. (3) Line 99, the `kumiko-measure --lstar` row's description says "缺省掃核桃木 L* 加 60/65/70/75/80" — stale species name, since `measurement.py:68` `_WOOD_HEX = "#D9B382"` (檜木) drives that default scan today, confirmed via `grep -n "核桃木" docs/loom/params.md` returning exactly lines 75/89/99, matching the plan's cited line numbers.

GREEN criteria as understood (verbatim):

> GREEN: each of the three 核桃木 hits in `params.md` (lines 75, 89, 99) carries a dated (2026-08-22 — the shipped-pair verification date per spec REQ-4/Design decision) correction naming 檜木／`#D9B382`, with the original wording left in place (repo-wide "annotate, never rewrite" convention, explicitly extended to T7 by the spec's REQ-4 and Design decision section — not a blind find-and-replace of "核桃木" with "檜木"). Line 75's type/default column additionally states the real fallthrough per REQ-2: the actual default is `None` (not a hex literal), resolving at runtime to `materials.py`'s `_WOOD_SRGB_HEX` — every value corrected must be checked against the actual code default, not assumed or copied from the assigned/target hex, and cited from T3's measurement note (`docs/loom/measurements/2026-08-20-shipped-pair-verification.md`) rather than recomputed. `bash scripts/verify-docs.sh`'s four design-log-related checks (of its 8 total; the first two — PRINCIPLES.md structure and seed-traceability — are pre-existing and unrelated to this branch, per plan Risk #2) stay PASS; I confirmed this is trivially satisfied since none of the four design-log checks reads `params.md`, `build_mesh.py`, or `measurement.py` (verified by `grep -n "design-log\|params.md\|build_mesh.py\|measurement.py" scripts/verify-docs.sh` and by running the script — baseline today: 2 FAIL (pre-existing, unrelated), 6 PASS, including all 4 design-log checks). No package-suite clause applies (spec's Design decision states this explicitly — `params.md` is pure prose, exercised by no test).

open_questions:
1. Line 75's correction mechanics: REQ-2 says the type/default column "shall state" the real fallthrough (`str | None`／`None`), which sounds like a direct edit to that data cell, while REQ-4 (explicitly naming T7) says corrections must annotate beside the original, never rewrite it. My planned resolution — keep the original `` `str`／`#6B4A2F`（design-log 核桃木） `` cell text verbatim and append a dated 2026-08-22 correction stating the real default/fallthrough and the current species/hex, inside the same cell — matches the file's own established convention elsewhere (e.g. the `setup_scene(diameter)` row's 2026-08-19 in-cell correction, and design-log.md's 木色選擇 row keeping "核桃木 ~#6B4A2F 安全；檜木 ~#D9B382 有洗白風險" verbatim with a superseding annotation). This is resolvable from the docs without asking, but worth a one-line confirmation before writing since it's the one place the plan's terse Test wording ("corrected to name hinoki/#D9B382") could be misread as a literal in-place replacement of the stale value rather than an annotation.
2. Which exactly 4 of `verify-docs.sh`'s 8 `chk` calls are "the four design-log checks" is not spelled out anywhere I found in the T7 task/spec text itself; I inferred it from `docs/loom/plans/2026-08-20-light-wood-and-darker-inside-paper.md:314`'s note that the first two checks (PRINCIPLES.md structure, seed-traceability) are pre-existing/unrelated failures, leaving the other 6 PASS, of which the 4 that actually read `design-log.md` (path-refs, DP4-links, DP4-three-section, drift) are the ones meant. This is immaterial to T7's own diff (none of the 4 read the 3 files T7 touches) but I'm flagging the inference rather than asserting it as settled fact.

NEEDS_CONTEXT count: 1 (item 1 — a low-stakes wording confirmation on how the line-75 type/default cell correction should be formatted; resolvable by following the file's own precedent, but I would not silently guess given it's the one REQ that could fork the diff's shape).

Files read (absolute paths):
- /private/tmp/claude-501/.../ab-clone-b/PLAN-charter.md (T1–T3, T7 sections)
- /private/tmp/claude-501/.../ab-clone-b/SPEC-engineering.md
- /private/tmp/claude-501/.../ab-clone-b/docs/loom/params.md (lines 60–110, and the exact 核桃木 hits at 75/89/99)
- /private/tmp/claude-501/.../ab-clone-b/blender/materials.py (lines 1–260 region, `_WOOD_SRGB_HEX`/`_PAPER_INSIDE_SRGB_HEX`)
- /private/tmp/claude-501/.../ab-clone-b/src/kumiko/output/measurement.py (`_WOOD_HEX` region)
- /private/tmp/claude-501/.../ab-clone-b/blender/build_mesh.py (lines ~860–885, `--wood-hex` argparse)
- /private/tmp/claude-501/.../ab-clone-b/docs/loom/design-log.md (木色選擇, 窗內底紙色, 組子的實物木材樹種 rows)
- /private/tmp/claude-501/.../ab-clone-b/docs/loom/measurements/2026-08-20-shipped-pair-verification.md (T3's note, cited as the required value source)
- /private/tmp/claude-501/.../ab-clone-b/scripts/verify-docs.sh (full file, plus a live run confirming baseline: 2 FAIL pre-existing/unrelated, 6 PASS)
