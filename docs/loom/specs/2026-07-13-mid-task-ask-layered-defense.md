# Brief: layered defense for mid-task decision asks (research-before-asking enforcement)

Date: 2026-07-13
Source: brainstorming (5-axis walk). Origin: user-reported recurring pattern —
mid-implementation agents surface decision forks to the user without the
mandated research; when the user manually orders "research industry practice
first", the fork collapses to a single recommended option. Rule exists in three
places (using-loom-code router rule #5, SDD §Asking gate ②, brainstorming
Axis-4) but is descriptive prose with no interception at the acting moment.

## Design-side on-ramp

Axis 0 negative guard — increment to existing loom-code mechanisms; skipped
silently.

## Problem

(Axis 1) The research-before-asking rule is read but not executed at the
moment it matters. Failure shape matches two committed store lessons:
`imperative-trigger-cards-beat-descriptive-preloads` (descriptive prose in
context moved behavior 0/2) and `pipeline-enforced-gates-beat-drafter-
instructions` (enforcement belongs in the pipeline, 22%→67%). Job to be done:
"when an agent hits a decision fork mid-task, foreseeable forks should already
be settled, and unforeseeable ones should reach me researched, recommended,
and batched — without me having to order the research myself."

## Users

(Axis 2) kouko + any-tier orchestrator sessions running loom-code work (SDD
and interactive); implementer subagents whose NEEDS_CONTEXT questions relay
through the orchestrator.

## Smallest End State

Three layers sharing ONE triage vocabulary (fact-in-repo → look it up /
user-fact·preference·irreversible-confirmation → ask directly / researchable
design fork → research first, then ask with a recommendation):

1. **L2 — ask-moment hook (the novel piece)**: new PreToolUse entry in
   `loom-code/hooks/hooks.json` with `"matcher": "AskUserQuestion"` (same
   shape as git-guard's) + `loom-code/hooks/ask-triage.py` emitting a static
   `hookSpecificOutput.additionalContext` card (MUST include `hookEventName`
   — repo gotcha). Card = the three-way triage as short imperatives, an
   explicit clearance line for confirmation-type asks (anti-over-deterrence:
   "confirmations and user-facts: ask freely — this card is not a reason to
   avoid asking"), and a pointer to SDD §Asking gate ② as SSOT.
   **Scope-leak patch (counter-review finding)**: plugin hooks register
   globally (git-guard precedent) — the card fires on EVERY AskUserQuestion
   in any session with loom-code enabled, including non-coding work. Card
   wording must be domain-NEUTRAL ("facts checkable within the task's own
   sources", not "explore the codebase") so a non-coding ask reads it as
   harmless; the clearance line carries the rest.
2. **L1 — kickoff fork harvest (lite, post-complexity-critique)**: extend
   `kickoff-briefing.md` (uncapped, 980w) §b sweep from "one-way-door
   decisions" to also sweep **foreseeable implementation forks** (per-task:
   unpinned library/pattern/format choices an implementer would otherwise
   hit); research is **pay-per-hit** (Axis-4-lite ONLY over researchable
   forks the sweep actually finds — a zero-fork plan pays nothing); fold
   results into the SAME single batched briefing (§c, unchanged); resolved
   forks land in the plan's EXISTING free-form `## Notes` section as
   `Kickoff decision: <fork> → <resolution>` lines (line format pinned in
   the kickoff-briefing §; greppable; NO plan-format.md schema change —
   complexity-critique PAGNI test: an internal schema section retrofits at
   zero penalty if the Notes convention proves insufficient, so the
   dedicated section is deferred, not designed in). `## Decision Log` keeps
   its runtime-only invariant untouched. writing-plans/SKILL.md §Kickoff
   briefing line gets a ~5-word scope update ("one-way-door decisions +
   foreseeable implementation forks").
   **Propagation patch (counter-review finding)**: SDD step 1's dispatch
   instruction gains one line — relevant `Kickoff decision:` lines from the
   plan's Notes ride the implementer's task packet; without this the
   decisions exist but never reach the executor.
3. **L3 — valve legitimacy**: implementer.md NEEDS_CONTEXT definition gains
   the legitimacy clause ("returning NEEDS_CONTEXT is always better than
   guessing — it is a correct outcome, not a failure"; mirrors
   PASS_WITH_NOTES's existing "use this freely" so the asymmetry that breeds
   silent guessing disappears) + the triage vocabulary. SDD step 2 relay
   gains one sentence: classify the relayed question per the triage before
   phrasing (researchable → research first per gate ②, already SSOT there).

Triage SSOT lives in SDD §Asking gate ① (extending the existing
"un-inferable intent" bullet into the named three-way rule); the L2 card
carries an operative restatement (sanctioned pattern — telemetry precedent:
pull-chains go unread, cf. brainstorming §Visual companion operative line);
implementer.md and kickoff-briefing.md point, not copy.

Version: loom-code 0.29.1 → 0.30.0 (new hook = feature) + CHANGELOG + codex
manifest sync (hooks are Claude-Code-only; .codex-plugin mirrors plugin.json
only — existing git-guard precedent, no new gap).

Verification: TDD on the hook script (pytest: output shape, hookEventName
present, valid JSON — lands in the CI-covered loom-code/scripts or hooks
path); cold-read dogfood of the card wording (weak-model agent given the
card + two scenarios — a confirmation ask and an unresearched design fork —
must let the first through untouched and research-first the second);
package suite green.

## Current State Evidence

- **Forward**: hooks registration at `loom-code/hooks/hooks.json:15-25`
  (PreToolUse matcher regex, git-guard shape); SessionStart card injection
  precedent at `loom-code/hooks/session-start:13,35`. kickoff-briefing.md
  structure: §a two-axis test (:19-28), §b sweep "expect 1-3 hits" (:37-41),
  §c ONE batched briefing (:44-47), §e Decision Log routing (:85-92), §f
  mid-implementation escalation — the L1↔L3 seam.
- **Reverse**: no existing consumer of a "kickoff decisions" concept;
  `## Decision Log` is runtime-only with the never-authors invariant pinned
  at plan-format.md:153-155 — reason the new section is separate.
- **Error**: hook failure mode = malformed JSON silently disables the hook
  (repo gotcha `hook 輸出 hookSpecificOutput 必帶 hookEventName`) — covered
  by the TDD shape test.
- **Data**: word counts — writing-plans/SKILL.md 4,086 (+414 headroom), SDD
  4,033 (+467), kickoff-briefing.md 980 (uncapped), implementer.md 2,673
  (uncapped). All pointer additions fit.
- **Boundary**: no fact/decision/researchable triage vocabulary exists yet
  anywhere in loom-code (nearest fragments: SDD gate ① "un-inferable
  intent", brainstorming confident-read rule) — the three-way rule is new
  vocabulary, not a rename.

## Alternatives Considered

(Axis 4 — EN+JA WebSearch, 5 shipped approaches + Pocock structural study)

1. **Front-loaded plan interview** — Claude Code Plan Mode/AskUserQuestion,
   GitHub Copilot Plan Mode, Devin plan-confidence, Google Jules (EN:
   code.claude.com agent-sdk/user-input; github.blog Agent HQ; docs.devin.ai).
   Industry mainstream. → ADOPTED as L1 (loom shape: kickoff-briefing
   extension). JA field note: Devin users report 仕様外判斷 still surfaces
   mid-run — front-loading alone insufficient, hence L2/L3.
2. **Structured mid-task ask as first-class tool** — AskUserQuestion,
   HumanLayer human_as_tool, AutoGen human_input_mode, LangGraph interrupt()
   (EN: humanlayer PyPI; microsoft.github.io/autogen). → ALREADY HAVE
   (NEEDS_CONTEXT + AskUserQuestion); L3 keeps it legitimate.
3. **Async escalate-or-continue** (Devin sleep/wake, Jules async-by-design)
   — REJECTED for now: loom sessions are interactive/attended; async queue
   is architecture we don't need (JA: licensecounter.jp Devin 檢證).
4. **Policy-tiered interrupts** — CyberAgent HITL measurement study (JA:
   developers.cyberagent.co.jp/blog/archives/64352/): 90 sessions, 106
   interventions, ~65% necessary / ~30% avoidable; their fix was STANDING
   POLICY, not threshold tuning; also quantified blocking-ask idle cost
   (median 74s, max 50+ min). → Strongest grounding for L1+L2 as policy.
5. **Ask-vs-act decision policies** (INTENT-SIM NAACL 2025, Learning to Ask
   EMNLP 2025, EVPI-based OpenReview 2026) — research-only, nothing shipped;
   their cascade insight (cheap filter first, expensive logic in the gray
   zone) shapes the L2 card's ordering. → NOT built; watch.
6. **Pocock structural prevention** (grilling front-load + decision-free
   implement + fact/decision dichotomy) — evaluated in-session: adopts the
   dichotomy sharpness and the batch-front-load HALF; rejects the
   "mid-task decisions don't exist" half (fog guarantees residual forks;
   prose-only + strong-model + human-present assumptions don't hold here).

**Honest no-hits**: no shipped "ask budget" (deliberately NOT inventing one);
no published confidence thresholds; **no shipped PreToolUse-hook-reshapes-the-
ask equivalent — L2 is novel** (nearest: LangGraph pauses without reshaping)
— treated as a dogfood-carefully flag, not a blocker.

**EN-JA disagreement (finding)**: EN ships the asking UI; JA quantifies the
operational cost of over-asking (CyberAgent 13-metric study). Both converge
on "policy over threshold".

**My take**: L2 first-class (novel but cheapest and directly precedented by
this repo's own trigger-card evidence), L1 as the industry-standard
frequency reducer, L3 as the two-line anti-perverse-incentive patch. All
three share one triage text or the rules will fight.

## Complexity critique + counter-review (2026-07-13/14, both run pre-plan)

`dev-workflow:complexity-critique` (PAGNI mindset) verdict **RESHAPE**,
applied above: L1 slimmed (no plan-format.md change, `## Notes` line
convention, pay-per-hit research); named trade-off ≈ +125-130 lines, 1 new
mechanism (the hook), buying interception at the single user-facing-ask
choke point. Q3 bonus REJECTED on inspection: trimming `hooks/router-card.md`
rule #5 to a pointer would open a coverage hole — the L2 hook fires only on
the AskUserQuestion TOOL call, while rule #5 also governs prose-form asks,
which no hook can intercept; the card line stays as the prose-ask coverage.
Counter-review (completeness/stability pass) added the two
patches now embedded in §Smallest End State (dispatch propagation;
domain-neutral card wording) — both versions of the design needed them.
Lite→full upgrade is penalty-free (internal schema), making lite the
reversible choice.

## Decision

Build L1(lite)+L2+L3 as scoped in §Smallest End State, in one branch (they
share the triage vocabulary — splitting would ship a dangling SSOT). NOT
build: ask budgets, async question queues, confidence thresholds, Codex-side
hook (no hook primitive there), changes to brainstorming/Axis-4 protocol
(already correct), any Decision Log semantic change, any plan-format.md
change (deferred per PAGNI — retrofit is penalty-free).

## Out of Scope

- Applying the triage card to other plugins' ask surfaces (investing-toolkit
  etc.) — revisit after loom-code dogfood.
- Telemetry A/B of the card (ride the existing ascii-graph BACKLOG re-run
  pattern later; ship first).
- The wayfinder-style persistent decision-map (separate future arc).
- Fixing gate ② prose itself (it is already correct; it becomes the SSOT).

## What Becomes Obsolete

(Axis 5) The auto-memory entry
`feedback_mid_task_asks_skip_research_before_asking` gets superseded-noted
once shipped (its "修復候選未立案" line). No repo file is deleted; the L2
card is additive, and its anti-over-deterrence line is the guard against the
card itself becoming negative-value. Purely-additive flag answered by: the
user-reported recurrence + CyberAgent's 30%-avoidable measurement = demand
is empirical, not speculative.

## Open Questions

(none — L1 output home decided as the existing `## Notes` section's
`Kickoff decision:` line convention (post-complexity-critique; the dedicated
section was deferred per PAGNI); L2 card wording drafted at implementation
and cold-read dogfooded before ship.)
