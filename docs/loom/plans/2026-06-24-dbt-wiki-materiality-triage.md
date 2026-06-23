# Plan: dbt-wiki Phase 2 — materiality triage

Source brief: docs/loom/specs/2026-06-24-dbt-wiki-materiality-triage.md
Total tasks: 10
Critical-path depth: 5 (≤5) — T1→T2→{T3‖T4}→T5→{T6‖T7‖T8‖T9‖T10}
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-24, round 2, 14/14 — Task 6 split per-module resolved the round-1 Check-4 gap)

Test convention: PEP-723 inline deps + custom `check(name, cond)` runner ending in
`<pass>/<total> passed` + `sys.exit`, per `skills/redistill/assets/collect_redistill_worklist_test.py`.
SKILL.md prose tasks use grep/structural RED→GREEN (Claude-prose can't pytest).

## Task 1 — logic_sha helper (comment-stripped normalized SQL hash)
- Description: Add `compute_logic_sha(sql, dialect="redshift") -> {"sha", "method"}`:
  md5 of `sqlglot.parse_one(sql, dialect).sql(comments=False, normalize=True)`;
  on sqlglot parse failure fall back to md5 of a regex comment-strip
  (`--…`, `/*…*/`, `{#…#}`) + whitespace-collapse, with `method` = "sqlglot" |
  "regex". Empty/None sql → method "regex", stable sha of "".
- Module: skills/rescan/assets/logic_sha.py
- Files touched: skills/rescan/assets/logic_sha.py, skills/rescan/assets/logic_sha_test.py
- Context paths:
  - skills/init/assets/extract_column_lineage.py  (sqlglot import + dialect pattern, PEP-723)
  - skills/redistill/assets/collect_redistill_worklist_test.py  (test-runner convention)
- Acceptance:
  - RED: skills/rescan/assets/logic_sha_test.py fails (module/function undefined)
  - GREEN: comment-only difference → identical sha; logic difference (same columns) →
    different sha; unparseable SQL → method "regex" + non-crashing sha; method flag correct.
- External surfaces: sqlglot (already a declared dependency; parse + .sql() serialization,
  comments=False / normalize=True). Pin via existing PEP-723 `sqlglot>=25.0`.
- Dependencies: none
- Independent: true
- Brief item covered: "a `logic_sha` for a model = md5 of its compiled SQL after
  stripping comments and normalizing via sqlglot … regex comment-strip fallback + method flag" (Smallest End State #1)

## Task 2 — per-model materiality classifier + logic_sha cache
- Description: Add `classify_changed_models(changed, cache, dialect="redshift") ->
  (materiality_map, updated_cache)`. `changed` = list of
  `{uid, status: added|modified|removed, old: {columns(set), depends_on(set),
  materialization} | None, new: {columns, depends_on, materialization, compiled_sql}}`.
  Per model: added/removed → "material"; modified → "material" if column-name-set OR
  depends_on OR materialization changed, OR new logic_sha != cached logic_sha, OR
  logic_sha `method=="regex"`, OR no cached baseline; else "cosmetic". Update cache
  `{uid: {sha, method}}` for every processed uid. Uses Task 1's `compute_logic_sha`.
- Module: skills/rescan/assets/classify_materiality.py
- Files touched: skills/rescan/assets/classify_materiality.py, skills/rescan/assets/classify_materiality_test.py
- Context paths:
  - skills/rescan/assets/logic_sha.py  (the function it composes — from Task 1)
  - skills/rescan/SKILL.md  (Step 2 modified-detection fields it mirrors, ~L157-172)
- Acceptance:
  - RED: skills/rescan/assets/classify_materiality_test.py fails (undefined)
  - GREEN: comment-only modified → "cosmetic" (edge 2,3); logic change same columns →
    "material" (edge 1); no cached baseline → "material" (edge 5); regex-method →
    "material" (edge 6); added & removed → "material" (edge 7); cache updated for all.
- External surfaces: none beyond Task 1's transitive sqlglot.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "rescan maintains _internal/logic_sha_cache.json … emits
  _internal/last_rescan_materiality.json … material if column-name-set, depends_on,
  materialization, OR logic_sha changed; or added/removed; or regex fallback / no baseline" (Smallest End State #2, #3)

## Task 3 — page-level triage (OR-aggregation over derived_from)
- Description: Add `triage(groups, materiality_map) -> {"material": {domain: [pages]},
  "cosmetic": [pages]}`. For each stale page in the work-list groups, a page is
  "material" iff ANY uid in `(page.derived_from ∩ materiality_map.keys())` maps to
  "material"; otherwise "cosmetic". Material pages keep their domain grouping; cosmetic
  pages are collected flat (dropped from the gate, still stale). A page with no changed
  model in the map → "cosmetic" (defensive).
- Module: skills/sync/assets/triage_worklist.py
- Files touched: skills/sync/assets/triage_worklist.py, skills/sync/assets/triage_worklist_test.py
- Context paths:
  - skills/redistill/assets/collect_redistill_worklist.py  (groups/entry shape: {slug,path,folder,derived_from})
- Acceptance:
  - RED: skills/sync/assets/triage_worklist_test.py fails (undefined)
  - GREEN: page with mixed material+cosmetic derived_from → "material" (edge 4);
    page with only-cosmetic changed models → "cosmetic"; cross-domain page triaged over
    its full derived_from (edge 8); material pages keep domain grouping.
- External surfaces: none (pure dict/set logic).
- Dependencies: Task 2 completes first  (consumes the materiality_map schema Task 2 defines)
- Independent: false
- Brief item covered: "a stale knowledge page is material iff ANY of its
  derived_from ∩ changed_uids models is material (OR-aggregation). Cosmetic-only stale
  pages are dropped from the gate" (Smallest End State #4)

## Task 4 — wire logic_sha + materiality map into rescan/SKILL.md
- Description: Edit rescan Step 2 to compute each changed model's logic_sha (run
  `<SKILL_DIR>/assets/classify_materiality.py`), read/update
  `.dbt-wiki/_internal/logic_sha_cache.json`, and (near Step 6.5) write the per-model
  verdict to `.dbt-wiki/_internal/last_rescan_materiality.json`. Self-heal block (Step 0)
  must copy the two new rescan assets into `_internal/` like other scripts. Add `logic_sha.py`
  + `classify_materiality.py` to the self-heal list. rescan stays 0-LLM.
- Module: skills/rescan/SKILL.md
- Files touched: skills/rescan/SKILL.md
- Context paths:
  - skills/rescan/SKILL.md  (Step 0 self-heal ~L31-41, Step 2 ~L131-172, Step 6.5 ~L446-471)
  - skills/rescan/assets/classify_materiality.py  (entry point invoked — from Task 2)
- Acceptance:
  - RED: `grep -c 'last_rescan_materiality\|logic_sha' skills/rescan/SKILL.md` == 0
  - GREEN: rescan Step 2 references computing/caching logic_sha and emits
    `last_rescan_materiality.json`; self-heal list includes the two new assets;
    `<SKILL_DIR>/...` placeholder convention used (not bare `../`).
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "rescan maintains _internal/logic_sha_cache.json … emits
  _internal/last_rescan_materiality.json for every changed model" (Smallest End State #2, #3)

## Task 5 — wire triage into sync/SKILL.md gate
- Description: Insert a triage step in sync after work-list collection (Step 2) and before
  the gate (Step 3): run `<SKILL_DIR>/assets/triage_worklist.py` over the work-list +
  `.dbt-wiki/_internal/last_rescan_materiality.json`; only **material** pages enter the
  gate; cosmetic-only pages are reported as "skipped (cosmetic-only)" and left stale.
  If the materiality map is absent (rescan from an older run / first upgrade) → treat all
  as material (no triage, current behaviour) and note it. Update the Phase-1 "no triage"
  note (sync ~L24-27) to reflect triage now shipping.
- Module: skills/sync/SKILL.md
- Files touched: skills/sync/SKILL.md
- Context paths:
  - skills/sync/SKILL.md  (Step 2 ~L48-68, Step 3 gate, the Phase-2 note ~L24-27)
  - skills/sync/assets/triage_worklist.py  (entry point invoked — from Task 3)
- Acceptance:
  - RED: `grep -c 'triage\|cosmetic-only\|last_rescan_materiality' skills/sync/SKILL.md` == 0
  - GREEN: sync runs triage between collection and gate; cosmetic-only pages bypass the gate
    and are surfaced; missing-map fallback = all-material; the Phase-2 note updated.
- Dependencies: Tasks 3, 4 complete first
- Independent: false
- Brief item covered: "sync triage step … Cosmetic-only stale pages are dropped from the
  gate (left flagged stale, not re-distilled, surfaced in the summary). Only material pages
  enter the gate" (Smallest End State #4)

## Task 6 — version bump plugin.json 3.0.0 → 3.1.0
- Description: Bump `version` in plugin.json from 3.0.0 to 3.1.0 (additive minor — triage
  is a new feature, no breaking change).
- Module: .claude-plugin/plugin.json
- Files touched: .claude-plugin/plugin.json
- Context paths:
  - .claude-plugin/plugin.json  (current "version": "3.0.0")
- Acceptance:
  - RED: `grep -c '"version": "3.1.0"' .claude-plugin/plugin.json` == 0
  - GREEN: `grep -c '"version": "3.1.0"' .claude-plugin/plugin.json` == 1
- Dependencies: Tasks 4, 5 complete first
- Independent: true
- Brief item covered: ships the Decision (approach B feature) — version reflects the new triage capability.

## Task 7 — CHANGELOG 3.1.0 entry
- Description: Add a `## [3.1.0] — 2026-06-24` entry above the 3.0.0 entry describing the
  materiality triage: sync auto-skips the redistill gate for cosmetic-only changes via a
  comment-stripped logic_sha (rescan emits a materiality map). Preserve history.
- Module: CHANGELOG.md
- Files touched: CHANGELOG.md
- Context paths:
  - CHANGELOG.md  (3.0.0 entry format / Keep-a-Changelog style)
- Acceptance:
  - RED: `grep -c '## \[3.1.0\]' CHANGELOG.md` == 0
  - GREEN: `grep -c '## \[3.1.0\]' CHANGELOG.md` == 1; 3.0.0 entry still present (history intact).
- Dependencies: Tasks 4, 5 complete first
- Independent: true
- Brief item covered: documents the shipped Decision (approach B triage feature).

## Task 8 — README.md retire Phase-2 backlog line
- Description: In README.md, remove/retire the "materiality triage in sync (Phase 2)"
  backlog item (now shipped) and note that sync auto-skips cosmetic-only changes.
- Module: README.md
- Files touched: README.md
- Context paths:
  - README.md  (backlog item "materiality triage in sync (Phase 2)")
- Acceptance:
  - RED: `grep -c 'materiality triage in sync (Phase 2)' README.md` == 1 (the stale backlog line)
  - GREEN: that backlog line is gone; README reflects sync auto-skipping cosmetic-only changes.
- Dependencies: Tasks 4, 5 complete first
- Independent: true
- Brief item covered: retires the README "materiality triage in sync (Phase 2)" backlog line added in Phase 1.

## Task 9 — README.ja.md retire Phase-2 backlog line
- Description: In README.ja.md, retire the materiality-triage (Phase 2) backlog item and
  note sync auto-skips cosmetic-only changes (JA).
- Module: README.ja.md
- Files touched: README.ja.md
- Context paths:
  - README.ja.md  (the JA backlog item mirroring README.md)
- Acceptance:
  - RED: the JA Phase-2 triage backlog line is present
  - GREEN: that JA backlog line is retired; JA text reflects shipped triage.
- Dependencies: Tasks 4, 5 complete first
- Independent: true
- Brief item covered: tri-language consistency — retires the JA Phase-2 backlog line added in Phase 1.

## Task 10 — README.zh-TW.md retire Phase-2 backlog line
- Description: In README.zh-TW.md, retire the materiality-triage (Phase 2) backlog item and
  note sync auto-skips cosmetic-only changes (zh-TW).
- Module: README.zh-TW.md
- Files touched: README.zh-TW.md
- Context paths:
  - README.zh-TW.md  (the zh-TW backlog item mirroring README.md)
- Acceptance:
  - RED: the zh-TW Phase-2 triage backlog line is present
  - GREEN: that zh-TW backlog line is retired; zh-TW text reflects shipped triage.
- Dependencies: Tasks 4, 5 complete first
- Independent: true
- Brief item covered: tri-language consistency — retires the zh-TW Phase-2 backlog line added in Phase 1.

## Notes

- Helpers live in `skills/rescan/assets/` (logic_sha, classify_materiality — rescan
  computes them) and `skills/sync/assets/` (triage_worklist — sync owns the gate
  decision). `collect_redistill_worklist.py` is left UNCHANGED (triage is a separate
  helper, per brief "decide in planning" → separate helper chosen: keeps the committed,
  reviewed Phase-1 helper untouched).
- All `_internal/*.json` are rebuildable caches (precedent: ownership.json).
- `<SKILL_DIR>/...` placeholder convention is mandatory for cross-asset paths (the Phase-1
  review 🟡 — bare `../` breaks after rescan's `cd` to git root).
