# Brief: the anchor is the citation, the line number is optional precision

Date: 2026-08-22
Author: kouko (session)

## Design-side on-ramp

not fired — a rule inversion inside loom's own plan/review contracts; no product-shaped or user-facing surface

## Problem

When a plan or a review finding cites a location in a file, the citation is
written *before* the content it points at settles — a plan's Stated facts
are drafted while the source is still being edited, and a reviewer's `where:`
is filed against a tree the implementer is about to change. A line number
written at that moment rots within the same change that writes it.

The job is to cite a location that survives the change that writes it, so
that a downstream reader — implementer, reviewer, or a future session — can
resolve the cite without re-deriving it.

The evidence is from one arc and is one-sided. In the code-as-spec-lens-no-op-bar
plan, three citation defects shipped and were caught across two review
rounds. All three were in the numbers — a range read off `sed` output whose
leading blank lines are invisible, off by two at the start and one at the
end; then a second range off by one at both ends; then a heading pointer off
by one.

Zero defects landed on the anchors: the role-contract item number, the
function name, the section heading, and the field name all resolved exactly,
in both rounds. The number is the fragile half; the anchor is the stable
half. The rule today requires the fragile half and treats the stable half as
an added pairing duty.

## Users

Two writers, one reader, all inside loom's pipeline. A **plan author**
writes `file:line` citations in Stated facts and Context paths, before the
source settles. A **reviewer** writes `where:` findings against a tree the
implementer is changing.

The **reader** is the downstream implementer, reviewer, or session that
navigates by the cite — by reading, not by re-deriving. The existing tools
are `plan-format.md` (prescribes line-first), the reviewer agents' R2
(enforces `file:line` or SHA), and `check_doc_citations.py` (bound-checks the
line). All three treat the number as the citation and the anchor as optional
pairing.

## Smallest End State

The rule inverts: the anchor — a verbatim string or a stable heading — is
the citation. A line number is optional precision, required only when the
anchor alone is ambiguous (the string occurs more than once in the file).

Every surface that states or consumes the line-first rule is inverted in the
same arc, because a change that softens it in one place and not the others
produces a contract that contradicts itself. The mechanical checker gains
substring verification — "does this quoted string still occur in this file"
— as the primary check, with line-bounds kept as a secondary check when a
line number is given.

BI-1 — `plan-format.md` §Stated facts inverted: the anchor is the required
citation, the line number optional precision. The "cite the narrowest form
that resolves — `file:line`" sentence becomes "cite the anchor that resolves
— the verbatim string or stable heading; a line number is optional
precision."

BI-2 — the reviewer R2 block inverted at its SSOT
(`loom-code/scripts/_reviewer-discipline.md`), so `distribute.py` propagates
the change to all four verdict-producing agents (code-reviewer,
code-quality-reviewer, spec-reviewer, docs-reviewer) in one run. The `where:`
field's locator becomes the anchor; a line number is optional precision.

BI-3 — `docs-reviewer.md` rule 7 and its output schema inverted: `where:`
is the path, `quote:` (the anchor) is the primary locator, a line number is
optional precision. This surface is docs-reviewer-specific and not in the
shared R2 block.

BI-4 — `handoff-brief-format.md` §Current State Evidence inverted: each
sub-bullet's `file:line` requirement becomes an anchor requirement.

BI-5 — `quality-gate.md` inverted at its SSOT
(`domain-teams/skills/code-team/rubrics/quality-gate.md`), so `distribute.py`
propagates it into `loom-code`. "File path + line number + specific problem"
becomes "anchor + specific problem."

BI-6 — `check_doc_citations.py` gains substring verification: when a citation
carries a paired quoted string, the checker verifies the string occurs in the
named file. The file-reading and path-resolution machinery is already in
place; the work is a regex to capture the paired quote and one `in` check
against the already-read text. Line-bounds checking stays as a secondary
check when a line number is present.

BI-7 — the schema-example surfaces aligned: `gate-markers-spec.md`,
`requesting-code-review/SKILL.md`, and `requesting-docs-review/SKILL.md`
carry `where: <file:line>` as the illustrative required form; these become
`where: <path + anchor; line optional>` so the examples do not contradict
the inverted rule.

BI-8 — the plugin version bumped across all coupled sites for every plugin
whose shipped content changed (loom-code for the agents/skills/scripts;
domain-teams for the quality-gate SSOT). Declared here rather than
discovered after implementation — a contract-content PR that does not bump
the version is a silent no-op after merge, the failure this repo has
recorded.

## Current State Evidence

- **Forward** — the line-first rule is stated at
  `loom-code/skills/writing-plans/references/plan-format.md:298` ("Cite the
  narrowest form that resolves — `src/renderers/csv.ts:120`") and consumed
  by at least thirteen surfaces: the four the bet named plus the sibling
  reviewer agents' R2 blocks, `dispatch-hygiene-notes.md`, the brief schema,
  the orchestrator skills' `where:` schemas, the plan-document-reviewer, the
  quality rubric, and the external-surface-grounding standard.

- **Reverse** — the SSOT chain, confirmed by reading `distribute.py` and
  `_reviewer-discipline.md`. The R2 block's canonical text lives at
  `loom-code/scripts/_reviewer-discipline.md:28-38`; `distribute.py:196-202`
  injects it into the four reviewer agents between `reviewer-discipline-v1`
  BEGIN/END markers, so editing the SSOT and re-running `distribute.py`
  propagates R2 to all four in one pass. `quality-gate.md`'s SSOT is in
  `domain-teams/skills/code-team/`, copied one-way into `loom-code` by the
  same script. The direction is domain-teams → loom-code; loom-code is the
  consumer, so the quality-gate edit lands in domain-teams.

- **Error** — three citation defects in one plan in one day, all in the
  numbers, none in the anchors they were paired with (bet entry origin). The
  contract already contradicts itself: `plan-format.md:298` cites
  `dispatch-hygiene-notes.md` §Dispatch-packet context (a) as the authority
  for its pairing duty, but that file at lines 113-119 already states
  "Anchor by string, never by line number alone. Line numbers rot within a
  single branch." The authority plan-format.md defers to says the opposite
  of what plan-format.md prescribes.

- **Data** — `check_doc_citations.py` does path resolution and line-bounds
  only; its docstring at line 27 is explicit: "No quoted-string verification,
  no other semantic check." `extract_citations` (line 130) captures
  `path:line` spans only. The file is already read at line 229
  (`read_text` + `splitlines()`); a substring check reuses that read. The
  missing piece is a regex to capture the paired quoted string and one `in`
  check. The `--sections` opt-in pattern (line 448) is the template for
  shipping behind a flag if needed, though default-on is safe: no existing
  citation carries a paired quote today, so the new check verifies nothing
  until authors add quotes per the new rule.

- **Boundary** — `dispatch-hygiene-notes.md:113-119` is already
  anchor-primary and is the canonical source the rule points at; it needs no
  inversion, only to stop being contradicted. `check_contract_citations.py`
  has no overlap with this rule — it bans `docs/` path citations in contracts
  and only strips a trailing `:line` before classifying a path; it never
  verifies a line number.

## Decision

Invert the line-cite rule from line-number-first to anchor-primary across
every surface that states or consumes it, in one arc. The anchor — a verbatim
string or a stable heading — is the citation. A line number is optional
precision, required only when the anchor alone is ambiguous.

The mechanical checker gains substring verification as the primary check;
line-bounds stay as a secondary check when a line number is given. The
`distribute.py` SSOTs (`_reviewer-discipline.md` for the four reviewer
agents, `domain-teams` for `quality-gate.md`) collapse the blast radius: one
edit per SSOT propagates to its copies.

This is a strengthening, not a trade — the verification-cost question is
answered (substring search is cheap-tier, and the checker already reads the
file), and the rule's own cited authority already says anchor-first.

What we will NOT build: no retroactive flagging of existing line-only
citations in already-merged plans/specs. The checker verifies anchors that
are present; the rule text and the reviewers drive authors to add them. No
ban on line numbers — optional precision that disambiguates a repeated
string stays useful. No change to `check_contract_citations.py` or to the
debt-list exit condition parked in the parent bet.

## Alternatives Considered

Research was conducted in the parent bet entry (same day): no shipped system
uses line-number-primary with a live verifier; GitHub's permalink sidesteps
drift by freezing to a commit SHA; Sphinx `literalinclude` and mkdocs
Snippets verify quoted-string anchors at build time. The bet entry's survey
is cited rather than re-run — it is zero days old and recorded in the repo.

- **Keep line-first, strengthen the pairing duty.** The pairing duty already
  exists at `plan-format.md:298` ("Pair every such line cite with the verbatim
  string"), and the three defects still landed in the numbers. Pairing does
  not fix rot — it adds a second cite that the author must keep in sync with
  the number, and the number still rots. Rejected.
- **Freeze to commit SHA (the GitHub permalink model).** A plan cites
  working-tree files that change within the branch. A SHA points at a commit
  that predates the edit, so it cannot locate the post-edit line anyway; SHA
  is for cross-branch permanence, not in-branch navigation. Rejected.
- **Ban line numbers entirely.** A line number disambiguates an anchor whose
  string occurs more than once in a file. Banning it loses that precision and
  forces a longer quote where a number would do. Rejected — optional
  precision is kept.

## Out of Scope

- The debt-list exit condition parked in the parent bet entry (move the
  relocation target outside the checker's scope, or make
  `references/design-evidence.md` an exempt shape). That is a separate
  decision about the citation checker's scope, not about line numbers.
- Retroactive cleanup of existing line-only citations in merged plans/specs.
- `check_contract_citations.py` — no overlap with this rule.
- `dispatch-hygiene-notes.md` — already anchor-primary; needs no inversion.
- The repo split. This arc ships under the current monkey-skills structure.

## Queue relation

in-queue: 2026-08-22-line-cites-should-be-anchor-primary-across-the-loom-institutions

## Open Questions

N/A — the rule's boundary (anchor-primary, line optional, required when
ambiguous), the verification cost (cheap-tier substring search), and the
transition (checker verifies present anchors, does not retroactively flag)
were settled by the parent bet entry and the surface extraction. The
distribute.py SSOT chain was confirmed by reading the script.
