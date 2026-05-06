# NAER 樂詞網 / 學術名詞資料集

## Origin

國家教育研究院 樂詞網 (National Academy for Educational Research, Academic
Terms Database). The canonical zh-TW academic-terminology source maintained
by Taiwan's Ministry of Education.

Site:        https://terms.naer.edu.tw/
Open Data:   https://data.gov.tw/dataset/15211 (foreign place names) and
             dataset family across 數十個學術領域 (各學科 學術名詞)

The catalogue spans dozens of academic domains including:

- 電子計算機名詞 (Computer Science)
- 資訊名詞 (Information Technology)
- 統計學名詞 (Statistics)
- 法律名詞 (Law)
- 醫學名詞 (Medicine)
- 經濟學名詞 (Economics)
- 物理學名詞 (Physics)
- 化學名詞 (Chemistry)
- 心理學名詞 (Psychology)
- 外國地名譯名 (Foreign Place Names)

## Manual download (recommended for full dataset)

Only the foreign place-names dataset has a stable direct CSV endpoint:

```
curl -fsSL "https://opendata.naer.edu.tw/學術名詞/國家教育研究院-外國地名譯名.csv" \
     -o vendor/naer/place-names-zh-TW.csv
```

(~64,000 entries, ~5.8 MB.)

For the per-domain academic-term sets, download interactively from the
data.gov.tw UI:

1. Open https://data.gov.tw/ and search for the domain name (e.g.,
   "電子計算機名詞").
2. Download the CSV/JSON resource for each desired domain.
3. Concatenate into a single CSV with columns:

   ```
   英文名稱,中文名稱,學術領域
   ```

4. Save the merged file as `academic-terms-zh-TW.csv` in this directory,
   replacing the sample shipped with v0.1.

## Sample shipped with v0.1.0

`academic-terms-zh-TW.csv` is a curated ~50-entry sample drawn from across
six representative domains plus a few foreign place names. It exercises
the domain-mapping branches in the build script:

| 學術領域 (NAER category)   | mapped domain   |
|----------------------------|-----------------|
| 電子計算機名詞              | tech.software   |
| 資訊名詞                    | tech.software   |
| 統計學名詞                  | statistics      |
| 法律名詞                    | legal           |
| 醫學名詞                    | medical         |
| 經濟學名詞                  | finance         |
| (anything else)            | general         |

Columns: `英文名稱, 中文名稱, 學術領域` (UTF-8). Alternate column names
(`英文`, `中文`, `category`, `分類`, `en_term`, `zh_TW_term`, `English`,
`Traditional Chinese`) are also accepted by the parser for compatibility
with full-dataset downloads that use slightly different headers.

## License

政府資料開放授權條款 第 1 版 (Open Government Data License v1) — compatible
with CC-BY 4.0. See `LICENSE` in this directory for full terms and
attribution.
