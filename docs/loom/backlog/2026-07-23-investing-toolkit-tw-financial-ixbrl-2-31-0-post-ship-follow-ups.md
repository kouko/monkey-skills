---
name: 2026-07-23-investing-toolkit-tw-financial-ixbrl-2-31-0-post-ship-follow-ups
description: investing-toolkit TW financial iXBRL 2.31.0 — post-ship follow-ups
status: OPEN
origin: TW financial-sector iXBRL (branch feat-tw-ixbrl-fh, 2026-07-23, 2.31.0); whole-branch review PASS with carried 🟢 debt.
---

- Origin: TW financial-sector iXBRL (branch feat-tw-ixbrl-fh, 2026-07-23, 2.31.0);
  whole-branch review PASS with carried 🟢 debt.
- What: ~~(a) **memo Phase-4 consumption of `not_applicable` DCF**~~ ✅ SHIPPED 2.32.1
  (three render surfaces branch on the marker → "DCF: N/A — financial sector"; live
  2882.TW dogfood CLEAN). ~~(b) 🟢 Rule-of-Three duplication~~ ✅ SHIPPED 2.32.1
  (`_ordered_values_meta` in canonical, `_group_and_select_current` in notes). (c) 🟢
  over-soft-cap functions: `dcf_compute.main`, `pack_memo_fetch` — STILL OPEN (and
  `report-equity-memo/SKILL.md` body now within ~115 words of the hard cap; next addition
  needs a trim). ~~(d) 🟢 fact-count guard under production decode~~ ✅ SHIPPED 2.32.1
  (`test_fixture_fact_counts_match_under_production_decode`, 8 fixtures, zero deltas).
  ~~(e) 🟢 stale scratchpad citations~~ ✅ SHIPPED 2.32.1 (all 5 replaced with the
  operative measured fact inline). (f) US financial filers (`pack_us`) get no
  `sector_class` guard — pre-existing; a future US financial-comps path needs its own.
