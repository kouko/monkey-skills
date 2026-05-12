---
clause_id: deemed-breach-cascade
contract_types_applicable: [NDA, mutual NDA, 服務委任, 採購]
walk_away_triggers:
  - "員工違約自動視為 receiving party 違約（無 due care defense）"
  - "離職員工 5 年內違約仍構成 receiving party 違約"
  - "第三人 / sub-contractor 違約自動視為 receiving party 違約（無 sub-cap）"
  - "員工/第三人違約直接連動到 100 萬定額違約金 + 律師費"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / 人資主管]"
escalate_to_hint: "通常是 法務主管 + 人資主管雙簽；deal_size 大則 GC"
risk_default: red
currency: TWD
last_updated: 2026-05-12
statute_verified_at: 2026-05-12  # v0.3.1+: cross-checked at https://law.moj.gov.tw
case_citations_verified_at: 2026-05-12  # v0.3.2+: verify-or-removed at https://judgment.judicial.gov.tw
owner: "[請編輯為你的姓名]"
source_type: bundled_fallback
source_attribution: |
  v0.3.4 NDA dogfood independent audit (2026-05-12) caught this as
  carry-over false negative across 3 audit rounds — bundled fallback
  was SaaS-shaped + did not cover «員工 + 第三人 違約自動算 receiving
  party 違約 cascade» NDA-native pattern. v0.3.5 Phase 1.9 addition
  per ROADMAP §1.6.2 Deferred → NDA-native fallback baselines.
  Doctrinal anchors: 民法 §188 受僱人侵權連帶責任 + §224 履行輔助
  人責任 + 王澤鑑《侵權行為法》「企業責任之擴張與限縮」.
---

# 員工 + 第三人違約 cascade（Deemed-Breach Cascade）

## 偏好立場
員工違約 + 第三人 / sub-contractor 違約之 receiving party 連帶責任，限於：

1. **合理控制範圍**：在職員工 + 主動指派之 sub-contractor（不含離職員工自由意志行為 + 未經 receiving party 同意之 sub-tier）
2. **保留 due care 抗辯**：receiving party 已盡相當注意義務（培訓 + 員工 NDA + sub-contractor agreement）時不負連帶責任
3. **離職員工時效**：離職 N 年後不再連帶（建議 2 年；對 receiving party 為 SME 為 1 年）
4. **Sub-cap**：第三人違約連帶責任 cap NT$50 萬 / 單一事件，不直接連動到合約主違約金

## Fallback 1
員工違約 receiving party 連帶 + 留 due care defense（員工 NDA 訓練 + 內部 SOP 紀錄）+ 離職 2 年內可連帶。
Sub-contractor 違約 receiving party 連帶 + sub-cap NT$50 萬 / 單一事件 + 須事前以書面同意之 sub-contractor 名單才連帶。

## Fallback 2
員工違約 receiving party 連帶（含離職員工 5 年內）+ 接受 receiving party 須以書面確認員工 NDA 簽訂時生效。
Sub-contractor 違約 cap NT$100 萬 / 單一事件 + 主合約違約金不雙重計算。

## 為什麼這條重要
這條決定 NDA 真實 exposure ceiling。沒有 sub-cap 的 cascade clause = 一個員工/一個 OEM 廠商失誤就觸發主合約懲罰性違約金（典型 NT$100 萬）+ 律師費。

對 SME receiving party 是 catastrophic risk：員工流動性 + sub-contractor 多元化的場景下，原 NDA 簽訂時雙方對等的設計，因為連帶責任 cascade 變成單邊極端 exposure。

近年實務趨勢：法院對企業負連帶責任之認定逐步傾向採用「合理控制」+「due care defense」框架（民法 §188 / §224 commentary），但合約文字若直接寫「視為 receiving party 違約」可能排除這些抗辯。

## 替代條款文字
> 收受方就其下列人員之違反本合約規定之行為負連帶責任：(a) 在職員工 + 受任處理本合約所涉業務之員工；(b) 受任處理本合約所涉業務之承攬商、外包廠商或代理人。但收受方就下列情形不負連帶責任：(i) 收受方已盡相當注意義務（已於該員工 / 承攬商簽訂與本合約條款實質相同之保密合約 + 已給予合理之保密教育訓練）者；(ii) 員工於離職 2 年後之違反行為，但揭露方能證明該員工係受收受方安排從事規避本合約之行為者除外；(iii) 收受方未經事前書面同意之 sub-tier 承攬商之違反行為。就承攬商 / 外包廠商違反本合約之單一事件，收受方之連帶責任以新台幣 50 萬元為上限，但故意行為不在此限。

## 相關規範與學說參考
<!-- v0.3.5: NDA-native fallback baseline; bundled statute references
     cross-checked at https://law.moj.gov.tw on case_citations_verified_at.
     No bundled case citations — TW commentary tradition cites statute
     + 學說 over specific anchor cases for this doctrine area. -->

- **民法 §188** 受僱人因執行職務不法侵害他人權利者，僱用人連帶負損害賠償責任；但僱用人已盡相當注意者，不負賠償責任 — 提供 due care defense 之法源
- **民法 §224** 履行輔助人責任 — 但侵權法 + 契約法區分上 due care defense 適用範圍不同
- 王澤鑑《侵權行為法》「企業責任之擴張與限縮」(2010, 民法 §188 commentary) — 連帶責任成立要件 + due care defense 之 burden shift 分析
- ⚠️ 引用具體判決前，請於 https://judgment.judicial.gov.tw 檢索查證
