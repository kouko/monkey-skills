# Plan: mid-task ask layered defense (L1-lite + L2 hook + L3 valve)

Source brief: docs/loom/specs/2026-07-13-mid-task-ask-layered-defense.md
Total tasks: 5   ← uncapped
Critical-path depth: 2 (≤5)   ← longest Dependencies chain; this is the ceiling
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-14, 14/14 checks, general-purpose evaluator)

## Task 1 — L2 ask-triage hook (hooks.json entry + script + pytest)

- Description: Add a PreToolUse entry to loom-code/hooks/hooks.json with `"matcher": "AskUserQuestion"` (same shape as the existing git-guard entry at hooks.json:15-25) invoking a NEW `loom-code/hooks/ask-triage.py`. The script reads stdin (hook input JSON, content unused), and emits `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "<CARD>"}}` — `hookEventName` is MANDATORY (repo gotcha: missing it silently disables the hook and spams validation errors). CARD is the pinned text in this plan's ## Notes §Pinned card text — transcribe VERBATIM (domain-neutral wording + confirmation clearance line are load-bearing per brief). TDD: write loom-code/scripts/test_ask_triage_hook.py FIRST (test file must live under loom-code/scripts/ — CI's pytest collects `loom-code/scripts/ scripts/ .claude/hooks/`, NOT loom-code/hooks/). Tests: (a) script runs and emits valid JSON on stdin input; (b) `hookSpecificOutput.hookEventName == "PreToolUse"`; (c) additionalContext contains the three triage arms AND the clearance sentence (assert on distinctive stable fragments, not full-string equality); (d) hooks.json parses and contains an AskUserQuestion matcher entry.
- Module: loom-code/hooks (script + registration; test file in loom-code/scripts per CI collection constraint)
- Files touched: loom-code/hooks/hooks.json, loom-code/hooks/ask-triage.py, loom-code/scripts/test_ask_triage_hook.py
- Context paths:
  - loom-code/hooks/hooks.json
  - loom-code/hooks/git-guard.py
  - docs/loom/specs/2026-07-13-mid-task-ask-layered-defense.md
- Acceptance:
  - RED: `python3 -m pytest loom-code/scripts/test_ask_triage_hook.py -q` fails (file absent / script absent)
  - GREEN: that pytest passes; `python3 -c "import json;json.load(open('loom-code/hooks/hooks.json'))"` exits 0; full suite still green
- External surfaces: <Claude Code hooks API — PreToolUse matcher + hookSpecificOutput.additionalContext shape; grounded against the working git-guard + session-start entries in the same file, not docs recall>
- Dependencies: none
- Independent: true
- Brief item covered: "L2 — ask-moment hook … MUST include hookEventName … Card = the three-way triage … Scope-leak patch … domain-NEUTRAL" (brief §Smallest End State item 1)

## Task 2 — L1-lite kickoff fork harvest (kickoff-briefing + SKILL.md scope line)

- Description: In loom-code/skills/writing-plans/references/kickoff-briefing.md, extend §b (Collection step, currently "sweep every task in the plan for one-way-door engineering decisions … expect 1-3 hits") to ALSO sweep foreseeable implementation forks (unpinned library/pattern/format choices an implementer would otherwise hit mid-task); classify each found fork per the triage (pointer to SDD §Asking the user gate ① — point, don't copy); run Axis-4-lite research ONLY over researchable forks actually found (pay-per-hit; a zero-fork plan pays nothing; "Axis-4-lite" = the §c-batched form of brainstorming's Axis-4 protocol — cite it, don't restate it); resolved forks land in the plan's existing `## Notes` section as lines with the EXACT pinned format `Kickoff decision: <fork> → <resolution>` (define the line format here; it is the grep key). Fold everything into §c's ONE batched briefing (unchanged). Then in loom-code/skills/writing-plans/SKILL.md §Kickoff briefing (~line 119-121), update the scope wording from "one-way-door decisions" to "one-way-door decisions + foreseeable implementation forks" (≤10 words net growth; SKILL.md at 4,086/4,500 has +414 headroom).
- Module: loom-code/skills/writing-plans
- Files touched: loom-code/skills/writing-plans/references/kickoff-briefing.md, loom-code/skills/writing-plans/SKILL.md
- Context paths:
  - loom-code/skills/writing-plans/references/kickoff-briefing.md
  - loom-code/skills/writing-plans/SKILL.md
  - docs/loom/specs/2026-07-13-mid-task-ask-layered-defense.md
- Acceptance:
  - RED: `grep -c 'Kickoff decision:' loom-code/skills/writing-plans/references/kickoff-briefing.md` returns 0
  - GREEN: kickoff-briefing.md defines the sweep extension + pinned line format + pay-per-hit rule; SKILL.md §Kickoff briefing mentions foreseeable forks; `wc -w` of SKILL.md ≤ 4,500
- External surfaces: (omit — internal skill content)
- Dependencies: none
- Independent: true
- Brief item covered: "L1 — kickoff fork harvest (lite) … pay-per-hit … `Kickoff decision: <fork> → <resolution>` lines … NO plan-format.md schema change" (brief §Smallest End State item 2)

## Task 3 — Triage SSOT + propagation + relay lines in SDD SKILL.md

- Description: Three surgical edits to loom-code/skills/subagent-driven-development/SKILL.md (4,033/4,500, +467 headroom; total net growth budget for this task ≤120 words): (1) §Asking the user gate ① — extend the existing "Genuine taste / scope / un-inferable intent → ask" bullet into the NAMED three-way triage (the SSOT): fact checkable within the task's own sources → look it up, never ask; user-fact / preference / irreversible confirmation → ask directly; researchable design fork → research first (gate ② already owns the research protocol pointer), transcribing the arm wording VERBATIM from this plan's ## Notes §Pinned triage arms so the L2 card (Task 1) and this SSOT never diverge. (2) Step 1 dispatch instruction — one sentence: relevant `Kickoff decision:` lines from the plan's `## Notes` ride the implementer's task packet (the propagation patch). (3) Step 2 NEEDS_CONTEXT relay — one sentence: classify the relayed question per gate ①'s triage before phrasing; researchable → research first per gate ②.
- Module: loom-code/skills/subagent-driven-development
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md
- Context paths:
  - loom-code/skills/subagent-driven-development/SKILL.md
  - docs/loom/specs/2026-07-13-mid-task-ask-layered-defense.md
- Acceptance:
  - RED: `grep -c 'Kickoff decision:' loom-code/skills/subagent-driven-development/SKILL.md` returns 0
  - GREEN: gate ① names the three arms; step 1 carries the propagation sentence; step 2 carries the relay-triage sentence; `wc -w` ≤ 4,500
- External surfaces: (omit — internal skill content)
- Dependencies: none
- Independent: true
- Brief item covered: "Triage SSOT lives in SDD §Asking gate ① … Propagation patch … SDD step 2 relay gains one sentence" (brief §Smallest End State items 2-3 + SSOT paragraph)

## Task 4 — L3 valve legitimacy in implementer.md

- Description: Two edits to loom-code/agents/implementer.md (uncapped agent file): (1) at the NEEDS_CONTEXT status definition (~line 356), add the legitimacy clause: "Returning NEEDS_CONTEXT is always better than guessing — it is a correct outcome, not a failure. Use it freely when the trigger conditions hold." (mirrors DONE_WITH_CONCERNS's existing "use this freely" at ~line 348, closing the asymmetry). (2) In the same block, one pointer sentence: the orchestrator triages your question (task-scoped fact / user-fact / researchable fork) per SDD §Asking the user — so state which kind you believe it is when you can. Do NOT copy the triage arms into this file (point, don't copy).
- Module: loom-code/agents (implementer contract)
- Files touched: loom-code/agents/implementer.md
- Context paths:
  - loom-code/agents/implementer.md
  - docs/loom/specs/2026-07-13-mid-task-ask-layered-defense.md
- Acceptance:
  - RED: `grep -c 'better than guessing' loom-code/agents/implementer.md` returns 0
  - GREEN: legitimacy clause + triage pointer present at the NEEDS_CONTEXT definition; no triage-arm copy (grep for 'researchable design fork →' returns 0 in this file)
- External surfaces: (omit — internal agent contract)
- Dependencies: none
- Independent: true
- Brief item covered: "L3 — valve legitimacy: implementer.md NEEDS_CONTEXT definition gains the legitimacy clause … + the triage vocabulary [as pointer]" (brief §Smallest End State item 3)

## Task 5 — Version bump 0.30.0 + CHANGELOG + codex manifest sync

- Description: Bump loom-code/.claude-plugin/plugin.json 0.29.1 → 0.30.0 (new hook = feature); run `python3 scripts/sync_codex_manifests.py loom-code`; add CHANGELOG 0.30.0 entry (dated 2026-07-14) covering the three layers + the two counter-review patches + the complexity-critique RESHAPE provenance, hooks noted as Claude-Code-only (git-guard precedent).
- Module: loom-code (plugin metadata)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Context paths:
  - loom-code/CHANGELOG.md
  - loom-code/.claude-plugin/plugin.json
- Acceptance:
  - RED: `python3 -c "import json;v=json.load(open('loom-code/.claude-plugin/plugin.json'))['version'];exit(0 if v=='0.30.0' else 1)"` exits 1
  - GREEN: 0.30.0 in both manifests; `python3 scripts/sync_codex_manifests.py --check loom-code` exit 0; CHANGELOG entry present
- External surfaces: (omit — repo-internal metadata)
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Brief item covered: "Version: loom-code 0.29.1 → 0.30.0 (new hook = feature) + CHANGELOG + codex manifest sync" (brief §Smallest End State)

## Notes

- Kickoff decision: test import mechanism for the hyphenated `ask-triage.py` (not importable as a module) → the pytest invokes the script via subprocess (`echo '<input-json>' | python3 loom-code/hooks/ask-triage.py`), asserting on stdout JSON — no import, no filename rename. (Kickoff sweep 2026-07-14: 0 one-way-door hits; this was the sole foreseeable implementation fork, repo-checkable, resolved without a user ask per triage arm 1.)
- No loom-spec change-folder bound (layer ii: 0 non-archived docs/loom/<change-id>/ folders) — brief-only input; coverage script N/A.
- Tasks 1-4 are disjoint-file → one parallel wave; Task 5 joins (depth 2).
- Prose-content tasks (2-4) use grep/wc acceptance probes per the docs
  exemption; Task 1 is real TDD (pytest RED→GREEN in the CI-collected path).
- §Pinned card text (Task 1 transcribes VERBATIM as additionalContext):
  "Before asking: triage this question. (1) A fact checkable within the
  task's own sources (files, config, docs in scope) → look it up instead of
  asking. (2) A user-only fact, a preference, or a confirmation of an
  irreversible/outward-facing action → ask directly; this card is never a
  reason to avoid or delay such asks. (3) A design/approach fork that
  industry practice could inform → research first (loom-code: SDD §Asking
  the user, gate ②), then ask WITH a cited recommendation. Questions
  arriving with options + a recommendation respect the user's time;
  unresearched forks outsource your work to them."
- §Pinned triage arms (Task 3 transcribes the three arm phrases verbatim):
  "fact checkable within the task's own sources → look it up, never ask" /
  "user-fact, preference, or irreversible/outward-facing confirmation → ask
  directly, freely" / "researchable design fork → research first, then ask
  with a cited recommendation".
- Task 1's card and Task 3's SSOT share wording via the pins above — the
  two-copy limit (SSOT + operative card restatement) is by design; Tasks 2
  and 4 point, never copy.
- Dogfood gate (post-wave, pre-finishing): weak-model cold-read of the card
  — scenario A (confirmation ask: "merge now?") must pass through untouched;
  scenario B (unresearched design fork: "which retry backoff?") must
  research-first. Runs after Task 5, before finishing-a-development-branch.
