---
name: reviewer-severity-tags-do-not-encode-load-bearingness
description: A reviewer's 🟡/🔴 severity assignment is not a reliable signal of whether a finding is load-bearing — any relaxation that trusts reviewers to escalate the ones that must not ship is built on an empirically falsified premise
type: practice
origin: 2026-08-11 review-cost-reduction arc — docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md (14/14), user option-1 decision
---

When the 2026-08-11 arc sampled every reachable 2+🟡-gated docs verdict
(6 verdicts, 14 classifiable findings), all 14 turned out load-bearing —
an unexecutable instruction or a misleading fact — yet every one had
been tagged 🟡, not 🔴, by top-tier reviewers. The planned "🟡 ships as
debt at any count; a reviewer who believes a 🟡 must not ship escalates
it to 🔴" relaxation was dropped on this evidence: the escalation valve
assumes severity tags encode load-bearingness, and the sample showed
they do not.

**Why:** severity tags encode the reviewer's local judgment of fix
urgency, not a measurement of downstream consequence. Mechanisms that
gate on counts of a severity class survive weak models; mechanisms that
trust the tagger to route the dangerous subset do not survive even
strong ones.

**How to apply:** before relaxing any threshold that stops gating a
finding class, sample what that class historically caught (the
2026-08-11 audit is the worked method); never accept "the reviewer will
escalate the important ones" as the safety argument — reviewers
demonstrably did not.
