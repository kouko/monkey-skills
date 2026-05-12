---
clause_id: limitation-of-liability
variant_id: large-deal
gates:
  deal_size:
    gte: 1000000
walk_away_triggers:
  - "cap < 12 個月服務費"
  - "無 super-cap 機制（IP / confidentiality 範圍以外的高風險情境）"
  - "indemnification carve-out 被限縮（僅針對 third-party direct claim）"
  - "雙方 cap 不對等（對方 unlimited，我方 capped）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / CFO]"
escalate_to_hint: "通常需 GC + CFO 雙簽（單一合約金額超過營收 10% 警戒）"
risk_default: red
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# Large-deal LoL（deal_size >= USD 1M）

## 偏好立場
**Cap = 24 個月服務費** + 4 大 carve-out + **super-cap = 36 個月** 適用於：
- IP 侵權 / confidentiality 違反 / 重大過失 / 故意行為（standard 4 carve-outs）
- 重大資料外洩（影響 > 10K 當事人）
- Indemnification 履行
- 監管罰款（因對方原因）

雙方 cap 對等；indirect/consequential damages 互相排除（標準業界慣例）。

## Fallback 1
**Cap = 18 個月** + super-cap = 24 個月 + 4 大 carve-out 全保留。

## Fallback 2
**Cap = 12 個月** + super-cap = 18 個月 + 至少保留 IP / confidentiality /
indemnification 3 大 carve-out。低於此即觸發 walk_away（red default）。
