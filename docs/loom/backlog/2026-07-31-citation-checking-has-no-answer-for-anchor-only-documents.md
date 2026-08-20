---
name: 2026-07-31-citation-checking-has-no-answer-for-anchor-only-documents
description: Citation checking has no answer for anchor-only documents
status: open
origin: PR #634 (loom-code 0.42.3). Whole-branch review demonstrated it on that PR's own audit note.
start: when a docs-review round misses a citation defect in a document that cites by `§N` anchor, OR when the `docs/loom/` corpus's anchor-cited population grows enough that `checked 0` runs stop being rare. Not urgent today — the gap is documented at both ends (loom-code CHANGELOG 0.42.3 "Known gap"; `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md` §附帶產出), so a reader who hits it is not misled.
---

- Start: when a docs-review round misses a citation defect in a document that
  cites by `§N` anchor, OR when the `docs/loom/` corpus's anchor-cited
  population grows enough that `checked 0` runs stop being rare. Not urgent
  today — the gap is documented at both ends (loom-code CHANGELOG 0.42.3
  "Known gap"; `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md`
  §附帶產出), so a reader who hits it is not misled.
- Origin: PR #634 (loom-code 0.42.3). Whole-branch review demonstrated it on
  that PR's own audit note.
- What: `check_doc_citations.py` bounds-checks `path:line` citations. A
  document with **zero recognized citations** — one citing purely by `§N`
  anchor, or naming files in prose — hits the `unchecked == 0` branch and
  prints `checked 0 / unchecked 0 / findings 0` + `OK: all citations resolve.`
  + exit 0, byte-identical to the pre-0.42.3 silent-all-clear the release
  fixed. Only the pathless-`:N` family was closed.
- Why it is not a simple oversight: the two citation forms have **opposite**
  robustness properties, and the repo mandates the one the checker cannot
  read. `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`
  carries an erratum requiring downstream documents to cite it by `§N` (line
  numbers drift when text is inserted — that erratum's own insertion proved
  it). The `§N` anchor check exists but ships behind `--sections`, off by
  default, because it produced zero confirmed true positives across four
  measurement rounds. So: line numbers are machine-verifiable and
  human-fragile; anchors are human-robust and machine-opaque. Closing the gap
  means deciding what "a citation" is when nothing in the text is
  machine-recognizable — a design question, not a patch.
- Non-starter already ruled out: turning `--sections` on by default. Measured at
  0.42.4 on the **tracked** `docs/loom/plans/` corpus — 154 files, pinned by
  `python3 loom-code/scripts/check_doc_citations.py $(git ls-files 'docs/loom/plans/*.md')`:
  `checked 122 / unchecked 72 / findings 1` becomes `checked 141 / unchecked 180 /
  findings 1` with `--sections`. The flag encounters 127 `§N` refs: it resolves 19 of them (finding **zero**
  additional defects) and reports the other 108 as `unchecked`.
  **The stable quantity is the share, not the counts**: 108 of the 127 `§N` refs the
  flag encounters — **≈85%** — are unresolvable against documents with no
  numbered-heading convention.
- Re-derive this measurement, never cite it. The entry has now been wrong about the
  absolute counts twice. Draft 1 wrote `unchecked 11 → 164`: pre-0.42.3 numbers, taken
  before pathless `:N` shorthands began counting as unchecked, and its ≈91% put
  non-`§N` unchecked refs in a `§N` numerator. Draft 2 wrote `129/73 → 157/226` with a
  "quote the deltas, not the absolutes" rule — whole-branch review falsified it: those
  were the untracked-inclusive working tree (167 files), where the deltas are +28/+153
  rather than the tracked corpus's +19/+108. **Counts and deltas are both
  population-bound; only the ≈85% share survived every population** (84.5% working
  tree, 85.0% tracked).
- Adjacent next-touch on the same script (all 🟢 from PR #634's review, none
  blocking): `main()` is 87 lines against the 50-line house ceiling
  (pre-existing; the reviewers' suggested cut is extracting the three-branch
  reporting tail as `_print_success_line`); `OK: all 1 checked citations
  resolve` reads ungrammatically at N==1 and a test pins the exact string, so
  a fix costs a paired edit; the "pathless `:N` shorthand, ambiguous path, or
  absent target" parenthetical is now duplicated across two branches — below
  Rule of Three, extract only if a third appears.
