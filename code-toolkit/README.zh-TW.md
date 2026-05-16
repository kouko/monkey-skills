# code-toolkit

> **狀態**: 僅設計階段（Phase 0 — PRODUCT/TECH/ROADMAP 已鎖，尚未出貨任何 skill）
> 語言: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

流程紀律 + 一級書目 grounding 程式開發工具組。雙層架構：

- **流程層**（Superpowers 風格）：SessionStart hook 自動注入的 7 階段工作流 — brainstorm → plan → SDD（子代理串接開發）→ TDD 鐵律 → systematic debugging → code-review → finish-branch。
- **知識層**（code-team grounding）：`domain-teams:code-team` 的 standards / rubrics / checklists 以 byte-identical functional copy 形式攜帶。每條規則皆可溯源到一級書目（Clean Code / Pragmatic Programmer / SOLID / Beck 2002 TDD / Fowler 2018 Refactoring / Feathers 2004 Legacy Code / OWASP ASVS v5.0.0 / 徳丸本 第 2 版 Ch.6）。

## 狀態

| Phase | Version | Skills | 狀態 |
|---|---|---|---|
| 0 | 0.1.0-draft | — | ⏳ 設計鎖定（本 PR） |
| 1 | 0.1.0 | 3 (using / tdd-iron-law / SDD) | 待開工 |
| 1.5 | 0.1.5 | 3 (+soft-mode) | 待開工 |
| 2 | 0.2.0 | 6 (+brainstorming / writing-plans / sys-debugging) | 待開工 |
| 2.5 | 0.2.5 | 6 (+Codex CLI 出貨) | 待開工 |
| 3 | 0.3.0 | 9 (Superpowers parity) | 待開工 |
| 4 | 1.0.0 | 9 (GA) | 待開工 |

完整計畫見 [ROADMAP.md](ROADMAP.md)。

## 設計文件

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — 商業 / 目標使用者 / 目標 / Q-lock
- [TECH-SPEC.md](TECH-SPEC.md) — 架構 / SSOT / hooks / interface contracts
- [ROADMAP.md](ROADMAP.md) — phase 計畫 / 決策台帳

## 並存

- **`domain-teams:code-team`** — 被動 gate 入口（已產出要審查）。code-toolkit 是主動建構入口。
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — code-toolkit 在合適時機 delegate 過去。

## 衝突

- **`obra/superpowers`** — 兩者都 ship SessionStart hook 及重疊的 skill 名稱。設定 `export CODE_TOOLKIT_MODE=off` 來關閉本 plugin 的 hook 注入即可。

## 授權

MIT
