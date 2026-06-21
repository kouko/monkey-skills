# Plan: framework-audit verify-backfill check

Source brief: docs/loom/specs/2026-06-13-framework-audit-backfill-check.md
Total tasks: 2
Critical-path depth: 2 (≤5)   — T1 (function + CLI) → T2 (SKILL.md doc mirrors the CLI)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-06-13; 14/14, no gaps)

## Conventions
- Run tests from `research-toolkit/skills/deep-deep-research/scripts/`: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q` (baseline 71 passed; clean `__pycache__` with `find -delete`, NOT `rm -rf`).
- stdlib-only; do NOT touch synced primitives (schemas/rank/prompts/dedup.py) or mode_route.py.
- Behavior-additive: do not change existing `backfill`-unrelated functions/CLI.

## Task 1 — framework_audit.py: backfill_check + `backfill` CLI
- Description: Add `backfill_check(gap_angles, confirmed_labels)` to `framework_audit.py`. It returns `{unlanded, landed_count, unlanded_count}` where `unlanded` is the list of gap angles whose case-folded `label` is NOT present in `confirmed_labels` (each unlanded entry preserves `label`, `framework`, `cell`, `query` when present). Normalize labels with casefold+strip on both sides (reuse the label-keying convention from `_angle_keys`). Empty `gap_angles` or all-landed → `unlanded: []`. Wire a `backfill` argparse subcommand reading `{gap_angles, confirmed_labels}` from stdin → the result dict on stdout (mirror the `select` stdin/stdout `main()` idiom). Keep existing `schema`/`classify-prompt`/`audit-prompt`/`select` subcommands working.
- Module: scripts/framework_audit.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/framework_audit.py, research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/framework_audit.py (`select_gaps`/`_angle_keys`/`select` CLI as the mold)
  - research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py (test mold)
- Acceptance:
  - RED: `test_backfill_check_flags_unlanded` — a gap whose label is absent from `confirmed_labels` appears in `unlanded` (with its framework+cell preserved); a gap whose label IS present (case-insensitively) does NOT; empty gaps → `unlanded: []`; `landed_count` + `unlanded_count` sum to len(gap_angles). Plus a `backfill` CLI round-trip (stdin JSON → stdout JSON, exit 0).
  - GREEN: `echo '{"gap_angles":[...],"confirmed_labels":[...]}' | python framework_audit.py backfill` prints `{unlanded, landed_count, unlanded_count}`, exit 0; full suite green (72+).
- Dependencies: none
- Independent: true
- Brief item covered: "`backfill_check(gap_angles, confirmed_labels)` … Returns `{unlanded, landed_count, unlanded_count}` … the gap angles whose label is absent from `confirmed_labels`" + "`backfill` CLI subcommand — stdin … → stdout …"

## Task 2 — SKILL.md: backfill step + quick-ref row
- Description: In the `### Opt-in: Framework completeness-audit` subsection of SKILL.md, add a short step (after the existing select/feed-Stage-2 steps) for the post-verify backfill check: after the pipeline runs, collect `confirmed_labels` (the angle labels whose claims survived Stage-5 quorum), run `python scripts/framework_audit.py backfill` with the TAGGED gap angles (the audit-prompt output, which still has framework+cell) + `confirmed_labels`, then for each `unlanded` gap either re-search that angle within remaining `MAX_FETCH` OR surface it in the report as an explicitly-flagged known gap. State the degradation: empty `unlanded` → nothing to do. Add a `framework_audit.py backfill` row to the Script-invocation quick-reference table with its stdin→stdout shape.
- Module: SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md (the framework-audit subsection + quick-ref table)
- Acceptance:
  - RED: `grep -q "backfill" SKILL.md` fails.
  - GREEN: the backfill step is present in the framework-audit subsection, names the TAGGED gap angles as its input and the re-search-or-surface-as-known-gap action; quick-ref lists `framework_audit.py backfill` with `{gap_angles, confirmed_labels}` → `{unlanded, ...}`; the documented command runs (`echo '{"gap_angles":[],"confirmed_labels":[]}' | python scripts/framework_audit.py backfill` exit 0).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "SKILL.md — a short step in the framework-audit subsection: after the pipeline runs, derive `confirmed_labels`, run `backfill`, and for each unlanded gap either re-search … OR surface it … as an explicitly-flagged known gap"

## Notes
- T2 depends on T1 (doc mirrors the shipped CLI). Depth 2.
- Faithful-copy: no task touches schemas/rank/prompts/dedup.py. After build, the finishing flow + CI MD5 gate confirm zero drift; sibling suites stay green.
- The check is intentionally decoupled from the claim schema (takes `confirmed_labels` as a given set) — out-of-scope note in the brief.
