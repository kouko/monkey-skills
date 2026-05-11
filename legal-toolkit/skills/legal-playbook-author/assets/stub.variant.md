---
clause_id: REPLACE_ME                            # required, MUST match parent _clause.md
variant_id: REPLACE_ME                           # required, kebab-case (e.g. small-deal / gdpr-overlay)
gates:                                           # required — ABAC rule that selects this variant
  # example shapes — pick one or combine
  # deal-size-keyed:
  deal_size:
    gte: 100000
    lt: 1000000
  # jurisdiction-keyed:
  # data_subjects_jurisdiction:
  #   any_of: [EU, UK, EEA]
  # counterparty-keyed:
  # counterparty_type:
  #   eq: enterprise
walk_away_triggers:                              # required, >= 1
  - "REPLACE_ME_TRIGGER_1"
escalate_to: "REPLACE_ME"                        # required
risk_default: yellow                             # required ∈ {green, yellow, red}
currency: USD                                    # optional ∈ {USD, TWD}
last_updated: YYYY-MM-DD
source_type: user_playbook
---

# REPLACE_ME (variant 名稱, e.g. "Mid-deal LoL")

## 偏好立場
<REPLACE_ME: 在這個 variant 條件下的偏好立場>

## Fallback 1
<REPLACE_ME>

<!-- 共享 metadata (business 翻譯、替代條款 template、相關判例) 通常放在
     <clause-id>/_clause.md，本檔只放 variant-specific 內容。 -->
