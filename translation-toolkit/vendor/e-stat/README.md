# e-Stat 統計用語集

## Origin

e-Stat (政府統計の総合窓口) — Statistics of Japan. Operated by 総務省 統計局
and 独立行政法人 統計センター, e-Stat is the canonical portal for Japanese
government statistical data and the associated bilingual terminology
(統計用語集).

Site: https://www.e-stat.go.jp/
Terms portal: https://www.e-stat.go.jp/classifications/terms/90

## Manual download (recommended for full dataset)

The terms portal renders results in HTML; there is no stable direct CSV
download. To replace the bundled sample with a fuller dataset:

1. Open https://www.e-stat.go.jp/classifications/terms/90 in a browser.
2. Browse / filter the 統計用語集 by 分類 (classification) and by 言語
   (Japanese / English).
3. Manually export to CSV via the page's table-export controls, or scrape
   responsibly within e-Stat's 利用規約 (rate limits / robots.txt).
4. Save the resulting file as `stat-terms-en-ja.csv` in this directory
   with columns:

   ```
   English,Japanese
   ```

   (UTF-8 BOM is OK — the parser uses `utf-8-sig`.)

## Sample shipped with v0.1.0

`stat-terms-en-ja.csv` is a curated ~30-entry sample of canonical
statistical terminology (sample / population / mean / standard deviation
etc.). All entries are tagged `domain=statistics` by the build parser.

Columns: `English, Japanese` (UTF-8 with BOM). The parser also accepts
alternate column names (`en_term`, `ja_term`, `英文`, `日本語`, `用語`)
for compatibility with full-dataset exports that use different headers.

## License

政府標準利用規約 第 2.0 版 — compatible with CC-BY 4.0. See `LICENSE` in
this directory for full terms and attribution.
