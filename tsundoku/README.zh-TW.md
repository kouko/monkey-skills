# tsundoku 積読

語言：[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 把買了卻沒讀的 e-book 山，轉成 agent 可呼叫的 skill — login、search、download、extract、distill。

> ⚠️ **僅支援 Claude Code CLI**。Cowork sandbox 會阻擋 `kobo.com` 的 device-flow 認證與 EPUB 下載。請見下方 [Cowork 相容性](#cowork-相容性)。

**Version**：0.11.0 ・ **License**：MIT ・ **Part of**：[monkey-skills](../README.md)

## Cowork 相容性

此 plugin **與 Claude Desktop 的 Cowork tab 不相容**。4 個 skill 中有 2 個（`kobo-auth`、`kobo-library`）會對 `kobo.com` 與 kobodl 下載 CDN 發出對外請求，而這兩個目標都不在 Cowork 的 URL allowlist 內。剩下 2 個 skill（`book-extract`、`book-distill`）只處理本機檔案，單獨在 Cowork 內可動，但 pipeline 必須整段串起來才有意義。

請從 **Claude Code CLI** 執行此 plugin（或使用 Claude Desktop 內嵌的 Code tab）。同樣的 sandbox 結論在 [`investing-toolkit`](../investing-toolkit/docs/mcp-setup.md) 也有完整文件。

## Background

積読（つんどく）是日文，指買回家卻沒讀、堆在那邊的書。每次新買就多累積一份「擁有但沒被取出的知識」。此 plugin 把這座書山當成起點 — 把已經付過錢的 e-book 隨需取出，轉成 agent 可重複呼叫的方法論。

pipeline 共 4 stage，每段之間以磁碟上的穩定 artifact 隔開，每個 stage 都能獨立重跑：

```
kobo-auth ──▶ kobo-library ──▶ book-extract ──▶ book-distill
 (一次)         (日常)            (每本書)         (每本書)

   login  ──▶  EPUB on disk ──▶ chunked .md  ──▶ atomic SKILL.md set
```

`kobo-*`（綁 Kobo platform）與 `book-*`（與格式無關）的分層是刻意的：未來的同層 sibling 例如 `kindle-*` 或 `apple-books-*` 會排在 `kobo-*` 旁邊，而 `book-extract` / `book-distill` 接受任何來源的 EPUB / Markdown 目錄。

## Skills

| Skill | Layer | 角色 |
|---|---|---|
| [`tsundoku`](commands/tsundoku.md) | router | 依使用者意圖（login / search / convert / distill）派送到對應 skill |
| [`kobo-auth`](skills/kobo-auth/SKILL.md) | source-platform（`kobo-*`） | 首次 setup、device-flow 認證、credential 輪換、multi-account |
| [`kobo-library`](skills/kobo-library/SKILL.md) | source-platform（`kobo-*`） | 以 title / author / series / publication date / category / description text / reading status / language 搜尋 Kobo library，下載挑選的書為 DRM-free EPUB |
| [`book-extract`](skills/book-extract/SKILL.md) | format-agnostic（`book-*`） | 透過 NCX 驅動的章節切分把 EPUB 轉成逐章 Markdown；CJK 安全 |
| [`book-distill`](skills/book-distill/SKILL.md) | format-agnostic（`book-*`） | 以 RIA-TV++（Adler 分析閱讀 → 5 個並行 extractor → 三重驗證 → RIA++ render → Zettelkasten linking → 對抗式壓力測試）把 Markdown 蒸餾為 atomic SKILL.md 集 |

**命名規則**：`kobo-*` skill 綁定 Kobo platform（auth、library API、kobodl binary）。`book-*` skill 接受任何 EPUB 或 chunked Markdown，不依賴 Kobo。也就是 `book-extract` 與 `book-distill` 對其他來源（手動丟進來的 EPUB、圖書館借閱、public domain）也直接適用。

## Quick start

5 個常見情境。把意圖用自然語言講出來，router skill 會自動派送。

### A. Router — 「我想用 tsundoku」

```
/tsundoku
```

說明 4 stage、問你要從哪一步開始。第一次使用請依 B → C → D → E 順序執行。

### B. 首次 login（`kobo-auth`）

```
/tsundoku-kobo-auth
```

skill 會把 kobodl binary 安裝到 `~/.tsundoku/kobo/bin/`，然後**把 device-flow 認證交回你的終端機執行** — kobodl 會印出一組 6 位數驗證碼，需要你到 `https://www.kobo.com/activate` 輸入；若透過 Claude 的 Bash tool 跑，畫面會 buffer 起來、驗證碼在執行中途被 truncate 看不到。Claude 等你回覆「done」之後，再用 `kobo_login.sh status` 確認認證狀態。

如果你已經有現成的 `kobodl.json`：

```
「把 ~/KobodlLibrarySync/config/kobodl.json 的 kobodl 認證匯入」
```

### C. 搜尋與下載（`kobo-library`）

```
/tsundoku-kobo-library
```

接著用自然語言描述要找的東西。例如：

```
「找書名有行為經濟學的，最近五年內出版的，我還沒讀過的」
「Silent Witch 系列全部，整套下載」
「兩年以上前買的、還沒開始讀的」
```

skill 會把意圖映射成 `kobo_query.py` filter（title / author / series / publisher / `--description` 在 title + description text 跨欄位關鍵字搜尋 / `--pub-after` / `--purchased-after` / `--status` / `--language` / ...），把比對結果以 table / markdown card / summary 呈現，讓你確認後透過 `kobodl book get` 下載到 `~/Books/kobo/`。

### D. 轉換（`book-extract`）

```
/tsundoku-book-extract
```

把 EPUB 路徑丟進來（不一定要是 Kobo 的）。skill 第一次會 install pandoc，parse EPUB 的 NCX（目次）取得正規章節邊界，pre-clean Kobo 特有的 markup（`<span class="koboSpan">`），逐章跑 pandoc，把每章 Markdown 寫到 `~/.tsundoku/cache/markdown/<title-slug>-<id8>/` 底下。

輸出：`index.md`（TOC + 各章 token 估算）+ `metadata.json` + `NN-<chapter>.md` 檔案群。

### E. Distill（`book-distill`）

```
/tsundoku-book-distill
```

把 chunked Markdown 透過 **RIA-TV++** pipeline 蒸餾成 atomic skill set：

```
Stage 0: Adler 分析閱讀                 → BOOK_OVERVIEW.md
Stage 1: 5 個並行 sub-agent extractor   → frameworks / principles / cases /
                                            counter-examples / glossary
Stage 1.5: 三重驗證 filter              → 方法論密度高的書 ~30-50% 通過
Stage 2: 每個 skill 走 RIA++ render     → SKILL.md（R / I / A1 / A2 / E / B）
Stage 3: Zettelkasten linking          → INDEX.md + 交叉引用
Stage 4: 對抗式壓力測試                 → test-prompts.json（lure 必備）
```

輸出**會適配語言**：原書是日文，產出的 SKILL.md description 與 trigger signal 也會是日文，這樣 Claude 才能對上使用者實際 query 的語言。R 欄位的引用永遠保持原書 verbatim。

## Under the hood

4 個 skill 都是 shell + Python script 的薄層 wrapper。如果你想直接呼叫底層 script 不走 skill 也可以：

```bash
# 載入路徑環境變數（任一 skill 的 scripts/ 都可以 source）
source ~/.claude/plugins/cache/monkey-skills/tsundoku/0.11.0/skills/kobo-library/scripts/tsundoku_paths.sh

# Auth lifecycle
bash <skill-dir>/kobo-auth/scripts/kobo_install.sh           # 安裝 kobodl
bash <skill-dir>/kobo-auth/scripts/kobo_login.sh status      # 0=已認證 / 1=未認證 / 3=binary 未安裝
bash <skill-dir>/kobo-auth/scripts/kobo_login.sh import-from PATH

# Search 與 download
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"
python3 <skill-dir>/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "行為經濟,behavioral economics" --pub-after 2020 --status ReadyToRead \
    --format markdown
bash <skill-dir>/kobo-library/scripts/kobo_get.sh "$REVISION_ID"

# Extract
bash <skill-dir>/book-extract/scripts/install_pandoc.sh
python3 <skill-dir>/book-extract/scripts/epub_to_markdown.py \
    --epub "$EPUB" --strip-images --strip-frontmatter

# Distill bootstrap
bash <skill-dir>/book-distill/scripts/book_distill_init.sh <book-slug-id8>
```

這保持 skill 是可稽核的 — 凡是發生的事，讀 script 就能複現。

## Storage layout

單一 root，下面按 platform 分 subdir。未來的 `kindle-*` / `apple-books-*` 會在 `kobo/` 旁邊以同樣方式並列。

```
~/.tsundoku/                       ← TSUNDOKU_ROOT（default）
├── kobo/                            Kobo platform 狀態
│   ├── auth/                         chmod 700
│   │   └── kobodl.json               chmod 600（Kobo session credentials）
│   └── bin/kobodl-macos              ~14 MB upstream binary
├── tmp/                             共用 TMPDIR override（PYI-1270 修正）
└── cache/                           可重新產生、可整批 wipe
    ├── kobo/library.json             cached library export
    ├── markdown/<book>/...           EPUB → chunked Markdown（與 platform 無關）
    └── distilled/<book>/...          book-distill 輸出

~/Books/kobo/                       ← TSUNDOKU_DOWNLOADS（使用者可見的 EPUB）
├── <author> - <title> <id8>.epub
└── ...
```

`cache/` 子樹是可重新產生的（library 重新 export、EPUB 重新 extract）；`auth/`、`bin/`、`~/Books/kobo/` 不是。

## 環境變數

兩個由你設定的 decision-point 變數，五個由 script 推導的 derived path。在 source `tsundoku_paths.sh` 之前覆寫兩個 root 即可。

| 變數 | 必須 | Default | 說明 |
|---|---|---|---|
| `TSUNDOKU_ROOT` | No | `~/.tsundoku` | auth、binary、cache、tmp 的 root |
| `TSUNDOKU_DOWNLOADS` | No | `~/Books/kobo` | 使用者可見的 EPUB 下載位置 |
| `TSUNDOKU_TMPDIR` | derived | `$TSUNDOKU_ROOT/tmp` | TMPDIR override（PyInstaller PYI-1270 修正） |
| `TSUNDOKU_MARKDOWN_DIR` | derived | `$TSUNDOKU_ROOT/cache/markdown` | EPUB → Markdown 輸出 root |
| `TSUNDOKU_KOBO_CONFIG` | derived | `$TSUNDOKU_ROOT/kobo/auth/kobodl.json` | Kobo session credentials |
| `TSUNDOKU_KOBO_BINARY` | derived | `$TSUNDOKU_ROOT/kobo/bin/kobodl-macos` | kobodl CLI binary |
| `TSUNDOKU_KOBO_LIBRARY_JSON` | derived | `$TSUNDOKU_ROOT/cache/kobo/library.json` | `book list --export-library` 的 cache |

請不要直接設 derived 變數 — 改 `TSUNDOKU_ROOT` 才是正確做法。

## Repository 結構

```
tsundoku/
├── .claude-plugin/
│   └── plugin.json
├── commands/                          slash-command 介面
│   ├── tsundoku.md                     router
│   ├── kobo-auth.md
│   ├── kobo-library.md
│   ├── book-extract.md
│   └── book-distill.md
├── skills/
│   ├── kobo-auth/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── tsundoku_paths.sh       共用 path resolver（複本）
│   │       ├── kobo_install.sh         下載 kobodl binary
│   │       └── kobo_login.sh           subcommand router（status / add / remove / import-from / path）
│   ├── kobo-library/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── tsundoku_paths.sh       共用 path resolver（複本）
│   │       ├── kobo_query.py           library JSON 的 filter + format
│   │       └── kobo_get.sh             以 RevisionId 下載，冪等
│   ├── book-extract/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── install_pandoc.sh       brew → standalone fallback
│   │       ├── epub_to_markdown.py     NCX 驅動章節切分 + pandoc
│   │       └── cache_clear.sh          清除 markdown / library cache
│   └── book-distill/
│       ├── SKILL.md
│       ├── ATTRIBUTION.md              cangjie-skill / nuwa-skill / Adler / RIA / Munger
│       ├── methodology/                  各 stage 設計依據
│       │   ├── 00-overview.md
│       │   ├── 01-stage0-adler.md
│       │   ├── 02-stage1-parallel-extract.md
│       │   ├── 03-stage1.5-triple-verify.md
│       │   ├── 04-stage2-ria-plus.md
│       │   ├── 05-stage3-zettelkasten.md
│       │   └── 06-stage4-pressure-test.md
│       ├── extractors/                   5 個並行 sub-agent prompt
│       │   ├── framework-extractor.md
│       │   ├── principle-extractor.md
│       │   ├── case-extractor.md
│       │   ├── counter-example-extractor.md
│       │   └── glossary-extractor.md
│       ├── templates/
│       └── scripts/
│           └── book_distill_init.sh
├── README.md
├── README.ja.md
└── README.zh-TW.md
```

## 系統需求

| 項目 | 備註 |
|---|---|
| **macOS** 或 **Linux** | `kobo-*` skill 內附 macOS 用 kobodl binary；Linux 使用者請 `pipx install kobodl` 並覆寫 `TSUNDOKU_KOBO_BINARY`。`book-*` skill 與 platform 無關。 |
| **Python 3.9+** | 只用 stdlib，沒有額外套件需求 |
| 有購書的 **Kobo account** | `kobo-auth` / `kobo-library` 需要。Trial / KoboPlus 來的書也可。 |
| **pandoc** | 由 `book-extract/scripts/install_pandoc.sh` 自動安裝（先試 Homebrew，失敗 fallback 到 GitHub release 的 standalone binary） |
| **Calibre**（選用） | 只在使用 `kobo_get.sh --convert-pdf` 時才需要。如果你想連 PDF 一起產出，請另外安裝。 |

完整 end-to-end 流程需要 Claude Code CLI；Cowork tab 不能用 — 請見 [Cowork 相容性](#cowork-相容性)。

## Security

`kobodl.json` 等同你的 Kobo session token，**請當成密碼處理**。

| 控制 | 由誰強制 | 備註 |
|---|---|---|
| `~/.tsundoku/kobo/auth/` 設 `chmod 700` | 每次寫入時由 `kobo_login.sh` 強制 | 僅擁有者可進入 |
| `kobodl.json` 設 `chmod 600` | `add` 與 `import-from` 完成後 `kobo_login.sh` 強制 | 僅擁有者可讀寫 |
| `import-from` 覆寫前先備份 | `kobo_login.sh` | 留下 `kobodl.json.bak.<timestamp>` |
| Multi-user scope 限制 | 所有 command 都接受 `-u EMAIL` flag | 當 `kobodl.json` 內有多個 account 時 |

**不要** commit `kobodl.json`、不要貼到 chat、不要上傳到 cloud。如果不慎外洩或想輪換，請登入 Kobo 並到 <https://www.kobo.com/account/devices> 把對應的 device entry 撤銷 — 只刪本機檔案不會讓 upstream 的 token 失效。

## Notes

- **kobodl 的 bug**：`book wishlist` 在 kobodl 0.10.x 是壞的，本 plugin 不使用。Removed books（`IsRemoved=True`）下載常失敗，預設會從 query 結果排除。
- **Description 上限**：Kobo API 把 `Description` 截在 500 字、以 HTML 回傳。`kobo_query.py` 在比對與輸出時會 strip HTML。請把 description 視為 ONIX 的行銷文案，不是真正的 synopsis。
- **OS 支援**：實測過的 path 是 macOS。Linux 可用 `pipx install kobodl` 加上手動覆寫 `TSUNDOKU_KOBO_BINARY`。Windows 沒測過 — PR 歡迎。
- **Furigana**：pandoc 預設會把 `<rt>` 內容 drop 掉，所以 EPUB → Markdown 過程中日文振り仮名會遺失。如需保留請參考 [`waldeir/pandoc-filter-furigana`](https://github.com/waldeir/pandoc-filter-furigana)。

## Lineage

- `kobo-auth` + `kobo-library` 是從早期的 shell-script sync tool（`kobodl-library-sync.sh`、`~/KobodlLibrarySync/` 舊目錄）fork 出來的。`import-from` subcommand 就是為了讓舊 tool 使用者可以平順遷移。
- `book-distill` 是 [`kangarooking/cangjie-skill`（蒼頡-skill）](https://github.com/kangarooking/cangjie-skill)（MIT，2026）的 fork，做了完整的英譯、語言適配輸出、自動讀取 `book-extract` 輸出的 entry contract。其中 Triple Verification filter 本身又是從 [`alchaincyf/nuwa-skill`](https://github.com/alchaincyf/nuwa-skill) adapt 來的。完整 credit chain（Adler / Luhmann / 趙周 RIA / Forte / Munger）請見 [`skills/book-distill/ATTRIBUTION.md`](skills/book-distill/ATTRIBUTION.md)。
- `kobodl` 本身是 [`subdavis/kobo-book-downloader`](https://github.com/subdavis/kobo-book-downloader)。本 plugin 只是 orchestrate 它。

## Install

在 Claude Code CLI 內：

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install tsundoku
```

呼叫 router 確認可用：

```
/tsundoku
```

接著執行 `/tsundoku-kobo-auth` 完成 Kobo login。

## Contributing

- **問題回報**：請到 <https://github.com/kouko/monkey-skills/issues> 開 issue。
- **PR**：請以 `main` 為 target，使用 Conventional Commits。skill 內容更動（特別是 `book-distill` 的 methodology）請在 commit body 附上 primary source citation。
- **Cowork 相關問題**：請先讀 [Cowork 相容性](#cowork-相容性)；幾乎可以肯定是已被文件化的 sandbox 限制，不是 plugin 的 bug。

## License

MIT — 詳見 repository root 的 [LICENSE](../LICENSE)。

`book-distill` 另外保留 upstream cangjie-skill architecture 的 `Copyright (c) 2026 kangarooking`；請見 [`skills/book-distill/ATTRIBUTION.md`](skills/book-distill/ATTRIBUTION.md)。
