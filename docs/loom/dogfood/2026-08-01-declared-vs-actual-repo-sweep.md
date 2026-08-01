# Dogfood — declared-vs-actual repo sweep (post-parser-fix)

- **Date**: 2026-08-01
- **Branch**: `docs-declared-vs-actual-measurement`
- **Comparator**: `scripts/check_files_touched.py` (post Tasks 6-7 fixes:
  `3b3970ac` continuation lines, `dfa1002e` annotation tails)
- **Complements**: `docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md`
  (frozen 10-cell corpus; this sweep is the wild-data counterpart)
- **RED (diagnostic)**: before authoring,
  `test -f docs/loom/dogfood/2026-08-01-declared-vs-actual-repo-sweep.md`
  exited 1 (observed this session).

## 1. Methodology

Run from the repo root (`/Users/kouko/GitHub/monkey-skills`):

```sh
for f in docs/loom/plans/*.md docs/plans/*.md; do
  python3 scripts/check_files_touched.py "$f" --repo .
done
```

169 plans under `docs/loom/plans/` + 1 under `docs/plans/` = 170 plans.
Exit contract: 0 all-OK (tolerates non-gating NO_JOIN rows while ≥1
join key exists) / 1 flagged, an unresolvable `done(<sha>)`, or — added
by the whole-branch review fix AFTER this sweep ran — ≥1 parse error on
an otherwise-clean run / 2 loud-empty (0 tasks or 0 join keys; wins
over 1) — `scripts/check_files_touched.py` `EXIT_CONTRACT`. The
distribution below was re-derived after that post-review amendment:
unchanged (the lone exit-0 plan has zero parse errors).

**Machine-local sha caveat**: `done(<sha>)` join keys resolve against
this machine's object store. Squash-merged branches' original commits
resolve only until `git gc` prunes them, and never existed on other
clones — the sweep is NOT CI-reproducible; treat every verdict below as
a this-machine, this-day measurement.

## 2. Exit-code distribution — pre-fix vs post-fix

| exit | pre-fix (orchestrator) | pre-fix (re-run) | post-fix |
|---|---|---|---|
| 0 | 1 | 1 | 1 |
| 1 | 4 | 4 | 4 |
| 2 | 165 | 165 | 165 |

- Pre-fix (orchestrator): recorded by the orchestrator before Tasks 6-7
  — provenance: orchestrator sweep, same session, pre-fix parser.
- Pre-fix (re-run): independently reproduced this session by running the
  pre-fix parser blob (`git show eedf33d3:scripts/check_files_touched.py`)
  from a scratch directory over the same loop. Matches the orchestrator
  record exactly.
- Post-fix: run this session with the fixed parser.

The plan-level distribution is unchanged: both fixed gaps produced extra
*false alarms inside already-flagged plans*, not extra flagged plans. All
movement is inside the plans — parse errors 204 → 25 sweep-wide, and
R2-UNDER task verdicts 27 → 16 on the ledgered plans (§3, §5).

Post-fix breakdown of the 165 × exit 2: 10 plans parse to 0 tasks (they
use other heading conventions than `## Task <N>` — none of the 10 is
letter-suffix-related, verified per plan), 155 parse tasks but carry 0
join keys.

## 3. Ledgered plans — per-plan verdicts, pre-fix vs post-fix

Ledgered = raw text contains a `Status: … done(<sha>)` line (grep over
the corpus): 6 plans.

| plan | exit | parse_errors pre→post | R2-UNDER tasks pre→post | post-fix per-task verdicts (R2) |
|---|---|---|---|---|
| 2026-07-11-investing-toolkit-data-consolidation | 1 | 3 → 0 | 3 → 1 | T1 UNDER; T2, T4 OK (T4 R1-only OVER, §5c) — parser sees 3 of 12 done tasks, §5b |
| 2026-07-25-kpi-id-injective-identity | 1 | 6 → 0 | 7 → 2 | T1-T4, T7 OK; T5, T6 UNDER (shared-commit cross-flags, §4) |
| 2026-07-25-company-total-revenue | 2 | 11 → 11 | 0 → 0 | none — all 11 `done(<sha>)` join keys dropped (status annotation tails, §5c), plan reads as "no ledger" |
| 2026-07-26-as-filed-statement-reconstruction | 1 | 11 → 0 | 11 → 8 | T1-T3 OK; T4-T11 UNDER |
| 2026-07-26-us-as-reported-statement-lane | 1 | 0 → 0 | 6 → 5 | T1-T4, T6 OK; T5, T7-T10 UNDER |
| 2026-08-01-declared-vs-actual-files-touched-check | 0 | 0 → 0 | 0 → 0 | T1-T7 OK; T8 NO_JOIN (this task — unledgered while this report is being written) |

Pre-fix parse-error class check: the orchestrator's recorded pre-fix
class — `token normalizes to nothing` on wrapped plans — counted 170
instances in the pre-fix re-run and **0** post-fix. The class
disappeared. Full class arithmetic (both sweeps re-run, classes
diffed): pre-fix 204 = 170 normalizes-to-nothing + 23
`line has no parseable value` + 11 Status annotation tails (§5c);
post-fix 25 = 8 no-parseable-value (Task 6 removed 15: the
no-value-plus-continuation shapes) + the same 11 Status tails + **6
NEW** `non-annotation tail after closing backtick` errors — paths that
pre-fix were silently CONTAMINATED with no error at all; Task 7 made
them loud (204 − 170 − 15 + 6 = 25 ✓). None on the four exit-1 plans
above.

## 4. TRUE wild under-declaration list (the load-bearing output)

Verification method: for every post-fix UNDER, the plan's actual task
block was opened and each flagged path checked against the `Files
touched` declaration *including continuation lines* (scripted substring
check over the extracted declaration, this session). Result: **all 16
flagged tasks' paths are genuinely absent from their declarations — zero
remaining parser artifacts among the post-fix UNDERs.**

The flags then split into two classes by *commit-level* reading (the
ledger allows several tasks to share one `done(<sha>)`):

**(a) Shared-commit cross-flags — 5 tasks, 0 undeclared paths.** Every
flagged path is declared by a *sibling task ledgering the same sha*; the
commit equals the union of the sibling declarations. Mechanically true
per-task, but not evidence of undeclared coupled state — a check-semantics
finding for the ship arc (a commit that discharges N tasks flags each
task on its siblings' files):

- kpi-id T5 + T6 (both `done(bd88c0cd)`): each flagged exactly on the
  other's declaration; commit = union.
- as-filed T4 + T5 + T6 (all `done(20607453)`): commit = exact union of
  the three declarations (6 files, verified via `git show`).

**(b) TRUE wild under-declarations — 11 tasks, 10 commits, 19 path
instances.** Path present in the commit, declared by NO task joined to
that commit:

| plan / task | sha | missed path(s) | coupling |
|---|---|---|---|
| 07-11 T1 | 91d80a8f | tests/test_skill_structure.py | repo-wide structural guard test updated alongside the new module (the cell-2 guard-test shape) |
| as-filed T7 + T11 | 5a898662 (shared) | kpi_equity_terms.py, test_kpi_equity_terms.py, kpi_us_statement_cells.py | an entire module + its test, declared NOWHERE in the plan (grep: 0 hits), plus a sibling-module source edit |
| as-filed T8 | 5a12dde0 | kpi_us_statement_shape.py, test_kpi_us_statement_shape.py | new source module + test created undeclared next to the declared check-module work |
| as-filed T9 | 1033e619 | skills/data-markets/SKILL.md | skill doc surface riding a code commit |
| as-filed T10 | 4142e444 | tests/data/fixtures/capture_ko_fy2017_income_as_filed.py | fixture-capture script landed beside the declared fixture JSON |
| us-lane T5 | 1840695e | kpi_us_statements.py, tests/data/test_sec_edgar_top_line_backfill.py | cross-module source edit + sibling guard test |
| us-lane T7 | dada7641 | docs/loom/BACKLOG.md | BACKLOG edit riding a feature commit |
| us-lane T8 | e54073a2 | scripts/pack.py, tests/data/test_pack_facade.py | facade registration seam + its guard test (registration shape) |
| us-lane T9 | a68df126 | kpi_us_statements.py, test_kpi_us_statements.py | sibling module + test co-edited |
| us-lane T10 | 051be100 | kpi_us_statements.py, kpi_us_statements_ingest.py, + both tests | 4 code files riding a docs/version-bump commit |

(Paths abbreviated to their tail under `investing-toolkit/`; full
spellings in the sweep output. "as-filed" =
2026-07-26-as-filed-statement-reconstruction, "us-lane" =
2026-07-26-us-as-reported-statement-lane.)

Every true instance lands in a known coupling family the source brief
predicted (guard tests, registration/SSOT seams, BACKLOG/doc edits,
sibling-module co-edits) — plus one family the frozen corpus did not
model: code riding a docs commit (us-lane T10, the reverse of the
doc-riding-code shape).

## 5. Parser-scope findings

**(a) The two fixed gaps — found only by wild data, both failed toward
false alarms.** The frozen 10-cell corpus (audit doc) shipped R3 clean;
neither gap was representable in single-line fixture declarations.
Wild plans wrap declarations (continuation lines, fixed `3b3970ac`) and
append post-PASS annotations (trailing parentheticals, fixed
`dfa1002e`). Cost while unfixed: 11 of the 27 pre-fix R2-UNDER tasks
were pure false alarms, spread over all four ledgered exit-1 plans
(as-filed T1-T3, kpi-id T1-T4/T7, 07-11 T2/T4, us-lane T1 — sums to
11), and surviving UNDER lists carried extra artifact paths.
Direction: false alarm — annoying, not dangerous.

**(b) NEWLY OBSERVED, still open — letter-suffixed task headings
(silent non-coverage, the dangerous direction).** `_TASK_HDR` matches
only `## Task <digits>`. Real plans use `## Task 3a` … `## Task 5b`
(e.g. `docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md`).
Quantified this session (`grep -E '^## Task [0-9]+[a-z]'` over the
corpus): **13 plans, 51 letter-suffixed task headings** the sweep never
sees. In the ledgered set the damage concentrates in 07-11: 12 tasks all
carry `done(…)`, the parser sees 3 — **9 completed, ledgered tasks
silently unswept**. Unlike (a), a missed task produces no output at all:
this is silent non-coverage, NOT a false alarm. Recommended as ship-arc
work. (Two of the 9 hidden tasks also use multi-sha
`done(fa65ef52+9a5fe56f)`-style values, outside the ledger vocabulary —
fixing the heading pattern alone would surface them as parse errors,
not verdicts.)

**(c) Also newly observed, still open (all loud, lower priority).**

- *Status annotation tails*: `- Status: done(<sha>)  # spec PASS …`
  fails the ledger vocabulary; in
  `2026-07-25-company-total-revenue.md` all 11 tasks carry such tails →
  0 join keys → a fully-ledgered plan exits 2 as "no ledger". Loud (11
  parse errors on stderr) but the plan is indistinguishable from the
  154 genuinely ledger-less plans in the same zero-join-key bucket at
  the exit-code level.
- *Nested-bullet declarations*: `- Files touched:` followed by indented
  `- <path>` sub-bullets (`2026-07-13-us-sec-narrative-memo-wiring.md`,
  8 tasks). The continuation rule excludes `- `-prefixed lines by
  design, so each errors loudly as "no parseable value".
- *Bare-token parenthetical tails*: `…test_cross_layer_chains.py (path
  refs only)` (07-11 T4) keeps its tail — documented behavior of the
  annotation fix (backticked tokens only). Here it surfaces only as a
  cosmetically dirty R1 OVER token; R2/R3 unaffected (the commit did
  not touch the file).

## 6. Weak-model consumption probe — deferred to the ship arc

The mechanism measured here is a deterministic script: parse, set
arithmetic, `git show`. No model tier participates in producing the
verdicts above, so a weak-model probe of the *mechanism* would measure
nothing. Tier only starts to matter at the consumption seam — whichever
agent (orchestrator, reviewer, or hook) reads the comparator's output
and must act on UNDER/NO_JOIN/exit-2 correctly — and that seam does not
exist until the ship arc decides the wiring (CI gate? SDD checkpoint?
finishing-branch step?). The probe is therefore deferred to the ship
arc, to be run against the chosen consumption point.

## 7. Selection caveats

- **Ledgered plans skew recent**: all 6 are 2026-07-11 or later; the
  `done(<sha>)` ledger convention postdates most of the corpus. The
  under-declaration rates above describe recent SDD practice, not the
  repo's history.
- **Sha resolvability is machine-local and gc-dependent** (§1): the 16
  UNDER verdicts and the 10-commit TRUE list depend on objects only
  this clone holds.
- **The 165 exit-2 plans exercise only the loud-empty path** (164
  ledger-less + one fully-ledgered plan whose 11 join keys the parser
  drops, §5c): exit 2 proves the comparator refuses an all-clear
  without a readable ledger, and nothing else about those plans.
  Coverage of the actual comparison logic comes from 6 plans (5 with
  joins post-fix).

## 8. Citation-checker output

`python3 loom-code/scripts/check_doc_citations.py docs/loom/dogfood/2026-08-01-declared-vs-actual-repo-sweep.md` (this session):

```
checked 0 / unchecked 0 / findings 0
OK: all citations resolve.
```

(exit 0; recorded verbatim, then the run repeated on the doc containing
this block — output identical. `checked 0` is the checker reporting its
own scope: this doc cites plain paths and shas, none of the anchored
citation shapes the checker verifies.)
