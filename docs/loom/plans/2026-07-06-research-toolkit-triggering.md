# Plan: research-toolkit triggering improvements

Source brief: docs/loom/specs/2026-07-06-research-toolkit-triggering.md
Total tasks: 9
Critical-path depth: 4 (T1 → T6 → T7 → T9)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-06, round 2 — round-1 gaps fixed: T7/T9 Module single-scope, T9 verification-phase exemption declared, T1 Independent)

## Task 1 — add static description-standard test (RED)
- Description: Write `research-toolkit/scripts/test_research_toolkit_descriptions.py`
  (stdlib + pytest, unique module name to avoid cross-skill pytest collision):
  parse every `research-toolkit/skills/*/SKILL.md` frontmatter and assert
  (a) a `using-research-toolkit` skill exists with valid name+description
  frontmatter; (b) every description is non-empty, ≤250 chars, no XML tags;
  (c) `deep-deep-research`'s description contains ≥1 differentiation marker
  from {inspectable, editable, tunable, portable} (repositioning vs the
  built-in). Test must currently FAIL on (a) and (c).
- Module: research-toolkit/scripts
- Files touched: research-toolkit/scripts/test_research_toolkit_descriptions.py
- Context paths:
  - research-toolkit/skills/ (current four SKILL.md frontmatters)
  - skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py (house precedent for shape)
- Acceptance:
  - RED: `pytest research-toolkit/scripts/test_research_toolkit_descriptions.py` fails on router-existence + differentiation-marker assertions
  - GREEN (deferred to T6/T4): same command passes once router + rewrites land
  - Command surface: runnable via plain `pytest <path>` from repo root (flat import, no package install); no new command verb added
- External surfaces: pytest (repo's existing test runner); PyYAML NOT used — frontmatter parsed by line-split (house precedent)
- Dependencies: none
- Independent: true
- Brief item covered: "Behavioral A/B evidence" precondition + "Four rewritten description fields per the house standard" (static floor of Smallest End State items 1-2)

## Task 2 — rewrite cite-check description
- Description: Replace the description block in
  `research-toolkit/skills/cite-check/SKILL.md` per house standard: what+when,
  positive triggers front-loaded, ONE representative CJK trigger (e.g.
  「查證這份文件的引用」), keep the key-free clause short, ≤250 chars. Body untouched.
- Module: research-toolkit/skills/cite-check
- Files touched: research-toolkit/skills/cite-check/SKILL.md
- Context paths:
  - docs/skill-mining/2026-06-19-skill-description-standard.md
  - docs/loom/specs/2026-07-06-research-toolkit-triggering.md
- Acceptance:
  - RED (diagnostic): current description has no CJK trigger — `grep -c '查證\|引用' research-toolkit/skills/cite-check/SKILL.md` returns 0 within frontmatter
  - GREEN: rewritten description ≤250 chars, contains one CJK trigger, T1 test's length/format assertions pass for this file
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Four rewritten `description` fields per the house standard"

## Task 3 — rewrite deep-read description
- Description: Same recipe for `research-toolkit/skills/deep-read/SKILL.md`:
  one representative CJK trigger (e.g. 「精讀這本/這篇」), keep the
  depth-on-one vs breadth positive redirect to deep-deep-research (fix the
  stale `deep-research` name in the description's contrast clause), ≤250 chars.
- Module: research-toolkit/skills/deep-read
- Files touched: research-toolkit/skills/deep-read/SKILL.md
- Context paths:
  - docs/skill-mining/2026-06-19-skill-description-standard.md
- Acceptance:
  - RED (diagnostic): frontmatter description currently contrasts against the stale name (`deep-research's breadth`) and has no CJK trigger
  - GREEN: rewritten ≤250 chars, one CJK trigger, redirect names `deep-deep-research`, T1 length/format assertions pass
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Four rewritten `description` fields per the house standard" + Obsolete "stale deep-research name residue"

## Task 4 — rewrite + reposition deep-deep-research description
- Description: Rewrite `research-toolkit/skills/deep-deep-research/SKILL.md`
  description with positive specificity vs the built-in `deep-research`:
  lead with what only this version offers (inspectable/editable pipeline,
  host-portable incl. Codex, key-free), one CJK trigger, ≤250 chars.
- Module: research-toolkit/skills/deep-deep-research
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md (body lines 8-60: executor model, portability)
  - docs/skill-mining/2026-06-19-skill-description-standard.md
- Acceptance:
  - RED: T1 test's differentiation-marker assertion fails against the current description
  - GREEN: that assertion passes; description ≤250 chars with one CJK trigger
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "deep-deep-research repositioned by positive specificity"

## Task 5 — rewrite fact-check description
- Description: Tighten `research-toolkit/skills/fact-check/SKILL.md`
  description per standard; KEEP the existing representative CJK trigger
  「這個說法對嗎」 (do not add more — house 51-probe A/B), keep the positive
  redirect "Full report → deep-deep-research", ≤250 chars.
- Module: research-toolkit/skills/fact-check
- Files touched: research-toolkit/skills/fact-check/SKILL.md
- Context paths:
  - docs/skill-mining/2026-06-19-skill-description-standard.md
- Acceptance:
  - RED (diagnostic): current description length vs cap unverified — measure; if already compliant, GREEN is a no-regression re-issue keeping trigger + redirect
  - GREEN: ≤250 chars, exactly one CJK trigger, redirect intact, T1 assertions pass
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Four rewritten `description` fields per the house standard"

## Task 6 — author using-research-toolkit router skill
- Description: Create `research-toolkit/skills/using-research-toolkit/SKILL.md`
  (systems-thinking bucketed style, ≤110 lines): frontmatter description =
  family entry (research 意圖 → route), body = one intent-bucket table
  (查證一個說法→fact-check; 審引用→cite-check; 精讀單一文件→deep-read;
  多來源深研究報告→deep-deep-research), a negative guard (trivial lookup /
  stable knowledge → answer directly, no skill), and a boundary note on the
  host built-in `deep-research` (generic CC deep-research ask may route
  there; this family's value = inspectable/portable/sibling verbs). Flat
  folder (no subdirs) to satisfy validate-skill-folder-structure hook.
- Module: research-toolkit/skills/using-research-toolkit
- Files touched: research-toolkit/skills/using-research-toolkit/SKILL.md
- Context paths:
  - systems-thinking-toolkit/skills/using-systems-thinking-toolkit/SKILL.md (pattern)
  - research-toolkit/skills/*/SKILL.md (member frontmatters)
  - docs/loom/specs/2026-07-06-research-toolkit-triggering.md
- Acceptance:
  - RED: T1 test's router-existence assertion currently fails
  - GREEN: `pytest research-toolkit/scripts/test_research_toolkit_descriptions.py` fully passes (with T2-T5 landed)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "One new skill using-research-toolkit — family entry router"

## Task 7 — metadata ripple (version + description sync + stale names)
- Description: Bump version 0.2.1 → 0.3.0 in BOTH
  `research-toolkit/.claude-plugin/plugin.json` and
  `research-toolkit/.codex-plugin/plugin.json`; update the plugin
  description to name the router (byte-identical mirror into
  `.claude-plugin/marketplace.json` same commit); fix stale `deep-research`
  → `deep-deep-research` in codex `interface.longDescription` and in both
  `keywords` arrays.
- Module: research-toolkit plugin manifests
- Files touched: research-toolkit/.claude-plugin/plugin.json, research-toolkit/.codex-plugin/plugin.json, .claude-plugin/marketplace.json
- Context paths:
  - scripts/check-marketplace-description-sync.py
  - scripts/check-plugin-description-skill-coherence.py
- Acceptance:
  - RED: after editing plugin.json first, `python scripts/check-marketplace-description-sync.py` fails until marketplace.json mirrors
  - GREEN: both check scripts exit 0; `grep -rn 'deep-research' research-toolkit/.c*-plugin/ | grep -v deep-deep-research` returns nothing
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: "Metadata ripple: … version 0.2.1 → 0.3.0" + Obsolete stale-name residue

## Task 8 — author research-ask firing corpus
- Description: Write `docs/loom/firing-corpus/research-asks.jsonl` —
  ~16 records {query, expected, notes}: 3-4 per member skill in mixed
  中/日/英 natural phrasings (description-derived intents, ≥15 chars,
  self-contained), 2 router-level ambiguous research asks
  (expected `research-toolkit:using-research-toolkit`), and 3 near-miss
  records expected NONE (trivial lookup, stable-knowledge question, coding
  ask). Validate with the harness's corpus parser.
- Module: docs/loom/firing-corpus
- Files touched: docs/loom/firing-corpus/research-asks.jsonl
- Context paths:
  - docs/loom/firing-corpus/direct-ask.jsonl (format precedent)
  - loom-code/scripts/loom_firing_harness.py (parse_corpus contract: content not path; traps #2/#5)
- Acceptance:
  - RED: file absent; `parse_corpus` has nothing to parse
  - GREEN: `python -c "…parse_corpus(open('docs/loom/firing-corpus/research-asks.jsonl').read())"` returns 16 records, 0 validate warnings
- Dependencies: none
- Independent: true
- Brief item covered: "Behavioral A/B evidence: firing corpus (research asks, 中/日/英 + near-miss NONE records)"

## Task 9 — run A/B firing test + evidence doc
- Description: Following docs/loom/memory/headless-branch-plugin-testing-recipe.md
  (wrapper scripts per arm with `--plugin-dir`, neutral empty cwd, probe
  before corpus) and harness docstring traps #1-#6: Arm A = main via git
  worktree, Arm B = this branch; drive `run_corpus(claude_bin=<wrapper>)`
  with `--model sonnet`, max_turns ≥4; custom research-family grader in the
  driver (EXACT / FAMILY(research-toolkit:*) / OVER on expected=NONE).
  Write `docs/loom/dogfood/2026-07-06-research-toolkit-firing-ab.md` with
  per-criterion table + verdict. The driver script and raw outputs are
  session-local tooling (reuse /private/tmp/loom-firing-ab/driver.py shape),
  not tracked modules.
  VERIFICATION-PHASE EXEMPTION: this task is the branch's
  verification-before-completion behavioral check, executed by the
  orchestrator (multi-phase evaluation run) — explicitly EXEMPT from SDD's
  per-task ≤5-min implementer triad; SDD must NOT dispatch it as a normal
  implementer task.
- Module: docs/loom/dogfood
- Files touched: docs/loom/dogfood/2026-07-06-research-toolkit-firing-ab.md
- Context paths:
  - docs/loom/dogfood/2026-07-06-router-card-firing-ab.md (report format precedent)
  - docs/loom/memory/headless-branch-plugin-testing-recipe.md
  - loom-code/scripts/loom_firing_harness.py
- Acceptance:
  - RED: no evidence doc; goal's "clear improvement" unverified
  - GREEN: evidence doc exists with A vs B table over the 16-record corpus; B ≥ A overall AND B fires research-toolkit on ≥3 records where A missed AND zero new over-fires on expected=NONE; contaminated records surfaced not swallowed
- External surfaces: live `claude` CLI headless runs (subprocess; the harness's documented seam)
- Dependencies: Tasks 2, 3, 4, 5, 6, 7, 8 complete first
- Independent: false
- Brief item covered: "Behavioral A/B evidence … Clear improvement = B fires research-toolkit on records A misses, with zero new over-fires"

## Notes
- Tasks 2-6 form one parallel wave after Task 1 (disjoint files, no shared
  symbol; cross-references use stable skill names only).
- Version-bump commit subject convention: `feat(research-toolkit): … (0.3.0)`.
- The A/B run (Task 9) doubles as the branch's verification-before-completion
  behavioral check; package-level pytest still runs at review time.
