---
name: 2026-07-24-investing-toolkit-tw-financial-ixbrl-2-32-1-post-ship-follow-ups
description: investing-toolkit TW financial iXBRL 2.32.1 — post-ship follow-ups
status: open
origin: TW financial iXBRL Phase-4 consumption arc (branch tw-fin-ixbrl-followups, 2026-07-24, 2.32.1 — renumbered from 2.31.1 after main advanced to 2.32.0); 2882.TW live render dogfood.
---

- Origin: TW financial iXBRL Phase-4 consumption arc (branch tw-fin-ixbrl-followups,
  2026-07-24, 2.32.1 — renumbered from 2.31.1 after main advanced to 2.32.0);
  2882.TW live render dogfood.
- What: (a) 🟢 **stale/over-broad `_status.failed_sections`** — the 2882.TW memo-fetch
  emits `_status.failed_sections: ["mops"]` while `mops.*` (company_basic + balance/income/
  cash) is fully populated with legible data; the flag looks stale/over-broad. Pre-existing
  in `pack_tw`'s `_status` computation, out of the DCF-render arc; a memo would surface it in
  Limitations. Reconcile the flag with actual section presence on next `pack_tw` touch.
  (b) 🟢 **em-dash grep fragility** — the pin phrase `DCF: N/A — financial sector` uses an
  em-dash (`—`); the orchestrator acceptance grep and every render surface share the one
  pinned string (internally consistent, cannot drift without a deliberate edit), but a future
  hand-edit typing a hyphen would silently break the grep. Consider a hyphen-tolerant match
  or a stable marker token if the phrase is ever re-typed. (c) 🟢 Rule-of-Three tail (below
  threshold, next-touch): `_derive_total_debt` now == `_sum_concepts(...)` verbatim (2 sites),
  and two `twse_ixbrl_canonical.py` builder loops (~:350/:528) + `_derive_fcf` still inline the
  `sorted→values→meta` shape `_ordered_values_meta` abstracts — route through the helper when
  next touched. (d) 🟢 `test_twse_ixbrl_fixtures.py` module docstring still says "these 7
  fixtures" though it now also exercises the -ci 2330 fixture; the 2330 fact-count literal
  `2002` is a 3rd pin copy — touch-up on next edit.
