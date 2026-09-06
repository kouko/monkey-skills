# A/B run A2 — original plan (4,633 words), task T7, cold implementer (sonnet), read-only, git history off-limits

Scratch clone of the sample repo at c1d8cc7. Verbatim status report follows.

---

No hits — `verify-docs.sh` doesn't grep params.md's wood-colour text, so the edit shouldn't interact with it. That's confirmed safe to leave untouched.

I now have everything needed to report.

status: DONE_WITH_CONCERNS

RED found (verbatim, as I would write it in a status report):

> `grep -n '核桃木' docs/loom/params.md` returns exactly three hits, one per row (the file is a one-row-per-line table, so each hit's "enclosing row" is that single line):
> - `docs/loom/params.md:75` — `| \`build_mesh.py --wood-hex\`（Blender 端指令列） | \`str\`／\`#6B4A2F\`（design-log 核桃木） | ...`
> - `docs/loom/params.md:89` — `| \`build_scene(wood_hex)\` | \`str \| None\`／\`None\`（keyword-only） | ...讓 \`materials\` 用自己的預設（design-log 核桃木）...`
> - `docs/loom/params.md:99` — `| \`kumiko-measure --lstar\`（指令列旗標） | \`float\`／可重複；缺省掃核桃木 L* 加 60/65/70/75/80 | ...`
>
> None of the three rows carries any dated correction naming this arc (no `2026-08-2x 更正` marker anywhere in the row, unlike several sibling rows in the same file — e.g. the DECLARED_SIZES row's 2026-08-06 correction and the `setup_scene(diameter)` row's 2026-08-19 correction — which already follow that pattern).
>
> Source values confirmed by reading the code directly:
> - `blender/materials.py:29` — `_WOOD_SRGB_HEX = "#D9B382"` (the actual materials default `apply_placeholder_wood(..., wood_hex=_WOOD_SRGB_HEX)` at line 101), and `blender/build_mesh.py`'s `--wood-hex` argparse flag itself defaults to `None` (line ~872-874: `default=None`), passing through to that materials default when unset.
> - `src/kumiko/output/measurement.py:68` — `_WOOD_HEX = "#D9B382"`, and `_DEFAULT_LSTARS` (line 71-73) starts with `lstar_of(_WOOD_HEX)` — i.e. the sweep's first value is derived from the *current* (hinoki) wood colour, not walnut.
> - `docs/loom/design-log.md:54` and multiple `docs/loom/measurements/2026-08-2*.md` files confirm `#D9B382` = 檜木 (hinoki), and `#6B4A2F` = the old 核桃木 (walnut) value superseded by this arc's Task 2 (already shipped in this tree — commits `d57d2a6`…`c1d8cc7`, including `a312e7c feat(colour): 木材換檜木 #D9B382…`).

GREEN criteria as understood: all three rows are corrected so they name hinoki (檜木) and `#D9B382` instead of walnut (核桃木)/`#6B4A2F`, each value checked against the two source files above (report must quote both source constants verbatim); `bash scripts/verify-docs.sh`'s four design-log-related checks still PASS (script itself untouched — confirmed it does not grep params.md at all, so this edit can't break it); `scripts/verify-docs.sh` file itself is not modified.

open_questions (2):

1. **Silent fix vs. in-place dated annotation.** The task's own Acceptance text only asks that the three hits "name hinoki and `#D9B382`" — read alone that could mean a plain find-and-replace. But `docs/loom/specs/2026-08-20-light-wood-and-darker-inside-paper.md` BI-5 (the brief item this task is explicitly tagged to) says verbatim: *"every prose statement that asserts hinoki was rejected, or that names the wood as walnut, carries an in-place dated correction naming this arc."* That is a preserve-original-plus-annotate contract, not a silent overwrite — and it matches the convention already used elsewhere in this very file (2026-08-06 and 2026-08-19 corrections) and in `design-log.md` (2026-08-21 corrections, "註記不刪除" convention). I'd follow BI-5 and add dated corrections rather than quietly rewriting the cells, but the task text alone doesn't force that reading, so I'd confirm before writing.
2. **Which date to stamp.** Sibling Task 8 is told explicitly to use "2026-08-20"; Task 7 gives no date. The tree's own measurement evidence for this specific colour pair is dated 2026-08-22 (`docs/loom/measurements/2026-08-20-shipped-pair-verification.md`'s header says "量測日：2026-08-22"), which is also the date of the most recent commit in this tree. I'd default to 2026-08-22 unless told otherwise, since it's the date the shipped pair was actually verified, but this isn't stated anywhere in T7's own text.

NEEDS_CONTEXT count: 2
