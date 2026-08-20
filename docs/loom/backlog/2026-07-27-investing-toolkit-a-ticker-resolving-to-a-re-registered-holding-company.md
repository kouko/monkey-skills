---
name: 2026-07-27-investing-toolkit-a-ticker-resolving-to-a-re-registered-holding-company
description: investing-toolkit — a ticker resolving to a re-registered holding company returns nothing, successfully
status: open
origin: dogfood of `pack.py --pack reconstruct`. `XOM` returns `requested: 0 / succeeded: 0 / failed: 0`, `failed_items: []`, `_status: "ok"`, exit 0, in 0.1 s — a clean success over zero filings.
start: READY. Smallest end state is a typed error when a resolved CIK yields zero filings of the requested form, naming the CIK so the reader can see the entity is wrong rather than the history empty.
---

- Origin: dogfood of `pack.py --pack reconstruct`. `XOM` returns
  `requested: 0 / succeeded: 0 / failed: 0`, `failed_items: []`,
  `_status: "ok"`, exit 0, in 0.1 s — a clean success over zero filings.
- Cause, measured 2026-07-27 with the post-#621 merged read: SEC's own
  `company_tickers.json` maps `XOM` to CIK **2115436** ("ExxonMobil Holdings
  Corp"), which carries 26 filings (S-8 POS ×23, 8-K, POSASR, 8-K12B) and
  **zero 10-Ks**. The predecessor CIK **34088** carries 3,552 filings and
  **31 10-Ks spanning 1994-03-11 to 2026-02-18**. `resolve_cik` succeeds,
  `list_filings` returns an empty list, the loop never runs, and
  `pack_reconstruct` reports the empty result as healthy. The defect is ours:
  `requested == 0` is not distinguished from a completed run.
- **Two populations, not one — do not conflate them.** Only **1 of 71** roster
  filers exhibits THIS defect (`silent_empty`: XOM alone). `BLK` is the
  neighbouring shape: its current CIK 2012383 carries 5,049 filings but only
  **2 10-Ks, 2025-02-25 and 2026-02-25**, so it returns a truthful-but-shallow
  4-year history rather than a silent nothing. Both stem from the same cause
  (a re-registration that leaves the history under a predecessor CIK) and the
  population grows with every such reorganisation, but only XOM's failure mode
  is a lie.
- Scope note: `statement-backfill` already fails loud here — verified from
  source, not from the CHANGELOG sentence: `sec_edgar_client.py:3980-3990`
  returns `_statement_backfill_error_slot` when the `us_gaap` concept set is
  empty, and `pack_us.py:1166-1171` passes it through with no `facts` key,
  while `pack_reconstruct` (`pack_us.py:1539-1544`) iterates an empty
  `list_filings` and reports ok. **The two US lanes genuinely disagree on the
  same ticker** — but note their guards trip on DIFFERENT conditions (backfill
  on "zero us-gaap concepts", reconstruct on "zero 10-K filings"); they agree
  about XOM only because both happen to hold. Fixing the guard is cheap;
  deciding whether to STITCH across a predecessor CIK is a separate, larger
  question that 2.38.0 explicitly declined ("never stitched from a predecessor
  CIK") and this entry does not reopen.
- Start: READY. Smallest end state is a typed error when a resolved CIK yields
  zero filings of the requested form, naming the CIK so the reader can see the
  entity is wrong rather than the history empty.
