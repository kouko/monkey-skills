---
name: 2026-07-18-knowledge-triage-v2-1-mechanize-enforcement-semantics
description: knowledge-triage v2.1 — mechanize enforcement semantics
status: OPEN
origin: 2026-07-18 live dogfood, both weak-model legs (`docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`); knowledge-triage arc PR #581/#582.
---

- Origin: 2026-07-18 live dogfood, both weak-model legs
  (`docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md`);
  knowledge-triage arc PR #581/#582.
- What (diagnosis): across spec+design stations on haiku, the headline
  rule survives (landmines flagged domain-convention) but prose-only
  ENFORCEMENT SEMANTICS do not — leg 1: invented enum values, dropped
  SHAPING tier + gate language, hardcoded settlement-basis in REQ-002
  against its own flag; leg 2: enum held, SHAPING label kept but its
  consequence INVERTED ("do not block"), 締め日 silently assumed to
  calendar month. Vocabulary survives; enforcement dies in prose.
- Fix (three cuts, per pipeline-enforced-gates precedent):
  a. loom-spec `validate_spec_output.py`: `evidence_needed:` value
     whitelist (three pin values only); SHAPING|DEFERRABLE label
     required within each domain-convention tag's neighborhood;
     SHAPING without `deferred: <reason>` ⇒ nonzero exit (gate rule
     encoded mechanically). RED fixtures = the real leg-1 artifacts.
  b. loom-interface-design: design-critic gains a mechanical pre-check
     row (grep the artifact: out-of-enum tag values, or SHAPING marked
     non-blocking without `deferred:` ⇒ NEEDS_REVISION finding);
     one-line supplement AFTER the pin in both drafting references
     stating the SHAPING consequence inline (proximity for weak
     readers, extraction-severing precedent).
  c. loom-spec completeness-critic: consistency lens — proposal-level
     open flags vs spec.md requirement text that silently resolves the
     same question (leg 1's REQ-002; not mechanically checkable).
  d. loom-product-principles `validate_principles_output.py` (leg 3,
     2026-07-18): `evidence_needed:`/`— assumption:` marker whitelist
     when present + provenance check (Anchors rows claiming seed
     provenance must quote strings literally present in the seed —
     kills the fabricated-attribution variant). The unmarked
     target-invention evasion is judgment-shaped, NOT mechanizable —
     residual = interactive human ratification + downstream stations'
     own triage; labeled honestly, no grep pretends to catch it.
- Evidence note: leg 3 doubles as a natural control — within one weak
  run, every validator-enforced dimension survived and every prose-only
  duty died. The mechanize-the-consequences thesis is confirmed, not
  just inferred.
- Next-touch (from cut-d review, 2026-07-18): the `--seed` provenance
  check has no in-skill caller — product-principles has no persisted
  raw-seed-file convention, so Step 8 cannot pass the flag (T16
  spec-reviewer endorsed omission; live callers today = dogfood/CI
  harnesses holding the seed independently). Re-trigger: when
  loom-pipeline (or any headless driver) starts persisting its
  run-input seed to a fixed path, add a conditional pass-through
  sentence to product-principles SKILL.md Step 8. Also re-measure
  `_PROVENANCE_MIN_MATCH` (n=1, 3-char corridor) against the next real
  dogfood artifact.

Swept 2026-08-06: de-committed COMMITTED-NEXT → OPEN. Shipped same-day
(2026-07-18): cuts a+c in loom-spec 0.6.0 (`validate_spec_output.py`
whitelist / SHAPING-tier checks + completeness-critic consistency-lens),
cut b in loom-interface-design design-critic SKILL.md mechanical pre-check
(~:86-106), cut d in loom-product-principles 0.11.0 (marker whitelist +
Anchors provenance). Remaining work is only the trigger-gated Next-touch
above (seed pass-through once a driver persists its run-input seed;
`_PROVENANCE_MIN_MATCH` re-measure) — commitment tier was stale, entry
stays open on its trigger.
