<!--
  Skeleton: legal-incident-response / pii-breach / PDPC 通報文
  Citations hardcoded from references/statute-citations.md
  Variables marked {{name}} are filled by protocols/pii-breach.md (Task 5)
  Path A discipline: use 「即時」 per 施行細則 §22; use 「委託者／受託者」 per 個資法 §4; use 「未滿十八歲」 per 民法 §12 (2023-01-01 修正)
  SOP-specific numeric thresholds MUST NOT appear in this body — they belong in compliance.md TBD migration tracker
  Forbidden phrasings are enumerated in scripts/grade_response.py PATH_A_ANTIPATTERNS
-->

<!-- TBD_PDPC_notification_url: 籌備處 URL 未驗證；正式委員會掛牌後 update -->
<!-- TBD_PDPC_pending: PDPC 仍為籌備處階段；正式通報機制待掛牌後驗證 -->
<!-- TBD_PDPC_timeframe: 個資法 §12 §4 授權子法尚未發布；本文以施行細則 §22「即時」為安全基準 -->

<!--
  Variable semantics — date vs datetime:
  - {{notification_date}}: send date for header/footer; format YYYY-MM-DD
  - {{notification_datetime}}: same event at ISO 8601 timestamp precision;
    format YYYY-MM-DDTHH:MM±TZ; used in 說明 body where exact time matters
  Both should refer to the SAME instant; LLM should derive
  notification_date = notification_datetime.split("T")[0].
-->

# 個人資料外洩事故通報函

**發文機關**：{{company_name}}
**發文字號**：{{document_reference_number}}
**發文日期**：{{notification_date}}（事故發現後即時通報）

## 受文機關

個人資料保護委員會籌備處（法務部）

## 主旨

為通報本公司於 {{incident_datetime}} 發現之個人資料外洩事故，依個人資料保護法施行細則 §22「即時」通報原則辦理，請鑒核。

## 說明

一、**事故時間**

   - 發生時間：{{incident_datetime}}
   - 發現時間：{{discovery_datetime}}
   - 通報時間：{{notification_datetime}}（即本函送達時點）

二、**影響範圍**

   - 受影響當事人筆數：約 {{affected_count}} 筆
   - 受影響個資類別：
{{data_categories_bullets}}
   - 是否涉及個資法 §6 特種個資（病歷／醫療／基因／性生活／健康檢查／犯罪前科）：{{special_category_assessment}}
   - 是否涉及跨境傳輸：{{cross_border_assessment}}

三、**事故概要**

   {{incident_summary}}

四、**已採取之措施**

{{containment_actions_bullets}}

五、**法源依據**

   - 個人資料保護法 §12（個資外洩通知義務）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=12
   - 個人資料保護法 §27（安全維護措施）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=27
   - 個人資料保護法施行細則 §22（即時通報基準）：https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22

## 後續行動

一、本公司將持續調查事故根因，並依鈞處後續指示補充說明。
二、本公司刻正依個資法 §27 進行安全維護措施全面檢視，並於檢視完成後函覆鈞處。
三、對受影響當事人之通知作業：{{data_subject_notification_plan}}。
四、後續若鈞處公告通報範圍（個資法 §12 §2 授權子法）與通報時限細節（§12 §4 授權子法），本公司將依公告事項補正本通報內容。

## 聯絡窗口

**個人資料保護聯絡人（DPO）**：
- 姓名：{{dpo_name}}
- 電子郵件：{{dpo_email}}
- 電話：{{dpo_phone}}

{{external_counsel_block}}

---

謹此通報

{{company_name}}　謹啟
{{notification_date}}
