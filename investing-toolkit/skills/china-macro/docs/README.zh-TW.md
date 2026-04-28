# china-macro / docs

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

開發者導向的參考資料。Skill runtime 不會載入 — 保留於此是為了讓未來的實作工作（例如撰寫補充版的 `nbs_client.py` 以替換 industrial / trade 指標的過期 akshare 鏡像）能查閱，無需在 WAF 壓力下重新探索 NBS API。

使用者導向的指標說明位於 `../references/`，由 `SKILL.md` 引用、由 Claude 消費。本目錄的檔案是供瀏覽 repo 的開發者參考。

## 檔案

| 檔案 | 用途 |
|---|---|
| `nbs-indicator-catalog.md` | 逆向工程的 `data.stats.gov.cn` new-SPA API：endpoint contracts、`dts` range 語法、session/cookie 規則、WAF 行為、akshare↔NBS preset 對照、CPI 範例 |
| `nbs-tree-monthly.md` | 月頻 catalog tree（14 個頂層分類，605 個 leaf tables）— folders 與 leaves 連同其 UUID |
| `nbs-tree-quarterly.md` | 季頻 tree（8 個分類，116 個 leaves） |
| `nbs-tree-yearly.md` | 年頻 tree（28 個分類，2187 個 leaves） |
| `nbs-indicators-monthly.{json,md}` | 每個月頻 leaf 完整的指標 UUID catalog（605 cids，約 15k indicator rows） |
| `nbs-indicators-quarterly.{json,md}` | 116 cids，約 3k indicators |
| `nbs-indicators-yearly.{json,md}` | 2187 cids，約 57k indicators |
| `tools/` | 用於擷取上述 catalog 的一次性 admin scripts。何時需要重新執行請見 `tools/README.md`。 |

### 兩層 catalog 如何搭配

- `nbs-tree-*.md` — NBS catalog 的**樹狀結構**。Folders 用於導航，leaves 代表統計表。Leaf 的 `_id` 即 runtime API 中的 `cid` 參數。
- `nbs-indicators-*.{json,md}` — 每個 leaf table **內部**的內容。每一列為一個獨立統計指標，擁有自己的 UUID。這些 UUID 會放入 `POST getEsDataByCidAndDt` 的 `indicatorIds[]` array。

兩者搭配：tree 告訴你要傳哪個 `cid`，indicator catalog 告訴你要傳哪些 `indicatorIds[]`。Runtime 的 `nbs_client.py` 為每個 preset hardcode `(cid, indicatorIds[])` tuple，以避免 runtime discovery（會被 WAF 偵測）。

### 總計（2026-04-18 擷取）

- **2908 個 leaf tables**（`cid`s），跨月頻/季頻/年頻
- **約 75,719 個獨立指標**（`indicatorId`s）
- 每個 leaf 平均約 26 個指標（CPI 有 13 個，小表 1-3 個，分行業工業經濟指標等交叉表 80+）
