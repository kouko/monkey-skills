---
name: 2026-08-19-should-required-field-skip-seq-for-research-notes
description: should `required-field` skip `seq` for `origin == "research"`, matching the two existing research carve-outs? Three pieces of evidence in dag.py say a research note was designed not to need a position in the reasoning chain — two sibling rules already carve out that origin, and the loader's sort deliberately tolerates a missing seq — but the required-field rule demands it anyway; the transparency arc documented the wart instead of resolving it, because adding a third carve-out is a behaviour change to a shipped rule
status: open
origin: 2026-08-19 think-orbit transparency arc, T3 follow-up — surfaced when node-schema.md's worked examples were brought under the `<!-- example: -->` marker convention and the real `check`; the research-note example failed `required-field` and the file's own "minimal frontmatter" sentence had omitted `seq` too
start: next `think-orbit/scripts/dag.py` touch, or the next time a research note trips `required-field`
---

`_rule_required_field` requires `seq` on every node with no `origin` carve-out, so a
research note must carry one. Three pieces of evidence in the same file say research
notes were designed NOT to need a position in the reasoning chain, which is what `seq`
means — a research note is an external source entering the graph, not a step inside it:

- `_rule_fact_source` carves out `origin == "research"` (`dag.py:288`).
- A second carve-out for the same origin exists at `dag.py:645`.
- The loader's own sort tolerates a missing `seq` deliberately —
  `key=lambda n: (n.seq is None, n.seq, ...)` at `dag.py:240` sorts unsequenced nodes last.

Surfaced 2026-08-19 while bringing `references/node-schema.md`'s worked examples under
the `<!-- example: -->` marker convention and the real `check` (transparency-both-faces
arc, T3 follow-up). The example `research/r1.md` failed `required-field`, and the file's
own "minimal frontmatter" sentence had omitted `seq` too. That was fixed the documenting
way — the example and the sentence now both carry `seq`, and the examples are gate-verified
— because adding a third carve-out is a behaviour change to a shipped rule, outside that
arc's brief, and the whole-branch reviewer judged that deciding it inside a redaction fix
round would be the scope creep the plan had already refused elsewhere.

So the wart is documented and test-pinned rather than resolved. The open question is which
way it should settle: keep `seq` required everywhere (and the doc is now correct), or add
the third `origin == "research"` carve-out so the exemption mechanism is consistent across
all the sibling rules that already have it. Whoever picks this up should decide on the
meaning of `seq` for an external source, not on which is the smaller diff.
