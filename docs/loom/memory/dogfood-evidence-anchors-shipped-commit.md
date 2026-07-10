---
name: dogfood-evidence-anchors-shipped-commit
description: A dogfood behavioral PASS certifies only the commit it ran against — post-dogfood remediation ships unexercised unless the probes re-run at the remediated text, and reports must anchor on-branch SHAs (pre-squash SHAs dangle)
type: process
origin: feat/digest-multiview-synthesis whole-branch review (2026-07-10)
---

A skill-text dogfood's behavioral PASS is evidence about ONE commit — the one
the executors read. Two live failure shapes from the digest multi-view branch:
(1) the dogfood PASS anchored pre-squash commit 929bb294, which after the
squash was reachable from no branch, so the report's provenance anchor dangled;
(2) ~90 lines of post-dogfood remediation (including a new unified exactly-2
form) shipped without any probe ever exercising them. The whole-branch review
panel flagged both; the fix was a cheap re-run — two fresh blind probes at the
remediated on-branch commit.

**Why:** this is the skill-text analogue of loom-code's gate-marker rule
("review what you ship, not what you reviewed an amend ago") — for behavioral
skill text, the dogfood IS the test layer, so stale dogfood evidence is a
stale green light.

**How to apply:** after ANY post-dogfood change to skill text, re-run the
affected blind probes at the new commit (cheap: one executor per behavioral
dimension touched) and append a re-run section to the report. Anchor dogfood
reports to a SHA reachable from the branch (`git branch --contains <sha>`),
never a pre-squash object.
