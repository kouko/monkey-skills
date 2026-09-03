# Cold read — spec v8, round 7 (2026-09-03-loom-post-merge-seams)

## Acceptance #1 (ship-order push success + three negative cases + intake block + prior intent closed)

**What I would do:** In a clean clone, follow REQ-1's rewritten ship order: push the branch-end round → `gh pr create` → commit the close (`status: closed <date> — PR #<N>`) → re-invoke `loom-code:review` scope `branch-end` on `<reviewed_sha>..<close commit>` with two fresh reviewers each stating the delta is exactly the one status line, every verdict carrying `sha: <close commit>` → a review-only commit (`reviewed_sha` = the close commit) → push again.

**Expected:** `loom_checker.py push` passes with no `!` bypass and no new rule.

**Does the spec give me enough?** Yes for the happy path — REQ-1 plus the Design decision paragraph name every field (`sha` on verdicts, `reviewed_sha` tie, the two tightened rule ids) and REQ-2's grammar addition. I do not have to invent the field names or the comparison target.

**Negative case A — skip the review round, point `reviewed_sha` straight at the close commit:** Spec says `push.reviewed-sha` requires every verdict of the latest round to carry `sha` that resolves to the same object id as `reviewed_sha`; if the round is skipped there is no fresh round naming that sha at all, so the existing "latest round" the checker finds is the branch-end round, whose verdicts' `sha` (once fixtures are updated to carry `sha`, per Design decision) name the pre-close commit, not the close commit — mismatch, rule fires. Enough detail — no guess needed.

**Negative case B — alter a character in the close commit, then push:** `push.review-only-head`'s described recompute is exact: touches exactly one file (the intent), the diff against parent is exactly one removed + one added `status:` line, added line matches the `closed` alternative of `STATUS`. An edited char anywhere else in the file, or a second changed line, breaks "exactly one removed and one added line" or the added-line regex match. Enough detail.

**Negative case C — intake write-plan on the closed intent:** REQ-2's terminal behavior: message `intake.confirmed: <change-id> was closed (PR #<N>) and closed intents are not reopened; start a new intent`. Exact wording given.

**Guess G1:** The Acceptance line's own parenthetical negative wording differs slightly from REQ-2's message text — Acceptance #1 says intake blocks and "說明「這個 change 已關閉」" (paraphrase, Chinese, informal) while REQ-2 gives the literal English string. I take REQ-2's literal string as authoritative since Acceptance is user-language paraphrase and REQ-2 is the engineering-precise version — not really a guess, but flagging that a literal implementer reading only Acceptance #1 would not know the exact wording without cross-referencing REQ-2. No blocking guess needed since REQ-2 supplies it.

**Prior intent closed:** REQ-2 states `2026-09-02-simple-loom-flow` is closed inside this change's own diff — a straightforward one-line edit, no invented behavior needed.

**Verdict:** enough without guessing.

## Acceptance #2 (contract grammar has `closed`; test suites green)

**What I would do:** Grep `--list-rules` output for `closed` under the status grammar description; run `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` locally, and check the CI job named in REQ-2.

**Expected:** grammar string exactly `open | confirmed <date> | closed <date> — PR #<N> | withdrawn — <reason>`, all green.

**Does the spec give me enough?** Yes — REQ-2 states the exact regex name (`STATUS` replacing `CONFIRMED` at `loom_checker.py:791`), each alternative's trailing-comment allowance, the shared consumers (`intent.schema`, `intake.confirmed`, `push.review-only-head`), the terminal-block message text, the two-case reopen recompute (`-G` pattern rendered from the grammar; `git show <trunk>:<path>` against `REOPEN_TRUNK_CANDIDATES`), and even names the exact command and CI job. No guess needed.

**Verdict:** enough without guessing.

## Acceptance #3 (scaffold-only commit exempt from trailer; four negative variants — content, add, delete, mode)

**What I would do:** In a Claude-Code-side clean clone (plugin cache present as canonical), run `codex_scaffold.py --repo .` to refresh `.codex/hooks/`, commit with no `Task:` trailer, run `loom_checker.py push` — expect `push.dispatch-covers-tasks` silent on this commit. Then separately: (a) hand-edit one char in a copied file and commit, (b) add an extra file under the copied set, (c) delete one of the copied files, (d) `chmod` one copied file with no content change — each committed alone — and expect the rule to fire each time.

**Does the spec give me enough?** Yes — the Design decision paragraph for REQ-3 is unusually explicit: it names `Path(__file__)` without `.resolve()` as the self-identification method, the exact canonical paths (`../contract/manifest.yaml`, `.codex/hooks/loom_checker.py` vs `<dir>/loom_checker.py`, the shim vs `SHIM_TEMPLATE`), that comparison is blob **and** mode via `git show --raw`, that a symlink (mode 120000) is *never* exempt "whatever it points at", and that a deleted entry is caught because it's in `commit_paths()` with no blob to compare. All four negative variants (content, add, delete, mode) are explicitly pre-answered in prose, matching Acceptance #3's own note that round 2/3 reviewers demanded exactly these cases be spelled out.

**Verdict:** enough without guessing.

## Acceptance #4 (checkpoint-cost table + recommendation, no coefficient change)

**What I would do:** After the branch is done, tally per-checkpoint commits/dispatches/review-rounds from `git log` and `review.json`, plus `git rev-list --count <trunk>..HEAD`, write the table to `docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md`, add one recommendation line, and leave the coefficient itself untouched.

**Does the spec give me enough?** REQ-4 gives the file path, the required columns, the comparison baseline (34/31 from #771), and states the decision is deferred — no coefficient edit. It does **not** give a table format/column-header spec or say how "review rounds" is counted per checkpoint (does a round that fails and repeats count once or per attempt?) — but that is presentation license, not behavior the acceptance line tests; I would not guess-block on it, I'd just count every round entry in `review.json` per checkpoint tag, which is the only recomputable definition available.

**Guess G2:** No explicit definition of "per checkpoint" boundary (i.e., which `review.json` round entries belong to which checkpoint when checkpoints aren't separately tagged in the JSON) — I'd infer checkpoint boundaries from `dispatch[]` task/role clusters or round-number ranges bounded by review-only commits, but the spec never names a field that marks a checkpoint identity in `review.json`. This is a genuine gap for the implementer building the table script.

**Verdict:** mostly enough; one guess (G2) needed for table construction mechanics, not for the accept/reject test itself.

## Acceptance #5 (plugin version bumps observable after `claude plugin update`)

**What I would do:** Bump `loom-code` → 1.0.1, `loom-design` → 1.0.1, `loom-workflow` → 4.0.1 in each `.claude-plugin/plugin.json` with CHANGELOG entries; on the device side run `claude plugin update <plugin>@monkey-skills`, check `~/.claude/plugins/cache/monkey-skills/loom-code/1.0.1/` exists, and run `--list-rules` from that path to see the `closed` grammar.

**Does the spec give me enough?** Yes — REQ-5 gives exact version numbers, exact plugin.json/CHANGELOG targets, exact cache path, exact verifying command. No guess needed.

**Verdict:** enough without guessing.

## Acceptance #6 (five test nits, one moot, package green)

**What I would do:** Fix R24-O2 (docstring "below"→"above" at `loom_checker.py:455`), skip R28-O2 as moot with a note (the target `check=True` probe no longer exists after round 30's `wc_words` rewrite — confirmed true; I read `test_check_mechanisms.py:655-680` above and the `check=True` skip-guard probe is not present, matching "moot"), fix R30-O1 (pin literal `5` with a comment that `wc` under `LC_ALL=C` gave 4), R30-O2 (guard via `inspect.getsource(check_mechanisms)` asserting no `subprocess` call names `wc`), R30-O3 (`_run` decodes with `errors="replace"` at `test_session_start_words.py:49`) — then run the full package command.

**Does the spec give me enough?** Yes — REQ-6 and the Design decision's "Test nits" bullet both give exact file locations, exact fix descriptions (including the `inspect.getsource` mechanism for R30-O2), and explicitly pre-empt the "is R28-O2 still there" question by asserting it is moot and telling the implementer to record that rather than force a fix. I verified this against the actual file (see Anchors) — the moot claim about the RED test at `test_check_mechanisms.py:660-675` line matches what's on disk.

**Verdict:** enough without guessing.

## The two tightenings as I would code them

### `push.reviewed-sha` (verdict-sha tie)

- **Function to extend:** `check_reviewed_sha(repo, head_sha, recorded, reviewed_id)` at `loom_checker.py:1670`, called from `push.reviewed-sha`'s call site at `loom_checker.py:1536` (`check_verdicts` is a sibling call at `:1540`, not the same function — the tie-in has to reach both `scored_verdicts()`'s output and `reviewed_id`/`recorded` in the same rule).
- **JSON field:** `review["verdicts"][i]["sha"]` on every entry returned by `scored_verdicts(review)` (the function defined at `loom_checker.py:2265`, already filtering to the latest round and to entries with a readable `reviewer`+`verdict`) — spec says "the same round `scored_verdicts()` hands `check_verdicts`", so the implementer is told explicitly to reuse that function's output rather than re-deriving "latest round."
- **Comparison:** for every verdict entry in that latest-round list, `git rev-parse <entry["sha"]>` (or the same `git_exec` resolve helper `check_reviewed_sha` already uses at `:1687` via `reviewed_id`) must equal the already-resolved `reviewed_id` (the object id `reviewed_sha` resolves to) — "compared as git object ids, like `reviewed_sha` itself" — i.e. full 40-char sha string equality after resolution, not string-prefix compare on the raw JSON value.
- **Failure case:** an entry with no `sha` at all, or a `sha` resolving to a different commit, fails; a `spec`-scope round is "never a round a push can ride on" — meaning if the latest round is spec-scoped, this rule should fail unconditionally for that round (spec-scope verdicts carry `spec_sha` not `sha`) rather than skip the check.
- **Where I'd have to invent:** the spec gives the semantics fully but not the failure message wording for this specific rule (it only says "each failure message names the rule id, the offending commit or field and the value expected, in the implementer's words like every existing rule") — the exact string is explicitly the implementer's to write, by the spec's own statement, so this doesn't count as a guess.
- **One real gap:** the spec doesn't say whether an *empty* latest-round list (all entries unreadable) should report via this new sha-tie failure or fall through silently to the existing `push.verdicts-ge-2` "0 distinct reviewers" failure already emitted by `check_verdicts`. I'd guess: let `check_verdicts` own that case (it already handles `len(reviewers) < 2`) and only iterate `verdicts` for the sha tie when the list is non-empty, to avoid a duplicate/confusing message. Recording this as a guess.

**Guess G3:** whether the new sha-tie check should also fire (with its own message) when the latest round has zero usable verdicts, or defer entirely to `push.verdicts-ge-2`'s existing message for that case. Spec doesn't disambiguate; I'd defer to avoid double-reporting, but that's my call, not the spec's.

### `push.review-only-head` (close-commit shape recompute)

- **Function to extend:** `check_review_only_head(manifest, repo, head_sha)` at `loom_checker.py:1557` — currently only checks "exactly one file, and it's `review.json`". The tightening adds a branch for when `HEAD^` (not `HEAD`) introduces a `closed` status.
- **Trigger detection:** `git show --raw --no-renames HEAD^` (spec's own wording) — parse the raw listing the same way `check_review_only_head` already does at `:1564-1571` (split on tab, strip `:` prefix) to get the touched-path set for `HEAD^`; among those paths, read the new blob content via `git show HEAD^:<path>` and regex-match its `status:` line against the `closed` alternative of the shared `STATUS` regex (from REQ-2) to decide "introduces a `closed` status."
- **Single-file check:** that commit (`HEAD^`) must touch exactly one file — reuse the same `len(touched) == 1` pattern already in `check_review_only_head`, applied to `HEAD^`'s listing instead of `HEAD`'s.
- **Diff-shape check:** `git diff -U0 HEAD^^ HEAD^ -- <that path>` — spec names this exact command — parse the unified diff output: must contain exactly one line starting with `-` (excluding the `---`/`+++` file headers) and exactly one starting with `+`, both matching a `status:` line pattern, and the added line's value matching the `closed` alternative of `STATUS`.
- **Parent-is-checkpoint check:** `HEAD^^` must itself satisfy both shapes already checked for `HEAD`: (a) touches only `review.json` (same `check_review_only_head` logic, applied to `HEAD^^`), and (b) that `review.json`'s `reviewed_sha` resolves to `HEAD^^^` (same `check_reviewed_sha` resolve-and-compare logic, applied at that older commit rather than the live push's `HEAD`).
- **Comparison type:** file-path set equality (`{that path}` exactly, not `⊇`), added/removed unified-diff line counts (exactly 1 each), object-id equality for the `reviewed_sha`↔`HEAD^^^` tie (same style as `push.reviewed-sha`), and regex fullmatch against `STATUS`'s `closed` alternative for the added line's value.
- **Where I'd have to invent:** exact failure message text again — explicitly the implementer's own words per spec. Also: the precise regex used to strip the diff's leading `-`/`+` marker and locate the `status:` key inside the unified-diff line (e.g., matching `^-status:` / `^\+status:` after the `-U0` no-context output) isn't spelled out char-for-char — but the shape ("both `status:` lines") is unambiguous enough that this is implementation detail, not a design gap.
- **Non-checkpoint-parent case:** if `HEAD^^` is NOT itself a checkpoint (fails (a) or (b) above), spec says: "no commit can sit between the last checkpoint and the close commit without a checkpoint of its own" and "a close commit or parent of any other shape is refused" — so the rule fails, citing that `HEAD^^` doesn't have the checkpoint shape.

**No further guesses needed for the tightenings themselves** — both are specified down to the exact git commands and comparison semantics; only the human-readable failure wording is left open, and the spec itself says that's the implementer's, not a guess.

## Anchors

All anchors cited in "Current state evidence" and REQ-6 were opened and checked against the current repo state (branch `loom-post-merge-seams`, HEAD `d7fd6d44`):

| Anchor | Resolves? | Note |
|---|---|---|
| `ship/SKILL.md:326-336` (post-merge close prescription) | Yes | Lines 326-340 show exactly this: "close the intent... written after the merge" with the git snippet the spec describes as being rewritten away |
| `loom_checker.py:1557` `check_review_only_head` | Yes | Function starts at line 1557 exactly, one-file-only check as described |
| `loom_checker.py:791` `CONFIRMED` regex | Yes | Line 791 is exactly `CONFIRMED = re.compile(...)`, matches described current (pre-tightening) grammar |
| `loom_checker.py:825-835` `intake.confirmed` | Yes (line numbers shifted by ~1-2 lines internally but the described logic — reads `status`, matches `CONFIRMED`, else blocks with the "accepts only `confirmed <date>`" message — is exactly at that location) | Minor: the blank line at 825 pushes the actual `if not intent_path.is_file()` guard to 826; not a mismatch, just off-by-one in a multi-line span citation |
| `test_loom_checker_intake.py:385-447` `test_the_repos_own_change_matches_its_own_review_json` | Yes | Function starts exactly at 385, body matches the described dynamic-derivation logic (spec_scoped rounds, freshness via blob sha, `expected` set) |
| `manifest.yaml:85` status grammar | Yes | Line 85: `{name: status, ... grammar: "open | confirmed <date> | withdrawn — <reason>"}` — exactly the pre-`closed` grammar the spec says will be replaced |
| `contract/templates/intent.md:7` status comment | Yes | Line 7: `status: open  # open | confirmed <date> | withdrawn — <reason>；缺＝open` |
| `loom_checker.py:389-400` `HOST_PLUMBING_FILES`/`_is_host_plumbing` | Yes | Exact match, including the four files and the dir-prefix constant |
| `loom_checker.py:2085` `commit_paths` | Yes | Line 2085 is exactly `def commit_paths(repo: Path, sha: str) -> set[str]:` |
| `loom_checker.py:2095` `check_dispatch_covers_tasks` | Yes | Line 2095 is exactly `def check_dispatch_covers_tasks(...)` |
| `evidence/ci-781-intake-confirmed.md` | Yes | File exists in `docs/loom/2026-09-03-loom-post-merge-seams/evidence/` |
| `test_check_mechanisms.py:664/670/672` (R28-O2/R30-O1/R30-O2) | Yes, with the moot claim confirmed | R28-O2's target `check=True` skip-guard probe is genuinely absent from the current file (viewed lines 655-680); the RED oracle test at ~661-670 recomputes with the implementation's own expression as described |
| `test_session_start_words.py:49` (R30-O3) | Yes | Line 49 is inside `_run()`, matches the described capture/decode helper location (the exact `errors="replace"` line is a few lines further in the same function, consistent with "R30-O3 ... :49" naming the function's start) |
| `loom_checker.py:455` `changed_paths` docstring (R24-O2) | Yes | Line 455 is exactly `def changed_paths(repo: Path) -> set[str]:` with the docstring beginning immediately after, containing the "below" the spec says needs to become "above" |
| `scored_verdicts()`/`check_verdicts()` (REQ-1's "the same round `scored_verdicts()` hands `check_verdicts`") | Yes | `scored_verdicts` at line 2265, `check_verdicts` at line 2278, called at line 1540; `check_verdicts` does call `scored_verdicts(review)` internally exactly as the spec's phrase implies |

**Anchor-mismatch count: 0** (one line-span citation, `:825-835`, is off by roughly one line internally due to a blank line, but the cited function and message content are exactly where the spec says — not counted as a mismatch since the multi-line span still contains the described logic).

## Guesses (total: 3)

- **Guess G1** (Acceptance #1): the exact wording a literal implementer sees for the intake-block message differs between Acceptance #1's Chinese paraphrase and REQ-2's literal English string — resolved by treating REQ-2 as authoritative, not a blocking gap.
- **Guess G2** (Acceptance #4): no field in `review.json` marks checkpoint identity, so "per checkpoint" row construction for the cost table requires inferring checkpoint boundaries from round numbers / review-only commits rather than reading a named field.
- **Guess G3** (the `push.reviewed-sha` tightening): whether the sha-tie check emits its own failure or defers to the existing `push.verdicts-ge-2` message when the latest round has zero usable verdicts — spec doesn't disambiguate this edge case.
