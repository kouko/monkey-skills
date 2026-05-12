---
clause_id: indemnification
variant_id: small-deal
gates:
  deal_size:
    lt: 100000
walk_away_triggers:
  - "單方面 indemnification（只我方賠對方，對方無對等義務）"
  - "Indemnify scope 包含對方自己的故意 / 重大過失行為"
  - "對方可單方 settle 涉及 admit liability 的條款"
  - "IP 侵權 indemnification 受 LoL cap 限制"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常是 法務主管"
risk_default: yellow
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# Small-deal Indemnification（deal_size < USD 100K）

## 偏好立場
**雙向 indemnification** for: IP 侵權、違反 confidentiality、重大過失 /
故意行為三大 trigger。
- Notice + cooperation 義務雙向
- Settlement consent 必須雙方
- IP 侵權 indemnification carve-out from LoL cap（unlimited）

## Fallback 1
雙向 indemnification 但只限 IP 侵權 + confidentiality 兩大 trigger。
重大過失 / 故意可放入 general liability 處理，無需獨立 indemnification 條款。

## Fallback 2
單方面 indemnification（對方 indemnify 我方）僅針對 IP 侵權，且必須：
- Capped at deal value（不可 unlimited）
- 包含 prompt notice + cooperation 義務
- 我方有 settlement consent
