---
name: two-fresh-readers-raising-the-same-wrong-nit-means-the-contract-omits-the-exception
description: When two independent fresh-context readers raise the same finding and a ratified policy says they are wrong, the defect is in the contract they read, not in the readers — list the exception in the contract text they were handed (the reviewer contract now names the artifacts that stay in the user's language) and stop rebutting it round after round
type: practice
sources:
  - resource: 2026-09-05-artifact-charter-boundaries-and-edit-rights — the anthropic and codex readers each flagged the blind-run report for not being English at two checkpoints; the language-policy intent's Acceptance 1 keeps that report in the user's language, and the reviewer contract's language paragraph had not listed it
---

The reviewer contract said internal artifacts are English and listed the
kinds — spec, plan, review notes, evidence, probe docstrings, commit
messages — without naming the exceptions. Two readers of different vendors
inferred that the blind-run report was internal and flagged it, twice.
Each rebuttal was accepted, and the next fresh reader raised it again.

**Why:** a rebuttal reaches one reader once; the contract reaches every
reader every round. A finding that recurs across independent readers is a
measurement of the text, and the cheapest fix is the sentence they lacked.

**How to apply:** on the second independent occurrence of a finding a
policy already settles, edit the contract or lens the readers were handed
to state the exception, pin it with a prose test, and only then dismiss the
finding — cite the new sentence in the dismissal.
