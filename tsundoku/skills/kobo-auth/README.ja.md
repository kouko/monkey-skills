# kobo-auth

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Kobo の認証ライフサイクル。credential ファイルと binary を所有する。

[tsundoku](../..) plugin の一部。Claude が実際に load する skill は
[`SKILL.md`](SKILL.md)。この README はフォルダを覗く人間向け。

## この skill を使うタイミング

| トリガ | 動作 |
|---|---|
| tsundoku を初めて使う | Flow A（対話的 activation） |
| `kobo-library` が auth 必須と通知 | Flow A |
| 別の Kobo アカウントへ切り替える | Flow A または D |
| 以前のインストールから引き継いだ credentials がある | Flow B（import） |

Login はアカウントごとに 1 回きりのイベント。それ以降は
[`kobo-library`](../kobo-library) が日常の検索 / ダウンロードを担当する。

## Quick start

```bash
# kobodl binary をインストール（約 14 MB、idempotent）
bash scripts/kobo_install.sh

# 対話的 activation
bash scripts/kobo_login.sh add
# → kobodl が "Open kobo.com/activate and enter XXXXXX" と表示
# → ユーザーがブラウザを開き、サインインし、code を入力

# 確認
bash scripts/kobo_login.sh status
```

以前のインストール（旧 `~/KobodlLibrarySync/` shell script や upstream の
`~/.config/kobodl/`）からの場合：

```bash
bash scripts/kobo_install.sh
bash scripts/kobo_login.sh import-from ~/KobodlLibrarySync/config/kobodl.json
```

## ディスクに残るもの

login 成功後：

```
~/.tsundoku/kobo/
├── auth/                              chmod 700
│   └── kobodl.json                    chmod 600  ← Kobo session credentials
└── bin/kobodl-macos                   約 14 MB の upstream binary
```

`kobodl.json` は **Kobo パスワード相当**。commit、貼付、アップロードは厳禁。

## このフォルダのファイル

| Path | 役割 |
|---|---|
| [`SKILL.md`](SKILL.md) | Claude が load する skill spec。200+ 行、全 flow を網羅。 |
| [`scripts/kobo_install.sh`](scripts/kobo_install.sh) | Binary ダウンロード（idempotent） |
| [`scripts/kobo_login.sh`](scripts/kobo_login.sh) | サブコマンド：`status` / `add` / `remove` / `import-from` / `path` |

path resolver の `tsundoku_paths.sh` は plugin root
（[`tsundoku/lib/`](../../lib)）に配置されており、各 script から source される。

## 関連

- [`tsundoku` README](../..) — plugin 全体のオリエンテーション
- [`kobo-library`](../kobo-library) — この skill の auth を消費する側
