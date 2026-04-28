# korea-macro/docs

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

`korea-macro` を保守するための開発者向け文書とツール。

## 内容

### Catalog

- **`bok-ecos-keystat-catalog.md`** — `FinanceDataReader` を介して API key なしでアクセスできる BOK ECOS KEYSTAT 全 98 コードの人間可読 catalog。カテゴリ（monetary、rates、markets、FX、activity、CI、labor、BoP、prices、demographics）ごとにグループ化。
- **`bok-ecos-keystat.json`** — `probe-keystat.py` の生 JSON 出力。BOK が KEYSTAT を更新した後に再インポート / diff 可能。

### Tools

- **`tools/probe-keystat.py`** — KEYSTAT catalog を再 probe（既定では `K001-K500` をスイープ）。BOK が key 指標を追加したときに再実行。

## メンテナンス

BOK が KEYSTAT を更新したとき（稀、年 1-2 回）、probe を再実行し、出力をコミット済みの JSON と diff します：

```bash
cd investing-toolkit/skills/korea-macro/docs/tools
uv run probe-keystat.py
diff <(jq --sort-keys . ../bok-ecos-keystat.json) <(jq --sort-keys . ../bok-ecos-keystat.json.new)
```

追加項目があれば、新しい行を `bok-ecos-keystat-catalog.md` に反映し、preset 化するかどうかを判断してください（v1.8.0 以降の 10-group 構造は `SKILL.md` を参照）。

## 完全 ECOS vs KEYSTAT

本文書は **KEYSTAT のみ**（BOK が精選した 100대 통계지표 サブセット、約 98 コード）を扱います。完全な BOK ECOS catalog（10,000+ series）は API key が必要です。詳細は `bok-ecos-keystat-catalog.md` 下部の「Why not the full ECOS catalog?」セクションを参照。
