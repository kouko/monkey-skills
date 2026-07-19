# Plan: tw-ixbrl-ingestion (收斂版 ②)

Source brief: docs/loom/specs/2026-07-19-tw-ixbrl-ingestion.md
Total tasks: 6
Critical-path depth: 4 (≤5)   ← longest Dependencies chain: T1→T3→T5→T6
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-19)

## Conventions (from repo recon — apply to every task)

- Scripts dir: `investing-toolkit/skills/data-markets/scripts/`
- Tests dir: `investing-toolkit/tests/data/` ; fixtures: `investing-toolkit/tests/data/fixtures/`
- Offline test command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/ -q -m "not network"`
- House style: PEP 723 self-contained script header (`#!/usr/bin/env python3` + `# /// script`,
  pinned deps), `<name> — <purpose>` docstring + `Usage:` block, modern type hints
  (`dict[str,Any]`, `str | None`, `from __future__ import annotations`), NO dataclasses,
  `requests` for HTTP, `import cache_util`, `_log(stage,msg)` stderr logger, argparse CLI
  emitting JSON to stdout with `_error` envelopes.
- Prefer stdlib for parsing (`re` / `xml`) — do NOT add lxml; regex/`iterparse` over `ix:` tags
  is mandatory (DOM traversal silently drops ~85% of nested facts — see brief edge case #10).
- Golden fixture: TSMC 2330 2024Q3 consolidated = **2002 facts** (1552 nonFraction + 450 nonNumeric).

## Task 1 — Generic iXBRL fact parser
- Description: Parse a decoded TW iXBRL document into a list of normalized fact records —
  extraction via regex/`iterparse` over `ix:nonFraction`/`ix:nonNumeric` tags (never DOM),
  each record carrying `{concept (ns:localname), context_ref, raw_value, decimals, unit,
  period}`, with decimals scaling applied (`decimals=-3` → ×1000) and `context_ref` resolved
  to its period (instant or start/end) + entity.
- Module: `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py`
- Files touched:
  `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py`,
  `investing-toolkit/tests/data/test_twse_ixbrl_parser.py`,
  `investing-toolkit/tests/data/fixtures/twse_ixbrl_2330_2024Q3_C.html` (commit the saved Big5
  filing — copy from session scratchpad `tsmc_2330_2024Q3_C.ixbrl.html`)
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py` (fact-record shape reference)
  - `investing-toolkit/tests/data/test_sec_edgar_dimensional.py` (offline fixture-test pattern, FIXTURES resolution)
- Acceptance:
  - RED: `test_parse_tsmc_golden` — loading the fixture (`read_text(encoding="big5")`) and
    parsing yields **exactly 2002 facts**; a traced golden fact
    (`ifrs-full:CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome`) has its
    raw value scaled by the iXBRL `scale` attribute (scale-driven, NOT decimals-driven —
    `decimals` is precision metadata; T1 found `PercentageOfOwnership4` disproves decimals-driving)
    and a resolved period matching the 2024-Q3 context.
  - GREEN: parser returns the normalized fact list; count + golden-fact assertions pass; test
    is offline (no `network` marker).
- External surfaces: stdlib only (`re`/`xml.etree`) — no new dependency (house stdlib-preference).
- Dependencies: none
- Independent: true
- Brief item covered: "Layer A — Generic fact extraction … via iterparse/regex over ix: tags, not DOM"

## Task 2 — iXBRL fetch helper (URL / Big5 / not-found / season-fallback / retry)
- Description: Build the `t164sb01` request, fetch it (tier-agnostic: 上市/上櫃/興櫃/KY on one
  URL), decode Big5→str, cache via `cache_util`, detect the 98-byte "檔案不存在" body as an
  absence sentinel (not an error), iterate season fallback (98-byte at a season ⇒ try next;
  emerging-board primary Q2/Q4), and retry-with-backoff on HTTP 502.
- Module: `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_fetch.py`
- Files touched:
  `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_fetch.py`,
  `investing-toolkit/tests/data/test_twse_ixbrl_fetch.py`,
  `investing-toolkit/tests/data/fixtures/twse_ixbrl_notfound.html` (98-byte "檔案不存在" body)
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/mops_client.py` (`_cached_post` cache pattern, ~:262)
  - `investing-toolkit/skills/data-markets/scripts/cache_util.py` (`cache_path`/`load_cache`/`save_cache`)
  - `investing-toolkit/tests/data/test_sec_edgar_dimensional.py` (`sec_client` fixture stubbing `requests` via sys.modules, :44-60)
- Acceptance:
  - RED: `test_fetch_url_and_notfound` — `build_t164sb01_url(co_id="2330", year=2024, season=3,
    report_id="C")` returns the exact endpoint URL; feeding the 98-byte fixture body returns the
    not-found sentinel (not raw content); with `requests` stubbed, a 502-then-200 sequence
    retries and returns the decoded body.
  - GREEN: URL builder + not-found detection + retry pass offline (`requests` stubbed, no `network` marker).
- External surfaces: MOPS HTTP endpoint `mopsov.twse.com.tw/server-java/t164sb01` (network — live path guarded behind cache + stubbed in tests); `requests` (existing house dep).
- Dependencies: none
- Independent: true
- Brief item covered: "Fetch-layer requirements … one t164sb01 URL; season fallback; 502 retry-with-backoff"

## Task 3 — Canonical three-statement mapping (industrial `-ci`)
- Description: Map parsed statement-level facts (`tifrs-bsci-ci` BS+P&L, `tifrs-SCF` cash-flow)
  into the toolkit's canonical shape — three top-level keys `income_statement` / `balance_sheet`
  / `cash_flow`, each a value-list (most-recent-first) plus per-line `_meta`
  (`source_label`, `accounting_standard="tifrs"`, `unit="TWD"`). Financial `-fh` filers are
  out of scope here (deferred sub-arc) — a `-fh` root returns an explicit "unsupported-financial"
  marker, never a crash.
- Module: `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py`
- Files touched:
  `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py`,
  `investing-toolkit/tests/data/test_twse_ixbrl_canonical.py`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/pack_tw.py` (deferred stub `_build_canonical_from_yf_financials_tw` :205-311 — target canonical shape + `_YF_LABEL_MAP_TW` :191)
  - `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py` (fact-record input shape — from Task 1)
- Acceptance:
  - RED: `test_canonical_ci_from_facts` — feeding the TSMC fixture's parsed facts yields a
    canonical dict whose `income_statement`/`balance_sheet`/`cash_flow` value-lists are
    non-empty, each line's `_meta.accounting_standard == "tifrs"` and `unit == "TWD"`, and the
    revenue line traces to the fixture's `tifrs-bsci-ci` revenue fact value; a `-fh` fact set
    returns the unsupported-financial marker.
  - GREEN: canonical mapper passes offline against the fixture-derived facts.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Fill the deferred canonical builder (pack_tw.py:205-311) … industrial (ci)"

## Task 4 — Curated high-value note fields
- Description: Extract a curated named-concept set from the parsed facts (NO general table
  reconstruction): financial-instruments-by-measurement-category (FVOCI / FVTPL / amortized-cost,
  current + non-current), Mainland-China accumulated investment + MOEA ceiling, related-party
  total receivable/payable balances + aggregate purchase flow, employee-benefit short-term
  expense + defined-benefit net liability. (Endorsement/guarantee DEFERRED mid-impl —
  ix:tuple-structured, no clean aggregate leaf; see Decision Log. Curated set = 4 categories.)
  Emit `{field:
  {value, concept, period}}`; absent concepts omitted (not zero-filled).
- Module: `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py`
- Files touched:
  `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py`,
  `investing-toolkit/tests/data/test_twse_ixbrl_notes.py`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py` (fact-record input — from Task 1)
  - `docs/loom/specs/2026-07-19-tw-ixbrl-ingestion.md` (§Annual verification — the ~5 curated categories + evidence values)
- Acceptance:
  - RED: `test_curated_notes_tsmc` — from the TSMC fixture's facts, the curated dict contains
    `financial_assets_fvoci` (scaled ≈ 1,896.5億 = 189,650,000 thousand-TWD magnitude) and
    `mainland_china_accumulated_investment` (≈ 494.6億) with correct `concept`/`period`; a
    concept absent from the fixture is omitted from the dict, not present as 0.
  - GREEN: curated extractor passes offline against the fixture.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Surface a curated ~5–10 high-value note fields as named concepts"

## Task 5 — iXBRL client CLI (assemble fetch → parse → canonical + notes → JSON)
- Description: A PEP 723 client script exposing an argparse CLI (`--co-id --year --season
  --report-id`) that fetches (Task 2), parses (Task 1), builds canonical (Task 3) + curated
  notes (Task 4), and emits one JSON object to stdout (`{canonical, notes, _meta}`) with
  `_error` envelope on failure — the `run_client`-invokable entry point.
- Module: `investing-toolkit/skills/data-markets/scripts/twse_ixbrl.py`
- Files touched:
  `investing-toolkit/skills/data-markets/scripts/twse_ixbrl.py`,
  `investing-toolkit/tests/data/test_twse_ixbrl_cli.py`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py` (argparse CLI + JSON-stdout + `_error` envelope pattern)
  - `investing-toolkit/skills/data-markets/scripts/twse_ixbrl_fetch.py` / `_parser.py` / `_canonical.py` / `_notes.py` (the modules it composes — Tasks 1-4)
- Acceptance:
  - RED: `test_twse_ixbrl_cli` — invoking the CLI with fetch stubbed to return the fixture body
    emits valid JSON whose `canonical` has the three statement keys and `notes` has the curated
    fields; a fetch not-found sentinel yields a JSON `_error` envelope, not a traceback.
  - GREEN: CLI composes the pipeline offline (fetch stubbed) and emits the expected JSON shape.
- External surfaces: emits the client JSON contract consumed by `pack_tw.run_client` (internal cross-script contract).
- Dependencies: Tasks 2, 3, 4 complete first
- Independent: false
- Brief item covered: "Build a TW iXBRL ingestion path that mirrors the sec_edgar_client.py shape"

## Task 6 — Wire iXBRL client into pack_tw
- Description: Call `twse_ixbrl.py` via `run_client` inside `pack_memo_fetch` (and the canonical
  path), wrapping with `wrap("A","twse_ixbrl",...)`; replace the deferred
  `_build_canonical_from_yf_financials_tw` call site with the real iXBRL canonical; add the new
  `twse_ixbrl` group key to the `out` init dict + the Tier-A partial-check loop. No new pack type
  (extends memo-fetch).
- Module: `investing-toolkit/skills/data-markets/scripts/pack_tw.py`
- Files touched:
  `investing-toolkit/skills/data-markets/scripts/pack_tw.py`,
  `investing-toolkit/tests/data/test_data_markets_tw.py`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/pack_tw.py` (`run_client` :140, `wrap` :172, `pack_memo_fetch` :404, stub :205-311, out-init :339-349)
  - `investing-toolkit/tests/data/test_data_markets_tw.py` (existing TW pack assertions + `run_client` stubbing pattern)
- Acceptance:
  - RED: `test_memo_fetch_wires_ixbrl_canonical` — with `run_client("twse_ixbrl.py",…)` stubbed
    to return a canonical+notes payload, `build_pack("memo-fetch", ["2330.TW"])` output carries
    a `twse_ixbrl` group whose canonical `income_statement` is non-empty and provenance-wrapped
    (`_meta` tier "A", source "twse_ixbrl"); the deferred-stub call site no longer runs for TW.
  - GREEN: pack output includes iXBRL canonical; full offline suite green
    (`… pytest investing-toolkit/tests/ -q -m "not network"`).
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "Fill the deferred canonical builder … wire into pack_tw's pack_memo_fetch"

## Notes

- Parallel waves: L1 = {T1, T2} (disjoint files, no shared symbol); L2 = {T3, T4} (both consume
  T1's fact-record shape but are mutually disjoint — canonical vs notes files). T5 joins T2/T3/T4;
  T6 follows T5.
- Coverage self-check (scenario→task) N/A — input is a brainstorming brief, not a loom-spec change-folder.
- Kickoff decision: parser library → stdlib `re`/`xml.etree`, NOT lxml (avoids a new pinned dep; regex/iterparse mandated to dodge the DOM-drop gotcha).
- Kickoff decision: integration surface → extend `memo-fetch` (not a new pack type) — user-approved 2026-07-19. TW iXBRL canonical + notes flow into the existing memo-fetch pack.

## Decision Log (two-way-door calls — agent-decided, late-vetoable)

- **Module layout**: 5 focused single-purpose scripts (`_parser`/`_fetch`/`_canonical`/`_notes`/
  `twse_ixbrl` CLI) over fewer fat modules — enables parallel SDD waves + matches house
  "plain functions per file" style. Reversible refactor; no product consequence.
- **Parser impl**: stdlib `re`/`xml.etree`, no lxml dep. Swappable behind the parser interface.
- **Fixture**: commit the full ~800KB Big5 TSMC filing (keeps the exact 2002-fact count anchor
  that catches the DOM-drop bug). Precedent: 193KB/284KB fixtures already committed. Trimmable later.
- **Endorsement/guarantee curated field DEFERRED** (mid-impl decision, 2026-07-19, T4 review):
  TW iXBRL tags endorsement/guarantee as per-counterparty `ix:tuple` rows (same-`contextRef`
  duplicates with differing values — no clean aggregate leaf), so a single "limit"/"used" number
  needs the note-table reconstruction that is out of scope (brief §Annual verification). It was
  also the weakest curated category (SITUATIONAL, trivial/zero values for blue-chips). Curated
  set reduced to **4 categories** (financial-instruments / Mainland-China / related-party /
  employee-benefit). Two-way / late-vetoable — addable via the note-reconstruction sub-arc.
- **iXBRL-failure degradation → yfinance stub** (mid-impl decision, 2026-07-19, T6 quality 🔴):
  the iXBRL canonical was missing `total_debt`/`cash`/`capex`/`ebit`/`fcf` (which `analysis-dcf`
  requires — absence silently zeroed net_debt for every TW ticker, overstating equity value).
  Fix: (a) canonical builder now emits those fields; (b) on iXBRL `_error` (both period attempts),
  `pack_memo_fetch` degrades to the retained yfinance stub rather than empty `{}` — preserving
  no-regression behavior (iXBRL when available, yfinance-derived otherwise). Two-way / late-vetoable.
- **total_debt = full ST + LT interest-bearing debt** (whole-branch review remediation, user-approved):
  the first canonical cut was long-term-debt-only (understated net_debt → overstated DCF equity, and
  mismatched the yfinance-stub fallback which sums ST+LT). Fixed: `_DEBT_CONCEPTS` = 3 LT +
  4 ST concepts, all **verified against real 2330 (ST-debt absent, net-cash) + 1301 (Formosa,
  ST-debt present — total_debt 136.6B) iXBRL fixtures** (1301 added as the 2nd `-ci` fixture).
  The one permanent exclusion is the unsplit non-debt grab-bag `tifrs-bsci-ci:LongtermLiabilitiesCurrentPortion`.
  LOOM-SIMPLIFY marker removed (ceiling met). Definitionally aligned with the yfinance-stub path.

- Deferred (NOT in this plan, per brief §Decision, §Annual verification, and §Out of Scope):
  financial `-fh` canonical/notes, parent-only statements, full note-table reconstruction engine,
  US-style dimensional KPI pack.
- Amendment after PASS: citation above corrected (§Out of Scope → §Decision/§Annual verification)
  and verdict flipped to PASS; additive/schema-safe (no task, field, or DAG change) — re-review skipped.
