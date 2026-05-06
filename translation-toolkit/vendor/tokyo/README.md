# 東京都 日英対訳辞書 (Tokyo Metropolitan Government EN-JA Glossary)

## Origin

東京都 (Tokyo Metropolitan Government). Maintains a bilingual glossary for
multilingual public-information services, covering 行政 (administration),
福祉 (welfare), 防災 (disaster preparedness), 観光 (tourism), 生活 (daily
life), and other resident-facing categories.

Open Data Catalog:
https://catalog.data.metro.tokyo.lg.jp/dataset/t000001d1800000014

## Manual download (recommended for full dataset)

The dataset page is gated by browser-side JavaScript / 403 for plain
`curl`. To replace the bundled sample with the full dataset:

1. Open the dataset URL above in a browser.
2. Download the .xlsx (or CSV variant if available).
3. Save as either `en-ja-translation.xlsx` or `en-ja-translation.csv` in
   this directory, replacing the sample shipped with v0.1.

The build parser auto-detects:

- `.csv` — UTF-8 (with optional BOM); columns `English, Japanese,
  カテゴリ` (or alternate headers — see below).
- `.xlsx` — first worksheet, first row = headers; requires `openpyxl`
  (`uv pip install openpyxl` or `python3 -m pip install openpyxl`). If
  `openpyxl` is unavailable the parser raises a helpful error and the
  build skips this source.

## Sample shipped with v0.1.0

`en-ja-translation.csv` is a curated ~30-entry sample drawn across the
five main categories (行政 / 福祉 / 防災 / 観光 / 生活). The build script
maps category to domain:

| カテゴリ (Tokyo)   | mapped domain |
|-------------------|---------------|
| 行政               | gov           |
| 福祉               | gov           |
| 防災               | general       |
| 観光               | general       |
| 生活               | general       |
| (anything else)   | general       |

Columns: `English, Japanese, カテゴリ`. Alternate column names
(`英語`, `日本語`, `用語`, `category`, `分類`, `en_term`, `ja_term`)
are also accepted by the parser.

## License

CC-BY 4.0. See `LICENSE` in this directory for full terms and
attribution.
