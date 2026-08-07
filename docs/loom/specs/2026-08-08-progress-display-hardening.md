# Brief: progress-display hardening — card rendering bound to ledger actions + host todo mirror

Date: 2026-08-08
Design-side on-ramp: N/A — mechanism increment on loom-code's own process layer (negative guard: not product-shaped); Backlog ready check ran (COMMITTED-NEXT empty; DIRECTION.md `## Next` themes unrelated — queue informs, not hijacks).
Endpoint named: yes → continuous (/goal「現在就把進度顯示的相關功能修好吧」issued immediately after user ratified the three-layer proposal in conversation; PR-open terminal; never auto-merge).

## Problem

When a long arc runs (SDD waves, review rounds, finishing), the user wants to glance and know where progress stands without reading long messages. Both display channels are currently failing:

1. The progress card (0.60.0 arc) is a prose duty ("every per-wave status report … renders the card first") whose trigger vocabulary does not match the real conversational unit — notification-driven sessions produce many small status notes, none of which feels like a "status report", so the duty under-fires. Measured in the direction-layer session (2026-08-08): 5+ stage flips, 2 cards rendered; the whole-branch NEEDS_REVISION gate STOP led with prose despite finishing's explicit card-first rule.
2. Claude Code's built-in todo list — the host-native, always-visible progress surface every vanilla session gets — is displaced by loom's plan-file ledger and never used, so loom arcs show LESS live progress than sessions with no tooling at all.

JTBD: 「當一個多小時的 arc 掛著跑時，我瞄一眼就要知道進行到哪——不用讀長訊息。」

## Users

- kouko, primarily on Claude Code (desktop/CLI) where the built-in todo list renders natively; also Codex hosts (no task tools — nothing may hard-depend on them).
- Operators are orchestrator agents mid-arc; the mechanism must survive weak-prose-obligation decay (repo lesson: 需判斷的散文死、指向可查動作的散文活).

## Smallest End State

1. **`scripts/plan_card.py` — ledger actions print the card.**
   - `--set-status "T<N>=<status>"` keeps its `old:`/`new:` lines and, after them, prints a blank line + the full rendered card (same body `build_card` produces). The flip action itself puts the card in front of the orchestrator; the relay duty shrinks from "remember to render" to "relay what the script just printed".
   - New `--set-stage "<text>"`: sets the `Stage:` header (free text — stage vocabulary evolves: `sdd:wave-N`, `review:round-N`, `finishing`), prints `old:`/`new:` + card. Refuses (FAIL, exit nonzero) when the plan lacks a `Stage:` header or the value is empty/whitespace. Replaces the hand-edit path rcr currently mandates.
   - `_USAGE` updated. All RED-first; the 5 exact-stdout pins in scripts/test_plan_card.py (:727-730, :758-761, :777-780, :793-796, :812-815) are updated to expect the card, plus new tests: --set-stage happy path, refusal on missing Stage header, refusal on empty value, card presence in both actions' stdout.
2. **SDD SKILL.md §Delivery form — duty rebound to the mechanical act.** Reword the operative sentence (loom-code/skills/subagent-driven-development/SKILL.md:54-56): the ledger actions (`--set-status`/`--set-stage`) print the card; ANY turn that runs one relays that card (family-relay §(a2) frame, live conversation language) in its user-facing text; wave reports / stage transitions / checkpoint sign-offs flip the ledger via the script, so the card rides them by construction. Inline fallback (script absent → four fields inline) stays.
3. **SDD SKILL.md — host todo mirror (conditional, display-only).** New short paragraph in §Delivery form: when the host provides built-in task tools (TaskCreate/TaskUpdate), mirror the plan's tasks into the todo list when SDD starts consuming the plan, and update each mirrored task's status in the same turn as its ledger flip. The mirror is a one-way display projection — the plan file's Status ledger stays the SSOT; the todo list is never read back. Hosts without task tools → skip silently (same conditional posture as the DIRECTION.md reads). Codex-safe by construction.
4. **rcr SKILL.md — stage flips go through the script.** Replace the sentence at loom-code/skills/requesting-code-review/SKILL.md:85: rounds update the Stage via `python3 scripts/plan_card.py --set-stage "review:round-N"` (the script prints the card — relay it), committed with that round's verdict or fixes; hand-edit only when the script is absent.
5. **Pins updated in lockstep** (all RED-first): test_review_stage_flip_duty.py (:26-27, :37-39 — the "no stage setter" claim becomes false), test_sdd_progress_card_duty.py (:42-63 window), test_sdd_extraction_pointers.py (:275-280 "hand-edit only when the script is absent" — verify window still true), test_wp_extraction_pointers.py (:161-173 — verify untouched claims stay true).
6. **loom-code 0.70.0** + CHANGELOG + version-pin migration `_0_69_0` → `_0_70_0`.

## Current State Evidence

- Forward: plan_card.py `--set-status` prints only `old:`/`new:` and returns 0 (scripts/plan_card.py:517-522); `build_card` renders the full card (:306-385); `main()` hand-rolled argv (:490-528); no `--set-stage` exists (grep clean); `Stage:` parsed via `_header_value` (:319-320, raises on absence).
- Reverse: family-relay §(a2) (loom-pipeline/hooks/family-relay.md:67-87) already assigns body-rendering to the script and reserves only the frame for the relayer (:78-80) — NO edit needed there; finishing's card duties (:102-107, :300) stay true — NO edit needed.
- Error: plan_card failures print `plan_card: FAIL — <reason>` and exit nonzero (pinned convention, scripts/test_plan_card.py); set_status grammar regex :430-433.
- Data: SDD Delivery form operative sentence at SKILL.md:54-56; ledger duty :112; back-reference :173. rcr hand-edit sentence :85 (verbatim, includes "plan_card.py has no stage setter").
- Boundary (pins): scripts/test_plan_card.py 39 tests, 5 exact-stdout set-status pins (lines above); test_review_stage_flip_duty.py pins the no-stage-setter claim; test_sdd_progress_card_duty.py pins the Delivery-form sentence + command string + §(a2) pointer; test_plan_format_progress_fields.py runs real plan_card end-to-end (:225-237).
- Evidence paths: scripts/plan_card.py · scripts/test_plan_card.py · loom-code/skills/subagent-driven-development/SKILL.md · loom-code/skills/requesting-code-review/SKILL.md · loom-code/skills/finishing-a-development-branch/SKILL.md · loom-pipeline/hooks/family-relay.md · loom-code/scripts/test_{review_stage_flip_duty,sdd_progress_card_duty,sdd_extraction_pointers,wp_extraction_pointers,finishing_progress_card,plan_format_progress_fields,docs_review_blocking_class}.py

## Alternatives Considered

- **Script-print + todo mirror (chosen)** — binds the display duty to acts that already happen every wave (statuses flow through the script; the todo list is the host's own always-visible surface). Judgment-shaped prose obligation → verifiable action; zero new infrastructure.
- **PostToolUse hook reminder on ledger actions** — rejected as redundant once the script itself prints the card (deletion-first); revisit only if under-firing recurs after this arc.
- **Reword expectations down (cards only at wave boundaries)** — rejected: honest but does not restore visibility; user's complaint is precisely the low frequency.
- Grounding: the 0.60.0 arc's industry research (state-in-ledger, deterministic projection — Manus recitation / Anthropic reread) still holds; the todo-mirror addition follows the host's own documented TaskCreate guidance (proactive tracking for multi-step work). No new web research — no open design fork remains (user ratified the three-layer proposal in conversation).

## What Becomes Obsolete

- rcr's hand-edit instruction ("plan_card.py has no stage setter") — replaced in the same change; its pin test forces the lockstep.
- The Delivery form's "remember to render at report moments" framing — replaced by the mechanical binding; no other artifact states it (finishing/§(a2) survive unchanged).

## Decision

Build 1-6 above as one arc on feat/progress-display-hardening; loom-code bumps to 0.70.0. Do NOT touch family-relay.md (no sentence becomes false), finishing SKILL.md (duties stay true), or loom-pipeline's version. Do NOT add a hook layer. The todo mirror is display-only and host-conditional; the plan ledger remains the only SSOT.

## Out of Scope

- Any read-back from the todo list into the ledger (one-way projection only).
- Codex-side equivalents (no task tools there; cards remain the only channel).
- finishing/family-relay wording changes; hook-based enforcement; plan_card rendering redesign (fields/order unchanged).
- Backfilling cards into other repos (mechanism ships in monkey-skills scripts/ as today).

## Open Questions

- None blocking. (Stage vocabulary intentionally left free-text in --set-stage; validation is presence+non-empty only.)
