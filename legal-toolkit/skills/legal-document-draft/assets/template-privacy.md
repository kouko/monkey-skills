<!--
  Skeleton: legal-document-draft / privacy mode
  Citations hardcoded from references/statute-citations.md
  Variables marked {{name}} are filled by protocols/draft.md
  Safe defaults applied for items deferred to PDPC 子法 (see references/tbd-migration-template.md)
-->

# {{company_name}} 隱私權政策

**生效日期**: {{effective_date}}
**最後更新**: {{last_updated}}

## 一、蒐集者身分

蒐集者：{{company_name}} (統一編號 {{company_id}})
登記地址：{{registered_address}}
聯絡：{{general_contact_email}}
個人資料保護聯絡人 (DPO)：{{dpo_name}} ({{dpo_email}})

(法源：個資法 §8 第一項第一款 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=8)

## 二、蒐集目的

本公司蒐集個人資料之主要目的：
{{collection_purposes_bullets}}

(法源：個資法 §8 第一項第二款)

## 三、蒐集個資類別

本公司蒐集之個人資料類別：
{{collected_categories_bullets}}

如蒐集 §6 特種個資 ({{special_category_handling}})，將另行書面同意。

(法源：個資法 §8 第一項第三款 + §6 + §9)

## 四、利用期間、地區、對象、方式

- 期間：{{retention_period}}
- 地區：{{usage_regions}}
- 對象：本公司及{{third_party_categories}}
- 方式：{{processing_methods}}

(法源：個資法 §8 第一項第四款 + §5)

## 五、當事人權利

依個資法 §3，您有以下權利：
- 查詢或請求閱覽
- 請求製給複製本
- 請求補充或更正
- 請求停止蒐集、處理或利用
- 請求刪除

行使方式：致函或寄送電子郵件至 {{dpo_email}}。

(法源：個資法 §3 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=3)

## 六、不提供個人資料之影響

當事人若不提供必要個人資料，可能無法使用 {{product_or_service_name}} 之全部或部分服務功能。

(法源：個資法 §8 第一項第六款)

## 七、第三方 SDK / 服務提供者揭露

本公司於提供服務時使用下列第三方 SDK / 服務：
{{third_party_sdks_bullets}}

如有跨境傳輸個資至下列國家 / 地區：
{{cross_border_destinations_bullets}}

跨境傳輸已採適當保護措施 (合約 / 標準條款 / 主管機關公告適格名單)。

(法源：個資法 §21 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=21)

## 八、個人資料外洩之通報

當本公司察覺個人資料遭非法蒐集、處理、利用或洩漏時，將依個資法相關規定**即時**通報主管機關，並通知受影響當事人。

<!--
  Safe default: 施行細則 §22 「即時」(see references/pdpa-current-state.md)
  TBD_PDPC_timeframe: When PDPC publishes 通報辦法 specifying timeframe, replace
  「即時」with the specific timeframe per references/tbd-migration-template.md
  TBD_PDPC_threshold: If 通報範圍 announced, add threshold-aware language here
-->

(法源：個資法施行細則 §22 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22)

## 九、安全維護措施

本公司採取下列安全維護措施：
{{security_measures_bullets}}

(法源：個資法 §27 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=27)

<!-- TBD_PDPA_audit_framework: When Art. 20-1 effective + PDPC 稽核辦法 published, add audit framework subsection here -->

## 十、未成年人保護

如使用者未滿七歲，不具行為能力，應由父母或監護人代為同意；未滿二十歲限制行為能力人，應經父母或監護人同意。本公司不主動蒐集未成年人之非必要個人資料。

(法源：民法 §12 + §13 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=12)

## 十一、政策修訂與生效

本政策得不定期修訂，修訂時將於 {{product_url_or_app}} 公告。修訂後之政策自公告日 30 日後生效，或您繼續使用服務時即視為同意。

## 十二、爭議處理

本政策依中華民國法律解釋。爭議發生時，雙方同意以{{preferred_court}}為第一審管轄法院。

## 十三、聯絡

如對本政策有疑問，請聯絡：
- 一般：{{general_contact_email}}
- 個人資料保護：{{dpo_email}}
