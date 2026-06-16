# Plan: framework-audit library + consuming prompt → English-only

Source brief: docs/code-toolkit/specs/2026-06-13-framework-audit-library-english-only.md
Total tasks: 3
Critical-path depth: 2 (≤5)   — T1 (library = vocabulary SSOT) → T2/T3 (mirror its routing keys)
Execution order: sequential (T1 first, establishes routing vocabulary; then T2, T3)
Plan-document-reviewer verdict: PASS (2026-06-13; 13/14, advisory note only)

## Conventions
- Behavior-preserving language refactor: translate ZH→EN, change NO framework cells, NO logic, NO schema, NO provenance citations (except surface ZH labels).
- Run tests from `research-toolkit/skills/deep-deep-research/scripts/`: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q` (expect 69 passed throughout; clean `__pycache__` with `find -delete`, NOT `rm -rf`).
- Do NOT touch synced primitives (schemas/rank/prompts/dedup.py) or mode_route.py's §三-C provenance citations.

## Task 1 — Translate framework-audit-library.md to English (routing-vocabulary SSOT)
- Description: In `references/framework-audit-library.md`, translate all Chinese surface text to English while preserving every framework block's cells, the routing-table structure (rows + framework choices), provenance citations, dedup notes, and the 12 blind-spots' substance EXACTLY. Specifically: H1 (`完整性稽核框架庫` → English), routing-table header + the 題型 left-column keys (e.g. `投資 / 個股` → "Investment / single stock", `總經 / 產業` → "Macro / industry", `政策 / 法規` → "Policy / regulation", `任何題(萬用起手)` → "Any question (general start)", etc. — pick natural English, keep the dual-tag where it aids matching), the framework-name `(EN / 中譯)` glosses → English-only names, the `框架自身的集體盲點` header, and the 12 blind-spot ZH item-names (e.g. `時間衰減 / 論點時效` → "Time-decay / shelf-life"). This file becomes the SSOT for the English routing-key vocabulary T2/T3 must mirror.
- Module: references/framework-audit-library.md
- Files touched: research-toolkit/skills/deep-deep-research/references/framework-audit-library.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/references/framework-audit-library.md (current bilingual content)
- Acceptance:
  - RED: `grep -cP '[\x{4e00}-\x{9fff}]' references/framework-audit-library.md` returns a non-zero count (Chinese present).
  - GREEN: that grep returns `0` (no CJK remaining); framework-block COUNT unchanged (still ≥19 blocks); routing-table row count unchanged (32 rows); all 12 blind-spots still present (now English names); `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q` from scripts/ still `69 passed` (a .md change must not perturb collection).
- Dependencies: none
- Independent: true
- Brief item covered: "references/framework-audit-library.md — H1, routing-table 題型 column + header, framework-name 中譯 glosses, the 框架自身的集體盲點 header, and the 12 blind-spot ZH item-names ... SSOT for the English routing-key vocabulary"

## Task 2 — Translate framework_audit.py prompts/comments to English + clean test assertions
- Description: In `scripts/framework_audit.py`, translate the Chinese in `classify_prompt` (題型/路由表/個股/產業/法規/UX/安全/萬用起手/走查格子), `audit_prompt` (一格一格走查格子 / 框架自身的集體盲點), and the `DEFAULT_FRAMEWORKS`/`select` comments (萬用起手), using the **EXACT English routing-key names Task 1 established in the library** (read the translated library first to copy its row labels verbatim — the classify→audit→library walk depends on this matching). Change no logic, no schema, no `DEFAULT_FRAMEWORKS` value (already English). Then in `scripts/test_framework_audit.py`, simplify the three assertions (`:56`, `:82`, `:107`) to assert the English term only (drop the now-dead `or "路由表"`/`or "格子"` ZH branches).
- Module: scripts/framework_audit.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/framework_audit.py, research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/references/framework-audit-library.md (Task-1 output — copy the exact English routing-key names)
  - research-toolkit/skills/deep-deep-research/scripts/framework_audit.py
  - research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py
- Acceptance:
  - RED: updated `test_classify_prompt_contains_question_and_routes` (now asserting English-only "routing table") FAILS against the still-Chinese-containing prompt OR `grep -cP '[\x{4e00}-\x{9fff}]' scripts/framework_audit.py` is non-zero.
  - GREEN: `grep -cP '[\x{4e00}-\x{9fff}]' scripts/framework_audit.py` returns `0`; the test assertions reference the English term with no ZH OR-branch; `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q` = `69 passed`; the classify_prompt's routing keys match Task-1 library row labels (spot-check: a key named in classify_prompt exists as a routing-table row in the library).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "scripts/framework_audit.py — classify_prompt + audit_prompt bodies + the DEFAULT_FRAMEWORKS/select comments, using the exact same English routing keys ... scripts/test_framework_audit.py — the three assertions with dead Chinese OR-branches → assert the English term only"

## Task 3 — Translate the SKILL.md 萬用起手 reference
- Description: In `SKILL.md`, replace the one `萬用起手` reference (~line 175, "the general 萬用起手 route") with its English equivalent matching Task-1's library route label (e.g. "the general (any-question) route"). No other SKILL.md change.
- Module: SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md
  - research-toolkit/skills/deep-deep-research/references/framework-audit-library.md (Task-1 route label to match)
- Acceptance:
  - RED: `grep -cP '[\x{4e00}-\x{9fff}]' SKILL.md` returns non-zero (the 萬用起手 ref present).
  - GREEN: `grep -cP '[\x{4e00}-\x{9fff}]' SKILL.md` returns `0`; the replacement names the same general route the library uses; the documented `python scripts/framework_audit.py audit-prompt … --frameworks …` line still reads correctly.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "SKILL.md — the one 萬用起手 reference (line ~175) → English"

## Notes
- T1 is the routing-vocabulary SSOT; T2 and T3 both mirror its route labels → both depend on T1 (semantic dependency, not just file-disjointness). T2 and T3 touch different files (framework_audit.py+test vs SKILL.md) and could run in parallel after T1, but are small enough to run sequentially; the depth-2 critical path is T1→T2 (or T1→T3).
- mode_route.py / test_mode_route.py `§三-C 測試1` provenance citations are explicitly OUT of scope (cite a Chinese-titled source; translating loses fidelity).
- Faithful-copy: no task touches schemas/rank/prompts/dedup.py.
