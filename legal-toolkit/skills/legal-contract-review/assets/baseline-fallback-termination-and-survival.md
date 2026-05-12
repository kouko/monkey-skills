---
clause_id: termination-and-survival
contract_types_applicable: [SaaS, MSA, 採購, 服務委任, 經銷]
walk_away_triggers:
  - "單方面 termination for convenience（只對方可隨時終止，我方不可）"
  - "Termination 後立即停止服務（無 transition / wind-down period）"
  - "Survival clause 過廣（讓全部義務 indefinitely survive，特別是非合理性的）"
  - "對方違約後我方仍須履行義務 30+ 天（給對方修補機會但對方無對等義務）"
escalate_to: "[請編輯為你公司的角色：法務主管 / GC]"
escalate_to_hint: "通常是 法務主管；涉及刑責或重大違約則 GC"
risk_default: yellow
currency: USD
last_updated: 2026-05-12
statute_verified_at: 2026-05-12  # v0.3.1+: bundled statute references cross-checked at https://law.moj.gov.tw; refresh annually or after major legislative amendment
case_citations_verified_at: 2026-05-12  # v0.3.2+: all previously-shipped judicial case citations verified-or-removed at https://judgment.judicial.gov.tw
owner: "[請編輯為你的姓名]"
source_type: bundled_fallback
source_attribution: |
  WorldCC 2024 Benchmark + ContractKen Termination & Survival Playbook +
  民法 §254 (給付遲延之解除) + 民法 §263 (解除權之行使) +
  民法 §259 (解除契約之回復原狀義務) + 民法 §227 (不完全給付)
---

# 終止與存續 (Termination and Survival)

## 偏好立場
**雙方對等的 termination 權**：
- **For cause（重大違約）**: 雙方均可 — 給予 30 天 cure period + 書面 notice
- **For convenience（任意終止）**: 雙方均可 — 60-90 天 prior written notice，
  避免單方面條款
- **Wind-down period**: 終止生效後 30-60 天 transition，避免立即斷供
- **Survival clauses 限制範圍**: 僅 (a) 保密 / (b) IP / (c) 限定責任 / (d) 已產生的付款義務 / (e) 準據法與管轄 — 不接受其他義務 indefinitely survive

## Fallback 1
- For cause: cure period 縮短到 14-30 天
- For convenience: 30-60 天 notice
- Wind-down: 30 天
- Survival 範圍同偏好立場

## Fallback 2
僅 deal value < USD 100K 且關係短期時：
- 對方有 termination for convenience 但 notice ≥ 90 天
- 我方無對等權，但 cure period 延長到 60 天保護自己
- Wind-down 30 天

## 為什麼這條重要
合約進入 termination 通常是關係破裂的時刻 — 雙方信任降到最低。
這時 termination 條款規定的是「分手手續」: 誰先停、誰退款、
誰承擔正在進行的工作。Wind-down period 對我方很重要 —
若客戶突然斷服，業務 portfolio 內所有依賴此服務的 SLA 都會
連環違約。Survival 範圍若不限制，會讓某些義務（例如非
compete / non-solicit）變成永久包袱。

## 替代條款文字
> "Termination for Cause. Either Party may terminate this
> Agreement upon thirty (30) days' prior written notice to the
> other Party if the other Party materially breaches this
> Agreement and fails to cure such breach within such 30-day
> period. Termination for Convenience. Either Party may
> terminate this Agreement for any reason upon ninety (90) days'
> prior written notice to the other Party. Transition Period.
> Upon any termination, the Parties will cooperate in good faith
> for thirty (30) days following the effective date of
> termination to wind down active work. Survival. The
> following Sections survive termination of this Agreement:
> Confidentiality (Section [N]), IP (Section [N]), Limitation
> of Liability (Section [N]), Indemnification (Section [N] but
> only as to claims accrued prior to termination), Governing
> Law (Section [N]), and any payment obligations accrued prior
> to the effective date of termination."

## 相關規範與學說參考
<!-- v0.3.2 update: previously cited 最高法院 100 年度台上字第 1166 號 +
     最高法院 95 年度台上字第 2755 號. 2026-05-12 verification:
     both case-numbers returned zero hits across judicial.gov.tw +
     6law + firm commentary. Replaced with statute + commentary
     doctrine per soft-citation rule (L7 Step 9.3.0). -->

- **民法 §254** 給付遲延之解除 — 給付期間屆滿後須先催告（民法 §254 末段）+ 相當期限未為給付始得解除
- **民法 §255** 即時解除（非定期行為 + 性質上不能達契約目的時）
- **民法 §256** 給付不能之解除 — 全部給付不能與部分給付不能之區辨
- **民法 §263** 解除權之行使（單方意思表示 + 須準用§258關於通知）
- **民法 §259** 解除契約之回復原狀義務（雙方互負義務）
- **民法 §549** 委任契約之任意終止權 — 委任性質契約雙方原則可隨時終止（受任人對委任人負損害賠償）
- **民法 §227** 不完全給付之 baseline — 與材料瑕疵 §354 + 工作瑕疵 §493 之區辨
- 王澤鑑《債法原理》「契約解除之要件與效力」commentary — 重大違約之實務認定標準（commentary 通說，非具體判決 anchor）
- ⚠️ 引用具體判決前，請於 https://judgment.judicial.gov.tw 檢索查證；註：「重大違約」與「任意終止權限制」doctrine 之 anchor case 為動態演進，建議用 statute + commentary baseline 而非固定 case anchor
