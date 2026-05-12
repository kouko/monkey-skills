---
clause_id: REPLACE_ME                            # required, kebab-case (e.g. confidentiality)
contract_types_applicable: [SaaS, MSA, NDA]      # optional; common defaults
walk_away_triggers:                              # required, >= 1
  - "REPLACE_ME_TRIGGER_1"
  # - "REPLACE_ME_TRIGGER_2"
escalate_to: "REPLACE_ME"                        # required (e.g. 法務主管 / GC / 老闆兼法務)
risk_default: yellow                             # required ∈ {green, yellow, red}
currency: USD                                    # optional ∈ {USD, TWD}
last_updated: YYYY-MM-DD                         # ISO date — bumped on every save
owner: REPLACE_ME                                # optional
source_type: user_playbook                       # required ∈ {user_playbook, bundled_fallback, advisory}
# variant_upgrade_offered: true                  # set automatically by skill when a flat→variant upgrade is declined
---

# REPLACE_ME (中文 clause name)

## 偏好立場
<REPLACE_ME: 我方理想立場，1-3 句>

## Fallback 1
<REPLACE_ME: 第一退讓階梯>

<!-- ## Fallback 2 (optional)
<REPLACE_ME: 第二退讓階梯> -->

## 為什麼這條重要
<REPLACE_ME: 業務翻譯，一句話告訴非法務>

<!-- ## 替代條款文字 (optional, for redline output to paste)
<REPLACE_ME: 可直接用的條款 text> -->

<!-- ## 相關判例 (optional)
<REPLACE_ME: 司法院判決字號 / 學說 reference> -->
