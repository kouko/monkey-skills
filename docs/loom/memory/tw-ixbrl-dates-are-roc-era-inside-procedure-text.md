---
name: tw-ixbrl-dates-are-roc-era-inside-procedure-text
description: TW iXBRL date facts are ROC-era (民國) years embedded in procedure prose, not clean ISO dates — e.g. the financial-statement authorisation-for-issue fact (tifrs-notes:DateAndProceduresOfAuthorisationForIssueOfFinancialStatements) reads "本合併財務報告於115年5月13日經董事會通過。" → parse the 民國 date out (115+1911=2026 → 2026-05-13). Guard the ROC year with a LEFT digit boundary so a 4-digit Gregorian "2026年" is NOT misread as ROC "026"→1937 (silent wrong century).
type: gotcha
origin: branch tw-kpi-store (2026-07-25, 2.35.0) — the TW KPI producer needed a non-wall-clock as_of; the board authorisation-for-issue date is in the iXBRL but as a ROC-era date wrapped in 董事會 procedure text.
---

Taiwan financial iXBRL carries dates as **ROC-era (民國) years inside prose**,
never as a clean machine date. The authorisation-for-issue date — the board's
approval date, a useful non-wall-clock `as_of` — lives in
`tifrs-notes:DateAndProceduresOfAuthorisationForIssueOfFinancialStatements`,
whose value is a sentence: `"本合併財務報告於115年5月13日經董事會通過。"`. The
date is `民國 115年5月13日` = ROC year 115, and ROC+1911 = 2026 → `2026-05-13`.

**Why it bites twice:**
1. The date is not a field — it is buried in procedure text (「經董事會通過」),
   so a naive date parse must extract `\d+年\d+月\d+日` from prose, and the same
   fixture carries OTHER ROC dates in non-target facts (109年/113年) — key the
   extraction on the exact concept, not a document-wide date scan.
2. A regex like `(\d{2,3})\s*年` with NO left digit boundary, tried before a
   Gregorian branch, silently miscounts a 4-digit Gregorian year: `"2026年"`
   matches the trailing 3 digits `026` → 026+1911 = **1937**, a silent
   wrong-century value. Real TW filings use 民國 for this concept, so the path
   is easy to ship untested.

**How to apply:** extract the 年月日 date from the concept's own value (not a
doc-wide scan). Add a LEFT digit-boundary guard (`(?<!\d)`) and a digit-count
era discriminator: **4-digit year = Gregorian (as-is), 2-3 digit year = ROC
(+1911)** — one rule, not a fragile branch ordering. Test the 4-digit-年 form
explicitly (`"2026年…"` must stay 2026, never 1937). Numeric facts are ASCII and
unaffected; this is a nonNumeric-text-fact hazard, same green-suite-hides-it
class as [[tw-financial-ixbrl-served-utf8-despite-big5-declaration]].
