---
name: preamble-wording-is-contract-surface
description: In prompt-artifact work, a station preamble's vocabulary steers downstream machine classification — treat preamble word choice like an API field name
type: gotcha
origin: PR #487 (loom-pipeline v1.1 driver debts, 2026-07-04)
---

In prompt-artifact work — where the shipped artifact is prompt text
that other automated steps consume — the vocabulary of a preamble
steers downstream classification, not just tone. Real case in the
loom pipeline (an automated principles→design→spec→code run):
a pipeline station (one LLM-driven step) filed a cost-cutting
"adopt" action as an entry in the run ledger's `interventions[]`
list BECAUSE the preamble text called that action an intervention.
The fix (PR #487) was wording: "adopt = cost-cut record in summary,
never an interventions[] entry."

**Why:** an LLM consuming a preamble treats its nouns as the
category system for what it later writes; a casual word choice
becomes a wrong machine-readable classification with no error
raised.

**How to apply:** when writing or editing prompt text that a
downstream step classifies against (ledgers, status fields,
verdicts), review each category noun in the preamble as a contract
surface — the same care as renaming an API field — and state
explicitly which bucket each action belongs to.
