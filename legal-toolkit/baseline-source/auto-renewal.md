---
clause_id: auto-renewal
contract_types_applicable: [SaaS, MSA, 訂閱服務, 軟體授權]
walk_away_triggers:
  - "自動續約 + 無 notice 義務（對方不通知就直接續約一年）"
  - "Notice 期間 < 30 天（給對方的通知窗口太短，實務上錯過）"
  - "續約時自動漲價 > CPI + 5%（無 cap 的漲價條款）"
  - "續約後僅可在續約日當天 termination（一旦過了就鎖死另一個 cycle）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常是 法務主管；若客戶 deal_size 大則 GC"
risk_default: yellow
currency: USD
last_updated: 2026-05-11
owner: "[請編輯為你的姓名]"
source_type: bundled_fallback
source_attribution: |
  WorldCC 2024 Benchmark (Auto-renewal — Top 5 most-renegotiated) +
  ContractKen Auto-Renewal Playbook + 消保法 §17 (定型化契約應記載及不得記載事項) +
  公平交易法 §25 (附加不公平交易條件)
---

# 自動續約 (Auto-Renewal)

## 偏好立場
**No auto-renewal** 為理想（雙方必須積極選擇續約）；若對方堅持
auto-renewal，則：
- **60-90 天 prior notice** 由對方主動發送（不是「您忘了就續約」）
- Notice 必須是 **書面 + email + 系統內訊息** 三管齊下
- 續約價格漲幅 cap **≤ CPI + 3%** 或固定不漲
- 續約 cycle 不超過 **12 個月**（年約即可，不接受多年）

## Fallback 1
- **30-60 天 notice** 由對方發送
- 漲價 cap **≤ CPI + 5%**
- 1-year renewal cycle 可接受

## Fallback 2
僅當 deal value < USD 50K 時：
- **30 天 notice 由我方發送**（自動續約預設，但我方可隨時取消）
- 漲價依市場行情無 cap，但必須在 notice 中明示金額
- 此版本僅可用於低 risk SaaS 工具類

## 為什麼這條重要
自動續約是 vendor lock-in 的隱藏機制。法務時間有限，每年無法
review 所有合約是否該續，若 notice window 太短就會「被迫續約」
另一個 cycle。對 portfolio 而言，這是現金流自由度議題 —
而非單一條款議題。

## 替代條款文字
> "This Agreement has an initial term of one (1) year from the
> Effective Date. The Term will automatically renew for
> successive one-year periods unless either Party gives the
> other written notice of non-renewal at least sixty (60) days
> prior to the end of the then-current term. Pricing for any
> renewal term will not increase by more than five percent (5%)
> over the immediately preceding term, or the change in the
> Consumer Price Index for All Urban Consumers published by the
> [台灣行政院主計總處 / U.S. Bureau of Labor Statistics], whichever
> is less."

## 相關判例
- 行政院消費者保護處 2018 函釋（消保法 §17 定型化契約應記載及不得記載事項 — SaaS 訂閱）
- 最高行政法院 108 年度判字第 245 號（電信合約自動續約 unfair commercial term）
