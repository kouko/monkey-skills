---
clause_id: indemnification
contract_types_applicable: [SaaS, MSA, 服務委任, 採購, 經銷, 授權]
has_variants: true
market_data: |
  WorldCC 2024 Benchmark: 雙向 indemnification 出現率 = 65% (B2B SaaS)；
  IP 侵權第三方索賠 indemnification = 88% (服務提供者扛)；
  data breach indemnification = 52% (deal_size > USD 500K)。
last_updated: 2026-05-12
owner: "[請編輯為你的姓名]"
source_attribution: |
  WorldCC 2024 Most Negotiated Terms (Indemnification) + ContractKen
  Indemnification Playbook + 民法 §227 §184 §188 + 公平交易法 §25
---

# 賠償義務 (Indemnification)

依 deal_size 分三 variant — walk_away / fallback / preferred 立場見對應
`<variant-id>.md`。

## 為什麼這條重要 (適用於所有 variant)

Indemnification 是合約裡的「兜底保險」條款。設定錯就把雙邊的義務變成
單邊保險：對方覺得「反正出問題你會 indemnify 我」，我方覺得「對方違約
我自己扛」。

業界 baseline：
- **第三方索賠**（IP 侵權 / 系統服務缺陷 / 違反 confidentiality 致對方
  被訴）→ 服務提供者 indemnify
- **資料外洩賠償**（個資外洩致 data subject 索賠）→ 視責任歸屬分擔
- **監管罰款**（因對方違規導致主管機關開罰）→ 違規方 indemnify

關鍵設計：
1. **Trigger conditions** 明確 — 不接受「any claim arising from your
   activities」這種寬鬆寫法
2. **Notice + cooperation** 義務雙向 — 被索賠方須 prompt notice，並
   配合 indemnifying party 抗辯
3. **Settlement consent** — indemnifying party 不可單方 settle 涉及
   admit liability 或 affect business reputation 的條款
4. **Cap interaction** with LoL — IP 侵權 indemnification 通常 carve-out
   from LoL cap（design coupling with LoL clause）

## 替代條款文字 (shared template)

> "Each Party (the 'Indemnifying Party') will defend, indemnify, and
> hold harmless the other Party from any third-party claim arising from
> (a) the Indemnifying Party's breach of [confidentiality / IP / data
> protection] obligations, (b) the Indemnifying Party's gross negligence
> or wilful misconduct, or (c) [variant-specific triggers — see variant
> file]. The Indemnified Party will: (i) provide prompt written notice
> of the claim; (ii) reasonably cooperate in the defence at the
> Indemnifying Party's expense; and (iii) not settle the claim without
> the Indemnifying Party's prior written consent. The Indemnifying Party
> may not settle any claim that admits liability or imposes non-monetary
> obligations on the Indemnified Party without prior written consent."

## 相關判例
- 智慧財產法院 100 年度民營訴字第 32 號（IP 侵權 indemnification）
- 最高法院 96 年度台上字第 2032 號（不完全給付 + 第三人責任分擔）
