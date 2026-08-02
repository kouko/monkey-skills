# Plan: reviewer findings carry a quote-gated origin

Source brief: docs/loom/specs/2026-08-02-finding-origin-attribution.md
Total tasks: 10
Critical-path depth: 5 (≤5) — Task 1 → 2 → 3 → 5 → 6; Task 4 is a depth-3 leaf.
The Task 7-10 re-cut adds a second chain, Task 7 → 8 → 10 (depth 3), with
Task 9 an independent depth-1 leaf feeding Task 10's dependency; neither
exceeds the depth-5 critical path above.
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-08-02, round 4) — 15/15, no gaps,
for Tasks 1-6 only; supersedes the round-3 PASS that the round-3-note
amendment made stale. Tasks 7-10 (the ledger-first re-cut below) were added
after that round and have not been through a plan-review round of their own —
adding tasks is outside `writing-plans`' no-re-review list (see the Round-3
amendment note below for the precedent this follows).

## Notes

- **Round-1 re-cut.** The plan-document-reviewer's first round falsified this
  plan's premise, not merely its wording: the previous version shipped the
  contract on `code-quality-reviewer` because that agent caught the arc's
  eighth-site defect — but per-task review **mints no marker**, so the chosen
  enforcement point never sees its output. The brief's §Smallest End State was
  re-cut before this plan was rewritten; both now name `code-reviewer` as the
  marker-validated agent and state the per-task asymmetry explicitly. Three
  further round-1 gaps (shared-validator blast radius, sha-unavailable-at-
  validation, `requesting-code-review` §Verdict structure being the
  whole-branch schema) are addressed by Tasks 1, 2 and 5 respectively.

- **Round-2 fixes (2026-08-02), applied before this round-3 dispatch.** Four
  gaps and two advisory notes, all closed in this document rather than in a
  dispatch packet (a packet is ephemeral; every later gate reads only this
  file). (a) Task 1's RED was already GREEN today — re-cut to the code-arm case
  that fails now, with the docs-arm case kept as a *named* GREEN regression
  assertion so its discriminating power is not lost. (b) Task 2's RED was
  **unconstructible**: it posited a quote "present at HEAD but not at the
  reviewed sha", and there is no separate reviewed sha — re-cut to
  committed-content-vs-worktree, which fails today and passes only a `git show`
  implementation. (c) The dimension-gated requirement **failed open** — see
  §Pinned dimension partition's new fail-closed clause and Task 1's second named
  GREEN assertion. (d) A `head_sha` line citation was off by one (`:275` is
  `branch`), and its Intended slot repeated the wrong number as a *placement*
  instruction, which would have put the check between the two `_git` calls.
  Advisory 1 (Task 2's GREEN spanning two behaviours) is closed by naming a
  second RED, with the reason it stays one task written into that entry;
  advisory 2 (unreachable sha-unresolvable branch) is closed by pinning it to a
  helper-level unit test in GREEN.

  Fix (b) had a **wider blast radius than the finding named**: the same
  non-existent distinction was carried at eight sites — the brief's §Decision
  and §Resolved Questions 1, and this plan's §Pinned field grammar (which Tasks
  1, 3, 4 and 5 transcribe VERBATIM into shipped contracts), Task 2's title,
  Description, RED, GREEN and External surfaces. All eight are corrected;
  correcting only the two the reviewer pointed at would have shipped the wrong
  wording through the pin into three agent/skill files.

- **Round-3 amendment (2026-08-02) — the plan misstated a fact about its own
  target suite.** Round 3 returned PASS with a non-fatal note that the
  fail-closed clause's closing phrase — *"invisible to a suite whose fixtures
  all carry well-formed dimensions"* — reads as a claim that
  `test_loom_gate_markers.py`'s fixtures carry dimensions. They do not:
  independently measured, that file contains **zero** per-finding `dimension:`
  lines. Two consequences, both now written down rather than left for the
  implementer to hit: the clause is replaced by the measurement, and Task 1
  declares the fixture updates the fail-closed rule forces (every pre-existing
  finding fixture refuses to mint under it, and several tests assert a
  successful mint). Task 1's GREEN also gains the present-but-empty
  `dimension:` case, closing the one divergence round 3 flagged between the
  pin's "no *parseable* `dimension:`" and the naive "no `dimension:` line".

  Worth naming, because it is this arc's own subject matter: the phrase was a
  **plan fact that was wrong, actionable and silent** — introduced by the very
  edit that closed round 2's fail-open gap, and caught one stage before any code
  existed. The PASS it arrived with is superseded by this amendment (a change to
  a task's Description and GREEN is outside `writing-plans`' three-item
  no-re-review list), so the header returns to PENDING for round 4.

- **`Reuse-adequacy` `Observed` line citations below are as-of-authoring, not
  refreshed against this branch's own later edits to `loom_gate_markers.py`**
  — **this plan's own choice, recorded here; not an inherited convention.**
  `writing-plans/references/plan-format.md` §`Reuse-adequacy`
  (`loom-code/skills/writing-plans/references/plan-format.md:141-163`) records
  no refresh policy in either direction, and its `Observed` slot — "State, in
  the present tense, what the helper does **today**, about code that already
  exists" — if anything leans against the choice made here. Nothing mechanical
  enforces either reading: on a `path:line` citation `check_doc_citations.py`
  checks only that the line number falls within the target file's current
  length, never what stands at that line
  (`loom-code/scripts/check_doc_citations.py:229-233`). Its one lane that does
  read target content — `§N` anchor resolution — is opt-in behind `--sections`
  and marked experimental
  (`loom-code/scripts/check_doc_citations.py:88-95`). Fix (d) above corrected a
  citation that was wrong *at authoring time* (an off-by-one), which is a
  different thing from the line drift this branch's own implementation work
  causes afterward, and only the former is in scope for correction.

- **Change-folder binding: none, by recorded decision — not by a fresh skip.**
  Detection layer (ii) finds two non-archived folders
  (`docs/loom/2026-07-12-us-sec-primary-source-layer/`,
  `docs/loom/2026-07-19-8k-prose-kpi-intake/`), which would normally trigger
  the `>1 → ask` branch. The user's decision not to bind either is already
  recorded — carried forward from
  `docs/loom/plans/2026-08-01-backlog-one-entry-per-file.md` §Notes and
  independently corroborated by
  `docs/loom/backlog/2026-07-26-loom-docs-two-stale-change-folders-belong-to-shipped-arcs.md`,
  which records both as belonging to shipped arcs. A documented decision beats
  re-asking. `check_scenario_coverage.py` does not apply — the input is a
  brainstorming brief.

- **§Pinned field grammar** — Tasks 1, 3, 4 and 5 each write this into a
  different artifact. Transcribe **VERBATIM from this pin**, never from each
  other and never re-derived:

  ```
  origin: none
  origin: <path> :: "<verbatim quote from that file>"
  ```

  `none` is the only permitted no-quote value (brief §Resolved Questions 2).
  The quote is matched against **committed content**, never against the working
  tree (brief §Resolved Questions 1) — an uncommitted edit must not be able to
  satisfy the check. There is **no separate "reviewed sha"** to prefer over
  HEAD: `_cmd_review_pass` resolves exactly one sha, `head_sha` from
  `rev-parse HEAD`, and stamps it into the marker, so the committed content at
  that sha *is* the reviewed content. Any wording in a transcribed copy that
  contrasts "the reviewed commit" with "HEAD" is stale — see the brief's dated
  correction under §Resolved Questions 1.

- **§Pinned dimension partition** — the discriminator Task 1 branches on.
  Transcribe VERBATIM; do not re-derive from the agent files, and do not
  extend either set without re-reviewing this plan:

  ```
  code-arm  : security, architecture, correctness, naming, tests, refactoring,
              cross-task-coherence, external-surface-grounding,
              principles-conformance, deliberate-simplification
  docs-arm  : omission, ambiguity, inconsistency, incorrect-fact,
              missing-population
  ```

  Verified disjoint 2026-08-02. A finding carrying a code-arm dimension must
  carry `origin:`; a docs-arm dimension is untouched.

  **Fail closed on everything else — the requirement is the default, the
  docs-arm exemption is the branch.** A finding whose block carries no parseable
  `dimension:` line, or a `dimension:` value in neither set, is treated as
  **code-arm**: it refuses without `origin:`. This is not a detail — today
  `_finding_problems` never reads a per-finding `dimension:` at all (the
  module's only `dimension` reads are the `dimension_scores:` block-header
  check), so an implementation that grants the requirement only on a successful
  lookup into the code-arm set lets **every** unparseable finding escape it
  silently. Measured on the target suite 2026-08-02:
  `loom-code/scripts/test_loom_gate_markers.py` contains **zero** per-finding
  `dimension:` lines — every finding fixture in it *is* the unparseable case —
  so a fail-open implementation would leave the whole existing suite green while
  requiring `origin:` of nothing at all, and nothing in the suite would ever
  surface the hole. Write the exemption as the explicit branch
  (`dimension:` parses AND is in the docs-arm set → skip) rather than letting
  fail-closed emerge from a lookup happening to miss. Same shape as the `class:`
  precedent, verbatim: *"A finding whose class is unclear is tagged
  `instruction` (fail closed)"*
  (`loom-code/skills/requesting-docs-review/SKILL.md:55`).

- **Kickoff decision:** enforcement lands before prose. Tasks 1-2 ship before
  Tasks 3-5. Shipping the contract first would promise a field nothing
  enforces, which is the defect class this change exists to make countable.
  Hard dependency, not preference.

- **Kickoff decision:** the `validate` dry-run must fail loud, never silent.
  `validate` takes no `--repo`, so it cannot verify a quote. It must say so in
  its output. A silent pass there would be a fail-open on exactly the
  pre-flight path `requesting-code-review` Step 3 tells reviewers to use.

- **Kickoff decision:** the stop rule is pre-registered and must not be edited
  after data lands. Brief §Resolved Questions 3: accumulate ≥40 code-arm
  findings; all-`none` ⇒ delete the field; ≥1 human-confirmed true origin ⇒
  keep; the hit RATE is explicitly not the test (expected base rate ≈7%,
  measured n=14 on the 2026-08-02 arc).

- **Kickoff decision:** quote-match strictness → **two-stage, exact then
  normalised, recording which stage matched.** *(user, 2026-08-02, kickoff
  briefing; one-way-door escalation per `kickoff-briefing.md` §a — the repo has
  no `docs/loom/PRINCIPLES.md`, so §d's brief-everything default applied.)*
  Try byte-exact substring first; on a miss, retry under one **identical**
  normaliser applied to BOTH sides — NFC, collapse each run of whitespace to a
  single space, fold typographic quotes / dashes / non-breaking spaces to
  ASCII. The normaliser is **case-sensitive** and does **not** strip `**` or
  backticks; matching is scoped to the cited file's content, not widened. A
  quote that matches only after normalisation still mints, but the message
  records that it did. **Why the tier is recorded, not just the boolean:** the
  stop rule above is pre-registered and uneditable after data lands, so once 40
  findings accumulate there is otherwise no observable that separates "no
  quotable origins existed" from "the matcher rejected true ones" — the tier
  count is that observable, and it must be collected from the first finding or
  not at all. Byte-exact-only was rejected on a measured ground: this repo
  hard-wraps prose at 72-80 columns, so a truthful one-line quote of a
  multi-line passage fails it by construction. Industry grounding: two-stage
  exact→normalised is the shipped shape in arXiv 2605.16881 (95.2% of segments
  matched verbatim or after minor normalisation, and it is the only surveyed
  source that names the typographic-quote/dash class); scoping the search to
  the cited region rather than the whole file follows the shipped RAG validator
  surveyed in the same pass. **Reversal condition, observable:** if a red-team
  pass shows a quote with altered meaning (inserted or removed negation, a
  renamed identifier) passing the normaliser, drop to per-line byte-exact
  within the cited range. **Downgrade clause:** if recording the tier turns out
  to require threading a new return type through the mint path rather than a
  few lines, ship the matching rule alone and report the downgrade — the tiers
  are the measurement, the matching rule is the contract.

- **Kickoff decision:** `origin:` value escaping → **split on the FIRST ` :: `,
  and require the remainder to be a fully-quoted, non-empty quote.** *(agent —
  two-way door per `kickoff-briefing.md` §a; the user delegated brief §Resolved
  Questions 2, the field-grammar question, at message 19 of the 2026-08-02
  session: 「第 2、3 題你決定」.)* A path may not contain ` :: `; a quote may.
  So parse left-to-right on the first separator, then require the remainder to
  open and close with `"` — a quote containing an interior `"`, or containing
  ` :: ` itself, is accepted as its own content, and no escape character is
  introduced. The quote's interior must additionally be non-blank: `""` and
  `"   "` are refused. Rejected: adding a backslash-escape convention, which
  would put an escaping rule into three shipped contracts to buy a case
  reviewers can avoid by quoting a shorter span.

  **Amendment 2026-08-02, user decision — no length or width floor. The
  grammar rule is exactly the two lines above: split on the first ` :: `,
  require a fully-quoted, non-blank interior.** Transcribe THAT. There is no
  minimum size, and the absence is deliberate — five rounds of review
  established that no length-shaped rule can do the job this one was asked to
  do.

  **Why there is no floor.** The intent was real: a quote so short that anyone
  could write it without opening the cited document verifies against almost
  any file, and would enter the pre-registered ≥40 tally as a genuine origin.
  Four rules were tried — two whitespace tokens; characters in all-CJK runs;
  CJK letters within a run; display width ≥4 — and the fifth review measured
  what they actually bought. `origin: <any .md> :: "tion"` has display width
  exactly 4, clears the floor, and mints: **2581 of this repo's 2642 committed
  `.md` files contain it (97.7%)**. The value the floor refuses, `"e"`, is in
  99.8%. **The floor's measured benefit was 2.1 percentage points.**

  Raising the number does not rescue it. The best-document-frequency span at
  each width, measured over the same corpus: 4 → 97.7%, 6 → 84.4%, 8 → 61.7%,
  10 → 40.4%, 12 → 39.9%, 16 → 33.1%, 20 → 16.5% — and the tail is markdown
  table boilerplate, which no width threshold separates from prose. The
  failing thing is the **axis**, not the constant: length answers "how many
  columns", and the property being gated is "how surprising in this corpus".
  Those coincide for CJK and diverge by roughly 200× for Latin.

  **What the floor was never doing.** It was a screen, never the gate. The
  brief's stop rule (§Resolved Questions 3) keeps the field only when at least
  one non-`none` origin **survives a human check** — and `"tion"` does not
  survive one for a second. Shipping a rule that costs five review rounds to
  buy two percentage points, ahead of a human check that catches the whole
  class, is the wrong place to spend the branch.

  **What the five rounds did buy, and it is worth keeping.** This measured
  the display-width-≥4 rule (rule 4, since superseded — no floor ships; see
  below). The false-refusal side was measured clean: over 3000 real
  committed sentences per language, the refusal rate was **0.00% for
  English, Japanese and Chinese alike**, and at the single-token level
  English was refused MORE often (33.5%) than Japanese (10.1%) or Chinese
  (10.6%). The script
  discrimination this arc manufactured three times is gone — measured, not
  assumed. And the two-canonicalisation defect class is closed: the floor and
  the verifier were made to share one normaliser, an idempotence sweep over
  all 0x110000 codepoints found no separating input, and eight independent
  attacks on that seam held.

  **The successor, if one is wanted**: gate on **corpus selectivity** — refuse
  a quote that matches more than some fraction of the repo's documents — which
  is the axis the measurement points at, and whose threshold the
  document-frequency curve above can actually calibrate. That is a new
  mechanism and a new decision, not a sixth patch to this one; it belongs in
  its own brief. Filed at
  `docs/loom/backlog/2026-08-02-quote-informativeness-needs-corpus-selectivity-not-length.md`.

  **Reversal condition, observable:** if the ≥40 tally fills with quotes a
  human check rejects as uninformative — rather than with `none` — the screen
  was load-bearing after all, and the selectivity mechanism above becomes
  COMMITTED-NEXT rather than a backlog item.

  **History.** Four superseded rules, kept because the pattern is the lesson.
  (1) "Two whitespace-separated tokens" refused **every** Chinese and Japanese
  quote — CJK prose has no inter-word spaces. (2) "Count characters when a run
  is entirely CJK letters" still refused ~75% of them, because CJK prose is
  dense with `。`, `、`, `：`, `「」`. (3) "Count CJK letters within a run"
  refused `push再` while passing `push 再` — same content, decided by a space —
  and shipped a hole with it: the decomposed spelling of `が` counted 2 and
  cleared a 2-unit floor, so a one-character quote passed the check built to
  stop one-character quotes. (4) Display width ≥4 closed all of that, then
  fell to `"e   "` — the rejected `"e"` plus three spaces — which measured 4
  because grammar counted spaces the verifier collapses away.

  Rules 1-3 each answered "where does a token end?", a question Unicode
  (UAX #29: default word segmentation "is not adequate" for Chinese and
  Japanese), the linguistics (a lone Han character is frequently a bound
  morpheme), and Japan's own national corpus (BCCWJ annotates every sample
  twice, 短単位 and 長単位; Sudachi ships three modes) all decline to answer
  with one number. Rules 3 and 4 each failed the same second way: two
  canonicalisations, one gate. Superseded corpus figures from those attempts
  are **not** reproducible and must not be re-cited — their units were never
  stated, and this file has since absorbed the examples it measured.
- **Kickoff decision:** in-flight branches at the version boundary → **hard
  cutover, no grace period.** *(agent — two-way door per §a.)* A verdict
  written by a 0.44.0 reviewer carries no `origin:` and will refuse to mint
  under the 0.45.0 validator; the remedy is to re-run the review, which is a
  bounded, already-supported action. Rejected: a warn-only grace window, which
  is a fail-open on the enforcement path for as long as it lasts and would need
  its own removal task. Implementers do not need to handle this; it is recorded
  so the first person to hit the refusal recognises it as expected rather than
  as a bug.

- **Format-fix skip note (no re-review).** The three kickoff decisions above
  this round's additions were written `**Kickoff decision — …**`; SDD's
  dispatch step reads the literal key `Kickoff decision:`
  (`subagent-driven-development/SKILL.md:73`), so they would not have ridden
  any implementer packet. Repunctuated to carry the key. Formatting only, no
  field's assertion changed — `writing-plans` §Amending a PASS plan, kind 2.

- **No CI file is edited.** `loom-code-ci.yml:98` already runs
  `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v` and its
  `paths:` filter covers `loom-code/**` and `scripts/**` (verified round 1).

## Task 1 — Require `origin:` on code-arm findings only

- Description: Extend `_finding_problems` in `loom_gate_markers.py` so every
  finding block must carry an `origin:` line valued either `none` or
  `<path> :: "<quote>"`, **except** a block whose `dimension:` both parses and
  falls in the docs-arm set, which is untouched. Write it in that direction —
  requirement first, exemption as the explicit branch — so a block with an
  absent or unrecognised `dimension:` refuses rather than escaping (§Pinned
  dimension partition, fail-closed clause). Grammar only: the quote is not yet
  checked against any file (Task 2). Transcribe both pins VERBATIM.
  **Declared collateral — not incidental drift.** No finding fixture in
  `test_loom_gate_markers.py` carries a `dimension:` line today (measured
  2026-08-02: zero occurrences in the file), so under the fail-closed rule every
  pre-existing fixture refuses to mint and every test asserting a successful
  mint goes red. Updating those fixtures — give each one a code-arm `dimension:`
  and an `origin:`, keeping each test's original intent — is part of this task,
  and the file is already in `Files touched` for exactly this reason.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py
  - loom-code/scripts/test_loom_gate_markers.py
  - loom-code/skills/requesting-docs-review/SKILL.md
- Acceptance:
  - RED: `loom-code/scripts/test_loom_gate_markers.py::test_code_arm_finding_without_origin_refuses_to_mint` — a verdict whose finding carries a code-arm `dimension:` (`correctness`) and no `origin:` line must fail validation. This fails **today**: no `origin:` requirement exists, so that verdict validates clean and mints.
  - GREEN: `origin: none` and `origin: docs/loom/plans/x.md :: "seven call sites"` both validate; a bare path with no quote and a quote with no path both refuse; `python3 -m pytest loom-code/scripts/` passes. Two assertions inside GREEN are **named, and each is load-bearing on its own**:
    - `test_docs_arm_finding_without_origin_still_mints` — a verdict whose findings all carry docs-arm dimensions and no `origin:` must still validate. This is the discriminating case against over-reach: a naive **global** requirement satisfies every other criterion in this task and fails only this one, and shipping it would block every docs-only and mixed-branch push.
    - `test_finding_with_unparseable_dimension_refuses_without_origin` — three cases must **each** refuse without `origin:`: a finding block carrying no `dimension:` line at all, one carrying a value in neither pinned set, and one carrying a `dimension:` key with an empty or whitespace-only value. This is the discriminating case against under-reach (§Pinned dimension partition, fail-closed clause): an implementation that requires `origin:` only on a successful code-arm lookup passes every other criterion here and fails only this one. The third case is what keeps "no *parseable* `dimension:`" (the pin's wording) and "no `dimension:` line" (the naive reading) from diverging — a present-but-empty key must not read as a docs-arm exemption.
    - Pre-existing fixtures updated per the Description's declared collateral, each keeping its original assertion intent, and `python3 -m pytest loom-code/scripts/` green with them.
- External surfaces: none — stdlib `re`, matching the module's existing imports.
- Reuse-adequacy:
  - Observed: `_finding_problems` already splits the verdict into per-finding blocks and requires a path-like `where:` in each, refusing to mint otherwise — `read loom-code/scripts/loom_gate_markers.py:224-247`
  - Observed (blast radius): the docs arm mints the SAME marker through the same validator — `read loom-code/skills/requesting-docs-review/SKILL.md:56`
  - Observed (precedent): a per-finding field scoped by arm already ships, annotated inline — `read loom-code/skills/requesting-code-review/SKILL.md:151`
  - Intended: reuse the per-finding block split and the refuse-to-mint path unchanged; the `where:` check's **unconditional** shape does NOT carry over — `origin:` must carry an exemption branch keyed on the finding's own `dimension:` value, or it breaks every docs-only and mixed branch. Note the asymmetry with `where:`: because `where:`'s requirement is unconditional, its parse cannot fail open, whereas `origin:`'s can — so the exemption must be what the code tests for, never the requirement (§Pinned dimension partition, fail-closed clause).
- Dependencies: none
- Independent: false
- Brief item covered: "A finding carrying a code-arm dimension must carry `origin:`; one carrying a docs-arm dimension is untouched."

## Task 2 — Verify the quote against committed content, and say so when you cannot

- Description: Add quote verification as a distinct step in `_cmd_review_pass`,
  **after** `head_sha` resolves — not inside `validate_verdict_text`, which
  runs before the sha exists and is also reachable from a subcommand that has
  no repo. For each finding whose `origin:` names a path and quote, read that
  path **out of the commit** (`git show <head_sha>:<path>`), never off disk, and
  refuse to mint unless the quote occurs, naming path, sha and quote in the
  message. Distinguish "file absent at that sha" from "sha unresolvable" — the
  current git helper collapses both to `None`. On the `validate` dry-run path,
  state in the output that quote verification did not run.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py
  - loom-code/scripts/test_loom_gate_markers.py
- Acceptance:
  - RED: `loom-code/scripts/test_loom_gate_markers.py::test_origin_quote_present_only_in_worktree_refuses_to_mint` — a temp repo whose **committed** content at `head_sha` lacks the quoted sentence while the on-disk file contains it must refuse to mint. This is the discriminating case: it fails today (nothing verifies quotes), it still fails a `Path.read_text()` implementation, and it passes only a `git show`-based one.
  - RED (second entry point, same contract): `loom-code/scripts/test_loom_gate_markers.py::test_validate_dry_run_reports_quote_verification_did_not_run` — `validate --verdict-file <f>` on a verdict carrying a quoted `origin:` must print that quote verification did not run. Fails today: the subcommand is silent about it. **Why this stays inside Task 2 rather than becoming its own task**: the `validate` path has no `--repo`, so its only behaviour here is announcing the absence of the check the mint path performs — it is meaningless before that check exists and therefore cannot precede it; and splitting it out would place it on the enforcement-before-prose chain (§Notes kickoff decision), pushing critical-path depth from 5 to 6. Two entry points into one fail-loud contract, one module, one implementer move.
  - GREEN: a quote present in the committed content at `head_sha` mints; quote-absent-at-sha and file-absent-at-sha each refuse with **distinct** messages naming path, sha and quote; `origin: none` skips verification entirely; the `validate` dry-run does not silently pass; `python3 -m pytest loom-code/scripts/` passes. The **sha-unresolvable** refusal is exercised by a direct unit test on the new helper, **not** through `_cmd_review_pass` — on the integrated path the existing `if branch is None or head_sha is None` guard returns 2 before the check is reached, so that branch is unreachable end-to-end and an integration test for it would be untestable-by-construction rather than merely absent.
- External surfaces: `git` CLI via `subprocess` — already the module's mechanism, no new dependency. Use `git show <head_sha>:<path>`; reading the worktree is wrong by construction (brief §Resolved Questions 1).
- Reuse-adequacy:
  - Observed: `_git` shells out and returns `None` on ANY failure, discarding stderr — `read loom-code/scripts/loom_gate_markers.py:90-103`
  - Observed: `_cmd_review_pass` validates at `:257` and only resolves `head_sha` at `:276` (`:275` resolves `branch`, not the sha) — the sha does not exist when validation runs — `read loom-code/scripts/loom_gate_markers.py:257-279`
  - Observed: the `validate` subcommand registers only `--verdict-file` and `--suite-line`; it has no repo and no HEAD — `read loom-code/scripts/loom_gate_markers.py:468-470`
  - Intended: reuse `_git`'s subprocess mechanism, but NOT its collapse-to-`None` contract — Task 2's GREEN needs "file absent at sha" and "sha unresolvable" to be distinguishable, so this call site must inspect the failure rather than inherit `None`. Reuse of `_cmd_review_pass`'s ordering does not carry over either: place the check **after the `if branch is None or head_sha is None` guard at `:277-279`** — i.e. at the first point where `head_sha` is known non-`None` — never alongside the `:257` validation, and never between the two `_git` calls at `:275-276`, where `head_sha` is not yet bound.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "It runs as a distinct step in `_cmd_review_pass` after the sha resolves; the `validate` path reports loudly that quote verification did not run"

## Task 3 — Add the field to the code-reviewer contract

- Description: Add `origin:` to the finding schema in
  `loom-code/agents/code-reviewer.md` (schema block at `:346-350`) and state
  the quote gate as an action the reviewer performs, not a judgment it makes:
  name the upstream artifact ONLY when you can quote the wrong statement
  verbatim; otherwise write `none`. State explicitly that `none` carries no
  penalty — the field records what the reviewer holds, not what it can infer.
  Transcribe the grammar VERBATIM from §Pinned field grammar.
- Module: loom-code/agents/code-reviewer.md
- Files touched: loom-code/agents/code-reviewer.md, loom-code/scripts/test_finding_origin_attribution.py
- Context paths:
  - loom-code/agents/code-reviewer.md
  - loom-code/agents/docs-reviewer.md
  - docs/loom/specs/2026-08-02-finding-origin-attribution.md
- Acceptance:
  - RED: `loom-code/scripts/test_finding_origin_attribution.py::test_code_reviewer_schema_carries_origin_and_the_quote_gate` — asserts the finding schema names `origin:` AND that the surrounding text states both the verbatim-quote requirement and the no-penalty `none` fallback; fails against the current file.
  - GREEN: the assertions hold, the schema block's existing fields are unchanged, and `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none — prose edit plus a grep-window test.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "`code-reviewer` (whole-branch) is the agent whose output the marker validates."

## Task 4 — Add the field to the per-task reviewer, and state that it is unenforced

- Description: Add the same `origin:` field to
  `loom-code/agents/code-quality-reviewer.md` (schema block at `:339-343`),
  and state the asymmetry in the contract itself: per-task verdicts never
  reach `loom_gate_markers.py`, so this field is emitted but **not**
  marker-enforced here. Writing that down is the point — a reader who assumes
  symmetric enforcement would be wrong in exactly the way this plan's own
  round-1 premise was wrong. Transcribe the grammar VERBATIM from §Pinned
  field grammar.
- Module: loom-code/agents/code-quality-reviewer.md
- Files touched: loom-code/agents/code-quality-reviewer.md, loom-code/scripts/test_finding_origin_attribution.py
- Context paths:
  - loom-code/agents/code-quality-reviewer.md
  - loom-code/agents/code-reviewer.md
- Acceptance:
  - RED: `loom-code/scripts/test_finding_origin_attribution.py::test_code_quality_reviewer_states_origin_is_not_marker_enforced` — asserts the agent names `origin:` AND says per-task verdicts are not marker-enforced; fails against the current file.
  - GREEN: both assertions hold and `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "`code-quality-reviewer` (per-task) emits the same field, and is **not** marker-enforced … That asymmetry is written into the contract."

## Task 5 — Mirror the field into the whole-branch verdict structure

- Description: Add `origin:` to §Verdict structure in
  `loom-code/skills/requesting-code-review/SKILL.md` — the block that mirrors
  `code-reviewer`'s schema (confirmed by its `cross-task-coherence` and
  `principles-conformance` entries, which the per-task agent's block does not
  carry). Point at the agent for the quote-gate rule rather than restating it;
  a second copy of the rule is a second source of truth. Annotate the scoping
  inline, following the `class:` precedent at `:151`.
- Module: loom-code/skills/requesting-code-review/SKILL.md
- Files touched: loom-code/skills/requesting-code-review/SKILL.md, loom-code/scripts/test_finding_origin_attribution.py
- Context paths:
  - loom-code/skills/requesting-code-review/SKILL.md
  - loom-code/agents/code-reviewer.md
- Acceptance:
  - RED: `loom-code/scripts/test_finding_origin_attribution.py::test_review_skill_verdict_structure_names_origin_without_restating_the_rule` — asserts §Verdict structure names `origin:` and does NOT restate the quote-gate rule in full; fails against the current file.
  - GREEN: both assertions hold and `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "Enforcement is scoped by dimension family, not applied globally. … This follows the existing arm-scoping precedent for `class:` (`requesting-code-review/SKILL.md:151`)."

## Task 6 — Bump the plugin and record the change

- Description: Bump `loom-code` from 0.44.0 to 0.45.0 (a new required field on
  a shipped contract is a behaviour change, not a fix), sync the Codex
  manifest by script, add the matching CHANGELOG entry, and rename the
  version-pin test that tracks the current shipping version by design. Do not
  hand-edit the Codex manifest — run
  `python3 scripts/sync_codex_manifests.py loom-code`.
- Module: loom-code/.claude-plugin/plugin.json
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md
  - loom-code/scripts/test_docs_review_blocking_class.py
  - scripts/check_version_bump.py
- Acceptance:
  - RED: `loom-code/scripts/test_docs_review_blocking_class.py::test_plugin_version_and_changelog_at_0_45_0` — the renamed pin asserts `"version": "0.45.0"` and a `## [0.45.0]` CHANGELOG heading; fails while the manifest reads 0.44.0.
  - GREEN: both manifests read 0.45.0, the CHANGELOG entry matches the file's existing shape, `python3 scripts/check_version_bump.py --base main --head HEAD` reports OK, and `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/` passes.
- External surfaces: none — `sync_codex_manifests.py` is an in-repo script.
- Dependencies: Task 5 completes first
- Independent: false
- Brief item covered: "enforced by `loom_gate_markers.py` in the same fail-closed way `where:` already is" — the shipped-content bump this repo's rule requires for any PR changing agent or skill content. Depends on Task 5 rather than Task 1 so the CHANGELOG describes the whole shipped contract, not just its enforcement half.

## Re-cut after Tasks 1-6: ledger-first, gate-second

> **User decision 2026-08-02, after two independent soundness reviews of the
> shipped Tasks 1-6.** The mechanism as built enforces and verifies, but never
> **collects**. Measured on this repo: **0 of 24** severity-🔴 findings ever
> reach quote verification, because `_cmd_review_pass` returns 3 on
> `NEEDS_REVISION` before verification runs and the aggregation rule sends every
> 🔴 there; **51.5%** of files changed across the last 40 merges are `.md`, which
> a mixed branch routes to the exempt docs arm; and the marker file that holds
> the only machine-readable output is overwritten every run, with the human
> record living in 30-day-rolling transcripts.
>
> The consequence is not a smaller sample but a **biased** one: the findings that
> survive to verification are those still present in a round carrying no 🔴 and
> at most one 🟡 — the nit tail. Plan-caused defects concentrate in the
> severities that force `NEEDS_REVISION`, are fixed, and vanish from the next
> round's text. The pre-registered stop rule reads an all-`none` result as
> "delete the field", and the sampling bias points exactly that way. A null
> result would be the sampling rule restating itself, not evidence about plans.
>
> **The binding constraint is persistence, not enforcement.** Both code-arm
> contracts already require `origin:` on every finding in every round, so the
> datum is produced everywhere; nothing keeps it. Tasks 7-10 therefore move the
> value from a mint-time refusal to a durable record, and demote the refusal.
> Tasks 1, 3, 4 and 5 are unchanged; Task 2's verification code is kept and its
> output redirected.

**Correction on the `51.5%` figure above.** It states no reproduction
method and a reviewer recomputing it over the last 40 merges got **53.1%**
(first-parent, 423/796 files) and **56.6%** (unique paths) — close enough
that the argument it supports (a mixed branch routinely has a `.md`
majority) survives, but the exact figure does not. Treat the number above
as illustrative, not a reproducible measurement.

**Population/method note (this is the canonical site for the `0 of 24`
figure; other mentions in this arc's docs cite here rather than restate
the bare number).** The 24 is a tally of severity-🔴 findings across this
arc's own Tasks 1-6 review rounds, made by the two soundness reviews named
above reading the round history as it happened. It is a **transcript
measurement, not a script or a corpus artifact committed to this repo** —
there is no re-runnable extractor for it the way
`docs/loom/dogfood/2026-08-02-transcript-corpus-feasibility-probe.md`'s
`probe_extract.py` re-runs the docs-side "24" (a different, unrelated
count — see that dogfood's §Oracle check: raw 24 / deduped 14 A-class
*docs-arm* findings on the 2026-08-02 day, not severity-🔴 findings from
this arc). The two numbers are the same digit by coincidence, not the same
population; neither this plan nor the spec derives one from the other.

- **Kickoff decision:** stop-rule start condition → **counting begins when the
  durable ledger holds code-arm entries, not at first mint.** *(agent, taken
  now because this is the last moment it is legitimately editable — the rule's
  own binding clause is "must not be edited **after data lands**", and no data
  has landed: the branch is unpushed, the marker is per-checkout, and nothing in
  the repo reads the field.)* Only the start condition changes. The threshold
  (≥40), the verdict (all-`none` ⇒ delete; ≥1 human-confirmed true origin ⇒
  keep) and the explicit refusal to judge on hit RATE are untouched.

- **Kickoff decision:** ledger file → **`<git-common-dir>/loom/origin-ledger.json`,
  separate from the parked `review-rounds.json`.** *(agent.)*
  `docs/loom/plans/2026-07-30-review-round-ledger-and-bad-fix-recheck.md:11`
  already specifies a branch-keyed, append-only, never-reset round ledger that
  explicitly covers the `NEEDS_REVISION` path. That plan is PARKED for reasons
  orthogonal to this arc, and implementing half of it here would both pre-empt
  its unpark and braid two arcs. A separate purpose-scoped file avoids that;
  whoever unparks the round ledger can merge the two, and this decision is the
  note telling them to.

## Task 7 — A durable origin ledger, written on every round

- Description: Extend `_cmd_review_pass` in `loom_gate_markers.py` so **every**
  invocation appends one entry to `<git-common-dir>/loom/origin-ledger.json` —
  including the `NEEDS_REVISION` path that currently returns 3 writing nothing,
  and including invocations whose verdict text fails schema validation only in
  ways that still leave findings parseable. The file is keyed by branch name,
  append-only, never reset. Each entry carries `round` (1-based per branch),
  `verdict`, `head_sha`, `written_at`, and a `findings` list; each finding
  carries `arm` (`code` | `docs`, derived from its `dimension:` against §Pinned
  dimension partition), `dimension` (raw, or `null` when unparseable),
  `origin_raw` (the value as written, or `null` when the line is absent) and
  `quote_status`. Recording is **never** allowed to change an exit code or block
  a mint: wrap the write so any failure is reported on stderr and swallowed.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py
  - loom-code/scripts/test_loom_gate_markers.py
  - docs/loom/plans/2026-07-30-review-round-ledger-and-bad-fix-recheck.md
- Acceptance:
  - RED: `loom-code/scripts/test_loom_gate_markers.py::test_origin_ledger_appends_on_a_needs_revision_round` — a `NEEDS_REVISION` invocation must still exit 3 AND leave one ledger entry recording its findings. Fails today: the early return writes nothing.
  - GREEN: a second invocation appends `round: 2` under the same branch without rewriting round 1; a different branch gets its own key; each finding's `arm` is derived from the pinned partition with an unparseable `dimension:` recorded as `null` arm `code` (fail closed, matching §Pinned dimension partition); `origin_raw` is the value verbatim, `null` when the field is absent; a ledger write failure (make the directory unwritable) prints to stderr, leaves the exit code and the marker unchanged, and is asserted; `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none — stdlib `json` and `pathlib`, both already imported by this module.
- Reuse-adequacy:
  - Observed: `_iter_findings` already segments a verdict into per-finding blocks and resolves `dimension`/`origin`/duplicate state, and both the validating lane and the extraction lane already go through it — `read loom-code/scripts/loom_gate_markers.py:488-550`
  - Observed: `_write_marker` writes JSON via `os.replace` to a fixed name, which is a whole-file overwrite — `read loom-code/scripts/loom_gate_markers.py:337-350`
  - Intended: reuse `_iter_findings` unchanged — it is the only segmentation and the ledger must agree with the gate about what a finding is. `_write_marker`'s overwrite semantics do NOT carry over: the ledger must read-modify-write to append, and its failure must be non-fatal where `_write_marker`'s is fatal.
- Dependencies: none
- Independent: false
- Brief item covered: re-cut above — "the binding constraint is persistence, not enforcement"; unblocks §Resolved Questions 3's tally, which the brief requires be "collected from the first finding or not at all".

## Task 8 — Verification records instead of refusing

- Description: Demote quote verification from a mint refusal to a recorded
  fact. A **grammar** problem (malformed `origin:` value, duplicate lines) still
  refuses. Grammar is not flawless either — two known false-refusal shapes are
  filed and left open at
  `docs/loom/backlog/2026-08-02-finding-block-field-scanner-false-refuses-on-indent-drift.md`
  — but they fail in the safe direction (over-refusal, never a fail-open
  escape), which is why grammar stays the one remaining mint-time refusal. A
  **quote that does not verify** — absent, file absent, not a file,
  undecodable, sha unresolvable
  — no longer returns 4; it is recorded in the ledger as
  `quote_status: unverified-<reason>` and the mint proceeds. A quote that
  verifies records `verified-exact` or `verified-normalised`; `origin: none`
  records `none`; an absent field on an exempt docs-arm finding records
  `absent`. Move the verification call ABOVE the `NEEDS_REVISION` return so it
  runs on every round.
- Module: loom-code/scripts/loom_gate_markers.py
- Files touched: loom-code/scripts/loom_gate_markers.py, loom-code/scripts/test_loom_gate_markers.py
- Context paths:
  - loom-code/scripts/loom_gate_markers.py
  - loom-code/scripts/test_loom_gate_markers.py
- Acceptance:
  - RED: `loom-code/scripts/test_loom_gate_markers.py::test_unverifiable_quote_records_and_still_mints` — a well-formed `origin:` whose quote is absent from the cited file must exit 0, write the marker, and leave a ledger entry with `quote_status: unverified-quote-absent`. Fails today: it exits 4 and writes nothing.
  - GREEN: a malformed `origin:` still exits 4 and writes no marker; the five unverifiable reasons are recorded distinctly; verification runs on a `NEEDS_REVISION` round and its results reach the ledger even though exit stays 3; the `validate` dry-run still states it could not verify; the previously-shipped `origin_quote_tiers` marker key is **removed** — the ledger supersedes it, and leaving both would restate the population-mismatch defect already filed; `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/` passes.
- External surfaces: none.
- Dependencies: Task 7 completes first
- Independent: false
- Brief item covered: re-cut above — "moves the value from a mint-time refusal to a durable record, and demotes the refusal"; removes a push-blocking check that, per the re-cut above, was blocking on exactly the tail of findings it could never see (0 of 24 severity-🔴 findings ever reached it). Not to be confused with the two false-refusal shapes filed at `docs/loom/backlog/2026-08-02-finding-block-field-scanner-false-refuses-on-indent-drift.md` — those belong to `_finding_problems`'s column-anchored field scanner (grammar/structure), which this task deliberately leaves refusing.

## Task 9 — The reviewer can reach the documents it is asked to quote

- Description: The `code-reviewer` dispatch packet carries the diff, rubrics,
  checklists and branch context — **no plan, brief or spec path**. The agent is
  asked to quote documents it was never handed, which predicts a near-total
  `none` yield for a reason that is the input contract rather than the idea.
  Fix it by **self-derivation**, copying the shape already used for
  `docs/loom/PRINCIPLES.md` (`code-reviewer.md` D8, "Activation is
  self-derived") rather than by passing paths: the orchestrator has no
  branch→plan resolution rule and plans are dated-and-slugged and plural, so
  packet-passing would require inventing one. State in the agent contract that
  the reviewer derives candidate upstream artifacts from `docs/loom/plans/` and
  `docs/loom/specs/`, and that finding none is an ordinary `none`, not a defect.
- Module: loom-code/agents/code-reviewer.md
- Files touched: loom-code/agents/code-reviewer.md, loom-code/scripts/test_finding_origin_attribution.py
- Context paths:
  - loom-code/agents/code-reviewer.md
  - loom-code/skills/requesting-code-review/SKILL.md
- Acceptance:
  - RED: `loom-code/scripts/test_finding_origin_attribution.py::test_code_reviewer_self_derives_upstream_artifacts` — asserts the contract tells the reviewer where to look for upstream planning artifacts and that finding none is not a defect; fails against the current file.
  - GREEN: the assertion holds as one contiguous ordered clause (the shape Tasks 3-5 landed, not keyword presence); the D8 self-derivation precedent is cited rather than re-derived; no dimension is asked to score against a plan; `python3 -m pytest loom-code/scripts/` passes.
- External surfaces: none.
- Dependencies: none
- Independent: true
- Brief item covered: re-cut above — without it the field's yield is governed by the input contract rather than by whether documents cause defects.

## Task 10 — Make the shipped record match the shipped mechanism

- Description: Rewrite the `## [0.45.0]` CHANGELOG entry to describe what
  actually ships after Tasks 7-9 — a recorded origin with a durable per-branch
  ledger, a grammar-only refusal, and no `origin_quote_tiers` marker key — and
  amend the brief's §Resolved Questions 3 to carry the corrected stop-rule start
  condition. The existing entry describes the pre-re-cut behaviour and would be
  a shipped false claim.
- Module: loom-code/CHANGELOG.md
- Files touched: loom-code/CHANGELOG.md, docs/loom/specs/2026-08-02-finding-origin-attribution.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md
  - docs/loom/specs/2026-08-02-finding-origin-attribution.md
- Acceptance:
  - RED: `loom-code/scripts/test_docs_review_blocking_class.py::test_changelog_0_45_0_describes_the_ledger_not_a_mint_refusal` — asserts the entry names the ledger and does NOT claim a quote failure refuses to mint; fails against the current entry.
  - GREEN: the entry matches the shipped behaviour clause by clause; no mention of `origin_quote_tiers`; the brief's start condition reads as amended; the version stays 0.45.0 (one unreleased bump covers the whole arc); `python3 scripts/check_version_bump.py --base main --head HEAD` reports OK; `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/` passes.
- External surfaces: none.
- Dependencies: Tasks 7, 8, 9 complete first
- Independent: false
- Brief item covered: re-cut above — a release note describing behaviour the release does not have is the defect class this arc exists to count.

## Decision Log

1. chose to make every field in a review finding count only when it sits in that finding's own column, including the one field that already worked the old way, because leaving two different rules inside one reader is worse than the flaw it fixes — cost-of-change: the day a reviewer writes a finding whose lines drift out of alignment, this choice costs them a blocked submission whose message names a missing field rather than the misalignment that hid it
2. chose to stop tightening the field reader after the blank-line case and to record the two remaining misalignment shapes as a known debt, because closing them requires the reader to guess the layout a person intended, and that guess would sit inside the very check whose job is to refuse whenever it is unsure — cost-of-change: the day those shapes become common, this choice costs a move to a real structured reader rather than one more patch
