# L4 — Functional tier mapping (Burnham 5 business issues)

**Layer**: L4 (always runs; first business-impact layer)
**Reads**: playbook index frontmatter `business_issues` field (optional cross-check)

---

## Purpose

L4 maps every provision (or group of provisions on the same topic) to one or more of **Burnham's 5 functional tiers** — the business-impact taxonomy that translates "this is a legal clause" into "this matters for these reasons to the business":

1. **Money** — direct economic impact (price, payment terms, late fees, penalties, expenses)
2. **Risk** — exposure to financial loss not covered by Money (liability cap, indemnification, insurance)
3. **Control** — who decides what (assignment, change of control, IP rights, termination triggers)
4. **Standards** — what quality / level of performance applies (SLA, warranties, acceptance criteria)
5. **Endgame** — what happens at the end / when relationship breaks (termination, transition, dispute resolution, survival)

A single clause may touch multiple tiers (LoL → both Money and Risk; Termination → Endgame and Control). Tag all applicable.

Output powers L7 evaluation (the playbook entry's `business_issues` frontmatter field gets cross-checked here) and `issues.md.findings[i].business_issues`.

---

## Pipeline

### Step 1 — Map provisions to business tiers

For each provision (from L3 categorization), assign 1+ tier from {money, risk, control, standards, endgame}.

Heuristics:

| Clause type | Typical tier mapping |
|---|---|
| Pricing / fees / billing | **money** |
| Payment terms (Net 30 etc) | **money** + (sometimes **control** if non-payment triggers something) |
| Late fees / penalty interest | **money** + **risk** |
| Limitation of liability | **risk** + (often **money** if cap is monetary) |
| Indemnification | **risk** |
| Warranties (SLA / merchantability / fitness) | **standards** + **risk** (breach → liability) |
| Insurance requirements | **risk** + **money** (premium burden) |
| IP ownership / license grants | **control** |
| Assignment / change of control | **control** + **endgame** |
| Confidentiality | **risk** (info leak) + **control** (sharing rules) |
| Term / renewal | **endgame** |
| Termination | **endgame** + **control** |
| Force majeure | **endgame** + **risk** (allocation of disaster) |
| Governing law / jurisdiction | **endgame** + **control** (forum selection) |
| Dispute resolution / arbitration | **endgame** |
| Survival clauses | **endgame** |
| Notices / formalities | (administrative; rarely material — tag none or **control** if affecting deadlines) |

### Step 2 — Cross-check vs playbook `business_issues`

If a clause has a matched playbook entry (from L1's expectations + the eventual L7 matching), compare:

```
playbook_entry.frontmatter.business_issues  vs  L4-tagged tiers for the matched clause
```

Discrepancies = signal that either:
- The playbook entry's `business_issues` field is stale (user didn't update when the clause's nature changed)
- The contract clause is doing something **different** from what the playbook anticipated (e.g. LoL clause's `business_issues: [risk]` but the actual contract clause embeds a Money component too)

For each discrepancy, log to internal state (no `issues.md` finding yet; L7 decides whether to surface):

```yaml
playbook_drift:
  - clause_id: limitation-of-liability
    playbook_tags: [risk]
    detected_tags: [risk, money]
    note: "Contract LoL includes monetary penalty; playbook may need update"
```

### Step 3 — Flag high-impact concentration

Count provisions per tier. Flag if any single tier dominates (> 40% of total clauses):

```yaml
tier_concentration:
  money: 8 / 35 = 23%
  risk: 12 / 35 = 34%
  control: 11 / 35 = 31%        # HIGH
  standards: 2 / 35 = 6%        # LOW — flag: contract may be missing performance standards
  endgame: 2 / 35 = 6%          # LOW — flag: contract may be missing exit terms
```

LOW concentrations in **standards** or **endgame** are common signs of an under-developed contract — flag for L6 missing-items check.

### Step 4 — Output

Internal pipeline state:

```yaml
functional_tiering:
  per_provision:
    - { provision: "§2.1 Services", tiers: [control, standards] }
    - { provision: "§3.1 Fees", tiers: [money] }
    - { provision: "§11 LoL", tiers: [risk, money] }
    # ... etc
  tier_distribution:
    money: { count: 8, percent: 23 }
    risk: { count: 12, percent: 34 }
    control: { count: 11, percent: 31 }
    standards: { count: 2, percent: 6 }
    endgame: { count: 2, percent: 6 }
  playbook_drift: [...]      # from Step 2
  concentration_flags:
    - { tier: control, level: high }
    - { tier: standards, level: low }
    - { tier: endgame, level: low }
```

---

## Output contract

```
✅ L4 complete.
   Provisions tier-tagged: <count>
   Tier distribution: <summary>
   Playbook drift findings: <count>
   Concentration flags: <list>
   Pass to: L5
```

---

## Edge cases

- **Clause spans all 5 tiers** (rare but possible: a comprehensive damages clause): tag all 5; tier-concentration counts each tag separately, not per-clause.
- **mode == "nda"**: simpler taxonomy applies — NDAs mostly hit **risk** (info leak) and **endgame** (termination of obligations). Other tiers usually empty; don't flag low concentration in those.
- **Playbook `business_issues` is empty** (legacy entry without the field): don't flag drift; the field is optional in Phase 1 schema.
- **Long contract, > 100 provisions**: tier distribution is still meaningful but concentration thresholds should normalise to the larger N (e.g. > 40% is still > 40% regardless of N).
