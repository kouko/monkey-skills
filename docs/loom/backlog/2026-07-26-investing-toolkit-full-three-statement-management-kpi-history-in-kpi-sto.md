---
name: 2026-07-26-investing-toolkit-full-three-statement-management-kpi-history-in-kpi-sto
description: investing-toolkit — full three-statement + management-KPI history in kpi_store
status: OPEN
start: READY. The `kpi_id` identity arc it depended on shipped as 2.37.0 (branch `feat-kpi-id-consolidation-axis`); that ordering was a real dependency, not politeness — see §Sequencing.
---

- Start: READY. The `kpi_id` identity arc it depended on shipped as 2.37.0
  (branch `feat-kpi-id-consolidation-axis`); that ordering was a real dependency,
  not politeness — see §Sequencing.
- **The container is already right; only the feed is missing.** Grounding:
  - `report-kpi-tearsheet` is metric-AGNOSTIC — one row per `kpi_id`, periods as
    columns, whatever the store holds (`report-kpi-tearsheet/SKILL.md`). It never
    needs to learn about statements or operational KPIs.
  - `kpi_store` is bitemporal, so a restated line item keeps both vintages — the
    property that makes it an analysis substrate rather than a snapshot. Downstream
    analysis reads `kpi_store dump/query`, NOT the tearsheet (the tearsheet is a
    human one-pager over the same data).
  - **The TW producer already proves the shape**: `kpi_tw._KPI_FIELDS`
    (`kpi_tw.py:33-50`) writes a 15-field three-statement spine (revenue,
    gross_profit, operating_income, pretax_income, net_income, eps_basic,
    total_assets, total_liabilities, total_equity, cash, operating/investing/
    financing_cash_flow, capex, fcf) across `_STATEMENTS` (`:53`) into the same
    store the US dimensional producer writes to.

### Sub-arc (a) — US three-statement producer (mirror the TW lane)

- **Gap**: the US side computes canonical statements but never STORES them.
  `DCF_CONCEPT_MAPPING` (`pack_us.py:125-175`) is **14 fields chosen for DCF**,
  assembled into `income_statement` / `cash_flow` / `balance_sheet` inside
  `pack_memo_fetch` (`pack_us.py:939-941`) — and no caller of `kpi_store.append`
  consumes a memo-fetch pack (verified 2026-07-25 across every producer in
  `analysis-kpi/scripts/`). So every memo run re-fetches and accumulates nothing.
- **Cheap part**: the raw source is already fetched and cached — `action_facts`
  without `--concept` returns the filer's full concept inventory
  (`sec_edgar_client.py:695-700`, names + counts, values only per-concept). No new
  data layer.
- **Hard part, and the real work**: concept → line-item normalization. Statement
  hierarchy, sign conventions, and **subtotal reconciliation** (components must add
  back to the reported subtotal). Without the add-back check this lane is a silent-
  lie generator — a wrong mapping is invisible in a rendered table.
- **Identity**: follow the TW precedent — `kpi_id` from a repo-CANONICAL field slug,
  never the filer's raw concept string (a filer's tagging changes across years;
  a concept-keyed id fragments the series — `docs/loom/memory/derived-durable-id-
  slug-is-a-lossy-one-way-door.md`, and the 2.36.0 `total_revenue` decision).
- Open scope question for the brief: 14 DCF fields (parity with today) vs the TW
  15-field spine (cross-market comparability) vs a genuinely full statement. The
  spine is the likely smallest end state; a full statement is a different arc.

### Sub-arc (b) — management / non-financial KPI wiring

- **Gap**: the machinery shipped, the user path did not. `kpi_prose_candidates`
  (Part 1, 2.28.0) + number robustness (Part 2, 2.29.0) produce verbatim-anchored
  prose KPI candidates and `commit_to_store` (`kpi_prose_candidates.py:719`) appends
  them to the SAME store — but nothing is SKILL-wired, so the capability is
  unreachable from a conversation.
- **Fail-closed by design, keep it**: `commit_to_store(confirmed=False)` writes
  NOTHING without an explicit human confirm-all. Wiring must expose that confirm
  step, never route around it.
- **Blocked on**: Part 3 (lifecycle / re-verification / table-vs-prose and
  prose-vs-prose conflict, surface-version marker) — scoped in
  §"非金錢營運 KPI 自動化" above. Do not re-scope it here (SSOT).

### Sub-arc (c) — rendering the annual + quarterly continuum

- Already filed in full as §"KPI tearsheet — multi-granularity + per-market period
  menu (OPEN)" — sub-quarter classifier, per-market granularity menu, discrete-vs-
  cumulative axis, separate views per granularity. **Pointer only, do not restate.**
- Relevance here: US annual and quarterly each render correctly today; a MIXED
  table interleaves granularities. Once (a) lands, a company's store holds far more
  rows and the interleave stops being cosmetic.

### Sequencing (the dependency, stated)

1. `kpi_id` identity arc — **prerequisite for (a), and it SHIPPED as 2.37.0.** (a)
   multiplies stored series per company by roughly an order of magnitude (statement
   fields × periods, later × segment dimensions). Collision probability in a lossy
   id derivation rises with the number of distinct signatures, and a collision
   aborts an entire pack. Scaling the feed before fixing identity would have scaled
   the abort surface with it. The 2.37.0 close-out dogfood also showed why this
   ordering mattered concretely: JNJ's 4-axis signatures put the series FILENAME
   within 12 bytes of the OS limit, and (a)'s statement fields add more signatures
   per company, not fewer.
2. Sub-arc (a) — the largest capability gain per arc, and it has a worked TW
   precedent to mirror rather than design from scratch.
3. Sub-arc (c) — becomes user-visible pressure only after (a) fills the store.
4. Sub-arc (b) — independent of (a) and (c); ordering against them is a priority
   call, not a dependency. Blocked only on its own Part 3.

### Evidence log

- 2026-08-10 audit: sub-arc (a) delivered by PR #619 (2.38.0) —
  `kpi_us_statements_ingest.py` is the US envelope→points→`kpi_store.append`
  analog of the TW lane, and `kpi_spine_view.py`'s `SPINE_FIELD_CHAINS` defines
  the 14-field US spine. Remaining scope narrows to (b)+(c); status stays OPEN.
