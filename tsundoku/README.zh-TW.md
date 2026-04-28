# tsundoku 積読

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**Version**: 0.11.0
**Part of**: [monkey-skills](../)

> *tsundoku（積読）* — 日文，指買了卻還沒讀的書堆。
> 此 plugin 把這座書堆轉成可執行的知識。

依 **title / author / series / 出版日期 / category / description 全文 / 閱讀狀態 / 語言** 搜尋 Kobo 電子書 library，把符合的書以卡片呈現，下載選定的書為無 DRM 的 EPUB，將下載的 EPUB 轉為依章節切分的 Markdown，並透過 RIA-TV++ pipeline **將書蒸餾成原子化的 agent skill**（Adler analytical read → 5 個 parallel extractor → triple verification → RIA++ render → Zettelkasten linking → adversarial pressure test）。輸出語言會自適應（EN / 日本語 / 繁體中文）。底層包裝 [`subdavis/kobo-book-downloader`][kobodl]，並以 [pandoc][pandoc] 處理 EPUB→Markdown 階段。蒸餾方法論改編自 [`kangarooking/cangjie-skill`][cangjie]（MIT）。

[kobodl]: https://github.com/subdavis/kobo-book-downloader
[pandoc]: https://pandoc.org
[cangjie]: https://github.com/kangarooking/cangjie-skill

## Skills

| Skill | Slash command | 何時使用 |
|---|---|---|
| [`kobo-auth`](skills/kobo-auth/SKILL.md) | `/kobo-auth` | 首次設定、登入、帳號移轉、credential 輪替 |
| [`kobo-library`](skills/kobo-library/SKILL.md) | `/kobo-library` | 日常使用 — 搜尋、列表、批次下載 EPUB |
| [`book-extract`](skills/book-extract/SKILL.md) | `/book-extract` | 將 EPUB → 依章節切分的 Markdown |
| [`book-distill`](skills/book-distill/SKILL.md) | `/book-distill` | Markdown → 原子化的 agent skill（透過 RIA-TV++） |
| (router) | `/tsundoku` | 依意圖自動 route；模糊請求會詢問要走哪一步 |

命名慣例：
- **`kobo-*`** — 來源平台層（auth + library）：與 Kobo / kobodl 綁定。未來的
  `kindle-*` / `apple-books-*` 兄弟 skill 會比照此模式。
- **`book-*`** — 不分格式的處理層（extract + distill）：可作用於任何 EPUB /
  任何依章節切分的 Markdown，不論來源。未來的 `paper-distill`（學術論文）
  或 `transcript-distill`（podcast）會加入此層。

## Quick Start

### A. 全新設定（互動式啟用）

```bash
# 安裝 binary + 執行 device-flow login（會開啟 kobo.com/activate 的 code）
bash tsundoku/skills/kobo-auth/scripts/kobo_install.sh
bash tsundoku/skills/kobo-auth/scripts/kobo_login.sh add
```

依提示操作：在瀏覽器打開 `https://www.kobo.com/activate`、登入、輸入 kobodl
顯示的 6 位數 code。Activation 註冊完成後，指令會自動結束。

### B. 從既有的 kobodl 安裝移轉

如果你已在他處有 credentials（例如舊版 `~/KobodlLibrarySync/` shell script，
或 upstream 的 `~/.config/kobodl/`），可跳過 activation flow：

```bash
bash tsundoku/skills/kobo-auth/scripts/kobo_install.sh
bash tsundoku/skills/kobo-auth/scripts/kobo_login.sh \
    import-from ~/KobodlLibrarySync/config/kobodl.json
```

### C. 搜尋與下載

```bash
source tsundoku/skills/kobo-library/scripts/tsundoku_paths.sh  # 或任何其他 skill
export TMPDIR="$TSUNDOKU_TMPDIR"
mkdir -p "$TSUNDOKU_DOWNLOADS"

# 重新整理 library index
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"

# 搜尋（例如「提到 behavioral economics、2020 年後出版、尚未讀」的書）—
# 以精緻卡片預覽
python3 tsundoku/skills/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "行為經濟,行為金融,Behavioral" \
    --pub-after 2020 --status ReadyToRead --format markdown

# 下載選定的 RevisionId（idempotent — 已在 disk 上的會跳過）
bash tsundoku/skills/kobo-library/scripts/kobo_get.sh "$REVISION_ID"

# 或以 pipe 傳入過濾後的集合
python3 tsundoku/skills/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" --series "Silent Witch" --format ids \
  | bash tsundoku/skills/kobo-library/scripts/kobo_get.sh --convert-pdf
```

### D. EPUB → 依章節切分的 Markdown（為 book→skill 鋪路）

```bash
# 一次性：確認已安裝 pandoc
bash tsundoku/skills/book-extract/scripts/install_pandoc.sh

# 轉檔（預設使用 $TSUNDOKU_MARKDOWN_DIR — 不需要 --out-dir）
python3 tsundoku/skills/book-extract/scripts/epub_to_markdown.py \
    --epub "$EPUB_PATH" --strip-images --strip-frontmatter
# → 寫入 ~/.tsundoku/cache/markdown/<title-slug>-<id8>/index.md + 章節檔

# 完成後清掉 markdown cache
bash tsundoku/skills/book-extract/scripts/cache_clear.sh
```

### E. Markdown → 原子化 skill 集（book → skill）

```bash
# 從 extracted markdown 啟動一個 book-distill 工作目錄
bash tsundoku/skills/book-distill/scripts/book_distill_init.sh \
    一九八四-b9152ffe
# → ~/.tsundoku/cache/distilled/一九八四-b9152ffe/{candidates/, rejected/,
#                                                   BOOK_OVERVIEW.md.draft,
#                                                   metadata.snapshot.json,
#                                                   chapters.list}

# 接著 Claude 會讀取 book-distill 的 SKILL.md，跑完 6 個 stage 的 pipeline：
#   Stage 0: Adler analytical read         → BOOK_OVERVIEW.md
#   Stage 1: 5 個 parallel extractor        → candidates/
#   Stage 1.5: Triple verification          → verified.md（約 30-50% 通過）
#   Stage 2: RIA++ skill render             → <skill-slug>/SKILL.md
#   Stage 3: Zettelkasten linking           → INDEX.md
#   Stage 4: Adversarial pressure test       → test-prompts.json
```

各 section 的內文使用來源語言；YAML metadata + slug 使用英文。

## 儲存配置（單一 root，依平台分子目錄）

```
~/.tsundoku/                  ← TSUNDOKU_ROOT
├── kobo/                       Kobo 平台狀態
│   ├── auth/                    chmod 700
│   │   └── kobodl.json          chmod 600（Kobo session credentials）
│   └── bin/kobodl-macos         14 MB upstream binary
├── tmp/                        共用的 TMPDIR override（PYI-1270 修正）
└── cache/                      可重生、可整批清空
    ├── kobo/library.json        cached library export
    └── markdown/<book>/...      EPUB → MD（不分平台）

~/Books/kobo/                 ← TSUNDOKU_DOWNLOADS（使用者可見的 EPUB）
```

未來 `kindle-*` / `apple-books-*` skill 落地後，會比照配置在
`~/.tsundoku/kindle/`、`~/.tsundoku/cache/kindle/` 等目錄底下。

**兩個決策點 env 變數** — 設定這些可重新定位：

| Var | 預設 | 用途 |
|---|---|---|
| `TSUNDOKU_ROOT` | `~/.tsundoku` | 全部 toolkit 狀態（auth + binary + cache） |
| `TSUNDOKU_DOWNLOADS` | `~/Books/kobo` | 使用者可見的 EPUB 下載 |

**五個衍生路徑**由上面兩個計算得出（不要直接設定）：

| Var | 範圍 |
|---|---|
| `TSUNDOKU_TMPDIR` | 共用 |
| `TSUNDOKU_MARKDOWN_DIR` | 共用（cache/markdown） |
| `TSUNDOKU_KOBO_CONFIG` | Kobo：kobodl.json |
| `TSUNDOKU_KOBO_BINARY` | Kobo：kobodl-macos |
| `TSUNDOKU_KOBO_LIBRARY_JSON` | Kobo：library export |

source 任一 skill 的 `scripts/tsundoku_paths.sh` 時都會 export 這些變數。

`kobo/auth/` 子目錄是 `chmod 700`，`kobodl.json` 檔案是 `chmod 600`。
`cache/` 子樹可重生 — 任何時候都能透過
`book-extract/scripts/cache_clear.sh` 清空。

## 儲存庫結構

```
tsundoku/
├── .claude-plugin/plugin.json
├── README.md
├── commands/                    # slash command（與 skill 1:1 + 1 個 router）
│   ├── tsundoku.md              #   /tsundoku（router）
│   ├── kobo-auth.md             #   /kobo-auth
│   ├── kobo-library.md          #   /kobo-library
│   ├── book-extract.md          #   /book-extract
│   └── book-distill.md          #   /book-distill
└── skills/
    ├── kobo-auth/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobo_install.sh    # binary 下載（idempotent）
    │       └── kobo_login.sh      # add / status / remove / import-from / path
    ├── kobo-library/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobo_query.py      # 過濾 --export-library JSON、5 種輸出格式
    │       └── kobo_get.sh        # 依 RevisionId 下載（args 或 stdin）
    ├── book-extract/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── install_pandoc.sh     # brew → standalone fallback
    │       ├── epub_to_markdown.py   # NCX 驅動章節切分 + pandoc + 清理
    │       └── cache_clear.sh   # 清除 extracted markdown / library cache
    └── book-distill/                 # RIA-TV++ pipeline（fork 自 cangjie-skill，MIT）
        ├── SKILL.md                  # 頂層 orchestrator
        ├── ATTRIBUTION.md             # upstream credits + license
        ├── methodology/              # 7 個檔案：00-overview + 01-06 各 stage 詳解
        ├── extractors/               # 5 個 parallel sub-agent prompt
        │   ├── framework-extractor.md
        │   ├── principle-extractor.md
        │   ├── case-extractor.md
        │   ├── counter-example-extractor.md
        │   └── glossary-extractor.md
        ├── templates/                # BOOK_OVERVIEW / SKILL / INDEX / test-prompts
        └── scripts/
            └── book_distill_init.sh  # 從 book-extract 輸出啟動 distill 目錄
```

## 系統需求

- macOS 或 Linux（kobodl 出貨 macOS binary 並自動安裝；Linux 使用者可
  `pipx install kobodl` 並 override `TSUNDOKU_KOBO_BINARY`）
- Python 3.9+（query / extract scripts 只用 stdlib）
- 至少有一本已購書的 Kobo 帳號
- 選用：pandoc（給 `book-extract` 用 — 透過 brew 或 GitHub release standalone
  自動安裝；如已安裝則 no-op）
- 選用：[Calibre][calibre] 用於 EPUB → PDF 轉檔

[calibre]: https://calibre-ebook.com/download_osx

## 安全性

- `kobodl.json` 內含你的 **Kobo session credentials** — 等同密碼。
  絕不 commit、不貼到聊天、不上傳
- `kobo_login.sh` 在每次觸碰該檔的操作後都會強制 `chmod 600`
- 撤銷 session 的方法：刪除 `kobodl.json`，並造訪 Kobo 的
  [Authorized Devices](https://www.kobo.com/account/devices) 頁面
- 共用機器上請使用獨立的 macOS 使用者帳號

## 注意事項

- `book wishlist` 子指令目前在 upstream 損壞（kobodl 0.10.x）；只支援
  `book list`
- `Description` 欄位被 Kobo 的 API 限制在 500 字元（出版社 ONIX copy，
  不是 synopsis）
- macOS 會自動安裝預先建構的 kobodl binary；Linux/Windows 使用者請以
  `pipx install kobodl` 安裝 kobodl，並在 source `tsundoku_paths.sh` 後
  override `TSUNDOKU_KOBO_BINARY`

## 由來

把 [`kobodl-library-sync.sh`][ancestor] 單檔 shell script 一般化為一套
search-first 的 toolkit，並把 auth、runtime、extraction 適當切分；提供
metadata-rich query；產出供 LLM ingest 的依章節切分 Markdown；並把所有
資料統一收在 `~/.tsundoku/` 單一 root 底下。

[ancestor]: https://github.com/kouko/kobodl-library-sync
