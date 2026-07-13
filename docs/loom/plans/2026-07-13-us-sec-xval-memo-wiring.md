# Plan: wire analysis-xval into the equity-memo pipeline

**Source brief**: docs/loom/specs/2026-07-13-us-sec-xval-memo-wiring.md
**Total tasks**: 6
**Critical-path depth**: 3 (≤5 ✓ — deepest chain T2→T3→{T4,T5})
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-13; 14/14, round 2 after a Check-8 traceability fix + T4/T5 parallel-marking)

> **Input**: brainstorming brief (NOT a change-folder). Change-folder detection: no path
> handed (Layer 0 = explicit none); the one non-archived folder
> `2026-07-12-us-sec-primary-source-layer` is the SEC arc's 3-capability spec and does NOT
> cover memo-wiring (the consumption layer) — **deliberately NOT bound** (binding it would
> force coverage of unrelated narrative/xval/operational-kpi scenarios). No scenario-coverage
> check applies (brief-only input).
>
> **Layer discipline** (brief §Decision): the DATA parts (companyfacts pack builder, Source-A
> cells extraction+wrap, pack emission) live in **data-markets**; the COMPUTE (running
> `xval_compute`) lives in the **report-equity-memo analysis phase** — mirroring dcf/comps, NOT
> narrative's eager-in-pack. T5/T6 are prose (SKILL.md / seed-contract) — verified by a
> structural RED diagnostic + cold-read (per the repo's Claude-prose-can't-pytest reality),
> not a Python unit test.

## Task 1 — companyfacts Source-B pack builder

- **Description**: Add `build_companyfacts_pack(cik)` to `sec_edgar_client.py` that fetches the CIK's
  companyfacts (via the existing `fetch_facts`) and reshapes it into the exact Source-B pack shape
  `xval_compute.build_source_b_index` requires: `{"cik": <int>, "facts": {"<taxonomy>": {"<tag>":
  [<row>, ...]}}}` where each row is the `summarize_concept` shape (`{start, end, value, accn, form,
  fy, fp, filed}`). This is the Open-Q2 keystone — `fetch_facts`/`summarize_concept` exist but emit
  the wrong shape (raw JSON / a flat list). On a companyfacts fetch error, return a loud error slot
  (mirroring the file's `_acquire_error` convention), never a fabricated pack.
- **Module**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`, `investing-toolkit/tests/data/test_sec_xval.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`  (`fetch_facts` :237, `summarize_concept` :269, `_acquire_error` :807)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (`build_source_b_index` :133 — the exact consumer shape)
- **Acceptance**:
  - **RED**: `test_sec_xval.py::test_build_companyfacts_pack_shape` — given a mocked companyfacts raw payload (`data["facts"]["us-gaap"]["Revenues"]["units"]["USD"] = [...]`), `build_companyfacts_pack(cik)` returns `{"cik", "facts": {"us-gaap": {"Revenues": [rows...]}}}` where each row has the `summarize_concept` keys; and the result feeds `build_source_b_index` without error (round-trip: the built pack is a valid Source-B pack).
  - **GREEN**: the reshape produces the consumer-required shape; a fetch error returns an error slot, not a fabricated pack.
- **External surfaces**: SEC companyfacts API via the existing `fetch_facts` (already grounded); no new external surface.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: brief §Smallest End State part 1 — "Source-B companyfacts pack builder (the keystone / Open-Q2): a new data-markets function that turns companyfacts into `{cik, facts:{taxonomy:{tag:[rows]}}}`".

## Task 2 — Source-A cells pack producer (latest 10-K, envelope-wrapped)

- **Description**: Add `_fetch_xval_source_a(filings_rows)` to `pack_us.py` (mirroring `_fetch_sec_narrative`)
  that selects the latest 10-K accession from the already-fetched `sec_filings` rows, acquires the filing
  (`_acquire_raw_filing`), calls `extract_statement_cells` per primary statement (balance sheet / income /
  cash flow / equity), and **wraps the bare cell list into the Source-A pack envelope** `{"accession",
  "statement_name", "cells": [...]}` (defusing the documented envelope seam). A `StatementNotFound` (or the
  error-slot return) for a statement is a loud per-statement skip recorded in the status envelope, never a
  crash or a fabricated cell.
- **Module**: `investing-toolkit/skills/data-markets/scripts/pack_us.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/pack_us.py`, `investing-toolkit/tests/data/test_data_markets_us.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/pack_us.py`  (`_fetch_sec_narrative` :603 — the producer+status pattern to mirror; `sec_filings` rows :724)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`  (`extract_statement_cells` :1645 returns a BARE list or an error dict; `_acquire_raw_filing` :823)
- **Acceptance**:
  - **RED**: `test_data_markets_us.py::test_fetch_xval_source_a_wraps_cells_envelope` — with `extract_statement_cells` mocked to return a bare `[cell, ...]` list, `_fetch_xval_source_a(filings_rows)` returns a structure whose per-statement entry is the `{"accession", "statement_name", "cells": [...]}` envelope (the bare list is WRAPPED, not passed through); a mocked `StatementNotFound`/error-slot statement is recorded as a skipped statement, not crashed.
  - **GREEN**: the producer wraps every statement's cells into the envelope + records loud per-statement skips.
- **External surfaces**: edgartools statement extraction via the existing `extract_statement_cells`/`_acquire_raw_filing` (already grounded).
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: brief §Smallest End State part 1 — "Source-A doc-table-cells pack: acquire the latest 10-K filing … call extract_statement_cells per primary statement, and wrap the bare cell list into `{accession, statement_name, cells:[...]}`".

## Task 3 — emit xval_source_a + xval_source_b from pack_memo_fetch (depth-1 status)

- **Description**: Wire `build_companyfacts_pack` (Task 1) + `_fetch_xval_source_a` (Task 2) into
  `pack_memo_fetch`'s return dict as two new top-level keys `xval_source_a` and `xval_source_b`, each
  carrying a **depth-1 `_status` envelope** with the `{requested, succeeded, failed}` count-triple pattern
  (mirror `_fetch_sec_narrative`'s status discipline — never require walking nested `cells`/`facts` to
  learn completeness). The keys are data-bearing on success and carry a loud depth-1 failure signal on
  error.
- **Module**: `investing-toolkit/skills/data-markets/scripts/pack_us.py`
- **Files touched**: `investing-toolkit/skills/data-markets/scripts/pack_us.py`, `investing-toolkit/tests/data/test_data_markets_us.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/data-markets/scripts/pack_us.py`  (`pack_memo_fetch` :700, return dict :741-763, narrative status triple :603-621)
- **Acceptance**:
  - **RED**: `test_data_markets_us.py::test_pack_memo_fetch_emits_xval_packs_with_status` — `pack_memo_fetch(ticker)` (Tasks 1+2 mocked) returns a dict with `xval_source_a` and `xval_source_b` keys, each exposing a depth-1 `_status` with a `{requested, succeeded, failed}`-style triple; a mocked companyfacts/extraction failure surfaces as a depth-1 failed status (not a silent empty).
  - **GREEN**: both keys present with depth-1 status; failures are depth-1 visible.
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false
- **Brief item covered**: brief §Smallest End State part 1 — "Both land as memo-fetch pack keys with a depth-1 `_status` envelope".

## Task 4 — pack_inventory recognizes xval keys via positive allowlist

- **Description**: Extend `pack_inventory.py` so the new `xval_source_a` / `xval_source_b` pack keys are
  classified **present/absent by a positive data-shape allowlist**, not by an error-key denylist — per the
  `shared-classifier-over-open-dialects-needs-allowlist` lesson. A data-bearing xval pack reports present; a
  depth-1-failed or absent one reports absent; the change must NOT reopen the false-presence hole for the
  other 4 markets' sections.
- **Module**: `investing-toolkit/skills/report-equity-memo/scripts/pack_inventory.py`
- **Files touched**: `investing-toolkit/skills/report-equity-memo/scripts/pack_inventory.py`, `investing-toolkit/tests/report/test_pack_inventory.py`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/report-equity-memo/scripts/pack_inventory.py`  (`_is_failed_section` :98, `present = keys > 0 and not _is_failed_section` :131, `build_inventory` :143)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md`
- **Acceptance**:
  - **RED**: `test_pack_inventory.py::test_xval_packs_present_by_positive_allowlist` — `build_inventory` on a pack containing a data-bearing `xval_source_a`/`xval_source_b` reports them present; on a depth-1-failed xval pack reports absent; and a control assertion confirms an existing section's presence classification is unchanged (no false-presence regression).
  - **GREEN**: xval keys classified by positive data-shape; no regression on the other markets' sections.
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: brief §Smallest End State part 1 — "a pack_inventory-safe (positive-allowlist) data shape, so pack_inventory reports them present/absent correctly … without reopening the false-presence hole".

## Task 5 — report-equity-memo xval analysis step (Phase 2.6) + Phase-4 handoff

- **Description**: Add a report-equity-memo analysis step (a Phase alongside comps/DCF) that runs
  `xval_compute.py --source-a <xval_source_a pack> --source-b <xval_source_b pack>` on the memo-fetch
  packs → `xval.json`, and hand `xval.json` into the Phase-4 investing-team delegation packet (mirroring
  how `dcf.json` / `comps.json` are handed in Phase 4). PROSE task (SKILL.md orchestration — no Python
  unit; the repo's Claude-prose-can't-pytest reality). Respect the layer discipline: the COMPUTE runs here
  (analysis phase), not in the data-markets pack layer.
- **Module**: `investing-toolkit/skills/report-equity-memo/SKILL.md`
- **Files touched**: `investing-toolkit/skills/report-equity-memo/SKILL.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/report-equity-memo/SKILL.md`  (Phase 2.5 comps + Phase 3 DCF orchestration + Phase 4 delegation packet — the pattern to mirror)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/scripts/xval_compute.py`  (CLI `--source-a`/`--source-b` :647)
- **Acceptance**:
  - **RED (structural diagnostic)**: `grep -n "xval_compute" investing-toolkit/skills/report-equity-memo/SKILL.md` returns nothing before the edit (the xval analysis step is absent). GREEN: the SKILL.md documents an xval analysis phase running `xval_compute.py --source-a … --source-b … → xval.json` from the memo-fetch packs, and `xval.json` is listed in the Phase-4 delegation packet — verified by a fresh-context cold-read that the invocation reads the two xval pack keys and hands xval.json to investing-team.
  - **GREEN**: the SKILL.md carries a runnable-by-the-agent xval analysis step + Phase-4 handoff, layer-consistent with comps/DCF.
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: brief §Smallest End State part 2 — "a new report-equity-memo Phase-2.5 step: run xval_compute.py --source-a <pack> --source-b <pack> → xval.json, mirroring the existing dcf.json / comps.json analysis steps"; also part 3 — "hand xval.json into the Phase-4 investing-team delegation packet".

## Task 6 — seed-contract element 6 (`xval` — read before you cite)

- **Description**: Add element 6 to `phase4-seed-contract.md` — an `xval` element instructing the memo
  writer to READ the xval `high_alerts` (doc-vs-XBRL divergences) and `single_source` doc-only findings
  before citing a financial-statement number, and to weight/challenge a number a high-alert flags (mirroring
  §5 `sec_narrative` read-before-cite + §1 rule_verdict). Update the seed-contract header ("five elements" →
  "six") and the orchestrator acceptance check to reference the new element. PROSE task (cold-read verified).
- **Module**: `investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md`
- **Files touched**: `investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md`
- **Context paths**:
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md`  (element format :14-85, §5 sec_narrative :61, orchestrator acceptance check :87)
  - `/Users/kouko/.supacode/repos/monkey-skills/finacial-analytics-r2/investing-toolkit/skills/analysis-xval/SKILL.md`  (the report envelope: high_alerts / single_source / source_mode the writer reads)
- **Acceptance**:
  - **RED (structural diagnostic)**: `grep -n "## 6. \`xval\`" investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md` returns nothing before the edit. GREEN: element `## 6. \`xval\`` exists with a read-high_alerts-before-cite instruction; the "five elements" header count is updated to six; the orchestrator acceptance check references element 6 — verified by a fresh-context cold-read.
  - **GREEN**: element 6 present, count updated, acceptance check references it.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: brief §Smallest End State part 3 — "add a seed element 6 ('read the xval high_alerts / doc-only findings before you cite a financial number') mirroring narrative's seed §5".

## Notes

### Layer discipline (the load-bearing decision)
Data fetch (Tasks 1–3, data-markets) vs compute (Task 5, report-equity-memo analysis phase) is split per
CLAUDE.md's Cross-Plugin Delegation contract ("data layer I/O only; analysis layer computes"). This is why
xval does NOT follow narrative's eager-in-pack pattern (narrative is pure data) but the comps/dcf
separate-analysis-step pattern. Rejected alternatives recorded in the brief §Alternatives Considered.

### Prose tasks (T5, T6)
report-equity-memo SKILL.md + the seed contract are agent-followed PROSE, not pytest-able (repo memory:
Claude-prose-can't-pytest). Their RED is a structural grep diagnostic (section absent → present); their real
acceptance is a fresh-context cold-read that the documented step/element is correct and followable. This is
the repo's established discipline for process/prose mechanisms.

### Deferred (brief §Out of Scope)
A dedicated hard mechanical trust-signal GATE for xval high-alerts (a CHK-CIT-007-adjacent `rule_verdict`
check) is DEFERRED — the seed read-instruction (Task 6) is the smallest honest surfacing; the gate is a
proven-wiring follow-on. Also deferred: xval on the 10-Q (this slice: latest 10-K only).

### Close-out obligations (finishing-a-development-branch)
- Version bump: any change under `investing-toolkit/skills/**` requires bumping
  `investing-toolkit/.claude-plugin/plugin.json` (2.8.0 → 2.9.0) + `python3 scripts/sync_codex_manifests.py
  investing-toolkit`.
- Update the `xval_compute.py` docstring "Open Q2 — companyfacts fetcher not wired" caveat (:89-133): the
  builder now exists (retire the caveat) — a mechanical doc touch at close-out or folded into Task 1.
- Commit the untracked brief with the first SDD commit.

### Kickoff one-way-door decisions (surface at SDD kickoff)
1. **Layer placement** — data fetch vs analysis-phase compute (convention-locked by the layer discipline +
   comps/dcf precedent; late-vetoable).
2. **Scope: 10-K only** — xval the latest 10-K, defer 10-Q (late-vetoable).
3. **Surfacing depth** — seed read-instruction now, hard gate deferred (late-vetoable).
