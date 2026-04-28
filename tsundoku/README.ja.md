# tsundoku 積読

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**Version**: 0.11.0
**Part of**: [monkey-skills](../)

> *tsundoku（積読）* — 買ったまま読んでいない本の山を指す日本語。
> この plugin はその山を実行可能な知識へと変える。

Kobo 電子書 library を **title / author / series / 出版日 / category /
description 全文 / 閲読状態 / 言語** で検索し、ヒットした本をカード表示。
選んだ本を DRM-free EPUB としてダウンロードし、章ごとに分割した Markdown
へ変換、さらに RIA-TV++ pipeline により **本を atomic な agent skill へ蒸留**
する（Adler analytical read → 5 つの parallel extractor → triple verification →
RIA++ render → Zettelkasten linking → adversarial pressure test）。出力言語は
自動適応（EN / 日本語 / 繁體中文）。内部では [`subdavis/kobo-book-downloader`][kobodl]
をラップし、EPUB→Markdown 段階で [pandoc][pandoc] を使う。蒸留方法論は
[`kangarooking/cangjie-skill`][cangjie]（MIT）から派生。

[kobodl]: https://github.com/subdavis/kobo-book-downloader
[pandoc]: https://pandoc.org
[cangjie]: https://github.com/kangarooking/cangjie-skill

## Skills

| Skill | Slash command | 使うタイミング |
|---|---|---|
| [`kobo-auth`](skills/kobo-auth/SKILL.md) | `/kobo-auth` | 初回セットアップ、ログイン、アカウント移行、credential のローテーション |
| [`kobo-library`](skills/kobo-library/SKILL.md) | `/kobo-library` | 日常利用 — 検索、一覧、EPUB の一括ダウンロード |
| [`book-extract`](skills/book-extract/SKILL.md) | `/book-extract` | EPUB → 章ごとに分割した Markdown |
| [`book-distill`](skills/book-distill/SKILL.md) | `/book-distill` | Markdown → atomic な agent skill（RIA-TV++ 経由） |
| (router) | `/tsundoku` | 意図に応じて自動 route。曖昧なら「どの段階か」を質問 |

命名規則：
- **`kobo-*`** — 入手元プラットフォーム層（auth + library）：Kobo / kobodl に
  紐づく。将来の `kindle-*` / `apple-books-*` 兄弟 skill も同じ構造に従う。
- **`book-*`** — 形式に依存しない処理層（extract + distill）：入手元を問わず
  任意の EPUB / 任意の章分割 Markdown に対して動作する。将来の `paper-distill`
  （学術論文）や `transcript-distill`（podcast 書き起こし）はここに加わる。

## Quick Start

すべての flow は Claude Code 上で slash command を呼び出すところから
始まる。skill が binary install、対話プロンプト、credentials 保存、
pipeline orchestration をすべて引き受けるので、shell script を直接
実行する必要はない。

### A. ゼロからの初期設定（初回ログイン）

```
/kobo-auth
```

または自然言語で：「Kobo のログインを設定して」。

skill が kobodl binary をインストールし、device-flow activation
（`kobo.com/activate` を開いて 6 桁 code を入力）を案内し、
credentials を `chmod 600` で `~/.tsundoku/kobo/auth/` に保存する。

### B. 既存の kobodl インストールから移行

```
/kobo-auth
```

その上で：「`~/KobodlLibrarySync/config/kobodl.json` に既存の
`kobodl.json` があるので import してほしい」と伝える。skill は
既存 credentials を import し、activation flow をスキップする。

### C. 検索とダウンロード

```
/kobo-library
```

または：「Kobo 書庫から behavioral economics に言及していて、2020 年以降に出版された未読本を検索」。

skill は library index を refresh、multi-criteria filter を実行、
ヒットをリッチカードで preview、選択した本を DRM-free EPUB として
`~/Books/kobo/` にダウンロードする。idempotent — disk 上にすでに
ある本は自動でスキップされる。

### D. EPUB → 章ごとに分割した Markdown

```
/book-extract
```

または：「この EPUB を章ごとに分割した Markdown に変換」。

skill は pandoc が無ければ自動 install、EPUB の NCX table-of-contents
で章を分割、画像と frontmatter を除去し、
`~/.tsundoku/cache/markdown/<title-slug>-<id8>/` に書き出す。

### E. Markdown → 原子化された agent skill 群

```
/book-distill
```

または：「この本を再利用可能な agent skill へ蒸留して」。

skill は作業ディレクトリを bootstrap し、6 段階の RIA-TV++ pipeline
を実行する：

| Stage | 動作 | 出力 |
|---|---|---|
| 0 | Adler analytical read | `BOOK_OVERVIEW.md` |
| 1 | 5 つの parallel extractor | `candidates/` |
| 1.5 | Triple verification | `verified.md`（30-50% が通過） |
| 2 | RIA++ skill render | `<skill-slug>/SKILL.md` |
| 3 | Zettelkasten linking | `INDEX.md` |
| 4 | Adversarial pressure test | `test-prompts.json` |

本文は原典の言語に合わせる。YAML metadata と slug は英語。

### どこから始めるか分からないとき

```
/tsundoku
```

router skill — 意図を述べれば対応する sub-skill に dispatch する。
曖昧な要求には「どの段階か」を聞き返す。

## Under the Hood（script を直接呼ぶ）

上の slash command が推奨インターフェース。debug、CI scripting、
power-user 用途では各 skill の下層 script を直接呼べる。skill は
これらに委譲しているだけ：

### Auth (kobo-auth)

```bash
# binary install + device-flow activation
bash tsundoku/skills/kobo-auth/scripts/kobo_install.sh
bash tsundoku/skills/kobo-auth/scripts/kobo_login.sh add

# あるいは既存 credentials を import
bash tsundoku/skills/kobo-auth/scripts/kobo_login.sh \
    import-from ~/KobodlLibrarySync/config/kobodl.json
```

### Library (kobo-library)

```bash
source tsundoku/skills/kobo-library/scripts/tsundoku_paths.sh
export TMPDIR="$TSUNDOKU_TMPDIR"
mkdir -p "$TSUNDOKU_DOWNLOADS"

# library index を refresh
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"

# 検索（出力 5 形式：markdown / json / table / ids / paths）
python3 tsundoku/skills/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "behavioral,economics,行為經濟" \
    --pub-after 2020 --status ReadyToRead --format markdown

# RevisionId 指定でダウンロード（idempotent）
bash tsundoku/skills/kobo-library/scripts/kobo_get.sh "$REVISION_ID"

# 絞り込み結果を pipe で渡す
python3 tsundoku/skills/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" --series "Silent Witch" --format ids \
  | bash tsundoku/skills/kobo-library/scripts/kobo_get.sh --convert-pdf
```

### Extract (book-extract)

```bash
# 一回だけ：pandoc を確認
bash tsundoku/skills/book-extract/scripts/install_pandoc.sh

# 変換（既定で $TSUNDOKU_MARKDOWN_DIR を使う）
python3 tsundoku/skills/book-extract/scripts/epub_to_markdown.py \
    --epub "$EPUB_PATH" --strip-images --strip-frontmatter

# 完了後 cache をクリア
bash tsundoku/skills/book-extract/scripts/cache_clear.sh
```

### Distill (book-distill)

```bash
# 抽出済み markdown から作業ディレクトリを bootstrap
bash tsundoku/skills/book-distill/scripts/book_distill_init.sh \
    一九八四-b9152ffe
# Claude が book-distill/SKILL.md を読み、6 段階 pipeline を実行
```

## ストレージ配置（単一 root、プラットフォームごとのサブディレクトリ）

```
~/.tsundoku/                  ← TSUNDOKU_ROOT
├── kobo/                       Kobo プラットフォーム状態
│   ├── auth/                    chmod 700
│   │   └── kobodl.json          chmod 600（Kobo session credentials）
│   └── bin/kobodl-macos         14 MB upstream binary
├── tmp/                        共用 TMPDIR override（PYI-1270 修正）
└── cache/                      再生成可能、まとめて消去できる
    ├── kobo/library.json        cached library export
    └── markdown/<book>/...      EPUB → MD（プラットフォーム非依存）

~/Books/kobo/                 ← TSUNDOKU_DOWNLOADS（ユーザー可視 EPUB）
```

将来 `kindle-*` / `apple-books-*` skill が登場したら、`~/.tsundoku/kindle/`、
`~/.tsundoku/cache/kindle/` といった配置で同じ構造を踏襲する。

**判断ポイントとなる env 変数 2 つ** — 場所を変えたいときに設定：

| Var | 既定値 | 用途 |
|---|---|---|
| `TSUNDOKU_ROOT` | `~/.tsundoku` | toolkit の状態すべて（auth + binary + cache） |
| `TSUNDOKU_DOWNLOADS` | `~/Books/kobo` | ユーザー可視 EPUB のダウンロード先 |

**派生する 5 つの path** は上の 2 つから計算される（直接設定しない）：

| Var | スコープ |
|---|---|
| `TSUNDOKU_TMPDIR` | 共用 |
| `TSUNDOKU_MARKDOWN_DIR` | 共用（cache/markdown） |
| `TSUNDOKU_KOBO_CONFIG` | Kobo: kobodl.json |
| `TSUNDOKU_KOBO_BINARY` | Kobo: kobodl-macos |
| `TSUNDOKU_KOBO_LIBRARY_JSON` | Kobo: library export |

いずれの skill の `scripts/tsundoku_paths.sh` を source しても全部 export される。

`kobo/auth/` サブディレクトリは `chmod 700`、`kobodl.json` は `chmod 600`。
`cache/` ツリーは再生成可能 — `book-extract/scripts/cache_clear.sh` でいつでも
消去できる。

## リポジトリ構成

```
tsundoku/
├── .claude-plugin/plugin.json
├── README.md
├── commands/                    # slash command（skill と 1:1 + router 1 つ）
│   ├── tsundoku.md              #   /tsundoku（router）
│   ├── kobo-auth.md             #   /kobo-auth
│   ├── kobo-library.md          #   /kobo-library
│   ├── book-extract.md          #   /book-extract
│   └── book-distill.md          #   /book-distill
└── skills/
    ├── kobo-auth/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobo_install.sh    # binary ダウンロード（idempotent）
    │       └── kobo_login.sh      # add / status / remove / import-from / path
    ├── kobo-library/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── kobo_query.py      # --export-library JSON を絞り込み、5 形式
    │       └── kobo_get.sh        # RevisionId 指定でダウンロード（引数 or stdin）
    ├── book-extract/
    │   ├── SKILL.md
    │   └── scripts/
    │       ├── install_pandoc.sh     # brew → standalone fallback
    │       ├── epub_to_markdown.py   # NCX 駆動の章分割 + pandoc + 整形
    │       └── cache_clear.sh   # 抽出 markdown / library cache を消去
    └── book-distill/                 # RIA-TV++ pipeline（cangjie-skill, MIT から fork）
        ├── SKILL.md                  # トップレベル orchestrator
        ├── ATTRIBUTION.md             # upstream credits + license
        ├── methodology/              # 7 ファイル：00-overview + 01-06 stage 詳細
        ├── extractors/               # 5 つの parallel sub-agent prompt
        │   ├── framework-extractor.md
        │   ├── principle-extractor.md
        │   ├── case-extractor.md
        │   ├── counter-example-extractor.md
        │   └── glossary-extractor.md
        ├── templates/                # BOOK_OVERVIEW / SKILL / INDEX / test-prompts
        └── scripts/
            └── book_distill_init.sh  # book-extract の出力から distill ディレクトリを起動
```

## 必要環境

- macOS または Linux（kobodl は macOS binary が同梱され自動インストール。
  Linux ユーザーは `pipx install kobodl` で入れて `TSUNDOKU_KOBO_BINARY` を
  上書き）
- Python 3.9+（query / extract scripts は stdlib のみ使用）
- 購入済みの本が 1 冊以上ある Kobo アカウント
- 任意：pandoc（`book-extract` 用 — brew あるいは GitHub release standalone から
  自動インストール。導入済みなら no-op）
- 任意：[Calibre][calibre]（EPUB → PDF 変換用）

[calibre]: https://calibre-ebook.com/download_osx

## セキュリティ

- `kobodl.json` には **Kobo session credentials** が入っている — パスワードと同等。
  commit、チャットへの貼付、アップロードは絶対に行わない
- `kobo_login.sh` は当該ファイルを触る操作のたびに `chmod 600` を強制する
- session を失効させるには `kobodl.json` を消し、Kobo の
  [Authorized Devices](https://www.kobo.com/account/devices) ページにアクセスする
- 共用マシンでは macOS ユーザーアカウントを専用に分ける

## 注意点

- `book wishlist` サブコマンドは現状 upstream 側で壊れている（kobodl 0.10.x）。
  使えるのは `book list` のみ
- `Description` フィールドは Kobo の API により 500 文字に制限されている
  （出版社の ONIX copy であり synopsis ではない）
- macOS には事前ビルドの kobodl binary が自動でインストールされる。
  Linux/Windows ユーザーは `pipx install kobodl` で kobodl を入れ、
  `tsundoku_paths.sh` を source した後で `TSUNDOKU_KOBO_BINARY` を上書きする

## 系譜

[`kobodl-library-sync.sh`][ancestor] という単一ファイルの shell script を、
auth・runtime・extraction を分離した search-first の toolkit へ一般化したもの。
metadata の豊富な query、LLM 取り込み向けの章分割 Markdown、`~/.tsundoku/`
配下に統一された単一 root のストレージ配置を備える。

[ancestor]: https://github.com/kouko/kobodl-library-sync
