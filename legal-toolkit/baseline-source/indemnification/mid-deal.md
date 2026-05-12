---
clause_id: indemnification
variant_id: mid-deal
gates:
  deal_size:
    gte: 100000
    lt: 1000000
walk_away_triggers:
  - "單方面 indemnification"
  - "Data breach 完全由我方扛（無 contributory negligence 分擔）"
  - "Settlement 對方可單方且 affects our reputation / non-monetary obligations"
  - "Indemnification 範圍延伸到對方員工 / 子公司 / 客戶（無 standard knock-on 限制）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常需 GC 簽核（mid-deal 已涉及實質金額）"
risk_default: yellow
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# Mid-deal Indemnification（USD 100K - 1M）

## 偏好立場
**雙向 indemnification** for:
1. IP 侵權第三方索賠 (mandatory)
2. 違反 confidentiality 致對方被訴
3. 重大過失 / 故意行為
4. **資料外洩 + 監管罰款** — 視責任歸屬分擔（不單方扛）

Procedural standards 同 small-deal（雙向 notice / cooperation / settlement
consent），加上：
- IP 侵權 indemnification 無 cap（carve-out from LoL）
- 其他 indemnification capped at super-cap (24 個月服務費)
- Knock-on 範圍限對方直接員工 + 直接客戶被訴情境

## Fallback 1
保留三大 trigger（IP / confidentiality / 重大過失）+ data breach 完全
由 root cause 方扛（捨棄 contributory negligence）。

## Fallback 2
僅 IP + confidentiality 兩大 trigger，但 IP indemnification 必須
unlimited（carve-out from LoL），且包含 IP infringement 的
"defend-and-indemnify" 義務（不只是賠錢，要主動 defend）。
