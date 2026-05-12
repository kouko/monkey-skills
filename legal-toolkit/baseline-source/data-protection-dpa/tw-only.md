---
clause_id: data-protection-dpa
variant_id: tw-only
gates:
  data_subjects_jurisdiction:
    eq: TW
walk_away_triggers:
  - "Breach notification > 24 小時（無法達成個資法 72hr 義務 — 違法）"
  - "Sub-processor 使用無 prior notice（無對抗權，違反個資法 §27 委外要求）"
  - "Audit rights 完全拒絕（即使以 SOC 2 / ISO 證據替代亦不可）"
  - "Return / deletion 義務不存在（違反個資法 §11 蒐集目的消失後義務）"
  - "個資法 2025/11 新制 72hr 通報 / 跨境傳輸 / 未成年保護任一項未對應"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / DPO]"
escalate_to_hint: "需 DPO 或 法務主管 簽核；無 DPO 公司則 GC"
risk_default: red
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# TW-Only DPA（data_subjects_jurisdiction = TW）

當資料當事人僅限台灣居民、無跨境傳輸時適用。

## 偏好立場
完全符合個資法 + 2025/11 新制：
- **告知義務**：§8 全文覆蓋（蒐集目的 / 個資類別 / 利用方式 / 第三方揭露 / 當事人權利）
- **特定目的**：§5 比例原則 + 蒐集 / 處理 / 利用一致
- **委外處理**（§27 處理者）：DPA 條款覆蓋處理目的 / 期間 / 個資類別 / 安全措施 / 監督機制
- **跨境**: 預設禁止（本 variant 適用 TW 限定情境）
- **未成年（< 18）保護**: 法定代理人同意機制 + 不得 profiling
- **Breach notification**: 24 hr to controller（讓 controller 達成 PDPC 72 hr）
- **Sub-processor**: 30 天 prior written notice + controller 反對權

## Fallback 1
告知義務 / 特定目的 / 委外 DPA 同上；breach notification 縮短到 48 hr；
sub-processor notice 縮短到 14 天但保留反對權。

## Fallback 2
僅當對方是 enterprise 客戶 + 自身有 PDPC 函釋認可的 compliance program：
- Breach notification 縮為 by-default 在發現後 reasonable time
- Sub-processor notice 縮為 list-based（雙方協議 approved list，新增時須 notice）

低於此即觸發 walk_away（個資法是強行規定，無法退讓到失效程度）。
