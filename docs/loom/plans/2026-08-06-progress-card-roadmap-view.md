# Plan: progress-card roadmap view + authored glosses

Source brief: docs/loom/specs/2026-08-06-progress-card-roadmap-view.md
Goal: the card shows execution order (topological steps), and every
    task carries an authored user-language gloss stating its effect and
    goal relation — done/remaining/order readable at a glance.
Stage: finishing
Critical-path depth: 3 (≤5)
Total tasks: 6
Execution order: parallel-where-possible (Wave 1 = T1+T2+T3+T4, disjoint files; T5 after; T6 after T5)
Plan-document-reviewer verdict: PASS (2026-08-06, round 3 — rounds
1-2 NEEDS_REVISION each fixed and re-verified; round 3 clean 15/15)
Endpoint named: yes → continuous (user 「go」; runs to PR-open; merge stays with the user)

## Task 1 — plan_card.py: steps, glosses, --detail

- Description: Extend scripts/plan_card.py: (a) parse per-task
  `- Dependencies:` (grammar: "none" | "Task <n> completes first" |
  "Tasks <n>[, <n>]... complete first" | "Tasks <n>[, <n>]... parallel"
  — multi-task forms take one-or-more comma-separated numbers and are
  treated IDENTICALLY for level derivation: every listed task is a
  prerequisite; absent field = none) and compute topological levels; a cycle or a reference to a
  nonexistent task → exit 1 loud naming it. (b) A-layout: before each
  level's rows print a separator — untitled `-- step <L> --`, titled
  `-- step <L>: <title> --`, with ` (needs: T<a> T<b>)` inserted
  before the trailing `--` when the level has prerequisites (union of
  its tasks' deps), e.g. titled
  `-- step 2: error handling (needs: T1 T2 T3) --`, untitled
  `-- step 2 (needs: T1) --`. Plain ASCII hyphens (two each side, no
  trailing fill — CJK-safe); no blank lines added anywhere — each
  separator sits directly above its rows and under the previous row
  (or the counts line, for step 1); needs lists ascending by task
  number, space-separated.
  (c) parse optional header block `Steps:` (numbered lines
  `  1. <title>`); when present, count MUST equal derived level count
  else exit 1 loud; titles attach to levels in order. (d) parse
  optional per-task `- Gloss: <text>` — bullet regex mirrors
  `_STATUS_BULLET`'s `\*{0,2}` bold tolerance (accepts `- **Gloss**:`);
  when present render the text as one indented line (six spaces)
  under the task row. (e) new mode
  invoked exactly as `python3 scripts/plan_card.py <plan-path>
  --detail T<N>` (plan path first; main()'s argc check widens): prints
  `T<N> <name>` then `description:`, `why (brief item):`,
  `acceptance:` (RED/GREEN indented), `gloss:` — each transcribed
  verbatim from the task block, omitting absent fields; unknown task
  number → exit 1 loud. Tests RED-first in scripts/test_plan_card.py:
  exact stdout for titled+glossed plan, untitled/glossless plan
  (backward-compat: current flat rendering becomes stepped only when
  Dependencies exist — a plan with all-"none" deps renders ONE step
  without separators to keep old-plan output unchanged — UNLESS the
  plan declares a one-line `Steps:` block, in which case the single
  titled separator `-- step 1: <title> --` renders; count check still
  applies), needs-list separator, Steps-count mismatch exit 1, cycle
  exit 1, --detail happy + unknown-task exit 1, and: all-none deps +
  declared 1-line `Steps:` → exact stdout carries the single titled
  separator.
- Module: scripts
- Files touched: scripts/plan_card.py, scripts/test_plan_card.py
- Context paths:
  - scripts/plan_card.py (current parser structure)
- Acceptance:
  - RED: new tests fail against current code.
  - GREEN: `python3 -m pytest scripts/ -q` green; live run against
    docs/loom/plans/2026-08-06-progress-cards-and-plan-ledger.md
    renders its real dependency structure correctly.
- Dependencies: none
- Independent: true
- Status: done(2508d37b)
- Brief item covered: Smallest End State 1

## Task 2 — plan-format: Steps + Gloss schema + example

- Description: In loom-code/skills/writing-plans/references/plan-format.md:
  (a) header schema gains the optional `Steps:` block per ## Notes N3a;
  (b) per-task schema gains `- Gloss:` per N3b; (c) the canonical
  worked example gains a `Steps:` block (its own language: the
  example is English, so English titles) and one `- Gloss:` line per
  task obeying the contract (effect + goal relation, not a name
  restatement). Extend loom-code/scripts/test_plan_format_progress_fields.py
  RED-first: N3a lead present, N3b lead present, the
  never-restatement contract sentence present (whitespace-normalized
  schema-sentence pins — NOT `- Gloss:` literal counts: the example
  uses the bold style `- **Gloss**:` consistent with its siblings),
  the example carries a `Steps:` block and ≥3 bold Gloss lines.
  ALSO: add one non-gating sentence to
  loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md
  near its Status-field sentence, naming the Gloss contract ("Gloss
  lines, when present, state effect + goal relation in the user's
  conversation language — accept and read, never require") + a pin.
- Module: loom-code/skills/writing-plans (reference)
- Files touched: loom-code/skills/writing-plans/references/plan-format.md, loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md, loom-code/scripts/test_plan_format_progress_fields.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-format.md
- Acceptance:
  - RED: new pins fail against unedited file.
  - GREEN: pin file green.
- Dependencies: none
- Independent: true
- Status: done(0bdd0b75)
- Brief item covered: Smallest End State 2; brief Decisions bullet 2
  (reviewer-prompt Gloss sentence); Decision "language rule"

## Task 3 — writing-plans: emit duty extension

- Description: In loom-code/skills/writing-plans/SKILL.md, extend the
  **Progress surface.** paragraph's first sentence per N2 (Steps +
  Gloss emitted at plan time in the user's conversation language).
  Measured fact: SKILL.md is 4003 words; N2 replaces a 12-word
  sentence with a 36-word one (+24) → 4027, over the 4023 ceiling —
  so the ceiling IS raised to 4047 (4027 + 20) at the FOUR in-repo
  sites in test_wp_extraction_pointers.py (:14 docstring, :191
  function name test_word_count_at_most_4023 → _4047, :193 assert,
  :194 message), arc-named message. Also pin N2's new clause. (The
  brief's "ceiling 4023" line goes stale — planning snapshot,
  non-gating.)
- Module: loom-code/skills/writing-plans
- Files touched: loom-code/skills/writing-plans/SKILL.md, loom-code/scripts/test_wp_extraction_pointers.py
- Context paths:
  - loom-code/scripts/test_wp_extraction_pointers.py
- Acceptance:
  - RED: new pin fails against unedited SKILL.md; AND after the N2
    edit and before the ceiling raise,
    test_wp_extraction_pointers.py::test_word_count_at_most_4023
    fails (4027 > 4023) — observe both REDs.
  - GREEN: wp pin file green; count reported; four-site raise named.
- Dependencies: none
- Independent: true
- Status: done(043d7f58)
- Brief item covered: Smallest End State 3; Decision "counting
  convention / ceilings"; Decision "language rule"

## Task 4 — family-relay §(a2) frame contract v2

- Description: Replace §(a2)'s frame sentence(s) per N1 (goal
  plain-translation gloss; next grounded-explanatory gloss citing plan
  fields; every `[!]` explanation OPENS with the stop reason — needs
  your decision / waiting on an external condition — in the
  conversation language; pipeline-station narration forbidden unless
  a pending decision requires it; field order + script-rendered body
  rules unchanged). Extend the loom-pipeline CHANGELOG [0.14.0] entry
  with one bullet (roadmap steps + gloss lines + frame contract v2).
  In loom-pipeline/scripts/test_family_relay_progress_card.py:
  REWRITE test_progress_card_localization_rule — its pinned sentence
  ("the relayer adds only a one-line conversational frame ... same
  localized-content rule") is DELETED by N1; re-point it at N1's
  "The relayer's frame, in the live conversation language:" clause —
  then add RED-first pins: stop-reason opening, station-narration
  ban, grounded-gloss clause.
- Module: loom-pipeline/hooks
- Files touched: loom-pipeline/hooks/family-relay.md, loom-pipeline/CHANGELOG.md, loom-pipeline/scripts/test_family_relay_progress_card.py
- Context paths:
  - loom-pipeline/hooks/family-relay.md (§(a2))
- Acceptance:
  - RED: new pins fail against unedited §(a2); the rewritten
    localization pin's retirement is observed (old sentence gone
    post-N1).
  - GREEN: `python3 -m pytest loom-pipeline/scripts/ -q` green.
- Dependencies: none
- Independent: true
- Status: done(ff608959)
- Brief item covered: Smallest End State 4; Decision "language rule"

## Task 5 — bump loom-code 0.61.0

- Description: Both loom-code manifests → 0.61.0; CHANGELOG entry N4;
  test_docs_review_blocking_class.py version pin rewritten 0.60.0 →
  0.61.0 (name, docstring, assertions, messages). RED-first.
- Module: loom-code (manifests + changelog)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md ([0.60.0] head)
- Acceptance:
  - RED: rewritten pin fails pre-bump.
  - GREEN: `python3 -m pytest loom-code/scripts/ scripts/ loom-pipeline/scripts/ -q` passes.
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Status: done(16e7eb91)
- Review-weight: mechanical
- Brief item covered: Smallest End State 5

## Task 6 — three-leg haiku probes + dogfood report

- Description: Probes by-path against the edited tree: (a) given a
  titled+glossed rendered card, answer the intended order / what is
  done / what remains / what next; (b) frame contract — a `[!]` row
  surfaces: what must the explanation open with and in what language;
  (c) authoring duty — what does writing-plans emit for a zh-TW-user
  plan vs an English-user plan (language rule comprehension). Write
  docs/loom/dogfood/2026-08-06-progress-card-roadmap-probe.md with
  verbatim quotes + CLEAN/FAIL per leg.
- Module: docs/loom/dogfood
- Files touched: docs/loom/dogfood/2026-08-06-progress-card-roadmap-probe.md
- Context paths:
  - docs/loom/dogfood/2026-08-06-progress-cards-probe.md (shape)
- Acceptance:
  - RED: a leg answering with old behavior (station narrative in the
    frame, hardcoded-Chinese claim, gloss-as-name-translation) is the
    failure signal; any FAIL blocks close-out.
  - GREEN: report exists, three legs CLEAN with quotes.
- Dependencies: Task 5 completes first
- Independent: false
- Status: done(735b1dff)
- Review-weight: prose
- Brief item covered: Smallest End State 6

## Notes

Counting convention: len(text.split()).

**Pinned canonical texts — transcribe VERBATIM**:

N1 — §(a2) frame sentences (replace from "The body is rendered
mechanically" through the section end; the anchor wraps across source
lines — locate whitespace-normalized, not by literal string):

```markdown
The body is rendered mechanically by `scripts/plan_card.py` — never
compose it by hand when the script is available, never re-order or
drop fields. The relayer's frame, in the live conversation language:
a plain-translation gloss under the goal line; a grounded explanatory
gloss for `next:` (derived from that task's own plan fields — cite
the source item, never invent); and for every `[!]` row an
explanation that OPENS with the stop reason — "needs your decision:
…" or "waiting on an external condition: …". Pipeline-station
narration (waves, reviewer arms, verdicts) stays out of the frame
unless a pending decision cannot be understood without it.
```

N2 — writing-plans Progress-surface first-sentence extension (the
sentence "The plan carries `Goal:`, `Stage:`, and per-task `Status:`
from birth (schema below)." — wraps across source lines, locate
whitespace-normalized — becomes):

```markdown
The plan carries `Goal:`, `Stage:`, per-task `Status:`, an optional
`Steps:` title block, and per-task `Gloss:` lines from birth (schema
below) — Steps titles and Gloss lines are written at plan time in the
user's conversation language.
```

N3a — plan-format header schema addition (after the Stage: lines):

```markdown
Steps: <OPTIONAL numbered block, one line per derived dependency
    level, titles in the user's conversation language; when present
    the count must equal the plan's dependency-level count —
    plan_card.py exits 1 loud on mismatch>
```

N3b — plan-format per-task schema addition (after the Status: field):

```markdown
- **Gloss**: <one line in the user's conversation language stating
    the task's user-visible effect and why it matters to the goal —
    NEVER a restatement of the task name; rendered under the task row
    by plan_card.py; emitted by writing-plans for new plans, optional
    on old ones>
```

N4 — loom-code CHANGELOG entry:

```markdown
## [0.61.0] — 2026-08-06 — the card becomes a roadmap

### Added

- **Progress cards show execution order.** plan_card.py derives
  topological steps from `Dependencies:` and renders A-layout
  separators with needs-lists; opt-in `Steps:` titles and per-task
  `Gloss:` lines (both authored at plan time in the user's
  conversation language — the gloss states effect and goal relation,
  never a name restatement); `--detail T<N>` prints one task's full
  fields on demand. The frame contract (family-relay §(a2)) now
  requires stop-reason openings on blocked rows and bans
  pipeline-station narration. Designed interactively with the user;
  markdown-table output rejected for cross-platform stability.
```

## Decision Log

- 2026-08-06: separators use plain ASCII hyphens with no trailing
  fill — CJK titles make width-padding unsafe (the repo's ascii-graph
  lesson); two hyphens each side, constant.
- 2026-08-06: a plan whose tasks all have Dependencies "none"/absent
  renders WITHOUT separators — old-plan output byte-unchanged
  (backward compat pinned in T1's tests). Exception: such a plan that
  DECLARES a one-line `Steps:` block opts in — render the single
  `-- step 1: <title> --` separator (declaring a title is an explicit
  request to see it; pinned in T1's tests).
- 2026-08-06 (round-2 fix): the Steps-opt-in exception now lives in
  T1's Description AND test list, not only here (the fix-skips-
  neighbor split round 2 caught).
- 2026-08-06 (round-1 plan-review fixes): Dependencies grammar
  generalized to one-or-more; separator/blank-line/needs-order/
  --detail invocation disambiguated; Gloss regex bold-tolerant, T2's
  pins switched to schema-sentence form; T3's ceiling raise stated as
  measured fact (4003+24=4027 → 4047, four sites) with its own RED;
  T4 retires/re-points the localization pin N1 deletes;
  reviewer-prompt Gloss sentence folded into T2; Decision
  traceability spread onto T2/T3/T4.
