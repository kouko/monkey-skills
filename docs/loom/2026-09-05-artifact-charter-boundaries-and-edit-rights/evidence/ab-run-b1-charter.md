# A/B run B1 — charter plan (941 words), task T7, cold implementer (sonnet), read-only

Scratch clone of the sample repo at c1d8cc7; plan file PLAN-charter.md ("T7"). Verbatim status report follows.

---

**Files read**: `docs/loom/params.md`, `blender/build_mesh.py`, `src/kumiko/output/measurement.py`, plus (per T7's Risk note, citing T3) `docs/loom/measurements/2026-08-20-shipped-pair-verification.md`, and `docs/loom/design-log.md`'s 木色選擇 row for the current SSOT anchor. Also checked T2's already-landed commit (`a312e7c`) to confirm the code-side state this task must match.

### RED found (verbatim, as I'd report it)

`docs/loom/params.md` has three stale `核桃木` references that no longer match the shipped code (design-log's 木色選擇 row was already corrected in an earlier task to a species-neutral `出貨色 ~#D9B382` anchor, per commit `7f38d12`/`a312e7c`):

1. Line 75, `build_mesh.py --wood-hex` row: states value as `str`／`#6B4A2F`（design-log 核桃木）. Two things are wrong here, not one: the species name is stale, **and** the stated default itself is wrong — `build_mesh.py:870-877`'s actual argparse default is `None` (not any hex literal); the help text there also still reads "…走 `materials` 的預設（design-log 的核桃木）" — same stale phrase, in code, not just docs.
2. Line 89, `build_scene(wood_hex)` row: prose says "讓 `materials` 用自己的預設（design-log 核桃木）" — same stale phrase also appears verbatim in `build_mesh.py:129` (the function's own docstring).
3. Line 99, `kumiko-measure --lstar` row: "缺省掃核桃木 L* 加 60/65/70/75/80" — verified against `src/kumiko/output/measurement.py:71-78`: the default tuple base is `lstar_of(_WOOD_HEX)` with `_WOOD_HEX = "#D9B382"` (comment there already correctly calls this "樹種中立" / species-neutral); the 60/65/70/75/80 offsets are correct, only the species label is stale.

`measurement.py` itself needed no fix (already carries a dated `2026-08-21 核桃木 → 檜木` correction) — it served only as the verification source, per the Test's "verified against the code's actual default, not assumed."

### GREEN criteria as understood

- All three `核桃木` hits in `params.md` corrected against the actually-verified current defaults (not the pre-shipped `#6B4A2F`, and not assumed).
- `build_mesh.py`'s own two matching stale mentions (docstring line ~129, help text line ~874-875) also corrected — it's a listed File, and nothing else in the plan (T5/T6 own materials.py / the smoke test) claims it.
- `verify-docs.sh`'s four design-log checks still PASS (should be unaffected — none of T7's edits touch `design-log.md` itself).

### open_questions

1. The plan's Test line literally says "corrected to name hinoki/`#D9B382`" — but `design-log.md`'s own 2026-08-21 correction to the 木色選擇 row explicitly established the anchor as species-neutral ("出貨色", "刻意不帶樹種名") *specifically* to stop species names from becoming stale labels on the hex value. Writing "檜木/hinoki" literally into `params.md` would reintroduce the exact pattern that row just corrected. Should the three hits cite the species-neutral `design-log 出貨色 #D9B382` anchor (matching the established convention) instead of literally naming the species, contra the plan's literal wording?
2. For the `--wood-hex` row specifically: is a same-shape swap (`#6B4A2F` → `#D9B382`) sufficient, or does the type/default itself need restating as `str | None`／`None`（缺省沿用 materials 的預設）to match what the code actually does — since the argparse default is `None`, not a hex literal? The Risk note ("do not copy the assigned hex blindly") suggests the latter but doesn't say so explicitly.
3. T5's Test (same-arc, same kind of prose artifact) requires materials.py's corrections to be dated annotations, not silent rewrites ("annotate-don't-delete" convention used across T4/T5/T6/T8/T9). T7's Test line doesn't say this explicitly for either `params.md` or `build_mesh.py`'s docstring/help text. Should T7 follow the same annotate-in-place convention, or is a direct correction acceptable here?

### Output contract

status: NEEDS_CONTEXT
RED found: docs/loom/params.md lines 75/89/99 cite `核桃木` (and, at line 75, the wrong default value/type entirely — `#6B4A2F` vs actual argparse default `None`); blender/build_mesh.py carries the identical stale `design-log 的核桃木` phrase in its own docstring (line ~129) and `--wood-hex` help text (line ~874-875), matching the code state before T2's `a312e7c` shipped `#D9B382`/species-neutral anchor.
GREEN criteria as understood: all three params.md hits corrected against verified (not assumed) code defaults; build_mesh.py's matching two stale mentions also corrected; verify-docs.sh's four design-log checks PASS (unaffected by these edits).
open_questions: (1) literal species-name wording vs design-log's own species-neutral convention; (2) whether `--wood-hex` row needs its type/default column restructured, not just its hex literal swapped; (3) whether corrections must follow this arc's annotate-don't-rewrite convention.
NEEDS_CONTEXT count: 3

---

Orchestrator note: question (1) is the design rationale the charter routes to the spec; this engineering change has no spec, so the charter plan could not carry it and the reader asked. Questions (2) and (3) were asked in substance by run A1 as well.
