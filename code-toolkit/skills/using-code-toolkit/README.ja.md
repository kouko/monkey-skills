# using-code-toolkit

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> code-toolkit のルーター兼フレームワーク憲章。プラグインの SessionStart フックで Claude Code / Codex CLI の全セッションに自動注入され、エージェントがコードを書く前にルールを知る状態を保証する。

[code-toolkit](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)。本 README はインストール判断のための人間向け文書。

## なぜルーターが要るか

`code-toolkit` は Superpowers 風のプロセス層（brainstorm → plan → SDD → TDD iron-law → debugging → code-review → finish-branch）と、`domain-teams:code-team` の standards をバイトレベルで完全一致でコピーした知識層を提供する。ルーターが無いと、エージェントはどの段階でどの skill をロードし、どの一次資料（Beck / Martin / Fowler / OWASP / 徳丸本）を引用するかを毎回ゼロから判断することになる。ルーターはその意思決定を一元化する。

SessionStart フックでルーターを注入するのは、ユーザーが「あ、call し忘れた」となる事故を防ぐため。Phase 1.5 で `obra/superpowers` と併用するユーザー向けに `CODE_TOOLKIT_MODE=off` 退避フラグを追加する。

## ルーティング先

| 段階 | Skill | v0.1.0 status |
|---|---|---|
| Discovery | [`brainstorming`](../brainstorming) | ✅ shipped |
| Planning | [`writing-plans`](../writing-plans) | Phase 2 |
| Execution | [`subagent-driven-development`](../subagent-driven-development) | ✅ shipped |
| Discipline | [`tdd-iron-law`](../tdd-iron-law) | ✅ shipped |
| Repair | [`systematic-debugging`](../systematic-debugging) | Phase 2 |
| Review | [`requesting-code-review`](../requesting-code-review) | Phase 3 |
| Verification | [`verification-before-completion`](../verification-before-completion) | Phase 3 |
| Branch close | [`finishing-a-development-branch`](../finishing-a-development-branch) | Phase 3 |

## 使う場面

- あらゆるコーディング作業 — 機能追加 / バグ修正 / リファクタ / マイグレーション / 依存更新 / レビュー。
- トリガー語（多言語）：「機能を追加 / バグを直して / リファクタ / add a feature / refactor / fix this bug / 加個功能 / 重構 / 修 bug」。

## 使わない場面

- 「この関数は何をする？」のような読み取り専用の質問 — ルーターは何も書かない／監査しないので、直接回答。
- 出荷済みアーティファクトの遵守スコア監査 — `domain-teams:code-team`（パッシブ gate）を使う。
- アプリコードではなく *skill* を書く・リファクタする — `dev-workflow:skill-creator-advance` / `skill-refactor`。

## 共存

- **`domain-teams:code-team`** — 監査用のパッシブ gate として維持。本 toolkit の知識層はその functional copy で、`scripts/verify-drift.py` がドリフトを監視。
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — 必要箇所で委譲する（再実装しない）。
- **`obra/superpowers`** — skill 名称と SessionStart フックが重複。フックを無効化したい場合は `export CODE_TOOLKIT_MODE=off`。

## 関連

- [`SKILL.md`](SKILL.md) — エージェント向け運用仕様。
- [`../../PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) — 商業 / ユーザー / Q-lock。
- [`../../TECH-SPEC.md`](../../TECH-SPEC.md) — アーキテクチャ / hooks / SSOT。
- [`../../ROADMAP.md`](../../ROADMAP.md) — フェーズ計画 / 決定台帳。
