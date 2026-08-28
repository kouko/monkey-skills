---
name: 2026-08-28-line-leading-heading-anchor-is-copy-pasted-across-packages
description: The line-leading heading-anchor idiom is now a shared per-package helper in loom-code and loom-design, but think-orbit still inlines it and loom-workflow never adopted it at all — its heading windows are still the bare unanchored form the idiom exists to replace
status: open
origin: pin-granularity branch (2026-08-28) — filed as a deferral, then rewritten after two review arms independently measured the deferral's premises and found them wrong
start: next time a heading window in loom-workflow or think-orbit needs touching
---

## What actually remains

`loom-code/scripts/heading_window.py` and
`loom-design/scripts/pipeline/heading_window.py` now hold one
`line_leading(text, heading, start=0) -> int` each, imported by every site in
those two packages via the sibling-module pattern `loom-code/scripts/` already
used for `distribute.py` — no `__init__.py`, no conftest, no cross-package
import. Two packages are done. What is left:

- **`loom-workflow` has not adopted the idiom at all.** Its heading windows are
  still bare substring searches — `test_handoff_compaction.py:77`
  `text.index("## Prepare mode")`, `:82`, `:93`, and
  `test_brief_before_asking_compaction.py:64`. These carry the original defect:
  `"## Foo"` matches inside an earlier `"### Foo"`, silently retargeting the
  window while the assertions inside it keep passing. Not a duplication item —
  an unconverted one.
- **`think-orbit` has a single site** (`scripts/test_skill_md.py:351`), left
  inline deliberately: one caller does not earn a module.

## Correction — what this entry said before, and why it was wrong

The first version deferred the whole consolidation, claiming the twelve sites
spanned five packages including `loom-workflow`, so extracting a helper would
have to cross the cold-install package boundaries the fingerprint evidence
depends on. Two review arms measured it independently and both refuted it:

- `loom-workflow` carries **zero** sites, so it was never a boundary case; the
  real spread was four packages, and **ten of fifteen sites sat inside
  `loom-code` alone**, where no boundary is crossed at all.
- The count itself was wrong — twelve inline ternaries plus seven helper call
  sites, not "twelve, three of which use a helper".
- The fingerprint objection did not survive either: a package-content change
  costs one recomputed candidate hash, and
  `scripts/test_stage_specific_complexity_behavior_evidence.py` verifies that
  hash against a live recomputation, so the cost is checked rather than
  trusted.

The lesson is kept here rather than smoothed away: the deferral was argued from
a package list nobody had counted, and the boundary it invoked was real but did
not apply to the majority of the work.

Related: the pre-existing collection failure when `pytest loom-design/scripts`
or `pytest loom-workflow` is invoked as one directory — duplicate test-module
basenames with no package namespacing. The repo's CI already works around it by
invoking each directory separately.
