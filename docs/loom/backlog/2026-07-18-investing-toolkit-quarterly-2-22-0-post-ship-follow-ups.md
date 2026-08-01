---
name: 2026-07-18-investing-toolkit-quarterly-2-22-0-post-ship-follow-ups
description: investing-toolkit quarterly 2.22.0 — post-ship follow-ups
status: OPEN
origin: scope-B quarterly rebuild (branch feat-operational-kpi-quarterly, 2026-07-18); whole-branch review PASS_WITH_NOTES ship-as-debt rulings + T9 spec-reviewer follow-up.
start: next touch of `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py` or `analysis-kpi/scripts/kpi_xbrl.py`.
---

- Start: next touch of `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  or `analysis-kpi/scripts/kpi_xbrl.py`.
- Origin: scope-B quarterly rebuild (branch feat-operational-kpi-quarterly,
  2026-07-18); whole-branch review PASS_WITH_NOTES ship-as-debt rulings +
  T9 spec-reviewer follow-up.
- What: (a) split `extract_dimensional_revenue` (~355 lines, the one 🟡);
  (b) thread the REAL `filing.form` string into the fact pack so the analysis
  layer stops inferring `source_form` from dei focus; (c) public alias for
  `_dimension_quarterly_absence` (cross-layer underscore bind); (d) call
  `assert_dqc_schema` at kpi_xbrl's data-layer-flag ingestion point (~:464);
  (e) 🟢 nits: selection-gap slot overwrite, literal 'None' in gap reason,
  accession-less 10-K coverage entry.
