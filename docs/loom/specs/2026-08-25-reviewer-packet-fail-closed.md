# Reviewer packet fail-closed hardening

Date: 2026-08-25 · Author: kouko + Claude (Fable 5) · Status: draft

## Design-side on-ramp

not fired — bug-fix/hardening of an existing mechanism (negative guard); no product-shaped new work.

Loom-init offer: N/A — repo already has the queue layer.

## Queue relation

unqueued — no live bet entries exist; this arc responds to same-day live-test evidence (fail-closed breach, n=2). It does, however, satisfy the start condition of open backlog entry `2026-08-04-a-rule-can-ship-into-a-skill-and-never-reach-its-agent-contract` ("before the next branch that adds or edits a rule constraining reviewer behaviour") — that entry's concern (rule/contract pairing) is partially addressed by Leg B below.

## Problem

When an SDD orchestrator dispatches a loom reviewer with an incomplete immutable review context packet (e.g. missing `reviewed_sha`), I want the dispatch to be refused mechanically before or at the packet boundary, so a reviewer can never silently manufacture its own evidence base — live tests today (n=2, same session) show reviewers deriving their own SHA via `git log`, reading the mutable worktree, and emitting a full verdict whose content is wrong relative to the true snapshot.

## Users

Loom orchestrators (Claude Code sessions and Codex sessions running SDD / requesting-code-review / requesting-docs-review) and the humans who trust their review verdicts. Conditions: reviewer role prompts are shared verbatim across both hosts; the packet producer is `loom-code/scripts/review_context.py`; verdict consumption is `loom-code/scripts/loom_gate_markers.py` + `loom-code/hooks/git-guard.py`.

## Smallest End State

Three thin legs, all mechanical or pointing at a mechanical action, none new-framework:

1. **Leg A — pre-dispatch packet gate.** `review_context.py` gains a `--validate` mode (packet JSON in → exit 0 / nonzero with the missing/invalid field named). Checks: all four keys present (`target_repo`, `reviewed_sha`, `plugin_version`, `resources`), `reviewed_sha` is full 40-hex and exists in `target_repo` (`git cat-file -e`), every `resources` value is an absolute existing path. The three orchestrator call sites (`subagent-driven-development/SKILL.md`, `requesting-code-review/SKILL.md`, `requesting-docs-review/SKILL.md`) add one REFUSE line: run the validator before any reviewer dispatch; nonzero exit → do not dispatch.
2. **Leg B — observable refusal state.** `scripts/_reviewer-discipline.md` R0/R1a change from "return no verdict" (silence — indistinguishable from a dead arm) to: emit exactly `verdict: MALFORMED_PACKET` plus a `missing_fields:` list, read no repository content, cite nothing. `loom_gate_markers.py` recognizes `MALFORMED_PACKET` as an explicit never-mintable refusal (clear message, distinct from a schema error). Re-run `distribute.py` to regenerate the four reviewer agent files.
3. **Leg C — always-on SHA check at verdict intake.** `validate_verdict_text` requires `reviewed_sha` present and full-40-hex even when `--expected-head` is not passed.

## Current State Evidence

- **Forward**: packet born in `loom-code/scripts/review_context.py` (`resolve_context`, anchor "def resolve_context"); consumed by orchestrator prose at `subagent-driven-development/SKILL.md` (anchor "one unchanged immutable context packet"), `requesting-code-review/SKILL.md` (anchor "Keep its full JSON packet unchanged"), `requesting-docs-review/SKILL.md` (anchor "complete immutable context packet"). No code path touches the packet between producer and Task dispatch — completeness is asserted, never tested.
- **Reverse**: SSOT for reviewer rules is `loom-code/scripts/_reviewer-discipline.md`, injected by `loom-code/scripts/distribute.py` (anchor `AGENT_REVIEWER_DISCIPLINE_TARGETS`) into the four reviewer agent files; drift guarded by `loom-code/scripts/verify-drift.py` (anchor "INJECTION-DRIFT"). Edit the SSOT, never the injected blocks.
- **Error**: the only malformed-packet defense is prose — R0 (anchor "return no verdict until the orchestrator supplies the complete packet") and R1a (anchor "do not produce a verdict"). Live breach n=2 this session: reviewer ran `git log --oneline -1` to derive its own short SHA, `cat` the mutable worktree, and emitted `NEEDS_REVISION` whose content contradicted the true snapshot.
- **Data**: verdict schema check `validate_verdict_text` in `loom-code/scripts/loom_gate_markers.py` (anchor "def validate_verdict_text") does not require `reviewed_sha`; full-40-hex enforcement (anchor `_FULL_SHA_RE`) fires only under `--expected-head`. Allowed verdict values (anchor `ALLOWED_VERDICTS`) have no refusal state.
- **Boundary**: the only existing mechanical packet validation lives in `loom-code/scripts/live_gate_station_receipt.py` (anchor `PACKET_KEYS`) — a release-gate fixture harness, not the runtime path; its key-set + SHA-shape logic is the reference implementation Leg A reuses. Push-time gate `loom-code/hooks/git-guard.py` (anchor "review-pass.json") reads only the marker file, so it cannot catch a malformed dispatch.

## Alternatives Considered

My take — **Recommend**: Legs A+B+C together. **Why**: industry consensus (EN+JA agree) is that model-side prose refusal is not a control — fail-closed means mechanical schema validation at both boundaries (reject + name the error), with the model-side text only pointing at the mechanism; this repo's own documented precedent says judgment-shaped prose fails while verifiable-action prose holds. **Conditional reversal**: if Leg A's orchestrator REFUSE line proves to be skipped in practice (it is still prose-invoking-a-script), escalate to wiring the validator into a PreToolUse hook on Task dispatch — deferred now because no evidence yet shows orchestrators skip named script steps (they reliably run `review_context.py` itself today).

| Alternative | Pros | Cons | Who ships this pattern |
|---|---|---|---|
| Prose-only tightening (rewrite R0 harder) | zero code | n=2 evidence says it fails; refusal stays unobservable | nobody credible — both EN and JA guardrail literature treats output prose as the layer that MUST be backed by validation ([FutureAGI](https://futureagi.com/blog/what-is-llm-input-output-validation-2026/), [GMO Flatt Security (JA)](https://blog.flatt.tech/entry/llm_guardrail)) |
| Pre-dispatch validator only (Leg A alone) | smallest diff | a malformed packet that slips past (hand-built dispatch, Codex path) still yields silent self-repair; verdict intake stays SHA-blind | SDK-level validators (Pydantic AI / Guardrails AI) pair input AND output checks ([Guardrails AI](https://www.guardrailsai.com/docs/concepts/concurrency), [glukhov.org](https://www.glukhov.org/llm-performance/benchmarks/llm-structured-output-validation-python/)) |
| Full PreToolUse hook interception of Task dispatches | strongest guarantee | parses free-form dispatch prompts — brittle; heavy for n=2 evidence; Codex has no equivalent hook | deferred — named as the conditional reversal |

## Decision

Build Legs A+B+C in one branch, Codex-parity by construction: every leg lives in shared SKILL.md prose, plugin Python scripts, or the regenerated SSOT — no Claude-only mechanism (frontmatter, hooks) on the main path. Regenerate agents via `distribute.py`; bump plugin version to 0.99.0. We will NOT build dispatch-prompt interception hooks, NOT widen the mintable verdict values, and NOT change the Codex adapter beyond what SSOT regeneration carries.

## Out of Scope

- PreToolUse hook interception of Task dispatch prompts (conditional reversal only).
- Backfilling packet validation into `live_host_review_gate.py` / release fixtures beyond keeping their existing checks green.
- The broader backlog entry `2026-07-20-loom-gate-hardening-deferred-ci-side-arc` (CI/server-side gate re-checks) — its start condition fires with this arc's `loom_gate_markers.py` touch; record that, do not execute it here.
- Reviewer behavior on other prose rules (checklist-loading compliance was 2/3 in live tests; separate evidence track, not legislated here).

## What Becomes Obsolete

- R0/R1a's "return no verdict" silence-refusal wording — replaced by the observable `MALFORMED_PACKET` contract in the same change (SSOT edit + regenerated agent files).
- Nothing else is removed; the packet producer, marker minter, and git-guard keep their interfaces.

## Open Questions

- OQ-1: should `review_context.py --validate` also verify `plugin_version` matches the installed plugin.json it was resolved from, or is field presence enough? (Default: presence + non-empty string; equality check is one line if the implementer finds it free.)

## Evidence paths appendix

- `loom-code/scripts/review_context.py` — packet producer (`resolve_context`).
- `loom-code/scripts/loom_gate_markers.py` — verdict schema + marker minter (`validate_verdict_text`, `ALLOWED_VERDICTS`, `_FULL_SHA_RE`).
- `loom-code/scripts/_reviewer-discipline.md` — reviewer rule SSOT (R0/R1a).
- `loom-code/scripts/distribute.py`, `loom-code/scripts/verify-drift.py` — SSOT injection + drift guard.
- `loom-code/scripts/live_gate_station_receipt.py` — reference packet-validation logic (`PACKET_KEYS`).
- `loom-code/skills/subagent-driven-development/SKILL.md`, `loom-code/skills/requesting-code-review/SKILL.md`, `loom-code/skills/requesting-docs-review/SKILL.md` — orchestrator call sites.
- `loom-code/hooks/git-guard.py` — push-time marker consumer.
- Live-test evidence: this session's sandbox runs (snapshot `MAX_RETRIES = 3` vs worktree `5`; malformed dispatch yielded derived-SHA + worktree-read + wrong `NEEDS_REVISION`).
