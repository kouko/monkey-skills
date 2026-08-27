---
name: a-compaction-test-written-from-the-compacted-file-cannot-see-what-left
description: A test authored alongside a compaction pins phrases read off the AFTER file, so every rule the compaction dropped is absent from the pin set by construction and the suite goes green over the loss; #740 shipped 33 such tests and four independent audits later found five deleted rules none of them could have caught — the guard against loss is a before/after rule diff, never the post-hoc presence list
type: gotcha
origin: fix/740-compaction-followups (2026-08-27) — three per-family audits plus one blind second opinion, all reading `git show <base>^:<path>` rather than the test files, found five rules #740 deleted outright; the compaction suite was green throughout
---

PR #740 compacted 33 loom skill entrypoints and shipped 33
`test_*_compaction.py` files, each pinning ~20 load-bearing phrases and all
but one a word-count band. Every one passed. Four independent audits of the same diff
then found five rules the compaction had deleted with no successor anywhere:
`complexity-critique`'s mindset SSOT edit-order rule, `cot-explain`'s
`think-orbit:*` routing destinations, `completeness-critic`'s deletable-lenses
section, `subagent-driven-development`'s stdlib-over-third-party rule with its
`NEEDS_REVISION` consequence, and a `verification-before-completion` README
still advertising exemptions its own SKILL.md had revoked.

**Why:** the pin set was read off the compacted file. A phrase that left in the
same change is not in the AFTER text, so nobody writes an assertion for it —
the test cannot detect the deletion it was written after. Presence assertions
are also blind to additions by construction, so the suite constrains neither
end of the change it exists to guard. A word-count band looks like it covers
the gap and does not: it measures volume, never which content is present.

**How to apply:** when a change removes prose from a contract file, the guard
is a rule-level before/after diff — enumerate the rules in
`git show <base>^:<path>`, then check each one has a successor in the new file
or a named destination it moved to. Sort every removed passage into (a) same
rule, fewer words, (b) moved to a reference (name the file, verify the pointer
exists), or (c) rule changed or gone — only (c) is a finding, and only a
human-or-agent reading both versions produces it. Write the compaction test
from that enumeration, not from the file you just finished writing. Related:
[[a-test-can-pin-behaviour-with-a-false-rationale]],
[[a-cap-raised-at-every-touch-is-not-a-cap]].
