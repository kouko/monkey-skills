# L6 — Cycle / cross-reference (universal layer)

**Layer**: L6 (always runs; bounded loop until convergence)
**Reads**: playbook index (for missing-items flag)
**Loop**: continues until `gaps == 0 AND cycle >= 2`

---

## Purpose

L6 is the **consistency** layer. It iterates over the categorised + tiered contract structure and asks: do all the parts cohere? Three sub-checks run in each cycle, bounded by a "no new gaps + at least 2 cycles" termination condition.

1. **If-breach branch check** — for every Obligation (Stark concept) the contract defines, is there a corresponding consequence-on-breach? (If not: gap.)
2. **Definitions cross-read** — every term used elsewhere in the contract must trace back to either the Definitions section or an inline definition. (If not: gap.)
3. **Missing-items vs L1 expectations** — for every expected clause from L1, is it present somewhere in the contract? (If not: high-weight finding.)

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

  gaps.extend(new_gaps_this_cycle)
  no_new_gaps = len(new_gaps_this_cycle) == 0

  exit condition: cycle >= 2 AND no_new_gaps
while not exit_condition
```

### Step 3 — Emit findings

For each gap accumulated:

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
  termination_condition: gaps_zero_at_cycle_<N>
  missing_clauses_by_priority:
    tier_1: <count>
    tier_2: <count>
    tier_3: <count>
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
