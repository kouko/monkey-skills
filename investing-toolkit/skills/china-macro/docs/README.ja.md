# china-macro / docs

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

開発者向けの参考資料。skill のランタイムでは読み込まれません — 将来の実装作業（例：industrial / trade 指標の古い akshare ミラーを置き換える補完用 `nbs_client.py`）が WAF 圧下で NBS API を再探索せずに参照できるよう、ここに保管しています。

ユーザー向けの指標説明は `../references/` に置かれ、`SKILL.md` から参照され Claude に消費されます。本ディレクトリのファイルは、repo を閲覧する人間向けです。

## ファイル

| ファイル | 用途 |
|---|---|
| `nbs-indicator-catalog.md` | リバースエンジニアリングした `data.stats.gov.cn` new-SPA API：endpoint contracts、`dts` レンジ構文、session/cookie ルール、WAF 挙動、akshare↔NBS preset マッピング、CPI 実例 |
| `nbs-tree-monthly.md` | 月次 catalog tree（14 トップカテゴリ、605 leaf tables）— folder と leaf に UUID 付き |
| `nbs-tree-quarterly.md` | 四半期 tree（8 カテゴリ、116 leaves） |
| `nbs-tree-yearly.md` | 年次 tree（28 カテゴリ、2187 leaves） |
| `nbs-indicators-monthly.{json,md}` | 月次 leaf ごとの完全な指標 UUID catalog（605 cids、約 15k indicator rows） |
| `nbs-indicators-quarterly.{json,md}` | 116 cids、約 3k indicators |
| `nbs-indicators-yearly.{json,md}` | 2187 cids、約 57k indicators |
| `tools/` | 上記 catalog を取得するための one-shot admin scripts。再実行のタイミングは `tools/README.md` を参照。 |

### 2 層 catalog の関係

- `nbs-tree-*.md` — NBS catalog の**ツリー**。Folder はナビゲーション、leaf は統計表を表します。Leaf の `_id` がランタイム API の `cid` パラメータになります。
- `nbs-indicators-*.{json,md}` — 各 leaf table の**内部**。各行は独立した統計指標で、独自の UUID を持ちます。これらの UUID は `POST getEsDataByCidAndDt` の `indicatorIds[]` 配列に入ります。

両者を組み合わせ、tree がどの `cid` を渡すかを教え、indicator catalog がどの `indicatorIds[]` を渡すかを教えます。ランタイムの `nbs_client.py` は preset ごとに `(cid, indicatorIds[])` のタプルをハードコードし、WAF 検知につながるランタイムでの discovery を避けます。

### 合計（2026-04-18 取得時点）

- **2908 leaf tables**（`cid`s）— 月次・四半期・年次にまたがる
- **約 75,719 個の独立した指標**（`indicatorId`s）
- 1 leaf あたり平均 ~26 指標（CPI は 13、小さなテーブルは 1-3、分行業工業經濟指標のようなクロス表は 80+）
