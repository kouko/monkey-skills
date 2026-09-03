# Spec red-team — 2026-09-03-loom-post-merge-seams (round 2, v3)

R1 PR spoofing — holds. `closed` now only reaches trunk via squash-merge itself
(no claim to verify); design decision's own sentence: "a closed on the trunk
is itself the proof of the merge — no PR-number verification is needed and
none is done." No fabricated-PR path survives to trunk.

R2 future/garbage date on `closed` — escapes, unchanged. Design decision says
the grammar regex is shared across confirmed/closed/intent.schema but never
says `is_real_date()` is called on the closed branch's date, unlike its
sibling. Add: "the closed-date branch also calls `is_real_date`, same as
`confirmed`."

R3 rename-based smuggling (--no-renames on the close commit) — moot, not
fixed. v3 dropped round-1's new push-gate shape for the close commit
entirely ("no rule gains a shape"); there is no shape rule left for renames
to defeat. But see new attack below — dropping the shape rule reopens R1's
old #4/#5.

R4 second file in the same commit — escapes (regression from round 1). The
close commit is no longer gated by any exactly-one-file check; only
`push.dispatch-covers-tasks` fires, and only for `code`/`skill`/`gate`
paths. A close commit can carry an arbitrary second *docs*-typed edit
(another intent's status line, a plan.md rewrite, KICKOFF-DEFAULTS.md) with
zero automated flag — the spec relies entirely on kouko reading the PR diff
before pressing merge, and never says so. Add to Design decision/Boundary:
"the close commit's shape is not machine-checked; smuggled non-trailer-duty
content is caught only by the PR diff kouko reads before merging" — state
it, don't leave it implicit.

R5 second hunk / whitespace noise — same as R4, now escapes for the same
reason (no shape rule left). Same fix line covers both.

R6 silent reopen (closed→confirmed hand-edit) — escapes, unaddressed in v3.
No rule treats `closed` as terminal against a later commit reverting it, and
the round-1 open question return is not answered by REQ-2's grammar-sharing
sentence. Add a rule (or `intake.confirmed` extension) rejecting a
`closed → confirmed` transition, or an explicit accepted-risk sentence.

R7 plumbing hidden under `.codex/hooks/contract/` — holds. REQ-3's
content-bound exemption (blob-equal to the canonical file next to the
running checker) closes the path-prefix hole; a hand-authored or altered
file no longer classifies as plumbing merely by location. Acceptance #3
only exercises the positive case though (add: a negative acceptance line —
a hand-edited/extra file under `.codex/hooks/contract/` must still owe a
Task: trailer — or the byte-comparison's negative branch ships untested).

## New attacks on v3

1. Close commit + review-only commit collapsed into one commit (touching
   intent + review.json together) — escapes REQ-1's prose ("a review-only
   commit that follows") but not machine-checked: `check_review_only_head`
   would reject it (HEAD must touch only review.json) since that check is
   unchanged and still runs on HEAD. **Holds**, via the untouched rule, not
   via REQ-1's own text.

2. `closed` reaches trunk without review — verified CI does NOT recompute
   the push gate. `.github/workflows/loom-code-ci.yml`'s only job is
   "pytest + knowledge-drift + codex-manifest-drift" (`python3 -m pytest
   loom-code/scripts/ scripts/ .claude/hooks/ -v` + a filesystem-boundary
   check) — it never invokes `loom_checker.py push`. The push gate is a
   client-side pre-push hook only; nothing server-side re-verifies
   `reviewed-sha`, `dispatch-covers-tasks`, or the probes before merge is
   allowed. REQ-1's whole "closed-on-trunk-is-proof" argument rests on the
   push gate having actually run, but a bypassed/uninstalled local hook (or
   `--no-verify`, or a push from a machine that never scaffolded the hook)
   plus an inattentive merge-click puts fabricated `review.json`/`closed`
   on trunk with zero automated check ever firing. Pre-existing
   architecture (not introduced by this spec), but REQ-1 leans on it more
   than round 1 did and the spec never states the reliance. **Important** —
   add one Boundary sentence naming the push gate as client-side-only and
   the PR-merge click as the actual trust boundary (matches "kouko presses
   merge" already being user-decided, so this is a documentation gap, not
   new design work).

3. Second push after close commit skips probe re-run — does not escape.
   `check_probes_package_tests`/`check_probes_adversarial` require
   `probe.sha` to resolve to `reviewed_id`, and `check_reviewed_sha`
   requires `reviewed_id == HEAD^` — i.e., the close commit exactly. The
   checker then actually executes the declared command against the clean
   working tree (loom_checker.py:1825-1900), not the recorded `result`.
   **Holds.**

4. Close-and-abandon then reuse the change-id — does not escape. `closed`
   never reaches trunk unless merged (per the design's own invariant); an
   abandoned branch leaves the trunk's intent still `confirmed`, so a fresh
   branch off trunk sees an ordinary re-plannable confirmed intent — no
   inconsistent state is created. **Holds.**

5. REQ-3 on Claude Code with two cached plugin versions — undefined.
   "the running checker" resolves to whichever `~/.claude/plugins/cache/
   monkey-skills/loom-code/<version>/scripts/loom_checker.py` the harness
   invoked for *this* session; a stale cached version comparison could
   accept a `.codex/hooks/loom_checker.py` copy that matches an OLD
   canonical checker no longer in effect, or reject one that matches the
   current-but-not-yet-reloaded canonical file. **Escapes as an
   under-specified boundary** — add: "the running checker" means
   `Path(__file__)` of the process executing `push`, so a stale cache
   compares against a stale canonical and produces a stale (not wrong, but
   possibly outdated) verdict; this is the same three-step-sync gap the
   repo's own memory already tracks, not a new hole — one sentence
   suffices, no new mechanism.

6. On Codex, the running checker IS the copy — the design decision already
   states this trivializes the checker-file comparison and calls it a
   "recorded, not hidden" pre-existing gap (concept-model §7). That
   sentence is enough for the checker-file comparison specifically. It is
   **not** enough for `git_exec.py` or `contract/<rel>`: those still
   compare the *deployed* copy against the *deployed* canonical
   (`Path(__file__).parent`'s siblings and `contract/`), which on Codex are
   the same tree the attacker already controls before the checker ever
   runs — an attacker who edits `.codex/hooks/git_exec.py` and
   `.codex/hooks/loom_checker.py` together (so the running checker's own
   comparison logic is the attacker's patched logic) can make any content
   compare equal to itself. This is one level worse than the stated gap:
   it is not "the checker-file check is trivially true," it is "the
   attacker can rewrite the check itself." **Fatal** on Codex specifically
   — the spec's single "recorded, not hidden" sentence covers only the
   narrower case it names (checker-file self-comparison) and silently
   extends coverage to a case (co-modified `git_exec.py`) it never
   analyzed. Fix: state explicitly that on Codex the entire host-plumbing
   exemption is unverifiable end-to-end (not just the checker-file leg) —
   or scope the exemption to Claude Code only.

7. `.codex/hooks/contract/extra.md` added, not written by the scaffold —
   does not escape. No canonical `contract/extra.md` exists next to the
   running checker to compare equal to, so the byte-comparison fails by
   construction and the path falls through to `gate` classification,
   owing a trailer. **Holds**, contingent on the comparison being
   "canonical file exists AND bytes match" rather than "path is under the
   prefix" (round-1's bug) — REQ-3's design decision text supports the
   former reading.

## REQ-4/5/6 falsifiability

REQ-4: table + `git rev-list --count` + one recommendation line — checkable
by inspection, falsifiable. REQ-5: version strings + directory existence +
`--list-rules` output — falsifiable. REQ-6: five nits each pinned to
`file:line` with a named fix — falsifiable. No unfalsifiable clauses found
in REQ-4/5/6, same conclusion as round 1's item 8.

## Verdict

**NEEDS_REVISION** — fatal: 1 (new attack #6, Codex co-modification of the
checker's own comparison logic). important: 4 (R2 date realism; R4/R5
close-commit shape now unguarded and undocumented; new attack #2 push-gate
is client-side-only and unstated; new attack #5 stale-cache "running
checker" undefined). nit: 1 (R7's Acceptance #3 has no negative test case).
R1, R3(moot), R6(carried, unaddressed — folded into "important" count above
as part of the close-commit-shape family), new attacks #1/#3/#4/#7 hold.
