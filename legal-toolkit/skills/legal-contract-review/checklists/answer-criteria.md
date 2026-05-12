# answer-criteria — binary all-pass rubric for findings.json#self_grade (answer_score)

> **v0.3.0 (Phase 1.6) status**: full 20-criterion rubric. Consumed by
> `scripts/self_grade.py` (deterministic Python check on the rubric's
> programmatically-verifiable subset) AND by the LLM at session-grade time
> (for criteria that require semantic judgment).

> **Convention** (Harvey BigLaw Bench): binary all-pass. Each criterion is
> "did the answer satisfy this?" — yes / no. NEVER averaged. Failed
> criteria listed explicitly in `findings.json#self_grade`. No rounding. "12 of 20" is
> not the same as "60%" — show the gap, don't hide it.

> **Two tiers**: each criterion is tagged `tier: deterministic` (Python
> checks `self_grade.py` can verify) or `tier: semantic` (LLM must judge).
> `self_grade.py` runs the deterministic tier; protocols emit prompts for
> the LLM to run the semantic tier and append results.

---

## Criteria (N = 20)

### Tier: deterministic (Python-verifiable in self_grade.py)

| ID | Criterion (zh-TW) | Verification | Source field |
|---|---|---|---|
| **ANS-01** | 全部 7 層（L0a / L0b / L1-L7 / L6.5）依照 mode 規則執行 | `pipeline_path` 字串包含 mode-required layer names | `contract_metadata.pipeline_path` |
| **ANS-02** | 每條 finding 都帶 valid `source_type` enum 值 | 100% findings have `source_type ∈ {user_playbook, bundled_fallback, advisory}` | `findings[].source_type` |
| **ANS-03** | 每條 user/bundled finding 都有 `matched_entry_path`；advisory 才允許 null | for non-advisory findings, `playbook_trace.matched_entry_path` is non-null | `findings[].playbook_trace.matched_entry_path` |
| **ANS-04** | 每個高風險 finding 在 `findings.json#escalations[]` 有對應 row (rendered in `legal.md §升級簽核`) | high-risk = (severity==red OR walk_away_triggered OR low_confidence); for each high-risk finding, escalations has matching clause_id | `findings[]` ↔ `escalations[]` |
| **ANS-05** | Escalation Override 紅字 banner 出現在 `legal.md` 檔頭 (v0.3.4+: 不再檢 escalation.md，因為 v0.3.4 把 escalation 併進 legal.md) | when `override_triggered == true`, `legal.md` first 30 lines contain `> [!danger]` block | `legal.md` first 30 lines |
| **ANS-06** | 每份輸出 .md 檔尾含 Mandatory Disclaimer (v0.3.4+: 2 files — `legal.md` + `business.md`; was 5 files in v0.3.3) | both output .md files end with `## ⚠️ 重要聲明（Disclaimer）` section | last 50 lines of each output |
| **ANS-07** | 含 placeholder escalate_to 時 `findings.json#placeholder_warnings[]` 非空 (rendered in `legal.md §升級簽核` warning callout) | when any finding has `escalate_to_is_placeholder == true`, placeholder_warnings non-empty | `placeholder_warnings[]` |
| **ANS-08** | 每條 finding 含 zh-TW summary（非空、非 placeholder）| `summary_zh_tw` non-empty AND does not contain "TBD" / "[REPLACE_ME]" | `findings[].summary_zh_tw` |
| **ANS-09** | redline 條目的 `proposed_text_source` 明確標示 (in `findings.json#redlines[]`, rendered in `legal.md §主動 Redline 提案`) | every redline has `proposed_text_source ∈ {playbook_body, llm_generated}` | `redlines[].proposed_text_source` |
| **ANS-10** | `business.md` 三句結構完整 (Why/What/What-if) | `findings.json#summary_business` has all 3 keys, each non-empty, each ≤ 80 chars | `summary_business.{why,what,what_if}` |
| **ANS-11** | `findings.json#self_grade.failed_criteria` 不藏（v0.3.4+: self_grade 已從 findings.json#self_grade 遷入 findings.json） | `failed_criteria[]` is populated iff (answer_passed<answer_total OR source_passed<source_total) | `failed_criteria[]` |
| **ANS-12** | Pipeline 沒跳步 — L6 cycle 達到 termination condition | `cycle_check.termination_condition == "gaps_zero_at_cycle_<N>"` (not `max_cycles_hit`) | internal pipeline state |
| **ANS-13** | Party-consistency check ran (L2) | L2 anatomy emits `party_consistency.inconsistencies[]` (possibly empty) | `anatomy.party_consistency` |
| **ANS-14** | output-schema 驗證通過 (v0.3.4+: 3 outputs — legal-md / business-md / findings) | each output's JSON shape validates against its `output-schema-*.json` | 3 schemas |
| **ANS-15** | ABAC pre-filter logged variant decisions for variant-folder entries | for findings with variant-folder source, ABAC outcome ∈ {single, advisory, multi} recorded | internal pipeline state |
| **ANS-16** | TW jurisdiction → L0a + L0b + L6.5 all fired | when `jurisdiction == TW`, pipeline_path includes "L0a", "L0b", "L6.5" | `contract_metadata.{jurisdiction, pipeline_path}` |
| **ANS-17** | `--external-share` flag correctly applied when passed | when external_share flag set, `playbook_trace.external_share_strip_id == true` (rendered in `legal.md §法律分析` + §升級簽核 sections); Override banner NOT stripped | runtime flag + output content |

### Tier: semantic (LLM-judged at session-grade time)

| ID | Criterion (zh-TW) | LLM judgment prompt |
|---|---|---|
| **ANS-18** | 每條 finding 跟 contract clause 真的對得起來（不是 hallucinated） | "Does this finding describe a real clause from the contract? Quote the clause text and assess." |
| **ANS-19** | walk_away_trigger 判斷沒有 false positive（觸發的紅線確實是 contract 違反）| "For each `walk_away_triggered == true` finding, does the contract clause actually match the trigger condition cited?" |
| **ANS-20** | `business.md` "What-if" 句具體可行動（不是 generic「會出事」） | "Does the 'what_if' sentence contain a concrete consequence + specific impacted action, not generic 'risk exists'?" |

---

## Calibration (v0.3.0)

Pearson correlation target for LLM self-eval vs hand-grading:
- **answer_score Pearson ≥ 0.6** across 5-10 dogfood contracts
- If < 0.6: re-balance the criteria — move misfiring semantic items to
  advisory tier; add tighter binary versions; never just lower the bar
- If gap is on the deterministic tier — that's a `self_grade.py` bug, fix it

See `docs/dogfood-procedure.md` for the calibration workflow.

---

## Anti-patterns the rubric is designed to detect

- **Skipping a layer** (LLM forgets to run L4) → ANS-01 / ANS-16
- **Tagging everything as user_playbook** when source is bundled → ANS-02 + ANS-03
- **Quiet failure of high-risk escalation** (red finding but no escalation row) → ANS-04
- **Disclaimer drop** (LLM "tidies up" and removes the footer) → ANS-06
- **Placeholder leak** (escalate_to placeholder never gets called out) → ANS-07
- **`source_score: 0/0` collapse** to hide failures → ANS-11
- **Hallucinated findings** (LLM invents a clause that isn't in the contract) → ANS-18
- **False-positive walk-aways** (over-triggering red) → ANS-19
- **Generic `business.md` prose** ("這個合約有風險") → ANS-20
- **External-share leakage** (Override banner stripped) → ANS-17

---

## Output (consumed by findings.json#self_grade generator)

For each criterion, emit:

```yaml
criterion_id: ANS-01
criterion_zh_tw: 全部 7 層依照 mode 規則執行
tier: deterministic
result: pass / fail
evidence: "<pipeline_path string captured>" OR "<which layer was skipped>"
```

Append all results to `findings.json#self_grade.answer_score.criteria_results`,
count passes and total. The aggregated `answer_score: passed/total` is
**the score**; `failed_criteria` is the audit trail.

`self_grade.py` runs the 17 deterministic checks; the 3 semantic checks
are emitted as LLM prompts the protocol-driven session evaluates.
