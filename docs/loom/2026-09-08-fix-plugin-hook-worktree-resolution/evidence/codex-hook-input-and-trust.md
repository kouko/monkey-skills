# Codex hook input and trust observation

Observed locally on 2026-09-08 with Codex CLI 0.153.4 and the installed
`loom-code` 2.0.2 hook. The capture used a harmless `pwd` Bash call whose
executor `workdir` was the feature worktree while the task root was the main
checkout. The installed checker was instrumented for this one call, the raw
payload was written only to `/tmp`, and the checker was restored byte-for-byte
before the payload was inspected. The command text and identifiers are omitted
from this committed record.

## PreToolUse payload shape

```json
{
  "cwd": "<main-checkout>",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "<redacted>"
  }
}
```

Top-level keys additionally included model, permission mode, session, turn,
transcript, tool-use identifiers. `tool_input` contained exactly one key,
`command`; neither `tool_input.workdir` nor `tool_input.cwd` existed. Therefore
an installed hook cannot recover the executor-selected worktree from this
payload. A publication command must carry its repository selection in command
bytes if it differs from top-level `cwd`.

## Trust identity shape

The local Codex config names installed plugin hooks independently of a
repository path, for example:

```text
loom-code@monkey-skills:hooks/hooks.json:pre_tool_use:0:0
```

Repository-local hooks are instead keyed by the absolute configuration path,
for example:

```text
<repo-root>/.codex/hooks.json:post_tool_use:0:0
<repo-root>/.codex/hooks.json:post_tool_use:0:1
```

The absolute paths above are privacy-normalized; their key shape and indices
are unchanged. Each entry carries a `trusted_hash`; Codex 0.153.4's local hook UI labels a new
hook and a definition modified since its trusted hash as requiring review.
Consequently, creating a worktree does not create another installed Loom hook
identity, while a repository-local hook under a different absolute worktree
path is a distinct host trust identity. This repository's two local
PostToolUse hooks are not Loom publication hooks.
