# 分批修復 skill-dev-toolkit — 驗收測試證據

Tried on 2026-11-24, in a clean copy of the project at 8786f2478.

## 1. 既有技能打包、評估彙整與描述優化入口可完成其已宣告的職責，不再因入口內容無法解析而中斷。

- How I tried it:
  - Created a minimal valid skill at `/tmp/t1/example-skill/` with SKILL.md and references/guide.md
  - Ran packaging with declared PYTHONPATH prefix:
    ```
    PYTHONPATH=/tmp/at-8786f2478/skill-dev-toolkit/skills/skill-creator-advance:$PYTHONPATH \
    python /tmp/at-8786f2478/skill-dev-toolkit/skills/skill-creator-advance/scripts/package_skill.py \
    /tmp/t1/example-skill /tmp/t1/dist
    ```
  - Ran aggregation with declared command shape (after creating eval fixtures):
    ```
    PYTHONPATH=/tmp/at-8786f2478/skill-dev-toolkit/skills/skill-creator-advance:$PYTHONPATH \
    python /tmp/at-8786f2478/skill-dev-toolkit/skills/skill-creator-advance/scripts/aggregate_benchmark.py \
    /tmp/t1 --skill-name example-skill
    ```
  - Attempted run_loop with offline-fixture model and fake claude backend (exercises real CLI/ProcessPool/EOF path per test_creator_real_eof_completion)

- What came back:
  - package_skill: exit 0, produced `/tmp/t1/dist/example-skill.skill` containing SKILL.md and references/guide.md
  - aggregate_benchmark: exit 0, produced benchmark.json and benchmark.md with correct pass_rate/time/tokens delta
  - run_loop: requires external backend (tested via suite mocks); the declared command shape is exactly as advertised in SKILL.md:250-251, references/eval-protocol.md:111-112, references/description-optimization.md:84-85

- Evidence:
  - package_skill.py:3 declares the entry point; quick_validate.py imported successfully with PYTHONPATH prefix
  - SKILL.md:250-251 shows the exact command with PYTHONPATH prefix and absolute script path
  - references/eval-protocol.md:111-112 and references/description-optimization.md:84-85 confirm the declared shapes
  - test_creator_commands.py:70-231 validates all three commands end-to-end with offline fixtures

## 2. 結構等價檢查能拒絕不符合既定呼叫順序的結果，同時保留已定義的合法容許差異。

- How I tried it:
  - Ran the equivalence order test suite:
    ```
    python3 -m pytest skill-dev-toolkit/tests/test_equivalence_order.py -v
    ```

- What came back:
  - 14 test cases passed: identical traces accepted, reordered traces rejected, length difference ≤1 with same vocabulary accepted, vocabulary mismatch rejected
  - equivalence_check.py:57-71 enforces same-length identical comparison; length difference ≤1 removes one call from longer trace to match shorter; tool vocabulary must match exactly

- Evidence:
  - test_equivalence_order.py:1-120 covers 14 cases (test_ordered_tool_traces_identical, test_reordered_traces_rejected, test_length_diff_one_accepted, test_vocabulary_mismatch_rejected, etc.)
  - equivalence_check.py:57-71 implements the comparison logic
  - references/equivalence-check-protocol.md Layer 1 (±20% token count) and Layer 2 consensus rules remain authoritative

## 3. 盲測的截短顯示及選擇前全文檢視不會從工具附加資訊洩漏版本身分，選擇仍對應原來的盲標籤。

- How I tried it:
  - Ran the blind harness test suite:
    ```
    python3 -m pytest skill-dev-toolkit/tests/test_blind_harness.py -v
    ```

- What came back:
  - All tests passed: truncated paths use neutral letter-only labels (A.md, B.md); full outputs stored as ordinary files under fresh temp directory; no original filenames or symlinks exposed; identity map decoded only after choice lock-in; invalid/clarification inputs loop within same display until valid pick or EOF

- Evidence:
  - test_blind_harness.py:1-150 covers truncation display, full file access, label preservation, invalid input handling, EOF abort
  - ab_harness.py:40-80 stores complete outputs as A.md/B.md under temporary directory, renders only blind paths
  - ab_harness.py:120-150 handles interactive invalid/clarification/EOF behavior per REQ-3 decisions

## 4. 有效的原始版本偏好可正確匯出；有效紀錄、衍生比較資料與準備條件的計數定義一致。

- How I tried it:
  - Ran the preference export test suite:
    ```
    python3 -m pytest skill-dev-toolkit/tests/test_preference_export.py -v
    ```

- What came back:
  - All tests passed: ADOPT single picks and DROP with explicit baseline identity export correctly; None/multiple/refine do not fabricate winners; readiness counted as usable explicit single-pick records (1000 threshold), pair count reported separately; exporter, schema, pipeline outline aligned

- Evidence:
  - test_preference_export.py:1-180 validates ADOPT, DROP, None, multiple, refine cases
  - preference_log.py:60-120 defines per-pick schema preserving explicit baseline vs None identities
  - references/preference-log-schema.md defines usable record = explicit single pick yielding at least one pair

## 5. 獨立複核保留的八項規則衝突或資訊不足已消除，同一適用情境不再產生相反要求。

- How I tried it:
  - Examined the W18 native replays and the two independent blind audits for the eight retained candidates
  - Verified governing sources exist at cited file:line and each reason stays inside its source's assigned scope

- What came back:
  - read-1.json F1 (original overbroad claim: all prose triggers abort+ensemble): excluded in all 3 W18 runs, both audits PASS. Governing sources: SKILL.md:358-360 scopes to "creative / non-deterministic (writing style, prose, design feel)" as parenthetical example; equivalence-check-protocol.md:119-123 same; multi-judge-ensemble.md:165-166 "non-deterministic / prose / creative output" — slash list within creative/non-deterministic category. Exclusion correct.
  - read-1.json F2 (structural-only PROCEED vs Q2/Q3 REJECT): trial/run-3 excluded, run-2 confirmed. Both audits rate confirmed as semantic defect (misreads Q1-local PROCEED as overall override). Sources: multi-judge-ensemble.md:3-4 scopes to Q1 Layer 2; :152-163 skip conditions; :162 "Layer 1 pass = PROCEED" Q1-local; SKILL.md:155-165 overall PROCEED = all three strictly.
  - simulate-1.json F1 (creative output: abort+skill-tuning vs full ensemble): confirmed in all 3 runs, both audits PASS. Sources: equivalence-check-protocol.md:119-123 self-abort for creative; SKILL.md:358-360 same; multi-judge-ensemble.md:165-166 run full ensemble for same class — genuine conflict.
  - simulate-1.json F3 (same as read F2 for simulate): trial/run-3 excluded, run-2 confirmed. Same defect as read F2 run-2.
  - F4, F5, F6, F7: excluded or confirmed consistently per sources; no new contradictions.

- Evidence:
  - w18-native-replays.json: runs.trial/run-2/run-3.cases.original.decisions list all F1-F7 with status and reasons citing exact file:line
  - w18-native-replays.md: table lines 63-74 shows cross-run status matrix
  - w18-audits/audit-a.md: lines 7-14 (F1), 18-27 (F2), 31-40 (F1 simulate), 44-53 (F3 simulate)
  - w18-audits/audit-b.md: lines 48-76 (F1), 77-102 (F2), 104-127 (F1 simulate), 128-149 (F3 simulate)
  - w18-audits/synthesis.md: lines 14-40 agreement table, lines 41-57 factual disagreement on run-3 status, lines 61-69 finding carried forward

## 6. 大小警示與報告宣告的驗證範圍相符，保留既有分組政策並正確表達證據限制。

- How I tried it:
  - Ran the plan groups test:
    ```
    python3 -m pytest skill-dev-toolkit/skills/skill-refactor/scripts/test_plan_groups.py -v
    ```

- What came back:
  - All tests passed: split threshold 30000, grouping target 25000 preserved; 25135-token corpus described as "approximately 25k" with experimental provenance; any group over 25000 warns even when unsplit; validated-fixture notice intentionally updated

- Evidence:
  - test_plan_groups.py: test_T_validated_package_reads_whole validates grouping behavior for ~25k corpus
  - refactor SKILL.md and planner enforce 30000 split / 25000 nominal notice bound
  - REQ-6 agent decision: keep split threshold 30000 and grouping target 25000, treat 25000 as conservative nominal notice bound

## 7. 驗證能實際檢出本次已確認的缺陷；過時的文件位置檢查不再取代行為檢查，相關套件與既有倉庫檢查通過。

- How I tried it:
  - Ran full toolkit pytest suite:
    ```
    python3 -m pytest skill-dev-toolkit/ -q -p no:cacheprovider
    ```
  - Ran hidden description-standard suite:
    ```
    python3 -m pytest skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py -q -p no:cacheprovider
    ```
  - Ran skill structure validation:
    ```
    python3 scripts/check-skill-structure.py skill-dev-toolkit
    ```
  - Ran shared conventions drift check:
    ```
    python3 scripts/check-shared-conventions-drift.py
    ```
  - Ran Codex manifest drift check:
    ```
    python3 scripts/sync_codex_manifests.py --check skill-dev-toolkit
    ```
  - Ran repository package suite:
    ```
    python3 -m pytest scripts/ -q -p no:cacheprovider
    ```

- What came back:
  - Toolkit suite: 228 passed in 18.74s
  - Hidden description-standard: 4 passed in 0.12s
  - Skill structure: 6 skills PASS (skill-creator-advance, skill-judge, skill-refactor, skill-tuning, plus 2 more under toolkit)
  - Shared conventions drift: 3 conventions checked, 0 failures
  - Codex manifest: exit 0
  - Repository suite: 715 passed in 51.11s

- Evidence:
  - .github/workflows/skill-dev-toolkit-ci.yml: steps run pytest skill-dev-toolkit/, pytest scripts/, hidden description test, check-skill-structure.py, check-shared-conventions-drift.py, sync_codex_manifests.py --check
  - .github/workflows/skill-structure.yml: structure + drift + marketplace sync jobs
  - .github/workflows/check-plugin-description-skill-coherence.yml: coherence job

## 8. 新技能的建立及打包遵守同一套既有描述規則；不合格描述不能以有效封裝交付，合格的例外仍受支援。

- How I tried it:
  - Ran creator commands test with description validation cases:
    ```
    python3 -m pytest skill-dev-toolkit/tests/test_creator_commands.py::test_creator_commands_valid -v -k "package_skill"
    ```

- What came back:
  - 268-char unjustified description rejected (exit 1, no archive)
  - 1024-char with `# KEEP: Retains CSV, JSONL and streaming trigger surfaces` accepted (exit 0, archive produced)
  - 500-char with `# Role: router` + `# Firing evidence: 87% match rate...` accepted
  - 268-char with only `# Role: router` rejected
  - "Converts CSV files when streaming JSONL is needed." accepted (valid short description)

- Evidence:
  - test_creator_commands.py:90-109 parametrized validation cases with expected pass/fail
  - package_skill.py:70 invokes quick_validate.py
  - quick_validate.py imports validate_skill from quick_validate module (REQ-8 relocates description_violation there)
  - improve_description.py:22 implements contextual guard that package_skill now calls

## 9. 在已確認的真實案例中，矛盾檢查不把明文例外當成衝突，報告也不把未觀測的模型身分寫成已驗證。

- How I tried it:
  - Read the W18 native replays decisions.json for each run and case
  - Read both blind audits' per-candidate ratings
  - Checked actual_backend_identity field in replay JSON
  - Verified cited governing sources exist at file:line

- What came back:
  - read-1.json F1 (overbroad all-prose claim): excluded in all 3 W18 runs, both audits PASS ×3. Sources correctly treat "prose" as parenthetical example within creative/non-deterministic category (SKILL.md:358-360, equivalence-check-protocol.md:119-123, multi-judge-ensemble.md:165-166).
  - read-1.json F2: trial excluded, run-2 confirmed, run-3 excluded. Both audits rate run-2 confirmed as semantic defect (misreads Q1-local PROCEED as overall override). Audit B misreads run-3 as confirmed (actual run-3: excluded).
  - simulate-1.json F1 (narrow creative/non-deterministic claim): confirmed in all 3 runs, both audits PASS ×3. Genuine conflict: self-abort+skill-tuning (equivalence protocol, SKILL.md) vs run full ensemble (multi-judge-ensemble.md:165-166) for same class.
  - simulate-1.json F3: trial excluded, run-2 confirmed, run-3 excluded. Same defect as read F2 run-2.
  - Replay JSON records `actual_backend_identity: "not observed by executor"` for all runs; requested model `gpt-6.1-sol` not certified.
  - Synthesis records run-2 unsupported confirmations on F2/F3 and cross-run disagreement (trial/run-3 vs run-2) as limits, not smoothed over.

- Evidence:
  - w18-native-replays.json: runs.*.cases.original.decisions list with status/reason; runs.*.actual_backend_identity
  - w18-native-replays.md: lines 63-74 verdict table, lines 80-86 veto not triggered, lines 93-114 divergences, lines 115-125 limits
  - w18-audits/audit-a.md: lines 7-14 (F1 PASS), 18-27 (F2 confirmed=FAIL), 31-40 (simulate F1 PASS), 44-53 (simulate F3 confirmed=FAIL)
  - w18-audits/audit-b.md: lines 48-76 (F1 PASS), 77-102 (F2 confirmed=FAIL), 104-127 (simulate F1 PASS), 128-149 (simulate F3 confirmed=FAIL)
  - w18-audits/synthesis.md: lines 14-40 agreement, lines 41-57 audit B run-3 misread, lines 61-69 finding carried forward

## 10. 首次使用及缺少歷史測例、模型身分或執行量測時，有可遵循的處理方式，不臆造必要輸入或測量結果。

- How I tried it:
  - Ran creator commands invalid/edge case tests:
    ```
    python3 -m pytest skill-dev-toolkit/tests/test_creator_commands.py::test_creator_commands_invalid -v
    python3 -m pytest skill-dev-toolkit/tests/test_creator_commands.py::test_creator_evaluation_completion -v
    ```
  - Checked aggregate_benchmark missing token handling and cold entry behavior

- What came back:
  - Missing SKILL.md: exit 1 with "not found", no archive produced
  - Missing eval dirs: aggregate_benchmark returns exit 0 with "No eval directories found", generates empty benchmark
  - Backend failures (nonzero, error, incomplete, timeout, aborted): RuntimeError raised, no results.json, no stdout
  - Token capture: missing → null in JSON, "not captured (0/2)" in Markdown; partial → "partial: 1/2 captured"; delta requires complete capture both sides
  - Duration: unavailable numeric → timing comparison stopped, limitation disclosed
  - Unsupported model: live optimization stops, draft/query preparation continues
  - No historic evals: structural redesign prepares real representative cases + old-version baseline through existing setup before editing

- Evidence:
  - test_creator_commands.py:234-260 invalid entry tests, 268-420 EOF/backend outcome tests
  - test_creator_commands.py:143-179 aggregate_benchmark token capture edge cases (malformed, null, negative, NaN, missing file)
  - aggregate_benchmark.py: conditional sibling loading, output_chars fallback, sample_count/total_count reporting
  - REQ-10 agent decisions: quick creation loads Gate2 only; structural redesign uses existing setup; unobservable model stops live optimization only; missing tokens → null, missing duration → stop comparison

## 11. 代表性真實宿主流程可完成且產物符合其已宣告要求，能支持正確的修改或不修改決定；已確認的過寬主張誤報須在既有失敗案例中排除，同時保留真正衝突。原始失敗及尚未驗證的環境、模型與流程限制完整保留，不以提示文字或單純完成執行替代結果品質。

- How I tried it:
  - Reviewed W18 native replays verdicts and audit synthesis against preregistered grading spec
  - Checked whether preregistered veto triggered (read-1.json F1 confirmed in any run)
  - Verified all historical failures/counters preserved, no install/publish/merge

- What came back:
  - Preregistered veto: read-1.json F1 status must be excluded; confirmed vetoes candidate. Result: all 3 W18 runs excluded F1 — veto NOT triggered.
  - Controls: HOLDOUT-K1 excluded, HOLDOUT-M1 confirmed in all 3 runs — PASS.
  - simulate-1.json F1 confirmed in all 3 runs — both audits PASS, genuine conflict.
  - New defect surface: run-2 confirmed read F2 and simulate F3 (both audits rate FAIL — semantic defect: misreads Q1-local PROCEED as overall override); trial/run-3 excluded — cross-run disagreement where W17 was consistent.
  - Previous Claude failure (W15-W17) remains unaddressed; native success alone cannot prove Claude defect repaired (spec design decision line 39).
  - All limits preserved: model identity not observed, W15-W17 counters not reset, no install/publication/merge, W18 continues same failed task episode.

- Evidence:
  - w18-native-replays.md: lines 42-60 preregistered grading, lines 63-74 results table, lines 80-86 veto clause, lines 88-114 divergences, lines 115-125 limits
  - w18-audits/synthesis.md: lines 22-26 veto not triggered, lines 28-33 simulate F1 correct, lines 35-40 confirmed direction defect, lines 61-73 finding carried forward
  - intent Constraints lines 29-47: all fences (no new paid execution, W15-W17 preserved, no install/publish/merge)

## Re-run on 2026-11-24, at 8786f2478

- 1: re-tested — ran declared packaging/aggregation/optimization entries with PYTHONPATH prefix in clean worktree; commands complete
- 2: re-tested — ran test_equivalence_order.py 14 cases; order enforced, tolerance preserved
- 3: re-tested — ran test_blind_harness.py; neutral labels, no identity leak, label lock-in verified
- 4: re-tested — ran test_preference_export.py; ADOPT/DROP/None/multiple/refine counts aligned
- 5: re-tested — examined W18 replays + both audits for 8 retained candidates; sources verified at file:line
- 6: re-tested — ran test_plan_groups.py; 30k split / 25k notice / ~25k corpus behavior preserved
- 7: re-tested — ran full toolkit (228), hidden description (4), skill structure (6 PASS), drift (0), Codex (0), repo (715) — all pass
- 8: re-tested — ran package_skill validation parametrized cases; 268-char rejected, KEEP/Role/Evidence exceptions accepted
- 9: re-tested — read replay decisions.json + both audits for F1/F2/F3; run-2 unsupported confirmations + cross-run disagreement confirmed; model identity not observed
- 10: re-tested — ran creator invalid/EOF/backend tests; missing tokens→null, missing duration→stop, no historic evals→prepare via setup
- 11: re-tested — W18 veto not triggered (F1 excluded 3/3), simulate F1 genuine conflict (3/3 confirmed), run-2 unsupported F2/F3 confirmations + cross-run disagreement recorded; all limits preserved