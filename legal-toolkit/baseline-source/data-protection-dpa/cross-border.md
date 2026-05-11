---
clause_id: data-protection-dpa
variant_id: cross-border
gates:
  data_subjects_jurisdiction:
    any_of: [US, CN, JP, KR, IN, BR, SG, AU, HK, CA, MX, AE]
walk_away_triggers:
  - "Transfer destination 在禁止傳輸列表（個資法 §21 + PDPC 函釋禁止國名單）"
  - "中國大陸傳輸無「個人信息保護法」配合條款 + 跨境傳輸申報程序"
  - "美國傳輸無 SCC 或無 Data Privacy Framework (DPF) 認證"
  - "TIA (Transfer Impact Assessment) 結果為高風險但仍堅持傳輸無補救措施"
  - "Sub-processor 在第三國（無上述任一機制保障）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / DPO]"
escalate_to_hint: "跨境傳輸涉及個資法 §21 違規 + GDPR Chapter V 雙重風險；建議 GC + DPO 簽核"
risk_default: red
currency: USD
last_updated: 2026-05-12
source_type: bundled_fallback
---

# Cross-Border DPA（data_subjects_jurisdiction 非 TW / 非 EEA）

適用於資料當事人居住國非 TW、非 EEA / UK 的情境（包含 US / CN / JP / KR
/ IN / BR / SG / AU / HK / CA / MX / AE 等），這類資料當事人會帶入第三國
法律 overlay + 跨境傳輸複雜度。

> ABAC discriminator note：本 DPA 三 variant 共用 `data_subjects_jurisdiction`
> 作為單一 gate key，避免 multi-match 問題（tw-only 對 TW、gdpr-overlay 對
> EEA/UK、cross-border 對其他國家居民）。跨境傳輸目的地（destinations）在
> 各 variant 的 body 內處理，不再作為 ABAC gate。

## 偏好立場
**Layered protection** — 三層安全網：

### 1. TW 個資法 §21 條件
- 涉及國家利益 / 重大公益 → 主管機關核准
- 受傳國對個資保護法律完備（adequacy）
- 跨境契約具備保護措施（contractual safeguard）→ 走 DPA + SCC 機制
- 當事人書面同意（last resort）

### 2. SCC / 等效機制（per destination）
- **US**: EU-US Data Privacy Framework (DPF) 認證 OR SCC + supplementary measures
- **China**: 個人信息保護法配合條款 + 跨境傳輸申報程序（CAC）+ 數據出境安全評估
- **JP/KR/IN/BR**: SCC + TIA + supplementary measures
- 受傳國法律不得允許政府機關超出比例調取個資（FISA 702 / China 國安法等問題）

### 3. TIA (Transfer Impact Assessment) — 評估受傳國法律 + 對方治理 +
合約有效保障是否抵銷風險。結果若 high risk 須有 supplementary measures
（end-to-end encryption / pseudonymisation / split processing 等）。

加上：標準 DPA Art.28 條款（同 gdpr-overlay variant 8 大強制條款）+
24hr breach notification + audit rights + return/deletion 義務。

## Fallback 1
3 層保護全保留 + TIA 結果若 medium risk 可接受（不須 high risk 才補救）。

## Fallback 2
僅當 destination 是 adequacy decision-recognised jurisdiction (e.g. 日本)：
- 可豁免 SCC + TIA（adequacy 已涵蓋）
- 仍需 Art.28 8 大強制條款 + 24hr breach notification

低於此即觸發 walk_away（跨境 + 個資外洩 = mandatory Escalation Override
per L7 evaluate protocol）。
