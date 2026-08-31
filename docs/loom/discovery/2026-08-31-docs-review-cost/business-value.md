# Business value — docs-review-cost

Date: 2026-08-31
Verdict: NO-GO

> Register: Shape-Up betting — is a broad `loom-docs` plugin worth the time
> budget now? This is not a market-size or revenue judgment.

## Why now

Document review has been the largest perceived development cost, and the core
reviewer contracts have continued to change after several dedicated convergence
audits. The cost is real, but current records cannot quantify the latest flow's
cost or isolate its dominant source (`evidence.md` C1–C9).

## Why me

The maintainer controls the full Loom authoring, review, and release pipeline and
has unusually rich local incident evidence. That makes this repository able to
test process changes against its own hard cases rather than adopting generic
documentation doctrine.

## Opportunity cost

No competing project was named. The continuing cost is therefore the maintenance
burden created by any new plugin boundary: another router, manifest, release
surface, cross-plugin composition contract, and duplicated ownership decisions.
The absence of a competing commitment weakens the time-budget claim rather than
making the work free.

## Business complexity

**Continuing burden:** a broad plugin spanning technical documentation, business
analysis, and strategy would require several distinct truth standards and would
overlap current owners (`evidence.md` C15). Maintainers would have to coordinate
routing and review authority across those boundaries.

**Worth:** the observed needs N1–N3 are valuable, but they concern attribution,
signal calibration, and earlier prevention—not a new document-production brand.

**Avoidance:** improving evidence and prevention at existing lifecycle stages can
avoid another top-level orchestrator while preserving current specialist skills.

**Downstream risk:** without telemetry, reorganizing first would make before/after
comparison impossible and could hide the same reviewer behavior behind a new
name.

## Evidence consulted

- [`evidence.md`](evidence.md) and the three reports under [`research/`](research/).
- Existing owners: `domain-teams:docs-team`,
  `loom-code:requesting-docs-review`,
  `systems-thinking-toolkit:strategy-lever-and-cascade`, and
  `loom-workflow:proposal-critique`.
- EN and JA primary/authoritative sources listed as C10–C14.

## Recommendation

**NO-GO**

Do not build the proposed broad `loom-docs` plugin now. The evidence supports a
documentation-quality problem, but not a missing omnibus documentation product.
First serve N1–N3 through a bounded, measurable quality campaign at the existing
authoring and review stages. Reconsider a separate plugin only if that work
demonstrates a stable cross-plugin responsibility that cannot have one existing
owner without duplication.
