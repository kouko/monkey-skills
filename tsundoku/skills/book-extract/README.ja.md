# book-extract

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> EPUB を章ごとに分割した Markdown へ変換し、LLM が取り込めるようにする。
> Format-agnostic — Kobo 由来でなくても、任意の EPUB に効く。

[tsundoku](../..) plugin の一部。Claude が load する skill spec は
[`SKILL.md`](SKILL.md)。この README は人間向け。

## なぜ独自 converter か（pandoc 単体ではダメか）

多くの EPUB は意味的な `<h1>` ではなく Kobo 固有の markup
（`<span class="koboSpan">`）で章を表す。pandoc を直接かけると **markdown
heading が一つも生まれない** ため、後段の chunk 分割が機能しなくなる。

この skill は EPUB の `toc.ncx`（または EPUB3 nav）を起点に章を分割する
ので、意味的な章マークアップを使わない本でも動作する。Kobo / 角川 /
時報 / O'Reilly の EPUB で end-to-end 検証済み。

## Pipeline

```
EPUB
  ↓
unzip + OPF/NCX をパース      ← 順序付き spine items（XHTML ファイル）
                              + NCX から対応付けた章ラベル
  ↓ spine item ごと
XHTML を pre-clean            ← kobo span / SVG / script / 空 div を除去
  ↓
pandoc で XHTML → GFM Markdown
  ↓
MD を post-clean              ← 行頭の全角インデント、hard-break `\` の
                              残骸、raw <img> タグを除去
  ↓
NN-<slugified-label>.md      ← H1 = NCX の章ラベル
+ index.md（TOC + token 概算）
+ metadata.json（title / authors / publisher / ISBN / chapters）
```

## Quick start

```bash
# 1 回だけ：pandoc が入っているか確認（brew → standalone fallback）
bash scripts/install_pandoc.sh

# パスを load
source scripts/tsundoku_paths.sh
EPUB=~/Books/kobo/"<author> - <title> b9152ffe.epub"

# 変換（既定で $TSUNDOKU_MARKDOWN_DIR を使う — --out-dir 不要）
python3 scripts/epub_to_markdown.py --epub "$EPUB" \
    --strip-frontmatter

# → ~/.tsundoku/cache/markdown/<title-slug>-<id8>/ に書き込み
#       index.md + metadata.json + NN-chapter.md + images/
#
# 純テキストのみ（LLM 蒸留用途）にしたい場合は --strip-images を追加
```

## 変換オプション

| Flag | 効果 |
|---|---|
| `--out-dir DIR` | 出力 ROOT（内部で本ごとのサブディレクトリを自動作成。既定 `$TSUNDOKU_MARKDOWN_DIR`） |
| `--no-subdir` | 本ごとのサブディレクトリを無効化、`--out-dir` 直下に書く |
| `--strip-images` | 画像の抽出をスキップし参照もすべて削除 — 純テキスト出力用 |
| `--strip-frontmatter` | 書封 / 目次 / 版権 / cover / contents 等をスキップ |
| `--strip-backmatter` | 索引 / 謝辞 / index / acknowledg をスキップ（附録 / 訳者あとがきは残す） |
| `--merge-small N` | N トークン未満の章を直前の章に併合 |
| `--pandoc PATH` | pandoc binary を上書き |
| `--quiet` | 章ごとの進捗表示を抑制 |

## 出力構造

```
~/.tsundoku/cache/markdown/<title-slug>-<id8>/
├── index.md                      ← TOC + 章ごとの token 概算
├── metadata.json                 ← title / authors / publisher / ISBN / chapters[]
├── images/                       ← デフォルトで抽出。`--strip-images` で無効化
│   └── cover.jpg, ch03-fig1.png, ...
├── 01-cover.md                   ← --strip-frontmatter 指定時はスキップ
├── 02-序.md
├── 03-chapter-01.md              ← H1 = NCX の章ラベル、`![](images/...)` 参照
├── 04-chapter-02.md
...
```

章ファイル名：`NN-<slugified-label>.md`（CJK は保持）。サブディレクトリ名は
`<slug-of-title>`、入力ファイル名が kobodl 命名 pattern にマッチすれば
`<slug-of-title>-<id8>`。章 Markdown 内の画像は inline GFM 構文
`![alt](images/<file>)` で参照されます。

## Token 予算の目安

| 本のサイズ | 合計 token（CJK 概算） | 戦略 |
|---|---|---|
| ≤80K | one-shot context | Claude 1 回の call で本全体 |
| 80-150K | chapter-by-chapter | ファイルごとに反復 |
| 150K+ | outline-first | まず要約、その後ピンポイントに再読 |

## Cache 管理

```bash
# 全消去（markdown + library.json）。auth と EPUB は保持
bash scripts/cache_clear.sh

# 1 冊分の markdown だけ消去
bash scripts/cache_clear.sh --book 一九八四-b9152ffe

# プレビュー
bash scripts/cache_clear.sh --dry-run

# library.json だけ消去（強制再 export）
bash scripts/cache_clear.sh --library-only
```

Auth（`~/.tsundoku/kobo/auth/`）、binary、ダウンロード済み EPUB は **決して**
触らない。

## このフォルダのファイル

| Path | 役割 |
|---|---|
| [`SKILL.md`](SKILL.md) | Claude が load する skill spec（完全な変換 + chunking の参照） |
| [`scripts/install_pandoc.sh`](scripts/install_pandoc.sh) | Brew → GitHub-release standalone fallback |
| [`scripts/epub_to_markdown.py`](scripts/epub_to_markdown.py) | NCX 駆動の章分割 + pandoc + 整形。約 620 行、stdlib のみ |
| [`scripts/cache_clear.sh`](scripts/cache_clear.sh) | 抽出 markdown / library cache を消去（4 モード） |

## 受け入れ可能な入手元

- ✅ Kobo 由来の EPUB（[`kobo-library`](../kobo-library) 経由）
- ✅ Project Gutenberg
- ✅ BookWalker / 角川 / 講談社 のダウンロード書き出し
- ✅ Apple Books 書き出し
- ✅ 手作業で用意した EPUB
- ⚠️ NCX も EPUB3 nav も無い EPUB は、ファイル名 stem を章名として fallback
- ❌ PDF（別形式。`pdf-extract` skill が別途必要）

## 関連

- [`book-distill`](../book-distill) — 自然な次の段階：分割済み Markdown を
  まとまった agent skill 群に変える
- [`tsundoku` README](../..) — pipeline 全体像
