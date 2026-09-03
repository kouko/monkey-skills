# Adversarial red-team — REQ-1 `push.review-only-head` amended sentence (spec v10)

Target commit: `3048021afb388c11f54344f33c1c600b745c1b2f`
Code referenced throughout is the **committed** `loom-code/scripts/loom_checker.py`
at `HEAD` (read via `git show HEAD:loom-code/scripts/loom_checker.py`), since the
working tree copy is stated to be mid-edit. Where the spec's design differs from
what `HEAD`'s code currently does, that is treated as an in-progress build gap,
not scored against the spec — findings below are about the *design the amended
sentence describes*, whether the description is internally sound and whether the
mechanism it prescribes actually delivers what its own prose claims.

## 1. Trigger

**F1 (fatal) — symlink swap forges a close-commit shape.** Neither
`check_close_commit_shape`'s condition (1) (`touched != [closing_path]`) nor
condition (2) (the raw removed/added `status:` line check) inspects git mode —
`_raw_diff_paths` / `git diff --raw --no-renames` reports a regular→symlink
typechange as a single `T` entry on the same path, and `git diff -U0` on that
pair prints the old text as one removed line and the new symlink's *target
string* as one added line, exactly like an ordinary content edit. A symlink
whose target text is literally `status: closed <date> — PR #<N>` therefore
produces "1 path touched, 1 removed / 1 added `status:` line, added line matches
the closed alternative" — passing every check this rule (old content-based *and*
new structural) performs, without a real intent document ever containing that
status anywhere. Reproduced concretely:

```
git init -q /tmp/x && cd /tmp/x
git config user.email a@a; git config user.name a
printf 'status: confirmed 2026-01-01\n' > f.md && git add f.md && git commit -qm base
git rm -q f.md
ln -s "status: closed 2026-01-01 — PR #1" f.md   # target text, not a real path
git add f.md && git commit -qm close
git diff --raw --no-renames HEAD^ HEAD     # -> ":100644 120000 <old> <new> T  f.md" (ONE path)
git diff -U0 HEAD^ HEAD -- f.md            # -> exactly 1 "-status:..." / 1 "+status:..." line
```
This is exactly the class the amendment's own justification lists ("a rename, a
deletion, a BOM, a second `status:` line" — every way of making the diff *look*
like an ordinary close without the eye seeing real content) — a mode/type swap
is a sibling of that list and is left open.
**Fix**: reject any close-commit path whose old or new git mode is not `100644`
(read the mode fields already present in the `--raw` line, or `git ls-tree` the
path at both endpoints) in condition (1) or (2).

**F2 (important) — the glob that defines "an intent path" is read from a live,
mutable file, not pinned to the commit under test.** `_cmd_push` calls
`load_manifest()` once from disk (`repo`'s current `loom-code/contract/manifest.yaml`
at whatever HEAD the working tree/cwd is on), and `check_close_commit_shape`
derives `is_intent` from `manifest["artifacts"]["intent"]["path"]` *at that live
read* — never from `close_sha`'s or `head_sha`'s own tree. If any commit earlier
in history (not necessarily HEAD^ itself, and not necessarily reverted) changes
`artifacts.intent.path` in a way that no longer matches the real intent file's
path (a typo, a directory rename that ships ahead of a mass-move, or a
deliberate narrowing), `is_intent.match(real_path)` becomes false forever after
that edit lands and stays live. `intent_paths` is then empty, and
`check_close_commit_shape` returns `[]` — **indistinguishable from "HEAD^
legitimately touched no intent file at all."** This is not introduced by this
amendment (the pre-amendment content-based code derives `is_intent` from the
exact same live-manifest read), but the amended sentence's prose now presents
the glob match as the entire trigger ("the trigger is structural… if that diff
touches any path matching the intent artifact template") without noting that
the template itself is unpinned, mutable, ordinary-editable contract content —
so the sentence overclaims the trigger's robustness.
**Fix**: assert `manifest["artifacts"]["intent"]["path"]` against a hardcoded
expected literal (failing closed, loudly, on drift) before using it to build
`is_intent`, or read the manifest from `close_sha`'s own tree rather than the
live checkout.

**Path-template edge cases probed and found to HOLD (no escape):**
- *Extension/case mismatch* (`foo.MD`, `foo.md.bak`): `glob_to_regex` anchors
  with `\Z` and matches literal `.md` case-sensitively, so these never match —
  but they also never match anywhere else the schema resolves "the" intent
  path (`artifact_path()` uses the identical template), so a stray file at
  such a path is simply not the governing intent artifact anywhere in the
  system. No exploit.
- *Case-insensitive filesystem*: irrelevant — every comparison here is over git
  tree object paths (`git diff --raw`, `git show <sha>:<path>`), which are
  byte-exact regardless of host filesystem case folding.
- *Subdirectory* (`docs/loom/intent/sub/x.md`): `*` in `glob_to_regex` does not
  cross `/`, so this never matches `docs/loom/intent/*.md`. Moot in practice
  (no legitimate intent artifact is ever resolved at such a path by any other
  part of the checker), but worth a one-line note in the spec now that this
  workstream's stated goal is enumerating every masquerade path (nit).
- *Merge at `HEAD^`*: the amendment already fixed this specific case (round 7,
  spec-R23) by diffing `HEAD^^..HEAD^` as a two-tree diff rather than
  `git show HEAD^`, so a second-parent's content is captured in the tree diff
  regardless of how HEAD^ was constructed. Confirmed sound for the *close
  commit itself*. See F6 below for a residual `git show` use elsewhere.
- *Mode-only change* (chmod, no content diff): correctly rejected — 0
  removed/0 added lines fails condition (2)'s "exactly 1/1" requirement, so a
  mode-only touch to the intent path as HEAD^ is refused, not silently passed.
- *Empty diff with the path in `--raw`*: doesn't arise — git's raw diff only
  lists a path when something about it (blob, mode, or existence) actually
  differs between the two trees.

## 2. Raw-line rule

**F3 (important) — condition (2)'s regex check is `re.search`, not anchored
against the whole value, so it accepts a closed line with trailing garbage the
canonical grammar rejects.**

```python
python3 -c "
import re
_STATUS_CLOSED_ALT = r'closed (\d{4}-\d{2}-\d{2}) — PR #(\d+)'
STATUS = re.compile(r'(?:open|confirmed (\d{4}-\d{2}-\d{2})|' + _STATUS_CLOSED_ALT + r'|withdrawn — .+)(?:\s+#.*)?')
line = 'status: closed 2026-01-01 — PR #1 EXTRA-GARBAGE-NOT-A-COMMENT'
val = line[len('status:'):].strip()
print('fullmatch (real grammar):', STATUS.fullmatch(val))
print('search (close-commit-shape check):', re.search(_STATUS_CLOSED_ALT, line))
"
# -> fullmatch: None        (the value is NOT a legal STATUS per REQ-2's own grammar)
# -> search:    <Match ...> (check_close_commit_shape's condition (2) accepts it anyway)
```
The added line `status: closed 2026-01-01 — PR #1 EXTRA-GARBAGE-NOT-A-COMMENT`
starts with `status:` (passes the raw-prefix check) and *contains* the closed
alternative as a substring (passes `re.search`), so it is accepted as a valid
close-commit shape — even though `STATUS.fullmatch` (the grammar `intake.confirmed`
and every other rule actually enforces on the real frontmatter value) rejects
it outright, because the trailing text after the PR number isn't a `\s+#…`
comment. The amended sentence's own prose promises "the added one matching the
closed alternative of the shared status regex" — implying the same grammar
used elsewhere — but the code delivers a looser substring test.
**Fix**: validate with `STATUS.fullmatch(added[0][1:].strip()[len("status:"):].strip())`
(or `re.fullmatch(_STATUS_CLOSED_ALT + r"(?:\s+#.*)?", …)`), reusing the exact
grammar object rather than a bare `re.search` on the raw line.

**F4 (important) — the raw-line scan is not scoped to the frontmatter region,
so a body-text decoy can satisfy the shape check while the real `status:` field
never changes.** Condition (2) runs `git diff -U0` over the *whole file* and
classifies any `+`/`-` line that, after `.strip()`, starts with `status:` —
with no reference to `parse_document`'s frontmatter/body boundary (the region
before the first `## ` heading). A commit whose real frontmatter `status:`
line is untouched, but which (a) adds one line of body prose that happens to
start with `status: closed <date> — PR #<N>` (e.g. inside a Design-decision
paragraph describing the future close) and (b) removes some unrelated
pre-existing body line that also happens to start with `status:` (plausible in
a doc that discusses the status grammar itself, or trivially plantable),
produces exactly the "1 removed / 1 added, both `status:`, added matches
closed" shape this rule looks for — while the intent's real status stays
`confirmed`. This is the same class the amendment's stated rationale singles
out ("every way of making the parser see something other than what the eye
sees") — a fake `status:`-shaped line sitting in prose is exactly that, and it
remains open because raw-line matching, unlike frontmatter parsing, has no
concept of "inside the frontmatter" at all.
**Fix**: locate the frontmatter/body boundary structurally first (reuse
`parse_document`'s own split, which needs no value-level parsing to find the
boundary), and restrict the raw removed/added-line scan to lines before that
boundary in both trees.

**Probed and found to HOLD:**
- Hunk headers (`@@ … @@`) never start with `+`/`-`, excluded correctly.
- `\ No newline at end of file` starts with `\`, excluded correctly (verified:
  a real symlink-swap diff above produces exactly this marker line and it is
  correctly not counted toward `removed`/`added`).
- CRLF on the removed line only: `.strip()` strips the trailing `\r` along
  with other whitespace before the `startswith("status:")` check, so a
  CRLF-only removed line is still recognized. No escape.

## 3. Legitimate flows

**F5 (important) — the structural trigger's blast radius covers every touch to
an intent path, not just alternate edits to an already-known status line, and
that includes flows this repo's own skills document as routine.**

`loom-code/skills/ship/SKILL.md` documents decision-point-① confirmation:
> "1. Write `status: confirmed <date>` into the intent… 2. Commit with the
> message `docs(loom): intent <change-id> confirmed`."

and `loom-code/skills/maintain/SKILL.md` documents writing a brand-new intent:
> "Copy `${CLAUDE_PLUGIN_ROOT}/contract/templates/intent.md` to
> `docs/loom/intent/<slug>.md` and fill it in… commit."

Both are ordinary, single-purpose commits that touch a path matching
`docs/loom/intent/*.md`. Neither is a close transition — a fresh intent add has
no "before" text at all (many added lines, not one), and `open`→`confirmed`
does not match the closed alternative. Under the amended structural trigger, if
either commit happens to land as literally `HEAD^` immediately before *any*
review-only push (plausible for a small/fast change, or simply by coincidence
of commit ordering — the rule fires on every push, not only the dedicated
close-intent flow), condition (2) fails ("expected 1 removed / 1 added
`status:` line… got 0 removed / N added") and the push is refused — even though
the commit has nothing to do with closing anything.

The amended sentence states the consequence plainly — "the last commit before
a review-only commit may not edit an intent for any other reason — such an
edit goes in an earlier commit, and the diagnostic says so" — but its wording
("edit… for any other reason") reads as scoped to *editing an already-existing
status line differently*, not to *creating* a new intent or *confirming* one.
The mechanism's actual reach is broader than the sentence's own framing
suggests, and it lands squarely on two flows named in the station files above.
**Fix**: either state explicitly (in the amended sentence, not left implicit)
that intent creation and confirmation are included in "may not edit an intent
for any other reason," so an implementer sequencing commits knows to keep those
away from the position right before a checkpoint push; or narrow the trigger to
fire only when the value on that path actually changes to something
closed-shaped (requiring a "before" text to exist and differ), so a fresh add
or a confirm never enters the close-commit-shape gate at all.

W1-04 (closing the previously-merged `2026-09-02-simple-loom-flow` intent
inside this same change's diff, per REQ-2's own text) is **not** broken by this
rule — it is precisely the shape the rule is designed to accept, provided it is
committed alone and immediately precedes its own review-only commit, which is
how the spec already describes it.

## 4. Constraint and principles

The intent's Constraints (`docs/loom/intent/2026-09-03-loom-post-merge-seams.md`)
state: "不加新規則、不放寬任何規則" (no new rule, no relaxing any rule), with an
explicit 2026-09-03 user-decided exception permitting **tightening** two named
existing rule ids — no new rule id is introduced by this amendment, and it
reuses `push.review-only-head` throughout, so it is compliant on that literal
count.

Whether it stays a pure tightening is not clean, however:
- F3 and F4 are not new relaxations *introduced* by this amendment (the
  underlying condition-2 code — the raw `-U0` scan and the `re.search` call —
  is unchanged by the diff; only the *selection* of which commits get
  subjected to it changed, from content-detected transitions to any touch).
  But the amended sentence's prose describes condition (2) with a confidence
  ("both beginning with the literal bytes `status:` compared as raw lines…
  the added one matching the `closed` alternative of the shared status
  regex") that overstates what the shared code actually verifies — this is a
  spec-accuracy defect against the sentence under review, independent of
  whether the underlying gap predates this commit.
- F5 is arguably an *unintended* broadening beyond "the closing-transition
  shape" into "almost every intent-path touch," which is disclosed in the
  sentence's own consequence clause but not scoped to match the
  Constraint's implicit target (tightening the close-commit check, not
  blocking unrelated intent lifecycle commits). This is a design-completeness
  gap for review, not a rule id violation.

Repo-root `PRINCIPLES.md` is a product constitution (Who / Non-negotiables /
Won't do / Fixed choices for product/design trade-offs) and does not speak to
this engineering/checker mechanism; nothing in it is implicated either way.

**F6 (nit) — `check_review_only_head` (used both for the real push `HEAD` and,
recursively, for validating `HEAD^^` as a checkpoint in condition (3)) still
uses `git show --raw --no-renames --pretty=format: <sha>`.** `git show` on a
merge commit suppresses paths that are "uninteresting" relative to either
parent by default, which is exactly the failure mode the amendment's own
round-7 justification (spec-R23) cites for abandoning `git show` in the
close-commit diff itself. If `HEAD` or `HEAD^^` is ever a merge, this call can
report zero touched paths and the push fails closed (blocks) rather than being
bypassed — not an escape, but an inconsistency with the "never `git show`"
principle the amendment states for the sibling check, worth aligning for
uniformity even though it costs nothing security-wise today.

Verdict: NEEDS_REVISION — fatal: 1, important: 4, nit: 2
