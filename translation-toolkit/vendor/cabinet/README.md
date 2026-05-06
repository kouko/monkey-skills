# 内閣官房 部局課名・官職名英訳名称一覧

## Origin

内閣官房 (Cabinet Secretariat, Government of Japan) — 部局課名・官職名英訳
名称一覧 / Names of Government Organizations and Positions. The canonical
EN-JA reference for Japanese government organisation names, bureau names,
and official position titles.

Site: https://www.cas.go.jp/jp/seisaku/hourei/name.html
PDF:  https://www.cas.go.jp/jp/seisaku/hourei/name.pdf

The upstream document explicitly notes that translations were collated
from those used by individual ministries / agencies and have not been
collectively authorised by the Government of Japan; users should consult
each ministry / agency for current naming.

## Bundled extraction (shipped with v0.1.0)

`gov-orgs-en-ja.csv` is extracted from the upstream PDF using:

```
curl -fsSL -A "Mozilla/5.0" -o cabinet.pdf \
  "https://www.cas.go.jp/jp/seisaku/hourei/name.pdf"
pdftotext -layout cabinet.pdf cabinet.txt
# heuristic column-split: split each line at the first run of >=2 spaces
# (see scripts/extract_cabinet.py one-shot used at v0.1 ingest time).
```

Approximately 3,000 entries. Some entries from the original PDF's vertical
ministry-marker sidebar may bleed in as short JA tokens; these are
filtered out by the extractor's "drop short pure-CJK column" rule.

Columns: `Japanese, English` (UTF-8 with BOM). Alternate column names
(`en_term`, `ja_term`) are also accepted by the build parser.

## Manual refresh

If 内閣官房 publishes an updated edition of the PDF (the bundled extraction
is from the 2008-06-09 dataset, which is the most recent canonical issue
as of v0.1.0):

1. Download the new PDF from the URL above.
2. Run `pdftotext -layout name.pdf name.txt`.
3. Re-run the column-split heuristic (see git history for the one-shot
   script) to produce CSV.
4. Replace `gov-orgs-en-ja.csv`.

## Domain assignment

All entries are tagged `domain=gov` by the build parser — the source is
exclusively government organisation / position names.

## License

政府標準利用規約 第 2.0 版 — compatible with CC-BY 4.0. See `LICENSE` in
this directory for full terms and attribution.
