---
name: 2026-07-25-investing-toolkit-top-line-revenue-lane-2-36-0-post-ship-follow-ups
description: investing-toolkit top-line revenue lane 2.36.0 — post-ship follow-ups
status: open
origin: company total (top-line) revenue arc (branch feat-total-revenue-lane, 2026-07-25, 2.36.0). Brief `docs/loom/specs/2026-07-25-company-total-revenue.md`, plan `docs/loom/plans/2026-07-25-company-total-revenue.md`. Every item below is a per-task review ruling that was deliberately NOT closed in-branch, with the reason recorded — none is an oversight.
start: next touch of `analysis-kpi/scripts/kpi_xbrl_ingest.py`, `analysis-kpi/scripts/kpi_store.py`, `analysis-kpi/scripts/kpi_xbrl.py`, or `data-markets/scripts/sec_edgar_client.py`.
---

- Start: next touch of `analysis-kpi/scripts/kpi_xbrl_ingest.py`,
  `analysis-kpi/scripts/kpi_store.py`, `analysis-kpi/scripts/kpi_xbrl.py`, or
  `data-markets/scripts/sec_edgar_client.py`.
- Origin: company total (top-line) revenue arc (branch feat-total-revenue-lane,
  2026-07-25, 2.36.0). Brief `docs/loom/specs/2026-07-25-company-total-revenue.md`,
  plan `docs/loom/plans/2026-07-25-company-total-revenue.md`. Every item below is
  a per-task review ruling that was deliberately NOT closed in-branch, with the
  reason recorded — none is an oversight.
- What:
  (a) 🟡 **`_q4_basis_mismatch_reason` guards the map ENTRY, not the field**
      (`kpi_xbrl.py:989,997`). A present calendar entry whose `fiscal_year_end`
      is `None` compares EQUAL to another such entry, so two unstated calendars
      silently affirm "shared basis" — the opposite of this repo's fail-loud
      posture. Unreachable today (Lane A emits no 9-month YTD rows and
      `derive_q4_points` takes one pack's map) but `pack_us.py:1017-1019` already
      merges two lanes' calendars into one envelope, which is the shape that
      reaches it. Fix is a field-level guard, consumer-side. TRIPWIRE (whole-branch
      review 2026-07-25): the unreachability expires the moment the multi-granularity
      arc makes Lane A quarterly — which the brief's §Out of Scope explicitly plans —
      so prefer a guard in the entry over relying on the reachability note.
  (b) 🟡 **`_SOURCE_FORM_BY_FOCUS` cannot express an amendment** (`kpi_xbrl.py:231-233`).
      Because focus→form maps `FY` to the literal `"10-K"`, the top-line backfill
      must skip `10-K/A` carriers rather than mislabel them — and a 10-K/A is the
      canonical carrier of a RESTATED annual figure. So an amended fiscal year
      keeps its ORIGINAL number in the backfill lane and never learns the
      correction. This is a value-staleness gap, not a coverage gap. Fix is
      consumer-side vocabulary, then widen the producer allowlist; pinned today by
      a red test so a producer-only widening cannot slip through.
  (c) 🟡 **Lane B's envelope contract is unverified at the seam.** The two-lane e2e
      (`tests/analysis/test_top_line_two_lane_e2e.py`) runs Lane A through its real
      producer but hand-builds Lane B's envelope, because `pack_kpi_quarterly`
      reaches its facts through edgartools `Filing` objects an offline suite cannot
      stub. The envelope-contract defect class this arc caught on Lane A is
      therefore NOT covered on Lane B — the same blind spot, one lane over. The
      file states the asymmetry; closing it needs a fixture strategy for the
      per-filing lane.
  (d) 🟡 **`summarize_concept` is currency-blind** (`sec_edgar_client.py:281`):
      `units.get("USD") or next(iter(units.values()), [])` returns whatever unit
      exists when USD is absent, and `float(row["value"])` then pushes it into a
      USD-assumed store with no error — a number carries no unit. Found while
      probing carrier forms: TM and HMC report in JPY. Blocked today only
      incidentally, because those filers' rows are all 20-F and the carrier-form
      allowlist drops them. Pre-existing, not introduced by this arc.
  (e) 🟢 **Promote `kpi_store._dedup_key` / `_canonical_value` to public aliases.**
      `kpi_xbrl_ingest`'s disagreement guard reaches across into both private
      symbols — correct, because a local copy would silently drift from the store's
      own definitions, but the encapsulation is owed. A zero-behaviour alias beside
      each private definition plus four call-site flips; deliberately deferred
      because `kpi_store.py` was outside the arc's declared file scope.
  (f) 🟡 **In-batch disagreement is unguarded.** Two conflicting flat facts sharing
      a dedup key WITHIN one pack still reach `kpi_store.append`'s silent
      first-record-wins (`kpi_store.py:321-325`). The shipped guard is store-aware
      (cross-call) only. Unreachable through either producer today — one winner per
      filing upstream — so it would require a producer bug; ~5 lines to close by
      accumulating validated keys in-batch. RAISED 🟢→🟡 by the whole-branch
      review 2026-07-25: the reachability reason is sound, but cheap hardening
      inside a file this arc already owns should not hide behind 'unreachable
      today' when it guards the exact invariant the arc exists to protect on a
      one-way door.
  (g) 🟢 **`coverage.skipped_rows` merges gap types under one key** in the backfill
      lane, discriminated by `type`, where this module's convention elsewhere is one
      coverage key per gap type (`unclassifiable_periods`, `fetch_failures`,
      `axis_exclusions`, `top_line_gaps`).
  (h) 🟢 **`"accessions": [None]` violates the ONE DQC flag schema** when a skip
      flag names a row with no accession (`assert_dqc_schema`, `kpi_xbrl.py:270-280`,
      requires non-empty strings). Pre-existing across sibling flags in
      `sec_edgar_client.py`, not introduced here.
  (i) 🟢 **`kpi_tw_ingest` has no `## CLI (...)` section in
      `analysis-kpi/references/cli-reference.md`** — it is the only one of the
      twelve indexed persistence/compute scripts missing one (the file documents
      eleven). Pre-existing since 2.35.0 (the TW iXBRL arc), surfaced while
      reconciling the index count during this branch's close-out. Deliberately NOT
      closed here: writing it means reading the shipped `kpi_tw_ingest.py` CLI and
      documenting its real flags/exit codes, which belongs to the TW arc's file
      scope, not the top-line lane's. `analysis-kpi/SKILL.md` now DISCLOSES the gap
      in the CLI-reference sentence rather than stating a count that is wrong about
      one referent or the other — so closing this item also means deleting that
      disclosure clause.
  (l) 🟢 **A kpi_id collision aborts BOTH lanes for the WHOLE pack** — FILED AS
      DELIBERATE, not a defect. `ingest_pack` builds every point before appending
      any (`kpi_xbrl_ingest.py`, `_claim_kpi_id` raises during selector mapping),
      so one colliding dimensional signature refuses the pack's top-line lane too:
      the live INTC Lane B run of 2026-07-25 landed ZERO of 473 facts on a single
      Intel-Foundry signature collision. That all-or-nothing blast radius is arc
      (d)'s shipped design and the alternative is worse — partial ingest would
      leave an append-only store holding one lane of a pack, and the store's dedup
      key would silently keep the FIRST of two colliding series, which is exactly
      the one-way-door data loss the guard exists to prevent
      (`docs/loom/memory/derived-durable-id-slug-is-a-lossy-one-way-door.md`).
      Fail-loud beats a silent discard on a durable store. Revisit ONLY if a real
      pack is found where a genuinely-distinct collision coexists with an
      otherwise-healthy top-line lane AND the operator cannot re-run after fixing
      the producer; the fix would then be per-lane isolation of the claim map, not
      a weaker guard. Raised by the whole-branch review 2026-07-25 while closing
      the over-fire that made the blast radius visible.
  (j) 🟡 **The New-Year guard misses a two-sided divergence along the dei NOMINAL
      fiscal-year end** (`sec_edgar_client.py::_is_near_new_year_boundary`). The
      shipped guard is one-sided along `period_end` — correct, and it recovered the
      whole December-filer backfill — but the two lanes' labels diverge along a
      SECOND axis the guard cannot see: the filing's `dei:CurrentFiscalYearEndDate`,
      which drifts per filing for 52/53-week filers. When that nominal sits in early
      January and the row's actual end fell back into late December, Lane B
      (`_derive_fiscal_label`) walks FORWARD to the January nominal and answers the
      next year while Lane A answers the period-end year; the guard does not fire
      and no coverage reason is emitted. Measured against both real label functions
      (2026-07-25): `2024-12-28` / nominal `--01-03` → Lane A 2024, Lane B 2025 FY;
      `2025-12-31` / `--01-02` → Lane A 2025, Lane B 2026 FY. Cost is a MISLABELLED
      year, not an absent one — the two lanes then key one fiscal year two ways and
      the store shows a spurious restatement dagger from a single filing, which is
      exactly the failure the two-lane e2e's docstring names.
      **Why Lane A cannot close it alone:** the guard's whole premise is that this
      lane has no dei calendar, and its `companyconcept` rows carry only
      `{start, end, value, accn, form, fy, fp, filed}` (`summarize_concept`). None of
      those varies with the nominal — a 52/53-week year is 364/371 days whatever the
      nominal — and `fy`/`fp` are the CARRYING filing's focus, not the fact's
      (measured over all 777 `concept_*.json` files in the local EDGAR cache
      2026-07-25 — split across two cache-envelope payload shapes, 480 files with
      the body at `data` and 297 nested one level deeper at `data.data`; a re-run
      must cover both or it silently drops whichever shape it doesn't parse —
      predicate stated so it can be re-run: us-gaap `companyconcept` payloads, rows
      as `summarize_concept` reshapes them, `start`/`end`/`accn`/`filed` present and
      `fy` an int, `end - start` within 340-380 days — 10175 of 15276 such annual
      rows, 66.6%, carry an `fy` differing from `end`'s own calendar year). So a
      late-December row from a January-nominal filer is indistinguishable here
      from a plain December filer's row, and narrowing the guard on this axis
      is not available to the producer.
      **What would close it:** the same consumer-side work as item (a) — both reduce
      to Lane A having no calendar, so the fix belongs where the two lanes' calendars
      MEET (`pack_us.py:1017-1019` merges both into one envelope). Once Lane B's
      per-accession `fiscal_calendars` are in hand beside Lane A's facts, a consumer
      can re-label or quarantine a Lane A year whose Lane B calendar puts it in a
      different fiscal year. A producer-side alternative exists but is partial and
      was NOT taken: `fy` IS authoritative on a row that is its own filing's
      current-period fact, so grouping rows by accession could recover the nominal
      label for years whose own 10-K is still in the API's XBRL window (~2009+) —
      it does nothing for the older comparative-only years that are this lane's
      reason to exist, and it would mean reading `fy`, which this module forbids by
      name. Filed as its OWN item rather than folded into (a): they share a root
      cause but not a failure mode (that one silently affirms "shared basis" between
      two unstated calendars; this one mislabels a year) and not a fix site, and
      folding a live mislabeling hazard into an unreachable-today entry would bury
      it. Sequence it WITH (a) when the consumer-side calendar work is picked up.
      Documented at the four producer sites + `data-markets/SKILL.md` +
      `investing-toolkit/CHANGELOG.md` (2026-07-25) rather than left implied.
  (k) 🟢 **`_is_near_new_year_boundary` is misnamed** — it no longer means "near"
      (symmetric proximity), it means "has crossed into January". The docstring
      compensates; the name does not, and a symmetric-sounding name on an asymmetric
      guard is precisely the shape
      `docs/loom/memory/a-test-can-pin-behaviour-with-a-false-rationale.md` §2 tells
      us to hunt. Deliberately NOT renamed in the doc-only round that found (j): a
      coherent rename also drags the pinning test's NAME
      (`test_near_new_year_skip_leaves_lane_b_the_sole_authority`), a local in
      `test_sec_edgar_top_line_backfill.py:277`, and three narrative docstrings in
      `test_top_line_two_lane_e2e.py` (:71, :110, :396) — leaving any behind
      desynchronizes the vocabulary, which is its own drift surface. Behaviour-
      preserving; wants one sweep + a suite run, not a prose commit.
