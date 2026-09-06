# 淺木色與更深的窗內紙 — spec (engineering, sample)
intent: 2026-08-20-light-wood-and-darker-inside-paper@n/a

Written from `contract/templates/spec-minimal.md` for the kumiko sample
change (`ab-plan-charter.md`), needs-design: no. No `confirmed-behavior:`
line — decision point ② stays product-only.

## Requirements
REQ-1 — params.md names the shipped species and hex
  WHEN `docs/loom/params.md` is read, the three 核桃木 references at lines
  75/89/99 shall read 檜木／`#D9B382`, each checked against the code's
  actual default rather than assumed. → T7 Test.

REQ-2 — the `--wood-hex` row states the real fallthrough
  WHEN the `--wood-hex` row is read, it shall state the type/default as
  `str | None`／`None`, falling through to `blender/materials.py`'s
  `_WOOD_SRGB_HEX` — not a hex literal claimed as `build_mesh.py`'s own
  default (its argparse default is `None`). → T7 Test, Risk.

REQ-3 — verify-docs.sh stays unaffected
  WHEN `scripts/verify-docs.sh` runs after these edits, its four
  design-log checks shall PASS exactly as before — none of them reads
  `params.md`, `build_mesh.py`, or `measurement.py`. → T7 Test.

REQ-4 — corrections annotate, never rewrite
  WHEN a prose correction lands in a T4–T9 artifact, the original wording
  shall stay in place, with a dated correction (`2026-08-22`, the shipped-
  pair verification date) added beside it. → T4/T5/T6/T8/T9 Test lines'
  shared convention.

## Design decision
- agent-decided — `docs/loom/design-log.md`'s 木色選擇 row anchors on a
  species-neutral `出貨色 ~#D9B382`, deliberately unnamed by species, so a
  hex value never carries a species label that goes stale; every REQ above
  names 檜木 only beside the hex, never instead of it.
- agent-decided — T4–T9 correct prose by annotating a dated correction
  beside the original claim, never rewriting it; T7 follows the same
  convention, dated 2026-08-22 (the shipped-pair verification date).
- agent-decided — `build_mesh.py --wood-hex`'s argparse default is `None`;
  the resolved value comes from `materials.py:_WOOD_SRGB_HEX`, not a
  literal on the flag itself — REQ-2 restates the type/default column
  rather than swapping only the hex.
- agent-decided — `verify-docs.sh`'s four design-log checks read
  `design-log.md` and code constants, not `params.md`; REQ-1/REQ-2 cannot
  change their result.
- agent-decided — T7's Test carries no package-suite clause: `params.md`
  is pure prose, exercised by no test, unlike T4/T5/T6/T8/T9; the absence
  is deliberate.

## Alternatives considered
- Naming only the hex on the `--wood-hex` row, leaving `str`／`#D9B382` as
  its stated default — rejected: same wrong claim (a literal default) as
  the walnut hex, just a new number.

## Current state evidence
- Forward: docs/loom/params.md:75,89,99
- Reverse: blender/materials.py:29 (`_WOOD_SRGB_HEX`), src/kumiko/output/measurement.py:68 (`_WOOD_HEX`)
- Boundary: blender/build_mesh.py:870-877 (`--wood-hex` argparse default is `None`)

## UI flows
N/A
