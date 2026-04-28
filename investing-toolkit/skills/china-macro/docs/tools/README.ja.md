# china-macro / docs / tools

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

`docs/` 配下の NBS 指標 catalog を取得するための one-shot admin scripts。runtime skill の一部では**なく**、NBS が新たな基準期間セグメントを公表したとき（約 5 年に一度）や `queryIndicatorsByCid` の response schema が変わったときにのみ実行します。

## Scripts

| Script | 用途 | 標準的な実行時間 |
|---|---|---|
| `probe-nbs-tree.py` | 3 つの頻度すべてに対して `queryIndexTreeAsync` を再帰的に走査し、`nbs-tree-{monthly,quarterly,yearly}.md`（folder+leaf の UUID catalog）を生成 | ~15-20 分 |
| `probe-nbs-indicators.py` | 3 つのツリーの各 leaf cid に対して `queryIndicatorsByCid` を呼び出し、cid 別の JSON を cache に格納、集約結果として `nbs-indicators-{frequency}.{json,md}` を出力 | ~60-90 分 |
| `tree-to-markdown-tables.py` | ネスト箇条書き形式のツリー出力をカテゴリ別セクション化された表へ変換（フォーマット移行で一度だけ使用） | 数秒 |

## 再実行のタイミング

### 約 5 年に一度（基準期間改定）
NBS は方法論改定を 5 年周期で公表します。2031 年には現行の `(2026-)` CPI/PPI series がほぼ確実に `(2026-2030)` で凍結され、新たな UUID を持つ `(2031-)` series が登場します。`probe-nbs-tree.py` と `probe-nbs-indicators.py` の両方を再実行して新しい leaves を取り込んでください。

### 上流側の変更が確認されたとき
skill 利用者から `nbs_client.py` が古い／空のデータを返すと報告された場合、まず `queryIndicatorsByCid` の呼び出しを 1 回手動で検証します。schema が漂移していたら probe scripts を再実行してください。

### アドホック：新たな preset を追加するとき
既存の `docs/nbs-indicators-*.md` に対して欲しい概念で grep するだけで十分です — 指標 UUID は既に取得済みです。NBS にとって本当に新しい指標でない限り、再実行は不要です。

## 前提条件

- Python 3.9+（stdlib のみ — 外部依存なし）
- `data.stats.gov.cn` への HTTPS アウトバウンド
- **NordVPN 等**：台湾 / Anthropic インフラから VPN 経由で到達可能であることを検証済み。WAF は大量走査で発動しますが、scripts が指数バックオフ + session ローテーションを処理します。

## 使い方

```bash
# Tree 構造（folder/leaf 階層 + catalog ID を取得）
python3 probe-nbs-tree.py
# → /tmp/nbs-tree-{monthly,quarterly,yearly}.txt に書き出し
# → 手動でコピーし、tree-to-markdown-tables.py を適用して
#   docs/nbs-tree-*.md を生成

# 各 leaf の指標 UUID（60-90 分）
python3 probe-nbs-indicators.py
# → /tmp/nbs-probe-cache/{cid}.json に書き出し（再開可能）
# → /tmp/nbs-indicators-final.{json,md} に集約
# → 手動で頻度別に分割し docs/ にコピー
```

## WAF / rate-limit のメモ

`probe-nbs-indicators.py` は 2026-04-18 の取得時にチューニングされました：

- Base throttle：NordVPN 経由（動作確認済み IP は `194.233.x.x` / M247 レンジ）でのリクエスト間隔は 0.5s。住宅非 VPN IP では安全な値として 1.5s を推奨。
- Session priming：最初に必ずホームページを GET して `JSESSIONID` cookie を確立し、以降の API 呼び出しはすべてこれを再利用します。
- WAF 検出：response body が `<` で始まる場合は WZWS の JS challenge が発動しています。script は指数的にバックオフ（60s、120s、240s、…、最大 10 分）し、session をローテーションして再試行します。
- HTTP `RemoteDisconnected` / 一時的な `URLError`：線形バックオフ（2s、4s、6s）で 3 回再試行。
- 2026-04-18 のフルカタログ実行は WAF イベント 0 件、ネットワークエラー 1 件（完全性のため手動で再試行）で完了しました。

## 出力 schema（コンシューマ向け）

```json
{
  "<cid-uuid>": {
    "cid": "<cid-uuid>",
    "path": "月度 → 价格指数 → ... → 全国居民消费价格分类指数 (2026-)",
    "freq": "月度",
    "leaf_name": "全国居民消费价格分类指数 (2026-)",
    "indicators": [
      {
        "_id": "<indicator-uuid>",
        "name": "居民消费价格指数 (上年同月=100)",
        "group": "居民消费价格指数",
        "unit_code": "<unit-uuid>",
        "unit_name": "%",
        "order": 1,
        "kj1_name": "上年同月=100"
      }
    ]
  }
}
```

エラー項目は通常の形式の代わりに `{"cid": "...", "error": "...", "path": "..."}` を持ちます。
