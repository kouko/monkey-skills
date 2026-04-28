# korea-macro/docs

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

維護 `korea-macro` 所需的開發者導向文件與工具。

## 內容

### Catalog

- **`bok-ecos-keystat-catalog.md`** — 透過 `FinanceDataReader` 不需 API key 即可存取的全部 98 個 BOK ECOS KEYSTAT 代碼之人類可讀 catalog。依分類（monetary、rates、markets、FX、activity、CI、labor、BoP、prices、demographics）分組。
- **`bok-ecos-keystat.json`** — `probe-keystat.py` 產出的原始 JSON，可在 BOK 更新 KEYSTAT 後重新匯入或 diff。

### 工具

- **`tools/probe-keystat.py`** — 重新探測 KEYSTAT catalog（預設掃描 `K001-K500`）。BOK 新增關鍵指標時重跑。

## 維運

當 BOK 更新 KEYSTAT 時（少見，每年 1-2 次），重新執行 probe，並將輸出與已 commit 的 JSON 做 diff：

```bash
cd investing-toolkit/skills/korea-macro/docs/tools
uv run probe-keystat.py
diff <(jq --sort-keys . ../bok-ecos-keystat.json) <(jq --sort-keys . ../bok-ecos-keystat.json.new)
```

若有新增項目，請更新 `bok-ecos-keystat-catalog.md` 加入新列，並決定是否將其升格為 preset（10-group 結構參見 `SKILL.md`，自 v1.8.0 起）。

## 完整 ECOS vs KEYSTAT

本文件僅涵蓋 **KEYSTAT**（BOK 精選的 100대 통계지표 子集，約 98 個代碼）。完整 BOK ECOS catalog（10,000+ series）需要 API key。詳見 `bok-ecos-keystat-catalog.md` 底部「Why not the full ECOS catalog?」段。
