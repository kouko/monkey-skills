# Research question 3 — What capability boundary is actually unsupported?

## Goal

Identify the unmet outcome without presuming that a new `loom-docs` plugin is
the required mechanism.

## Method

- Compare existing ownership across `docs-team`, `requesting-docs-review`,
  strategy formation, and proposal critique.
- Identify which observed needs lack a stable owner or evidence loop.
- Check external engineering guidance on automated pre-review checks and human
  judgment.

## Findings

### Document production and document judgment already have owners

`domain-teams:docs-team` covers technical document production and its own gates.
`loom-code:requesting-docs-review` covers branch-level contract prose review.
Strategy formation and proposal critique live in separate toolkits (C15).
Therefore, “write technical, business, and strategy documents” is not itself an
unserved capability.

### The unsupported outcome is causal feedback across the lifecycle

No durable evidence chain currently answers:

- which stage introduced each defect;
- which check found it and at what cost;
- whether a fix closed the population rather than one named line;
- which defect classes escaped to later stages;
- whether a contract change improved cost or quality over a stable corpus.

The absence is evidenced by the historical reconstruction limit (C9), not by a
missing writing protocol.

### External practice supports separating deterministic checks from judgment

English engineering guidance places automatable checks before human review and
keeps later assurance for judgment that automation cannot replace (C13).
Japanese SI-document research similarly treats guideline-conformance automation
as review support in a domain where ambiguity and reviewer dependence remain
hard (C14).

## Insight skeleton

- Need: make document quality an observable lifecycle rather than a terminal
  reviewer verdict.
- Evidence: C7–C9, C13–C15.
- Current workaround: add reviewer clauses, scripts, and audits after individual
  failures, without a shared outcome ledger.
- Open solution question: whether this belongs inside existing Loom owners, in a
  small shared layer, or in a separate plugin must be decided downstream.
