---
name: a-behavioral-ab-binds-the-exact-wording-it-tested
description: A behavioral A/B on a prompt artifact (trigger card, agent contract, template sentence) validates only the EXACT wording that ran — a post-A/B reword, even one that "just clarifies" a reviewer-found ambiguity, ships an untested variant and silently discards the evidence; the disposition that survives review is to ship the tested wording with the ambiguity recorded as debt and schedule the reword WITH its own fresh A/B leg
type: practice
origin: feat/ascii-graph-generative-trigger (2026-08-12) — docs arm found "lead the explanation with the generated diagram" two-readings-ambiguous AFTER the A/B (candidate 2/2 loose reading, 0/2 strict); rewording then would have unshipped the 2/2 evidence, so the wording shipped as-tested and the reword rides the telemetry re-run arc; the same reviewer adjudicated the disposition acceptable
---

The generative-trigger arc A/B-tested the card sentence (candidate 2/2,
anti-decoration 0/1), then whole-branch review found the sentence's key
clause ambiguous — the strict reading ("final text embeds the diagram")
measured 0/2 even on the passing runs. The tempting fix (reword now,
ship clearer text) would have shipped wording no probe ever ran.

**Why:** behavioral evidence on prompt artifacts is wording-bound, not
intent-bound — models act on the exact tokens. An evidence-improving
edit and an evidence-invalidating edit look identical in a diff; the
only safe classifier is whether the shipped bytes are the tested bytes.
Same mechanism family as
[[agent-contract-edits-do-not-reach-this-sessions-subagents]] (behavior
claims need the artifact that actually ran) and the equivalence-gate
lesson (equivalence proofs don't transfer across edits).

**How to apply:** when review finds a wording defect in an artifact that
already passed a behavioral test: (1) ship the tested wording, record
the defect as carried debt with the two readings spelled out; (2) any
reword lands only WITH a fresh behavioral leg (batched into the next
scheduled measurement is fine); (3) state in the review disposition that
the A/B binds the wording — reviewers accept this when said explicitly.
The success predicate ambiguity itself is a lesson: operationalize
"success" in the test plan (which reading counts) BEFORE running, so a
found ambiguity is a wording bug, not an evidence dispute.
