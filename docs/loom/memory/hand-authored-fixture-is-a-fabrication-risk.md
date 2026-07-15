---
name: hand-authored-fixture-is-a-fabrication-risk
description: A hand-built test fixture for an anti-fabrication feature is itself a fabrication risk — verify every value against the real source, ideally by cross-checking the live extractor
type: gotcha
origin: operational-kpi tier-② XBRL pilot (feat-operational-kpi-xbrl-pilot, 2026-07-15)
---

When TDD'ing an anti-fabrication feature (one whose whole purpose is to
never invent, mislabel, or zero-fill a value) against a REAL-data
fixture, the fixture itself is the weakest link: if you hand-author its
values from a rounded probe printout or from memory, you can silently
fabricate the very precision/pairing the feature exists to protect.

Real case: a 5-fact Apple XBRL fixture was hand-built from earlier
probe output that only printed values to ~1 decimal (`209.6 B`). Three
of five values were wrong — two carried fabricated trailing digits
(`209628000000` vs the real `209586000000`; `195228000000` vs
`195201000000`), and one paired the FY2015 iPhone value with the FY2016
period label (`155041000000`@2016-09-24 — actually FY2015; real FY2016
was `136700000000`). All three survived the unit tests (which asserted
the fixture's own wrong numbers) and were caught ONLY when the live
data-layer extractor returned different values and the mismatch was
investigated.

**Why:** a fixture is an oracle; tests can only be as truthful as it is.
A green test against a fabricated fixture is a false green — it proves
the code matches the lie, not the source. Rounded/printed probe output
drops exactly the precision an anti-fabrication feature must preserve.

**How to apply:** author fixture values from an EXACT-integer dump of
the real source, not a rounded/eyeballed printout; keep a one-line
provenance cite in the fixture (accession + "verified live YYYY-MM-DD");
and before trusting the offline tests, cross-check at least the shared
values against the live extractor (a divergence is a defect in one of
them — investigate, never wave it off as "close enough"). Relates to
[[fail-closed-default-must-be-enforced-not-emergent]].
