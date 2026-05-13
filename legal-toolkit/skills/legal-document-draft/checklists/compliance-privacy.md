# Privacy mode — compliance review checklist

> Hand-curated checklist aligned with current in-force 個資法 + 民法.
> Each item is verified by the LLM during the COMPLY_CHECK step of protocols/draft.md.
> Verdict options: PASS / FAIL / TBD_<id> where <id> is from references/pdpa-current-state.md canonical OPEN list.

## 個資法 §8 mandatory disclosure items (一至六款)

- [ ] §8 第一項第一款 — 蒐集者公司名稱已揭露？ — **{{verdict}}**
- [ ] §8 第一項第二款 — 蒐集目的已揭露？ — **{{verdict}}**
- [ ] §8 第一項第三款 — 蒐集個資類別已揭露？ — **{{verdict}}**
- [ ] §8 第一項第四款 — 利用期間 / 地區 / 對象 / 方式已揭露？ — **{{verdict}}**
- [ ] §8 第一項第五款 — 當事人權利 (§3) 已揭露 + 行使方式說明？ — **{{verdict}}**
- [ ] §8 第一項第六款 — 不提供個資之影響已揭露？ — **{{verdict}}**

## 特種個資 + 跨境

- [ ] §6 + §9 — 若蒐集特種個資，書面同意機制已說明？ — **{{verdict}}** (PASS if not collecting; FAIL if collecting but no mechanism)
- [ ] §21 — 若涉跨境傳輸，目的地清單揭露 + 保護措施說明？ — **{{verdict}}**

## 安全維護 + 通報

- [ ] §27 — 安全維護措施列舉？ — **{{verdict}}**
- [ ] 施行細則 §22 — 個資外洩通報用「即時」(NOT 72hr GDPR)？ — **{{verdict}}**
- [ ] §20-1 — Audit framework 段落？ — **TBD_PDPA_audit_framework** (Art. 20-1 promulgated 2025-11-11; 施行日期未定)

## 未成年人保護

- [ ] 民法 §12-13 — 未成年人同意機制依民法行為能力規定？(NOT a PDPA-specific age threshold) — **{{verdict}}**

## 結構性

- [ ] 政策生效日期已填？ — **{{verdict}}**
- [ ] DPO 聯絡 email 已填？ — **{{verdict}}**
- [ ] 第三方 SDK 揭露段落 (即使列表為空亦應說明「未使用」)？ — **{{verdict}}**

## TBD migration tracking

(populate during COMPLY_CHECK; cite references/tbd-migration-template.md for migration steps when PDPC sub-regulations resolve)

- **TBD_PDPA_audit_framework**: monitor PDPC announcements; when Art. 20-1 effective + 稽核辦法 published, add audit-framework subsection to §9 安全維護 per tbd-migration-template.md entry.

(Additional TBD entries appear here only if specific session conditions warrant — e.g., TBD_PDPC_timeframe if user explicitly asks about 72hr language; TBD_PDPC_threshold if special-volume notification.)
