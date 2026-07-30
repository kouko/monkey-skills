# Brief: docs-review blocking class — only instruction defects gate a prose branch

- **Date**: 2026-07-30
- **Origin**: `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` §1 + §6b.
  Supersedes the (P1+P2) ledger slice as the next thing to build — that slice is
  PARKED in `docs/loom/BACKLOG.md` with an unpark condition tied to this one's
  outcome.
- **Status**: brief. The user ratified the shape ("純 A", no round budget) on
  2026-07-30 before it was written.

## Problem

The job: **let a documentation branch's review end.**

A review loop needs a termination oracle. Code has one — tests re-verify every
fix. Prose has none: `requesting-code-review/SKILL.md:97` says so in its own
words, "an unchanged line in a document is an untouched line, not a correct one —
documents have no tests."

0.40.0 gave documentation its own review *input* — whole-artifact scope, five
prose dimensions, a mechanical citation pre-pass. It did not give documentation
its own *decision function*. The aggregation rule at
`requesting-code-review/SKILL.md:172-181` is shared verbatim with code: any 🔴, or
**2 or more 🟡**, returns NEEDS_REVISION.

That shared rule mechanically explains the nine-round loop. Applying it to the
audit's own round table (§1) reproduces **every** verdict:

| round | findings | rule that fired | verdict |
|---|---|---|---|
| 1 | 4 🟡 | 2+ 🟡 | NEEDS_REVISION |
| 2 | 1 🟡 | exactly 1 🟡 | PASS_WITH_NOTES |
| 3 | 2 🟡 | 2+ 🟡 | NEEDS_REVISION |
| 5 | 3 🟡 | 2+ 🟡 | NEEDS_REVISION |
| 6 | 2 🟡 | 2+ 🟡 | NEEDS_REVISION |
| 7 | 1 🔴 + 1 🟡 | 🔴 | NEEDS_REVISION |
| 8 | 4 🟡 | 2+ 🟡 | NEEDS_REVISION |
| 9 | 1 🔴 | 🔴 | NEEDS_REVISION |

**Six of the eight blocking rounds were blocked purely by accumulated 🟡
warnings — none by a 🔴.** A prose reviewer scoring omission / ambiguity /
inconsistency / incorrect-fact / missing-population generates 🟡 findings
routinely, so on prose the 2+ 🟡 clause fires nearly every round, and each firing
triggers a rewrite that nothing re-verifies. The audit measured the consequence:
six of nine rounds found a defect introduced by the previous round's own
remediation.

The asymmetry is the whole argument. **Blocking code triggers a fix that tests
re-verify. Blocking prose triggers a rewrite that injects.** The same decision
function has opposite expected value on the two artifact types.

(Caveat, stated rather than hidden: the table above assumes those 🟡 findings were
evidence-class. The audit states this explicitly for round 8 — "four findings were
evidence defects in original text" — and describes rounds 1/3/5/6 as citation,
abridgement, and unswept-sibling issues, which are evidence-class. It is not
verified finding-by-finding.)

## Users

**When** I close out a documentation branch, **I want** the review to block only on
text that would misdirect someone acting on it, **so I can** ship with the
remaining observations written down instead of rewriting narrative prose for six
more rounds.

Specifically: the loom-code orchestrator running `requesting-code-review` (directly
or via `finishing-a-development-branch`) on a branch whose diff is all `.md`, and
the two `loom-code:code-reviewer` arms it dispatches.

## Smallest End State

Docs-only mode gains a **finding classification** that runs before aggregation.
Nothing else changes.

1. **Reviewers tag each finding** with `class: instruction | evidence`.
   - **instruction** — text a reader or executor will act on: a rule, a step, an
     acceptance criterion, a prescribed command or path, a citation used as an
     instruction. Getting this wrong misdirects work.
   - **evidence** — narrative claims about what happened or what is true: a
     measurement, an absolute, a provenance attribution, a citation supporting a
     claim. Getting this wrong makes the record less trustworthy; it misdirects
     no one downstream.
2. **The orchestrator applies the existing aggregation rule to instruction-class
   findings only.** Evidence-class findings are listed in the verdict as recorded
   observations with no veto.
3. **Recorded means recorded, not rewritten.** Evidence-class findings on settled
   narrative prose are appended as a correction naming what they supersede, never
   edited in place (ADR immutability, Nygard 2011 — an accepted record is
   superseded, not edited).

**No round budget, no numeric cap.** Convergence comes from the instruction class
being a finite set — the audit's §6b measured exactly this: round 7 (the first
whole-artifact round) found the instruction defect, round 8 "found **no**
instruction defects at all, and reported the class clean", and round 9
independently re-verified that the class was clean and it held. Rounds 8 and 9
blocked only on evidence defects.

**Retrodiction against the nine-round loop**: round 2 (PASS_WITH_NOTES, 1 🟡)
never blocked, with or without classification. Round 4 was a focused check that
carried no dimension scores (audit §3.3), so it sits outside this framework's
per-finding accounting. Rounds 1, 3, 5, 6 and 8 ship with their findings
recorded; round 7's 🔴 — a live bullet instructing an implementer to derive
`kpi_id` from a canonical field slug while the shipped code does the opposite —
is instruction-class by the definition above and still blocks. Round 9's 🔴 was
a repair written into only one of the two artifacts that carried the claim
round 8's remediation was meant to fix. The audit does not classify this
finding outright, but chaining §1 (round 9's finding source: "round 8's
remediation, applied to one of two artifacts") with §6b (round 8's four
findings "were evidence defects in original text") makes evidence-class the
supportable reading — an incompletely-applied repair to an evidence-class claim
is itself evidence-class, not a new instruction. On that reading, nine rounds
become roughly two, and the one genuine hazard round 7 caught is still caught.

## Current State Evidence

- **Forward** — `requesting-code-review/SKILL.md:97` adds the docs-only addendum to
  both dispatches when every file in `git diff main...HEAD --name-only` ends in
  `.md`; `:98` dispatches two byte-identical `loom-code:code-reviewer` arms; `:100`
  unions their findings and re-runs the aggregation rule on the union; `:172-181`
  is that rule.
- **Reverse (SSOT ownership — read from the distribution script, not inferred)** —
  the aggregation rule "aligned with `rubrics/quality-gate.md` §Verdict Rules"
  (`:172`), and `rubrics/quality-gate.md` is a **distributed functional copy** whose
  canonical version lives in `domain-teams:code-team`
  (`loom-code/scripts/distribute.py:87-88`), byte-diffed in CI by
  `verify-drift.py`. **Editing the aggregation rule from loom-code would create
  drift.** This brief therefore does not change it — classification happens
  *before* it, and the rule itself is untouched.
- **Error** — a verdict whose findings lack `where:` citations is malformed and
  flips to NEEDS_REVISION regardless of severity (`:175-176`); a new `class:` field
  must not weaken that, so a finding missing `class:` in docs mode fails closed
  (treated as instruction-class).
- **Data** — the verdict's `dimension_scores` block carries nine named dimensions
  (`:131-139`); docs mode substitutes five prose dimensions for the code-shaped
  ones at dispatch time without changing the schema. The `class:` tag is a
  per-finding field, not a dimension.
- **Boundary** — `requesting-code-review/SKILL.md` is at 3,930 words against
  CHK-SKL-010's 4,500-word hard cap (≈570 words of headroom) and already above the
  repo's ~3,750 soft target. This change must be small or must trade words out.
  `loom-code/scripts/test_docs_review_mode.py` guards the existing docs-mode text.

**Evidence paths**: `loom-code/skills/requesting-code-review/SKILL.md`,
`loom-code/scripts/distribute.py`, `loom-code/scripts/verify-drift.py`,
`loom-code/scripts/test_docs_review_mode.py`,
`loom-code/agents/code-reviewer.md`,
`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`.

## Alternatives Considered (Axis 4)

External research on this specific question is **thin** — a focused EN + JA round
found no literature on differential review rigor by artifact type beyond one weak
2009 CS-classroom peer-review paper noting that "different occasions support
different levels of inspection". What industry does ship is *structural* routing,
not judgment: GitHub rulesets support
[path-based approval rules with negation patterns](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
so matched paths need no approvals, `paths-ignore` on `**/*.md` skips CI, and
["require pull requests without requiring reviews"](https://github.blog/changelog/2021-11-09-require-pull-requests-without-requiring-reviews/)
is a supported mode. Two JA practitioner patterns match the shape:
[CyberAgent](https://developers.cyberagent.co.jp/blog/archives/60882/) runs only
light tests at PR time and defers heavy E2E until after approval;
[ZOZO](https://techblog.zozo.com/entry/ai-driven-dev-with-claude-and-devin) uses a
`skip-ai-review` label for explicit opt-out. Common shape: **tier the review, and
declare the tier mechanically** — which is what this brief does.

| Alternative | Retrodiction / evidence | Disposition |
|---|---|---|
| **Restrict which class may block** (this brief) | 9 rounds → ~2; the one live hazard still blocks | **Adopted** |
| Hard 1-round budget for docs branches | 1 round, but round 1 diff-scoped missed the instruction defect for six rounds in the real case — a 1-round budget could ship a live wrong instruction | Rejected — trades the only class that matters |
| Single-arm panel on docs branches | Halves findings per round; the 2+ 🟡 rule still fires. ~9 → ~6 | Rejected — does not address the unbounded loop. Also `Nine Judges, Two Effective Votes` (arXiv 2605.29800, preprint) finds panel diversity buys little independence, so arm count is not the lever |
| Mechanical checks only, no LLM panel on docs | The citation checker caught 8 bounds errors at 0% false positives, but audit §5 states plainly: "Neither found the hard defects (§2 needed judgement)" | Rejected — would ship the live wrong instruction |
| A separate docs-reviewer agent / separate skill | Audit §6b: detection was achieved "through dispatch text alone" in rounds 7-9. A second agent contract is a second drift surface — `docs/loom/memory/core-rule-removal-needs-plugin-wide-sweep.md` records one rule needing fixes across 14+ files | Rejected — fork the decision function, not the reviewer |
| Change the aggregation rule for docs mode | `rubrics/quality-gate.md` is a distributed functional copy (`distribute.py:87-88`) — editing it from loom-code is drift by construction | Rejected — classify before the rule instead of changing it |

**My take**: tag findings by class in the docs-mode dispatch, and filter what
reaches the existing aggregation rule. **Why**: it is the only option that both
kills the unbounded loop and keeps the one defect class that caused real harm; it
changes no shared SSOT; and it needs no new agent, dimension, or script.
**Conditional reversal**: if a prose branch ships an instruction defect that a
reviewer had tagged `evidence`, the class boundary is wrong — fix the boundary
definition, and if it cannot be made reliable, fall back to a 2-round budget on
the whole docs path rather than re-widening the veto.

## Decision

In `requesting-code-review`'s docs-only mode: require a `class: instruction |
evidence` tag on every finding, apply the existing aggregation rule to
instruction-class findings only, present evidence-class findings as recorded
observations, and require evidence-class findings on settled narrative prose to be
superseded rather than edited in place. Fail closed on a missing `class:`.

Do **NOT** build: any change to `rubrics/quality-gate.md` or the aggregation rule
itself; any change to code-branch review behaviour; a new reviewer agent, skill, or
dimension; a round budget or numeric cap; any change to panel width; the parked
ledger slice.

## Out of Scope

- The parked (P1+P2) ledger slice and its sub-items (see `docs/loom/BACKLOG.md`).
- Mixed branches (some `.md`, some code). The docs-only trigger at `:97` already
  keeps them on the code path unchanged, and the second pathological loop was a
  mixed branch — so this brief does **not** claim to fix that case. Stated, not
  hidden.
- Diátaxis-style corpus restructuring; deriving doc claims from code.
- Whether the same unbounded loop can occur on a code branch — untested, per audit
  §7.

## What Becomes Obsolete

- The unbounded docs review loop.
- Audit §3.2's convergence-criterion proposal, for the docs path — resolved here by
  restricting the veto rather than by measuring rounds.
- Most of the parked ledger slice's justification, if this works. The BACKLOG entry
  already carries the unpark condition and the close-instead condition.

## Open Questions

1. **Where the `class:` tag is required.** Options: the docs-mode dispatch text
   only (smallest, no agent-contract change), or the verdict-structure section as a
   conditional field. Leaning: dispatch text plus one line in §Verdict structure
   marking it docs-mode-only, so `loom_gate_markers.py`'s schema validation is
   untouched.
2. **Whether the boundary needs a worked example per class.** The repo's standing
   finding is that a term a weak reader must guess is a defect
   (`docs/loom/memory/doc-string-tests-pass-while-weak-readers-misread.md`).
   Leaning: yes — one instruction example and one evidence example, both drawn from
   the audit's real findings, which costs ~40 words.
3. **Word budget.** At ~570 words of headroom, this change plus two examples
   probably fits, but if it does not, which existing paragraph trades out is a
   plan-time decision — not an append.

## Design-side on-ramp

N/A — process tooling for loom-code itself; Axis 0 negative guard (incremental,
non-product-shaped) applied.
