# Dogfood: `check_doc_citations.py` full-corpus run (P3 acceptance)

> **Round 2 amendment (2026-07-28, same day):** the resolver fix described in
> §Round 2 below was applied per the user's decision on Round 1's finding.
> Round 1's content below is preserved verbatim as the historical record —
> see **§Round 2: resolver fix + re-measurement** at the end of this file for
> the current numbers and verdict.

Command: `python3 loom-code/scripts/check_doc_citations.py docs/loom/audits/*.md
docs/loom/specs/*.md docs/loom/plans/*.md`, run against this branch's working
tree (`feat-docs-citation-check-and-review-mode`, 2026-07-28). Exit code: 1
(findings present).

**Verdict up front (see §5): the brief's ~10% false-positive reversal
condition TRIPS.** This note stops here per the plan's Task 3 instruction
rather than proceeding to wire the script into Task 4's dispatch text as
written.

## 1. Population (counts are floors — see Limitations)

- **Files scanned**: 329 (`docs/loom/audits/*.md` = 12, `docs/loom/specs/*.md`
  = 154, `docs/loom/plans/*.md` = 163). Includes this branch's own plan and
  spec (`2026-07-28-docs-citation-check-and-review-mode.md`,
  `2026-07-28-doc-branch-review-loop-audit.md`,
  `2026-07-28-revenue-chain-and-hierarchy-audit.md`) — not excluded.
- **Backtick `path:line` / `path:line-range` citations parsed**: 779
  (324 single-line, 455 range form). This is the population the two shipped
  checks (Task 1, Task 2) operate on.
- **`§N` / `§N.M` anchor refs parsed**: 401.
- **Total citations checked**: 1,180.
- **Two known-filtered classes, measured separately (v1 does NOT see these)**:
  - **Extensionless backtick citations** (the `.`-heuristic filter pinned by
    `test_backtick_citation_without_extension_is_filtered`): **0 occurrences**
    in this corpus. The limitation exists and is real (any future
    `` `Dockerfile:10` ``-shaped citation would be silently dropped), but this
    corpus happens not to exercise it.
  - **Bare, unbackticked `path:line`-shaped prose** (deliberately out of v1
    scope per the module docstring): **184 occurrences**, grep-measured
    (pattern: a `.`-extensioned relative path immediately followed by `:digits`
    outside any backtick span). Example: `SKILL.md:336` in
    `docs/loom/specs/2026-07-07-deep-deep-research-file-carrier.md:58`. These
    184 are real citation-shaped text the tool cannot check at all — the
    779 backtick citations above are a genuine floor, not the full picture.
- Every count above is a **floor**: `extract_citations`/`extract_section_refs`
  only recognize the two literal grammars Tasks 1-2 shipped; any other
  citation shape (prose, footnotes, HTML comments) is invisible to both the
  tool and this count.

## 2. Findings + adjudication

**925 total findings** (629 `file not found`, 296 `section not found`) out of
1,180 citations checked — a 78% raw finding rate. Adjudicated below by class,
not by individual line, because at this volume a flat 925-row table would
bury the signal the classes carry; every class boundary was verified against
≥1 concrete instance (cited below) before being counted, and the three
smallest/highest-value classes (confirmed true drift) are listed in full.

### 2a. `file not found` (629)

| Class | Count | Verdict | Reasoning |
|---|---|---|---|
| Bare-shorthand path, unique real target, in bounds | 467 | 🟢 **false positive** | Cited path omits its directory prefix (e.g. `sec_edgar_client.py:3483` for `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`); doc discusses one skill/plugin throughout and the writer relies on that context. Verified: 475 unique-suffix-matches total, of which 467 also have the cited line in-bounds on the real file. Often paired with a markdown link carrying the full path right next to the short label (e.g. `docs/loom/specs/2026-05-27-distill-sessions-v0.4.1-brief.md:50`) — the writer already disambiguated it for a human reader. |
| Bare-shorthand path, unique real target, **line out of bounds on resolved target** | 8 | 🟡 **masked true drift** | Same shorthand convention, but the cited line/range no longer fits the real file once resolved (e.g. `scripts/report.py:122-490` cited in `docs/loom/specs/2026-05-27-distill-sessions-v0.5-brief.md`, resolves to `dev-workflow/skills/distill-sessions/scripts/report.py`, now only 173 lines). v1 reports "file not found" here — the correct underlying defect ("line drifted") is real but reported under the wrong reason, and only visible because we manually resolved the shorthand. |
| Bare-shorthand path, **ambiguous** (matches ≥2 real files) | 123 | 🟡 **likely false positive, unconfirmed** | Same shorthand pattern (e.g. bare `SKILL.md:N` — 75 of these findings alone, matching any of 196 tracked `SKILL.md` files) but the basename doesn't uniquely resolve, so the "does it actually exist" question can't be answered mechanically. Sampled 5 and all were genuine same-doc-context shorthand (confirms the pattern), but exact-target confirmation was not done for all 123. |
| Directory renamed, hard-cut, no alias (`code-toolkit`→`loom-code`, `spec-toolkit`→`loom-spec`, `interface-design-toolkit`→`loom-interface-design`, `research-toolkit/skills/deep-research`→`deep-deep-research`, `dbt-wiki/skills/refresh`→`rescan`) | 21 | 🔴 **true drift** | Confirmed via `git log --diff-filter=R` / the rename changeset (`docs/loom/audits/2026-06-21-loom-rename-changeset.md`, PR #440) and dbt-wiki's PR #452. Citations in specs written before each rename now resolve nowhere. |
| Skill consolidation (`data-{kr,jp,cn,us}/*`, `scripts/sync-clients.sh` → `data-markets`, PR #536) | 5 | 🔴 **true drift** | `docs/loom/specs/2026-07-11-investing-toolkit-data-consolidation.md` describes the pre-consolidation five-skill layout as its own "before" state; those paths are gone at HEAD. |
| External / non-repo path (`/tmp/code-toolkit-mine.py`, `memory/project_distill_sessions_v0_3_post_ship_dogfood.md` — the user's private `~/.claude/projects/.../memory/` store) | 2 | 🟢 **false positive** | Deliberately outside the repo; never resolvable by a repo-root-relative checker, by design. |
| Wildcard / elliptical notation (`.../kpi_store.py`, `research-toolkit/skills/*/SKILL.md`) | 2 | 🟢 **false positive** | Not a literal single-file path — author-intended elision, not a citation the current grammar should try to resolve. |
| Genuine citation defect (inconsistent shorthand: `improve-loop.js:400` vs. the same doc's own established name `principles-improve-loop.js`, used 6 other times in the same doc) | 1 | 🔴 **true positive** | Real authoring error, caught correctly. |

### 2b. `section not found` (296)

| Class | Count | Verdict | Reasoning |
|---|---|---|---|
| Self-reference into a doc with **no numbered headings at all** | 230 | 🟢 **false positive** | The corpus's dominant `§N` usage is informal — a table row number, a numbered list item inside a named section, or a reference to an external doc named only in prose (no backtick, e.g. "Research §3", "research memo §4-domain landscape") — none of which is the literal `## N.` heading grammar Task 2 implements. Verified `docs/loom/specs/2026-05-28-handoff-v0.1-brief.md` (headings are all named: Problem/Users/Smallest End State/…) as a representative case: every `§N` there is a *table row number*. |
| Self-reference into a doc **with** numbered headings, but not this N | 2 | 🟢 **false positive** (both individually verified) | Not real heading drift: (a) `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md:7`'s "§3.4" refers to numbered **list item 4 under `## 3.`**, never rendered as a `### 3.4` heading; (b) `docs/loom/specs/2026-05-22-skill-log-mining-v0.1-brief.md:111`'s bare "§4" is a prose reference to an external "research memo" (no backtick), mis-bound to self by the nearest-doc-name fallback — and the doc's only "numbered heading" is a false match itself: `### 6 open questions converged` parses as heading `(6, None)` because the heading text happens to start with a cardinal number, not a section marker. |
| Cross-doc bare shorthand (doc name missing its directory prefix) that **resolves cleanly once the real path is substituted** | 14 | 🟢 **false positive**, folds via the known limitation `test_missing_target_file_folds_into_section_not_found` | E.g. `` `distill-metrics.md` §3/§5 `` → resolves to `dbt-wiki/skills/init/references/distill-metrics.md`, which genuinely has `§3`/`§5`. This and the next row are the two outcomes of one 19-item bucket (bare doc-name shorthand that resolves to a unique real file): 14 resolve cleanly on the real target; 5 do not (next row). |
| Cross-doc bare shorthand, resolves to a real file, but that file **also lacks the section** | 5 | 🟢 **false positive** (grammar mismatch, not drift) | E.g. `2026-07-04-harness-engineering-audit.md` (bare, cited from `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md:241`) has no numbered headings — same informal-§N class as row 1, just reached via a bare-shorthand doc name instead of a self-reference. One instance (`2026-07-18-agent-loop-convergence-audit.md §6`, cited from `2026-07-20-loom-mechanism-weakness-audit.md:6`) is a distinct parser mis-bind: the §6 is a same-document forward pointer ("see §6 for the dedup map") but the nearest-preceding-backtick-doc-name heuristic wrongly attached it to a different audit named earlier in the same sentence for an unrelated reason. Confirmed: the citing doc's own `## 6. Dedup vs prior audits` is the intended target. |
| Target resolves to a real bare-named file (e.g. `absent.md`-style but the name happens to exist at repo root) with no numbered headings | 7 | 🟢 **false positive** | Same grammar mismatch as above. |
| External path (`judgment-rubrics.md` — the user's private dotfiles rules file, not in this repo) | 5 | 🟢 **false positive** | Outside the repo, same class as §2a's external-path row. |
| Ephemeral/scratchpad path (`scratchpad/axis4-unforgeable-gate-research.md`) | 1 | 🟢 **false positive** | Never committed by design. |
| Template placeholder (`` `dev-workflow/skills/<name>/SKILL.md` `` — a verbatim quote of brief text, not a real path) | 1 | 🟢 **false positive** | `<name>` is a template variable inside a quoted excerpt. |
| Generic-pattern reference (`docs/loom/PRINCIPLES.md`) | 1 | 🟢 **false positive** | The citing plan describes a path pattern the *tooling* looks for in whatever target repo it runs against ("grep the target repo's `docs/loom/PRINCIPLES.md`") — not a literal citation meant to resolve in this repo. |
| Forward-reference to an apparently never-shipped plan (`to-sql` skill + `prompt-assembly.md`, dbt-wiki) | 27 | 🟡 **ambiguous** | `dbt-wiki/skills/` has no `to-sql` directory today (only `ingest/init/pack/query/redistill/rescan/review/update`). Could be an abandoned/renamed plan (true drift) or a spec forward-citing its own not-yet-built deliverable path (normal spec-authoring, not drift) — genuinely can't tell without deeper archaeology than this task's budget allows. Not counted as a confirmed false positive or confirmed true drift. |
| Directory renamed (`code-toolkit/...`) | 3 | 🔴 **true drift** | Same rename class as §2a. |

## 3. Recall vs. documented ground truth

### 3a. The four `feat-plan-fact-grounding` instances (`docs/loom/BACKLOG.md`
"Plan-stage fact grounding — what 0.39.0 does NOT close", item 3)

All four were **self-corrections made and merged during that branch's plan
review** (recorded narratively in
`docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`), not live broken
citations sitting on main today. What matters for recall is whether the
*mechanism* (silent content drift under a bounds-only check) is still live
and whether this tool would catch a recurrence:

| # | Instance | Still observable on main? | Flagged? | Why / why not |
|---|---|---|---|---|
| 1 | `:365`→`:372` shift on `loom-code/agents/code-quality-reviewer.md` | **Yes, and worse than the branch recorded.** The plan's shipped citation (`:365`, referring to an "unconditional verify-everything mandate" sentence) no longer matches *any* line in the file — the phrase is absent entirely (0 grep hits), not merely shifted. | **No.** | File exists, has 427 lines (`:365` in bounds) → bounds check passes silently. This is the declared v1 scope boundary ("no quoted-string verification") firing exactly as documented, on a real, current, live case. |
| 2 | `:41` vs `:40` ("Check 8" location) | Not independently re-verifiable: the corrected citation (`:40`) is one of many bare, multi-match `README.md`/checks-table references in the same plan; which exact file was meant is ambiguous by the same bare-shorthand pattern in §2a (75 findings share the bare-`SKILL.md`-style ambiguity). | N/A | Same content-only defect shape as #1 — even if pinned to an exact file, a bounds check cannot see "the numbered check moved." |
| 3 | `:32-39` vs `:34-39` (README field-bullet list) | **Yes, same mechanism as #1.** The doc's shipped citation (`README.md:34-39` — bare, no directory) resolves at repo-root to the top-level `README.md`, whose lines 34-39 are Gemini CLI install instructions, not a six-field bullet list. | **No** (script raises nothing — file exists, 92 lines, bounds pass). | Compound of two v1 gaps: (a) bare-shorthand ambiguity (§2a) means the resolved target may not even be the intended file, and (b) even for the intended file, no content check exists. |
| 4 | Path missing its directory segment (`scripts/…` → `loom-code/scripts/…`) | **No — fixed, and stays fixed.** Current doc cites `loom-code/scripts/test_plan_fact_grounding.py` etc. (full path). | **Would be caught if it recurred** — verified `scripts/test_plan_fact_grounding.py` does not exist at repo root, so an un-prefixed regression would produce a real `file not found` finding. | This is the one instance class the tool structurally handles: a missing-directory-prefix citation to a file that does not exist anywhere plausible is indistinguishable from true drift only when the bare name is also ambiguous (§2a); here it is not. |

**Reading**: 2 of 4 are live, current, unflagged content-drift instances (the
exact defect class BACKLOG item 3 names); this is not a v1 bug but its
declared scope boundary — "no quoted-string verification" — manifesting on
real material, and the recall floor for *this specific defect shape*
(bounds-valid, content-stale) is **0%** by construction. The tool's actual
value is confined to the bounds/existence class, which item 4 confirms works.

### 3b. `analysis-kpi` stale quote (BACKLOG's reconciliation entry, item 3)

`docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md:111`
cites `` `analysis-kpi/SKILL.md:200-201` `` for the text "GOOGL from 2014,
DIS from 2018." At HEAD: the real file is
`investing-toolkit/skills/analysis-kpi/SKILL.md` (337 lines); the corrected
text ("GOOGL from 2012, DIS from 2016") now lives at lines 204-205, not
200-201.

**Flagged?** Yes — but for the wrong reason, and the right one is invisible.
As written (bare `analysis-kpi/SKILL.md`, no directory), the script emits
`file not found`, which is the §2a bare-shorthand false-positive class, not a
genuine catch of the stale quote. If a maintainer "fixed" the obvious
problem by adding the correct directory prefix
(`investing-toolkit/skills/analysis-kpi/SKILL.md:200-201`), the citation
would then resolve cleanly (337 ≥ 201, in bounds) and the tool would go
**silent** on the exact same stale-quote defect the audit is about. This is
a coincidental double-hit, not a true recall win for content-staleness
detection — recorded here so Task 6's BACKLOG annotation doesn't overstate
what got mechanised.

## 4. False-positive rate

**Exclusion list** (confirmed 🟢 false-positive classes from §2, i.e. the
finding reflects nothing wrong with the citation):
bare-shorthand-path-in-bounds; external/non-repo path; wildcard/elliptical
notation; self-reference or cross-doc reference into a doc using named
(non-numbered) headings; bare cross-doc §N shorthand that resolves cleanly
on the real target; ephemeral/scratchpad path; template placeholder;
generic-pattern reference; the one confirmed parser mis-bind
(same-document forward pointer wrongly bound to an earlier-named doc).

- Confirmed false positives: 471 (file) + 266 (section) = **737**
- Confirmed true drift / true positives: 35 (file, incl. the 8 masked-reason
  cases) + 3 (section) = **38**
- Unresolved / ambiguous (multi-match bare shorthand; forward-refs to an
  apparently unshipped plan): 123 (file) + 27 (section) = **150**

**FP rate = 737 / 925 = 79.7%** (confirmed-only basis; the brief's own
"manually adjudicate all hits" standard). Even crediting every ambiguous
finding as a true positive (the most generous-to-the-tool reading) still
gives (925 − 737) / 925 = 20.3% flagged, of which most of the 150 ambiguous
ones are the *same* bare-shorthand pattern as the confirmed false positives
— so the honest ceiling on precision here is nowhere near the brief's ~10%
line either way.

## 5. Reversal-condition evaluation

The brief's reversal condition (§Alternatives, "My take"): **stop if the
false-positive rate exceeds ~10% after legitimate-pattern exclusions.**

**TRIPPED.** 79.7% (confirmed) is roughly 8x the threshold. The dominant
driver is a single, structural cause: **this corpus's docs routinely cite
implementation files and sibling docs by bare name or partial relative path,
trusting doc-level or section-level context** (475+123 = 598 of 629
file-not-found findings — 95% — are this one pattern), which v1's
literal-repo-root-relative resolution cannot follow. This is not a parser
bug to patch cheaply: resolving it would mean adding basename/suffix
fallback matching, which is a materially different (and ambiguity-prone —
see the 123 multi-match cases) design than the "exact path, exact bounds"
contract Tasks 1-2 shipped and tested against.

Two mitigating considerations for whoever adjudicates this, neither of which
changes the verdict above but both of which bound its scope:

1. Task 4's actual wiring point runs the script only over a PR's **changed**
   `.md` files, not this full historical corpus. This run deliberately covers
   329 files spanning 2026-05 through today, including pre-rename specs from
   before four hard-cut plugin renames (§2a) and a five-skill consolidation
   (§2a) — a harsher population than a typical incremental PR diff would
   contain. Whether a live PR's citation hygiene is materially better is
   untested by this task (that is Task 5's planted-fixture design, not this
   one).
2. The 38 confirmed-true-drift findings are real value the script would not
   otherwise surface, and the recall analysis (§3) shows the tool's positive
   contribution is real but narrow: it catches missing-file and out-of-range
   defects reliably (BACKLOG item 3's instance #4, confirmed) and is
   structurally blind to content-correctness defects (instances #1 and #3,
   and the analysis-kpi stale quote) by its declared "no semantic checking"
   scope — that gap is not what the FP-rate reversal condition measures, but
   it does mean recall against the two live ground-truth instances observed
   here is 0/2 for the content-drift shape specifically.

**Recommendation carried to the user, not decided here**: do not wire
`check_doc_citations.py` into `requesting-code-review`'s docs mode (Task 4)
as currently scoped without addressing the bare-shorthand precision problem
— either a repo-root-relative citation-writing convention enforced going
forward, a suffix-resolution fallback (accepting the ambiguity cost shown in
the 123 multi-match cases), or restricting Task 4's invocation to a
narrower, measured-safe subset (e.g. only citations that already carry a
full path from a known top-level directory). Task 4 and Task 5 should not
proceed on the current plan until this is resolved.

## Parser fixes considered, not made

Three candidate fixes were identified during this run and deliberately
**not** made:

- **Bare-shorthand/suffix-fallback resolution** — the single highest-value
  change (would resolve 598 of 629 file-not-found findings), but it is a
  scope change to the "exact path" contract Tasks 1-2 shipped and tested,
  not a bug fix, and it reintroduces ambiguity (123 of those 598 have ≥2
  candidate targets). Left for the user's decision per §5.
- **Nearest-preceding-doc-name mis-bind for self-referencing `§N`** (the
  `2026-07-20-loom-mechanism-weakness-audit.md:6` case, §2b) — a genuine
  parser limitation, but disambiguating "forward pointer into this same
  document" from "this document is discussing another doc, so the trailing
  §N is about it" needs semantic judgment a regex heuristic cannot supply
  safely; n=1 observed.
- **Excluding `<placeholder>`-shaped paths** (the `<name>` template-variable
  case, §2b) — safe and cheap, but n=1 in this corpus and does not change
  the finding's flagged/unflagged status (the doc has no numbered headings
  either way), only its reported target. Declined under Simplicity First —
  no material effect on any verdict in this note.

No amendments were made to `check_doc_citations.py` or its test file.
`python3 -m pytest loom-code/scripts/ -q` — 391 passed (unchanged baseline;
this task made no code changes).

## Limitations

- **Adjudication is class-level, not line-level**, for the two large classes
  (bare-shorthand-in-bounds, self-ref-into-named-headings). Every class
  boundary was verified against ≥1 concrete instance before counting: see
  the "Reasoning" column in §2 for the specific citations checked. The 123
  ambiguous multi-match findings were sampled (5 checked) and not
  individually resolved.
- **§3's dbt-wiki "to-sql" forward-reference class (27 findings) is left
  ambiguous**, not adjudicated either way — resolving it needs archaeology
  (checking whether the plan shipped under a different name) beyond this
  task's budget.
- **No new citations were added or fixed by this task** — this is a
  measurement-only run per the plan's Task 3 scope; the reversal condition
  firing means Task 4/5 should not proceed on the current script as-is.
- **This note's own citations are not self-checked** — running
  `check_doc_citations.py` on itself was out of scope for this run (the file
  did not exist until this task wrote it).

## Round 2: resolver fix + re-measurement (2026-07-28, same day)

Round 1's own numbers above are **left unchanged** as the historical record.
This section is a new measurement after fixing the one root cause Round 1
identified: `check_doc_citations.py` gained a repo-wide suffix-match
fallback (implementation + RED-first tests in
`loom-code/scripts/check_doc_citations.py` /
`loom-code/scripts/test_check_doc_citations.py`; full mechanism in the
module docstring). When a cited path doesn't resolve literally at the repo
root, the tool now searches the whole tree for files whose path **ends
with** the cited string: a unique match resolves and bounds-checks
normally; zero or multiple matches make the citation **UNCHECKED** — a new
third bucket, reported but never turned into a finding, since a repo-wide
search that itself comes up empty or ambiguous cannot support a confident
"file not found" claim (asserting one would repeat the false-positive
problem in mirror image).

### Same command, same corpus

`python3 loom-code/scripts/check_doc_citations.py docs/loom/audits/*.md
docs/loom/specs/*.md docs/loom/plans/*.md` — same 329 files, same 1,180
citations (779 backtick `path:line`/`path:line-range` + 401 `§N`/`§N.M`)
as Round 1's population (§1 above); population caveats there still apply
unchanged.

**New top-line result**: `checked 988 / unchecked 192 / findings 252`
(exit 1). That is 988 + 192 = 1,180, matching Round 1's population exactly
— a consistency check that no citation was silently dropped by the new
code path.

- **Findings dropped from 925 → 252** (73% fewer raw items).
- **`file not found` findings: 629 → 0.** This is now a **structural**
  result, not a measured one: once a citation resolves to a target at all
  (direct match or a unique suffix match), that target is by construction
  a real file, so "file not found" can no longer be produced as a finding
  reason — only a bounds/section check can still fail. The 598-of-629
  bare-shorthand false-positive class Round 1 identified is gone by
  construction, not by exclusion-list adjudication.
- **`line`/`section exceeds bounds` findings: 296 → 252**, split as **8
  file-citation "line exceeds file length"** + **244 `§N` "section not
  found"**.
- **New: 192 citations UNCHECKED** (see coverage-limitation note below) —
  a category Round 1's tool could not express at all; every one of those
  192 was previously silently folded into either a finding or a clean pass
  depending on what the literal resolver happened to hit.

### Re-adjudication of the new findings set

**The 8 `line exceeds file length` findings are true positives, and are
the same 8 instances Round 1 already found and mis-labeled.** Verified by
diffing target paths: 7 occurrences are `scripts/report.py`, all in
`docs/loom/specs/2026-05-27-distill-sessions-v0.5-brief.md` (Round 1
§2a's "8 masked-reason" row's worked example), plus 1 occurrence of
`cache_util.py` in `docs/loom/plans/2026-07-12-us-sec-narrative.md`. Round 1
called these **"masked true drift"** because its resolver reported them as
`file not found` (the bounds check never ran, since v1 required a literal
repo-root match to even attempt it). Round 2 correctly resolves the
bare shorthand via the suffix fallback and reports the real defect
("line N exceeds file length") instead of the wrong one. **Re-used from
Round 1, not re-verified from scratch**: the underlying citations and
their true-drift status; **newly confirmed this round**: the reason string
is now correct.

**All 244 `section not found` findings are false positives, by the exact
same mechanism Round 1 documented and this fix does not touch.**
Programmatically re-resolved each finding's target (using the same
`resolve_cited_path` the tool uses) and re-ran `parse_headings` against it:

| Class | Count | Verdict |
|---|---|---|
| Target resolves, but has **no numbered headings at all** (informal `§N` usage — table row, list item, or a prose reference to a document that just doesn't use the `## N.` grammar) | 240 | 🟢 false positive — **same mechanism as Round 1's §2b row 1** (230 instances there), now reached via the fixed resolver instead of the fold, count differs because the resolver also legitimately reclassified some of Round 1's other §2b rows (cross-doc shorthand that resolves cleanly, external paths, template placeholders) out of "finding" entirely into either a silent pass or `unchecked` |
| Target resolves, has numbered headings, but **the specific match is a parser mis-bind or a false heading match**, not real content drift | 4 | 🟢 false positive — **2 are Round 1's own individually-verified instances, re-used verbatim**: `docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md:7` (§3.4 is a list item under `## 3.`, never a real `### 3.4` heading) and `docs/loom/audits/2026-07-20-loom-mechanism-weakness-audit.md:6` (same-document forward pointer mis-bound to an earlier-named doc by the nearest-preceding-backtick heuristic — real target is that doc's own `## 6. Dedup vs prior audits`). **2 are newly spot-checked this round, same mechanism**: `docs/loom/specs/2026-05-22-skill-log-mining-v0.1-brief.md:111`'s bare `§4` is prose ("Full landmark in research memo §4-domain landscape") naming an *external* document with no backtick on the line, so the nearest-doc-name fallback wrongly binds it to the citing doc itself (verified: that doc's only "heading" match is `### 6 open questions converged`, a false match from cardinal-number heading text — same false-resolve class Round 1 pinned in `test_date_style_heading_parses_as_section_number`); `docs/loom/specs/2026-05-26-distill-sessions-v0.4-brief.md:62` cites `` `2026-05-22-skill-log-mining-v0.1-brief.md` §172 `` — not a real section number at all (that doc has no `§172`-shaped heading; `172` is not even a line-count-plausible section index), same doc/same false "6" heading match applies |

Confirmed false positives: 244. Confirmed true positives: 8. **No
ambiguous/unresolved bucket this round** — every one of the 252 findings
was individually or class-verified above (unlike Round 1's 150 unresolved
findings, which no longer arise because the same-shaped citations either
resolve cleanly now or fall into `unchecked`).

### FP rate — computed the same way as Round 1, and the number moves the wrong direction

**FP rate = 244 / 252 = 96.8%** (confirmed-only basis, Round 1's own
standard). This is **numerically higher than Round 1's 79.7%**, despite
the fix eliminating the single largest, and only previously-measured,
false-positive class in the corpus. Both things are true at once and
neither cancels the other:

- **What actually improved**: file-citation precision. Round 1 measured
  467 confirmed false positives + 123 unconfirmed-ambiguous out of 629
  `file not found` findings on that check alone; Round 2 has **zero**
  false positives on that check, because `file not found` can no longer
  be produced as a reason at all. On the narrow "does a `path:line`
  citation resolve correctly" question, this fix worked exactly as
  designed.
- **What did not move, because this fix never touched it**: the `§N`
  anchor check's dominant false-positive class is a **heading-grammar
  mismatch** (informal `§N` usage into documents that don't use the
  `## N.` numbered-heading convention) — a completely different defect
  from the bare-shorthand **path-resolution** problem this fix targeted.
  That class was already the majority of Round 1's `section not found`
  findings (230 of 296) and is now effectively **all** of Round 2's
  findings (240 of 244), because Round 2's population of `section not
  found` findings shrank far less than its `file not found` population
  did (296 → 244 vs. 629 → 0), so the untouched class now dominates the
  denominator.
- **Direction, not magnitude, is the only honest claim about the
  aggregate ratio**: the 96.8% figure is not evidence the fix made things
  worse — it is an artifact of computing one ratio over two problems that
  moved in opposite directions (one solved, one untouched) using a
  denominator the fix shrank asymmetrically. Reporting it without this
  context would be exactly the kind of population-less magnitude claim
  Task 4's own prose-defect taxonomy would flag in review.

### Coverage limitation: 192 unchecked citations (honest floor, not a fix)

192 of 1,180 citations (16%) are `unchecked` — the tool explicitly
declines to render a verdict, rather than guessing. This is a real,
measured recall cost, most visible on Round 1's confirmed **true-drift**
classes: spot-checked a sample of 17 pre-rename citations to the four
hard-cut renamed directories (`code-toolkit/`, `spec-toolkit/`,
`interface-design-toolkit/` — Round 1 §2a's 21-instance confirmed-true-drift
row), and **all 17 are now `unchecked`**, not findings — the suffix
fallback correctly finds zero repo-wide matches for a fully-qualified path
under an old directory name with no alias, and the design (loudly) refuses
to convert that into a confident "file not found" claim. **This is a
deliberate recall-for-precision trade the task explicitly specified, not
an accidental gap**: real drift that manifests as "this exact full path no
longer exists anywhere" is now invisible to a `findings` count, and only
surfaces at all via the `unchecked` count in the summary line. Anyone
consuming this tool's exit code / findings list alone (as Task 4's
proposed wiring would) would not learn that 192 citations, including at
least those 17 confirmed genuine renames, went unverified this run.

### Reversal-condition evaluation (fresh, against the brief's ~10% threshold)

**Still TRIPS.** By the same FP-rate methodology as Round 1 (confirmed
false positives ÷ confirmed findings), Round 2 measures **96.8% (244/252)**
— not merely still above ~10%, but a higher ratio than Round 1's 79.7%,
for the structural reason explained above (one problem solved, a different,
untouched problem now dominates the denominator). The fix did exactly what
it was scoped to do — eliminate the bare-shorthand file-citation
false-positive class — and that class is now completely gone (0 of 629
equivalent). But the brief's reversal condition is evaluated on the
**aggregate** finding set the tool would hand to a reviewer, and that
aggregate is dominated by a second, structurally distinct false-positive
class (the `§N` heading-grammar mismatch) that this task's Part A scope
never targeted and did not fix.

**status: NEEDS_CONTEXT.** Per this task's own dispatch instruction, this
result is reported as-is, not softened. The open question for whoever
reviews this: is the path forward (a) a second resolver-shaped fix
targeting the `§N` heading-grammar mismatch specifically (same
precision/recall shape as this round's fix, likely similarly effective on
its own narrow target), (b) restricting Task 4's wiring to the file-citation
check only (which this round shows is now at effectively 100% measured
precision) and dropping or gating the `§N` check separately, or (c) some
other disposition Task 4/5 should not proceed past without. This note
does not decide that question — it surfaces the evidence per the brief's
own reversal-condition contract.

## Round 3: §N applicability rule + mis-bind reconciliation (2026-07-28, same day)

Rounds 1 and 2's content above is **left unchanged** as the historical
record. This section answers Round 2's open question option (a): a
second resolver-shaped fix targeting the `§N` heading-grammar mismatch
specifically. `check_section_anchor` now treats a resolved target with
**zero numbered headings** as UNCHECKED, not a finding — the `§N` grammar
does not apply to a document that uses named headings exclusively, in
either direction (self-reference or cross-doc). A finding may only fire
when the target HAS numbered headings but lacks the specific one cited.
Implementation + RED-first tests in `check_doc_citations.py` /
`test_check_doc_citations.py` (`check_section_anchor`'s `if not headings:
return False, None` guard; two tests: one new
`test_section_anchor_target_with_no_numbered_headings_is_unchecked`, one
redefined `test_bare_section_anchor_self_ref_with_no_numbered_headings_is_unchecked`
— see below for why the redefinition is legitimate here).

### Same command, same corpus

`python3 loom-code/scripts/check_doc_citations.py docs/loom/audits/*.md
docs/loom/specs/*.md docs/loom/plans/*.md` — same 329 files, same 1,180
citations as Rounds 1 and 2.

**New top-line result**: `checked 748 / unchecked 432 / findings 12` (exit
1). 748 + 432 = 1,180, matching the population exactly (no citation
silently dropped).

- **Findings dropped from 252 → 12** (95% fewer than Round 2, 99% fewer
  than Round 1).
- **`unchecked` rose from 192 → 432** (+240): the entire drop in findings
  moved into the unchecked bucket, not away entirely — every one of the
  240 previously-flagged "target has no numbered headings" citations
  (Round 2's dominant remaining class, §2b/Round-2-table row 1: 240 of
  244) is now loudly UNCHECKED instead of a finding. This is the same
  "loud skip over confident wrong guess" trade Round 2 made for
  ambiguous/zero-match path resolution, applied to the applicability
  question instead.
- **Findings remaining: 12** = the 4 individually-adjudicated
  parser-mis-bind instances (Round 2's table row 2) + the 8 confirmed
  true-drift `line exceeds file length` findings (Round 2's re-used
  Round-1 instances) that Round 2 already resolved correctly and this
  round's fix does not touch:

```
docs/loom/audits/2026-07-18-agent-loop-convergence-audit.md:7 -> ...:§3.4 section not found
docs/loom/audits/2026-07-20-loom-mechanism-weakness-audit.md:6 -> 2026-07-18-agent-loop-convergence-audit.md:§6 section not found
docs/loom/specs/2026-05-22-skill-log-mining-v0.1-brief.md:111 -> ...:§4 section not found
docs/loom/specs/2026-05-26-distill-sessions-v0.4-brief.md:62 -> 2026-05-22-skill-log-mining-v0.1-brief.md:§172 section not found
docs/loom/specs/2026-05-27-distill-sessions-v0.5-brief.md:{60,61,62,63,214,215,216} -> scripts/report.py:* line exceeds file length (7 findings)
docs/loom/plans/2026-07-12-us-sec-narrative.md:198 -> cache_util.py:170-252 line exceeds file length
```

### Per-mis-bind disposition — reproduced against the real corpus, fixed or documented

All 4 were reproduced against the live files at HEAD (not re-derived from
the Round 2 note) before disposition. **None was fixed** — each is either
an inherent grammar limitation or a case Round 1's own "Parser fixes
considered, not made" section already declined as unsafe to special-case;
fixing any of them would need semantic judgment a regex heuristic cannot
supply safely, which is the same conclusion Round 1 reached, not a new
one reached here.

| # | Instance | Diagnosis | Disposition | Reason |
|---|---|---|---|---|
| 1 | `2026-07-18-agent-loop-convergence-audit.md:7` §3.4 | Not a doc-name mis-bind (bare self-ref, correctly resolved) and not a false heading match (the doc's own `## 3. Designs...` heading is real). The defect is grammar-shaped: `§3.4` in the amendment bullet ("Added Gaps 8–10, §3.4, and the numeric-drift note") names a **numbered list item inside §3** (a Gap sub-item), never rendered as a real `### 3.4` heading. | **Documented, not fixed** | Distinguishing "a `§N.M` that names a real subsection heading" from "a `§N.M` that names an in-prose numbered list item" needs understanding what the prose means, not just where the digits sit — no heading-set change fixes this without also risking new false negatives on genuine `### N.M` drift. Out of v1's declared "no semantic check" scope. |
| 2 | `2026-07-20-loom-mechanism-weakness-audit.md:6` §6 | Confirmed doc-name mis-bind: the line names two other docs by backtick (`2026-07-04-harness-engineering-audit.md`, `2026-07-18-agent-loop-convergence-audit.md`) before a same-document forward pointer ("See §6 for the dedup map"); the nearest-preceding-backtick heuristic binds §6 to the second named doc instead of recognizing it as pointing at the citing doc's own `## 6. Dedup vs prior audits` (verified present at line 96 of the citing doc). | **Documented, not fixed** | Round 1's "Parser fixes considered, not made" section already examined this exact shape (n=1) and declined a fix: preferring "self has this heading" over "nearest preceding doc name" when they conflict is a plausible heuristic but risks silently swallowing genuine cross-doc drift where the citing doc coincidentally shares a heading number. No new information this round changes that call. |
| 3 | `2026-05-22-skill-log-mining-v0.1-brief.md:111` §4 | Confirmed doc-name mis-bind: the line reads "Full landscape in research memo §4-domain landscape" — the referenced document ("research memo") is named only in prose, no backtick anywhere on the line, so the self-reference fallback (`target_doc_name=None` when no backtick doc name is on the line) wrongly treats §4 as pointing at the citing doc's own headings. | **Documented, not fixed** | The self-reference fallback is deliberate documented v1 behavior (module docstring: "a bare §N with no document named on that line resolves against the containing document itself"); making it recognize an *unbacktracked prose* document name would require free-text entity extraction, well outside a regex-based checker's scope. |
| 4 | `2026-05-26-distill-sessions-v0.4-brief.md:62` §172 | Confirmed false heading match, not a doc-name mis-bind: the citation correctly resolves to `2026-05-22-skill-log-mining-v0.1-brief.md` (backtick-named on the same line) and correctly finds no `§172` heading — because that document's only "numbered heading" is `### 6 open questions converged` (a false match: heading text that happens to start with a cardinal number, not a real `## N.` convention), the doc's heading set is non-empty and the round-3 zero-headings rule does not fire. | **Documented, not fixed** | Same false-heading-match class Round 1 pinned as an accepted, not-to-fix limitation (`test_date_style_heading_parses_as_section_number` — the doc's `## 2026 Release Notes` case). Tightening heading detection to exclude cardinal-number titles would flip that pinned test's expected outcome and is exactly the kind of "improve an adjacent thing that isn't this task's target" move Simplicity/Surgical-changes rules out; instances 3 and 4 share this one root cause (the same target document), not two independent defects. |

### FP rate — same methodology as Rounds 1–2

Confirmed false positives: all 4 mis-bind instances above (each verified
individually — none is real content drift). Confirmed true positives: the
8 `line exceeds file length` findings (re-used verbatim from Round 2's own
re-verification, unaffected by this round's change). No ambiguous bucket.

**FP rate = 4 / 12 = 33.3%** — down from Round 2's 96.8% and Round 1's
79.7%, but **still above the brief's ~10% line**.

### Coverage limitation: 432 unchecked citations, now including the no-numbered-headings class

432 of 1,180 citations (36.6%, up from Round 2's 16%) are `unchecked`.
This is **two structurally distinct classes stacked**, not one:

- **192, unchanged from Round 2**: bare/suffix path citations with zero
  or multiple repo-wide matches (file citations and `§N` doc-name
  resolution alike) — untouched by this round's fix.
- **240, new this round**: `§N` citations whose target resolves to a real
  file but that file has no numbered headings at all — the applicability
  class this round's fix converts from "finding" to "unchecked." This
  means the round-1 confirmed-true-drift instances that depend on a
  numbered-heading target still work as findings (none were lost — the
  8 true positives above are unaffected), but **any real content drift
  in a `§N` citation into a named-heading document is now structurally
  invisible**, same shape as Round 2's "hard-cut rename with no alias"
  gap for file citations. Anyone consuming only the findings list /
  exit code (as Task 4's proposed wiring would) still would not learn
  that over a third of all citations in this corpus went unverified.

### Reversal-condition evaluation — three-round trajectory

| Round | Fix scope | checked | unchecked | findings | Confirmed FP | Confirmed TP | Ambiguous | FP rate | vs. ~10% |
|---|---|---|---|---|---|---|---|---|---|
| 1 | none (measurement only) | n/a (no 3-bucket split) | n/a | 925 | 737 | 38 | 150 | 79.7% | **TRIPS** |
| 2 | bare/suffix path-resolution fallback | 988 | 192 | 252 | 244 | 8 | 0 | 96.8% | **TRIPS** (higher than R1) |
| 3 | §N zero-numbered-headings applicability rule | 748 | 432 | 12 | 4 | 8 | 0 | 33.3% | **TRIPS** (lower than R1 and R2) |

**Still TRIPS.** Two consecutive fixes, each precisely targeted at the
prior round's dominant measured false-positive class, cut findings by
99% (925 → 12) and moved the FP rate from 79.7% → 96.8% → 33.3% — real,
compounding, verified progress — but the ratio has not crossed the
brief's ~10% threshold, and the residual is no longer a bulk pattern:
it is 4 individually-diagnosed parser-grammar edge cases (all
adjudicated above as not safely fixable within this checker's regex-based
design) against 8 true positives. There is no further single-class fix
left to make on this corpus — the remaining 4 false positives are as
architecturally distinct from each other as this round's fix was from
Round 2's.

**status: NEEDS_CONTEXT.** Per this task's own dispatch instruction, this
result is reported as-is, not softened. The open question carries
forward from Round 2, sharpened by this round's evidence: on a
12-finding residual with 8 confirmed true positives and 4 individually
undismissable-but-unfixable false positives, is the path forward (a)
accept a human-adjudication step for the `§N` check specifically (its
remaining false-positive surface is now small enough — 4 instances on a
329-file corpus — to plausibly review per-PR rather than trust
mechanically), (b) wire only the file-citation check (0 false positives,
confirmed across two rounds) into Task 4 and drop or gate the `§N` check
separately, or (c) some other disposition. This note does not decide
that question — it surfaces the evidence per the brief's own
reversal-condition contract.

## Round 4 — disposition (2026-07-29, final)

Rounds 1-3's content above is **left unchanged** as the historical
record. The user resolved Round 3's open question with option (b),
split further: **split-half shipping**. The default invocation of
`check_doc_citations.py` now runs ONLY the `path:line` bounds check;
the `§N` anchor check moves behind an opt-in, **experimental**
`--sections` flag. Implementation + RED-first tests in
`check_doc_citations.py` / `test_check_doc_citations.py` (`main`'s
`--sections` flag; `check_doc_report`/`check_doc`'s `check_sections`
parameter, default `False`, gating whether `extract_section_refs` even
runs). "Experimental" reflects that the `§N` convention itself is only
days old in this corpus (round 1 §1) — its value is prospective, not
yet demonstrated; the module docstring and `--sections`' usage text
both name this dogfood note and state the re-measure trigger: revisit
default-on once the corpus's `§N` usage has grown materially past
round 1's 401-ref population.

### Decision evidence: per-check split across all four rounds

| Round | Check | Confirmed TP | Confirmed FP | FP rate |
|---|---|---|---|---|
| 1 | both, undifferentiated | 38 | 737 | 79.7% |
| 2 | file-citation (after suffix-fallback fix) | 8 | 0 | **0%** |
| 2 | `§N` anchor (untouched by that fix) | 0 | 244 | 100% |
| 3 | file-citation (unchanged from round 2) | 8 | 0 | **0%** |
| 3 | `§N` anchor (after zero-numbered-headings fix) | 0 | 4 | (4/4 of remaining `§N` findings; 0 TP ever recorded) |
| 4 (this run, same 329-file corpus) | file-citation (default mode) | 8 | 0 | **0%** (8/8) |
| 4 (this run, same corpus) | `§N` anchor (`--sections`) | 8*/0 | 4 | *the 8 true positives in `--sections` mode are the same file-citation TPs, mixed back in by the combined counters — the `§N` check itself has contributed **zero** confirmed true positives in any of the four rounds |

The split is decisive, not marginal: across every round measured, the
file-citation check never produced a false positive once the round-2
resolver fix landed (0/8, twice independently confirmed), and the `§N`
check never produced a true positive at all — its entire measured
value across 401 corpus refs and two targeted fixes is zero confirmed
catches against 4 residual false positives.

### Reversal-condition evaluation — what ships wired

Task 4's dispatch (`loom-code/skills/requesting-code-review/SKILL.md:97`)
invokes `check_doc_citations.py` in **default mode** (no `--sections`
in its command line). Re-running the full historical corpus in default
mode this round measured **checked 625 / unchecked 154 / findings 8**,
all 8 the same confirmed true positives Round 2/3 already verified
(`scripts/report.py` line-drift ×7, `cache_util.py` line-drift ×1) —
**0 confirmed false positives (0% of 8)**.

**The brief's ~10% reversal condition is SATISFIED for the shipped
wiring.** 0% is not merely under the ~10% line, it is the best result
measured across all four rounds on either check. Task 4's text needs no
change to reflect this — it was already written to invoke the script
plainly, with no `--sections`, and default-mode semantics now make that
exactly correct (verified below).

**The `§N` check is NOT wired and stays labelled experimental.** Its
corpus record — **zero confirmed true positives, 4 residual false
positives** — is the reason, stated plainly: two rounds of targeted
fixes eliminated its bulk false-positive classes (925 → 12 raw findings
overall) without ever surfacing one real content-drift catch, and the
remaining 4 are individually-diagnosed grammar limitations already
adjudicated in Round 3 as not safely fixable by a regex heuristic. A
check with a 0/8 record on the same corpus its sibling check is 8/8 on
does not meet the same bar for unconditional wiring.

### T4 dispatch text verification

Read `loom-code/skills/requesting-code-review/SKILL.md:97` (Step 1's
docs-only dispatch mode, item (c)): the invocation is
`python3 loom-code/scripts/check_doc_citations.py <changed .md files>`
— no `--sections` flag anywhere in the line or its surrounding prose.
**Verification result: NO CHANGE NEEDED.** Since `--sections` is
opt-in (default `False`), an invocation that never mentions the flag
already gets exactly the shipped-safe, 0%-FP default-mode behavior;
the text was correct before this task under the old (always-both)
semantics only insofar as no such split existed yet, and is correct
now under the new semantics without editing a single character.

### Coverage limitations (restated, default mode)

Anyone consuming only `check_doc_citations.py`'s default-mode exit code
/ findings list — as Task 4's wiring does — does not learn about:

- **The `unchecked` bucket** (154 of 779 file citations this run, 19.8%):
  bare/suffix path citations with zero or multiple repo-wide matches,
  including confirmed genuine renames with no alias (round 2's 17-sample
  spot-check, all `unchecked`). A real "this file was deleted, nothing
  replaced it" defect is invisible unless the `unchecked` count itself
  is read.
- **The extensionless-citation class** (`` `Dockerfile:10` ``-shaped):
  0 occurrences in this corpus (round 1 §1), but still silently dropped
  by `_looks_like_citation`'s dot-in-final-segment filter if one ever
  appears — pinned by `test_backtick_citation_without_extension_is_filtered`.
- **The bare (unbackticked) `path:line` prose class**: 184 occurrences
  measured in round 1 §1, deliberately out of scope for both modes —
  the tool only ever sees backtick-quoted citations.
- **The entire `§N` class in default mode, new this round**: 401 anchor
  refs in this corpus, now completely invisible to a default-mode run
  — not `checked`, not `unchecked`, not a `finding`, simply never
  extracted. This is the intended effect of the split (avoid implying
  section anchors were checked when they were not), but it means a
  default-mode consumer sees a strictly narrower population than any
  prior round's tool did; `--sections` is required to see any `§N`
  signal at all, experimental status notwithstanding.

### Verification

`python3 -m pytest loom-code/scripts/ -q` — 404 passed (400 baseline +
4 new: default-mode omission, `--sections` restores round-3 behavior,
and the two `main()`-level CLI-flag tests). 10 existing `§N`-related
tests were updated to pass `check_sections=True` explicitly — see
`test_check_doc_citations.py`'s Round 4 header comment and the per-test
comments for which and why (each was pinning `§N` mechanism behavior
that would otherwise pass trivially/vacuously once `§N` extraction
became opt-in-off by default, not a behavior change to what `--sections`
mode itself does).
