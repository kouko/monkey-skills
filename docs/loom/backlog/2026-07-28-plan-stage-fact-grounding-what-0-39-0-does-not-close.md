---
name: 2026-07-28-plan-stage-fact-grounding-what-0-39-0-does-not-close
description: Plan-stage fact grounding — what 0.39.0 does NOT close
status: open
origin: whole-branch review of `feat-plan-fact-grounding` (loom-code 0.39.0), which held the branch to the standard the branch itself argues for. Findings 1-3 of that review plus the orchestrator's carried close-out list.
start: next time a planning-origin defect reaches close-out despite 0.39.0's contracts — or when the PCE entry above is first evaluated, whichever comes first. Each item below is independently actionable; do not treat the list as one unit of work.
---

- Start: next time a planning-origin defect reaches close-out despite 0.39.0's contracts —
  or when the PCE entry above is first evaluated, whichever comes first. Each item below is
  independently actionable; do not treat the list as one unit of work.
- Origin: whole-branch review of `feat-plan-fact-grounding` (loom-code 0.39.0), which held
  the branch to the standard the branch itself argues for. Findings 1-3 of that review plus
  the orchestrator's carried close-out list.
- What:
  1. **The preventive half of the citation rule is unenforced.**
     `writing-plans/references/plan-format.md:169` ("Any verifiable technical assertion in a
     plan carries a `file:line` citation…") requires a citation on every verifiable
     assertion, but no plan-document-reviewer check verifies compliance. Reviewer item 7
     is by design a no-op when no citation is present.
     - **Evidence corrected 2026-08-03.** This item originally read "the checks table stays
       at 16 rows" and cited the append-only pin's constant as `= 16`. Check 17
       (`Reuse-adequacy`) shipped as an authorized append, so the table's maximum and
       `loom-code/scripts/test_plan_obligation_sweep.py:78`'s pin both now read 17
       (constant at `test_plan_obligation_sweep.py:42`). **The conclusion is unchanged** —
       no check verifies citation compliance, and Check 17 grades a different obligation
       (reuse declarations, not citations). Only the row count that was offered as proof
       had gone stale. Corrected while completing the §8 candidate backtest
       (`docs/loom/audits/2026-08-03-remediation-candidate-status-and-live-population.md`).
     Net effect: 0.39.0 catches a **cited** false fact (measured — see the dogfood note's
     §Re-run) and misses an **uncited** one, which is the cheaper authoring path and the
     shape of the audit's own §3.8 instance ("15 fields" asserted three times where
     the code says 14). Fix is either **a new check — the next free number is 18**, Check 17
     having shipped as `Reuse-adequacy` (see the correction above) — plus amending the pin,
     or an explicit decision to accept the residual. Do NOT reuse or renumber 17:
     `docs/loom/memory/retire-numbered-checks-dont-renumber.md` forbids it, and this
     prescription said "Check 17" until 2026-08-03, when the number it named was taken by
     something else. Branch-local evidence that author-side discipline does not
     self-hold: five citation inaccuracies in this branch's own commits, the fifth inside the
     section documenting the citation fixes.
  2. **The acceptance-criteria family is untouched.** Candidate check, append-only numbering:
     *acceptance criteria must be executable by the actor bound to satisfy them.* Origin:
     Task 7's GREEN required `check_version_bump.py`, which reads committed blobs, while the
     implementer is forbidden from committing. It survived all three plan-review rounds — the
     rounds asked whether the criteria were correct, never whether the bound actor could run
     them. Two further instances in the audit's §3.8 (a RED naming filers with no data; a RED
     contradicting the brief on DUK) sit in this family.
  3. **`file:line` citations drift under parallel edits.** Four measured instances on this
     branch (`:365`→`:372` from a concurrent insertion, `:41` vs `:40`, `:32-39` vs `:34-39`,
     a path missing its directory). The T1 rule should prefer an anchor that survives
     insertion, and date any bare line number it keeps.
     - **DETECTION (mechanised, 0.40.0).** The `loom-code/scripts/check_doc_citations.py`
       script (default mode: path:line bounds with unique-suffix fallback) now verifies every
       `` `path:line` `` and `` `path:line-range` `` citation in the docs/loom corpus. Measured
       on the committed corpus: **0% false positive, 8/8 true positives on the line-exceeds-bounds class**; the documented content-drift instances (bounds-valid, content-wrong) are NOT detectable by this check — see `docs/loom/dogfood/2026-07-28-citation-check-corpus-run.md` §3a.
     - **PREVENTION (open).** Durable anchors over bare line numbers remain unimplemented.
     - **§N-anchor detection (experimental, implemented behind the flag but not invoked by the
       review mode).** The `--sections` flag detects §N references resolving to numbered
       headings (§N / §N.M in the cited file). Zero true positives on the corpus to date.
       **Escalation to default: re-measured at 0.42.4 and ruled out** — not awaiting a
       threshold any more. See "Citation checking has no answer for anchor-only documents
       (OPEN)" at the end of this file for the numbers (≈85% of `§N` refs unresolvable,
       zero additional defects) and the re-derive-don't-cite rule that entry carries.
       Same corpus-run note, same section.
     - **Quoted-citation false positives (parser v1 limitation).** The default-mode check
       cannot distinguish a citation inside fenced code blocks, blockquotes, table cells, and inline examples — dogfood notes quoting
       tool output, deliberately-broken fixture examples — from a live citation; both are
       checked identically, producing false findings. 2/2 observed on this branch's own
       dogfood notes. Reviewers must treat pre-pass findings inside fenced code blocks, blockquotes, table cells, and inline examples as
       advisory, not as defects (see `requesting-docs-review/SKILL.md:54` — this caveat lived
       at `requesting-code-review/SKILL.md:97` until loom-code 0.46.0 moved it; that line is
       now blank; further copies of the stale pointer survive outside this entry and are
       filed at `docs/loom/backlog/2026-08-03-stale-requesting-code-review-97-pointers-outside-this-branch.md`,
       which lists them by path and deliberately states no total — it is itself inside the
       corpus a sweep for that pointer walks).
  4. ~~**`Reuse-adequacy` is declarative-only.** Nothing enforces that a task carrying a reuse
     instruction fills the field.~~ **CLOSED 2026-08-03** — Check 17 (v0.43.0+) grades the
     block in four parts, the first being **presence**: a task whose Description instructs
     reuse of an existing helper on a new call path must carry the block. Shipped via
     `docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md`; the SHIPPED
     backlog entry is `2026-07-27-reuse-adequacy-got-the-gate-it-had-been-missing.md`.
     Left struck rather than deleted so the remaining open items keep their numbering.
  5. **Implementer test counts are not reproducible.** Two implementers reported "437 passed";
     no scope reproduces it. The reproducible ones, each with the command that yields it:
     `python3 -m pytest loom-code/scripts/ -q` → 363 at the time of that report, and
     `python3 -m pytest loom-code/scripts/ loom-pipeline/scripts/ -q` → 581. Both are dated
     figures, not standing ones — re-run the command rather than citing the number. A count
     that cannot be reproduced is not a verification claim.
     Candidate fix: require the dispatch packet's `Resolved test command` to be echoed
     verbatim in the report beside the count.
  6. **The drift-boundary clause lands at one tier only.** Measured before/after on the same
     fixture: sonnet went from silently absorbing a stale pointer (while asserting the source
     said it at that location) to detecting, classifying and recording it; haiku went from
     naming the drift to papering it over with an invented `:180-182` range. Verdicts stayed
     correct in all four cells and no false alarm appeared, so the clause ships — but the two
     haiku runs contradict each other, so run-to-run variance at that tier exceeds the effect
     at n=1. Do not describe the clause as working at both tiers.
     Evidence: `docs/loom/dogfood/2026-07-27-plan-fact-grounding-coldread.md`.
  7. **Next amendment to reviewer item 7 must split it, not extend it.** Three amendments were
     concatenated into one ~200-word numbered list item (~6× its sibling contract items).
     Split into labelled sub-bullets — action / consequence / boundary — before adding a
     fourth. A long run-on read by the weakest tier is the shape this repo's standing finding
     says fails.
  8. **`loom-code/scripts/test_writing_plans_readme_sync.py:51-52` uses `str.index`** — raises
     `ValueError` on a missing anchor instead of a readable assertion failure. 🟢
  9. **The two cross-read guard test files are ~45% identical.** Defensible under this repo's
     SSOT-and-functional-copy convention and the two genuinely different verdict models;
     next-touch only. 🟢
  10. **Shipped with a known defect of its own, stated rather than fixed.** The
      entry titled "investing-toolkit arc defect-provenance audit — internal inconsistencies
      need reconciliation" still opens by saying the audit "makes four internally
      inconsistent claims" while its item 4 is struck WITHDRAWN and its own §Why it matters
      concludes that items 1-3 are the live ones. The audit's erratum says 三處; this
      entry's header is the stale copy — withdrawing item 4 did not re-measure the tally
      that counts it.
      - **Why it is shipped rather than corrected**: this is the self-referential class
        described in `docs/loom/memory/a-passage-that-describes-itself-decays-on-every-edit.md`,
        and every close-out round that fixed an instance of it wrote a fresh one into
        whatever surface the fix touched — a wrong file citation, an invalidated pointer set,
        a stale shift magnitude, a wrong positional descriptor, a wrong instance tally, a
        round count sitting between its own abstention and its own prohibition. The
        terminal-round rule set before that round's verdict was: another instance of this
        class gets recorded, not rewritten. Round after round of moving one clause is evidence that
        this prose surface is not driven clean by iteration, and that evidence is worth more
        shipped than hidden behind a seventh edit.
      - **Fix when the reconciliation runs**: correcting the audit's three live
        inconsistencies and re-deriving this entry's header tally is one task, not two. Do
        not fix the tally alone — that re-creates the same decoupling in the other direction.
  11. **`writing-plans/SKILL.md` is at its hard word cap.** This change pushed it over
      CHK-SKL-010's 4,500-word ceiling (CI caught it at 4,571); rationale prose was trimmed
      to bring it back under, and it now sits a handful of words below the cap. The next
      addition to that file **cannot be an append** — it must extract an existing section to
      `references/` and link it, or trade words out. Note the extraction hazards already
      recorded in this store: `extract-to-reference-load-bearing-rule` and
      `extraction-severing-cross-ref-needs-weak-model-test` (a strong-model equivalence gate
      passes while a weak model drops the severed link, so extraction needs a weak-model
      cold read). The file is also far above the repo's ~3,750-word soft target, which is a
      standing condition of this skill rather than something this change introduced.
  12. **Release obligations are invisible to every plan check.** This branch's plan passed
      14/14 with no version-bump task; the omission produced a live wrong version token in a
      shipped annotation (item 3's 0.39.0/0.40.0 finding above). Check 8 sweeps the brief;
      nothing sweeps repo conventions. Candidate: a standing release-obligations note in
      writing-plans, or an append-only reviewer check.
  13. **A gating obligation stated in a task Description binds nothing.** T3's "stop before
      Task 4 ships the dependency" lived in prose; the Dependencies field did not encode it;
      parallel marking let T4 commit first. Second consequence: the pre-pass population
      caveat later folded into what was then `requesting-code-review/SKILL.md:97`, now
      `requesting-docs-review/SKILL.md:54` (the 0% false-positive
      figure's scope) reached that file only at whole-branch review, not during the branch's
      own plan-driven tasks. Candidate: plan-format rule — a Description sentence that gates
      ANOTHER task must be encoded as a Dependencies edge or it does not exist.
