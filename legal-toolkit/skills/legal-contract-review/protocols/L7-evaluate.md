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

### Step 1.5 — Stance-asymmetry pass (v0.3.1+)

**Run this BEFORE Step 2 (VTYPE) for EVERY clause that passed Step 1a-1c**, regardless of source_type.

Toolkit playbooks (bundled fallback + most user playbooks) are written from a **neutral two-sided perspective** — "best-practice default" wording assumes the user wants balanced provisions. When `stance` is `ours` and the contract is already asymmetric in our favor (e.g. the counterparty bears uncapped liability, or all 個資 obligations sit on the counterparty), naïvely applying the playbook flags clauses as "risk" *because they're missing from neutral best-practice* — and proposes redlines that **erode the favorable position we already have**.

#### Decision

For each finding the pipeline is about to emit, ask:

```
Q1: Is the underlying logic of this finding "the contract is missing
    a neutral best-practice clause" (LoL, mutual indemnity, balanced
    cure period, symmetric notice, etc.)?

  ├── no → proceed to Step 2 normally
  └── yes → ask Q2

Q2: With stance = ours, does the absence of this clause EXPOSE us
    or PROTECT us?

  ├── EXPOSE (concrete: dollar / month / customer / regulatory exposure
  │           we have to absorb because the clause is absent)
  │       → proceed to Step 2 normally; finding stays as-is
  │
  └── PROTECT (the absence means the counterparty bears risk or has
              no leverage; OR the "balanced" clause would equalise
              a position currently favorable to us)
       → DOWNGRADE finding:
         - severity: green
         - subtype: strategic_note  (NOT a risk finding)
         - presentation:
             • issues.md: list under "✓ 對我方有利 / strategic note"
               section (NOT main findings table)
             • redline.md: split the proposed text:
               · `proposed_text_send_now`: empty (don't offer)
               · `proposed_text_internal_fallback`: the original
                 substitute text, marked "INTERNAL — if 對方 raises this"
             • memo-business.md: include in "✓ favorable position"
               box, not Top-3 business impacts
             • escalation.md: NOT included (this is not a risk)
         - flag: stance_asymmetry_downgrade = true
         - playbook_trace.matched_entry_path still recorded
```

#### Quantifiable downside test

A "concrete quantifiable downside" requires ONE of:
- Specific currency amount (TWD / USD / EUR) of potential exposure
- Specific time-bound impact (e.g. "if 乙方 takes 90 days to respond, our 店家 churn ≈ X%")
- Specific customer count / regulatory penalty (e.g. "PDPC fine 5-50萬 if §20-1 不履行")
- Specific clause-cascade (e.g. "§9 違約金 + §四 indemnity stack on a single 員工 失誤")

If you can only argue "industry best practice says X" without one of the above, the downside is NOT concrete; downgrade.

#### Examples (from v0.3.0 dogfood)

```
Contract: SaaS reseller, stance=甲方
Finding candidate: "LoL clause absent → flag red, propose 2× annual revenue cap"
- Q1: yes (best-practice default missing)
- Q2: PROTECT (乙方 currently has uncapped exposure that we benefit from)
- Action: downgrade to green / strategic_note
- proposed_text_send_now: empty
- proposed_text_internal_fallback: "if 乙方 raises LoL at renewal, our floor = 12-month revenue × 1×"

Contract: SaaS reseller, stance=甲方
Finding candidate: "Auto-renewal 1-month notice → flag yellow"
- Q1: yes (best-practice default = 60-90 day notice)
- Q2: EXPOSE (we get locked into 2-year cycles with only 1-month escape;
              dollar exposure = 2 years × monthly minimum × 50% migration cost)
- Action: keep yellow finding; proceed normally
```

#### Output contract

The pipeline must record per-clause:

```yaml
stance_asymmetry_check:
  ran: true
  q1_neutral_best_practice_missing: <bool>
  q2_decision: <expose / protect / not_applicable>
  downgrade_applied: <bool>
  quantifiable_downside: <bool>
```

This is consumed by `self_grade.py` semantic-tier criteria (planned ANS-21 in v0.3.2+) and by `requesting-code-review` audit.

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

If `mode ∈ {review, redline}` and `severity ∈ {yellow, red}` and `stance_asymmetry_check.downgrade_applied != true`:

- Pull `## 替代條款文字` from playbook body (if present) → use as `proposed_text`, `proposed_text_source: playbook_body`
- Otherwise, LLM-generate substitute text grounded in the `preferred` position → `proposed_text_source: llm_generated`
- Append to `redline.md.redlines`

#### Step 9.1 — Editorial-parenthetical filter (v0.3.1+)

Before emitting any `proposed_text` substitute clause, scrub the body for editorial / amendment-history parentheticals that DO NOT belong inside operative contract text. Examples to STRIP or relocate to memo-legal.md only:

| ❌ DON'T put in `proposed_text` | ✅ DO put in `memo-legal.md` analysis |
|---|---|
| `(含 §20-1 安全維護義務，原 §27 已於 2025-11-11 修正後條次變更)` | "本條引用個資法 §20-1（原 §27 於 2025-11 修正後條次變更）" |
| `(本條較原條款增加 cure period 5 天)` | "本提案較原條款增加 cure period 5 天" |
| `(WorldCC 2024 benchmark)` | "依 WorldCC 2024 benchmark..." |
| `(暫定金額，後續協商)` | "提案金額 NT$X（協商空間 NT$Y-Z）" |

Commercial agreements do not carry amendment-history annotations in operative text. If the proposed substitute clause body contains parentheticals matching pattern `(含|原|較|依|暫定|備註|參|note|amended|previously|previous)\s*§|.*\s+(已於|修正後|benchmark|fallback)` → STRIP from `proposed_text`, optionally move equivalent prose to `redline.md.rationale_zh_tw` OR `memo-legal.md` analysis section.

#### Step 9.2 — Stance-asymmetry redline split (v0.3.1+)

If `stance_asymmetry_check.downgrade_applied == true`, the redline emit changes:

- `proposed_text_send_now`: empty string (or omit field)
- `proposed_text_internal_fallback`: the substitute text, with rationale framed as "if 對方 raises X at renewal, our floor is Y"
- `redline.md` rendering: this finding appears in a separate **"## 內部 fallback 預案（不主動提案）"** section, BELOW the main `## 主動 redline 提案` section
- `redline.md.send_now_table` lists only main-section redlines (these are what you copy-paste into the counter-proposal email)

### Step 9.3 — Citation applicability gate (v0.3.1+)

Before emitting any statute citation to `memo-legal.md` `citations[]`, the LLM MUST internally verify **applicability** (not just article-number existence):

```
For each citation candidate, answer:

  Q: Does this statute / article actually apply to the fact pattern
     of THIS contract clause?

  Common applicability traps (from v0.3.0 dogfood):
  - 民法 §247-1: applies ONLY to 定型化契約 (standard-form / adhesion).
    A 1-on-1 negotiated B2B contract does NOT qualify. If you cite
    §247-1, the memo MUST state whether the contract IS adhesion or
    NOT, and what the citation's scope is.
  - 公平交易法 §25: requires market-impact element (顯失公平 must
    affect 交易秩序). Single bilateral clause without market-impact
    framing is too thin.
  - 民法 §110: protects bona-fide THIRD PARTY against unauthorised
    agent (not principal seeking reimbursement from agent). For
    "principal claim-back" cite §107 + 不當得利 §179 instead.
  - 營業秘密法 §13-1: this is the CRIMINAL liability article. For
    CIVIL trade-secret protection cite §11 (injunctive relief) or
    §12 (damages); for the survival-after-termination point cite
    §§2, 10, 11.
  - 個資法 §27: DELETED 2025-11-11. For 安全維護義務 of 非公務機關
    use §20-1.

  If the citation passes applicability but is borderline:
  → record `applicability_caveat` field on the citation:
    "本條主要規範 X 場景；本合約屬 Y 場景，類推適用空間有限"
  → still emit citation, but memo-legal.md analysis must include the caveat
```

#### Step 9.4 — Headline rule for memo-business (v0.3.1+)

When emitting `memo-business.md.top_3_business_impacts`:

```
Pick the 3 findings that have ALL THREE properties:
  1. severity ∈ {yellow, red}
  2. concrete quantifiable downside (per Step 1.5 definition)
  3. actionable in next 30/60/90 days (not "monitor at renewal")

DO NOT include findings whose only argument is "best-practice
default is missing" — these went through Step 1.5 downgrade or
should be filtered out at headline time.

DO NOT order by playbook structure (confidentiality / governing-law / ...)
— order by deal-priority weight for THIS contract.
```

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
