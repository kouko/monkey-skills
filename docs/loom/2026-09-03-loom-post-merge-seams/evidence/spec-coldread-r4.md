# Cold read — spec v5, round 4 (2026-09-03-loom-post-merge-seams)

## Acceptance #1 — close-intent-on-branch, push passes, intake blocks a closed intent

What I'd do: in a clean clone, follow ship's rewritten order — push branch, `gh pr create` (PR number known), commit `docs(loom): close intent <change-id>` changing `status:` to `closed <date> — PR #<N>`, run a review round over `reviewed_sha..close-commit`, commit review.json (review-only), push again. Then run `loom_checker.py intake write-plan 2026-09-02-simple-loom-flow` and expect a block naming "closed".

Enough to do without guessing the mechanics of push/intake? Yes for the intake side — REQ-2 gives the exact block message and the two reopen checks. For the review-round side, REQ-1 gives scope (`branch-end`), delta typing (`intent`), lens pair (docs + user-judgment-leak), reviewer count (two, fresh-context), what each verdict must additionally state (that the delta is the one status line, nothing else), what every verdict record's `sha` field must be (`<close commit>`), that no blind run is owed, and that probes are re-pinned at the close commit. That is a full recipe in prose — but the spec never names the *command* that starts a "branch-end" scoped round on a delta that isn't a checkpoint's normal task/wave boundary (loom-code:review's own description talks about "a checkpoint" or "branch end", not "one more commit after branch end"). I would have to guess whether this is literally the same `loom-code:review` invocation used at ship's own branch-end step, re-run a second time, or some other entry point.

Guess G1: which command/skill invocation actually performs "the review station runs one more round... scope `branch-end`" for a single one-line delta after the branch-end pass already happened — spec states the round's parameters but not how it is triggered (rerun of `loom-code:review`? A different flag?).

The "previous change closed inside this change's own diff" clause is concrete and checkable (I'd `git log` / read `docs/loom/intent/2026-09-02-simple-loom-flow.md` to see if `status: closed …` appears) — no guess needed there.

Verdict: mostly executable; one procedural gap (G1) on how the extra round is invoked.

## Acceptance #2 — `--list-rules` shows `closed`, full test suite green

What I'd do: run `loom_checker.py --list-rules` and grep for `closed` under `intake.confirmed`; run `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` locally and the CI job at `.github/workflows/loom-code-ci.yml:114` (verified: that line is inside the "Run pytest suites" step, `-v` variant, matches spec's citation).

Enough to do without guessing: yes, fully mechanical and both commands are named verbatim in REQ-2.

## Acceptance #3 — plumbing exemption is content-bound, not path-bound

What I'd do: in a clean Claude Code checkout (plugin cache present as canonical), run `codex_scaffold.py --repo .` to refresh `.codex/hooks/`, commit without a `Task:` trailer, run `loom_checker.py push` and expect it not to fire `push.dispatch-covers-tasks`. Then as a negative check: edit one character in a copied file / add a new file / delete a file / `chmod` a file under the scaffold output, commit, and expect the rule to fire on each of the four variants.

Enough to do without guessing: REQ-3 plus the Design decision's second bullet give the exact comparison algorithm (checker self-identifies via `Path(__file__).resolve()` + a sibling `../contract/manifest.yaml`, blob-compares `.codex/hooks/loom_checker.py`/`git_exec.py` against the source tree after stripping the stamp line, compares the stamp's version first, compares `.codex/hooks/loom-checker` against `codex_scaffold.SHIM_TEMPLATE`, compares each `contract/<rel>` file). This is unusually well specified for an agent-decided mechanism — I would not have to guess the shape of the check. One soft gap: the four negative variants (edit-a-byte / add-a-file / delete-a-file / mode-change) are named in Acceptance #3 itself but the spec's Design decision doesn't walk each one explicitly against the algorithm (e.g., which comparison catches a deleted file — presumably "a plumbing path with no canonical counterpart... fails the comparison" covers add, but the reverse — a canonical file present with no copy, i.e. deletion — isn't stated symmetrically).

Guess G2: whether a *deleted* scaffold file (canonical exists, copy missing) is caught by the same "content comparison" language, or needs its own presence check — the spec states the case for an *extra* file under `contract/` but not explicitly for a *missing* one.

## Acceptance #4 — checkpoint cost table + recommendation

What I'd do: build `docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md`, count commits/dispatches/rounds per checkpoint from `git log` and `review.json`, add `git rev-list --count <trunk>..HEAD`, compare to 34/31, write one recommendation line.

Enough to do without guessing: yes, REQ-4 and the Design decision ("written by the blind-runner... from git log and review.json") are concrete about source and content, though "per checkpoint" isn't formally defined (which commits belong to which checkpoint) — a minor judgment call, not flagged as a guess since the spec's own review station has checkpoint boundaries by convention (ship, build waves) that this repo's history already demonstrates.

## Acceptance #5 — plugin version bumps

What I'd do: bump `loom-code` to 1.0.1, `loom-design` to 1.0.1, `loom-workflow` to 4.0.1 in each `.claude-plugin/plugin.json`, add a CHANGELOG entry naming the change, then (device-side, not verifiable from the repo alone) run `claude plugin update` and check the cache path.

Enough to do without guessing: yes for the repo-side edits; the device-side verification step is explicitly a real machine action outside repo scope, correctly flagged by the spec as needing `claude plugin update` — not something I can execute from a clean clone alone, but that's inherent to the acceptance line, not a spec gap.

## Acceptance #6 — five carried test nits closed

What I'd do: open each cited anchor, make the described fix, run the package test command green.

Enough to do without guessing: **no — one clear mismatch.** See Anchors below; R28-O2 and R30-O1's cited lines (test_check_mechanisms.py:664 and :670) do not contain what the spec says is there ("check=True on the skip-guard probe"; "literal 5 asserted"). I could not identify R28-O2's actual referent anywhere in the file — there is no "skip-guard" concept, and no `check=True` call, anywhere in `test_check_mechanisms.py` outside two unrelated subprocess calls (lines 509, 691, both pre-existing git/scaffold plumbing, neither a "skip-guard probe").

Guess G3: where R28-O2's actual fix site is — the spec's line anchor is wrong and no textual match exists elsewhere in the file for "skip-guard probe" / `check=True`.
Guess G4: whether R30-O1 ("literal `5` asserted") is even still an open nit — the code at the cited location (`test_matches_python_split_not_bsd_wc`, ending at line 670) already computes the expected count dynamically via `len(self.SAMPLE.decode(...).split())` rather than asserting a literal `5`; the only literal `5` in the file is inside a prose comment ("4 vs 5") two lines earlier, not an assertion. This nit may already be resolved and mis-described, or the description names a different, unfound site.

## Anchors

| Anchor | Resolves? | Spec's claim vs. actual |
|---|---|---|
| `loom-code/skills/ship/SKILL.md:326-336` | Yes | Matches — lines 324-336 read "The status line cannot be written on the branch... it is written **after** the merge" with the exact commit recipe shown. |
| `loom-code/scripts/loom_checker.py:1557` (`check_review_only_head`) | Yes | Function starts exactly at line 1557. |
| `loom_checker.py:791` (`CONFIRMED` regex) | Yes | `CONFIRMED = re.compile(r"confirmed (\d{4}-\d{2}-\d{2})(\s+#.*)?")` is exactly line 791. |
| `loom_checker.py:825-835` (`intake.confirmed`) | Yes (approx) | The `confirmed = CONFIRMED.fullmatch(status)` check and its `intake.confirmed` failure message span roughly 823-836; close enough to be the right region. |
| `loom-code/scripts/test_loom_checker_intake.py:385-447` | Yes | `test_the_repos_own_change_matches_its_own_review_json` starts exactly at 385; docstring content matches spec's description (derives expected block from the repo's own intent/review state). |
| `docs/loom/2026-09-03-loom-post-merge-seams/evidence/ci-781-intake-confirmed.md` | Yes | File exists at that path. |
| `loom-code/contract/manifest.yaml:85` | Yes | Line 85 is exactly the `status` grammar row `"open \| confirmed <date> \| withdrawn — <reason>"`. |
| `loom-code/contract/templates/intent.md:7` | Yes | Line 7 is the `status: open # open \| confirmed <date> \| withdrawn — <reason>；缺＝open` comment. |
| `loom_checker.py:389-400` (`HOST_PLUMBING_FILES`/`_is_host_plumbing`) | Yes | `HOST_PLUMBING_FILES` at 389, `HOST_PLUMBING_DIR_PREFIX` at 397, `_is_host_plumbing` at 400. |
| `loom_checker.py:2085` (`commit_paths`) | Yes | Function starts exactly there; body confirms spec's parenthetical "(no plumbing filter)" — it does not call `_is_host_plumbing`. |
| `loom_checker.py:2095` (`check_dispatch_covers_tasks`) | Yes | Function starts exactly there. |
| `loom-code/scripts/codex_scaffold.py` (`SHIM_TEMPLATE`, `_checker_copy_content`, `CONTRACT_COPY`) | Yes | All three names present in the file. |
| `.github/workflows/loom-code-ci.yml:114` | Yes | Line 114 is the `run: python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -v` step, same paths as the local command with `-v` instead of `-q`. |
| `loom_checker.py:455` (R24-O2, "below"→"above") | Yes | Line 455 literally reads "...HOST_PLUMBING_DIR_PREFIX below), never a surface a user reads..." — and `HOST_PLUMBING_FILES`/`HOST_PLUMBING_DIR_PREFIX` are defined at 389/397, i.e. *above* this docstring, not below. Genuine nit, correctly anchored. |
| `test_check_mechanisms.py:664` (R28-O2, "`check=True` on the skip-guard probe") | **No** | Line 664 is a prose comment ("pinned to LC_ALL=C does not split on the CJK ideographic space") inside `test_matches_python_split_not_bsd_wc`. No `check=True` and no "skip-guard" concept appears anywhere in this file outside two unrelated, pre-existing subprocess calls at lines 509 and 691 (git/scaffold plumbing). Cannot resolve — see Guess G3. |
| `test_check_mechanisms.py:670` (R30-O1, "literal `5` asserted") | **No** | Line 670 is a closing `)` of the assert statement above it. The assertion at 668-670 (`assert cm.wc_words(self.SAMPLE) == len(self.SAMPLE.decode("utf-8", errors="replace").split())`) computes the expected value dynamically, not via a literal `5`. The only literal `5` on screen is in a prose comment two lines up ("4 vs 5"). Mismatch — see Guess G4. |
| `test_check_mechanisms.py:672` (R30-O2, "moot locale test... replaced by a guard") | Partial | Line 672 is `def test_count_is_stable_across_locales(self, monkeypatch):` — this is plausibly the test *to be* replaced (it still exists, unreplaced, at this line), which is consistent with an open nit whose fix hasn't landed yet. Anchor points at the right object but the spec's phrasing ("replaced by a guard...") describes the target state, not what's currently there — acceptable for a not-yet-fixed nit, unlike the two above where the described *current* content doesn't exist at all. |
| `test_session_start_words.py:49` (R30-O3, `_run` bytes/decode) | Yes | `def _run(cwd: Path) -> str:` is exactly line 49; it currently uses `text=True` and returns `proc.stdout`, consistent with "not yet fixed to capture bytes and decode with errors='replace'". |

Anchor-mismatch count: **2** (test_check_mechanisms.py:664 and :670 do not contain the content the spec attributes to them; :672 is a borderline "points at the right test but describes the target state" case, not counted as a hard mismatch).

## Guesses (total: 4)

- Guess G1: which command/entry point actually runs the extra "branch-end" scoped review round on the close commit — REQ-1 specifies every parameter of the round but not how it's invoked.
- Guess G2: whether a *deleted* scaffold file (canonical present, copy missing) is caught by the content-comparison mechanism, or needs a separate presence check — spec states the symmetric case (extra file) but not this one.
- Guess G3: where R28-O2's actual fix site is — no "check=True on the skip-guard probe" exists anywhere in test_check_mechanisms.py; the cited line 664 is unrelated prose.
- Guess G4: whether R30-O1 ("literal `5` asserted") is still open — the cited code already computes the expected value dynamically rather than asserting a literal 5.
