# clreq — Requirements for Chinese Text Layout (extracted source)

Source: https://www.w3.org/TR/clreq/
Repo:   https://github.com/w3c/clreq
License: W3C Document License (see LICENSE)
Extract date: 2026-05-06

This file is a manually extracted subset of the W3C clreq specification,
focused on rules that affect translation output across Simplified
(zh-CN) and Traditional (zh-TW / zh-HK) Chinese. It is NOT a complete
reproduction; consult the canonical URL above for the full normative
text.

## 1. Punctuation marks (標點符號)

clreq groups Chinese punctuation into:
- **Sentence-end** marks (句末)
- **Pause / clause** marks (頓號、逗號)
- **Quotation** marks (引號)
- **Parenthesis / bracket** marks (括號)
- **Title** marks (書名號)
- **Other** (省略號、破折號、間隔號)

### 1.1 Sentence-end marks (句末)

| Mark | zh-CN | zh-TW | Notes |
|------|-------|-------|-------|
| period | `。` | `。` | full-width; no following space |
| question | `？` | `？` | full-width |
| exclamation | `！` | `！` | full-width |

The period glyph is identical across zh-CN / zh-TW (both U+3002), but
**positioning differs**: zh-CN sets it on the baseline (lower-left of
the em-square, like a period); zh-TW (and traditional zh-HK) centers
it within the em-square (中央定位). Font selection handles this; in
plain Unicode source you write `。` either way.

### 1.2 Comma / pause marks (逗號／頓號)

| Mark | zh-CN | zh-TW | Use |
|------|-------|-------|-----|
| comma | `，` (U+FF0C) | `，` (U+FF0C) | between clauses |
| enumeration | `、` (U+3001) | `、` (U+3001) | between list items |

Same glyph, **same baseline-vs-centered positioning difference** as `。`.

### 1.3 Quotation marks (引號) — KEY zh-CN vs zh-TW DIFFERENCE

This is the largest visible difference for translators:

| Level | zh-CN (Mainland) | zh-TW (Taiwan) | zh-HK (Hong Kong) |
|-------|------------------|----------------|--------------------|
| outer | `"..."` (U+201C / U+201D, "curly double") | `「...」` (U+300C / U+300D) | `「...」` |
| inner | `'...'` (U+2018 / U+2019, "curly single") | `『...』` (U+300E / U+300F) | `『...』` |

Translator rule:

- **zh-CN translation:** convert source `“ ”` and `‘ ’` to U+201C/D and
  U+2018/9 (curly Western quotes, full-width-spaced). Do NOT use
  `「」` in zh-CN body text — it reads as a Taiwanese / vintage
  affectation.
- **zh-TW translation:** convert source quotes to `「...」` outer,
  `『...』` inner. Do NOT use Western `“”` in zh-TW body text.
- **zh-HK translation:** same as zh-TW (`「」` / `『』`).
- ASCII straight quotes `"..."` and `'..'` are NEVER correct in any
  Chinese variant body text.

### 1.4 Brackets and parentheses (括號)

| Use | zh-CN | zh-TW |
|-----|-------|-------|
| general parenthesis | `（ ）` (U+FF08 / U+FF09) | `（ ）` |
| heading / emphasis | `【 】` | `【 】` |
| nested / aside | `〔 〕` | `〔 〕` |
| range | `［ ］` | `［ ］` |

Both variants use full-width forms in body text. ASCII `( )` is reserved
for code, math, or runs of Latin text.

### 1.5 Title marks (書名號) — zh-CN / zh-TW DIFFERENCE

| Level | zh-CN | zh-TW |
|-------|-------|-------|
| outer (book / film / album) | `《...》` (U+300A / U+300B) | `《...》` (acceptable) or underline / italic |
| inner (chapter / article / song) | `〈...〉` (U+3008 / U+3009) | `〈...〉` (acceptable) |

zh-TW also frequently uses straight underlines (in print) or italic /
bold (on web) instead of `《》`; either is acceptable. zh-CN is
strictly `《》` / `〈〉`.

### 1.6 Other marks

- `——` (U+2014 doubled, em-dash pair) — break / parenthetic. Always
  doubled in clreq, never single. Used identically in zh-CN / zh-TW.
- `……` (U+2026 doubled) — ellipsis. Always doubled in clreq.
- `·` (U+00B7 MIDDLE DOT) — used in zh-CN to separate parts of a
  foreign personal name: `约翰·史密斯`. zh-TW more often uses `‧`
  (U+2027 HYPHENATION POINT) or `·` interchangeably.
- `~` (U+FF5E FULLWIDTH TILDE) — range, e.g. `9時~17時`. Both variants.

### 1.7 Spacing

clreq specifies **no inter-character space** between Chinese characters.
For Chinese-Latin runs (similar to jlreq's 和欧文間隔), clreq recommends
a 1/4 em gap, automatically inserted by the layout engine. In plain
source text:

- DO NOT insert ASCII space between Chinese characters and adjacent
  Latin text. Write `Web標準` (zh-CN: `Web标准`) not `Web 標準`.
- ASCII number + unit follows the same convention as jlreq: scientific
  style adds a space (`100 kg`), consumer style does not (`100kg`).

## 2. Line composition (行的構成)

### 2.1 Line-end / line-start exclusion (避頭尾 / 標點懸掛)

clreq §6.1.1 — characters NOT allowed at line-start (避頭):

```
zh-CN: 。，、；：？！）」』〕】》〉］｝
zh-TW: 。，、；：？！）」』〕】》〉］｝
```

Characters NOT allowed at line-end (避尾):

```
（「『〔【《〈［｛
```

These rules are essentially identical to jlreq's kinsoku rules — both
zh-CN and zh-TW renderers must shift the break to satisfy.

### 2.2 Punctuation hanging (標點懸掛)

When a line ends just before `。`、`，`、`、`、`；`、`：`、`？`、`！`,
clreq permits the punctuation to hang into the right margin in
justified text rather than forcing a line break. This is widely used
in print typography and is supported by CSS `hanging-punctuation`.

### 2.3 Inter-script gap (中西文間距)

Same rule as §1.7 — 1/4 em gap auto-inserted by the layout engine
between Chinese and Latin runs. Translator inputs no ASCII space.

## 3. Numerals, dates, units

### 3.1 Numerals

Two systems:
- **Arabic** (`0-9`) — modern default for body text. Use ASCII
  half-width (`2026`), not full-width (`２０２６`).
- **Chinese characters** (`零一二三四五六七八九` or capital forms
  `零壹貳參肆伍陸柒捌玖`) — used for:
  - Formal / legal documents (capital forms for amounts to prevent
    forgery: `壹仟元整`).
  - Vertical text.
  - Round numbers in literary register: `三十年` not `30年`.

### 3.2 Dates

| Form | Example | Use |
|------|---------|-----|
| Arabic + 年月日 | `2026年5月6日` | most common in body text |
| Chinese numerals | `二〇二六年五月六日` | formal / vertical / literary |
| ISO | `2026-05-06` | technical / data |

**zh-TW also commonly uses Republican Era**: `民國115年` (= 2026).
For zh-TW translation:
- Government / legal / official documents → use 民國 era.
- General body text → either Arabic Gregorian or 民國 acceptable;
  match source convention.

### 3.3 Currency

- zh-CN: `¥1,000` (U+00A5, RMB) or `1000元`. ASCII comma every 3 digits.
- zh-TW: `NT$1,000` or `1,000元` or `新台幣1,000元`.

## 4. Simplified vs Traditional — orthographic differences

clreq covers layout rules; orthographic conversion (字形) is out of
scope. But for translators:

- zh-CN ↔ zh-TW is NOT a 1:1 character substitution. Many words have
  different lexical choices (滑鼠 / 鼠標, 軟體 / 软件, 影片 / 视频),
  which the per-pair glossary handles.
- DO NOT use OpenCC-style mechanical conversion as a substitute for
  human translation; it gets the characters but misses register,
  punctuation (Western vs corner quotes), and lexical choice.

## 5. Mixed-script line composition

Same rules as jlreq §6 (with 中西文 rather than 和欧文):

1. Inter-script spacing — auto 1/4 em gap.
2. Digit grouping — ASCII digits stay together.
3. Latin word integrity — break at ASCII space / hyphen / slash.
4. Punctuation hanging — permitted, optional.

## 6. Vertical text (直書 / 縱排)

zh-TW retains a stronger vertical-text tradition than zh-CN
(continued use in literature, classical reprints, calligraphy).
Vertical-set translation considerations:

- Use Chinese numerals for dates and counts: 二〇二六.
- Quotation marks rotate to vertical orientation; `「 」` becomes the
  rotated `﹁ ﹂` (CJK PRESENTATION FORMS). Tools handle this
  automatically; source text is still `「 」`.
- Latin runs use tate-chu-yoko 直中橫 for ≤ 4 chars; longer runs
  rotate sideways.

For default Markdown / web body text, assume horizontal (橫排) and
ignore vertical-specific concerns.

## 7. References

- W3C clreq Working Draft: https://www.w3.org/TR/clreq/
- W3C clreq-h (Hong Kong subset): https://www.w3.org/TR/clreq-h/
- GB/T 15834-2011 — 標點符號用法 (zh-CN national standard).
- 重訂標點符號手冊 (zh-TW Ministry of Education).
