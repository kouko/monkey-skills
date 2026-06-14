# Brief — Complete + verify code-toolkit's Codex CLI compatibility

> Date: 2026-06-14 · Stage: brainstorming → writing-plans
> Branch target: feature branch off `main` (cbdaea76)

## Problem

(Axis 1 — JTBD) Make the claim *"code-toolkit runs identically on {Claude Code,
Codex}"* a **verified fact, not an assumption**. code-toolkit already ships Codex
scaffolding (a `.codex-plugin/plugin.json` manifest, a dual-shape SessionStart
hook, and a `tests/codex-cli/` harness) but the scaffolding (a) was built on an
**incorrect model** of Codex's hook contract, (b) has **drifted** out of lock-step
with the Claude manifest, and (c) was **never run against a real Codex CLI**. The
job behind this work: pay down that tech debt so the downstream "merge vs delegate
spec-toolkit" (B-vs-D) decision can be settled on a proven `{CC, Codex}` coverage
fact rather than a hope.

## Users

(Axis 2) kouko — solo dev, macOS, **both Claude Code and Codex CLI 0.139.0
installed** (`~/.local/bin/codex`). Wants code-toolkit's router + 11 skills to
activate identically on either host. Secondary user: anyone installing code-toolkit
from the public `monkey-skills` marketplace who runs Codex — verified compat has
external value.

## Smallest End State

(Axis 3) code-toolkit is **proven** to work on the installed Codex 0.139.0, with the
defects that blocked that proof fixed and a guard preventing the root-cause drift
from recurring:

1. **Hook contract aligned to ground truth.** Establish — by probing real Codex
   0.139.0, not just the doc — which SessionStart output key Codex actually consumes
   (`hookSpecificOutput.additionalContext` per official doc). Align the hook; remove
   the dead keys that encode the wrong model **only if** verification confirms they
   are unused.
2. **Manifest drift fixed + guarded.** Re-sync `.codex-plugin/plugin.json`
   (0.9.0 → 0.16.0 + missing keywords) **via a sync script**, with a **CI drift-gate**
   that fails on divergence — mirroring the repo's existing `distribute.py` /
   `verify-drift.py` SSOT pattern. (User-chosen approach.)
3. **Test harness asserts the RIGHT thing.** Fix `test-hook-injection.sh` to assert
   the verified key; fix `test-skill-loading.sh`'s command names to the **real**
   Codex surface (`codex plugin add` / `codex plugin list` / `codex plugin
   marketplace add` — NOT the `codex plugin install` / `codex plugin details` it
   currently guesses).
4. **Live verification ritual actually run.** Install code-toolkit into Codex
   0.139.0 (local marketplace), confirm skill discovery + that the hook's router
   context is actually consumed at session start. Record the result.
5. **Docs replace guesses with facts.** Strip the `⚠️ TBD verify` markers and the
   false "lock-step since v0.4.0" / "verification deferred" notes in
   `tests/codex-cli/README.md` and `references/codex-tools.md`; replace with what
   was verified.

## Current State Evidence

- **Forward (entry / activation path):** `code-toolkit/hooks/hooks.json` declares a
  `SessionStart` hook → `${CLAUDE_PLUGIN_ROOT}/hooks/session-start`. The bash hook
  (`code-toolkit/hooks/session-start:51-55`) emits three keys:
  `hookSpecificOutput.additionalContext` (correct for both hosts per official doc),
  `additional_context` (snake_case — built believing this was "the Codex shape"),
  and bare `additionalContext` (legacy). Official Codex contract
  (developers.openai.com/codex/hooks): Codex consumes
  `hookSpecificOutput.additionalContext` — the **same** key as Claude Code → the hook
  already works on Codex; the snake_case key is dead weight.
- **Reverse (SSOT ownership / sync direction):** **No sync script exists** for the
  two manifests (`grep` of `code-toolkit/scripts/` + repo scripts = no match). The
  "bumped in lock-step since v0.4.0" claim in `tests/codex-cli/README.md` is **manual
  discipline that failed** → `.codex-plugin/plugin.json` version `0.9.0` vs
  `.claude-plugin/plugin.json` `0.16.0`, and the codex manifest's `keywords` is
  missing `brainstorming / clean-code / solid / owasp-asvs / session-start-hook /
  superpowers-parity`. Canonical SSOT = `.claude-plugin/plugin.json`; `.codex-plugin`
  is the derived copy (it adds only the Codex-specific `interface` block).
- **Error (wrong-assertion path):** `tests/codex-cli/test-hook-injection.sh:44-53`
  asserts the **wrong** key (`data.get('additional_context')`, snake_case top-level);
  `:120` even self-doubts ("Codex CLI ignores 'additional_context' key (use
  different key name?)"). So the test can be green while Codex consumes nothing.
- **Data (manifest interface block):** `.codex-plugin/plugin.json` carries a full
  `interface` block (displayName / longDescription / capabilities / defaultPrompt /
  brandColor) — this is Codex-specific and must be **preserved** by any sync script
  (sync the shared fields, leave `interface` alone).
- **Boundary (real Codex CLI surface, probed 2026-06-14):** `codex 0.139.0` exposes
  `codex plugin {add, list, marketplace, remove}` and `codex plugin marketplace
  {add,list,upgrade,remove}`. The test scripts' `codex plugin install` (test-skill-
  loading.sh:48,73) and `codex plugin details` (:87) **do not exist** → must change
  to `codex plugin add` / `codex plugin list`. No CI runs the codex tests or
  drift-checks the manifest (`.github/` grep = no match).

### Evidence paths appendix
- `code-toolkit/hooks/session-start`, `code-toolkit/hooks/hooks.json`
- `code-toolkit/.codex-plugin/plugin.json`, `code-toolkit/.claude-plugin/plugin.json`
- `code-toolkit/tests/codex-cli/{test-hook-injection.sh, test-skill-loading.sh, README.md}`
- `code-toolkit/skills/using-code-toolkit/references/codex-tools.md`
- Official: developers.openai.com/codex/hooks (fetched 2026-06-14)

## Decision

Build, in evidence-first order: (i) **probe real Codex 0.139.0** to establish the
hook-injection ground truth and the real plugin command surface; (ii) **fix the
hook** to match (align keys, drop dead ones only if confirmed unused); (iii) add a
**manifest sync script + CI drift-gate** (`.claude-plugin` → `.codex-plugin`,
preserving the `interface` block) and run it to clear the 0.9.0→0.16.0 drift; (iv)
**fix both test scripts** to assert the verified key and use real command names; (v)
**run the live verification ritual** and record it; (vi) **correct the docs**.

We will NOT change the hook's fundamental mechanism (keep the single dual-shape bash
hook as the shared Claude+Codex SSOT — do not fork into a Codex-only AGENTS.md path).
We will NOT redesign the router or skills. We will NOT touch spec-toolkit (the
B-vs-D decision is downstream of this and explicitly out of scope here).

## Out of Scope

- The spec-toolkit merge-vs-delegate (B-vs-D) decision — this work *informs* it but
  does not execute it.
- A full per-skill tool-name audit beyond what live verification empirically
  surfaces (if a skill breaks on Codex during the ritual, fix that skill; do not
  pre-emptively rewrite all 11).
- Any new Codex-only feature / AGENTS.md injection path (keep the shared hook).
- Codex compat for *other* monkey-skills plugins (this is code-toolkit only).
- Cursor / web / other-host support (the residual portability question stays open
  for B-vs-D; not built here).

## Alternatives Considered

(Axis 4 — narrow problem space; **no competing industry approaches to research** —
the mechanism is fixed by the official Codex hooks contract and empirically
checkable on the installed CLI. "Execution = truth" applies.)

- **Offline-only fix (trust the doc, defer live run).** Rejected: Codex 0.139.0 is
  installed, so we can establish ground truth empirically — and the doc may differ
  from 0.139.0's actual behavior. Leaving it unverified defeats the whole purpose
  (turn assumption → fact).
- **Fork the injection mechanism (Codex via AGENTS.md, Claude via hook).** Rejected:
  the official doc confirms Codex honors plugin-bundled `hooks/hooks.json` + the same
  `hookSpecificOutput.additionalContext` key → one shared hook is DRY and already
  correct. Forking would create two mechanisms to maintain.
- **One-shot manual manifest sync (no guard).** Rejected by user — it's the exact
  root cause that produced this drift; a sync-script + CI gate prevents recurrence
  (repo already has the `distribute.py` / `verify-drift.py` precedent).

## What Becomes Obsolete

(Axis 5 — remove in the same change)
- The hook's dead `additional_context` (snake_case) + bare `additionalContext`
  (legacy) keys — **iff** live verification confirms Codex 0.139.0 reads only
  `hookSpecificOutput.additionalContext`.
- The `⚠️ TBD verify` markers, the false "lock-step since v0.4.0" claim, and the
  "verification deferred per user direction" note in `tests/codex-cli/README.md`.
- The guessed command names (`codex plugin install` / `codex plugin details`) in the
  test scripts.
- Manual manifest-sync discipline → replaced by the sync script + CI gate.

## Open Questions

- Does Codex 0.139.0 honor a **plugin-bundled** `hooks/hooks.json` the same way as a
  user-config hook? (Official doc says yes — "plugins can bundle lifecycle config
  through their plugin manifest or a default `hooks/hooks.json`" — but confirm in the
  live ritual.)
- Does the local-marketplace install flow (`codex plugin marketplace add .` →
  `codex plugin add code-toolkit@monkey-skills`) work from this repo layout, or does
  it need a packaged snapshot? (Resolve in the live ritual.)
