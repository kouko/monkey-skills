# Attribution

This skill is an English-language adaptation of the **RIA-TV++** methodology
originally designed by [kangarooking](https://github.com/kangarooking) in
[cangjie-skill (蒼頡-skill)](https://github.com/kangarooking/cangjie-skill)
(MIT licensed, 2026).

## What was forked

- The 6-stage pipeline architecture (Adler → parallel extract → triple verify
  → RIA++ render → Zettelkasten → pressure test)
- The 5 extractor decomposition (framework / principle / case /
  counter-example / glossary)
- The Triple Verification (V1 cross-domain / V2 predictive power / V3
  exclusivity) — itself adapted from
  [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) by alchaincyf
- The R/I/A1/A2/E/B per-skill schema (RIA from 趙周's *《這樣讀書就夠了》*,
  extended with E + B for agent execution)
- The output structure (`BOOK_OVERVIEW.md` / `INDEX.md` / `candidates/` /
  `rejected/` / per-skill dirs)

## What was changed

- Translated all instructions, methodology, and templates to English
  (canonical) for wider audience and marginally more reliable instruction
  following on complex schemas
- Added an **adaptive output language rule** so Claude writes the
  resulting SKILL.md fields in the source book's language while
  instructions stay in English
- Added a **trilingual glossary (EN / 日本語 / 繁體中文)** at the top of
  each extractor for term alignment across languages
- Replaced the upstream entry contract: tsundoku auto-feeds chapter
  markdown + `metadata.json` from `book-extract`'s output directory
  (Cangjie expected the user to manually supply book text + metadata)
- Removed the explicit `darwin-skill` integration (kept the
  `test-prompts.json` artifact format for future compatibility, but
  no orchestrator hook)
- Reframed examples and identification signals to be cross-cultural
  (Munger's inversion, Bezos's two-pizza, Aurelius's negative
  visualization) instead of mostly-Chinese-context examples (段永平 /
  巴菲特 / 黃帝內經)

## Inspirations also honored

- **Mortimer Adler — *How to Read a Book*** — Stage 0 analytical reading
  (Structural / Interpretive / Critical) is taken directly from Adler
- **Niklas Luhmann — Zettelkasten** — atomicity, linking, and "rewrite in
  your own words" are Luhmann's principles
- **趙周 — 《這樣讀書就夠了》** — the original RIA notation
  (Reading / Interpretation / Appropriation)
- **Tiago Forte — *Building a Second Brain*** — Progressive Summarization
  inspires Stage 4's "verifiable compression chain"
- **Charlie Munger — *Poor Charlie's Almanack*** — the inversion principle
  and many of the worked examples in extractor identification signals

## License

This skill is distributed under MIT, matching cangjie-skill's license.
The original copyright notice (`Copyright (c) 2026 kangarooking`)
applies to the architecture; tsundoku's adaptations are similarly MIT.

## How to cite

If you fork this further, please credit both:

> Based on cangjie-skill (kangarooking, 2026, MIT) and tsundoku
> (kouko, 2026, MIT).
