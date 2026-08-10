---
name: a-documented-fallback-can-legitimize-a-delivery-gap
description: A skill that documents its own degradation path ("script absent → hand-edit / say N/A") turns a delivery defect into apparent design — reviewers verify the fallback claim is TRUE and never ask whether the state it describes is RIGHT, so the gap ships gate-approved; when writing a fallback, state which condition is a temporary environment state vs a permanent delivery gap, and treat "permanently degraded everywhere but the dev repo" as a defect no fallback text may normalize
type: practice
origin: 2026-08-10, ship-progress-tooling arc — plan_card.py/backlog_index.py were mandated at 10 call sites by five shipped skills yet shipped in no plugin; the skills' own text said "ships in no plugin" with a loud N/A fallback, so four days of plan gates, SDD triads, and whole-branch reviews all verified the claim true and none flagged the state wrong; surfaced only when an external repo (kumiko) hand-invented a progress table that drifted four times
---

The progress tooling defect survived every gate because the gates were
aimed at claim-truth, not state-rightness:

- The skill text **documented the absence** ("`backlog_index.py` absent
  (ships in no plugin) → say N/A loudly"). Every reviewer who checked it
  found the claim accurate — the script really did ship in no plugin.
  A defect wearing a fallback reads as defensive design.
- The duty tests **pinned the fallback wording**, so the degradation
  path acquired test protection: certifying the skill *teaches* the
  degradation is one grep away from certifying the degradation is fine.
- The dev repo is the one environment where the defect cannot manifest
  (the repo-root scripts exist exactly there), so every dogfood, triad,
  and whole-branch review ran in the blind spot. Detection came from a
  consumer repo's own drift pain, not from any gate.

Practice, when writing or reviewing a fallback clause:

1. Classify the trigger: is the absent thing **environmentally absent**
   (host lacks a tool, plugin genuinely optional) or **undelivered**
   (we own the artifact and simply never shipped it)? Only the first
   deserves a fallback; the second is a defect the fallback is hiding.
2. If a fallback fires on 100% of a population (every external repo,
   every run outside the dev machine), it is not a fallback — it is the
   de-facto behavior, and the "primary" path is fiction.
3. Review question to add on any "X absent → degrade" clause: *who
   ships X, and does X actually arrive where this skill runs?* The
   claim being true is not the bar; the state being intended is.

Related: `dogfood-evidence-anchors-shipped-commit` (evidence must bind
what shipped), `subprocess-red-tests-go-false-green-before-the-script-exists`
(the sibling false-green class at test level). The mechanism-level fix
candidate (a foreign-repo cold-start probe) is
`docs/loom/backlog/2026-08-10-foreign-repo-cold-start-probe-for-plugin-shipped-mechanisms.md`.
