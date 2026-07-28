# Plan: docs citation check + docs-branch review mode (P3+P4)

Source brief: docs/loom/specs/2026-07-28-docs-citation-check-and-review-mode.md
Total tasks: 6
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible (T3 and T4 are a parallel pair after T2)
Plan-document-reviewer verdict: PASS (2026-07-28, round 2, 14/14)

## Notes

- **Kickoff sweep result: zero one-way-door hits.** All three brief forks were
  resolved as the Kickoff decisions below; each is a two-way door (trigger
  rule, wiring point, and anchor grammar are all revisable without rework
  beyond the sentence that states them). No batched briefing required. Round-1
  Check-8 gap (the BACKLOG annotation obligation) resolved as Task 6, not a
  briefing item. Reviewer round-2 advisory (T5/T6 parallel-eligible) noted,
  not adopted — marking them is a schema change outside the post-PASS closed
  list, and sequential dispatch of two doc-writing tasks costs nothing.
- Stamped verdict: post-PASS amendment kind 1 (stamping the verdict) — no
  re-review required per the closed list.
- **Change-folder binding: none, loudly.** Two non-archived `docs/loom/<change-id>/`
  folders exist (`2026-07-12-us-sec-primary-source-layer`,
  `2026-07-19-8k-prose-kpi-intake`); both are prior investing-toolkit arcs with no
  relation to this brief. Input is the explicitly handed brainstorming brief; no
  binding, no content-similarity guessing.
- Kickoff decision: docs-only trigger → **every changed file ends in `.md`**,
  path-agnostic (brief Open Question 1's leaning, adopted — simplest rule an
  orchestrator at any tier can apply mechanically; a mixed branch falls back to
  the default code path).
- Kickoff decision: script wiring point → **the dispatch step of
  `requesting-code-review`'s docs mode** (brief Open Question 2's leaning,
  adopted — single wiring point; `finishing-a-development-branch` inherits via
  its existing delegation, zero edits there).
- Kickoff decision: §N anchor grammar → **numbered headings only** (`## 5.`,
  `### 3.7`, and `§N` / `§N.M` reference forms) in v1 (brief Open Question 3's
  leaning, adopted — that is what the corpus uses; named anchors are a
  measured-need extension).
- Word-budget guard: `requesting-code-review/SKILL.md` is at 3,709 words
  (hard cap 4,500). T4's acceptance includes re-measuring after the edit AND
  running `python3 scripts/check-skill-structure.py loom-code` locally (the cap
  check is CI-only; a green pytest run says nothing about it).
- Standing trap-guards for every implementer dispatch: Read before Edit;
  re-Read on modified-since-read; stop after two identical guard blocks; no
  `git add`/`git commit` by implementers (orchestrator commits with explicit
  pathspecs); the Write tool refuses basename `report.md` — write another name
  and `mv`.

## Task 1 — citation extractor + path:line bounds check

- Description: Create `loom-code/scripts/check_doc_citations.py` (stdlib-only,
  read-only): parse `` `path:line` `` and `` `path:line-range` `` citations
  from given Markdown files, resolve each path against the repo root, and
  report any citation whose file does not exist or whose line (or range end)
  exceeds the file's length. Exit 0 = all resolve; exit 1 = findings (one line
  per finding: `<doc>:<lineno> -> <cited-path>:<cited-line> <reason>`); exit 2
  = usage error. Per brief §Smallest End State item 1, the v1 scope is exactly
  this check plus Task 2's — no quoted-string verification, no semantic
  checking.
- Module: loom-code/scripts/check_doc_citations.py
- Files touched: loom-code/scripts/check_doc_citations.py, loom-code/scripts/test_check_doc_citations.py
- Context paths:
  - loom-code/scripts/check-living-spec-index.py (CLI + exit-code conventions)
  - docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md (§5 — the
    live-tested prototype this reimplements)
- Acceptance:
  - RED: `test_check_doc_citations.py::test_flags_out_of_range_line` fails
    (fixture doc citing a real temp file at a line past its length must be
    flagged; a citation within bounds must not be).
  - GREEN: the test passes; running
    `python3 loom-code/scripts/check_doc_citations.py <fixture>` exits 1 on
    the bad fixture and 0 on the clean one. Runnable-capability note: the new
    verb is `python3 loom-code/scripts/check_doc_citations.py <files…>`; it is
    declared in the command surface by Task 4's dispatch-step text (this plan's
    declared wiring point) — no other command registry exists for loom-code
    scripts.
- External surfaces: none (stdlib only — `re`, `pathlib`, `argparse`, `sys`).
- Dependencies: none
- Independent: false
- Brief item covered: "every `path:line` / `path:line-range` citation in the
  target docs resolves to a file that exists and a line within its length"
  (brief §Smallest End State item 1, first check)

## Task 2 — §N anchor check

- Description: Extend `check_doc_citations.py` with the second v1 check: a
  `§N` / `§N.M` reference pointing into a named sibling document (the pattern
  `` `<doc>.md` §N `` or `§N` adjacent to a document reference on the same
  line) resolves to an existing numbered heading (`## N.` / `### N.M`) in that
  document. Unresolvable anchors are findings with the same output format as
  Task 1. Bare `§N` with no document named on the same line refers to the
  containing document itself.
- Module: loom-code/scripts/check_doc_citations.py
- Files touched: loom-code/scripts/check_doc_citations.py, loom-code/scripts/test_check_doc_citations.py
- Context paths:
  - docs/loom/audits/2026-07-28-revenue-chain-and-hierarchy-audit.md (§N
    citation convention in live use — its header defines the convention)
- Acceptance:
  - RED: `test_check_doc_citations.py::test_flags_missing_section_anchor`
    fails (fixture citing `§9` of a sibling with sections 1–7 must be flagged;
    a valid `§3.7` must not be).
  - GREEN: the test passes; full suite
    `python3 -m pytest loom-code/scripts/ -q` green.
- External surfaces: none.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "every `§N` / `§N.M` anchor into a named sibling
  document resolves to an existing numbered heading there" (brief §Smallest
  End State item 1, second check)

## Task 3 — corpus dogfood run (P3 acceptance measurement)

- Description: Run the finished script over the full corpus
  (`docs/loom/audits/*.md docs/loom/specs/*.md docs/loom/plans/*.md`, ~831
  citations measured at brief time) and record the result as a dogfood note at
  `docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md`: total citations
  parsed, findings count, per-finding adjudication (true drift vs false
  positive), recall against the documented ground-truth drift instances (the
  four on `feat-plan-fact-grounding`, the erratum-insertion invalidations on
  `docs-backlog-resequence-around-hierarchy` — enumerate which are still
  observable on main), and the false-positive rate. State the population and
  that counts are floors (the brief's own standard). The reversal condition
  from the brief (§Alternatives, "My take") — FP rate above ~10% after
  legitimate-pattern exclusions — is evaluated HERE: if tripped, stop and
  surface to the user before Task 4's text ships a dependency on the script.
  Script fixes discovered by the run (parser gaps, legitimate-pattern
  exclusions) are in scope for this task as RED-first amendments.
- Module: docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md
- Files touched: docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md,
  loom-code/scripts/check_doc_citations.py,
  loom-code/scripts/test_check_doc_citations.py
- Context paths:
  - docs/loom/BACKLOG.md ("Plan-stage fact grounding — what 0.39.0 does NOT
    close" item 3 — the ground-truth drift instances)
  - docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md (report
    conventions: population statements, limitations section)
- Acceptance:
  - RED: the dogfood note does not exist; the recall claim is unmeasured.
  - GREEN: the note exists with all five elements (population, findings,
    adjudication table, recall vs ground truth, FP rate); every ground-truth
    instance still observable on the branch is either flagged by the script or
    its non-detection is explained in the note; suite green.
- External surfaces: none.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "run against the full docs/loom corpus … Recall floor:
  every documented real drift instance from the two source branches must be
  flagged. Precision: manually adjudicate all hits" (brief §Dogfood item 1)

## Task 4 — docs-only dispatch mode in requesting-code-review

- Description: Amend `requesting-code-review/SKILL.md` **in place** at the
  diff-scope step (the `:96` "Determine diff scope" region): when every file
  in the branch diff ends in `.md`, the dispatch (a) instructs reviewers to
  read each changed artifact **whole**, with the diff as context — including
  the explicit question "does any UNCHANGED claim in this file contradict the
  change, or the current code?"; (b) names the prose defect taxonomy —
  omission / ambiguity (an absolute like "only/never/zero" without support) /
  inconsistency (cross-paragraph, changed-vs-unchanged) / incorrect-fact (a
  citation that does not support its claim) / missing population on a measured
  number — as the dimensions that replace the code-shaped ones for this
  dispatch; (c) runs `python3 loom-code/scripts/check_doc_citations.py` over
  the changed files and includes its output in the dispatch packet. Add a new
  guard test `loom-code/scripts/test_docs_review_mode.py` pinning: the
  trigger condition, the whole-artifact instruction, all five taxonomy labels
  with inline definitions, the script invocation, and polarity (an inverted
  "review only the diff" mutation must fail) — scoped to the added section per
  the repo's grep-window convention. The `code-reviewer.md` agent contract and
  its ten dimensions are NOT touched (brief §Decision).
- Module: loom-code/skills/requesting-code-review/SKILL.md
- Files touched: loom-code/skills/requesting-code-review/SKILL.md,
  loom-code/scripts/test_docs_review_mode.py
- Context paths:
  - loom-code/skills/requesting-code-review/SKILL.md (current dispatch step)
  - loom-code/scripts/test_plan_fact_grounding.py (guard-test style: section
    isolation + polarity, whitespace-normalized matching — hard-wrap lesson)
  - docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md (§3.1
    proposal text, §3.3 dimension list, §6b measured result)
- Acceptance:
  - RED: `test_docs_review_mode.py::test_rcr_carries_docs_only_mode` fails
    against the unamended SKILL.md.
  - GREEN: the test passes; the six pre-existing guard tests referencing
    requesting-code-review text
    (`test_asking_user_briefing_escalation.py`,
    `test_code_reviewer_principles_derivation.py`,
    `test_finishing_step3_autoproceed.py`, `test_git_guard.py`,
    `test_reviewer_dispatch_role_anchor.py`, loom-pipeline's
    `test_family_relay.py`) all still pass;
    `python3 scripts/check-skill-structure.py loom-code` passes locally with
    the post-edit word count stated in the task report (pre-edit: 3,709 /
    cap 4,500).
- External surfaces: none.
- Dependencies: Task 2 completes first (the mode text names the script and its
  real CLI; writing it against an unbuilt script is the doc-mirrors-code
  dependency this field exists to declare)
- Independent: true
- Brief item covered: "A docs-only dispatch mode in requesting-code-review —
  one in-place amendment at the diff-scope step … (a) whole changed artifact …
  (b) prose defect taxonomy … (c) the citation script's output rides the
  dispatch packet" (brief §Smallest End State item 2)

## Task 5 — planted-defect A/B dogfood (P4 acceptance measurement)

- Description: Build a fixture docs branch state (scratchpad or throwaway
  worktree — never committed) carrying exactly one defect per taxonomy class:
  a stale `path:line` citation, an unsupported absolute, a population-less
  measurement, a cross-paragraph contradiction (one side OUTSIDE the diff),
  and an omission. **Mechanically verify the fixture before any dispatch**
  (each planted defect confirmed present and isolated — the
  contaminated-fixture lesson, `2026-07-27` coldread §Over-firing). Dispatch
  two review arms on identical material: control = current default dispatch
  text; treatment = Task 4's docs-mode dispatch. Record per-arm classes
  caught in `docs/loom/dogfood/2026-07-28-docs-review-mode-ab.md` with the
  standing disciplines: interpretation rules written BEFORE results arrive;
  weak-tier cells n≥2 or direction-only conclusions; n=1 limitations stated;
  agent-type confound (general-purpose carrying working-tree text vs
  installed-cache skill) disclosed.
- Module: docs/loom/dogfood/2026-07-28-docs-review-mode-ab.md
- Files touched: docs/loom/dogfood/2026-07-28-docs-review-mode-ab.md
- Context paths:
  - docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md (the 2×2
    method template: fixture verification, pre-written readings, limitations)
  - docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md (Task 3's real
    drift material seeds the planted-citation defect)
- Acceptance:
  - RED: the A/B note does not exist; the mode's detection claim rests only on
    the source branch's rounds 7–9.
  - GREEN: the note exists with both arms' per-class detection table, the
    pre-written interpretation rules, and a stated verdict on whether the
    codified mode reproduces the rounds-7–9 result (whole-artifact catches
    what diff-scope misses); fixture-verification evidence included.
- External surfaces: none.
- Dependencies: Tasks 3, 4 complete first
- Independent: false
- Brief item covered: "Mode (P4): planted-defect A/B … mechanically verify the
  fixture before dispatch … count classes caught per arm. Weak-tier cells n≥2
  or direction-only conclusions" (brief §Dogfood item 2)

## Task 6 — annotate the superseded BACKLOG residual entry

- Description: Edit `docs/loom/BACKLOG.md`'s "Plan-stage fact grounding — what
  0.39.0 does NOT close" item 3 (`file:line` citations drift under parallel
  edits): append a note that the DETECTION half is now mechanised by
  `loom-code/scripts/check_doc_citations.py` (cite the corpus-run dogfood note
  for the measured result), while the PREVENTION half — durable anchors over
  bare line numbers — remains open. Do not delete or restructure the item; the
  brief mandates annotate-not-delete.
- Module: docs/loom/BACKLOG.md
- Files touched: docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md (Task 3's note —
    the citation target)
- Acceptance:
  - RED: grep of the BACKLOG item-3 block for `check_doc_citations` returns
    nothing (the annotation is absent).
  - GREEN: the item-3 block names the script and the corpus-run note, states
    the detection/prevention split, and the item's original text is unchanged
    above the annotation; suite green.
- External surfaces: none.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "`docs/loom/BACKLOG.md` 'what 0.39.0 does NOT close'
  item 3 (citation drift) — the detection half is mechanised; annotate the
  entry at close-out rather than deleting it" (brief §What Becomes Obsolete)

## Decision Log

- 2026-07-28 (T3 round 1 → user): corpus run tripped the brief's ~10% FP
  reversal condition (79.7%). User chose "fix the resolver, re-measure" over
  narrowing scope or dropping the script. Establishes the ratified principle:
  when the check's grammar cannot adjudicate a citation, classify it UNCHECKED
  loudly — never emit a finding, never skip silently.
- 2026-07-28 (T3 round 2 → orchestrator, logged not asked): round 2 still
  trips the threshold, but the entire remaining FP class is §N references into
  documents with zero numbered headings — the same grammar-not-applicable
  shape the user already ratified for ambiguous basenames. Applied the same
  principle (§N → UNCHECKED when the target has no numbered headings) as a
  two-way-door scope rule and dispatched round 3, rather than re-asking; a
  documented decision beats re-asking. If round 3 still trips, the full
  trajectory goes back to the user.
- 2026-07-29 (T3 round 3 → user): three-round FP trajectory 79.7% → 96.8% →
  33.3%, still above threshold, but decisively split per check: path:line at
  0% FP (8/8 TP), §N at zero TP with 4 architecturally-distinct residual FPs.
  User chose **split-half shipping**: default invocation = path:line only
  (reversal condition satisfied for the shipped wiring); §N behind an
  experimental `--sections` flag with a stated re-measure trigger (the §N
  convention entered the corpus only days before the run — prospective value,
  no retrospective evidence).
- 2026-07-28 (T3∥T4 sequencing miss, recorded for close-out): T3's Description
  carried a gating obligation over T4 ("stop before Task 4's text ships a
  dependency") that the Dependencies field did not encode; the parallel
  marking (round-1 reviewer advisory, adopted) made T4 commit before T3's
  reversal evaluation ran. Same defect class this branch exists to close — an
  obligation living in prose that the structural fields do not encode. Carry
  to whole-branch review.
