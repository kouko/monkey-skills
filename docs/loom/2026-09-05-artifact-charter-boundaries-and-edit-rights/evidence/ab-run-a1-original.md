# A/B run A1 — original plan (4,633 words), task T7, cold implementer (sonnet), read-only

Scratch clone of the sample repo at c1d8cc7; plan file PLAN-original.md ("Task 7"). Verbatim status report follows.

---

status: DONE
RED found: `grep -n '核桃木' docs/loom/params.md` returns exactly 3 hits in the current working tree:
- `:75` — `| \`build_mesh.py --wood-hex\`（Blender 端指令列） | \`str\`／\`#6B4A2F\`（design-log 核桃木） | ...` — enclosing block is this single table row (params.md line 75, one row, no surrounding multi-line block).
- `:89` — `| \`build_scene(wood_hex)\` | \`str \| None\`／\`None\`（keyword-only） | ...讓 \`materials\` 用自己的預設（design-log 核桃木）...` — enclosing row is line 89 only.
- `:99` — `| \`kumiko-measure --lstar\`（指令列旗標） | \`float\`／可重複；缺省掃核桃木 L* 加 60/65/70/75/80 | ...` — enclosing row is line 99 only.
None of the three rows carries a dated correction naming this arc (no "2026-08-2x" annotation referencing the wood-colour change anywhere in these rows).

GREEN criteria as understood: All three rows must name the wood as hinoki (檜木) and the hex `#D9B382`, and — per the task's own instruction to verify against code rather than assume — each claim must match what the code actually does, not just a mechanical find-replace of the species name:
- `blender/build_mesh.py`'s `--wood-hex` argparse flag (around line 869-877) has `default=None` — it is **not** a fixed hex default at all. The doc's current claim of `str`／`#6B4A2F` is wrong on two independent axes: the stale species name (pre-existing bug unrelated to this arc) and the false claim that there is a literal hex default (also pre-existing, unrelated to this arc). The honest default description is `str | None`／`None`, falling through to `blender/materials.py`'s `_WOOD_SRGB_HEX = "#D9B382"` when unset.
- `src/kumiko/output/measurement.py:68` — `_WOOD_HEX = "#D9B382"` — this is the constant the `--lstar` sweep defaults are offset from (line 72: `lstar_of(_WOOD_HEX)`).
- `bash scripts/verify-docs.sh`'s four design-log-related checks must still show PASS (not overall exit 0 — line 4 hard-codes `/Users/kouko/.claude/plugins/cache/...` which won't resolve on this scratch machine, confirmed by reading the script).
- `scripts/verify-docs.sh` itself must not be modified.

open_questions:
1. Line 75's fix is not a simple s/核桃木/檜木/ — the already-shipped fix (commit `b25f634`, not an ancestor of this clone's HEAD, confirming this is genuinely pre-implementation) rewrote it as `str \| None`／`None` with an explanatory annotation distinguishing "stale species name" from "pre-existing wrong-type/default documentation," while lines 89 and 99 got straight corrections with no annotation. Should I follow that same asymmetric treatment (annotate :75, plain-correct :89/:99), or does the task want uniform treatment across all three? The task Description only says "so they name hinoki and `#D9B382`" — it doesn't by itself flag that :75 has this second, unrelated defect; a plain-replace on :75 would leave a false "fixed hex default" claim standing.
2. Whether the annotation on :75 (if following the precedent) should cite this arc/commit by name — the Description says nothing about dated annotations for T7 (unlike T8's explicit "annotate in place with a dated note"), so it's not clear whether a citation is required or optional here.

NEEDS_CONTEXT count: 2

---

Orchestrator note: the clone carried the sample repo's full history, so this run could and did read the real landing commit b25f634 (not an ancestor of the checked-out base). Run B1 had the same clone shape, so the two arms are comparable; a stricter harness would clone with `--depth` or export the tree at the base commit.
