<!--
  Skeleton: legal-document-draft / dpa mode
  Citations hardcoded from references/statute-citations.md
  Variables marked {{name}} are filled by protocols/draft.md
-->

# {{client_company_name}} 與 {{processor_company_name}} 個人資料委託處理協議

**簽訂日期**: {{effective_date}}

## 第一條 委託範圍

委託人 {{client_company_name}} 委託受託人 {{processor_company_name}} 處理下列個人資料：

- 個資類別：{{processor_data_categories}}
- 處理目的：{{processing_purpose}}
- 處理方式：{{processing_methods}}
- 處理期間：{{processing_period}}

(法源：個資法 §4 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=4)

## 第二條 受託人義務

受託人應遵守下列義務：

1. 依委託範圍處理個資；非經委託人書面同意，不得逾越委託範圍或為其他目的之利用。
2. 採取適當之安全維護措施 (§27 + 施行細則 §12)：{{processor_security_measures}}
3. 不得將委託處理之個資外洩予第三人。
4. 受託人之受僱人或受託處理之第三人，亦負本協議所定義務。
5. 配合委託人或主管機關之監督、稽核要求。

(法源：個資法 §8 + 施行細則 §12 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=12)

## 第三條 子委託 (再委託)

受託人非經委託人事前書面同意，不得將委託處理之個資再委託第三人。

如經同意之子委託，子受託人應遵守與本協議同等之義務，受託人對子受託人之行為負完全責任。

(法源：個資法 §4 第二項解釋)

## 第四條 個資外洩通報

受託人察覺個資遭非法蒐集、處理、利用或外洩時，應**即時**通知委託人，並提供下列資訊：

- 事件發生時間 (推定 / 實際)
- 影響個資類別 + 當事人估算數量
- 已採取之防止擴大措施
- 復原計畫與時程

委託人依個資法 §22 + 施行細則 §22 對主管機關通報之責任不因受託人之通知而免除。

<!--
  TBD_PDPC_timeframe: When PDPC publishes 通報辦法 specifying timeframe,
  replace 「即時」 with specific timeframe (see references/tbd-migration-template.md).
-->

(法源：個資法施行細則 §22 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22)

## 第五條 委託人之監督權

委託人對受託人之個資處理情形，得依下列方式行使監督權：

- 書面查詢
- 現場稽核 (預先通知 {{audit_notice_days}} 日以上)
- 委由第三方獨立稽核
- 要求受託人提供安全維護措施執行紀錄

受託人應配合，不得無正當理由拒絕。

## 第六條 委託終止後之處理

本協議終止後，受託人應於 {{post_termination_disposal_days}} 日內：

- 返還或銷毀全部受託處理之個資及其副本
- 出具書面證明返還或銷毀完成
- 如法律另有保存義務，僅得保留必要之最低限度

## 第七條 責任分配

依個資法 §4 解釋，委託人對受託人之違法行為負連帶責任。受託人若違反本協議致委託人受損害，應負損害賠償責任，賠償範圍包括：

- 委託人對當事人之賠償金
- 主管機關之行政罰
- 訴訟費用及合理律師費

(法源：個資法 §4 + §28-29 + 民法 §227 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=4)

## 第八條 通知方式

任何依本協議所為之通知，應寄送下列地址：

- 委託人 DPO：{{client_dpo_email}}
- 受託人 DPO：{{processor_dpo_contact}}

## 第九條 適用法律與管轄

本協議依中華民國法律解釋。爭議應以 {{preferred_court}} 為第一審管轄法院。

## 第十條 其他

- 本協議自雙方簽署日生效，有效期間至委託處理結束或本協議解除為止。
- 本協議修訂應經雙方書面同意。
- 本協議一式兩份，雙方各執一份為憑。

---

委託人：{{client_company_name}} (蓋章 / 代表簽名)
受託人：{{processor_company_name}} (蓋章 / 代表簽名)
日期：{{effective_date}}
