# 日本銀行 時系列統計 DB 名一覧 / BOJ Time-Series Statistics DB Catalog

Complete catalog of all databases available through the Bank of Japan's
Time-Series Data Search API (`stat-search.boj.or.jp`). Use this as a
lookup table when constructing `boj_client.py --db` calls.

API documentation: https://www.stat-search.boj.or.jp/info/api_guide_en.html

---

## 金利（預金・貸出関連） / Interest Rates on Deposits and Loans

| DB名 | 日本語 | English |
|------|-------|---------|
| IR01 | 基準割引率および基準貸付利率 | Basic Discount Rate and Basic Loan Rate |
| IR02 | 預金種類別店頭表示金利の平均年利率等 | Average Interest Rates Posted by Type of Deposit |
| IR03 | 定期預金の預入期間別平均金利 | Average Interest Rates on Time Deposits by Term |
| IR04 | 貸出約定平均金利 | Average Contract Interest Rates on Loans and Discounts |

## マーケット関連 / Financial Markets

| DB名 | 日本語 | English |
|------|-------|---------|
| FM01 | 無担保コールO/N物レート | Uncollateralized Overnight Call Rate |
| FM02 | 短期金融市場金利 | Short-term Money Market Rates |
| FM03 | 短期金融市場残高 | Short-term Money Market Balances |
| FM04 | コール市場残高 | Call Money Market Outstanding |
| FM05 | 公社債発行・償還および現存額 | Bonds Issued, Redeemed and Outstanding |
| FM06 | 公社債消化状況 | Government Bond Distribution |
| FM07 | （参考）国債窓口販売額・窓口販売率 | (Ref) Gov Bond OTC Sales |
| FM08 | 外国為替市況 | Foreign Exchange Rates |
| FM09 | 実効為替レート | Effective Exchange Rate |

## 決済関連 / Payment and Settlement

| DB名 | 日本語 | English |
|------|-------|---------|
| PS01 | 各種決済 | Payment Systems |
| PS02 | フェイルの発生状況 | Fails in Settlement |

## 預金・マネー・貸出 / Money, Deposits and Loans

| DB名 | 日本語 | English |
|------|-------|---------|
| MD01 | マネタリーベース | Monetary Base |
| MD02 | マネーストック | Money Stock |
| MD03 | マネーサーベイ | Money Survey |
| MD04 | （参考）マネーサプライ（M2+CD）増減と信用面の対応 | (Ref) Money Supply Changes and Credit Counterparts |
| MD05 | 通貨流通高 | Currency in Circulation |
| MD06 | 日銀当座預金増減要因と金融調節（実績） | BOJ Current Account Changes and Market Operations |
| MD07 | 準備預金額 | Reserves |
| MD08 | 業態別の日銀当座預金残高 | BOJ Current Account by Sector |
| MD09 | マネタリーベースと日本銀行の取引 | Monetary Base and BOJ Transactions |
| MD10 | 預金者別預金 | Deposits by Depositor |
| MD11 | 預金・現金・貸出金 | Deposits, Cash, and Loans |
| MD12 | 都道府県別預金・貸出金 | Deposits and Loans by Prefecture |
| MD13 | 貸出・預金動向 | Lending and Deposit Trends |
| MD14 | 定期預金の残高および新規受入高 | Time Deposits Balance and New Acceptance |

## 貸出関連 / Loans

| DB名 | 日本語 | English |
|------|-------|---------|
| LA01 | 貸出先別貸出金 | Loans by Sector |
| LA02 | 日本銀行貸出 | BOJ Loans |
| LA03 | その他貸出残高 | Other Outstanding Loans |
| LA04 | コミットメントライン契約額、利用額 | Commitment Lines |
| LA05 | 主要銀行貸出動向アンケート調査 | Senior Loan Officer Survey |

## 金融機関バランスシート / Balance Sheets of Financial Institutions

| DB名 | 日本語 | English |
|------|-------|---------|
| BS01 | 日本銀行勘定 | Bank of Japan Accounts |
| BS02 | 民間金融機関の資産・負債 | Financial Institutions Assets and Liabilities |

## 資金循環 / Flow of Funds

| DB名 | 日本語 | English |
|------|-------|---------|
| FF | 資金循環 | Flow of Funds |

## その他の日本銀行関連 / Other BOJ Statistics

| DB名 | 日本語 | English |
|------|-------|---------|
| OB01 | 日本銀行の対政府取引 | BOJ Transactions with Government |
| OB02 | 日本銀行が受入れている担保の残高 | Collateral Accepted by BOJ |

## 短観 / TANKAN

| DB名 | 日本語 | English |
|------|-------|---------|
| CO | 短観 | TANKAN (Short-Period Economic Survey of Enterprises) |

## 物価 / Prices

| DB名 | 日本語 | English |
|------|-------|---------|
| PR01 | 企業物価指数 | Corporate Goods Price Index (CGPI) |
| PR02 | 企業向けサービス価格指数 | Services Producer Price Index (SPPI) |
| PR03 | 製造業部門別投入・産出物価指数 | Input-Output Price Index (IOPI) |
| PR04 | ＜サテライト指数＞最終需要・中間需要物価指数 | Final/Intermediate Demand Price Index |

## 財政関連 / Public Finance

| DB名 | 日本語 | English |
|------|-------|---------|
| PF01 | 財政資金収支 | Treasury Receipts and Payments |
| PF02 | 政府債務 | National Government Debt |

## 国際収支・BIS関連 / Balance of Payments and BIS

| DB名 | 日本語 | English |
|------|-------|---------|
| BP01 | 国際収支統計 | Balance of Payments |
| DER | デリバティブ取引に関する定例市場報告 | Derivatives Market Report |
| BIS | BIS国際資金取引統計 | BIS International Banking Statistics |

## その他 / Others

| DB名 | 日本語 | English |
|------|-------|---------|
| OT | その他 | Others |

---

## Usage Notes / 使用上の注意

### API Access / APIアクセス

```bash
# Fetch data by DB + series code
uv run boj_client.py --db FM01 --code STRDCLUCON --start-date 202501

# Multiple series codes
uv run boj_client.py --db FM01 --code STRDCLUCON,STRDCLUCONH --start-date 202501
```

### Series Code Discovery / シリーズコードの発見

Most DBs contain multiple series codes that change with base-year revisions.
Use the BOJ `getMetadata` endpoint to discover current valid codes:

```
GET https://www.stat-search.boj.or.jp/api/v1/getMetadata?format=json&db={DB_NAME}
```

This is required for: PR01, MD02, CO, FM08, FM09, BP01 (and others with
complex code structures).

### Rate Limits / レート制限

The BOJ API does not publish explicit rate limits, but the `boj_client.py`
adapter includes retry logic with exponential backoff for HTTP 429 responses.
Avoid sending more than ~10 requests per second.

### Data Currency / データの最新性

BOJ updates most series at **8:50 AM JST** (23:50 UTC previous day).
The `boj_client.py` adapter caches responses for 24 hours by default.
Use `--no-cache` to bypass.
