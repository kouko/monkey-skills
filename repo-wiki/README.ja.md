# repo-wiki

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Karpathy の LLM Wiki Pattern をコードリポジトリに適用。隠し `.repo-wiki/` ナレッジベースを src/ ツリー全体のスキャン（全 module に entity stub）+ module 毎の直近 5 commits + 90 日 bounded global git scan で seed。変更と会話から成長させ、自然言語でクエリ。`src/` が常に真実の源 — wiki は重要な瞬間にキャッシュを verify する。

**Version**: 1.1.0 · **Part of**: [monkey-skills](https://github.com/kouko/monkey-skills) · **License**: MIT

## 背景

AI コーディングツールは単一セッション内でしかコードベースを理解しない。次のセッションはゼロから。既存の解決策は二極化している：

- **SaaS セマンティック検索**（Greptile、DeepWiki、Cursor @Codebase）— コードがマシンを離れる、ナレッジが repo にない
- **フラット Markdown コンテキスト**（CLAUDE.md、AGENTS.md、Memory Bank）— 全文注入、repo サイズで token コスト爆発、合成された WHY なし

`repo-wiki` はそのギャップを埋める：永続的・repo にコミットされた・合成済みのナレッジを、AI エージェントが全文注入なしで、SaaS 依存なしでクエリできる。

[Karpathy LLM Wiki Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) をコードに対応：

```
raw/      (general wiki)  →  src/**       (code repo)
wiki/     (general wiki)  →  .repo-wiki/  (code repo)
ingest    (general wiki)  →  /repo-wiki:ingest
query     (general wiki)  →  /repo-wiki:query
```

## Skills

| Skill | いつ | 主入力 |
|---|---|---|
| [`/repo-wiki:init`](skills/init/) | リポジトリごとに 1 回（再実行安全） | Phase 1: `git ls-files`（src/ 全体）+ module 毎 last-5 commits。Phase 2: 90 日 global git scan（最大 50 commits / 15 source pages）。Phase 3（`init full-history` でオプトイン）: era-grouped 完全履歴 backfill。 |
| [`/repo-wiki:ingest`](skills/ingest/) | 意義のある変更後 OR コンテキスト捕捉時 | 前回 ingest 以降の git diff、テキスト引数、またはファイルパス |
| [`/repo-wiki:query`](skills/query/) | コードベースについて聞きたいとき | `.repo-wiki/index.md` + 関連ページ、重要な瞬間に `src/` で verify |

## クイックスタート

[monkey-skills marketplace](https://github.com/kouko/monkey-skills) からインストールし：

```bash
# Repo のルートで初回：
/repo-wiki:init

# 次の機能完了後：
/repo-wiki:ingest

# コードベースについて聞く：
/repo-wiki:query "AuthModule はどう動いてる？"
```

`init` は `.repo-wiki/` を `SCHEMA.md` + `index.md` + `log.md` + `overview.md` で scaffolding し、src/ ツリー全体をスキャンして完全な entity カバレッジを構築（検出された全 module に stub: `paths` + `Common Entry Points` + 直近 5 commits を `Recorded Decisions` として seed）、続いて 90 日 bounded global git scan で cross-module 変更の source page を生成。同時に `CLAUDE.md` に小さな idempotent ブロックを書き込み、将来のセッションが `.repo-wiki/` は AI 所有だと知るようにする。

`init` は **再実行安全**：`log.md` 履歴、ingest で蓄積された entity セクション（`Responsibility`、`Architecture Snapshot`、`Gotchas`、`Dependencies`）、`overview.md` の `## Repository` 自定義セクションを保持。再実行は init 所有データ（paths、entry points、seed された直近 commits）のみリフレッシュし、`log.md` の last commit SHA を使って新 commit のみ増分処理。

**デフォルトモード**（`/repo-wiki:init`）は実用 80% をカバー：完全な現状 + 直近活動。**完全履歴モード**（`/repo-wiki:init full-history`、または `"full backfill"` / `"完整歷史"`）は Phase 3 を追加：era-grouped（6 ヶ月単位）の歴史的 major commit backfill。Era pages は 15-page Phase 2 cap の対象外。

**init が読まないもの**：src/ ファイル内容。`git ls-files` のパス、entry-point ファイルのパス、`git log` メタデータのみ使用。WHY-not-WHAT 原則を維持し、Greptile/DeepWiki スタイルのコード要約ツールと区別される。

## ingest は多態的

同じ skill が引数から 3 つの入力モードを判別：

```bash
# Git mode（デフォルト）— 前回 ingest の commit SHA から増分
/repo-wiki:ingest

# Context mode — commit に入らなかった tribal knowledge を捕捉
/repo-wiki:ingest "AuthModule の命名は 2020 年の old-auth-service からの migration が由来"

# Doc-import mode — 外部設計ドキュメントを取り込む（明示的マーカー必須）
/repo-wiki:ingest "import design doc: docs/architecture/postgres-decision.md"
```

明示的 import マーカー（`import`、`import doc`、`讀取`、`匯入`、`読み込んで` 等）なしでパスに言及しても、context mode のままになる — 偶発的なファイル読み込みを避けるため。

## `.repo-wiki/` は AI 所有、しかし `src/` が権威

最重要の設計判断：**`.repo-wiki/` はベストエフォートのキャッシュであり、真実の源ではない**。entity ページの実装記述は古くなる可能性がある。これを誠実に保つため、`/repo-wiki:query` は **Eager verification** パイプラインを実行する：

以下のいずれかの trigger が発動すると、query は `src/` を読んで現在の振る舞いに関する主張を spot-check：

| ID | Trigger |
|---|---|
| T1 | 読み込んだページの `last_updated > 60 日` |
| T2 | 質問に「currently」「now」「still」「現在」「目前」「今」が含まれる |
| T3 | 回答が新コードを書く判断材料になる（action 動詞 OR 直近の Edit/Write） |
| T4 | 読み込んだ source page に TODO / 「subject to change」/「待確認」 |
| T5 | 複数の読み込み済みページが互いに矛盾 |
| T6 | 質問が純粋に過去決定について（negative trigger — verification skip） |
| T7 | ユーザーが明示的に verification を要求 |

trigger 発動時、回答は **segmented**：

```markdown
## Verified Claims (against src/)
- AuthModule は jose を JWT signing に使う — src/auth/jwt.ts:12 で verify

## Unverified Claims (from .repo-wiki/ cache)
- AuthModule は SessionStore に依存 — AuthModule.md より、未 verify

## Discrepancies Found
- entity に "throws AuthError" とあるが src/auth/jwt.ts:42 は JwtError を throw
  → 提案：/repo-wiki:ingest "AuthError was renamed to JwtError"

## Verification Coverage
- Triggers fired: T2
- Files read: 3 of 80 candidate paths (3.8%)
- Selection: claim-mentioned + entry points
- Uncovered: src/auth/session.ts, src/auth/refresh.ts, ... (75 more)
```

Verification depth は `budget = max(1, min(10, ceil(0.05 × total_paths)))` で制限される — 1 つの query で `src/` ファイルを 10 件以上開かない。Coverage section により実際の verification 深度が見える。純粋な決定問題（「なぜ Postgres を選んだのか」）は verification を起動しない — 過去の決定は陳腐化しない。

## 日常ワークフロー

```
1. 機能完成 → /repo-wiki:ingest
   AI が git log + diff を読む
   → sources/2026-05-02-add-payment.md (origin: git) を書く
   → entities/PaymentService.md を更新
   → 必要なら concepts/IdempotencyKey.md を作成
   → index.md + log.md を更新

2. Tribal knowledge を入手 → /repo-wiki:ingest "PaymentService のリトライが 5 回なのは <理由>"
   → sources/2026-05-02-manual-payment-retries.md (origin: manual) を書く
   → entities/PaymentService.md gotchas を更新

3. 質問がある → /repo-wiki:query "PaymentService のエラー処理はどうなってる？"
   → index.md を読む → PaymentService entity + 最近の sources を load
   → verification を発動（T2 if "currently"; T1 if stale; etc.）
   → segmented 回答 + src/ ポインター
   → synthesis 保存を提案
```

## 既存ツールとの違い

| ツール | ギャップ |
|---|---|
| Greptile / DeepWiki | SaaS、コードがマシンを離れる、オフライン不可 |
| Code-Index-MCP | セマンティック検索は良いが WHY 合成なし |
| Roo Memory Bank | 全文注入、page type なし、verification なし |
| RepoAgent | 知識更新を auto-commit（多人数リスク） |
| SamurAIGPT/llm-wiki-agent | 汎用ドキュメント、git/コード非対応 |
| `dev-workflow:git-memory` | **commit 時点**の決定コンテキストを捕捉；`repo-wiki` は **cross-commit のアーキテクチャ的全体像** — 補完的・競合せず |

`repo-wiki` の独自の組み合わせ：**git-aware ingest + 多態的コンテキスト捕捉 + 構造化された WHY ナレッジ + AI 所有 wiki + verification-fenced reads + ゼロ外部依存**。

## 設計哲学

5 つの原則：

1. **Synthesize at ingest time, not query time** — ナレッジは ingest 時に整理；query は読むだけ
2. **WHY first, WHAT is best-effort cache** — 実装記述は許容、しかし非権威
3. **Verify at key moments** — trigger 発動時 query が `src/` を読む；segmented 出力で不確実性を明示
4. **Gap is feedback** — query がページを見つけない / 古い情報を発見すると具体的な `/repo-wiki:ingest` を提案
5. **Multi-source input** — git がデフォルト、conversational context と外部ドキュメントも同じ ingest pipeline

## Schema は v2.0 まで凍結

`.repo-wiki/SCHEMA.md` の page type、frontmatter 構造、命名規則は v1.x の間は変更しない。v2.0 で migration script と共にメジャー変更を出す。v1 ユーザーは v1.x 内で migration を計画する必要なし。

## v2 backlog

- `knowledge/inputs/` — フォーマルな人間編集可能 input ディレクトリ
- 多人数 CI workflow（AI が提案、人間が PR コメントで承認）
- `/repo-wiki:lint` — ヘルスチェック（broken links、git-aware staleness、orphan concepts）
- `/repo-wiki:graph` — markdown link 参照からのナレッジグラフ
- Monorepo サポート（app ごとの `.repo-wiki/` サブディレクトリ）
- AGENTS.md drop-in（ベンダー中立配布）
- v1.x 安定後の独立リポジトリ graduation

## インスピレーション & クレジット

- [Karpathy LLM Wiki Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — 概念的ルーツ
- [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) — `raw/ → wiki/` アーキテクチャ参照
- [llmrix/llm-wiki-skill](https://github.com/llmrix/llm-wiki-skill) — SKILL.md 実装参照
