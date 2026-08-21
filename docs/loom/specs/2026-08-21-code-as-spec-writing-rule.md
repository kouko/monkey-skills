# code-as-spec writing rule — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-21
> **Author**: agent (discovery ran in the prior session; decisions frozen in that session's handoff Block 5, with kouko present for every one)

## Design-side on-ramp

not fired — negative guard: this arc is a refactor plus a test-covered increment over existing scripts and agent prose; no user-facing surface, no new product-shaped object

## Queue relation

unqueued — the arc was born from the `dissolve-direction-layer` close-out research, not from a queue entry; the related entry `2026-08-21-checkers-for-load-bearing-superlatives-and-existence-claims` is `status: open`, not `bet`, so it cannot be cited by `in-queue:`

## Problem

When a reviewer reads a sentence in this repo's prose that describes a mechanism, they cannot tell whether the sentence is still true without re-deriving it from the code — and eight review rounds on `dissolve-direction-layer` proved they mostly do not. I want prose whose claims a reader cannot silently mis-verify, so I can stop spending review rounds on sentences instead of on behaviour.

## Users

- **Whole-branch reviewers (`loom-code:code-reviewer`, `loom-code:docs-reviewer`, human)** — read a diff without the author's design intent in working memory; today they must re-derive every mechanism sentence's truth from the code, and rounds 5–8 of the source arc show they do not.
- **The next author of a gate script** — reads a sibling script's docstring to learn the family's conventions; today they inherit sentences that restate a code shape which has since moved.
- **Agents executing skill and agent prose** — bound by contract-class `.md` (skills, agents). NOT in scope for this arc: whether their behaviour survives losing a mechanism sentence is untested, and is what the deferred A/B exists to measure.

## Smallest End State

Four artifacts change and nothing else does. The recorded recommendation for this defect class matches what was actually decided; the six gate scripts' prose states only what their code cannot; the branch reviewer carries the rule as a per-sentence lens with its coverage limit stated; and the two capability claims that currently live only in an ephemeral scratchpad are asserted by standing tests. Success criterion: the full suite passes and every changed prose claim is either un-derivable from the code or pinned by a test. Explicit non-criterion: this arc does NOT measure whether agent behaviour survives the rule — no skill body is touched.
<!-- narrative: the criterion and the non-criterion only mean anything against the four-artifact scope stated in the opening sentence — split apart, "the full suite passes" reads as a claim about the whole repo and the non-criterion loses the scope it is excepting from -->

- BI-1 — The superseded backlog entry records the code-as-spec writing rule and the deferred A/B design in place of the dropped Checker 1 and the demoted Checker 2.
- BI-2 — The six gate scripts' docstrings and comments state the reason, the goal, the expected effect, the bounds, and how the implementation choice was made; sentences restating structure, counts, branches, or call sites are deleted, and a rationale is added only where a record already carries it.
- BI-3 — Each review arm's agent contract carries the reviewer lens for the rule, scoped to the material that arm actually receives, and states in the same edit which document classes it does not reach.
- BI-4 — The oracle's two capability claims — that it kills every guard mutant in its family, and that it catches every reviewer-found escape shape — are asserted by standing pytest tests.

## Current State Evidence

- **Forward**: The six scripts' prose is read by reviewers and by the next gate author, never executed — `loom-code/scripts/backlog_index.py:10`, `check_north_star_link.py:25`. No agent dispatch reads a script docstring, so BI-2 cannot change runtime behaviour.
- **Reverse**: `loom-code/agents/code-reviewer.md` is dispatched by `loom-code/skills/requesting-code-review/SKILL.md`. Three regions of that file are machine-managed — `reviewer-discipline-v1` (`code-reviewer.md:46-130`), `rule-sheet-v1` (`:132-177`), `baseline-v1` (`:179-294`) — rebuilt by `loom-code/scripts/distribute.py` and byte-compared in CI by `loom-code/scripts/verify-drift.py` (`.github/workflows/loom-code-ci.yml:104`). Rule 9 (`:248-251`) is the nearest rule in shape but sits INSIDE `baseline-v1`; the hand-authored `## Role contract — behavioral rules` list (`:14-45`) is where a per-file behavioural rule lands. The output contract (`:341-402`) fixes the `dimension_scores` key set and the aggregation rule over it; `loom-code/scripts/loom_gate_markers.py:872-873` checks only that the block is present, not its keys, so nothing mechanical would catch a new key — which is exactly why the lens must not become one: a new dimension is a schema change to the reviewer's output that every consumer of the verdict would have to learn, and nothing would tell them.
- **Error**: `N/A — not error-path code.` The oracle's own contract (`test_gate_scripts_fail_loud_on_unreadable_input.py:19-21`) and its assert messages (`:237-247`) are both left to BI-2's judgment, not pre-decided here.
- **Data**: The promoted tests read the four FAMILY scripts' source and the oracle's own `leaky_scopes()` / `EXEMPT` symbols (`test_gate_scripts_fail_loud_on_unreadable_input.py:276-398`, `:90-118`). The scratchpad probes mutate the real repo files in place and restore them; the promoted form must not. Running the whole oracle as a subprocess against a `tmp_path` copy is NOT a substitute: `test_exempt_leak_count_matches_the_filed_ledger` resolves its ledger via `SCRIPTS.parents[1]` (`:490`), which does not exist under a copied directory, so the oracle always exits non-zero there and every mutant reads as killed. The production assertion of the AST leg is `leaky_scopes(source) & {"main", "<module>"}` (`:402-417`); calling it in-process on mutated source text is the exact check, not a proxy. The classification leg skips `test_*` files (`:438-442`), so a new test module needs no `EXEMPT` entry.
- **Boundary**: `[FRAGILE]` The source probes splice text into `check_north_star_link.py` at a verbatim anchor (`"def find_offending_entry("`) — an anchor that rots on the next edit of that file. The promoted form must not depend on it.
- **Evidence paths**:
  - `loom-code/scripts/backlog_index.py:10`, `:11-15`, `:46-50`, `:238-263`, `:279-293`, `:464-475`, `:520-529`, `:632`, `:649-650`, `:664-677`, `:724-725`
  - `loom-code/scripts/check_queue_relation.py:1-9`, `:19-24`, `:50-51`, `:62-84`, `:161-164`, `:229-233`
  - `loom-code/scripts/check_north_star_link.py:13-29`, `:51-64`, `:92-101`, `:108-140`
  - `loom-code/scripts/check_onramp_choice.py:15-19`, `:71-77`, `:90-95`, `:139-144`, `:180-189`, `:300-305`
  - `loom-code/scripts/archive_change_folder.py:7-14`, `:48-80`, `:121-127`, `:174-198`, `:211-245`, `:259-272`, `:320-329`, `:375-380`, `:428-432`
  - `loom-code/scripts/test_gate_scripts_fail_loud_on_unreadable_input.py:3-27`, `:46-61`, `:81-89`, `:251-253`, `:276-398`, `:401-436`, `:454-494`
  - `loom-code/agents/code-reviewer.md:248-251`, `:449-472`
  - `docs/loom/backlog/2026-08-21-checkers-for-load-bearing-superlatives-and-existence-claims.md` (whole file)
  - `docs/loom/backlog/README.md:7-20` — the format SSOT; `docs/loom/BACKLOG.md:3` is a generated file and is NOT the SSOT
  - `docs/loom/plans/2026-08-21-dissolve-direction-layer.md:928-954` (DL-32), `:1026-1047` (DL-35)

## Decision

We ship the rule's zero-risk and low-risk layers and defer its direction-changing layer. Prose may state what the code cannot show — intent, invariants, bounds, trade-offs, rejected alternatives; prose may not restate what the code does show — structure, counts, branches, call sites. Losing the restatement is only half the rule: prose must carry the reason, the goal, the expected effect, and how the implementation choice was made — sourced from a Decision Log entry, a memory file, or git history, never invented, and left unwritten with the gap reported when no source carries it. That line is applied to script docstrings (where no behaviour depends on the outcome), recorded as a reviewer lens in BOTH review arms — each scoped to the material that arm is actually handed — and backed by the two tests that make the source arc's oracle claims executable. We do NOT touch any skill body. The trade-off: the lens reaches contract-class `.md` through the docs arm and non-`.md` docstrings and comments through the code arm, and reaches record-class documents through neither, so the class where several of the source arc's defects actually landed stays ungated — accepted deliberately, because closing it means changing how skill prose is written, and that rests on an untested assumption.
<!-- narrative: each sentence is the reason the next one is safe — the rule's line licenses the three placements, the placements are what bound the blast radius, and the bounded blast radius is what makes the stated coverage gap an acceptable trade rather than an oversight -->

- BI-5 — The rule is applied where its blast radius is zero or reversible, its known coverage gap is stated rather than papered over, and the deferred layer is left to a pre-designed experiment.

## Out of Scope

- Rewriting any skill body (`loom-code/skills/*/SKILL.md`) to drop mechanism sentences — the deferred layer; blocked on the A/B.
- Running the A/B experiment itself — a separate step after this PR merges.
- Building either checker from the superseded entry. Checker 1 is dropped; Checker 2 is demoted to "extend `check_doc_citations.py`" and stays filed, not built.
- Wiring `check_doc_citations.py` into CI so code-arm branches reach it — filed separately; it would not have caught any of the source arc's eight defects.
- Extending the reviewer lens to generated documents (backlog entries, plans) — the stated coverage gap; recorded as debt in this PR, not closed by it.
- A standalone chain-of-thought page recording how eight review rounds produced this rule — genuinely valuable, and the reasoning currently survives only in this brief and the plan's Notes; deliberately left to a follow-up rather than widened into this arc.
- Mermaid decision diagrams inside the changed artifacts — the repo's own visual routing sends option comparisons to a table, which `## Alternatives Considered` already is, and a three-node diagram is a sentence.
- Promoting `measure_exempt.py` or `probe_ast.py` — their assertions already live permanently inside the oracle as `exempt_leaks` plus `test_exempt_leak_count_matches_the_filed_ledger`, and as `leaky_scopes` itself, in `test_gate_scripts_fail_loud_on_unreadable_input.py`; re-asserting them would be duplicate coverage. Cited by symbol, not line: this arc's own docstring pass shifted every line number in that file after the citation was written.

## Alternatives Considered

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| RFC 2119 keyword discipline (MUST / SHOULD / MAY) | IETF RFC 2119; deployed form is Vale / textlint | Back-tested 0/8 against the source arc's own findings — it disambiguates obligation strength, and every defect here was a factual claim stated confidently and wrong |
| Checker 1 — a load-bearing superlative must carry a pin | The superseded backlog entry, this repo | Judgment-type, high false-positive rate; its 4/8 back-test over-fitted, since the historical measurement found superlatives are not a dominant sub-kind |
| Checker 2 — an existence claim must be a resolvable path | Same entry; partially realized as `loom-code/scripts/check_doc_citations.py` | Back-tested 1/8. Not rejected outright — demoted to "extend the existing checker", and left filed |
| `/opsx:verify` style spec↔code check | OpenSpec | Its own docs state it "does not block archive, but surfaces issues" — advisory, so it cannot stop the loop this arc is trying to stop |
| Apply the rule to skill bodies now | The user's own proposal, layer 2 | Strongest back-test (6–7/8) but rests on an untested assumption about weak-model agent behaviour; deferred to the A/B rather than rejected |

## What Becomes Obsolete

- BI-6 — The superseded recommendation in `docs/loom/backlog/2026-08-21-checkers-for-load-bearing-superlatives-and-existence-claims.md` — deleted in this PR by rewriting the entry.
- BI-8 — The `_FS_CALLS` rationale carried twice inside the oracle (`test_gate_scripts_fail_loud_on_unreadable_input.py:46-50` above the `frozenset`, `:57-61` inside it) — one copy deleted in this PR. (BI-7 retired: it also claimed the module-docstring contract was restated in the assert messages; verification found the two serve different readers — a reader's contract versus an operator's failure message — so that item is a judgment call inside BI-2's docstring pass, not an obsolescence.)

## Open Questions

N/A — no unresolved question: the three forks this arc reached (scope of the probe promotion; whether to close the reviewer-lens coverage gap now; whether to fix the duplications in this PR) were each put to kouko and answered in this session — promote two probes, state the gap and file it as debt, fix the duplications here.

## Diagrams

N/A — no flow/state/architecture-shaped content: the arc is four independent edits to four artifacts with no shared runtime path, no state machine, and no new component boundary; the dependency shape is carried by the plan's own task-flow diagram.
