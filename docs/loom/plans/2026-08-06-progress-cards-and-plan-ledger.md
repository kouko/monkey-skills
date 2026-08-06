# Plan: progress cards + plan ledger default-on

Source brief: docs/loom/specs/2026-08-06-progress-cards-and-plan-ledger.md
Goal: the user sees the full plan + live progress at defined moments
    without asking, and the orchestrator re-anchors on the goal at every
    card render (fill-from-file via plan_card.py).
Stage: finishing
Total tasks: 9
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible (Wave 1 = T1-T7, disjoint files; T8 after Wave 1; T9 after T8)
Plan-document-reviewer verdict: PASS (2026-08-06, round 4 — rounds 1-3
NEEDS_REVISION each fixed-and-verified as new-finding deltas; round 4
clean 15/15)
Endpoint named: yes → continuous (user 「好」 froze the four-round
design; the arc runs to PR-open; merge stays with the user)

## Task 1 — plan-format: Goal/Stage headers + Status default-on

- Description: In loom-code/skills/writing-plans/references/plan-format.md:
  (a) add the two header lines to the header schema section, transcribed
  from ## Notes N1; (b) in the §Progress ledger section, flip the opt-in
  framing: writing-plans now EMITS `Status: pending` per task by default;
  a plan without Status fields (old plans) behaves as before — transcribe
  N1b. Create loom-code/scripts/test_plan_format_progress_fields.py
  pinning: `Goal:` schema line present, `Stage:` enum line present
  (planning / sdd:wave-N / review:round-N / finishing), the default-on
  sentence, the old-plan compatibility sentence, + a positive-fact
  control. Whitespace-normalized contiguous (helper shape from
  test_dispatch_hygiene_worktree_section.py).
- Module: loom-code/skills/writing-plans (reference)
- Files touched: loom-code/skills/writing-plans/references/plan-format.md, loom-code/scripts/test_plan_format_progress_fields.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-format.md (§header schema, §Progress ledger)
- Acceptance:
  - RED: new test fails against unedited plan-format.md (control passes).
  - GREEN: new test passes; `python3 -m pytest loom-code/scripts/ -q` green.
- Dependencies: none
- Independent: true
- Status: done(3001126e)
- Brief item covered: Smallest End State 1

## Task 2 — writing-plans: schema block + emit duty + plan-PASS card

- Description: In loom-code/skills/writing-plans/SKILL.md: (a) the
  minimal-structure fenced block gains three lines (`Goal:`, `Stage:
  planning`, and per-task `- Status: pending`), matching N1's schema;
  (b) insert the emit-duty + plan-PASS-card sentence N2 directly after
  the §Kickoff briefing section's closing sentence. Adjust
  loom-code/scripts/test_wp_extraction_pointers.py: if the new count
  exceeds the 3900 ceiling, raise the ceiling to (new count + 20) as a
  deliberate act (assert message updated to name this arc); extend the
  same file (or a small new test) with pins: N2's lead phrase, the
  command string `python3 scripts/plan_card.py`, the fire-and-continue
  clause, the `§(a2) Progress card` pointer, the inline-fallback field
  list. RED-first for the new pins.
  Ceiling-raise sweep: `3900` appears at THREE sites in
  test_wp_extraction_pointers.py — the module docstring (~:14), the
  function NAME `test_word_count_at_most_3900` (~:154), and the assert
  + message (~:156) — raise all three to the new ceiling (rename the
  function to match), assert message naming this arc. The rename
  touches ONLY this file — test_rcr_extraction_pointers.py:149 has a
  same-named function for a different skill; leave it untouched.
- Module: loom-code/skills/writing-plans
- Files touched: loom-code/skills/writing-plans/SKILL.md, loom-code/scripts/test_wp_extraction_pointers.py
- Context paths:
  - loom-code/scripts/test_wp_extraction_pointers.py (ceiling pin location)
- Acceptance:
  - RED: new pins fail against unedited SKILL.md; AND, after the
    SKILL.md edit and before the ceiling raise,
    test_wp_extraction_pointers.py::test_word_count_at_most_3900 fails
    (word count > 3900) — observe both REDs.
  - GREEN: full wp pin file green; word count reported; the three-site
    ceiling raise present and named.
- Dependencies: none
- Independent: true
- Status: done(002450b5)
- Brief item covered: Smallest End State 2 + 4; Decisions "fill-from-file
  enforced mechanically" + "ceiling raises are deliberate acts"

## Task 3 — plan_card.py renderer + tests

- Description: Create scripts/plan_card.py: argv = one plan-file path;
  parses `Goal:`, `Stage:`, task headings (`## Task N — <name>`), and
  per-task `- Status: <value>` lines; prints the card body exactly in
  the N5-variant field order:
  line 1 `🎯 <goal>`; line 2 `tasks: ✅D ⏳C ⬜P 🚫B` (done/claimed/
  pending/blocked counts; done matches `done(`, claimed matches
  `claimed(`); then one line per task `<mark> T<N> <name>`; then
  `stage: <stage>`; then `next: <first task whose status is not done>`
  or `next: close-out` when all done. A plan missing `Goal:` or
  `Stage:` or having zero tasks → exit 1 with a one-line loud message
  naming the missing field (never render a partial card). Tests
  scripts/test_plan_card.py RED-first: happy path (mixed statuses,
  exact stdout), all-done → `next: close-out`, missing-Goal exit 1,
  statusless old plan → exit 1 naming Status, no-Task-headings exit 1.
  Stdlib only, conventions from scripts/backlog_index.py +
  scripts/test_backlog_index.py.
- Module: scripts (repo-root; CI lane runs `pytest scripts/`)
- Files touched: scripts/plan_card.py, scripts/test_plan_card.py
- Context paths:
  - scripts/backlog_index.py (CLI + parsing conventions)
- Acceptance:
  - RED: tests fail before the script exists (subprocess non-zero with
    a real-run assertion, per the false-green memory rule).
  - GREEN: `python3 -m pytest scripts/test_plan_card.py -q` green; live
    run against THIS plan file exits 1 loudly IF this plan predates the
    emit duty (no Status fields) — assert whichever is true honestly.
- Dependencies: none
- Independent: true
- Status: done(01232d35)
- Brief item covered: Smallest End State 3; Decision "dual-audience
  mechanics" (the rendered card entering context is the recitation)

## Task 4 — SDD: wave-card cadence + Stage duty + ceiling raise

- Description: In loom-code/skills/subagent-driven-development/SKILL.md
  §Asking the user, replace the existing "**Delivery form.**" paragraph
  with N3 (transcribe verbatim — it keeps the family-relay pointer and
  adds: render via plan_card.py at every wave completion and stage
  transition; update the plan's `Stage:` header in the same ledger
  commit; inline-fallback field list). Raise the ceiling in
  loom-code/scripts/test_sdd_extraction_pointers.py:81 from 3900 to
  (new count + 20), assert message naming this arc (MANDATORY — current
  headroom is 3 words). Create
  loom-code/scripts/test_sdd_progress_card_duty.py pinning: N3's lead,
  the command string, the Stage-update duty, BOTH pointers
  (`§Family relay discipline` and `§(a2) Progress card`), the fallback
  field list, + a positive-fact control. RED-first.
- Module: loom-code/skills/subagent-driven-development
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md, loom-code/scripts/test_sdd_extraction_pointers.py, loom-code/scripts/test_sdd_progress_card_duty.py
- Context paths:
  - loom-code/scripts/test_sdd_extraction_pointers.py:81 (WORD_CEILING)
- Acceptance:
  - RED: new pin file fails against unedited SKILL.md; AND, after the
    Delivery-form replacement and before raising WORD_CEILING at :81,
    test_sdd_extraction_pointers.py's ceiling assertion fails — observe
    both REDs.
  - GREEN: both SDD test files green; new ceiling named; word count
    reported; AND `python3 -m pytest loom-pipeline/scripts/test_family_relay.py -q`
    green — test_sdd_pointer's ≥2 "§Family relay discipline"
    phrase-count must survive the N3 replacement (N3 deliberately
    keeps that phrase alongside the new §(a2) reference).
- Dependencies: none
- Independent: true
- Status: done(d7e7f749)
- Brief item covered: Smallest End State 5; Decisions "fill-from-file
  enforced mechanically" + "ceiling raises are deliberate acts"

## Task 5 — finishing: entry card + gate-stop clause

- Description: In loom-code/skills/finishing-a-development-branch/SKILL.md:
  (a) insert sentence N4a into the Default flow step 1 (render the card
  once on entry; no plan or old-format plan → skip silently; script or
  family-relay absent → render the four fields inline); (b) append
  clause N4b to the §ASK rationale paragraph (every gate-STOP surface
  leads with the card). Create
  loom-code/scripts/test_finishing_progress_card.py pinning: N4a's
  lead, the command string, the `§(a2) Progress card` pointer, the
  inline-fallback field list, N4b's gate-STOP clause, + a
  positive-fact control. RED-first. Word count ≤4500.
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_progress_card.py
- Context paths:
  - loom-code/scripts/test_finishing_backlog_close.py (helper shape)
- Acceptance:
  - RED: new pin file fails against unedited SKILL.md (control passes).
  - GREEN: all finishing pin files green; wc ≤4500.
- Dependencies: none
- Independent: true
- Status: done(091d62a1)
- Brief item covered: Smallest End State 6

## Task 6 — family-relay progress-card variant + loom-pipeline 0.13.0

- Description: In loom-pipeline/hooks/family-relay.md, insert the
  progress-card variant block N5 immediately BEFORE the
  `### (b) Visual defaults` heading (N5's own heading is
  `### (a2) Progress card`, same level as its siblings); bump
  loom-pipeline/.claude-plugin/plugin.json (and its .codex-plugin
  mirror if present) 0.12.0 → 0.13.0; prepend loom-pipeline/CHANGELOG.md
  entry N7. Create loom-pipeline/scripts/test_family_relay_progress_card.py
  (beside the existing test_family_relay.py — loom-pipeline's own
  pytest CI lane, the real precedent home) pinning:
  the variant heading, the four field names in order, the localization
  rule sentence, + a positive-fact control (§(a) heading). RED-first.
- Module: loom-pipeline/hooks
- Files touched: loom-pipeline/hooks/family-relay.md, loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/CHANGELOG.md, loom-pipeline/scripts/test_family_relay_progress_card.py
- Context paths:
  - loom-pipeline/hooks/family-relay.md (§(a) block)
- Acceptance:
  - RED: new pin file fails against unedited family-relay.md.
  - GREEN: the assertions T6 OWNS green —
    test_family_relay_progress_card.py (all) +
    test_family_relay.py::test_relay_section +
    ::test_reception_includes_visual_defaults (the rollup markers,
    anti-copy assertion, and session-start §(b) awk-range extraction
    all survive the insertion, which is why N5 lands immediately
    BEFORE `### (b)`); the FULL loom-pipeline lane green is T8's joint
    gate (a mid-wave test_sdd_pointer red belongs to T4, not here);
    both loom-pipeline manifests read 0.13.0; CHANGELOG heading
    present.
- Dependencies: none
- Independent: true
- Status: done(71d9859b)
- Brief item covered: Smallest End State 7 + Smallest End State 9
  (loom-pipeline half); Decision "cross-plugin coordination"

## Task 7 — Codex hook backlog entry update (ride-along, data-only)

- Description: In docs/loom/backlog/2026-07-06-codex-hook-events-apply-patch-handler-emits-none.md,
  append body block N8 (upstream state researched 2026-08-06:
  apply_patch handler fixed by openai/codex PR #18289 merged
  2026-04-20; the probed symptom likely the still-open repo-local
  config silent-no-fire bug openai/codex#17532; status stays UPSTREAM
  — the remaining trigger is #17532 closing or our next Codex-side
  re-probe). Frontmatter status unchanged → no index regeneration
  expected; run `python3 scripts/backlog_index.py --check` to confirm
  (exit 0), and `--validate` exit 0.
- Module: docs/loom/backlog
- Files touched: docs/loom/backlog/2026-07-06-codex-hook-events-apply-patch-handler-emits-none.md
- Context paths:
  - docs/loom/backlog/README.md (body-update conventions)
- Acceptance:
  - RED: N/A-adjacent — the deterministic pre/post check is the grep
    pair: `grep -c "18289"` on the entry exits with 0 matches before
    the edit and ≥1 after.
  - GREEN: the grep finds N8's PR reference; `--check` and `--validate`
    both exit 0.
- Dependencies: none
- Independent: true
- Status: done(01e4fda7)
- Review-weight: prose
- Brief item covered: Smallest End State 8

## Task 8 — bump loom-code 0.60.0

- Description: Both loom-code manifests → 0.60.0; prepend CHANGELOG
  entry N6; rewrite test_docs_review_blocking_class.py version pin
  0.59.0 → 0.60.0 (name, docstring, assertions, messages). RED-first.
- Module: loom-code (manifests + changelog)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md ([0.59.0] head)
- Acceptance:
  - RED: rewritten version-pin test fails pre-bump.
  - GREEN: full `python3 -m pytest loom-code/scripts/ scripts/ loom-pipeline/scripts/ -q` passes.
- Dependencies: Tasks 1, 2, 3, 4, 5, 6, 7 complete first
- Independent: false
- Status: done(81cf2aea)
- Review-weight: mechanical
- Brief item covered: Smallest End State 9 (loom-code half; the
  loom-pipeline half ships in Task 6)

## Task 9 — three-leg haiku probes + dogfood report

- Description: Dispatch three haiku cold-read probes (by-path against
  the edited tree): (a) card comprehension — given a real
  `plan_card.py` render of THIS arc's plan mid-flight, answer the goal
  / who is done / what's next; (b) SDD wave duty — a wave just
  completed: what command runs, what gets updated (Stage line), what
  gets relayed and in what language; (c) fill-from-file + degradation —
  why may the card never be composed from memory (what enforces it),
  and what happens when family-relay.md is absent (four fields inline,
  nothing dropped). Write
  docs/loom/dogfood/2026-08-06-progress-cards-probe.md with verbatim
  quotes and CLEAN/FAIL per leg.
- Module: docs/loom/dogfood
- Files touched: docs/loom/dogfood/2026-08-06-progress-cards-probe.md
- Context paths:
  - docs/loom/dogfood/2026-08-06-backlog-ready-verb-probe.md (report shape)
- Acceptance:
  - RED: a probe leg answering with the old behavior (composes a card
    from memory, skips the Stage update, or claims the card is lost
    without family-relay) is the failure signal — any FAIL blocks
    close-out until wording is fixed and the leg re-probed.
  - GREEN: report exists at the named path, all three legs CLEAN with
    verbatim supporting quotes.
- Dependencies: Task 8 completes first
- Independent: false
- Status: done(7cbd0a60)
- Review-weight: prose
- Brief item covered: Smallest End State 10

## Notes

Kickoff decisions: no one-way doors — all additive; ceiling raises are
deliberate and changelog-noted; below-threshold decisions log here.
Counting convention: `len(text.split())`.

**Pinned canonical texts — transcribe VERBATIM**:

N1 — plan-format header schema addition (two lines added to the header
block, after the `Source brief:` line):

```markdown
Goal: <one sentence transcribed from the brief's Smallest End State at
    plan time — frozen with the plan; never edited afterward>
Stage: <planning | sdd:wave-N | review:round-N | finishing — updated by
    the orchestrator at each transition, committed with the nearest
    ledger or close-out commit>
```

N1b — Progress ledger default-on sentences (replacing the opt-in
framing sentence in §Progress ledger; the surrounding write-back
protocol is unchanged):

```markdown
The ledger is DEFAULT-ON: writing-plans emits `Status: pending` on
every task at plan time. A plan without `Status` fields (written
before this default) behaves exactly as before — the ledger stays
opt-in-by-presence for old plans.
```

N2 — writing-plans emit duty + plan-PASS card (one paragraph, inserted
after §Kickoff briefing's closing sentence):

```markdown
**Progress surface.** The plan carries `Goal:`, `Stage:`, and
per-task `Status:` from birth (schema above). After the reviewer PASS
is stamped, run `python3 scripts/plan_card.py <plan-path>` and relay
its card in the conversation language — fire-and-continue, not a new
pause, framed per `loom-pipeline/hooks/family-relay.md §(a2) Progress
card` (file or script absent → render the four fields inline: goal,
task table, stage, next). The card re-reads the plan file by
construction; never compose it from memory.
```

N3 — SDD Delivery-form paragraph (replaces the existing "**Delivery
form.**" paragraph verbatim):

```markdown
**Delivery form.** Every per-wave status report, stage transition, and
checkpoint sign-off renders the progress card first: run
`python3 scripts/plan_card.py <plan-path>` and relay its output in the
live conversation language, framed per
`loom-pipeline/hooks/family-relay.md §Family relay discipline` —
progress-card variant `§(a2) Progress card` (file or script absent →
render the four fields inline: goal, task table, stage, next —
nothing is dropped). Update the plan's `Stage:` header
in the same commit as that wave's ledger writes. The card re-reads the
plan file by construction — never compose it from memory. **Never copy
the card template body here; point at it.** Internal machine traffic
(verdict tokens, wave labels) stays precise below the card.
```

N4a — finishing entry sentence (appended to Default flow step 1):

```markdown
When the branch has a plan carrying the progress headers, render the
card once on entry (`python3 scripts/plan_card.py <plan-path>`, framed
per `loom-pipeline/hooks/family-relay.md §(a2) Progress card`) so the
user sees the whole arc before the gates run. No plan or old-format
plan → skip silently; script or family-relay absent → render the four
fields inline: goal, task table, stage, next.
```

N4b — gate-STOP clause (appended to the §ASK rationale paragraph):

```markdown
Every gate STOP that surfaces to the user (a NEEDS_REVISION, a privacy
BLOCK, a probe FAIL) leads with the progress card — the user sees
where the arc stopped before deciding.
```

N5 — family-relay progress-card variant (inserted immediately before
the `### (b) Visual defaults` heading, own heading level ###):

```markdown
### (a2) Progress card

The plan-progress variant of the rollup card. Field order is fixed:
**Goal** (one line, verbatim from the plan header), **task table**
(✅ done / ⏳ claimed / ⬜ pending / 🚫 blocked, counts then rows),
**Stage**, **next** (first not-done task, or close-out). The body is
rendered mechanically by `scripts/plan_card.py` — the relayer adds
only a one-line conversational frame in the live conversation
language, same localized-content rule as the rollup card above. Never
re-order or drop fields; never compose the body by hand when the
script is available.
```

N6 — loom-code CHANGELOG entry:

```markdown
## [0.60.0] — 2026-08-06 — the plan becomes the progress surface

### Added

- **Plans carry Goal/Stage headers and a default-on Status ledger.**
  writing-plans emits `Status: pending` per task from birth; the
  orchestrator updates `Stage:` at transitions. Old plans without the
  fields behave as before.
- **Progress cards at defined moments, rendered by script.**
  `scripts/plan_card.py` projects the plan file into a fixed-field
  card (goal / task table / stage / next; exit 1 on missing fields).
  writing-plans relays it at plan PASS, SDD at every wave completion
  and stage transition, finishing at entry and on every gate STOP —
  fill-from-file by construction (the industry recitation pattern:
  the card entering recent context re-anchors the orchestrator on the
  goal), advisory-tier, no hook dependency, Codex-compatible. The SDD
  and writing-plans pin ceilings rise deliberately to admit the duty
  paragraphs (the banked-headroom contract honored, not bypassed).
```

N7 — loom-pipeline CHANGELOG entry:

```markdown
## [0.13.0] — 2026-08-06

### Added

- family-relay.md gains §(a2) Progress card — the plan-progress
  variant of the user-rollup card (goal / task table / stage / next,
  body rendered by loom-code's `scripts/plan_card.py`, relayer adds
  only a localized one-line frame).
```

N8 — Codex hook backlog entry body addition:

```markdown
Upstream state re-researched 2026-08-06 (web, not a live re-probe):
the apply_patch handler gap this entry recorded was fixed upstream by
openai/codex PR #18289 (merged 2026-04-20); the symptom our live probe
hit is now more likely openai/codex#17532 (repo-local `.codex/`
config hooks silently not firing in interactive sessions — still open
as of 2026-08-06). Status stays UPSTREAM: the trigger is #17532
closing, or our next Codex-side live re-probe, whichever first.
```

## Decision Log

- 2026-08-06: card body format (emoji marks, field order) is pinned
  once in N5 and implemented once in plan_card.py — the two are the
  same spec; test_plan_card.py pins the implementation, the N5 pin
  test pins the description; a future format change edits both in one
  commit (falsified-neighbor duty named here in advance).
- 2026-08-06: T9 probes run by-path against the edited tree.
- 2026-08-06 (wave-1 execution riders, both implementer-flagged +
  orchestrator-approved): plan-format.md:74-77's per-task Status
  annotation aligned to default-on (was OPTIONAL/Default-OMITTED — the
  falsified neighbor T1 honestly reported); N2's "(schema above)"
  shipped as "(schema below)" in writing-plans SKILL.md (the schema
  block follows the insertion point; the plan's N2 block retains the
  original wording as the planning-time snapshot). This plan's own
  ledger backfilled at wave-1 close (the plan predates the emit duty
  it ships — needed for T9 leg (a)'s real-card probe).
- 2026-08-06 (corrected round 2): T6's pin test lives in
  loom-pipeline/scripts/ beside the existing test_family_relay.py —
  loom-pipeline HAS its own pytest CI lane
  (.github/workflows/loom-pipeline-ci.yml), which round 1's entry
  mis-stated; the cross-plugin CONTRACT coupling is still deliberate
  (test_family_relay.py already pins SDD's pointer phrase from that
  lane, so the precedent existed all along), and T4/T8's GREENs now
  run that lane explicitly.
- 2026-08-06 (round-3 fixes): the `§(a2)` pointer pin propagated to
  T2 and T4 (T5's round-2 fix had not swept its siblings — the
  fix-skips-neighbor class again); T4 pins BOTH pointers so the Gap-A
  invariant is locally visible; T6's GREEN scoped to the assertions it
  owns (full-lane green stays T8's joint gate). Reviewer's fail-open
  note (loom-pipeline-ci paths filter omits the consumer files
  test_family_relay.py reads — a loom-code-only PR can drop the
  pointer ungated) is pre-existing and out of this arc's scope →
  backlog entry to be filed at close-out.
- 2026-08-06 (round-2 fixes): N3 keeps BOTH pointers ("§Family relay
  discipline" + "§(a2) Progress card") so test_family_relay.py's ≥2
  phrase-count invariant survives; T4/T6/T8 GREENs run the
  loom-pipeline lane; T6's test relocated to loom-pipeline/scripts/;
  T5's gloss aligned to fixed N4a and its pin spec itemized; N5 label
  line aligned; T2 rename scoped away from RCR's same-named function.
- 2026-08-06 (round-1 fixes): N2/N4a gained the family-relay pointer;
  N4a's degradation split (no-plan → skip; script/file absent → inline
  fields, matching the brief's rule); N3 re-carries the never-copy
  sentence; T2/T4 gained ceiling-leg REDs (T2's names the three 3900
  sites incl. the function rename); T6 insertion anchored before
  `### (b) Visual defaults`; SES-9/Decision traceability spread onto
  T2/T3/T4/T6/T8.
- 2026-08-06: commit 2c4c4793 (T9 ledger write-back) reuses 7cbd0a60's
  probe-report message verbatim — an index.lock race split one chain
  into two commits and the retry inherited the message; content
  correct, messages collapse at squash-merge; recorded for the log's
  honesty.
- 2026-08-06 (round-2 whole-branch): the round-2 plan-review entry
  above ('N3 keeps BOTH pointers so the ≥2 invariant survives') was
  superseded by the review fix commit — SDD:171 now routes via the
  Delivery-form cross-reference, and test_family_relay.py's invariant
  deliberately moved to ≥1 + the cross-reference literal (rationale in
  that test's docstring); recorded so the dated entries read in
  sequence.
