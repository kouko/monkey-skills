# L0a — 強行 / 任意 規定二分 (Taiwan jurisdiction overlay)

**Layer**: L0a (Taiwan-only pre-layer; runs before L1 when `jurisdiction == TW`)
**Runs**: jurisdiction == TW only
**Skipped**: any other jurisdiction (US / CN / cross-border without TW pivot)

---

## Purpose

Before the universal 7-layer pipeline runs, Taiwan-jurisdiction contracts get a **bilateral pre-pass** that filters out clauses contradicting 強行規定 (mandatory rules) before any further analysis. The reason: a clause that violates 強行規定 is **legally void** (民法 §71) regardless of any negotiated agreement. There is no point in evaluating against the user's playbook a clause that cannot legally exist.

L0a is a **filter**, not a finding generator. Clauses flagged here are tagged in `issues.md` as `severity: red` with `subtype: void_under_mandatory_rule`, and the L7 evaluate step skips them (no playbook comparison needed; recommendation is "strike or replace, not negotiate").

---

## Pipeline

### Step 1 — Build the 強行規定 reference list

Pull from bundled TW legal knowledge (no playbook read):

**Common mandatory-rule scopes affecting B2B / employment / consumer contracts**:

| Statute | §  | Subject |
|---|---|---|
| 民法 | §71 | 違反強制 / 禁止規定之法律行為無效 |
| 民法 | §72 | 違反公共秩序善良風俗之法律行為無效 |
| 民法 | §247-1 | 定型化契約顯失公平 — 4 款（partly overlaps with L0b） |
| 勞基法 | §9-1 | 競業禁止有效要件（時間/區域/職務範圍/補償） |
| 勞基法 | §15-1 | 最低服務年限有效要件 |
| 勞基法 | §16 | 預告期間 |
| 勞基法 | §70 | 工作規則應記載事項 |
| 消保法 | §11-1 | 定型化契約應給予 30 日審閱期 |
| 消保法 | §17 | 主管機關得公告定型化契約應記載及不得記載事項 |
| 個資法 | §3 | 當事人權利不得預先拋棄 |
| 個資法 | §5 | 蒐集 / 處理 / 利用 應符合特定目的 + 比例原則 |
| 個資法 | §8 | 告知義務 |
| 公平交易法 | §20 | 禁止獨占 / 結合 / 聯合行為對特定條款的限制 |
| 公平交易法 | §25 | 對交易相對人之顯失公平條款 |
| 公司法 | §15 | 公司資金不得貸與股東或他人之強行規定 |
| 公司法 | §16 | 公司對外保證之強行規定 |
| 證交法 | §36 | 重大訊息揭露義務 |
| 證交法 | §157-1 | 內線交易禁止 |

### Step 2 — Scan contract for likely violations

For each clause in the contract:

1. **Subject-matter quick filter**: does the clause touch any of: 競業禁止 / 最低服務年限 / 個資處理 / 自動續約 / 賠償上限 / 仲裁強制 / 法律免責 ?
2. If yes, run the corresponding 強行規定 check:
   - 競業禁止 → 勞基法 §9-1 四要件（時間 ≤ 2 年 / 區域 limited / 職務 specific / 合理補償）
   - 最低服務年限 → 勞基法 §15-1（雇主需專業培訓投入 OR 給付合理報償，且年限合理）
   - 個資處理 → 個資法 §3 §5 §8（特定目的 / 比例 / 告知義務）
   - 定型化契約審閱期 → 消保法 §11-1（30 天，僅適用消費者契約）
   - 不公平交易條件 → 公平交易法 §25（顯失公平 / 不正當）

### Step 3 — Output

For each detected violation, emit a finding with this shape:

```yaml
clause_id: <inferred>
source_type: bundled_fallback   # because L0a uses bundled TW knowledge, not playbook
severity: red
subtype: void_under_mandatory_rule
violated_statute: "勞基法 §9-1"
violated_provision: "競業期間 5 年超過 2 年上限"
contract_text: "<verbatim clause snippet>"
remediation: "刪除或修改為 ≤ 2 年；或主張條款無效"
```

Add to `issues.md.findings` array. Set `findings[i].playbook_trace.matched_entry_path: null` (no playbook entry will be loaded for void clauses).

### Step 4 — Pass control to L0b

L0b checks 定型化契約 §247-1 顯失公平 4 款. Some clauses caught here may also be caught by L0b; report both findings (not redundant — different grounds, different remediation arguments).

---

## Output contract

```
✅ L0a complete.
   Mandatory-rule violations found: <count>
   Findings added to issues.md: <count>
   Pass to: L0b (TW jurisdiction continues)
```

---

## Edge cases

- **Clause violates both 強行規定 and a playbook walk-away**: emit two findings (one from L0a tagged `void_under_mandatory_rule`, one from L7 tagged `walk_away_triggered`). L0a's verdict is stronger; the playbook finding is recorded for traceability but L7 should not generate a "negotiate to fallback" suggestion.
- **Clause is borderline (e.g. 競業期間 18 months — under 2y cap but suspicious)**: do NOT flag as void; let it flow to L7. L0a is for **clear** violations only.
- **Subject matter is non-Taiwan (e.g. US labor law)**: skip L0a entirely; the jurisdiction filter caught it at the top.
- **User contests the bundled list (e.g. 「我們有 PDPC 函釋特例」)**: L0a uses bundled knowledge only; user-specific exceptions belong in `.legal-toolkit/config.yml` global_rules, not L0a. For Phase 1, this is not configurable; Phase 1.5 adds the override path.
