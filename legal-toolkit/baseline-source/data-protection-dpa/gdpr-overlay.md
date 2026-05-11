---
clause_id: data-protection-dpa
variant_id: gdpr-overlay
gates:
  data_subjects_jurisdiction:
    any_of: [EU, UK, EEA]
walk_away_triggers:
  - "DPA 不含 GDPR Art.28 (3) 8 大強制條款 (purpose / instructions / confidentiality / security / sub-processor / data subject assistance / DPIA assistance / return-delete)"
  - "Breach notification > 24 hr to controller (controller 無法達成 Art.33 72hr 義務)"
  - "Sub-processor 無 prior consent (Art.28(2): general OR specific consent required)"
  - "Transfer outside EEA 無 SCC / BCR / adequacy decision (Chapter V 違反)"
  - "資料主體權利請求拒絕協助 (Art.12-22 範圍)"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / DPO]"
escalate_to_hint: "GDPR 涉及罰款最高營業額 4%；建議 GC + DPO 雙簽"
risk_default: red
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# GDPR Overlay DPA（data_subjects_jurisdiction ∈ {EU, UK, EEA}）

適用於資料當事人有 EU / UK / EEA 居民，無論我方是否為 EU entity。

## 偏好立場
完全符合 GDPR Art.28(3) 的 8 大強制條款：
1. **Documented instructions only** — processor 僅依 controller 書面指令處理
2. **Confidentiality obligation** — 員工 confidentiality 義務書面化
3. **Security measures (Art.32)** — encryption / pseudonymisation / availability / resilience / regular testing
4. **Sub-processor consent (Art.28(2))** — general or specific written consent + same obligations passed down
5. **Data subject rights assistance (Art.12-22)** — access / rectification / erasure / portability / objection / automated decision
6. **DPIA + prior consultation assistance (Art.35-36)** — high-risk processing
7. **Breach notification (Art.33)** — 24 hr to controller
8. **Return or deletion + audit rights** — at end of services + on-request

加上：
- **Standard Contractual Clauses (SCC)** 或 **Adequacy Decision** for cross-border transfer (Chapter V)
- **DPA + SCC 一體簽署** — 不接受 SCC 後補

## Fallback 1
8 大強制條款全保留 + SCC 必含 + audit rights 可改為 SOC 2 + ISO 27001
證據替代（仍保留 right to physical audit 一年一次）。

## Fallback 2
僅當對方是 GDPR-certified processor (e.g. AWS / Azure 已 Art.28 compliant)：
- SCC 可改為 module 比照 + cross-border 走 adequacy decision
- 但 8 大強制條款 + 24 hr breach notification 不可退讓（GDPR 強行規定）

低於此即觸發 walk_away（GDPR 違規最高罰款 = 全球年營收 4% — red 預設）。
