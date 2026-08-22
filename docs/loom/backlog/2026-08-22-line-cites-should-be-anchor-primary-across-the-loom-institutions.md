---
name: 2026-08-22-line-cites-should-be-anchor-primary-across-the-loom-institutions
description: the loom institutions currently REQUIRE a `path:line` cite and treat the stable anchor as an added pairing duty; the evidence says the numbers rot and the anchors do not, so the primary/secondary relationship should be inverted — a change that spans plan-format, both reviewer evidence contracts, and the citation checker
status: open
origin: 2026-08-22 code-as-spec-lens-no-op-bar arc — three citation defects in one plan, all in the line numbers, none in the anchors those cites were paired with; user asked for the rule to be made explicit in the loom mechanism
start: the next touch of plan-format.md §Stated facts, either reviewer agent's evidence contract, or check_doc_citations.py — whichever comes first
---

- The problem is not a missing rule; it is a rule pointing the other way.
  `plan-format.md` §Stated facts today reads "Cite the narrowest form that
  resolves — `src/renderers/csv.ts:120` or `:120-134`", making the line
  number the required form and the anchor an added pairing duty ("Pair every
  such line cite with the verbatim string or stable heading it locates").
  The proposal inverts that: the anchor is the citation, and a line number is
  optional precision that may be omitted whenever the anchor resolves alone.

- The evidence is from one arc and is one-sided. In the
  code-as-spec-lens-no-op-bar plan, three citation defects shipped and were
  caught across two review rounds. All three were in the numbers — a range
  read off `sed` output whose leading blank lines are invisible, off by two
  at the start and one at the end; then a second range off by one at both
  ends; then a heading pointer off by one. Zero defects landed on the
  anchors: the role-contract item number, the function name, the section
  heading, and the field name all resolved exactly, in both review rounds.

- The blast radius is what makes this an arc rather than a line edit. At
  least four surfaces state or consume the current rule:
  `loom-code/skills/writing-plans/references/plan-format.md` §Stated facts;
  `loom-code/agents/code-reviewer.md` Rule R2, whose evidence contract
  requires every finding to carry a `where:` citing `file:line` or a commit
  SHA, and flips the verdict to NEEDS_REVISION without one;
  `loom-code/agents/docs-reviewer.md`, whose finding schema pairs `where:`
  with `quote:`; and `loom-code/scripts/check_doc_citations.py`, which
  resolves paths and bounds. A change that softens the line-cite requirement
  in one place and not the others produces a contract that contradicts itself.

- Open question the arc must answer, not assume: an anchor-primary rule is
  strictly better for prose that a human or agent navigates by reading, but
  a line number is what a mechanical checker can bound-check cheaply. Whether
  `check_doc_citations.py` can verify an anchor — that the quoted string
  still occurs in the named file — at acceptable cost is unknown, and the
  answer decides whether this is a strengthening or a trade.

- Related, and already recorded from the other side:
  `docs/loom/memory/a-line-cite-fixed-before-its-file-is-edited-goes-stale-again.md`
  covers WHEN to resolve a cite (last step, after the content edits settle).
  This entry covers WHETHER the number should be there at all.
