# Codex Claude reviewer credential boundary — spec
intent: 2026-09-10-codex-claude-reviewer-outside-sandbox@9ca1435d3a3bee7c8ba9324ffe0a400e8b10723f
confirmed-behavior: 2026-09-10 @fa61807
pre-build-review: required — changes the cross-system execution and authorization contract between Codex and Claude Code

## Requirements
REQ-1 — Reuse an existing Claude login
  WHEN an already-authenticated user selects Claude Code as a second reader on Codex, the review shall run in an execution environment that can access that existing authentication without asking the user to log in again → Acceptance #1

REQ-2 — Preserve the bounded reviewer contract
  WHEN Claude Code is selected as the second reader on Codex, Codex shall invoke the installed plugin's existing single-attempt `claude_reviewer.py` with the host's outside-sandbox execution permission and a reusable approval prefix scoped to that runner command; it shall not fall back to sandboxed Claude, add a preflight or runner-level retry, or copy credentials → Acceptance #2

REQ-3 — Ground login guidance in the effective environment
  IF Claude Code reports unauthenticated in the credential-capable execution environment THEN the review shall stop with that diagnosis; a sandbox-only unauthenticated result shall not trigger login guidance → Acceptance #3

## Design decision
agent-decided — Standardize the exact path proven during PR #818: Codex invokes the installed `claude_reviewer.py` with outside-sandbox execution permission and a reusable approval prefix scoped to that runner command. In the observed incident, sandboxed `claude auth status` reported logged out while the same command outside the sandbox reported logged in and the reviewer completed successfully.

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
Selects Claude Code as the second reader in Codex → Codex uses the same outside-sandbox runner invocation proven to see the existing Claude login during PR #818.

Approves the narrowly scoped host authorization while already logged in to Claude Code → Codex runs the reviewer outside its sandbox and completes the review without asking for another login.

The host denies or cannot provide outside-sandbox execution → Review stops with an authorization blocker; Codex does not fall back to sandboxed Claude or issue login guidance.

The outside-sandbox runner still reports unauthenticated → Review stops with the Claude login diagnosis; the user can authenticate before trying again.

The Claude review returns empty output or times out → Review preserves the existing diagnostics and at most one retry without adding another invocation policy.
