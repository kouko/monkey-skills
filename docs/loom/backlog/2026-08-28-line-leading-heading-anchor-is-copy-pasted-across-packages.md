---
name: 2026-08-28-line-leading-heading-anchor-is-copy-pasted-across-packages
description: The line-leading heading-anchor idiom is now a shared helper in loom-code and loom-design/pipeline; loom-workflow still has bare unanchored heading windows carrying the original defect, and three single-site packages stay inline — the entry gives the grep commands rather than a site count, because three review rounds refuted three different totals
status: open
origin: pin-granularity branch (2026-08-28) — filed as a deferral, then rewritten after two review arms independently measured the deferral's premises and found them wrong
start: next time a heading window in loom-workflow or think-orbit needs touching
---

## What actually remains

`loom-code/scripts/heading_window.py` and
`loom-design/scripts/pipeline/heading_window.py` each hold one
`line_leading(text, heading, start=0) -> int`, via the sibling-module
pattern `loom-code/scripts/` already used for `distribute.py` — no
`__init__.py`, no conftest, no cross-package import.

**What "done" means here, precisely.** Every site that had hand-rolled the
line-leading *idiom* — the ternary or the five-line if/else — now imports
the helper, in the import roots that have one. It does NOT mean no bare
heading search remains anywhere: a much larger population of
`text.find("## Foo")` calls exists across the repo, most of them end
bounds, searches over test-generated output, or windows nobody has
examined. This branch never claimed that population, and a reviewer who
greps for it will find dozens inside packages this entry calls done. Two
review arms raised exactly that, which is why the distinction is written
here rather than left to the reader.

What is left:

- **`loom-workflow` heading windows that are still bare substring searches.**
  These carry the original defect: `"## Foo"` matches inside an earlier
  `"### Foo"`, silently retargeting the window while the assertions inside it
  keep passing. The package is NOT uniformly unanchored —
  `skills/goal-create/scripts/test_skill_md.py` `_section` anchors correctly
  with `r"^##\s+" + re.escape(heading) + r"\s*$"` under `re.MULTILINE`, a
  different mechanism that is equally sound — so this is specific sites, not
  a package-wide gap.
- **`loom-design/scripts/interface/` keeps two sites inline.** `scripts/`
  there is split into per-subdirectory import roots, so `pipeline/`'s helper
  is not importable from `interface/`; two sites do not earn a third copy of
  four lines.
- **`think-orbit` and `copywriting-toolkit` have one site each**, both already
  correctly anchored, both left inline: one caller does not earn a module.

## No site counts here, on purpose

Earlier drafts of this entry stated totals, and three review rounds refuted
them in a row — the last time by two reviewers who each counted independently
and got DIFFERENT answers. The reason is that "the same idiom" spans a
one-line ternary and a five-line if/else, and no draft ever wrote down which
to count; every total was defensible under one rule and wrong under the other.

So the numbers are replaced by the commands that produce them. Run these
rather than trusting a sentence:

```
# hand-rolled line-leading anchors NOT yet on the shared helper.
# This is the item's actual population; it reproduces the residual above.
grep -rn 'startswith(.*heading' --include='test_*.py' .

# sites already on the shared helper
grep -rn 'from heading_window import' --include='test_*.py' .
```

A third grep is deliberately NOT given. Searching for every bare
`.find("## …")` returns dozens of hits in packages this entry calls done,
because that pattern also matches end bounds and searches over generated
output. Sorting a defective one from a correct one there needs reading, not
grepping — treat that as a separate, unscoped question rather than a
to-do list this entry hands over.

## What the deferral got wrong, kept visible

The first version of this entry deferred the whole consolidation, claiming the
sites spanned five packages including `loom-workflow`, so extracting a helper
would have to cross the cold-install package boundaries the fingerprint
evidence depends on. Both arms of that round measured it and refuted it:
`loom-workflow` carries none of the idiom, so it was never a boundary case,
and the large majority of sites sat inside `loom-code` alone, where no
boundary is crossed at all. The fingerprint objection did not survive either —
a package-content change costs one recomputed candidate hash, and
`scripts/test_stage_specific_complexity_behavior_evidence.py` verifies that
hash against a live recomputation, so the cost is checked rather than trusted.

The lesson is kept rather than smoothed away: the deferral was argued from a
package list nobody had counted, and the boundary it invoked was real but did
not apply to the work it was invoked against.

Related: the pre-existing collection failure when `pytest loom-design/scripts`
or `pytest loom-workflow` is invoked as one directory — duplicate test-module
basenames with no package namespacing. The repo's CI already works around it
by invoking each directory separately.
