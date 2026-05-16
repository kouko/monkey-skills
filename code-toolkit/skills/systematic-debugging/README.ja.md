# systematic-debugging

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> **HARD-GATE — 再現せずに修正するな。** 4 フェーズ規律：REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY。tdd-iron-law の「失敗テストなしで実装するな」のデバッグ版。Kernighan & Pike (1999) *The Practice of Programming* 第 5 章 (ISBN 978-0201615869) と Hunt & Thomas (2019) *Pragmatic Programmer* Topic 28 (ISBN 978-0135957059) を一次資料とする。ランダムパッチ、仮説なしロギング、try/except マスキング、「俺のマシンでは動く」を **拒否** する。

[code-toolkit](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## 4 フェーズ

| フェーズ | ゴール | 次への gate |
|---|---|---|
| 1 — **REPRODUCE** | 再現可能な trigger（RED テスト相当） | 🟢 再現可能 OR 🟡 条件限定済み |
| 2 — **ISOLATE** | 最小バグ locus に絞り込み（1 行 / 関数 / 依存 / 入力フィールド） | 単一コンポーネントまで narrow |
| 3 — **HYPOTHESIZE** | まだ観測していない事象を予言する **falsifiable** な仮説 | 仮説が falsifiable（何を観測すれば反証になるか明示） |
| 4 — **VERIFY** | 実験実行；確認 or 反証；確認なら fix + 回帰テスト + blast radius 比例 defense-in-depth | 仮説確認；fix 適用；回帰テスト配置 |

フェーズが gate を通らなければ次に進まない — 前フェーズに新情報を持って戻る。

## 使う場面

自動 routing：
- `tdd-iron-law` §False-green diagnostic が「初回 RUN でテスト pass + production code をコメントアウトしてもテスト失敗しない」を返す（テストが思った対象を測定していない）。
- SDD `implementer` サブエージェントが `BLOCKED` + `unblock_step: "test will not go RED"` を返す（実バグに対する失敗テストが構築できない）。
- ユーザが「動かない」と言うが原因が non-obvious — *"intermittent"*、*"俺のマシンでは動くが CI では動かない"*、*"動くべきなのに動かない"*。

## 使わない場面

[`SKILL.md`](SKILL.md) §When NOT to Use 限定列挙：

- 失敗テストが既に存在 AND 間違いの line が自明（tdd-iron-law でそのまま修正）
- typo / config 値の trivial bug（追跡すべき behavior chain なし）
- spec の通り動いている が spec 側が間違っている（brainstorming で spec を改訂）
- 前セッションで root-cause 済み

## このスキルが ship するもの

- [`SKILL.md`](SKILL.md) — 4 フェーズ運用仕様、Red Flags（8 rationalization × ja + zh-TW 多言語）、cross-skill 契約。
- [`references/root-cause-tracing.md`](references/root-cause-tracing.md) — Phase 2 ISOLATE サブプロトコル。bisection 軸表（git / dependency / input / component / time / 5-Whys）；halving コスト heuristics；anti-patterns。
- [`references/condition-based-waiting.md`](references/condition-based-waiting.md) — Phase 1 🟡 と Phase 2 time-axis bisection。`sleep(500)` anti-pattern を condition-polling に置換。言語別ライブラリ helpers。
- [`references/defense-in-depth.md`](references/defense-in-depth.md) — Phase 4 VERIFY 後の layering。6 層 ladder（回帰テスト → 入力検証 → 不変条件 assert → 型システム → 監視 → アーキ refactor）+ 比例ルール（コスト ≤ 次回発生時の想定損害）。
- [`references/character-encoding-debug.md`](references/character-encoding-debug.md) — エンコーディング固有の bisection（BOM / UTF mismatch / NFC-NFD / サロゲートペア / stream decoder buffer 境界）。`domain-teams:code-team/standards/character-encoding-security.md`（徳丸本 第 2 版 Ch.6）へリンク（セキュリティ視点）。

## Cross-skill 契約

- **上流**: `tdd-iron-law`（false-green diagnostic）または `subagent-driven-development`（implementer BLOCKED on test-cannot-go-RED）から呼び出される。
- **下流**: Phase 4 VERIFY の fix が `tdd-iron-law` の回帰テストを駆動（再現が RED）。
- **横（任意）**: ISOLATE で untanglable モジュールが判明した時は `dev-workflow:complexity-critique` で refactor-before-fix；*"なぜこのコードはこう書かれているのか"* の再導出前に `repo-wiki:query` / `dbt-wiki:query`。

## このスキルがしないこと

- 新機能を書かない（brainstorming → writing-plans → SDD → tdd-iron-law を使う）。
- `tdd-iron-law` の false-green diagnostic の代わりにはならない — それは entry condition であって substitute ではない。
- 先回りで defense-in-depth を追加しない。防御層は Phase 4 *結果* であって Phase 0 *姿勢* ではない。
- blast radius / 優先度を決めない — ユーザ / オーケストレータの判断。

## 関連

- [`SKILL.md`](SKILL.md) — 運用仕様。
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — このスキルを呼び出し、その出力を消費する規律。
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — implementer-BLOCKED 時にこのスキルを呼び出すオーケストレータ。
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — ルータ；本スキルは Stage 5（Repair、詰まった時）。
