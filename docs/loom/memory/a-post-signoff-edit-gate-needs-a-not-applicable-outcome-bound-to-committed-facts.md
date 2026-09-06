---
name: a-post-signoff-edit-gate-needs-a-not-applicable-outcome-bound-to-committed-facts
description: A gate that asks "was this document edited after it was signed off" finds its answer by locating the sign-off commit, so once the work ships and the merge collapses that commit away the gate reports tampering forever on every already-delivered change; the outcome it needs is a third one, not-applicable, and every fact the carve-out rests on must be committed and reachable — an uncommitted or unreadable status turns a merely missing commit into blanket amnesty
type: practice
origin: 2026-09-06 graduated-probes-survive-squash W1-01 — two independent readers each narrowed the first draft of the carve-out
---

A gate of this shape has two natural outcomes: the document is unchanged
since sign-off (pass), or it changed (block). Both are computed from the
sign-off commit. When the work ships and the merge rewrites history, that
commit stops existing, and the gate falls into the block branch for a reason
that has nothing to do with tampering — it simply cannot find its baseline.
Every shipped change then reports as an edited one, permanently, and the
signal is gone for the in-flight changes the gate exists to protect.

The fix is a third outcome, named: not applicable, at a passing exit, saying
why. Naming it matters as much as the exit code, because an ordinary pass is
silent, and a silent zero cannot be told apart from "nothing is wrong" by
either a human or a later machine check.

The carve-out is where this gets dangerous. "The baseline commit is missing"
is not evidence of anything on its own — a branch that never made the commit
looks identical to one whose commit a merge erased. So the amnesty has to
rest on a second fact, and that fact has to be committed and reachable from
the current head: a closed status sitting only in the working tree is a claim
anyone can write, and an absent, unreadable, or unparseable status is not a
claim at all. Each of those must fall back to blocking, which is the safe
side. A closed status is also not blanket permission: when the baseline
commit IS present, an edit to already-delivered work still blocks.

**Why:** The two failure directions cost differently and both are quiet. Too
narrow, and the gate cries tampering over every shipped change until people
learn to ignore it — the ignoring is the real loss, and it happens on the
in-flight changes too. Too wide, and deleting one commit buys silence on a
document nobody may edit any more.

**How to apply:** Give the gate three outcomes and make the third one speak.
Bind the carve-out to facts that are committed and reachable, never to
working-tree text; treat absent, unreadable and malformed alike as in-flight
and block. Recompute a terminal state from history rather than from whatever
line is checked out now, so reverting the status line does not reopen the
window. Keep the carve-out conditional on the baseline being genuinely
absent. Write the boundary cases as tests before the carve-out exists —
uncommitted status, deleted document, unreadable document, malformed status,
baseline present but content tampered — because each one is a way the amnesty
silently widens. See
[[a-plan-is-a-dispatch-ticket-and-changes-only-by-charter-policy-after-its-commit]]
for the rule this gate enforces, and
[[a-full-history-rehearsal-cannot-model-the-squash-that-lands-the-branch]]
for catching the same erasure before it reaches the trunk.
