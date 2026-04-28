# china-macro / docs / tools

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

用於擷取 `docs/` 下 NBS 指標 catalog 的一次性 admin scripts。**並非** runtime skill 的一部分 — 僅在 NBS 公布新基期區段時（約每 5 年）或 `queryIndicatorsByCid` response schema 變更時才執行。

## Scripts

| Script | 用途 | 一般執行時間 |
|---|---|---|
| `probe-nbs-tree.py` | 對全部 3 個頻率遞迴呼叫 `queryIndexTreeAsync`；輸出 `nbs-tree-{monthly,quarterly,yearly}.md`（folder+leaf UUID catalog） | ~15-20 分 |
| `probe-nbs-indicators.py` | 對 3 棵 tree 中每個 leaf cid 呼叫 `queryIndicatorsByCid`；快取每個 cid 的 JSON；產出彙總後的 `nbs-indicators-{frequency}.{json,md}` | ~60-90 分 |
| `tree-to-markdown-tables.py` | 將巢狀 bullet 形式的 tree 輸出轉為依 category 分區的表格（曾用於一次性格式遷移） | 數秒 |

## 何時重新執行

### 約每 5 年（基期修訂）
NBS 約每 5 年公布方法論修訂。2031 年時，目前的 `(2026-)` CPI/PPI series 幾乎可確定會凍結為 `(2026-2030)`，並出現新的 `(2031-)` series 帶有全新 UUID。請重新執行 `probe-nbs-tree.py` 與 `probe-nbs-indicators.py` 以納入新的 leaves。

### 確認上游有變更後
若 skill 使用者回報 `nbs_client.py` 回傳過期/空白資料，先手動執行一次 `queryIndicatorsByCid` 驗證。若 schema 已漂移，再重新執行 probe scripts。

### 臨時：新增 preset 時
直接在現有 `docs/nbs-indicators-*.md` 內 grep 你要的概念 — 指標 UUID 已預先擷取完畢。除非該指標對 NBS 而言確實是全新項目，否則無需重跑。

## 前置條件

- Python 3.9+（僅使用 stdlib，無外部相依套件）
- 對 `data.stats.gov.cn` 的對外 HTTPS
- **NordVPN 或同類**：已驗證可從台灣 / Anthropic 基礎設施透過 VPN 連線。WAF 會在大量遍歷時觸發，但 scripts 會處理指數退避 + session 輪換。

## 使用方式

```bash
# Tree 結構（擷取 folder/leaf 階層 + catalog ID）
python3 probe-nbs-tree.py
# → 輸出 /tmp/nbs-tree-{monthly,quarterly,yearly}.txt
# → 手動複製並套用 tree-to-markdown-tables.py 產生
#   docs/nbs-tree-*.md

# 每個 leaf 的指標 UUID（耗時 60-90 分）
python3 probe-nbs-indicators.py
# → 輸出 /tmp/nbs-probe-cache/{cid}.json（可續跑）
# → 彙總至 /tmp/nbs-indicators-final.{json,md}
# → 手動依頻率切分後複製到 docs/
```

## WAF / rate-limit 備註

`probe-nbs-indicators.py` 在 2026-04-18 擷取期間調校過：

- Base throttle：透過 NordVPN 執行時 requests 間 0.5s（觀測到可運作的 IP 範圍為 `194.233.x.x` / M247）。住宅非 VPN IP 較安全的設定為 1.5s。
- Session priming：必先 GET 首頁建立 `JSESSIONID` cookie；後續所有 API 呼叫沿用同一 session。
- WAF 偵測：response body 開頭為 `<` 表示觸發 WZWS JS challenge。Script 會以指數退避（60s、120s、240s、…，上限 10 分）並輪換 session 後重試。
- HTTP `RemoteDisconnected` / 暫時性 `URLError`：以線性退避（2s、4s、6s）重試 3 次。
- 2026-04-18 一次完整 catalog 跑共 0 次 WAF 事件，1 次暫時性網路錯誤（為求完整性手動重試該錯誤）。

## 輸出 schema（消費端參考）

```json
{
  "<cid-uuid>": {
    "cid": "<cid-uuid>",
    "path": "月度 → 价格指数 → ... → 全国居民消费价格分类指数 (2026-)",
    "freq": "月度",
    "leaf_name": "全国居民消费价格分类指数 (2026-)",
    "indicators": [
      {
        "_id": "<indicator-uuid>",
        "name": "居民消费价格指数 (上年同月=100)",
        "group": "居民消费价格指数",
        "unit_code": "<unit-uuid>",
        "unit_name": "%",
        "order": 1,
        "kj1_name": "上年同月=100"
      }
    ]
  }
}
```

錯誤項目以 `{"cid": "...", "error": "...", "path": "..."}` 取代正常結構。
