---
name: a-mechanism-difference-is-not-a-defect
description: An audit finding of the form "lane A uses method X while lane B uses the better method Y" describes a MECHANISM, not an outcome — twice in one day a planned conversion was withdrawn because measuring the two methods' ANSWERS showed they agree almost everywhere, and where they differ the "better" method was wrong (a structural rule promoted the wrong equity figure on 8 of 8 filers, and left 3 currently-answered fields unresolved). Before converting a lane to the better mechanism, measure the answers, not the mechanisms; and count how often the two can even be compared, because a sample where only one candidate exists cannot discriminate at all.
type: gotcha
sources:
  - resource: 2026-07-28 — two ratified work items withdrawn on measurement before implementation; full evidence in docs/loom/audits/2026-07-28-revenue-chain-and-hierarchy-audit.md §2-§3 (the first) and §8 (the second)
---

An audit is good at finding that two lanes do the same job differently. That
finding is cheap to write, reads as a defect, and plans get built on it. Twice on
one day a plan built that way was withdrawn before any code was written, both
times because nobody had asked the next question: **does the difference change
any answer?**

- One lane fetched a fixed list of concepts while a sibling read the filing's own
  structure. The proposed fix — widen the list — was measured and failed: the
  identity that would have validated the widening held in 61 of 148 filer-years
  and the same filer flipped between holding and failing across adjacent years.
- The other lane selected 13 of 14 statement fields by a hardcoded name chain
  while a sibling field used a structural rule. Converting the 13 was measured
  across 14 filings and rejected: the two methods AGREE wherever both resolve,
  the structural analogue is **systematically wrong** on `total_equity` (8 of 8
  filings — the parent-only figure's calculation parent is always the
  including-NCI figure, so a structural filter always promotes the wrong one),
  and it leaves three fields unresolved that the name chain answers correctly.

**Why the framing misleads.** "Lane A does not use the better mechanism" is a
true sentence about code that says nothing about output. The mechanism gap is
visible by reading; the outcome gap needs a measurement nobody has run yet — so
the finding ships as an actionable defect while the evidence for it does not
exist. It is also asymmetric in a way that hides the risk: the mechanism sounds
principled ("use the filer's own declared structure") and the incumbent sounds
crude ("a hardcoded list"), which makes the conversion feel like obvious hygiene.

**A sample-size trap rides along.** The first pass at the second measurement ran
on the 2 filings the repo held structured data for, and concluded the methods
were equivalent by construction because 11 of 14 fields had only one candidate.
At 14 filings that set collapsed to 6 — multi-candidate cases are common. The
conclusion survived but its reasoning was wrong, and only the larger sample
showed which. **A filing where only one candidate exists cannot discriminate
between two selection methods at all**; count the discriminating cases before
trusting an agreement rate.

**How to apply:** when an audit reports that one lane uses a worse mechanism,
treat it as a hypothesis with an unmeasured outcome. Before planning a
conversion, measure per case: do the methods AGREE, DIVERGE, or does the
proposed method fail to decide? For every DIVERGE, judge which answer is
financially/semantically CORRECT — a divergence where the new method is wrong is
evidence AGAINST the conversion, and it is the easiest result to misread as
progress. Count how many cases can discriminate at all. And record the negative
result next to the original finding, or the mechanism observation will be
re-proposed by the next reader. Bounds
[[concept-name-matching-cannot-separate-a-line-from-its-namesakes]]: the declared
hierarchy settles TOTAL-versus-COMPONENT, which is what that entry needed; it
does NOT settle which of several legitimate totals a reporting convention wants.
