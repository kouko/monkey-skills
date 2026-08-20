---
name: 2026-07-26-investing-toolkit-the-reconstruct-verb-inverts-the-pack-layering
description: investing-toolkit — the `reconstruct` verb inverts the pack layering
status: open
---

- **What.** `pack_us.py` is a Layer-1 I/O module, and the `reconstruct` verb
  there imports an analysis-layer function (`kpi_us_statement_shape.statements_for`)
  — the opposite of this repo's usual direction, where analysis calls data and
  never the reverse. The inversion is named in a comment at the site, so it is
  visible rather than silent.
- **Why it was accepted rather than fixed mid-arc.** It is a TWO-WAY door. The
  repo's convention crosses layers by SUBPROCESS, which is unavailable here:
  `statements_for` takes a live edgartools `Filing` object, which does not
  survive a JSON boundary. Restructuring inside the arc would have been a plan
  change improvised at implementation time.
- **The honest resolution, not yet decided.** The verb probably belongs in
  analysis-kpi, with data-markets supplying only acquisition
  (`sec_edgar_client._acquire_raw_filing`). That is a plan change and wants its
  own brief — it moves a shipped command surface, so the SKILL.md declaration
  and `SUPPORTED_PACKS` registration move with it.
- Re-trigger: the next arc that touches `pack_us.py`'s verb set or the
  analysis-kpi ↔ data-markets boundary; or a second analysis import landing in a
  Layer-1 module, which would make this a pattern rather than one exception.
