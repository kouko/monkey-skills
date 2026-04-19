# Taiwan PMI / NMI / 台灣採購經理人指數 / 台湾購買担当者指数

Added v1.11.0. Taiwan publishes monthly ISM-style Purchasing Managers'
Indices for both manufacturing (PMI) and non-manufacturing (NMI). The
survey is compiled by **中華經濟研究院 (CIER)** under commission by
**國家發展委員會 (NDC)** and released through the official government
open-data portal **政府資料開放平臺** (`data.gov.tw/en/datasets/6100`).

## Why this skill uses the NDC open-data CSV

- **Authoritative primary source with unambiguous licence**: the CSV is
  released by NDC under 政府資料開放授權條款-第1版 (Taiwan Government
  Open Data License v1). The licence is CC BY-equivalent — commercial
  reuse permitted with attribution, no scraping restrictions.
- **Machine-readable**: stable CSV schema (`Date,PMI,NMI`) served via
  `ws.ndc.gov.tw/Download.ashx` with no authentication.
- **Same underlying data as CIER press releases**: the CIER own website
  (`cier.edu.tw`) publishes monthly PDF + Excel reports; the NDC CSV is
  exactly the same headline series, just in a structured format.
- **Contrast with US / JP / KR**: in those markets S&P Global holds the
  PMI licence, so those skills fall back to URL-only cross-references.
  Taiwan's PMI is uniquely available as free structured government open
  data among APAC markets covered by this toolkit.

---

## pmi-mfg: 製造業採購經理人指數 / Manufacturing PMI

- **Series key**: `pmi-mfg`
- **Source**: NDC via 政府資料開放平臺 dataset 6100 (CSV)
- **Unit**: Index (50 = neutral, ISM-style diffusion)
- **Frequency**: Monthly
- **Publication lag**: ~1-2 weeks after reference month (CIER press
  release cadence — typically first business day of the following month)
- **History**: From 2012-07

**What it measures**: Taiwan's monthly manufacturing diffusion index,
composed of five sub-indices each weighted 20%:

| Sub-index | 細項 |
|-----------|------|
| New Orders | 新增訂單 |
| Production | 生產 |
| Employment | 僱用人力 |
| Supplier Deliveries | 供應商交貨時間 |
| Inventories | 存貨 |

Coverage: six manufacturing industries — electronics & optical; basic
raw materials; power & machinery; chemicals & biotech / medical; food &
textiles; transport vehicles.

**Interpretation**:
- `> 50` → manufacturing expansion (new orders and production rising)
- `< 50` → manufacturing contraction
- Direction / momentum is more informative than the absolute level;
  CIER press releases highlight month-over-month change and sub-index
  breadth.

**Cross-market parallels**:
- US: S&P Global Manufacturing PMI (licensed; not fetched — OECD CLI
  proxy in `us-macro` pmi group)
- JP: au Jibun Bank Manufacturing PMI (licensed; not fetched — see
  `japan-macro` SKILL.md "PMI (URL reference only)" section)
- KR: S&P Global Korea Manufacturing PMI (licensed; not fetched — see
  `korea-macro` SKILL.md "PMI (URL reference only)" section)
- CN: Caixin Manufacturing PMI (via `china-macro` pmi group, akshare)
  and NBS 製造業 PMI (via `china-macro` pmi group, nbs_client)

---

## pmi-nmi: 非製造業經理人指數 / Non-Manufacturing NMI

- **Series key**: `pmi-nmi`
- **Source**: NDC via 政府資料開放平臺 dataset 6100 (CSV)
- **Unit**: Index (50 = neutral)
- **Frequency**: Monthly
- **Publication lag**: ~1-2 weeks after reference month
- **History**: From 2014-08 (NMI launched ~2 years after PMI)

**What it measures**: Taiwan's monthly services / non-manufacturing
diffusion index, using an analogous ISM-style methodology but with
different weights and sub-indices (business activity, new orders,
employment, supplier deliveries). CIER covers a broader set of non-
manufacturing industries than the manufacturing PMI panel.

**Interpretation**: same 50-threshold convention as `pmi-mfg`. Given
services are the largest share of Taiwan's GDP, NMI is structurally an
important complement to the manufacturing-heavy PMI reading.

---

## Primary sources

- NDC open-data portal (CSV, structured, machine-readable — what this
  skill fetches): https://data.gov.tw/en/datasets/6100
- NDC PMI / NMI explainer pages:
  - https://index.ndc.gov.tw/n/zh_tw/PMI
  - https://index.ndc.gov.tw/n/zh_tw/NMI
- CIER monthly reports (PDF + Excel, for human reference only):
  - https://www.cier.edu.tw/en/eco_cat/pmi-en/
  - https://www.cier.edu.tw/nmi
- NDC FAQ on PMI methodology: https://www.ndc.gov.tw/nc_337_2257
