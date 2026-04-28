# kobo-library

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 用 10+ 種過濾條件搜尋 Kobo 電子書 library，把符合的書以卡片呈現，
> 把選定的書下載成無 DRM 的 EPUB。

屬於 [tsundoku](../..) plugin。Claude 載入的 skill spec 是
[`SKILL.md`](SKILL.md)；本 README 給人類閱讀。

## 它做什麼

使用者面向的流程：

```
"找一本近 5 年內的 behavioral economics 的書，我還沒讀過的"
                              ↓
                kobo_query.py 過濾本機 library JSON
                              ↓
                卡片（markdown / table / summary / ids）
                              ↓
                "看起來不錯 — 下載 #2 跟 #5"
                              ↓
                kobo_get.sh 下載選定的 RevisionId
                              ↓
                ~/Books/kobo/ 中的無 DRM .epub
```

## 前置條件

[`kobo-auth`](../kobo-auth) 必須先成功跑過。如果
`bash ../kobo-auth/scripts/kobo_login.sh status` 不回 0，請先處理那個。

## Quick start

```bash
# 載入路徑（取得 TSUNDOKU_KOBO_BINARY / _CONFIG / _LIBRARY_JSON 等）
source scripts/tsundoku_paths.sh
mkdir -p "$TSUNDOKU_DOWNLOADS"

# 重新整理 library index（把 Kobo metadata export 成本機 JSON）
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"

# 搜尋 — 以卡片預覽
python3 scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "行為經濟,Behavioral" \
    --pub-after 2020 --status ReadyToRead \
    --format markdown

# 下載選定的 RevisionId
bash scripts/kobo_get.sh "$REVISION_ID"

# 或透過 pipe 批次處理
python3 scripts/kobo_query.py --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --series "Silent Witch" --format ids \
  | bash scripts/kobo_get.sh
```

## `kobo_query.py` 支援的 filter

| Filter | 效果 |
|---|---|
| `--title PATTERN` | Title substring 比對 |
| `--author PATTERN` | 任一 contributor substring 比對 |
| `--series PATTERN` | series 名稱 substring 比對 |
| `--description PATTERN` | 已清理 description 全文（逗號 = OR） |
| `--description-all PATTERN` | 逗號分隔的關鍵字；全部都得 match |
| `--status` | `Finished` / `Reading` / `ReadyToRead` |
| `--language CODE` | `zh` / `ja` / `en` ... |
| `--country CODE` | `tw` / `jp` / `us` ... |
| `--publisher PATTERN` | publisher 名稱 substring |
| `--isbn ISBN` | 完全 ISBN |
| `--pub-after YYYY[-MM[-DD]]` | 出版日 >= |
| `--pub-before YYYY[-MM[-DD]]` | 出版日 <= |
| `--genre UUID` / `--category UUID` | UUID 比對（進階） |
| `--min-progress N` / `--max-progress N` | 閱讀進度 0-100 |

輸出格式：`table` / `json` / `ids` / `markdown` / `summary`。
所有 filter 以 AND 結合。

## 此資料夾的檔案

| Path | 角色 |
|---|---|
| [`SKILL.md`](SKILL.md) | Claude 載入的 skill spec（完整 filter / 輸出 reference） |
| [`scripts/kobo_query.py`](scripts/kobo_query.py) | 過濾 library JSON、5 種輸出格式。純 stdlib |
| [`scripts/kobo_get.sh`](scripts/kobo_get.sh) | 依 RevisionId 下載（args 或 stdin pipe），idempotent skip |

## 輸出位置

```
~/Books/kobo/
└── <author> - <title> <id8>.epub      ← 使用者可見、無 DRM
```

EPUB 開箱即無 DRM（kobodl 在下載時即解密）。

## 另見

- [`kobo-auth`](../kobo-auth) — 先 login
- [`book-extract`](../book-extract) — 自然下一步：把 EPUB 變成依章節
  切分的 Markdown 供 LLM ingest
- [`tsundoku` README](../..) — 完整 pipeline 概覽
