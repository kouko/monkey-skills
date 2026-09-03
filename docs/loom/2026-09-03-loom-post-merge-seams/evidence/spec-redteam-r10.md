# Adversarial red-team, round 10 — REQ-1 `push.review-only-head`, spec v11

Target commit: `30e2c8009868446384642534b4b62f62d2199be0` ("spec v11").
Code cross-checked at `HEAD` (`git show HEAD:loom-code/scripts/loom_checker.py`,
`check_close_commit_shape` / `parse_document` / `STATUS`), scored as an
in-progress build gap where the code hasn't caught up to the spec text yet —
findings are about the *design v11 describes*.

## 1. Round-9 findings under v11

**F1 (fatal, symlink typechange forges close shape) — HOLDS CLOSED.**
v11: *"the path's git mode is `100644` on both sides (a typechange to a
symlink, `T` in `--raw`, fails even though its target string could read like
a status line)"*. This directly rejects the `T`-typechange `--raw` entry
round-9 exploited (old mode `100644`, new mode `120000`, or vice versa) —
neither side is `100644`, condition trips. No residual re-opens it.

**F2 (important, unpinned live manifest read for the intent glob) —
PARTIALLY CLOSED, one sub-issue still open and unstated.**
v11: *"read from the running checker's own contract package (`MANIFEST_PATH`,
the plugin's file, never the repo under test; in this repo the two coincide),
exposed as one named constant so the glob has one source"*. Verified against
`_contract_dir()`/`MANIFEST_PATH` (loom_checker.py:44-57): the path is
resolved from `Path(__file__).resolve()`'s own siblings, not from the repo
argument or from `close_sha`'s tree — so for a real plugin install (checker
running out of `~/.claude/plugins/cache/...`) the glob source is now pinned
to the plugin's own bundled file and genuinely cannot be tainted by commits
to the repo under test. **The residual sentence is accurate**: in *this* repo
the checker's `scripts/` and `contract/` are siblings inside the same
tree being pushed, so the "two coincide" here, and the spec says so rather
than hiding it. That closes the *which-file* half of F2.
The *silent-fail-open-on-drift* half of round-9's F2 (round-9's own stated
Fix: "assert the manifest's intent path against a hardcoded expected literal,
failing closed, loudly, on drift") is **not addressed and not mentioned** by
v11 or by the resolution note in `review.json:1089`. `load_manifest()` is
still a live disk read with no assertion against an expected literal; a typo
or drift in `artifacts.intent.path` (in the plugin's own contract package,
independent of this repo) still makes `is_intent.match()` false forever after
and `check_close_commit_shape` returns `[]` indistinguishably from "no intent
path touched" — for every future close-commit, plugin-wide, not just in this
repo. This is a real, still-open gap the v11 sentence does not disclose.
Not closed — carry forward as important.

**F3 (important, `re.search` accepts trailing garbage) — HOLDS CLOSED.**
v11: *"the added one's value satisfying `STATUS.fullmatch` on its `closed`
alternative (trailing text outside the comment group fails)"*. Confirmed:
`fullmatch` on the full post-`status:` value rejects
`closed 2026-01-01 — PR #1 EXTRA-GARBAGE`, since the trailing text isn't a
`\s+#.*` comment. Probed whether a *second field* can hide inside the comment
group instead (`status: closed <date> — PR #<N> #status: open`): `.*` in the
comment group swallows it, but this can't smuggle a competing status value —
`fullmatch` still requires the whole non-comment prefix to be one grammar
alternative, and there is exactly one physical line (no embedded newline in a
diff line), so no second field can override the first. No new escape here.

**F4 (important, raw-line scan not scoped to frontmatter) — HOLDS OPEN under
a new variant (see §2, new finding N1); closed for the case round-9 actually
demonstrated.** v11: *"both located — by the hunk header's line numbers —
before the first `## ` heading of their respective file version (a body-text
decoy pair fails)"*. For a document with a normal, well-formed `## ` heading,
this closes round-9's exact scenario (decoy pair sitting in a body section
after the real heading now fails the before-heading test). But the same
mechanism — and the pre-existing `parse_document` it borrows the heading
concept from — degenerates when no real heading exists at all (§2 N1),
re-opening the class of attack under a document shape v11 does not name.

**F5 (important, structural trigger's broadened blast radius on ordinary
intent-lifecycle commits) — HOLDS CLOSED per the stated bar.** v11 rewords the
consequence from "may not edit an intent for any other reason" to *"may not
touch an intent for any other reason — not the decision-point-① confirmation
commit, not a new intent from `maintain`, not an amendment — such a commit
goes earlier, and the diagnostic says so"* and appends "(W1-01)". Verified
`docs/loom/2026-09-03-loom-post-merge-seams/plan.md:49` carries a real task,
`W1-01 ship／review 站文字：關閉順序與裁定的 sha`, whose job is to land this
exact consequence in `loom-code/skills/ship/SKILL.md` §6 (not yet written —
`grep` on ship/SKILL.md for this text returns nothing, consistent with build
not having started). The false-block itself is not eliminated (confirmation
and fresh-intent commits still trip the rule if they land at `HEAD^` right
before a checkpoint push) — but per the task's stated bar for F5, an explicit
consequence carried into a concrete station-text task satisfies it. Closed.

**Nit — subdirectory glob (`docs/loom/intent/sub/x.md` never matches) —
still unaddressed, still a nit.** v11 adds no note on this; `glob_to_regex`'s
`*` still doesn't cross `/`. No behavioral risk (round-9 already found this
moot in practice), just the documentation nit round-9 flagged. Open.

**F6/nit — `check_review_only_head` still uses `git show --raw` (not a
first-parent diff) for the real `HEAD` and, recursively, for `HEAD^^`'s
checkpoint check — inconsistent with the "never `git show`" principle stated
for the sibling close-commit check.** v11's diff touches none of this
function's code or prose. Still open, still nit-severity (fails closed on a
merge, doesn't open an escape).

## 2. New attacks on v11's new clauses

**N1 (fatal) — a headingless (or malformed-heading) intent document lets a
later, spurious `status:` line silently override the real one, in
`parse_document`'s own dict, defeating BOTH the pre-existing
transition-detection and the new before-heading boundary check at once.**

`parse_document` (loom_checker.py:268-291) does `front[match.group(1)] =
value` for every line matching `^status:\s*(.*)$` *until* it sees a line that
is exactly `"## "`-prefixed. If the file never has such a line (no `## `
heading at all — or the would-be heading is malformed, e.g. `##NoSpace`,
which fails the exact `"## "` test and is silently skipped as "not a heading,
not frontmatter either" since it starts with `#`), `current` never leaves
`None` and the *entire file* is scanned as candidate frontmatter — with a
plain dict assignment, so the **last** matching `status:` line wins, not the
first. `check_close_commit_shape`'s transition test (`before_closed`/
`after_closed`) reads `front.get("status")` off exactly this dict.

Construct (headingless before/after trees, real per-template headings never
required by any check here since the attacker fully controls both trees of
the fabricated commit):

```
# before
title: Some intent
status: confirmed 2026-01-01
status: stray line to delete

# after
title: Some intent
status: confirmed 2026-01-01
status: closed 2026-01-01 — PR #1
```

- Transition test: `before_front["status"]` = last match = "stray line to
  delete" → `before_closed = False`. `after_front["status"]` = last match =
  "closed 2026-01-01 — PR #1" → `after_match` succeeds, `after_closed = True`.
  `closing_path` is set — the rule believes a legitimate close just happened.
- Condition (1): one path touched. OK.
- Condition (2), diff on that path: exactly 1 removed
  (`status: stray line to delete`) / 1 added (`status: closed 2026-01-01 —
  PR #1`) line, both start with the literal bytes `status:`, the added one
  **passes `STATUS.fullmatch`** (it's a syntactically perfect closed line) —
  v11's F3 fix does not help here, the line really is well-formed.
- v11's new before-heading check: vacuously true for both — there is no
  `## ` heading in either tree, so "before the first heading" covers the
  whole file. v11's new mitigation does not help here either.
- The line that actually carries the intent's real, meaningful status —
  `status: confirmed 2026-01-01` — is **never touched by the diff at all**,
  is not removed, not added, sits there unchanged in both trees.

The consequence is not merely "the shape check is fooled": `intake.confirmed`
(REQ-2)'s own reopen detection (`git log -G'^status:[[:space:]]*closed '`)
and the trunk-copy check (`git show <trunk>:<path>` parsed the same way)
**also** run through `parse_document`'s same last-write-wins dict — so the
same document, if it lands on the trunk this way, is treated as genuinely
`closed` by every consumer of `parse_document`, not just by this one push
rule, even though the canonical first `status:` field still literally reads
`confirmed`. That is a full bypass of the closed/confirmed distinction the
whole REQ-1/REQ-2 mechanism exists to make trustworthy without a human
reading the diff — reachable by the same single-agent-crafts-history threat
model round-9's F1–F5 already treat as in-scope (this is not the "multi-user
repo cheating" or "admin pushes to trunk" class the intent's Out-of-scope and
Design decision 1's stated assumption explicitly carve out; it's a parser
weakness against adversarial *document shape*, the same class as the F1
symlink and F4 body-decoy attacks v11 was written to close).
**Fix**: `parse_document` should treat a duplicate frontmatter key as an
error (or at minimum `check_close_commit_shape` should independently assert
that `status:` appears exactly once in each of the before/after trees before
trusting `front.get("status")` for the transition test), and/or the
before-heading boundary check should refuse to validate a close commit at
all when no real `## ` heading is found in either tree, rather than treating
"no heading" as "everything qualifies."

**Mode-check edge cases probed and found to HOLD (no escape) — precisely
answering the four cases asked for:**
- *100755→100644 (chmod on an already-executable file, real content edit)*:
  correctly rejected — old mode is not `100644`, so a legitimately-shaped
  status transition on a file that happened to carry the executable bit
  throughout is refused. False block, not an escape (intent files are never
  expected to be executable; consistent with every other rule's fail-closed
  posture in this spec).
- *Submodule (mode `160000`)*: `--raw` reports mode `160000` on the gitlink
  side; the `100644`-both-sides check rejects it outright, and even without
  the mode check the diff body is `Subproject commit <sha>` lines, not
  literal `status:` text, so this is doubly closed.
  Consistent with the mode check applying to `closing_path` (already pinned
  to the one path condition (1) verifies) rather than to every touched path.
- *Path that is a directory in one parent, a file in the other*: git's
  `--raw` never emits a mode for a bare tree entry; the file-side endpoint
  shows as an `A`(dd) or `D`(elete) with the *absent* side reported as mode
  `000000`, not `100644` — the both-sides-`100644` check rejects it on the
  same basis as the submodule case (one side is provably not a regular
  blob).

**Frontmatter-boundary edge cases, remaining three from duty 2:**
- *Status line at exactly the heading's own line number* — the spec text
  does not say whether "before" is `<` or `<=` the heading's hunk line
  number; the only way a status line and a heading line coincide is if the
  hunk replaces the heading line itself with `## status: closed …`-shaped
  text, which would also change `current` in `parse_document` for anything
  after it — a genuinely odd, low-value edge the spec should pin down (nit,
  not escalated to a finding: no working exploit constructed, just an
  underspecified boundary).
- *`-U0` hunk header with a `,0` count* — moot for reaching the boundary
  check at all: condition (2) already requires exactly one removed and one
  added line in the *whole-file* diff before the boundary check runs, and a
  `,0`-count hunk (a pure insertion or pure deletion) cannot by itself supply
  both a removed and an added line, so this shape never reaches the new
  clause. Not an escape; a hunk-parsing detail with no live exploit.

## 3. Consistency (REQ-2, Design decision 1, Constraint)

No new rule id is introduced anywhere in v11's diff (still
`push.review-only-head`, the sole rule this sentence governs); the diff is
additive detail inside that rule's own recompute, matching the Constraint's
2026-09-03 exception ("允許把兩條既有規則加嚴" — tightening two named
existing rules, no new rule, no waiver). REQ-2's `STATUS` grammar,
`REOPEN_TRUNK_CANDIDATES`, and terminal-`closed` semantics are untouched by
this diff. Design decision 1's stated assumption ("the trunk receives only
merges… loom does not verify the PR number and does not check who can push
to the trunk… out of scope with the other multi-user cheating cases") is not
contradicted — N1 above is explicitly *not* one of those multi-user cases
(§2 argues this at length); it is a same-class parser weakness to the ones
v11 itself was written to close, so it does not fall under that carve-out
and is properly in scope for this review.

One accuracy note, not a Constraint violation: F2's still-open sub-issue
(§1) means the "the trigger is structural" framing in the amended sentence
slightly overstates robustness for the general (non-self-hosting) case too —
"structural" here still rests on an unpinned, unasserted live file read, just
one that's no longer the repo-under-test's own file. Worth a one-line
disclosure alongside the existing "in this repo the two coincide" clause the
next time this sentence is touched, but it does not itself break any of
REQ-2 / Design decision 1 / the Constraint.

Verdict: NEEDS_REVISION — fatal: 1, important: 2, nit: 3
