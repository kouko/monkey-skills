# Brief: the code-as-spec lens may not declare itself a no-op

Date: 2026-08-22
Author: kouko (session), after an independent assessment overturned this brief's first recommendation

## Design-side on-ramp

not fired — a defect fix to shipped reviewer-contract text, found by measurement; no product-shaped or user-facing surface

## Problem

When a reviewer holding the code-as-spec lens meets a diff that adds
docstrings or comments, I want the surplus-prose half of the rule to
either fire or visibly fail, so that a review round that skipped it does
not read exactly like a review round that ran it and found nothing.

## Users

The `loom-code:code-reviewer` and `loom-code:docs-reviewer` agents, at
whatever tier the session runs, on every branch this repo closes. They
hold the contract in an injected system prompt, have no memory of prior
rounds, and are read by a human who sees only the verdict block — a
dimension scored PASS with no findings and a dimension never examined are
indistinguishable to that reader.

## Smallest End State

One sentence added to the lens in each agent contract, barring the reviewer
from declaring the lens not applicable, out of scope, or a no-op — each stated
in that arm's own terms, because the two arms govern different material and
score different dimensions. Plus the version bump that puts it in force, and a
re-run of the existing sandbox to see whether the route it targets is actually
closed.

BI-1 — the no-op bar, in `loom-code/agents/code-reviewer.md` §D10.

BI-2 — the same bar in `loom-code/agents/docs-reviewer.md`, stated in that
arm's own terms rather than mirrored word for word: it governs contract-class
prose and has no `deletion-first` dimension, so the bar there names `omission`
and the lens itself. Literally mirroring the code arm's sentence ships a
dangling referent, which is what the first attempt did.

BI-3 — a test pinning both arms, whitespace-flattened and per-arm, covering
the prohibition itself and not only its headline clause.

BI-4 — the version bump across its five coupled sites.

BI-5 — a re-run of the dogfood arms against the unchanged sandbox, with the
transcripts retained this time, whatever the outcome.

## Current State Evidence

- **Forward** — the deletion duty enters at role-contract item 7
  (`loom-code/agents/code-reviewer.md`, role-contract item 7) and expands at §D10's
  `##### Code-as-spec lens`. Its findings file at 🟡
  (the lens's "File every finding as `dimension: deletion-first` … at **🟡 should-fix**" sentence).
- **Reverse** — the mirror is rule 8 plus `## Code-as-spec lens` in
  `loom-code/agents/docs-reviewer.md`, role-contract rule 8. Neither file is inside a
  `distribute.py`-managed region; the lens sits in the hand-authored
  sections. Confirmed before editing, because the managed regions are
  byte-compared in CI by `verify-drift.py`.
- **Error** — the failure this fixes is silent by construction: deployed
  arm 1 scored `deletion-first: PASS` and listed the dimension among
  "no-ops for this branch" without enumerating a sentence
  (`docs/skill-dogfood/2026-08-22-code-as-spec-reviewer-lens/transcripts/deployed-arm-1.md`).
- **Data** — deletion class across five samples of the new contract:
  `1/2, 2/2, 0/2, 0/2, 2/2`, against `0/4` on the old contract
  (`docs/skill-dogfood/2026-08-22-code-as-spec-reviewer-lens/README.md`
  §Results).
- **Boundary** — the version pin lives in five coupled places:
  `loom-code/.claude-plugin/plugin.json` `version` field,
  `loom-code/.codex-plugin/plugin.json` `version` field, the `## [0.93.0]` heading in
  `loom-code/CHANGELOG.md`, `test_plugin_version_and_changelog_at_0_93_0`'s name, its two assertions
  and its docstring in
  `loom-code/scripts/test_docs_review_blocking_class.py`, and Check 19's
  `(vX.Y.Z+)` tag in `plan-document-reviewer-prompt.md`, which
  `test_check19_version_tag_matches_shipping_version` binds live to
  `plugin.json`.

## Decision

Add the no-op bar to both contracts and nothing else. The bar is an
availability rule, not a new judgment: it does not tell the reviewer what
counts as surplus, add a carve-out, or require an artifact — it removes one
specific escape, the one a transcript shows was taken.

What we will NOT build: an artifact duty. This brief opened by recommending
that the deletion half emit a per-sentence classification table before the
dimension could be scored, reasoning that the execution half works because
it demands a produced outcome while the deletion half asks only an internal
question.

An independent assessment overturned that on evidence already in this
repository. The contract ALREADY carries a prose-demanded enumeration duty
two paragraphs above the lens — "Operational check — execute this, don't
only reason narratively: (a) enumerate each NEW abstraction…"
(`loom-code/agents/code-reviewer.md` §D10's **Operational check** paragraph) — and the arm that declared
the lens a no-op sailed past that duty too.

A prose enumeration requirement has therefore already been tested here, and
skipped. Adding a second one, at higher per-branch cost, would be the same
genre of fix with a story attached about why this one is different.

Two further findings kept the scope this small. The deletion half has never
changed a verdict in seven recorded runs — its findings are 🟡 and every
NEEDS_REVISION came from the 🔴 correctness route. And the transcript of the
run that reached zero by invoking the carve-outs was never retained, so any
design aimed at that route would be designed against a record nobody can
open; BI-5 exists partly to stop that recurring.

## Alternatives Considered

- **Require an artifact (per-sentence classification table).** Rejected on
  the evidence above — the precedent for prose-demanded enumeration in this
  same file is that it gets skipped.
- **Delete the deletion half entirely**, keeping the execution half and
  moving surplus-prose removal to authoring time. Defensible; it catches
  something 2 times in 5, so deleting it forfeits real value. Held.
- **Change nothing and rely on the two-reviewer union.** The union is the
  shipped mechanism and it did recover the miss in the deployed run. From
  five samples the pair still misses at least one planted item in roughly
  30% of pairs. Not chosen, but the gap it leaves is 🟡-only.
- **A mechanical pre-pass script.** No mechanical detector for prose
  redundancy ships anywhere — not ESLint, Pylint, Ruff, or SonarQube; the
  research line on comment/code inconsistency (iComment SOSP 2007,
  @tComment ICST 2012, Panthaplackel et al. AAAI 2021) targets FALSE
  comments, which is the half already working. Ours would be a keyword
  heuristic wearing a mechanical costume.

## Out of Scope

- The record-class gap — `docs/**` prose is gated by nobody. Named in the
  source arc's brief as accepted debt; unchanged here.
- Any change to the execution half, which measures 6/6.
- The deferred A/B on whether the writing rule extends to skill bodies. It
  runs next, from its own backlog entry, and is a separate arc.
- Re-sampling to settle the deletion class's magnitude. Five samples showed
  the spread widening, not converging.

## Queue relation

unqueued — a one-line fix to shipped rule text, surfaced by the deployed
dogfood run; the queued item is the A/B that follows it

## Open Questions

N/A — no unresolved question: the fork was briefed, independently assessed,
overturned, and decided by the user in favour of the narrow bar plus the A/B.
