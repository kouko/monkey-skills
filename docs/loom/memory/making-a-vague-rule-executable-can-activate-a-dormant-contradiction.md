---
name: making-a-vague-rule-executable-can-activate-a-dormant-contradiction
description: Rewriting a judgment-shaped instruction into a mechanically checkable one can turn a harmless ambiguity into a live conflict with a neighbouring rule — the two coexisted only because neither was precise enough to disagree, so hardening one demands re-reading every rule it now interacts with
type: gotcha
origin: 2026-08-18 stale-render arc (loom-code 0.88.0) — a delivery check was rewritten from "matches the plugin whose protocol you are reading" to naming the exact manifest file to read, which then false-blocked the working-tree carve-out stated two paragraphs above it; the branch making the change was itself the worked example
---

A protocol carried two rules: an exception letting a session that is
DEVELOPING a tool run its own working-tree copy, and a delivery check that
the output's version stamp "matches the plugin whose protocol you are
reading". Vague, the second rule never bit — a reader who could not tell
which artifact to compare simply exercised judgment.

Hardened into "read `"version"` from this exact path and string-compare it",
it bit immediately: under the sanctioned exception the two manifests are
different files BY CONSTRUCTION, so their versions differ whenever the
branch has bumped, and the newly-precise rule demanded a re-run that could
never reconcile them. The reviewer's phrasing was exact — the conflict *was
latent under the vague wording; making the comparison executable is what
made it bind.*

**Why:** precision is normally strictly good, and this is the case where it
has a cost worth budgeting for. Vague rules fail open — readers route around
them. Precise rules fail closed, which is the point, and closing includes
closing on the cases someone else's rule deliberately left open.

**How to apply:** when converting judgment-shaped prose into a checkable
action, list every neighbouring rule that grants an exception, a fallback,
or a "unless" — then walk each one against the new mechanical form and ask
whether it now produces a state the hardened rule rejects. Carry the
carve-outs forward explicitly into the hardened rule rather than assuming
proximity in the document implies they still apply.
Related: [[a-rule-edit-falsifies-the-unchanged-prose-composed-with-it]].
