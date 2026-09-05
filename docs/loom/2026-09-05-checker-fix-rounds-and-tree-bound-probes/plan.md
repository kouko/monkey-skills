# checker: fix rounds by the raising reader; tree-bound probes and verdicts; the close line rides in the review-only commit — plan
intent: 2026-09-05-checker-fix-rounds-and-tree-bound-probes@2f212f8d

## Current State Evidence
- Forward: `loom-code/scripts/loom_checker.py:335-342` — `latest_round()` picks
  the verdicts with the highest `round` number across the whole record;
  `check_verdicts()` (`:3419-3440`) counts distinct reviewers in that round
  against the lane floor (2 in the full lane). Every fix round therefore
  needs both readers, and a branch-end round numbered 1 after a wave-end
  round 3 scores the wrong verdicts (memory-step change, 2026-09-05).
- Reverse: `loom-code/scripts/loom_checker.py:2479` and `:2815` — the probe
  rules compare a probe's recorded `sha` to `reviewed_id` as commit ids
  ("ran against sha …, not the reviewed commit"); `:2250-2300`
  `push.reviewed-sha` does the same for every scored verdict. A commit that
  touches only `review.json` moves the id without moving the reviewed
  content; #791 re-ran its 1368-test suite about eight times for that.
- Error: `loom-code/scripts/loom_checker.py:1864-1865` — `push.review-only-head`
  refuses any HEAD touching a file other than `review.json`; `:2036` onward
  validates the close-commit shape (HEAD^ regenerated from the status line
  only, `_regenerated_closed_text()` at `:1932-1946` writes
  `closed <date> — PR #<n>`); `:959-963` `_STATUS_CLOSED_ALT` accepts only the
  `PR #<n>` form, and `intake.confirmed` (`:1020-1096`) treats that form as
  terminal. The PR number exists only after a push, which is why the close
  costs a second push and a review round of its own.
- Data: `loom-code/scripts/test_loom_checker_push.py`,
  `test_loom_checker_push_probes.py`, `test_loom_checker_hardening.py`,
  `test_loom_checker_cli.py` are the checker's own suites; they build
  sandbox repos with recorded review.json shapes — the pattern the new
  cases follow. `docs/loom/2026-09-03-artifact-language-policy/review.json`
  is the real fixture for the single-reader fix round (round 3 codex-only)
  and the trailer-only rewrite (rounds 5→6).
- Boundary: `--list-rules` prints 27 lines; four rule descriptions change
  wording, none is added or removed. `.codex/hooks/loom_checker.py` is a
  byte mirror checked by `loom-code/scripts/test_codex_mirror_matches_checker.py`
  — every checker edit regenerates it (`codex_scaffold.py --repo .`). Station
  text: `loom-code/skills/ship/SKILL.md:323-360` §6 (close commit, its own
  checkpoint, push again; 3,252 words), `loom-code/skills/review/SKILL.md:323-`
  §7 and `references/fix-rounds.md:14-28` (resume every reader).

## Task DAG

Lane: full — `loom_checker.py` is gate-typed, so every checker task is
adversary-first and the closing round runs adversary, blind run and two
readers. Second vendor: Codex (user's answer at ①). The three checker tasks
edit the same 3,800-line file: they run **serially** in the working tree
(agent-decided — parallel worktrees on one file trade a merge conflict for
nothing). This change closes itself under option A (agent-decided — its
Acceptance 6 says so): the final review-only commit carries the close line,
no close round, and the PR body shows `git log <reviewed_sha>..HEAD` with
one commit.

**W0-01 Adversarial probes for the four rule changes**  after: —
- Files: `docs/loom/2026-09-05-checker-fix-rounds-and-tree-bound-probes/evidence/probes/test_abuse_checker_semantics.py`
- Test: the probe file — sandbox repos built the way the checker's own
  suites build them, RED today on: (a) a fix round whose only verdict is
  the raising reader's, with the fix delta inside that reader's finding
  anchors, blocked by `push.verdicts-ge-2`; (b) the same scenario with the
  fix delta touching a file outside the anchors — must still block after
  the change (GREEN today, stays GREEN: a regression pin); (c) a probe
  recorded at a commit whose tree equals the reviewed commit's tree apart
  from `review.json` — blocked by `push.probes-package-tests`; (d) a
  trailer-only rewrite (same trees, new shas) — verdicts blocked by
  `push.reviewed-sha`; (e) a review-only commit that also changes the
  intent's `status:` line to `closed <date> — branch <name>` — blocked by
  `push.review-only-head`; (f) `intake write-plan` on an intent closed
  with the branch form — must block as terminal (RED today: the regex
  does not match, so the intent reads as neither confirmed nor closed);
  (g) GREEN pin: `--list-rules` = 27. Three-part names, English docstrings,
  no sha literals — locate commits by subject or trailer.
- Risk: probes that call the checker as a subprocess on a sandbox are slow
  (~1 s each); acceptable. Agent-decided: pin behaviours, not messages.

Wave 1 — the checker, three serial tasks in the working tree.

**W1-01 Fix rounds: only the raising reader must return**  after: W0-01
- Files: `loom-code/scripts/loom_checker.py` (`latest_round`, `check_verdicts`),
  `loom-code/scripts/test_loom_checker_push.py`, `.codex/hooks/loom_checker.py` (regenerated)
- Test: W0-01 probes (a) and (b); unit cases in `test_loom_checker_push.py`:
  first round of a checkpoint still needs the lane floor; a later round
  counts a non-returning reader's earlier PASS as standing only when every
  path in the fix delta (`<that reader's verdict sha>..<this round's sha>`)
  is a file named in some open finding's anchor of the returning reader;
  otherwise the floor applies as before. Round numbers are compared within
  a `scope` (the memory-step gotcha: rounds restarting per checkpoint must
  not resurrect a wave-end verdict).
- Risk: "raising reader" = the reviewer named in `open_findings[].raised_by`
  for findings still open at that round; a round with no open findings is a
  first round. The Constraint's safety line is the anchor-file rule — keep
  it strict (path equality, not prefix). Agent-decided: a `dismissed`
  finding counts as closed for this purpose.

**W1-02 Probes and verdicts bound to the tree, review.json excluded**  after: W1-01
- Files: `loom-code/scripts/loom_checker.py` (a helper `content_tree_id(repo, sha)`
  that hashes the tree with `docs/loom/<change-id>/review.json` removed —
  `git ls-tree` + `git mktree` is the cheapest honest way; the three rules
  compare that id), `loom-code/scripts/test_loom_checker_push_probes.py`,
  `.codex/hooks/loom_checker.py`
- Test: W0-01 probes (c) and (d); unit cases: review.json-only commit on
  top of a recorded probe → pass; any other file changed → block; a
  trailer-only rewrite → pass; the recorded sha not resolving → still
  block with the existing message.
- Risk: the id must exclude only this change's review.json, never every
  review.json (another change's record is content). Agent-decided: keep
  the commit-id fast path (equal ids → pass without building trees).

**W1-03 The close line rides in the review-only commit; close grammar accepts a branch name**  after: W1-02
- Files: `loom-code/scripts/loom_checker.py` (`push.review-only-head`,
  the close-commit shape at `:2036-`, `_STATUS_CLOSED_ALT`, `intake.confirmed`,
  `_regenerated_closed_text`, the four `--list-rules` descriptions),
  `loom-code/scripts/test_loom_checker_push.py`, `test_loom_checker_cli.py`,
  `.codex/hooks/loom_checker.py`
- Test: W0-01 probes (e), (f), (g); unit cases: review-only commit + the
  status line only → pass; + any other intent line → block; + a third
  file → block; both close forms terminal for `intake.confirmed`; the old
  shape (separate close commit under a review-only commit) still passes
  (older branches keep working).
- Risk: the status regex gains an alternative
  `closed <date> — branch <name>`; the name charset is `[A-Za-z0-9._/-]+`.
  Agent-decided: the old `PR #<n>` form stays accepted forever.

Wave 2 — station text and release plumbing.

**W2-01 Station text: fix rounds, round numbering, ship without a close round**  after: W1-03
- Files: `loom-code/skills/review/SKILL.md` (§7: rounds continue across
  checkpoints; §8a one sentence: a fix round resumes the raising reader,
  the other reader's PASS stands when the delta stays inside the anchors),
  `loom-code/skills/review/references/fix-rounds.md`,
  `loom-code/skills/ship/SKILL.md` (§6 rewritten: after ③, one commit —
  `review.json` plus the intent's `status: closed <date> — branch <name>`
  line — then push, PR with a "Closing log" section showing
  `git log <reviewed_sha>..HEAD`, merge, verify; the "commit right before
  a review-only commit" consequence paragraph goes), pins in
  `loom-code/scripts/test_ship_station_text.py` and `test_review_station_text.py`
  (moved, not deleted; affirmative, un-negated, with a synthetic negative)
- Test: pins RED first; W0-01 unaffected; package suite green; SKILL.md
  ≤ 4,500 words.
- Risk: ship §1 fact 4 (HEAD review-only, `reviewed_sha` = HEAD^) is
  unchanged — the close line joins the review-only commit, it does not
  replace it. The PR-body template gains the Closing log section.

**W2-02 Changelog 1.4.0, version, Codex manifest and mirror**  after: W2-01
- Files: `loom-code/CHANGELOG.md`, `loom-code/.claude-plugin/plugin.json`
  (1.3.1 → 1.4.0 — rule semantics changed), `loom-code/.codex-plugin/plugin.json`
  via `scripts/sync_codex_manifests.py loom-code`, `README.md` version row,
  `.codex/hooks/**` via `codex_scaffold.py --repo .`
- Test: `check_version_bump.py`, `sync_codex_manifests.py --check loom-code`,
  `test_codex_mirror_matches_checker.py`, package suite green.
- Risk: minor bump (agent-decided — four push-gate rules recompute
  differently; consumers' recorded review.json shapes stay valid).

**W2-memory Memory step — graduated probes and store entries**  after: W2-02
- Files: `loom-code/scripts/test_probes_checker_semantics.py` (byte copy of
  the W0-01 file, path lines only), one `docs/loom/memory/` entry (a gate
  that binds records to commit ids taxes every bookkeeping commit; bind to
  content) + regenerated index
- Test: `check_loom_memory_integrity.py` exit 0; the graduated copy passes;
  no name collision in `loom-code/scripts/`.
- Risk: orchestrator's own task (`fresh_context: false`); dispatch entry
  committed BEFORE the work (the memory-step change's gotcha); `git add`
  new files before the path-limited commit.

Checkpoints: wave-end after wave 1 (checker code, well past 400 lines) and
the single closing round after W2-memory — two of five, no `after-task`
markers. Round numbers continue across the two checkpoints. Before the
closing round: every CI job's check locally (package command,
`loom-design/scripts/`, doc-citation selection, memory integrity,
version bump, manifest sync, contract citations, marketplace sync).

## Questions asked
1 — what — 你要的是——checker 三條既有規則改重算方式：修正輪只要「提了還開著的 finding 的讀者」回來確認（前提：修正只碰那些 finding 錨定的檔案，否則仍要兩位）；探針、整包測試、verdict 的紀錄改成比「樹的內容（排除 review.json）」而不是 commit sha，只改 review.json 或只改 commit 訊息不再逼重錄。規則數不變。對嗎？
1 — what — 這兩個 change 要不要都用 Codex 當第二位讀者？
1 — what — 甲案：關閉 intent 那一行與 review-only 同一個 commit、關閉文法接受分支名、ship 拿掉關閉輪——照甲走嗎？
<!-- the review station copies this section into review.json questions[] at the first checkpoint -->

## Risks
1. user-decided — Codex is the second reader.
2. user-decided — option A: the close line rides in the final review-only
   commit; the close grammar accepts a branch name; ship has no close round.
3. The installed checker (1.3.1) gates this branch's own push with the OLD
   rules until the change ships, so this change's fix rounds still need
   both readers and its own close must satisfy 1.3.1's `push.review-only-head`
   — which refuses the option-A commit shape. Agent-decided: this change
   ships under the old close sequence (separate close commit, close round)
   and Acceptance 6's "this intent closes under option A" is verified by
   the blind run against a sandbox and by running the branch's own checker
   copy (`python3 loom-code/scripts/loom_checker.py push`) on the option-A
   shape in that sandbox; the first real option-A close is the next change.
   The blind-run report says this.
4. Closing-round probes still cannot graduate before the closing round
   (memory-step gotcha); with tree-bound probes the review-only commit no
   longer forces a re-run, but graduation itself stays a follow-up — noted,
   not solved here.
5. No checker rule added or removed; `--list-rules` 27 (Constraints).
