# PII-breach mode — compliance review checklist

> Hand-curated checklist aligned with current in-force 個資法 + 施行細則 + 民法.
> Each item is verified by the LLM during the COMPLY_CHECK step of
> `protocols/pii-breach.md`.
> Verdict options: PASS / FAIL / TBD_<id> where <id> is from
> `references/pdpa-current-state.md` canonical OPEN list (fabricated ids fail
> SELF_GRADE).
>
> Path A discipline: each item phrases the rule by naming the **correct**
> statutory citation + phrasing. Forbidden phrasings are enumerated in
> `scripts/grade_response.py` `PATH_A_ANTIPATTERNS` (single source of truth);
> do not inline them here, even in "NOT X" form — the grader will eventually
> tighten the scan and any leakage from this file into `legal.md` would
> retroactively fail prior outputs.

## 個資法 §8 mandatory disclosure (re-applied to incident notification context)

§8 第一項一至六款 itemizes mandatory告知 fields. In an incident notification,
the LLM verifies these were either disclosed already (in the pre-existing
privacy policy referenced) or are addressed in the breach notification:

- [ ] §8 第一項第一款 — 蒐集者公司名稱已揭露於 PDPC 通報文與當事人通知？ — **{{verdict}}**
- [ ] §8 第一項第二款 — 蒐集目的已揭露？(可引用既有 privacy policy 內容) — **{{verdict}}**
- [ ] §8 第一項第三款 — 受影響個資類別已具體揭露？ — **{{verdict}}**
- [ ] §8 第一項第四款 — 利用期間 / 地區 / 對象 / 方式已揭露 (含異常存取後狀態)？ — **{{verdict}}**
- [ ] §8 第一項第五款 — 當事人權利 (§3 查詢／更正／刪除／停止處理／異議) 已揭露 + 行使方式說明？ — **{{verdict}}**
- [ ] §8 第一項第六款 — 不提供個資之影響已揭露 (incident 後續救濟脈絡)？ — **{{verdict}}**

## 個資法 §12 通報義務 + 施行細則 §22 用語基準

§12 課予個資外洩通報義務（2025-11 公布的修正版具體小時數授權子法尚未發布；
本 checklist 採用 §22 安全基準）。

- [ ] §12 通報對象 — 已寄送個人資料保護委員會籌備處 (PDPC 籌備處，法務部)？ — **{{verdict}}**
- [ ] §12 通報主體 — 通報文以委託者（個資法 §4）名義發出？ — **{{verdict}}**
- [ ] 施行細則 §22 — 通報用語採「即時」基準 (incident_datetime → notification_datetime 延遲已說明)？ — **{{verdict}}**
- [ ] §12 通報文齊備 — 含事故時間 / 影響範圍 / 採取措施 / DPO 聯絡 4 大要素？ — **{{verdict}}**

## 個資法 §6 / §9 特種個資

§6 列舉特種個資（病歷／醫療／基因／性生活／健康檢查／犯罪前科）；蒐集處理利用
須符合 §6 第一項各款例外或書面同意。incident response 場景下要驗證 incident
中是否涉及特種個資、若涉及則 §6 / §9 配套機制是否齊備。

- [ ] §6 — 是否確認 incident 是否涉及特種個資？(special_category_assessment 已填) — **{{verdict}}**
- [ ] §6 — 若涉及特種個資，原蒐集處理是否依 §6 第一項各款合法事由 (含書面同意機制)？ — **{{verdict}}** (PASS if not affected; FAIL if affected without 書面同意 mechanism)
- [ ] §9 — 若涉及特種個資且係 §6 但書場景，第三人提供告知機制是否說明？ — **{{verdict}}**

## 個資法 §21 跨境傳輸

§21 授權主管機關公告限制；incident 若涉及跨境傳輸場景，需揭露目的地清單 +
保護措施 + 是否觸及主管機關公告之限制行業。

- [ ] §21 — 是否確認 incident 是否涉及跨境傳輸？(cross_border_assessment 已填) — **{{verdict}}**
- [ ] §21 — 若涉跨境，目的地清單已揭露 + 保護措施已說明？ — **{{verdict}}** (PASS / N/A; if 涉及 then must cite 目的地 + 保護措施)
- [ ] §21 — 若涉及主管機關公告之限制行業，是否符合公告要件？ — **{{verdict}}** (PASS / N/A / TBD_GOV_CLOUD_restrictions if relevant)

## 個資法 §27 安全維護

§27 課予「適當之安全措施」義務；incident 後 §27 落實情況是技術 + 行政兩面。

- [ ] §27 — 技術措施已列舉 (technical_actions_bullets)？ — **{{verdict}}**
- [ ] §27 — 行政措施已列舉 (administrative_actions_bullets)？ — **{{verdict}}**
- [ ] §27 — 證據保全已列舉 (evidence_preservation_bullets)？ — **{{verdict}}**

## 個資法 §4 委託處理

§4 規範委託處理場景；若 incident 發生於委託處理鏈，責任主體 + 通報義務歸屬
須依 §4 確認。

- [ ] §4 — 是否確認 incident 是否涉及委託處理？(processor_involvement 已填) — **{{verdict}}**
- [ ] §4 — 若涉及，通報主體（委託者）與受託者責任分工已說明？ — **{{verdict}}**

## 民法 §12-13 未成年人保護

成年年齡為十八歲（民法 §12 修正 2023-01-01 生效）；未滿十八歲之未成年人為
限制行為能力人（民法 §13）。incident 若涉及未成年當事人，當事人通知應加註
法定代理人收受機制。

- [ ] 民法 §12-13 — 是否確認 incident 是否涉及未成年當事人？(minor_involvement 已填) — **{{verdict}}**
- [ ] 民法 §12-13 — 若涉及，當事人通知是否加註法定代理人收受機制？ — **{{verdict}}** (PASS / N/A)

## §20-1 Audit framework (TBD)

- [ ] §20-1 — Audit framework 段落？ — **TBD_PDPA_audit_framework** (Art. 20-1 promulgated 2025-11-11; 施行日期未定)

## 結構性

- [ ] 時間軸完整 — 至少包含發生 / 發現 / 初步應變 / 圍堵 / PDPC 通報 5 個 ISO 8601 anchors (未發者以 `⏳ 待 X` 標記)？ — **{{verdict}}**
- [ ] DPO 聯絡完整 — name / email / phone 三項皆填？ — **{{verdict}}**
- [ ] 採取措施分技術 / 行政兩段明列？ — **{{verdict}}**
- [ ] 對外溝通 Top 3 已列於 business.md？ — **{{verdict}}**
- [ ] 文件字號 (document_reference_number) 已填？ — **{{verdict}}**
- [ ] 嚴重度等級 (severity_level) 已判定？ — **{{verdict}}**

## TBD migration tracking

(populate during COMPLY_CHECK; cite `references/tbd-migration-template.md`
for migration steps when sub-regulations publish)

- **TBD_PDPC_pending** — PDPC 籌備處 → 正式委員會 transition; 通報機制待掛牌後驗證。Migration: 公告掛牌時 update 通報入口資訊。
- **TBD_PDPC_threshold** — 通報範圍授權子法 (個資法 §12 §2)。Migration: 子法公布後，按閾值規則重評本案是否仍需通報；若閾值規定可豁免低風險案件，可補入「依新子法不需通報」之 §6 update。
- **TBD_PDPC_timeframe** — 通報時限具體小時數授權子法 (個資法 §12 §4)。Migration: 子法公布後，按具體時程規則 audit 本案 incident_datetime → notification_datetime 延遲是否仍合規；若否，補入「延遲說明」段落。
- **TBD_PDPC_notification_url** — 正式通報入口 URL。Migration: 取得正式入口後，update 通報文發送管道紀錄。
- **TBD_PDPA_effective_date** — Executive Yuan announcement of 2025/11 batch 施行日期。Migration: 公告施行後，整體 incident response SOP 重新檢視 §12 / §20-1 等條文配套。
- **TBD_PDPA_audit_framework** — §20-1 audit framework. Migration: 稽核辦法 published 後，補入 audit-framework 段落於 §27 安全維護。
- **TBD_GOV_CLOUD_restrictions** — 政府機關雲端服務限制 (likely 政府採購法 / 資通安全管理法)。Migration: 法源確認後，若 incident 涉相關場景，補入限制條款引註。

(Per-session TBD entries beyond this baseline appear only when specific session
conditions warrant — e.g., `tbd_root_cause_label = TBD_PDPC_pending` when root
cause investigation is gated on PDPC formal channels.)
