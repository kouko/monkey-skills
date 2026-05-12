# Domain Priority by Contract Type

Per-contract-type priority ordering of clauses, used by L5 (domain priority sort) to tier issues for output emission.

⚠️ **Priority** = "review attention" priority, not "legal importance" — a clause may be legally critical but rarely problematic (e.g. Severability), and another may be less legally important but always heavily negotiated (e.g. Auto-Renewal). Priority reflects the latter.

Source: WorldCC 2024 Benchmark Top-10 Most Negotiated Terms + ContractKen Playbook prioritisation + Taiwan in-house practice convention (理律 / 寰瀛 / 眾達 newsletters 2020-2024).

---

## SaaS / MSA / Services Agreement

**Tier 1 (critical — top 5)**:

1. **Limitation of liability** (LoL caps, super-cap exclusions, indirect/consequential damages)
2. **Indemnification** (IP-infringement, breach-of-warranty, third-party-claim coverage; mutuality)
3. **Data protection / DPA** (GDPR Art.28 + 個資法 §27; cross-border transfer; 72hr 通報 義務)
4. **IP ownership & license grants** (work product / pre-existing IP / customer data; license scope and exclusivity)
5. **Termination & survival** (for-cause / for-convenience / wind-down / survival of confidentiality / IP / accrued claims)

**Tier 2 (important — ranks 6-15)**:

6. Auto-renewal & pricing changes
7. Confidentiality
8. Warranties & disclaimers (SLA / merchantability / fitness for purpose)
9. SLA / performance standards (uptime, support response, credits)
10. Governing law & jurisdiction
11. Payment terms & invoicing (Net N, late fees, disputed amounts)
12. Assignment / change of control
13. Force majeure
14. Audit rights
15. Insurance requirements

**Tier 3 (admin / boilerplate — rank 16+)**:

16. Notices
17. Severability
18. Entire agreement
19. Counterparts
20. Amendment / modification
21. Waiver
22. Headings & captions

---

## NDA / Confidentiality Agreement

**Tier 1 (critical — top 5)**:

1. **Definition of Confidential Information** (scope, exclusions, residual knowledge)
2. **Mutuality** (one-way vs. mutual)
3. **Term of confidentiality obligation** (3 / 5 years vs. perpetual)
4. **Carve-outs** (public domain / independent development / third-party rightful disclosure / required-by-law)
5. **Remedies & injunctive relief**

**Tier 2 (important)**:

6. Return / destruction of materials
7. Notice of compelled disclosure
8. Governing law / jurisdiction
9. No license / no obligation to enter further agreement
10. Standstill / non-solicit (if present)

**Tier 3 (admin)**:

11. Entire agreement
12. Severability
13. Counterparts

---

## 採購合約 / Purchase Agreement

**Tier 1 (critical)**:

1. **Specifications & acceptance criteria** (what counts as conforming goods)
2. **Warranties** (merchantability, fitness for purpose, hidden defects under 民法 §354)
3. **Delivery & risk of loss** (Incoterms; transfer of title)
4. **Payment terms** (Net N, milestones, retention)
5. **Termination & remedies** (for non-conformity, for late delivery)

**Tier 2 (important)**:

6. IP infringement indemnification
7. Limitation of liability
8. Inspection rights
9. Change orders & price escalation
10. Force majeure
11. Governing law / jurisdiction
12. Insurance & liability assumption

**Tier 3 (admin)**:

13. Notices, entire agreement, severability, counterparts, etc.

---

## 勞動契約 / Employment Agreement

**Tier 1 (critical)**:

1. **競業禁止 (Non-compete)** — 勞基法 §9-1 四要件：(a) 時間 ≤ 2 年；(b) 區域限定；(c) 職務範圍限定；(d) 合理補償
2. **最低服務年限 (Minimum service period)** — 勞基法 §15-1：(a) 雇主有專業培訓 OR 給付合理報償；(b) 年限合理
3. **智財權歸屬 (IP assignment)** — 受雇職務範圍 vs 業餘創作 carve-out
4. **報酬結構 (Compensation)** — 薪資、獎金、福利、加班、休假
5. **解雇 / 終止條件 (Termination grounds)** — 勞基法 §11/§12 vs §14；資遣 vs 解雇

**Tier 2 (important)**:

6. 試用期 (Probation period) — 合理性
7. 工作場所 / 職務 / 工作時間
8. 保密
9. 工作規則 (Work rules)
10. 主管機關報備事項

**Tier 3 (admin)**:

11. 勞健保 / 退休金
12. 教育訓練
13. 離職交接

---

## DPA / Data Processing Agreement

**Tier 1 (critical)**:

1. **Scope of processing** (categories of data, processing purposes, retention)
2. **Sub-processor management** (consent / list / notice)
3. **Cross-border transfer** (個資法 §21 / GDPR Chapter V / SCCs / TIA)
4. **Security measures** (encryption, access control, breach detection)
5. **Breach notification** (72-hour window — 個資法 2025/11 新制 / GDPR Art.33)

**Tier 2 (important)**:

6. Data subject rights (access, deletion, portability)
7. Cooperation with regulators
8. Audit rights & evidence of compliance (SOC 2, ISO 27001)
9. Data return / deletion on termination
10. Liability allocation (controller vs processor)

**Tier 3 (admin)**:

11. Term, governing law, notices, etc.

---

## 經銷 / 代理 / Distribution Agreement

**Tier 1 (critical)**:

1. **Territory & exclusivity**
2. **Minimum purchase / sales commitments**
3. **Pricing & price-change rights**
4. **Term & renewal & termination**
5. **Post-termination obligations** (inventory buyback, customer transition)

**Tier 2 (important)**:

6. IP rights & trademark use
7. Quality control & brand standards
8. Competing products restriction
9. Liability & indemnification
10. Reporting & audit rights

**Tier 3 (admin)**:

11. Governing law, notices, severability, etc.

---

## Default priority (when contract_type is unknown or mixed)

When L1 cannot infer the contract type confidently:

- Use the **SaaS / MSA** priority list (most generic, covers most B2B service relationships)
- Tag `priority_inferred_low_confidence: true`
- Downstream layers treat the ordering as informational, not load-bearing
- Suggest user provide `contract_type` explicitly on re-run

---

## How L5 uses this file

```
1. Look up contract_type's priority list (or default to SaaS/MSA)
2. Build base ordering for the contract's clauses
3. For each clause that has a matched playbook entry, augment +1 position
4. Tier into Tier 1 / 2 / 3 by rank cutoffs
5. Pass to L6 / L7 / output emission
```

L7 prioritises Tier 1 clauses for full LLM evaluation; Tier 3 clauses get a lighter pass.

---

## Updating this file

When monkey-skills phase 2-5 add new contract types (e.g. corporate-governance materials use a different priority list), this file extends with a new section. The file is **content-only** — the L5 protocol's loading logic is fixed and doesn't need updating.

Phase 1.5 / 1.6 may calibrate the tier cutoffs based on dogfood feedback (e.g. "Auto-renewal should be Tier 1 for our user base, not Tier 2" — this is editable text, not code).
