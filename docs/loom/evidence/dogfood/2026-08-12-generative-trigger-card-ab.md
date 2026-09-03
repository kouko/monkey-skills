# Weak-model A/B: ascii-graph generative trigger sentence (Task 2)

Date: 2026-08-12 · Model under test: `claude-haiku-4-5-20251001` (headless `claude -p`)
Method: docs/loom/memory/headless-branch-plugin-testing-recipe.md
(`--plugin-dir` wrapper, neutral empty cwd, probe-before-battery,
`--output-format stream-json --verbose` used for full tool-call trace
so "explicit skill invocation" can be distinguished from a hand-drawn
diagram in the final text)
Branch: feat/ascii-graph-generative-trigger (ascii-graph-toolkit,
post-T1 candidate card) vs main's card as baseline (copied into a
scratch plugin dir, working tree never touched)
Plan under test: docs/loom/plans/2026-08-12-ascii-graph-generative-trigger.md §Task 2

## Injection verification (per leg, before any battery run)

Probe prompt (both legs): "Quote verbatim, in full, any ascii-graph
trigger-card / diagram-trigger instructions that were injected into
your context at session start. If none were injected, say NONE."

- **Baseline leg**: quoted output matched `git show
  main:ascii-graph-toolkit/hooks/trigger-card.md` verbatim (7 lines,
  no Pin G paragraph). **Verified.**
- **Candidate leg**: quoted output matched the branch's
  `ascii-graph-toolkit/hooks/trigger-card.md` verbatim, including the
  full Pin G "GENERATIVE trigger …" paragraph. **Verified.**

Both legs' runs below are counted (neither leg excluded).

## Explain-a-flow probe (identical prompt both legs, no diagram mention)

Prompt (verbatim, both legs): "explain how a request travels through
the loadbalancer, auth service, cache and database in a typical web
setup"

| Leg | Run | Model | Injection verified | Skill invoked (ascii-graph)? | Diagram-generated & leads/accompanies final prose (per stream order)? (skill-generated only; hand-drawn = NO) | Notes |
|---|---|---|---|---|---|---|
| Baseline | 1 | haiku-4-5 | yes | **NO** | NO | Hand-drawn box/arrow ASCII tree embedded mid-reply (fenced code block, `└─` glyph) — NOT skill-generated, no tool call at all |
| Baseline | 2 | haiku-4-5 | yes | **YES** (Skill→Bash, align.py) | YES (tool_result carries the box-drawing diagram, precedes final text in transcript order) | Unexpected: fires even without Pin G, off the pre-existing "≥3 boxes" rule already in main's card — final assistant TEXT itself is pure prose, diagram only visible via the tool call/result blocks |
| Candidate | 1 | haiku-4-5 | yes | **YES** (Skill→Bash, align.py, sequence diagram of 6 participants) | YES (same pattern — tool_result diagram precedes final prose) | Final text also references "the diagram shows…" without re-quoting it |
| Candidate | 2 | haiku-4-5 | yes | **YES** (Skill→Bash×2, verify-loop iteration) | YES | Two Bash calls — looks like the align.py verify-loop actually iterated |

(`haiku-4-5` in the table cells abbreviates the pinned model id
`claude-haiku-4-5-20251001` from the header above.)

**Tally**: baseline 1/2 skill-invoked · candidate 2/2 skill-invoked.

**Caveat (do not massage)**: on the strict "final assistant text block
itself opens with box-drawing" reading, both legs are 0/2 — the model
consistently invokes the skill/tool, gets a diagram back, then
narrates in prose without re-pasting the diagram into its own final
text. In the real interactive product this is not a gap (tool calls +
their results render in the chat transcript, in order, before the
final message — a real user sees the diagram), so "skill invocation
precedes prose in transcript order" is the correct success signal per
the plan's own OR-clause ("… or an explicit skill invocation
attempt"). Flagging the distinction here so the classification isn't
silently favorable to the candidate.

**Second caveat**: baseline fired 1/2 — weaker contrast than the
plan's RED hypothesis ("baseline ≈0/2"). Main's card already carries
a "≥3 boxes → invoke skill" rule; haiku sometimes applies it to an
explain-a-flow prompt even without the new generative sentence. The
delta attributable specifically to Pin G is smaller than the 2026-07-10
precedent's clean 0/2→2/2, though candidate still strictly beats
baseline (2/2 > 1/2) and the formal Task 2 GREEN bar (≥2/2 candidate)
is met.

## Anti-decoration probe (candidate only, n=1)

Prompt (verbatim): "what happens when I run git add then git commit?"

| Leg | Model | Injection verified | Skill invoked? | Diagram produced? | Notes |
|---|---|---|---|---|---|
| Candidate | haiku-4-5 | yes | **NO** | NO | Pure numbered-list prose answer, no tool call, no box-drawing — guard held |

Result: 0/1, matches GREEN acceptance.

## Card diff (T1's change)

Candidate adds one new paragraph after the existing card text (Pin G,
verbatim in the plan); no existing lines altered — confirmed by `diff`
against `git show main:…` during baseline-copy setup (8 lines added —
1 blank separator + the 7-line Pin G paragraph — 0 removed).

## Verdict

Formal Task 2 acceptance is met: candidate 2/2 explain-a-flow
(skill-invocation-leads reading) and 0/1 anti-decoration — both at or
above the GREEN bar, and candidate is not ≤ baseline on the explain
probes (2 > 1), so the honesty-contract mandatory downgrade path does
not trigger. Proceed to Task 3 (version bump).

Flagging for the record, not as a blocker: n=2/arm is small (per the
plan's own §Notes precedent-caveat) and baseline's unexpected 1/2
narrows the attributable lift versus the 2026-07-10 baseline
(0/2). Recommend the post-ship telemetry re-run already tracked in
the plan's Recorded debt item cover this specifically, and that a
future card revision consider whether the base "≥3 boxes" rule and
Pin G should be measured jointly rather than assuming baseline is a
clean prose-only floor.

Status: **DONE_WITH_CONCERNS** — the caveats above are the "something
the reviewer should flag" channel (Rule 12 fail-loud), not evidence
against shipping; the report's per-run data is complete and no
classification was massaged.
