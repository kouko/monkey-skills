# Plan: US SEC narrative → memo data pack wiring

Source brief: `docs/loom/specs/2026-07-13-us-sec-narrative-memo-wiring.md`
Total tasks: 7
Critical-path depth: 4 (≤5) — T1 → T2 → T3 → T6
Execution order: parallel-where-possible (T1, T4, T5 form the level-0 wave; T6, T7 form a second wave after T3)
Plan-document-reviewer verdict: PASS (2026-07-13; all file:line citations independently opened and confirmed; 4 non-blocking nits, 2 applied — see §Post-PASS amendment note)

## Change-folder binding — deliberate NON-bind (surfaced, not silent)

Detection layer (i) (branch slug) missed; layer (ii) found exactly **one**
non-archived change-folder (`docs/loom/2026-07-12-us-sec-primary-source-layer/`),
which by the default rule would auto-bind.

**We do NOT bind it, deliberately.** That folder's `specs/narrative/spec.md`
is **already shipped** (PR #552, squash `58eeb0dc`) — every one of its
scenarios maps to code that exists on main. Binding would (a) re-plan
already-implemented work, and (b) drag `check_scenario_coverage.py` into
demanding tasks for the `financial-table-xval` and `operational-kpi`
scenarios, both of which the brief puts explicitly **Out of Scope**. The
folder also records the memo-feed contract as **undefined** — concern
**C6** (`proposal.md:179`), which is precisely what this plan closes.

Input is therefore the brainstorming brief; the change-folder is upstream
context. `check_scenario_coverage.py` is **not** run (it applies only to the
change-folder input path). On merge, mark C6 resolved for the narrative
capability.

## Notes

- **Test-fixture law for this branch** (repo memory `fixtures-mirror-producer-shape`,
  whose 2nd instance IS this arc): **never mock `acquire_filing` or any other
  projection** — mock the real producer boundary (`edgar.get_by_accession_number`).
  Mocking one layer up is what let a production `AttributeError` ship green.
- **Cache law** (repo memory `cache-key-collision-across-migration`): any new
  cached payload shape gets a **distinct key**. This plan adds no new cache
  key — it reuses the producer's existing `narrative_sections_{accession}`
  (immutable TTL) unchanged. If an implementer finds itself inventing a cache
  key, that is out of plan — stop and surface.
- **CI dep set**: offline tests run with pytest + pyyaml ONLY. The `sec_client`
  fixture (`tests/data/test_sec_narrative.py:92`) stubs both `edgar` and
  `requests` into `sys.modules`. **Do NOT add `--with edgartools` / `--with
  requests` to the CI command.**
- **Version bump obligation**: this branch touches `investing-toolkit/skills/**`
  → `investing-toolkit/.claude-plugin/plugin.json` MUST bump (2.6.0 → 2.7.0)
  and `python3 scripts/sync_codex_manifests.py investing-toolkit` must run.
  CI job `plugin version bump` enforces this. Handled at branch close-out.
- **Close-out checklist (no owning task, by design — these are not code):**
  (a) the 2.7.0 bump + codex manifest sync above; (b) mark change-folder
  concern **C6** resolved for the narrative capability
  (`docs/loom/2026-07-12-us-sec-primary-source-layer/proposal.md:179`) — the
  memo-feed contract is defined by this branch. Named here so neither is
  discovered at merge time.

### Post-PASS amendment note

Plan-document-reviewer returned **PASS**. Two of its non-blocking nits were
then applied: Tasks 6 and 7 flipped to `Independent: true` (its Check-15
missed-parallel advisory — both hang off Task 3 with disjoint `Files
touched`), and the C6 close-out item was given an explicit home above.
Both edits are **additive and schema-safe** — no task added/removed, no
`Dependencies` edge changed, DAG and critical-path depth unchanged (4).
Re-review skipped per writing-plans §"Amending a PASS plan" (b).

## Decision Log

Kickoff-briefing sweep (kickoff-briefing.md §a two-axis test). No
`docs/loom/PRINCIPLES.md` in this repo → default applies: brief every
one-way-door hit.

**One-way-door hits: 1 — already decided and user-signed-off, so NOT re-asked**
(judgment-rubrics §3(c): a documented decision beats re-asking).

- **The `sec_narrative` payload shape IS the memo-feed contract** (closes
  change-folder concern C6). One-way door: once the memo template, the
  Phase-4 seed contract, and the gates cite its field names, changing them
  means rewriting every consumer — and invalidating the provenance claims of
  memos already archived against it. **Decided in the brief §Decision,
  user-approved 2026-07-13**: top-level `failed_items` + a required
  `{requested, succeeded, failed}` count triple, `requested` fixed by the
  policy. Rationale + the 5 researched alternatives are in the brief; not
  restated here.

**Two-way-door decisions (agent-decided; late-vetoable, logged not briefed):**

- **N = 4 quarters** of earnings 8-Ks. Reversal ≈ changing a parameter default.
  Chosen to align with TTM (trailing twelve months) — the repo has a recorded
  incident of a weak model mislabeling FY figures as TTM — so four consecutive
  releases form a genuine rolling year rather than an arbitrary count.
- **`_status` is an opt-in field in `pack.py`, not a rewrite of the classifier**
  (Task 4). Purely additive: sections without `_status` keep today's inference
  path unchanged, so the other four market packs are untouched. Reversal ≈
  deleting one branch. Rejected: a general recursive walk (the classifier's own
  LOOM-SIMPLIFY note defers that to cross-market provenance normalization, T5+ —
  out of scope here).
- **The selection policy lives in `sec_edgar_client.py`, not `pack_us.py`**
  (Task 2). It is a pure function over already-fetched rows, so it is offline-
  testable next to the producer it serves and reusable by any future consumer.
  Reversal ≈ moving a function.
- **`pack_inventory` presence semantics tighten for ALL markets** (Task 5), not
  just US: `present` now requires no error marker and `succeeded ≥ 1`. This has
  product consequence (a memo may now correctly report data as missing where it
  previously saw a phantom) but is a revert away — top-left cell, late-vetoable.

---

## Task 1 — `list_filings` preserves the submissions `items` and `reportDate` fields

- Description: Extend `list_filings` to carry through two fields the SEC
  submissions API already returns but the function currently drops: `items`
  (the comma-joined 8-K item codes, e.g. `"2.02,9.01"`) and `reportDate`
  (the filing's period of report). Without `items`, an earnings 8-K cannot be
  identified without an extra fetch; without `reportDate`, filings cannot be
  bucketed into quarters.
- Module: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- Files touched:
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `investing-toolkit/tests/data/test_sec_narrative.py`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py:320-347` (`list_filings` — the rows it builds today)
  - `investing-toolkit/tests/data/test_sec_narrative.py:92-125` (the `sec_client` fixture — stubs `edgar` + `requests`)
- Acceptance:
  - RED: `tests/data/test_sec_narrative.py::test_list_filings_preserves_items_and_report_date` fails — the row dicts carry no `items` / `reportDate` key.
  - GREEN: given a stubbed submissions payload whose `recent` dict contains
    `items: ["2.02,9.01", "5.02"]` and `reportDate: [...]`, each returned row
    carries `items` and `reportDate`; a form with no items (10-K) yields
    `items` as an empty string (the API's own representation), not a missing key.
- External surfaces: SEC `data.sec.gov` submissions JSON — the `recent` dict's
  `items` and `reportDate` arrays. **Live-verified 2026-07-13** against CIK
  0000320193: both fields present; 8-K rows carry values like `"2.02,9.01"`,
  `"5.02"`, `"5.07,9.01"`. Parallel arrays, index-aligned with `form` —
  guard the same `i < len(...)` way the existing fields are guarded.
- Dependencies: none
- Independent: true
- Brief item covered: "`list_filings` is extended to preserve the submissions API's `items` and `reportDate` fields (live-verified to exist)."

## Task 2 — quarter-anchored filing-selection policy (pure function)

- Description: Add a pure function that, given a filings list (as returned by
  the extended `list_filings`) and `n_quarters` (default 4), selects the
  filings whose narrative the memo will read: the latest 10-K, the latest
  10-Q, and **one earnings 8-K per quarter for the last N quarters** — an
  earnings 8-K being one whose `items` include `2.02`. Selection is by
  **item code and period, never by recency rank**: the latest 8-K is often a
  5.02 executive change, not an earnings release (live-observed on AAPL).
  A quarter with no qualifying 8-K yields an explicit **gap** entry naming
  that quarter — never a silent omission, and never a short list passed off
  as complete.
- Module: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- Files touched:
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `investing-toolkit/tests/data/test_sec_narrative.py`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py` (Task 1's extended `list_filings` rows)
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py:922` (`_section_gap` — the repo's existing gap-slot idiom to mirror)
- Acceptance:
  - RED: `tests/data/test_sec_narrative.py::test_select_narrative_filings_picks_earnings_8k_by_item_not_recency` fails (function undefined).
  - GREEN: given a filings list where the most recent 8-K carries `items="5.02"`
    and an older one carries `items="2.02,9.01"`, the selection returns the
    **2.02** filing's accession as that quarter's earnings 8-K and does NOT
    return the 5.02 one; the result also carries the latest 10-K and latest
    10-Q; and for a quarter with no 2.02 8-K in the window, the result carries
    an explicit gap entry naming the quarter and the reason.
  - GREEN: `requested` count is fixed by the policy (`2 + n_quarters`),
    independent of how many filings actually matched.
- External surfaces: none (pure function over already-fetched rows).
- Dependencies: Task 1 completes first (needs `items` / `reportDate` on the rows).
- Independent: false
- Brief item covered: "the earnings 8-K (submissions `items` ⊇ `2.02`) of each of the last N quarters, N=4 by default … Selection is by item code, never by recency … The selection window is anchored in TIME (quarters), never in filing count."

## Task 3 — `pack_memo_fetch` emits `sec_narrative` with a structurally visible failure surface

- Description: Wire the narrative into `pack_us.pack_memo_fetch`. Using the
  filings list it already fetches, run Task 2's selection, invoke the SEC
  client's `--action narrative` once per selected accession, and assemble a
  new top-level `sec_narrative` key. The wrapper carries, at **its own top
  level**: the per-filing narrative results, a **`failed_items`** list hoisted
  to depth 1 (where the one-level classifier can see it), a **required count
  triple** `{requested, succeeded, failed}` where `requested` is fixed by the
  policy, and a self-declared `_status` (ok / partial / failed) derived from
  those counts and the producers' own `narrative_status` values. A filing that
  fails entirely gets an error-bearing entry — never a silently absent key.
  Also add `sec_narrative` to the US memo-fetch fixture so the fixture mirrors
  the real producer shape.
- Module: `investing-toolkit/skills/data-markets/scripts/pack_us.py`
- Files touched:
  - `investing-toolkit/skills/data-markets/scripts/pack_us.py`
  - `investing-toolkit/tests/data/test_data_markets_us.py`
  - `investing-toolkit/tests/data/fixtures/data-us-memo-fetch-sample.json`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/pack_us.py:552-597` (`pack_memo_fetch` — the filings fetch at `:561-565` already has the accessions)
  - `investing-toolkit/skills/data-markets/scripts/pack_us.py:187` (`run_client` — the subprocess helper; each narrative fetch is one call)
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py:1283-1301` (the producer's real return shape — the fixture MUST mirror this, not an invented shape)
- Acceptance:
  - RED: `tests/data/test_data_markets_us.py::test_memo_fetch_emits_sec_narrative_with_counts` fails (`sec_narrative` absent from the pack).
  - GREEN: with `run_client` monkeypatched to return producer-shaped narrative
    results, `pack_memo_fetch("AAPL")["sec_narrative"]` carries the per-filing
    results, `requested == 6` (2 + N, N=4), `succeeded + failed == requested`,
    a top-level `failed_items` list, and `_status == "ok"`.
  - GREEN: when one selected filing's producer result carries
    `narrative_status: "partial"`, the wrapper's `_status` is `"partial"` and
    that filing's failed item ids appear in the wrapper's top-level
    `failed_items` — i.e. the failure is readable at depth 1 without walking
    into any `sections` list.
- External surfaces: the SEC client subprocess (`--action narrative --accession
  <ACCN>`, `sec_edgar_client.py:1306-1332`). Its cached, immutable-TTL key
  `narrative_sections_{accession}` is reused **unchanged** — this task
  introduces no new cache key.
- Dependencies: Task 2 completes first (needs the selection function).
- Independent: false
- Brief item covered: "`pack_us.pack_memo_fetch(ticker)` returns one additional top-level key, `sec_narrative` … a structurally visible failure surface … `failed_items` hoisted to depth 1 … a required count triple `{requested, succeeded, failed}`."

## Task 4 — `_classify_result` honors a section's self-declared `_status`

- Description: Teach the pack classifier that a section may **declare its own
  status**, and that a self-declaration wins over inference. Today
  `_dict_section_status` infers status by inspecting a dict's non-empty
  dict-valued sub-fields — which structurally cannot see a failure nested
  inside a **list** (the documented LOOM-SIMPLIFY ceiling at `pack.py:264-278`).
  A section carrying `_status: ok|partial|failed` is classified by that value
  directly. This is additive: sections without `_status` keep today's inference
  path byte-for-byte, so the other four market packs are unaffected.
- Module: `investing-toolkit/skills/data-markets/scripts/pack.py`
- Files touched:
  - `investing-toolkit/skills/data-markets/scripts/pack.py`
  - `investing-toolkit/tests/data/test_pack_facade.py`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/pack.py:192-310` (`_has_error_marker` → `_dict_section_status` → `_section_status` → `_classify_result`)
- Acceptance:
  - RED: `tests/data/test_pack_facade.py::test_classify_honors_self_declared_status` fails — a section dict whose per-item errors live in a **list** and which declares `_status: "partial"` is currently classified `"ok"`.
  - GREEN: a result containing a section with `_status: "partial"` classifies
    the whole pack as `partial` and names that section in `failed_sections`;
    `_status: "failed"` classifies it `failed`; a section with **no** `_status`
    key is classified exactly as before (assert the existing inference cases
    still hold — this is the regression guard for the other four markets).
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "make the narrative's degradation reach the pack's `_status` … both of our readers (`_classify_result`, `pack_inventory._classify`) are structural readers."

## Task 5 — `pack_inventory` stops reporting an all-failed section as data-present

- Description: Fix the false-presence bug. `_classify` currently marks any dict
  with ≥1 key as `present: true`, so a narrative wrapper that fetched nothing
  and carries only an error would be inventoried as **data present** — the
  exact inversion of what `pack_inventory.py` exists to prevent (its job is to
  catch a memo falsely claiming data is missing; it must not let a memo falsely
  claim data is there). A section is **not** present when it declares
  `_status: "failed"`, carries a direct `error` / `_error` marker, or reports a
  count triple with `succeeded == 0`.
- Module: `investing-toolkit/skills/report-equity-memo/scripts/pack_inventory.py`
- Files touched:
  - `investing-toolkit/skills/report-equity-memo/scripts/pack_inventory.py`
  - `investing-toolkit/tests/report/test_pack_inventory.py`
- Context paths:
  - `investing-toolkit/skills/report-equity-memo/scripts/pack_inventory.py:41-66` (`_classify` + `_inventory`; note only `mops` gets a hardcoded second-level expansion)
- Acceptance:
  - RED: `tests/report/test_pack_inventory.py::test_all_failed_section_is_not_present` fails — a section dict carrying only an `error` key (and a `{requested: 6, succeeded: 0, failed: 6}` triple) is currently reported `present: true`.
  - GREEN: that section is reported `present: false`; a section with
    `succeeded >= 1` remains `present: true`; and every existing inventory
    assertion (the TW memo-fetch fixture cases) still passes unchanged.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: "`pack_inventory` marks any dict with ≥1 key as `present: true` → an error-only narrative wrapper would be inventoried as data-present (false presence) … giving `pack_inventory` a hard predicate for presence (`present ⟺ succeeded ≥ 1`)."

## Task 6 — remove the now-false `non_gaap_eps_note`

- Description: Delete the stale `us_specific.non_gaap_eps_note` string
  (`"Out of scope for T3 v1; lives in 8-K narratives."`). Once the earnings
  8-K's narrative IS in the pack, this note points at a gap that no longer
  exists — leaving it is technical debt by design (brief, Axis 5). Scope is
  this one note only: `segment_revenue_note` describes a genuinely still-open
  gap (XBRL segment revenue) and **stays**.
- Module: `investing-toolkit/skills/data-markets/scripts/pack_us.py`
- Files touched:
  - `investing-toolkit/skills/data-markets/scripts/pack_us.py`
  - `investing-toolkit/tests/data/test_data_markets_us.py`
  - `investing-toolkit/tests/data/fixtures/data-us-memo-fetch-sample.json`
- Context paths:
  - `investing-toolkit/skills/data-markets/scripts/pack_us.py:593-596` (`us_specific`)
- Acceptance:
  - RED: `tests/data/test_data_markets_us.py::test_us_specific_drops_stale_non_gaap_note` fails — `non_gaap_eps_note` is still present in the pack.
  - GREEN: `pack_memo_fetch("AAPL")["us_specific"]` has no `non_gaap_eps_note`
    key, and still has `segment_revenue_note` (the guard that this removal did
    not overreach).
- External surfaces: none.
- Dependencies: Task 3 completes first (same file and same fixture; and the note is only false *once* the narrative is actually wired).
- Independent: true  # parallel-eligible with Task 7 (both hang off T3; file sets disjoint)
- Brief item covered: "`pack_us.py:594` — `us_specific.non_gaap_eps_note` … Remove or rewrite it in the same PR."

## Task 7 — live network shape-anchor for the memo→narrative seam

- Description: Add a `@pytest.mark.network` end-to-end anchor that runs the
  real `pack_memo_fetch` narrative path against the live SEC API for one
  ticker and asserts the seam holds: the selection really finds an item-2.02
  8-K, the producer really returns file-backed sections, and the wrapper's
  counts really reconcile. This exists because repo memory
  (`fixtures-mirror-producer-shape`) records that **skipping a live anchor is
  one of the two ways a green offline suite certifies a production crash** —
  and on this very arc a live anchor caught stale grounding three times. It is
  deselected in CI (`-m "not network"`), so it costs the offline suite nothing.
- Module: `investing-toolkit/tests/data/test_data_markets_live.py`
- Files touched:
  - `investing-toolkit/tests/data/test_data_markets_live.py`
- Context paths:
  - `investing-toolkit/tests/data/test_data_markets_live.py` (existing `@pytest.mark.network` shape anchors — mirror their idiom)
  - `investing-toolkit/skills/data-markets/scripts/pack_us.py` (Task 3's wiring)
- Acceptance:
  - RED: `tests/data/test_data_markets_live.py::test_live_memo_fetch_narrative_seam` fails (test does not exist / the seam is unwired).
  - GREEN: run with network enabled against a real ticker, the pack's
    `sec_narrative` carries `succeeded >= 1`, at least one selected filing is
    an 8-K whose selected accession's submissions `items` include `2.02`, and
    at least one returned section carries a `text_path` that exists on disk.
  - GREEN: the offline suite is unchanged — `-m "not network"` still collects
    and passes exactly as before (this test must be deselected there).
- External surfaces: live SEC EDGAR (`data.sec.gov` submissions + Archives) via
  edgartools. SEC identity is HARDCODED in `sec_edgar_client.USER_AGENT` — it is
  NOT read from an env var (the plan originally claimed otherwise; Task 7's
  implementer checked and corrected it). Network-marked and CI-deselected by design.
- Dependencies: Task 3 completes first (there is no seam to anchor until the wiring exists).
- Independent: true  # parallel-eligible with Task 6 (both hang off T3; file sets disjoint)
- Brief item covered: "a structurally visible failure surface … full provenance per section … section bodies on disk (`text_path`)" — verified against the real producer rather than a fixture.

## Task 8 — replace the filing-count window with a policy-derived DATE window

**Added mid-execution.** Not in the original plan: Task 7's live anchor
discovered this defect against the real SEC API, exactly as that task was
designed to. Recorded here so the plan matches what shipped.

- Description: `pack_memo_fetch` fetched filings with `--limit 8` — a count cap
  **across all forms combined**. AAPL's 8-K/10-Q volume crowded the annual 10-K
  entirely out of the window, so the selection reported "no 10-K filing found":
  a **FALSE GAP**, i.e. the data layer fabricating a "data missing" signal — the
  precise fabrication class this repo's defenses exist to prevent, produced by us,
  upstream of them. Replace the count window with a window derived from what the
  POLICY needs (the same time-not-count law the brief already states, applied one
  layer further up — the count window was the root cause).
- Module: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- Files touched:
  - `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
  - `investing-toolkit/skills/data-markets/scripts/pack_us.py`
  - `investing-toolkit/tests/data/test_sec_narrative.py`
  - `investing-toolkit/tests/data/test_data_markets_us.py`
  - `investing-toolkit/tests/data/test_data_markets_live.py`
- Acceptance:
  - RED: a 10-K pushed beyond the old window by 8-K/10-Q volume is reported as a
    gap; assert it IS selected.
  - RED: a 10-K dated `366 + 104` days back (a Rule 12b-25 NT-10-K extension lag)
    is dropped by the first-cut 456-day window; assert it IS recovered.
  - GREEN: window = `max(366 + 105 + 30, n_quarters * 92)` = **501** days at N=4.
    `105` = the 90-day non-accelerated 10-K deadline **plus SEC Rule 12b-25's
    automatic 15-calendar-day extension** (the first cut used 90 and was rejected:
    the true worst case is 105, and 456 left only 1 day of slack). `30` is a
    deliberate margin.
  - GREEN: a GENUINE absence still gaps — no false gap traded for a false presence.
  - GREEN (live): AAPL's 10-K is selected; the only remaining gap is the
    not-yet-filed current quarter's 8-K — a real absence.
- Residual risk, accepted and documented in code: a filer that blows even the
  EXTENDED deadline (genuinely delinquent) still produces a gap. That is correct
  — the 10-K really is overdue.
- Also: `list_filings` no longer `break`s early on the date cutoff; it filters every
  row. The early break rested on an unverified "SEC `recent` arrays are
  date-descending" assumption — structurally the same "truncate early on an
  assumption" pattern as the `--limit 8` bug it replaced.
- Dependencies: Task 7 completes first (it found the defect).
- Independent: false
- Brief item covered: the brief's design law — "The selection window is anchored in
  TIME (quarters), never in filing count" — which the filings FETCH was violating
  even after the selection honored it.
