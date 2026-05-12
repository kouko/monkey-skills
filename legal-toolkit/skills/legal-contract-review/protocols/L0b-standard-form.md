# L0b — 定型化契約 §247-1 + 消保法 §11-1 (Taiwan jurisdiction overlay)

**Layer**: L0b (runs after L0a, before L1, when `jurisdiction == TW`)
**Runs**: jurisdiction == TW only
**Skipped**: any other jurisdiction; also skipped when contract is clearly bespoke / individually-negotiated (e.g. one-off M&A) per the §247-1 definition

---

## Purpose

L0b applies the 定型化契約 (standard-form / boilerplate-form contract) doctrine to flag clauses that may be **顯失公平** (manifestly unfair) and therefore voidable under 民法 §247-1, plus the 30-day review-period requirement under 消保法 §11-1 (consumer contracts only).

Like L0a, L0b is a filter — clauses caught here may also be caught by L7 playbook evaluation, but the §247-1 finding is reported separately as it provides a stronger remediation argument (the clause may be **void** in court, not merely "below fallback").

---

## Pipeline

### Step 1 — Is this a 定型化契約?

A contract qualifies as 定型化契約 when:

- One party has drafted standard terms intended for **plural transactions**
- The other party has no real opportunity to negotiate the terms individually
- Common B2B targets: SaaS subscription / cloud hosting / consumer-facing services
- Common non-targets: bespoke M&A / one-off bilateral negotiated agreements

If the contract is **bilateral negotiated** (e.g. user provides clear evidence of back-and-forth negotiation, or the contract type is clearly bespoke), skip L0b entirely.

Decision heuristic for the LLM:

```
is_standard_form ?
  = (contract_type ∈ {SaaS, 訂閱服務, 消費者服務, ToS, EULA, 雲端服務}) AND
    (no evidence of individual negotiation visible in the contract preamble) AND
    (user did NOT explicitly say "this is fully negotiated")
```

If unsure, **lean toward L0b applying** — false positives here are mild (LLM flags a clause that turns out to be negotiated → user dismisses), false negatives are worse (LLM misses an obvious unfair clause).

### Step 2 — §247-1 顯失公平 4 款 check

For each clause in the contract, evaluate against the 4 categories of presumptively-unfair terms:

**款 1** — 免除或減輕預定契約條款之當事人之責任者
（Disclaims or reduces the drafter's own liability.）
- LoL caps that protect only the drafter
- "We are not liable for ANY damages" clauses
- Force majeure that covers only the drafter

**款 2** — 加重他方當事人之責任者
（Imposes additional liability on the other party beyond fair allocation.）
- Indemnification by counterparty without reciprocal protection
- Customer-only late-fees / penalty interest
- "You will defend us at your cost" with no carve-outs

**款 3** — 使他方當事人拋棄權利或限制其行使權利者
（Forces other party to waive rights or restricts their exercise of rights.）
- Mandatory arbitration in drafter's jurisdiction
- Waiver of class action / consolidated proceeding
- Time-bar < 1 year on bringing claims

**款 4** — 其他於他方當事人有重大不利益者
（Otherwise materially disadvantages the other party.）
- Auto-renewal without meaningful notice (often: 30 天以下 notice = §247-1 款 4)
- Unilateral termination for convenience with no transition
- Price changes during term without justification

For each clause that triggers any of these 4 款, emit a finding:

```yaml
clause_id: <inferred>
source_type: bundled_fallback
severity: red                      # §247-1 顯失公平 = high severity by default
subtype: standard_form_unfair
violated_statute: "民法 §247-1 款 <N>"
violated_provision: "<which category>"
contract_text: "<verbatim>"
remediation: "主張條款無效 / 修改為對等條款 / 加 carve-out"
```

### Step 3 — 消保法 §11-1 review-period check (consumer contracts only)

If contract is a **consumer contract** (B2C, e.g. SaaS ToS for individual users / 行動應用程式服務條款):

- 消保法 §11-1: 企業經營者與消費者訂立定型化契約前，應有 30 日以內之合理期間，供消費者審閱全部條款
- Check: does the contract / its surrounding facts evidence the 30-day review period? Common evidence: pre-signing email exchange / time stamps / explicit clause acknowledging review period.
- If no evidence: emit finding `subtype: insufficient_review_period`, severity yellow, remediation "確認簽約前 30 天有提供條款給對方審閱 / 否則條款無效"

For B2B contracts, §11-1 is **not directly applicable**; do not flag.

### Step 4 — Pass control to L1

After L0a + L0b run, control passes to L1 (Expectations). Findings from L0a/L0b are **already in `issues.md`** so they survive the rest of the pipeline.

---

## Output contract

```
✅ L0b complete.
   定型化契約 status: standard_form / bespoke
   §247-1 violations found: <count>
   §11-1 review-period issue: yes / no / not applicable (B2B)
   Findings added to issues.md: <count>
   Pass to: L1
```

---

## Edge cases

- **Clause unfair under multiple 款**: report the most specific 款 (款 1-3 are more specific than 款 4); keep 款 4 for the genuine catch-all.
- **Bilateral SaaS but with negotiated MSA layer**: SaaS underlying ToS often have §247-1 issues even when MSA is bilaterally negotiated. Flag the ToS-level issues but note in remediation: "若 MSA 已 override 此條，§247-1 finding 可豁免".
- **個資處理 條款 unfair**: report both §247-1 finding (L0b) AND 個資法 §3 violation (L0a). User can decide which argument to lead with.
- **Contract is a translated foreign-template**: §247-1 applies to the TW party signing it, regardless of origin. Do not skip just because clauses look "imported".
- **User contests 「我已 review」**: L0b's review-period check is evidence-based — if the user-supplied contract bundle includes pre-signing exchange showing review opportunity, mark `review_period_satisfied: true`.
