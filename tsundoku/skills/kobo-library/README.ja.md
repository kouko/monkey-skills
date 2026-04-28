# kobo-library

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 10 軸以上の filter で Kobo 電子書 library を検索し、ヒットした本を
> カード表示、選んだ本を DRM-free EPUB としてダウンロードする。

[tsundoku](../..) plugin の一部。Claude が load する skill spec は
[`SKILL.md`](SKILL.md)。この README は人間向け。

## 何をする

ユーザー視点のフロー：

```
「直近 5 年で出た behavioral economics の本で、まだ読んでないやつ探して」
                              ↓
                kobo_query.py がローカル library JSON を絞り込み
                              ↓
                カード（markdown / table / summary / ids）
                              ↓
                「OK、#2 と #5 ダウンロードして」
                              ↓
                kobo_get.sh が選ばれた RevisionId をダウンロード
                              ↓
                ~/Books/kobo/ に DRM-free .epub
```

## 前提条件

[`kobo-auth`](../kobo-auth) が成功している必要がある。
`bash ../kobo-auth/scripts/kobo_login.sh status` が 0 を返さない場合は
先にそちらを実行する。

## Quick start

```bash
# パスを load（TSUNDOKU_KOBO_BINARY / _CONFIG / _LIBRARY_JSON 等を得る）
source scripts/tsundoku_paths.sh
mkdir -p "$TSUNDOKU_DOWNLOADS"

# library index を再構築（Kobo の metadata をローカル JSON に export）
"$TSUNDOKU_KOBO_BINARY" --config "$TSUNDOKU_KOBO_CONFIG" \
    book list --export-library "$TSUNDOKU_KOBO_LIBRARY_JSON"

# 検索 — カードでプレビュー
python3 scripts/kobo_query.py \
    --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --description "行為經濟,Behavioral" \
    --pub-after 2020 --status ReadyToRead \
    --format markdown

# 選んだ RevisionId をダウンロード
bash scripts/kobo_get.sh "$REVISION_ID"

# あるいは pipe で一括
python3 scripts/kobo_query.py --library "$TSUNDOKU_KOBO_LIBRARY_JSON" \
    --series "Silent Witch" --format ids \
  | bash scripts/kobo_get.sh
```

## `kobo_query.py` の filter

| Filter | 効果 |
|---|---|
| `--title PATTERN` | Title の substring マッチ |
| `--author PATTERN` | 任意の contributor に対する substring マッチ |
| `--series PATTERN` | series 名 substring マッチ |
| `--description PATTERN` | クリーン化済み description の全文（カンマ = OR） |
| `--description-all PATTERN` | カンマ区切りキーワード、全て match 必要 |
| `--status` | `Finished` / `Reading` / `ReadyToRead` |
| `--language CODE` | `zh` / `ja` / `en` ... |
| `--country CODE` | `tw` / `jp` / `us` ... |
| `--publisher PATTERN` | publisher 名 substring |
| `--isbn ISBN` | 完全一致 ISBN |
| `--pub-after YYYY[-MM[-DD]]` | 出版日 >= |
| `--pub-before YYYY[-MM[-DD]]` | 出版日 <= |
| `--genre UUID` / `--category UUID` | UUID 一致（上級者向け） |
| `--min-progress N` / `--max-progress N` | 読書進捗 0-100 |

出力形式：`table` / `json` / `ids` / `markdown` / `summary`。
全 filter は AND で結合。

## このフォルダのファイル

| Path | 役割 |
|---|---|
| [`SKILL.md`](SKILL.md) | Claude が load する skill spec（完全な filter / 出力 reference） |
| [`scripts/kobo_query.py`](scripts/kobo_query.py) | library JSON を絞り込み、5 形式で出力。純 stdlib |
| [`scripts/kobo_get.sh`](scripts/kobo_get.sh) | RevisionId 指定でダウンロード（args または stdin pipe）、idempotent skip |

## 出力先

```
~/Books/kobo/
└── <author> - <title> <id8>.epub      ← ユーザー可視、DRM-free
```

EPUB は最初から DRM-free（kobodl がダウンロード時に復号する）。

## 関連

- [`kobo-auth`](../kobo-auth) — まず login
- [`book-extract`](../book-extract) — 自然な次の段階：EPUB を LLM が
  取り込める章分割 Markdown に変換
- [`tsundoku` README](../..) — pipeline 全体像
