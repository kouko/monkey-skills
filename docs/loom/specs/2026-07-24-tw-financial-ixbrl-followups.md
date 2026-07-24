# TW financial iXBRL 2.31.0 post-ship follow-ups

Brief (brainstorming output) — 2026-07-24. Origin: `docs/loom/BACKLOG.md`
§"investing-toolkit TW financial iXBRL 2.31.0 — post-ship follow-ups",
user-selected as the next arc (option (c) of the P3 fork).

## Problem

The 2.31.0 arc shipped the data layer (financial-sector canonical + DCF
fail-loud marker), but the loop is not closed: when `dcf_compute` emits the
structured `{"not_applicable": "financial-sector"}` result for a financial
ticker, **no downstream consumer recognizes the marker**. Recon confirms the
outcome today is *silent degradation*, not a graceful "DCF N/A" and not a
crash: the memo frontmatter's `intrinsic_mid` resolves to null and the
verdict prose is simply absent, with no explanation to the reader. The arc
also carried 🟢 debt: two Rule-of-Three duplications, a fact-count guard that
tests through the *old* decode path, and five dead scratchpad citations.

## Users

- kouko running `report-equity-memo` on TW financial tickers (2882 國泰金,
  2801 彰銀, 2867 三商壽 …) — must get a memo that says *why* DCF is absent.
- Future maintainers of `twse_ixbrl_{canonical,notes}.py` — duplicated
  blocks and dead comment citations raise change cost.

## Smallest End State

1. **(a) DCF N/A consumption** — the three prose surfaces that read dcf.json
   each gain an explicit `not_applicable` branch:
   - `report-equity-memo/SKILL.md` Phase 3/4: on marker, frontmatter
     `intrinsic_mid: null` is *stated* (with reason), not silently defaulted.
   - `report-equity-memo/references/phase4-seed-contract.md`: marker semantics
     defined — `rule_verdict` N/A branch, CHK-THX-007 explicitly vacuous.
   - `domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md`
     (+ template): §DCF renders "DCF N/A — financial sector" with the reason
     string; Deviation Block not required in the N/A branch.
   Producer (`dcf_compute.py`) unchanged.
2. **(b) Rule-of-Three ×2** — extract one shared meta-block helper in
   `twse_ixbrl_canonical.py` (3 sites) and one group+select helper in
   `twse_ixbrl_notes.py` (3 sites). Behavior-preserving; existing 963-test
   suite stays green.
3. **(d) decode-coverage test** — new test asserting whole-file fact-count
   equality under the production `decode_ixbrl_document` (UTF-8-first), per
   `docs/loom/memory/tw-financial-ixbrl-served-utf8-despite-big5-declaration.md`.
4. **(e) citation cleanup** — the 5 dead `scratchpad/fh-measurement*` comment
   citations replaced by the operative measurement fact inline (or trimmed).
5. Version bumps: investing-toolkit → 2.31.1, domain-teams → patch bump;
   codex manifests via `python3 scripts/sync_codex_manifests.py`.

## Current State Evidence

- **Forward**: `dcf_compute.py:419` guards, `:427-442` emits the flat marker
  object (`ticker` / `not_applicable` / `reason` / `_provenance`) — omitting
  every field a normal run emits (`:479-510`, e.g. `intrinsic_value.mid`
  `:483-484`, `verdict_thresholds` `:487`). Consumers:
  `report-equity-memo/SKILL.md` Phase-4 frontmatter clause reads dcf.json
  `mid` → `intrinsic_mid` (~:496 region);
  `references/phase4-seed-contract.md:18-29` reads
  `verdict_thresholds.rule_verdict` (binding-or-gated);
  `investing-team/protocols/deep-equity-research-memo.md:318-332` + template
  `:468-469` render the verdict. Repo-wide grep: **zero** non-producer
  `not_applicable` hits.
- **Reverse (SSOT/ownership)**: memo protocol + gates are owned by
  `domain-teams:investing-team` (CLAUDE.md cross-plugin contract: analysis
  layer stays in domain-teams; toolkit must not replicate gate logic). The
  Phase-4 fix therefore lands in BOTH plugins, each editing its own surface.
- **Error path**: no consumer branches on the marker → `intrinsic_mid`
  silently null; Phase-3 artifact gate is file-existence only
  (`report-equity-memo/SKILL.md:344` — satisfied as-is, per the producer's
  own comment `dcf_compute.py:424-426`); CHK-THX-007 recomputation gate
  (`phase4-seed-contract.md:27-29`) is vacuously satisfied — nothing renders
  an N/A.
- **Data (duplication)**: canonical meta-block triplicated at
  `twse_ixbrl_canonical.py:231-244` (`_derive_total_debt`), `:449-462`
  (`_sum_concepts`), `:700-713` (`_first_present`); varies in `source_label`,
  `concept`, value extraction, and sum-variant `derivation`/`components`
  keys. Notes grouping triplicated at `twse_ixbrl_notes.py:146-154`,
  `:253-267` (fh, nested in per-company loop), `:339-347` (basi); varies in
  `label` arg + fh's outer loop.
- **Boundary (tests/citations)**:
  `test_twse_ixbrl_fixtures.py:76-81` decodes fixtures via
  `big5hkscs, errors="replace"` (old fetch path), not the production
  `decode_ixbrl_document`; comment `:70-75` documents the old rationale.
  Dead citations: `twse_ixbrl_canonical.py:391, 569, 647, 654`,
  `twse_ixbrl_notes.py:217` — no `scratchpad/` or `fh-measurement*` exists
  in the repo.

Evidence paths: `investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py`,
`investing-toolkit/skills/report-equity-memo/SKILL.md`,
`investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md`,
`domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md`,
`investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py`,
`investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py`,
`investing-toolkit/tests/data/test_twse_ixbrl_fixtures.py`.

## Alternatives Considered

- **(a) placement — orchestrator skips DCF section entirely in Phase 3**
  (report-equity-memo branches on the marker and never seeds DCF): rejected —
  the reader would see a memo with no valuation section and no explanation;
  the protocol-owned "DCF N/A + reason" render keeps the fail-loud doctrine
  end-to-end and respects domain-teams' ownership of the memo surface.
- **(a) producer-side fix — emit dummy `verdict_thresholds`** so existing
  prose "works": rejected — a fabricated verdict on a financial ticker is
  exactly the silently-wrong-valuation failure the 2.31.0 guard exists to
  prevent.
- **Narrow space otherwise** — items (b)(d)(e) are mechanical debt paydown
  with no real design alternatives.

## What Becomes Obsolete

- The 5 dead scratchpad citations (removed in this change).
- The two triplicated code blocks (collapsed into shared helpers).
- The implicit "when provided" reading of `rule_verdict` in
  `phase4-seed-contract.md` (replaced by an explicit N/A branch).

## Decision

Ship items (a)(b)(d)(e) as one small branch (`tw-fin-ixbrl-followups`, off
`526c4b10`). (a) is prose/protocol edits across investing-toolkit +
domain-teams, each plugin editing its own surface, both version-bumped.
(b)(d) are TDD-covered code changes; (e) rides along on the touched files.
We will NOT touch `dcf_compute.py` output shape, will NOT build any new
analysis capability, and will NOT re-measure fixture profiles unless the (d)
test exposes a real count drift (that would be a finding, not a silent
re-baseline). Final verification includes one live e2e memo dogfood on a
financial ticker (e.g. 2882) to see the "DCF N/A" render actually appear.

## Out of Scope

- BACKLOG (c) over-soft-cap functions (`dcf_compute.main`,
  `pack_memo_fetch`) — cosmetic, deferred in place.
- BACKLOG (f) US financial filers `sector_class` guard in `pack_us` —
  pre-existing, needs its own arc.
- Endorsement/guarantee note-table reconstruction; 興櫃 multi-period series
  (next major arcs, unchanged in BACKLOG).
- Any change to `dcf_compute.py`'s emitted marker shape.

## Open Questions

- None blocking. (Whether the (d) test finds a count drift under UTF-8-first
  decode is an empirical outcome the plan handles either way.)
