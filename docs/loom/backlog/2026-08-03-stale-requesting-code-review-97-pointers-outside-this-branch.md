---
name: 2026-08-03-stale-requesting-code-review-97-pointers-outside-this-branch
description: Documents outside branch `feat-repair-side-sweep` still cite `requesting-code-review/SKILL.md:97` for the citation pre-pass fence/blockquote caveat, which loom-code 0.46.0 moved to `requesting-docs-review/SKILL.md:54` — the cited line is now blank, so the pointer fails silently and the bounds-only citation checker cannot see it; the surviving copies are listed here by path, without a total, because this entry is itself inside the swept corpus
status: open
origin: found by `scripts/claim_copy_sweep.py` while repairing the in-scope copies on branch `feat-repair-side-sweep` (2026-08-03). A docs reviewer, working from the branch diff, named only the copies inside review scope; the sweep found more outside it — and a first draft of THIS entry then undercounted its own sweep output, which a later reviewer caught.
start: the next time anyone opens one of the listed files for another reason — or immediately, if a reader is about to follow one of these pointers. Re-run the sweep first (below); do not work from the list alone.
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

## Re-run this before acting

```
python3 scripts/claim_copy_sweep.py --claim "requesting-code-review/SKILL.md:97"
```

**No count is stated in this entry, deliberately.** This file is a `.md` inside
the corpus the sweep walks, so every sentence here that names the pointer becomes
another hit; a total written down would be wrong the moment it landed. That is
leak three in
`docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`,
and the first draft of this entry demonstrated it by undercounting its own sweep.

## Copies outside this branch's scope, as of commit 6b946ed0

Hits inside this entry, inside `docs/loom/BACKLOG.md` (generated from the
frontmatter above), inside the memory entry, and inside
`docs/loom/backlog/2026-07-28-plan-stage-fact-grounding-what-0-39-0-does-not-close.md`
are self-referential or already repaired — they name the stale pointer in order
to discuss it. Hits under `.claude/handoffs/` are gitignored historical records:
leave them. What remains, each needing a decision:

| Path | Reading |
|---|---|
| `docs/loom/backlog/2026-07-30-standalone-docs-review-skill-shape-decided-shipped-this-arc-0-42-0.md:39` | Operative — a backlog entry a reader acts on |
| `docs/loom/plans/2026-07-30-docs-review-blocking-class.md:11` | Needs a judgement (see below) |
| `docs/loom/specs/2026-07-30-docs-review-blocking-class.md:16` | Needs a judgement (see below) |
| `docs/loom/specs/2026-07-30-docs-review-blocking-class.md:115` | Second copy in the same file — present tense, reads as operative |
| `docs/loom/specs/2026-07-30-requesting-docs-review-standalone-skill.md:60` | Cites a range (`:97,100,147,173-186`); needs the same judgement |

## Why these are filed rather than fixed

The branch that found them was not editing these files for any other reason, and
this repo's convention is surgical edits: fix what your change touches, name what
it does not. The copies inside that branch's own scope were repaired there.

**The plan and spec copies need a judgement the fixer must make, not a
find-and-replace**: they are dated 2026-07-30 artifacts describing a design as it
stood then, so whether each is an operative pointer a reader would follow or a
frozen record of what was true at authoring time has to be decided per site. The
backlog entry is unambiguously operative.
