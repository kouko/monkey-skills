# distill-sessions runtime protocol

Read this reference only when dispatching trajectory or advisory subagents,
converting their outputs, changing threshold configuration, or diagnosing
runtime/folder failures. The entrypoint remains the authority for approval,
privacy, required artifacts, stop conditions, and final verification.

## Step 2 dispatch

Read `top.json`, then fan out one subagent for every
`subagent_payload[]` entry. Select
`agents/prompt-failure-analysis.md` or
`agents/prompt-success-analysis.md` from the payload `kind`; pass the
observable session events and current target SKILL.md. Sibling dispatches are
independent because they read disjoint trajectories.

Claude Code uses the dispatch alias `model: "sonnet"`; its tool rejects the
literal `claude-sonnet-4-6`. Codex has no equivalent per-call Claude alias, so
use the model option supported by the Codex agent tool. The literal stored in
`scripts/main.py` documents the intended model generation; host call syntax is
not portable.

Each analysis prompt defines strict markdown:

```markdown
# Failure Memory Item 1
## Title
...
## Description
...
## Content
...
```

Success analysis uses `# Success Memory Item <i>`. Preserve returned markdown
until collection; do not request raw JSON from the subagent.

## Mechanical collection schema

Convert each Memory Item block to one JSON entry. The source of truth is
`scripts/propose.py:32-49` plus
`scripts/fixture_subagent_results.json`:

```json
[
  {
    "session_id": "<subagent_payload session>",
    "target_skill_path": "<subagent_payload target>",
    "memory_items": [
      {
        "title": "...",
        "description": "...",
        "content": "...",
        "kind": "failure",
        "section_anchor": "When to use",
        "requires_new_reference_file": false
      }
    ]
  }
]
```

Map `## Title`, `## Description`, and `## Content` directly. Set `kind`
from the prompt dispatched. `section_anchor` is required, non-blank, and must
name a real heading in the target SKILL.md. Never restore the retired silent
`Examples` default. `requires_new_reference_file` is optional and false by
default; true items remain deferred rather than being applied.

`propose.py` clusters by normalized title plus anchor before rendering. N≥2
session support is promoted; N=1 remains in the pending bucket. An anchor that
does not match stays in the mismatch bucket with valid headings listed.

## Advisory report dispatch

1. Read `agents/prompt-advisory-analyst.md` completely.
2. Run `report.py --input <merged.json> --lang <zh-TW|en|ja>` and read stdout
   JSON.
3. Dispatch one current-Sonnet subagent with the prompt body and
   `dispatch_payload.input` (`merged_data`, `lang`, `date_str`).
4. Write the returned markdown verbatim to `output_path`; the response is the
   entire file.

The report is cross-target and independent from `propose.py` → `apply.py`.
Its prose language follows `--lang`; identifiers, source snippets, and code
remain in their source language. The analyst performs semantic clustering;
there is no heuristic fallback. Historical token-based clustering incorrectly
merged unrelated items through generic shared tokens, which is why LLM
judgment is retained here.

## Configuration meanings

The partial JSON config overrides these defaults:

| Key | Default | Meaning |
| --- | ---: | --- |
| `interrupt_window_sec` | 600 | User interruption within this many seconds of brainstorming/planning contributes an interrupt signal. |
| `needs_revision_threshold` | 2 | Consecutive review rejections needed for a streak. |
| `redispatch_threshold` | 2 | Implementer re-dispatches on one task needed for concentration. |
| `tool_error_proximity_events` | 10 | Event window used to classify a tool-error cluster. |
| `min_session_count` | 3 | Qualifying sessions needed before a skill ranks. |
| `cross_project_count` | 2 | Distinct projects needed for the confidence bump. |

Override only the keys needed. These defaults were derived from the original
v0.1 mining demo; changing them changes signal sensitivity, not privacy or
approval policy.

## History relevant to operations

- Minimal Stage 4 clustering shipped after single-session suggestions proved
  too weak for automatic promotion. Full SDD consolidation remains deferred.
- The per-trajectory model moved from Haiku to Sonnet for analysis quality.
  The observed maximum trajectory was 559K tokens (56% of the 1M window);
  this is evidence, not permission to omit the runtime estimate.
- Claude facet availability depends on local retention and interactive
  `/insights`; Codex events normally have no matching facet.
- Future engines and instruction-file write-back are outside the current
  implementation. Do not simulate those paths.

## Runtime cleanup

Always disable bytecode for tests:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  loom-workflow/skills/distill-sessions/scripts/ -v
```

If bytecode directories already exist, remove files first and then empty
directories:

```bash
find loom-workflow/skills/distill-sessions -type d -name __pycache__ \
  -print | xargs -I {} find {} -type f -delete
find loom-workflow/skills/distill-sessions -type d -name __pycache__ \
  -empty -delete
```

Avoid recursive deletion and inline `shutil.rmtree` shortcuts; repository
safety hooks intentionally block destructive command patterns.
