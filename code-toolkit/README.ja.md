# code-toolkit

> **Process-discipline + canon-grounded コーディングワークフロー for Claude Code (+ Codex CLI)。** 10-skill プラグイン。SessionStart で router charter を自動注入し、エージェントが合理化をやめて defer し始めるよう仕向ける — 各ルールは一次情報源に grounded（Beck on TDD / Martin on naming / Fowler on refactoring / Feathers on legacy code / OWASP ASVS on security / 徳丸本 on encoding security）。

**状態**：v0.7.0（10 skill 出荷済 — v0.3.0 以来 Superpowers parity；v0.6.0 / P15-12 以来 4 つの plugin-level subagent が SSOT 注入の 12 ルール engineering baseline を運搬；v0.7.0 は **reviewer-output discipline R1+R2**（`standards_version` スタンプ + evidence-citation 必須、第 2 の SSOT 注入ブロック `_reviewer-discipline.md` 経由）+ brainstorming brief schema に **Current State Evidence** セクション追加（5 次元 recon チェックリスト Forward / Reverse / Error / Data / Boundary）+ artifact パス移行 `docs/superpowers/` → `docs/code-toolkit/` を出荷；Codex CLI build 完了、実機検証は延期中；merge to main はユーザポリシー「完全做好之前不合 main」+ v1.0.0 目標 ≥5 dogfood notes でブロック中）
**言語**：[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)
**Repository**：[`monkey-skills`](https://github.com/kouko/monkey-skills) の一部

---

## 30 秒の例

新しい Claude Code セッションに貼り付け（インストール後 — 下記参照）：

```
新機能をゲートできるようにフィーチャーフラグシステムを追加したい。
まだ無いから。基本版だけでいい：env var チェック + ハードコードした enabled list。
ブレインストーミングは不要、設計は明らか。
```

**何が起きるか**（code-toolkit インストール済み）：

SessionStart で注入された router が Rule #1（*"implementing 前に brainstorm"*）を発火。`brainstorming` skill が 5-axis HARD-GATE で起動。discovery のスキップを拒否、JTBD framing を明文化、alternatives を提示（何もしない / 単一 env var / 完全 flag system）、最後に `dev-workflow:complexity-critique` への次ステップ委譲を推奨 — フィーチャーフラグシステムはまさに PAGNI の典型的 smell だから。

**得られないもの**：まだ surfaced していない問題のために前もって書かれた 200 行の feature-flag infrastructure。

[`docs/examples/`](docs/examples/) に 3 つの end-to-end 完全フロー（Python / TypeScript / Swift）。

---

## インストール

### Claude Code

```bash
# 一度きり：marketplace を追加
claude plugin marketplace add https://github.com/kouko/monkey-skills.git

# インストール
claude plugin install code-toolkit@monkey-skills

# 確認
claude plugin list | grep code-toolkit       # 期待：enabled
claude plugin details code-toolkit           # 期待：10 skills + 1 SessionStart hook
```

### Codex CLI（build 完了、実機検証は延期中）

⚠️ Codex CLI manifest は build 済みで Claude Code 変体と同期して v0.7.0 までバンプ済み、しかし実 Codex CLI 環境での install + 検証 ritual はユーザ指示により延期中。準備ができたら [`tests/codex-cli/README.md`](tests/codex-cli/README.md) を参照。

### ローカル開発（コントリビューター向け）

```bash
# monkey-skills を clone + local marketplace として登録
git clone https://github.com/kouko/monkey-skills.git
cd monkey-skills

# local-scope marketplace として追加（code-toolkit 変更のテスト用）
claude plugin marketplace add . --scope local
claude plugin install code-toolkit@monkey-skills --scope local
```

---

## 10 のスキル

| # | Skill | Stage | 何をするか |
|---|---|---|---|
| Router | [`using-code-toolkit`](skills/using-code-toolkit/) | Always-on | SessionStart 自動注入；4 つの load-bearing rules + Skill Priority テーブル |
| 1 | [`brainstorming`](skills/brainstorming/) | Discovery | HARD-GATE 5-axis 探索（Problem / Users / Smallest End State / Alternatives / What Becomes Obsolete）；v0.7.0+ ブリーフに `Current State Evidence` 5 次元 recon セクション搭載；discovery スキップの合理化を拒否 |
| 2 | [`writing-plans`](skills/writing-plans/) | Planning | ≤5-task plan + 各タスク RED-GREEN acceptance；BLOCKED → child-test フォールバック（Beck Part II §Child Test） |
| 3 | [`subagent-driven-development`](skills/subagent-driven-development/) | Execution | タスクごとに triad を派遣（implementer + spec-reviewer + code-quality-reviewer）；reviewer 三人組は `reviewer-discipline-v1` SSOT 注入ブロック（R1+R2）搭載 |
| 4 | [`tdd-iron-law`](skills/tdd-iron-law/) | Discipline | "FAILING TEST なしに production code を書くな"（Beck 2002 Preface, ISBN 978-0321146533）；§Feathers (2004) 正当な legacy code backfill 区別 |
| 5 | [`systematic-debugging`](skills/systematic-debugging/) | Repair | 4 フェーズ REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY；HARD-GATE "再現せず fix するな" |
| 6 | [`requesting-code-review`](skills/requesting-code-review/) | Review | 全ブランチレビュー 7 次元スコア（cross-task-coherence はブランチ限定次元）；v0.7.0+ verdict に `standards_version` スタンプ、findings は `where:` file:line 必須；push-as-trigger |
| 7 | [`verification-before-completion`](skills/verification-before-completion/) | Verification | "PACKAGE-LEVEL TEST 実行なしに DONE するな"；20+ stack の canonical コマンドを網羅 |
| 8 | [`finishing-a-development-branch`](skills/finishing-a-development-branch/) | Branch close | 7 ステップ orchestrator（review → verify → git-memory 必須 → commit → push → 任意 PR + worktree cleanup） |
| Aux | [`using-git-worktrees`](skills/using-git-worktrees/) | Lateral | ネイティブ `git worktree` ワークフロー；`.worktrees/<slug>/` 慣習 |

---

## Quickstart — 線形フロー

非 trivial タスクで意図されたユーザフロー：

```
あなた: "feature X を追加したい"
  ↓ (SessionStart hook router 自動発火)
brainstorming → 5-axis brief + Current State Evidence → docs/code-toolkit/specs/<topic>.md
  ↓
writing-plans → ≤5-task plan → docs/code-toolkit/plans/<topic>.md
  ↓
subagent-driven-development → タスクごとに triad ディスパッチ
  ↓ (各 implementer subagent 内)
  tdd-iron-law → RED-GREEN-REFACTOR
  ↓ (implementer が decomposition 信号付きで BLOCKED を返す)
  writing-plans (再呼び出し) → Child Test 子分解
  ↓ (各タスク DONE)
SDD orchestrator 継続
  ↓ (全タスク DONE)
finishing-a-development-branch
  ↓ Step 1: requesting-code-review (cross-task-coherence 次元；verdict は standards_version スタンプ付き)
  ↓ Step 2: verification-before-completion (npm test / pytest / etc.)
  ↓ Step 3: dev-workflow:git-memory (Decision: / Learning: / Gotcha: trailers)
  ↓ Step 4: git commit (ユーザ承認後)
  ↓ Step 5: git push (ユーザ再認可後)
  ↓ Step 6: gh pr create (任意、opt-in)
  ↓ Step 7: git worktree remove (任意、確認)
```

オンデマンド：
- **`systematic-debugging`** は「明らかな 1 行 fix」ではないバグに遭遇したときに発火 — 断続的、"my machine では動く"、レース条件など。
- **`using-git-worktrees`** は並列ブランチが必要なときに発火（本プラグイン自体が worktree で開発されている）。

---

## 互換性

| Harness | 状態 |
|---|---|
| **Claude Code** | ✅ 複数 ritual サイクル完全検証 — Phase 3 orchestrator (v0.3.0)、Phase 4 prep (v0.4.0)、多言語研究 (v0.5.1)、plugin-level agent dispatch (v0.5.2 + v0.6.0)、cross-task-coherence 次元での全ブランチ code-review (v0.6.0)、reviewer-discipline SSOT extraction + Current State Evidence section (v0.7.0) |
| **Codex CLI** | ⚠️ Manifest は build + v0.7.0 までトラック済；実機 install + 検証 ritual はユーザ指示により延期中（`tests/codex-cli/README.md` 参照） |

SessionStart hook は portable な JSON shape を発出し、Claude Code の `hookSpecificOutput.additionalContext`、Codex CLI の `additional_context`、legacy `additionalContext` keys をカバー — 同じ hook が両 harness を提供。

---

## 共存

本プラグインは関連プラグインと競合せず共存するよう設計：

| Plugin | 関係 |
|---|---|
| **[`domain-teams:code-team`](https://github.com/kouko/monkey-skills/tree/main/domain-teams/skills/code-team)** | パッシブ gate コンプライアンス reviewer。code-toolkit はアクティブ build orchestrator で、code-team の standards を知識層として使用（`scripts/distribute.py` 経由でバイト一致 functional copy、`scripts/verify-drift.py` で drift check）。同じ一次情報源、異なる呼び出しモード。 |
| **[`dev-workflow:git-memory`](https://github.com/kouko/monkey-skills/tree/main/dev-workflow/skills/git-memory)** | `finishing-a-development-branch` Step 3 で必須委譲先（P3-D）。Commit-trailer 判断（Decision: / Learning: / Gotcha:）を決める；code-toolkit は重複実装しない。 |
| **[`dev-workflow:complexity-critique`](https://github.com/kouko/monkey-skills/tree/main/dev-workflow/skills/complexity-critique)** | `brainstorming` Axis 3 で complexity smell が出たときの任意委譲先。同じ SSOT-and-functional-copy mindset framing。 |
| **[`obra/superpowers`](https://github.com/obra/superpowers)** | 設計インスピレーション；`CODE_TOOLKIT_MODE=off` env var escape hatch 経由で共存（env var 設定で code-toolkit hook を無効化、superpowers のみ発火）。両プラグイン同時インストール可；env var で切替。 |

クロスプラグイン挙動は [`tests/integration/`](tests/integration/) 内 5 つの integration test script で検証。

---

## なぜこのプラグインが存在するか

`monkey-skills` には既に 2 つの関連プラグインがある：

- **`domain-teams:code-team`** — 一次情報源 grounded standards / rubrics / checklists（Beck から 徳丸本 まで 8 冊）。強い知識層、弱い呼び出し：エージェントが call を覚えていなければならない。
- **`obra/superpowers`（別 repo）** — SessionStart hook + measure rhetoric（"Delete it. Start over."）。強い呼び出し、弱い grounding：ルールが自分自身を引用し、canon を引用しない。

`code-toolkit` はその統合：Superpowers 風の自動注入 + code-team 風の canon-grounded measures。各ルールは構造的に強制され（SKILL.md HARD-GATE + Red Flags 拒否パターン経由）かつ実質的に正当化される（ISBN / URL / 章レベルの一次情報源引用経由）。

---

## ドキュメント

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — 設計意図、ターゲットユーザ、Q-lock 決定
- [TECH-SPEC.md](TECH-SPEC.md) — アーキテクチャ、SSOT メカニズム、hook contract
- [ROADMAP.md](ROADMAP.md) — phase 計画、決定台帳、Phase 1.5 rolling backlog
- [CHANGELOG.md](CHANGELOG.md) — Journey overview + バージョンごと詳細
- [docs/examples/](docs/examples/) — 3 つの end-to-end 完全例（Python / TypeScript / Swift）
- [docs/announcement/v1.0.0-announcement.md](docs/announcement/v1.0.0-announcement.md) — 公開 announcement ドラフト（v1.0.0 で公開）
- [research/grounding-v0.1.0.md](research/grounding-v0.1.0.md) — バージョンごと grounding audit

---

## コントリビューション

Issue + PR 歓迎：https://github.com/kouko/monkey-skills/issues に `code-toolkit:` プレフィックスで。

実使用 dogfood notes（v1.0.0 を阻害する P15-5 backlog 項目）は `research/dogfood-YYYY-MM-DD-<topic>.md` に投入 — 短いノートでも工具紀律強度の calibration に役立つ。

---

## ライセンス

MIT — repo ルートの [LICENSE](../LICENSE) を参照。
