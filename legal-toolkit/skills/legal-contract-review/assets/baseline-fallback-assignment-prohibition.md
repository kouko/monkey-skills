---
clause_id: assignment-prohibition
contract_types_applicable: [NDA, mutual NDA, 服務委任, 採購, 經銷, MSA]
walk_away_triggers:
  - "全部或一部禁止轉讓，且違反條款轉讓無效（無 affiliate / successor carve-out）"
  - "禁止 change of control（公司被併購視為轉讓需對方同意）"
  - "雙方均不得轉讓但實際操作不對等（receiving party 業務變動較頻繁）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / 董事會]"
escalate_to_hint: "通常是 GC；涉及 M&A 場景必董事會 / 老闆"
risk_default: yellow
currency: TWD
last_updated: 2026-05-12
statute_verified_at: 2026-05-12  # v0.3.1+: cross-checked at https://law.moj.gov.tw
case_citations_verified_at: 2026-05-12  # v0.3.2+: verify-or-removed at https://judgment.judicial.gov.tw
owner: "[請編輯為你的姓名]"
source_type: bundled_fallback
source_attribution: |
  v0.3.4 NDA dogfood independent audit (2026-05-12) NEW finding: §11
  「除經雙方事先書面同意外，不得將其全部或一部讓與第三人；任何違反
  本條約定之讓與行為均屬無效」屬 M&A blocker — 公司被併購 / 換手控
  制權時，permitted-affiliate / successor 轉讓被排除。v0.3.0/v0.3.1
  /v0.3.4 三輪 audit 都漏抓因為 SaaS-shaped fallback 未涵蓋此 NDA-
  native pattern. v0.3.5 Phase 1.9 addition per ROADMAP §1.6.2.
---

# 轉讓禁止之 carve-out（Assignment-Prohibition Carve-Outs）

## 偏好立場
合約轉讓禁止條款，須保留下列 **permitted assignment** carve-out：

1. **Affiliate 轉讓**：轉讓予具有共同控制權之關係企業（母公司 / 子公司 / 兄弟公司）— 無須對方同意
2. **Successor 轉讓**：因合併 / 收購 / 資產交易而由 successor entity 承接本合約 — 通常須事前通知但非必同意
3. **Permitted financing**：轉讓予 lender 作為融資擔保（須附 lender carve-out — change of control 不視為違約）
4. **書面通知條款**：上述 carve-out 須事前 N 日書面通知對方（建議 30 日）
5. **Conditional consent**：對 carve-out 外之轉讓須對方書面同意，但「同意不得無理拒絕（consent shall not be unreasonably withheld）」

## Fallback 1
- Permitted affiliates ✓
- Permitted successors（M&A 場景）✓ 加事前 30 日書面通知
- Permitted lender carve-out ✓
- Consent for other assignments ✓ 加「不得無理拒絕」

## Fallback 2
- Permitted successors（M&A）✓ 加事前 30 日書面通知
- 其他需 consent — without "不得無理拒絕" 文字（雙方信任度較高 / 早期 NDA 可接受）

## 為什麼這條重要
**M&A blocker 風險**：當我方被收購 / 賣掉 / 重組時，successor entity 接手本合約需要對方同意。如果對方策略性拒絕（典型出價競爭情境），我方 M&A 交易 valuation 直接受影響。

具體 exposure：
- 我方公司被收購 → buyer 須額外取得對方同意（否則合約終止 / 違約）→ deal valuation 折損
- 我方拆分子公司 → 子公司無法承接本合約 → 業務移轉受阻
- 我方接受 strategic investor → investor 取得控制權 → 可能被解讀為「換手控制權」= 轉讓

**對 SME 特別敏感**：SME 階段公司架構變動頻繁（增資 / 重組 / 設子公司）。沒有 permitted affiliate carve-out 的合約 = 每次內部重組都要對方同意 = ops friction。

**標準業界做法**：M&A 律師審閱合約時，permitted affiliates + permitted successors 是 NDA / MSA / 服務合約之 baseline carve-out。不寫 = 不專業。

## 替代條款文字
> 關於本合約之所有權利與義務，除經雙方事先書面同意外，不得將其全部或一部讓與第三人。但下列情形不在此限：(a) 任一方得將其於本合約項下之權利義務全部讓與其關係企業（包含母公司、子公司、兄弟公司），無須他方同意，但應於讓與生效前 30 日內以書面通知他方；(b) 任一方因合併、收購、出售絕大部分資產或其他類似之 corporate transaction，將本合約由 successor entity 承接者，無須他方同意，但應於 transaction 完成後 30 日內以書面通知他方；(c) 任一方得將本合約項下之金錢請求權轉讓予 lender 作為融資擔保，且 lender 行使該擔保不視為本條意義之轉讓。除前述 (a)~(c) 之 carve-out 外，其他轉讓行為須經他方事前書面同意，但同意不得無理拒絕。

## 相關規範與學說參考
<!-- v0.3.5: NDA-native fallback baseline; bundled statute references
     cross-checked at https://law.moj.gov.tw on case_citations_verified_at. -->

- **民法 §294** 債權讓與通知 — TW 法之轉讓 baseline rule
- **民法 §297** 債權讓與之效力 — 通知為生效要件
- **公司法 §316-1 / §316-2** 公司分割 + 合併之 successor 承接權利義務 — 法定承繼路徑
- **企業併購法 §22 / §23** 概括承受 — M&A 場景之法定承受機制
- 王文宇《商事法論》「契約承擔與企業併購」(2015 ed., 企業併購 §22 commentary) — successor entity 承接合約權利義務之 doctrine
- ⚠️ 引用具體判決前，請於 https://judgment.judicial.gov.tw 檢索查證；註：M&A 場景下 successor 是否需對方同意之判決見解分歧，視合約文字而定，建議以明文 carve-out 取代依賴判例
