---
clause_id: limitation-of-liability
variant_id: mid-deal
gates:
  deal_size:
    gte: 100000
    lt: 1000000
walk_away_triggers:
  - "cap < 6 個月服務費"
  - "IP 侵權 carve-out 被限縮（例：須對方故意才適用）"
  - "違反 confidentiality 受 cap 限制"
  - "indirect/consequential damages 雙方均不可請求（disadvantage 在我方）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常是 GC 簽核"
risk_default: yellow
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# Mid-deal LoL（USD 100K - 1M）

## 偏好立場
**Cap = 12 個月服務費** + 4 大 carve-out + **super-cap = 24 個月**
適用於 IP 侵權 / confidentiality 違反 / 重大過失 / 故意行為以外的高風險
情境（例如：因產品缺陷導致 systemic data corruption）。

## Fallback 1
**Cap = 12 個月** + 4 大 carve-out（無 super-cap）。

## Fallback 2
**Cap = 9 個月** + 至少保留 IP / confidentiality / gross negligence
3 大 carve-out。
