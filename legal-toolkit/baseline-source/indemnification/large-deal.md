---
clause_id: indemnification
variant_id: large-deal
gates:
  deal_size:
    gte: 1000000
walk_away_triggers:
  - "Indemnification cap < super-cap (24-36 個月)"
  - "對方 indemnification 不含 data breach + 監管罰款"
  - "雙方非對等 indemnification（單方扛某類風險）"
  - "Settlement consent 對方可單方 in any scenario"
  - "Cross-indemnity 不含 IP background warranty（對方拒絕保證其 IP 不侵權）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / CFO]"
escalate_to_hint: "通常需 GC + CFO 雙簽（涉及 unlimited liability 場景）"
risk_default: red
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# Large-deal Indemnification（deal_size >= USD 1M）

## 偏好立場
**Comprehensive 雙向 indemnification** 涵蓋 5 大 trigger：
1. IP 侵權 / 違反 IP warranty
2. 違反 confidentiality
3. 重大過失 / 故意行為 / 詐欺
4. **資料外洩** — 完整分擔 + indemnifying party 負責 PDPC / GDPR 通報義務
5. **監管罰款** — 因對方違規導致 → 對方全額 indemnify

雙方對等；procedural standards 同前 + IP indemnification + data breach +
監管罰款 三大 carve-out from LoL（unlimited）。其他 indemnification capped
at super-cap = 36 個月服務費。

**Cross-indemnity required**: 對方須提供 IP background warranty (its
pre-existing IP doesn't infringe) AND defend-and-indemnify obligation
(not just pay damages — actively defend the claim).

## Fallback 1
5 trigger 全保留 + IP / data breach unlimited，其他 capped at 24 個月。
Cross-indemnity 包含 IP background warranty 但 defend-and-indemnify
可改為 pay-defense-costs（we control defence）。

## Fallback 2
保留 4 大 trigger（捨棄監管罰款項，視個案處理）+ IP unlimited + others
capped at 18 個月。低於此即觸發 red walk_away（IP unlimited + cross-
indemnity 是 large-deal 紅線）。
