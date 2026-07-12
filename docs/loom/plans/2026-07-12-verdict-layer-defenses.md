# Plan — Verdict-layer defenses for report-equity-memo (weak-model hardening round 2)

**Date**: 2026-07-12
**Branch**: `feat/verdict-layer-defenses`
**Brief-equivalent**: conversation 2026-07-12 (user-approved). Origin: controlled
strong-vs-weak model comparison on identical 2330.TW pipeline data
(`/tmp/memo-model-comparison.md`, session artifact; key findings mirrored in
the tasks below). #539's artifact gates held (no fake completion); the weak
model instead failed at the **verdict layer**: rule deviation dressed as
argument (HOLD vs mechanical SELL, uplift figure in no file), post-gate
un-evaluated edits, false data-unavailability claim (T86/margin data present
in fetch.json), 2.5/5 mandatory disclosures, UTC date leakage.
Rejected alternative (re-confirmed): per-section subagents + merge — fixes
≤1.5/5 failure classes, amplifies cross-section incoherence (observed:
weak memo self-contradicts on comps direction), industry survey (#542)
classes multi-agent debate as architecture theater. Chosen shape:
**numbers-by-code** — mechanical verdict computed by script; LLM adopts or
files a gated Deviation Block.

## Tasks

### A (code, TDD, independent) — `rule_verdict` in dcf_compute.py
- Files: `investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py`,
  `investing-toolkit/tests/analysis/test_analysis_dcf.py`
- `_verdict_thresholds()` gains price-aware application: output block gains
  `rule_verdict` — deterministic string, one of `SELL` / `HOLD` /
  `BUY (grade per analyst conviction)` per the existing rule text
  (price > sell_threshold → SELL; buy_threshold_grade_a < price ≤
  hold_threshold → HOLD; price ≤ buy_threshold_grade_a → BUY…), plus
  `rule_verdict_basis` `{price, compared_to}` so the memo can cite the
  comparison. No behavior change to any existing key.

### B (code, TDD, independent) — pack-section inventory script
- Files: `investing-toolkit/skills/report-equity-memo/scripts/pack_inventory.py`
  (new), `investing-toolkit/tests/report/test_pack_inventory.py` (new)
- CLI: `--input <pack.json>` → JSON to stdout:
  `{sections: {<top-level-key>: {present, kind, rows|keys}}, mops: {<sub>: …},
  _meta: {generated_from, generated_at_source: _status}}` — rows for arrays,
  keys-count for dicts, presence booleans; include `_status` verbatim.
  Pure stdlib, exit 0/64 contract consistent with repo scripts.

### C (prose, orchestrator) — Phase 4 seed contract reference
- Files: `investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md`
  (new), `investing-toolkit/skills/report-equity-memo/SKILL.md` (pointer lines
  only — body is at ~95% token budget, content goes in the reference)
- Content: seed context MUST carry (a) `rule_verdict` from dcf.json — memo
  adopts it or files a Deviation Block (structure defined here; deviation
  with revised thresholds still breaching → auto-reject at gate);
  (b) pack-section inventory JSON — any "data unavailable" claim in the memo
  must be consistent with the inventory; (c) date anchoring — memo date =
  execution date in issuer timezone; figures cite `reference_period`, never
  `fetched_at` (PR#543 lesson class); (d) mandatory-disclosure list with
  "transcribe upstream `_status`/`warnings` verbatim" pass criterion.

### D (prose, orchestrator) — investing-team gate discipline
- Files: `domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md`,
  `domain-teams/skills/investing-team/checklists/investment-thesis-soundness-checklist.md`,
  `domain-teams/skills/investing-team/checklists/primary-source-citation-compliance.md`
- Protocol Phase 6: verdict must state seed `rule_verdict`; deviation only
  via Deviation Block (template added to output template §Verdict). New
  §Gate integrity: any post-gate body edit voids affected gates → diff-scoped
  re-eval; the 2-round cap caps revision rounds, never un-evaluated edits.
- Thesis-soundness checklist: new item — verdict ≠ rule_verdict requires a
  Deviation Block; evaluator recomputes its revised thresholds; still
  breached → NEEDS_REVISION.
- Citation-compliance checklist: new item — upstream `_status` +
  `warnings[]` + seed mandatory disclosures appear verbatim-grade in
  Limitations; silent dropping/relabeling (e.g. FY→TTM) = fail.

### E (chore) — version bumps + sync
- investing-toolkit 2.4.1 → 2.5.0 (+CHANGELOG), domain-teams 5.6.0 → 5.7.0
  (+CHANGELOG), `python3 scripts/sync_codex_manifests.py` for both.

Dependencies: A, B independent (parallel dispatch); C consumes A+B names
(can draft in parallel, finalize after); D independent; E last.
