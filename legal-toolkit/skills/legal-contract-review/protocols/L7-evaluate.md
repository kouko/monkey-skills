# L7 — Evaluate against playbook (the integration layer)

**Layer**: L7 (always runs; final substantive layer before self-grade)
**Reads**: playbook **frontmatter + body** (matched entries only)
**The core of the skill** — every other layer feeds inputs to L7

---

## Purpose

L7 is where the contract meets the playbook. For each clause identified in L3 / L5:

1. Find the matching playbook entry (user playbook → bundled fallback → advisory)
2. ABAC pre-filter to the single matched variant (rule-based, no LLM)
3. Check for `escalate_to` placeholder; emit warning if found
4. LLM-judge walk-away triggers
5. LLM-compare contract clause to `preferred` / `fallback` body prose
6. Emit colored finding (🟢 / 🟡 / 🔴) with full traceability

The output of L7 is the bulk of `issues.md` findings and the source for `redline.md` / `escalation.md` / `memo-legal.md`.

---

## Pipeline

For each clause (iterating in **L5 priority order**, Tier 1 first):

### Step 1 — IDX_LOOKUP (user playbook)

```
playbook_index = scan(legal-playbook/ in working folder OR bundled fallback)

if clause.id ∈ playbook_index AND playbook source is user_playbook:
  → load user entry → proceed to Step 2 (VTYPE)
else:
  → proceed to Step 1b (BUNDLED_LOOKUP)
```

### Step 1b — BUNDLED_LOOKUP (cold-start fallback)

```
if clause.id ∈ bundled_fallback_index (4 clauses: confidentiality / governing-law / auto-renewal / termination-and-survival):
  → load bundled fallback entry
  → tag source_type = bundled_fallback
  → set banner = "⚠️ 使用 bundled fallback baseline — 建議跑 legal-playbook-author 客製化你公司的紅線"
  → proceed to Step 2 (VTYPE)
else:
  → proceed to Step 1c (ADVISORY)
```

### Step 1c — ADVISORY mode

No matching entry. Emit finding:

```yaml
clause_id: <inferred>
source_type: advisory
severity: yellow (default for advisory; bump to red only if clause is high-risk subject-matter)
subtype: no_playbook_entry
contract_text: "<verbatim>"
recommendation: "建議呼叫 /legal-playbook-author extend <clause-id> 為這條 clause 建立 your company's position"
```

Skip Steps 2-6 for this clause; advance to next.

### Step 2 — VTYPE check (flat vs variant-folder)

```
if entry.has_variants == true (variant-folder layout):
  → proceed to Step 3 (ABAC pre-filter)
else (flat layout):
  → skip Step 3; entry is the working entry; proceed to Step 4
```

### Step 3 — ABAC pre-filter (variant-folder only)

**v0.2.0+ (Phase 1.5)**: invoke the dedicated Python implementation:

```bash
uv run <plugin>/skills/legal-contract-review/scripts/abac_filter.py \
    --deal-context '<json>' \
    --variants '@<path-to-variants-json>'
```

The script returns `{ outcome, chosen_variant_id, matched_count, matched_variant_ids }`
where `outcome ∈ {single, advisory, multi}`. Use `chosen_variant_id`
as the matched variant for Step 4.

Equivalent in-LLM logic (used as a fallback if scripts aren't
available in the host runtime):

```
match = True
for gate_key, gate_value in variant.gates.items():
  if not check_gate(gate_value, deal_context[gate_key]):
    match = False
    break

if match:
  matched_variants.append(variant)
```

`check_gate` semantics:

- Numeric: `{lt, gte, lte, gt, eq}` against `deal_context[key]`
- Enum: `{any_of: [...]}` or `{eq: value}` against `deal_context[key]`
- Always-true: gate == `any` or key missing from deal_context AND gate has `any_match` rule

After matching:

```
if len(matched_variants) == 0:
  → emit ADVISORY-style finding "deal_context 不符合任何 variant 範圍"
  → suggest playbook-author may need a new variant for this deal shape
  → advance to next clause

if len(matched_variants) == 1:
  working_entry = matched_variants[0]
  → proceed to Step 4

if len(matched_variants) > 1:
  log_warning("multi-match: ABAC gates may overlap — Phase 1.5 detect_conflicts.py will catch")
  working_entry = matched_variants[0]   # take first; deterministic
  → proceed to Step 4
```

### Step 4 — `escalate_to` placeholder detection

```
if working_entry.escalate_to.startswith("[請編輯"):
  emit warning to runtime console
  add callout to escalation.md (prepended for this clause's escalation row):
    "⚠️ 此 finding 使用未客製化的 bundled fallback。
     建議：跑 `legal-playbook-author revise <clause-id>` 把 escalate_to 改成
     你公司的實際角色（法務主管 / GC / 部門主管 / 老闆）"
  set finding.flags.escalate_to_is_placeholder = true
  (pipeline continues — do NOT abort)
```

### Step 5 — Walk-away trigger LLM judge

LLM-judge the contract clause against `working_entry.walk_away_triggers` (frontmatter array):

Prompt shape (English):

```
You are evaluating a contract clause against walk-away triggers
encoded in the user's negotiation playbook.

Contract clause (verbatim):
<contract clause text>

Walk-away triggers (any one of these, if matched, means this is
NOT negotiable — escalate, don't fallback):
- <trigger 1>
- <trigger 2>
- ...

Question: Does the contract clause match any of the walk-away
triggers? Answer with the trigger that matched, or "none" if no
match. Be conservative — only call a match when the contract
clause's substance clearly implements the trigger condition.
Answer format: { "matched_trigger": "<exact text of trigger>" | "none", "confidence": 0.0-1.0 }
```

```
if matched_trigger != "none":
  → walk-away path:
    finding.walk_away_triggered = true
    finding.severity = red
    finding.escalate_to = working_entry.escalate_to     # USE FRONTMATTER VERBATIM; do NOT let LLM rewrite
    finding.matched_walk_away = [matched_trigger]
    add escalation entry to escalation.md
    (skip Step 6 LLM body comparison; the answer is already "walk")
  → advance to next clause
```

### Step 6 — LLM body comparison (non-walk path)

If no walk-away triggered, compare the contract clause to the `## 偏好立場` / `## Fallback N` body sections.

Prompt shape (English):

```
You are comparing a contract clause to a negotiation playbook's
preferred / fallback positions.

Contract clause (verbatim):
<contract clause text>

Playbook preferred position:
<entry.body.preferred>

Playbook fallback 1:
<entry.body.fallback_1>

Playbook fallback 2 (if present):
<entry.body.fallback_2>

Question: Where does the contract clause fall on this spectrum?
- ≥ preferred: contract clause meets or exceeds our preferred position (🟢 green)
- between preferred and fallback_1: contract is acceptable, slight movement from preferred (🟢 green)
- ≈ fallback_1: contract matches our first fallback (🟡 yellow)
- between fallback_1 and fallback_2: contract is past first fallback, approaching last (🟡 yellow)
- ≈ fallback_2 or worse: contract is past our acceptable fallback (🔴 red)

Answer format: {
  "color": "green" | "yellow" | "red",
  "fallback_level_used": "preferred" | "fallback-1" | "fallback-2" | "worse",
  "confidence": 0.0-1.0,
  "reasoning": "<1-2 sentence explanation>"
}
```

### Step 7 — Apply confidence threshold

```
if llm_confidence < 0.7:
  → fall back to working_entry.risk_default
  → finding.severity = working_entry.risk_default
  → finding.flags.low_confidence = true
  → trigger Escalation Override (low confidence is a trigger condition)
else:
  → finding.severity = color from LLM
```

### Step 8 — Collect finding

```yaml
clause_id: <id>
variant_id: <id or null>
source_type: <user_playbook / bundled_fallback>
severity: <green / yellow / red>
walk_away_triggered: <bool>
business_issues: <from L4>
playbook_trace:
  matched_entry_path: legal-playbook/<id>.md or fallback bundled path
  matched_walk_away: <list or empty>
  matched_fallback_level: <preferred / fallback-1 / fallback-2 / worse>
  external_share_strip_id: <set later if --external-share>
banner: <from cold-start fallback step, if applicable>
contract_text: <verbatim>
summary_zh_tw: <LLM-generated zh-TW summary of this finding>
flags:
  escalate_to_is_placeholder: <bool>
  low_confidence: <bool>
```

Append to `issues.md.findings` array. If `severity == red` OR `walk_away_triggered` OR `low_confidence`, also add to `escalation.md.escalations` and trigger Escalation Override prepend on issues.md / memo-legal.md / escalation.md.

### Step 9 — Emit redline (if mode allows)

If `mode ∈ {review, redline}` and `severity ∈ {yellow, red}`:

- Pull `## 替代條款文字` from playbook body (if present) → use as `proposed_text`, `proposed_text_source: playbook_body`
- Otherwise, LLM-generate substitute text grounded in the `preferred` position → `proposed_text_source: llm_generated`
- Append to `redline.md.redlines`

---

## Output contract

```
✅ L7 complete.
   Clauses evaluated: <count>
   By source: user_playbook=<N> / bundled_fallback=<M> / advisory=<K>
   By severity: green=<N> / yellow=<N> / red=<N>
   Walk-aways triggered: <count>
   Low-confidence fallbacks: <count>
   Placeholder warnings: <count>
   Pass to: self-grade
```

---

## Edge cases

- **Multiple matching variants** (ABAC gates overlap): take first; log warning. Phase 1.5 `detect_conflicts.py` enforces gate non-overlap at playbook-author validate time.
- **LLM returns invalid JSON**: re-prompt once with stricter format hint; if still invalid, treat as low-confidence (use risk_default).
- **Contract clause is missing entirely** (the expected clause is not in contract): not L7's job — L6 detected this as `missing_expected_clause`. L7 doesn't iterate clauses that don't exist.
- **Walk-away triggered + LLM body comparison both run** (shouldn't happen — walk path skips body): treat as bug; emit `pipeline_warning` to self-grade.
- **mode == "redline"**: Step 9 emphasis on substitute text generation; other outputs simplified.
- **mode == "nda"**: L2-L3 skipped → L7 reads clauses directly from contract text + bundled NDA template. Same evaluation logic, simpler input shape.
- **--external-share flag passed**: after L7 emits findings, a post-processing pass strips `playbook_trace.matched_entry_path` from issues.md / memo-legal.md / escalation.md (replaces with "依本公司紅線政策"). Override red banner is **never** stripped.
- **Phase 1.5 status**: `scripts/abac_filter.py` is the canonical implementation as of v0.2.0. The inline-LLM rules above are the fallback for hosts without script execution. Importable as `from abac_filter import match_variant`.
