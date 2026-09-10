# Codex Claude reviewer credential boundary — spec
intent: 2026-09-10-codex-claude-reviewer-outside-sandbox@9ca1435d3a3bee7c8ba9324ffe0a400e8b10723f
confirmed-behavior: 2026-09-10 @22e302c
pre-build-review: required — changes the cross-system execution and authorization contract between Codex and Claude Code

## Requirements
REQ-1 — Reuse an existing Claude login
  WHEN an already-authenticated user selects Claude Code as a second reader on Codex, the review shall run in an execution environment that can access that existing authentication without asking the user to log in again → Acceptance #1

REQ-2 — Preserve the bounded reviewer contract
  WHILE Codex runs the Claude reviewer outside its sandbox, the review shall use the existing single-attempt runner and preserve its valid-output, empty-output, timeout, and Closing Review retry behaviour → Acceptance #2

REQ-3 — Ground login guidance in the effective environment
  IF Claude Code reports unauthenticated in the credential-capable execution environment THEN the review shall stop with that diagnosis; a sandbox-only unauthenticated result shall not trigger login guidance → Acceptance #3

## Design decision
agent-decided — Codex-to-Claude review must invoke the existing runner outside the Codex sandbox with narrowly scoped host authorization; the skill cannot and shall not bypass the host's approval boundary itself.

agent-decided — Make the credential-capable runner invocation the standard path, not an additional authentication preflight, because a separate probe would add another external call and can disagree with the actual review environment.

agent-decided — Leave Claude Code and non-Codex hosts unchanged because the observed mismatch is specific to Codex sandbox credential visibility.

## Alternatives considered
- Ask the user to log in whenever sandboxed `claude auth status` is false — rejected because the same machine was demonstrably authenticated outside the sandbox.
- Add an authentication preflight before every review — rejected because it adds ceremony and a second environment-sensitive result instead of fixing the actual invocation boundary.
- Copy credentials into the sandbox — rejected because it expands secret handling and bypasses the host's authorization model.

## Current state evidence
- Forward: `loom-code/skills/review/SKILL.md:33` starts the Codex-to-Claude second-reader path.
- Reverse: `loom-code/skills/review/SKILL.md:37` directs the host to the single-attempt runner.
- Error: `loom-code/skills/review/SKILL.md:40` defines runner outcomes but not the credential visibility required by the host execution boundary.
- Data: `loom-code/scripts/claude_reviewer.py:19` defines the observable attempt result without storing credentials.
- Boundary: `loom-code/scripts/claude_reviewer.py:77` owns one subprocess attempt and explicitly does not own retry or authentication.

## UI flows
已登入 Claude Code，並在 Codex 選擇它作為第二讀者 → Codex 使用可讀取既有登入的受控執行環境完成 review，不要求再次登入。

該受控執行環境仍回報未登入 → review 停止並顯示登入診斷，使用者處理登入後才能繼續。

Claude review 回傳空輸出或逾時 → 沿用既有診斷與最多一次重試，不因執行環境調整而增加呼叫次數。
