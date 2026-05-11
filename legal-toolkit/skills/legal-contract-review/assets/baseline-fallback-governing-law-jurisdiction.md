---
clause_id: governing-law-jurisdiction
contract_types_applicable: [SaaS, MSA, NDA, 採購, 跨境服務]
walk_away_triggers:
  - "中華人民共和國法律 + 中國法院（除非客戶是中國 entity 且有真實當地履約）"
  - "對方所在國法律 + 對方所在國法院（單方面 home court advantage）"
  - "強制仲裁地點對方所在國 + 對方指定仲裁機構"
  - "選擇紐約 / 倫敦法但無真實 connecting factor（單純對方偏好）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常是 GC 或 法務主管；跨境議題建議 GC 簽核"
risk_default: yellow
currency: USD
last_updated: 2026-05-11
owner: "[請編輯為你的姓名]"
source_type: bundled_fallback
source_attribution: |
  SpotDraft Glossary (Governing Law & Jurisdiction) + 民事訴訟法 §6 (國際管轄) +
  涉外民事法律適用法 §20 (契約準據法當事人意思自治) + 仲裁法 §32
---

# 準據法與管轄 (Governing Law & Jurisdiction)

## 偏好立場
**準據法**: 中華民國法律（台灣方為服務提供 / 採購方時）；
**管轄法院**: 台灣台北地方法院為第一審管轄法院；
**或仲裁**: 中華民國仲裁協會 (CAA) 於台北以中文進行。

## Fallback 1
**雙方各自所在地法律 + 各自所在地法院** 二選一，先程式判斷
（誰先起訴在誰那）；或 **新加坡法 + SIAC 仲裁**（中性 hub，
共通性高，符合亞太多邊合約 industry norm）。

## Fallback 2
僅當對方有 enterprise scale 真實談判力時：
**香港法 + HKIAC 仲裁** — 仍 keep 仲裁地中性，避開單一 home court。

## 為什麼這條重要
管轄條款是「跟對方起訴成本」的硬約束。對方在自己國家的法院，
你要訴訟必須請當地律師、依當地程序、可能語言不通；對你而言
成本可能 5-10 倍。即使你在條款上「贏」，你也可能因成本而 walk
away。所以管轄是 portfolio-level 的「議價成本」議題。

## 替代條款文字
> "This Agreement is governed by and construed in accordance
> with the laws of the Republic of China (Taiwan), without
> regard to its conflict of laws principles. The Parties
> submit to the exclusive jurisdiction of the Taipei District
> Court of Taiwan as the court of first instance for any
> dispute arising out of or in connection with this Agreement."
>
> [Or arbitration variant:]
> "Any dispute arising out of or in connection with this
> Agreement shall be finally settled by arbitration under the
> Arbitration Rules of the Chinese Arbitration Association,
> Taipei, by three arbitrators, conducted in Mandarin Chinese,
> with the seat of arbitration in Taipei, Taiwan."

## 相關判例
- 最高法院 96 年度台上字第 2032 號（準據法當事人意思自治）
- 智慧財產法院 99 年度民營訴字第 7 號（境外服務合約管轄判斷）
