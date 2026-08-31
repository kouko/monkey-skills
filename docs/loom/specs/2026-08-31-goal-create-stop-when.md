# goal-create Stop-when repair — brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-08-31
> **Author**: agent (Fable 5) with kouko

## Design-side on-ramp

not fired — negative guard: a contract repair of an existing skill's prose and its checker, covered by the skill's own test files; not product-shaped, no user-facing surface, no new multi-state behaviour

## Queue relation

unqueued — this arc started from a usage review of goal-create's seven real invocations, not from the queue; the backlog entry whose start condition it trips (`2026-08-28-one-test-function-bundles-fifteen-independent-claims`, "the next arc that touches goal-create's input-floor contract", already `status: closed` under amnesty-2026-08-30 so not citable as `in-queue:`) is worked here as a rider the user accepted at sign-off (BI-8)

## Problem

When I hand a long-running agent run a goal drafted by `goal-create`, I want the run to push the whole piece of work to its end and stop only when the work is done or a hard bound is hit, so I can walk away without the run either quitting early on a "needs a human" exit or running past its bound because the evaluator never read that bound as completion.

## Users

- **Repo owner driving loom arcs (kouko)** — runs goals in Claude Code `/goal`; wants a run to reach the PR, not to hand decisions back mid-way. Willing to correct a run's decision after the fact rather than be asked before it.
- **The drafting agent inside `goal-create` SESSION mode** — reads `references/goal-shape.md` and `references/input-floor.md` once per invocation; needs a rule that says where a human-dependent fork goes, not only that it is disallowed.
- **The `/goal` evaluator (small fast model)** — reads only the conversation, returns Not yet met / Met / Impossible; needs a bound phrased as a completion condition it can mark Met, not as a permission it may ignore.

## Smallest End State

- BI-1 — `references/goal-shape.md` §4 defines `Stop-when` as exactly one mechanical bound (turn or wall-clock), phrased so that reaching the bound and posting a status report is itself a completion condition ("… — reaching it with a report posted counts as the run completing, as a failure report"), and states why: a bare "stop after N turns" is read by the evaluator as permission to stop, not as the condition being met, so it neither releases the run nor bounds it.
- BI-2 — `references/input-floor.md` §4 item 3 gains the remedy for a human-dependent fork: it never becomes a `Stop-when` branch; the goal pre-decides it in `Constraints`, or delegates it to the run with a standing rule ("choices the goal does not pre-decide are the run's to make: search first, decide, record decision + sources in a named file, never stop to ask"). Only an irreversible or outward-facing act (merge, deploy, send) sits outside the run — and that is already where `Outcome` ends.
- BI-3 — `goal-shape.md` §2 (`Constraints`) carries that standing decision rule as a default entry SESSION mode emits, tagged per input-floor §5, so a user does not have to remember to write it each time.
- BI-4 — `scripts/goal_lint.py` warns (never fails) when `Stop-when` contains no numeric bound (no digit) — a syntactic feature, not a stop-word list, per the repo's own record that word lists are defeated by the next word.
- BI-5 — Evidence: the two-run experiment of 2026-08-31 in this session — a goal with a decidable fork was completed without asking the user (searched once, decided, recorded three source URLs); a goal with an unreachable Outcome and the new Stop-when phrasing was released by the evaluator at turn 2 after the failure report, with the evaluator's own reason text counting turns against the bound.
- BI-8 — Rider (user-accepted 2026-08-31): `scripts/test_input_floor.py`'s `test_defines_slots_refusal_bar_and_provenance` (359 lines, ~15 separable claims) is regrouped into one test per claim, named for the claim, sharing the file's existing section-extraction helpers; every verbatim pin moves unchanged, no assertion weakened or dropped, and the split is by *claim*, not by source paragraph. Pure test refactor — no production or prose behaviour changes.

Non-criteria: this arc does not change how often `goal-create` fires, does not measure rework saved, and does not touch ARC mode.

## Current State Evidence

- **Forward**: `references/goal-shape.md` `## 4 — Stop-when` — "Bounds the run." + "for example a turn clause such as 'or stop after 20 turns.'" is the whole definition; nothing says one bound, nothing says the bound is a completion condition. Every real SESSION goal (7 invocations, 4 sessions) inflated it to 3–6 OR-branches including "if a human decision is needed, stop and report" exits.
- **Reverse**: `SKILL.md` `## SESSION mode` — "SESSION emits the four-field goal condition defined in `references/goal-shape.md`" and "read `references/input-floor.md` for … the provenance tag every field must carry"; `loom-workflow/README*.md` row `goal-create` names the four fields only (no semantics) — no README wording changes.
- **Error**: `references/input-floor.md` `## 4 — The bar` item 3 "**Free of dependence on a person**" says such a condition "makes it their goal, not the run's" — a prohibition with no destination, which is where the agent's instinct to park it in `Stop-when` comes from. `scripts/goal_lint.py` module docstring: "`Stop-when` is covered only by the field-presence check — no word list stands in".
- **Data**: goal text (≤4,000 chars) pasted by the user into `/goal`; `goal_lint.py` `FIELD_LABELS = ["Outcome", "Constraints", "Verification", "Stop-when"]` unchanged; tri-language label fixtures in `scripts/test_goal_lint_languages.py` ("Stop-when: 達成目標即停止，或跑滿 20 輪後停止。") stay valid under a warning-only check.
- **Boundary**: `[API]` Claude Code `/goal` evaluator — vendor doc "Write an effective condition": "To bound how long a goal runs, include a turn or time clause in the condition … the evaluator judges it from the conversation"; verdicts "Not yet met / Met / Impossible". `[FRAGILE]` `scripts/test_goal_shape.py` pins `"turn" in content_lower` for §4 and the vendor-attribution paragraph ("this skill's own choice"; negative guard on "both … require"); `scripts/test_input_floor.py` pins item 3's "person acting or answering" sentence — both must survive.
- **Evidence paths**:
  - `loom-workflow/skills/goal-create/references/goal-shape.md` — `## 4 — Stop-when`, `## 2 — Constraints`, attribution paragraph "this skill's own choice"
  - `loom-workflow/skills/goal-create/references/input-floor.md` — `## 4 — The bar` item 3, `## 5 — Provenance tags`
  - `loom-workflow/skills/goal-create/SKILL.md` — `## SESSION mode`
  - `loom-workflow/skills/goal-create/scripts/goal_lint.py` — module docstring, `FIELD_LABELS`
  - `loom-workflow/skills/goal-create/scripts/test_goal_shape.py` — "Stop-when must give a turn-clause example bounding the run."
  - `loom-workflow/skills/goal-create/scripts/test_input_floor.py` — "The bar must state the condition must not depend on a person"
  - `loom-workflow/skills/goal-create/scripts/test_goal_lint.py` — "No hard failure ever fires for Stop-when's content"
  - `docs/loom/memory/a-list-of-forbidden-words-is-defeated-by-the-word-outside-it.md`
  - session transcripts (usage evidence): `~/.claude/projects/*/b73d44a6*.jsonl` @391, `9baf33e5*.jsonl` @667/@718/@2111/@3952/@6370, `50cdbb50*.jsonl` @11225/@13071/@13072
  - https://code.claude.com/docs/en/goal — "Write an effective condition", "How evaluation works"

## Decision

- BI-6 — Keep the four-field shape and repair what `Stop-when` and the person-dependence rule say. `Stop-when` becomes one mechanical bound written as a completion condition; a human-dependent fork is resolved *before* the run (pre-decided in `Constraints`, or delegated to the run under the standing search-decide-record rule) and never becomes an exit; the linter gains one syntactic warning. We do NOT drop `Stop-when` (the vendor-shared three-field shape) — it costs `FIELD_LABELS`, tri-language fixtures, three READMEs and the #748 attribution paragraph, and does not remove the misuse, which would move into `Outcome`'s OR-clause unchanged. We do NOT add a stop-word or branch-count check. Trade-off accepted: the run will make decisions the user might have made differently; correction moves from before the decision to after it, which is the user's stated preference.

## Out of Scope

- Provenance tags leaking into the pasteable `/goal` block (a separate cleanliness fix; cheap, but not what stopped the runs)
- Mode selection (SESSION vs ARC) via `AskUserQuestion` instead of prose
- The "drafted but never installed" gap — the skill cannot invoke `/goal`; only the user can
- Confirmation prompts that come from loom-code gates (push, rebase) — not goal-create's
- ARC mode (`PURPOSE.md` `Why` / `Done when`)
- Codex `/goal` behaviour — no Codex invocation exists yet to ground a change against
- Any other test-file restructuring in goal-create beyond BI-8's one function (the other three test functions in `test_input_floor.py` and the sibling test files stay as they are)

## Alternatives Considered

My take: **Recommend** the repair above. **Why**: the failure is in what the two reference files tell the drafting agent, not in the shape; the experiment showed the evaluator honours a bound written as a completion condition. **Conditional reversal**: if a second, blind-run experiment (a fresh session, same goal text) shows the run still stops to ask despite the standing rule, the rule is prose that does not hold and the fix must move to the evaluator side (a custom Stop hook), which this arc does not build.

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| Status quo — thin §4 plus agent judgement | goal-create v0.1.0 (#748) | 7/7 real goals inflated Stop-when; two failure modes observed (early stop; never stops) |
| Drop `Stop-when`; bound inside `Outcome` as "or stop after 20 turns" | Anthropic `/goal` docs (EN): "include a turn or time clause in the condition" | Same misuse relocates to `Outcome`'s OR-clause; reverses #748; touches `FIELD_LABELS`, tri-language fixtures, 3 READMEs |
| Completion condition + iteration cap as two separate mechanisms | Agentic-loop guidance (EN: MindStudio, datasciencedojo; JA: Zenn/Qiita 「最大ステップ数＋タイムアウト＋同一ツール連続呼び出し制限」) | `/goal` has no separate cap knob; the cap must live in the condition text, which is what BI-1 writes |
| Stop-word / OR-branch count lint on `Stop-when` | My own first proposal | Repo memory: a forbidden-word list is defeated by the next word; #748 already removed one such list from this linter |

EN and JA sources agree on "completion condition + hard cap, both"; neither says anything about human-decision forks — the fork rule (BI-2/BI-3) is this skill's own choice, as the fourth field already is.

## What Becomes Obsolete

- BI-7 — The "needs a human decision → stop and report" exit branch pattern, which every real SESSION goal carried; after this arc a drafted goal has no such branch to copy from.

## Open Questions

(empty — the wording of the standing rule and the warning message are plan-level detail)

## Diagrams

N/A — two prose-rule edits and one warning line; no flow, state, or architecture changes to draw.
