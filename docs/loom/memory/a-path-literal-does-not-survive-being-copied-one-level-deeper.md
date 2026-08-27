---
name: a-path-literal-does-not-survive-being-copied-one-level-deeper
description: A relative path that resolves from SKILL.md dangles when the same text is copied into references/ or rubrics/ one level down, and check-skill-crossrefs.py cannot see it — by its own docstring it checks inline markdown links only, so a backtick-quoted path is unchecked at any depth; the reviewer who first found one dismissed it on the same reasoning the checker encodes, that plain text is not a link
type: gotcha
origin: fix/conditional-ops-path (2026-08-27) — three dangling path literals in subagent-driven-development/references/conditional-operations.md, all created when #740 extracted prose out of SKILL.md; the checker reported OK throughout, and #740's own reviewer had seen one and filed it as a nit
---

`#740` moved prose out of `subagent-driven-development/SKILL.md` into a new
`references/conditional-operations.md`. Three path literals came with it and
stopped resolving, because the new home sits one directory deeper:
`hooks/family-relay.md` and `hooks/family-reception.md` (correct from the plugin
root, which is how the sibling `SKILL.md` files write them) and
`using-loom-code/references/environment-gotchas.md` (needs `../../` from
`references/`). `check-skill-crossrefs.py` reported
`OK: all relative skill cross-references resolve` before and after.

**Why:** the checker's docstring states its own bound — "only INLINE links
``](target)`` are checked". All three were backtick-quoted plain text, so none
was ever in scope. The more useful half of this: #740's whole-branch reviewer
*did* find one, and filed it as a nit with the reason "it is plain text, not a
link" — the same assumption the checker encodes. The tool and the human failed
identically. An agent told to open a path does not care whether the path is a
markdown link, so "not a link" is not a reason for it to matter less.

**How to apply:** when prose moves between depths — SKILL.md into
`references/`, a reference into `rubrics/`, anything into `agents/` — re-resolve
every path literal from the NEW directory, not just the markdown links. A
repo-root-relative form (`loom-code/hooks/family-relay.md`) survives the move;
a bare or shallowly-relative one does not. Two cheap rules that avoid the class:
prefer the plugin-qualified form for anything outside the current skill, and
when the pointer crosses into another skill, ask whether the content should be
internalized instead — a reference file that needs a second skill open to be
actionable is a dependency, not a citation. Do not read a green
`check-skill-crossrefs.py` as coverage of anything but inline links.
Related: [[a-mechanical-check-can-go-green-by-skipping]],
[[a-compaction-test-written-from-the-compacted-file-cannot-see-what-left]].
