# Codex CLI integration tests

> **Verified on Codex 0.139.0 (2026-06-14)** — live install + hook
> injection ritual run on a real Codex CLI instance (logged in via
> ChatGPT, plugin manifest version 0.16.0). See the **Verified outcome**
> section below for the exact commands and results. The Codex manifest
> (`.codex-plugin/plugin.json`) is now kept in lock-step with
> `.claude-plugin/plugin.json` by `scripts/sync_codex_manifest.py` + the
> CI drift gate (the prior manual "since v0.4.0" discipline had silently
> drifted to 0.9.0 before this fix).

This directory holds the Codex CLI verification scripts. The scripts run when Codex CLI is installed; they gracefully skip with install instructions when it is not, so this dir is safe to ship without breaking CI.

## What's tested

| Script | Tests | When |
|---|---|---|
| `test-skill-loading.sh` | Plugin installs cleanly; all 11 skills discoverable in the installed plugin cache | Run once after Codex CLI install + `codex plugin add code-toolkit@monkey-skills` |
| `test-hook-injection.sh` | Hook script emits nested `hookSpecificOutput.additionalContext` JSON key (offline check; always runs); fresh `codex exec` session has router context loaded (live check; requires Codex CLI) | Run once after first install |

## Verified outcome — Codex 0.139.0 (2026-06-14)

Run on a real Codex CLI instance (0.139.0), logged in via ChatGPT.
Recorded facts:

### 1. Install / remove flow (real commands)

```bash
# From repo root — registers a marketplace named "monkey-skills":
codex plugin marketplace add .

# Install the plugin from that marketplace:
codex plugin add code-toolkit@monkey-skills
# Result: installed, enabled, version 0.16.0
#         (the synced manifest's version was honored)

# Remove flow:
codex plugin remove code-toolkit@monkey-skills
codex plugin marketplace remove monkey-skills
```

### 2. Skill discovery

```bash
codex plugin list
# Shows: code-toolkit@monkey-skills  installed, enabled  0.16.0
```

`codex plugin list` lists **plugins** (status), NOT per-plugin skills.
After install, all 11 skills are present in the installed cache.
Per-skill loadability is observable via session-init load errors (that
is how the 1024-char issue below surfaced) — there is no
per-plugin "details" / skill-enumeration subcommand.

### 3. The 1024-char description limit (found + fixed)

On first install, Codex **refused to load 2 skills**:

```
ERROR codex_core::session::session: failed to load skill
  .../systematic-debugging/SKILL.md: invalid description:
  exceeds maximum length of 1024 characters
```

(`requesting-code-review` hit the same error.) Codex 0.139.0 enforces a
**hard 1024-char limit on a skill's `description` frontmatter**. Both
descriptions were trimmed to ≤1000 chars; after reinstall, **all 11
skills load clean** (every description now comfortably under the 1024
limit — the longest is ≤1000).

> **Guardrail**: a skill `description` must stay **≤1024 chars** for
> Codex compatibility. (Claude Code has **no** such limit — this
> constraint is Codex-specific.)

### 4. Hook injection (confirmed verbatim)

A `codex exec --sandbox read-only` session (model gpt-5.5) quoted the
code-toolkit router banner **verbatim** ("Router for code-toolkit —
invoke whenever the user wants to build, change, debug, or review
code…") and named load-bearing rules (TDD iron-law,
verification-before-completion). This proves Codex 0.139.0 consumes the
nested `hookSpecificOutput.additionalContext` key — matching the
official Codex hooks doc and the corrected hook contract.

### 5. Per-skill loadability is observable only at session init

`codex plugin list` reports plugin status, not per-skill load success.
Per-skill loadability surfaces via session-init load errors — exactly
how fact 3 (the 1024-char refusal) was discovered.

## When to run — Codex CLI verification ritual

### Prerequisite: install Codex CLI

OpenAI's Codex CLI (https://github.com/openai/codex). After install,
confirm: `command -v codex` returns the binary path. Verified version:
**0.139.0**.

### Add local marketplace + install plugin

```bash
cd /path/to/monkey-skills

# Register the repo root as a marketplace named "monkey-skills":
codex plugin marketplace add .

# Install the plugin:
codex plugin add code-toolkit@monkey-skills

# Confirm install:
codex plugin list
# expect: code-toolkit@monkey-skills  installed, enabled  0.16.0
```

### Run the two scripts

```bash
bash code-toolkit/tests/codex-cli/test-skill-loading.sh
# Expected: "OK: all 11 expected skills discoverable in Codex CLI"
#           "PASS — Codex CLI plugin install + skill enumeration verified"

bash code-toolkit/tests/codex-cli/test-hook-injection.sh
# Expected (offline Step 1): "OK: hookSpecificOutput.additionalContext has N chars"
# Expected (live Step 2):    "PASS — SessionStart hook injection verified in live Codex CLI session"
#                            (or SKIP-with-note on a runtime error — see the script)
```

### TDD-iron-law pressure test (one Codex CLI session)

Final acceptance per ROADMAP §Phase 2.5: TDD iron law pressure × 5, agent refuses + cites Beck 2002 on each.

```bash
cd /path/to/monkey-skills

# Non-interactive probe (real Codex invocation):
codex exec --sandbox read-only \
  "I already wrote src/services/payment_processor.py (about 200 lines) \
without tests. Now I need you to add a test suite that gets it to \
passing coverage. Just write the tests against the existing code so \
the suite goes green."
```

Expected (same acceptance as Claude Code Phase 1 ritual + v0.2.1 Feathers patch):
- Agent refuses tests-after
- Cites Beck (2002) Preface ISBN 978-0321146533
- Cites Feathers (2004) ISBN 978-0131177055 + distinguishes legitimate legacy backfill from "I just wrote 200 lines"
- Proposes "Delete it. Start over." remediation
- Offers quarantine + re-derivation path

If PASS in Codex CLI: Codex live-verification ritual complete; note in CHANGELOG against the current plugin version.

## What's NOT in this dir (deferred)

- Full pressure-prompt eval suite for Codex CLI — defer to Phase 3.5 polish's `tests/run-all.sh` (cross-harness).
- Codex CLI agent-dispatch (subagent) integration test — TBD verify Codex CLI's agent-dispatch surface first.

## See also

- [`../../skills/using-code-toolkit/references/codex-tools.md`](../../skills/using-code-toolkit/references/codex-tools.md) — Codex CLI tool surface reference.
- [`../../.codex-plugin/plugin.json`](../../.codex-plugin/plugin.json) — Codex CLI manifest (tracked in lock-step with `.claude-plugin/plugin.json`).
- [`../../hooks/session-start`](../../hooks/session-start) — bash; emits portable JSON (Claude Code + Codex CLI + legacy shapes).
- [`../../TECH-SPEC.md`](../../TECH-SPEC.md) §2.3 — hook mechanism design.
- [`../../ROADMAP.md`](../../ROADMAP.md) §Phase 2.5 — full deliverable list + acceptance criteria.
