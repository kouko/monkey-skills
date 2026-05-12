---
clause_id: limitation-of-liability
variant_id: small-deal
gates:
  deal_size:
    lt: 100000
walk_away_triggers:
  - "cap < 3 個月服務費"
  - "IP 侵權無 carve-out 或 cap 範圍內含 IP 賠償"
  - "違反 confidentiality 受 cap 限制（應 carve-out）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常是 法務主管"
risk_default: yellow
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# Small-deal LoL（deal_size < USD 100K）

## 偏好立場
**Cap = 12 個月服務費**；IP 侵權 / 違反 confidentiality / 重大過失 / 故意行為
4 大 carve-out 不受 cap 限制；雙方對等 cap，無 super-cap。

## Fallback 1
**Cap = 6 個月服務費** + 同樣 4 大 carve-out。

## Fallback 2
**Cap = 3 個月服務費** + 至少 (a) IP 侵權 (b) confidentiality 兩項 carve-out
必須保留。低於此即觸發 walk_away。
