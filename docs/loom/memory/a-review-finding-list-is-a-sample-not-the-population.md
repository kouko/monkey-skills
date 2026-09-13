---
name: a-review-finding-list-is-a-sample-not-the-population
description: A reviewer's finding list enumerates the sites it happened to reach, not every site carrying the defect — three stale copies of one false claim were named and fixed, two more survived because they paraphrase the claim without naming its symbol; treat each finding as a defect CLASS and sweep for its paraphrases, not just its citations
type: gotcha
sources:
  - resource: feat-us-quarterly-statement-series (US quarterly three-statement series arc, rounds 3-4 whole-branch review, 2026-08-07)
---

A round-3 whole-branch review found that a contract change — `_acquire_raw_filing`
went from *raising* on a `None` accession to *returning a loud slot* — had left
neighbouring prose asserting the old behaviour. It named **three** sites. All three
were fixed.

Round 4 found **two more**, and one of them was the docstring of the very test
whose stub had just been corrected — the fix and the stale text were 25 lines
apart in the same function.

**Why the sweep missed them.** The three named sites all quoted the mechanism:
`_accession_nodash`, `AttributeError`, `BEFORE its try`. A grep on those symbols
finds them. The two survivors said the same false thing in prose that names no
symbol:

- *"neither handed to the acquisition boundary (which crashes on it)"*
- *"A filer with no 10-K therefore aborts memo-fetch with a traceback"*

A reviewer only reached them by running a **second** sweep on paraphrase wording
(`crashes on|with a traceback|not defensive|aborts`). Nothing in the finding list
told anyone a second sweep was owed.

**The mistake underneath is procedural, not textual.** A finding list reads like a
work order: fix these N, and you are done. It is actually a *sample* — reviewers
cite the instances they reached, bounded by their scope, their grep, and their
budget. One reviewer named the failure exactly: *"this suggests the round-3
findings were treated as a fix list rather than as a defect class."*

**What to do**

- For each finding, write down the CLAIM in one sentence, then sweep for the claim
  — including at least one sweep that assumes the text never names the symbol.
  Paraphrase sweeps are where the survivors live.
- When a fix is a contract change, the sweep scope is every file that describes the
  contract, not every file that calls it. Docstrings and test docstrings are the
  usual carriers; a test's own docstring is the easiest one to miss, because the
  fix is in the same function and feels done.
- Say in the fix report how the sweep was done and what it would not have found.
  "Fixed the three sites" is a claim about the population; "fixed the three cited
  sites; swept symbols and paraphrases, found N more" is a claim about the sweep.

Related: [[a-rule-edit-falsifies-the-unchanged-prose-composed-with-it]] (the
neighbouring-prose class this specialises), [[core-rule-removal-needs-plugin-wide-sweep]]
(same sweep discipline for a removal), [[a-semantics-change-needs-a-plugin-wide-contradiction-sweep-arm]]
(the dedicated review arm that institutionalises it).
