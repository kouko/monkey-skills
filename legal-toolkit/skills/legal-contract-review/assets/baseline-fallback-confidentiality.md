---
clause_id: confidentiality
contract_types_applicable: [SaaS, MSA, NDA, 採購, 服務委任]
walk_away_triggers:
  - "單方面義務（只我方有保密義務，對方無對等義務）"
  - "永久保密（無 termination / 無 期限，影響營運自由）"
  - "保密範圍未定義（all info / any communication 等 over-broad 寫法）"
  - "Residual knowledge clause 完全排除（限制員工跳槽後正常工作能力）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / 部門主管]"
escalate_to_hint: "通常是 法務主管 / GC / 部門主管 / 老闆兼法務"
risk_default: yellow
currency: USD
last_updated: 2026-05-12
statute_verified_at: 2026-05-12  # v0.3.1+: bundled statute references cross-checked at https://law.moj.gov.tw; refresh annually or after major legislative amendment
case_citations_verified_at: 2026-05-12  # v0.3.2+: all previously-shipped judicial case citations verified-or-removed at https://judgment.judicial.gov.tw
owner: "[請編輯為你的姓名]"
source_type: bundled_fallback
source_attribution: |
  WorldCC 2024 Benchmark (Top 10 Most-Negotiated Terms) + ContractKen Confidentiality Playbook +
  理律法律事務所 newsletter 2023-09「機密資訊條款實務」+ 民法 §247-1 定型化契約條款顯失公平
---

# 保密條款 (Confidentiality)

## 偏好立場
雙向保密義務（mutual NDA-style），保密期限 **3-5 年**（不寫永久），
機密資訊範圍**明確定義**（必須以書面或口頭明示為機密，公開資訊 /
獨立開發 / 第三方合法取得 / 反向工程 4 大 carve-out 不可少）。
殘餘知識條款（residual knowledge）保留 — 員工腦中留下的概念性
記憶不受限制。

## Fallback 1
雙向 + 期限 3-5 年 + 加 carve-out「已知資訊」「獨立開發」即可接受。

## Fallback 2
單方面保密**僅在**對方有明顯資訊不對稱優勢時（例如供應商揭露
trade secret 給我方做評估），且期限 **不超過 3 年**，且我方無
permanent injunctive remedy 風險時可勉強接受。

## 為什麼這條重要
出商業祕密我們扛得起賠償風險，但若對方拿走我們的東西卻沒有
對等義務，這是 portfolio 性的不對稱 — 一份合約看不出來，
但 10 份合約之後，所有東西都是「對方的機密」。

## 替代條款文字
> "Each Party (the 'Disclosing Party') may disclose to the other
> Party (the 'Receiving Party') certain Confidential Information.
> 'Confidential Information' means information disclosed in
> writing and marked as confidential, or disclosed orally and
> identified as confidential at the time of disclosure and
> reduced to writing within 30 days. Confidential Information
> excludes information that: (a) is or becomes publicly known
> without breach of this Agreement; (b) was rightfully known by
> the Receiving Party prior to disclosure; (c) was independently
> developed by the Receiving Party without reference to
> Confidential Information; or (d) was rightfully received from
> a third party without confidentiality obligation. The
> Receiving Party will protect Confidential Information using
> the same degree of care it uses for its own confidential
> information of like importance, but not less than reasonable
> care. The Receiving Party's obligations under this Section
> survive for [3 / 5] years after termination."

## 相關規範與學說參考
<!-- v0.3.2 update: previously cited 智慧財產法院 102 年度民營訴字第 6 號 +
     最高法院 105 年度台上字第 1501 號. 2026-05-12 verification at
     https://judgment.judicial.gov.tw + ipc.judicial.gov.tw + 6law +
     TIPO 重要判決 returned zero hits for both. Replaced with statute +
     commentary doctrine per soft-citation rule (L7 Step 9.3.0). -->

- **營業秘密法 §2** 三要件（秘密性 / 經濟價值 / 合理保密措施）— 機密資料之 baseline definition；契約保密義務終止後是否仍受營業秘密法保護，視是否仍滿足三要件
- **營業秘密法 §11** 排除及防止侵害請求權 — civil injunctive relief 的法源（非 §11-1，§11-1 不存在）
- **勞動基準法 §9-1** 競業禁止四要件（2015/12 增訂）— 與保密義務不同，競業禁止有合理性審查、補償金、地域期間限制；NDA 內若混用兩種義務需區辨
- 王澤鑑《侵權行為法》commentary 對「殘餘知識」之分析（員工腦中概念性記憶不受營業秘密法限制；屬學說通說而非具體判例 anchor）
- ⚠️ 引用具體判決前，請於 https://judgment.judicial.gov.tw 檢索查證
