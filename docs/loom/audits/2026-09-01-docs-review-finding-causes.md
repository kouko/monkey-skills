# 四專案 docs-review 缺陷成因證據文件

**Date**: 2026-09-01
**Scope**: consolidates finding-cause mining across four projects —
monkey-skills, kumiko-zaiku-app-icons, dotfiles, youtube-summarize-scraper
(yss) — that motivated the "prose-edit self-sweep" brief
(`docs/loom/specs/2026-08-31-prose-edit-self-sweep.md`). This document does
not itself measure or claim any effect of that brief's rule; it only
records the pre-existing finding-cause distribution the brief cites as
motivation.

## Method

**Sources**:
- monkey-skills: `docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md`
  (14 classified 🟡 findings from 6 merged-PR docs-review verdicts; already
  committed in this repo, not re-copied here — see that file for the
  original per-finding text and load-bearing classification).
- kumiko-zaiku-app-icons: session-scratchpad mining of 5 Claude session
  transcripts, `findings-kumiko.md` (52 findings, appendix §A.1).
- dotfiles: session-scratchpad mining of PR bodies + `code-reviewer`
  panel output (`requesting-docs-review` was never dispatched in this
  project — see Limits), `findings-dotfiles.md` (16 findings, appendix §A.2).
- youtube-summarize-scraper: session-scratchpad mining of git log + `gh pr
  view` bodies (the literal `docs-reviewer` schema never appears in this
  project's transcripts either — see Limits), `findings-yss.md` (22
  findings, appendix §A.3).

The three scratchpad source files die with the authoring session; their
finding tables are reproduced verbatim in the Appendix so this document is
the durable record.

**Dedup rule**: each source file applies its own dedup method (stated in
its own Limits section, reproduced in the appendix) — task-id dedup for
kumiko (background-agent re-fire keeps the longest result text per
task-id), same-claim-across-rounds folding for dotfiles and yss (a finding
re-raised as "still open" in a later round is counted once; a fix that
births a NEW distinct false claim is counted as a separate row). This
document does not re-dedup across projects — the four counts are kept
project-scoped, not merged into one global count, because each project's
mining method differs (live reviewer transcript vs PR-body/diff inference)
and merging would hide that grain difference.

**A–K cause taxonomy** (as used consistently across the three scratchpad
files and the monkey-skills sample; one-line definitions):

| Code | Definition |
|---|---|
| A | Stale-neighbour: one passage/claim was edited or added; a sibling passage that should agree with it (heading, other file, cross-reference) was not updated and now contradicts it. |
| B | False claim about the writer's own work: a count, measurement, or status statement ("verified", "N left", "harmless") is wrong when checked against the actual artifact/output. |
| C | Placement / reading-path defect: content is misplaced relative to how a reader or tool actually parses/reads the document (dangling "see below", markdown swallowing a paragraph, a fix placed inside a skip-marked block, a missing table delimiter). |
| D | Unexecutable instruction: an instruction cannot actually be carried out as written (no matching schema slot, a mechanism that doesn't exist). |
| E | Omission: a decision, goal, or audience is left unstated where the document's own purpose requires it. |
| F | Omission: alternatives or rationale for a choice are missing. |
| G | Omission: a risk, verification step, or recovery/timeout path is missing. |
| H | Unsupported claim: a citation resolves to real text but that text does not actually support the claim, or a claim has no grounding at all. |
| I | Open question left without a stated reason when its own re-trigger condition was met. |
| J | Ambiguity of wording, or a direct self-contradiction inside one paragraph/clause. |
| K | Other — does not fit A–J cleanly (each source file states its own rationale where used). |

## Cause distribution

Every count below was recomputed from the appendix rows' own `Cause`
column (Appendix §A.1–§A.3) plus a fresh per-row cause assignment for the
monkey-skills sample (§Recount notes) — not transcribed from the mining
sessions' own summary tables, which in two cases (kumiko H-count,
dotfiles B/K split, yss K-count) undercounted or overcounted relative to
a direct row-by-row count. See "Recount notes" below the table for the
specific discrepancies found and corrected.

| Cause | monkey-skills | kumiko | dotfiles | yss |
|---|---|---|---|---|
| A | 4 | 23 | 0 | 3 |
| B | 4 | 6 | 9 | 2 |
| C | 3 | 4 | 0 | 0 |
| D | 1 | 0 | 0 | 2 |
| E | 0 | 0 | 0 | 8 |
| F | 0 | 2 | 0 | 0 |
| G | 0 | 1 | 0 | 2 |
| H | 0 | 11 | 3 | 3 |
| I | 0 | 1 | 0 | 0 |
| J | 2 | 3 | 0 | 1 |
| K | 0 | 1 | 4 | 1 |
| **Project total** | **14** | **52** | **16** | **22** |

Grand total across all four projects: **104 findings**.

### Recount notes (what changed vs. the mining session's own summaries)

- **kumiko**: a direct row-by-row count of all 52 rows in Appendix §A.1
  gives A=23, B=6, C=4, F=2, G=1, H=11, I=1, J=3, K=1 (D=0, E=0), summing
  to 52. The scratchpad's own "§2 Cause-category x count" table (not
  reproduced here) stated A=22 and H=9, summing to only 51 — one row
  short of its own stated total of 52. This document uses the row-level
  recount (A=23, H=11), which is internally consistent (sums to 52).
- **dotfiles**: a direct row-by-row count of all 16 rows in Appendix §A.2
  gives B=9, H=3, K=4 (all other codes 0), summing to 16. The scratchpad's
  own summary table stated B=8 and K=5 — its K-count named only 4 rows
  (#5, #11, #13, #14) while claiming a count of 5. This document uses the
  row-level recount (B=9, K=4).
- **yss**: a direct row-by-row count of all 22 rows in Appendix §A.3 gives
  E=8, A=3, B=2, D=2, G=2, H=3, J=1, K=1, summing to 22. The scratchpad's
  own summary table stated K=2, listing row #18 and "row #7 alt-read not
  used" as its two K instances — but row #7's own `Cause` column value is
  `A`, not `K`; the "alt-read" mention is commentary, not a second cause
  assignment. This document counts each row's stated `Cause` column value
  once (K=1, from row #18 only), which is the only assignment consistent
  with the stated total of 22.
- **monkey-skills**: the source audit (`2026-08-11-yellow-finding-...md`)
  classifies each of its 14 findings as load-bearing/reason but does not
  assign an A–K cause code (that taxonomy postdates it). This document
  assigns one A–K code per finding by reading each finding's own
  paraphrase in that source file against the definitions above:
  F1(D — unexecutable fold instruction), F2(B — false completeness
  claim), F3(A — doc's backlog-state claim vs. actual store),
  F4(C — heading positioned before required content), F5(B — implied
  verification that wasn't run), F6(A — clause tail not updated after
  clause tightened), F7(A — preamble falsified by a later addition in the
  same file), F8(C — fix placed inside a skip-marked block), F9(J — gate
  clause contradicts its own parenthetical), F10(J — splice changed what
  a template-copier would read), F11(C — placement rule would fold into
  the wrong field), F12(B — false "byte-preserved" provenance claim),
  F13(B — same defect, second quote), F14(A — two-word swap contradicts
  the branch's own stated condition). Tally: A=4, B=4, C=3, D=1, J=2,
  summing to 14. This is this document's own classification of an
  already-committed source, not a re-quote of the source's own words —
  flagged so a reader does not mistake it for the original audit's
  verdict.

## Rounds evidence

**kumiko — rounds per branch** (best-effort; task-notification proximity
to nearest preceding `gitBranch`, background dispatches interleave across
branches — see Limits):

| Branch | Docs-review rounds observed |
|---|---|
| docs/m1-container-re-examination | 8 |
| feat/m1-marukiwa-third-role | 6 |
| docs/progress-table-catchup | 6 |
| feat/loom-backlog-store | 6 |
| docs/oq6-narrow | 6 |
| feat/m1-part-3-svg-output | 5 |
| feat/m1-part-4-t1-t2 | 4 |
| feat/light-wood-colour | 4 |
| feat/non-circular-container | 4 |
| feat/m1-rim-thickness-parameter | 3 (+2 more in a different session file = 5 total across sessions) |
| feat/m1-part-2-panel | 2 (+2 in another session file = 4 total) |
| docs/pattern-size-look-dev | 2 |
| docs/shape-independent-sharpness | 2 |
| feat/light-wood-and-pattern-ratio-measurement | 2 |
| feat/per-slat-geometry-part-2 | 1 |
| docs/chirashi-forward-compat | 1 |
| feat/m1-part-2-container-2d | 1 |
| docs/memory-slicing-by-file-leaves-gaps | 1 |

Several branches (docs/m1-container-re-examination,
feat/m1-marukiwa-third-role) show NEEDS_REVISION → fix → NEEDS_REVISION
again on newly-introduced sibling-drift, rather than settling in round 2.

**dotfiles — PR#40 (claude-omlx alias) 10-round case**: 10 rounds, 2
reviewers/round, final verdict PASS. Rounds 1–3 found real code defects
(race condition, `pgrep | head -1`, untested branches — not prose).
Rounds 4–10 found ONLY prose defects (a `.zshrc` alias comment,
cause-B/H throughout — see Appendix §A.2 rows #6–#12): each fix planting
the next false claim, until the fix pattern shifted from correcting facts
to removing all checkable facts from the comment entirely. This is the
single most-rounds case across all four projects' mining and the
concrete instance the brief cites for "rounds 4–10 prose-only."

## Limits

- **monkey-skills**: the 14-finding sample is itself explicitly thin
  (N=6 verdicts out of 55 merged PRs, selection-biased toward findings
  narrated in enough PR-body detail to classify — stated in the source
  audit's own Limits). This document's A–K cause assignment for those 14
  is a fresh classification against a taxonomy the source audit predates
  (see Recount notes) — not the source audit's own labels.
- **kumiko**: extraction is non-exhaustive. 74 distinct task-notification
  blocks matched the docs-reviewer shape; only ~40 had a recoverable
  Findings section in the captured extract (the rest were bare
  PASS/PASS_WITH_NOTES verdicts, or the result text was truncated by the
  extraction script's 2500-char cap per block, cutting off items 5+ in
  several blocks). The true finding count in this project's history is
  higher than the 52 tabulated. Branch attribution (the rounds table
  above) is approximate — background dispatches interleave across
  branches in these transcripts and are matched to the nearest preceding
  `gitBranch` field by line proximity, not a verified causal link.
- **dotfiles**: `loom-code:docs-reviewer` / `requesting-docs-review` was
  **never actually dispatched** in this project's history (zero
  `agentType:"loom-code:docs-reviewer"` metadata across 27 sessions; zero
  invocation-marker matches; no docs-reviewer vocabulary in any of 43 PR
  bodies). Every finding in Appendix §A.2 instead comes from
  `loom-code:code-reviewer` (`requesting-code-review`) reviewing branches
  that happened to mix code + prose — so the `class: instruction|evidence`
  column is not recoverable (n/a throughout) and the five-dimension
  omission/ambiguity/inconsistency/incorrect-fact/missing-population
  rubric was never applied to this project's docs; cause-code assignment
  is this document's own mapping of code-reviewer's findings onto the
  A–K taxonomy, not the reviewer's own labels. Only 5 of 27 sessions were
  opened in depth; low-keyword-hit sessions were not opened individually
  and could contain an unmatched docs-reviewer dispatch this pass missed
  (plausible but unconfirmed).
- **yss**: the literal `docs-reviewer` structured schema never appears in
  any of 146 session transcripts either — most likely because this
  project's `.md` changes are always committed alongside `.go` changes in
  the same PR, so `requesting-docs-review`'s "every changed file is
  `.md`" gate never trips. The 16 spec-review findings (rows #1–16) are
  **diff-inferred, not verbatim reviewer quotes**: they predate loom
  (March 2026, pre-rename), no session transcript from that period is
  retained, and they were reconstructed from fix-commit itemized lists
  cross-checked against before/after spec diffs — severity/class are
  marked "none"/"unknown" rather than guessed. The 6 loom-era code-review
  findings (rows #17–22) carry an inferred `class` (based on whether the
  finding blocked merge), because PR bodies quote severity but not the
  internal `class` field.
- **Cross-project comparability**: the four projects' evidence grain
  differs by construction (kumiko = live reviewer transcript output;
  monkey-skills = PR-body narration of reviewer transcripts; dotfiles and
  yss = no true docs-reviewer output at all, substituted with the nearest
  available analog). The grand total (104) and per-cause counts should be
  read as four independently-mined, non-commensurable samples juxtaposed
  in one table, not as a single unified count from one measurement
  method.

## Consumers

- `loom-code/agents/implementer.md` rule 14 ("Prose-edit self-sweep") —
  the brief that motivates this document (`docs/loom/specs/2026-08-31-
  prose-edit-self-sweep.md`) cites this cause distribution (edit-
  consistency causes A/B/H/C dominating over omission-class E/F/G/I in
  three of the four projects) as the reason the rule's five actions
  target restatement-checking, self-claim verification, reading-path
  walk, and instruction-schema checking rather than an omission
  checklist. This document does not measure rule 14's effect — it
  predates the rule and records only the pre-existing distribution.
- The A/B protocol under `docs/loom/dogfood/2026-08-31-prose-selfsweep-ab/`
  — its historical case selection and its `cause` field values (the
  closed A–K set validated by `prose_selfsweep_tally.py`) are grounded in
  the taxonomy defined in this document's Method section.

## Appendix — verbatim scratchpad tables

Reproduced verbatim from the session scratchpad (paths as authored; these
files die with the session, so this appendix is the only durable copy).
monkey-skills' 14 findings are NOT reproduced here — see
`docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md` for
that source's own findings table.

### A.1 kumiko-zaiku-app-icons — `findings-kumiko.md` §1 Findings table

Columns: project | branch (best-effort, by nearest preceding `gitBranch`
in the transcript — session files interleave background dispatches, so
this is an approximation, not ground truth) | doc type | author | severity
| class | one-line paraphrase | cause. Quotes ≤1 line, translated/trimmed
where the original is Chinese prose.

| # | Branch | Doc type | Author | Sev | Class | Paraphrase | Cause |
|---|---|---|---|---|---|---|---|
| 1 | feat/m1-part-2-panel | decision log (decisions.md) | orchestrator session | 🟢 | evidence | design-log.md's own "四道守衛" count undercounts the function's actual 5 raise conditions | A |
| 2 | feat/m1-rim-thickness-parameter | spec/design-log (design-log.md) | orchestrator | 🟡 | instruction | a formula stated as a blanket fact about "地組" actually only holds for square lattices, not the triangular lattice asanoha uses — same file's own table says asanoha is triangular | A |
| 3 | feat/m1-rim-thickness-parameter | decisions.md | orchestrator | 🟡 | instruction | a charter-adjacent decision recorded only in a commit trailer + PURPOSE.md prose has no dated entry in decisions.md, though every other milestone decision gets one | A (decision made but not recorded in its canonical ledger) |
| 4 | feat/m1-rim-thickness-parameter | backlog item | orchestrator | 🟡 | instruction | new look-dev evidence directly investigates one of three knobs a backlog item calls inseparable, but neither file cross-references the other — orphaned backlog entry | A |
| 5 | docs/pattern-size-look-dev | measurement note (design-log.md) | orchestrator | 🟡 | instruction | headline claim ("no metric shows degradation") unscoped, but body documents a 32px metric that does degrade 24% — headline overclaims beyond what body supports | B |
| 6 | docs/pattern-size-look-dev | measurement note | orchestrator | 🟡 | instruction | a new 465KB look-dev image this commit adds is never referenced by path/filename anywhere in the note it presumably documents | A (orphaned artifact) |
| 7 | docs/pattern-size-look-dev | decisions.md trailer | orchestrator | 🟢 | evidence | cited principle (EP1, about not loosening geometric-invariant tests) doesn't quite match the scope of the claim it's cited to support | H |
| 8 | docs/shape-independent-sharpness | PURPOSE.md | orchestrator | 🟡 | instruction | one leg of a two-leg Done-when acceptance criterion requires leaving evidence; the sibling leg added this branch has no equivalent evidence requirement | G |
| 9 | docs/shape-independent-sharpness | PRINCIPLES.md Open Questions | orchestrator | 🟡 | instruction | branch produced exactly the evidence that was the stated re-trigger condition for two open questions, but neither question was touched/closed/deferred | I |
| 10 | docs/shape-independent-sharpness | backlog item | orchestrator | 🟡 | instruction | unchanged backlog file still asserts no 32px render exists; new evidence this branch added contradicts it | A |
| 11 | feat/m1-part-2-panel | plan (specs) | orchestrator | 🟡 | instruction | a plan merges two quantities the SSOT (design-log.md) explicitly separates and warns are "not the same quantity" | A |
| 12 | feat/m1-part-2-panel | PRINCIPLES.md / decisions.md | orchestrator | 🟡 | instruction | precedent citation points at "decisions.md revision 6," which doesn't exist — actual quote lives in a plan file under a different heading | H |
| 13 | feat/m1-part-2-panel | PRINCIPLES.md | orchestrator | 🟡 | instruction | claim "it must return False" is refuted by the entry's own re-trigger clause 40 characters later — a rotation-equivariant panel satisfies the entry's own definition yet the checker returns True | J |
| 14 | feat/m1-part-2-panel | plan | orchestrator | 🟡 | instruction | "existing error paths" inventory lists 5 conditions but cites 6 line ranges; one ValueError guard is omitted from the prose despite being in the cited range | A |
| 15 | docs/m1-container-re-examination | plan (Task retrofit) | implementer (SDD) | 🟡 | evidence | TDD Iron-Law breach: production code (a raise) written before its failing test; remediation later closes the gap but the sequence violation itself is recorded | K (process-compliance defect, not prose content) |
| 16 | docs/m1-container-re-examination | test comment | implementer | 🟡 | evidence | comment says "one vertex" outside the circle at a given epsilon; reviewer measured 18 vertices outside — number wrong, in the direction that weakens the underlying argument | B |
| 17 | docs/m1-container-re-examination | params.md | orchestrator | 🟡 | instruction | citation to "plan line 138" for a quoted requirement — the quote is actually at line 143; :138 points at an unrelated bullet | H |
| 18 | docs/m1-container-re-examination | params.md table | orchestrator | 🟡 | instruction | 19 new parameter rows appended without the required delimiter row — under GFM they're absorbed as blockquote continuation, not real table rows | C |
| 19 | docs/m1-container-re-examination | params.md | orchestrator | 🟡 | evidence | same statistic (a 17°-angle failure rate) published with two different denominators (3/4 vs 9/12) in two live documents, neither naming its sampling set | A |
| 20 | docs/m1-container-re-examination | decisions.md | orchestrator | 🟡 | evidence | decisions.md cites progress.md as recording a trigger condition; progress.md's actual text never contained that trigger — citation resolves but doesn't support | H |
| 21 | feat/m1-part-3-svg-output | plan (Part 3) | orchestrator | 🟡 | instruction | plan still instructs reader to settle two width constants by eyeballing a 32px render, though an earlier decision explicitly retired that plan | A |
| 22 | feat/m1-part-3-svg-output | decisions.md | orchestrator | 🟡 | instruction | an "Open Questions closed" entry never propagated to the charter (PRINCIPLES.md) — still lists the questions open, no version-bump entry | A |
| 23 | feat/m1-part-3-svg-output | params.md | orchestrator | 🟡 | instruction | 3 new public surfaces landed this branch with no row, violating params.md's own "every public parameter gets a row" rule | F (undocumented public surface, closest true rationale/coverage-omission hit) |
| 24 | feat/m1-part-3-svg-output | memory file | orchestrator | 🟡 | instruction | a memory-file citation claims a height assertion lives in contact_sheet.py; it actually lives in the test file — source module has no assertion at all | H |
| 25 | feat/m1-part-3-svg-output | memory file | orchestrator | 🟡 | evidence | rule says "two copies were left behind still using the old name"; reviewer found three | B |
| 26 | feat/m1-marukiwa-third-role | decisions.md | orchestrator | 🔴 | instruction | a rule reversal recorded in a new dated entry never propagated an in-place marker to the original entry, though the repo's own convention (used 4 times elsewhere) requires one | A |
| 27 | feat/m1-marukiwa-third-role | decisions.md | orchestrator | 🔴 | instruction | entry's central thesis ("zero repo-wide hits for a discussed direction") is false — reviewer's own grep found 2 on-point hits; the direction was scoped and excluded explicitly, not silently dropped | H |
| 28 | feat/m1-marukiwa-third-role | plan | orchestrator | 🟡 | instruction | a "this diagnosis is wrong" correction landed in one task of a plan but its verbatim copy 234 lines earlier in the same plan was never updated | A |
| 29 | feat/m1-marukiwa-third-role | decisions.md | orchestrator | 🔴 | instruction | entry says "harmless today — already subtracted in 2D, no-op" while a sibling module's own comment says the opposite | A |
| 30 | feat/m1-marukiwa-third-role | design-log.md | orchestrator | 🔴 | instruction | SSOT row still asserts a claim decisions.md explicitly calls false for one half of it — edited from 五種→四種 but false clause left standing | A |
| 31 | feat/m1-marukiwa-third-role | decisions.md | orchestrator | 🔴 | instruction | citation resolves but doesn't support: cited spec line answers a different question than the one the entry claims it pre-answers | H |
| 32 | feat/m1-marukiwa-third-role | memory file | orchestrator | 🔴 | evidence | a brand-new lesson file republishes a bare number (111) as a measurement two lines after quoting a different number (113) as "the same measurement" — and 111 is a number this same commit retires elsewhere as non-reproducible | B |
| 33 | feat/m1-marukiwa-third-role | plan | orchestrator | 🟡 | instruction | a markdown lazy-continuation bug (missing blank line after a blockquote) swallows the following paragraph into a reviewer-marker quote — same defect class a prior fix addressed 3 files over | C |
| 34 | feat/m1-marukiwa-third-role | plan | orchestrator | 🟡 | evidence | "67 only true at the branch's starting commit" is false — reviewer's sweep found 67 also holds at a second (docs-only) commit | B |
| 35 | feat/m1-marukiwa-third-role | plan + script | orchestrator | 🟡 | evidence | claim ".md prose is the majority of this repo's prose" is near-tautological under a narrow reading and false under the natural reading (42% / 46.8%) — no population named | H |
| 36 | feat/m1-rim-thickness-parameter | PRINCIPLES.md | orchestrator | 🟡 | instruction (defaulted) | an 18x ratio figure rests on one extreme configuration with no named population/rationale for that choice; a second real-world figure gives 4.4x instead | F |
| 37 | feat/m1-rim-thickness-parameter | PRINCIPLES.md | orchestrator | 🟡 | instruction | a number copied into the constitution when the SSOT file declares itself sole source and says "other docs cite, don't copy" | A |
| 38 | feat/m1-rim-thickness-parameter | PRINCIPLES.md | orchestrator | 🟡 | instruction | term "框厚" used ambiguously — two distinct objects share the plausible name, conflated as if comparable (102.4px crest ring vs 5.6px frame member) | J |
| 39 | feat/m1-rim-thickness-parameter | PRINCIPLES.md | orchestrator | 🟡 | instruction | a "Deviation Ledger" heading labels the deviation with the wrong object of a just-separated pair; decisions.md's copy has the identical error while its own body gets it right | A |
| 40 | feat/m1-rim-thickness-parameter | PRINCIPLES.md | orchestrator | 🟡 | instruction | a parenthetical "(width below)" points at nothing — the referenced value never appears later in the file | C |
| 41 | feat/m1-rim-thickness-parameter | PRINCIPLES.md | orchestrator | 🟡 | evidence | pixel conversions never state which of two documented container diameters (8 vs 8.25) they used, despite a same-day ruling requiring every conversion to name its diameter | H |
| 42 | docs/progress-table-catchup | decisions.md | orchestrator | 🟡 | instruction | entry says "d=8 is this project's reference diameter"; the value used everywhere executable (5 test files + 5 prior ledger entries + this branch's own brief) is 8.25 | H |
| 43 | docs/progress-table-catchup | decisions.md | orchestrator | 🟡 | instruction | a re-trigger clause names an unqualified constant but every listed condition is container-scoped; a sibling module already meets the (unlisted) condition and has documented it, uncross-referenced | A |
| 44 | docs/oq6-narrow | decisions.md | orchestrator | 🟡 | instruction | "Deviation Ledger" heading labels the deviation using the wrong side of a pair its own body just finished distinguishing; heading and body internally split | A |
| 45 | docs/oq6-narrow | PRINCIPLES.md | orchestrator | 🟡 | instruction | "見下" (see below) points at nothing — referenced value exists in the repo but is never linked to from this clause | C |
| 46 | docs/oq6-narrow | PRINCIPLES.md | orchestrator | 🟡 | evidence | pixel conversions state which diameter but not which rule requires that disclosure; a same-day rule requiring exactly this isn't followed | H |
| 47 | feat/loom-backlog-store | decisions.md | orchestrator | 🟡 | instruction (defaulted) | entry says a gate "faithfully implements" a check clause; three other sentences in the same entry say the clause is only half-mechanized — direct self-contradiction | J |
| 48 | feat/loom-backlog-store | decisions.md | orchestrator | 🟡 | instruction | citations use line numbers despite the same file's own explicit ban on line-number citations; one citation already drifted by 1 line within this branch | A |
| 49 | feat/loom-backlog-store | decisions.md | orchestrator | 🟡 | evidence | entry says "one row" was moved out of a section; plan Task title and brief both say "two rows," and the actual commit moved two | B |
| 50 | feat/m1-part-4-plan | plan | orchestrator | 🟡 | instruction | acceptance clause states a justification the same file twice records elsewhere as measured-false | A |
| 51 | feat/m1-part-4-plan | plan | orchestrator | 🟡 | instruction | "RED (four items)" list actually has five items, numbered out of order; GREEN section elsewhere correctly says "five" | A |
| 52 | feat/m1-part-4-plan | plan/spec | orchestrator | 🟡 | instruction | acceptance clause demands a since-corrected "extreme-only" framing be reproduced — the artifact it's grading was already fixed to use a range | A |

### A.2 dotfiles — `findings-dotfiles.md` §1 Findings table

All rows are `loom-code:code-reviewer` panel findings on prose/comment
content (never `docs-reviewer` — see Limits). "Round" = review round
within that branch's panel.

| # | Branch/PR | Doc type | Author | Severity | Class | Finding (paraphrase, <=1 quoted line) | Cause |
|---|---|---|---|---|---|---|---|
| 1 | PR#38 herdr gruvbox theme, round 1-2 | README.md (herdr) | orchestrator session | yellow | n/a (code-reviewer, no instr/evid tag) | Config-template prose written as tested fact; one instance directly disproved by running the command ("dark_name/light_name regardless of auto_switch is validated" -- reviewer ran it, refuting the doc's claim) | B |
| 2 | PR#38, same round, instance 2 | README.md | orchestrator | yellow | n/a | Second "template says X -> wrote X as happening" instance, same class | B |
| 3 | PR#38, instance 3 | README.md | orchestrator | yellow | n/a | Third instance, same class per PR body "four yellow all same defect kind" | B |
| 4 | PR#38, instance 4 | README.md | orchestrator | yellow | n/a | Fourth instance, same class | B |
| 5 | PR#36 theme follows system appearance, round 2 | ghostty/README.md + config comment | orchestrator | yellow (kept, not fixed -- recorded override) | n/a | Comment restates the mechanism the adjacent light:X,dark:Y config line already demonstrates -- not a contradiction, just redundant with a neighbouring passage | K (redundant-with-neighbour; closest fixed category is A but there is no contradiction, only restatement -- repo owner's deliberate no-fix) |
| 6 | PR#40 claude-omlx alias, round 4 | zsh/.zshrc alias comment (prose in code, not .md) | orchestrator | yellow | n/a | Comment claimed the -- argv-splitting happens in omlx/cli.py's launch subparser via os.execvpe; actual: splitting is in main() before argparse, execvpe never appears in cli.py | B |
| 7 | PR#40, round 5 | same .zshrc comment | orchestrator | yellow | n/a | Fix for #6 introduced a new unverifiable claim about ollama's env var handling on a closed-source binary with no way to check | H |
| 8 | PR#40, round 6 | same comment | orchestrator | yellow | n/a | "the other eight pass through untouched" -- wrong, two are actually overridden | B |
| 9 | PR#40, round 7, finding A | same comment | orchestrator | yellow | n/a | Comment said a fact "has been wrong twice"; reviewer traced git log -p and found it was wrong once -- the self-correcting sentence was itself false | B |
| 10 | PR#40, round 7, finding B | same comment | orchestrator | yellow | n/a | Comment claimed omlx start is idempotent; reviewer: the code only proves request/response shape, not the idempotency claim | H |
| 11 | PR#40, round 8 | comment + spec doc | orchestrator | yellow | n/a | Restructuring (moving checkable facts out of the comment into the spec) was incomplete -- a health-check relationship claim was still sitting unverified in the comment/tests, not migrated to the spec's Verified section | K (incomplete migration between neighbouring artifacts, spec vs comment) |
| 12 | PR#40, carried forward, unresolved | .zshrc comment | orchestrator | yellow | n/a | "auto mode asks the serving model to classify tool calls" -- a third-party mechanism claim with no grounding cite; verified true independently but left unfixed as accepted debt | H |
| 13 | fix/brewfile-stale-taps | README.md:273 | orchestrator | yellow | n/a | GitHub Repository link -- repo moved, link now 301-redirects to a different org | K (stale external fact/link; no exact taxonomy match) |
| 14 | fix/brewfile-stale-taps | README.md:271 | orchestrator | yellow | n/a | Install instructions reference the old sst/tap/opencode formula path instead of the renamed bare opencode | K (same stale-fact class as #13) |
| 15 | herdr-integrations branch | AGENTS.md | orchestrator | yellow | n/a | AGENTS.md claimed wiring checked for all four profiles but the test only exercises claude-test, never the other three | B |
| 16 | herdr-integrations branch | commit message ("other") | orchestrator | yellow | n/a | Commit message claimed "deleted two blocks" -- git diff showed otherwise | B |

### A.3 youtube-summarize-scraper — `findings-yss.md` §1 Findings table

| # | Project | PR/branch or date | Doc type | Author | Severity | Class | Paraphrase (≤1 line quote) | Cause |
|---|---|---|---|---|---|---|---|---|
| 1 | ytss | 2026-03-22, commit `ae1209b` (pre-loom "spec review") | spec | orchestrator session (kouko + Opus 4.6 co-author) | none (pre-loom, unscored) | unknown | "Clarify per-platform build process with directory layout" | E |
| 2 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Pin whisper.cpp binary name to `whisper-cli`" (was generic "`main` binary") | J |
| 3 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Define language detection mechanism via yt-dlp metadata" | E |
| 4 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Expand LLM interface to `SummarizeOptions`, specify stdin for CLI backends" — original `Summarize(text string)` couldn't support CLI backends without hitting OS arg-length limits | D |
| 5 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Add gemini_cli config fields (model, path)" — config block was `{}` | E |
| 6 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Define sequential processing model with timeouts" | G |
| 7 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Normalize language codes (BCP 47 → ISO 639-1) for whisper model lookup" — `summary.language` used BCP-47-style tags (`zh-Hant`) elsewhere, `language_models` keys used bare ISO 639-1 (`zh`), no stated mapping | A |
| 8 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Use glob pattern for skip detection resilience" — folder-existence check breaks on title-change/sanitization-logic changes | G |
| 9 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Specify WAV 16kHz audio format for whisper.cpp compatibility" — whisper.cpp rejects other formats, original spec was silent | D |
| 10 | ytss | `ae1209b` | spec | orchestrator | none | unknown | "Clarify default LLM behavior without config" | E |
| 11 | ytss | 2026-03-22, commit `4819db8` ("6 spec issues from end-to-end review") | spec | orchestrator | none | unknown | "ytss video/channel: auto-detect channel name from metadata" (output path was previously unstated for these two subcommands) | E |
| 12 | ytss | `4819db8` | spec | orchestrator | none | unknown | "Channel video fetching: yt-dlp --flat-playlist + filter config (types/min/max duration, per-channel override)" — whole fetch+filter mechanism and its config schema were absent | E |
| 13 | ytss | `4819db8` | spec | orchestrator | none | unknown | "Add obsidian config to main config example" — `obsidian:` block was documented in prose but missing from the canonical config example | A |
| 14 | ytss | `4819db8` | spec | orchestrator | none | unknown | "Stage 3 Mermaid prompt language follows summary.language" — spec stated this rule for Stage 1 but left Stage 3 silent, implying a different/undefined behavior | A |
| 15 | ytss | `4819db8` | spec | orchestrator | none | unknown | "Language-specific tier thresholds: CJK (500/3000/10000) vs English (1000/5000/15000)" — spec had one threshold set claimed universal, missed a stated info-density rationale for splitting them | E |
| 16 | ytss | `4819db8` | spec | orchestrator | none | unknown | "Mermaid placed after overview, before section summaries" — assembly order of frontmatter/summary/Mermaid was unstated | E |
| 17 | ytss | PR #64 (`b78cda4`, loom whole-branch review) | code (build script prose + Go) | implementer (SDD) | 🟡 | instruction (inferred) | "FORCE=1 overwrites yt-dlp in place via curl -o … a mid-download failure truncates the previously-good binary" | B |
| 18 | ytss | PR #64 | code | implementer | 🟢 nit ×2 (accepted debt, not gating) | evidence | "ffmpeg/whisper use `cp` not `mv` after a successful build" | K (low-severity consistency nit, left unfixed as accepted debt) |
| 19 | ytss | PR #63 (`eb23e61`) | code | implementer | 🟡 | instruction (inferred) | "escape set stopped at `\n\r\t`, leaving ~29 other C0 control chars + DEL unescaped" | H |
| 20 | ytss | PR #63 | code | implementer | 🟡 | evidence (inferred) | "tests under-sampled control chars" | H |
| 21 | ytss | PR #61 (`ebc1d85`) | code | implementer | 🟡 | instruction (inferred) | "DefaultConfig()-seeded 'default' openai-compat instance made the resolver's 'bare openai-compat with no default → error' contract unreachable" (yaml.v3 map-merge on Load()) | B |
| 22 | ytss | PR #46 | code | implementer | unstated (fixed, not gating language given) | unknown | "caught a missing `~`-expansion in `expandPaths()`, fixed under TDD" | H |
