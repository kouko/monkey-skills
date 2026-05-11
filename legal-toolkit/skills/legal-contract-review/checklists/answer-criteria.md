# answer-criteria — binary all-pass rubric for self-grade.md (answer_score)

> **Phase 1 status**: stub — the criteria below are the **Phase 1 baseline**, intended to be runnable as LLM self-eval prompts in protocols. Phase 1.6 introduces `scripts/self_grade.py` for automated scoring + dogfood-corpus calibration. The list will grow / be re-weighted based on Phase 1.6 hand-grading.

> **Convention** (Harvey BigLaw Bench): binary all-pass. Each criterion is "did the answer satisfy this?" — yes / no. NEVER averaged. Failed criteria listed explicitly in `self-grade.md`. No rounding. No "80%" — "8 of 10" is not the same as "80% correct".

---

## Criteria (Phase 1 baseline, N = 12)

| ID | Criterion (zh-TW) | Verification |
|---|---|---|
| **ANS-01** | 全部 7 層（L0a / L0b / L1-L7 / L6.5）依照 mode 規則執行 | check pipeline_path in contract_metadata covers all required layers |
| **ANS-02** | 每條 finding 都帶 `source_type` 標籤（user_playbook / bundled_fallback / advisory）| 100% findings have valid source_type enum value |
| **ANS-03** | 每條 finding 都帶 `playbook_trace.matched_entry_path` 或標 advisory | 100% findings have non-null matched_entry_path UNLESS source_type == advisory |
| **ANS-04** | 高風險 finding（red / walk_away / 低 confidence）都有 escalation entry | for each finding satisfying high-risk condition, escalation.md has a matching entry |
| **ANS-05** | Escalation Override 紅字 banner 在所有高風險輸出檔頭 | for each output containing high-risk finding, the file starts with Override block |
| **ANS-06** | 每份輸出檔尾含 Mandatory Disclaimer | for each of 6 output files, footer matches assets/disclaimer-block.md template |
| **ANS-07** | `escalate_to` 佔位符 placeholder warning 顯示給使用者 | when any finding's `escalate_to.startswith("[請編輯")`, escalation.md prepends placeholder callout |
| **ANS-08** | 每條 finding 含 zh-TW summary（非空、非 placeholder）| findings[i].summary_zh_tw is non-empty, not "TBD" or "[REPLACE_ME]" |
| **ANS-09** | redline.md 條目的 `proposed_text` 來源明確標示 | proposed_text_source ∈ {playbook_body, llm_generated} for every redline entry |
| **ANS-10** | memo-business.md 三句 Why/What/What-if 結構完整 | summary has all 3 keys, each ≤ 80 chars |
| **ANS-11** | self-grade.md 不藏 failed_criteria | failed_criteria array is populated whenever passed < total in answer_score or source_score |
| **ANS-12** | Pipeline 沒跳步 — L6 cycle 達到 termination condition | cycle_check.termination_condition is gaps_zero_at_cycle_<N>, not max_cycles_hit |

---

## Phase 1.6 expansion targets

Reserved IDs for future criteria (ANS-13 onwards), TBD based on hand-grading findings:

- ANS-13: party-consistency check ran and findings recorded
- ANS-14: 簽約主體一致性 verified (L2)
- ANS-15: definitions cross-reference complete (no undefined Capitalised Term)
- ANS-16: TW 強行規定 check fired on all relevant clauses (only when jurisdiction == TW)
- ANS-17: missing-expected-clause findings marked at correct priority tier
- ANS-18: ABAC pre-filter logged variant match decisions (single / zero / multi)
- ANS-19: walk-away LLM judge confidence captured per clause
- ANS-20: external-share strip correctly applied when flag passed

---

## Calibration (Phase 1.6)

Pearson correlation target for LLM self-eval vs hand-grading:
- answer_score Pearson ≥ 0.6 across 5-10 dogfood contracts
- If < 0.6: re-balance the criteria weights (move misfiring ones to "advisory" tier, add tighter binary versions)

---

## Anti-patterns the rubric is designed to detect

- **Skipping a layer** (e.g. LLM forgets to run L4): caught by ANS-01
- **Tagging everything as user_playbook** when source is bundled: ANS-02 + ANS-03 detect when source_type is omitted / wrong enum
- **Quiet failure of high-risk escalation** (red finding but no escalation row): ANS-04
- **Disclaimer drop** (LLM "tidies up" and removes the footer): ANS-06
- **Placeholder leak** (escalate_to never gets called out): ANS-07
- **`source_score: 0/0` collapse** to hide failures: ANS-11 still surfaces failed_criteria

---

## Output (consumed by self-grade.md generator)

For each criterion, emit:

```yaml
criterion_id: ANS-01
criterion_zh_tw: 全部 7 層依照 mode 規則執行
result: pass / fail
evidence: <pipeline_path string> OR <which layer was skipped>
```

Append all results to `self-grade.md.answer_score.criteria_results`, count passes and total.
