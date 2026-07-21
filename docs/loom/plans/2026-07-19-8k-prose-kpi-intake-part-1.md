# Plan: 8-K prose KPI intake — Part 1 (walking skeleton)

Source change-folder: docs/loom/2026-07-19-8k-prose-kpi-intake/ (loom-spec, validated + completeness-critic PASS_WITH_NOTES)
Bound via: Layer 0 explicit handoff (orchestrator-authored change-folder)
Total tasks: 9   (uncapped)
Critical-path depth: 4 (≤5)   ← longest Dependencies chain: T1→T2→T3→T8
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-20, 14/14 checks)

Scope: Part 1 of a 3-part split (user-approved 2026-07-19). Part 1 = the
end-to-end walking skeleton (extract → verify → propose → confirm → commit →
store → honest-gap → memo-boundary). Parts 2 (number robustness) and 3
(lifecycle/hardening) are separate follow-on briefs — their scenarios are listed
as user-approved deferrals in §Notes (coverage-check escape).

New modules (siblings to shipped Route B machinery):
- `investing-toolkit/skills/data-markets/scripts/exhibit_prose.py` — mechanical prose scanner (sibling of `exhibit_tables.py`)
- `investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py` — prose candidate producer (sibling of `kpi_8k_candidates.py`)

## Task 1 — canonical prose surface + table exclusion
- Description: From raw EX-99 HTML, produce the single named canonical flattened prose text with well-formed `<table>` content excluded; this text is the one surface offsets and the substring gate index.
- Module: exhibit_prose.py
- Files touched: investing-toolkit/skills/data-markets/scripts/exhibit_prose.py, investing-toolkit/tests/test_exhibit_prose.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/exhibit_tables.py
  - investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py
- Acceptance:
  - RED: test_prose_surface_excludes_table_text — HTML with table cell "999" + prose "employees 1,576,000" → canonical text contains the prose phrase, not "999"
  - GREEN: a `prose_surface(html) -> str` returns the flattened non-table text deterministically
- External surfaces: HTML parsing via Python stdlib `html.parser` (stdlib-preferred; mirrors exhibit_tables.py's stdlib walker) — no new dependency
- Dependencies: none
- Independent: true
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Canonical text surface and anchor durability / Scenario: offset basis is the named canonical surface

## Task 2 — number-token locator with offset span + verbatim quote
- Description: Locate candidate number tokens in the canonical prose text, each carrying char_offset_span[start,end] and the verbatim matched token; guarantee canonical_text[start:end] == token.
- Module: exhibit_prose.py
- Files touched: investing-toolkit/skills/data-markets/scripts/exhibit_prose.py, investing-toolkit/tests/test_exhibit_prose.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/exhibit_tables.py
- Acceptance:
  - RED: test_locate_returns_token_span_quote — canonical text "...had 1,576,000 employees..." → candidate {token:"1,576,000", span:[s,e]} with text[s:e]==token
  - GREEN: `locate_numbers(text) -> list[dict]` returns plain numeric tokens (digits, separators, decimal) with exact offset spans (word-scale multipliers deferred to Part 2)
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Mechanical prose candidate extraction with verbatim anchor / Scenario: locate a prose-stated KPI

## Task 3 — propose raw candidate (mechanical fields, null semantics, needs_semantic)
- Description: propose() wraps located tokens into raw candidates carrying mechanical fields (value derived from token, verbatim_quote, char_offset_span, unit_hint/period_hint) and NULL semantic slots (kpi_id/unit/period) with needs_semantic=true; the semantic step never sets value/quote/offset.
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_8k_candidates.py
  - investing-toolkit/skills/data-markets/scripts/exhibit_prose.py
- Acceptance:
  - RED: test_propose_emits_raw_candidate_needs_semantic — propose(canonical_text) → candidate with value/quote/offset set, kpi_id None, needs_semantic True
  - GREEN: `propose(text) -> list[candidate]` emits mechanical-only raw candidates
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Mechanical prose candidate extraction with verbatim anchor / Scenario: value is never LLM-produced
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Three-layer trust — LLM proposes semantics, human confirms / Scenario: propose marks incomplete semantics

## Task 4 — anti-fabrication substring gate (token, not normalized value)
- Description: A pure gate verifying the candidate's matched token AND verbatim_quote are substrings of the canonical text; the normalized numeric value is NOT required to be a substring; a candidate failing the check is rejected.
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_8k_candidates.py
- Acceptance:
  - RED: test_gate_checks_token_rejects_invented — literal candidate token "1,576,000" present in text passes; an invented token absent from text is rejected; the comma-stripped normalized value 1576000 is NOT required to appear
  - GREEN: `gate(candidate, canonical_text) -> bool` verifies the token/quote, not the normalized value
- Dependencies: none
- Independent: false   # same file as Tasks 3/5/6/7 — serial dispatch, but no dependency edge
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Anti-fabrication substring gate / Scenario: LLM-invented value is rejected
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Anti-fabrication substring gate / Scenario: normalized value need not be a substring

## Task 5 — legitimate zero value survives the gate (falsy-zero pin)
- Description: A candidate whose value is exactly 0 is located, passes the substring gate, and stays eligible to commit — 0 is not treated as "no value" (guards the repo's known falsy-zero trap).
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - docs/loom/memory/falsy-guard-rejects-legitimate-zero-provenance.md
- Acceptance:
  - RED: test_zero_value_survives_gate — a candidate with value 0 and token "0" passes the gate and remains eligible (a test that FAILS under a falsy `if not value` guard)
  - GREEN: the gate/eligibility path uses `is None` / truthy-token semantics, never a bare falsy test
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Anti-fabrication substring gate / Scenario: legitimate zero value is not dropped

## Task 6 — confirm-all gate → commit (no auto-commit; bypass illegal)
- Description: A candidate is committed only after a human confirm-all; there is no auto-commit; any attempt to move a candidate located→committed without the human confirm step is rejected as illegal. The interim no-taxonomy filter holds (a human-confirmed candidate commits regardless of a fixed KPI taxonomy).
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_8k_candidates.py
- Acceptance:
  - RED: test_commit_requires_confirm — commit() on an unconfirmed candidate does not append; a located candidate cannot bypass to committed
  - GREEN: `commit(candidates, confirmed=True)` is the only path that appends
- Dependencies: Task 4 completes first
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Three-layer trust — LLM proposes semantics, human confirms / Scenario: commit requires human confirmation
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Three-layer trust — LLM proposes semantics, human confirms / Scenario: bypassing confirmation is forbidden
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Capture taxonomy [deferred] / Scenario: interim no-taxonomy filter

## Task 7 — store append: prose anchor + attribution, kpi_store byte-unchanged
- Description: A confirmed candidate is committed via the existing `kpi_store.append` with per-point provenance carrying source_kind="prose", a prose:{start}-{end} anchor, the verbatim_quote, and filing attribution (accession, document, filing date, confirmer identity, confirm timestamp); `kpi_store.py`/`kpi_validate.py` stay byte-unchanged.
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_8k_candidates.py
- Acceptance:
  - RED: test_committed_point_carries_prose_anchor_and_attribution — an appended prose point carries source_kind="prose", prose:{start}-{end}, verbatim_quote, accession/document/filing-date/confirmer/timestamp
  - GREEN: commit appends a schema-valid point; a diff shows kpi_store.py/kpi_validate.py unchanged
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Byte-compatible store integration with prose anchor / Scenario: committed prose point carries its anchor
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Committed point carries filing attribution and confirmer identity / Scenario: provenance is auditable and citable

## Task 8 — honest gaps (empty result; ≥2-exhibit gap)
- Description: When the scan finds no prose KPI, return an explicit empty result with a "0 prose candidates" note (never fabricate); when an 8-K carries ≥2 EX-99 exhibits, emit a gap marker and extract nothing (inherit the Route B LOOM-SIMPLIFY ceiling), never silently pick one.
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - docs/loom/specs/2026-07-19-8k-earnings-kpi-intake.md
- Acceptance:
  - RED: test_empty_and_multi_exhibit_gaps — no-KPI text → explicit empty (0 candidates note); a ≥2-exhibit input → gap marker, zero extraction
  - GREEN: the producer distinguishes empty-success from a loud multi-exhibit gap
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Honest gaps for empty and multi-exhibit cases / Scenario: no prose KPI found
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Honest gaps for empty and multi-exhibit cases / Scenario: two or more exhibits yields a gap

## Task 9 — memo-boundary lock: prose points absent from memo feed
- Description: A regression-locking test pinning that the existing quarterly memo feed reads the XBRL series (`build_quarterly_series`), NOT `kpi_store`, so a committed prose point does not surface in the memo feed output under Slice A.
- Module: (test-only — locks an existing invariant, no production change)
- Files touched: investing-toolkit/tests/test_prose_memo_boundary.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_memo_feed.py
- Acceptance:
  - RED: test_prose_point_absent_from_memo_feed — with a prose point present in a store fixture, `build_quarterly_memo_feed` output does not include it
  - GREEN: the test passes, pinning the decoupling (kpi_memo_feed.py:13) against future regression
- Dependencies: none
- Independent: true
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Prose points do not surface in the memo (Slice-A boundary) / Scenario: a committed prose point is absent from the memo feed

## Notes

- Kickoff decision: durable store provenance shape → CONFIRMED as specified (user 2026-07-20) — source_kind="prose", anchor prose:{start}-{end}, verbatim_quote, + accession/document/filing-date/confirmer/timestamp; mirrors Route B's proven provenance (kpi_8k_candidates.py) + the prose anchor.
- Kickoff decision: canonical text surface (offset basis) → CONFIRMED reuse edgartools flattened text (the existing narrative-layer flattener, sec_edgar_client.py `_segment` EX-99 path), NOT raw HTML; stdlib html.parser fallback only if reuse proves unavailable. Prose + narrative share one text surface. (Part 3 adds hash+version drift guard.)
- Kickoff decision (arm-1 look-up, unbriefed): number tokenization → Python stdlib `re`, no new dependency (mirrors exhibit_tables.py's stdlib walker).

- **Part-1 numeric scope:** Part 1 handles PLAIN numeric tokens (digits, thousands
  separators, decimals — e.g. AMZN employees 1,576,000, TSLA deliveries 480,126,
  and 0). Word-scale multipliers ("3.56 billion"/"million") are Part 2 (Requirement
  "Consistent text normalization"). Examples use plain integers accordingly.
- **Post-PASS amendment (2026-07-20, re-review skipped — additive + schema-safe):**
  T1/T2/T4 RED-test EXAMPLES changed from the word-scale "3.56 billion" to plain
  integers to match the Part-1 numeric scope above. No task/dependency/coverage/
  field change — same RED test names, same DAG, same Brief-item mappings — so the
  plan-document-reviewer PASS still holds.
- **Depth ≤5 via isolatable tests:** Tasks 4 and 6 are pure functions tested with
  literal candidates (no dependency on the propose chain), keeping the DAG
  wide-and-shallow (depth 4) rather than one linear pipeline chain.
- **Same-file serialization:** Tasks 3–8 all touch `kpi_prose_candidates.py`, so
  they dispatch serially (Independent: false) even where no dependency edge exists;
  this is a dispatch/width constraint, not a critical-path-depth one.
- **User-approved deferrals (coverage-check escape, 2026-07-19 "3-part split, Part 1 first"):**
  the following change-folder scenarios are OUT of Part 1 by the approved split and
  become Part 2 / Part 3 follow-on briefs — not dropped:
  - **Part 2 (number robustness):** Requirement "Date and period tokens are not KPI values" / Scenario: period label is not a candidate; Scenario: bounding qualifiers are not stored as bare equality values · Requirement "Consistent text normalization" / Scenario: nbsp-separated number is not false-rejected · Requirement "Minimal provenance capture for privacy" / Scenario: bounded context window, not full paragraph.
  - **Part 3 (lifecycle/hardening):** Requirement "Three-layer trust" / Scenario: human edit of a mechanical field re-runs the gate; Scenario: per-field provenance distinguishes machine from human · Requirement "Table-versus-prose deduplication" / Scenario: table point wins on duplicate; Scenario: conflicting values raise; Scenario: prose-versus-prose collision is arbitrated; Scenario: dedup outcome is order-independent · Requirement "Canonical text surface and anchor durability" / Scenario: anchor drift is detected on read · Requirement "Resource bounds on scan and proposal" / Scenario: pathological input degrades to a loud gap · Requirement "Slice-A concurrency scope and batch-commit atomicity" / Scenario: crash mid-batch leaves all-or-none · Requirement "Exhibit prose is untrusted input to the proposer" / Scenario: injected directive is ignored · Requirement "Proposal infra-failure is distinct from needs_semantic" / Scenario: rate-limit is not a semantic gap · Requirement "Amended-filing conflict is raised (Slice-A minimal)" / Scenario: amendment conflict raises.
