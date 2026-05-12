# L6.5 — 六準則契約解釋 (Taiwan jurisdiction overlay)

**Layer**: L6.5 (runs after L6, before L7, when `jurisdiction == TW`)
**Runs**: jurisdiction == TW only
**Skipped**: any other jurisdiction
**Reads**: no playbook (bundled TW interpretation rules)

---

## Purpose

L6.5 applies Taiwan's **六準則契約解釋** (six-criterion contract interpretation) to any clauses identified as **ambiguous** during L2-L6. The 六準則 are the canonical Taiwan-law hierarchy for resolving ambiguity in contract terms; applying them surfaces interpretation risk that would otherwise hide in plain language.

Source: 王澤鑑《契約解釋》(2014) + 吳從周〈契約解釋之六準則〉法學新論第 17 期 (2009) + 民法 §98 (依當事人之真意，不拘泥於所用辭句).

The 6 criteria, in priority order:

1. **當事人之目的** (parties' purpose)
2. **習慣** (custom / trade usage)
3. **任意法規** (default rules — the gap-filler statute)
4. **誠信原則** (good faith and fair dealing)
5. **文義** (textual reading — the plain meaning of words used)
6. **體系** (systematic / contextual reading — how the clause fits the rest of the contract)

When a clause is ambiguous, L6.5 asks: what does criterion 1 say? If it resolves the ambiguity, stop. If not, proceed to criterion 2. And so on. Only after exhausting 1-4 do you fall back to plain text (5) and systematic reading (6).

---

## Pipeline

### Step 1 — Identify ambiguous clauses

From L2-L6 outputs, collect clauses tagged with any of these flags:

- L3: `mixed_concept_provision`, `will_disguised_obligation`
- L4: `playbook_drift` (the clause is doing something different from what playbook anticipates)
- L6: `undefined_term`, `if_breach_branch_missing`
- L6: `missing_expected_clause` where there is a partial clause that could be interpreted multiply

For each ambiguous clause, proceed to Step 2.

### Step 2 — Apply 六準則 in order

For each ambiguous clause:

**Criterion 1 — 當事人之目的**

Look at the **preamble's recitals** (whereas clauses) and the contract's **stated purpose**. Does it constrain the ambiguous clause to one of the candidate interpretations?

- Example: ambiguous "Services" definition + recital says "...desires Vendor to provide cloud-hosted SaaS for HR management" → "Services" is clearly the SaaS HR product, not consulting / dev work.

If resolved, record:
```yaml
interpretation_at: 當事人之目的
resolved_to: <interpretation>
reasoning: <recital text + how it constrains>
```

If not resolved, proceed.

**Criterion 2 — 習慣 (trade custom)**

Is there an industry-standard interpretation? Reference common contract conventions:

- SaaS "uptime" without specification → industry custom = 99.9% / monthly / excluding scheduled maintenance
- "Best efforts" without specification → industry custom = commercially reasonable efforts
- "Material breach" without specification → custom = breach affecting essential function of contract

If 習慣 resolves, record similarly.

**Criterion 3 — 任意法規 (default rules)**

What does the relevant statute say if the parties hadn't spoken? 民法 has many gap-filler rules:

- 民法 §227 (不完全給付) → default for service performance issues
- 民法 §229 (遲延) → default for delayed performance
- 民法 §354 (買賣物之瑕疵) → default for goods quality
- 民法 §490 (承攬人之報酬) → default for fee disputes

Apply the default rule's interpretation.

**Criterion 4 — 誠信原則 (good faith and fair dealing)**

What interpretation would a good-faith counterparty have understood? 民法 §148 派生原則 — exercise of rights subject to good faith. Reject interpretations that would create absurd / one-sided outcomes a reasonable party would not have agreed to.

- Example: an over-broad indemnification that, literally read, would require the customer to indemnify the vendor for the vendor's own fraud — 誠信原則 says this interpretation must be rejected.

**Criterion 5 — 文義 (plain meaning)**

If 1-4 don't resolve, fall back to the **plain meaning** of the words used. Note: 文義 is **last among priority** in Taiwan law (民法 §98), unlike US "plain meaning rule".

**Criterion 6 — 體系 (systematic reading)**

Read the ambiguous clause in light of the rest of the contract. Are there other provisions that constrain its meaning?

- Example: ambiguous "Confidential Information" definition + later clause has "Customer Data is treated as Confidential Information except for aggregated analytics" → 體系 confirms scope.

### Step 3 — Emit findings

For each ambiguous clause that goes through 六準則 interpretation:

```yaml
clause_id: <inferred>
source_type: advisory
severity:
  - if interpretation hinges on 誠信原則 / 任意法規 (and could swing dispute): yellow
  - if resolved cleanly at 當事人之目的 / 習慣: green (informational, not finding)
  - if irresolvable even after 6 criteria: red (genuine ambiguity, recommend amendment)
subtype: tw_six_criteria_interpretation
ambiguity: <original ambiguous text>
resolved_at_criterion: <which one>
chosen_interpretation: <text>
alternative_interpretations: [<list>]
remediation: <suggested clarifying language, if not resolved cleanly>
```

### Step 4 — Output

Internal pipeline state:

```yaml
six_criteria_check:
  total_ambiguities: <count>
  resolved_at:
    當事人之目的: <count>
    習慣: <count>
    任意法規: <count>
    誠信原則: <count>
    文義: <count>
    體系: <count>
    unresolved: <count>
```

Pass to L7.

---

## Output contract

```
✅ L6.5 complete (TW jurisdiction).
   Ambiguous clauses analysed: <count>
   Resolution distribution by criterion: <summary>
   Unresolved (genuine ambiguity): <count>
   Pass to: L7
```

---

## Edge cases

- **No ambiguities** (contract is well-drafted): L6.5 outputs zero findings; no overhead. This is the common case.
- **Ambiguity is intentional** (the parties want optionality): not a finding. The LLM should be conservative — only flag if the ambiguity creates a substantive risk of dispute.
- **Recitals are skeletal** ("whereas Vendor offers software"): 當事人之目的 not very useful; lean on 習慣 / 任意法規.
- **No applicable 任意法規** (cutting-edge tech contracts e.g. AI training rights): proceed to 誠信原則 / 文義 / 體系.
- **GDPR overlay** clauses where TW 民法 has no equivalent: skip 任意法規, lean on 習慣 (international trade custom) and 誠信原則.
- **Mixed-jurisdiction contract** (e.g. TW + US choice of law): apply 六準則 to clauses governed by TW law only; for US-law clauses, use US contract interpretation principles (out of scope for L6.5 — L7 may emit advisory finding).
