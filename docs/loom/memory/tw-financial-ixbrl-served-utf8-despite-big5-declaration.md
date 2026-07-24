---
name: tw-financial-ixbrl-served-utf8-despite-big5-declaration
description: TWSE MOPS t164sb01 serves the WHOLE financial family (-fh/-basi/-bd/-ins) as UTF-8 even though the document declares charset=big5; -ci industrial filings are MIXED — some genuine Big5 (1301/2330), some UTF-8-despite-big5 (1101, 2026Q1) — so served encoding is NOT predictable from taxonomy. A hardcoded big5hkscs decode silently garbles every Chinese-text (nonNumeric) fact for the UTF-8-served bodies (company/subsidiary names, note labels); numeric facts + fact counts are ASCII-safe and unaffected. Decode UTF-8-strict first, big5hkscs fallback (handles both regardless of declaration or taxonomy).
type: gotcha
origin: branch feat-tw-ixbrl-fh (2026-07-22) — TW financial-sector iXBRL; surfaced when -fh NPL notes needed the legible bank-subsidiary name and big5hkscs yielded "國泰世華銀行" → "��𧢲陸銝𤥁虾���銵�"
---

The `-ci` industrial arc hardcoded `resp.content.decode("big5hkscs", errors="replace")`
in the fetch layer. That is CORRECT for `-ci` filings (genuine Big5) but WRONG for the
whole financial family: TWSE serves `-fh`/`-basi`/`-bd`/`-ins` t164sb01 bodies as UTF-8
despite the `charset=big5` declaration in the markup. Byte-verified: the 2882 (國泰金)
`tifrs-notes:NameOfTheCompany` bytes are `\xe5\x9c\x8b\xe6\xb3\xb0…` = UTF-8 for
國泰世華銀行; a `big5hkscs` decode produces garbage. All 7 financial fixtures decode CLEAN
under strict UTF-8; the `-ci` fixtures 1301/2330 raise `UnicodeDecodeError` under UTF-8
and decode cleanly only under Big5. **Correction (2026-07-24, branch tw-ixbrl-endorsement):
"-ci ⇒ genuine Big5" is an over-generalization** — the -ci filer 台泥 1101 (2026Q1) is served
UTF-8-despite-charset=big5 exactly like the financial family (its `台灣水泥公司` bytes decode
clean as strict UTF-8; big5hkscs yields mojibake). So the Big5-vs-UTF-8 split is NOT along the
-ci/financial taxonomy line; it varies per filer/period. This does not weaken the fix — the
UTF-8-first/Big5-fallback decode already handles every case; it only kills any shortcut that
predicts encoding from taxonomy.

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
do NOT assume "Taiwan filing ⇒ Big5", and do NOT assume "-ci ⇒ Big5" either (1101 disproves
it). Tests that assert Chinese text must decode the fixture the same UTF-8-first way the
producer now does.
