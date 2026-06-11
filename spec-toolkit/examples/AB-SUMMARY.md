# A/B dogfood — cross-seed summary (4 seeds)

> **Date**: 2026-06-11
> **Design**: per seed, two mutually-blind subagents — Arm A (spec-toolkit: spec-expansion 3-phase + completeness-critic) vs Arm B (a capable model's unaided one-shot brainstorm). Orchestrator diffs. Tests caveat (a) from the first run: *does the scaffold win where the model's priors are thinner?*
> **Seeds**: `password-reset` (security-canonical), `table-merge` (POS), `subscription-pause` (SaaS billing), `stock-reservation` (inventory).
> All 4 Arm-A outputs pass `validate_spec_output.py` (exit 0): 5 visible sections, non-empty blind spots, OpenSpec-pure delta with GIVEN/WHEN/THEN scenarios.

## Per-seed recall verdict (did Arm A catch omissions Arm B missed?)

| Seed | Domain prior density | Recall verdict | Arm A's distinctive catches | Arm B's distinctive catches |
|---|---|---|---|---|
| password-reset | very high (security textbook) | **INCONCLUSIVE** | MFA-vs-reset | token-in-URL leakage, email normalization, CAPTCHA, lost-email dead-end |
| table-merge | medium | **MARGINAL (slight A)** | PCI on captured tenders, KDS re-label network failure, chained-merge cycle guard, "merge is a Check op not a Table op" | N-way vs pairwise, cross-revenue-center, loyalty-member conflict |
| subscription-pause | high (well-documented SaaS) | **TIE / baseline-edge** | consumer-protection re-consent, cron-lag resume SLA | MRR/churn metrics, DST/TZ + leap-year, chargeback, price-grandfather on resume |
| stock-reservation | lower / deep object graph | **MODERATE (clear A edge)** | Allocation≠Reservation, ASN/Lot/Bin/Kit objects, FEFO/FIFO, lot-recall clawback, dual-write OMS/WMS, event-bus replay double-decrement, short-pick priority | core 3-quantity model, consistency-model-reintroduces-oversell |

## The actual pattern (refines caveat (a))

The scaffold's recall edge does **not** track "canonical vs bespoke" — it tracks **domain object-structure depth**:

- Where the domain is a **well-documented pattern** (security auth, SaaS billing), a capable model's free brainstorm is *already* near-exhaustive → scaffold edge ≈ zero or negative. subscription-pause is "bespoke business logic" yet the baseline matched/beat Arm A, because pause/billing is a heavily-blogged SaaS pattern.
- Where the domain has a **deep, less-uniformly-documented object graph** (inventory: allocations, ASNs, lots, bins, kits, ledgers), the **OOUX per-object fan-out + the matrix surfaced structure the free brainstorm flattened** → Arm A's clearest win.

So the honest refinement: **spec-toolkit earns its recall keep in deep-object-structure domains, not "non-canonical" ones per se.** The lenses help most when there are many objects × states to sweep mechanically.

## The domain-independent finding (consistent across all 4)

Two things held on **every** seed, regardless of recall:

1. **Verification-ready output.** Arm A always produced testable `#### Scenario:` GIVEN/WHEN/THEN acceptance criteria (16–21 per seed) → directly consumable by `code-toolkit:writing-plans` as RED/GREEN. Arm B always produced a prose list — thorough but **not** TDD-ready.
2. **Enforced, tagged honesty.** Arm A always emitted a non-empty, structured `## Blind spots — needs human/field input` naming the human/field source per item, plus seeded/inferred/critic-found provenance. Arm B's "open questions" overlapped in content but were unstructured and untagged.

## Bottom line for the bet

- **Recall superiority: WEAKLY supported, domain-dependent, never dramatic.** Across 4 seeds the scaffold ranged from slightly-behind to moderately-ahead on omissions; it never decisively beat a capable baseline. The A/B-baseline lesson holds: a strong model brainstorms well by instinct.
- **Structural value: STRONG and consistent.** Verification-ready scenarios + enforced blind-spots/provenance are real, one-directional advantages the baseline never provides — independent of domain.
- **Implication**: position spec-toolkit's value as **"structured, verification-ready, honestly-tagged spec output"** (reliable) — and as a **recall aid specifically in deep-object-structure domains** (situational) — NOT as a general "finds more than you would" tool (unproven).

## Recommended next step (decision for kouko)
1. **Re-position** the brief/README around the structural value + the deep-object-structure recall niche (drop any "finds more omissions" framing). Then it's a defensible, honest MVP worth shipping.
2. **Or park** — the build-to-learn goal is met; the finding is recorded; expand only if a deep-domain use case bites.
3. Either way: **do not expand to the full 5-skill pipeline on a recall argument** — the recall case is not strong enough to justify it. Expand on the *structural/verification-readiness* argument if at all.
