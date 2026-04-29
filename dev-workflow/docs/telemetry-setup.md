# Skill Telemetry Setup

How to wire optional **opt-in, per-user** telemetry for dev-workflow
skill invocations.

This document is the operational counterpart to
`scripts/skill-telemetry.py`. Telemetry data lives **on each user's
local machine**; nothing is committed to the repo, and there is no
server-side aggregation in this scaffold.

---

## Why telemetry

Per the skill-evolution architecture (Layer 0 — Foundation):

- **Identify which skills are actually used** — invocation
  frequency informs which skills to prioritize for refactor /
  tasting / retirement
- **Detect failure patterns** — frequent errors or re-runs on a
  skill signal it needs improvement
- **Inform quarterly audits** — see
  `dev-workflow/docs/quarterly-audit-runbook.md` step 2 (skill
  lifecycle state review) and step 5 (validation gate status)

Without telemetry, all of these become "ask the user" or "guess
from git activity". Telemetry makes them data-driven.

---

## Privacy stance

The telemetry script is designed to minimize data sensitivity:

1. **Local-only by default** — log lives at `~/.claude/skill-telemetry.jsonl`;
   never auto-uploaded; never auto-shared
2. **Prompt content is hashed, not stored** — `prompt_hash` (sha256)
   preserves "is this the same prompt as before" without storing
   text. PII never leaves the user's machine in raw form.
3. **`prompt_summary` is opt-in** — only set if the user explicitly
   provides a non-sensitive summary
4. **Sanitized export** — when sharing logs (e.g., for cross-user
   research), use `skill-telemetry.py export --strip-*` to redact
   user-id / notes / prompt summary

The intended threat model: a single user wants per-skill usage
analytics for their own decisions. The script does not assume any
multi-user federation; that's out-of-scope.

---

## Setup for Claude Code

Claude Code supports user hooks via `settings.json`. Hooks fire on
skill invocation events. To wire telemetry:

### Option A: Manual logging (no hook needed)

Skip hooks entirely; log events from your terminal manually after
notable sessions:

```bash
python3 scripts/skill-telemetry.py log \
    --skill complexity-critique \
    --plugin dev-workflow \
    --event-type skill_invoke \
    --user-reaction accept \
    --notes "Used to gate the auth-redesign refactor proposal"
```

This is the simplest setup — useful for spot-tracking specific
skills you care about, without taking on hook configuration.

### Option B: Hook-driven (more comprehensive but env-dependent)

Configure your `~/.claude/settings.json` to call the telemetry
script on relevant events. The exact hook event names depend on
your Claude Code version's hook API.

A representative configuration shape (verify against your CC
version's hook reference):

```json
{
  "hooks": {
    "post-skill-invocation": {
      "command": "python3 /path/to/monkey-skills/scripts/skill-telemetry.py log",
      "args": [
        "--skill", "${SKILL_NAME}",
        "--plugin", "${PLUGIN_NAME}",
        "--event-type", "skill_invoke"
      ]
    }
  }
}
```

The hook should pass available context as flags. If your Claude
Code version exposes a different hook API (e.g., env vars vs args,
or different event names), adapt accordingly.

**This script does NOT auto-detect your Claude Code hook API.**
Hook integration is environment-dependent and the script is
intentionally agnostic.

---

## Running summaries

Periodically (or as part of quarterly audit step 2):

```bash
# Per-skill usage summary
python3 scripts/skill-telemetry.py summarize

# Filter to a single skill
python3 scripts/skill-telemetry.py summarize --skill skill-refactor
```

Output is JSON suitable for piping to `jq` or further analysis.

Example summary structure:

```json
{
  "log_path": "~/.claude/skill-telemetry.jsonl",
  "filter_skill": null,
  "total_entries": 142,
  "by_skill": {
    "complexity-critique": {"invokes": 23, "completes": 22, "errors": 1, "rerun": 3},
    "skill-refactor": {"invokes": 8, "completes": 7, "errors": 1, "rerun": 0},
    ...
  }
}
```

`rerun` count is a useful regret signal — if a skill has high
re-run rate, something about its first-pass output is unsatisfying.

---

## Sanitized export

If you ever need to share aggregate telemetry (research project,
team sync, debugging session):

```bash
python3 scripts/skill-telemetry.py export \
    --out /tmp/sanitized.jsonl \
    --strip-prompt-summary \
    --strip-user-id \
    --strip-notes
```

This produces a copy with sensitive fields removed. Review before
sharing.

---

## What this scaffold does NOT do

- **Auto-aggregate across users** — not implemented; intentionally
  out-of-scope until a real federation use case emerges
- **Real-time anomaly detection** — local script; no streaming /
  alerting
- **Cross-skill correlation** ("after invoking X, what did the
  user invoke next?") — a known H4-future feature; current
  schema supports it via timestamps but no analyzer is built yet
- **Hook event translation** — the script accepts CLI flags, not
  raw hook event JSON; hook integration requires per-environment
  glue

These gaps are deliberate. PR-5 ships the foundation; the user
chooses what to build on top.

---

## Telemetry → quarterly audit

The audit runbook step 2 (skill lifecycle state review) consumes
telemetry summaries:

```bash
# Identify skills with low invocation count over the last quarter
python3 scripts/skill-telemetry.py summarize | jq '.by_skill | to_entries[] | select(.value.invokes < 5) | .key'
```

Skills with persistent low usage become candidates for
**Deprecated** state (per `skill-governance.md` Skill Lifecycle
States). Skills with high re-run / error rates become candidates
for **Refactor** or **Tasting** intervention.

Without telemetry, this analysis is impossible; the audit
defaults to "everything is Active because no one's complained".
With telemetry, the audit becomes evidence-based.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `summarize` reports 0 entries | Hook not firing OR log path mismatch | Verify settings.json hook references the same log path used by `summarize` |
| `prompt_hash` empty | `--prompt` not passed | Add `--prompt "${USER_PROMPT}"` to hook config |
| Log file grows quickly | Many skill invocations | Periodic archival: `mv ~/.claude/skill-telemetry.jsonl ~/.claude/skill-telemetry.YYYYMM.jsonl` |
| Script import error | Python version | Requires Python 3.9+ for type hints; standard library only |
| Want to disable telemetry temporarily | (no in-script flag) | Comment out hook config in settings.json |

---

## Schema versioning

The current schema is `schema_version: 1`. If schema changes:

1. Increment `SCHEMA_VERSION` in script
2. Document change in this file's history
3. Old entries with `schema_version: 1` remain readable; analyses
   should handle mixed-version logs

No automated migration is provided — schema is forward-compatible
by design (new fields are optional).
