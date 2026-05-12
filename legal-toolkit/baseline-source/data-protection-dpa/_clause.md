---
clause_id: data-protection-dpa
contract_types_applicable: [SaaS, MSA, DPA, 服務委任]
has_variants: true
market_data: |
  個資法 2025/11 新制: 72hr 通報義務 + 跨境傳輸限制 + 未成年保護加碼；
  GDPR Art.28 強制 DPA 條款覆蓋率 = 99% (EU 客戶)；
  SCC (Standard Contractual Clauses) 出現率 = 85% (cross-border data transfer)。
last_updated: 2026-05-12
owner: "[請編輯為你的姓名]"
source_attribution: |
  個資法 §3 §5 §8 §21 §27 + 2025/11 新制條文 + GDPR Art.28 Chapter V +
  PDPC 通報實務指引 + 理律 newsletter 2024-11「個資法新制 DPA 對照」+
  Addleshaw Goddard DPA Playbook
---

# 資料保護 (Data Protection Agreement)

依 data subject jurisdiction 分三 variant。本條款是 portfolio-level 高
影響條款 — risk_default 預設 red（不是 yellow），因為個資處理涉及刑責
+ 監管罰款 + reputational damage 三重風險。

## 為什麼這條重要 (適用於所有 variant)

DPA 不是「政策性條款」，而是**法定義務的合約化**：
- 個資法 §27 強制要求「個資處理委外」須以契約規範
- GDPR Art.28 強制要求 processor 與 controller 簽訂 DPA
- 2025/11 新制要求 72 小時內通報

工具邏輯：
1. DPA 條款的 baseline 是**法律義務**，不是議價空間 — 任何低於法律要求
   的 fallback 都是無效條款（民法 §71）
2. 跨境傳輸涉及多重 jurisdiction overlay（TW 個資法 + GDPR + 對方所在地）
3. Sub-processor 管理是高風險點 — 對方使用第三方 SaaS 處理我方資料時必須
   告知 + 取得同意

關鍵設計：
1. **明確 controller / processor 角色** — 不接受 ambiguous wording
2. **Sub-processor consent / notice** — 至少 30 天 prior notice + 反對權
3. **Breach notification** — TW: 72hr (2025/11 新制) / GDPR: 72hr Art.33
4. **Cross-border transfer** — TW: §21 條件 / GDPR: SCC + TIA
5. **Audit rights** — at least 1x/year + SOC 2 / ISO 27001 證據替代
6. **Return / deletion on termination** — 30-90 天內

## 替代條款文字 (shared template)

詳細條款文字依 variant 不同（tw-only 跑台灣 §21 / gdpr-overlay 跑 SCC /
cross-border 跑混合）— 見對應 variant 檔案。共同 procedural standards：

> "Processor will: (a) process personal data only on documented
> instructions from Controller; (b) ensure persons authorised to
> process personal data have committed to confidentiality; (c)
> implement appropriate technical and organisational security
> measures including encryption in transit and at rest; (d) assist
> Controller in fulfilling data subject rights requests within 10
> business days; (e) notify Controller of any personal data breach
> within 24 hours of awareness (allowing Controller to meet its 72-hour
> regulator notification deadline); (f) make available all information
> necessary to demonstrate compliance and allow audits; (g) at choice
> of Controller, delete or return all personal data after end of
> services."

## 相關函釋 / 判例
- 個資保護處 109 年 7 月 28 日 法律字第 10903XXX 號（跨境傳輸個資判斷標準）
- 個資保護處 110 年 11 月 函釋（72 小時通報要件）
- 智慧財產法院 108 年度民營訴字第 22 號（DPA 條款違反 §247-1 顯失公平）
