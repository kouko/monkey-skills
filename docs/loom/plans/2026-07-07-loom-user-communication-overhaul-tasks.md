# Plan: loom user-communication overhaul

Source brief: docs/loom/plans/2026-07-07-loom-user-communication-overhaul.md
Total tasks: 21
Critical-path depth: 5 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-07, 14/14 applicable checks)

Shared external-surface facts (referenced by tasks below):
- Claude Code hook stdin JSON: every event carries `transcript_path`,
  `cwd`, `hook_event_name`; Stop events add `stop_hook_active` (true when
  a previous Stop-hook block already re-ran Claude — MUST exit 0 then, or
  we loop). PostToolUse adds `tool_name` / `tool_input` / `tool_response`.
- Context injection: emit `{"hookSpecificOutput": {"hookEventName":
  "<Event>", "additionalContext": "..."}}` — `hookEventName` is MANDATORY
  (memory: hook-specific-output-requires-hookeventname; omitting it
  silently disables the hook).
- Stop-hook block: emit `{"decision": "block", "reason": "..."}` top-level.
- Transcript = JSONL; user/assistant turns have `type`, `message.content`
  (string or content-block array), `isSidechain` (exclude true).
- Worked example for stdin parsing + fail-open: loom-code/hooks/git-guard.py:350-365.
- All hooks fail-open: malformed input / missing file / any exception → exit 0, no output.

## Task 1 — language-detection helper `lang_detect.py`
- Description: Create pure-python helper: `detect_script(text) -> 'ja'|'zh'|'en'|None`
  (kana chars → ja; Han without kana → zh; mostly-ASCII letters → en; too
  short / mixed-noise → None) and `conversation_language(transcript_path,
  n_turns=3) -> 'ja'|'zh'|'en'|None` reading the LAST n user main-chain
  turns (skip `isSidechain: true`, skip tool-result/command messages,
  strip code fences/inline code/URLs/file paths before counting; return a
  language only when the majority of sampled turns agree, else None).
  No hardcoded target language anywhere.
- Module: loom-pipeline/hooks/lang_detect.py
- Files touched: loom-pipeline/hooks/lang_detect.py, loom-pipeline/scripts/test_lang_detect.py
- Context paths:
  - loom-code/hooks/git-guard.py (fail-open + stdin patterns)
  - loom-code/scripts/test_git_guard.py (how tests import a hooks/ module by path)
- Acceptance:
  - RED: loom-pipeline/scripts/test_lang_detect.py::test_detect_and_conversation_language fails (module absent)
  - GREEN: ja/zh/en/None cases pass incl. code-fence stripping, sidechain exclusion, majority rule, and a mixed CJK-with-English-terms zh case
- External surfaces: Claude Code transcript JSONL shape (see header facts)
- Dependencies: none
- Independent: true
- Brief item covered: "Shared detection helper: infer conversation language … Pure code, no model judgment" (Smallest end state 1a)

## Task 2 — tail language anchor hook (PostToolUse on Skill)
- Description: Create `loom-pipeline/hooks/language-anchor.py`: on
  PostToolUse for tool_name `Skill`, resolve conversation language via
  lang_detect; if 'ja' or 'zh', emit additionalContext with ONE line
  written IN that language directing user-facing narration to stay in it
  (e.g. zh: 「對使用者的敘述一律使用繁體中文（機器面 artifact 不變）」;
  ja equivalent); if 'en'/None → no output (exit 0). Register in
  loom-pipeline/hooks/hooks.json under PostToolUse matcher "Skill".
  The zh/ja literals are emitted DIRECTIVE TEXT for a detected language,
  not behavior selectors (brief Non-goals: no hardcoded output language).
- Module: loom-pipeline/hooks/language-anchor.py
- Files touched: loom-pipeline/hooks/language-anchor.py, loom-pipeline/hooks/hooks.json, loom-pipeline/scripts/test_language_anchor.py
- Context paths:
  - loom-pipeline/hooks/lang_detect.py
  - loom-pipeline/hooks/hooks.json (existing SessionStart entry — extend, don't replace)
- Acceptance:
  - RED: test_language_anchor.py::test_anchor_emits_in_detected_language fails (hook absent)
  - GREEN: zh transcript → zh anchor with hookEventName present; ja → ja anchor; en/None/malformed → empty exit 0; hooks.json valid JSON containing both SessionStart and the new PostToolUse entry
- External surfaces: hookSpecificOutput contract (header facts)
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Tail anchor: hook injects a one-line directive in (and naming) the detected language after large English context loads" (Smallest end state 1b)

## Task 3 — Stop-hook language-consistency validator
- Description: Create `loom-pipeline/hooks/language-stop-check.py` (Stop
  event): exit 0 immediately when `stop_hook_active` is true. Else read
  transcript tail: expected = conversation_language(); reply = final
  assistant message text (concatenate text blocks; strip code fences,
  inline code, URLs, paths, table pipes). Block ONLY when expected ∈
  {ja, zh} AND visible reply length ≥ 200 chars AND target-script char
  ratio < 0.15 — emit decision:block with the corrective reason written
  in the expected language. Never block when expected is en/None.
  Register in hooks.json under Stop.
- Module: loom-pipeline/hooks/language-stop-check.py
- Files touched: loom-pipeline/hooks/language-stop-check.py, loom-pipeline/hooks/hooks.json, loom-pipeline/scripts/test_language_stop_check.py
- Context paths:
  - loom-pipeline/hooks/lang_detect.py
- Acceptance:
  - RED: test_language_stop_check.py::test_blocks_english_reply_in_cjk_session fails (hook absent)
  - GREEN: full-English reply in zh session → block (reason in zh); zh reply with English technical terms + code blocks → pass; en session → never blocks; stop_hook_active → exit 0; short replies → pass; malformed stdin → exit 0
- External surfaces: Stop-hook decision/block + stop_hook_active loop guard (header facts)
- Dependencies: Tasks 1, 2 complete first (Task 2 serializes hooks.json edits)
- Independent: false
- Brief item covered: "Stop-hook validator: detected conversation language vs reply body … mismatch → block with corrective reminder" (Smallest end state 1c)

## Task 4 — family relay-discipline SSOT section + mechanical test file
- Description: Append a `## Family relay discipline` section to
  loom-pipeline/hooks/family-reception.md (the existing family SSOT all
  routers point to) containing: (a) the user-rollup card template —
  mandatory slots with fixed SEMANTICS, language-neutral slot definitions
  (task restated / current state / what changed / impact on you / next +
  decision), content always in the live conversation language; (b) visual
  defaults — ≥2 options at a fork → markdown comparison table; flow/state
  shape → ascii-graph-toolkit (CJK width-aware); Mermaid only where the
  channel renders it (terminal degrades to table/ASCII); (c) turn-ordering
  rule — a briefing ENDS the turn or precedes the ask inline; never bury a
  briefing and an AskUserQuestion dialog in the same turn-final position;
  (d) translate-jargon + stakes-first one-liners POINTING to (not copying)
  the existing loom-code ③-gate rules. Also create
  loom-pipeline/scripts/test_family_relay.py with assertion functions:
  test_relay_section (this task), test_sdd_pointer, test_review_pointer,
  test_brainstorming_visuals, test_design_side_pointers (parametrized over
  the three routers, ids: spec / interface-design / product-principles),
  test_brief_before_asking_ordering (those stay RED until Tasks 5-11).
- Module: loom-pipeline/hooks/family-relay.md (see Notes: post-PASS amendment 2)
- Files touched: loom-pipeline/hooks/family-relay.md, loom-pipeline/hooks/family-reception.md, loom-pipeline/scripts/test_family_relay.py
- Context paths:
  - loom-code/skills/requesting-code-review/SKILL.md (③ rules to point at, lines 34-56)
  - docs/loom/plans/2026-07-07-loom-user-communication-overhaul.md (§Smallest end state 2-3)
- Acceptance:
  - RED: test_family_relay.py::test_relay_section fails (section absent)
  - GREEN: test_relay_section passes (section present with card slots, visual defaults, turn-ordering rule; no copied ③ rule bodies — pointer phrasing asserted)
- External surfaces: none (markdown + tests)
- Dependencies: none
- Independent: true
- Brief item covered: "extract the relay discipline … into ONE shared reference" + "User-rollup card … mandatory template slots" (Smallest end state 2, 3)

## Task 5 — SDD narration seams adopt the rollup card
- Description: Edit loom-code/skills/subagent-driven-development/SKILL.md:
  in `## Asking the user` ③ (lines ~43-61) and `## Status handling`
  (~160), add the requirement that per-wave status reports and checkpoint
  sign-offs are delivered as the family rollup card (pointer to
  family-relay.md §Family relay discipline — no copied template body),
  in the conversation language; internal traffic (verdicts, wave labels)
  stays machine-precise below the card.
- Module: loom-code/skills/subagent-driven-development/SKILL.md
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md
- Context paths:
  - loom-pipeline/hooks/family-relay.md (§Family relay discipline)
  - loom-pipeline/scripts/test_family_relay.py
- Acceptance:
  - RED: test_family_relay.py::test_sdd_pointer fails before edit
  - GREEN: test_sdd_pointer passes (pointer line present in both seams; no template-body copy)
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "User-rollup card at the narration seams (SDD per-wave report, checkpoint sign-offs …)" (Smallest end state 2)

## Task 6 — review relay seam adopts card + option table
- Description: Edit loom-code/skills/requesting-code-review/SKILL.md ③
  (lines ~34-56): relay of a review verdict to the user is a rollup card
  (pointer to family SSOT), findings walked at the user's pace; when the
  user must choose among ≥2 remediation options, a markdown comparison
  table is the default.
- Module: loom-code/skills/requesting-code-review/SKILL.md
- Files touched: loom-code/skills/requesting-code-review/SKILL.md
- Context paths:
  - loom-pipeline/hooks/family-relay.md (§Family relay discipline)
  - loom-pipeline/scripts/test_family_relay.py
- Acceptance:
  - RED: test_family_relay.py::test_review_pointer fails before edit
  - GREEN: test_review_pointer passes
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "review relay" seam + "≥2 options → markdown comparison table" (Smallest end state 2)

## Task 7 — brainstorming visual catalog gets channel-aware degradation
- Description: Edit loom-code/skills/brainstorming/references/visual-companion.md
  (Mermaid-only catalog: add a channel table — terminal/PR-text → markdown
  table or ascii-graph-toolkit with CJK-width oracle; Mermaid/Excalidraw
  only where rendered; labels in the conversation language) and
  references/handoff-brief-format.md `## Diagrams` (same degradation note);
  add one pointer line in SKILL.md near line 181 (plain-language summary
  rule) to the family relay section.
- Module: loom-code/skills/brainstorming/ (one skill dir)
- Files touched: loom-code/skills/brainstorming/references/visual-companion.md, loom-code/skills/brainstorming/references/handoff-brief-format.md, loom-code/skills/brainstorming/SKILL.md
- Context paths:
  - loom-pipeline/hooks/family-relay.md (§Family relay discipline)
  - loom-pipeline/scripts/test_family_relay.py
- Acceptance:
  - RED: test_family_relay.py::test_brainstorming_visuals fails before edit
  - GREEN: test_brainstorming_visuals passes (degradation table present; ascii-graph-toolkit named; conversation-language label rule present; SKILL.md pointer present)
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "replace the Mermaid-only catalog with channel-aware degradation (terminal → table/ASCII)" (Smallest end state 2)

## Task 8 — relay pointer in using-loom-spec §Intake
- Description: Add one pointer line to loom-spec/skills/using-loom-spec/SKILL.md
  `## §Intake` (~line 20): all user-facing narration follows
  family-relay.md §Family relay discipline (pointer, never copy).
- Module: loom-spec/skills/using-loom-spec/SKILL.md
- Files touched: loom-spec/skills/using-loom-spec/SKILL.md
- Context paths:
  - loom-pipeline/hooks/family-relay.md (§Family relay discipline)
  - loom-pipeline/scripts/test_family_relay.py
- Acceptance:
  - RED: test_family_relay.py::test_design_side_pointers[spec] fails before edit
  - GREEN: test_design_side_pointers[spec] passes
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "loom-spec / loom-interface-design / loom-product-principles point to it" (Smallest end state 3)

## Task 9 — relay pointer in using-loom-interface-design §Intake
- Description: Same one-line pointer edit as Task 8, in
  loom-interface-design/skills/using-loom-interface-design/SKILL.md
  `## §Intake` (~line 12).
- Module: loom-interface-design/skills/using-loom-interface-design/SKILL.md
- Files touched: loom-interface-design/skills/using-loom-interface-design/SKILL.md
- Context paths:
  - loom-pipeline/hooks/family-relay.md (§Family relay discipline)
  - loom-pipeline/scripts/test_family_relay.py
- Acceptance:
  - RED: test_family_relay.py::test_design_side_pointers[interface-design] fails before edit
  - GREEN: test_design_side_pointers[interface-design] passes
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "loom-spec / loom-interface-design / loom-product-principles point to it" (Smallest end state 3)

## Task 10 — relay pointer in using-loom-product-principles §Intake
- Description: Same one-line pointer edit as Task 8, in
  loom-product-principles/skills/using-loom-product-principles/SKILL.md
  `## §Intake` (~line 16).
- Module: loom-product-principles/skills/using-loom-product-principles/SKILL.md
- Files touched: loom-product-principles/skills/using-loom-product-principles/SKILL.md
- Context paths:
  - loom-pipeline/hooks/family-relay.md (§Family relay discipline)
  - loom-pipeline/scripts/test_family_relay.py
- Acceptance:
  - RED: test_family_relay.py::test_design_side_pointers[product-principles] fails before edit
  - GREEN: test_design_side_pointers[product-principles] passes
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "loom-spec / loom-interface-design / loom-product-principles point to it" (Smallest end state 3)

## Task 11 — brief-before-asking: buried-briefing fix + anti-diagram rescope
- Description: Edit dev-workflow/skills/brief-before-asking/SKILL.md:
  (a) strengthen Mode A lines ~20-22 with the explicit turn-ordering rule
  (briefing lands as turn-final text OR the ask is inline text — never a
  full briefing + AskUserQuestion dialog stacked in one turn; cite the
  recurrence); (b) rescope anti-diagram wording at lines ~73 and ~185:
  keep "don't answer stakes-confusion with a diagram INSTEAD of plain
  words", add "an explicit user request for a visual is always honored;
  option comparisons default to a table".
- Module: dev-workflow/skills/brief-before-asking/SKILL.md
- Files touched: dev-workflow/skills/brief-before-asking/SKILL.md
- Context paths:
  - loom-pipeline/scripts/test_family_relay.py
- Acceptance:
  - RED: test_family_relay.py::test_brief_before_asking_ordering fails before edit
  - GREEN: test_brief_before_asking_ordering passes (turn-ordering rule present; blanket anti-diagram phrasing replaced; explicit-request carve-out present)
- External surfaces: none
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "Fold in the buried-briefing fix" + "anti-diagram wording" (Smallest end state 3, Non-goals)

## Task 12 — comms metrics recipe `comms_metrics.py`
- Description: Create loom-pipeline/scripts/comms_metrics.py: given
  transcript JSONL path(s), compute (a) wrong-language turn ratio
  (assistant main-chain turns whose script mismatches the rolling
  conversation language, via lang_detect), (b) visual-at-fork rate
  (AskUserQuestion tool_use turns with a markdown table / ascii diagram in
  the same or 2 preceding assistant turns), (c) confusion-signal count
  (user-turn regex set: 什麼意思/看不懂/？？/意義與影響/講簡單|白話/what do
  you mean — extensible list). CLI: `python3 comms_metrics.py <jsonl...>
  [--json]`. Ship 2-3 small synthetic fixtures under
  loom-pipeline/scripts/fixtures/.
- Module: loom-pipeline/scripts/comms_metrics.py
- Files touched: loom-pipeline/scripts/comms_metrics.py, loom-pipeline/scripts/test_comms_metrics.py, loom-pipeline/scripts/fixtures/ (new jsonl fixtures)
- Context paths:
  - loom-pipeline/hooks/lang_detect.py (reuse — import by path like test_git_guard.py does)
  - docs/loom/audits/2026-07-06-loom-comms-transcript-baseline.md (metric definitions §B4, §D)
- Acceptance:
  - RED: test_comms_metrics.py::test_three_metrics_on_fixtures fails (module absent)
  - GREEN: fixture with known planted signals yields exact expected counts/ratios for all three metrics; --json output parses
  - Runnable capability declared: invocation documented in the audit-recipe doc (Task 13) §How to rerun
- External surfaces: transcript JSONL shape; AskUserQuestion tool_use block shape (verify against a real transcript before asserting)
- Dependencies: Task 1 completes first (imports lang_detect)
- Independent: true
- Brief item covered: "repeatable audit … computing (a)(b)(c)" (Smallest end state 4)

## Task 13 — run recipe against baseline sessions + method doc
- Description: Run comms_metrics.py over the 11 baseline sessions listed
  in docs/loom/audits/2026-07-06-loom-comms-transcript-baseline.md; write
  docs/loom/audits/2026-07-07-comms-metrics-recipe.md: how to rerun (exact
  command), per-session + aggregate numbers, deviation notes vs the
  hand-mined baseline (they will not match exactly — explain each gap),
  and the post-ship target thresholds from the brief. Numbers are measured
  facts — recompute, never copy from the baseline doc.
- Module: docs/loom/audits/2026-07-07-comms-metrics-recipe.md
- Files touched: docs/loom/audits/2026-07-07-comms-metrics-recipe.md
- Context paths:
  - loom-pipeline/scripts/comms_metrics.py
  - docs/loom/audits/2026-07-06-loom-comms-transcript-baseline.md
- Acceptance:
  - RED: doc absent / script errors on ≥1 real session file
  - GREEN: doc exists with all three aggregate numbers, per-session table, rerun command verified by actually running it
- External surfaces: real transcripts under ~/.claude/projects/ (read-only)
- Dependencies: Task 12 completes first
- Independent: true
- Brief item covered: "Baseline = the 2026-07-06 audit doc" + brief Acceptance 4 (recipe reproduces baseline)

## Task 14 — release metadata: loom-pipeline 0.5.0→0.6.0
- Description: Bump version in loom-pipeline/.claude-plugin/plugin.json +
  loom-pipeline/.codex-plugin/plugin.json; add CHANGELOG.md entry (hooks:
  lang anchor + stop validator; relay SSOT section; comms metrics recipe)
  stamping the real test counts from the suite run (memory:
  stamp-changelog-test-counts-at-closeout).
- Module: loom-pipeline plugin metadata (three sibling files, formulaic)
- Files touched: loom-pipeline/.claude-plugin/plugin.json, loom-pipeline/.codex-plugin/plugin.json, loom-pipeline/CHANGELOG.md
- Context paths:
  - loom-pipeline/CHANGELOG.md (entry format)
- Acceptance:
  - RED: `grep -q '0.6.0' loom-pipeline/CHANGELOG.md` fails before edit
  - GREEN: both plugin.json report 0.6.0; CHANGELOG entry present with test counts from an actual `python3 -m pytest loom-pipeline/scripts/` run
- External surfaces: none
- Dependencies: Tasks 3, 5, 6, 7, 8, 9, 10, 11, 12 complete first
- Independent: true
- Brief item covered: repo release conventions for shipped Smallest end state 1-4 (loom-pipeline carrier)

## Task 15 — release metadata: loom-code 0.26.0→0.27.0
- Description: Same as Task 14 for loom-code (SDD/review/brainstorming
  relay seams + visual degradation), 0.26.0→0.27.0.
- Module: loom-code plugin metadata (three sibling files, formulaic)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Context paths:
  - loom-code/CHANGELOG.md (entry format)
- Acceptance:
  - RED: `grep -q '0.27.0' loom-code/CHANGELOG.md` fails before edit
  - GREEN: both plugin.json report 0.27.0; CHANGELOG entry present
- External surfaces: none
- Dependencies: Tasks 5, 6, 7 complete first
- Independent: true
- Brief item covered: repo release conventions (Smallest end state 2 carrier)

## Task 16 — release metadata: dev-workflow 2.20.1→2.21.0
- Description: Same as Task 14 for dev-workflow (brief-before-asking
  turn-ordering + anti-diagram rescope), 2.20.1→2.21.0.
- Module: dev-workflow plugin metadata (three sibling files, formulaic)
- Files touched: dev-workflow/.claude-plugin/plugin.json, dev-workflow/.codex-plugin/plugin.json, dev-workflow/CHANGELOG.md
- Context paths:
  - dev-workflow/CHANGELOG.md (entry format)
- Acceptance:
  - RED: `grep -q '2.21.0' dev-workflow/CHANGELOG.md` fails before edit
  - GREEN: both plugin.json report 2.21.0; CHANGELOG entry present
- External surfaces: none
- Dependencies: Task 11 completes first
- Independent: true
- Brief item covered: repo release conventions (Smallest end state 3 carrier)

## Task 17 — release metadata: loom-spec 0.4.1→0.4.2
- Description: Same as Task 14 for loom-spec (§Intake relay pointer),
  0.4.1→0.4.2.
- Module: loom-spec plugin metadata (three sibling files, formulaic)
- Files touched: loom-spec/.claude-plugin/plugin.json, loom-spec/.codex-plugin/plugin.json, loom-spec/CHANGELOG.md
- Context paths:
  - loom-spec/CHANGELOG.md (entry format)
- Acceptance:
  - RED: `grep -q '0.4.2' loom-spec/CHANGELOG.md` fails before edit
  - GREEN: both plugin.json report 0.4.2; CHANGELOG entry present
- External surfaces: none
- Dependencies: Task 8 completes first
- Independent: true
- Brief item covered: repo release conventions (Smallest end state 3 carrier)

## Task 18 — release metadata: loom-interface-design 0.4.1→0.4.2
- Description: Same as Task 14 for loom-interface-design (§Intake relay
  pointer), 0.4.1→0.4.2.
- Module: loom-interface-design plugin metadata (three sibling files, formulaic)
- Files touched: loom-interface-design/.claude-plugin/plugin.json, loom-interface-design/.codex-plugin/plugin.json, loom-interface-design/CHANGELOG.md
- Context paths:
  - loom-interface-design/CHANGELOG.md (entry format)
- Acceptance:
  - RED: `grep -q '0.4.2' loom-interface-design/CHANGELOG.md` fails before edit
  - GREEN: both plugin.json report 0.4.2; CHANGELOG entry present
- External surfaces: none
- Dependencies: Task 9 completes first
- Independent: true
- Brief item covered: repo release conventions (Smallest end state 3 carrier)

## Task 19 — release metadata: loom-product-principles 0.4.0→0.4.1
- Description: Same as Task 14 for loom-product-principles (§Intake relay
  pointer), 0.4.0→0.4.1.
- Module: loom-product-principles plugin metadata (three sibling files, formulaic)
- Files touched: loom-product-principles/.claude-plugin/plugin.json, loom-product-principles/.codex-plugin/plugin.json, loom-product-principles/CHANGELOG.md
- Context paths:
  - loom-product-principles/CHANGELOG.md (entry format)
- Acceptance:
  - RED: `grep -q '0.4.1' loom-product-principles/CHANGELOG.md` fails before edit
  - GREEN: both plugin.json report 0.4.1; CHANGELOG entry present
- External surfaces: none
- Dependencies: Task 10 completes first
- Independent: true
- Brief item covered: repo release conventions (Smallest end state 3 carrier)

## Task 20 — marketplace.json version sync
- Description: Update root .claude-plugin/marketplace.json entries for the
  six bumped plugins to match their plugin.json versions (memory:
  plugin-json-location-and-description-sync).
- Module: .claude-plugin/marketplace.json
- Files touched: .claude-plugin/marketplace.json
- Context paths:
  - .claude-plugin/marketplace.json
- Acceptance:
  - RED: version-consistency diagnostic fails before edit (marketplace version ≠ plugin.json version for ≥1 bumped plugin)
  - GREEN: one-shot python consistency check confirms marketplace.json agrees with both plugin.json files for all six plugins
- External surfaces: none
- Dependencies: Tasks 14, 15, 16, 17, 18, 19 complete first
- Independent: false
- Brief item covered: repo release conventions (marketplace sync memory) — mechanical completion of Tasks 14-19, each anchored to a Smallest-end-state carrier

## Task 21 — BACKLOG: close the loom-spec briefing-gate item
- Description: Mark the OPEN "loom-spec … lacks the brief-before-asking
  escalation for INTERACTIVE use" item (docs/loom/BACKLOG.md:65-73)
  resolved per the BACKLOG header's entry format, citing the family relay
  section + Task 8's pointer.
- Module: docs/loom/BACKLOG.md
- Files touched: docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/BACKLOG.md (header defines entry format)
- Acceptance:
  - RED: BACKLOG item still shows OPEN status before edit (grep diagnostic)
  - GREEN: item marked resolved with citation, format matching the BACKLOG header spec
- External surfaces: none
- Dependencies: Tasks 4, 8 complete first
- Independent: true
- Brief item covered: "Closes BACKLOG 'loom-spec briefing gate'" (Smallest end state 3)

## Notes

- Critical path (depth 5): Task 1 → 2 → 3 → 14 → 20.
- Parallel waves: wave 1 {T1, T4}; wave 2 {T2, T12, T5, T6, T7, T8, T9,
  T10, T11, T21 after both deps}; wave 3 {T3, T13, T15-T19 as deps
  clear}; final {T14 → T20}.
- Task 4's test file contains RED functions for Tasks 5-11 by design —
  per-task acceptance is the NAMED test function/param id, not
  whole-file green.
- No hardcoded output language anywhere (brief Non-goals) — reviewers
  should flag any zh/ja literal that SELECTS behavior; literals that are
  the emitted directive/reason text for a detected language are correct.
- Post-PASS amendments (2026-07-07, per reviewer notes; additive and
  schema-safe, re-review skipped): verdict field flipped to PASS; Task 13
  marked Independent: true (write set collides with nothing); Task 20
  traceability phrasing made self-contained. No task content, DAG, or
  acceptance changes.
- Post-PASS amendment 2 (2026-07-07, Task 4 execution finding): the relay
  section lives in NEW loom-pipeline/hooks/family-relay.md, with only a
  ≤2-line pointer in family-reception.md — the reception file has a
  test-pinned ≤60 non-empty-line budget
  (test_pipeline_reception.py::test_reception_content_contract; it is
  injected every SessionStart, so lines = standing token cost). Canonical
  pointer phrase for Tasks 5-11 becomes `family-relay.md §Family relay
  discipline`. Task 4's Files touched gains family-relay.md; downstream
  context paths updated in place. DAG/acceptance semantics unchanged.
