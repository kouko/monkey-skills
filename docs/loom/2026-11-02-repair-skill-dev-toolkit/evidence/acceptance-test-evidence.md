Tried on 2026-11-24, in a clean copy of the project at c8d6de0ad7357a50da276d7b92b7fc3a7deb7a.

# 分批修復 skill-dev-toolkit — 驗收測試證據

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): fix 2a6f311cd only moved 9 research .py programs (scope-diagnostic, w18-native-replay) byte-for-byte out of the change store into docs/loom/evidence/research/ and updated one markdown link; no skill code, test, or entry-point content changed. This row is unaffected.

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): equivalence_check.py and its tests are unchanged by the fix; only research .py moved.

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): ab_harness.py and its tests are unchanged by the fix.

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): preference_log.py and its tests are unchanged by the fix.

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): the W18 verdict JSON, replay markdown, and both audits live under evidence/ (untouched by the fix). Only the research .py programs moved out of research/. Evidence chain re-verified intact for row 9/11 re-test (see below); this row's reconciliation conclusion is unchanged.

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): planner code and tests unchanged by the fix.

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): the CI definitions, check scripts, and suite code are all unchanged by the fix (which touched only docs/loom/). The two mechanical suite commands re-ran at the new HEAD and passed — see the re-run section below.

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): description validation code and tests are unchanged by the fix.

## 9. 在已確認的真實案例中，矛盾檢查不把明文例外當成衝突，報告也不把未觀測的模型身分寫成已驗證。

- How I tried it:
  - Read the W18 native replays decisions.json for each run and case
  - Read both blind audits' per-candidate ratings
  - Checked actual_backend_identity field in replay JSON
  - Verified cited governing sources exist at file:line
  - Re-verified the full evidence chain at the new HEAD after the fix (research .py programs moved out of research/; verdict JSON, replay markdown, and audits remain under evidence/ untouched)

- What came back:
  - read-1.json F1 (overbroad all-prose claim): excluded in all 3 W18 runs, both audits PASS ×3. Sources correctly treat "prose" as parenthetical example within creative/non-deterministic category (SKILL.md:358-360, equivalence-check-protocol.md:119-123, multi-judge-ensemble.md:165-166).
  - read-1.json F2: trial excluded, run-2 confirmed, run-3 excluded. Both audits rate run-2 confirmed as semantic defect (misreads Q1-local PROCEED as overall override). Audit B misreads run-3 as confirmed (actual run-3: excluded).
  - simulate-1.json F1 (narrow creative/non-deterministic claim): confirmed in all 3 runs, both audits PASS ×3. Genuine conflict: self-abort+skill-tuning (equivalence protocol, SKILL.md) vs run full ensemble (multi-judge-ensemble.md:165-166) for same class.
  - simulate-1.json F3: trial excluded, run-2 confirmed, run-3 excluded. Same defect as read F2 run-2.
  - Replay JSON records `actual_backend_identity: "not exposed in exec JSONL"` for all runs; requested model `gpt-6.1-sol` not certified.
  - Synthesis records run-2 unsupported confirmations on F2/F3 and cross-run disagreement (trial/run-3 vs run-2) as limits, not smoothed over.

- Evidence:
  - w18-native-replays.json: runs.*.cases.original.decisions list with status/reason; runs.*.actual_backend_identity
  - w18-native-replays.md: lines 63-74 verdict table, lines 80-86 veto not triggered, lines 93-114 divergences, lines 115-125 limits
  - w18-audits/audit-a.md: lines 7-14 (F1 PASS), 18-27 (F2 confirmed=FAIL), 31-40 (simulate F1 PASS), 44-53 (simulate F3 confirmed=FAIL)
  - w18-audits/audit-b.md: lines 48-76 (F1 PASS), 77-102 (F2 confirmed=FAIL), 104-127 (simulate F1 PASS), 128-149 (simulate F3 confirmed=FAIL)
  - w18-audits/synthesis.md: lines 14-40 agreement, lines 41-57 audit B run-3 misread, lines 61-69 finding carried forward

- Re-test at 2026-11-24, HEAD 2a6f311cd (full re-verification, not carried over):
  - The fix diff `git show 2a6f311cd` is 9 renames (similarity index 100%) of research .py programs plus 1 markdown link update; no evidence/ content touched.
  - Confirmed at new worktree: `docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/w18-native-replays.json` present; all 3 runs (trial, run-2, run-3) complete=True; each run has 9 decisions; decisions identical to prior walk (trial: read F1 excl / read F2 excl / sim F1 conf / sim F3 excl; run-2: read F1 excl / read F2 conf / sim F1 conf / sim F3 conf; run-3: read F1 excl / read F2 excl / sim F1 conf / sim F3 excl).
  - `actual_backend_identity` = "not exposed in exec JSONL" for all 3 runs (unchanged).
  - `w18-native-replays.md` (124 lines) and `w18-audits/{audit-a,audit-b,synthesis}.md` present under evidence/ and intact.
  - Verdict unchanged: partly. The evidence chain still reads correctly after the move; run-2 unsupported confirmations and cross-run disagreement stand.

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

- Carried-over note (2026-11-24 re-run, HEAD 2a6f311cd): cold-entry logic and tests are unchanged by the fix.

## 11. 代表性真實宿主流程可完成且產物符合其已宣告要求，能支持正確的修改或不修改決定；已確認的過寬主張誤報須在既有失敗案例中排除，同時保留真正衝突。原始失敗及尚未驗證的環境、模型與流程限制完整保留，不以提示文字或單純完成執行替代結果品質。

- How I tried it:
  - Reviewed W18 native replays verdicts and audit synthesis against preregistered grading spec
  - Checked whether preregistered veto triggered (read-1.json F1 confirmed in any run)
  - Verified all historical failures/counters preserved, no install/publish/merge
  - Re-verified the full evidence chain at the new HEAD after the fix (research .py programs moved out of research/; verdict JSON, replay markdown, and audits remain under evidence/ untouched)

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

- Re-test at 2026-11-24, HEAD 2a6f311cd (full re-verification, not carried over):
  - Confirmed preregistered veto still recorded as NOT triggered: all 3 runs (trial/run-2/run-3) excluded read-1.json F1.
  - Confirmed controls: HOLDOUT-K1 excluded, HOLDOUT-M1 confirmed in all 3 runs.
  - Confirmed simulate-1.json F1 confirmed in all 3 runs — genuine conflict preserved.
  - Confirmed run-2 still confirms read-1.json F2 and simulate-1.json F3; trial/run-3 exclude them — cross-run disagreement preserved.
  - Confirmed `actual_backend_identity: not exposed in exec JSONL` for all 3 runs — model identity not certified.
  - Confirmed w18-native-replays.md (124 lines) and w18-audits/synthesis.md (83 lines) intact under evidence/; only research .py moved out of research/.
  - Verdict unchanged: partly. Full host usability remains unverified; native success alone does not prove Claude defect repaired; all limits preserved.

## Re-run on 2026-11-24, at 2a6f311cd8a0d8afb807d939572c01322e41f9e4

This re-run follows fix commit 2a6f311cd8a0d8afb807d939572c01322e41f9e4 ("docs(loom): relocate research programs out of the change store"), fix range 8786f2478..2a6f311cd.

### What the fix did

- Moved 9 research .py programs byte-for-byte (git rename, 100% similarity) out of `docs/loom/2026-11-02-repair-skill-dev-toolkit/research/` into `docs/loom/evidence/research/2026-11-02-repair-skill-dev-toolkit/`:
  - scope-diagnostic-20261109/{prepare.py, run.py, run-startup-recovery.py, corrected/prepare.py, corrected/run.py} (5 files)
  - w18-native-replay/{grade_one.py, make_archive.py, rebuild_inputs.py, run_one.py} (4 files)
- Updated exactly one markdown link in `docs/loom/2026-11-02-repair-skill-dev-toolkit/research/03-scope-diagnostic-results.md:73` to point at the corrected runner at its new location.
- No functional code, skill content, test, or evidence content changed. No files under `docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/` were touched.

### What this re-run checked

- Byte-identity of the moves: `git show 2a6f311cd` reports "similarity index 100%" for all 9 renames (no content lines added or removed; the 1 insertion / 1 deletion is the single markdown link).
- The one updated link resolves: at the new worktree, `docs/loom/2026-11-02-repair-skill-dev-toolkit/research/03-scope-diagnostic-results.md:73` now points at `../../evidence/research/2026-11-02-repair-skill-dev-toolkit/scope-diagnostic-20261109/corrected/run.py`, and that file exists at the new location (confirmed via `ls` of `docs/loom/evidence/research/2026-11-02-repair-skill-dev-toolkit/scope-diagnostic-20261109/corrected/`).
- Evidence chain intact: all W18 verdict JSONs, replay markdown, and audit files remain under `docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/` (untouched). Confirmed `w18-native-replays.json` parses with 3 complete runs (trial/run-2/run-3), each with 9 decisions; decisions and `actual_backend_identity` values identical to the prior walk. Confirmed `w18-native-replays.md` (124 lines) and `w18-audits/{audit-a,audit-b,synthesis}.md` present and intact.
- The 2 mechanical suite commands re-ran at the new HEAD in the clean worktree:
  - `python3 -m pytest skill-dev-toolkit/ -q -p no:cacheprovider` → 228 passed in 18.67s
  - `python3 -m pytest scripts/ -q -p no:cacheprovider` → 715 passed in 50.59s

### Per-row re-run disposition

- 1: carried over — fix only moved research .py tooling, no skill code/test change
- 2: carried over — fix only moved research .py tooling, no equivalence logic change
- 3: carried over — fix only moved research .py tooling, no blind harness change
- 4: carried over — fix only moved research .py tooling, no preference export change
- 5: carried over — fix only moved research .py tooling, no rule reconciliation change (W18 verdict chain re-verified intact via row 9 re-test)
- 6: carried over — fix only moved research .py tooling, no planner change
- 7: carried over — fix only moved research .py tooling; suite re-ran at new HEAD and passed
- 8: carried over — fix only moved research .py tooling, no description validation change
- 9: carried over — full re-test completed at prior re-run (HEAD 2a6f311cd); this fix edits only the intent pin line, no Acceptance wording, W18 evidence, code, or test changed
- 10: carried over — fix only moved research .py tooling, no cold-entry logic change
- 11: carried over — full re-test completed at prior re-run (HEAD 2a6f311cd); this fix edits only the intent pin line, no Acceptance wording, W18 evidence, code, or test changed

## Re-run on 2026-11-24, at c8d6de0ad7357a50da276d7b92b7fc3a7deb7a

This second re-run follows fix commit c8d6de0ad7357a50da276d7b92b7fc3a7deb7a ("docs(loom): intent 2026-11-02-repair-skill-dev-toolkit confirmed"), fix range 2a6f311cd..c8d6de0ad.

### What the fix did

- Edited exactly one frontmatter line in `docs/loom/intent/2026-11-02-repair-skill-dev-toolkit.md`: `intent_confirmed_sha` corrected from `e8d997a242c58bf638b94a128a076c815b9864ce` to `a8926f6b0a04d91274fccbb029ca9d36250d0cfd`.
- No Acceptance wording, no requirement, no product code, no skill content, no test, no evidence changed.
- Verified the pin is now self-consistent: recomputing the intent content identity (`grep -v -e '^status:' -e '^intent_confirmed_sha:' <intent> | git hash-object --stdin`) yields `a8926f6b0a04d91274fccbb029ca9d36250d0cfd`, matching the declared value.

### What this re-run checked

- Diffed `2a6f311cd..c8d6de0ad`: only the single pin-line change in the intent file; all three loom-files (report, evidence, intent) appear in the diff because report/evidence were updated as part of this same re-anchoring deliverable, not because acceptance reasoning changed.
- Confirmed the Acceptance section of the intent is byte-identical between 2a6f311cd and c8d6de0ad.
- Evidence chain intact: all W18 verdict JSONs, replay markdown, and audit files remain under `docs/loom/2026-11-02-repair-skill-dev-toolkit/evidence/` (untouched by this fix).
- The confirmation suite command re-ran at the new HEAD in the clean worktree at `/tmp/at-c8d6de0ad`:
  - `python3 -m pytest scripts/ -q -p no:cacheprovider` → 715 passed in 49.92s

### Per-row re-run disposition

- 1-8, 10: carried over — fix only edits intent pin line; no Acceptance wording, code, test, or evidence changed; suite re-ran at new HEAD and passed (row 7)
- 9: carried over — full re-test completed at prior re-run (HEAD 2a6f311cd); this fix edits only the intent pin line; W18 verdict chain unchanged; verdict stays partly
- 11: carried over — full re-test completed at prior re-run (HEAD 2a6f311cd); this fix edits only the intent pin line; W18 verdict chain unchanged; verdict stays partly