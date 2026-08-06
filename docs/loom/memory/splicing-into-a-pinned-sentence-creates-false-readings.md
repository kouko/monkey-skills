---
name: splicing-into-a-pinned-sentence-creates-false-readings
description: Extending an existing contract sentence in place — adding new material inside an enumeration or as indented continuation lines of a schema placeholder — creates defects that presence-pins cannot see, because the pinned substrings all still match while the JOINT reading changes; new contract material goes in its own sentence (or inside the placeholder it governs), and the guard is whole-sentence reading or mutation testing, never substring presence
origin: 2026-08-06 progress-card roadmap arc (branch fix-plan-card-ascii-marks), round-2 whole-branch review
---

# Splicing into a pinned sentence creates false readings

## What happened

Both round-2 placement defects in the same arc had the same shape —
new material added *inside* an existing load-bearing sentence:

1. `family-relay.md §(a2)`: the `--detail T<N>` clause was spliced
   into the "Field order is fixed: Goal / task table / Stage / next"
   enumeration. Every field-name pin still passed, but the joint
   reading now claimed detail output carries Stage/next — false.
2. `plan-format.md` Goal schema: the indentation rule was written as
   indented continuation lines under the `Goal:` template entry —
   exactly the position the parser folds into the value, so copying
   the template froze rule text into a real plan's goal.

## How to apply

- New contract material next to an existing pinned sentence goes in
  its **own sentence** — or, for schema templates, **inside the
  placeholder** it governs (so a copier replaces it wholesale).
- Presence-pins (substring asserts) are blind to placement: they
  pass while the joint reading flips. When reviewing an edit near a
  pinned sentence, read the **whole resulting sentence** as a cold
  reader would, and mutation-test the pin (delete the new clause —
  does anything go red?).
- Fix rounds are the high-risk moment: the writer is focused on the
  content being added, not the sentence being extended (the
  fix-round-writes-defects family; this is its placement variant).
