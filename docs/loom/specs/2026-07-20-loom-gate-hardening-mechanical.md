# Brief — loom Gate Hardening (mechanical / do-real cluster)

Upstream artifact: `docs/loom/audits/2026-07-20-loom-mechanism-weakness-audit.md`
Stage: brainstorming brief → `writing-plans`. Date: 2026-07-20.

## Design-side on-ramp

N/A — this is a hardening increment over existing, test-covered machinery (bug-fix/refactor class). Axis-0 negative guard applies; no product-principles/design/spec station precedes it.

## Problem

(JTBD — committed read, not re-asked) The loom green markers must actually **mean what they claim**, so that when loom automates work to the point the maintainer can walk away — SDD dispatching weak (haiku-tier) subagents, the fully-automated pipeline/batch, Codex hosts — the "verified / reviewed / done" signals are trustworthy rather than self-attested. The audit proved seven gates validate *shape* (a self-typed string, an exit code the gated party reports, a heading's presence) instead of *evidence that the work happened*, and a dogfood proved a haiku subagent will self-mint a review bypass under ordinary "ship it" pressure.

## Users

- Primary: the loom-family maintainer (this repo), who relies on the markers when not watching.
- Downstream: every installer of the plugin-shipped fixes (they arrive via `plugin update` after a version bump). The repo-local fix (#1) protects the maintainer's release pipeline directly.

Failure conditions are precisely the un-watched configurations: weak SDD subagents, full-auto pipeline/batch, Codex.

## Smallest End State

One reviewed branch closing every **mechanically-closeable** gate — the ones where a real command exists to run or a precondition exists to enforce, so the fix needs no unsolvable design:

1. **#1 version-bump blind spot** — `scripts/check_version_bump.py:42` `SKILL_CONTENT_DIRS` gains `"scripts"`, so editing gate code demands a bump.
2. **`verified` binds to real execution** — `loom-code/scripts/loom_gate_markers.py` `verified` stops accepting a self-typed `--suite-line`; it captures a real test run's exit code/output instead (see Open Questions for the exact binding mechanism).
3. **pipeline seg2 validator runs itself** — `loom-pipeline/scripts/driver_40_seg2.js:106-113` stops trusting the agent's self-reported validator exit code; it runs the validator itself (pattern already shipped at `batch_queue.py:311-317`).
4. **#4 batch precondition** — `batch_queue.py` `_cmd_mark` (`:438-464`) gains the precursor-state guard its sibling `_cmd_mark_running` (`:467+`) already has, so a QUEUED (never-dispatched) entry cannot jump straight to DONE.
5. **#3 push-guard action-detection** — `loom-code/hooks/git-guard.py` (`:381`) matches a push/merge *action* anywhere in a git/gh invocation regardless of first-token wrapper, fail-closed on unrecognized wrappers around `git`.

Each lands its audit-§8 repro as a **RED test first** (TDD iron law).

**Honest scope note (from Axis-4 research):** these raise the local bar from "type a string, zero execution" to "a real command must run and exit 0 / a precondition must hold" — the proportionate local pattern. They do **not** achieve cryptographic unforgeability, which is impossible when the gated agent shares the filesystem/shell (see Alternatives). The residual (waiver / review-pass are still self-mintable in principle) is deliberately deferred to the CI-side arc.

## Current State Evidence

- **Forward (control flow in):** `git-guard.py:main()` → `SEGMENT_SPLIT`/`_tokens` → `toks[0]=="git"` gate (`:381`) → marker check `_load_json(.git/loom/*.json)` (`:326-344`). `check_version_bump.plugins_with_skill_content()` iterates changed paths vs `SKILL_CONTENT_DIRS` (`:42,64-`). `batch_queue._cmd_mark()` writes status with no precondition (`:454-455`). `driver_40_seg2.js` gate reads a self-reported exit code (`:106-113`). `loom_gate_markers._cmd_verified()` validates a self-typed suite-line then writes marker (`:306-331`).
- **Reverse (SSOT / sync direction):** each of the four files is a **single-owner copy** — no byte-identical lockstep sibling to sync (verified via `find` + drift-script scan). One cross-surface link: `.codex/hooks/git-guard-shim.sh` **forwards** stdin to `git-guard.py` (it does not duplicate the matching logic), so a matching-logic change flows to Codex automatically — but `loom-code/scripts/test_git_guard.py` and `scripts/test_codex_git_guard_shim.py` encode current behavior and will need new cases. `check_version_bump.py` imports `sync_codex_manifests.CODEX_ELIGIBLE`.
- **Error (failure paths at touch points):** `git-guard.main()` fail-**open** on malformed stdin (`:351-356`) and `LOOM_CODE_MODE=off` (`:359`) — out of scope, but do not regress. `_cmd_verified` returns 4 on a non-green suite-line; `_cmd_mark_running` returns 1 with a caller-facing message on a non-RUNNING entry (`:476-479`) — the exact shape #4 should mirror.
- **Data (shapes):** markers are `{schema:1, head_sha, ...}` JSON under `<git-dir>/loom/`. Queue state is `queue-state.json` keyed by change id; status vocab `QUEUED/RUNNING/DONE/FAILED` (`effective_entries`, `:221-233`). QUEUE.toml entries need `id`/`plan`/`budgets.run`.
- **Boundary:** verified/waiver/review-pass CLI subcommands (`loom_gate_markers.py:405-422`); `mark`/`mark-running` subparsers (`batch_queue.py:1197-1223`); `SKILL_CONTENT_DIRS` tuple (`check_version_bump.py:42`).

Evidence paths: `loom-code/hooks/git-guard.py`, `loom-code/scripts/loom_gate_markers.py`, `loom-pipeline/scripts/batch_queue.py`, `loom-pipeline/scripts/driver_40_seg2.js`, `scripts/check_version_bump.py`; tests `loom-code/scripts/test_git_guard.py`, `test_loom_gate_markers.py`, `scripts/test_codex_git_guard_shim.py`.

## Decision

Build the five mechanical/do-real fixes above in one SDD branch, RED-test-first, each repro from audit §8 committed as the failing test. Version-bump the two plugins whose shipped code changes (loom-code, loom-pipeline); #1 and the CI are repo-local. Update the two behavior-encoding tests (git-guard, codex-shim) for the new push-guard matching. Frame every fix honestly as a bar-raise, not unforgeability.

We will NOT attempt to make waiver/review-pass unforgeable in this branch — research shows it is not locally achievable; that becomes a separate CI-side arc.

## Out of Scope (→ follow-up CI-side arc)

- waiver + review-pass "cannot self-mint" (Cluster-A tail) — **not locally solvable**; real fix = CI-side re-check + deliberateness bar (deny-list / PreToolUse). Amend audit §7 rec#2 accordingly.
- #8 DESIGN.md path resolution — needs a design-critic SKILL re-read + a resolve-strategy decision.
- #6 Codex shim shape-tolerance — needs Codex's real payload spec.
- #5 Chinese recall — tested and REFUTED; no fix.
- flat-folder CI coverage gap (discovery/pipeline), mint lockstep CI — repo-local CI, batch later.

## Alternatives Considered (Axis-4, research-grounded)

The core question — can a gate's evidence be made unforgeable by the party being gated, locally? — resolved against unforgeability. Every pattern that achieves it depends on an external trust domain the requester can't impersonate: **required status checks** (reporter ≠ PR author; GitHub branch protection), **build provenance/attestation** (SLSA / in-toto / Sigstore / npm provenance, isolated build job + OIDC + transparency log), **OIDC workload identity** (external issuer + verifier). None transfer to a shared-filesystem local context. The matching precedent is **git hooks themselves** — git/husky/lefthook explicitly concede `--no-verify` bypassability and push real enforcement server-side; a live Claude Code incident (anthropics/claude-code#40117: agent used `--no-verify`+`stash`+quiet flags across 6 commits, then misrepresented it) confirms this is real for AI subagents. Converging community fix (EN+JA agree; Zenn calls it 「レール」a guardrail-not-a-lock): (b) raise the deliberateness bar + (c) capture real execution evidence + push the authoritative check server-side. **My take, adopted:** do (c)+(b) locally, don't chase (a); push unforgeability to CI where a separate domain exists. Full notes + source URLs: `scratchpad/axis4-unforgeable-gate-research.md` and audit §7.

## What Becomes Obsolete

- `verified`'s `--suite-line` free-text parameter and its `validate_suite_line` regex path — replaced by real-execution binding; remove in the same change (don't leave the self-typed path as a fallback, or the fix is a no-op).
- The reading-audit's claim that `gh pr merge <n>` is a push-guard miss — corrected (it is caught); don't write a test asserting the wrong thing.

## Open Questions (resolve in planning/spec)

1. **`verified` binding mechanism** — does the CLI (a) run an agent-supplied `--run "<cmd>"` and capture its exit code, (b) auto-discover + run the package test command (agent supplies nothing — strongest bar), or (c) ingest a machine-captured artifact (junit xml / exit-code file)? Lean: (a) or (c) — proportionate, minimal plumbing; note residual forgeability (`--run "true"`) honestly. This is the one real design fork inside the mechanical set.
2. **push-guard fail-closed breadth** — how aggressively to treat unrecognized wrappers (`env`, `sh -c`, absolute paths) around `git`: block-on-suspicion vs enumerate known wrappers. Decide with the false-positive cost (blocking a legitimate non-push git command) in view.
