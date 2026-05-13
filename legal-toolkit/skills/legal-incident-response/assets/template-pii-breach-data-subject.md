<!--
  Skeleton: legal-incident-response / pii-breach / 當事人通知文
  zh-TW only per spec Q11 (no EN/JA variants in v0.4.2 scope)
  Variables marked {{name}} are filled by protocols/pii-breach.md (Task 5)
  Tone: 親和、平實、不使用法律術語；同理當事人關切
  Path A discipline: 平實用語；不引入 GDPR 翻譯詞彙（forbidden phrasings enumerated in scripts/grade_response.py PATH_A_ANTIPATTERNS）
-->

# 關於您的個人資料保護之重要通知

親愛的 {{company_name}} 客戶您好：

## 事件摘要

我們很抱歉地通知您，{{company_name}} 於 {{incident_date}} 發現一起個人資料安全事件。經初步調查，部分客戶之個人資料可能受到影響。我們在此向您致上最誠摯的歉意。

{{incident_plain_summary}}

## 您的資料是否受到影響

本次事件可能影響的個人資料類別包括：

{{data_categories_affected}}

如需確認您的帳號是否在受影響範圍，您可以：

1. 登入 {{customer_account_url}} 查看本公司於帳號訊息中的個別通知
2. 來信至 {{dpo_email}} 詢問

## 本公司已採取的措施

為保護您的權益，本公司已立即執行下列措施：

{{containment_actions_consumer_facing}}

本公司亦已依個人資料保護法施行細則第 22 條規定，向主管機關（個人資料保護委員會籌備處）即時通報本事件。

## 建議您可以做的事

為進一步保障您的個人資料安全，我們建議您：

{{recommended_user_actions}}

如您發現任何異常情形（例如收到可疑訊息、帳號異常登入），請立即聯絡本公司客服。

## 您的權利

依個人資料保護法第 3 條，您對個人資料享有下列權利：

- 查詢或請求閱覽
- 請求製給複製本
- 請求補充或更正
- 請求停止蒐集、處理或利用
- 請求刪除

行使方式：來信至 {{dpo_email}}。

## 聯絡資訊

- **個人資料保護聯絡窗口（DPO）**：{{dpo_email}}
- **客戶服務專線**：{{customer_service_contact}}
- **客戶服務時間**：{{customer_service_hours}}

如您對本通知或本次事件有任何問題，歡迎透過上述管道與我們聯絡。本公司全體同仁將秉持最高誠意，協助您解決相關疑慮。

---

<!--
  Variable semantics for date fields:
  - {{incident_date}}: when the incident OCCURRED (used in 事件摘要 body)
  - {{notification_date}}: when THIS LETTER is sent (used in落款 sign-off)
  Both YYYY-MM-DD format; almost always notification_date > incident_date.
-->

{{company_name}} 敬上

{{notification_date}}
