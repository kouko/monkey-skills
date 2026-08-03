# Brief — extract a self-contained `skill-dev-toolkit` plugin

> code-toolkit:brainstorming output, 2026-06-20. Consumed by writing-plans.
> Discovery done in-conversation + a Tier-1 blind experiment (see Alternatives).

## Problem
(JTBD) **When** I want to hand someone — or a fresh agent — *just* the
skill-authoring tools, **I want** them as a self-contained, independently
installable plugin, **so I can** distribute skill-authoring capability without
shipping the whole `dev-workflow` grab-bag (git-memory / handoff / recap-state /
critiques / dbt-model-style). The job is **distribution / standalone
installability**, not tidiness — a router or doc index (the cheaper options) was
explicitly rejected because neither makes the tools independently installable.

## Users
- A teammate / external user who wants to author Claude skills (create → judge /
  dogfood → refactor / tune) and does **not** want the rest of dev-workflow.
- A fresh agent/session that should be able to install `skill-dev-toolkit` alone
  and have it **work with zero cross-plugin dependencies**.

## Smallest End State
A new plugin `skill-dev-toolkit` containing the **5** skill-authoring skills,
**self-sufficient (zero `plugin:skill` references to other plugins)**:
`skill-creator-advance`, `skill-judge`, `skill-refactor`, `skill-tuning`,
`dogfood-skill-testing`. Self-sufficiency achieved by **inlining** a 2–3-question
worth-it / smallest-skill check into creator-advance / refactor / tuning (NOT
forking the critique skills, NOT adding a new shared skill — both rejected, see
Alternatives) and **genericizing** the remaining outbound doc references. The
critique skills (`complexity-critique`, `proposal-critique`) and
`distill-sessions` **stay in dev-workflow**.

## Current State Evidence (brownfield)
- **Forward (do the skills move cleanly?)**: the 5 are self-contained dirs, each
  with its own `scripts/`; grep confirms **no coupling to dev-workflow
  plugin-level files** (`dev-workflow/scripts/`, `.claude-plugin/`) → `git mv` of
  each dir is safe.
- **Reverse (SSOT ownership — read the gates, don't infer)**: two intra-set CI
  gates live OUTSIDE the skill dirs and must travel into the new plugin:
  (a) `dev-workflow/.claude-plugin/test_skill_description_standard.py` hard-codes
  `dev-workflow/skills/skill-creator-advance` + `skill-judge` paths (the grep
  guard); (b) `scripts/check-shared-conventions-drift.py` + the
  `shared-conventions-drift` job in `.github/workflows/skill-structure.yml` verify
  `skill-refactor` (canonical SoT) ↔ `skill-tuning` (functional copies). Both
  gates are **internal to the 5** → become plugin-internal after the move (clean),
  but the scripts + workflow must be repathed.
- **Error (what dangles on move?)**: inbound `dev-workflow:<moved-skill>` IDs in
  ~11 files outside the 5 → must repoint to `skill-dev-toolkit:`:
  `dev-workflow/skills/{brief-before-asking,distill-sessions}/SKILL.md`,
  `tsundoku/skills/{book-distill,book-extract}/SKILL.md`,
  `code-toolkit/skills/using-code-toolkit/README.md`, `deconstruct-toolkit/README.md`,
  `dev-workflow/README.md`, `dev-workflow/skills/{brief-before-asking,proposal-critique}/README.md`,
  `four-dx-coach/optimization-workspace/README.md`, root `README.md`,
  `dev-workflow/skills/distill-sessions/scripts/test_aggregate.py`.
- **Data (outbound deps to sever for self-sufficiency)**:
  creator-advance → `complexity-critique`,`proposal-critique` (inline check);
  skill-refactor → `complexity-critique`,`proposal-critique`,`domain-teams:code-team`
  (SSOT pointer — drop, content already bundled) + fix typo `dev-workflow:skill-tasting`→`skill-tuning`;
  skill-tuning → `proposal-critique` (inline/drop);
  skill-judge → `domain-teams:skill-team` (**13×**, all doc/boundary prose across
  SKILL/NOTICE/README×3 — genericize to "structural convention gates are a separate
  concern", no functional call);
  dogfood-skill-testing → `dev-workflow:distill-sessions` (drop redirect).
- **Boundary**: `.claude-plugin/marketplace.json` (+1 entry → 25 plugins);
  new `skill-dev-toolkit/.claude-plugin/plugin.json` + README ×3 (en/ja/zh-TW per
  repo convention) + CHANGELOG (0.1.0); `dev-workflow` plugin.json (drop 5 skills,
  version bump, CHANGELOG); memory `feedback_skill_description_standard.md` +
  `docs/skill-mining/2026-06-19-skill-description-standard.md` (string refs to
  `dev-workflow:skill-creator-advance` / `skill-judge`).

## Decision
Build `skill-dev-toolkit` with the 5 skills, **self-sufficient via inlined
worth-it checks + genericized doc refs**. Critique skills + distill-sessions stay
in dev-workflow. Keep each moved skill's behavior, body, and internal version
unchanged except the dependency-severing edits. Fix the `skill-tasting` typo in
passing. Per-plugin: dev-workflow version bump + CHANGELOG; new plugin 0.1.0;
marketplace +1.

## Alternatives Considered (resolved in-session, not web-search)
This is a **repo-internal plugin-architecture** decision, not a choice of external
library — so Axis-4 web research was low-value; alternatives were resolved by repo
convention + a **Tier-1 blind experiment**:
1. **Router / doc index inside dev-workflow** — REJECTED: gives discoverability but
   NOT independent installability (the actual job).
2. **Fork + adapt the critique skills into skill-dev-toolkit** — REJECTED by
   experiment: ran the generic `complexity-critique` on 2 real skill-authoring
   proposals (incl. a known-answer historical one); it reframed naturally to
   skill-domain terms (SKILL.md count / routing-shadowing / "already owned by
   creator-advance") and hit the right verdicts — so a fork adds a drift-prone
   maintained copy for ~0 fit gain (the over-build its own gate refuses).
3. **Inline a tiny worth-it check + genericize doc refs** — CHOSEN. Matches the
   repo's self-contained-skill convention (bundled-mindset precedent) and the
   experiment's own RESHAPE verdict ("inline, don't add a skill").

## What Becomes Obsolete
- dev-workflow's ownership of the 5 skills + their `dev-workflow:` IDs (replaced by
  `skill-dev-toolkit:` IDs; remove/repoint in the same change — no dangling IDs).

## Out of Scope
- Moving `distill-sessions` (functional hard-dep on `code-toolkit:dispatching-parallel-agents`
  → can't be self-sufficient without inlining dispatch; stays in dev-workflow).
- Moving `domain-teams:skill-team` (team-convention-bound, 10 intra-domain refs) or
  `superpowers:writing-skills` (external upstream).
- Any behavior change to `complexity-critique` / `proposal-critique` (stay, unchanged).
- Changing the moved skills' own workflows beyond dependency-severing edits.

## Open Questions
- Final plugin name: `skill-dev-toolkit` (assumed) — confirm vs `skill-authoring-toolkit`.
- Worktree vs plain feature branch (lean: plain branch, like the description sweeps).
