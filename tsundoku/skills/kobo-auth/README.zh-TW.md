# kobo-auth

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Kobo 的認證生命週期。負責 credential 檔與 binary。

屬於 [tsundoku](../..) plugin。Claude 真正載入的 skill 是
[`SKILL.md`](SKILL.md)；本 README 給人類瀏覽資料夾用。

## 何時使用此 skill

| 觸發情境 | 動作 |
|---|---|
| 第一次使用 tsundoku | Flow A（互動式 activation） |
| `kobo-library` 回報需要 auth | Flow A |
| 切換到不同的 Kobo 帳號 | Flow A 或 D |
| 已有先前安裝留下的 credentials | Flow B（import） |

Login 是「每帳號一次」的事件。完成後，[`kobo-library`](../kobo-library) 接手
日常的搜尋／下載。

## Quick start

```bash
# 安裝 kobodl binary（約 14 MB，idempotent）
bash scripts/kobo_install.sh

# 互動式 activation
bash scripts/kobo_login.sh add
# → kobodl 會印出「Open kobo.com/activate and enter XXXXXX」
# → 使用者開瀏覽器、登入、輸入 code

# 驗證
bash scripts/kobo_login.sh status
```

對於先前的安裝（舊版 `~/KobodlLibrarySync/` shell script，或 upstream 的
`~/.config/kobodl/`）：

```bash
bash scripts/kobo_install.sh
bash scripts/kobo_login.sh import-from ~/KobodlLibrarySync/config/kobodl.json
```

## 落地的檔案

成功 login 之後：

```
~/.tsundoku/kobo/
├── auth/                              chmod 700
│   └── kobodl.json                    chmod 600  ← Kobo session credentials
└── bin/kobodl-macos                   約 14 MB upstream binary
```

`kobodl.json` **等同於你的 Kobo 密碼**。絕不 commit、貼上、或上傳。

## 此資料夾的檔案

| Path | 角色 |
|---|---|
| [`SKILL.md`](SKILL.md) | Claude 載入的 skill spec。200+ 行，涵蓋全部 flow。 |
| [`scripts/kobo_install.sh`](scripts/kobo_install.sh) | Binary 下載（idempotent） |
| [`scripts/kobo_login.sh`](scripts/kobo_login.sh) | 子指令：`status` / `add` / `remove` / `import-from` / `path` |

路徑解析器 `tsundoku_paths.sh` 位於 plugin root
（[`tsundoku/lib/`](../../lib)），每個 script 都會 source 它。

## 另見

- [`tsundoku` README](../..) — 整體 plugin 導覽
- [`kobo-library`](../kobo-library) — 此 skill 的 auth 由它消費
