# W3C jlreq / clreq — typography rules for ja-JP and zh-{CN,TW}

## Origin

The W3C International Layout Task Force publishes two normative reference
documents that codify how Japanese and Chinese text should be laid out by
software (browsers, word processors, e-book renderers, etc.):

- **jlreq** — Requirements for Japanese Text Layout
  - Spec:  https://www.w3.org/TR/jlreq/
  - Repo:  https://github.com/w3c/jlreq
- **clreq** — Requirements for Chinese Text Layout
  - Spec:  https://www.w3.org/TR/clreq/
  - Repo:  https://github.com/w3c/clreq

Both are maintained by editors who are native speakers and typography
experts (jlreq: 小林 敏 et al.; clreq: 梁海 et al.) under the W3C Process.

## What is shipped here

The full specs are large (jlreq alone is several hundred printed pages)
and most of their content addresses pixel-level layout questions —
line-break exception tables, glyph metric algorithms, ruby placement
geometry — that an LLM does not need verbatim to produce well-typeset
translations.

This vendor folder ships **manually-extracted summaries** of the rules
that matter for translation work:

- `jlreq-source.md` — extracted prose covering Japanese punctuation,
  半角/全角 spacing, 禁則処理 (kinsoku — line-break exclusion),
  parenthesis pairs, ruby (振り仮名) placement basics.
- `clreq-source.md` — extracted prose covering Simplified vs Traditional
  Chinese punctuation differences, 行首/行末 line-break rules,
  parenthesis pairs across zh-CN / zh-TW conventions.

These source files are then templated by `scripts/build-typography-summaries.py`
into the canonical summaries `scripts/canonical/{jlreq,clreq}-summary.md`,
which are distributed to each active skill under `<skill>/typography/`.

## v0.1.0 fetch method

- **Date fetched:** 2026-05-06
- **Method:** Manual summary by AI assistant, drawing on knowledge of the
  published W3C specs, NOT a programmatic crawl. The summaries focus
  on rules a translator / LLM needs to apply at the sentence level. They
  are not a faithful reproduction of the full normative documents — for
  any layout-engine implementation, consult the canonical W3C URLs above.
- **License:** W3C Document License (3 February 2023). See `LICENSE`.

The full specs may be re-extracted programmatically in v0.2 if a stable
section-mapping is needed; this v0.1 method ships within license terms
(W3C Document License permits derivative summaries with attribution) and
is sufficient for the LLM-prompt use case.

## Updating

To refresh in a future version:
1. Re-read https://www.w3.org/TR/jlreq/ and https://www.w3.org/TR/clreq/.
2. Update `jlreq-source.md` / `clreq-source.md` in this directory.
3. Re-run `python3 scripts/build-typography-summaries.py` from the
   plugin root.
4. Re-run `python3 scripts/distribute.py` to push the updated summaries
   out to each active skill.
5. Bump the `last_synced` field in the canonical summary frontmatter.
