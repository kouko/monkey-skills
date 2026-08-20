---
name: 2026-08-02-quote-informativeness-needs-corpus-selectivity-not-length
description: no length or width threshold can separate an informative origin quote from a corpus-universal fragment — the measured axis is document frequency, and a selectivity gate is the successor mechanism
status: open
origin: the finding-origin-attribution arc (docs/loom/plans/2026-08-02-finding-origin-attribution.md), five code-quality review rounds on one grammar floor, 2026-08-02
start: when the origin field's ≥40-finding tally fills with human-rejected quotes rather than with `none` — that is the observable saying the screen was load-bearing after all
---

## What was tried, and what it measured

The `origin:` field records the upstream sentence that caused a defect, and a
validator greps that quote in the cited file. A quote short enough to write
without opening the document verifies against almost anything, so four
successive rules tried to impose a minimum size:

1. at least two whitespace-separated tokens
2. characters counted individually in all-CJK runs
3. CJK letters counted within a run
4. display width ≥ 4 (East Asian Width weighted, one canonical form shared with
   the verifier)

Rules 1-3 were language filters in different disguises; rule 4 removed that
entirely — measured false-refusal rate over 3000 real committed sentences per
language was **0.00% for English, Japanese and Chinese alike**. Rule 4 then
failed on its own terms.

## The measurement that ends the length axis

`origin: <any .md> :: "tion"` has display width exactly 4, clears the floor,
and mints a marker end-to-end. **2581 of the repo's 2642 committed `.md` files
contain it — 97.7%.** The value the floor refuses, `"e"`, appears in 99.8%.
The floor's measured benefit is **2.1 percentage points**.

Best document frequency at each width, same corpus:

| width | 4 | 6 | 8 | 10 | 12 | 16 | 20 |
|---|---|---|---|---|---|---|---|
| best-span DF | 97.7% | 84.4% | 61.7% | 40.4% | 39.9% | 33.1% | 16.5% |

The tail is markdown table boilerplate (`|---|---|`), which no width threshold
distinguishes from prose. Length answers *how many columns*; the gate needs
*how surprising in this corpus*. The two coincide for CJK and diverge by
roughly 200× for Latin — a width-4 Latin 4-gram sits at 97.7% while a
width-4 CJK example measured in this same pass, `引述`, sits at 0.5%.

## The successor mechanism

Gate on **corpus selectivity**: refuse a quote whose document frequency across
the repo's own `.md` corpus exceeds some fraction. This is the axis the
measurement points at, and unlike every length constant tried, its threshold
can be calibrated from the curve above rather than invented.

Open design questions, none of them answered here:

- What corpus is the denominator — the whole repo, the cited file's directory,
  or the set of documents this field is allowed to cite?
- Is the check per-run (grep at mint time, bounded cost) or precomputed?
- What does it do about a quote that is genuinely rare but drawn from a
  boilerplate section repeated across many files?
- Does it replace the non-blank rule or sit alongside it?

## Why it was not built here

It is a new mechanism and a new decision, not a sixth patch. The grammar it
would change is transcribed VERBATIM into three shipped contracts, so it
carries a sweep cost that a fresh brief should price deliberately. And the
field's real gate was never this screen: the brief's stop rule keeps the field
only when at least one non-`none` origin **survives a human check**, and
`"tion"` does not survive one for a second.

## What shipped instead

No floor. The grammar is: split on the first ` :: `, require a fully-quoted,
non-blank interior. The absence is recorded in the plan's §Notes with this
measurement, so the next reader does not re-derive the alarm and re-attempt
the same axis.
