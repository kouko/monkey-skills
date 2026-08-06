# Brief: progress-card roadmap view + authored glosses

Date: 2026-08-06
Status: FROZEN (designed interactively with the user over ~12 rounds
this session; user: 「go」 — endpoint = PR, continuous)
Consumer: writing-plans → SDD; ships as loom-code 0.61.0 +
loom-pipeline 0.14.0 (already bumped on this branch for the ASCII
marks; this arc extends the same release)

## Problem

The 0.60.0 card is a flat snapshot: task rows in file order, no
visible execution order or dependency structure, and its text is
English-only (plan-file verbatim). The user's stated need: a
roadmap-style view — what is done, what remains, the intended
implementation order — plus per-task explanations in THEIR language
that state each task's effect and relation to the goal (not a
translation of its name). Iterated design (all user-ratified):

- A-layout: tasks grouped into topological steps derived MECHANICALLY
  from `Dependencies:` (top-to-bottom = execution order; same step =
  parallelizable), separator lines carry `(needs: …)`.
- Opt-in `Steps:` header field — step titles authored at plan time in
  the user's conversation language, rendered when present; declared
  count must match derived levels (mismatch → loud error).
- Per-task `Gloss:` field — one line in the user's conversation
  language stating the task's user-visible effect and why it matters
  to the goal; NEVER a restatement of the task name. Authored at plan
  time (context is maximal), default-emitted for new plans, rendered
  under the task row; absent → row renders without it (old plans
  compatible).
- `--detail T<N>` — pull-only view printing that task's Description /
  Brief item covered / Acceptance / Gloss verbatim.
- §(a2) frame contract v2: goal line gets a plain-translation gloss;
  `next:` gets a grounded explanatory gloss (derived from the plan's
  own fields, cited); every `[!]` row's explanation OPENS with the
  stop reason — 「停止原因：需要你決定…」or「等外部條件…」in the
  conversation language ("stop reason: needs your decision / waiting
  on an external condition"); pipeline-station narration (waves,
  arms, verdicts) is forbidden in the frame unless a pending decision
  requires it.
- Markdown-table output REJECTED (code-fence relay renders raw pipes;
  Codex/terminal table rendering unstable; line format is the only
  everywhere-identical shape). Marks stay `[v]/[~]/[ ]/[!]`.

## Smallest End State

1. plan_card.py: topological step grouping from `Dependencies:`
   (parse "none" / "Task N completes first" / "Tasks N, M complete
   first" / "Tasks N, M parallel"); A-layout separators with needs
   lists; `Steps:` titles rendered when present (count-mismatch →
   exit 1 loud); `Gloss:` lines rendered indented under rows;
   `--detail T<N>` mode; unresolvable/cyclic Dependencies → exit 1
   loud. Tests RED-first (exact stdout incl. titled + untitled +
   glossed + detail + cycle/mismatch error paths).
2. plan-format.md: `Steps:` header field (opt-in) + per-task `Gloss:`
   field schema (authoring contract: effect + goal relation, user's
   conversation language, never name-restatement) + the canonical
   worked example gains both. Pin test additions.
3. writing-plans SKILL.md: the Progress-surface paragraph's emit duty
   extends to Steps + Gloss (one sentence). Pin adjustment; ceiling
   4023 budgeted.
4. family-relay §(a2): rewritten frame contract v2 (see above). Pin
   updates in test_family_relay_progress_card.py +
   loom-pipeline CHANGELOG [0.14.0] entry extended.
5. loom-code → 0.61.0 (manifests + CHANGELOG + version-pin rewrite).
6. Haiku probes: (a) read a titled+glossed card → answer order/done/
   remaining/next; (b) frame contract — a [!] surfaces: what must the
   explanation open with, in what language; (c) plan-authoring duty —
   what writing-plans emits for a zh-TW user vs an en user. Dogfood
   report.

## Out of scope

- `--md` presentation flag (YAGNI; canonical stays line format).
- Retro-fitting Steps/Gloss into existing plans.
- Card-body localization (body stays plan-verbatim + authored
  gloss lines; no runtime translation in the script).

## Decisions

- Language rule: Steps/Gloss/frame glosses are in the USER'S
  conversation language (family-relay's localized-content rule) —
  zh-TW in this repo's sessions, but the legislation is
  language-agnostic.
- Gloss/Steps are authoring content → LLM writes at plan time,
  plan-document-reviewer treats them like task names (Check 1/3
  untouched; no new check this arc — reviewer prompt gains one
  sentence naming the Gloss contract, non-gating).
- Counting convention len(text.split()); ceilings: wp ≤4023,
  SDD ≤3974 (untouched this arc), finishing ≤4500 (untouched).
