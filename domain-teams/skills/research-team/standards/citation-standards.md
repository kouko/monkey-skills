---
title: Citation and Output Standards
tier: 2
---

# Citation and Output Standards

Single source of truth for research-team output rules — how to search,
how fresh sources need to be, how to tag confidence and likelihood,
how to label facts vs analysis vs speculation, and how to format
citations in major styles. Both worker (when producing) and evaluator
(when reviewing) reference this file. Tier 2: LLMs know APA / Chicago
/ IEEE / SIST by name but routinely muddle the version numbers and
recent revisions (Chicago 17th vs 18th, Booth 4th vs 5th) and confuse
which style governs which field. The body spells out format examples
for each style and flags two attribution corrections.

## Primary Sources

- American Psychological Association (2020) *Publication Manual of the American Psychological Association*, 7th ed. The current APA style manual used across psychology, education, and the social sciences. 7th edition (2020) introduced "they" as singular, simplified DOI presentation, and removed the publisher location for most book entries.
- University of Chicago Press (2024) *The Chicago Manual of Style*, 18th ed. https://www.chicagomanualofstyle.org/. Released **2024-09** and supersedes the 17th edition (2017). Chicago provides both Author-Date (sciences) and Notes-Bibliography (humanities) citation systems.
- IEEE (current) *IEEE Editorial Style Manual*. https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/ieee-editorial-style-manual/. The citation standard for engineering, computer science, and electrical disciplines published in IEEE journals and conferences.
- 科学技術振興機構 (2007) 『SIST 02-2007 参照文献の書き方』. https://warp.ndl.go.jp/info:ndljp/pid/12003258/jipsti.jst.go.jp/sist/pdf/SIST02-2007.pdf. 日本の科学技術情報流通における参照文献記述の標準規格。2012 年に SIST 自体は廃止されたが、SIST 02-2007 の記述方式は JST や国会図書館、多くの学協会で事実上の標準として継続して採用されている。

## Critical Attribution Corrections

### Chicago Manual of Style is 18th edition (2024), not 17th

Chicago Manual of Style released its **18th edition in September 2024**,
superseding the 17th edition (2017). LLM training data drift tends to
treat the 17th edition as current because it was current for seven
years. For v4.9.0 and onward, cite the **18th edition** for any Chicago
format example. The 18th edition introduced several changes to how
book citations are formatted — notably, the 18th edition **removes
the place-of-publication requirement** for most book entries and
**drops inclusive page numbers for full chapters**, matching the
direction APA 7 moved in 2020. When producing a Chicago citation,
verify against 18th edition rules, not 17th.

### Booth *Craft of Research* is 5th edition (2024), not 4th

Booth, Colomb, Williams, Bizup, and FitzGerald published the **5th
edition on 2024-06-25**, superseding the 4th edition. Cross-referenced
from `systematic-review-methodology.md` where the 5-element argument
model is spelled out. Research-team standards files that cite Booth
MUST cite the 5th edition. The core argument model is stable since
the 1st edition (1995); 5th-edition-only content (generative AI
chapter, visual/oral presentation updates) is post-most-LLM-cutoffs,
so body-level content for those sections must be Read rather than
parametrically recalled.

## Search Protocol

- **Always search in both English AND Japanese**
  - EN: natural phrasing ("topic best practices", "topic review 2024")
  - JP: 「〇〇 使い方」「〇〇 ベストプラクティス」「〇〇 設定」
- Add search in the user's language for regional topics or on request
- **Cross-verify claims across 2+ independent sources** — grounded in
  Tetlock & Gardner 2015's finding that aggregating independent
  forecasts outperforms any single source (see
  `confidence-and-claim-language.md`).
- Prefer **primary sources**: official docs, SEC filings, central
  bank reports, peer-reviewed papers. Classification is per
  `source-quality-and-evidence.md` (JMU / Cornell / ACRL taxonomy).

## Data Freshness

- Flag sources older than **6 months** for fast-moving topics
  (technology, market, policy). Always note the data date for
  financial / economic data.
- "Stale data kills analysis" — explicitly mark outdated figures.

### Freshness threshold is internal convention, not IPCC-grounded

The **6-month threshold is a research-team operational heuristic**, not
a prescription from IPCC AR5, PRISMA 2020, or the Cochrane Handbook.
None of those primary sources specify a numerical age cutoff — they
prescribe judgment about relevance for the research question. The
6-month figure is calibrated for the technology / market / policy
topics research-team typically investigates, where half-lives are
short. Disclose this as internal convention when citing it to an
external reader.

## Output Language

- All research output in the `output_language` specified in the launch
  prompt.
- Preserve original language for proper nouns, technical terms, and
  direct quotes. Do not force-translate domain jargon.

## Confidence Levels (summary — full ladder in `confidence-and-claim-language.md`)

Tag key conclusions with one of three levels:

- **高 (High)** — Multiple corroborating primary sources; consensus
  view. Maps to IPCC AR5 "High" or "Very high" confidence.
- **中 (Medium)** — 2+ sources agree but some ambiguity or limited
  data. Maps to IPCC AR5 "Medium" confidence.
- **低 (Low)** — Single source, contested, or speculative; clearly
  hedged. Maps to IPCC AR5 "Low" or "Very low" confidence.

For probabilistic claims ("how likely is X?") use the IPCC 7-level
likelihood ladder in `confidence-and-claim-language.md` separately
from confidence — they are orthogonal.

## Fact / Analysis / Speculation

Every claim MUST be categorized (operational expression of Kovach &
Rosenstiel 2021 Ch.4 "Journalism of Verification"):

- **事實 (Fact)** — Cited, verifiable, attributed to a source.
- **分析 (Analysis)** — Reasoned inference from facts; logic chain
  explicit.
- **推測 (Speculation)** — Forward-looking or uncertain; hedged
  language required. Must carry a likelihood tag from the IPCC
  ladder and a confidence tag.

Full taxonomy and examples in `confidence-and-claim-language.md`
§Fact / Analysis / Speculation Taxonomy.

## Citation Format Examples

### APA 7 (Author-Date, social sciences)

```
Book:     Author, A. A. (Year). Title of book (Xth ed.). Publisher.
Article:  Author, A. A., & Author, B. B. (Year). Title of article.
          Journal Name, volume(issue), pages. https://doi.org/xxxx
Web page: Author, A. A. (Year, Month Day). Title of page. Site Name. URL
```

Example: `Damodaran, A. (2012). Investment valuation: Tools and
techniques for determining the value of any asset (3rd ed.). Wiley.`

### Chicago 18th ed — Author-Date (sciences)

```
Book:     Author, First Middle. Year. Title of Book. Xth ed. Publisher.
Article:  Author, First M., and First M. Author. Year. "Title of Article."
          Journal Name volume (issue): pages. https://doi.org/xxxx
```

Example: `Damodaran, Aswath. 2012. Investment Valuation: Tools and
Techniques for Determining the Value of Any Asset. 3rd ed. Wiley.`

**Note**: 18th edition (2024) removes the place-of-publication field
from most book entries. If an older Chicago style guide shows "New
York: Wiley", do not replicate — 18th edition is just "Wiley."

### Chicago 18th ed — Notes-Bibliography (humanities)

```
Note (first):   1. First M. Author, Title of Book, Xth ed. (Publisher,
                Year), page.
Bibliography:   Author, First M. Title of Book. Xth ed. Publisher, Year.
```

### IEEE (engineering, computer science)

```
Book:     [N] A. Author, Title of Book, Xth ed. Publisher, Year.
Article:  [N] A. Author and B. Author, "Title of article," Journal
          Name, vol. X, no. Y, pp. Z-Z, Month Year, doi: xxxx.
Web:      [N] A. Author. "Title of page." Site Name.
          URL (accessed Mon. DD, YYYY).
```

Example: `[1] A. Damodaran, Investment Valuation, 3rd ed. Wiley, 2012.`

### SIST 02-2007 (Japanese scientific and technical literature)

```
図書:     著者名. 書名. 版表示, 出版者, 出版年, 総ページ数.
雑誌論文: 著者名. "論文名". 誌名. 出版年, 巻数, 号数, 掲載ページ.
Web:      著者名. "ウェブページタイトル". サイト名.
          入手先, (参照 YYYY-MM-DD).
```

Example: `ダモダラン, A. 企業価値評価. 第 3 版, ワイリー, 2012.`

## Which Style When

| Field / publication venue | Style |
|---|---|
| Psychology, education, social sciences (most) | **APA 7** |
| Humanities, history, literature, art | **Chicago 18 Notes-Bibliography** |
| Sciences (non-medical), some interdisciplinary | **Chicago 18 Author-Date** |
| Engineering, computer science, IEEE-published | **IEEE** |
| 日本語 学術技術情報 (JST / 国会図書館 / 学協会) | **SIST 02-2007** |
| Medicine, clinical research | Vancouver (not covered here — see ICMJE) |

When producing research output for research-team deliverables (not
for external submission), use **APA 7 by default** — it is the most
forgiving style, handles mixed citation types cleanly, and the 7th
edition's DOI-as-URL presentation is the most readable.

## Structure

- End with actionable recommendations.
- Recommendations MUST be specific and prioritized.
- Include confidence levels on recommendations themselves (not just
  on the underlying facts).
- Follow Booth's 5-element argument model (Claim / Reason / Evidence
  / Warrant / Acknowledgment-and-Response) for load-bearing
  recommendations — see `systematic-review-methodology.md` for the
  full model.

## Anti-Patterns

- Citing Chicago 17th edition format rules when producing output
  dated 2024-09 or later. Use 18th edition.
- Citing Booth *Craft of Research* 4th edition. Use 5th edition.
- Using the 6-month freshness threshold as if it were an IPCC
  standard — it is internal convention. Disclose it as such.
- Mixing citation styles within a single deliverable.
- Omitting the confidence tag on a key recommendation (the tag is
  load-bearing; without it the reader cannot calibrate).
- Treating "fact / analysis / speculation" as a stylistic suggestion.
  It is a tagging requirement — every sentence in a deliverable
  belongs to exactly one of the three.
