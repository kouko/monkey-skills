# us-macro

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

investing-toolkit 向けの米国マクロ経済およびセクターレベルデータ skill。

## 概要

FRED（Federal Reserve Economic Data）から 25 項目の米国マクロ経済・セクターレベル指標を取得し、11 の指標 group（rates、inflation、growth、nowcast（コア macro）、加えて housing、industrials、energy、financials、consumer、tech、ppi（セクターレベル））にまとめた構造化 JSON を返します。セクター group は投資分析向けにセクター ETF にマッピングされます。本 skill はデータ取得のみで、分析・regime マッピング・投資判定の生成は行いません。

**月次 GDP proxy**：米国の公式 GDP は四半期（`GDPC1`）です。`nowcast` group（GDPNow、CFNAI、WEI、OECD CLI）が合わせてリアルタイムの GDP モメンタム proxy となり、china-macro の三大数据や japan-macro の景気動向指数 CI 三本柱と並列の位置付けです。

## データソース

**FRED CSV endpoint** — API key 不要。script は St. Louis Fed の公開エンドポイントから直接 CSV データをダウンロードします：

```
https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES}&cosd={START}
```

オプションで JSON API mode（`--use-api`）も利用でき、より柔軟なクエリが可能ですが `FRED_API_KEY` 環境変数が必要です。既定の CSV mode で本 skill のすべてのユースケースをカバーします。

## 指標

### コア macro

| Series | 名称 | Group | 頻度 | 標準ラグ |
|--------|------|-------|-----------|-------------|
| T10Y2Y | 10Y-2Y 国債スプレッド | rates | 日次 | 1 営業日 |
| DGS10 | 10 年米国債利回り | rates | 日次 | 1 営業日 |
| DGS2 | 2 年米国債利回り | rates | 日次 | 1 営業日 |
| FEDFUNDS | 実効フェデラル・ファンド・レート | rates | 月次 | 月末から ~1 週 |
| CPIAUCSL | ヘッドライン CPI（All Items） | inflation | 月次 | ~2-3 週 |
| CPILFESL | コア CPI（食品・エネルギー除く） | inflation | 月次 | ~2-3 週 |
| GDPC1 | 実質 GDP | growth | 四半期 | ~1 ヶ月（advance est.） |
| INDPRO | 鉱工業生産指数 | growth | 月次 | ~3-4 週 |
| GDPNOW | Atlanta Fed GDPNow（SAAR %） | nowcast | 四半期 snapshot | 当四半期内に月 6-7 回更新 |
| CFNAI | Chicago Fed National Activity Index | nowcast | 月次 | ~2-3 ヶ月 |
| WEI | NY Fed Weekly Economic Index | nowcast | 週次 | ~1 週 |
| USALOLITOAASTSAM | OECD Composite Leading Indicator（USA） | nowcast | 月次 | ~1 ヶ月 |

### セクターレベル

| Series | 名称 | Group | 頻度 | 標準ラグ |
|--------|------|-------|-----------|-------------|
| PERMIT | 建築許可 | housing | 月次 | ~2-3 週 |
| HOUST | 住宅着工 | housing | 月次 | ~2-3 週 |
| CSUSHPISA | Case-Shiller 住宅価格指数 | housing | 月次 | ~2 ヶ月 |
| MORTGAGE30US | 30 年住宅ローン金利 | housing | 週次 | ~1 週 |
| DGORDER | 耐久財受注 | industrials | 月次 | ~4 週 |
| DCOILWTICO | WTI 原油価格 | energy | 日次 | 1 営業日 |
| DHHNGSP | Henry Hub 天然ガス価格 | energy | 日次 | 1 営業日 |
| BAMLH0A0HYM2 | ハイイールド信用スプレッド | financials | 日次 | 1 営業日 |
| RSAFS | 速報小売売上高 | consumer | 月次 | ~2 週 |
| UMCSENT | 消費者信頼感（UMich） | consumer | 月次 | ~2-4 週 |
| CES3133440001 | 半導体雇用 | tech | 月次 | ~3-4 週 |
| PCUAINFOAINFO | PPI：情報サービス | tech | 月次 | ~2-3 週 |
| PCUOMFGOMFG | PPI：製造業全体 | ppi | 月次 | ~2-3 週 |

11 の group に編成：

- **rates**：T10Y2Y、DGS10、DGS2、FEDFUNDS
- **inflation**：CPIAUCSL、CPILFESL
- **growth**：GDPC1、INDPRO
- **nowcast**：GDPNOW、CFNAI、WEI、USALOLITOAASTSAM
- **housing**：PERMIT、HOUST、CSUSHPISA、MORTGAGE30US
- **industrials**：DGORDER
- **energy**：DCOILWTICO、DHHNGSP
- **financials**：BAMLH0A0HYM2
- **consumer**：RSAFS、UMCSENT
- **tech**：CES3133440001、PCUAINFOAINFO
- **ppi**：PCUOMFGOMFG

## セクター ETF マッピング

| Group | 主要 ETF | 備考 |
|-------|-------------|-------|
| housing | XLRE、XHB | MORTGAGE30US は XLF にも影響 |
| industrials | XLI | INDPRO（growth group）も関連 |
| energy | XLE | 原油は航空・消費支出・インフレに影響 |
| financials | XLF | T10Y2Y（rates group）が銀行マージンを駆動 |
| consumer | XLY、XLP | 小売売上が裁量品 vs 生活必需品のローテーションを駆動 |
| tech | XLK | 半導体雇用がサプライチェーンを反映 |
| ppi | （セクター横断） | CPI に 3-6 ヶ月先行；マージン圧迫シグナル |

## アーキテクチャ

```
us-macro skill
├── SKILL.md                    <- Claude が読む
├── scripts/
│   ├── fred_client.py          <- FRED CSV adapter（API key 不要）
│   └── setup.sh                <- uv を自動インストール
└── references/
    └── us-macro-indicators.md  <- 25 指標エントリ + 解釈
```

scripts は `investing-toolkit/scripts/` から `sync-scripts.sh` 経由で同期されたコピーです。skill ディレクトリは自己完結しており、Claude Code は skill ルートを基準にすべてのパスを解決します。

## 動作の仕組み

1. **series リストを解決** — `--indicators` パラメータ（既定値：`all`）は FRED series ID にマッピングされます。例えば `--indicators rates` は T10Y2Y、DGS10、DGS2、FEDFUNDS に解決されます。

2. **data-fetcher agent を起動** — skill は fetch リクエストを `data-fetcher` agent に dispatch し、agent が `uv run` 経由で `fred_client.py` を実行します。リクエストは頻度ごとにグループ化され、適切な period 数を使用します（例：日次/月次は 24 period、四半期は 12 period）。

3. **出力を構造化** — 各 series について最新と前回の観測値を抽出し、方向（Rising / Falling / Flat）を計算し、指標 group key の下に集約します。

## 出力 contract

```json
{
  "fetched_at": "2026-04-16T08:00:00Z",
  "groups": {
    "rates": {
      "T10Y2Y": {
        "latest": { "date": "2026-04-15", "value": 0.42 },
        "prior":  { "date": "2026-04-14", "value": 0.38 },
        "direction": "Rising"
      },
      "DGS10":    { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "DGS2":     { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "FEDFUNDS": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "inflation": {
      "CPIAUCSL": { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "CPILFESL": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "growth": {
      "GDPC1":  { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "INDPRO": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "nowcast": {
      "GDPNOW":           { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "CFNAI":            { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "WEI":              { "latest": { "..." }, "prior": { "..." }, "direction": "..." },
      "USALOLITOAASTSAM": { "latest": { "..." }, "prior": { "..." }, "direction": "..." }
    },
    "housing": { "PERMIT": { "..." }, "HOUST": { "..." }, "CSUSHPISA": { "..." }, "MORTGAGE30US": { "..." } },
    "industrials": { "DGORDER": { "..." } },
    "energy": { "DCOILWTICO": { "..." }, "DHHNGSP": { "..." } },
    "financials": { "BAMLH0A0HYM2": { "..." } },
    "consumer": { "RSAFS": { "..." }, "UMCSENT": { "..." } },
    "tech": { "CES3133440001": { "..." }, "PCUAINFOAINFO": { "..." } },
    "ppi": { "PCUOMFGOMFG": { "..." } }
  }
}
```

すべてのエントリの `_provenance` は暗黙的に FRED です。series によって公表ラグが異なるため、参照期間を確認するには `latest.date` を必ずチェックしてください。

## クロス plugin 利用

```
us-macro（本 skill）-> macro-regime-snapshot -> domain-teams:investing-team
```

1. **us-macro** — FRED データを取得し、構造化 JSON を返す
2. **macro-regime-snapshot** — Investment Clock phase + Growth-Inflation Positioning（GIP）象限にマッピングし、regime 判定を出力
3. **domain-teams:investing-team** — フル分析、conviction scoring、portfolio implications

`macro-regime-snapshot` を起動するときは、出力 JSON をそのまま `### Input` セクションとして渡します。

## セットアップ

`uv`（Python パッケージランナー）のみ必要。`setup.sh` script が見つからなければ自動でインストールします。既定の CSV エンドポイントには API key は不要です。

```bash
# 手動テスト
uv run scripts/fred_client.py --series T10Y2Y,DGS10 --periods 24
```

## メンテナンスと検証

### すべての series がデータを返すか検証

```bash
cd investing-toolkit/scripts

for series in T10Y2Y DGS10 DGS2 FEDFUNDS CPIAUCSL CPILFESL GDPC1 INDPRO GDPNOW CFNAI WEI USALOLITOAASTSAM PERMIT HOUST CSUSHPISA MORTGAGE30US DGORDER DCOILWTICO DHHNGSP BAMLH0A0HYM2 RSAFS UMCSENT CES3133440001 PCUAINFOAINFO PCUOMFGOMFG; do
  uv run fred_client.py --series "$series" --periods 3 --no-cache 2>&1 | \
    python3 -c "
import json, sys
d = json.load(sys.stdin)
l = d.get('latest') or {}
pv = d.get('_provenance') or {}
err = d.get('error', '')
if err:
    print(f'$series: ERROR - {err}')
else:
    print(f'$series: date={l.get(\"date\",\"???\")}  value={l.get(\"value\",\"\")}  staleness={pv.get(\"staleness_days\",\"?\")}d')
"
done
```

**頻度別の期待 staleness：**

| 頻度 | Series | 期待 staleness |
|-----------|--------|-------------------|
| 日次 | T10Y2Y、DGS10、DGS2、DCOILWTICO、DHHNGSP、BAMLH0A0HYM2 | < 5 日 |
| 週次 | MORTGAGE30US、WEI | < 10 日 |
| 月次 | FEDFUNDS、CPIAUCSL、CPILFESL、INDPRO、PERMIT、HOUST、DGORDER、RSAFS、UMCSENT、CES3133440001、PCUOMFGOMFG、PCUAINFOAINFO、USALOLITOAASTSAM | < 60 日 |
| 月次（lagging） | CSUSHPISA、CFNAI | < 90 日 |
| 四半期 | GDPC1、GDPNOW | < 200 日 |

### FRED CSV endpoint を検証

```bash
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10" | tail -3
```

### series ID がまだ有効か検証

FRED は時折 series を retire したり renaming します：

```bash
curl -sS "https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}" | head -3
```

retire されている場合は後継を `https://fred.stlouisfed.org/series/{SERIES_ID}` で確認します。

### 新しい FRED series を追加

1. https://fred.stlouisfed.org で series ID を見つける
2. 検証：`uv run fred_client.py --series {ID} --periods 12 --no-cache`
3. `SKILL.md`（group に追加）+ `references/us-macro-indicators.md`（エントリを追加）を更新
4. `fred_client.py` のコード変更は不要（任意の FRED series ID を受け付ける）

### 最新の検証

**日付**：2026-04-18 — 全 25 series ACTIVE、CSV エンドポイントから 2026 データを返却。月次 GDP proxy として `nowcast` group（GDPNOW、CFNAI、WEI、USALOLITOAASTSAM）を追加。
