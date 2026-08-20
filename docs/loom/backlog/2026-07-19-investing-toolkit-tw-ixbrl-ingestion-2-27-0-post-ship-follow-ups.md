---
name: 2026-07-19-investing-toolkit-tw-ixbrl-ingestion-2-27-0-post-ship-follow-ups
description: investing-toolkit TW iXBRL ingestion 2.27.0 — post-ship follow-ups
status: open
origin: TW iXBRL ingestion (branch xbrl-tw, PR #592, 2026-07-19); brief/plan Decision Log + whole-branch review ship-as-debt rulings.
start: next touch of `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_*.py` or `pack_tw.py` memo-fetch.
---

- Start: next touch of `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_*.py`
  or `pack_tw.py` memo-fetch.
- Origin: TW iXBRL ingestion (branch xbrl-tw, PR #592, 2026-07-19); brief/plan
  Decision Log + whole-branch review ship-as-debt rulings.
- What: ~~(a) **financial `-fh` canonical + notes sub-arc**~~ ✅ SHIPPED 2026-07-23
  (2.31.0, branch feat-tw-ixbrl-fh) — `-fh`/`-basi`/`-bd`/`-ins` canonical builders +
  5-way classifier + bank asset-quality notes + smart-decode + DCF fail-loud;
  securities-dealer (`-bd`) and insurer (`-ins`, incl. life/P&C/reinsurance sub-shapes)
  resolved too. ~~(b) **endorsement/guarantee curated field**~~ ✅ SHIPPED 2.33.0
  (branch tw-ixbrl-endorsement) — `extract_endorsement_guarantee_notes`
  reconstructs per-counterparty rows by document-order segmentation on the
  `CompanyNameOfTheEndorserGuarantor` anchor + a span-scoped curated aggregate
  (avoids the 資金貸與 doc-wide-sum overcount), routed by population through
  `_extract_notes`; the deferral test flipped to an inclusion assertion.
  (c) **興櫃 multi-period series** — semiannual
  (Q2/Q4) cadence; season-fallback already handles per-period absence, a series
  builder is future. **Update (2.35.0):** the TW KPI store producer (`kpi_tw` +
  `kpi_tw_ingest`) now handles the 興櫃 semiannual cadence — a 6-month duration
  maps through the store's existing `_qtrs` machinery (→ 2 quarters) with no new
  `period_kind`. So 興櫃 multi-period now only needs 興櫃 FETCH; the series-build
  side is done. (d) 🟢 debt: T3 canonical tie-break order untested (membership
  only), T2 3×502-exhaustion branch untested.
