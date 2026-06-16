# Plan: deep-deep-research levers ① framework-audit + ② meta-mode

Source brief: docs/code-toolkit/specs/2026-06-13-deep-deep-research-framework-audit-meta-mode.md
Total tasks: 10   (width is fine; uncapped)
Critical-path depth: 2 (≤5)   — longest semantic Dependencies chain (module group → its SKILL.md doc)
Execution order: parallel-where-possible (two file-disjoint module streams + one reference, then two doc tasks)
Plan-document-reviewer verdict: PASS (2026-06-13; 14/14, no gaps)

## Conventions (all tasks)

- Run all `python …` and `pytest` from `research-toolkit/skills/deep-deep-research/scripts/` (`pytest.ini` sets `pythonpath=.`).
- New modules are **stdlib-only, no network, no API keys** (mirror `scope_vs.py` / `vs_select.py`).
- **Never** edit the four synced SSOT primitives `schemas.py / rank.py / prompts.py / dedup.py` (CI MD5 gate). Importing `dedup.norm_url` read-only is allowed (`vs_select.py` already does).
- **Never** name a module after a stdlib module (`framework_audit.py` / `mode_route.py` are clear; no `select.py`).
- TDD iron law: each module task writes its RED test first, then GREEN implementation.
- Degradation contract (`SKILL.md:344-364`) must hold: opt-in passes never crash — no gaps → proceed with original angles; mode-classify fails → fall back to unmodified base synthesis prompt.

---

## Task 1 — framework_audit.py: gap-angle schema + `schema` CLI
- Description: Create `framework_audit.py` with `FRAMEWORK_AUDIT_SCHEMA` (gap-fill angles in the existing SCOPE_SCHEMA angle shape: `{question, gaps:[{label, query, rationale, framework, cell}]}`) and an argparse CLI `schema` subcommand printing it as JSON (exit 0; unknown/missing subcommand → stderr + exit 1, mirroring `scope_vs.py:107-145`).
- Module: framework_audit.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/framework_audit.py, research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/scope_vs.py (CLI + schema mold)
  - research-toolkit/skills/deep-deep-research/scripts/test_scope_vs.py (test mold)
- Acceptance:
  - RED: `test_schema_subcommand_emits_gap_schema` — `framework_audit.py schema` returns JSON whose `gaps[].items` require `label`, `query`, `framework`, `cell`.
  - GREEN: subcommand prints valid JSON, exit 0; bad subcommand exits 1 with stderr.
- Dependencies: none
- Independent: true
- Brief item covered: "Lever ① `framework_audit.py` — carries its own prompt text + schema … a gap-angle schema"

## Task 2 — framework_audit.py: `classify_prompt` + `classify-prompt` CLI
- Description: Add `classify_prompt(question)` returning a prompt that asks the agent to classify the question's **type** (mapping to the routing-table題型 keys, e.g. investment / policy / macro-industry / product-UX / general) so it can pick 2–3 audit frameworks; wire a `classify-prompt --question Q` CLI subcommand. Prompt instructs reading `references/framework-audit-library.md` routing table.
- Module: framework_audit.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/framework_audit.py, research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/scope_vs.py (prompt-builder mold)
- Acceptance:
  - RED: `test_classify_prompt_contains_question_and_routes` — prompt includes the question text AND instructs picking 2–3 frameworks via the routing table.
  - GREEN: `classify-prompt --question Q` prints the prompt, exit 0.
- Dependencies: none   (same file as T1 → SDD serializes; no semantic dep)
- Independent: false
- Brief item covered: "classify question-type → routing-table picks 2–3 audit frameworks"

## Task 3 — framework_audit.py: `audit_prompt` + `audit-prompt` CLI
- Description: Add `audit_prompt(question, angles, frameworks)` returning a prompt that walks each chosen framework's **cells** against the existing angle set and proposes gap-fill angles **only for uncovered cells** (conforming to `FRAMEWORK_AUDIT_SCHEMA`), explicitly tagging each gap with its `framework` + `cell`; instruct deduping against existing angles and flagging the 12 collective blind-spots. Wire `audit-prompt --angles A --question Q` CLI.
- Module: framework_audit.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/framework_audit.py, research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/scope_vs.py
- Acceptance:
  - RED: `test_audit_prompt_walks_cells_and_proposes_gaps` — prompt includes the angles, instructs per-cell walk, and asks for gap angles tagged with framework+cell.
  - GREEN: `audit-prompt --angles '<json>' --question Q` prints the prompt, exit 0.
- Dependencies: none   (same file as T1/T2)
- Independent: false
- Brief item covered: "walk each framework's cells against the existing angle set → propose gap-fill angles for uncovered cells"

## Task 4 — framework_audit.py: `select_gaps` deterministic selector + `select` stdin CLI
- Description: Add `select_gaps(gap_angles, existing_angles, fetch_slots)` — drop any gap whose case-folded label OR normalized query matches an existing angle (reuse `dedup.norm_url` read-only, as `vs_select.py:41`), cap survivors to `fetch_slots`, strip each to `{label, query, rationale}` (SCOPE_SCHEMA shape). Empty result is valid (→ caller proceeds with original angles). Wire a `select` subcommand reading `{gap_angles, existing_angles, fetch_slots}` from stdin → `{angles}` on stdout.
- Module: framework_audit.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/framework_audit.py, research-toolkit/skills/deep-deep-research/scripts/test_framework_audit.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/vs_select.py (dedup + strip + stdin/stdout mold)
  - research-toolkit/skills/deep-deep-research/scripts/dedup.py (norm_url; read-only import)
- Acceptance:
  - RED: `test_select_gaps_dedups_and_caps` — a gap duplicating an existing angle is dropped; with more gaps than `fetch_slots`, output length == `fetch_slots`; each output angle has exactly `{label, query, rationale?}`; empty gaps → `{angles: []}`.
  - GREEN: `echo '{...}' | python framework_audit.py select` prints `{angles:[...]}`, exit 0.
- Dependencies: none   (same file as T1-T3)
- Independent: false
- Brief item covered: "dedup + budget-cap to the top gaps within remaining MAX_FETCH → hand the augmented angle set (same shape) into unchanged Stage 2"

## Task 5 — references/framework-audit-library.md (bundled audit resource)
- Description: Create `references/framework-audit-library.md` distilled from the vault framework library: (a) the **routing table** (題型 → first-line + reinforcement frameworks) in full; (b) the **12 collective blind-spots** in full; (c) a **curated set of framework cells** — each routable first-line framework as `name → cells/dimensions → as-auditor one-liner → blind-spot`, covering at minimum the investment/policy/macro/general/risk routes the eval validated (PESTEL, Porter Five Forces, equity risk taxonomy, bull/bear, DuPont, MECE, 5W1H, SATs/ACH, Bardach, stakeholder, systems iceberg); (d) cross-framework dedup notes. Keep it token-bounded (target ≤ ~600 lines). **Generic frameworks only — no customer/private data** (red-line scrub).
- Module: references/framework-audit-library.md (content; no unit test — diagnostic acceptance)
- Files touched: research-toolkit/skills/deep-deep-research/references/framework-audit-library.md
- Context paths:
  - /Users/kouko/kouko-obsidian-vault/research/2026-06-13 分析框架庫 — 完整性稽核清單.md (source SSOT — routing table lines 1248-1283, dedup notes 1287-1310, blind-spots 1318-1329, cells throughout)
- Acceptance:
  - RED: `grep -q "路由表" references/framework-audit-library.md` fails (file absent).
  - GREEN: file present; `grep` confirms the routing table header, all 12 numbered blind-spots, and ≥10 framework cell-blocks; no private identifiers (a `grep` for real company names / personal names / "real customer" returns nothing).
- Dependencies: none
- Independent: true
- Brief item covered: "Consumes a bundled `references/framework-audit-library.md` (distilled from the vault library: routing table + framework cells + cross-framework dedup notes + the 12 collective blind-spots)"

## Task 6 — SKILL.md: Lever ① opt-in subsection (between Stage 1 and Stage 2)
- Description: Insert `### Opt-in: Framework completeness-audit` after the VS opt-in subsection (`SKILL.md:151`), before `## Stage 2`. Document the flow (classify → routing-table picks 2–3 frameworks via `references/framework-audit-library.md` → `audit-prompt` cell-walk → `select` dedup+budget-cap → feed augmented angles into unchanged Stage 2), mirroring the VS subsection's tone. State it is **opt-in / additive / zero default-path change** and that empty gaps → proceed with original angles. Add the four new `framework_audit.py` commands to the **Script-invocation quick reference** table.
- Module: SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md (VS opt-in subsection 83-149 as the mold; quick-ref table 367-385)
- Acceptance:
  - RED: `grep -q "Framework completeness-audit" SKILL.md` fails.
  - GREEN: subsection present between Stage 1 and Stage 2; quick-ref table lists `framework_audit.py schema/classify-prompt/audit-prompt/select` (command surface declared) and each documented command **actually runs** (`python framework_audit.py schema` etc. exit 0).
- Dependencies: Tasks 1, 2, 3, 4, 5 complete first  (doc mirrors the module CLI + the bundled reference)
- Independent: false
- Brief item covered: "new opt-in subsection between Stage 1 (Scope) and Stage 2 (Search)"

## Task 7 — mode_route.py: mode-verdict schema + `schema` CLI
- Description: Create `mode_route.py` with `MODE_VERDICT_SCHEMA` whose **only required field is `mode_binary` ∈ {settled, unsettled}** (the robust binary), plus an **optional low-confidence** `mode_label` ∈ {clear, complicated, complex, chaotic} and a `rationale`. Wire a `schema` CLI subcommand (mold: `scope_vs.py`). Docstring records provenance (Cynefin / Snowden HBR 2007; Hard-Soft) without jargon leaking into behavior.
- Module: mode_route.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/mode_route.py, research-toolkit/skills/deep-deep-research/scripts/test_mode_route.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/scope_vs.py (CLI + schema mold)
- Acceptance:
  - RED: `test_mode_schema_binary_required_label_optional` — schema requires `mode_binary` (enum settled/unsettled) and lists `mode_label` as optional (not in `required`).
  - GREEN: `mode_route.py schema` prints valid JSON, exit 0.
- Dependencies: none
- Independent: true
- Brief item covered: "a mode-verdict schema whose only robust field is `settled` vs `unsettled` … no hard switch on complicated↔complex"

## Task 8 — mode_route.py: `classify_prompt` (4-mode taxonomy, from evidence)
- Description: Add `classify_prompt(question, confirmed_block, killed_block)` carrying the **load-bearing 4-mode taxonomy verbatim** — explicit "context-dependent = complex", "loud-opinion ≠ contested" — and the three hard rules: (1) classify **from the evidence / stance spread**, not question-text framing; (2) **fail-safe to `unsettled`/complex** when unsure; (3) treat the clear/complicated/complex label as a low-confidence soft signal, only settled-vs-unsettled is binding. Wire `classify-prompt --confirmed-block CB --killed-block KB --question Q` CLI.
- Module: mode_route.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/mode_route.py, research-toolkit/skills/deep-deep-research/scripts/test_mode_route.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/scope_vs.py
  - /Users/kouko/kouko-obsidian-vault/projects/2026-06-12 deep-deep-research VS 角度選擇器 eval（多語覆蓋與成本模型）.md (§三-C hard rules — design SSOT)
- Acceptance:
  - RED: `test_classify_prompt_has_taxonomy_and_hardrules` — prompt contains the evidence blocks, the "context-dependent"/"loud opinion" taxonomy markers, the classify-from-evidence instruction, and the fail-safe-to-complex rule.
  - GREEN: `classify-prompt --confirmed-block CB --killed-block KB --question Q` prints the prompt, exit 0.
- Dependencies: none   (same file as T7)
- Independent: false
- Brief item covered: "carries the load-bearing 4-mode taxonomy prompt verbatim … Classifies from evidence, fail-safe to complex when unsure"

## Task 9 — mode_route.py: `stance_block` + `stance` stdin CLI
- Description: Add `stance_block(mode_binary, mode_label=None)` returning the synthesis-**stance directive string** to prepend to the base synthesis prompt: `settled` → "give the consensus answer clearly, don't over-hedge"; `unsettled` → "do NOT force a verdict; map competing positions, calibrate confidence DOWN, surface the debate"; `chaotic` (via mode_label) → "flag volatility/recency". Unknown/missing → safe `unsettled` default (fail-safe). Wire a `stance` subcommand reading `{mode_binary, mode_label?}` from stdin → `{stance_block}` on stdout.
- Module: mode_route.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/mode_route.py, research-toolkit/skills/deep-deep-research/scripts/test_mode_route.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/vs_select.py (stdin/stdout mold)
- Acceptance:
  - RED: `test_stance_block_maps_modes` — `settled` block says give consensus clearly; `unsettled` block says map positions + calibrate down + don't force verdict; unknown mode falls back to the unsettled block.
  - GREEN: `echo '{"mode_binary":"unsettled"}' | python mode_route.py stance` prints `{stance_block: "..."}`, exit 0.
- Dependencies: none   (same file as T7/T8)
- Independent: false
- Brief item covered: "a stdin→stdout step that emits the synthesis-stance directive block to prepend to the base synthesis prompt"

## Task 10 — SKILL.md: Lever ② opt-in subsection (inside Stage 6)
- Description: Add `### Opt-in: Meta-mode synthesis-stance routing` inside Stage 6 (around `SKILL.md:310`). Document: after verify, run `mode_route.py classify-prompt` over the confirmed/killed blocks → emit a mode verdict → `mode_route.py stance` → **prepend** the returned `stance_block` to the base synthesis prompt from `prompts.py synthesis` (the synced prompt stays byte-identical). State: opt-in / additive; classify-failure → fall back to the unmodified base synthesis prompt (degradation contract). Add the `mode_route.py` commands to the Script-invocation quick reference.
- Module: SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md (Stage 6 296-342; quick-ref 367-385)
- Acceptance:
  - RED: `grep -q "Meta-mode synthesis-stance" SKILL.md` fails.
  - GREEN: subsection present inside Stage 6, explicitly says it **prepends** the stance block and does NOT edit `prompts.py`; quick-ref lists `mode_route.py schema/classify-prompt/stance` (command surface declared) and each runs (exit 0).
- Dependencies: Tasks 7, 8, 9 complete first  (doc mirrors the module CLI)
- Independent: false
- Brief item covered: "new opt-in branch inside Stage 6 (Synthesize), synthesis-stage only … prepend it to the base synthesis prompt"

---

## Notes

- **Two parallel module streams.** `framework_audit.py` (T1-T4) and `mode_route.py` (T7-T9) each share a file → SDD serializes **within** each group (Independent: false, no parallel dispatch on the same file). The two groups plus the reference (T5) are file-disjoint, so the opening wave **T1 / T5 / T7** is parallel-dispatch-safe (Independent: true). Same-file successors carry `Dependencies: none` (no semantic dependency) so critical-path **depth stays 2** — they serialize via SDD's one-implementer-at-a-time floor, not via Dependencies edges (per the depth-not-count discipline: file-serialization ≠ a semantic chain).
- **Doc tasks (T6, T10)** both edit SKILL.md → serialize (Independent: false); each depends on its module group + (T6) the reference.
- **Faithful-copy guard.** No task edits `schemas.py / rank.py / prompts.py / dedup.py`. After the build, the finishing flow + CI `check-script-sync.yml` MD5 gate confirm zero drift; sibling suites (fact-check 28 / cite-check 41 / deep-read 26) must stay green.
- **Lever ② has no separate reference file** (scope reduction from the brief's "two reference files"): the 4-mode taxonomy is load-bearing and lives verbatim in `mode_route.py`'s `classify_prompt`; provenance rides in the module docstring + SKILL.md subsection.
