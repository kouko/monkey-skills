# Plan: TW iXBRL endorsement/guarantee ingestion

Source brief: docs/loom/specs/2026-07-24-tw-ixbrl-endorsement.md
Total tasks: 4
Critical-path depth: 4 (≤5)
Execution order: sequential (each task builds on the prior; no independent pair)
Plan-document-reviewer verdict: PASS (2026-07-24, round 2 — 14/14 checks)

## Kickoff

Kickoff sweep (2026-07-24): NO one-way-door decisions — all tasks are reversible
data-layer extraction / test / version work; scope (aggregate + per-counterparty
detail) user-decided; concept names + expected values pinned in ## Notes; no
researchable fork left open. Nothing to brief. Tasks are a sequential chain
(depth 4, no independent pair) → SDD dispatches one at a time.

## Decision Log

- **T2 measurement corrected two plan PINs (2026-07-24, checkable-fact resolution,
  not a user decision):** (1) SUM(ActualAmountProvided) is 62.8bn span-scoped, NOT
  the recon's doc-wide 105.9bn — the doc-wide sum conflated the endorsement table
  with a separate 資金貸與 note (74 of 113 facts belong to the other table). The
  extractor sums only endorsement-span rows; this is the correct behavior and
  validates why per-counterparty reconstruction (not doc-wide summing) is needed.
  (2) The "none" fixture is 2882 (0 anchors), NOT 1301 — 1301 actually has 1 real
  endorsement row; the recon mischaracterized it. Both settled by measurement, plan
  PINs corrected, extractor tests assert the measured-correct values.

## Notes

- **Scope (user-decided)**: aggregate summary **+ per-counterparty detail rows**.
- **No parser change, no fetch change** — the data is reachable with the current
  pipeline; the extractor anchors on document order (recon-proven).
- **Citation hygiene from the start** (producer-marker arc lesson): the extractor's
  docstrings/comments cite the `tifrs-notes:` concept names and the operative
  measured fact inline — NEVER a `scratchpad/` path. The recon evidence file
  (`scratchpad/endorsement-recon-evidence.md`) is NOT committed; its key facts
  live in the brief §Current State Evidence.
- **PIN — endorsement concept names (transcribe VERBATIM from recon, `tifrs-notes:`)**:
  outer tuple `EndorsementGuaranteeProvidedToOthers`; row anchor
  `CompanyNameOfTheEndorserGuarantor`; inner tuple `Counterparty2` → `NameOfTheCompany`;
  per-row `LimitOnEndorsementGuaranteeAmountProvidedToIndividualCounterparty`,
  `EndingBalance2`, `ActualAmountProvided`,
  `AmountOfEndorsementsGuaranteesSecuredWithCollateral`,
  `RatioOfAccumulatedEndorsementGuaranteeAmountToNetAsset`,
  `LimitOfTotalGuaranteeEndorsementAmount` (per-endorser ceiling, NOT an aggregate);
  Y/N flags `EndorsementsGuaranteesProvidedToSubsidiaryByParentCompany`,
  `EndorsementsGuaranteesProvidedToParentCompanyBySubsidiaries`,
  `EndorsementsGuaranteesProvidedToCompanyInMainlandChina`.
- **PIN — expected values (台泥 1101)**: 39 endorser rows;
  SUM(ActualAmountProvided) = **62,786,222,000 (span-scoped, endorsement-only)** —
  CORRECTED from the recon's 105.9bn, which was a DOC-WIDE sum that conflated the
  endorsement table with a separate 資金貸與 (financing-to-others) note (74 of 113
  `ActualAmountProvided` facts precede the first endorser anchor and belong to that
  other table). Span-scoping to endorsement rows is the honest total and is exactly
  why per-counterparty reconstruction (not doc-wide summing) is required.
  SUM(EndingBalance2) = 107,613,931,000 ✓ (that concept appears only in the
  endorsement table); row0 endorser=台灣水泥公司 counterparty=聯誠貿易公司
  ending=1,420,000 actual=0; row1 counterparty=信昌投資公司 ending=2,370,000
  actual=1,140,000. (T2 measurement-verified 2026-07-24.)
- **"none" case fixture = 2882** (0 endorser anchors), NOT 1301 — CORRECTED: 台塑
  1301 actually has 1 real endorsement row (本公司→台塑集團開曼, 7.9bn), the recon
  mischaracterized it. No section-present-but-empty placeholder fixture exists; all
  0-anchor fixtures are banks (section absent). The extractor keys on
  `CompanyNameOfTheEndorserGuarantor` anchor count → 0 anchors yields "none"
  identically whether the section is absent or a present-but-empty placeholder, so
  2882 exercises the same none-path. 鴻海 2317 = 28 rows (secondary, not fixtured).
- Test command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/`
  (971 offline-passing at branch base 6fb8505d; 18 live-network failures pre-existing).

## Task 1 — endorsement fixture + fact-count entry

- Description: Add a real MOPS iXBRL fixture for a filer WITH populated endorsement
  rows — 台泥 1101 (39 rows), sourced from the recon body at
  `scratchpad/1101_2026Q1_C.html` (raw bytes; `-ci` industrial, but the body is
  **UTF-8 despite a charset=big5 declaration** — spec-reviewer verified 1101 is
  NOT genuine Big5, refining the assumption that only the financial family is
  served UTF-8) — into the fixtures dir, and register its whole-file fact count. FIRST check whether
  an existing fixture already carries populated endorsement rows (grep the fixtures
  for `CompanyNameOfTheEndorserGuarantor`); if one does, reuse it and SKIP adding the
  2MB blob (note the choice). Else add `twse_ixbrl_1101_2026Q1_C.html`.
- Module: investing-toolkit/tests/data
- Files touched: investing-toolkit/tests/data/fixtures/twse_ixbrl_1101_2026Q1_C.html, investing-toolkit/tests/data/test_twse_ixbrl_fixtures.py (+ a *.profile.json sibling if that is the existing per-fixture count convention)
- Context paths:
  - investing-toolkit/tests/data/test_twse_ixbrl_fixtures.py (EXPECTED_FACT_COUNTS :45, decode tests :68-124)
  - investing-toolkit/tests/data/fixtures/ (existing fixture naming + profile convention)
  - .gitattributes (twse_ixbrl_*.html binary glob — already covers a new file)
- Acceptance:
  - RED: `1101` absent from EXPECTED_FACT_COUNTS (grep → 0) and no 1101 fixture on disk
  - GREEN: fixture present (or an existing populated fixture identified + reused); 1101 (or the chosen fixture) in EXPECTED_FACT_COUNTS; BOTH fact-count tests (legacy big5hkscs + production `decode_ixbrl_document`) pass for it with zero deltas; full offline suite green
- External surfaces: none (offline fixture; body is UTF-8-despite-charset=big5 — production `decode_ixbrl_document` handles it UTF-8-first. NOTE: this refines the tw-financial-ixbrl-served-utf8 memory — the served-UTF-8 behavior is NOT financial-family-only; a -ci industrial filer (1101) shows it too, so encoding is not predictable from taxonomy)
- Dependencies: none
- Independent: false
- Brief item covered: "Current State Evidence — real structure (1101 台泥, 39 rows)"; the populated fixture the extractor test needs (Smallest End State)

## Task 2 — endorsement extractor (per-counterparty rows + aggregate summary)

- Description: Add `extract_endorsement_guarantee_notes(facts)` to
  `twse_ixbrl_notes.py` — reconstruct per-endorser rows by document-order
  segmentation on the `CompanyNameOfTheEndorserGuarantor` anchor (the
  `_fh_npl_tree_segments` document-order trick; endorsement has no leaf `tuple_ref`
  and only shared `context_ref`s, so document order is the sole handle). Each row
  carries endorser / counterparty (inner `Counterparty2`→`NameOfTheCompany`) /
  individual limit / ending balance / actual provided / collateral-secured /
  relationship Y-N flags (concept names per PIN). Also emit a curated aggregate
  summary: SUM(actual), SUM(ending balance), counterparty count, ratio-to-net-asset,
  and a subsidiary-vs-external split derived from the Y/N flags. Handle the
  no-endorsement case (0 `CompanyNameOfTheEndorserGuarantor` anchors; fixture 2882
  — see corrected PIN, NOT 1301) as a first-class "none" result (explicit empty
  summary + empty rows, never a crash or silent zero).
- Module: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py, investing-toolkit/tests/data/test_twse_ixbrl_notes.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py (`_fh_npl_tree_segments` :221-254, `extract_fh_npl_coverage_notes` :257-302, `_group_and_select_current`)
  - investing-toolkit/tests/data/test_twse_ixbrl_notes.py (existing note-test idioms + `_fixture_facts`)
- Acceptance:
  - RED: new test `test_endorsement_guarantee_populated_and_empty` does not exist (collection = 0)
  - GREEN: the test passes — 1101 → 39 rows (row0/row1 endorser+counterparty+amounts per PIN) + aggregate (SUM actual 62,786,222,000 span-scoped, SUM ending 107,613,931,000, count 39, subsidiary/external split); none-case fixture 2882 (0 anchors) → explicit "none" summary + empty rows; full offline suite green
- External surfaces: none (pure in-memory transform, stdlib only)
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "extract_endorsement_guarantee_notes … reconstructs per-endorser rows … + a curated aggregate summary … graceful empty case" (Smallest End State)

## Task 3 — wire into notes routing + flip the deferral test

- Description: Route the endorsement extractor through `_extract_notes` in
  `twse_ixbrl.py` so the curated endorsement field surfaces in the pipeline output
  (for every taxonomy where the section is present — industrials most commonly). In
  the same change, flip the existing deferral test
  `test_curated_notes_excludes_endorsement_guarantee`
  (`test_twse_ixbrl_notes.py:109-120`) from a "must NOT surface" assertion to an
  inclusion assertion (endorsement now surfaces).
- Module: investing-toolkit/skills/data-markets/scripts/twse_ixbrl.py
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl.py, investing-toolkit/tests/data/test_twse_ixbrl_notes.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl.py (`_extract_notes` routing by taxonomy)
  - investing-toolkit/tests/data/test_twse_ixbrl_notes.py (the deferral test to flip, :109-120)
- Acceptance:
  - RED: new test `test_extract_notes_routes_endorsement` (pipeline output carries the endorsement curated field for a populated filer) does not exist / fails today; the deferral test `test_curated_notes_excludes_endorsement_guarantee` still asserts exclusion
  - GREEN: `test_extract_notes_routes_endorsement` passes (populated → data, empty → "none"); the flipped test asserts inclusion; full offline suite green
- External surfaces: none (internal routing, stdlib only)
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "Wired into the notes routing (`_extract_notes` by taxonomy)"; "the deferral test flips to an inclusion test" (Smallest End State / What Becomes Obsolete)

## Task 4 — version bump + manifest sync + BACKLOG + CHANGELOG

- Description: Bump investing-toolkit 2.32.1 → 2.33.0 (new curated data field = minor)
  in `.claude-plugin/plugin.json`; mirror the codex manifest via
  `python3 scripts/sync_codex_manifests.py investing-toolkit`; add a CHANGELOG entry;
  mark BACKLOG §"TW iXBRL 2.27.0" item (b) endorsement/guarantee **shipped** and its
  origin note. domain-teams untouched (memo-render is a deferred follow-up, out of scope).
- Module: investing-toolkit/.claude-plugin/plugin.json (coordination anchor)
- Files touched: investing-toolkit/.claude-plugin/plugin.json, investing-toolkit/.codex-plugin/plugin.json (via sync script only), investing-toolkit/CHANGELOG.md, docs/loom/BACKLOG.md
- Context paths:
  - scripts/sync_codex_manifests.py
  - investing-toolkit/CHANGELOG.md, docs/loom/BACKLOG.md
- Acceptance:
  - RED: `grep -m1 version investing-toolkit/.claude-plugin/plugin.json` → 2.32.1 today
  - GREEN: version reads 2.33.0; sync `--check` clean (no diff on re-run); CHANGELOG entry present; BACKLOG (b) marked shipped
- External surfaces: none (repo metadata; codex via committed sync script)
- Dependencies: Tasks 1, 2, 3 complete first
- Independent: false
- Brief item covered: implied ship step for the Decision (surface the new curated field); What Becomes Obsolete (BACKLOG (b) deferral marked shipped)
