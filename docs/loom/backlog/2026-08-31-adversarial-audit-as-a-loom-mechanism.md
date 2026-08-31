---
name: 2026-08-31-adversarial-audit-as-a-loom-mechanism
description: Decide whether a post-merge adversarial audit (break-it, zero-context, reproduce-or-hold) becomes a loom-code mechanism for safety-bearing changes, or stays an ad-hoc dispatch
status: closed
origin: 2026-08-31 — an ad-hoc opus adversarial audit of main 96a56d8b (loom-code 0.106.0), dispatched by the orchestrator outside any loom skill, reproduced four 🔴 in the batch-review adapter one hour after #767 merged with every per-task triad and the whole-branch review PASS
start: event — the batch-review-hardening arc (docs/loom/specs/2026-08-31-batch-review-hardening.md) closes, so the value of the audit that produced it can be weighed against its cost with the fix arc's numbers in hand
---

Every existing review station asks "does this change meet the standard?"
against a diff: the per-task triad, the whole-branch `code-reviewer`, and
`verification-before-completion` all inherit the author's plan and read the
changed lines. None asks "can a motivated party defeat this?" against the
merged system. The 2026-08-31 audit did — seven attack vectors, zero
context, a hard rule to distinguish "reproduced" from "attempted, held" —
and found that `apply-result` could finalize a commit no reviewer saw
(F1), that one hand-written PASS file worked across repositories (F2), and
that a hand-set `done` laundered through crash recovery (F4). All were on
paths the 146-test floor never exercised; all survived three review layers.

The audit is not part of loom: its attack list was authored by the
orchestrator from personal memory, its run was a plain `general-purpose`
dispatch, and nothing in `finishing-a-development-branch` or
`requesting-code-review` names it. Whether it should be one is the open
question. Arguments for: it is the only station that reads the system
rather than the diff, and the only one that runs attacks instead of
reading code. Arguments against: cost (opus, ~120k tokens, ~7 minutes,
real subprocess runs), coverage limited to the vectors a human lists, and
the risk of turning "attempted, held" into a checkbox.

Candidate shapes, none chosen: (a) an optional close-out step gated on a
plan-level `safety-bearing: yes` flag; (b) a standalone
`loom-code:adversarial-audit` skill invoked by name post-merge; (c) a
`references/attack-vectors.md` catalogue that the whole-branch reviewer
reads as an extra dimension without a separate dispatch. The choice needs
the fix arc's outcome first — if the seven closures land cheaply, the audit
paid for itself and (a) or (b) is worth a brief; if they sprawl, the
finding is that the audit should run before merge, not after.

Closed 2026-08-31 — the station ships pre-merge, not post-merge as this
entry proposed: shapes (a) (plan-level flag) and (c) (a catalogue read by
the reviewer) were adopted; (b) the standalone post-merge skill was not.
See `docs/loom/specs/2026-08-31-adversarial-audit-station.md`.
