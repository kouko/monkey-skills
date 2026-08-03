# Plan: loom family connective tissue — reception, uniform entries, §Intake

**Source brief**: docs/loom/specs/2026-07-04-loom-family-connective-tissue.md
**Total tasks**: 17
**Critical-path depth**: 5 (F1a → F1b → F1c → F2 → F3)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-04, 14/14 checks, round 2)

## Plan-level notes (settle brief §Open Questions)

1. **Reception content lives in `loom-pipeline/hooks/family-reception.md`**
   (hooks/ is not a skill folder — flat rule not in play); the hook script
   injects that file, NOT using-loom-pipeline/SKILL.md. Structural test caps
   it at ≤60 non-empty lines (brief §Open Q1).
2. **Harness home = `loom-code/scripts/`** (brief §Open Q4): the only
   plugin scripts dir already wired into pytest CI; harness unit tests ride
   the existing suite. Live behavioral runs are manual/in-session (need the
   `claude` CLI + tokens), never CI.
3. Versions: loom-pipeline 0.3.1→0.4.0, loom-product-principles 0.3.0→0.4.0,
   loom-spec 0.3.1→0.4.0, loom-interface-design 0.3.0→0.4.0, loom-code
   0.21.2→0.22.0 (all additive → minor). Each plugin's bump rides its own
   final task with its CHANGELOG + Codex-manifest sync.
4. **Wave discipline** (parallel implementers on one branch, learned on PR
   #483's wave): stage only your own files; on `git commit` verify
   `git show --stat HEAD` afterward; index.lock → retry ≤3.
5. **loom-code's family-entry §Intake = brainstorming's Axis 0**
   (deliberate, per the brief's "loom-code's full brainstorming is the
   thickest instance" framing): `using-loom-code/SKILL.md` does NOT gain a
   duplicate §Intake heading — it gains the red-flag row + family pointer
   (Task E2), and the intake work lives in brainstorming (Task E1). The
   §Intake-presence structural test therefore covers the OTHER four
   entries + brainstorming's Axis 0.
6. **Task F3 is orchestrator-run**: SDD must NOT dispatch an implementer
   for it — the orchestrator executes it directly (live `claude` CLI +
   branch skills reloaded), after all other tasks are DONE.

## Task A1 — family reception: content + hook mechanism (loom-pipeline)

- **Description**: Create `loom-pipeline/hooks/family-reception.md` (≤60
  non-empty lines): family map (five `using-loom-*` entries, one line
  each), the three doors (interactive design-side / interactive loom-code /
  explicit Workflow pipeline+batch — states verbatim that the Workflow door
  is described, never auto-opened), and the **on-ramp criteria table**
  (SSOT): no `docs/loom/PRINCIPLES.md` + product-shaped work →
  product-principles first; user-facing surface + no DESIGN.md/ui-flows →
  interface-design first; multi-state/multi-object + no spec/change-folder →
  spec-expansion first; negative guard: bug fix / refactor / test-covered
  increment → do not interrupt; recommend-once + record-choice rule. Create
  `loom-pipeline/hooks/hooks.json` + `loom-pipeline/hooks/session-start`
  (bash) mirroring loom-code's mechanism (SessionStart matcher
  `startup|clear|compact`; emits the canonical
  `hookSpecificOutput.additionalContext` + the two defensive keys).
- **Module**: `loom-pipeline/hooks/` (new)
- **Files touched**: `loom-pipeline/hooks/family-reception.md`, `loom-pipeline/hooks/hooks.json`, `loom-pipeline/hooks/session-start`, `loom-pipeline/scripts/test_pipeline_reception.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/hooks/hooks.json
  - /Users/kouko/GitHub/monkey-skills/loom-code/hooks/session-start
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-04-loom-family-connective-tissue.md (§Smallest End State 1)
- **Acceptance**:
  - **RED**: `test_pipeline_reception.py::test_reception_content_contract` fails (files absent)
  - **GREEN**: test asserts ≤60 non-empty lines; five `using-loom-*` names present; "never auto" phrase for the Workflow door; all three criteria rows + negative guard present; hooks.json shape matches loom-code's (matcher + command); session-start is executable and emits the three context keys (run it, parse JSON)
- **External surfaces**:
  - Internal sibling contract: Claude Code SessionStart hook shape — grounding: in-repo evidence `loom-code/hooks/hooks.json` + `loom-code/hooks/session-start` (live-proven mechanism)
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: "Family reception (loom-pipeline hook) … family map … three doors … on-ramp criteria table (SSOT)" (Smallest End State 1) + Decision §"Front door lives in loom-pipeline (P2)"

## Task A2 — §Intake for using-loom-pipeline

- **Description**: Add the `## §Intake` section to
  `loom-pipeline/skills/using-loom-pipeline/SKILL.md`: step 1 前站檢查
  (reference the reception criteria table — point, don't copy), step 2
  對站檢查 (interactive work → hand to the right interactive entry), step 3
  reaffirms the explicit-invocation + Workflow-availability fire condition
  VERBATIM-preserving the existing N/A-loud wording (brief §Open Q2: no
  softening of the never-hand-drive constitution). Extend
  `test_pipeline_skill_contract.py` with the §Intake presence + N/A-wording
  preservation assertions.
- **Module**: `loom-pipeline/skills/using-loom-pipeline/SKILL.md`
- **Files touched**: `loom-pipeline/skills/using-loom-pipeline/SKILL.md`, `loom-pipeline/scripts/test_pipeline_skill_contract.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-pipeline/skills/using-loom-pipeline/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-pipeline/hooks/family-reception.md (criteria SSOT, from Task A1)
- **Acceptance**:
  - **RED**: `test_pipeline_skill_contract.py::test_skill_intake_section_contract` fails (section absent)
  - **GREEN**: §Intake present with the three steps; existing N/A-loud phrases still byte-present; suite green
- **Dependencies**: Task A1 completes first
- **Independent**: true
- **Brief item covered**: "§Intake contract — a uniformly named first section in all five family entries" (Smallest End State 3) + Open Q2

## Task A3 — loom-pipeline README, CHANGELOG, version 0.4.0

- **Description**: README gains §Family entries & naming convention
  (`using-loom-*` = entry; artifact names = stations; `brainstorming` =
  loom-code's discovery skill; one-sentence rule 「要用 loom-X 就從
  using-loom-X 開始」) and a reception paragraph; CHANGELOG `[0.4.0]`
  entry; plugin.json 0.3.1→0.4.0; `python3 scripts/sync_codex_manifests.py
  loom-pipeline`; extend `test_pipeline_readme.py` with the
  naming-convention presence assertion.
- **Module**: `loom-pipeline/README.md`
- **Files touched**: `loom-pipeline/README.md`, `loom-pipeline/CHANGELOG.md`, `loom-pipeline/.claude-plugin/plugin.json`, `loom-pipeline/.codex-plugin/plugin.json`, `loom-pipeline/scripts/test_pipeline_readme.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-pipeline/README.md
  - /Users/kouko/GitHub/monkey-skills/loom-pipeline/hooks/family-reception.md
- **Acceptance**:
  - **RED**: `test_pipeline_readme.py::test_readme_family_naming_convention` fails
  - **GREEN**: README documents the convention; grep `"version": "0.4.0"` exits 0; `sync_codex_manifests.py --check loom-pipeline` rc=0; manifest tests green
- **Dependencies**: Tasks A1, A2 complete first
- **Independent**: true
- **Brief item covered**: "Naming convention documented" (Smallest End State 6)

## Task B1 — new thin entry: using-loom-product-principles

- **Description**: Create
  `loom-product-principles/skills/using-loom-product-principles/SKILL.md`:
  §Intake (step 1 references the reception criteria; step 2 redirects
  spec/design/code asks to their entries; step 3 hands off to
  `product-principles`). Description tuned as ENTRY (guidance intent), must
  not steal `product-principles`' direct asks (#456 positive-specificity
  rule; near-miss corpus will verify). Add
  `loom-product-principles/scripts/test_entry_skill.py` (structural: file
  exists, §Intake three steps, description mentions entry/routing not
  generation).
- **Module**: `loom-product-principles/skills/using-loom-product-principles/` (new)
- **Files touched**: `loom-product-principles/skills/using-loom-product-principles/SKILL.md`, `loom-product-principles/scripts/test_entry_skill.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-pipeline/hooks/family-reception.md
  - /Users/kouko/GitHub/monkey-skills/loom-interface-design/skills/using-loom-interface-design/SKILL.md (existing thin-entry style reference)
- **Acceptance**:
  - **RED**: `test_entry_skill.py::test_using_entry_intake_contract` fails (skill absent)
  - **GREEN**: SKILL.md present with §Intake; frontmatter description ≤ house length norms and entry-framed; plugin suite green
- **Dependencies**: Task A1 completes first
- **Independent**: true
- **Brief item covered**: "Two new thin entry skills … completing the using-loom-* convention" (Smallest End State 2)

## Task B2 — product-principles cross-ref + plugin 0.4.0

- **Description**: `product-principles/SKILL.md` gains a next-station
  close-out line (PRINCIPLES.md done → `using-loom-interface-design` for
  UI-bearing products, or `using-loom-spec` to expand a feature); CHANGELOG
  `[0.4.0]`; plugin.json 0.3.0→0.4.0; Codex manifest sync. Keep the ~73-char
  compression debt untouched (separate parked item).
- **Module**: `loom-product-principles/skills/product-principles/SKILL.md`
- **Files touched**: `loom-product-principles/skills/product-principles/SKILL.md`, `loom-product-principles/CHANGELOG.md`, `loom-product-principles/.claude-plugin/plugin.json`, `loom-product-principles/.codex-plugin/plugin.json`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-product-principles/skills/product-principles/SKILL.md
- **Acceptance**:
  - **RED**: diagnostic — grep for a next-station line naming `using-loom-interface-design` in product-principles/SKILL.md exits non-zero
  - **GREEN**: grep exits 0; `sync_codex_manifests.py --check loom-product-principles` rc=0; plugin suite (56+ tests) green
- **Dependencies**: Task B1 completes first
- **Independent**: true
- **Brief item covered**: "Interactive chain cross-refs — each design-side station's output states its next station" (Smallest End State 4)

## Task C1 — new thin entry: using-loom-spec

- **Description**: Create `loom-spec/skills/using-loom-spec/SKILL.md`:
  §Intake (step 1 reception criteria; step 2 redirect; step 3 disambiguates
  `spec-expansion` (draft from seed) vs `completeness-critic` (critique an
  existing draft) — the #456-documented adjacent mis-route). Description
  entry-framed, no stealing of members' direct asks. Add
  `loom-spec/scripts/test_entry_skill.py` (structural).
- **Module**: `loom-spec/skills/using-loom-spec/` (new)
- **Files touched**: `loom-spec/skills/using-loom-spec/SKILL.md`, `loom-spec/scripts/test_entry_skill.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-spec/skills/spec-expansion/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-spec/skills/completeness-critic/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-pipeline/hooks/family-reception.md
- **Acceptance**:
  - **RED**: `test_entry_skill.py::test_using_entry_intake_contract` fails (skill absent)
  - **GREEN**: SKILL.md present with §Intake incl. expansion-vs-critic disambiguation phrases; plugin suite green
- **Dependencies**: Task A1 completes first
- **Independent**: true
- **Brief item covered**: "Two new thin entry skills … spec's entry also disambiguates expansion vs critic" (Smallest End State 2)

## Task C2 — spec-expansion cross-ref + plugin 0.4.0

- **Description**: Verify/add spec-expansion's next-station line (validated
  change-folder → `loom-code:writing-plans` consumes it — wiring exists;
  make the pointer explicit if absent); CHANGELOG `[0.4.0]`; plugin.json
  0.3.1→0.4.0; Codex sync.
- **Module**: `loom-spec/skills/spec-expansion/SKILL.md`
- **Files touched**: `loom-spec/skills/spec-expansion/SKILL.md`, `loom-spec/CHANGELOG.md`, `loom-spec/.claude-plugin/plugin.json`, `loom-spec/.codex-plugin/plugin.json`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-spec/skills/spec-expansion/SKILL.md
- **Acceptance**:
  - **RED**: diagnostic — grep for `writing-plans` next-station pointer in spec-expansion/SKILL.md §close-out exits non-zero (skip-note if already present: flip task to verify-only, record in commit)
  - **GREEN**: pointer present; `sync_codex_manifests.py --check loom-spec` rc=0; suite green
- **Dependencies**: Task C1 completes first
- **Independent**: true
- **Brief item covered**: "spec → writing-plans is already wired" verification + Smallest End State 4

## Task D1 — §Intake for using-loom-interface-design

- **Description**: Add `## §Intake` to
  `loom-interface-design/skills/using-loom-interface-design/SKILL.md`
  (step 1: PRINCIPLES.md check per reception criteria → recommend
  `using-loom-product-principles` when absent; step 2 redirect; step 3
  existing design-system/interaction-flows routing). Add structural test
  in `loom-interface-design/scripts/` following that plugin's existing test
  conventions.
- **Module**: `loom-interface-design/skills/using-loom-interface-design/SKILL.md`
- **Files touched**: `loom-interface-design/skills/using-loom-interface-design/SKILL.md`, `loom-interface-design/scripts/test_entry_intake.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-interface-design/skills/using-loom-interface-design/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-pipeline/hooks/family-reception.md
- **Acceptance**:
  - **RED**: `test_entry_intake.py::test_using_entry_intake_contract` fails
  - **GREEN**: §Intake present; plugin suite green
- **Dependencies**: Task A1 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State 3 (§Intake in all five family entries)

## Task D2a — design-system cross-ref

- **Description**: `design-system/SKILL.md` gains a next-station close-out
  line (DESIGN.md done → `using-loom-spec` to expand the feature, or
  `interaction-flows` if flows not yet mapped).
- **Module**: `loom-interface-design/skills/design-system/SKILL.md`
- **Files touched**: `loom-interface-design/skills/design-system/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-interface-design/skills/design-system/SKILL.md
- **Acceptance**:
  - **RED**: diagnostic — grep for `using-loom-spec` in design-system/SKILL.md exits non-zero
  - **GREEN**: pointer present; plugin suite green
- **Dependencies**: Task D1 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State 4 (design → spec cross-ref)

## Task D2b — interaction-flows cross-ref + plugin 0.4.0

- **Description**: `interaction-flows/SKILL.md` gains the next-station
  close-out line (ui-flows.md done → `using-loom-spec`); then the plugin
  close-out: CHANGELOG `[0.4.0]`, plugin.json 0.3.0→0.4.0, Codex sync.
- **Module**: `loom-interface-design/skills/interaction-flows/SKILL.md`
- **Files touched**: `loom-interface-design/skills/interaction-flows/SKILL.md`, `loom-interface-design/CHANGELOG.md`, `loom-interface-design/.claude-plugin/plugin.json`, `loom-interface-design/.codex-plugin/plugin.json`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-interface-design/skills/interaction-flows/SKILL.md
- **Acceptance**:
  - **RED**: diagnostic — grep for `using-loom-spec` in interaction-flows/SKILL.md exits non-zero
  - **GREEN**: pointer present; grep `"version": "0.4.0"` exits 0; `sync_codex_manifests.py --check loom-interface-design` rc=0; suite green
- **Dependencies**: Tasks D1, D2a complete first
- **Independent**: true
- **Brief item covered**: Smallest End State 4 (design → spec cross-ref) + plugin release mechanics

## Task E1 — brainstorming Axis 0 (loom-code)

- **Description**: Add "Axis 0 — upstream artifacts (§Intake steps 1-2)" to
  `loom-code/skills/brainstorming/SKILL.md`, positioned BEFORE Axis 1:
  check the target repo against the reception criteria table (point to it,
  don't copy); on trigger, surface the recommendation ONCE (design-side
  sequence named concretely), record the user's choice in the brief
  (`## Design-side on-ramp: offered — user chose <X>`), proceed either way;
  negative guard verbatim (bug fix / refactor / covered increment → skip
  Axis 0 silently). Structural test in loom-code/scripts/ asserting Axis 0
  presence + recommend-once + negative-guard phrases.
- **Module**: `loom-code/skills/brainstorming/SKILL.md`
- **Files touched**: `loom-code/skills/brainstorming/SKILL.md`, `loom-code/scripts/test_brainstorming_axis0.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/brainstorming/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-pipeline/hooks/family-reception.md
- **Acceptance**:
  - **RED**: `test_brainstorming_axis0.py::test_axis0_contract` fails (section absent)
  - **GREEN**: Axis 0 present before Axis 1 with the three load-bearing phrases (criteria reference / recommend-once+record / negative guard); loom-code suite green
- **Dependencies**: Task A1 completes first
- **Independent**: true
- **Brief item covered**: Decision §"Guidance without being asked rides the strongest existing mechanism" — the guarantee chain's checkpoint

## Task E2 — using-loom-code red-flag + family pointer + loom-code 0.22.0

- **Description**: `using-loom-code/SKILL.md` gains (a) one red-flag row:
  "skipping brainstorming's Axis 0 upstream check before writing a brief =
  violation", (b) one §Coexistence/family line pointing to the loom-pipeline
  reception as the family map (keep additions minimal — this file is
  hook-injected every session; net growth ≤15 lines). CHANGELOG `[0.22.0]`;
  plugin.json 0.21.2→0.22.0; Codex sync. MUST NOT break
  `tests/integration/test-superpowers-mode-off.sh` (hook 3-key check) or
  existing router tests.
- **Module**: `loom-code/skills/using-loom-code/SKILL.md`
- **Files touched**: `loom-code/skills/using-loom-code/SKILL.md`, `loom-code/CHANGELOG.md`, `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`, `loom-code/scripts/test_brainstorming_axis0.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/skills/using-loom-code/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/loom-code/hooks/session-start
- **Acceptance**:
  - **RED**: extend `test_brainstorming_axis0.py::test_router_axis0_red_flag` fails (row absent)
  - **GREEN**: red-flag row + family pointer present; net line growth of using-loom-code/SKILL.md ≤15 (test-asserted); full loom-code suite + hook integration test green; `sync_codex_manifests.py --check loom-code` rc=0
- **Dependencies**: Task E1 completes first
- **Independent**: false  # extends E1's test file — sequential by design
- **Brief item covered**: Smallest End State 4 ("one red-flag line in using-loom-code")

## Task F1a — harness: corpus parser + contamination filter

- **Description**: Create `loom-code/scripts/loom_firing_harness.py`
  (stdlib) with the corpus layer: JSONL corpus parser (query / expected
  skill or NONE / notes; validator warns on non-self-contained short lines
  — trap #2) and the session-limit contamination filter (detect via result
  subtype + "session limit" grep; contaminated records are DISCARDED, never
  graded — trap #3). TDD with canned fixtures; no live `claude` calls in
  tests.
- **Module**: `loom-code/scripts/loom_firing_harness.py` (new)
- **Files touched**: `loom-code/scripts/loom_firing_harness.py`, `loom-code/scripts/test_loom_firing_harness.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-07-04-loom-family-connective-tissue.md (§Smallest End State 5)
- **Acceptance**:
  - **RED**: `test_loom_firing_harness.py::test_corpus_parse_and_contamination_discard` fails (module absent)
  - **GREEN**: parser round-trips a fixture corpus; a contaminated record is DISCARDED with a count surfaced; loom-code suite green
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Behavioral-test harness lands in-repo … five documented method traps baked in" (Smallest End State 5 — traps #2, #3)

## Task F1b — harness: EXACT/FAMILY/MISS/OVER grader

- **Description**: Add `grade` mode to the harness: per-record scoring
  EXACT (fired = expected) / FAMILY (fired sibling in same loom family —
  counted separately from EXACT, trap #4) / MISS (expected a skill, none
  or non-loom fired) / OVER (expected NONE but a loom-family skill fired —
  non-loom fires do NOT count as OVER, trap #4's grader rule); per-corpus
  aggregate table. TDD with canned graded fixtures.
- **Module**: `loom-code/scripts/loom_firing_harness.py`
- **Files touched**: `loom-code/scripts/loom_firing_harness.py`, `loom-code/scripts/test_loom_firing_harness.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/scripts/loom_firing_harness.py
- **Acceptance**:
  - **RED**: `test_loom_firing_harness.py::test_grade_exact_family_miss_over` fails (grade mode absent)
  - **GREEN**: all four verdict classes graded correctly on fixtures incl. the expected=NONE + non-loom-fire → not-OVER case; suite green
- **Dependencies**: Task F1a completes first
- **Independent**: false
- **Brief item covered**: Smallest End State 5 (grading EXACT/FAMILY/MISS/OVER — traps #4)

## Task F1c — harness: live run mode (claude -p shell-out)

- **Description**: Add `run` mode: per corpus line, shell
  `claude -p "<q>" --max-turns 4 --allowedTools Skill --output-format
  stream-json --verbose` (max-turns configurable, floor 4 — trap #1),
  capture fired `Skill` tool_use `.input.skill` + result subtype into the
  record format F1a parses/F1b grades. Subprocess list-form args; TDD via
  a stub `claude` executable on PATH in tests (no real CLI calls).
- **Module**: `loom-code/scripts/loom_firing_harness.py`
- **Files touched**: `loom-code/scripts/loom_firing_harness.py`, `loom-code/scripts/test_loom_firing_harness.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/scripts/loom_firing_harness.py
- **Acceptance**:
  - **RED**: `test_loom_firing_harness.py::test_run_mode_captures_fired_skill` fails (run mode absent)
  - **GREEN**: stub-CLI test captures fired skill + subtype; `--max-turns 3` refused (floor guard); suite green
- **External surfaces**:
  - CLI flag: `claude -p --max-turns --allowedTools --output-format stream-json --verbose` — grounding: in-repo evidence memory project_loom_firing_test_router_asymmetry (live-proven 2026-06-24/25) + live re-verification during Task F3
- **Dependencies**: Task F1b completes first
- **Independent**: false
- **Brief item covered**: Smallest End State 5 (headless run mode — trap #1)

## Task F2 — firing corpus files

- **Description**: Create `docs/loom/firing-corpus/goal-oriented.jsonl`,
  `near-miss.jsonl`, `direct-ask.jsonl` in the harness's line format
  (query + expected skill or NONE + notes): goal-oriented = 「幫我做一個記帳
  app」-type utterances expecting the design-side recommendation path;
  near-miss = utterances that must NOT fire the two new entries (e.g.
  critique-an-existing-spec must go to completeness-critic, generic chat);
  direct-ask = #456's tuned direct asks expecting stations to keep firing
  (regression). ≥8 lines per file, self-contained phrasing (trap #2).
  Validated by the harness's corpus validator in a unit test.
- **Module**: `docs/loom/firing-corpus/` (new)
- **Files touched**: `docs/loom/firing-corpus/goal-oriented.jsonl`, `docs/loom/firing-corpus/near-miss.jsonl`, `docs/loom/firing-corpus/direct-ask.jsonl`, `loom-code/scripts/test_loom_firing_harness.py`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/scripts/loom_firing_harness.py
- **Acceptance**:
  - **RED**: `test_loom_firing_harness.py::test_shipped_corpus_validates` fails (files absent)
  - **GREEN**: all three corpus files parse + pass the self-containedness validator; each ≥8 entries
- **Dependencies**: Task F1c completes first
- **Independent**: false  # extends the harness test file — sequential by design
- **Brief item covered**: "Acceptance runs: (a) goal-oriented corpus … (b) near-miss corpus … (c) direct-ask corpus" (Smallest End State 5)

## Task F3 — live behavioral acceptance run + report

- **Description**: ORCHESTRATOR-RUN (not an implementer dispatch; needs the
  live `claude` CLI + the branch's skills installed/reloaded): execute the
  harness over the three corpora against the branch state, grade, and write
  `docs/loom/dogfood/2026-07-04-family-tissue-firing-test.md` (per-corpus
  score table, discarded-contamination count, verdict vs the brief's three
  acceptance criteria, any finding routed back as fix tasks). A failed
  criterion blocks branch close-out (this is the tissue's verification
  gate, mirroring the brief's "behavior is the acceptance, not prose").
- **Module**: `docs/loom/dogfood/` (report)
- **Files touched**: `docs/loom/dogfood/2026-07-04-family-tissue-firing-test.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/loom-code/scripts/loom_firing_harness.py
  - /Users/kouko/GitHub/monkey-skills/docs/loom/firing-corpus/
- **Acceptance**:
  - **RED**: diagnostic — report file absent before the run
  - **GREEN**: report exists with all three corpora graded; goal-oriented recommendation-surfacing ≥ agreed threshold; near-miss OVER=0 for the two new entries; direct-ask parity with #456 (2/2-equivalent)
- **External surfaces**:
  - CLI flag: `claude -p …` live invocation — grounding: live verification (this task IS the live verification)
- **Dependencies**: Tasks A1, A2, A3, B1, B2, C1, C2, D1, D2a, D2b, E1, E2, F1a, F1b, F1c, F2 complete first
- **Independent**: false
- **Brief item covered**: Smallest End State 5 acceptance runs + Users §"the model needs the guidance to sit on surfaces it reliably reads"

## Notes

- **Critical path**: F1a → F1b → F1c → F2 → F3 = depth 5. The plugin
  tracks are shallower: A1 → (A2 | B1 | C1 | D1 | E1) → (A3 | B2 | C2 |
  D2a | E2) → D2b → F3 joins.
- **Wave 2 (post-A1) parallel-eligible**: A2, B1, C1, D1, E1 (disjoint
  files, `Independent: true`) — F1a runs alongside from the start; wave
  discipline per plan-level note 4. Wave 3: A3, B2, C2, D2a (E2 and the
  F-chain run sequentially in their tracks). D2b after D2a.
- **Reception SSOT rule**: §Intake sections and Axis 0 REFERENCE the
  reception criteria (`loom-pipeline/hooks/family-reception.md` /
  "the loom family reception's on-ramp table") — no copying of the table
  body into any SKILL.md (drift prevention; the one-SSOT decision is in the
  brief's Decision section).
- **No @req tags** anywhere (living-spec namespace gate — rule 11 is now
  namespace-guarded, but this plan binds no registered REQ-ids).
- Marketplace.json: carries no per-plugin version field (verified PR #483
  era) — untouched unless a description changes (none planned).
