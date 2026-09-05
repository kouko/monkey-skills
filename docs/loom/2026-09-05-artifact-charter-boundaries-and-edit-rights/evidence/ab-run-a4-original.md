# A/B run A4 — original plan (4,633 words), task T7, cold implementer (sonnet), read-only, git history off-limits

Scratch clone of the sample repo at c1d8cc7. Verbatim status report follows.

---

Confirmed — the hard-coded path `/Users/kouko/.claude/plugins/cache/...` matches the plan's note that this script can't exit 0 on this machine (this scratch clone). Now delivering the report.

status: DONE

**RED found** (verbatim, as I'd write it in the status report):

> Grep `核桃木` in `docs/loom/params.md` finds exactly three hits, all in single-line table rows with no dated correction naming this arc:
> - `:75` — `build_mesh.py --wood-hex`（Blender 端指令列）row, enclosing block = line 75 only (the table row is one physical line): `str`／`#6B4A2F`（design-log 核桃木）
> - `:89` — `build_scene(wood_hex)` row, enclosing block = line 89 only: `str | None`／`None`（keyword-only），描述文字含「design-log 核桃木」
> - `:99` — `kumiko-measure --lstar`（指令列旗標）row, enclosing block = line 99 only: `float`／可重複；缺省掃核桃木 L* 加 60/65/70/75/80
>
> None of the three rows carries a dated annotation citing this arc; the doc still names 核桃木 (walnut) as the shipped default in prose, even though the actual code default is hinoki `#D9B382`.

**GREEN criteria as understood** (verbatim):

> All three hits are rewritten to name hinoki (檜木) and `#D9B382`, each verified against the value actually read from source, not assumed:
> - `blender/build_mesh.py`: the `--wood-hex` CLI flag itself defaults to `None` (line ~872, `default=None`) — it does NOT carry the hex literal. The resolved default hex comes from `blender/materials.py:29` — `_WOOD_SRGB_HEX = "#D9B382"` — which `apply_placeholder_wood(objects, *, wood_hex=_WOOD_SRGB_HEX)` (materials.py:101) falls back to when `build_mesh.py` passes nothing. So the doc's line 75 row (which documents `--wood-hex`'s effective/described default `#6B4A2F` "design-log 核桃木") needs updating to `#D9B382` "design-log 檜木" or equivalent, and should trace to `materials.py`'s `_WOOD_SRGB_HEX`, not to a hex literal that lives in `build_mesh.py` itself (it doesn't — build_mesh.py's own default is `None`).
> - `src/kumiko/output/measurement.py:68`: `_WOOD_HEX = "#D9B382"` — this is already hinoki's hex. The `:89` and `:99` rows in params.md describe `wood_hex=None` and `--lstar`'s default sweep as falling back to "design-log 核桃木" prose — these need the word 核桃木 replaced with 檜木; the numeric value `#D9B382` is already correct in code (measurement.py's constant already carries the comment "**樹種中立**：出貨樹種會換（2026-08-21 核桃木 → 檜木）" — confirming the migration already happened at the code layer; only the prose in params.md is stale).
> - `bash scripts/verify-docs.sh` shows its four design-log-related checks (PRINCIPLES.md 結構符合授權契約 is not one of the four — the four are: re-trigger 格式、DP4 三段分類齊備、design-log 落地比例一致、其餘 chk 呼叫) PASS — not that it exits 0. Confirmed: line 4 hard-codes `P=/Users/kouko/.claude/plugins/cache/monkey-skills/loom-product-principles/0.12.0/scripts`, an absolute path that will not resolve identically on every machine, so a nonzero exit from the first two `python3 $P/...` calls is expected/tolerated per the plan's own note. Must NOT edit `scripts/verify-docs.sh`.

**Source values quoted, as required by GREEN:**
- `blender/materials.py:29` → `_WOOD_SRGB_HEX = "#D9B382"` (comment still literally says "核桃木" — that comment itself is stale, same bug class, but T7's Files touched is only `docs/loom/params.md`, so this is out of scope for T7 itself — flagging as a same-class residual, not something to fix here).
- `src/kumiko/output/measurement.py:68` → `_WOOD_HEX = "#D9B382"`, with an explicit "樹種中立" comment noting the 2026-08-21 walnut→hinoki migration.

**open_questions:**
1. `blender/build_mesh.py`'s own `--wood-hex` flag default is `None`, not a hex literal — the plan's Files/Context list names `build_mesh.py`'s "flag default" as one of the two things to verify, but the actual resolved value lives in `blender/materials.py` (not directly named in T7's context paths). Should the doc's citation for line 75 point to `materials.py`'s `_WOOD_SRGB_HEX`, or should I treat `build_mesh.py`'s help text (line 875, which also says "design-log 的核桃木") as the thing being verified? Both `build_mesh.py:875` and `materials.py:104` carry the same stale "核桃木" phrase in prose/help text, outside `docs/loom/params.md`, but T7's Files touched is only `docs/loom/params.md` — confirming those code-comment fixes are correctly out of scope per the task's stated file boundary, not an oversight.
2. What exact date should the correction cite, and does GREEN require a literal "dated correction" annotation added alongside each fix (as is the pattern used in Task 8's `decisions.md` entry), or is directly rewriting 核桃木→檜木 in place sufficient? The plan's RED line says rows currently have "no dated correction naming this arc" — implying GREEN may want a dated annotation format similar to other tasks in this plan (e.g., "**2026-08-20 更正**：..."), rather than a silent in-place rewrite. The Task 7 Description says "make the doc match the code" (silent correction) while other sibling tasks in this plan (per the Notes section) consistently use dated in-place annotations rather than silent rewrites — this is a real ambiguity about which convention applies to T7 specifically.
3. What is "this arc"'s name/citation string to use in a dated annotation, if one is required? Candidate: `docs/loom/specs/2026-08-20-light-wood-and-darker-inside-paper.md` (matches Task 8's Context paths for the same wood-color change), but T7 itself doesn't list this spec file in its own Context paths, so I cannot be fully certain this is the correct arc to cite without user/plan confirmation.

**NEEDS_CONTEXT count: 3**
