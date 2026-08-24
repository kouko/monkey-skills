# Cross-host review-gate live-host run

status: PASS
candidate root: [CANDIDATE_PLUGIN]
consumer SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
cli versions: Claude Code=2.1.241 (Claude Code); Codex=codex-cli 0.149.0
authentication: caller-supplied private Codex file is copied only into disposable CODEX_HOME; the explicitly authorized disposable Claude sandbox is used directly and never deleted.
pre/post user state: unchanged
Claude sandbox metadata: CHANGED (authorized disposable sandbox)
finally cleanup: PASS

## Cases
### claude / valid-code
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: CODE
CODE_STATION_PACKET: [CANDIDATE_PLUGIN] ea8af1ae459a99a7511ac3f810c083acaabd78b6
```
### claude / valid-docs
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: DOCS
DOCS_STATION_PACKET: [CANDIDATE_PLUGIN] ea8af1ae459a99a7511ac3f810c083acaabd78b6
```
### claude / valid-mixed
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: MIXED
MIXED_STATION_PACKET: [CANDIDATE_PLUGIN] ea8af1ae459a99a7511ac3f810c083acaabd78b6
```
### claude / valid-sdd
command: claude session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: SDD
SDD_STATION_PACKET: [CANDIDATE_PLUGIN] ea8af1ae459a99a7511ac3f810c083acaabd78b6
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
REVIEWED_SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: CODE
CODE_STATION_PACKET: [CANDIDATE_PLUGIN] ea8af1ae459a99a7511ac3f810c083acaabd78b6
```
### codex / valid-docs
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: DOCS
DOCS_STATION_PACKET: [CANDIDATE_PLUGIN] ea8af1ae459a99a7511ac3f810c083acaabd78b6
```
### codex / valid-mixed
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: MIXED
MIXED_STATION_PACKET: [CANDIDATE_PLUGIN] ea8af1ae459a99a7511ac3f810c083acaabd78b6
```
### codex / valid-sdd
command: codex session invocation [REDACTED_ARGUMENTS]
exit: 0
output:
```text
CANDIDATE_ROOT: [CANDIDATE_PLUGIN]
REVIEWED_SHA: ea8af1ae459a99a7511ac3f810c083acaabd78b6
PACKET_SOURCE: scripts/review_context.py
HOST_SKILL_INVOKED: SDD
SDD_STATION_PACKET: [CANDIDATE_PLUGIN] ea8af1ae459a99a7511ac3f810c083acaabd78b6
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
