---
name: 2026-08-22-line-cites-should-be-anchor-primary-across-the-loom-institutions
description: contract text must cite only what its reader can resolve, and loom breaks that two ways — line numbers that rot within the change that writes them, and 28 citations naming `docs/loom/**`, which resolve inside monkey-skills but not in any repo that merely installed the plugin; one rule and one checker cover both
status: closed
origin: 2026-08-22 code-as-spec-lens-no-op-bar arc — three citation defects in one plan, all in the line numbers, none in the anchors those cites were paired with; user asked for the rule to be made explicit in the loom mechanism
start: promoted to bet 2026-08-22; the dangling-path half is already broken in production and is the first leg
serves: The purpose's "Done when" requires a foreign repo to install loom cold with no contract text citing a document that repo cannot open. The 28 `docs/loom/**` citations are exactly that: they resolve in monkey-skills and nowhere else, so they are the standing blocker on that condition.
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
  directory exists there.

  **Corrected 2026-08-22, same day, before any work started.** The first
  write-up of this leg said all 28 were unresolvable for every dispatched
  agent. That is false, and the error was mine. A dispatched agent has
  filesystem tools and reads the WORKING REPOSITORY, not the plugin bundle —
  inside monkey-skills these citations resolve, and a docs-reviewer on this
  repo reported opening one and checking a claim against it. What actually
  breaks is a repo that installed the plugin and has no `docs/loom/` of its
  own. That makes this a portability blocker against the purpose's Done-when,
  not a live defect here — a smaller claim, and the true one.

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

## Leg 1 shipped 2026-08-22, with one exit condition recorded as unreachable

Leg 1 (citations that do not travel) shipped: a checker with a shrink-only
debt list, the rule written into `CLAUDE.md`, the three agent contracts
cleared, and `loom_init.py` scaffolding the memory store its own skills cite.

A whole-branch reviewer named a limit worth carrying forward rather than
rediscovering. Provenance removed from the agent contracts was relocated into
the `references/design-evidence.md` siblings — but those files are themselves
inside the checker's scope and on the debt list, so the relocation moved
citations from one banned file into another. Since the list is shrink-only and
every relocation re-pins its target, the list cannot reach empty while that
pattern continues.

Two ways out, neither chosen here: move the relocation target outside the
checker's scope, or make `references/design-evidence.md` an exempt shape by
rule — which reopens the self-signed-exemption question this arc deliberately
answered no to. Whoever runs leg 2 should decide it explicitly rather than
inherit it.

- Shipped on branch `anchor-primary-line-cite-rule`: leg 2 made anchors the
  primary locator across author, plan, reviewer, and checker contracts; the
  follow-up dogfood also confirms the rule is explicit for prose, code, and
  configuration anchors.
