# Plan: requesting-docs-review — standalone docs-review skill

Source brief: docs/loom/specs/2026-07-30-requesting-docs-review-standalone-skill.md
Total tasks: 8
Critical-path depth: 5 (T1→T2→T3→T4→T7 and T1→T5→T6→T8→T7)
Execution order: parallel-where-possible (T2 ∥ T5 after T1)
Plan-document-reviewer verdict: PASS (2026-07-30, round 1, 14/14); amendment (Task 8 added) re-reviewed: PASS (2026-07-30, 14/14)

## Task 1 — docs-reviewer agent contract + distribution registration
- Description: Create the prose-native reviewer agent `loom-code/agents/docs-reviewer.md`
  (mirrors code-reviewer.md structure: name+description frontmatter, verdict-only
  role-contract rules, verdict template with prose `dimension_scores:`
  [omission / ambiguity / inconsistency / incorrect-fact / missing-population] and
  per-finding `class: instruction | evidence`, whole-artifact scope duty, path-like
  `where:` on findings per loom_gate_markers.py:224-247) carrying the three injection
  marker pairs (baseline-v1, reviewer-discipline-v1, rule-sheet-v1), and register it
  in distribute.py's AGENT_BASELINE_TARGETS / AGENT_REVIEWER_DISCIPLINE_TARGETS /
  rule-sheet target lists.
- Module: loom-code/agents
- Files touched: loom-code/agents/docs-reviewer.md, loom-code/scripts/distribute.py,
  loom-code/scripts/test_docs_reviewer_agent.py
- Context paths:
  - loom-code/agents/code-reviewer.md
  - loom-code/scripts/distribute.py
  - loom-code/scripts/_baseline.md
  - loom-code/scripts/_reviewer-discipline.md
  - loom-code/scripts/loom_gate_markers.py
- Acceptance:
  - RED: `pytest loom-code/scripts/test_docs_reviewer_agent.py` fails (agent file
    absent; distribute.py target lists lack docs-reviewer).
  - GREEN: test passes — agent file exists with all three BEGIN/END marker pairs,
    prose dimension_scores template, class field, verdict-only contract; docs-reviewer
    present in the three distribute.py target lists; `python3 loom-code/scripts/distribute.py`
    exits 0 and injects markers; `python3 loom-code/scripts/verify-drift.py` exits 0.
    New test file auto-runs under CI's existing `pytest loom-code/scripts/` invocation
    (.github/workflows/loom-code-ci.yml:94) — no new command-surface verb.
- External surfaces: None (repo-internal scripts + prose contracts).
- Dependencies: none
- Independent: false
- Brief item covered: "New agent `loom-code/agents/docs-reviewer.md` — prose-native
  contract mirroring `code-reviewer.md` structure … carrying the three
  injection-marker blocks and registered in `distribute.py` target lists"

## Task 2 — requesting-docs-review SKILL.md (jurisdiction + convergence contract)
- Description: Create `loom-code/skills/requesting-docs-review/SKILL.md` (flat folder;
  body ≤6k tokens) owning the docs arm: docs-only dispatch trigger (diff non-empty AND
  all files `.md`), whole-artifact scope, the five prose dimensions, `class:
  instruction | evidence` fail-closed to instruction, instruction-only aggregation,
  check_doc_citations.py pre-pass riding the dispatch packet, appended-corrections
  rule for unchanged prose — relocated semantics from requesting-code-review — PLUS
  the new convergence contract: hard cap 2 rounds then STOP-and-surface (breach only
  by explicit user authorization, critics' precedent), round-2 dispatch carries
  round-1 findings verbatim with fix-verification duty and a re-litigation ban
  (a closed finding may not be re-raised in new words), oscillation stop (a
  fix-verified finding resurfacing ends the loop → user). Convergence imperatives
  placed as prominent dispatch-moment directives, not trailing prose asides
  (docs/loom/memory/imperative-placement-prominence-decides-weak-model-firing.md).
- Module: loom-code/skills/requesting-docs-review
- Files touched: loom-code/skills/requesting-docs-review/SKILL.md,
  loom-code/scripts/test_requesting_docs_review_skill.py
- Context paths:
  - docs/loom/specs/2026-07-30-requesting-docs-review-standalone-skill.md
  - loom-code/skills/requesting-code-review/SKILL.md
  - loom-code/scripts/check_doc_citations.py
  - loom-code/scripts/test_docs_review_mode.py
  - loom-code/scripts/test_docs_review_blocking_class.py
- Acceptance:
  - RED: `pytest loom-code/scripts/test_requesting_docs_review_skill.py` fails (skill
    file absent).
  - GREEN: test passes — pins trigger phrasing, whole-artifact polarity (with mutation
    guard mirroring test_docs_review_mode.py:166-185), all five dimension names,
    class taxonomy + fail-closed sentence, instruction-only aggregation, citation
    pre-pass + "dispatch packet", 2-round cap imperative, round-1-findings-verbatim
    handoff, re-litigation ban, oscillation stop, appended-corrections rule,
    user-authorized cap breach, and the verdict-minting instruction
    (`loom_gate_markers.py review-pass` with prose dimension_scores).
    Grep assertions scoped to anchored windows
    (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md).
    `.claude/hooks/validate-skill-folder-structure.sh` passes on the new folder.
- External surfaces: None (prose contract + repo-internal script references).
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "New skill `loom-code/skills/requesting-docs-review/` … owning
  the docs arm of branch review … convergence contract (the new part)"

## Task 3 — requesting-code-review three-way routing + relocation cleanup + trivial-skip boundary
- Description: Rewrite requesting-code-review Step 1 into the three-way dispatch
  (all `.md` → delegate whole review to requesting-docs-review; mixed → per-file
  split: code files → code-reviewer panel, `.md` files → docs-reviewer, orchestrator
  unions verdicts and both arms must pass; code-only → unchanged); delete the
  relocated docs-mode content at source (SKILL.md:97 paragraph, :100 docs sentence,
  :147 class comment scope, :173-186 docs aggregation paragraph); narrow the
  trivial-skip exemptions (:48,54) from blanket "doc change / doc-only changes" to
  mechanical doc edits only (typo, version bump, generated/sync output) with
  authored prose routed to docs review; update test_docs_review_mode.py and
  test_docs_review_blocking_class.py to pin the new routing text and assert the old
  inline docs-mode paragraph is ABSENT (content pins that moved now live in Task 2's
  test file; version pins stay 0.41.0 here and are updated in Task 7).
- Module: loom-code/skills/requesting-code-review
- Files touched: loom-code/skills/requesting-code-review/SKILL.md,
  loom-code/scripts/test_docs_review_mode.py,
  loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/skills/requesting-docs-review/SKILL.md
  - loom-code/skills/requesting-code-review/SKILL.md
- Acceptance:
  - RED: updated `pytest loom-code/scripts/test_docs_review_mode.py
    loom-code/scripts/test_docs_review_blocking_class.py` fails against current
    SKILL.md (three-way routing text absent; old inline paragraph still present;
    trivial-skip still blanket).
  - GREEN: both updated test files pass; full `pytest loom-code/scripts/` stays green
    (Task 2's test file unaffected by the removal).
- External surfaces: None.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "Routing stays where callers already are —
  `requesting-code-review` Step 1 becomes a three-way dispatch" + "Trivial-skip
  boundary defined"

## Task 4 — finishing-a-development-branch names the docs arm + cap-breach surfacing
- Description: Update finishing-a-development-branch flow text (SKILL.md:19-20 flow
  diagram, :81 delegation row, :100-117 verdict routing) to name the three-way review
  dispatch and the docs-arm convergence outcome: a 2-round-cap STOP from
  requesting-docs-review surfaces to the user (with surviving findings) instead of
  entering the silent fix→re-review loop at :113-117.
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md,
  loom-code/scripts/test_finishing_docs_arm.py
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md
  - loom-code/skills/requesting-docs-review/SKILL.md
- Acceptance:
  - RED: new `pytest loom-code/scripts/test_finishing_docs_arm.py` fails (flow text
    lacks docs-arm + cap-STOP surfacing).
  - GREEN: test passes; assertions window-scoped per
    docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md.
- External surfaces: None.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "`finishing-a-development-branch:19-20,81,100-117` keeps
  invoking requesting-code-review as today (no caller-facing change); its flow text
  updates to name the docs arm" + convergence contract "(a) … STOP and surface to
  the user"

## Task 5 — SDD Review-weight: prose
- Description: Extend subagent-driven-development's Review-weight mechanism
  (SKILL.md:110-117) with `prose`: a plan task declaring `Review-weight: prose`
  keeps implementer + spec-reviewer and replaces code-quality-reviewer with the
  docs-reviewer agent; allowed only when the task's Files touched are all `.md`
  authored prose; any violation fails closed to the full triad (mirroring
  mechanical's fail-closed rule).
- Module: loom-code/skills/subagent-driven-development
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md,
  loom-code/scripts/test_review_weight_prose.py
- Context paths:
  - loom-code/skills/subagent-driven-development/SKILL.md
  - loom-code/agents/docs-reviewer.md
- Acceptance:
  - RED: new `pytest loom-code/scripts/test_review_weight_prose.py` fails (prose
    weight absent from SKILL.md).
  - GREEN: test passes — pins the declaration syntax, the reviewer substitution
    (spec-reviewer stays), the all-`.md` authored-prose eligibility rule, and the
    fail-closed sentence.
- External surfaces: None.
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "SDD per-task prose review … plan tasks may declare
  `Review-weight: prose` … the orchestrator then replaces the code-quality-reviewer
  arm with the docs-reviewer agent — implementer and spec-reviewer stay"

## Task 6 — plan-document-reviewer Check 16 prose row
- Description: Extend Check 16 in the plan-document-reviewer prompt
  (references/plan-document-reviewer-prompt.md:48,67) with the `prose` weight row:
  eligible only for tasks whose Files touched are all `.md` authored prose (never
  code, config, scripts); wording transcribed from Task 5's shipped SDD text
  (docs/loom/memory/prose-contract-mechanism-transcribes-from-code.md — transcribe
  from the SSOT, don't re-derive).
- Module: loom-code/skills/writing-plans
- Files touched:
  loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md,
  loom-code/scripts/test_check16_prose_row.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md
  - loom-code/skills/subagent-driven-development/SKILL.md
- Acceptance:
  - RED: new `pytest loom-code/scripts/test_check16_prose_row.py` fails (Check 16 has
    no prose row).
  - GREEN: test passes — Check 16 lists prose alongside mechanical with the
    eligibility rule matching SDD's wording.
- External surfaces: None.
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "Plan-side gate: extend Check 16 … with the prose row"

## Task 7 — release mechanics + BACKLOG flip + version pins
- Description: Bump loom-code to 0.42.0 (plugin.json + CHANGELOG entry describing the
  extraction, routing, convergence contract, SDD prose weight); update the 0.41.0
  version pins in test_docs_review_blocking_class.py (:319-336) to 0.42.0; sync
  marketplace description (check-marketplace-description-sync.py) and codex manifests
  (sync_codex_manifests.py); flip docs/loom/BACKLOG.md §"Standalone docs-review
  skill" from PARKED to shipped-in-this-arc (keep the unpark-condition history,
  point to the brief/plan).
- Module: loom-code
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/CHANGELOG.md,
  loom-code/scripts/test_docs_review_blocking_class.py,
  .claude-plugin/marketplace.json (listed, ultimately unchanged — sync check was
  clean), loom-code/.codex-plugin/plugin.json, docs/loom/BACKLOG.md
- Context paths:
  - scripts/check_version_bump.py
  - scripts/check-marketplace-description-sync.py
  - scripts/sync_codex_manifests.py
  - docs/loom/BACKLOG.md
- Acceptance:
  - RED: `pytest loom-code/scripts/test_docs_review_blocking_class.py` fails after
    bumping plugin.json alone (CHANGELOG/`0.42.0` pins not yet aligned) — the version
    pins are the failing test; alternatively `python3 scripts/check_version_bump.py`
    fails while skill content changed and version is still 0.41.0.
  - GREEN: full `pytest loom-code/scripts/ scripts/` green;
    `sync_codex_manifests.py --check --all` clean; marketplace description sync
    clean; BACKLOG entry updated.
- External surfaces: None (repo-internal CI scripts; marketplace.json is a committed
  file, publishing happens on merge to main per the GitHub-source marketplace flow).
- Dependencies: Tasks 3, 4, 6, 8 complete first
- Independent: false
- Brief item covered: "Test migration + release: … bump plugin.json to 0.42.0
  (+ CHANGELOG, marketplace description sync, codex manifest sync)" + "What Becomes
  Obsolete … BACKLOG.md §'Standalone docs-review skill' PARKED entry — flips"

## Task 8 — plan-format.md documents the prose review-weight
- Description: Document `Review-weight: prose` in the plan schema so a plan author
  consulting plan-format.md alone discovers the value is legal: extend the field
  enum at plan-format.md:60 (`<mechanical | prose | OMIT>`) and add the prose case
  to §Review-weight (~:81-87) — eligibility wording transcribed from the SDD SSOT
  (subagent-driven-development/SKILL.md "Prose review-weight substitution" block),
  consistent with Check 16's shipped row. Origin: Task 6 code-quality-review 🟡
  finding (plan-format.md never documents the value Check 16 validates; no original
  task touched plan-format.md).
- Module: loom-code/skills/writing-plans
- Files touched: loom-code/skills/writing-plans/references/plan-format.md,
  loom-code/scripts/test_plan_format_prose_weight.py
- Context paths:
  - loom-code/skills/writing-plans/references/plan-format.md
  - loom-code/skills/subagent-driven-development/SKILL.md
  - loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md
- Acceptance:
  - RED: new `pytest loom-code/scripts/test_plan_format_prose_weight.py` fails
    (enum lacks prose; §Review-weight lacks the prose case).
  - GREEN: test passes — window-scoped pins on the enum line and the §Review-weight
    prose sentence matching SDD's eligibility wording.
- External surfaces: None.
- Dependencies: Task 6 completes first
- Independent: false
- Brief item covered: "Plan-side gate: extend Check 16 … with the prose row (allowed
  only when the task's Files touched are all `.md` authored prose …)" — the schema
  file Check 16's own Behavioral rule 1 charters must document the same value.

## Notes

- Verdict history: original PASS stamped round 1 (stamping = amendment kind 1, no
  re-review). The LATER Task-8 addition was a substantive amendment and DID
  re-review — PASS, stamped in the header. Reviewer advisory notes: T3∥T6 / T4∥T6 left unmarked intentionally
  (T6 transcribes from T5's shipped text; release join stays simple at T7);
  keep the post-ship cold-read dogfood commitment visible at close-out.
- Kickoff decision: docs-arm verdict minting → SAME review-pass marker via
  `loom_gate_markers.py review-pass` (schema already accepts prose dimension names,
  loom_gate_markers.py:201-218; git-guard.py:12-25 requires review-pass.json
  regardless of arm — a separate docs marker would break the push gate). Arm-1
  lookup, recorded unbriefed.
- Kickoff decision: mixed-branch verdict join → requesting-code-review orchestrator
  unions both arms' findings; branch verdict is the WORSE of the two arm verdicts
  (either arm NEEDS_REVISION → branch NEEDS_REVISION). Arm-1 lookup (mirrors the
  existing panel-union convention at requesting-code-review Step 3), recorded
  unbriefed.
- Brief Open Question 1 resolved here: the docs arm mirrors requesting-code-review's
  existing two-arm panel union convention (pure-docs and mixed alike) — parity keeps
  the orchestrator contract uniform; panel width was never implicated in the loop
  pathology (the aggregation rule was). Brief Open Question 2 resolved: cap-breach
  wording adopts the critics' "user-authorized breach" precedent verbatim (Task 2).
- Honest limitation carried from the brief: the 2-round cap and re-litigation ban are
  enforced by orchestrator contract prose + grep-test pins this arc, not by a
  validator (round-count instrumentation is the parked P1+P2 ledger slice —
  docs/loom/BACKLOG.md). Mitigation per
  docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md: imperative
  placement at the dispatch moment (Task 2) + a post-ship cold-read dogfood on the
  next docs branch. If the cap fails to hold in practice, that incident is the
  ledger's unpark trigger.
- This branch itself is a MIXED branch (`.md` prose + Python tests) and will close
  out under the OLD review path (0.41.0's docs mode does not cover mixed) — treat
  the close-out as a live measurement of the pain this arc removes.
- Correction (2026-07-30 close-out, supersedes the previous bullet's prediction):
  the close-out ran the branch's OWN new mixed-branch per-file split live (two
  code arms + two docs arms, joined verdict, mint-once) — the old-path prediction
  did not hold; the live run doubles as the mixed-path dogfood.
- Task 3 and Task 7 both touch test_docs_review_blocking_class.py — sequential by
  Dependencies (T3 → T7), no parallel conflict.
- Task 2 bundles the relocated jurisdiction content and the new convergence contract
  into one SKILL.md + one pin-test file: one artifact, one failing test module;
  splitting them would push critical-path depth to 6 (>5 ceiling) for no independent
  verifiability gain.
