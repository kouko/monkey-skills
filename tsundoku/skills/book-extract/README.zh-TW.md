# book-extract

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 把 EPUB 轉成依章節切分的 Markdown，供 LLM ingest。
> Format-agnostic — 適用任何 EPUB，不限 Kobo 來源。

屬於 [tsundoku](../..) plugin。Claude 載入的 skill spec 是
[`SKILL.md`](SKILL.md)；本 README 給人類閱讀。

## 為什麼自製 converter（而不是直接用 pandoc）？

許多 EPUB 用 Kobo 專屬 markup（`<span class="koboSpan">`）取代語意化的
`<h1>` 來標章節。直接跑 pandoc 會產出 **零個 markdown heading**，
讓後續的 chunk 切分整個失效。

本 skill 改由 EPUB 的 `toc.ncx`（或 EPUB3 nav）驅動章節切分 — 對沒採用
語意化章節標記的書也能運作。已在 Kobo / 角川 / 時報 / O'Reilly 的 EPUB
端到端驗證過。

## Pipeline

```
EPUB
  ↓
unzip + parse OPF/NCX        ← 依序的 spine items（XHTML 檔）
                              + 從 NCX 對應的章節標籤
  ↓ 對每個 spine item
pre-clean XHTML              ← 去除 kobo span、SVG、script、空 div
  ↓
pandoc XHTML → GFM Markdown
  ↓
post-clean MD                ← 去除 leading 全形縮排、hard-break `\`
                              的殘渣、raw <img> tag
  ↓
NN-<slugified-label>.md      ← H1 = NCX 的章節標籤
+ index.md（TOC + token 估算）
+ metadata.json（title / authors / publisher / ISBN / chapters）
```

## Quick start

```bash
# 一次性：確認已安裝 pandoc（brew → standalone fallback）
bash scripts/install_pandoc.sh

# 載入路徑
source scripts/tsundoku_paths.sh
EPUB=~/Books/kobo/"<author> - <title> b9152ffe.epub"

# 轉檔（預設使用 $TSUNDOKU_MARKDOWN_DIR — 不需要 --out-dir）
python3 scripts/epub_to_markdown.py --epub "$EPUB" \
    --strip-images --strip-frontmatter

# → 寫入 ~/.tsundoku/cache/markdown/<title-slug>-<id8>/
#       index.md + metadata.json + NN-chapter.md 檔案
```

## 轉換選項

| Flag | 效果 |
|---|---|
| `--out-dir DIR` | 輸出 ROOT（內部會自動建每書子目錄；預設 `$TSUNDOKU_MARKDOWN_DIR`） |
| `--no-subdir` | 停用每書子目錄；直接寫入 `--out-dir` |
| `--strip-images` | 丟棄圖片 reference — 文字為主的書建議使用 |
| `--strip-frontmatter` | 跳過書封 / 目錄 / 版權 / cover / contents 等 |
| `--strip-backmatter` | 跳過索引 / 致謝 / index / acknowledg（附錄 / 譯後記保留） |
| `--merge-small N` | 把 token 數 < N 的章節合併進前一章 |
| `--pandoc PATH` | 覆寫 pandoc binary |
| `--quiet` | 關閉每章進度輸出 |

## 輸出結構

```
~/.tsundoku/cache/markdown/<title-slug>-<id8>/
├── index.md                      ← TOC + 各章 token 估算
├── metadata.json                 ← title / authors / publisher / ISBN / chapters[]
├── 01-cover.md                   ←（若 --strip-frontmatter 則跳過）
├── 02-序.md
├── 03-chapter-01.md              ← H1 = NCX 的章節標籤
├── 04-chapter-02.md
...
```

章節檔名：`NN-<slugified-label>.md`（CJK 保留）。子目錄名：
`<slug-of-title>` 或 `<slug-of-title>-<id8>`，後者用於輸入檔名符合
kobodl 命名 pattern 時。

## Token 預算參考

| 書本大小 | 總 token（CJK 估算） | 策略 |
|---|---|---|
| ≤80K | one-shot context | 一次 Claude call 餵整本 |
| 80-150K | chapter-by-chapter | 一檔一檔迭代 |
| 150K+ | outline-first | 先摘要，再針對性地回讀 |

## Cache 管理

```bash
# 全清（markdown + library.json），保留 auth + EPUB
bash scripts/cache_clear.sh

# 清掉一本書的 markdown
bash scripts/cache_clear.sh --book 一九八四-b9152ffe

# 預覽
bash scripts/cache_clear.sh --dry-run

# 只清掉 library.json（強制重新 export）
bash scripts/cache_clear.sh --library-only
```

Auth（`~/.tsundoku/kobo/auth/`）、binary、與下載的 EPUB **絕不**會被動到。

## 此資料夾的檔案

| Path | 角色 |
|---|---|
| [`SKILL.md`](SKILL.md) | Claude 載入的 skill spec（完整轉換 + chunk reference） |
| [`scripts/install_pandoc.sh`](scripts/install_pandoc.sh) | Brew → GitHub-release standalone fallback |
| [`scripts/epub_to_markdown.py`](scripts/epub_to_markdown.py) | NCX 驅動章節切分 + pandoc + 清理。約 620 行，純 stdlib |
| [`scripts/cache_clear.sh`](scripts/cache_clear.sh) | 清除 extracted markdown / library cache（4 種模式） |

## 接受的來源

- ✅ Kobo 來源 EPUB（透過 [`kobo-library`](../kobo-library)）
- ✅ Project Gutenberg
- ✅ BookWalker / 角川 / 講談社 下載匯出
- ✅ Apple Books 匯出
- ✅ 手工準備的 EPUB
- ⚠️ 沒 NCX 也沒 EPUB3 nav 的 EPUB 會 fallback 到以檔名 stem 當章節
- ❌ PDF（不同格式，需要另一個 `pdf-extract` skill）

## 另見

- [`book-distill`](../book-distill) — 自然下一步：把切分好的 Markdown
  變成一組連貫的 agent skill
- [`tsundoku` README](../..) — 完整 pipeline 概覽
