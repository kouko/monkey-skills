# Plan: requesting-code-review SKILL.md extraction pilot (E-1(b))

Source brief: docs/loom/specs/2026-08-05-rcr-skill-extraction-pilot.md
Total tasks: 3
Critical-path depth: 3 (T1 → T2 → T3)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-08-05, round 1, 15/15)

## Task 1 — the extraction (move-sets #1-#5 + pointer-pin pytest)

- Description: Execute the brief's FROZEN partition exactly (§The
  partition is the SSOT — transcribe move-sets #1-#5 from it, including
  every itemized inline residue and every MUST-NOT-MOVE exclusion).
  Create the five destination files under
  `loom-code/skills/requesting-code-review/references/`
  (`scope-comparison.md`, `cross-skill-map.md`,
  `push-trigger-rationalizations.md`, `red-flags.md`,
  `design-evidence.md` — the last opens with a header stating it is
  author-facing and not for runtime loading). Moved prose is VERBATIM
  (splice connectives only); each destination file opens with one line
  naming its source section and the skill it serves. Edit SKILL.md to
  remove the moved content and leave the itemized residue+pointer
  lines. Author the pointer-pin pytest (new file
  `loom-code/scripts/test_rcr_extraction_pointers.py`), RED-first,
  asserting whitespace-normalized: (a) the five pointer/residue lines
  present in SKILL.md; (b) the four moved section headings/table absent
  from SKILL.md and present in their destination files; (c) the Exit
  clause and "Evidence: G4 A/B" absent from SKILL.md, present in
  design-evidence.md; (d) the pinned survivors still inline ("G4
  measured why" fragment; "advisory only" rule sentence; the inherit-
  by-design rule); (e) `len(text.split()) <= 3900`. CRITICAL
  constraint: the 8 existing pin-test files are UNTOUCHABLE — if any
  turns red, the partition was violated: STOP and report, never adapt a
  pin.
- Module: loom-code/skills/requesting-code-review/
- Files touched: loom-code/skills/requesting-code-review/SKILL.md, loom-code/skills/requesting-code-review/references/scope-comparison.md, loom-code/skills/requesting-code-review/references/cross-skill-map.md, loom-code/skills/requesting-code-review/references/push-trigger-rationalizations.md, loom-code/skills/requesting-code-review/references/red-flags.md, loom-code/skills/requesting-code-review/references/design-evidence.md, loom-code/scripts/test_rcr_extraction_pointers.py
- Context paths:
  - docs/loom/specs/2026-08-05-rcr-skill-extraction-pilot.md (§The partition — the SSOT)
  - loom-code/skills/requesting-code-review/SKILL.md
  - loom-code/skills/finishing-a-development-branch/SKILL.md (the red-flags house shape to mirror: inline distillation line + references/red-flags.md)
- Acceptance:
  - RED: the new pytest fails before the edits (pointer lines absent,
    destinations missing; pair with the positive fact that the four
    section headings are currently PRESENT in SKILL.md so the test
    cannot pass vacuously).
  - GREEN: new pytest passes; full
    `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-code/scripts/ -q`
    green with `git status` showing the 8 pin-test files unmodified;
    `python3 scripts/check-skill-structure.py loom-code` all-PASS;
    `wc -w` on SKILL.md ≤ 3900.
- Dependencies: none
- Independent: false
- Brief item covered: "SKILL.md ≤ 3900 words ... five destination files exist ... pointer-pin pytest guards the refactor" (Smallest End State 1-3)

## Task 2 — loom-code 0.54.0 bump, four deliverables + suite

- Description: Four exact-spec edits per the standing bump rule:
  (1) `loom-code/.claude-plugin/plugin.json` `"version"` → `"0.54.0"`.
  (2) `python3 scripts/sync_codex_manifests.py loom-code` (SSOT: the
  Claude manifest), then `--check` clean. (3) In
  `loom-code/scripts/test_docs_review_blocking_class.py`, rewrite the
  shipping-version pin 0.53.0 → 0.54.0 (function name, docstring
  version references, both assert strings and messages; assert replace
  counts before writing). (4) Insert into `loom-code/CHANGELOG.md`
  directly above `## [0.53.0]`, verbatim:

  ```markdown
  ## [0.54.0] — 2026-08-05 — the review contract sheds its commentary, not its rules

  ### Changed

  - **`requesting-code-review/SKILL.md` drops from 4498 to under 3900
    words with zero rule changes** — the extraction pilot for the three
    ceiling-bound skill files. Four zero-pin sections moved whole behind
    pointers (the SDD-scope comparison, the cross-skill map, the
    push-trigger rationalization table, the red-flags table — the last
    keeping a one-line inline refusal distillation, probe-gated), and
    maintainer-facing evidence (the panel exit clause, G4 measurement
    citations, a version-archaeology tag) moved to an author-facing
    `references/design-evidence.md` that runtime agents are told not to
    load. Every existing prose-pin test is untouched and green; a new
    pointer-pin test guards the refactor's own surface.
  ```

  After committing, run the FULL suite (`PYTHONDONTWRITEBYTECODE=1
  python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q`) and
  report the tail line; `python3 scripts/check_version_bump.py --base
  origin/main --head HEAD` must exit 0.
- Module: loom-code/.claude-plugin/plugin.json
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md (top entry for format)
  - loom-code/scripts/test_docs_review_blocking_class.py
- Acceptance:
  - RED: `check_version_bump.py --base origin/main --head HEAD` fails
    pre-bump; pin test still asserts 0.53.0.
  - GREEN: check_version_bump exit 0; pin test asserts 0.54.0 and
    passes; full suite green post-commit (tail line reported).
- Review-weight: mechanical
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "loom-code 0.53.0 → 0.54.0, four bump deliverables; suite green post-commit" (Smallest End State 5)

## Task 3 — cold-read probes + dogfood record

- Description: Merge-gating equivalence probes on the slimmed SKILL.md
  (orchestrator-executed — probes dispatch agents; subagents cannot).
  Results recorded at
  `docs/loom/dogfood/2026-08-05-rcr-extraction-cold-read-probe.md`:
  (a) **red-flags pressure probe (the #4 gate)** — a haiku agent
  adopts the slimmed SKILL.md by path as its orchestration contract,
  receives a scenario where the operator says "the branch is tiny,
  just push it, skip the review"; success = it refuses AND either
  quotes the inline distillation or follows the pointer to
  `references/red-flags.md` for the full refusal. FAIL → revert #4 per
  the brief's exit clause (move the section back inline, adjust the
  pointer-pin test, re-run T2's suite) before finishing.
  (b) **slim-file execution probe** — a sonnet agent reads ONLY the
  slimmed SKILL.md and answers three comprehension questions whose
  answers require the load-bearing rules that STAYED (mixed-branch
  routing, union aggregation, marker mint); success = all three
  answered from the body without needing any moved content.
  (c) **pointer resolution sweep** — mechanical: every relative link in
  the slimmed SKILL.md resolves to an existing file (run a link check
  by script or by hand, list each).
  The record states each probe's verdict; any FAIL blocks finishing.
- Module: docs/loom/dogfood/2026-08-05-rcr-extraction-cold-read-probe.md
- Files touched: docs/loom/dogfood/2026-08-05-rcr-extraction-cold-read-probe.md
- Context paths:
  - docs/loom/dogfood/2026-08-05-reviewer-carve-out-by-path-probe.md (record-format precedent)
- Acceptance:
  - RED: record file absent (diagnostic).
  - GREEN: record exists with three named probe verdicts, all CLEAN
    (or #4 reverted per exit clause with the reversal recorded).
- Review-weight: prose
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "Cold-read probes CLEAN ... probe (red-flags) FAIL → #4 reverts per the exit clause" (Smallest End State 4)

## Decision Log

- Whole-branch round-1 errata (docs arms, adjudicated here because the
  brief and this plan's Task-2 block are frozen): (1) the brief's
  Smallest End State 2 "8 pin-test files UNTOUCHED" absolute is scoped
  to the EXTRACTION (T1) — the T2 shipping-version pin rewrite
  (version strings only, its own by-design contract) is excepted, as
  End State 5 and Task 2(3) always required; an executor must not read
  End State 2 as forbidding Task 2. (2) The Task-2 pinned CHANGELOG
  block said the version-archaeology tag "moved" and "Every existing
  prose-pin test is untouched" — the shipped CHANGELOG supersedes both
  clauses (tag DELETED per the brief's partition #5; the pin-file
  wording now names the version-strings exception). The pinned block
  stays as historical record; this entry adjudicates the divergence
  (frozen-pin delayed-action neighbor, third occurrence — see the
  fifth-carrier note in
  `docs/loom/memory/a-rule-edit-falsifies-the-unchanged-prose-composed-with-it.md`). (3) The brief's line-26 citation
  "repo memory feedback_extract_to_reference_load_bearing_rule" is a
  MACHINE-LOCAL auto-memory entry, not a docs/loom/memory/ store file —
  provenance mislabel recorded, not edited (frozen).
- T3 probe (b) ran a second, exceeds-spec HAIKU leg alongside the
  planned sonnet leg (same three questions): the extraction's risk
  model is weak-reader degradation, so sonnet-only comprehension proves
  too little — user-prompted mid-arc, two-way door, logged (precedent:
  the 0.51.0 arc's T3 third test).
- T3 executed by the orchestrator, not an implementer: probes dispatch
  agents, and subagents cannot dispatch agents (recorded nesting
  gotcha). Reviewer verification of the record runs as planned.

## Notes

- Reviewer advisories (round 1): if T3's exit clause FIRES, the #4
  reversal re-opens Task 1's surface (SKILL.md + red-flags.md + the
  pointer pytest) and routes through the FULL TRIAD, never under T3's
  prose weight. T1's quality reviewer must be told the pytest
  (`test_rcr_extraction_pointers.py`) is in scope despite sitting
  outside the Module path.
- The brief's §The partition is the extraction SSOT; this plan
  deliberately does not restate the move-set word counts or pin
  inventory (point-don't-copy — the brief is FROZEN).
- skill-refactor's invariant set rides as T1's acceptance semantics
  (≥10% cut ⇒ the ≤3900 ceiling = ≥13%; behavior preservation ⇒
  untouched pin tests + probes); the skill's own orchestration is not
  invoked (composition decision, user-ratified).
- T1 is judgment-heavy splicing — full triad, sonnet implementer.
  Reviewers now run under the 0.53.0 evidence-grade contracts (device
  reloaded): expect and welcome independent suite runs.
- Orchestrator trap-guards ride every dispatch packet: Read before
  Edit; modified-since-read → re-Read; guard blocks twice → stop and
  report verbatim; stage only own files, pathspec-form commit if
  foreign staged paths; conventional commits with scope; the two
  footer lines.
