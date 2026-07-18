# Brief: Loop-Convergence Fixes (tier-1 + §4c batch/verdict designs, merged)

- **Date**: 2026-07-18
- **Source**: `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md` (4 rounds: mechanism inventory → industry comparison → adversarial verification → §4c deep-dive designs). All alternatives research, red-team caveats, and the two detailed designs live there; this brief cites, not repeats.
- **Status**: SHIPPED (2026-07-18) — merged scope: tier-1 items 1-5 + §4c Fix-1 (batch reconcile) + §4c Fix-4 (verdict files); see `docs/loom/plans/2026-07-18-loop-convergence-fixes.md` Task 20 for the shipping-tax commit

## Problem

Five loom-* loop/gate defects let an agent diverge from the user's goal without any mechanism noticing: (a) the interactive-mode writer↔critic outer cycle has no round cap or escalation clause (audit Gap 2); (b) loom-discovery's completeness validator exists but is wired into no flow (Gap 3); (c) the family's only mechanical gate (git-guard push block) is absent on the Codex host (Gap 10); (d) SDD's `NEEDS_CONTEXT` status is an uncapped re-dispatch channel bypassing the 3-round cap (Gap 8); (e) continuous-mode's 2-round halt and SDD's 3-round cap read as contradictory caps for the same loop (numeric drift). The job: close the cheap ones now — bounded loops, wired gates, reconciled numbers — without waiting for the heavyweight fixes (batch orphan, verdict schema) that need redesign.

## Users

kouko + any agent session (including weak-tier executors — the documented failure mode per `docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md`) running loom skills on Claude Code, and on Codex where hook enforcement currently does not exist.

## Smallest End State

Five surgical edits, no new machinery:

1. **Critic outer cap** — completeness-critic + design-critic SKILL.md resolution clauses gain: outer revision cycle capped at **2** (aligning with pipeline `RALLY_CAP=2`); on the 2nd consecutive NEEDS_REVISION after a revision, stop re-running and surface the unresolved findings to the user in plain language (explicit hand-back, never silent proceed). ≤~70 words each (completeness-critic word budget: 3,889/4,500 hard cap).
2. **Wire discovery validator** — user-insights + business-value SKILL.md gain a mandatory validate step invoking `scripts/validate_discovery_artifacts.py` before declaring done (mirror the exact wiring pattern of product-principles Step 8, `loom-product-principles/skills/product-principles/SKILL.md:254-264`); fix-and-rerun bounded at 2 attempts, then surface.
3. **Codex push-gate wiring** — repo-root `.codex/hooks.json` gains a `PreToolUse` / `Bash` entry via a `.codex/hooks/` shim invoking `loom-code/hooks/git-guard.py`. Scope limitation accepted: protects the monkey-skills repo only (Codex has no plugin-hook mechanism). Includes a payload-format compatibility check (Codex hook JSON vs Claude Code's) inside the shim.
4. **NEEDS_CONTEXT cap** — SDD SKILL.md one-liner: `NEEDS_CONTEXT` re-dispatches capped at 2 per task; a 3rd means the spec/plan is missing information — stop and surface to the user (mirrors the existing 3-round NEEDS_REVISION language).
5. **Numeric-drift reconciliation** — no number changes: continuous-mode.md documents that its 2-round halt is deliberately one round earlier than SDD's 3-round cap (no human is pumping; hand back slack early), and SDD's cap section cross-references it.

6. **Batch reconcile + recovery verbs** (audit §4c "Fix 1 revised design" — the six numbered points there are the spec): `dispatched_at` + `mark-running --run-id --session-dir`; reconciliation in `next` + new `reconcile` verb (never `status`); auto-FAIL only on definitive wf-record evidence (`failed`/`killed`), staleness → loud SUSPECT + human verbs; new `reset` / `force-fail` verbs with per-entry append-only `audit[]`; `done` = `terminal_count == total`; all state I/O under `flock(LOCK_EX)` + atomic replace (macOS: direct LOCK_EX, non-truncating open). Undocumented wf-record format treated as opportunistic evidence — unreadable ⇒ "no evidence" ⇒ SUSPECT path.
7. **Critic verdict files with teeth** (audit §4c "Fix 4 revised design"): in-tree `docs/loom/<change-id>/<critic>-verdict.json`; sha256 content binding over covered files; `mint`/`validate` CLI mirroring `loom_gate_markers.py` (validate exits 0 fresh-pass / 2 never-ran / 3 fresh-NEEDS_REVISION / 4 stale); NEEDS_REVISION still mints; overwrite-in-place; consumers = spec-expansion ui-flows intake + writing-plans change-folder intake, both refuse on non-zero.

Plus the repo's shipping tax: version bumps + CHANGELOG entries for the five touched plugins (loom-spec, loom-interface-design, loom-discovery, loom-code, loom-pipeline), marketplace.json sync, codex-manifest sync script; audit-doc Status line updated in the same PR.

## Current State Evidence

- **Forward** (call paths being changed): design-critic resolution `loom-interface-design/skills/design-critic/SKILL.md:255-256` ("route back … then re-run this critic", no bound); completeness-critic `loom-spec/skills/completeness-critic/SKILL.md:433-434`; SDD NEEDS_CONTEXT branch `loom-code/skills/subagent-driven-development/SKILL.md:15,102` + `agents/implementer.md:356-363`; continuous-mode halt row `loom-code/skills/using-loom-code/references/continuous-mode.md:91`; SDD cap `subagent-driven-development/SKILL.md:151-156`.
- **Reverse** (SSOT/ownership): validators are per-plugin-owned (`loom-discovery/scripts/validate_discovery_artifacts.py`, currently referenced only by its own tests + CHANGELOG — verified by grep, audit Gap 3); `.codex/hooks.json` is hand-maintained at repo root, NOT synced by `scripts/sync_codex_manifests.py` (grep: no hook fields copied); worked example for validator wiring is product-principles Step 8.
- **Error** (failure surfaces): `validate_discovery_artifacts.py` exits non-zero on missing sections/verdict-enum violations (199 lines, has own test suite); `git-guard.py` exits 2 to block; Codex hook events confirmed firing ONLY for Bash-routed calls (`docs/loom/codex-verification.md:102-116`; apply_patch emits none — upstream bugs openai/codex#16732/#20204).
- **Data**: `docs/loom/discovery/` does not exist in this repo — no real artifacts for validator calibration; calibration = its existing test fixtures + one synthetic golden sample. The wired step must therefore tolerate first-run/greenfield artifact creation.
- **Boundary**: completeness-critic SKILL.md at 3,889 words vs 4,500-word hard cap (~600-word headroom; soft target 3,750 already exceeded → PR must carry the one-line justification per repo rule); `.codex/hooks.json` currently PostToolUse-only (read in full — 19 lines).

Evidence paths appendix: all above verified this session (2026-07-18) via the audit's three rounds + direct Read/grep; audit doc carries the full citation set.

## Decision

Build the seven items + shipping tax above. Items 1-5 are prose-tier vocabulary + wiring; items 6-7 are the §4c mechanized designs with their red-team blockers resolved (each §4b hole either closed or explicitly accepted as residual in §4c). NOT building (still deferred): debugging outer budget (fix 3), `budgets.run` enforcement (Gap 9), resume test (fix 6), the PreToolUse-on-Skill hook upgrade path (pending probe P1).

## Out of Scope

- systematic-debugging hard budget; `budgets.run` floor enforcement; kill-resume test.
- PreToolUse-on-Skill hook gating of critic-verdict consumption (upgrade path; blocked on probe P1 — undocumented matcher).
- Changing either cap NUMBER in item 5 (documentation-only reconciliation).
- Live Codex verification of item 3 — user-run probe, out-of-band acceptance (this host cannot run Codex).
- GitHub branch-protection backstop (host-independent gate) — separate decision.

## Alternatives Considered

Recorded in the audit: §2 per-gap industry columns (bounded re-ask: Guardrails `num_reasks` / Instructor `max_retries`; framework runtime caps: LangGraph/Agents SDK/ADK; platform-level gates: Copilot/Devin branch protection), §4 minimal-fix shapes, §4b red-team of the rejected heavier variants. For item 1 the CrewAI-style "degrade and proceed with best answer" alternative was rejected in favor of explicit hand-back — silent degrade is the failure mode the audit's own memory store documents.

## What Becomes Obsolete

Nothing deleted; item 5 removes an ambiguity (the implied-but-false "two competing caps" reading). The audit doc's §4 recommendations 2/5/7/9/10 flip to shipped when this lands — amend its Status line in the same PR.

## Open Questions

- Whether continuous-mode's 2-round halt was originally intentional slack (assumed yes; the reconciliation wording works under either history and changes no behavior).
- Codex hook payload shape — resolved empirically by the shim's compatibility check + user's live probe.
