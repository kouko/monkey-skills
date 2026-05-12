---
source: w3c/jlreq
version: 0.1.0
last_synced: 2026-05-06
applies_to: ja-JP
---

# jlreq summary — Japanese typography rules for translation

> Source: https://www.w3.org/TR/jlreq/ (W3C Document License). Distilled for prompt context — see vendor/w3c/jlreq-source.md for the longer extract this summary is built from, and the W3C URL for the full normative text.

This summary distills the W3C jlreq rules a translator / LLM must respect when producing Japanese (ja-JP) output. It covers punctuation choice (`。`、`、`、quotation), half-width/full-width spacing (和欧文間隔), kinsoku (禁則 line-break exclusion), parenthesis pairs, and ruby (振り仮名) basics. Refer to the canonical W3C spec for implementation-level layout details.

## 1. Punctuation marks (約物 yakumono)

### 1.1 Sentence-end (句点 kuten)

- The Japanese sentence-end mark is `。` (U+3002 IDEOGRAPHIC FULL STOP),
  also written `．` (U+FF0E FULLWIDTH FULL STOP) in vertical math /
  scientific text and in some legal / official styles.
- `。` is full-width and occupies one em-square (全角); it is NOT
  followed by a space.
- Sentences within a quotation that ends with `」` typically OMIT the
  inner `。` — i.e. write `「行きましょう」` not `「行きましょう。」`.
  Exceptions exist in some publishers' house styles.

### 1.2 Comma / enumeration (読点 touten / 中黒 nakaguro)

- `、` (U+3001 IDEOGRAPHIC COMMA) is the standard Japanese comma /
  enumeration mark. Full-width, no following space.
- `，` (U+FF0C FULLWIDTH COMMA) is used in some scientific, legal, and
  governmental styles in place of `、`.
- `・` (U+30FB KATAKANA MIDDLE DOT, "中黒") joins paired/listed items
  especially with katakana names: `アメリカ・カナダ`, `氏名・住所`.

### 1.3 Quotation marks (括弧 kakko)

- Single-level Japanese quotation: `「 ... 」` (kagi-kakko).
- Nested inside that: `『 ... 』` (double-kagi).
- DO NOT use ASCII `"..."` or `'..'` in Japanese body text; replace
  with `「」` / `『』` during translation.
- Western-style 〝〟 (chouonpu-style quotes) appear in some literary
  styles but are not a default; prefer `「」`.

### 1.4 Brackets and parentheses

| Use                   | Pair       |
|-----------------------|------------|
| general parenthesis   | （ ）      |
| quotation             | 「 」      |
| nested quotation      | 『 』      |
| emphasis / aside      | 〔 〕      |
| heading / title       | 【 】      |
| range or interjection | ［ ］      |

All paired marks are full-width and self-spacing — do NOT add a regular
space between the bracket and the enclosed text.

### 1.5 Other marks

- `？` `！` (full-width) — full-width forms for question / exclamation.
  When used inside Japanese body text, DO NOT add following space.
- `…` (U+2026) — used singly or doubled `……`. Two-em ellipsis
  `‥‥` exists in older usage.
- `―` (U+2015 HORIZONTAL BAR / em-dash) — used for parenthetic
  insertion `――` (often doubled).
- `※` — note marker.
- `〜` (U+301C WAVE DASH) — range / "from-to": `9時〜17時`.

## 2. Half-width / full-width spacing (和欧文間隔)

When a run of Latin letters, ASCII digits, or ASCII punctuation is
embedded in a Japanese sentence, jlreq specifies a small inter-script
gap (typically 1/4 em = "四分アキ"). In digital typography this is
usually rendered automatically by the layout engine (CSS
`text-spacing-trim` / `text-autospace`); in plain Markdown / source text
the convention is:

- DO NOT insert ASCII space between Japanese characters and the Latin
  run — let the renderer add it.
- Example: write `Web標準` not `Web 標準` and not `Ｗｅｂ標準`.
- BUT: when an ASCII number directly precedes a unit, no extra space:
  `100kg` not `100 kg` (some style guides — e.g. JIS Z 8301 — disagree;
  technical writing tends to keep `100 kg`).
- Full-width Latin / digits (Ａ-Ｚ ａ-ｚ ０-９) are reserved for
  decorative or aligned tabular use; do NOT use them in body text.

Software / document translation rule of thumb:

- Variable names, code, URLs, brand names: keep ASCII, no surrounding
  space.
- Numerals in prose: ASCII half-width digits.
- Units following numerals: SI/scientific style → space (`100 kg`),
  consumer / casual style → no space (`100kg`).

## 3. Kinsoku (禁則処理) — line-break exclusion

jlreq §3.1 codifies which characters may not appear at line-start
(`行頭禁則`) or line-end (`行末禁則`). When breaking a line, the layout
engine must shift the line break to satisfy these rules.

### 3.1 Characters NOT allowed at line-start (頭禁則)

Closing brackets, sentence-end marks, mid-sentence delimiters:

```
、。，．）」』］｝〕〉》】〙〛
？！…‥・゛゜ー
ヽヾゝゞ々ぁぃぅぇぉっゃゅょゎ
ァィゥェォッャュョヮ・
```

Practical translator impact: NEVER start a translated line with `。`
or `」`. Tools handle this automatically; LLM output should also avoid
forcing such breaks via explicit `\n`.

### 3.2 Characters NOT allowed at line-end (末禁則)

Opening brackets:

```
（「『［｛〔〈《【〘〚
```

### 3.3 Characters that must stay together (分離禁止)

- Double-width punctuation pairs (e.g. `——`, `……`) should not be split
  across lines.
- Dotted leaders, em-dashes, ellipses are treated as 2-character units.

## 4. Ruby (振り仮名)

Ruby is small annotation text placed above (or to the right in vertical
text) of a base character to indicate its reading.

### 4.1 Form

- `モノルビ` — one ruby span per base character.
- `グループルビ` — one ruby span over a group of base characters
  (used for jukugo readings: 大人 ↔ おとな).
- `両側ルビ` — ruby on both sides (rare; used for furigana on top + 
  romanization on bottom).

### 4.2 In Markdown / HTML translation

- HTML uses `<ruby>大人<rt>おとな</rt></ruby>`.
- Markdown does not have native ruby; some flavors support `[大人]^(おとな)`
  or `{大人|おとな}`.
- For LLM translation output, preserve any `<ruby>` markup already in
  the source; do NOT spontaneously add furigana — that is a rendering
  decision for the publisher.

### 4.3 When to add ruby

- Personal names (especially uncommon kanji).
- Place names with non-standard readings.
- Specialized terminology with a non-obvious yomi.
- Educational / children's content (broadly).
- Generally NOT for common kanji in adult prose.

## 5. Numerals, dates, units

- Body text: half-width Arabic numerals `2026年5月6日`.
- Vertical text: traditional kanji numerals 二〇二六年五月六日 (more
  formal / literary).
- Dates: `2026年5月6日` is canonical; ISO `2026-05-06` acceptable in
  technical contexts.
- Time: `9時30分` or `9:30` (half-width colon).
- Currency: `1,000円` (ASCII comma every 3 digits, full-width 円
  symbol or `JPY 1,000` for international docs).

## 6. Mixed-script line composition

When a Japanese line contains a mix of CJK, kana, Latin, and digits,
jlreq permits these adjustments:

1. **Inter-script spacing** (和欧文間) — automatic 1/4 em gap.
2. **Digit grouping** — ASCII digits 0-9 are kept together; do not
   wrap mid-number.
3. **Latin word integrity** — ASCII alphabetic words are kept together;
   wrap at ASCII space, hyphen, or slash.
4. **Punctuation hanging (ぶら下げ)** — `、` `。` may be allowed to hang
   into the right margin in justified text instead of forcing a line
   break. Optional; some publishers disable it.

## 7. Vertical text (縦書き)

Vertical text rotates Latin text 90° (or sets it sideways via tate-chu-yoko
縦中横 for short runs ≤ 4 chars). Translators producing source for
vertical-set publication should:

- Avoid long Latin runs (URLs etc.) in body — quote them as footnotes.
- Use kanji numerals for dates / counts where stylistically appropriate.
- Use 「」 not "..." for quotation.

For default Markdown / web body text, assume horizontal (yokogaki) and
ignore vertical-specific concerns.
