# Fix command substitution and upgrade guidance — plan
intent: 2026-09-09-fix-command-substitution-and-upgrade-docs@3087c3f74
charter: 1.0

## Current State Evidence
- Forward: `_shell_segments` exposes backtick content but marks `$()` dynamic without exposing its enclosed command.
- Reverse: all push and PR classifiers consume `_shell_segments`, so one correction covers every publication action.
- Error: no-operator `$()` publishers remain hidden; the existing dynamic test passes only because it contains a pipe.
- Data: the hook receives one opaque shell command; quote state determines whether substitution syntax executes or stays literal.
- Boundary: three Loom READMEs own Codex update guidance; Claude Code dogfood records observed host behavior as evidence only.

## Task DAG

### Wave 1 — reproduce and correct

**W1-01 Dogfood Claude Code hook classification**  after: none  acceptance: 4
- Files: docs/loom/2026-09-09-fix-command-substitution-and-upgrade-docs/evidence/claude-hook-dogfood.md
- Test: A4 positive: harmless quoted publisher text runs; negative: any denial is attributed to its actual hook or permission source.
- Risk: agent-decided — use read-only commands only; record observations without treating installed 2.0.4 as candidate code.

**W1-02 Expose `$()` substitution content**  after: W1-01  acceptance: 1, 2, 4
- Files: loom-code/scripts/test_publish_command_detection.py, loom-code/scripts/loom_checker.py
- Test: A1 positive: no-operator publishers; negative: harmless substitution. A2 positive: literal searches pass; boundary: single quotes. A4 positive: reproduced defects gain tests; negative: unobserved cases do not.
- Risk: agent-decided — RED first; change only the existing conservative segmentation path and preserve fail-closed malformed input.

**W1-03 Correct installation guidance**  after: none  acceptance: 3
- Files: loom-code/README.md, loom-code/README.ja.md, loom-code/README.zh-TW.md
- Test: A3 positive: all languages require immediate restart; negative: none claims add preserves an active version path.
- Risk: agent-decided — describe the observed replacement behavior without promising undocumented host internals.

### Wave 2 — release integration

**W2-01 Release the maintenance correction**  after: W1-02, W1-03  acceptance: 1, 2, 3, 4
- Files: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Test: A1 positive: publishers caught; negative: harmless text. A2 positive: literals pass; boundary: malformed input. A3 positive: restart text; negative: no preservation claim. A4 positive: evidence exists; negative: no unattributed denial.
- Risk: agent-decided — patch release only; use the existing manifest synchronization command.

## Questions asked
1 — what — 那就照你的意見，先修 `loom-code` 那三項吧。
1 — what — 了解，請繼續實作。

## Risks
1. Substitution parsing is security-sensitive; literal data must remain allowed while executable content remains fail-closed.
2. Claude Code may deny a command through its own permission layer; evidence must not misattribute that denial to Loom.
