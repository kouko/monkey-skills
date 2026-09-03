# Cold read — spec v9, round 8 (2026-09-03-loom-post-merge-seams)

## Acceptance #1 (close-intent flow that pushes, plus its three negative cases + intake block + prior-change closure)

What I would do: on a clean clone, follow the order REQ-1 gives — push branch-end → `gh pr create` (PR number known) → commit `docs(loom): close intent <change-id>` changing `status:` to `closed <date> — PR #<N>` → invoke `loom-code:review` scope `branch-end` on `<reviewed_sha>..<close commit>` with two fresh reviewers (docs + user-judgment-leak lenses), each stating the delta is exactly that status line, each verdict recording `sha: <close commit>` → a review-only commit (`review.json` only, `reviewed_sha` = close commit) → push.

Expected: `loom_checker.py push` passes on existing rule ids (27 total), no `!` bypass, no new rule.

Negative A (skip the review round, point `reviewed_sha` straight at the close commit without a fresh round): expected block — `push.reviewed-sha` fails because the *latest round's* verdicts don't name the close commit as their `sha` (they were minted for an earlier commit). Spec gives this explicitly.

Negative B (close-intent commit changes one more character beyond the status line): expected block — `push.review-only-head`'s recompute of `git diff -U0 HEAD^^ HEAD^ -- <path>` no longer shows exactly one removed/one added `status:` line, so it refuses the shape. Spec gives this explicitly and even names it kouko's decision A.

Negative C (write-plan intake on the now-closed intent): expected block with message `intake.confirmed: … this change is closed (PR #<N>); a new change starts from a new intent`. Spec gives the exact message text for REQ-2's version of this message but Acceptance #1 just says "會被擋並說明" — close enough, no guess needed since REQ-2 supplies the literal string.

Also: the already-merged `2026-09-02-simple-loom-flow` intent (currently `confirmed`) gets closed by this same change's diff. I verified today's repo state: that intent file is not yet `closed` and the checker's `CONFIRMED` regex has no `closed` branch — consistent with this being unimplemented spec, nothing to guess.

**Guess G1**: Acceptance #1 does not spell out what "只重跑" a clean-clone sequence means operationally when there is no real PR yet to open (a cold walk-through can't actually call `gh pr create` against a throwaway fork without guessing at repo permissions/remote setup). I'd have to invent a stand-in "PR #<N>" value and a scratch remote to exercise this end-to-end; the spec assumes the ship station's own machinery exists to produce a real PR number, which is out of this document's control. Not fatal — REQ-1 describes the mechanism precisely enough to hand-simulate with a fabricated `<N>|<close-sha>`, but a literal clean-clone dry run needs a real GitHub round trip the spec doesn't hand me.

Everything else needed to implement/verify #1 (exact commit message, exact status grammar target, exact review round shape, exact rule names that fire) is fully specified — no further guess.

## Acceptance #2 (grammar shows `closed`; full test packages green)

What I would do: run `loom_checker.py --list-rules` and grep for `closed` under the intent status grammar description; then run `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q` locally and check the CI job `pytest + knowledge-drift + codex-manifest-drift` (`.github/workflows/loom-code-ci.yml:114`).

Expected: `--list-rules` describes `closed <date> — PR #<N>` under `intake.confirmed`; both test packages pass, including `test_the_repos_own_change_matches_its_own_review_json`.

Checked live: today's `CONFIRMED` regex (loom_checker.py:791) is `confirmed (\d{4}-\d{2}-\d{2})(\s+#.*)?` — no `closed` alternative yet; manifest.yaml:85 grammar is `open | confirmed <date> | withdrawn — <reason>` — no `closed` yet; template comment mirrors it. All three match the spec's "Current state evidence" claim exactly (pre-change state, expected to change under REQ-2). No guess: the exact regex, the exact `--list-rules` surface, and the exact test command are all named.

## Acceptance #3 (scaffold-refresh commit exempt from `push.dispatch-covers-tasks`; four negative variants: 1-char edit, extra file, deleted file, mode-only change)

What I would do: on a clean Claude-Code-side clone (plugin cache present as canonical), run `codex_scaffold.py --repo .` to refresh `.codex/hooks/`, commit with no `Task:` trailer, run `loom_checker.py push`.

Expected: passes — `push.dispatch-covers-tasks` does not fire, because REQ-3's content-bound-plus-canonical test says a scaffold-genuine refresh carries no trailer duty.

Negative 1 (edit one char in a plumbing file): blocked, blob no longer matches canonical.
Negative 2 (add an extra file under the plumbing dir): blocked — REQ-3 says "an altered, added, deleted or mode-changed entry... counts as gate work."
Negative 3 (delete a plumbing file): blocked — spec explicitly calls this out: "a deleted entry is in `commit_paths()` with no blob at the commit, so it fails the comparison."
Negative 4 (change only file permissions/mode, e.g. chmod +x on a plumbing file with unchanged content): blocked — spec explicitly says "the comparison is blob **and** mode ... a mode-only change fails like a content change."

Checked live: current code (`HOST_PLUMBING_FILES`, `HOST_PLUMBING_DIR_PREFIX`, `_is_host_plumbing`, `check_dispatch_covers_tasks`) filters by path only, with no blob/mode/canonical comparison yet (loom_checker.py:389-455, 2095+). This matches the "Current state evidence" claim of a path-only filter needing the content-bound-plus-canonical upgrade. No guess: the exact comparison mechanics (invoked-path self-identification, sibling `contract/` lookup, stamp-line-then-blob order, mode via `git show --raw`) are all spelled out in the Design decision paragraph.

## Acceptance #4 (checkpoint-cost table + recommendation)

What I would do: after this change's own branch is done, tabulate — per checkpoint (= one review-only commit touching only `review.json`) — commits, dispatches, review rounds, plus `git rev-list --count <trunk>..HEAD`, next to the #771 replay's 34/31, with one recommendation line, written into `docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md`.

Expected: the file and table exist with those columns; no coefficient is actually changed (REQ-4, Design decision "Checkpoint-cost table").

**Guess G2**: neither intent nor spec gives the exact column *order* or table format (Markdown table vs. list) for `checkpoint-cost.md` — REQ-4 says "one table" with named columns but not the header row wording, sort order, or whether the #771 comparison is a separate row or a footer line. I'd pick a straightforward Markdown table with checkpoints as rows and add a comparison row — a formatting choice, not a semantic gap, but the spec doesn't pin it.

## Acceptance #5 (plugin version bumps + observable after `plugin update`)

What I would do: bump `loom-code` to 1.0.1, `loom-design` to 1.0.1, `loom-workflow` to 4.0.1 in each `.claude-plugin/plugin.json`, add a CHANGELOG entry naming this change, then (device-side) `claude plugin update <plugin>@monkey-skills` and check `~/.claude/plugins/cache/monkey-skills/loom-code/1.0.1/scripts/loom_checker.py --list-rules` prints the `closed` grammar.

Expected: directory exists at the new version, `--list-rules` output includes `closed`. Fully specified — exact version numbers, exact path, exact check command all given. No guess.

## Acceptance #6 (five carried test nits)

What I would do: open each anchor and confirm a change or a recorded moot:
- R24-O2 — `loom_checker.py:455` docstring "below"→"above". I read lines 440-460 live: the current docstring says "This is scoped to those specific files, not to the whole `.codex/hooks/` directory" and references material *above* it in context (`HOST_PLUMBING_FILES` is defined right above, not below) — consistent with the nit description that this needs a wording fix; unfixed today, as expected for a spec not yet built.
- R28-O2 — I confirmed live: `check_mechanisms.py:582-587` `wc_words` is already Python `data.decode("utf-8", errors="replace").split()`, no `wc` subprocess, and `test_check_mechanisms.py` no longer contains any `check=True` wc-skip-guard probe at the old line — the round-30 rewrite already deleted it. REQ-6's "moot, nothing to fix" claim checks out exactly.
- R30-O1 — I read `test_check_mechanisms.py:668-670` live: `assert cm.wc_words(self.SAMPLE) == len(self.SAMPLE.decode("utf-8", errors="replace").split())` — this is indeed the RED oracle recomputing with the implementation's own expression (tautological), matching the nit description; not yet fixed (needs pinning literal `5` with a comment).
- R30-O2 — spec wants `check_mechanisms.py` guarded so no `subprocess` call names `wc`, via `inspect.getsource`. Not present yet in the file I read (no such guard test found in the grep). Consistent with unfixed state.
- R30-O3 — `test_session_start_words.py:49` `_run` — I read it live: `subprocess.run(["bash", str(HOOK)], ..., text=True)`. This decodes via the platform/locale default, not an explicit UTF-8 + `errors="replace"` decode. Matches the nit exactly — not yet fixed.

Expected outcome: four real fixes + one moot record, package command green. No guess — REQ-6 names every anchor, the current line numbers, and the exact target expression.

## The two tightenings as I would code them

**`push.reviewed-sha`** (in `check_reviewed_sha`, loom_checker.py ~1670, called from the section around line 1529-1536):
- JSON field read: `review["verdicts"]`, filtered to the latest round via `scored_verdicts(review)` (loom_checker.py:2265) — the same helper `check_verdicts` already uses — then within that round set, every verdict's `sha` field (new, additive to the manifest's `verdicts[]` grammar at manifest.yaml:120).
- Git command: resolve each verdict's `sha` and the existing `recorded = review.get("reviewed_sha")` to full git object ids — `git rev-parse <value>` (or the existing `git_text(repo, "rev-parse", ...)` pattern already used elsewhere in the file for `reviewed_id`), so a short hex prefix and a full sha compare equal.
- Comparison: every verdict's resolved `sha` object id must equal `reviewed_id` (the already-resolved `reviewed_sha`); a round with zero usable verdicts reports nothing here (that's `push.verdicts-ge-2`'s job, per spec's own words) — I'd guard with `if not latest_round_verdicts: return []` before the tie check.
- Failure message wording: the spec explicitly assigns this to me ("each failure message names the rule id, the offending commit or field and the value expected, in the implementer's words like every existing rule") — not a guess, spec says so.
- **Left to invent**: which specific helper resolves "the same round `scored_verdicts()` hands `check_verdicts`" into a *filterable* list I can iterate per-verdict for the `sha` field — `scored_verdicts` returns `tuple[int, list[dict]]` (count, list) per the grep; I'd reuse that list directly. This is mechanical, not a design guess.

**`push.review-only-head`** (in `check_review_only_head`, loom_checker.py ~1557):
- Git commands: `git diff --raw --no-renames HEAD^^ HEAD^` (never `git show`, spec is explicit about the merge-commit blind spot) to detect the file-set touched by `HEAD^` (the close commit) against its first parent; then `git diff -U0 HEAD^^ HEAD^ -- <that path>` to get the line-level diff.
- Regex: the added line must match "the `closed` alternative of the shared status regex" — i.e. the new `STATUS` regex's `closed` branch (REQ-2: `closed (\d{4}-\d{2}-\d{2})\s+—\s+PR #(\d+)` roughly, exact form not pinned character-for-character by REQ-2 beyond "closed <date> — PR #<N>" and "the em dash literal `—`" appearing in every example — I would write the regex directly from REQ-2's grammar string).
- Comparison: diff must touch exactly one file (an intent file), and that file's unified diff must be exactly one removed + one added line, both matching a `status:` line pattern, with the added one's value matching the closed branch.
- Additional recompute: `HEAD^^` (the close commit's parent) must itself be a checkpoint — touches only `review.json`, and that `review.json`'s `reviewed_sha` resolves to `HEAD^^^`. This is the same shape `check_review_only_head` already computes for `HEAD` itself, applied one commit up — I'd factor the existing single-file-touched check into a reusable helper and call it on `HEAD^^` too.
- Failure message wording: again explicitly the implementer's own words per spec — not a guess.
- **Left to invent**: the exact regex literal for the em dash / spacing tolerance (REQ-2 says "each alternative allowing the trailing `\s+#.*` comment `CONFIRMED` allows today" but doesn't spell out whether internal whitespace around `—` is `\s*—\s*` or a fixed `" — "`); and the exact refactor shape (new helper function vs. inline recursive call) for reusing the "checkpoint shape" check on `HEAD^^`. Both are ordinary implementation choices within a fully pinned behavioral contract, not directional guesses.

## Anchors

Opened and checked against the live repo (not the change's own evidence files, since I was told not to read those first):

- `loom-code/skills/ship/SKILL.md:326-336` — confirmed: prescribes the close commit **after** the merge, on `main` ("The status line cannot be written on the branch... after the merge"). Resolves — matches spec's claim exactly (this is the *pre-change* text the spec's Design decision says gets rewritten).
- `loom-code/scripts/loom_checker.py:1557` `check_review_only_head` — confirmed present, rejects any HEAD touching more than `review.json`. Resolves.
- `loom-code/scripts/loom_checker.py:791` `CONFIRMED` regex — confirmed: `confirmed (\d{4}-\d{2}-\d{2})(\s+#.*)?`, no `closed`. Resolves.
- `loom-code/scripts/loom_checker.py:825-835` `intake.confirmed` — confirmed present, only accepts `confirmed <date>`. Resolves.
- `loom-code/scripts/test_loom_checker_intake.py:385-447` `test_the_repos_own_change_matches_its_own_review_json` — confirmed present, derives expected block dynamically from spec/review state, no `closed` branch yet. Resolves.
- `loom-code/contract/manifest.yaml:85` grammar — confirmed: `open | confirmed <date> | withdrawn — <reason>` (line 85 in the file I read carries the `status` field grammar). Resolves.
- `loom-code/contract/templates/intent.md:7` — confirmed: comment mirrors the same three-way grammar, no `closed`. Resolves.
- `loom_checker.py:389-400` `HOST_PLUMBING_FILES` / `HOST_PLUMBING_DIR_PREFIX` / `_is_host_plumbing` — confirmed present exactly as described, path-only filter (no blob/mode compare yet). Resolves.
- `loom_checker.py:2085` `commit_paths` — confirmed present (found at a nearby line in my read, function body matches: `git show --raw --no-renames` listing). Resolves (I did not check the byte-exact line number 2085 vs. what my grep showed, which was ~2075-2095 window — the function is there and matches described behavior; treating as resolved since content, not exact line offset, is what matters for a spec anchor).
- `loom_checker.py:2095` `check_dispatch_covers_tasks` — confirmed present, docstring matches spec's description of current path-only exemption. Resolves.
- `loom-code/scripts/codex_scaffold.py` (`SHIM_TEMPLATE`, `_checker_copy_content`, `CONTRACT_COPY`) — not opened in this cold read (time-boxed); named symbols are plausible given `codex_scaffold.py` exists and is referenced consistently elsewhere in the anchors I did check. Not verified — I did not `grep` inside this file for the three exact symbol names.
- REQ-6 anchors: `test_check_mechanisms.py:664/670/672`, `test_session_start_words.py:49`, `loom_checker.py:455` — all opened and checked above (Acceptance #6 section); all resolve, including the R28-O2 "moot" claim (verified the probe truly no longer exists at that location).

**One anchor left unverified**: `codex_scaffold.py`'s `SHIM_TEMPLATE` / `_checker_copy_content` / `CONTRACT_COPY` symbol names (cited in the Design decision paragraph, not in "Current state evidence" proper) — I did not grep the file to confirm these three exact identifiers exist. Recorded as an open item, not a mismatch, since I did not check it either way.

## Guesses (total: 2)

- Guess G1: Acceptance #1's clean-clone walk-through implicitly needs a real `gh pr create` round trip to get a PR number; the spec's mechanism is fully pinned but a literal cold dry-run has to fabricate a stand-in PR number/remote, which is outside the spec's control to specify.
- Guess G2: `checkpoint-cost.md`'s exact table layout (column order, row grouping, whether the #771 comparison is a row or a footer) is not pinned by REQ-4 beyond naming the required columns.
