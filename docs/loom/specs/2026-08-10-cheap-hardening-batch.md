# Brief: cheap hardening batch — five small fixes from the 0.73.0 ship review

Date: 2026-08-10
Author: session 72453a7c (post-#683 design discussion)

## Problem

The post-ship discussion of PR #680–#683 surfaced five defects/debts whose
evidence is settled and whose fix is one sentence to a few lines each.
Left unfixed they each have a documented failure mode: plan-gate round-2
revisions keep introducing their own findings (n≥8 across three
consecutive arcs); AGENTS.md's command surface silently omits the newest
shipped verb; `loom_init` scaffolds at the wrong depth when run from a
nested cwd; one test probes the live repo where a tmp fixture suffices;
and two adjudicated design records (queue-layer family ownership, the
family-integration evaluation seed) exist only in conversation.

## Users

Future sessions (any model tier) running writing-plans' review gate,
cold agents reading AGENTS.md for the command surface, external-repo
users running `loom_init`, and future arcs that will need the two
recorded decisions as their starting context.

## Smallest End State

1. writing-plans' NEEDS_REVISION loop states: before re-dispatching the
   reviewer, re-run the pre-patch self-screen **on the revision delta
   itself** (the lines the fix added/changed). Word-cap ratchet raised
   deliberately (4047 → new value recorded in the test message, same
   mechanism as the 2026-08-06 raise). Pin test for the new sentence.
2. AGENTS.md's managed command-surface block declares `loom_init.py`,
   with the conventional `test_agents_md_declares_*` pin
   (precedent: `test_finishing_archive_step.py:163`,
   `test_writing_plans_change_binding.py:148`).
3. `loom_init.py` warns (stderr, advisory — never refuses) when the
   target dir is inside a git repo but is not `git rev-parse
   --show-toplevel`; silent skip when git is absent or the target is not
   a git repo (tmp-fixture tests stay silent; monorepo-subdir adoption
   stays legitimate).
4. `test_loom_init_ships_with_its_templates_and_runs` runs its refusal
   probe against a tmp fixture with a pre-made store, not `REPO_ROOT`.
5. Two backlog entries filed + index regenerated: (a) queue-layer North
   Star — the queue layer is conceptually family-wide but physically
   trapped in loom-code by the `${CLAUDE_PLUGIN_ROOT}` cross-plugin gap
   (note the loom-memory-in-pipeline / backlog-in-code dual-owner
   inconsistency); (b) family-integration evaluation seed — behavioral
   pull (`--family-scan` visibility on today's primitives; no stub
   files; Axis 0's product-shaped moment as the only hard-gate
   candidate) with partial merge loom-code⊕loom-pipeline as foundation.

Plus the carrier: loom-code 0.73.0 → 0.74.0 (items 1/3/4 change plugin
content), CHANGELOG entry, and migration of the shipping-version pin
test (`test_docs_review_blocking_class.py:200`).

## Current State Evidence

- Forward: `loom-code/skills/writing-plans/SKILL.md:107-109` — pre-patch
  self-screen exists but runs only before the FIRST dispatch; the
  NEEDS_REVISION loop at :109 re-dispatches with no delta self-check.
- Reverse: word-cap ratchet
  `loom-code/scripts/test_wp_extraction_pointers.py:206`
  (`test_word_count_at_most_4047`); SKILL.md is at 4045 words — 2-word
  headroom, so item 1 cannot land without a deliberate ratchet raise.
- Error: `loom-code/scripts/loom_init.py:96` resolves target from argv
  or `Path.cwd()` with no repo-root sanity check (PR #683 debt item 1).
- Data: `loom-code/scripts/test_loom_init.py:92-105` runs the refusal
  probe with `cwd=REPO_ROOT` against the live repo (PR #683 debt
  item 2); refusal-on-existing-store is already covered by the tmp-path
  test at :116, so the live probe's only unique value is "runs at all".
- Boundary: AGENTS.md managed block (`AGENTS.md:34` BEGIN → END) lists
  `plan_card.py:155` and `backlog_index.py:164` but no `loom_init.py`;
  no generator script manages the block — it is hand-maintained and
  pin-tested by convention. No test asserts loom_init's stderr is empty
  (warning channel is free).

## Decision

Ship all five in one small branch with one loom-code version bump
(0.74.0). Item 3 is advisory-not-refusal because a monorepo subdir
adopting its own queue layer is a legitimate nested-cwd run — a refusal
would false-positive (same advisory-vs-red split as `--stale-scan`).
Item 1's ratchet raise is the sanctioned mechanism (raise deliberately,
record the reason in the test message) — not an override.

## Out of Scope

- finishing-a-development-branch extraction arc (15-word headroom wall)
  — real arc, not a cheap fix; opens when it actually blocks.
- `--family-scan`, partial plugin merge, milestone layer — recorded as
  item 5's backlog seeds, not built here.
- Backlog item `2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-
  copies` — its start condition ("next touch of writing-plans SKILL.md")
  FIRES with this arc; surfaced to the user at close-out for a separate
  decision, deliberately not absorbed (this batch stays cheap).

## Design-side on-ramp

N/A — mechanism hardening on existing loom-code internals; negative
guard (test-covered increment) applies to rows 1–4; row 5 satisfied
(store exists).

## Open Questions

None — all five adjudicated in conversation 2026-08-10.
