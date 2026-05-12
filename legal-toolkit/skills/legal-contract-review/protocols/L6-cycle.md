# L6 — Cycle / cross-reference (universal layer)

**Layer**: L6 (always runs; bounded loop until convergence)
**Reads**: playbook index (for missing-items flag)
**Loop**: continues until `gaps == 0 AND cycle >= 2`

---

## Purpose

L6 is the **consistency** layer. It iterates over the categorised + tiered contract structure and asks: do all the parts cohere? **Four sub-checks** run in each cycle, bounded by a "no new gaps + at least 2 cycles" termination condition.

1. **If-breach branch check** — for every Obligation (Stark concept) the contract defines, is there a corresponding consequence-on-breach? (If not: gap.)
2. **Definitions cross-read** — every term used elsewhere in the contract must trace back to either the Definitions section or an inline definition. (If not: gap.)
3. **Missing-items vs L1 expectations** — for every expected clause from L1, is it present somewhere in the contract? (If not: high-weight finding.)
4. **Vagueness scan** (v0.3.1+) — for every clause that IS present, are the implementation sub-mechanisms specified? (e.g. an audit clause is present but with no cadence / cost / scope; a deletion clause is present but with no proof-of-deletion mechanism.) Sub-check 3 catches "whole clause missing"; sub-check 4 catches "clause exists but is vague at sub-mechanism level".

The cycle re-runs to catch second-order issues that emerge after first-pass fixes (e.g. fixing a missing-definition reveals another). Bound: minimum 2 cycles, terminate when `gaps == 0` (no new gaps found in the last cycle).

---

## Pipeline

### Step 1 — Initialise cycle counter

```
cycle = 0
gaps = []         # accumulated across cycles
```

### Step 2 — Cycle loop (runs at least 2 iterations)

```
do:
  cycle += 1
  new_gaps_this_cycle = []

  for each Obligation in L3 categorisation:
    if no corresponding consequence-on-breach in the contract:
      new_gaps_this_cycle.append({
        type: if_breach_branch_missing,
        clause: <ref>,
        obligation: <text>,
        suggested_remediation: "Add explicit consequence (e.g. material breach → termination right)"
      })

  for each Capitalised Term used in the contract:
    if term not in L2's definitions_index:
      new_gaps_this_cycle.append({
        type: undefined_term,
        term: <name>,
        used_at: <ref>,
        suggested_remediation: "Add definition or replace with un-capitalised general term"
      })

  for each expected_clause in L1's expectations:
    if expected_clause not represented anywhere in contract's anatomy:
      new_gaps_this_cycle.append({
        type: missing_expected_clause,
        clause_id: <expected_clause.clause_id>,
        source: bundled OR playbook OR both,
        priority: from L5 (tier 1 / 2 / 3),
        suggested_remediation: "Add clause; check playbook for canonical text"
      })

  # Sub-check 4 (v0.3.1+): vagueness scan
  for each present_clause in contract anatomy:
    dimensions = vagueness_dimensions_for(present_clause.id, contract_type)
    for each dimension in dimensions:
      if dimension.required AND clause_text does NOT specify dimension:
        new_gaps_this_cycle.append({
          type: vague_sub_mechanism,
          clause_id: present_clause.id,
          dimension: dimension.name,
          severity: dimension.severity_when_missing,
          suggested_remediation: dimension.remediation_hint
        })

  gaps.extend(new_gaps_this_cycle)
  no_new_gaps = len(new_gaps_this_cycle) == 0

  exit condition: cycle >= 2 AND no_new_gaps
while not exit_condition
```

### Step 2.1 — Vagueness dimension table (v0.3.1+)

`vagueness_dimensions_for(clause_id, contract_type)` returns a list of `{name, required, severity_when_missing, remediation_hint}` per (clause, contract_type) pair. v0.3.1 ships the canonical set for the most common clause families:

| clause_id | dimension | required for | severity if missing | remediation hint |
|---|---|---|---|---|
| `confidentiality` | `marking_requirement` (written-marking vs identified-by-context) | all | yellow | 「視為機密之識別方式（書面標示 / 口頭限期書面追認）」 |
| `confidentiality` | `survival_period` (specific years or perpetual) | all | yellow | 「保密期限 N 年 vs 永久」 |
| `confidentiality` | `residual_knowledge_carveout` | NDA / MSA | yellow | 「殘餘知識（員工腦中記憶概念）排除條款」 |
| `data-protection-dpa` | `sub_processor_consent` (list / opt-in / categories) | DPA / SaaS / 服務 | yellow | 「子處理者 list + 異議權」 |
| `data-protection-dpa` | `breach_notification_window` (24/48/72 hr) | all DPA | red | 「個資外洩通報 X 小時」 |
| `data-protection-dpa` | `proof_of_deletion` (certificate / log) | DPA / SaaS / 委任 | yellow | 「銷毀證明文件 / 銷毀 log」 |
| `data-protection-dpa` | `audit_rights` (cadence / cost / scope) | DPA | yellow | 「1×/年 + 30 日 notice + 重大不一致時 cost-shift」 |
| `limitation-of-liability` | `cap_amount` (fixed / multiplier / hybrid) | SaaS / MSA / 服務 | red | 「Cap = X TWD or N× annual fee」 |
| `limitation-of-liability` | `carve_outs` (gross negligence / IP / 個資 / 機密) | SaaS / MSA / 服務 | red | 「Carve-out 列舉」 |
| `indemnification` | `procedural_mechanics` (notice / control / settlement consent) | all | yellow | 「7-day notice + control rights + settlement consent」 |
| `indemnification` | `scope` (claims covered + carve-outs) | all | yellow | 「列舉受 indemnify 之 claim type」 |
| `termination-and-survival` | `cure_period_days` (specific number) | all | yellow | 「Material breach cure period N 日」 |
| `termination-and-survival` | `wind_down_mechanics` (transition assistance / data return / refund) | SaaS / MSA / 服務 / 委任 | yellow | 「Wind-down: data return + pro-rata refund + transition period」 |
| `termination-and-survival` | `survival_clauses_listed` (which clauses survive) | all | yellow | 「條列終止後仍存續之條款編號」 |
| `auto-renewal` | `notice_window_days` (specific number) | all with renewal | red | 「Notice window N 日（建議 60-90）」 |
| `auto-renewal` | `price_change_formula` (cap / index / ceiling) | all with renewal | yellow | 「續約調價公式 / 上限」 |
| `ip-ownership-assignment` | `work_product_definition` | SaaS / 服務委任 / 開發 | yellow | 「Work product 定義 + IP 歸屬條款」 |
| `ip-ownership-assignment` | `infringement_warranty` | SaaS / MSA | red | 「乙方保證所提供 IP 不侵害第三方權利」 |
| `assignment-change-of-control` | `consent_required` | all | yellow | 「轉讓 / 換手控制權需 prior written consent」 |
| `notices` | `delivery_method` (email / 掛號 / 雙軌) | all | green | 「Notice 送達方式（email + 掛號雙軌）」 |
| `payment` | `late_payment_remedy` (interest / suspend service) | all paid | yellow | 「逾期付款利率 / 停止服務權」 |

**Source dispatch**: a Python helper `vagueness_scan` could codify this table (Phase 1.6+); v0.3.1 ships the table as protocol reference for LLM-driven scan.

**Stance-asymmetry interaction**: vagueness gaps go through `L7 Step 1.5 (stance-asymmetry pass)` like any other finding. If the missing sub-mechanism *protects* our stance (e.g. counterparty has no audit right against us when stance=ours), the L6 vagueness gap downgrades to green / strategic-note at L7.

### Step 2.5 — Dedup overlap pass (v0.3.2+)

L6 can surface the same underlying concern through two sub-checks:
- Sub-check 3 (missing-items) flags `missing_expected_clause: residual-knowledge`
- Sub-check 4 (vagueness) flags `vague_sub_mechanism` for `confidentiality.residual_knowledge_carveout`
- L7 main loop also generates a `confidentiality` finding whose discussion already covers the same gap

v0.3.0 dogfood NDA run emitted both finding #1 (confidentiality scope including residual-knowledge analysis) AND finding #6 (residual-knowledge gap as separate item). User read 2 findings as 2 problems when it's really 1.

#### Dedup rule

Before passing gaps to Step 3 (emit findings), apply:

```
For each gap of type missing_expected_clause OR vague_sub_mechanism:
  let topic = gap.clause_id (e.g. "residual-knowledge")
  let parent = find playbook fallback / user entry whose body substantively covers topic

  if parent and parent will generate a finding in L7 main loop:
    gap.subsumed_by = parent.clause_id
    gap.severity = (gap.severity, parent.severity).max()
    DO NOT emit a separate finding for this gap
    instead, ensure parent finding's discussion_zh_tw mentions this gap topic
       with cross-reference: "本條 finding 已包含 <topic> gap，
                              詳見 redline §X.Y / playbook entry"

  else:
    emit gap as a standalone finding (current behavior)
```

#### Overlap detection heuristics

Two findings overlap if ALL of:
- Same `clause_id` (e.g. both belong to `confidentiality`)
- OR `gap.clause_id ∈ parent.body.discussion_topics[]` (the parent baseline explicitly discusses the gap topic in its body / preferred / fallback sections)
- AND the gap's `suggested_remediation` is a subset of the parent finding's recommended redline

This avoids over-merging (a true secondary gap that just happens to live near a flagged clause should still emit separately).

#### Examples

```
NDA contract:
  L6 sub-check 3 surfaces: missing_expected_clause: residual-knowledge
  L7 main loop generates: confidentiality finding (red, walk-away, includes "Residual knowledge clause 完全排除" trigger)
  → Dedup: residual-knowledge gap SUBSUMED by confidentiality finding
  → Output: 1 finding (confidentiality), not 2

SaaS contract:
  L6 sub-check 4 surfaces: vague_sub_mechanism: data-protection-dpa.proof_of_deletion
  L7 main loop generates: data-protection-dpa finding (red, multiple sub-mechanism gaps including proof_of_deletion)
  → Dedup: proof_of_deletion gap SUBSUMED into DPA finding
  → Output: 1 DPA finding listing all sub-mechanism gaps in one discussion
```

### Step 3 — Emit findings

For each gap accumulated (after Step 2.5 dedup):

```yaml
clause_id: <inferred or "structural">
source_type: advisory                # gap detection isn't playbook comparison
severity:
  - if missing_expected_clause is tier-1 priority: red
  - if undefined_term high-stakes (e.g. "Confidential Information" undefined): yellow
  - if if-breach-branch on minor obligation: yellow
  - else: green
subtype: <type from gap>
contract_text: <relevant excerpt or "not present">
playbook_trace:
  matched_entry_path: null         # gap findings have no matched entry; advisory
  cycle_detected: <number>
remediation: <from gap>
```

These findings go to `issues.md` at Tier 1 priority (visible at top) when severity is `red`.

### Step 4 — Output cycle stats

Internal pipeline state:

```yaml
cycle_check:
  total_cycles: <number, ≥ 2>
  total_gaps_found: <count>
  gaps_by_type:
    if_breach_branch_missing: <count>
    undefined_term: <count>
    missing_expected_clause: <count>
    vague_sub_mechanism: <count>     # v0.3.1+
  termination_condition: gaps_zero_at_cycle_<N>
  missing_clauses_by_priority:
    tier_1: <count>
    tier_2: <count>
    tier_3: <count>
  vague_sub_mechanisms_by_dimension:  # v0.3.1+
    <dimension_name>: <count>
```

Pass to L6.5 (if jurisdiction == TW) or directly to L7.

---

## Output contract

```
✅ L6 complete.
   Cycles run: <number>
   Gaps found: <total>
   Termination reason: gaps==0 AND cycle>=2 / max_cycles_hit
   Pass to: L6.5 (TW) / L7 (non-TW)
```

---

## Edge cases

- **Cycle runaway** (gaps keep appearing): hard-cap at 5 cycles. If still finding new gaps after 5, emit `pipeline_warning: cycle_did_not_converge` to `self-grade.md` failed_criteria so the user sees the rubric flag.
- **No obligations defined** (rare but possible — e.g. an MOU): skip the if-breach-branch sub-check.
- **Mode == "nda"**: still run L6 — NDAs benefit from missing-items detection (carve-outs / return-or-destroy / remedies are often missing).
- **L1's expected list has playbook-only entries not in bundled** (user has a custom clause): if missing, the gap is still flagged but with severity yellow (not red) — the user's playbook says they care, but the lack of a bundled expectation means the omission may be deliberate.
- **Definitions referenced before they appear in the doc** (forward reference): not a gap — Capitalised Term used in §1.2 may be defined in §3 Definitions. Only flag when the term is **never** defined.
- **Same term defined twice with different meanings** (catastrophic): emit a high-severity finding `subtype: term_redefinition` even without it being in the standard gap types. This is rare but breaks the contract's coherence.
