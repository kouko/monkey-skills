---
clause_id: ip-assignment-and-license
contract_types_applicable: [SaaS, MSA, 服務委任, 採購, 客製化開發, 授權]
walk_away_triggers:
  - "IP 全部讓渡無 background IP carve-out（我方原有 IP 一併移轉）"
  - "Work product IP 歸屬不明（未明定誰是 owner）"
  - "客戶資料 / 客戶 IP 被 service provider 取得使用權無 limit"
  - "Background IP license 範圍包含 sublicensable 但無 sub-licensee 限制"
  - "IP infringement warranty 受 LoL cap 限制"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常需 GC 簽核（IP 涉及核心資產）"
risk_default: red
currency: USD
last_updated: 2026-05-12
owner: "[請編輯為你的姓名]"
source_type: bundled_fallback
source_attribution: |
  WorldCC 2024 (IP Assignment Top 5 Most Negotiated) + ContractKen IP
  Assignment Playbook + 著作權法 §11-15（受雇 / 出資聘人關係）+
  專利法 §7-10 + 民法 §490 承攬人之報酬
---

# 智財權歸屬與授權 (IP Assignment & License)

## 偏好立場
**Three-tier IP framework**（最常見且穩定）：

### Tier 1 — Background IP
雙方各自 pre-existing IP 歸屬不變。雙方互不主張對方 background IP 的所有
權。雙方對自己的 background IP 維持 ownership。

### Tier 2 — Work Product IP（在合約期間產生）
- **客製化開發 / 服務委任**: work product 預設歸屬於 **付費方（客戶）**
- **SaaS / 軟體授權**: work product 預設歸屬於 **service provider**（客戶取得 license）
- **MSA + Statement of Work**: 由 each SoW 個別約定，預設承襲此 baseline

### Tier 3 — License Grants
- 對 work product 中含的 background IP：**limited, non-exclusive, royalty-free,
  worldwide license** 給對方僅供 work product 使用範圍
- 對對方資料 / 對方 IP：service provider 僅取得 **limited license** to perform
  the services（不可內部使用 / 訓練 / 商業化）
- **客戶資料**: service provider 處理客戶資料僅依合約 instructions，無
  derivative use / aggregated analytics carve-out 須明示同意

### IP Warranty + Indemnification
- 雙方各自保證其 background IP 不侵權 (warranty)
- IP 第三方索賠由 IP 提供方 indemnify，cap **carve-out from LoL**（unlimited）
- "Defend-and-indemnify" obligation: IP indemnifying party 主動 defend，
  不只 pay damages

## Fallback 1
Three-tier framework 保留 + work product 歸屬可依 SoW 個別調整 + IP
warranty 雙向但 cross-indemnity 可改為 pay-defense-costs（we control defence）。

## Fallback 2
僅當 deal 不涉及 work product 創作（pure SaaS subscription / 標準授權）：
- 簡化為 Tier 1 + Tier 3，無 Tier 2 work product 議題
- IP warranty 仍須雙向 + IP indemnification unlimited

低於此即觸發 walk_away（IP 是 portfolio-level 核心資產，red default 不可退讓）。

## 替代條款文字
> "Background IP. Each Party retains all right, title, and interest
> in its Background IP. Nothing in this Agreement transfers ownership
> of Background IP between the Parties.
>
> Work Product IP. Subject to payment in full of all fees, the
> [付費方/Service Provider] will own all right, title, and interest
> in the Work Product, including all intellectual property rights
> therein. The [other Party] hereby assigns to [付費方/Service
> Provider] all of its right, title, and interest in the Work Product
> upon creation. The [other Party] will execute any documents
> reasonably necessary to perfect such assignment.
>
> License Grants. Each Party grants to the other a limited,
> non-exclusive, royalty-free, worldwide license to use such Party's
> Background IP solely as necessary for the other Party's exercise
> of its rights or performance of its obligations under this
> Agreement. No license is granted by implication, estoppel, or
> otherwise.
>
> IP Warranty + Indemnification. Each Party warrants that its
> Background IP, as used in accordance with this Agreement, will
> not infringe any third-party intellectual property rights. Each
> Party will defend, indemnify, and hold harmless the other Party
> from any third-party claim alleging that such Party's Background
> IP infringes a third-party IP right. This obligation is not
> subject to the Limitation of Liability in Section [N]."

## 相關判例
- 智慧財產法院 100 年度民著訴字第 53 號（受雇關係 work product IP 歸屬）
- 最高法院 99 年度台上字第 1167 號（IP indemnification carve-out from LoL）
- 智慧財產法院 105 年度民營訴字第 17 號（pre-existing IP license scope）
