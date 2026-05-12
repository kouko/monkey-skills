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

The output of L7 is the bulk of `findings.json#findings[]` and the source for `legal.md` sections (§議題清單 / §升級簽核 / §法律分析 / §主動 Redline 提案 / §內部 Fallback 預案 / §對我方有利) + `business.md §主要 Redline 重點`. v0.3.4+ (Phase 1.8) consolidates the former 5 .md (issues/redline/memo-legal/memo-business/escalation) into 2 audience-shaped .md (legal/business).

---

## Pipeline

### Step 0 — Asset Identification Pass (v0.3.2+, runs BEFORE per-clause iteration)

Toolkit playbooks are designed to detect **risks** (missing or weak clauses). When `stance: ours` and the contract contains clauses that **advantage** the stance-holder, the playbook-based pipeline doesn't natively surface them — they generate no finding and become invisible. v0.3.0 dogfood SaaS run missed `§2.3 5-day silence-consent` / `§1.6 甲方單方訂價` / `§4.3 甲方單方退款決定` / `§3.3 末段 乙方 post-termination service obligation` exactly this way.

#### When to run

`stance == "ours"` only. Skip for `neutral` (no asymmetric advantage to identify) or `theirs` (asset-identification belongs to the other party).

#### Decision

Iterate over the L2-anatomy clause list (full contract clause inventory). For each clause that is NOT going to generate a yellow/red finding in the main loop, ask:

```
Q: Given stance=ours, does this clause's SUBSTANCE advantage us?

Common asset patterns:
- Short / asymmetric timing windows favoring us
  (silence-consent, fast objection deadlines, short notice WE require from 對方)
- Unilateral decision rights granted to us
  (pricing / refund / scope / SLA acceptance / acceptance criteria)
- Counterparty-borne liability / indemnity / regulatory obligation
  (個資, breach 連環責任, third-party indemnity, IP infringement warranty when given to us)
- Counterparty's post-termination service / transition obligation to us
  (wind-down maintenance, data return, transition assistance)
- Walk-away rights we hold unilaterally (termination for convenience for us only)
- Restrictive covenants binding 對方 not us (non-compete, non-solicit, exclusivity)
- Audit / inspection / information rights we hold over 對方
- Pricing protection (cap on 對方's price increase, floor on revenue share to us)

If yes:
  → add entry to `favorable_position_notes[]`:
    clause_id: <inferred from L3 or L5 categorisation>
    note_zh_tw: brief explanation framed as "我方有利 — <substance>";
                include "renewal-time floor" hint when applicable
                (e.g. "若對方續約挑戰，內部 floor: 10 日（vs 現 5 日）")
  → DO NOT emit a finding for this clause in the main loop
  → IF the clause also has a gap that warrants a finding, emit both:
    the gap finding (with severity per usual rules) AND the asset note;
    finding.discussion_zh_tw cross-references the favorable_position_note
```

#### Dual-nature clauses

A single clause section can carry BOTH a gap AND an asset (the SaaS run's `§3.3` ended with a 乙方 obligation to maintain paid-customer service post-termination — an asset — while the rest of §3 had wind-down vagueness — a gap). Treat them separately:

```
If clause has both gap (sub-mechanism vague / missing carve-out) AND asset (favorable substance):
  - Emit gap finding at yellow severity per L6 sub-check 4 / playbook
  - Also emit favorable_position_note with same clause_id
  - finding.discussion_zh_tw includes: "本條同時具有 favorable 元素，見 favorable_position_notes.<clause_id>，
     提案 redline 時不可一併重寫該條 — 改用 §X.Y 子項目補強"
```

#### Output contract

`findings.json.favorable_position_notes[]` populated per output-schema-findings.json + output-schema-memo-business.json.

### Step 1 — IDX_LOOKUP (user playbook)

Iterating in **L5 priority order**, Tier 1 first. For each clause:

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
             • legal.md §對我方有利 (Favorable Positions) section
               (NOT under §議題清單 main findings table)
             • legal.md §內部 Fallback 預案 section: the substitute text,
               marked "INTERNAL — if 對方 raises this"
             • redline split (in findings.json#redlines[]):
               · proposed_text_send_now: empty (don't offer)
               · proposed_text_internal_fallback: the substitute text
             • business.md §對我方有利 section (NOT in Top-3)
             • legal.md §升級簽核 section: NOT included (this is not a risk)
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
  add callout to legal.md §升級簽核 (prepended for this clause's escalation row):
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
    add escalation entry to findings.json#escalations[] (rendered in legal.md §升級簽核)
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

Append to `findings.json#findings[]` (rendered in `legal.md §議題清單`). If `severity == red` OR `walk_away_triggered` OR `low_confidence`, also add to `findings.json#escalations[]` (rendered in `legal.md §升級簽核`) and trigger Escalation Override prepend on `legal.md` head **only** (v0.3.4 Phase 1.8 banner scope; business.md never carries the banner).

### Step 9 — Emit redline (if mode allows)

If `mode ∈ {review, redline}` and `severity ∈ {yellow, red}` and `stance_asymmetry_check.downgrade_applied != true`:

- Pull `## 替代條款文字` from playbook body (if present) → use as `proposed_text`, `proposed_text_source: playbook_body`
- Otherwise, LLM-generate substitute text grounded in the `preferred` position → `proposed_text_source: llm_generated`
- Append to `findings.json#redlines[]` (rendered in `legal.md §主動 Redline 提案` + `business.md §主要 Redline 重點`)

#### Step 9.1 — Editorial-parenthetical filter (v0.3.1+)

Before emitting any `proposed_text` substitute clause, scrub the body for editorial / amendment-history parentheticals that DO NOT belong inside operative contract text. Examples to STRIP or relocate to `legal.md §法律分析` only:

| ❌ DON'T put in `proposed_text` | ✅ DO put in `legal.md §法律分析` |
|---|---|
| `(含 §20-1 安全維護義務，原 §27 已於 2025-11-11 修正後條次變更)` | "本條引用個資法 §20-1（原 §27 於 2025-11 修正後條次變更）" |
| `(本條較原條款增加 cure period 5 天)` | "本提案較原條款增加 cure period 5 天" |
| `(WorldCC 2024 benchmark)` | "依 WorldCC 2024 benchmark..." |
| `(暫定金額，後續協商)` | "提案金額 NT$X（協商空間 NT$Y-Z）" |

Commercial agreements do not carry amendment-history annotations in operative text. If the proposed substitute clause body contains parentheticals matching pattern `(含|原|較|依|暫定|備註|參|note|amended|previously|previous)\s*§|.*\s+(已於|修正後|benchmark|fallback)` → STRIP from `proposed_text`, optionally move equivalent prose to `findings.json#redlines[].rationale_zh_tw` OR `legal.md §法律分析` section.

#### Step 9.2 — Stance-asymmetry redline split (v0.3.1+)

If `stance_asymmetry_check.downgrade_applied == true`, the redline emit changes:

- `proposed_text_send_now`: empty string (or omit field)
- `proposed_text_internal_fallback`: the substitute text, with rationale framed as "if 對方 raises X at renewal, our floor is Y"
- `legal.md` rendering: this finding appears in **§內部 Fallback 預案（不主動提案）** section, BELOW **§主動 Redline 提案**.
- The `§主動 Redline 提案` section lists only `proposed_text_send_now` redlines (these are what you copy-paste into the counter-proposal email; clearly grep-able section header for extraction).
- `business.md §主要 Redline 重點` also only shows `proposed_text_send_now` redlines (with 條文 + why); internal_fallback never surfaces to business audience.

#### Step 9.3.0 — Soft case-citation rule (v0.3.2+)

Before emitting any `case` type citation (e.g. `"最高法院 X 年度 Y 字第 N 號"`):

```
Q: Have you independently verified this case number in THIS session?

  Verification = ONE of:
    - WebFetch-confirmed via https://judgment.judicial.gov.tw in this session
    - Listed in assets/statute-articles.json#cases_verified[] with verified_at within 365 days
    - Pulled from a user-supplied playbook entry tagged `case_verified_at: <date>`

  ├── yes → emit the case citation with citations[].verified=true and url field set
  └── no  → DO NOT emit "X 年度 Y 字第 N 號" pattern

Replace with one of the acceptable softer formulations:
  - "近年實務趨勢 / 法院見解" (no specific case number)
  - "司法院判決系統有多則相關案件" (general pointer)
  - "依 <statute> + 學者通說" (cite statute + academic commentary instead)
  - "[案號待查] — 引用前請以 https://judgment.judicial.gov.tw 檢索" (acceptable in DRAFT memos only; STRIP before sending)
```

#### Rationale

v0.3.0 dogfood:
- NDA run: bundled fallback `baseline-fallback-confidentiality.md` contained 「智慧財產法院 102 年度民營訴字第 6 號」which propagated into memo-legal as hedged citation "如該案號有效".
- SaaS run: `business.md` (v0.3.3 was memo-business.md) emitted「最高法院 113 年度台上字第 1244 號等趨勢」which auditor flagged needing verification.

Both are SRC-09 escape routes. The deterministic SRC-04 + blacklist (v0.3.1) catches fabricated sub-articles BUT does NOT catch unverified case numbers. The soft-citation rule above adds a protocol-level gate before SRC-04 ever sees the citation.

### Step 9.3.1 — Statute runtime fetch + verify (v0.3.3+, Phase 1.7)

Before emitting any `statute`-type citation, the LLM runs **cache-then-fetch-then-LLM** workflow:

#### Workflow

```
For each statute citation candidate <statute> <§article>:

1. cache_check (uv run scripts/cache_check.py statute --statute <X> --article <Y>):
   ├── exit 0 (hit)     → load cache entry; carry-through `content` + `verification` + `applicability_caveat`
   ├── exit 2 (expired) → load cache entry as preview, but proceed to fetch (refresh)
   ├── exit 1 (miss)    → proceed to fetch
   └── exit 3 (invalid) → discard cache file; proceed to fetch

2. If fetch needed:
   a. Look up URL from assets/legal-sources.json#statute_sources.<statute>.single_article_url_template
      Construct: https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=<pcode>&flno=<article>
      If <statute> not in legal-sources.json → mark `runtime_verified: false` with reason "statute not in toolkit's source registry" + proceed with caveat
   b. WebFetch the URL (main session; subagent dispatch reserved for v0.3.4+)
   c. Parse the response:
      - title (e.g. "民法第二百四十七條之一")
      - article text (verbatim body)
      - amendments list (date + type + note)
      - last_amended_at (most recent amendment date)
      - exists: True if non-empty result; False if 404 / structurally invalid
      - is_current: True if no recent amendments invalidating; False otherwise
      - deprecated: True if article 已刪除; False otherwise
      - successor: if deprecated, the successor article number (e.g. 個資法 §27 → §20-1)
   d. Write cache file at .legal-toolkit/cache/statutes/<statute>-<article>.json
      conforming to output-schema-citation-cache.json with ttl_days=30
   e. Carry-through `applicability_caveat` from assets/statute-articles.json#applicability_notes[<statute> <§article>] if listed

3. Emit citation in findings.json#citations[] with:
   - citation, type="statute", supports, url (from cache entry)
   - verified: true (cache hit fresh OR fetch ok with verification.exists=true AND verification.deprecated=false)
   - runtime_verified: true OR false (false ⇒ fell back to LLM training-data recall; emit warning callout in memo-legal head)
   - applicability_caveat: from cache or applicability_notes
   - amendment_note: if cache verification.is_current=false OR deprecated=true
```

#### Offline degradation (Q-B locked)

```
If WebFetch fails (timeout / network error / blocked) AND no cache entry exists:
  - Emit citation with runtime_verified: false
  - Add memo-legal "⚠️ Citation not runtime-verified — please cross-check at https://law.moj.gov.tw before relying" callout
  - DO NOT silently substitute LLM training-data recall as if it were verified

If WebFetch fails but cache exists (even expired):
  - Use cache content with runtime_verified: false + cached_at_stale: true
  - Note in memo-legal: "Citation from cache fetched at <date>; refresh failed (<reason>)"
```

#### Fetch budget (Q-E locked)

```
Per /legal-contract-review run:
  - Read assets/legal-sources.json#fetch_budget_defaults.max_unique_citations_per_run (default 10)
  - Override from .legal-toolkit/config.yml#runtime_fetch.max_unique_citations if set
  - Track unique (statute, article) tuples; cap fetches at the limit
  - When budget exhausted, emit remaining citations with runtime_fetch_skipped: true + runtime_verified: false
  - Use cache for already-fetched, soft-degrade for budget-exhausted
```

#### Examples (cache hit / miss / deprecated)

```
Cache hit (民法 §247-1 fetched 5 days ago, TTL 30d):
  → exit 0 hit
  → citation.runtime_verified=true
  → applicability_caveat carried from statute-articles.json: "本條主要規範定型化契約..."

Cache miss (新版條文 first time cited):
  → exit 1 miss
  → WebFetch https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=20-1
  → Parse response → write cache file
  → citation.runtime_verified=true
  → cache file ready for future hits within 30d

Cache expired (民法 §247-1 fetched 35 days ago, TTL 30d):
  → exit 2 expired
  → WebFetch refresh → write cache; check verification.is_current
  → If amendment_date > cached fetched_at, emit "本條 v0.3.x cached 為過去版本，已於 <date> 修正" in memo-legal Carve-outs

Deprecated (個資法 §27 cited after 2025-11-11 amendment):
  → cache check → verification.deprecated=true, successor="個人資料保護法 §20-1"
  → DO NOT EMIT this citation; instead emit successor with note
  → Already caught at SRC-04 blacklist (v0.3.1); this layer is the runtime backstop
```

#### Privacy

- WebFetch sends **only** the statute identifier (e.g. `pcode=B0000001&flno=247-1`) in the URL — **NO contract text** to external servers
- README "Data flow" section documents this clearly

### Step 9.3.2 — Case runtime fetch + verify (v0.3.3+, Phase 1.7)

Same shape as Step 9.3.1 but targets judicial decisions. v0.3.2 Step 9.3.0 soft-citation rule **forbids** emitting "X 年度 Y 字第 N 號" unless verification = cache hit OR in-session WebFetch. Step 9.3.2 is the cache-then-fetch wire-up.

#### Workflow

```
For each case citation candidate <court> <year> <case_type> <number>:

1. uv run scripts/cache_check.py case --court <X> --year <Y> --type <Z> --number <N>
   ├── exit 0 (hit)     → use cache.content + verification
   ├── exit 2 (expired) → preview cache; proceed to fetch
   └── exit 1/3 (miss/invalid) → proceed to fetch

2. uv run scripts/build_citation_url.py case --court <X> --year <Y> --type <Z> --number <N>
   → returns {url, source_host, source_metadata, verified}
   - verified="templated": direct-data URL constructed (judgment.judicial.gov.tw/FJUD/data.aspx?ty=JD&id=<court_code>,<year>,<type>,<number>)
   - verified="search-only": court not in court_codes registry; fall back to search page

3. WebFetch the URL (main session):
   - If verified="templated" + WebFetch returns case content → exists=true,
     parse holding_summary + decision_date
   - If verified="templated" + WebFetch returns empty page → exists=false
     (fabrication signature — strongly correlates with v0.3.2 verification
     subagent finding of 7/8 bundled case fabrications)
   - If verified="search-only" → LLM does keyword search at the search URL;
     if zero hits, exists=false

4. Write cache file at .legal-toolkit/cache/cases/<court>-<year>-<type>-<number>.json
   with ttl_days=7 (cases evolve faster than statutes — supersession,
   variance, later commentary correction)

5. Emit decision:
   - exists=true → emit citation; verified=true; runtime_verified=true;
     holding_summary in citations[].supports field
   - exists=false → DO NOT EMIT this citation; fall back to:
     · "近年實務趨勢" / "依司法院判決系統檢索" (soft formulation)
     · OR drop the case anchor entirely; cite statute + commentary instead
   - WebFetch failed + no cache → emit with runtime_verified=false +
     memo-legal warning callout; do NOT silently substitute LLM recall
```

#### Fabrication detection

A direct-data URL that resolves to an empty / 404-equivalent page is a strong fabrication signal. v0.3.2 verification subagent found 7/8 bundled case-numbers had this signature. Step 9.3.2 catches the same signal at runtime if any LLM-emitted case citation slips past the protocol-level soft-citation gate.

#### Privacy + budget

- WebFetch sends only `court_code + year + case_type + number` in the URL — NO contract text leaves
- Counts toward `fetch_budget_defaults.max_unique_citations_per_run` (default 10)
- Cache TTL 7 days: cases get cited less frequently than statutes; 7d is conservative against supersession / commentary revision

### Step 9.3.3 — Function letter runtime verify (v0.3.3+, Phase 1.7)

Function letters (主管機關 函釋) are the trickiest source — many lack direct permalinks and require keyword search at the agency's site.

#### Workflow

```
For each function letter citation candidate <agency> <letter_id?> + <topic>:

1. uv run scripts/cache_check.py function-letter --agency <X> --letter-id <Y>
   (if letter_id is known)
   ├── exit 0 (hit)     → use cache
   └── miss/expired/invalid → proceed to fetch

2. uv run scripts/build_citation_url.py function-letter --agency <X>
   → search-page URL hint (always "verified=search-only" — function letters
     have no direct permalink standard)

3. WebFetch the search URL + LLM does keyword search:
   - Search by letter_id (if known) → ideal case, direct match
   - Search by 主旨 / 法條 + topic — fuzzy match; LLM judges
   - If LLM finds a matching letter with confidence ≥ 0.7:
     · Extract summary + decision_date + letter_id (if not already known)
     · exists=true
   - If LLM finds nothing OR confidence < 0.7:
     · exists=false (unverifiable, not necessarily fabricated)
     · Soft formulation: "依 <agency> 主管實務" without specific letter_id
4. Write cache file at .legal-toolkit/cache/function_letters/<agency>-<letter_id>.json
   with ttl_days=30 (function letters change slower than cases)

5. Emit decision: same pattern as Step 9.3.2 — verified citation OR
   soft formulation OR runtime_verified=false marker
```

#### Note: 函釋 不容易 verify

Function letters often:
- Live across multiple agency sites that don't share search indices
- Get revoked / superseded without clear notice
- Are referenced informally without 字號 in industry commentary
- May be marked "內部 reference only" without public URL

The protocol accepts higher unverifiable rate for function letters than for statutes / cases. When `exists=false`, prefer soft formulations over fabricating; emit `runtime_verified: false` honestly.

### Step 9.3 — Citation applicability gate (v0.3.1+)

Before emitting any statute citation to `findings.json#citations[]` (rendered in `legal.md §法律分析` citations table), the LLM MUST internally verify **applicability** (not just article-number existence):

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
  → still emit citation, but `legal.md §法律分析` must include the caveat
```

#### Step 9.4 — Headline rule for memo-business (v0.3.1+)

When emitting `findings.json#top_3_business_impacts` (rendered in `business.md §Top 3 風險`):

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

### Step 10 — Render outputs (v0.3.4+ Phase 1.8 consolidation)

After all per-clause evaluation completes and `findings.json` is finalised, render the **3 outputs**:

#### 10.1 — Update findings.json (canonical SoT)

Write `findings.json` to `<cwd>/legal-outputs/<YYYY-MM-DD>-<slug>/findings.json`. This is the machine-readable source; conforms to `assets/output-schema-findings.json`. All structured data lives here including the new `self_grade` block (populated by `scripts/self_grade.py` after rendering).

#### 10.2 — Render legal.md (lawyer-facing)

Write `<cwd>/legal-outputs/<YYYY-MM-DD>-<slug>/legal.md` with sections in this order:

```
# 法務審查報告 — <contract name>

> [!danger] [Override banner if override_triggered]   ← prepended ONLY when triggered

## 議題清單（Issues）
| # | clause_id | severity | business_issues | summary_zh_tw |
| ... | ... | 🔴 / 🟡 / 🟢 | money / risk / control / standards / endgame | ... |

## 升級簽核（Escalation）
- (per findings.json#escalations[]) ← only emitted if non-empty
- Placeholder warnings if any escalate_to_is_placeholder=true

## 法律分析（CRAC）
### Conclusion / Rule / Analysis / Conclusion-again (from findings.json#crac)
### Citations table (from findings.json#citations[]) — incl. applicability_caveat
### Carve-outs (analysis limits)

## 主動 Redline 提案（可單獨抽出送對方）
- (per findings.json#redlines[] where proposed_text_send_now is non-empty)
- Format: clause_id + proposed_text body + rationale_zh_tw

## 內部 Fallback 預案（不對外）
- (per findings.json#redlines[] where stance_asymmetry_downgrade=true)
- proposed_text_internal_fallback content; framing: "if 對方 raises X at renewal"

## ✓ 對我方有利（Favorable Positions）
- (per findings.json#favorable_position_notes[])

## QA — self-grade
- answer N/M + source N/M (populated by self_grade.py findings.json#self_grade block)
- Failed criteria (if any)

---
Mandatory Disclaimer footer
```

#### 10.3 — Render business.md (non-lawyer-facing)

Write `<cwd>/legal-outputs/<YYYY-MM-DD>-<slug>/business.md`. **NO override banner — even when triggered.** Sections:

```
# 商業概要 — <contract name>

## 30 秒理解
**Why**: (from findings.json#summary_business.why; ≤80 chars)
**What**: (≤80 chars)
**What if**: (≤80 chars)

## Top 3 風險（量化）
- (per findings.json#top_3_business_impacts[]; severity yellow/red ONLY; with quantifiable_downside_evidence)

## ✓ 對我方有利
- (per findings.json#favorable_position_notes[])

## 主要 Redline 重點（含條文 + why）
- (per findings.json#redlines[] where proposed_text_send_now is non-empty)
- Same redlines as legal.md §主動 Redline 提案; intentional duplication for self-contained business.md
- Format: clause_id + proposed_text body + plain-language rationale

---
Mandatory Disclaimer footer
```

#### 10.4 — Run self_grade.py (in-place update)

```bash
uv run skills/legal-contract-review/scripts/self_grade.py \
  --input <outputs-dir>/findings.json \
  --outputs-dir <outputs-dir>
```

Default behavior (v0.3.4+): the script updates `findings.json#self_grade` block in-place and prints summary to stdout. NO separate `self-grade.md` file is created. Legal.md §QA section pulls from `findings.json#self_grade` at render time.

## Output contract

```
✅ L7 complete.
   Clauses evaluated: <count>
   By source: user_playbook=<N> / bundled_fallback=<M> / advisory=<K>
   By severity: green=<N> / yellow=<N> / red=<N>
   Walk-aways triggered: <count>
   Low-confidence fallbacks: <count>
   Placeholder warnings: <count>
   Pass to: Step 10 render (legal.md + business.md + findings.json) → self_grade.py
```

---

## Edge cases

- **Multiple matching variants** (ABAC gates overlap): take first; log warning. Phase 1.5 `detect_conflicts.py` enforces gate non-overlap at playbook-author validate time.
- **LLM returns invalid JSON**: re-prompt once with stricter format hint; if still invalid, treat as low-confidence (use risk_default).
- **Contract clause is missing entirely** (the expected clause is not in contract): not L7's job — L6 detected this as `missing_expected_clause`. L7 doesn't iterate clauses that don't exist.
- **Walk-away triggered + LLM body comparison both run** (shouldn't happen — walk path skips body): treat as bug; emit `pipeline_warning` to findings.json#self_grade.
- **mode == "redline"**: Step 9 emphasis on substitute text generation; legal.md §主動 Redline 提案 gets richer detail.
- **mode == "nda"**: L2-L3 skipped → L7 reads clauses directly from contract text + bundled NDA template. Same evaluation logic + same 2-output rendering.
- **--external-share flag passed**: after L7 emits findings, a post-processing pass strips `playbook_trace.matched_entry_path` from `legal.md §法律分析` + `§升級簽核` (replaces with "依本公司紅線政策"). Override red banner is **never** stripped.
- **Phase 1.5 status**: `scripts/abac_filter.py` is the canonical implementation as of v0.2.0. The inline-LLM rules above are the fallback for hosts without script execution. Importable as `from abac_filter import match_variant`.
