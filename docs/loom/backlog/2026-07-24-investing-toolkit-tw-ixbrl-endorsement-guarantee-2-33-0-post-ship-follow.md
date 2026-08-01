---
name: 2026-07-24-investing-toolkit-tw-ixbrl-endorsement-guarantee-2-33-0-post-ship-follow
description: investing-toolkit TW iXBRL endorsement/guarantee 2.33.0 — post-ship follow-ups
status: OPEN
origin: TW iXBRL endorsement/guarantee ingestion (branch tw-ixbrl-endorsement, 2026-07-24, 2.33.0); whole-branch review PASS, all 🟢.
---

- Origin: TW iXBRL endorsement/guarantee ingestion (branch tw-ixbrl-endorsement,
  2026-07-24, 2.33.0); whole-branch review PASS, all 🟢.
- What: (a) 🟢 **memo-render the endorsement field** (domain-teams / report-equity-memo
  layer, out of this data-layer arc) — `_extract_notes` now surfaces the
  `endorsement_guarantee` curated field (aggregate + per-counterparty rows); wire the
  memo protocol to render the credit-risk / self-dealing signal. The reserved
  `endorsement_guarantee` key is taxonomy-INDEPENDENT but sits in a taxonomy-SHAPED
  notes dict — the render consumer must special-case it regardless of taxonomy.
  (b) 🟢 **terminal-span forward-scan edge**: `_endorsement_row_segments`' last row span
  runs to end-of-facts; if a filing ever has a table trailing the endorsement section
  reusing a shared concept (EndingBalance2/ActualAmountProvided) AND the last endorser
  row omits it, `_first_in_span` could absorb the trailing value. Not observed on 1101
  (資金貸與 sits BEFORE the anchors); confirm with a 2nd endorsement fixture. (c) 🟢
  **no fh+endorsement fixture**: the cross-taxonomy "a financial holding can carry
  endorsement too" claim rests on the -ci 1101 merge + shared code, not a fixture where
  an fh notes dict actually gains `endorsement_guarantee` beside bank-name keys — add one
  when a populated-fh filing is available.
