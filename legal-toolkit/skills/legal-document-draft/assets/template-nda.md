<!--
  Skeleton: legal-document-draft / nda mode
  Citations hardcoded from references/statute-citations.md
  Variables marked {{name}} are filled by protocols/draft.md
  Bilateral NDA template; for unilateral, COMPLY_CHECK adjusts wording.
-->

# {{party_a_name}} 與 {{party_b_name}} 保密協議

**簽訂日期**: {{effective_date}}

## 第一條 機密資訊定義

「機密資訊」係指雙方因 {{purpose_of_disclosure}} 而揭露之下列資訊，無論其載體：

- 商業策略、業務計畫、財務資料
- 技術、產品、製程、原始碼
- 客戶 / 供應商名單
- 內部會議紀錄、報價、討論草案
- 其他標示「機密」或於揭露時口頭聲明為機密之資訊

**例外** (Carve-outs)：機密資訊不包括：
1. 揭露前已為接受方合法知悉者
2. 揭露時或揭露後已為公眾所知 (非因接受方違反本協議所致)
3. 接受方自第三方合法取得，且該第三方無保密義務者
4. 接受方獨立開發，無須使用揭露方機密資訊者
5. 經揭露方事前書面同意公開者

## 第二條 雙方義務

接受方應：

1. 採取**至少與保護自身機密資訊相同**之注意義務，且不低於合理注意義務。
2. 僅用於本協議所載 {{purpose_of_disclosure}} 之目的。
3. 揭露範圍限於接受方之受僱人、顧問、或受託處理人，且其有合理需求知悉者；該等人員應受同等保密義務拘束，接受方對其行為負連帶責任。
4. 不得反向工程、解構、複製機密資訊。
5. 機密資訊應與其他資訊分離保管。

## 第三條 法律強制揭露

接受方因法律、法院命令或主管機關要求必須揭露機密資訊時：

- 應於可行範圍內事前通知揭露方
- 配合揭露方爭取保密處理 (e.g., protective order)
- 揭露範圍限於法律所要求之最低限度

## 第四條 保密期間

本協議之保密義務自簽訂日起生效，**繼續有效 {{survival_years}} 年**，**除非機密資訊已符合第一條 carve-outs 例外之一**。

<!--
  Authoring note (not for counterparty): 預設 survival period 來自
  legal-playbook/confidentiality.md；典型範圍 3-7 年；技術機密可延至
  10 年或永久。Override via session input if the deal warrants.
-->


## 第五條 違約救濟

如接受方違反本協議：

- **金錢損害賠償**：依民法 §227 (不完全給付) 應賠償揭露方所受損害及所失利益。
- **約定違約金**：每次違約 {{liquidated_damages}}，揭露方仍得就超過違約金部分請求賠償 (民法 §250 第二項)。
- **禁制令**：揭露方得請求法院命接受方停止違約行為，包括但不限於假處分。
- **返還義務**：機密資訊應於違約時或揭露方書面要求時 {{return_days}} 日內銷毀或返還，並出具書面證明。

(法源：民法 §227 + §250 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=227)

## 第六條 適用法律與管轄

本協議依中華民國法律解釋。爭議應以 {{preferred_court}} 為第一審管轄法院。

## 第七條 其他

- **完整協議**：本協議為雙方就機密資訊揭露之完整約定，取代雙方先前所有書面或口頭協議。
- **修訂**：本協議修訂應經雙方書面同意。
- **可分割性**：本協議任一條款被認定無效時，不影響其他條款之效力。
- **無放棄**：揭露方未即時行使任一權利，不視為放棄該權利。
- **轉讓限制**：未經對方書面同意，任一方不得將本協議權利義務轉讓予第三人。
- **正本份數**：本協議一式兩份，雙方各執一份為憑。

---

{{party_a_name}} (蓋章 / 代表簽名)
{{party_b_name}} (蓋章 / 代表簽名)
日期：{{effective_date}}
