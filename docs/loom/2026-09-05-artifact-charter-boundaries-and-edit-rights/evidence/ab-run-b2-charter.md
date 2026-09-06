# A/B run B2 — charter plan (941 words), task T7, cold implementer (sonnet), read-only, git history off-limits

Scratch clone of the sample repo at c1d8cc7. Verbatim status report follows.

---

## Status: DONE_WITH_CONCERNS

I read T7's own block (plan lines 44-47) and, since its `after:` line points only to T2, I additionally read T2 (line 19-22) as instructed. I then read the three named files plus `blender/materials.py` (the code that actually owns the constant) and `scripts/verify-docs.sh` (to check the GREEN's cited mechanical gate), read-only, no edits.

### Files read
- `docs/loom/params.md` (three hit rows: lines 75, 89, 99)
- `blender/build_mesh.py` (argparse `--wood-hex`, lines 869-876; call site lines 166-172)
- `src/kumiko/output/measurement.py` (`_WOOD_HEX` const line 68, `_DEFAULT_LSTARS` lines 71-77, `main()` line 392)
- `blender/materials.py` (`_WOOD_SRGB_HEX` line 29 — the actual SSOT-copy constant, not in T7's Files list but needed to verify "the code's actual default")
- `docs/loom/design-log.md` (「木色選擇」row, line 54, confirms 出貨色 = `~#D9B382`／檜木; 核桃木 ~`#6B4A2F` is the retired nominal walnut hex)
- `scripts/verify-docs.sh` (full file, to check the "four design-log checks" claim)

### RED found (verbatim, as I'd write it in a status report)

> `docs/loom/params.md` still names 核桃木 as the wood default in three places, but the code's actual current default is already hinoki `#D9B382` — the doc has drifted behind a ship already landed by T2:
> - line 75, `build_mesh.py --wood-hex` row: `` `str`／`#6B4A2F`（design-log 核桃木） ``
> - line 89, `build_scene(wood_hex)` row: "...讓 `materials` 用自己的預設（design-log 核桃木）..."
> - line 99, `kumiko-measure --lstar` row: "缺省掃核桃木 L* 加 60/65/70/75/80"
>
> Ground truth checked in code: `blender/materials.py:29` `_WOOD_SRGB_HEX = "#D9B382"`, and `src/kumiko/output/measurement.py:68` `_WOOD_HEX = "#D9B382"` (whose own comment at lines 65-67 already documents "2026-08-21 核桃木 → 檜木"); `_DEFAULT_LSTARS` (measurement.py:71-77) is built from `lstar_of(_WOOD_HEX)` i.e. hinoki's L*, not walnut's. `design-log.md`'s 「木色選擇」row (line 54) confirms `#6B4A2F` was the retired nominal 核桃木 hex and `~#D9B382` is now the 出貨色/檜木 anchor. So all three doc cells cite a species/hex the shipped code no longer uses — this is a documentation-only drift, not a currently-failing automated test (nothing in the repo pins these three prose cells).

### GREEN criteria as understood

- All three cells in `params.md` are corrected to name hinoki (檜木) and `#D9B382`, each value independently checked against the current code default (not copy-pasted from one instance to the other three, and not assumed equal to the hex already fixed by T5/T6 elsewhere) — I verified this: `build_mesh.py`'s own default is `None` (delegates), and the value it delegates to (`materials.py:_WOOD_SRGB_HEX`, `measurement.py:_WOOD_HEX`) is `#D9B382` in both places today.
- `blender/build_mesh.py` and `src/kumiko/output/measurement.py` are read (per T7's Files list) but not necessarily edited — they already carry the correct value/comments; they're the verification source, not new drift targets I found in them.
- `verify-docs.sh`'s "four design-log checks" PASS.

### open_questions

1. **"Four design-log checks" is not a well-defined number I can locate.** `verify-docs.sh` has 8 `chk()` calls total; only 2 of their labels literally contain the string "design-log" (lines 36, 102), and a 3rd (line 33) is topically about `design-log.md` content but doesn't say "design-log" in its label. None of the 8 checks reference `params.md`, `build_mesh.py`, or `measurement.py` at all — T7's own edit targets are outside every one of these checks' scope. I can't tell whether "four" is a plan-author miscount, a copy-paste of T4's GREEN clause (which legitimately edits `design-log.md`) onto T7 where it's vacuously true, or whether I'm missing a fourth check somewhere.
2. **T7's Test line has no "package suite green" clause**, unlike T4/T5/T6/T8's Test lines. Is that a deliberate signal that no test run is required for a pure-prose params.md fix, or an omission I should still cover defensively?
3. **Annotation convention unstated for T7 specifically.** T7's own Risk line (unlike T4's, which explicitly says "annotate-don't-delete convention") says nothing about whether the correction must be a dated `**YYYY-MM-DD 更正**` annotation that preserves the original wording, vs. a silent rewrite. But `params.md` itself already has this exact convention in-file at least 5 times (lines 29, 38, 61, 79, 129, 133) for identical "the doc drifted from the truth" situations. I'd default to following the file's established convention, but it's not explicit for T7 and would need a stamped date (which date — 2026-08-21, matching when the ship value actually changed, or today's branch date — is also unstated).
4. **Row at line 75 has a pre-existing framing inaccuracy orthogonal to the walnut→hinoki fix**: it states the flag's "type／default" column as a concrete hex (`` `#6B4A2F` ``) as if that were `--wood-hex`'s own argparse default, but the real argparse default is `None` (confirmed at `build_mesh.py` line ~871: `default=None`) — the concrete hex is only the *effective* value once it falls through to `materials.py`. T7's Test only asks to correct species/hex naming, not this framing, but touching the same cell for one reason while leaving an adjacent inaccuracy sitting right next to it is a judgment call worth surfacing before I write the fix.

### NEEDS_CONTEXT count: 4
