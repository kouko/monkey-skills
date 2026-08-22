---
name: 2026-08-22-line-cites-should-be-anchor-primary-across-the-loom-institutions
description: contract text must cite only what its reader can resolve, and loom breaks that two ways — line numbers that rot within a single change, and 28 citations pointing at `docs/loom/**` that the plugin bundle does not ship, so every deployed agent holds references it cannot open; one rule and one checker cover both
status: bet
origin: 2026-08-22 code-as-spec-lens-no-op-bar arc — three citation defects in one plan, all in the line numbers, none in the anchors those cites were paired with; user asked for the rule to be made explicit in the loom mechanism
start: promoted to bet 2026-08-22; the dangling-path half is already broken in production and is the first leg
serves: A citation a reader cannot resolve is the most direct blocker to the purpose's "Done when" — a foreign repo installs loom cold and no contract text cites a document that repo cannot open. The 28 dangling `docs/loom/**` citations are that exact failure, live in the deployed 0.94.0 bundle today.
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

## Scope widened at promotion (2026-08-22)

The entry was filed as a line-number problem. Verifying the 0.94.0 deployment
widened it: the same defect class has a second and more damaging form.

- **Leg 1 — citations that do not ship.** 28 unique citations inside
  `loom-code/skills`, `loom-code/agents` and `loom-design/skills` name specific
  files under `docs/loom/specs|plans|memory`. The plugin bundle contains
  `agents`, `hooks`, `scripts`, `skills` and `loom-code/docs` — not the
  repository's `docs/loom/`. Verified against the deployed cache at
  `~/.claude/plugins/cache/monkey-skills/loom-code/0.94.0`: no `docs/loom`
  directory exists there, so all 28 are unresolvable for every dispatched
  agent, in this repo and in any other. This is broken now, not after a split.

- **Leg 2 — citations that rot.** Line numbers drift within the change that
  writes them. Three shipped in one plan in one day, all in the numbers, none
  in the anchors they were paired with.

- **One rule covers both:** contract text cites what its reader can resolve —
  an anchor that travels with the bundle, or a quoted string checkable by
  substring search. `plan-format.md` §Stated facts currently requires the
  opposite ("cite the narrowest form that resolves", line-first).

- **The verification cost question is now answered.** Industry survey found no
  shipped system uses line-number-primary with a live verifier; GitHub's
  permalink sidesteps drift by freezing to a commit SHA. Anchor verification
  splits into two tiers — symbol-name anchors need a language parser
  (expensive), while quoted-string and named-marker anchors are a build-time
  substring search (Sphinx `literalinclude`, mkdocs Snippets). Ours is the
  cheap tier: `check_doc_citations.py` already resolves paths and bounds, and
  "does this string still occur in this file" costs about the same.
