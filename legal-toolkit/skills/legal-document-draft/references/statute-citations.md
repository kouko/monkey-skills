# Statute citation index — hardcoded URLs

> All URLs use `law.moj.gov.tw` (全國法規資料庫 — 法務部 maintained). URL pattern stable since ~2015.
> Source of truth: `legal-toolkit/scripts/canonical/legal-sources.json` (post-SP1 SoT); this file is the manual cross-reference for template authoring.

## 個資法 (個人資料保護法, pcode I0050021)

- §3 (當事人權利): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=3
- §4 (委託): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=4
- §5 (利用範圍): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=5
- §6 (特種個資): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=6
- §8 (告知事項 — 第一項一至六款): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=8
- §9 (第三人提供告知): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=9
- §11 (個資保管 / 正確性): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=11
- §12 (通報義務 — promulgated 2025-11 amend; 施行日期未定): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=12
- §21 (跨境傳輸): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=21
- §22 (主管機關職權): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=22
- §27 (安全維護): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=27
- §47 (行政罰): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=47
- §48 (行政罰 — new tier promulgated 2025-11, 施行日期未定): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=48

Full text: https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0050021

## 個人資料保護法施行細則 (pcode I0050022)

- §12 (受託人義務): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=12
- §22 (即時通報 — safe default for breach notification timeframe): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22

Full text (last amended 2016-03-02; not yet updated for 2025/11): https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0050022

## 民法 (pcode B0000001)

- §12 (成年年齡，2023-01-01 起為 18 歲): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=12
- §13 (未滿七歲無行為能力 / 七歲以上未成年〔即未滿十八歲〕限制行為能力): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=13
- §227 (不完全給付): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=227
- §247-1 (定型化契約檢視): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=247-1
- §250 (違約金約定): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=250

## 消費者保護法 (pcode J0170001)

- §11-1 (定型化契約等候期 — 30 日): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0170001&flno=11-1
- §17 (定型化契約檢視): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0170001&flno=17

## 公平交易法 (pcode J0150002)

- §1 (立法目的): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0150002&flno=1
- §21 (不實廣告): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0150002&flno=21

## When to regenerate

If `legal-toolkit/scripts/canonical/legal-sources.json` URL templates change (very rare — last format change was ~2015), grep this file + all `assets/template-*.md` files for the affected pcode and update.
