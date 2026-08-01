---
name: 2026-07-18-investing-toolkit-memo-wiring-2-23-0-post-ship-follow-ups
description: investing-toolkit memo-wiring 2.23.0 — post-ship follow-ups
status: OPEN
origin: memo quarterly-KPI wiring slice (branch feat-memo-quarterly-kpi-wiring, 2026-07-18); per-task + whole-branch review ship-as-debt rulings.
start: next touch of `report-equity-memo/references/schema-phase4-input-bundle.json`, `analysis-kpi/scripts/kpi_memo_feed.py`, or `data-markets/scripts/pack.py`.
---

- Start: next touch of `report-equity-memo/references/schema-phase4-input-bundle.json`,
  `analysis-kpi/scripts/kpi_memo_feed.py`, or `data-markets/scripts/pack.py`.
- Origin: memo quarterly-KPI wiring slice (branch feat-memo-quarterly-kpi-wiring,
  2026-07-18); per-task + whole-branch review ship-as-debt rulings.
- What: (a) the one 🟡 — schema↔envelope coupling unguarded: nothing asserts
  `schema-phase4-input-bundle.json`'s kpi_quarterly_feed required-set equals
  the envelope `build_quarterly_memo_feed` actually emits (both sides pinned
  separately, can drift green-green) — add a coupling assertion or route a
  real feed through the B2 validator; (b) pack.py PEP 723 header declares no
  deps while pack_us direct-imports sec_edgar_client — bare `uv run pack.py`
  crashes on ModuleNotFoundError for EVERY networked pack incl. Phase 1
  memo-fetch (pre-existing, live-confirmed 2026-07-18); cheap hardening =
  add requests/edgartools pins to pack.py's header (touches all packs, needs
  its own review); (c) 🟢 nits: build-quarterly CLI exit-1 arm untested;
  non-dict series entries raise AttributeError not ValueError; `_is_blank`
  dup vs tier-① idiom; mixed-company sample fixture caveat; jsonschema-absent
  silent skip in test_pack_schemas; no socket guard in chain test; module-scoped
  sys.modules fixture no teardown; `${MEMO_DATE}` defined only in Phase 3.5;
  doc wording "concept" vs real field `kpi_id` in schema prose + CHANGELOG.
