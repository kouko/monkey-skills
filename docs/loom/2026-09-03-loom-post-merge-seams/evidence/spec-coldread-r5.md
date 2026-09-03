# Cold read — spec v6, round 5 (2026-09-03-loom-post-merge-seams)

## Acceptance 1 — close-commit sequence pushes clean; intake blocks the closed intent; previous change closed too

What I'd do: in a clean clone, follow the order REQ-1 gives — push, `gh pr create`
(number now known), commit `docs(loom): close intent <change-id>` changing
`status:` from `confirmed <date>` to `closed <YYYY-MM-DD> — PR #<N>`, invoke
`loom-code:review` again with `scope: branch-end` over `<reviewed_sha>..<close
commit>`, get two fresh-context reviewers under the docs + user-judgment-leak
lenses (each must say the delta is that one line), a review-only commit that
moves `reviewed_sha` to the close commit, then push again. Then run
`loom_checker.py intake write-plan 2026-09-03-loom-post-merge-seams` and expect
the `intake.confirmed` block naming the intent closed.

Enough to do without guessing: yes, once I cross-checked it against
`loom-code/skills/review/SKILL.md`. That file's scope table (`branch-end` →
`ship`, delta `<reviewed_sha>..HEAD`) and its artifact-type table's `intent` row
(`docs + user-judgment-leak | yes | no | no`) match REQ-1's claims word for
word — the "no blind run because the delta is intent-typed" line is not an
invented exception, it is the standing table. The procedural sequence (push →
PR → close commit → review round → review-only commit → push) is stated in
full, in order, with what each verdict must record (`sha: <close commit>`).
The one thing REQ-1 itself flags as not machine-checked — "the delta is that
one status line" is a reviewer's claim, not a rule's recomputation — is named
by the spec as a residual, not hidden; I did not have to discover that gap
myself.

Guess: none.

## Acceptance 2 — `--list-rules` shows `closed`; the two packages' tests are green locally and in CI

What I'd do: run `loom_checker.py --list-rules` and grep its `intake.confirmed`
description for `closed`; run `python3 -m pytest loom-code/scripts/ scripts/
.claude/hooks/ -q` locally, and check the CI job named in REQ-2
(`.github/workflows/loom-code-ci.yml:114`, `pytest + knowledge-drift +
codex-manifest-drift`) is green on the PR.

Enough to do without guessing: yes. REQ-2 names the exact package command,
the exact CI job and file:line, and states the equivalence condition itself
("only the exit code must agree") so I don't have to decide how strictly to
compare local vs CI output.

Guess: none.

## Acceptance 3 — scaffold-refresh commit needs no trailer; any content change to the copy still needs one

What I'd do: in a clean clone with the plugin checkout available (Claude Code
side), run `codex_scaffold.py --repo .` with nothing else changed, commit
without a `Task:` trailer, and check `loom_checker.py push` does not fire
`push.dispatch-covers-tasks` on that commit. Then, separately, edit one byte
in a file under `.codex/hooks/contract/`, add a new file there, delete one, or
just `chmod` one and commit — each time expecting the same rule to fire.

Enough to do without guessing: yes for three of the four counter-cases
(byte edit, added file, deleted file) — REQ-3 states the deleted-entry case
explicitly ("a deleted entry is in `commit_paths()` with no blob at the
commit, so it fails the comparison like any other mismatch"). The
mode-only-change case is named in the Acceptance line itself but I found no
sentence in REQ-3 or the Design decision paragraph that says how a pure
`chmod` (content identical, mode different) is supposed to fail the blob
comparison — a git blob comparison by content, as literally described
("the copy's stamp line... and the path's blob at the commit equals that
canonical file"), would not by itself distinguish a mode change from no
change at all, since blob shas don't encode file mode.

Guess G1: REQ-3 doesn't say whether the comparison also checks the git file
mode (extract `:100644`/`:100755` from `--raw`) alongside blob content, or
whether a mode-only change is caught some other way (e.g. `commit_paths()`
already lists the path from `--raw`, and possibly the mode-changed line still
shows a filemode-change entry that is treated as "not empty" without a blob
comparison at all — but this isn't stated). I would guess "yes it's checked"
to make the Acceptance line pass, rather than know it from the spec.

## Acceptance 4 — checkpoint-cost table exists with a recommendation line

What I'd do: open `docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md`
and check for one table (commits/dispatches/rounds per checkpoint),
`git rev-list --count <trunk>..HEAD`, the #771 comparison numbers (34/31),
and one recommendation line, with no coefficient actually changed anywhere
else in the diff.

Enough to do without guessing: yes. REQ-4 states path, contents, and that the
Design decision assigns authorship to the blind-runner at branch end (not the
implementer), which also tells me who should have written it when I check.

Guess: none.

## Acceptance 5 — plugin versions bumped and installed cache reflects them

What I'd do: check each `.claude-plugin/plugin.json` for 1.0.1/1.0.1/4.0.1
and a CHANGELOG entry naming this change; after `claude plugin update` check
`~/.claude/plugins/cache/monkey-skills/loom-code/1.0.1/` exists and that its
`loom_checker.py --list-rules` prints the `closed` grammar.

Enough to do without guessing: yes, exact versions and exact path given.

Guess: none.

## Acceptance 6 — five nits closed, one recorded moot, package green

What I'd do: for R24-O2 check `loom_checker.py:455`'s docstring says "above"
not "below"; for R28-O2 check the record states it's moot with a reason (not
a code fix); for R30-O1 check the RED oracle pins the literal `5` with a
comment about LC_ALL=C giving 4, instead of recomputing via `str.split()`
itself; for R30-O2 check a guard exists asserting (via
`inspect.getsource(check_mechanisms)`, per the Design decision) that no
`subprocess` call in the module names `wc`; for R30-O3 check `_run` in
`test_session_start_words.py:49` captures bytes and decodes UTF-8 with
`errors="replace"` rather than `text=True`. Then run the package command and
expect it green.

Enough to do without guessing: yes for what "fixed" means at each of the four
real anchors — each has a stated before/after. For R28-O2, the spec states
plainly, in bold, that it is moot and why ("the round-30 rewrite of
`wc_words` to Python `str.split` deleted that probe, so there is nothing to
fix and the record says so instead of pretending a fix") — that is stated
clearly enough that I would not guess at whether a fix is still owed there.

Guess: none.

## Anchors

All twelve distinct anchors cited in "Current state evidence" and the five (four real + one moot) in REQ-6 were opened. Every one resolves to the line/content the spec says is there. Mismatch count: **0**.

- `loom-code/skills/ship/SKILL.md:326-336` — matches: prescribes the close commit *after* the merge on the trunk (the current, unfixed order this change replaces).
- `loom-code/scripts/loom_checker.py:1557` (`check_review_only_head`) — matches: rejects a HEAD touching anything but `review.json`.
- `loom_checker.py:791` (`CONFIRMED` regex) — matches: `confirmed (\d{4}-\d{2}-\d{2})(\s+#.*)?`, no `closed` branch yet (current state, correctly cited as what REQ-2 extends).
- `loom_checker.py:825-835` (`intake.confirmed`) — matches: only accepts `confirmed <date>` today.
- `loom-code/scripts/test_loom_checker_intake.py:385-447` (`test_the_repos_own_change_matches_its_own_review_json`) — matches: derives its expected block dynamically from the intent/spec state, no `closed` branch yet.
- `evidence/ci-781-intake-confirmed.md` — exists at the cited path.
- `loom-code/contract/manifest.yaml:85` — matches: `status` grammar is `open | confirmed <date> | withdrawn — <reason>`.
- `loom-code/contract/templates/intent.md:7` — matches: same grammar in the template comment.
- `loom_checker.py:389-400` (`HOST_PLUMBING_FILES` / `HOST_PLUMBING_DIR_PREFIX` / `_is_host_plumbing`) — matches; `_is_host_plumbing` itself starts exactly at line 400.
- `loom_checker.py:2085` (`commit_paths`) — matches, `def commit_paths` at line 2085.
- `loom_checker.py:2095` (`check_dispatch_covers_tasks`) — matches, `def check_dispatch_covers_tasks` at line 2095.
- `loom-code/scripts/codex_scaffold.py` (`SHIM_TEMPLATE`, `_checker_copy_content`, `CONTRACT_COPY`) — all three names found in the file (96, 117, 210).
- REQ-6 anchor `loom_checker.py:455` (R24-O2) — matches exactly: line 455 is `HOST_PLUMBING_DIR_PREFIX below), never a surface a user reads --`, and `HOST_PLUMBING_DIR_PREFIX` is in fact defined *above* this docstring (line 397) — confirms the nit is real and still unfixed at v6.
- REQ-6 anchor `test_check_mechanisms.py:664` (R28-O2, moot) — the file at that region now (`TestWcWordsIsPythonSplit`, lines 650–678) contains no `wc`-subprocess call and no `check=True` skip-guard probe at all; the round-30 rewrite genuinely removed the target. The "moot" claim checks out and is stated clearly (bold, with the one-sentence reason) rather than left ambiguous.
- REQ-6 anchor `test_check_mechanisms.py:668-670` (R30-O1) — resolves to `test_matches_python_split_not_bsd_wc`'s assertion, which today still recomputes with `cm.wc_words(...) == len(SAMPLE.decode(...).split())` — i.e. the implementation's own expression, exactly the un-fixed state R30-O1 describes as the problem to fix.
- REQ-6 anchor `test_check_mechanisms.py:672` (R30-O2) — resolves to `def test_count_is_stable_across_locales`, the still-present "moot locale test" REQ-6 says gets replaced by the `inspect.getsource` guard; not yet replaced, consistent with an unimplemented fix target.
- REQ-6 anchor `test_session_start_words.py:49` (R30-O3) — resolves to `_run`'s `subprocess.run(..., capture_output=True, text=True)`, i.e. still `text=True` rather than bytes + explicit UTF-8 decode with `errors="replace"` — the un-fixed state R30-O3 targets.

Design-decision cross-checks that also held up (not required by the task but verified while anchors were open): the `intent` row of the review artifact-type table (`docs + user-judgment-leak | yes | no | no`) and the `branch-end` scope-table row both match REQ-1 verbatim; `TRUNK_CANDIDATES` at `loom_checker.py:376` does include `@{upstream}` last, matching REQ-2's claim that the new reopen check deliberately excludes it while `branch_base` keeps it.

## Guesses (total: 1)

- **Guess G1** (Acceptance #3, mode-only change): REQ-3 and its Design decision describe the trailer exemption as a content/blob comparison ("the copy's stamp line... and the path's blob at the commit equals that canonical file"). Acceptance #3's fourth counter-case is "只改檔案權限再 commit" (change only file permissions) and expects the same rule to still fire. A pure git blob-sha comparison does not by itself see a file-mode change (blob content is identical). Neither REQ-3 nor the Design decision paragraph states that the mode is compared too, or names an alternate mechanism (e.g. treating any non-empty `--raw` diff line for the path as disqualifying, independent of blob equality) that would make the mode-only case fail the same way as content changes. What's missing: one sentence saying whether/how mode is part of the comparison.
