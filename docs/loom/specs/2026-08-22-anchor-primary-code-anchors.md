# Brief: make anchor-primary citations concrete for code and configuration

Date: 2026-08-22

## Design-side on-ramp

not fired — a clarification to existing loom author and reviewer contracts;
it adds no product surface or interaction design.

## Problem

The anchor-primary rule says to cite a verbatim string or stable heading, but
does not explicitly say what counts as a good anchor in source code or
configuration. A reader can reasonably interpret “stable heading” as prose
only and fall back to line numbers for code.

## Users

Plan and brief authors, and reviewers writing findings against code,
configuration, and prose. A weaker model is the calibration target: it should
choose a program structure or distinctive literal without being coached in the
test prompt.

## Smallest End State

BI-1 — The brief author format and plan stated-facts format name anchors by
artifact type: prose uses a stable heading or distinctive phrase; code uses a
function, class, method signature, constant, or distinctive message; config
or data uses a key path plus distinctive value fragment.

BI-2 — Reviewer R2 carries the same compact guidance through its existing
SSOT propagation path, and the brainstorming entry no longer teaches
`file:line` citations.

BI-3 — Regression tests lock the positive examples and reject the retired
line-primary instruction.

BI-4 — A weak-model cold-read dogfood prompt asks for evidence citations from
a small mixed prose/code/config fixture; its recorded result shows whether the
new guidance is applied without extra explanation.

## Current State Evidence

- **Forward** — `handoff-brief-format.md` “Each citation requires a path
  paired with an anchor” and `plan-format.md` “Any verifiable technical
  assertion” define author behavior, while `_reviewer-discipline.md` Rule R2
  defines reviewer behavior.
- **Error** — `brainstorming/SKILL.md` currently retains `file:line` in its
  Current State Evidence output contract, contradicting the anchor-primary
  format it points to.
- **Data** — `check_doc_citations.py` accepts a quoted anchor in code files
  and verifies it as a verbatim substring; the missing piece is instruction,
  not parser capability.

## Decision

Add one compact artifact-type example set to each existing canonical author
and reviewer rule, without new syntax or a new guidance file. Correct the
brainstorming entry's retired wording. Test the text structurally, then run a
weak-model cold-read dogfood probe against a fixed fixture and record its
verdict.

## Alternatives Considered

- Add only a prose sentence saying “code works too.” Rejected: it leaves the
  choice of a useful code anchor ambiguous.
- Create a new citation-guidance file. Rejected: it creates another consumer
  and propagation surface for a small clarification.
- Teach examples in every README. Rejected: the canonical author and reviewer
  rules already own the behavior; broad copying would recreate drift risk.

## Out of Scope

- AST-aware citation verification.
- New citation syntax or changes to `check_doc_citations.py`.
- Retroactive rewriting of merged citations.

## Queue relation

unqueued — follow-up clarification shipped within the already-selected
anchor-primary branch, rather than as a separate backlog commitment.

## Open Questions

N/A — the artifact categories and dogfood acceptance criterion are settled.
