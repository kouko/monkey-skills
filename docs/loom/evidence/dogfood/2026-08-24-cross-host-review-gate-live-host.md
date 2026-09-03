# Cross-host review-gate live-host run

status: PASS
candidate root: [CANDIDATE_PLUGIN]
consumer SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
cli versions: Claude Code=2.1.241 (Claude Code); Codex=codex-cli 0.149.0
authentication: caller-supplied private Codex file is copied only into disposable CODEX_HOME; Claude uses only the named ~/.claude-test profile.
protected daily state: unchanged
Claude test-profile metadata: CHANGED (expected dedicated profile)
finally cleanup: PASS

## Cases
### claude / valid-code
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: CODE
CODE_STATION_PACKET: [CANDIDATE_PLUGIN] f4f341140825049ec5ecf78520c4098b6295fc6b
```
### claude / valid-docs
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: DOCS
DOCS_STATION_PACKET: [CANDIDATE_PLUGIN] f4f341140825049ec5ecf78520c4098b6295fc6b
```
### claude / valid-mixed
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: MIXED
MIXED_STATION_PACKET: [CANDIDATE_PLUGIN] f4f341140825049ec5ecf78520c4098b6295fc6b
```
### claude / valid-sdd
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: SDD
SDD_STATION_PACKET: [CANDIDATE_PLUGIN] f4f341140825049ec5ecf78520c4098b6295fc6b
```
### claude / invalid-reference
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
REFUSE: recorded
```
### claude / unchanged-post-fix
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
REFUSE: recorded
```
### codex / valid-code
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: CODE
CODE_STATION_PACKET: [CANDIDATE_PLUGIN] f4f341140825049ec5ecf78520c4098b6295fc6b
```
### codex / valid-docs
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: DOCS
DOCS_STATION_PACKET: [CANDIDATE_PLUGIN] f4f341140825049ec5ecf78520c4098b6295fc6b
```
### codex / valid-mixed
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: MIXED
MIXED_STATION_PACKET: [CANDIDATE_PLUGIN] f4f341140825049ec5ecf78520c4098b6295fc6b
```
### codex / valid-sdd
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: f4f341140825049ec5ecf78520c4098b6295fc6b
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: SDD
SDD_STATION_PACKET: [CANDIDATE_PLUGIN] f4f341140825049ec5ecf78520c4098b6295fc6b
```
### codex / invalid-reference
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
REFUSE: recorded
```
### codex / unchanged-post-fix
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
REFUSE: recorded
```
