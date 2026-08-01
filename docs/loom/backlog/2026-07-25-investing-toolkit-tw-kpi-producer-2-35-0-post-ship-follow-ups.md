---
name: 2026-07-25-investing-toolkit-tw-kpi-producer-2-35-0-post-ship-follow-ups
description: investing-toolkit TW KPI producer 2.35.0 — post-ship follow-ups
status: OPEN
origin: TW-market kpi_store producer (branch tw-kpi-store, 2.35.0, 2026-07-25); brief/plan `docs/loom/{specs,plans}/2026-07-25-tw-kpi-store-producer.md`.
start: next substantive touch of `analysis-kpi/scripts/kpi_tw.py` / `kpi_tw_ingest.py`, or the next TW-KPI-lane arc.
---

- Start: next substantive touch of `analysis-kpi/scripts/kpi_tw.py` /
  `kpi_tw_ingest.py`, or the next TW-KPI-lane arc.
- Origin: TW-market kpi_store producer (branch tw-kpi-store, 2.35.0, 2026-07-25);
  brief/plan `docs/loom/{specs,plans}/2026-07-25-tw-kpi-store-producer.md`.
- What:
  (a) 🟢 **glue-free TW envelope production** — a `pack_tw` verb emitting
  `{canonical, facts, coords}` (mirroring `pack_us.pack_kpi_quarterly`), so TW is
  "ticker→tearsheet without glue" like US. Today `run_pipeline` emits `canonical`
  but NOT `facts` (the `as_of` authorisation date lives in a fact), so the ingest
  consumes an envelope the caller assembles; the dogfood assembles it by hand. A
  data-markets envelope task closes this.
  (b) 🟢 **`tw_canonical_to_points` `zip(values, periods)` truncation** — a
  `zip` silently truncates if the two lists diverge in length; a len-assert would
  fail loud instead. Unreachable today (the canonical layer builds values and
  periods in parallel), but a future canonical change could desync them silently.
  (c) 🟢 **mirrored injective guard keys on bare field-name** — the collision
  guard keys `claimed_by` on the bare field-name, not `(statement, field)`. A
  field-name recurring across two statements would RE-CLAIM (merge) rather than
  raise. Unreachable today (the emitted field names are disjoint across
  statements); key on `(statement, field)` when a real cross-statement name
  appears.
  (d) 🟢 **wire the TW KPI store into report-equity-memo Phase 3.5** — like the
  US chain feeds the memo's quarterly-KPI section, the TW store should surface in
  the TW memo path. Deferred (out of this producer-only arc).
  (e) 🟢 **point `unit` is per-field best-effort** — `tw_canonical_to_points`
  copies `unit` from `_meta[field].get("unit")`; a canonical field whose `_meta`
  lacks `unit` silently yields `unit=None` (same class as the shipped TWD fix,
  per-field). Non-fatal (the dogfood path carried TWD); consider a fail-loud or a
  canonical-wide TWD default when a TW field's unit is absent.
