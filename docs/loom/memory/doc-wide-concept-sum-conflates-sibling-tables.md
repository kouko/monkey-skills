---
name: doc-wide-concept-sum-conflates-sibling-tables
description: In an iXBRL (or any tagged) document, a concept/tag name is NOT unique to one table — sibling note-tables reuse the same concept (e.g. TW MOPS `ActualAmountProvided`/`EndingBalance2` appear in BOTH the 背書保證 endorsement table AND the separate 資金貸與 financing-to-others table). Summing a concept DOC-WIDE silently conflates the tables and overcounts (1101: doc-wide 105.9bn vs endorsement-only 62.8bn — 74 of 113 facts belonged to the other table). Scope every aggregate to the row/section span, never a doc-wide concept sweep.
type: gotcha
origin: branch tw-ixbrl-endorsement (2026-07-24, 2.33.0) — the endorsement extractor's aggregate; the recon's doc-wide SUM(ActualAmountProvided)=105.9bn was wrong (conflated 資金貸與), span-scoped 62.8bn is correct; caught by the SDD implementer measuring, then whole-branch-verified.
---

A concept/tag name identifies a *kind of value*, not a *table*. TW MOPS
t164sb01 filings carry several per-counterparty note-tables in one iXBRL
instance — 背書保證 (endorsement/guarantee), 資金貸與 (financing-to-others),
and others — and they REUSE concept names: `ActualAmountProvided`,
`EndingBalance2`, `LimitOn…IndividualCounterparty` all appear in more than one
table. So `sum(f.raw_value for f in facts if f.concept == "ActualAmountProvided")`
sums across every table that carries the concept — a silent conflation.

**Why it hides:** the sum is a plausible large number; nothing errors. On 台泥
1101 the doc-wide `ActualAmountProvided` sum was 105.9bn — but 74 of the 113
facts sat BEFORE the first endorsement anchor and belonged to the 資金貸與 note;
the honest endorsement-only total is 62.8bn. A recon that eyeballs "sum all
ActualAmountProvided" ships the conflated figure; only bounding the sum to the
endorsement rows (each row = the span between successive
`CompanyNameOfTheEndorserGuarantor` anchors) recovers the correct total. The
conflation is invisible to any single-table test because both tables are real
data — the sum is wrong, not missing.

**How to apply:** when reconstructing a per-row table by document-order
segmentation (no leaf `tuple_ref`, shared `context_ref`s — see
[[ixbrl-dom-traversal-drops-nested-facts]]), aggregate **span-scoped**: bound
every fact to the row/section it structurally belongs to (its anchor span),
and sum only within those bounds — never a doc-wide `if concept == X` sweep.
Verify the span-scoped total against a concept that appears ONLY in the target
table (here `EndingBalance2`'s doc-wide sum happened to match because it too is
endorsement-scoped in this filing — but do not rely on that; cross-check with a
uniquely-scoped leaf). This is the aggregation-side dual of the field-level
document-order reconstruction the NPL notes use. Related producer↔consumer
trap: [[producer-marker-inert-until-consumer-branches-on-it]].
