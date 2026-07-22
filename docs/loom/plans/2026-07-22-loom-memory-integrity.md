# Plan: loom-memory store integrity (F1 + F4)

Source brief: docs/loom/specs/2026-07-22-loom-memory-integrity.md
Total tasks: 6
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible (L1: Tasks 1, 3; L2: Tasks 2, 6; L3: Tasks 4, 5)
Plan-document-reviewer verdict: PASS (2026-07-22, round 2 — verified against live skill-structure.yml:305 + loom-code-ci.yml:94)

## Task 1 — store-integrity checker script + test
- Description: Create `scripts/check_loom_memory_integrity.py` (Python stdlib, validate-only fail-loud like `check_version_bump.py`) that validates the loom-memory store's four invariants and names each offender on violation: (a) every body file (`docs/loom/memory/*.md` except README) has an index line in README §Index; (b) every index line points to an existing body file; (c) `filename (minus .md) == frontmatter name`; (d) index-line description `== frontmatter description` byte-identical. Exit 1 + print offenders on any violation, exit 0 clean. Accept a `--store` dir arg (default `docs/loom/memory`) so tests can point at a fixture.
- Module: scripts/check_loom_memory_integrity.py
- Files touched: scripts/check_loom_memory_integrity.py, scripts/test_check_loom_memory_integrity.py
- Context paths:
  - scripts/check_version_bump.py (validate-only + arg + exit-code + fail-loud pattern to follow)
  - docs/loom/memory/README.md (§Index format `[name](name.md) — description` at line 70+; the invariant prose at 71-75)
  - docs/loom/memory/assertion-must-encode-the-property-it-claims.md (frontmatter shape: name/description/type/origin)
- Acceptance:
  - RED (write FIRST): a test builds a tmp fixture store — an entry file present with NO matching index line — and asserts the checker exits nonzero AND stderr/stdout names that file. Also a clean-fixture case exits 0. Both RED against a not-yet-existing checker.
  - GREEN: the checker implements all four invariants; the orphan-fixture test fails the check (names offender), the clean-fixture test passes, byte-identical-description mismatch is caught.
- External surfaces: filesystem read of the store dir + a markdown-frontmatter parse (stdlib only — no PyYAML; parse the `key: value` frontmatter block by hand or with a minimal splitter, matching the repo's no-new-dependency norm).
- Dependencies: none
- Independent: true
- Brief item covered: "F1 — a mechanical store-integrity checker (scripts/check_loom_memory_integrity.py, following check_version_bump.py) with a test, that fails loud and NAMES the offender on any of (a)-(d)."

## Task 2 — backfill the 2 orphan index lines
- Description: Add the two missing index lines to README §Index so the real store passes the Task-1 checker: `ixbrl-dom-traversal-drops-nested-facts` and `market-canonical-must-satisfy-consumer-field-contract`, each `[name](name.md) — <description copied byte-identical from that file's frontmatter>`.
- Module: docs/loom/memory/README.md
- Files touched: docs/loom/memory/README.md
- Context paths:
  - docs/loom/memory/ixbrl-dom-traversal-drops-nested-facts.md (its frontmatter description — copy byte-identical)
  - docs/loom/memory/market-canonical-must-satisfy-consumer-field-contract.md (same)
  - docs/loom/memory/README.md (§Index — where to insert, matching existing line format)
- Acceptance:
  - RED: `python3 scripts/check_loom_memory_integrity.py` against the REAL store exits 1, naming the 2 orphans (this is the diagnostic RED — the real store currently violates invariant (a)).
  - GREEN: after adding the 2 index lines (descriptions byte-identical to frontmatter), the checker exits 0 against the real store.
- Dependencies: Task 1 completes first (the checker must exist to produce the RED/GREEN).
- Independent: true
- Brief item covered: "Backfill the 2 orphan index lines so the check passes."

## Task 3 — F4 staleness caveat in the loom-memory skill recall procedure
- Description: Add one line to the recall procedure of `loom-pipeline/skills/loom-memory/SKILL.md`: before acting on a recalled entry, verify any file/flag/skill it names still exists (mirrors the auto-memory protocol's warning).
- Module: loom-pipeline/skills/loom-memory/SKILL.md
- Files touched: loom-pipeline/skills/loom-memory/SKILL.md
- Context paths:
  - loom-pipeline/skills/loom-memory/SKILL.md (the recall procedure, step 3-4 where entries are surfaced)
- Acceptance:
  - RED: `grep -in "verify.*still\|still exists\|stale" loom-pipeline/skills/loom-memory/SKILL.md` shows no staleness caveat in the recall procedure (RED state).
  - GREEN: the recall procedure carries a one-line "verify any named file/flag/skill still exists before acting on a recalled entry" caveat.
- Dependencies: none
- Independent: true
- Brief item covered: "F4 — a staleness caveat: one line added to the loom-memory recall procedure."

## Task 4 — F4 staleness caveat in the store charter
- Description: Add the same staleness caveat to the store charter in `docs/loom/memory/README.md` (the charter/recall guidance section), so the committed store documents the verify-before-act rule.
- Module: docs/loom/memory/README.md
- Files touched: docs/loom/memory/README.md
- Context paths:
  - docs/loom/memory/README.md (charter §When to record / recall guidance)
- Acceptance:
  - RED: `grep -in "verify.*still\|still exists\|stale" docs/loom/memory/README.md` shows no staleness caveat (RED state).
  - GREEN: the charter carries the "verify a recalled entry's named file/flag/skill still exists before acting on it" caveat.
- Dependencies: Task 2 completes first (same file — README.md; sequential to avoid a same-file edit race).
- Independent: false
- Brief item covered: "F4 — ... and the store charter (docs/loom/memory/README.md)."

## Task 5 — wire the direct checker invocation into CI
- Description: Add a CI step running `python3 scripts/check_loom_memory_integrity.py` (a DIRECT invocation against the real store) to `.github/workflows/skill-structure.yml`, co-located with `check_version_bump.py`'s existing standalone direct-invocation step (that file is where the repo's direct store/structure validators live). NOTE: Task 1's new *test* file (`scripts/test_check_loom_memory_integrity.py`) is already auto-collected by `loom-code-ci.yml`'s existing `pytest … scripts/ …` step — no wiring needed for the test; this task adds only the direct real-store check that fixtures don't cover.
- Module: .github/workflows/skill-structure.yml
- Files touched: .github/workflows/skill-structure.yml
- Context paths:
  - .github/workflows/skill-structure.yml (the `check_version_bump.py` direct-invocation step — mirror its shape for the new checker)
  - scripts/check_loom_memory_integrity.py (the command to wire)
- Acceptance:
  - RED: `grep -rn "check_loom_memory_integrity" .github/workflows/` shows no wiring (RED state).
  - GREEN: a step in `skill-structure.yml` invokes the checker against the real store; running that exact command locally (post-backfill) exits 0; the step is in a PR-triggered job.
- Dependencies: Tasks 1, 2 complete first (checker exists; store is clean so the CI step passes rather than shipping a red main).
- Independent: false
- Brief item covered: "wired into CI as a job."

## Task 6 — bump loom-pipeline + Codex sync
- Description: Bump loom-pipeline (its shipped SKILL.md changed in Task 3) and sync the Codex manifest + CHANGELOG.
- Module: loom-pipeline/.claude-plugin/plugin.json
- Files touched: loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/CHANGELOG.md
- Context paths:
  - loom-pipeline/.claude-plugin/plugin.json (current 0.10.0)
  - loom-pipeline/CHANGELOG.md (entry format)
  - scripts/sync_codex_manifests.py (regenerates the .codex-plugin mirror)
- Acceptance:
  - RED: `python3 scripts/check_version_bump.py --base <branch-base> --head HEAD` exits 1 (loom-pipeline SKILL content changed without a bump).
  - GREEN: loom-pipeline 0.10.0 → 0.11.0; `.codex-plugin` mirror synced (`test_sync_codex_manifests.py` green); CHANGELOG entry added; `check_version_bump` exits 0.
- Dependencies: Task 3 completes first (the SKILL.md change requiring the bump).
- Independent: true
- Brief item covered: "loom-pipeline is plugin-shipped (SKILL.md change) → bump 0.10.0→0.11.0 + codex sync."

## Notes

- The checker is a **new runnable capability** (Task 1): its CI wiring (Task 5) is its command-surface declaration — that satisfies the runnable-capability accretion rule (the verb is declared where the repo declares its checks: the CI workflow).
- Task 4 depends on Task 2 only for same-file (README.md) sequencing, not a semantic dependency.
