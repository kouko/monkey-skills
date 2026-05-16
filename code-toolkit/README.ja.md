# code-toolkit

> **状態**: 設計のみ（Phase 0 — PRODUCT/TECH/ROADMAP ロック済み、skill 未出荷）
> 言語: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

プロセス規律 + 一次情報源 grounding コーディングツールキット。2 層アーキテクチャ：

- **プロセス層**（Superpowers 風）: SessionStart hook 自動注入による 7 段階ワークフロー — brainstorm → plan → SDD（subagent-driven development）→ TDD 鉄則 → systematic debugging → code-review → finish-branch。
- **知識層**（code-team grounding）: `domain-teams:code-team` の standards / rubrics / checklists を byte-identical な functional copy として保持。各ルールは一次情報源（Clean Code / Pragmatic Programmer / SOLID / Beck 2002 TDD / Fowler 2018 Refactoring / Feathers 2004 Legacy Code / OWASP ASVS v5.0.0 / 徳丸本 第 2 版 Ch.6）に traceable。

## 状況

| Phase | Version | Skills | 状態 |
|---|---|---|---|
| 0 | 0.1.0-draft | — | ⏳ 設計ロック（本 PR） |
| 1 | 0.1.0 | 3 (using / tdd-iron-law / SDD) | 予定 |
| 1.5 | 0.1.5 | 3 (+soft-mode) | 予定 |
| 2 | 0.2.0 | 6 (+brainstorming / writing-plans / sys-debugging) | 予定 |
| 2.5 | 0.2.5 | 6 (+Codex CLI 出荷) | 予定 |
| 3 | 0.3.0 | 9 (Superpowers parity) | 予定 |
| 4 | 1.0.0 | 9 (GA) | 予定 |

全体計画は [ROADMAP.md](ROADMAP.md) を参照。

## 設計文書

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — ビジネス / ターゲットユーザー / ゴール / Q-lock
- [TECH-SPEC.md](TECH-SPEC.md) — アーキテクチャ / SSOT / hooks / interface contracts
- [ROADMAP.md](ROADMAP.md) — phase 計画 / 意思決定台帳

## 共存

- **`domain-teams:code-team`** — 受動 gate 入口（既存成果物のレビュー）。code-toolkit は能動構築入口。
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — code-toolkit は適切なタイミングで委譲。

## 衝突

- **`obra/superpowers`** — 両者とも SessionStart hook と重複する skill 名を出荷。`export CODE_TOOLKIT_MODE=off` で本プラグインの hook 注入を無効化することで解決。

## ライセンス

MIT
