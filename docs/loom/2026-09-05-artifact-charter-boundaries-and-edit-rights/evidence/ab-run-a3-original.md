# A/B run A3 — original plan (4,633 words), task T7, cold implementer (sonnet), read-only, git history off-limits

Scratch clone of the sample repo at c1d8cc7. Verbatim status report follows.

---

Confirmed: verify-docs.sh's design-log-related checks are line 4 (hard-coded plugin path making exit-0 impossible on this machine, per plan Notes), and separate checks for DP4 classification and drift between design-log and code constants — none of them are string-matching on 核桃木/檜木/hex text, so this task's edit shouldn't affect those checks either way; I could not run them anyway without the plugin path.

I now have everything needed to report.

status: DONE

RED found: `grep -n 核桃木 docs/loom/params.md` returns exactly three hits, matching the plan's claim, with no dated correction naming this arc in any of the three rows:
- `docs/loom/params.md:75` — `| \`build_mesh.py --wood-hex\`（Blender 端指令列） | \`str\`／\`#6B4A2F\`（design-log 核桃木） | ...` (single-line table row; enclosing block = line 75–75)
- `docs/loom/params.md:89` — `| \`build_scene(wood_hex)\` | \`str \| None\`／\`None\`（keyword-only） | ...讓 \`materials\` 用自己的預設（design-log 核桃木）...` (enclosing block = line 89–89)
- `docs/loom/params.md:99` — `| \`kumiko-measure --lstar\`（指令列旗標） | \`float\`／可重複；缺省掃核桃木 L* 加 60/65/70/75/80 | ...` (enclosing block = line 99–99)

(Note: `docs/loom/params.md` is a one-line-per-table-row file, 147 lines total, so each "enclosing block" is exactly that one line — no multi-line row wrapping.)

GREEN criteria as understood: All three rows are edited so they name hinoki (檜木) instead of 核桃木, and the color value matches `#D9B382` — verified against the actual source values:
- `blender/build_mesh.py:872-876` — `--wood-hex` argparse default is literally `default=None`; its help text still says "（design-log 的核桃木）" (this occurrence is out of T7's Files-touched scope — the plan's Notes explicitly assign it to T10, alongside `:129`).
- `src/kumiko/output/measurement.py:65-68` — module constant `_WOOD_HEX = "#D9B382"`, with a comment already stating "樹種中立...出貨樹種會換（2026-08-21 核桃木 → 檜木）", confirming hinoki/`#D9B382` is the current shipped value.
- Corroborating cross-check (not a T7 context path but resolves the value question): `blender/materials.py:29` — `_WOOD_SRGB_HEX = "#D9B382"`; `docs/loom/design-log.md:54` — the 木色選擇 row records `出貨色 ~#D9B382` and explicitly names the historical reference values "核桃木 ~#6B4A2F 安全；檜木 ~#D9B382 有洗白風險", which confirms `#6B4A2F` currently sitting in params.md:75 is the *old* walnut hex, stale on two axes (species name and hex), and `#D9B382` is the correct target.

So the concrete edits: line 75's `#6B4A2F（design-log 核桃木）` → `#D9B382（design-log 檜木）`; line 89's `（design-log 核桃木）` → `（design-log 檜木）`; line 99's `核桃木 L*` → `檜木 L*`. `bash scripts/verify-docs.sh`'s design-log-related checks (DP4 classification count, and the design-log-vs-code drift check on 丸輪厚度/DP5 間隙) don't string-match on 核桃木/檜木, so this edit shouldn't affect their pass/fail; the script's own exit code will still be non-zero on this machine only because of the hard-coded `/Users/kouko/.claude/plugins/cache/.../0.12.0/scripts` path at line 4, which is out of scope to fix.

open_questions:
1. Row 99 currently mentions the species name only ("核桃木 L*"), with no hex literal in that sentence — while row 75 carries an explicit hex column. The plan's Description says the correction should make "they name hinoki and #D9B382" collectively; it's ambiguous whether row 99 must also gain an explicit `#D9B382` mention (e.g. "缺省掃檜木（`#D9B382`）L* 加 …") or whether swapping just the species word (核桃木→檜木) satisfies GREEN there, since `#D9B382` is already implicit via `_WOOD_HEX`/`lstar_of(_WOOD_HEX)`. I'd default to the minimal fix (word swap only, no hex insertion) unless told otherwise, since the plan's own worked table for T4/T5/T6-style corrections in the branch's Notes always scoped edits to "the sentence that carries the false claim," not to sentences that never claimed a hex in the first place.

NEEDS_CONTEXT count: 1
