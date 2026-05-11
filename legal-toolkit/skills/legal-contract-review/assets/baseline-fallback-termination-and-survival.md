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
last_updated: 2026-05-11
statute_verified_at: 2026-05-12  # v0.3.1+: bundled statute references cross-checked at https://law.moj.gov.tw; refresh annually or after major legislative amendment
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

## 相關判例
- 最高法院 100 年度台上字第 1166 號（重大違約之認定）
- 最高法院 95 年度台上字第 2755 號（任意終止權之限制）
