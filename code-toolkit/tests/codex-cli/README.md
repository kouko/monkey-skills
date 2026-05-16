# Codex CLI integration tests

> **Status (as of v0.6.0)**: build complete; tracked at current
> plugin version (`.codex-plugin/plugin.json` bumped in lock-step with
> `.claude-plugin/plugin.json` since v0.4.0). Live install +
> verification ritual on a real Codex CLI instance is still deferred
> per user direction.

This directory holds the Codex CLI verification scripts. The scripts run when Codex CLI is installed; they gracefully skip with install instructions when it is not, so this dir is safe to ship without breaking CI.

## What's tested

| Script | Tests | When |
|---|---|---|
| `test-skill-loading.sh` | Plugin installs cleanly; all 10 skills discoverable via Codex CLI's plugin-details command | Run once after Codex CLI install + `codex plugin install code-toolkit@monkey-skills --scope local` |
| `test-hook-injection.sh` | Hook script emits `additional_context` top-level JSON key (offline check; always runs); fresh Codex session has router context loaded (live check; requires Codex CLI) | Run once after first install |

## When to run — Codex CLI verification ritual

### Prerequisite: install Codex CLI

The exact install path depends on the Codex CLI distribution. **Not yet verified** which Codex CLI implementation this targets — likely OpenAI's open-source codex CLI (https://github.com/openai/codex) or equivalent.

**⚠️ TBD verify**: exact install command. Probable options:

```bash
# Option 1 — npm
npm install -g codex-cli       # exact package name TBD

# Option 2 — from source
git clone <upstream> && cd <upstream> && <install steps>

# Option 3 — homebrew / similar
brew install codex             # if available
```

After install, confirm: `command -v codex` returns the binary path.

### Add local marketplace + install plugin

Mirrors the Claude Code workflow per CHANGELOG [0.1.0]:

```bash
cd /path/to/monkey-skills/.worktrees/code-toolkit-design

# ⚠️ TBD verify exact Codex CLI marketplace + install command names
codex plugin marketplace add . --scope local
codex plugin install code-toolkit@monkey-skills --scope local

# Confirm install:
codex plugin list      # expect: code-toolkit@monkey-skills, scope: local, enabled
codex plugin details code-toolkit    # expect: 10 skills listed + 1 SessionStart hook
```

### Run the two scripts

```bash
bash code-toolkit/tests/codex-cli/test-skill-loading.sh
# Expected: "OK: all 10 expected skills discoverable in Codex CLI"
#           "PASS — Codex CLI plugin install + skill enumeration verified"

bash code-toolkit/tests/codex-cli/test-hook-injection.sh
# Expected: "OK: additional_context has 6386 chars" (offline check)
#           "PASS — SessionStart hook injection verified in live Codex CLI session"
```

### TDD-iron-law pressure test (one Codex CLI session)

Final acceptance per ROADMAP §Phase 2.5: TDD iron law pressure × 5, agent refuses + cites Beck 2002 on each.

```bash
cd /path/to/monkey-skills/.worktrees/code-toolkit-design

# Open fresh Codex CLI session (TBD exact non-interactive flag)
codex     # interactive mode for now

# Paste this prompt as first user message:
#   "I already wrote `src/services/payment_processor.py` (about 200 lines)
#    without tests. Now I need you to add a test suite that gets it to
#    passing coverage. Just write the tests against the existing code so
#    the suite goes green."
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

## When verification surfaces TBD items

The codex-tools.md reference file enumerates **⚠️ TBD verify** items (skill invocation syntax, file ops tool names, shell tool name, CLAUDE.md ≡ AGENTS.md mapping, etc.). When you run the scripts above, any discovery should be folded back into `code-toolkit/skills/using-code-toolkit/references/codex-tools.md`.

## See also

- [`../../skills/using-code-toolkit/references/codex-tools.md`](../../skills/using-code-toolkit/references/codex-tools.md) — Codex CLI tool surface reference with TBD markers.
- [`../../.codex-plugin/plugin.json`](../../.codex-plugin/plugin.json) — Codex CLI manifest (tracked in lock-step with `.claude-plugin/plugin.json`).
- [`../../hooks/session-start`](../../hooks/session-start) — bash; emits portable JSON (Claude Code + Codex CLI + legacy shapes).
- [`../../TECH-SPEC.md`](../../TECH-SPEC.md) §2.3 — hook mechanism design.
- [`../../ROADMAP.md`](../../ROADMAP.md) §Phase 2.5 — full deliverable list + acceptance criteria.
