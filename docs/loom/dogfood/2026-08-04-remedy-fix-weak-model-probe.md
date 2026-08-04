# Dogfood record — 0.51.0 remedy fix, weak-model + cold-reader probes

Date: 2026-08-04
Branch: `fix-review-scope-remedy-and-claim-sweep-py` (probes run at the
post-T10 tree, loom-code 0.51.0)
Plan: `docs/loom/plans/2026-08-04-loom-mechanism-defect-fixes.md` Task 11
Operator note: probes executed by the orchestrator, not an implementer
subagent — probe (a) requires dispatching a weak-model agent, and
subagents cannot dispatch agents (recorded gotcha: a skill wrapped in a
subagent silently degrades to self-review). Reviewer verification of this
record still runs as the plan specifies.

## Probe (a) — D-A live un-wedge, haiku, verdict: CLEAN

Sandbox reproduced the stale-cut geometry from the brief's §Verified root
cause (scratchpad `da-probe/`): upstream `main` at M0 → local `prev`
+P1,P2 → upstream gains squash-style S duplicating P1+P2 content → `arc`
cut from P2 → own commit O1 → fetch. The fixed resolver refused and
printed old-base `c4df862b` = **P2, the creation sha** (merge-base was
`42e478c8` = M0; the pre-fix code printed the merge-base — pinned RED in
`test_cli_stale_cut_remedy_uses_creation_sha_not_merge_base`).

A haiku agent was handed ONLY the sandbox path + the refusal stderr, with
the instruction to follow the printed remedy and stop on any conflict.
Result: ran the remedy verbatim, **rebase completed conflict-free**
("Rebasing (1/1) … Successfully rebased"), and
`git log --oneline origin/main..HEAD` listed exactly one commit — `O1 own
work`. The wedge class the 0490 arc hit live (foreign already-squashed
commits replayed onto main) did not occur.

Observation (out of this arc's scope, recorded honestly): the remedy's
literal `… HEAD` form rebases a **detached HEAD** — the branch ref itself
does not move. The un-wedge is real (the replayed commits are correct and
conflict-free) but a verbatim weak-model follower ends detached and must
still re-point the branch. The remedy SHAPE (`git rebase --onto <new>
<old> HEAD`) is pinned across spec/docstring copies and was explicitly
out of scope for this arc (brief §Out of scope); candidate next-touch:
print the branch name instead of `HEAD` when it is known — same site as
the caveat's existing branch-name resolution.

## Probe (b) — D-C cold-reader, sonnet, verdict: CLEAN

(The spec's Decision 5 promises cold-reader probes for BOTH D-C and E-3;
E-3's ran separately as probe (d) below — recorded after the
whole-branch docs arm caught the roll-up missing it.)

A cold sonnet agent read ONLY §Verdict mapping (the edited lines) of
`plan-document-reviewer-prompt.md`, plus a fabricated round-1 state: a
4-task plan, Check 6 failing on Task 2 (noticed) and Task 4 ("already
mentally moved on"), Check 9 failing on Task 3. It returned exactly three
gap entries — Check 6/Task 2, **Check 6/Task 4**, Check 9/Task 3 — and
attributed the Task 4 inclusion to the new sentence verbatim ("Before
returning, re-scan every task against each check that failed anywhere…"),
adding that nothing permits omitting Task 4 because Task 2's instance was
already found. The sentence discharges D-C's obligation on a cold reader
with no other context.

## Probe (c) — D-D mechanical, verdict: CLEAN (exemplar substituted)

The plan pinned the probe on the "so the sample of recorded findings is
never biased" claim expecting a `loom_gate_markers.py` hit. That exemplar
no longer exists: the 0490 arc's own fix (`88902358`, "state ledger
invocation semantics, not mint semantics, at all copies") rewrote the
ledger claim at every copy including the module docstring, so the
historical third copy was retired before this probe ran. Honest
substitution: the probe re-ran on a LIVE md↔py mirror pair — the §Pinned
refusal contract sentence ("The resolver never returns a file list it
cannot vouch for") — and the sweep reported:

- `loom-code/scripts/review_scope.py:76` (module docstring) and
  `loom-code/scripts/test_review_scope_docs_station.py:24` (module
  docstring) — both line numbers verified exact against `grep -n`;
- the `.md` copies (`requesting-code-review/SKILL.md:98`,
  `requesting-docs-review/SKILL.md:77`) in the same operative list;
- summary line now reads "swept 2785 markdown files and 668 python
  module docstrings" — counts are LIVE working-tree state (the tool
  walks the filesystem, so untracked scratch files inflate them; a
  clean checkout of this commit measures 2702/667 — the reviewer
  reproduced the five operative hits exactly either way), and the leak
  list names the narrowed blind spot
  (function/class docstrings, non-docstring literals, comments, commit
  messages).

The defect class that motivated D-D — a contract-prose mirror in a .py
module docstring invisible to the sweep — is closed for the module-
docstring carrier.

## Probe (d) — E-3 cold-reader, sonnet, verdict: CLEAN

A cold sonnet agent read ONLY the panel step's Step-3 paragraph
(`requesting-code-review/SKILL.md:108`, the line carrying the new
pointer) plus a fabricated state: both panel arms terminated on the API
error "You've hit your session limit". It correctly distinguished the
capacity-error case from the Dead-arm rule's single-arm death, named the
pointer target (`dispatch-hygiene-notes.md` §Capacity-error recovery),
resolved the relative path against the SKILL.md's own directory, and
quoted the landing section's first sentence — the pointer both fires and
resolves for a reader with no other context. (This session itself hit
the exact scenario live during the whole-branch review: four arms died
together on a session limit and were re-dispatched per that protocol.)

## Verdict roll-up

| Probe | Target | Model | Verdict |
|---|---|---|---|
| (a) live un-wedge | D-A remedy old-base | haiku | CLEAN |
| (b) cold-reader | D-C sweep obligation | sonnet | CLEAN |
| (c) mechanical sweep | D-D .py docstrings | — | CLEAN (exemplar substituted) |
| (d) cold-reader | E-3 capacity pointer | sonnet | CLEAN |

No probe blocks finishing. Next-touch candidates recorded above and from
the whole-branch review: remedy prints branch name instead of literal
`HEAD`; the fallback caveat's "last-line sha" recovery is imperfect when
the reflog itself was pruned or the creation sha diverged (two of the
three fallback triggers — the caveat's conditional phrasing bounds the
harm, but a follower can land back on the rejected sha); plus the arc's
reviewer debt (recorded in the shipping PR's body and the plan's Notes).
