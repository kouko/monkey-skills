---
name: 2026-07-25-investing-toolkit-us-xbrl-kpi-store-producer-2-34-0-post-ship-follow-ups
description: investing-toolkit US XBRL→kpi_store producer 2.34.0 — post-ship follow-ups
status: open
origin: arc (d) US XBRL→kpi_store producer (branch feat-kpi-xbrl-store-producer, 2.34.0, 2026-07-25); whole-branch review PASS_WITH_NOTES + per-task 🟢 findings, logged not fixed. Brief/plan `docs/loom/{specs,plans}/2026-07-24-kpi-xbrl-store-producer.md`.
start: next substantive touch of `analysis-kpi/scripts/kpi_xbrl_ingest.py` or the next US-XBRL-lane arc.
---

- Start: next substantive touch of `analysis-kpi/scripts/kpi_xbrl_ingest.py` or the
  next US-XBRL-lane arc.
- Origin: arc (d) US XBRL→kpi_store producer (branch feat-kpi-xbrl-store-producer,
  2.34.0, 2026-07-25); whole-branch review PASS_WITH_NOTES + per-task 🟢 findings,
  logged not fixed. Brief/plan `docs/loom/{specs,plans}/2026-07-24-kpi-xbrl-store-producer.md`.
- What:
  (a) ✅ **RESOLVED by the 2.37.0 identity arc — struck 2026-07-26.** This item said
  the collision guard keyed on a finer identity than the store, and that
  `derive_kpi_id` was consolidation-blind. Both were fixed on branch
  `feat-kpi-id-consolidation-axis`: `_signature_key` normalizes the consolidation
  qualifier through the consumer's own rule (2.36.0), and `derive_kpi_id` now takes
  the qualifier and gives a NON-default member its own token (`e60a0745`). Its
  prescribed remedy ("normalize consolidation in `_signature_key`, or compare
  NORMALIZED signatures in the guard") is what shipped. Kept as a struck line rather
  than deleted because (b) and (c) below are still open under this same heading.
  (b) 🟢 `kpi_xbrl_ingest.py` has NO try/except wrapper — a bad `--pack` / malformed
  JSON / a fact-pack missing both ticker+company surfaces as a raw traceback (exit 1),
  unlike sibling scripts' clean-message convention. Add clean error handling on next touch.
  (c) 🟢 `_real_shaped_pack`/`_FY2020_PERIOD_START` duplicated across
  `test_kpi_xbrl_ingest.py` + `test_kpi_xbrl_to_tearsheet_e2e.py` (2nd occurrence —
  Rule of Three). Lift to a shared `conftest.py` fixture at the 3rd caller.
