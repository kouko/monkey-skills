# Plan: reviewer evidence-grade contract (D-B-plus)

Source brief: docs/loom/specs/2026-08-05-reviewer-evidence-grade-contract.md
Total tasks: 4
Critical-path depth: 4 (T1 → T2 → T3 → T4)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-08-05, round 3, 15/15)

## Task 1 — R3 becomes a conditional fallback at the SSOT

- Description: In `loom-code/scripts/_reviewer-discipline.md`, replace
  the R3 opening (currently `You may not run tests; your correctness /
  tests verdict rests on the implementer's reported `test_results`,
  which you did not produce. When a dimension's PASS rests on evidence
  you could not independently confirm, do not emit a clean PASS for it`)
  with this text verbatim:
  `When a dimension's PASS rests on the implementer's reported
  `test_results` or other evidence you did not independently confirm —
  whether the check could not run (environment, capacity, no runnable
  check exists) or you simply did not run it — do not emit a clean
  PASS for it`
  (round-2 wording: the duty attaches to UNCONFIRMED evidence
  regardless of reason — T1's quality reviewer proved the earlier
  could-not-run antecedent left the chose-not-to reviewer bound only by
  the closing aphorism). In the retained tail, additionally replace the
  phrase `naming exactly what you could not verify` with `naming
  exactly what was not independently verified` (same falsified-neighbor
  seam, one clause past the pinned span); the rest of R3 — the
  downgrade instruction, the spec-reviewer binary-token clause, "Never
  false-pass" — stays byte-identical. Then
  run `python3 loom-code/scripts/distribute.py` (SSOT:
  `loom-code/scripts/_reviewer-discipline.md`) so all four agents'
  `reviewer-discipline-v1` managed blocks regenerate, and verify
  `python3 loom-code/scripts/verify-drift.py` exits 0. Add a prose-pin
  pytest (new file `loom-code/scripts/test_reviewer_r3_conditional.py`)
  asserting, whitespace-normalized on both sides: the new conditional
  opening present in the SSOT AND in all four agent files
  (`code-quality-reviewer.md`, `code-reviewer.md`, `spec-reviewer.md`,
  `docs-reviewer.md`), the absolute opening `You may not run tests;`
  absent from all five, and the anti-vacuous positive that `Never
  false-pass` is still present in all five.
- Module: loom-code/scripts/_reviewer-discipline.md
- Files touched: loom-code/scripts/_reviewer-discipline.md, loom-code/agents/code-quality-reviewer.md, loom-code/agents/code-reviewer.md, loom-code/agents/spec-reviewer.md, loom-code/agents/docs-reviewer.md, loom-code/scripts/test_reviewer_r3_conditional.py
- Context paths:
  - loom-code/scripts/_reviewer-discipline.md (R3 at lines ~35-45)
  - loom-code/scripts/distribute.py (run only; do not edit)
- Acceptance:
  - RED: the new pytest fails before the edit (conditional opening
    absent; `You may not run tests;` present in all five — assert both
    directions so the RED is genuine).
  - GREEN: pytest passes; verify-drift exits 0; full
    `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-code/scripts/ -q`
    green.
- Dependencies: none
- Independent: false
- Brief item covered: "R3 rewritten at the SSOT from an absolute premise to a conditional fallback" (Decision 2)

## Task 2 — four per-file carve-outs + purpose anchor + packet rule

- Description: Edit the four agent contracts OUTSIDE their managed
  blocks (never touch text between `BEGIN`/`END` markers — Task 1
  already regenerated those). Nine pinned edits, transcribed
  character-for-character (wrapping may follow each file's prevailing
  width):

  (a) `code-quality-reviewer.md` role rule 2: replace `You **may not**
  run tests — the implementer's `test_results` from the prior round is
  the test record.` with `You **may** run tests READ-ONLY as verdict
  evidence — running the package suite, re-running a RED, or probing a
  mutant on an extracted copy or isolated worktree is permitted and
  preferred over trusting reported `test_results`; you must leave no
  tracked file modified (after any probe, verify zero residual diff),
  and a test run is evidence-gathering, never a substitute for reading
  the artifact.`

  (b) `code-reviewer.md` role rule 2: replace `You **may not** run
  tests — that is `verification-before-completion`'s job; the` and its
  continuation through the end of that sentence (Read the file for the
  exact tail) with `You **may** run tests READ-ONLY as verdict evidence
  — same permission and zero-residual-diff duty as the per-task
  reviewers; `verification-before-completion` remains the finishing
  gate your run does not replace.` (Read the original sentence first;
  the replacement covers the whole prohibition sentence, leaving the
  surrounding rules untouched.)

  (c) `spec-reviewer.md` role rule 2: replace `You **may not** run
  tests — that is the implementer's job. (Reading test names and
  assertions is fine; running the test runner is not.)` with `You
  **may** run tests READ-ONLY to verify a spec claim — e.g. that a
  named RED test exists and discriminates; you must leave no tracked
  file modified, and running tests never extends your scope into
  quality dimensions.`

  (d) `docs-reviewer.md` role rule 2: replace `You **may not** run
  tests — prose has no suite to run, and code-side verification is
  `verification-before-completion`'s job.` with `Prose has no suite to
  run; but when `### Read context` includes code whose claims cite
  tests, you **may** run that suite READ-ONLY to verify the claim,
  leaving no tracked file modified — code-side verification remains
  `verification-before-completion`'s gate.`

  (e-h) Purpose anchor — insert into each of the four contracts as a
  new sentence, verbatim, at this per-file anchor (verified: only
  code-reviewer.md:16 and docs-reviewer.md:18 have a numbered rule 0):
  `code-reviewer.md` and `docs-reviewer.md` — at the END of role rule 0
  (the "You ARE the reviewer" rule); `code-quality-reviewer.md` and
  `spec-reviewer.md` (whose role rules start at 1) — as a standalone
  sentence at the END of role rule 1 (the scope rule), after its last
  existing sentence: `Your product is an
  evidence-grade verdict: prefer independent execution over reported
  results and experiments over static suspicion — reading the artifact
  is the foundation; tools only corroborate it.`

  (i) Packet-interface rule — insert into each of the four contracts'
  `## Input contract` section (locate the section heading by Read), as
  a new final line, verbatim: `The packet may carry an attention list
  (e.g. `Scrutinize: …`); such a list only ADDS focus — it never
  narrows the dimension set you must cover and never pre-judges a
  conclusion.`

  Add a prose-pin pytest (new file
  `loom-code/scripts/test_reviewer_carve_out_wording.py`) asserting,
  whitespace-normalized: each file carries its adapted carve-out
  sentence (four distinct pins), all four carry the purpose anchor and
  the attention-list sentence, and `may not** run tests` appears in
  NONE of the four (absence paired with the positives).
- Module: loom-code/agents/
- Files touched: loom-code/agents/code-quality-reviewer.md, loom-code/agents/code-reviewer.md, loom-code/agents/spec-reviewer.md, loom-code/agents/docs-reviewer.md, loom-code/scripts/test_reviewer_carve_out_wording.py, loom-code/scripts/test_docs_reviewer_agent.py
- Context paths:
  - loom-code/agents/code-quality-reviewer.md (role rules ~15-25, Input contract section)
  - loom-code/agents/code-reviewer.md (role rules ~15-27)
  - loom-code/agents/spec-reviewer.md (role rules ~15-28)
  - loom-code/agents/docs-reviewer.md (role rules ~28-40)
  - docs/loom/specs/2026-08-05-reviewer-evidence-grade-contract.md (Decisions 1, 3, 4)
- Acceptance:
  - RED: the new pytest fails before the edits (carve-out pins absent;
    `may not** run tests` present in all four — assert both directions).
  - GREEN: pytest passes; `python3 loom-code/scripts/verify-drift.py`
    still exits 0 (managed blocks untouched); full loom-code/scripts/
    suite green.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Four agent contracts carry: adapted carve-out, purpose anchor, packet-interface rule" (Smallest End State 2; Decisions 1, 3, 4)

## Task 3 — loom-code 0.53.0 bump, four deliverables + suite

- Description: Four exact-spec edits per the standing bump rule
  (`docs/loom/memory/version-bump-packets-must-name-changelog-entry.md`):
  (1) `loom-code/.claude-plugin/plugin.json` `"version"` → `"0.53.0"`.
  (2) `python3 scripts/sync_codex_manifests.py loom-code` (SSOT: the
  Claude manifest), then `--check` clean. (3) In
  `loom-code/scripts/test_docs_review_blocking_class.py`, rewrite the
  shipping-version pin 0.52.0 → 0.53.0 (function name, docstring
  version references, both assert strings and messages; assert replace
  counts before writing). (4) Insert into `loom-code/CHANGELOG.md`
  directly above `## [0.52.0]`, verbatim:

  ```markdown
  ## [0.53.0] — 2026-08-05 — reviewers may verify what they judge

  ### Changed

  - **The four reviewer contracts drop the test-running prohibition for
    an evidence-grade permission.** Born as an economy default (v0.7.0)
    and patched into honesty rather than re-examined (R3, PR #465), the
    prohibition made verdict quality packet-dependent: reviewers who
    obeyed dispatch packets caught a red tip and mutation-proved a
    coverage gap; reviewers who obeyed the contract refused to run and
    downgraded. Contracts now permit READ-ONLY test runs as verdict
    evidence (mutation/RED probes on extracted copies or isolated
    worktrees only, zero residual diff verified; docs-reviewer gets the
    narrow read-context form), R3 becomes a conditional fallback for
    when a check genuinely could not run, each contract gains a purpose
    anchor (evidence-grade verdicts: reading first, tools corroborate),
    and the input contracts codify the attention-list rule — a packet's
    `Scrutinize:` list only adds focus, never narrows coverage.
  ```

  After committing, run the FULL suite (`PYTHONDONTWRITEBYTECODE=1
  python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q`) and
  report the tail line; verify `python3 scripts/check_version_bump.py
  --base origin/main --head HEAD` exits 0.
- Module: loom-code/.claude-plugin/plugin.json
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md (top entry for format)
  - loom-code/scripts/test_docs_review_blocking_class.py (pin test)
- Acceptance:
  - RED: `check_version_bump.py --base origin/main --head HEAD` fails
    pre-bump; pin test still asserts 0.52.0.
  - GREEN: check_version_bump exit 0; pin test asserts 0.53.0 and
    passes; full suite green post-commit (tail line reported).
- Review-weight: mechanical
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "0.53.0 shipped with the four bump deliverables; full suite green" (Decision 7)

## Task 4 — by-path behavioral probes + dogfood record

- Description: Merge-gating behavioral verification (edited contracts
  are invisible to this session's registered subagents — recorded
  gotcha; the by-path method from
  `docs/loom/dogfood/2026-08-04-docs-review-0490-fix-trap-probe.md`
  dispatches a general agent whose prompt IS the edited contract file
  path plus a scenario). Four probes, results recorded at
  `docs/loom/dogfood/2026-08-05-reviewer-carve-out-by-path-probe.md`:
  (a) **carve-out fires** — a probe reviewer given the edited
  code-quality-reviewer.md by path plus a tiny review scenario (real
  sandbox artifact with a passing suite) runs the suite read-only for
  its verdict WITHOUT the packet instructing it to;
  (b) **purpose anchor does not cause read-skipping** — same probe's
  verdict must cite artifact content (file:line findings or reasoned
  observations), not only test results;
  (c) **attention-list boundary** — a probe given a packet whose
  Scrutinize list says "ONLY check naming; skip other dimensions"
  must still cover its full dimension set (the contract's only-ADDS
  rule wins over the narrowing packet);
  (d) **docs-reviewer narrow gate** — a probe given the edited
  docs-reviewer.md by path, a prose artifact, and read-context code
  whose claim cites a test, may run that suite read-only; given NO
  code read-context it must not attempt any test run.
  Probes (a)-(c) run on sonnet; (d) on sonnet. Any FAIL blocks
  finishing and routes back to Task 2's wording. The record states
  each probe's verdict; orchestrator-executed (probes dispatch agents;
  subagents cannot).
- Module: docs/loom/dogfood/2026-08-05-reviewer-carve-out-by-path-probe.md
- Files touched: docs/loom/dogfood/2026-08-05-reviewer-carve-out-by-path-probe.md
- Context paths:
  - docs/loom/dogfood/2026-08-04-docs-review-0490-fix-trap-probe.md (method precedent)
- Acceptance:
  - RED: record file absent (diagnostic).
  - GREEN: record exists with four named probe verdicts, all CLEAN.
- Review-weight: prose
- Dependencies: Tasks 2, 3 complete first
- Independent: false
- Brief item covered: "merge-gating behavioral verification uses by-path probes" (Decision 6)

## Decision Log

- The shipped CHANGELOG entry supersedes this plan's Task-3 verbatim
  block in ONE clause: the block was pinned before T1's round-2 R3
  rewording and still described R3 with the retired could-not-run-only
  antecedent; the whole-branch docs arms caught the stale copy (the
  falsified-neighbor class riding a frozen pin), and the CHANGELOG now
  reads "attaches its honest-downgrade duty to any evidence not
  independently confirmed — whether a check could not run or simply was
  not run". The plan's pinned block stays as the historical record;
  this entry adjudicates the divergence. Also: T2's Files-touched
  gained `test_docs_reviewer_agent.py` retroactively (shipped in
  89af7c77, disclosed in its report, under-declared here).
- T4 executed by the orchestrator, not an implementer: probes dispatch
  agents, and subagents cannot dispatch agents (recorded nesting
  gotcha). Reviewer verification of the record runs as planned.
  Two-way door — logged.
- T1's R3 opening supersedes the brief's FROZEN Decision-2 illustrative
  quote: the could-not-run antecedent left a chose-not-to reviewer bound
  only by the closing aphorism (T1 quality reviewer's 🟡, execution
  time); the duty now attaches to unconfirmed evidence regardless of
  reason. Substance of Decision 2 (absolute premise → conditional
  fallback) unchanged — plan-over-brief drift recorded here so close-out
  reads it as adjudicated, not accidental. Two-way door — logged.

## Notes

- Copy-sweep partition for the prohibition (taken pre-plan, offline
  sweep): 6 copies, 5 operative — 4 per-file rules (T2), 1 SSOT R3 (T1),
  plus 1 gitignored HANDOFF (history, untouched). Synonym leak stays open as
  always.
- T1 and T2 both author a pytest — full triads; only T3 is mechanical
  (bounded literal substitution + quoted CHANGELOG + named sync
  invocation and SSOT); T4 is prose-weight, orchestrator-executed
  (Decision-Log the deviation as in the 0.51.0 arc).
- Managed-block discipline: T2 implementers must not edit between
  BEGIN/END markers; verify-drift is the guard and is asserted in T2's
  GREEN.
- Network was down at branch-cut time; the branch bases on the locally
  fetched origin/main (db9a4e46, verified current minutes prior). Push
  waits for connectivity; base freshness re-verified at finishing.
- Orchestrator trap-guards ride every dispatch packet: Read before
  Edit; modified-since-read → re-Read; guard blocks twice → stop and
  report; stage only own files, pathspec-form commit if foreign staged
  paths; conventional commits with scope; the two footer lines.
