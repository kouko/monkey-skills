# Brief: progress cards + plan ledger default-on (user visibility × agent anchoring)

Date: 2026-08-06
Status: FROZEN (user: 「好」 after four design rounds + two industry
research passes; endpoint = PR, continuous)
Consumer: writing-plans → SDD; ships as loom-code 0.60.0 +
loom-pipeline 0.13.0

## Problem

Loom's progress machinery is strong after-the-fact (plans, Decision
Logs, PR bodies) and weak in-the-moment: the plan's Progress ledger is
opt-in and has never been used; there is no Stage-level state; and
0.58.0's continuous mode removed the pump stops that used to double as
progress reports — the user watches long arcs through ephemeral
narration, and their mid-arc questions ("這一輪做了哪些") are the
symptom. Meanwhile the orchestrator's goal awareness degrades across
context compactions (this session compacted twice mid-arc).

Industry evidence (EN+JP survey, 2026-08-06): every project solving
both visibility and drift uses an external checkbox-bearing plan
artifact that is (1) re-read at defined checkpoints — never trusted
from memory (Anthropic write-out-then-reread; beads mutable-state
file), and (2) re-injected into recent attention (Manus todo.md
recitation). Goal drift happens well before context exhaustion (every
tool output competes with the goal for attention), so cadence must be
wave-level, not stage-level. Zero quantitative validation exists
industry-wide — verification is behavioral probes + a deferred
re-measurement metric.

Cost/mechanization stance (user-ratified): state updates = LLM
judgment; card RENDERING = deterministic script (`plan_card.py`, same
philosophy as `--ready`); trigger = command-shaped duty sentences
(action-type prose survives weak models; industry: "LLMs consistently
forget" descriptive prose). Cards are advisory-tier — no hook
dependency; Codex ships no hook (repo-level hooks subject to the open
silent-no-fire bug; asymmetry accepted per industry three-layer model).

## Users

- The user mid-arc: sees the full plan + live progress at defined
  moments without asking.
- The orchestrator: every card generation is a forced re-read of the
  plan file — goal re-anchoring that survives compaction.
- Weak-tier orchestrators (probe-gated) and Codex hosts (host-neutral
  by construction: file + script + duty sentences).

## Smallest End State

Partition A — plan format carries the state (writing-plans):
1. `references/plan-format.md`: the header schema gains `Goal:` (one
   sentence transcribed from the brief's Smallest End State at plan
   time; never edited after freeze) and `Stage:` (enum: planning /
   sdd:wave-N / review:round-N / finishing; updated by the orchestrator
   at transitions, committed with the nearest ledger/close-out commit);
   the Progress ledger `Status:` field flips from opt-in to
   DEFAULT-ON (writing-plans emits `Status: pending` per task; the
   existing SDD write-back protocol is unchanged). Named deliverables:
   schema text + defaults note + pin test.
2. `writing-plans/SKILL.md`: the minimal-structure block shows
   `Goal:`/`Stage:`/`Status:`; a one-sentence emit duty. Ceiling note:
   current 3874 vs 3900 pin — if the edit exceeds headroom, RAISE the
   ceiling in test_wp_extraction_pointers.py as a deliberate,
   changelog-noted act (the banked-headroom mechanism working as
   designed). Named deliverables: block edit + duty sentence + pin
   adjustments.

Partition B — the renderer (repo-root script, host-neutral):
3. `scripts/plan_card.py <plan-path>`: reads Goal/Stage/Status (+ task
   names) from the plan file and prints the card body — Goal line
   first, then a task table (✅ done / ⏳ claimed / ⬜ pending / 🚫
   blocked with counts), current Stage, and `next:` (the first
   non-done task, or "close-out" when all done). Exit 1 with a loud
   message when the plan lacks the header fields (never render a
   half-card silently). Tests RED-first, same conventions as
   backlog_index's (tmp fixtures; error path; empty/all-done shapes).

Partition C — the duty moments (three skills + template):
4. `writing-plans/SKILL.md` (plan PASS moment): after the reviewer
   PASS + verdict stamp, run `python3 scripts/plan_card.py <plan>` and
   relay the card in the conversation language — fire-and-continue,
   not a new pause. (Rides the same edit as item 2.)
5. `subagent-driven-development/SKILL.md` (wave cadence): the existing
   §Delivery form paragraph upgrades — every per-wave rollup and stage
   transition renders the card via `plan_card.py` (fill-from-file is
   thereby mechanical) and relays it per the family-relay progress-card
   variant; the Stage: header update duty lands in the same paragraph.
   Ceiling: current 3897 vs 3900 pin — this edit REQUIRES a deliberate
   ceiling raise in test_sdd_extraction_pointers.py (changelog-noted).
   Named deliverables: paragraph rewrite + Stage duty + ceiling raise +
   pin test.
6. `finishing-a-development-branch/SKILL.md` (entry + gate stops): one
   sentence at entry (render the card once on entering the close-out —
   the user sees the whole arc before the gates run) and one clause on
   the gate-STOP paths (a NEEDS_REVISION/BLOCK surface includes the
   card so the user sees where the arc stopped). Step 13's queue-tail
   line unchanged. Named deliverables: two small edits + pin test.
7. `loom-pipeline/hooks/family-relay.md`: §(a) User-rollup card gains
   the progress-card variant (field order: Goal / task table / Stage /
   next; localized framing rule same as the rollup card). Duty
   sentences in items 4-6 carry the four field names inline
   (degradation path: family-relay absent → render fields inline
   plain) and point here for styling only. loom-pipeline → 0.13.0.
   Named deliverables: variant block + both plugin manifest bumps'
   coordination.

Partition D — ride-along + bump + verification:
8. `docs/loom/backlog/2026-07-06-codex-hook-events-apply-patch-handler-emits-none.md`:
   body updated with the researched upstream state (apply_patch
   handler fixed by openai/codex PR #18289 merged 2026-04-20; the
   probed symptom likely the still-open repo-local-config silent
   no-fire bug #17532; UPSTREAM status stays), with an evidence line
   per the sweep convention.
9. loom-code → 0.60.0 (manifests + CHANGELOG + shipping-version pin
   rewrite); loom-pipeline → 0.13.0 (manifest + its CHANGELOG).
10. Haiku probes: (a) given a rendered card + the plan file, answer
    goal / who's done / what's next; (b) SDD wave-completion duty —
    what command runs and what gets relayed; (c) fill-from-file
    comprehension — why may the card never be written from memory,
    and what happens when family-relay.md is absent (inline fields,
    nothing dropped). Dogfood report under docs/loom/dogfood/.

## Alternatives considered

- Standalone progress skill: rejected — cards are duties at moments
  inside existing flows, not user-routed intents; a skill shell would
  still need per-moment routing in the hosts.
- LLM-rendered cards (no script): rejected on cost+hallucination; the
  attention-recitation value survives because the card still flows
  through context — only formatting is mechanized (industry split:
  state=LLM, projection=mechanical).
- Second machine-readable state file (JP STATE.md dual-file pattern):
  rejected — plan header/ledger IS the machine-readable layer; a
  second file reintroduces dual-copy drift.
- Codex-side hook trigger: rejected — plugin-shipped hooks have no
  auto-registration path on Codex; repo-level hooks subject to the
  open silent-no-fire bug; cards are advisory-tier so prose duties +
  script suffice (industry: enforcement belongs to git/CI, which loom
  already has).
- CC-side reminder hook (PostToolUse on plan Status edits): deferred
  to Out of scope — optional insurance, add only if probes or live use
  show the duty sentence failing.

## What becomes obsolete

Nothing removed. The opt-in ledger semantics remain valid for old
plans (no Status field → behaves as before); recap-state/handoff stay
the pull-side complements.

## Out of scope

- CC reminder hook (insurance layer — first live miss reopens it).
- Retro-fitting Goal:/Stage:/Status: into existing plan files.
- Post-hoc effectiveness measurement (the mid-arc-question-frequency
  metric — re-run the pump-phrase mining after some arcs; recorded
  here as the deferred success metric, not built now).
- Codex live verification of the new duties (next Codex session,
  per host-scope precedent).
- loom-pipeline conductor-side card integration (its stations are
  Workflow-driven; separate arc if wanted).

## Decisions

- Dual-audience mechanics named explicitly: the card's Goal-first
  layout serves the human scan; the agent's anchoring comes from the
  card being PRODUCED (rendered output entering recent context = the
  Manus recitation position) — first-line-vs-tail is not a conflict
  because the two audiences get the goal through different mechanisms.
- fill-from-file is enforced mechanically: the duty is "run
  plan_card.py", and the script can only read the file — "never from
  memory" needs no prose prohibition beyond the command itself.
- Ceiling raises (SDD mandatory, wp if needed) are deliberate acts:
  new ceilings pinned at (new count + small margin), noted in the
  CHANGELOG entry — the banked-headroom contract from the extraction
  arcs honored, not bypassed.
- Cross-plugin coordination: loom-code duties reference
  family-relay.md by name with inline-fallback fields; loom-pipeline
  bumps in the same PR (both manifests; the repo's version-bump rule
  applies to every plugin whose content changes).
- Counting convention `len(text.split())`; ceilings verified at plan
  time: wp 3874/3900, SDD 3897/3900 (raise required), finishing
  4113/4500, plan-format is a reference (uncapped), family-relay 698
  (uncapped, hooks file).
