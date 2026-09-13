# Round 3 design re-look

Round 2 closed the fatal and returned two NEEDS_REVISION verdicts carrying
four blockers. The bounded episode requires a design re-look before the
terminal round rather than a third round of patches, and the four blockers
turn out to be one defect wearing four costumes.

## The four blockers

| Where | What |
|---|---|
| `test_review_convergence_contract.py:135` | `"functional content"` asserted against the whole file; the phrase occurs four times elsewhere, so the passage's sentence can be replaced entirely and every test stays green |
| `intent.md:21` Proposed outcome | still carries the justification the fatal overturned |
| `plan.md:23,41,42` | still claims the pins tolerate rewording |
| `blind-run-report.md` | certifies text this branch no longer ships |

## The one defect

**A check is scoped to a wider surface than the claim it protects, and a
claim lives in more places than one.** They are the same failure seen from
the two ends:

- scope too wide → the claim's real home can be emptied while some other
  occurrence keeps the check green;
- homes too many → correcting the claim in its real home leaves the copies
  asserting the old thing.

Every defect this episode found is an instance:

- the clause pins matched `SKILL.md ∪ operations.md`, so the shipped
  contract could be rewritten while the reference copy held it green
  (found in Round 2 by writing the negative case);
- the inertness guard matched one `\n\n` block, so the scarcity paragraph
  was unguarded (found in Round 1 by mutation);
- `"functional content"` matches the whole station file (found in Round 2
  by mutation) — **written in the same commit that fixed the first one**;
- the pin's own properties are restated in six documents, four of which
  still say the overturned thing.

That last line is worth stating plainly: the change whose subject is *a
rule with no normative home drifts* produced, in its own artifacts, a
claim with no normative home that drifted. The mechanism did not fail; the
discipline did, four times, in the same direction.

## What changes, rather than what gets patched

1. **Every assertion is scoped to the claim's home.** In the station test
   that means `_recording_passage()` for all passage assertions, not
   `REVIEW_WORDS`; in the memory test the Record section, not the union.
   A test that reads a wider text than the clause it defends is not a
   weaker test, it is a different test — one that passes for reasons
   unrelated to its name.
2. **A mechanism's properties are stated once, where the mechanism is.**
   The test module is that home; it is the only artifact that cannot drift
   from the mechanism, because it is the mechanism. The intent and the plan
   state the *outcome* — deletion is caught, dilution is caught — and stop
   describing how the matcher behaves. This removes four surfaces rather
   than correcting them, which is why it is a design change and not the
   fifth patch.
3. **Evidence is bound to the digest it ran against.** The blind run is
   re-run rather than edited: a report is not a claim to be corrected, it
   is an observation of one tree, and the tree changed.

## What this costs

The intent and the plan become less specific about the mechanism. A reader
who wants to know whether a reword goes red must open the test. That is the
intended trade: one accurate answer in the place that cannot lie, instead
of four convenient answers that already did.
