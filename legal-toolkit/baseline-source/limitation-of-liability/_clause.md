---
clause_id: limitation-of-liability
contract_types_applicable: [SaaS, MSA, 服務委任, 採購, 經銷]
has_variants: true
market_data: |
  WorldCC 2024 Benchmark: median LoL cap = 12 個月服務費 (SaaS / MSA)；
  IP infringement carve-out 出現率 = 78% (deal_size > USD 100K)；
  super-cap 出現率 = 42% (deal_size > USD 1M)。
last_updated: 2026-05-12
owner: "[請編輯為你的姓名]"
source_attribution: |
  WorldCC 2024 Most Negotiated Terms (LoL) + ContractKen LoL Playbook +
  理律 newsletter 2023-12「責任上限條款實務」+ 民法 §227 §247-1 +
  公平交易法 §25 不公平交易條件
---

# 責任上限 (Limitation of Liability)

本條款依 deal_size 分三 variant — 詳細 walk_away / fallback / preferred
立場見對應 `<variant-id>.md`。

## 為什麼這條重要 (適用於所有 variant)

LoL 是 portfolio-level 風險上限的設計工具，不是單一合約的「賠多少」議題。
工具邏輯：cap 太低 → 對方違約時我方無法 recover 真實損失；cap 太高 →
我方違約時暴露超出可控範圍的賠償。

業界 baseline 採 12 個月服務費為 cap，附 IP 侵權 / 違反 confidentiality /
重大過失 / 故意行為 4 大 carve-out（不受 cap 限制）。對 enterprise 客戶
（deal_size > USD 1M）常加 super-cap = 24-36 個月服務費。

## 替代條款文字 (shared template — variant-specific cap 數值見對應 variant)

> "EXCEPT for liability arising from (a) breach of confidentiality
> obligations, (b) infringement of third-party intellectual property
> rights, (c) gross negligence or wilful misconduct, or (d) indemnification
> obligations under Section [N], each Party's total cumulative liability
> under this Agreement is limited to [CAP] in the aggregate. IN NO EVENT
> will either Party be liable for indirect, consequential, special,
> incidental, or punitive damages, including lost profits, lost revenue,
> or lost data."

## 相關判例
- 智慧財產法院 99 年度民營訴字第 8 號（LoL 條款違反 §247-1 顯失公平）
- 最高法院 99 年度台上字第 1167 號（責任限制條款之效力範圍）
