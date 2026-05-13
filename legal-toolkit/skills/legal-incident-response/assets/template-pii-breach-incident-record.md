<!--
  Skeleton: legal-incident-response / pii-breach / 內部事件記錄
  Internal audit document — NOT for external eyes
  Variables marked {{name}} are filled by protocols/pii-breach.md (Task 5)
  Path A discipline: use 「即時」 per 施行細則 §22; use 「委託者／受託者」 per 個資法 §4; use 「未滿十八歲」 per 民法 §12 (2023-01-01 修正)
  SOP-specific numeric thresholds MUST NOT appear in this body — they belong in compliance.md TBD migration tracker (Task 5)
  Forbidden phrasings are enumerated in scripts/grade_response.py PATH_A_ANTIPATTERNS
-->

# 個人資料外洩事故內部記錄

> 本文件為內部稽核用途，不對外公開。
> 如有外部揭露需求，請依「PDPC 通報文」與「當事人通知文」另行處理。

## §基本資訊

- **公司名稱**：{{company_name}}
- **事件編號**：{{incident_id}}
- **事件處理人（事件指揮官）**：{{incident_commander}}
- **記錄建立時間**：{{record_created_at}}
- **記錄最後更新**：{{record_last_updated}}

## §事件分類 + 嚴重度

- **事件類別**：個人資料外洩（pii-breach）
- **嚴重度**：{{severity_level}}（依公司資安事件分級標準）
- **是否涉及特種個資（個資法 §6）**：{{special_category_assessment}}
- **是否涉及跨境傳輸（個資法 §21）**：{{cross_border_assessment}}
- **是否涉及委託處理（個資法 §4）**：{{processor_involvement}}
- **是否涉及未滿十八歲當事人（民法 §12 修正 2023-01-01）**：{{minor_involvement}}

## §時間軸

| 時間 (ISO 8601) | 事件 | 來源 |
|---|---|---|
| {{event_discovery_iso}} | {{event_discovery_desc}} | {{event_discovery_source}} |
| {{event_initial_response_iso}} | {{event_initial_response_desc}} | {{event_initial_response_source}} |
| {{event_containment_iso}} | {{event_containment_desc}} | {{event_containment_source}} |
| {{event_pdpc_notify_iso}} | 即時通報 PDPC 籌備處 | 個資法施行細則 §22 |
| ⏳ 待 {{tbd_data_subject_notify_label}} | 受影響當事人通知作業完成 | TBD_PDPC_threshold |
| ⏳ 待 {{tbd_root_cause_label}} | 根因分析報告完成 | （內部稽核作業排程） |
| ⏳ 待 TBD_PDPA_effective_date | 視 §12 施行日期是否在事故時點前後，補正通報內容 | TBD_PDPA_effective_date |

## §影響範圍

- **受影響筆數**：{{affected_count}}
- **個資類別**：
{{data_categories_bullets}}
- **特種個資判定**（個資法 §6）：{{special_category_detail}}
- **跨境傳輸判定**（個資法 §21）：{{cross_border_detail}}
- **委託受託關係判定**（個資法 §4）：{{processor_detail}}

## §採取措施

### 技術面（Technical Actions）

{{technical_actions_bullets}}

### 行政面（Administrative Actions）

{{administrative_actions_bullets}}

### 法源依據

- 個資法 §27（安全維護措施）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=27
- 個資法 §12（個資外洩通知義務）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=12
- 個資法 §4（委託處理 + 委託者全責）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=4
- 個資法 §6（特種個資）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=6
- 個資法 §21（跨境傳輸）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=21
- 個資法施行細則 §22（即時通報基準）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22

## §責任分工

| 角色 | 姓名 | 負責項目 | 聯絡方式 |
|---|---|---|---|
| CEO | {{ceo_name}} | 對外發言、最終裁決 | {{ceo_contact}} |
| CTO | {{cto_name}} | 技術根因調查、系統復原 | {{cto_contact}} |
| DPO（個資保護聯絡人） | {{dpo_name}} | PDPC 通報、當事人通知、法源檢視 | {{dpo_email}} |
| 法務 | {{legal_lead_name}} | 法源依據、合約責任分析、外部律師聯絡 | {{legal_lead_contact}} |
| 客服 | {{cs_lead_name}} | 當事人查詢應對、客服話術 | {{cs_lead_contact}} |
| 資安 | {{security_lead_name}} | 事件鑑識、入侵痕跡分析 | {{security_lead_contact}} |

{{external_counsel_block}}

## §證據保全

{{evidence_preservation_bullets}}

## §後續行動清單

{{follow_up_actions_bullets}}

## §法務檢視註記

- 本事件之 PDPC 通報已依施行細則 §22「即時」原則辦理。
- 個資法 §12（2025-11 公布）目前 施行日期未定（TBD_PDPA_effective_date）；若於本事件後續處理期間施行，須補正通報內容。
- 委託受託關係（如涉及）依個資法 §4：委託者就受託者之蒐集、處理、利用負同一責任。
- 若涉及未滿十八歲當事人，依民法 §12 修正 2023-01-01 起成年年齡為 18 歲，未滿十八歲者由法定代理人代行個資權利。

## §版本控制

| 版本 | 日期 | 修訂者 | 修訂內容 |
|---|---|---|---|
| {{version}} | {{version_date}} | {{version_author}} | {{version_changes}} |
