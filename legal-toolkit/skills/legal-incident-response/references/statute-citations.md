# Statute citation index — IR-specific hardcoded URLs

> All URLs use `law.moj.gov.tw` (全國法規資料庫 — 法務部 maintained). URL pattern stable since ~2015.
> Source of truth: `legal-toolkit/scripts/canonical/legal-sources.json` (post-SP1 SoT); this file is the manual cross-reference for legal-incident-response template authoring.
> Scope: statutes referenced by PII-breach path (Phase C/1) and reusable by authority-letter / contract-breach paths.

## 個資法 (個人資料保護法, pcode I0050021)

- §4 (委託處理 + 委託者全責 — Taiwan PDPA 委託者／受託者 model): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=4
- §6 (特種個資 — 病歷／醫療／基因／性生活／健康檢查／犯罪前科): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=6
- §12 (個資外洩通知義務 — 2025-11 公布；施行日期未定): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=12
- §21 (跨境傳輸 — 主管機關公告限制): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=21
- §27 (安全維護措施 — 事故發生後復原與檢視之法源): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=27

Full text: https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0050021

## 個人資料保護法施行細則 (pcode I0050022)

- §22 (即時通報語言基準 — Taiwan PDPA breach notification timeframe standard): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22

Full text (last amended 2016-03-02; not yet updated for 2025/11 母法 amendments): https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0050022

## 民法 (pcode B0000001)

- §12 (成年年齡，2023-01-01 起為 18 歲): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=12
- §13 (七歲以上未成年〔即未滿十八歲〕限制行為能力): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=13
- §125 (一般時效 15 年): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=125
- §197 (侵權行為時效 2 年／10 年): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=197
- §227 (不完全給付): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=227
- §229 (給付遲延): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=229
- §234 (受領遲延): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=234
- §250 (違約金約定): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=250

Full text: https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=B0000001

## 公司法 (pcode J0080001)

- §202 (董事會職權 — 事件升級裁決法源依據): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0080001&flno=202

Full text: https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=J0080001

## 行政程序法 (pcode A0030055)

- §49 (主管機關公文書送達時程 — authority-letter path 回函時程基準): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=A0030055&flno=49

Full text: https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030055

## Path A discipline note

This file uses only the current Taiwan statutory language. Out-of-scope GDPR / legacy phrasings (enumerated in `scripts/grade_response.py` `PATH_A_ANTIPATTERNS` and in `references/pdpa-current-state.md` "Out of scope" section) are deliberately not reproduced here, so this file is itself safe to embed verbatim in published output.

Required statutory phrasings (Taiwan PDPA, in force):

- 個資外洩通報基準：施行細則 §22「即時」
- 個資處理責任主體：個資法 §4 委託者／受託者
- 成年年齡（事故當事人能力判定）：民法 §12 修正 2023-01-01 起為十八歲；未成年人以「未滿十八歲」表述

Templates and protocols MUST cite from this file; ad-hoc URL construction is forbidden (causes drift from canonical SoT).

## When to regenerate

If `legal-toolkit/scripts/canonical/legal-sources.json` URL templates change (very rare — last format change was ~2015), grep this file + all `assets/template-pii-breach-*.md` files for the affected pcode and update.
