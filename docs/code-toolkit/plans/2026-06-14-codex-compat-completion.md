# Plan: Complete + verify code-toolkit's Codex CLI compatibility

Source brief: docs/code-toolkit/specs/2026-06-14-codex-compat-completion.md
Total tasks: 8 (width uncapped; 3 parallel roots)
Critical-path depth: 4 (≤5) — longest chain T1 → T2 → T7 → T8
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-14, 14/14) — post-PASS amendments below are additive/schema-safe (Independent flags + dep-syntax clarity), re-review skipped per writing-plans amend rule.

> Ground-truth basis: the official Codex hooks contract
> (developers.openai.com/codex/hooks, fetched 2026-06-14) confirms Codex
> consumes `hookSpecificOutput.additionalContext` (same key as Claude Code) from a
> plugin-bundled `hooks/hooks.json`; the real plugin command surface
> (`codex plugin add` / `list` / `marketplace add`) was probed live on the
> installed Codex 0.139.0. Fixes T1–T6 are driven by these facts; T7 is the
> end-to-end live proof that would catch any doc-vs-0.139.0 lag.

## Task 1 — Manifest sync script + drift-check
- Description: Create `sync_codex_manifest.py` that derives `.codex-plugin/plugin.json`'s shared fields from `.claude-plugin/plugin.json` (name, version, description, author, homepage, repository, license, keywords) while **preserving** the Codex-only `interface` block. Add a `--check` mode that exits non-zero on divergence (the CI gate uses it). Write a pytest alongside.
- Module: code-toolkit/scripts
- Files touched: code-toolkit/scripts/sync_codex_manifest.py, code-toolkit/scripts/test_sync_codex_manifest.py
- Context paths:
  - code-toolkit/.claude-plugin/plugin.json
  - code-toolkit/.codex-plugin/plugin.json
  - code-toolkit/scripts/ (existing test layout / conventions)
- Acceptance:
  - RED: `pytest code-toolkit/scripts/test_sync_codex_manifest.py` fails — script absent; test asserts (a) shared fields copied, (b) `interface` block preserved verbatim, (c) `--check` returns non-zero when manifests diverge and zero when synced.
  - GREEN: test passes; running the script with no flag rewrites `.codex-plugin` shared fields; `--check` is a pure read.
  - Command surface: the `sync_codex_manifest.py` verb (sync + `--check`) is declared in code-toolkit's command surface (AGENTS.md commands / Makefile / scripts README) and verified to run.
- External surfaces: none (stdlib `json` only; string equality for version — no `packaging`).
- Dependencies: none
- Independent: true
- Brief item covered: "Re-sync `.codex-plugin/plugin.json` ... via a sync script, with a CI drift-gate" (Smallest End State #2).

## Task 2 — Apply sync: clear the 0.9.0 → 0.16.0 drift
- Description: Run `sync_codex_manifest.py` to update the committed `.codex-plugin/plugin.json` (version 0.9.0 → 0.16.0; add missing keywords `brainstorming / clean-code / solid / owasp-asvs / session-start-hook / superpowers-parity`), leaving the `interface` block untouched.
- Module: code-toolkit/.codex-plugin
- Files touched: code-toolkit/.codex-plugin/plugin.json
- Context paths:
  - code-toolkit/scripts/sync_codex_manifest.py
- Acceptance:
  - RED: `python code-toolkit/scripts/sync_codex_manifest.py --check` exits non-zero (manifest at 0.9.0, short keywords).
  - GREEN: after running the sync, `--check` exits zero; `.codex-plugin/plugin.json` version == 0.16.0, keywords match `.claude-plugin`, `interface` block byte-identical to before.
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Re-sync `.codex-plugin/plugin.json` (0.9.0 → 0.16.0 + missing keywords)" (Smallest End State #2).

## Task 3 — CI drift-gate for the manifest
- Description: Add a CI step that runs `sync_codex_manifest.py --check` so a future manual edit that diverges the two manifests fails the build. Mirror the repo's existing drift-check pattern.
- Module: .github/workflows
- Files touched: (the code-toolkit CI workflow file under .github/workflows/ — implementer Reads the dir to find the right one)
- Context paths:
  - .github/workflows/
  - code-toolkit/scripts/sync_codex_manifest.py
- Acceptance:
  - RED: no CI job invokes the manifest drift-check (grep of .github = no match).
  - GREEN: a CI step runs `python code-toolkit/scripts/sync_codex_manifest.py --check`; locally simulating divergence makes the command exit non-zero (gate would fail).
- External surfaces: GitHub Actions workflow schema (CI config).
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "a CI drift-gate that fails on divergence" (Smallest End State #2).

## Task 4 — Fix the hook to the verified contract
- Description: Edit `hooks/session-start` to emit **only** `hookSpecificOutput.additionalContext` (the key both Claude Code AND Codex consume per the official doc), removing the dead snake_case `additional_context` and bare `additionalContext` keys from both the escape-hatch/early-return branches and the final `printf`. Update the header comment block to state the correct single-key contract (delete the "Emits BOTH ... Codex CLI shape" misconception).
- Module: code-toolkit/hooks
- Files touched: code-toolkit/hooks/session-start
- Context paths:
  - code-toolkit/hooks/session-start
- Acceptance:
  - RED: the hook currently emits 3 keys (grep finds `additional_context` snake_case).
  - GREEN: hook emits exactly `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"..."}}`; running the hook + `python3 -c "import json,sys;d=json.load(sys.stdin);assert 'additional_context' not in d and d['hookSpecificOutput']['additionalContext']"` passes; escape-hatch and missing-file branches likewise emit only the nested key.
- External surfaces: Codex/Claude SessionStart hook output contract (developers.openai.com/codex/hooks).
- Dependencies: none
- Independent: true
- Brief item covered: "Align the hook; remove the dead keys" (Smallest End State #1).

## Task 5 — Fix test-hook-injection.sh to assert the right key
- Description: Rewrite the offline assertion in `tests/codex-cli/test-hook-injection.sh` to check `data['hookSpecificOutput']['additionalContext']` (and assert the snake_case key is ABSENT), replacing the current wrong `data.get('additional_context')` check at :44-53. Update the file's comments/echo strings (:7, :22, :120) that reference the wrong key.
- Module: code-toolkit/tests/codex-cli
- Files touched: code-toolkit/tests/codex-cli/test-hook-injection.sh
- Context paths:
  - code-toolkit/tests/codex-cli/test-hook-injection.sh
  - code-toolkit/hooks/session-start
- Acceptance:
  - RED: `bash test-hook-injection.sh` Step 1 asserts the snake_case key (passes for the wrong reason / would pass even if Codex consumes nothing).
  - GREEN: Step 1 asserts `hookSpecificOutput.additionalContext` present + snake_case absent, and passes against the Task-4 hook.
- External surfaces: none (bash + python3 stdlib).
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "Fix `test-hook-injection.sh` to assert the verified key" (Smallest End State #3).

## Task 6 — Fix test-skill-loading.sh command names
- Description: Replace the non-existent `codex plugin install` (:48, :73) and `codex plugin details` (:87) with the real Codex 0.139.0 surface: `codex plugin marketplace add .` + `codex plugin add code-toolkit@monkey-skills` + `codex plugin list` (and the right enumeration command). Keep the graceful-skip-when-codex-absent behavior.
- Module: code-toolkit/tests/codex-cli
- Files touched: code-toolkit/tests/codex-cli/test-skill-loading.sh
- Context paths:
  - code-toolkit/tests/codex-cli/test-skill-loading.sh
- Acceptance:
  - RED: grep finds `codex plugin install` / `codex plugin details` (commands absent from `codex plugin --help`).
  - GREEN: script uses only commands present in `codex plugin --help` (add / list / marketplace / remove); `bash test-skill-loading.sh` runs against installed Codex without an "unknown subcommand" error (or skips cleanly if codex absent).
- External surfaces: Codex CLI `plugin` subcommand surface (probed: add/list/marketplace/remove).
- Dependencies: none
- Independent: true
- Brief item covered: "fix ... command names to the real Codex surface" (Smallest End State #3).

## Task 7 — Live verification ritual + record outcome
- Description: On the installed Codex 0.139.0, run the real ritual: `codex plugin marketplace add .` → `codex plugin add code-toolkit@monkey-skills` → confirm the 11 skills are discoverable (`codex plugin list` / enumeration) AND that a fresh `codex exec` session has the router context injected by the (Task-4) hook. Record the verified outcome in `tests/codex-cli/README.md`, replacing the "verification deferred per user direction" + "lock-step since v0.4.0" notes. If an auth/sandbox limit blocks the live session, record the blocker explicitly + fall back to the official-doc contract (do not fabricate a pass).
- Module: code-toolkit/tests/codex-cli
- Files touched: code-toolkit/tests/codex-cli/README.md
- Context paths:
  - code-toolkit/tests/codex-cli/README.md
  - code-toolkit/.codex-plugin/plugin.json
  - code-toolkit/hooks/session-start
- Acceptance:
  - RED: README says verification is deferred / status v0.9.0 / TBD.
  - GREEN: README records a dated, real result — skills discoverable (yes/no + command used) and hook router-context consumed (yes/no + how observed) — OR a documented blocker with the offline fallback; no remaining "deferred per user direction" claim.
- External surfaces: live Codex CLI 0.139.0 (auth + local-marketplace install flow).
- Dependencies: Tasks 2, 4, 6 complete first (join)
- Independent: false
- Brief item covered: "Live verification ritual actually run ... Record the result" (Smallest End State #4).

## Task 8 — Replace TBD markers in codex-tools.md
- Description: In `skills/using-code-toolkit/references/codex-tools.md`, strip the `⚠️ TBD verify` markers and the "Phase v0.4.0 / verification ritual pending" framing; replace with the verified command names (from Task 6/7) and the confirmed hook-injection contract, dated 2026-06-14.
- Module: code-toolkit/skills/using-code-toolkit
- Files touched: code-toolkit/skills/using-code-toolkit/references/codex-tools.md
- Context paths:
  - code-toolkit/skills/using-code-toolkit/references/codex-tools.md
  - code-toolkit/tests/codex-cli/README.md (the verified facts recorded in Task 7)
- Acceptance:
  - RED: grep finds `⚠️ TBD verify` (or "verification ritual pending") in codex-tools.md.
  - GREEN: no `TBD verify` markers remain; command names match `codex plugin --help`; the hook-contract line states the single verified key, dated.
- External surfaces: none (doc).
- Dependencies: Task 7 completes first
- Independent: false
- Brief item covered: "Docs replace guesses with facts" (Smallest End State #5).

## Notes
- Parallel waves: Level 0 = {T1, T4, T6} (disjoint roots); Level 1 = {T2, T3, T5} (T2,T3←T1; T5←T4; disjoint files); Level 2 = {T7}; Level 3 = {T8}.
- T7 is the only task touching a live authenticated external CLI — if dispatched to an implementer that can't auth/sandbox-exec `codex`, it BLOCKs and surfaces to the orchestrator/user to run the ritual; the recorded-fallback acceptance keeps it honest either way.
