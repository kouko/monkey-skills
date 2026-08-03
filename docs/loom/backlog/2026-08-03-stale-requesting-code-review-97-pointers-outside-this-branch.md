---
name: 2026-08-03-stale-requesting-code-review-97-pointers-outside-this-branch
description: Three documents still cite `requesting-code-review/SKILL.md:97` for the citation pre-pass fence/blockquote caveat, which loom-code 0.46.0 moved to `requesting-docs-review/SKILL.md:54` — the cited line is now blank, so the pointer fails silently and the citation checker cannot see it (in bounds, wrong content)
status: OPEN
origin: found by `scripts/claim_copy_sweep.py` while repairing the two in-scope copies on branch `feat-repair-side-sweep` (2026-08-03). A docs reviewer named the two copies inside that branch's review scope; the sweep found three more outside it.
start: the next time anyone opens one of the three named files for another reason — or immediately, if a reader is about to follow one of these pointers. Each is a one-clause edit.
---

## What

The caveat — *"treat pre-pass findings inside fenced code blocks, blockquotes,
table cells, and inline examples as advisory, not as defects"* — used to live at
`loom-code/skills/requesting-code-review/SKILL.md:97`. The review-scope-resolver
arc (loom-code 0.46.0, PR #641) rewrote that skill and the caveat now lives at
`loom-code/skills/requesting-docs-review/SKILL.md:54`. **Line 97 of the old file
is now blank**, so every surviving pointer resolves to nothing and says nothing —
the `repointing-a-stale-citation-can-trade-a-loud-failure-for-a-silent-one` shape
this store already records.

`check_doc_citations.py` cannot catch it: the line number is in bounds, so the
bounds check passes. Only opening the target reveals it.

## The three copies still stale

Swept with
`python3 scripts/claim_copy_sweep.py --claim "requesting-code-review/SKILL.md:97"`:

- `docs/loom/backlog/2026-07-30-standalone-docs-review-skill-shape-decided-shipped-this-arc-0-42-0.md:39`
- `docs/loom/plans/2026-07-30-docs-review-blocking-class.md:11`
- `docs/loom/specs/2026-07-30-docs-review-blocking-class.md:16`

Two further hits are in `.claude/handoffs/`, which is gitignored and is a
historical record — leave those alone.

## Why they are filed rather than fixed

The branch that found them (`feat-repair-side-sweep`) was not editing those three
files for any other reason, and this repo's convention is surgical edits: fix what
your change touches, name what it does not. The two copies inside that branch's
own scope were repaired there.

**The plan and spec copies need a judgement the fixer must make, not a
find-and-replace**: both are dated 2026-07-30 artifacts describing a design as it
stood then, so whether each is an operative pointer a reader would follow or a
frozen record of what was true at authoring time has to be decided per file. The
backlog entry is unambiguously operative.
