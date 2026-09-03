# Cold read — spec v7, round 6 (2026-09-03-loom-post-merge-seams)

Read alone: `docs/loom/intent/2026-09-03-loom-post-merge-seams.md` and
`docs/loom/2026-09-03-loom-post-merge-seams/spec.md`. No prior evidence
files opened before forming first impressions; anchors were then opened
against the live tree at commit e6f3062c to check they resolve.

## Acceptance #1 (REQ-1) — close-before-merge push shape, + 2 negative cases + reopen block

**What I'd do:** clean clone, get to a state where a branch-end review round
already passed (reviewed_sha = branch-end sha), push, `gh pr create` to get
`<N>`, then commit `docs(loom): close intent <change-id>` changing
`status: confirmed <date>` → `status: closed <date> — PR #<N>`, dispatch two
fresh reviewers (docs + user-judgment-leak lens) on that one commit, record
their verdicts with `sha: <close-commit>` in a new round, re-pin probes,
write a review-only commit moving `reviewed_sha` to the close commit, push.

**Expect:** `loom_checker.py push` passes with no `!` bypass and no new rule
id. Negative (a): if I skip the extra review round and hand-edit
`reviewed_sha` in review.json to point straight at the close commit, push
should block. Negative (b): if I add one more change to the close commit
(e.g. touch a second file, or reword the Problem section too), push should
block even though `reviewed_sha` still names that commit. Then:
`loom_checker.py intake write-plan 2026-09-03-loom-post-merge-seams` on the
now-closed intent should block with the exact message REQ-2 gives.

**Enough to do it without guessing?** Mostly, but not fully:
- Guess G1: REQ-1 never gives the literal wording of the two new
  `push.reviewed-sha` / `push.review-only-head` failure messages — I would
  have to invent them (see the coding section below).
- Guess G2: it never states how many failures fire when BOTH negative cases
  are true at once (e.g. skip-review AND multi-line close commit) — do both
  rule ids report, or does the recompute short-circuit on the first one? I
  assumed both report, since nothing says otherwise.
- Otherwise the sequence, the field names (`sha`, `reviewed_sha`), the
  comparison semantics ("as git object ids"), and the exact intake message
  are all given precisely enough to implement without asking.

## Acceptance #1 negative — reopen after close (REQ-2)

**What I'd do:** on a branch carrying the close commit (or cut from a trunk
whose ref already has the merge), run
`loom_checker.py intake write-plan <change-id>` and expect the block
message `intake.confirmed: <change-id> was closed (PR #<N>) and closed
intents are not reopened; start a new intent`.

**Enough?** Yes for the message text and the two detection paths (branch
history via `git log -G`, trunk ref via the four-name fallback). Guess G3:
the exact `-G` pattern string to render from the "closed" regex alternative
isn't given — REQ-2 says "rendered from the status regex's own `closed`
alternative (same whitespace tolerance)" but not the literal pattern
string or how "whitespace tolerance" (single space? any run of spaces?
tabs?) is expressed in a `-G`/extended-regex argument to `git log`. I'd
have to pick one.

## Acceptance #2 (REQ-2) — grammar + tests green

**What I'd do:** run `loom_checker.py --list-rules`, grep for `closed`
under `intake.confirmed`; run
`python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` locally
and push the branch to trigger the CI job named
`pytest + knowledge-drift + codex-manifest-drift`.

**Enough?** Yes — REQ-2 names the two files to edit (`manifest.yaml`,
`templates/intent.md`), the exact date/`<N>` validation reuse
(`is_real_date()`, positive integer), and the exact package command twice
(local + CI, same paths, CI just adds `-v`). No guess needed beyond G3
above, which recurs here since it's the same regex-rendering machinery.

## Acceptance #3 (REQ-3) — scaffold-refresh commit exempt only with matching canonical

**What I'd do:** clean clone with the plugin checkout available (Claude
Code side), run `codex_scaffold.py --repo .` alone, commit with no `Task:`
trailer, run `loom_checker.py push` — `push.dispatch-covers-tasks` should
not fire on that commit. Then four variants — edit one byte inside a copied
file, add an extra file under `.codex/hooks/contract/`, delete one of the
scaffolded files, and `chmod` one scaffolded file without touching its
content — each committed separately, and each should still trip
`push.dispatch-covers-tasks`.

**Enough?** Almost. The Design decision spells out the comparison
(`.codex/hooks/loom_checker.py`/`git_exec.py` vs `<contract dir>/…`, blob
**and** mode, symlink mode `120000` never exempt, stamp-version check
before blob compare) in enough detail to code directly. Guess G4: it names
the stamp format (`# loom-checker <version>`) and says compare it "after
… stripping" it, but doesn't say where the running checker's own version
string comes from for that stamp-vs-running-version comparison (a
module-level constant? read from `plugin.json`? from `manifest.yaml`?) — I
would have to find or invent that source myself.

## Acceptance #4 (REQ-4) — checkpoint-cost table

**What I'd do:** at branch end, gather from `git log`/`review.json` for
this change: per-checkpoint commit count, dispatch count, review-round
count, plus `git rev-list --count <trunk>..HEAD`; write the table into
`docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md`
next to the #771 replay's 34/31, with one recommendation line and no
coefficient change.

**Enough?** Yes, fully — no invented mechanics, this is a straight
tabulation task with the source data (`git log`, `review.json`) named.

## Acceptance #5 (REQ-5) — plugin versions bumped and observable

**What I'd do:** bump `loom-code/.claude-plugin/plugin.json` to `1.0.1`
(currently `1.0.0`), same for loom-design and loom-workflow to `1.0.1` /
`4.0.1` (currently `1.0.0` / `4.0.0` — confirmed by reading the files),
add a CHANGELOG entry each naming this change, then on the device side run
`claude plugin update <plugin>@monkey-skills` and confirm
`~/.claude/plugins/cache/monkey-skills/loom-code/1.0.1/` exists and its
`loom_checker.py --list-rules` shows the closed grammar.

**Enough?** Yes — version numbers and target paths are exact.

## Acceptance #6 (REQ-6) — five carried test nits

**What I'd do:** fix `loom_checker.py:455`'s docstring ("below"→"above" —
confirmed the current text does say "below" while `HOST_PLUMBING_FILES` is
defined *above* `changed_paths`, so the nit is real); record R28-O2 moot
with a note (confirmed: the `check=True` target it names no longer exists
after round 30's rewrite — the current `TestWcWordsIsPythonSplit` class at
`test_check_mechanisms.py:650` has no such probe); pin the literal `5` in
the RED-oracle comment at `test_check_mechanisms.py:668`; replace the
locale test at `test_check_mechanisms.py:672` with an
`inspect.getsource(check_mechanisms)`-based guard that no `subprocess`
call names `wc`; make `_run` in `test_session_start_words.py:49` capture
bytes and decode UTF-8 with `errors="replace"`. Then run the package
command green.

**Enough?** Yes — REQ-6 plus the Design decision paragraph together give
file, line, and the fix mechanism for all five with no gaps.

## The two tightenings as I would code them

**`push.reviewed-sha`** (in `check_reviewed_sha`, `loom-code/scripts/loom_checker.py`):
- Field: `review["verdicts"]`, each entry's new optional/required `sha` key
  (manifest.yaml `verdicts` grammar gains `sha` — additive, per the Design
  decision).
- Determine the latest round the same way `check_verdicts`/`scored_verdicts`
  already does (`round_number, verdicts = scored_verdicts(review)`).
- For every verdict in that round whose `scope` (lowered/stripped) is not
  `spec`:
  - if `str(entry.get("sha", "")).strip()` doesn't match
    `SHA_HEX = re.compile(r"[0-9a-f]{7,40}")` (the pattern already in the
    file), fail.
  - else resolve it: `git_maybe(repo, "rev-parse", "--verify", f"{sha}^{{commit}}")`.
  - compare the resolved object id to `reviewed_id` (the same
    `reviewed_id` `check_reviewed_sha` already resolves from
    `review["reviewed_sha"]`) — string-equal git object ids, exactly the
    style the existing HEAD^ comparison uses.
  - On mismatch/missing, append `("push.reviewed-sha", <message>)`.
- **Invented (Guess G1a):** the message text. I'd write something like
  `f"round {round_number} verdict by {entry['reviewer']} (scope "`
  `f"{scope or '(none)'}) has no sha; every non-spec verdict must name "`
  `"the commit it reviewed."` for the missing case, and
  `f"round {round_number} verdict by {entry['reviewer']} sha {sha[:8]} "`
  `f"resolves to {resolved[:8]} but reviewed_sha is {reviewed_id[:8]}; "`
  `"this round reviewed an older delta."` for the mismatch case — neither
  string is given in the spec.
- **Invented (Guess G1b):** whether "verdicts of the latest round" means
  literally the max `round` number across all verdict entries, or the max
  round among the *scored* ones `scored_verdicts` already filters to
  (dismissed/fallback entries excluded). I assumed the latter, reusing
  `scored_verdicts`, but the spec doesn't say which round-selection
  function this new check rides on.

**`push.review-only-head`** (in `check_review_only_head`,
`loom-code/scripts/loom_checker.py`):
- After the existing single-file-touches-review.json check on `head_sha`
  passes, additionally inspect `head_sha^` (the close commit candidate):
  `listing = git_text(repo, "show", "--raw", "--no-renames", "--pretty=format:", f"{head_sha}^")`,
  parsed into a path set the same way `commit_paths` already does.
- Resolve the intent artifact glob from the manifest the way
  `check_review_only_head` already resolves the review glob:
  `is_intent = glob_to_regex(manifest["artifacts"]["intent"]["path"].replace("<change-id>", "*"))`.
- For each touched path matching `is_intent`, pull the commit's patch for
  just that file: `git_text(repo, "show", "--no-color", f"{head_sha}^", "--", path)`
  (or `git diff <head_sha>^^ <head_sha>^ -- <path>`), and look for an added
  line matching a `CLOSED` regex analogous to the existing `CONFIRMED`
  regex, e.g. `re.compile(r"^\+status:\s*closed\s+(\d{4}-\d{2}-\d{2})\s*—\s*PR\s*#(\d+)")`
  against diff lines.
- If a closed-status line is found: require (a) `len(touched) == 1`
  (nothing else touched at `head_sha^`), and (b) exactly one added line and
  one removed line in that file's diff hunk (counting lines starting with
  `+`/`-` but not `+++`/`---`) — i.e. the whole diff is a single-line
  replace.
- On violation, append `("push.review-only-head", <message>)`.
- **Invented (Guess G5a):** the exact regex for the added `status:` line —
  literal em-dash `—` vs a looser `[-—]`, and how many spaces are tolerated
  around it — not given, same gap as G3 above (it's the "closed" grammar
  regex problem recurring a second place).
- **Invented (Guess G5b):** "the diff must change exactly that one line" —
  I read this as "exactly one `+` and one `-` content line in the file's
  hunk", but a `git diff` for a one-line edit can also legally show a
  single `@@` hunk with one changed line represented as adjacent -/+ pairs
  when context lines shift; the spec doesn't give the counting algorithm,
  so a different valid encoding (e.g. via `--word-diff` or a numstat check
  `1\t1\t<path>` from `git diff --numstat`) is equally defensible and I'd
  have picked one without being told which.
- **Invented (Guess G5c):** the message text, e.g.
  `f"HEAD^ introduces a closed status but touches {detail}; a close "`
  `"commit must touch exactly one intent file and change exactly its "`
  `"status: line."` — not given.

## Anchors

Opened every "Current state evidence" citation and both REQ-6 citation
sets against the live tree (commit e6f3062c). All resolve to what the
spec says they show:

- `loom-code/skills/ship/SKILL.md:326-336` — confirmed: still prescribes
  closing the intent **after** the merge, on `main` ("The status line
  cannot be written on the branch…").
- `loom-code/scripts/loom_checker.py:1557` — confirmed: `def
  check_review_only_head(...)`.
- `loom_checker.py:791` — confirmed: `CONFIRMED = re.compile(r"confirmed
  (\d{4}-\d{2}-\d{2})(\s+#.*)?")`.
- `loom_checker.py:825-835` — confirmed: the `intake.confirmed` block that
  only accepts `status: confirmed <date>`.
- `loom-code/scripts/test_loom_checker_intake.py:385-447` — confirmed:
  `test_the_repos_own_change_matches_its_own_review_json`, dynamically
  derives the expected block set, no `closed` branch yet.
- `evidence/ci-781-intake-confirmed.md` — confirmed: exists, shows the CI
  red (`intake.confirmed`, status "closed 2026-09-03 — PR #780") and the
  `push.review-only-head` block from the same session.
- `loom-code/contract/manifest.yaml:85` — confirmed: `status` grammar is
  `open | confirmed <date> | withdrawn — <reason>` (no `closed`).
- `loom-code/contract/templates/intent.md:7` — confirmed: comment mirrors
  the same grammar minus `closed`.
- `loom_checker.py:389-400` — confirmed: `HOST_PLUMBING_FILES`,
  `HOST_PLUMBING_DIR_PREFIX`, `_is_host_plumbing` all present as described.
- `loom_checker.py:2085` — confirmed: `def commit_paths(...)`.
- `loom_checker.py:2095` — confirmed: `def check_dispatch_covers_tasks(...)`.
- `codex_scaffold.py` (`SHIM_TEMPLATE`, `_checker_copy_content`,
  `CONTRACT_COPY`) — confirmed: all three exist (lines 117, 210, 96
  respectively), and `SHIM_TEMPLATE.format(stamp=..., checker=CHECKER_COPY)`
  at line 253 matches the Design decision's claim about the literal
  `{checker}` argument.
- REQ-6 anchors — all five confirmed:
  - `loom_checker.py:455` — `changed_paths` docstring does say
    "HOST_PLUMBING_FILES … below" while those constants are defined above
    (line 389) — the nit is real.
  - `test_check_mechanisms.py:664` (R28-O2) — the class at line 650
    (`TestWcWordsIsPythonSplit`) has no `check=True` skip-guard probe left;
    consistent with "moot, deleted by the round-30 rewrite."
  - `test_check_mechanisms.py:668-670` (R30-O1) — the RED-oracle assertion
    does recompute against `cm.wc_words(...)` vs. the implementation's own
    `str.split()` expression, not a pinned literal.
  - `test_check_mechanisms.py:672` (R30-O2) — `def
    test_count_is_stable_across_locales` is the still-present locale test
    to be replaced.
  - `test_session_start_words.py:49` — `def _run(cwd)` currently uses
    `text=True` (string decode via the default locale codec), not an
    explicit `errors="replace"` byte-decode — matches "not yet fixed."
- `.github/workflows/loom-code-ci.yml:114` — confirmed: line 114 is the
  pytest run step (`python3 -m pytest loom-code/scripts/ scripts/
  .claude/hooks/ -v`), and the job at line 86 is literally named `pytest +
  knowledge-drift + codex-manifest-drift`, matching REQ-2's citation
  exactly.
- Plugin versions (REQ-5 baseline) — confirmed currently `1.0.0` /
  `1.0.0` / `4.0.0` for loom-code/loom-design/loom-workflow, consistent
  with the spec's bump targets `1.0.1`/`1.0.1`/`4.0.1`.
- `TRUNK_CANDIDATES` (REQ-2's `REOPEN_TRUNK_CANDIDATES` design note) —
  confirmed: `TRUNK_CANDIDATES = ("origin/main", "main", "origin/master",
  "master", "@{upstream}")` at line 376, trailing `@{upstream}` present as
  the spec describes, and `REOPEN_TRUNK_CANDIDATES` (the new, narrower
  constant) does not exist yet — consistent with it being new work.

**Anchor-mismatch count: 0.** Every citation checked resolves to what the
spec claims it shows.

## Guesses (total: 8)

- Guess G1 (=G1a+G1b counted as one guess-point each below): the two new
  `push.reviewed-sha` failure messages are not given, and which round
  filter the new check rides on (`scored_verdicts`'s scored round vs. the
  raw max `round` number) is not stated.
- Guess G2: whether both negative-case rule ids fire together, or one
  short-circuits the other, when both faults are present at once.
- Guess G3: the literal `-G` pattern string (and its exact whitespace
  tolerance) to render from the "closed" status regex for the reopen
  history search — reused twice (Acceptance #1's reopen block and
  Acceptance #2's grammar work).
- Guess G4: where the running checker's own version string comes from for
  the stamp-line comparison in the scaffold-copy exemption (REQ-3).
- Guess G5 (=G5a+G5b+G5c): the exact `status:`-line-closed regex used by
  `push.review-only-head`'s new recompute, the counting algorithm for
  "changes exactly that one line," and that check's failure message text.

Counting each bullet as one guess: **8** (G1a, G1b, G2, G3, G4, G5a, G5b,
G5c).
