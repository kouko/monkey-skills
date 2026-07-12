# Plan: US SEC narrative capability (edgartools migration)

**Source brief**: docs/loom/2026-07-12-us-sec-primary-source-layer/specs/narrative/spec.md
**Total tasks**: 12
**Critical-path depth**: 5 (≤5 ✓)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-07-12; 14/14, depth 5 verified)

> **Input**: loom-spec change-folder `2026-07-12-us-sec-primary-source-layer`, capability `narrative`
> (21 scenarios / 11 Requirements). Bound via Layer 0 (explicit handoff). Validator `exit 0`.
> Traceability is by stable join key `<change-id> / Requirement: <name> / Scenario: <name>`
> (point-don't-copy — the spec is SSOT; this plan links back, never duplicates the delta).
> Full-coverage verified by `check_scenario_coverage.py` (see Notes).
>
> All 12 tasks touch the single module `sec_edgar_client.py` (+ its new test file), so every task is
> `Independent: false` (shared write set) and SDD dispatches them sequentially. The DAG is wide-but-
> shallow: acquisition (T1→T2) then a fan-out of segmentation / emission / compliance tasks, joined by
> the CLI-contract task (T12) at depth 5.

## Task 1 — Declare edgartools dependency + reject fetch when SEC identity unset

- **Description**: Add `edgartools` to `sec_edgar_client.py`'s PEP-723 inline `# /// script` dependency block, and configure the edgartools client identity from the existing `USER_AGENT` constant at entry. If no compliant `<name> <email>` identity is configured, the narrative acquisition path MUST reject before issuing any network request — edgartools does its own HTTP, so it must inherit the same SEC fair-access identity the legacy `_sec_get` already enforces, not a library default.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/conftest.py`
- **Acceptance**:
  - **RED**: `investing-toolkit/tests/data/test_sec_narrative.py::test_acquire_rejects_when_identity_unset` — with edgartools identity unconfigured, the acquisition entry returns an error slot (or raises a typed error) *before* any network call is attempted (assert no HTTP is issued, e.g. via a patched transport that fails the test if hit).
  - **GREEN**: `edgartools` is declared in the PEP-723 block and `uv run sec_edgar_client.py --help` resolves it; identity is set from `USER_AGENT` at entry; missing/empty identity → loud pre-send rejection.
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — identity configuration `edgar.set_identity(user_identity)` / env `EDGAR_IDENTITY` — grounding: edgartools `edgar/core.py` + `docs/configuration.md` (captured 2026-07-12; see Notes §edgartools grounding). ⚠ edgartools does NOT fail-fast on unset identity — `get_identity()` interactively prompts, then raises `TimeoutError` after ~60s — so OUR pre-send guard (check identity before calling edgartools) is the load-bearing enforcer of this scenario, not the library.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: SEC EDGAR fair-access compliance / Scenario: Missing User-Agent is rejected before send`

## Task 2 — Acquire 10-K/10-Q/8-K filing via edgartools (success + resolution/form error classes)

- **Description**: Replace the raw-HTML `fetch_narrative` acquisition front-half with an edgartools-based `acquire_filing` that, given a ticker/CIK (+ form filter) or an accession, returns a filing reference carrying accession, CIK, form, filingDate, period_of_report, primaryDocument, and a reconstructable SEC Archives URL. An unresolved ticker/CIK returns a loud error slot naming the identifier (never a silent empty result); a resolved filer that never filed the requested form returns a "form not available" result *distinct* from a resolution error.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`, `investing-toolkit/tests/data/test_data_markets_live.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/tests/data/test_data_markets_live.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_acquire_filing[success]`, `[not_found]`, `[form_unavailable]` (parametrized) — success returns a ref with all six provenance fields + reconstructable URL; not-found → error slot naming the unresolved identifier; form-unavailable → loud "form not available" distinct from the resolution-error class. PLUS network-marked `test_data_markets_live.py::test_edgartools_acquire_real_10k_shape` (`@pytest.mark.network`) capturing the REAL edgartools filing attribute shape.
  - **GREEN**: `acquire_filing` returns the provenance-bearing ref on success and two distinct loud error classes on failure; the live test confirms the real producer shape, and the offline unit mocks mirror THAT captured shape (fixtures-mirror-producer-shape — never hand-invent the edgartools object). ⚠ not-found is UNVERIFIED as an exception — empirically a never-filed form yields an EMPTY `Filings` (so `.latest()` returns `None`), not a raise; test against the empty/None result, do not assume an exception type.
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — acquisition `edgar.Company(ticker).get_filings(form=...).latest()` + `edgar.get_by_accession_number(acc)`; Filing attrs `accession_no`, `cik`, `form`, `filing_date`, `period_of_report`, `primary_document`; Archives URLs `homepage_url` / `filing_url` (NO `.url`) — grounding: edgartools filing API docs + `edgar/attachments.py` (captured 2026-07-12; see Notes §edgartools grounding).
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Filing Acquisition via edgartools / Scenario: Successful filing acquisition`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Filing Acquisition via edgartools / Scenario: Ticker or CIK not found`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Filing Acquisition via edgartools / Scenario: Requested form type not available`

## Task 3 — Segment 10-K (Item 7 + Item 1A) and 10-Q (Item 2) via edgartools; loud slot on absent item

- **Description**: Segment a 10-K primary document into distinct Item 7 (MD&A) and Item 1A (Risk Factors) section objects, and a 10-Q into an Item 2 (MD&A) section object, using edgartools' typed section API rather than regex header detection. A form/item combination absent from this specific filing (e.g. Item 1A omitted under a permitted exception) yields a per-section error slot naming the missing item — never an empty or fabricated section.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_segment_10k_item7_and_item1a`, `::test_segment_10q_item2`, `::test_segment_absent_item_emits_error_slot` — 10-K emits distinct Item 7 + Item 1A section objects (each with its own item id + non-empty extracted text); 10-Q emits an Item 2 section object; a requested-but-absent item emits a per-section error slot naming the missing item.
  - **GREEN**: segmentation for 10-K/10-Q runs through the edgartools section API; each present item is its own section object; absent item → named error slot (no empty/fabricated section). ⚠ a missing item returns `None` from the convenience property (edgartools issue #710 — combined "Items 1 and 2" headings return None) — guard every item for `None` and convert to the named error slot; do NOT assume every filing exposes every item.
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — `filing.obj()` → `TenK` / `TenQ`; 10-K `tenk.management_discussion` (Item 7), `tenk.risk_factors` (Item 1A), `tenk.items` / `tenk["Item 7"]`; 10-Q `tenq["Part I, Item 2"]` / `tenq.sections` (no dedicated Item-2 property confirmed) — grounding: edgartools `concepts/data-objects` docs + issue #710 (captured 2026-07-12; see Notes §edgartools grounding).
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: 10-K/10-Q Item Segmentation / Scenario: 10-K MD&A and Risk Factors segmentation`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: 10-K/10-Q Item Segmentation / Scenario: 10-Q MD&A segmentation`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: 10-K/10-Q Item Segmentation / Scenario: Requested item absent from this filing`

## Task 4 — Segment 8-K by reported item code, following Exhibit 99.x for the narrative text

- **Description**: Segment an 8-K by reported item code (2.02 / 7.01 / 8.01), and for each reported item follow the filing's Exhibit 99.x attachment to source the narrative text — the 8-K body typically carries only the item announcement, the substantive content lives in the exhibit. Each emitted section records the source exhibit filename in its provenance.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_segment_8k_item_2_02_from_ex99_1`, `::test_segment_8k_item_7_01_8_01_from_ex99_x` (parametrized over item codes 7.01/8.01) — each reported item emits a section object whose text is sourced from the corresponding Exhibit 99.x (not the 8-K body alone), with the exhibit filename recorded in provenance.
  - **GREEN**: 8-K segmentation reads reported item codes and resolves each to its Exhibit 99.x text via edgartools' attachments API; exhibit filename present in provenance.
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — 8-K `filing.obj()` → `EightK`; reported items `eightk.items` / `eightk["Item 2.02"]`; press-release exhibits `eightk.press_releases` (list of `Attachment`) / `eightk.has_press_release`; general `filing.attachments[...]`; per-exhibit `Attachment.text()`, `.document` (filename), `.document_type` (e.g. `"EX-99.1"` — identify exhibits by `document_type`, NOT a non-existent `exhibit_number`) — grounding: edgartools `edgar/attachments.py` + data-objects docs (captured 2026-07-12; see Notes §edgartools grounding).
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: 8-K Item Segmentation with Exhibit-Following / Scenario: 8-K Item 2.02 with Exhibit 99.1 present`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: 8-K Item Segmentation with Exhibit-Following / Scenario: 8-K Item 7.01/8.01 with Exhibit 99.x present`

## Task 5 — Emit a loud gap for an 8-K item reported without an Exhibit 99.x

- **Description**: Treat an 8-K item (2.02 / 7.01 / 8.01) listed in the filing's items metadata but lacking a corresponding Exhibit 99.x attachment as a loud extraction gap — an explicit gap/error slot naming the accession and item code — never a silent skip or an empty section.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_8k_reported_item_without_exhibit_emits_gap` — an 8-K whose metadata lists item 2.02 but whose accession folder has no Exhibit 99.x → an explicit gap/error slot for that item naming accession + item code (item is NOT omitted from output, section is NOT empty).
  - **GREEN**: the missing-exhibit branch emits the named gap slot; the item remains present in output as an error slot. NOTE — edgartools raises `KeyError("Document not found: …")` when indexing a non-existent attachment; catch that and convert it to the loud named gap slot (do not let it propagate as an uncaught crash).
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — `filing.attachments[name]` raises `KeyError("Document not found: {name}")` on a missing exhibit — grounding: edgartools `edgar/attachments.py` (captured 2026-07-12; see Notes §edgartools grounding).
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: 8-K Missing-Exhibit Gap / Scenario: Reported item without exhibit`

## Task 6 — Attach a complete provenance tuple + reconstructable URL to every section

- **Description**: Every emitted section (10-K / 10-Q / 8-K) carries a complete provenance tuple: accession number, CIK, item id, filingDate and period_of_report (where available), and a reconstructable SEC Archives URL to the source document — reconstructable without an additional lookup.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_every_section_carries_full_provenance` — for any successfully segmented section, provenance carries accession, cik, item id, filingDate/period_of_report, and a URL matching `https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-dashes}/{document}`.
  - **GREEN**: provenance tuple complete on every section; the URL is reconstructable from the tuple fields alone (assert the exact format against a known fixture).
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Section Provenance Completeness / Scenario: Provenance tuple present on every section`

## Task 7 — Paths-not-content: write each section's text to a file, return its text_path

- **Description**: Write each extracted section's text to a file and return that file path in the section object (a `text_path` field), rather than embedding the full section text inline in the action's JSON output.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/cache_util.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_section_text_written_to_path_not_inlined` — a successfully segmented section object carries a `text_path` pointing to a file whose contents equal the section text, AND the JSON result does not inline that section text.
  - **GREEN**: section text is file-backed via `text_path`; JSON result carries the path, not the body.
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Paths-Not-Content Section Emission / Scenario: Section text written to file`

## Task 8 — Fail-loud per-section aggregation feeding pack_inventory/_status

- **Description**: Surface any section that cannot be extracted as a per-section error slot that feeds `pack_inventory` / `_status`, and never emit a fabricated or silently empty section in its place. When one section fails within a multi-section filing, the successful sections emit normally, the failed one carries an explicit error, and the overall action classifies as partial; when every requested section fails, no top-level success is claimed. The per-section error marker keeps the existing `error`/`_error` sentinel so `pack.py`'s downstream `_status` classifier reads it unchanged.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/report-equity-memo/scripts/pack_inventory.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_one_section_fails_partial`, `::test_all_sections_fail_no_success` — Item 7 extracts, Item 1A throws → Item 7 emitted normally, Item 1A slot carries an explicit `error`/`_error`, overall result is partial; a filing whose primary document cannot be fetched/parsed at all → every requested slot carries an error and no top-level success.
  - **GREEN**: the error markers use the existing `error`/`_error` sentinel; a probe through `pack.py`'s `_classify_result` reads the partial vs failed status correctly (explicit test per except branch — no untested error path).
- **External surfaces**:
  - internal sibling-team contract: `pack.py` `_status` classifier reads `error`/`_error` markers (walks one dict level) — grounding: in-repo evidence `pack.py:192-194,253-308`.
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Fail-Loud Per-Section Extraction / Scenario: One section fails within a multi-section filing`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Fail-Loud Per-Section Extraction / Scenario: All requested sections fail`

## Task 9 — Tag 8-K exhibit-sourced sections with furnished-vs-filed disclosure status

- **Description**: Tag each section sourced from an 8-K Item 2.02/7.01 Exhibit 99.x with its legal disclosure status `disclosure_status: furnished` (distinct from `filed`), so downstream consumers can weight it.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_8k_exhibit_section_marked_furnished` — a section sourced from an 8-K Item 2.02/7.01 Exhibit 99.x carries `disclosure_status: furnished`, distinct from a `filed` section.
  - **GREEN**: the 8-K exhibit-following path stamps `disclosure_status: furnished` on the section provenance.
- **Dependencies**: Task 4 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Furnished-vs-filed status propagates to the memo / Scenario: Exhibit 99.x marked furnished`

## Task 10 — Distinct acquisition failure classes: timeout + edgartools version-drift

- **Description**: Distinguish transient/library failure modes from content gaps. A fetch that exceeds the timeout classifies as `timeout` (retryable), not merged into a generic `gap`/`error`. An edgartools section return of unexpected shape (e.g. after a library upgrade changes a section API surface) fails loud on the shape mismatch rather than emitting possibly-wrong section text.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_timeout_is_distinct_class`, `::test_version_drift_fails_loud` — a timed-out fetch classifies as `timeout` distinct from `gap`/`error`; an edgartools object whose section shape does not match the expected contract → a loud shape-mismatch error, not emitted text.
  - **GREEN**: timeout is its own retryable class; a shape guard on the edgartools return raises/returns a loud mismatch (explicit test on the shape-mismatch except branch). The shape guard asserts the expected attributes exist on the pinned edgartools version (`homepage_url`, `filing_url`, `accession_no`, `document_type`, `.text()`) — a v5 major-rewrite / attribute churn surfaces as a loud mismatch, never silently-wrong text.
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — section/attachment shape guarded against major-version churn (v5 rewrite; `TenK.items` canonicalization changed across 3.x; issue #710 None-returns) — grounding: edgartools PyPI version + GitHub source (captured 2026-07-12; see Notes §edgartools grounding).
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Distinct acquisition failure classes / Scenario: Network timeout is its own class`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Distinct acquisition failure classes / Scenario: edgartools version-drift is caught, not silently trusted`

## Task 11 — SEC fair-access: rate-limit backoff + filing cache reuse

- **Description**: On sustained requests approaching the ~10 req/s SEC ceiling, a 429/403 triggers back-off with jitter and retry — never an immediate fail nor a silent drop. edgartools ships its OWN rate-limit + retry stack (`pyrate-limiter` + `stamina` + `httpxthrottlecache`, over `httpx` — NOT the legacy `requests`-based `_sec_get` throttle, which does not cover the edgartools path); this task's job is to ensure that built-in backoff is active and our acquisition wrapper does not disable or swallow it (a caught-and-immediately-failed 429 would defeat it) — not to reimplement backoff. Separately, an accession already fetched within the cache window is read from OUR `cache_util` layer on a same-stage re-run instead of re-hitting SEC.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/cache_util.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_rate_limit_backoff_not_swallowed`, `::test_filing_cache_avoids_refetch` — a simulated 429/403 on the edgartools path leads to a retry (not an immediate fail, not a silent drop) — i.e. our wrapper does not catch-and-fail it; a second same-accession request within the window reads cache (assert zero additional SEC/edgartools fetch calls).
  - **GREEN**: edgartools' built-in `pyrate-limiter`/`stamina` backoff is left active (our wrapper preserves, not defeats, it); narrative acquisition reuses `cache_util` (`cache_path("sec_edgar", f"narrative_{accession}")`, immutable TTL) so a warm accession does not re-hit SEC.
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — built-in throttle/retry `pyrate-limiter` + `stamina` + `httpxthrottlecache` over `httpx` (do not disable) — grounding: edgartools dependency metadata, PyPI (captured 2026-07-12; see Notes §edgartools grounding).
  - internal contract: `cache_util.cache_path` / `load_cache` / `save_cache` envelope v2.0 — grounding: in-repo evidence `cache_util.py:170-252`.
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: SEC EDGAR fair-access compliance / Scenario: Rate-limit backoff`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: SEC EDGAR fair-access compliance / Scenario: Filing cache avoids re-fetch`

## Task 12 — Preserve the `--action narrative` CLI contract; retire regex internals from the code path

- **Description**: Preserve the existing `--action narrative --accession <accession>` CLI action name and its accession-based invocation contract (result keys accession/cik/form/filingDate/sections; exit 1 iff error) while the internal implementation is now edgartools-based. The retired regex internals (`parse_item_sections`, `_ITEM_HEADER_RE`, the exhibit-index skip heuristic) MUST no longer be on the segmentation code path for any 10-K/10-Q/8-K — edgartools' section API performs segmentation instead.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_cli_narrative_contract_preserved`, `::test_regex_internals_off_code_path` — invoking `sec_edgar_client.py --action narrative --accession <acc>` returns a result under the same contract keys and exit-code discipline (1 iff `error`); AND the TOC-vs-body regex path (`parse_item_sections`, `_ITEM_HEADER_RE`) is not invoked on any narrative segmentation (assert via a spy/removal — the symbol is either deleted or provably unreached).
  - **GREEN**: CLI action name + arg contract unchanged; edgartools performs all segmentation; a repo-wide **content** grep (not filetype-scoped) for `parse_item_sections` / `_ITEM_HEADER_RE` / `action_narrative` shows no remaining *code* consumer — every residual hit is a carved-out doc/spec/historical-record (justified inline).
- **Dependencies**: Tasks 3, 4, 7 complete first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: CLI Surface Preserved Across the edgartools Migration / Scenario: Existing CLI invocation still resolves`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: CLI Surface Preserved Across the edgartools Migration / Scenario: Regex internals no longer on the code path`

## Decision Log

1. chose to ship narrative as the `sec_edgar_client.py` CLI migration only, deferring `pack_us` memo-wiring to a follow-on memo-integration slice, because all 21 narrative scenarios are CLI-extraction and memo-wiring pairs naturally with the table/KPI slices that also feed the memo — cost-of-change: the day you want narrative visible end-to-end inside a memo, this choice costs one added memo-integration slice (pack_us ticker→accession resolution + a new pack key), not a rewrite. (User confirmed option A at kickoff, 2026-07-12; late-vetoable.)

## Notes

- **Coverage gate**: run `python3 <loom-code>/scripts/check_scenario_coverage.py docs/loom/2026-07-12-us-sec-primary-source-layer docs/loom/plans/2026-07-12-us-sec-narrative.md` before the plan-document-reviewer. NOTE — the change-folder holds THREE capabilities (narrative / financial-table-xval / operational-kpi); this plan covers ONLY `narrative` (21 scenarios). If the coverage script scans all three capability folders, its "uncovered" set will list the other two capabilities' scenarios — those are **out of scope by design** (separate future slices, brief §Decision capabilities 2-3), an approved scope boundary, not a coverage gap.
- **Scope boundary — memo surfacing deferred**: `pack_us.pack_memo_fetch` does NOT currently call the narrative action, and wiring narrative into the ticker-based memo pack (ticker→accession resolution + a new pack key + memo-worker consumption) is a distinct module (`pack_us.py`) and a natural SECOND slice. This plan implements the furnished-vs-filed Requirement at its **checkable observable** — the section object carries `disclosure_status` (Task 9). The Requirement's "…and the memo-feed surfaces it" clause (pack_us wiring) is deferred. **Surface this at the SDD kickoff briefing as a one-way-door scope decision** (include pack_us memo-wiring in this slice vs defer to a follow-on memo-integration slice).
- **Fixture discipline** (fixtures-mirror-producer-shape): edgartools is a third-party producer — capture its REAL filing/section object shape via the network-marked live test (Task 2) and mirror THAT in the offline unit mocks; never hand-invent the edgartools object shape (a hand-shaped fixture certifies code that fails on the real library).
- **Test harness**: new offline unit tests live in `investing-toolkit/tests/data/test_sec_narrative.py` (mock edgartools objects); network-marked live anchors extend `test_data_markets_live.py`. edgartools must be importable in the pytest env for offline mocking — run these via `uv run pytest` (PEP-723 resolves edgartools) OR inject a `sys.modules` mock; the implementer picks the approach that matches the existing sibling-client test pattern.
- **Regex-retirement sweep** (migration-acceptance-greps-scope-by-content-not-filetype): Task 12's GREEN grep is repo-wide by content, not filetype-scoped. Recon already confirmed the ONLY code consumer of the retired names is `sec_edgar_client.py` itself; all other hits are doc/spec/historical-record carve-outs (`docs/loom/**`, `docs/superpowers/**`).
- **edgartools grounding** (§ referenced by tasks' External surfaces — primary-source research captured 2026-07-12; sources: PyPI `pypi.org/pypi/edgartools/json`, GitHub `dgunning/edgartools` source, `edgartools.readthedocs.io`):
  - **Version / runtime**: current `5.42.0`, MIT, `import edgar`, `requires-python >=3.10` (compatible with the client's existing `>=3.11` pin). Version-pin with `==5.42.0` per the sibling-client `==` convention.
  - **Footprint** (⚠ heavy — was brief Open Question): edgartools uses **`httpx`, not `requests`** (adds a 2nd HTTP stack alongside the client's `requests==2.33.1`), and pulls `pandas>=2` + `pyarrow>=17` (~100MB+ installed) + `lxml` + `pydantic>=2` + `beautifulsoup4` + `rich` + `orjson` + `pyrate-limiter`/`stamina`/`httpxthrottlecache` + others. `pandas`/`lxml` already appear in sibling clients; `pyarrow`/`httpx` are new weight. **Surface this footprint at the SDD kickoff as an FYI/confirm** — the spec already committed to edgartools, so this is a heads-up, not a re-open.
  - **Identity**: `edgar.set_identity("Name email")` / env `EDGAR_IDENTITY`. Does NOT fail-fast when unset (interactive prompt → `TimeoutError` after ~60s) → Task 1's own pre-send guard is load-bearing.
  - **Acquisition**: `Company(ticker).get_filings(form=...).latest()`, `get_by_accession_number(acc)`; attrs `accession_no`/`cik`/`form`/`filing_date`/`period_of_report`/`primary_document`; URLs `homepage_url`/`filing_url` (no `.url`). Not-found → empty `Filings`/`.latest()==None` (UNVERIFIED as an exception — test the None result).
  - **Segmentation**: `filing.obj()` → `TenK`/`TenQ`/`EightK`; `tenk.management_discussion`(7)/`tenk.risk_factors`(1A)/`tenk["Item 7"]`; `tenq["Part I, Item 2"]`; absent item → `None` (issue #710 — guard None).
  - **8-K exhibits**: `eightk.items`/`["Item 2.02"]`; `eightk.press_releases`/`has_press_release`; `filing.attachments[name]`; `Attachment.text()`/`.document`/`.document_type` (`"EX-99.1"` — identify by `document_type`, not `exhibit_number`); missing → `KeyError("Document not found: …")`.
  - **Drift**: v5 was a major rewrite; `TenK.items` canonicalization changed across 3.x; issue #710 combined-headings return None → shape-guard tests against the pinned version (Task 10).
- **as_of invariant** (critic Gotcha C2): `as_of` for any cached/emitted narrative artifact MUST derive from the filing's disclosure date / accession, NEVER wall-clock — a same-day re-run must not double-append. Carried into every implementer packet.
- All 12 tasks are `Independent: false` (shared write set on `sec_edgar_client.py`); SDD dispatches sequentially. No parallel-dispatch markup applies.
