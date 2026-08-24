# Plan: claude-test profile live gate

Source brief: docs/loom/specs/2026-08-24-claude-test-profile-live-gate.md
Goal: 讓 live-host gate 使用可重複使用的 `claude-test` profile，同時保持日常設定、登入與 plugin 狀態不變。
Stage: review:round-1
Steps:
  1. 建立與驗證專用 Claude profile
  2. 將實機 gate 固定到該 profile
  3. 以兩個真實 host 完成實機驗證
Total tasks: 3
Critical-path depth: 3
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-08-24, round 1)

## Task-flow diagram

```mermaid
flowchart LR
    T1["T1 建立 claude-test profile"] --> T2["T2 固定 live gate"] --> T3["T3 實機驗證"]
```

## Open Questions

N/A — no unresolved question: the user approved the named test-profile boundary and its minimal configuration.

## Task 1 — 建立專用 profile

- Description: Add the managed `claude-test` Claude profile, its shell alias, and installer coverage following the existing named-profile convention.
- Module: `/Users/kouko/dotfiles` Claude profile package
- Files touched: `/Users/kouko/dotfiles/claude/.claude-test/settings.json`, `/Users/kouko/dotfiles/zsh/.zshrc`, `/Users/kouko/dotfiles/_scripts/stow-install.sh`, `/Users/kouko/dotfiles/_scripts/stow-restow.sh`, `/Users/kouko/dotfiles/_scripts/install-claude.sh`, `/Users/kouko/dotfiles/claude/README.md`, `/Users/kouko/dotfiles/tests/claude_profiles_test.sh`
- Context paths:
  - `/Users/kouko/dotfiles/claude/README.md`
  - `/Users/kouko/dotfiles/_scripts/install-claude.sh`
  - `/Users/kouko/dotfiles/zsh/.zshrc`
- Acceptance:
  - RED: `tests/claude_profiles_test.sh::test_claude_test_profile_is_managed_and_invokable` fails because `claude-test` is absent from one or more required profile integration points.
  - GREEN: The test proves the alias sets only `CLAUDE_CONFIG_DIR=$HOME/.claude-test`, stow creates that directory, installation and update enumerate it, and its minimal settings contain no inherited plugins or hooks.
- Dependencies: none
- Independent: false
- Brief item covered: BI-1
- Status: done(profile-wiring)
- Gloss: 建立可一次登入、往後可重複使用的測試帳號入口。

## Task 2 — 固定 gate 到專用 profile

- Description: Replace the caller-supplied disposable Claude sandbox with the exact `~/.claude-test` profile and retain daily configuration, authentication, and plugin mutation detection without rewriting HOME.
- Module: loom-code/scripts/live_host_review_gate.py
- Files touched: loom-code/scripts/live_host_review_gate.py, loom-code/scripts/test_live_host_review_gate.py, docs/loom/dogfood/2026-08-24-cross-host-review-gate-live-host.md
- Context paths:
  - loom-code/scripts/live_host_review_gate.py
  - loom-code/scripts/test_live_host_review_gate.py
  - docs/loom/specs/2026-08-24-claude-test-profile-live-gate.md
- Acceptance:
  - RED: `test_live_host_review_gate.py::test_live_gate_uses_only_named_claude_test_profile_without_home_rewrite` fails because the gate accepts an arbitrary disposable directory or overrides HOME.
- GREEN: The gate uses only `Path.home() / ".claude-test"`, fails safely when its authentication is unavailable, allows that profile's metadata to change, and fails if daily settings, Codex authentication, or plugin manifests differ; an in-memory digest is never reported, and session, log, and cache writes are ignored.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: BI-2, BI-3, BI-4, BI-5, BI-6
- Status: done(profile-gate-boundary)
- Gloss: 自動 gate 只動專用 profile；設定、登入或 plugin 被碰觸仍會拒絕出貨，正常執行紀錄不會誤判。

## Task 3 — 完成雙 host 實機驗證

- Description: Authenticate the dedicated profile once and run the real Claude Code and Codex gate to produce a redacted PASS report.
- Module: live-host release verification
- Files touched: docs/loom/dogfood/2026-08-24-cross-host-review-gate-live-host.md
- Context paths:
  - loom-code/scripts/live_host_review_gate.py
  - docs/loom/dogfood/2026-08-24-cross-host-review-gate-live-host.md
- Acceptance:
  - RED: `live_host_review_gate.py --candidate loom-code --codex-auth-source ~/.codex/auth.json --report <report>` exits non-zero before the dedicated profile is authenticated and configured.
  - GREEN: The same gate exits zero after one-time `claude-test` authentication; the report records PASS for all host cases, unchanged daily state, and no credential content.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: BI-2, BI-3, BI-4
- Status: done(live-dual-host-pass)
- Gloss: 最後以真實 Claude 與 Codex 證明自動化可出貨。

## Decision Log

- Use a durable Claude profile because its official local profile convention separates credentials by `CLAUDE_CONFIG_DIR`; retain ephemeral CODEX_HOME because the current gate already proves it isolates Codex runtime state.

## Notes

- The dotfiles worktree has unrelated changes; this plan touches only previously clean files plus a new test file.
