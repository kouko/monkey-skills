# NICT 日英中基本文 v1.2 — Japanese-English-Chinese Basic Sentence Data

## Origin

国立研究開発法人 情報通信研究機構 (NICT) — National Institute of
Information and Communications Technology, Japan.

The dataset is a curated collection of **5,304 sentence triples** in
Japanese / English / Simplified Chinese, designed as evaluation /
training material for machine translation between these three languages.
Triples are grouped by topic (greetings, weather, transport, dining,
medicine, etc.).

- Site:        https://alaginrc.nict.go.jp/jecbs/
- Full file:   https://alaginrc.nict.go.jp/jecbs/src/JEC_basic_sentence_v1-2.xls
- License:     CC-BY 3.0 — see `LICENSE`.

## What is shipped here

The full v1.2 spreadsheet is ~MB-scale and is **not committed** to this
repo (binary; large; would dominate diff history).

Instead, this directory ships a small **CSV fixture** drawn from across
~10 representative topics, used to:

- Exercise the `scripts/build-nict-corpus.py` pipeline end-to-end.
- Provide enough sentence-triple variety for the LLM to anchor style
  across en / ja / zh during translation.
- Keep the v0.1 distribution self-contained without a runtime fetch.

File: `JEC_basic_sentence_v1-2.csv` — UTF-8 with header
`topic,en,ja,zh` (4 columns). Approximately 30 triples across 10 topics.

## v0.1.0 fixture vs full corpus

| | v0.1 fixture (this repo) | Full v1.2 corpus (NICT) |
|---|---|---|
| Format | CSV | XLS (Excel 97-2003) |
| Triples | ~30 | 5,304 |
| Topics | 10 | ~30 |
| Use | LLM-prompt anchor | Full eval / training |

The full XLS may be added in v0.2 if a use-case emerges; for v0.1 the
fixture is sufficient because the corpus is consumed as **prompt-context
exemplars**, not as a training dataset.

## Updating

To swap in the full corpus:
1. Download `JEC_basic_sentence_v1-2.xls` from the NICT URL above.
2. Convert to CSV with header `topic,en,ja,zh` and place at
   `vendor/nict/JEC_basic_sentence_v1-2.csv` (replacing the fixture).
   Alternatively, add openpyxl/xlrd support to
   `scripts/build-nict-corpus.py` and read XLS directly.
3. Re-run `python3 scripts/build-nict-corpus.py` from the plugin root.
4. Re-run `python3 scripts/distribute.py`.
5. Bump the `count:` field in the canonical corpus frontmatter.

## Attribution

```
Source: NICT 日英中基本文データ v1.2 (sample)
Author: 国立研究開発法人情報通信研究機構 (NICT)
URL:    https://alaginrc.nict.go.jp/jecbs/
License: CC-BY 3.0
```
