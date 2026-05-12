# L1 — Expectations (universal layer)

**Layer**: L1 (always runs; first universal layer)
**Reads**: playbook **index** (filenames + `clause_id` frontmatter); not bodies

---

## Purpose

Before looking at what the contract **does say**, L1 lists what the contract **should say** — the universe of expected clauses given its type and the user's playbook. Missing-clause detection in L6 depends on this list.

Expectations = bundled defaults for the contract type **∪** the union of `clause_id` values present in the user's `legal-playbook/` (including bundled fallback when no user playbook exists).

---

## Pipeline

### Step 1 — Determine contract type

If the user supplied `contract_type` as input, use it. Otherwise, infer from contract content via standard markers:

| Contract type | Common markers |
|---|---|
| **NDA** | "Mutual Non-Disclosure Agreement" / "保密協議" / "Confidentiality Agreement" alone (no service obligations) |
| **SaaS / 訂閱服務** | "Subscription Services" / "SaaS" / "monthly fee" / "user accounts" / "uptime" / "SLA" |
| **MSA / 服務協議** | "Master Services Agreement" / "Statement of Work" / "Services" + "Deliverables" |
| **採購** | "Purchase Agreement" / "Goods" / "Delivery" / "Inspection" |
| **勞動契約** | "Employment Agreement" / "Employee" / "Compensation" / "Title" |
| **DPA** | "Data Processing Agreement" / "個資法 / GDPR" / "Personal Data" + Article 28 references |
| **經銷 / 代理** | "Distribution" / "Reseller" / "Territory" + "Exclusivity" |

If multiple types are mixed (common: SaaS contract embeds a DPA), L1 treats the **dominant** type as primary but lists expected clauses for all relevant types.

### Step 2 — Load bundled-expectation template for the type

For each canonical type, the bundled expectation list ships in this skill's domain knowledge. Examples:

**SaaS / MSA**:
- definitions / parties
- services & deliverables (incl. SLA)
- term & termination & survival
- payment terms & invoicing
- IP ownership & license grants
- confidentiality
- warranties & disclaimers
- limitation of liability
- indemnification
- data protection / DPA (when applicable)
- governing law & jurisdiction
- assignment / change of control
- force majeure
- notices

**NDA**:
- definitions of confidential information
- mutuality (one-way vs. mutual)
- term of confidentiality obligation
- residual knowledge clause
- carve-outs (public domain, independent development, etc.)
- remedies & injunctive relief
- return / destruction
- governing law

**勞動契約**:
- 職務 / 工作場所 / 工作時間
- 報酬 (薪資 / 獎金 / 福利)
- 試用期
- 競業禁止 (if any; subject to 勞基法 §9-1)
- 最低服務年限 (if any; subject to 勞基法 §15-1)
- 智財權歸屬
- 解雇 / 終止 條件
- 保密
- 準據法 / 管轄

(Full bundled-expectation tables live in [`references/domain-priority-by-type.md`](../references/domain-priority-by-type.md).)

### Step 3 — Union with playbook index

Scan `legal-playbook/` (or bundled fallback if discovery returned empty):

```
playbook_index = {
   <clause_id> from each .md file in legal-playbook/ (or fallback)
}
```

Build `expectations` set:

```
expectations = bundled_expectations[contract_type] ∪ playbook_index
```

If the playbook contains a `clause_id` not in `bundled_expectations[contract_type]`, **still include it** — the user has codified a custom position for that clause, and it should be checked even if not "expected" for this contract type. (Example: user has a `data-protection-dpa` entry; the contract is a vanilla NDA without DPA terms — still include DPA in expectations, so L6 may flag "missing DPA" as advisory.)

### Step 4 — Output expectations list

Emit to internal pipeline state (not directly to `issues.md`; downstream layers consume):

```yaml
expectations:
  contract_type: SaaS
  expected_clauses:
    - clause_id: definitions
      source: bundled
    - clause_id: confidentiality
      source: bundled ∪ playbook
    - clause_id: limitation-of-liability
      source: bundled ∪ playbook
      variant_layout: yes   # variant-folder detected
    # ... etc
```

L2 / L3 then map contract clauses to expectations; L6 flags expectations that have no matching contract clause (missing items).

---

## Output contract

```
✅ L1 complete.
   Contract type: <type>
   Expected clauses: <count>
   Source: bundled (<count>) + playbook (<count>) + intersection (<count>)
   Pass to: L2
```

---

## Edge cases

- **Multi-type contract (SaaS + DPA mixed)**: union both type's bundled lists; flag overlap (e.g. "data-protection" expected from both contexts).
- **Empty playbook + non-cold-start (user has the folder but no clauses)**: treat as cold-start fallback — use bundled fallback's 4 clauses for the union.
- **User passes `contract_type: unknown` or LLM cannot infer**: use a broad union (SaaS + MSA + NDA + 採購 cover ~80% of cases) and tag the L1 output `contract_type_inferred: low_confidence`. Downstream layers (especially L7) should be more conservative.
- **`legal-playbook/` has 100+ entries (Phase 2-3 future)**: only entries whose `contract_types_applicable` includes the inferred contract type or `[*]` join the expectations set.
