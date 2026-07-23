---
name: tw-financial-ixbrl-served-utf8-despite-big5-declaration
description: TWSE MOPS t164sb01 serves the WHOLE financial family (-fh/-basi/-bd/-ins) as UTF-8 even though the document declares charset=big5, while -ci industrial filings are genuine Big5 — a hardcoded big5hkscs decode silently garbles every Chinese-text (nonNumeric) fact for financial filers (company/subsidiary names, note labels); numeric facts + fact counts are ASCII-safe and unaffected. Decode UTF-8-strict first, big5hkscs fallback.
type: gotcha
origin: branch feat-tw-ixbrl-fh (2026-07-22) — TW financial-sector iXBRL; surfaced when -fh NPL notes needed the legible bank-subsidiary name and big5hkscs yielded "國泰世華銀行" → "��𧢲陸銝𤥁虾���銵�"
---

The `-ci` industrial arc hardcoded `resp.content.decode("big5hkscs", errors="replace")`
in the fetch layer. That is CORRECT for `-ci` filings (genuine Big5) but WRONG for the
whole financial family: TWSE serves `-fh`/`-basi`/`-bd`/`-ins` t164sb01 bodies as UTF-8
despite the `charset=big5` declaration in the markup. Byte-verified: the 2882 (國泰金)
`tifrs-notes:NameOfTheCompany` bytes are `\xe5\x9c\x8b\xe6\xb3\xb0…` = UTF-8 for
國泰世華銀行; a `big5hkscs` decode produces garbage. All 7 financial fixtures decode CLEAN
under strict UTF-8; both `-ci` fixtures (1301/2330) raise `UnicodeDecodeError` under UTF-8
and decode cleanly only under Big5.

**Why it hides:** numeric facts (assets, ratios) and the `ix:` tag structure are ASCII, so
the parser "works", fact counts are unchanged, and every numeric canonical field is correct
— only Chinese-text (`nonNumeric`) fact VALUES are corrupted. A count-based or numeric-only
test stays green while company/subsidiary names are silently mojibake. It only surfaces when
a feature reads a Chinese-text fact (here: the bank-subsidiary name that lets an NPL note
state its scope honestly). Same wrong-answer-hides-behind-a-green-suite class as
[[ixbrl-dom-traversal-drops-nested-facts]].

**How to apply:** decode iXBRL bodies with a helper that tries `utf-8` STRICT first and
falls back to `big5hkscs` (errors="replace") on `UnicodeDecodeError` — UTF-8-strict fails
cleanly on genuine Big5 so the fallback fires for `-ci`, and succeeds on the UTF-8 financial
bodies. Put the helper in the STDLIB-only parser module (not the `requests`-importing fetch
module) so test consumers can import it offline without stubbing requests
([[importing-a-module-runs-its-module-level-imports]]). Do NOT trust the declared charset;
do NOT assume "Taiwan filing ⇒ Big5". Tests that assert Chinese text must decode the fixture
the same UTF-8-first way the producer now does.
