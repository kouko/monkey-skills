# A/B dogfood — cross-seed summary (7 seeds)

> **Date**: 2026-06-11
> **Design**: per seed, two mutually-blind subagents — Arm A (loom-spec: spec-expansion 3-phase + completeness-critic) vs Arm B (a capable model's unaided one-shot brainstorm). Orchestrator diffs. Goal: test whether the scaffold's omission-recall beats a strong baseline, and where.
> All 7 Arm-A outputs pass `validate_spec_output.py` (exit 0): 5 visible sections, non-empty blind spots, OpenSpec-pure delta with GIVEN/WHEN/THEN scenarios.

## Per-seed recall verdict (7 seeds)

| Seed | Domain | Object-graph depth | Textbook-documented? | Recall verdict |
|---|---|---|---|---|
| password-reset | security auth | medium | **very** | INCONCLUSIVE |
| table-merge | restaurant POS | medium | partly | MARGINAL (slight A) |
| subscription-pause | SaaS billing | medium | **very** | TIE / baseline-edge |
| stock-reservation | inventory ops | **deep** | **no** (fragmented) | **MODERATE (clear A)** |
| rbac-roles | authorization | **deep** | **very** | TIE / baseline-edge |
| revenue-split | accounting/ledger | **deep** | **very** (double-entry) | TIE |
| shift-scheduler | workforce/rostering | **deep** | **no** (jurisdiction-specific) | **MARGINAL–MODERATE (A)** |

## The refined pattern (this is the real finding)

Object-graph depth **alone does not predict** the scaffold's edge — three deep-object domains (rbac, revenue-split) tied. The discriminator is **deep object graph AND thin/fragmented model priors**:

- **Textbook domains** (auth, RBAC, double-entry accounting, SaaS billing, security) → a capable model's free brainstorm is already near-exhaustive **even when the object graph is deep** → scaffold edge ≈ zero. RBAC is object-deep *and* textbook → baseline matched/beat Arm A (it independently flagged cross-workspace leakage as top-severity, plus circular nested roles, ReBAC, service-account principals).
- **Operational domains with fragmented real-world structure** (inventory: allocations/ASN/lots/bins/kits; workforce: demand-forecast coupling, fair-workweek notice clocks, relational two-person coverage, joint-employer hours) → the OOUX per-object fan-out + matrix surfaced structure the free brainstorm flattened → Arm A's only clear wins (stock-reservation, shift-scheduler).

**The honest discriminator: loom-spec earns recall keep only where the domain is BOTH object-deep AND not-well-trodden.** That is a narrow niche, and even there the edge was "moderate", never dramatic.

## Across all 7 seeds — two invariants

1. **Recall superiority is weak and situational.** Best case = "moderate edge" (stock-reservation). Most = tie. loom-spec **never dramatically beat** a capable baseline on omissions in 7 tries. The A/B-baseline lesson is robustly confirmed: a strong model brainstorms well by instinct.
2. **Structural value is strong and domain-independent.** On *every* seed, Arm A produced 16–27 testable `#### Scenario:` GIVEN/WHEN/THEN criteria (TDD-ready for `loom-code:writing-plans`) + a non-empty, source-tagged `## Blind spots` + seeded/inferred/critic-found provenance. Arm B always produced a thorough-but-prose list — never verification-ready, never tagged. This advantage held regardless of domain or recall outcome.

## Bottom line for the bet
- **"Finds more omissions than you would" — NOT supported as a general claim** (7-seed evidence). It's a narrow, situational benefit (object-deep + thin-priors domains), and modest even there.
- **"Produces structured, verification-ready, honestly-tagged spec output" — strongly and consistently supported.** This is the reliable, defensible differentiator vs a free brainstorm, independent of domain.

## Recommendation
1. **If shipping**: position loom-spec's value as **structured verification-ready output + enforced blind-spots/provenance** (reliable, domain-independent) — and as a **recall aid for object-deep, under-documented operational domains** (situational). Drop any "finds more than you would" framing — 7 seeds don't support it.
2. **Do NOT expand to the full 5-skill pipeline on a recall argument** — that case is now well-tested and weak. Expand only on the structural/verification-readiness argument, if at all.
3. The recall question is now **answered** (7 seeds) — no value in more A/B recall runs.
