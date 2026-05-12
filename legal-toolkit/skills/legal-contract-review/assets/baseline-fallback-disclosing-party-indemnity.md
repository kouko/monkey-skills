---
clause_id: disclosing-party-indemnity
contract_types_applicable: [NDA, mutual NDA, 服務委任, 採購]
walk_away_triggers:
  - "揭露方無限制 indemnify receiving party 對所有刑事 / 行政 / 民事 exposure（未設範圍 / 上限 / carve-out）"
  - "indemnify 含合理性與非合理性主張通包（receiving party 主張即觸發）"
  - "mutual NDA 結構下兩方都當揭露方時 = 雙方 unlimited cross-indemnity"
  - "indemnify 範圍含「收受方因取得行為而受之任何損害」(open-ended)"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常是 GC；mutual NDA 場景兩邊主管法務雙簽"
risk_default: red
currency: TWD
last_updated: 2026-05-12
statute_verified_at: 2026-05-12  # v0.3.1+: cross-checked at https://law.moj.gov.tw
case_citations_verified_at: 2026-05-12  # v0.3.2+: verify-or-removed at https://judgment.judicial.gov.tw
owner: "[請編輯為你的姓名]"
source_type: bundled_fallback
source_attribution: |
  v0.3.4 NDA dogfood independent audit (2026-05-12) NEW finding: §5.1
  揭露方擔保「收受方不因取得行為而受任何刑事訴追、行政處罰或民事
  求償」屬 finding #1-tier item — mutual NDA 兩方都當揭露方時 = 雙方
  unlimited cross-indemnity，但 v0.3.0/v0.3.1/v0.3.4 三輪 audit 都漏抓
  因為 SaaS-shaped fallback 未涵蓋此 NDA-native pattern. v0.3.5 Phase 1.9
  addition per ROADMAP §1.6.2 Deferred → NDA-native fallback baselines.
---

# 揭露方 indemnity 限縮（Disclosing-Party Indemnity Scope）

## 偏好立場
揭露方擔保 receiving party 不因取得 / 使用 / 處理機密資料而受損害之 indemnity，限於：

1. **範圍限縮**：僅限揭露方對該機密資料「有揭露權」之擔保（例如：揭露方之 IP / 自有 trade secret）—— 非無限保證「不受任何法律追訴」
2. **時效**：indemnity 義務於合約期間 + 終止後 N 年（建議 3 年）
3. **Carve-out**：receiving party 之故意 / 重大過失 / 自身違法行為造成之損害不在 indemnify 範圍
4. **Cap**：indemnity 金額 cap（建議 receiving party 一年內因本合約收受之揭露總價值 × 1-2 倍）
5. **程序**：receiving party 須在收受訴訟通知後 X 日內書面通知揭露方，由揭露方主導訴訟 / 和解（control rights）

## Fallback 1
- 範圍：限於揭露方有揭露權之擔保 + 主張第三人 IP 侵權之 carve-out
- 時效：終止後 3 年
- Cap：年內合約價值 × 2
- 含 receiving party 故意 / 重大過失 carve-out
- 含 receiving party 須書面通知 + 揭露方控制訴訟之程序

## Fallback 2
- 範圍：限於揭露方有揭露權之擔保
- 時效：終止後 5 年
- Cap：年內合約價值 × 5（或固定 cap NT$500 萬）
- 含 receiving party 故意 carve-out
- 含 receiving party 須書面通知之程序

## 為什麼這條重要
**Mutual NDA 場景**：本合約雙方都既是揭露方又是 receiving party。揭露方 unlimited indemnity 寫成「不因取得行為而受任何刑事訴追、行政處罰或民事求償」的時候 = 兩方在 mutual NDA 結構下都被綁定 unlimited cross-indemnity。

具體 exposure：
- 揭露方角色：對方因取得我方資料導致任何法律 exposure 都要賠（含合理 / 不合理）
- Receiving party 角色：我方因取得對方資料導致任何法律 exposure，對方都要賠
- 雙刃但都是 unlimited — 在 SME 之間是 catastrophic risk

對特定情境特別致命：
- 訴訟方主張機密資料含未公開財務數據 → 揭露方須 indemnify receiving party 對該主張之防禦費 + 任何 settlement
- 第三方主張機密資料侵害其 IP → 揭露方須擔保
- 政府機關主張該機密資料含個資 / 涉密 → 揭露方須 indemnify 行政處罰

實務上 NDA indemnity 應該**有界**，要求 receiving party 對「有揭露權」之擔保 + 限縮 carve-out，是大型律所 NDA template 之 baseline。

## 替代條款文字
> 揭露方擔保其對所揭露之機密資料具有合法揭露權。收受方因合法使用該機密資料而因揭露方所揭露之機密資料本身侵害第三人智慧財產權，致受第三人請求或主張時，揭露方應負損害賠償責任，但下列情形不在此限：(a) 收受方故意或重大過失之行為；(b) 收受方違反本合約其他條款之使用方式；(c) 收受方未於收受第三人主張或請求通知後十四日內書面通知揭露方者。揭露方之賠償責任以收受方因本合約於前一年度給付揭露方之合約對價之二倍為上限。揭露方有權主導前述第三人主張之訴訟 / 和解程序。

## 相關規範與學說參考
<!-- v0.3.5: NDA-native fallback baseline; bundled statute references
     cross-checked at https://law.moj.gov.tw on case_citations_verified_at. -->

- **民法 §247-1** 定型化契約顯失公平 — applicability_caveat：本約若為 1-on-1 negotiated B2B 而非定型化契約，§247-1 適用空間有限，僅作 talking point
- **民法 §227** 不完全給付 baseline — disclosing party 違反擔保之 baseline 責任
- **民法 §229 / §230** 給付遲延 / 不能 — indemnity 不履行之 default rules
- **公司法 §1** 公司負責人之忠實義務 — mutual NDA 之 unlimited indemnity 可能違反董事會審議規範
- 王澤鑑《債法原理》「契約上擔保責任之限縮」(commentary on §227, §247-1) — 商業 indemnity 限縮 doctrine
- ⚠️ 引用具體判決前，請於 https://judgment.judicial.gov.tw 檢索查證
