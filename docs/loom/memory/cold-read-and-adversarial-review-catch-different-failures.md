---
name: cold-read-and-adversarial-review-catch-different-failures
description: A fresh-context cold-read verifies a reader UNDERSTANDS a rule; an adversarial whole-branch review verifies the rule is ROBUST against a reader trying to exploit it — these are different failure classes and one does not substitute for the other on exemption/gate-mechanism changes
type: practice
origin: PR #520 (loom-code mechanical-exemption sync-script category, 2026-07-08)
---

A documentation change to `subagent-driven-development`'s
`Review-weight: mechanical` self-check passed a fresh-context cold-read
cleanly on its first draft (a reader given only the edited files
correctly classified the target scenario, unprompted). The same draft
then went through whole-branch adversarial review and was found to have
a real security-shaped gap: the self-check's "re-run the script and diff
its output" instruction never pinned the script itself to a trusted git
state, so an implementer could tamper with the script and the "zero
diff" check would tautologically pass against its own freshly-modified
output. The cold-read had no way to surface this — it only tests whether
a cooperative reader reaches the intended conclusion, not whether an
adversarial one can route around the rule.

**Why:** cold-read and adversarial review test orthogonal properties.
Cold-read = comprehension under good faith (does the wording communicate
what it means to communicate?). Adversarial review = robustness under
bad faith (can the wording be satisfied by something it wasn't meant to
allow?). A rule can pass one and fail the other independently — this
case passed comprehension and failed robustness, but the reverse is
equally possible (confusingly-worded but accidentally unexploitable).

**How to apply:** cold-read is a fine, low-cost verification method for
pure documentation/prose changes with no gate/exemption/self-check
mechanics involved (e.g. a SKILL.md prose clarification that doesn't
change what an agent is *allowed to skip*). The moment a doc change
touches an exemption, a gate, a self-check, or anything that lets an
agent skip a safety step under some condition, treat it as
security-relevant and get an adversarial whole-branch review — a
cold-read alone is not sufficient evidence the change is safe to ship,
even if it passes cleanly.
