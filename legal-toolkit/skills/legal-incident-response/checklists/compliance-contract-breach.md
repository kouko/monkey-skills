# Contract-breach mode — compliance review checklist

> Hand-curated checklist aligned with current in-force Taiwan 民法 +
> 民事訴訟法 + Q8 Soft-delegation cross-skill discipline.
> Each item is verified by the LLM during the COMPLY_CHECK step of
> `protocols/contract-breach-delegate.md`.
> Verdict options: PASS / FAIL. (No TBD_* ids apply — SP3b contract-breach
> path does not depend on PDPC sub-reg specifics.)
>
> Path A discipline: each item phrases the rule by naming the **correct**
> statutory citation. Forbidden phrasings are enumerated in
> `scripts/grade_response.py` `PATH_A_ANTIPATTERNS` (single source of truth);
> do not inline them here, even in "NOT X" form.

## §1 違約 classification 對齊

- [ ] handoff `breach_type` 字段值為 canonical 民法 §227 / §225 / §234 /
  §229 / §259 之一（canonical label，非自由文字）？ — **{{verdict}}**
- [ ] classified §number 已列於
  `legal-toolkit/scripts/canonical/legal-sources.json` `statute_sources`
  之 民法（`pcode=B0000001`）條目？ — **{{verdict}}**
- [ ] 原始 free-text `breach_type` 保留於 `notes` 字段供 legal-contract-review
  後續參考？ — **{{verdict}}**
- [ ] legal.md §1 違約 classification 段含 民法 §number + canonical 違約類型
  label + 對應合約條款引用？ — **{{verdict}}**

## §2 時間軸 ISO date completeness

- [ ] §時間軸 含 簽約日（或標示 `unknown`）？ — **{{verdict}}**
- [ ] §時間軸 含 `breach_date`（ISO 8601 `YYYY-MM-DD` 格式）？ — **{{verdict}}**
- [ ] §時間軸 含 `discovery_date`（ISO 8601 `YYYY-MM-DD` 格式）？ — **{{verdict}}**
- [ ] `discovery_date >= breach_date`？（發現一定不早於發生） — **{{verdict}}**
- [ ] 催告日 / 解除日 以 `⏳ 待催告` / `⏳ 待解除` 標記未發生？ — **{{verdict}}**

## §3 alleged_breach_clauses 非空

- [ ] handoff `alleged_breach_clauses` 長度 ≥ 1？ — **{{verdict}}**
- [ ] 條款引用格式合理（例：`§X.Y` / `第N條` / `Article N`）？ — **{{verdict}}**
- [ ] 所有 alleged clauses 在 legal.md §1 + §2 中皆有對應提及？ — **{{verdict}}**

## §4 handoff-context.json schema completeness

- [ ] 10 required keys 齊備：`schema_version` / `from_skill` / `to_skill` /
  `contract_path` / `breach_type` / `alleged_breach_clauses` / `breach_date`
  / `discovery_date` / `counterparty` / `urgency_level`？ — **{{verdict}}**
- [ ] `schema_version = 1`？ — **{{verdict}}**
- [ ] `from_skill = "legal-incident-response"`？ — **{{verdict}}**
- [ ] `to_skill = "legal-contract-review"`？ — **{{verdict}}**
- [ ] `urgency_level` ∈ {`high`, `moderate`, `low`}？ — **{{verdict}}**
- [ ] `counterparty.name` 已填（其餘子欄位 `company_id` / `contact_email`
  optional）？ — **{{verdict}}**

## §5 legal.md §2 Handoff pointer

- [ ] legal.md 含字串 `legal-contract-review`？（grader 強制檢查） — **{{verdict}}**
- [ ] `contract_path` 顯示於 §2，可由 user copy-paste 至 contract-review
  session？ — **{{verdict}}**
- [ ] `handoff-context.json` 路徑於 §2 提及，作為 seed file pointer？ — **{{verdict}}**
- [ ] §2 明確標註「在另一 session 執行 /legal-contract-review」（避免 user
  以為本 session 會 auto-invoke）？ — **{{verdict}}**

## §6 民法 時效 acknowledged in business.md

- [ ] business.md §4 含「民法 §125 一般時效 15 年」字樣？ — **{{verdict}}**
- [ ] business.md §4 含「民法 §197 侵權時效 2 年 / 10 年」字樣？ — **{{verdict}}**
- [ ] 若 `days_since_breach > 1825`（≈5 年），business.md flag 時效風險警示？
  — **{{verdict}}** (PASS / N/A)

## 結構性

- [ ] legal.md byte count > 500（grader `MIN_LEGAL_MD_BYTES`）？ — **{{verdict}}**
- [ ] business.md byte count > 200（grader `MIN_BUSINESS_MD_BYTES`）？ — **{{verdict}}**
- [ ] 沒有 Path A anti-pattern 字串出現於 legal.md / business.md
  （delegated to `scripts/grade_response.py` `PATH_A_ANTIPATTERNS`）？ — **{{verdict}}**
- [ ] `handoff-context.json` 為合法 JSON（`json.loads` 不報錯）？ — **{{verdict}}**
- [ ] business.md §2 Top 3 即時動作 each 含具體 action verb + 建議時點？ — **{{verdict}}**
