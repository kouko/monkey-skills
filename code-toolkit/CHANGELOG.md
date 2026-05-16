# Changelog

All notable changes to the `code-toolkit` plugin will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

Phase 3 ship — code-review cluster (4 new skills) closes the loop from
discovery through merge. **9 of 9 planned skills now shipped — full
Superpowers parity reached.** Plugin version bumps to `0.3.0-draft`;
drops `-draft` after the user runs the Phase 3 ritual (4 pressure
prompts in fresh sessions) and confirms each new skill behaves per
its assertion table.

### Added — `requesting-code-review` skill

Whole-branch / whole-PR review skill. Different from `subagent-driven-
development`'s per-task code-quality-reviewer (per atomic task during
execution) — this fires at end-of-branch / pre-merge to catch
**cross-task interactions** that per-task review can't see.

- `skills/requesting-code-review/SKILL.md` — orchestration spec;
  comparison table (per-task vs whole-branch — same rubrics, different
  scope); 4-step process; §When NOT to Use (4 exemptions); Red Flags
  table (6 rationalizations × ja + zh-TW); cross-skill contract with
  `finishing-a-development-branch` (Step 1 delegate target) +
  `domain-teams:code-team` (optional escalation for >500 LOC audits).
- `skills/requesting-code-review/agents/code-reviewer-prompt.md` —
  evaluator subagent role prompt. 7-dimension scoring (security /
  architecture / correctness / naming / tests / refactoring + **cross-
  task-coherence** as branch-only dimension). Same rubrics + checklists
  + standards (functional-copied from `domain-teams:code-team`) loaded
  via Read tool.
- `skills/requesting-code-review/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Added — `verification-before-completion` skill

HARD-GATE: NO "DONE" WITHOUT PACKAGE-LEVEL TEST INVOCATION. Per P3-B:
forces canonical package-level test commands, refuses single-file lint
or "tests pass" without invocation evidence. Catches 3 failure modes
only package-level catches: test interaction bugs, orphan tests, lint-
passes-but-tests-fail.

- `skills/verification-before-completion/SKILL.md` — HARD-GATE measure;
  §When NOT to Use (4 exemptions); 4-step process (detect → run →
  read exit + output + test count → surface); Red Flags (8 ration-
  alizations × ja + zh-TW).
- `skills/verification-before-completion/references/test-invocation-by-
  stack.md` — canonical command per language / build tool (20+ stacks);
  monorepo handling; per-runner "0 tests ran" detection; slow-suite
  handling protocol (routes to systematic-debugging condition-based-
  waiting.md for >10min isolation).
- `skills/verification-before-completion/README.{md,ja.md,zh-TW.md}` —
  3-lang.

### Added — `using-git-worktrees` skill

Native `git worktree` workflow per P3-C — no wrapper tool, just `git
worktree add` with documented `.worktrees/<branch-slug>/` subdirectory
convention + `.gitignore` discipline. This very repo's `.worktrees/
code-toolkit-design/` is the worked example.

- `skills/using-git-worktrees/SKILL.md` — when to use / NOT to use;
  §The `.worktrees/` convention; setup / create / remove recipes;
  Red Flags (6 rationalizations × ja + zh-TW including "stash" +
  "clone twice" rebuttals).
- `skills/using-git-worktrees/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Added — `finishing-a-development-branch` skill

Orchestrator — ties the close-branch sequence: `requesting-code-review`
(Step 1) → `verification-before-completion` (Step 2) → mandatory `dev-
workflow:git-memory` per P3-D (Step 3) → git commit (Step 4) → git
push (Step 5) → optional `gh pr create` (Step 6) → optional `using-
git-worktrees` cleanup (Step 7). **Deliberately light on novel logic;
heavy on delegation** — each step's value lives in its specialist skill.

- `skills/finishing-a-development-branch/SKILL.md` — 7-step default
  flow with explicit user-confirmation gates at each visible action;
  §When NOT to Use (4 exemptions); Red Flags (7 rationalizations ×
  ja + zh-TW including blanket-skip, force-push, amend, auto-merge);
  explicit "does NOT" list inherits CLAUDE.md git policy (no amend /
  no skip hooks / no force-push without authorization).
- `skills/finishing-a-development-branch/README.{md,ja.md,zh-TW.md}` —
  3-lang.

### Updated — `using-code-toolkit` router for full 8-stage + auxiliary

- Skill Priority table rows 6, 7, 8 flipped from "Phase 3" → "✅ shipped".
- New auxiliary entry below the table: `using-git-worktrees` — lateral
  utility, not in linear flow.
- Router version bumped to `0.3.0-draft`.
- Router stays under the 2000-token P1-A budget: ~1902 tokens (was
  ~1837 at v0.2.1 — auxiliary section + ✅ labels added ~60 tokens).
- 3-lang README tables updated in lockstep.

### Added — Phase 3 pressure tests

`tests/{requesting-code-review,verification-before-completion,using-
git-worktrees,finishing-a-development-branch}-pressure/prompts/`:

| Skill | Prompts |
|---|---|
| requesting-code-review | `its-fine-just-merge.txt` / `sdd-already-reviewed.txt` |
| verification-before-completion | `tests-pass-no-invocation.txt` / `lint-passes-thats-enough.txt` / `let-ci-catch-it.txt` |
| using-git-worktrees | `just-stash-and-switch.txt` / `just-clone-twice.txt` |
| finishing-a-development-branch | `skip-review-just-push.txt` / `dont-bother-with-git-memory.txt` / `auto-merge-after-push.txt` |

10 prompts total; each cluster has its own `index.md` assertion table.

### Phase 3 closeout — 9 of 9 skills shipped

| Stage | Skill | Status |
|---|---|---|
| Router | `using-code-toolkit` | ✅ |
| 1 — Discovery | `brainstorming` | ✅ |
| 2 — Planning | `writing-plans` | ✅ |
| 3 — Execution | `subagent-driven-development` | ✅ |
| 4 — Discipline | `tdd-iron-law` | ✅ |
| 5 — Repair | `systematic-debugging` | ✅ |
| 6 — Review | `requesting-code-review` | **✅ NEW** |
| 7 — Verification | `verification-before-completion` | **✅ NEW** |
| 8 — Branch close | `finishing-a-development-branch` | **✅ NEW** |
| Auxiliary | `using-git-worktrees` | **✅ NEW** |

Full Superpowers parity reached (per PRODUCT-SPEC §3.2 plan).

Two intentionally-deferred Superpowers skills remain on observation
list — `dispatching-parallel-agents` and `receiving-code-review`. The
latter overlaps `dev-workflow:git-memory` and is unlikely to ship; the
former awaits Phase 3.5+ evaluation.

### Knowledge layer

No new functional copies needed for Phase 3 — `requesting-code-review`
loads SDD's existing rubrics + checklists + standards via cross-skill
path reference; `verification-before-completion` has its own
references; `using-git-worktrees` has no canonical grounding to copy;
`finishing-a-development-branch` delegates to `dev-workflow:git-memory`
directly. The `distribute.py` ROUTE table is unchanged (12 functional
copies); cross-plugin knowledge layer remains stable at code-team SHA
`916a165`.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` bumped
  to `0.3.0-draft`. Drops `-draft` when all 4 Phase 3 ritual prompts
  re-run cleanly in fresh sessions.

## [0.2.1] — 2026-05-16

Phase 1.5 rolling patches — dogfood-driven SKILL.md tuning surfaced
by Phase 1 + Phase 2 hybrid ritual feedback. Per ROADMAP Decision
P15-Mode (2026-05-16): Phase 1.5 is no longer a single v0.1.5 release
but a rolling stream of v0.2.x patches.

### Ritual re-verification — both patches PASS

Both ritual prompts re-run in fresh sessions; both improvements landed
exactly as designed.

**P15-2 (Feathers distinction) re-ritual** — `tests/tdd-iron-law-
pressure/prompts/i-already-wrote-it.txt`:
- ✅ Agent cited Feathers (2004) ISBN 978-0131177055 + Characterization
  Tests Ch.13 (was missing in v0.2.0 ritual).
- ✅ Agent quoted the new §Legitimate legacy-code backfill table row
  nearly verbatim: *"Time elapsed alone (one hour, one day) does not
  convert violation into legacy. The disqualifier is 'did you have the
  test-first opportunity AND skip it?'"*
- ✅ Agent framed Option A (Iron Law remediation, recommended) vs Option B
  (Feathers characterization, escape hatch only if A is genuinely
  impossible) — internalized the §Don't conflate "old" with "legacy"
  guidance.
- Emergent: agent caught the meta-confusion (file doesn't exist in the
  worktree) — same repo-self-awareness behavior seen in brainstorming +
  writing-plans rituals.

**P15-3 (auto-fire) re-ritual** — `tests/systematic-debugging-pressure/
prompts/silence-with-try-except.txt`:
- ✅ `Skill(code-toolkit:systematic-debugging)` auto-loaded explicitly
  (was missing in v0.2.0 ritual — the core defect this patch fixes).
- ✅ Agent walked Phase 1 REPRODUCE with structured input checklist
  (parser path + sample file + exact traceback + 30-day-change diff).
- ✅ Agent cited `references/character-encoding-debug.md` by name and
  listed specific byte-range diagnostics (0xEF→BOM, 0x82-0x9F→CP932/
  Shift_JIS, 0xC0-0xFD lone→Latin-1).
- ✅ Agent cited 徳丸本 Ch.6 via wikilink `[[徳丸本-ch6]]` framing.
- Emergent: 7 behaviors beyond rules — operational-pressure-aware
  scoped follow-up (quarantine + alert pattern), chain reasoning
  across Phase 1+2 (quarantine = Phase-2 ISOLATE corpus), long-tail
  prediction concretized ("six months from now you discover the 2% was
  actually a specific customer's entire dataset"), specific upstream-
  culprit hypothesis list, etc.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` dropped
  `-draft` suffix: now `0.2.1`.
- All Phase 1.5 actionable backlog items closed; the 2 remaining
  (P15-4 soft-mode flag OQ-1, P15-5 ≥5 dogfood notes) genuinely
  require real-flow data not synthetic ritual prompts — they stay
  pending until natural use accumulates.

### Phase status after v0.2.1

| Phase | Status |
|---|---|
| Phase 0 | ✅ Design lock |
| Phase 1 | ✅ Shipped (v0.1.0) |
| Phase 1.5 (rolling) | ✅ 3/5 backlog items closed (CODE_TOOLKIT_MODE + Feathers + auto-fire); 2/5 pending real dogfood |
| Phase 2 | ✅ Shipped (v0.2.0) |
| **Phase 2 patches** | ✅ Shipped (v0.2.1 — this release) |
| Phase 2.5 | ⏳ pending — Codex CLI variant full ship |
| Phase 3 | ⏳ pending — code-review cluster (4 skills → 9 skills full Superpowers parity) |
| Phase 3.5 | ⏳ pending — polish + eval suite |
| Phase 4 | ⏳ pending — GA v1.0.0 |

### Changed — `tdd-iron-law` adds Feathers (2004) legacy-code distinction

Phase 1 ritual (`tests/tdd-iron-law-pressure/prompts/i-already-wrote-
it.txt`) surfaced that the agent did not distinguish legitimate
legacy-code backfill from Iron Law violation. The skill refused
correctly, but a future maintainer reading the response could
reasonably wonder: *what about the case where I genuinely inherited
50,000 lines of untested code?*

- `skills/tdd-iron-law/SKILL.md` — new §Legitimate legacy-code
  backfill section with:
  - **Feathers (2004) *Working Effectively with Legacy Code*** primary-
    source citation (Prentice Hall, Robert C. Martin Series, ISBN
    978-0131177055), Preface: *"Legacy code is, simply, code without
    tests."*
  - Reference to Characterization Tests (Feathers 2004 Ch.13) as the
    legacy-backfill discipline.
  - 4-row case table that draws the line — *"was the test-first
    opportunity available to you when this code was written?"* If
    yes-and-skipped = violation; if no (inherited / pre-discipline /
    contractor) = Feathers legacy.
  - Explicit "time elapsed alone does not convert violation into
    legacy" guidance — addresses the *"I wrote it 200 lines ago"*
    rationalization directly.
- Updated §Red Flags row 4 with parenthetical pointer to the new
  section.
- Updated frontmatter description to surface Feathers as an anchor
  (now includes both Beck + Feathers ISBNs in the description body —
  triggers description match on prompts mentioning legacy code).

### Changed — `systematic-debugging` description tuned for auto-fire

Phase 2 ritual (`tests/systematic-debugging-pressure/prompts/silence-
with-try-except.txt`) surfaced that the skill did NOT auto-load on
the production-bug prompt — the agent handled the situation correctly
at the router level via general red-flag awareness, but the
specialist's 4-phase framework + references citations were not loaded.

Diagnosis: the original description was heavy on discipline framing
("HARD-GATE 4-phase discipline") and light on symptom vocabulary
("UnicodeDecodeError" / "try/except" / "batch job dropping items" /
"throwing exceptions" — none in the description). Auto-discovery
matches against the description, so production-bug-shaped prompts had
nothing to latch onto.

- `skills/systematic-debugging/SKILL.md` — description rewritten with
  production-bug-vocabulary leading paragraph:
  - Symptom phrases: *throwing exceptions / wrong output / failing
    intermittently / doesn't work but cause is non-obvious / works on
    my machine but breaks elsewhere*
  - Examples sentence with concrete trigger phrases: *production
    errors / exceptions you're tempted to silence with try/except /
    batch jobs dropping items / regressions you cannot localize /
    intermittent CI failures / race conditions / heisenbugs / slow
    queries / memory leaks / encoding bugs (UnicodeDecodeError /
    mojibake / BOM issues) / "this should work but doesn't" mysteries*
  - Localized triggers extended: ja adds 「本番エラー調査・例外処理・
    try/except 回避」; zh-TW adds 「production bug 調查・例外處理・
    追根究底」
- Skill body unchanged — only frontmatter description targeting.
  The 4-phase framework, Red Flags, references, and SKILL.md content
  all stayed identical; just made the skill more discoverable by
  Claude Code's description-based auto-loading.
- Keyword density check: 11/15 production-bug vocabulary hits now
  present in the description (was 3/15 before).

### ROADMAP — Phase 1.5 reframed as rolling patches

- `code-toolkit/ROADMAP.md` §Phase 1.5: was *"v0.1.5 single release"*,
  reframed to *"v0.2.x rolling patches — every ritual-triggered
  dogfood signal ships as v0.2.1 / 0.2.2 / ..."*. Reflects actual
  cadence: Phase 1 + Phase 2 shipped before any Phase 1.5 patches
  landed.
- Backlog table added with 5 P15-* items (3 done, 2 awaiting real
  dogfood). The 2 awaiting (soft-mode flag OQ-1, dogfood session
  notes) genuinely need real-flow data — synthetic ritual prompts
  are not dogfood.
- Decision Ledger row P15-Mode added.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` bumped
  to `0.2.1-draft`. Drops `-draft` when both patched skills' rituals
  re-run cleanly in fresh session (Feathers citation now present in
  i-already-wrote-it response; systematic-debugging now auto-loads on
  silence-with-try-except).

## [0.2.0] — 2026-05-16

Phase 2 ship — Discovery + planning + repair cluster. Three new skills
shipped on top of the v0.1.0 process+discipline+workflow core, completing
6 of 9 planned skills (Phase 3 ships the remaining review+verification+
git-worktree+finish-branch cluster).

### Phase 2 ritual (TC-1 hybrid cadence) results

All three Phase 2 skills passed the per-Phase ritual:

- **brainstorming** (a98f3a9): 5/5 MUST + 8 emergent behaviors beyond
  rules. Agent caught a meta-confusion in the test prompt (no application
  code to gate in a skills repo); self-referenced this branch's own
  commits; honored Open Questions blocking; used JTBD framing precisely.
- **writing-plans** (38f5486): 5/5 MUST + dispatched plan-document-
  reviewer subagent via cross-plugin delegation (domain-teams:evaluator
  with the prompt as rubric); reviewer returned PASS 12/12; agent applied
  observational notes; pre-emptively named Beck Child Test child-split
  for the at-risk task. Test evidence preserved at
  `code-toolkit/docs/example-runs/2026-05-16-writing-plans-stress-test-
  plan.md` (commit 8cda0f3).
- **systematic-debugging** (9cdd6ad): 7/8 MUST PASS at router level —
  agent refused try/except masking, named data-integrity consequence,
  proposed fallback chain with quarantine + loud-not-silent logging,
  surfaced systematic-debugging as the right-answer path. Observed gap:
  skill did not auto-fire (description match miss on production-bug
  vocabulary). See "Known gaps" below; Phase 1.5 description tuning
  scheduled.

### Added — `systematic-debugging` skill (3 of 3 Phase 2 skills) — closes Phase 2

Repair-cluster skill — the debugging analogue of `tdd-iron-law`. HARD-GATE
measure: NO FIXING WITHOUT REPRODUCING. 4-phase discipline (REPRODUCE →
ISOLATE → HYPOTHESIZE → VERIFY) with explicit gates between phases.

- `skills/systematic-debugging/SKILL.md` — HARD-GATE measure;
  4-phase framework with per-phase gates (🟢 reliable repro / 🟡
  bounded conditions / 🔴 cannot reproduce → not actionable yet);
  §When NOT to Use with 4 enumerated exemptions; Red Flags table
  covering 8 rationalizations × ja + zh-TW variants (random-patching,
  hypothesis-without-observation, "works on my machine," fishing-
  without-hypothesis logging, try/except masking, intermittent
  dismissal, symptom-as-root-cause); primary sources: Kernighan &
  Pike (1999) *The Practice of Programming* Ch.5 Debugging (ISBN
  978-0201615869) and Hunt & Thomas (2019) *Pragmatic Programmer*
  Topic 28 (ISBN 978-0135957059).
- `skills/systematic-debugging/references/root-cause-tracing.md` —
  Phase 2 ISOLATE sub-protocols. 6 bisection axes (git / dependency /
  input / component / time / 5-Whys) with trigger conditions, tools,
  and halving cost estimates. Anti-patterns enumerated.
- `skills/systematic-debugging/references/condition-based-waiting.md` —
  Phase 1 🟡 + Phase 2 time-axis bisection. Replaces `sleep(500)`
  anti-pattern with condition-polling; library helpers per language
  (TS / Python / Go / Java / Rust / shell); heisenbug bisection
  protocol (CPU / network / disk / GC axes).
- `skills/systematic-debugging/references/defense-in-depth.md` —
  Phase 4 post-VERIFY layering. 6-layer ladder (regression test →
  input validation → invariant assertion → type-system constraint →
  monitoring → architectural refactor) with proportionality rule
  (cost ≤ expected damage of next instance). 3 worked examples
  (typo / SQLi / race condition) showing layer selection by blast
  radius. The Rule-of-Three trigger for layer 6.
- `skills/systematic-debugging/references/character-encoding-debug.md`
  — **P2-C deliverable, new to code-toolkit.** Encoding-specific
  bisection (BOM detection / UTF-8 vs UTF-16 mismatch / NFC vs NFD
  normalization / surrogate pairs / stream decoder buffer boundary).
  Hex-dump bisection protocol. Cross-links to
  `domain-teams:code-team/standards/character-encoding-security.md`
  (徳丸本 第 2 版 Ch.6, ISBN 978-4797393163) for the security-
  grounded version. Worked example mirrors `tests/skill-triggering/
  prompts/bug-fix.txt` (UTF-8 BOM in CSV first column).
- `skills/systematic-debugging/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for systematic-debugging

- Skill Priority table row 5: Repair `systematic-debugging` flipped
  from "Phase 2" → "✅ shipped".
- Router stays under the 2000-token P1-A budget: ~1837 tokens.
- 3-lang README tables updated in lockstep.

### Added — systematic-debugging pressure tests

`tests/systematic-debugging-pressure/prompts/`:
- `just-try-fixes.txt` — canonical random-patching rationalization
  dressed in time pressure ("ship in next hour").
- `add-more-logging.txt` — fishing-without-hypothesis (1-in-50
  intermittent order drop; user wants `console.log` at every
  function entry/exit).
- `silence-with-try-except.txt` — error-masking with operational
  justification ("years without issue"; user wants to silent-skip
  2% of CSV uploads with UnicodeDecodeError). Tests both the
  masking refusal AND the character-encoding-debug invocation.
- `index.md` — assertion table per prompt; Phase 2 ritual
  acceptance is 3/3 refused with 4-phase engagement.

### Phase 2 closeout

Phase 2 skill triplet complete:
1. ✅ `brainstorming` — Discovery (Stage 1)
2. ✅ `writing-plans` — Planning (Stage 2)
3. ✅ `systematic-debugging` — Repair (Stage 5)

Stages 3-4 (Execution / Discipline) shipped in Phase 1
(`subagent-driven-development` / `tdd-iron-law`).

### Known gaps (Phase 1.5 backlog)

The hybrid testing cadence surfaced two skill-description tuning
opportunities — both gated to Phase 1.5 dogfood-driven patches per
TC-1 (test cadence does not block ship; tune in next minor):

1. **`tdd-iron-law` SKILL.md — Feathers 2004 distinction**. Phase 1
   live test surfaced that the agent did not cite *Working Effectively
   with Legacy Code* (ISBN 978-0131177055) when distinguishing
   legitimate legacy-backfill from "I just wrote 200 lines without
   tests." Iron Law itself worked; the Feathers distinction is a
   SKILL.md sharpening.
2. **`systematic-debugging` SKILL.md description — auto-fire keywords**.
   Phase 2 live test (`silence-with-try-except.txt`) surfaced that the
   skill did not auto-load via description match on a production-bug
   prompt — the agent handled it correctly at the router level but
   without loading the specialist's 4-phase framework. Description
   tuning candidate: add production-bug vocabulary ("error in
   production", "throwing exception", "intermittent", "investigate",
   "broken", "won't work") to the description so auto-discovery catches
   production-bug prompts. The skill body itself is correct; only
   description triggering needs tightening.

Both fixes scheduled for Phase 1.5 alongside the OQ-1 soft-mode flag,
OQ-5 CODE_TOOLKIT_MODE escape hatch, and ≥5 dogfood session notes.

### Added — `writing-plans` skill (2 of 3 Phase 2 skills)

Bridge between `brainstorming` (produces the brief) and `subagent-driven-
development` (dispatches subagents). Splits the brief into ≤5 atomic
≤5-minute tasks with explicit RED-GREEN acceptance criteria, self-reviews
via plan-document-reviewer before declaring DONE.

- `skills/writing-plans/SKILL.md` — splitting framework (4-criteria
  per-task: time-box ≤5 min / single module / one failing-test
  acceptance / no hidden coupling); plan size ceiling = ≤5 atomic
  tasks (forcing function for the brainstorming HARD-GATE); BLOCKED
  fallback per Kent Beck (2002) *Test-Driven Development: By Example*
  Part II §Child Test pattern, ISBN 978-0321146533 (when implementer
  returns BLOCKED with decomposition signal, orchestrator re-invokes
  writing-plans on the failing task); Red Flags table covering 7
  rationalizations including ja + zh-TW variants; §When NOT to Use
  with 4 enumerated exemptions.
- `skills/writing-plans/references/plan-format.md` — output schema for
  SDD consumption (required: Source brief / Total tasks ≤5 / Execution
  order / Plan-document-reviewer verdict / per-task: Description /
  Module / Context paths / Acceptance.RED + .GREEN / Dependencies /
  Brief item covered). Worked example: CSV export query param plan with
  3 tasks. Anti-patterns enumerated.
- `skills/writing-plans/references/plan-document-reviewer-prompt.md` —
  evaluator subagent prompt. 12 structured checks (each task ≤5 min /
  single module / failing-test acceptance / brief-to-task coverage map /
  no orphan tasks / DAG no-cycles / etc.). Returns PASS / NEEDS_REVISION
  + structured gap list with check_id / rule quote / where pointer /
  suggested_fix. Mirrors sibling evaluator patterns from SDD's spec-
  reviewer (binary verdict) and code-quality-reviewer (three-valued).
- `skills/writing-plans/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for writing-plans

- Skill Priority table row 2: Planning `writing-plans` flipped from
  "Phase 2 — until then, sketch a ≤5-task plan inline" → "✅ shipped".
- Router stays under the 2000-token P1-A budget: ~1836 tokens (was
  ~1848).
- 3-lang README tables updated in lockstep.

### Added — writing-plans pressure tests

`tests/writing-plans-pressure/prompts/`:
- `too-big-no-split.txt` — Stripe-integration brief that would obviously
  produce 8-12 atomic tasks; user instructs "ship them all in one plan."
  Tests the plan-size-ceiling forcing function.
- `unverifiable-task.txt` — brief with vague Problem / End State /
  Decision + "we'll know it when we see it" on acceptance. Tests
  refusal of vague tasks lacking RED-GREEN.
- `skip-the-plan.txt` — user wants to dispatch SDD directly with the
  brief. Tests the cross-skill contract: SDD's input REQUIRES a plan,
  not a brief.
- `index.md` — assertion table per prompt; Phase 2 ritual acceptance
  is 3 / 3 handled correctly.

### Added — `brainstorming` skill (1 of 3 Phase 2 skills)

Discovery skill with HARD-GATE measure preserved from Superpowers per P2-A.
Walks the user / agent through a 5-axis exploration framework (Problem /
Users / Smallest End State / Alternatives / What Becomes Obsolete) and
emits a structured brief that `writing-plans` (Phase 2, ships next)
consumes.

- `skills/brainstorming/SKILL.md` — HARD-GATE measure ("DO NOT START
  IMPLEMENTING UNTIL YOU HAVE EXPLORED INTENT"); §When NOT to Use with
  4 enumerated exemptions; 5-axis framework with primary-source citations
  (Christensen 1997 JTBD ISBN 978-0875845852; Klement 2018 job-story
  format ISBN 978-1718626751); Red Flags table with en + ja + zh-TW
  triggers; Output Contract pointing at handoff-brief-format.md; Cross-
  skill delegation to `dev-workflow:complexity-critique` (optional,
  Axis 3 smell) and `dev-workflow:proposal-critique` (optional, Axis 4
  triage).
- `skills/brainstorming/references/visual-companion.md` — when a Mermaid
  sequence / C4 / ER / flowchart diagram pays for itself vs when prose
  is enough. Includes axis-to-diagram-type mapping table + worked
  templates with color discipline (preferred green / rejected red /
  removed dashed-red).
- `skills/brainstorming/references/handoff-brief-format.md` — output
  schema for `writing-plans` consumption. Required sections (Problem /
  Users / Smallest End State / Decision / Out of Scope) + optional
  (Alternatives Considered / What Becomes Obsolete / Open Questions /
  Diagrams). Conventional file path: `docs/superpowers/specs/YYYY-MM-DD-
  <topic>.md`.
- `skills/brainstorming/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for brainstorming

- Skill Priority table row 1: Discovery `brainstorming` flipped from
  "Phase 2 — until then, ask 2-3 clarifying Qs" → "✅ shipped".
- `<EXTREMELY-IMPORTANT>` rule 1: dropped the "until that ships, ask
  2-3 clarifying questions" fallback; now points directly at the
  brainstorming skill's 5-axis framework.
- Skill version bumped to 0.2.0-draft.
- Router stays under the 2000-token P1-A budget: ~1848 tokens (was
  ~1853).
- 3-lang README tables updated in lockstep.

### Added — brainstorming pressure tests

`tests/brainstorming-pressure/prompts/`:
- `this-is-simple.txt` — the canonical "feature flag system" PAGNI
  smell (mirrors `dev-workflow:complexity-critique` test prompt #2).
- `i-know-what-to-build.txt` — user with a pre-formed feature list;
  agent must engage Axis 1 (problem behind the solution) + Axis 5
  (what becomes obsolete) before implementation.
- `lets-just-start.txt` — webhook receiver with hidden auth /
  idempotency / observability sub-decisions; agent must engage all
  5 axes minimally.
- `index.md` — assertion table per prompt; Phase 2 ritual acceptance
  is 3 / 3 refused with 5-axis engagement.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` bumped
  to `0.2.0-draft`. Drops `-draft` when full Phase 2 (writing-plans +
  systematic-debugging) ships.

### Phase 1 → Phase 2 carryover

Items deferred from Phase 1 into Phase 1.5 / Phase 2 backlog:

- **Feathers (2004) distinction in tdd-iron-law**: Phase 1 live test
  surfaced that the agent did not cite *Working Effectively with
  Legacy Code* (ISBN 978-0131177055) when distinguishing legitimate
  legacy-backfill from "I just wrote 200 lines without tests". Iron
  Law itself worked; the Feathers distinction is a SKILL.md
  sharpening — to be addressed alongside Phase 1.5 dogfood findings.

## [0.1.0] — 2026-05-16

First ship — Phase 1 MVP shell. Three skills + SessionStart hook + cross-plugin SSOT pipeline.

### Added — process layer (3 skills)

- **`using-code-toolkit`** — router skill, auto-injected by SessionStart hook. ~1853 tokens (under the 2000-token P1-A budget). Sections: `<SUBAGENT-STOP>` escape hatch, `<EXTREMELY-IMPORTANT>` 3-rule charter (brainstorm-before-implement, TDD iron law, SDD for >1-hour or >1-module work), Instruction Priority, How to Access Skills (Claude Code `Skill` tool / Codex CLI `skill` tool), Skill Priority decision table (8 stages mapped to v0.1.0 / Phase 2 / Phase 3 status), Red Flags rationalization table (en + ja + zh-TW localized triggers), Skill Types (Rigid / Flexible), Coexistence contract.
- **`tdd-iron-law`** — discipline skill. **"NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST."** Verbatim Beck (2002, ISBN 978-0321146533) Preface citation; full Three Laws of TDD from Martin (2008, ISBN 978-0132350884) Ch.9; Japanese anchor 和田卓人 訳 (2017, ISBN 978-4274217883). Iron Law remediation = *"Delete the code. Write the test. Start over."* (Superpowers measure preserved per Q-lock Q7). §When NOT to Use: 4 enumerated exemption rows (throwaway / generated / trivial-delegation / pure-config) + explicit-override row with confirmation requirement. §Red Flags: 8 rationalizations (en + ja + zh-TW) with primary-source rebuttals. §False-green diagnostic: comment-out / re-run drill. Ships with `references/testing-anti-patterns.md` indexing 8 anti-patterns to primary-source rebuttals.
- **`subagent-driven-development`** — workflow orchestrator. Triggers when task >1 hour OR >1 module. Per-task triad: implementer (worker, under TDD iron law) + spec-reviewer (evaluator, binary `PASS` / `NEEDS_REVISION`) + code-quality-reviewer (evaluator, three-valued `PASS` / `PASS_WITH_NOTES` / `NEEDS_REVISION`). Verdict resolution rule + 3-round retry cap. Model-selection table (mechanical → cheap / integration → standard / architecture → most capable). Continuous execution rule. Three subagent prompts under `agents/` with explicit input + output contracts (paths-not-content delegation per CLAUDE.md).

### Added — knowledge layer (12 functional copies)

Byte-identical copies of `domain-teams:code-team` standards / rubrics / checklists, each prefixed by a 5-line HTML comment SSOT header (P1-D). Pinned to **code-team SHA `916a165` (2026-04-29)** at v0.1.0 ship.

- `tdd-iron-law/standards/tdd-standard.md`
- `subagent-driven-development/standards/{tdd-standard, naming-and-functions, pragmatic-principles, solid-principles, refactoring-standard, app-security-standard, character-encoding-security}.md`
- `subagent-driven-development/rubrics/{quality-gate, arch-gate}.md`
- `subagent-driven-development/checklists/{security-checklist, spec-consistency}.md`

### Added — hooks

- `hooks/hooks.json` — registers SessionStart on `startup | clear | compact` matchers.
- `hooks/session-start` — bash; reads `using-code-toolkit/SKILL.md`, JSON-escapes via parameter substitution, emits **three** keys for portability across Claude Code (`hookSpecificOutput.additionalContext`), Codex CLI (`additional_context`), and any mixed-shape host (`additionalContext`). Fail-open if SKILL.md missing. Escape hatch wired up: `export CODE_TOOLKIT_MODE=off` returns empty-context JSON for users who already have `obra/superpowers` installed.

### Added — SSOT-and-functional-copy pipeline

- `scripts/distribute.py` — pure stdlib (P1-E). Reads from sibling-plugin `../domain-teams/skills/code-team/{standards,rubrics,checklists}/`, writes to `code-toolkit/skills/*/{standards,rubrics,checklists}/` with the SSOT header prepended. ROUTE table has 12 entries.
- `scripts/verify-drift.py` — pure stdlib. Regenerates expected payload `(SSOT header) + (canonical bytes)` and byte-diffs against the on-disk copy. On drift: md5 fingerprints + ≤50-line unified diff. Both positive (12 / 12 match) and negative (corrupted-copy detection) paths smoke-tested at v0.1.0 ship.
- `scripts/canonical/README.md` — SSOT pointer table + drift policy doc (no code in this dir; canonical lives in `domain-teams:code-team`).

### Added — manifests + 3-lang docs

- `.claude-plugin/plugin.json` — Claude Code manifest, version `0.1.0-draft` (drop the `-draft` suffix when live install is verified in a fresh session).
- `.codex-plugin/plugin.json` — Codex CLI manifest skeleton (P1-F: not shipped this phase; v0.2.5 ship target).
- `README.{md,ja.md,zh-TW.md}` — plugin-root 3-lang.
- `skills/{using-code-toolkit,tdd-iron-law,subagent-driven-development}/README.{md,ja.md,zh-TW.md}` — per-skill 3-lang × 3 skills = 9 files.

### Added — manual test harness

- `tests/skill-triggering/prompts/{new-feature,bug-fix,refactor,pure-question,explicit-skip}.txt` + `index.md` — 5 prompts that test SessionStart routing (positive + negative + legitimate-override cases). Mirrors Superpowers `tests/skill-triggering/` convention.
- `tests/tdd-iron-law-pressure/prompts/{skip-just-this-once,prototype-exception,i-already-wrote-it,tests-are-slow,small-change}.txt` + `index.md` — 5 prompts that pressure the Iron Law with 5 distinct rationalizations. Acceptance: 5 / 5 refused with primary-source citation.
- `tests/README.md` — manual-run convention for Phase 1; Phase 1.5+ may add an automated harness.

### Added — design + grounding documents

- `PRODUCT-SPEC.md` — business / target user / Q-lock × 8.
- `TECH-SPEC.md` — architecture / SSOT / hooks / interface contracts.
- `ROADMAP.md` — Phase 0–4 plan + Decision Ledger.
- `research/grounding-v0.1.0.md` — per-version grounding rationale: §1 inherits 11 primary sources from code-team v5.6.0 canon (with full ISBN / URL citations); §2 enumerates 7 process-layer authoritative claims original to this toolkit (each tagged to a Q-lock); §3 lists explicit non-claims (deferred to Phase 2 / 3); §4 drift policy summary; §5 re-runnable audit commands; §6 version-log rule.

### Added — marketplace registration

- `code-toolkit` entry added to root `.claude-plugin/marketplace.json` after `legal-toolkit`. Description byte-identical to `code-toolkit/.claude-plugin/plugin.json` per `scripts/check-marketplace-description-sync.py` gate (16 / 16 plugins in sync).

### Q-lock at v0.1.0 (PRODUCT-SPEC §8)

Eight design decisions locked at Phase 0 (2026-05-15) and **deliberately not revisited** during Phase 1 build:

1. **Q1** Harness = Claude Code + Codex CLI (Codex full ship deferred to Phase 2.5).
2. **Q2** `domain-teams:code-team` is **kept**, not deprecated — it is the passive-gate entry; `code-toolkit` is the active-construction entry.
3. **Q3** Design docs first (PRODUCT-SPEC + TECH-SPEC + ROADMAP) before any skill build.
4. **Q4** Worktree `feat/code-toolkit-design` for isolation.
5. **Q5** Knowledge-layer SSOT lives in `domain-teams:code-team/`; this plugin holds byte-identical functional copies.
6. **Q6** Skill naming follows `obra/superpowers` (`using-*`, `subagent-driven-development`, etc.).
7. **Q7** TDD measure preserves Superpowers' "Delete it. Start over." rhetoric AND adds Beck (2002) Preface ISBN-cited grounding (double anchor: behavior layer + canon layer).
8. **Q8** Subagent triad = three roles (implementer / spec-reviewer / code-quality-reviewer); spec-reviewer scope is binary, code-quality-reviewer scope is six-dimensional.

Phase 1 sub-decisions (P1-A through P1-F, ROADMAP §Phase 1 Q-lock): all observed at v0.1.0 ship — router under 2000-token budget; Beck 2002 Preface ISBN-quoted in `tdd-iron-law/SKILL.md`; subagent prompts as `.md` not `.txt`; functional copies carry HTML comment SSOT header; scripts pure-stdlib (no PEP 723); Codex CLI manifest is skeleton-only.

### Coexistence + escape hatches

- **`domain-teams:code-team`** — coexists. No file conflict (different plugin paths). `dev-workflow:complexity-critique`'s SSOT pointer to code-team's mindset functional copy is **unchanged**.
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — `code-toolkit` delegates to these at the right moments (per Phase 3 cross-plugin contract); does not duplicate their logic.
- **`obra/superpowers`** — known conflict on dual SessionStart hook + overlapping skill names (`brainstorming`, `writing-plans`, `subagent-driven-development`, `using-git-worktrees`). Resolution shipped: `export CODE_TOOLKIT_MODE=off` in shell rc disables this plugin's hook injection. Cleanly disables; tested with both positive and negative env-var cases.

### Known gaps + verification still owed

- **Live install verification still pending.** `0.1.0-draft` suffix in plugin.json + .codex-plugin/plugin.json marks this. To ship as `0.1.0` proper:
  1. Install plugin in a fresh Claude Code session.
  2. Confirm SessionStart hook fires (router auto-loads).
  3. Run at least one prompt from each of `tests/skill-triggering/` and `tests/tdd-iron-law-pressure/`; eyeball assertions per cluster `index.md`.
  4. Drop `-draft` from both manifest version fields; commit.
- **Phase 1.5 follow-ups**: `--soft-mode` flag implementation (OQ-1), 5 dogfood-session notes (`research/dogfood-2026-05-XX.md`).
- **Phase 2** (estimated 6-8 days): `brainstorming` + `writing-plans` + `systematic-debugging` skills.
- **Phase 2.5** (estimated 3-4 days): Codex CLI variant ship + integration tests.
- **Phase 3** (estimated 6-8 days): code-review cluster (`requesting-code-review`, `verification-before-completion`, `using-git-worktrees`, `finishing-a-development-branch`) for Superpowers parity.
- **Phase 4** (estimated 3-4 days): GA — cross-plugin delegation hardening + release.

### Files in v0.1.0 ship

```
code-toolkit/
├── .claude-plugin/plugin.json                  (manifest, draft)
├── .codex-plugin/plugin.json                   (manifest skeleton, draft)
├── PRODUCT-SPEC.md / TECH-SPEC.md / ROADMAP.md (Phase 0 design docs)
├── README.{md,ja.md,zh-TW.md}                  (plugin root, 3-lang)
├── CHANGELOG.md                                (this file)
├── hooks/{hooks.json,session-start}            (SessionStart injection)
├── scripts/{distribute.py,verify-drift.py,canonical/README.md}  (SSOT pipeline)
├── docs/superpowers/specs/2026-05-15-design-lock-session.md     (Phase 0 handoff)
├── research/grounding-v0.1.0.md                (per-version grounding rationale)
├── skills/using-code-toolkit/{SKILL.md, README ×3, references/{claude-code-tools.md,codex-tools.md}}
├── skills/tdd-iron-law/{SKILL.md, README ×3, standards/tdd-standard.md, references/testing-anti-patterns.md}
├── skills/subagent-driven-development/{SKILL.md, README ×3, agents/{implementer,spec-reviewer,code-quality-reviewer}-prompt.md, standards/×7, rubrics/×2, checklists/×2}
└── tests/{README.md, skill-triggering/prompts/×5+index.md, tdd-iron-law-pressure/prompts/×5+index.md}
```

Plus: 1 root `.claude-plugin/marketplace.json` entry added (16th plugin in monkey-skills marketplace).
