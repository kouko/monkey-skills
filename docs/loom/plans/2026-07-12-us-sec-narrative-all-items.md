# Plan: US SEC narrative — pivot segmentation to ALL body items (no filtering)

**Source brief**: docs/loom/2026-07-12-us-sec-primary-source-layer/specs/narrative/spec.md (MODIFIED segmentation requirements)
**Total tasks**: 3
**Critical-path depth**: 2 (≤5 ✓)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-07-12; 14/14, depth 2 verified)

> **Design pivot (user decision, 2026-07-12)**: the data layer does PURE acquisition — no
> analysis-driven filtering. Segmentation changes from a curated subset (10-K Item 7 + 1A,
> 10-Q Item 2, 8-K exhibit-items only) to EVERY item the edgartools primary-document object
> enumerates (`obj.items`). 8-K still follows Exhibit 99.x for exhibit-bearing items (that is
> where the 8-K's substance lives); all OTHER attachments (EX-10/EX-21/certs/XBRL) stay out of
> scope. All the section-object machinery already on this branch — provenance (T6), paths-not-
> content (T7), per-section fail-loud (T8), furnished/filed (T9), timeout/version-drift (T10),
> cache (T11), CLI wiring (T12) — is REUSED verbatim; only item SELECTION in the three
> segmenters + the wholesale-fail enumeration change. This supersedes the filtered segmentation
> committed on this branch (T3/T4). Empirically confirmed feasible: a live probe showed the AAPL
> 10-K `obj.items` enumerates all 23 items (Item 1..16) each with extractable text, and the 8-K
> enumerates all reported items.
>
> Coverage note: this is a MODIFIED-behavior plan touching only the segmentation scenarios; the
> narrative spec's other requirements (acquisition, provenance, paths, fail-loud, disclosure,
> failure-classes, fair-access, CLI) are already implemented on this branch and are NOT re-covered
> here — a scenario-coverage scan will list them as "uncovered by this plan" by design.
> All 3 tasks touch `sec_edgar_client.py` (+ tests) → all `Independent: false`, dispatched sequentially.

## Task 1 — Enumerate ALL 10-K/10-Q items (drop the Item-7/1A curated filter)

- **Description**: Rewrite `_segment_10k` and `_segment_10q` to enumerate EVERY item in `obj.items` and yield one `(item_id, lambda: obj[item_id])` per item, instead of the hardcoded Item 7 + Item 1A (10-K) / Item 2 (10-Q). Each enumerated item flows through the existing `_build_section` → provenance + text_path + `_section_gap` on None (T3/T6/T7 machinery unchanged). No item is filtered out.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`, `investing-toolkit/tests/data/test_data_markets_live.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_segment_10k_emits_all_items` — a mock TenK whose `items` lists e.g. `["Item 1","Item 1A","Item 7","Item 8"]` (with subscript text per item) → `segment_filing` emits a section for EVERY listed item (assert the emitted item-id set equals the mock's full `items` set, incl. Item 1 Business + Item 8), not just Item 7/1A. Plus `test_segment_10q_emits_all_items` for the 10-Q enumeration. The existing None→gap behavior is re-asserted for an enumerated item whose subscript is None.
  - **GREEN**: `_segment_10k`/`_segment_10q` enumerate `obj.items`; every present item is its own section; None items → named error slot. Migrate the retired `test_segment_10k_item7_and_item1a`/`test_segment_10q_item2` assertions to the all-item shape (the live 10-K anchor asserts the emitted set is a SUPERSET of {Item 1, Item 1A, Item 7, Item 8}, proving all-item capture against real edgartools).
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — `obj.items` (full item list) + `obj[item_id]` subscript (str-or-None) — grounding: live probe 2026-07-12 (AAPL 10-K `obj.items` = 23 items) + plan Notes §edgartools grounding.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Full-Body Item Segmentation (10-K/10-Q) / Scenario: 10-K all-item segmentation`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Full-Body Item Segmentation (10-K/10-Q) / Scenario: 10-Q all-item segmentation`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Full-Body Item Segmentation (10-K/10-Q) / Scenario: Enumerated item absent or empty in this filing`

## Task 2 — Enumerate ALL 8-K reported items; exhibit-following only for exhibit-bearing items

- **Description**: Rewrite `_segment_8k` to emit a section for EVERY reported item in `obj.items` (not only 2.02/7.01/8.01). For an exhibit-bearing item (2.02/7.01/8.01) keep the existing Exhibit 99.x following (text from the exhibit, `disclosure_status: "furnished"`, exhibit filename in provenance, missing-exhibit → loud gap per T5). Every OTHER reported item carries its own body text (`obj[item_id]`) with `disclosure_status: "filed"`. No non-99.x attachment is fetched.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`, `investing-toolkit/tests/data/test_data_markets_live.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_segment_8k_emits_all_reported_items` — a mock 8-K reporting e.g. `["Item 2.02","Item 9.01"]` with an EX-99.1 for 2.02 → a section for BOTH items; Item 2.02 sourced from the exhibit (`disclosure_status=="furnished"`, exhibit filename present), Item 9.01 from its body text (`disclosure_status=="filed"`). Re-assert the T5 missing-exhibit gap still fires for an exhibit-bearing item whose 99.x is absent.
  - **GREEN**: `_segment_8k` enumerates all reported items; exhibit-bearing items follow 99.x (furnished), others use body text (filed); missing-exhibit gap preserved for exhibit-bearing items. Live 8-K anchor asserts the emitted set equals the real reported-item set (superset of {Item 2.02}).
- **External surfaces**:
  - SDK package: `edgartools` 5.42.0 — `CurrentReport.items` (all reported items), `obj[item]` body text, `obj.press_releases` (EX-99.x) — grounding: live probe 2026-07-12 (AAPL 8-K reported {Item 2.02, Item 9.01}) + T4 live anchor.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: 8-K Full-Item Segmentation with Exhibit-Following / Scenario: 8-K all reported items, exhibit-bearing item sourced from Exhibit 99.1`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: 8-K Full-Item Segmentation with Exhibit-Following / Scenario: 8-K Item 7.01/8.01 with Exhibit 99.x present`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Furnished-vs-filed status propagates to the memo / Scenario: Exhibit 99.x marked furnished`

## Task 3 — Reconcile the wholesale-fail enumeration + CLI/live anchors to dynamic all-items

- **Description**: With segmentation now dynamic (all `obj.items`), the static `_FORM_REQUESTED_ITEMS` map (and its T10 drift-guard test) can no longer enumerate the item set — and on a wholesale `obj()` failure the items are unknowable. Change the all-sections-failed path to a single form-level error slot for 10-K/10-Q (as 8-K already does), retire `_FORM_REQUESTED_ITEMS` + `test_form_requested_items_match_segmenters` (now obsolete), and update the T8 "all requested sections fail" test to the form-level shape. Update the T12 CLI-contract test + the CLI/live assertions to the all-items reality (sections now contains the full item set; the contract keys accession/cik/form/filingDate/sections + exit-1-iff-error are unchanged).
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_narrative.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Acceptance**:
  - **RED**: `test_sec_narrative.py::test_all_sections_fail_form_level_when_obj_raises` — when `filing.obj()` raises for a 10-K, the result is a single form-level error slot (no reliance on a hardcoded item list) that classifies as "failed" through pack.py. Update `test_cli_narrative_contract_preserved` to assert the 5 contract keys hold with the all-items `sections` list.
  - **GREEN**: `_FORM_REQUESTED_ITEMS` + its drift-guard test removed; the 10-K/10-Q wholesale-fail path emits a form-level slot; the CLI contract keys + exit code unchanged; full suite green.
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: Fail-Loud Per-Section Extraction / Scenario: All requested sections fail`
- **Brief item covered**: `2026-07-12-us-sec-primary-source-layer / Requirement: CLI Surface Preserved Across the edgartools Migration / Scenario: Existing CLI invocation still resolves`

## Notes

- **Reuse, don't rebuild**: provenance/text_path/per-section-fail-loud/disclosure/timeout/version-drift/cache/CLI machinery is unchanged — only the item-selection in `_segment_10k`/`_segment_10q`/`_segment_8k` and the wholesale-fail enumeration change. Keep every unrelated test green.
- **Live anchors are the real proof**: update the network-marked anchors so a real 10-K asserts the emitted item set is a superset of {Item 1, Item 1A, Item 7, Item 8} (proving all-item capture, esp. the newly-included Business + Financial Statements), and the real 8-K asserts all reported items are emitted. fixtures-mirror-producer-shape: offline mocks mirror the live `obj.items`/subscript shape.
- **Near-empty items are preserved as-is** (e.g. 10-K Item 1B "Not applicable" ~44 chars) — that IS the real content; the data layer does not editorialize. An item whose subscript is None (not just short) → the existing named error slot.
- **Out of scope (unchanged from the branch decision)**: non-99.x attachments (EX-10/EX-21/certifications/XBRL/graphics) and pack_us memo-wiring remain deferred future slices.
