# tsundoku 積読

言語：[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 持っているのに読んでいない e-book の山を、agent skill として実行できる形に変える — login、search、download、extract、distill。

> ⚠️ **Claude Code CLI 専用**。Cowork sandbox は `kobo.com` への device-flow 認証と EPUB ダウンロードを遮断します。下記 [Cowork 互換性](#cowork-互換性) を参照。

**Version**: 0.11.0 ・ **License**: MIT ・ **Part of**: [monkey-skills](../README.md)

## Cowork 互換性

この plugin は **Claude Desktop の Cowork tab とは非互換** です。4 つの skill のうち 2 つ（`kobo-auth`、`kobo-library`）が `kobo.com` および kobodl の download CDN への外部通信を行いますが、これらは Cowork の URL allowlist の対象外です。残り 2 つの skill（`book-extract`、`book-distill`）はローカルファイルのみで動作するため Cowork でも単体では動きますが、pipeline は最初から最後まで通って初めて意味があります。

この plugin は **Claude Code CLI** から実行してください（Claude Desktop に埋め込まれた Code tab でも可）。同じ sandbox 制約は [`investing-toolkit`](../investing-toolkit/docs/mcp-setup.md) でも文書化されています。

## Background

積読（つんどく）は、買ったまま読まずに積み上がっていく本のことを指す日本語です。買うたびに「持っているのに取り出されていない知識」が増えていく。この plugin はその山を起点とし、すでに購入済みの e-book を必要なときに取り出して、agent が呼び出せる再利用可能な方法論へと変換します。

pipeline は 4 stage 構成。各段の境界はディスク上の安定した artifact になっていて、どの stage も独立に再実行できます：

```
kobo-auth ──▶ kobo-library ──▶ book-extract ──▶ book-distill
 (一度だけ)    (日常)             (本ごと)         (本ごと)

   login  ──▶  EPUB on disk ──▶ chunked .md  ──▶ atomic SKILL.md set
```

`kobo-*`（Kobo platform 固有）と `book-*`（フォーマット非依存）の分離は意図的です：将来 `kindle-*` や `apple-books-*` のような同階層の skill を追加する場合は `kobo-*` の隣に並びます。一方 `book-extract` / `book-distill` は出所を問わず、任意の EPUB / Markdown directory を受け付けます。

## Skills

| Skill | Layer | 役割 |
|---|---|---|
| [`tsundoku`](commands/tsundoku.md) | router | ユーザの意図（login / search / convert / distill）に応じて適切な skill へ振り分ける |
| [`kobo-auth`](skills/kobo-auth/SKILL.md) | source-platform（`kobo-*`） | 初回 setup、device-flow 認証、credential rotation、multi-account |
| [`kobo-library`](skills/kobo-library/SKILL.md) | source-platform（`kobo-*`） | Kobo library を title / author / series / publication date / category / description text / reading status / language で検索し、選択した本を DRM-free EPUB として download |
| [`book-extract`](skills/book-extract/SKILL.md) | format-agnostic（`book-*`） | NCX 駆動の章分割で EPUB を chapter ごとの Markdown に変換。CJK 安全 |
| [`book-distill`](skills/book-distill/SKILL.md) | format-agnostic（`book-*`） | RIA-TV++（Adler analytical read → 5 並列 extractor → triple verification → RIA++ render → Zettelkasten linking → adversarial pressure test）で Markdown を atomic SKILL.md set へ |

**命名規則**：`kobo-*` skill は Kobo platform に紐づきます（auth、library API、kobodl binary）。`book-*` skill は任意の EPUB / chunked Markdown で動作し、Kobo 依存はありません。つまり `book-extract` と `book-distill` は他経路（手動の EPUB drop、図書館の貸出、public domain）で入手した本にもそのまま使えます。

## Quick start

5 つの典型シナリオ。意図を自然言語で書けば router skill が振り分けます。

### A. Router — 「tsundoku を使いたい」

```
/tsundoku
```

4 stage の概要を提示し、どの段から始めるか確認します。初めて使う場合は B → C → D → E の順に進めてください。

### B. 初回 login（`kobo-auth`）

```
/tsundoku-kobo-auth
```

skill は kobodl binary を `~/.tsundoku/kobo/bin/` に install し、その後 **device-flow 認証をユーザのターミナルへ hand off** します。kobodl は 6 桁のコードを表示し、それを `https://www.kobo.com/activate` で入力する必要がありますが、Claude の Bash tool 経由で実行するとコードが buffer されて途中で truncate されてしまいます。Claude はユーザの「done」返信を待ち、その後 `kobo_login.sh status` で認証完了を確認します。

既存の `kobodl.json` を流用したい場合：

```
"~/KobodlLibrarySync/config/kobodl.json から既存の kobodl credentials を import して"
```

### C. Search と download（`kobo-library`）

```
/tsundoku-kobo-library
```

そのあと、欲しいものを自然言語で記述します。例：

```
「行動経済学について、ここ 5 年以内に出版された、まだ読んでいない本を探して」
「Silent Witch シリーズを全部見せて、まとめて download して」
「2 年以上前に買って手をつけていない本」
```

skill はその意図を `kobo_query.py` の filter（title / author / series / publisher / `--description` の title + description text 横断キーワード検索 / `--pub-after` / `--purchased-after` / `--status` / `--language` / ...）にマップし、結果を table / markdown card / summary で提示し、ユーザの確認後に `kobodl book get` で `~/Books/kobo/` へ download します。

### D. 変換（`book-extract`）

```
/tsundoku-book-extract
```

EPUB のパスを渡します（Kobo 由来である必要はありません）。skill は初回に pandoc を install、EPUB の NCX（目次）を parse して正準な章境界を取得、Kobo 固有の markup（`<span class="koboSpan">`）を pre-clean、章ごとに pandoc を実行し、`~/.tsundoku/cache/markdown/<title-slug>-<id8>/` 以下に章ごとの Markdown を書き出します。

出力：`index.md`（TOC + 章ごとの token 推定）+ `metadata.json` + `NN-<chapter>.md` ファイル群。

### E. Distill（`book-distill`）

```
/tsundoku-book-distill
```

chunked Markdown を **RIA-TV++** pipeline で atomic skill set に蒸留：

```
Stage 0: Adler analytical read           → BOOK_OVERVIEW.md
Stage 1: 5 並列 sub-agent extractor      → frameworks / principles / cases /
                                            counter-examples / glossary
Stage 1.5: Triple verification filter    → 方法論密度の高い本で ~30-50% pass
Stage 2: skill ごとの RIA++ render       → SKILL.md（R / I / A1 / A2 / E / B）
Stage 3: Zettelkasten linking            → INDEX.md + cross-refs
Stage 4: Adversarial pressure test       → test-prompts.json（lure 必須）
```

出力は **言語適応**：原書が日本語なら、生成される SKILL.md の description と trigger signal も日本語になり、ユーザの自然な query で activation するようになります。R フィールドの引用は常に原書言語の verbatim です。

## Under the hood

4 つの skill はすべて shell + Python script の薄いラッパーです。skill 経由でなく直接呼び出すこともできます：

```bash
# path 環境変数を読み込む（任意の skill の scripts/ から source 可能）
source ~/.claude/plugins/cache/monkey-skills/tsundoku/0.11.0/skills/kobo-library/scripts/tsundoku_paths.sh

# Auth lifecycle
bash <skill-dir>/kobo-auth/scripts/kobo_install.sh           # kobodl install
bash <skill-dir>/kobo-auth/scripts/kobo_login.sh status      # 0=認証済 / 1=未認証 / 3=binary 未 install
bash <skill-dir>/kobo-auth/scripts/kobo_login.sh import-from PATH

# Search と download
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"
python3 <skill-dir>/kobo-library/scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "行動経済,behavioral economics" --pub-after 2020 --status ReadyToRead \
    --format markdown
bash <skill-dir>/kobo-library/scripts/kobo_get.sh "$REVISION_ID"

# Extract
bash <skill-dir>/book-extract/scripts/install_pandoc.sh
python3 <skill-dir>/book-extract/scripts/epub_to_markdown.py \
    --epub "$EPUB" --strip-images --strip-frontmatter

# Distill bootstrap
bash <skill-dir>/book-distill/scripts/book_distill_init.sh <book-slug-id8>
```

これにより skill は監査可能なまま保たれます — script を読めば再現できないことは何も起こりません。

## Storage layout

単一 root の下に platform ごとの subdir。将来の `kindle-*` / `apple-books-*` も `kobo/` 階層をミラーする形で並びます。

```
~/.tsundoku/                       ← TSUNDOKU_ROOT（default）
├── kobo/                            Kobo platform state
│   ├── auth/                         chmod 700
│   │   └── kobodl.json               chmod 600（Kobo session credentials）
│   └── bin/kobodl-macos              ~14 MB upstream binary
├── tmp/                             共有 TMPDIR override（PYI-1270 対策）
└── cache/                           再生成可能、まとめて wipe 可
    ├── kobo/library.json             cached library export
    ├── markdown/<book>/...           EPUB → chunked Markdown（platform 非依存）
    └── distilled/<book>/...          book-distill 出力

~/Books/kobo/                       ← TSUNDOKU_DOWNLOADS（user 可視 EPUB）
├── <author> - <title> <id8>.epub
└── ...
```

`cache/` 配下は再生成可能です（library を再 export、EPUB を再 extract できる）。`auth/`、`bin/`、`~/Books/kobo/` は再生成できません。

## 環境変数

ユーザが設定する 2 つの decision-point 変数と、script が計算する 5 つの derived path。`tsundoku_paths.sh` を source する前に root 2 つを上書きしてください。

| 変数 | 必須 | Default | 説明 |
|---|---|---|---|
| `TSUNDOKU_ROOT` | No | `~/.tsundoku` | auth、binary、cache、tmp の root |
| `TSUNDOKU_DOWNLOADS` | No | `~/Books/kobo` | user 可視の EPUB download 先 |
| `TSUNDOKU_TMPDIR` | derived | `$TSUNDOKU_ROOT/tmp` | TMPDIR override（PyInstaller PYI-1270 対策） |
| `TSUNDOKU_MARKDOWN_DIR` | derived | `$TSUNDOKU_ROOT/cache/markdown` | EPUB → Markdown 出力 root |
| `TSUNDOKU_KOBO_CONFIG` | derived | `$TSUNDOKU_ROOT/kobo/auth/kobodl.json` | Kobo session credentials |
| `TSUNDOKU_KOBO_BINARY` | derived | `$TSUNDOKU_ROOT/kobo/bin/kobodl-macos` | kobodl CLI binary |
| `TSUNDOKU_KOBO_LIBRARY_JSON` | derived | `$TSUNDOKU_ROOT/cache/kobo/library.json` | `book list --export-library` の cache |

derived 変数を直接設定しないでください — `TSUNDOKU_ROOT` を上書きする方が正しい方法です。

## Repository 構成

```
tsundoku/
├── .claude-plugin/
│   └── plugin.json
├── commands/                          slash-command surface
│   ├── tsundoku.md                     router
│   ├── kobo-auth.md
│   ├── kobo-library.md
│   ├── book-extract.md
│   └── book-distill.md
├── skills/
│   ├── kobo-auth/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── tsundoku_paths.sh       共有 path resolver（コピー）
│   │       ├── kobo_install.sh         kobodl binary を download
│   │       └── kobo_login.sh           subcommand router（status / add / remove / import-from / path）
│   ├── kobo-library/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── tsundoku_paths.sh       共有 path resolver（コピー）
│   │       ├── kobo_query.py           library JSON の filter + format
│   │       └── kobo_get.sh             RevisionId 指定の冪等 download
│   ├── book-extract/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── install_pandoc.sh       brew → standalone fallback
│   │       ├── epub_to_markdown.py     NCX 駆動の章分割 + pandoc
│   │       └── cache_clear.sh          markdown / library cache の wipe
│   └── book-distill/
│       ├── SKILL.md
│       ├── ATTRIBUTION.md              cangjie-skill / nuwa-skill / Adler / RIA / Munger
│       ├── methodology/                  stage ごとの設計根拠
│       │   ├── 00-overview.md
│       │   ├── 01-stage0-adler.md
│       │   ├── 02-stage1-parallel-extract.md
│       │   ├── 03-stage1.5-triple-verify.md
│       │   ├── 04-stage2-ria-plus.md
│       │   ├── 05-stage3-zettelkasten.md
│       │   └── 06-stage4-pressure-test.md
│       ├── extractors/                   5 並列 sub-agent prompt
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

## 動作要件

| 要件 | 備考 |
|---|---|
| **macOS** または **Linux** | `kobo-*` skill は macOS 用 kobodl binary を同梱。Linux ユーザは `pipx install kobodl` のうえ `TSUNDOKU_KOBO_BINARY` を上書きしてください。`book-*` skill は platform 非依存。 |
| **Python 3.9+** | stdlib のみ。追加 package 不要 |
| 購入本のある **Kobo account** | `kobo-auth` / `kobo-library` で必須。Trial / KoboPlus 由来の本も動作可。 |
| **pandoc** | `book-extract/scripts/install_pandoc.sh` が自動 install（Homebrew が優先、なければ GitHub release の standalone binary に fallback） |
| **Calibre**（任意） | `kobo_get.sh --convert-pdf` を使うときだけ必要。EPUB 以外に PDF も欲しい場合に別途 install。 |

end-to-end での利用には Claude Code CLI が必要です。Cowork tab では動作しません — [Cowork 互換性](#cowork-互換性) を参照。

## Security

`kobodl.json` は Kobo の session token を保持します。**パスワードと同じ扱いを。**

| 制御 | 強制元 | 備考 |
|---|---|---|
| `~/.tsundoku/kobo/auth/` の `chmod 700` | 書き込みのたびに `kobo_login.sh` が enforce | 所有者のみアクセス可 |
| `kobodl.json` の `chmod 600` | `add` および `import-from` の後に `kobo_login.sh` が enforce | 所有者の read/write のみ |
| `import-from` 時の上書き前 backup | `kobo_login.sh` | `kobodl.json.bak.<timestamp>` を残す |
| Multi-user の scope 制限 | 全 command で `-u EMAIL` flag | `kobodl.json` に複数 account がある場合 |

`kobodl.json` を **commit しない、chat に貼らない、cloud に upload しない** — もし漏洩した場合や rotate したい場合は、Kobo に sign in して <https://www.kobo.com/account/devices> から該当 device entry を revoke してください。ローカル file の削除だけでは upstream の token は無効化されません。

## Notes

- **kobodl の bug**：`book wishlist` は kobodl 0.10.x で壊れているため使用していません。Removed books（`IsRemoved=True`）は download に失敗することが多く、query 結果からは default で除外されます。
- **Description の上限**：Kobo の API は `Description` を 500 文字で truncate し HTML として返します。`kobo_query.py` は match 用と出力用に HTML を strip します。description は ONIX の宣伝文句であって synopsis ではないと考えてください。
- **OS support**：tested path は macOS。Linux は `pipx install kobodl` + `TSUNDOKU_KOBO_BINARY` の手動上書きで動作します。Windows は未検証 — PR 歓迎。
- **Furigana**：pandoc は default で `<rt>` 内容を drop するため、EPUB → Markdown 変換時に振り仮名が失われます。保持したい場合は [`waldeir/pandoc-filter-furigana`](https://github.com/waldeir/pandoc-filter-furigana) を参照。

## Lineage

- `kobo-auth` + `kobo-library` は旧 shell-script sync tool（`kobodl-library-sync.sh`、レガシーな `~/KobodlLibrarySync/` directory）を fork したものです。`import-from` subcommand は旧 tool からの移行を想定して用意されています。
- `book-distill` は [`kangarooking/cangjie-skill`（蒼頡-skill）](https://github.com/kangarooking/cangjie-skill)（MIT、2026）の fork で、英語への完全翻訳・言語適応出力・`book-extract` 出力からの自動 entry contract を加えています。Triple Verification filter 自体は [`alchaincyf/nuwa-skill`](https://github.com/alchaincyf/nuwa-skill) からの adaptation です。完全な credit chain（Adler / Luhmann / 趙周 RIA / Forte / Munger）は [`skills/book-distill/ATTRIBUTION.md`](skills/book-distill/ATTRIBUTION.md) を参照。
- `kobodl` 自体は [`subdavis/kobo-book-downloader`](https://github.com/subdavis/kobo-book-downloader)。本 plugin はそれを orchestrate しているだけです。

## Install

Claude Code CLI 内で：

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install tsundoku
```

router を起動して動作確認：

```
/tsundoku
```

そのあと `/tsundoku-kobo-auth` で Kobo login を済ませてください。

## Contributing

- **質問 / bug 報告**：<https://github.com/kouko/monkey-skills/issues> に issue を立ててください。
- **PR**：`main` をターゲットに。Conventional Commits 必須。skill 内容の変更（特に `book-distill` の methodology 変更）は commit body に primary source citation を入れてください。
- **Cowork 関連の問題**：まず [Cowork 互換性](#cowork-互換性) のセクションを読んでください。ほぼ確実に文書化済みの sandbox 制約であって、plugin の bug ではありません。

## License

MIT — 詳細は repository root の [LICENSE](../LICENSE) を参照。

`book-distill` は upstream の cangjie-skill architecture について `Copyright (c) 2026 kangarooking` も保持します。[`skills/book-distill/ATTRIBUTION.md`](skills/book-distill/ATTRIBUTION.md) を参照。
