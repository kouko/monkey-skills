# L5 — Domain priority sort (universal layer)

**Layer**: L5 (always runs; runs after L4)
**Reads**: playbook index (for `augment` step)

---

## Purpose

L5 sorts the contract's clauses by **domain priority** — the per-contract-type priority ordering that decides which clauses get the most review attention and which findings should rank highest in `issues.md`. The output is a priority-weighted ordering of the contract's clauses for downstream L6 / L7 / output emission.

The "domain priority" is contract-type-specific: an LoL clause is high-priority in a SaaS MSA, less in an NDA. Auto-renewal is high-priority in SaaS, irrelevant in an NDA. The bundled per-type priority tables ship in [`references/domain-priority-by-type.md`](../references/domain-priority-by-type.md).

User's playbook augments — if the user has codified a position on a clause, that clause's priority is elevated (the user has signalled "I care about this").

---

## Pipeline

### Step 1 — Load bundled domain priority for contract type

From [`references/domain-priority-by-type.md`](../references/domain-priority-by-type.md):

**SaaS / MSA priority (top 10)**:
1. Limitation of liability
2. Indemnification
3. Data protection / DPA (if applicable)
4. IP ownership & license grants
5. Termination & survival
6. Auto-renewal & pricing changes
7. Confidentiality
8. Warranties & disclaimers
9. SLA / performance standards
10. Governing law & jurisdiction

**NDA priority (top 5)**:
1. Definition of Confidential Information (scope)
2. Mutuality (one-way vs. mutual)
3. Term of confidentiality obligation
4. Carve-outs (public domain, independent development, etc.)
5. Remedies & injunctive relief

**勞動契約 priority (top 8)**:
1. 競業禁止 (有效要件 勞基法 §9-1)
2. 最低服務年限 (有效要件 §15-1)
3. 智財權歸屬
4. 報酬結構 (薪資 / 獎金 / 福利)
5. 解雇 / 終止條件
6. 保密
7. 試用期 (合理性)
8. 工作時間 / 加班 / 休假

(Full per-type tables in the references file.)

### Step 2 — Augment with playbook signals

For each clause in the contract that has a matched playbook entry (from L7's eventual matching — but we make a preliminary pass here):

- If the entry has `priority_boost: true` frontmatter (Phase 2+ feature, default off in Phase 1), elevate by 2 positions
- Otherwise, the mere presence of a playbook entry elevates the clause by 1 position

Rationale: the user has signalled "I have a position on this" by codifying it. That elevates the clause's review priority.

### Step 3 — Sort and tier

Re-order the contract's clauses by computed priority:

```yaml
priority_ordering:
  - rank: 1
    clause_id: limitation-of-liability
    bundled_priority: 1
    playbook_signal: +1 (entry exists)
    final_score: 0   # rank 1 = top
  - rank: 2
    clause_id: indemnification
    bundled_priority: 2
    playbook_signal: 0 (no entry)
    final_score: 2
  # ...
```

### Step 4 — Tier the ordering for output

Three tiers used by L7 / output formatting:

- **Tier 1 (critical)**: top 5 clauses by domain priority
- **Tier 2 (important)**: ranks 6-15
- **Tier 3 (admin / boilerplate)**: rank 16+ (e.g. counterparts, notices)

`issues.md` lists Tier 1 findings prominently at the top; Tier 2 in the body; Tier 3 in an appendix.

### Step 5 — Output

Internal pipeline state:

```yaml
domain_priority:
  contract_type: SaaS
  priority_ordering:
    tier_1_critical: [limitation-of-liability, indemnification, data-protection-dpa, ip-assignment, termination-and-survival]
    tier_2_important: [auto-renewal, confidentiality, warranties, sla, governing-law, ...]
    tier_3_admin: [counterparts, notices, entire-agreement, ...]
  playbook_signals_used: <count>
  augmentations: [{clause_id: X, from: rank-7, to: rank-5}, ...]
```

---

## Output contract

```
✅ L5 complete.
   Contract type: <type>
   Tier 1 / 2 / 3 distribution: <counts>
   Playbook augmentations: <count>
   Pass to: L6
```

---

## Edge cases

- **Contract type is "unknown" or mixed**: use the broadest priority (SaaS + MSA union top 10) and tag `priority_inferred_low_confidence: true`. Downstream layers should treat the priority ordering as informational, not load-bearing.
- **Empty playbook**: no augmentation step; bundled priority is the only signal. Cold-start fallback's 4 entries (confidentiality / governing-law / auto-renewal / termination-and-survival) provide signal for those 4 clauses.
- **All clauses are in playbook** (well-developed user playbook): augmentation makes everything +1, so the ordering reverts to bundled priority. Don't double-augment.
- **Tier-1 clause is missing from the contract entirely**: L6 will flag this as a missing-items issue; L5 just produces the priority ordering, not the gap check.
