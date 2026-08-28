---
name: 2026-08-28-line-leading-heading-anchor-is-copy-pasted-across-packages
description: The line-leading heading-anchor idiom now appears at a dozen sites across five plugin packages, and the obvious fix — one shared helper — is blocked by the cold-install package boundary the fingerprint evidence depends on
status: open
origin: pin-granularity branch, round-3 review (2026-08-28) — one arm raised the duplication as 🟡 refactoring; the branch carried it as declared debt rather than crossing a boundary another arm had ruled on
start: next time a heading-anchor site needs changing, or when a shared test-support module is introduced for another reason
---

## The item

Twelve window helpers now resolve a markdown heading only at a line start,
because `"## Foo"` is a substring of `"### Foo"` and a bare search silently
retargets the window. Three of them use a named `_line_leading()` helper;
the rest inline the same ternary, each with a near-identical comment. Rule
of Three is exceeded fourfold, and the next change to the idiom has to be
made twelve times.

## Why the obvious fix was not taken

The twelve sites live in five different plugin packages — `loom-code`,
`loom-design`, `loom-workflow`, `think-orbit`, `copywriting-toolkit`. A
single shared module would have to be imported across those package
boundaries, and those boundaries are load-bearing: each plugin's
cold-install package is hashed independently, and the complexity-gate
evidence in `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
binds to those per-package fingerprints. A review arm ruled on that same
constraint earlier in this branch when declining a different cross-package
extraction.

So the real options are narrower than "extract it once":

- **One helper per package** (~5 copies instead of 12). Respects the
  boundary. Needs a place to live: the `scripts/` dirs carry no
  `__init__.py`, and adding one changes how pytest resolves modules — the
  same suites already collide on duplicate basenames when a whole tree is
  invoked at once, so this is not a free change.
- **A `conftest.py` per scripts dir** exposing the helper. Auto-loaded, no
  package required, but conftest is conventionally fixtures rather than
  importable utilities.
- **Leave it.** Twelve copies of four lines, each with the reason written
  next to it. The duplication is real; the coupling is not — no site's
  behaviour depends on another's.

## What would settle it

Whether the `scripts/` dirs should become real packages. That question is
older than this item (the basename-collision debt below is the same root),
and answering it makes the per-package helper trivial.

Related: the pre-existing collection failure when `pytest loom-design/scripts`
or `pytest loom-workflow` is invoked as one directory — same missing-package
root cause, noted by two review arms on this branch.
