# Memory step before branch-end; prose-pin rule and Task-trailer check in the contracts — plan
intent: 2026-09-05-memory-step-before-branch-end-and-prose-pin-rule@d8850558

## Current State Evidence
- Forward: `loom-code/skills/ship/SKILL.md:129-196` — §3 "Memory" tells ship
  to write store entries (line 174: "commit it separately before the
  review-only commit, and re-run the branch-end checkpoint") and to graduate
  probes (line 180: "Before the push, copy this change's pytest probes …";
  line 191: "this graduation commit lands before the review-only commit …
  re-run the branch-end checkpoint"). Both sentences schedule a post-review
  commit by design. Six tests in `loom-code/scripts/test_ship_station_text.py`
  (lines 31-72) pin those paragraphs — they move with the text, they are not
  deleted.
- Reverse: `loom-code/skills/build/SKILL.md:201-203` — §4 step 1 says "check
  the commit exists and carries its `Task:` trailer" with no command;
  `build/SKILL.md:248-250` §5 "Wave end" runs `git diff --stat` only. Nothing
  in build mentions graduation or the memory store; `docs/loom/README.md:15`
  attributes the store to "ship station's memory step".
- Error: three review records show the cost — `docs/loom/2026-09-03-artifact-language-policy/review.json`
  notes[] (close re-created three times; rounds 4–11 all post-review),
  `docs/loom/2026-09-04-codex-hook-trust-covers-every-definition-and-worktree/review.json`
  and `docs/loom/2026-09-04-positioning-paragraph-cap-redesign/review.json`
  (each carries a 4a/4b round for the same reason). The prose-pin defect was
  raised three times in one change (rev-we1-codex wave-end:1-03, rev-be-codex
  branch-end-02 and round 9), always by the same mechanism: keyword
  co-occurrence satisfied by a negated sentence.
- Data: `loom-code/agents/adversary.md:53-56` names the three-part probe shape
  and English docstrings, nothing about how to pin prose; body 556 words of
  a 600 cap (`test_reviewer_agent_single_contract.py` `AGENT_CAPS`).
  `loom-code/references/engineering-baseline.md:130-148` §5 "Working
  discipline" is a numbered list of terse rules; 1280 words of a 1500 cap
  (`test_engineering_baseline_reference.py` `WORD_CAP`).
- Boundary: `loom_checker.py --list-rules` prints 27 lines; `push.dispatch-covers-tasks`
  requires every code-touching commit to carry a `Task:` trailer claimed by
  an implementer dispatch entry — the memory-step commits (graduated tests
  are code) therefore need a task id and a dispatch record, which the plan
  gives them as a real task (W2-02). Station SKILL.md caps: soft 5,000 /
  hard 6,000 tokens; ship is 3,404 words today, build 2,677 — room for a
  section each.

## Task DAG

Lane: full — `SKILL.md`, `agents/*.md` and `references/*.md` are skill-typed.
Second vendor: Codex (user's answer at decision point ①). This change is its
own first sample of the new order (agent-decided — Acceptance 1 says "a new
change"; W2-02 performs the memory step before branch-end here, so the
branch-end blind run can show the `git log` shape on this very branch, and
ship then finds nothing left to graduate or store).

**W0-01 Adversarial probes for the memory-step move and the two contract sentences**  after: —
- Files: `docs/loom/2026-09-05-memory-step-before-branch-end-and-prose-pin-rule/evidence/probes/test_abuse_memory_step.py`
- Test: the probe file — RED today on (a) ship §3 still instructing probe
  graduation or store entries after the checkpoint; (b) build carrying no
  memory-step section placed before the branch-end call; (c) adversary.md
  and engineering-baseline.md lacking an affirmative, un-negated prose-pin
  sentence (affirmative verb before the literal, no negation token, self-
  tests named) — use the matcher shape from
  `loom-code/scripts/test_language_station_text.py`; (d) build §4/§5 lacking
  a copyable trailer-check command (a fenced `git log … grep '^Task: '`
  line); GREEN pins on (e) `--list-rules` = 27 and (f) a sandbox repo where a
  commit without `Task:` is caught by the command the probe extracts from
  build's text (skip until (d) is GREEN, never fail). Three-part names,
  English docstrings; no branch-scope probe this time (the memory store
  lesson from #791).
- Risk: probes that pin wording over-fit; agent-decided — pin facts
  (section present before the branch-end sentence; a fenced command
  containing both `git log` and `Task:`), not sentences.

Wave 1 — three disjoint files sets, parallel worktrees.

**W1-01 ship: §3 keeps trailers and questions only; graduation and store entries leave**  after: W0-01
- Files: `loom-code/skills/ship/SKILL.md`, `loom-code/scripts/test_ship_station_text.py`
- Test: W0-01 probe (a) turns GREEN; the six ship pins in
  `test_ship_station_text.py` are re-targeted to the build section that now
  owns the text (same assertions, new source — never deleted); package suite
  green.
- Risk: ship §1's fourth fact and §6's close sequence stay byte-for-byte;
  §3 must still say that a store entry or a graduation found missing at ship
  time goes back to `build` as a task (the escape hatch), so the exception
  path is stated once. Agent-decided: §3.5's nit batch stays where it is —
  it is review-record work, not memory.

**W1-02 build: memory step before the branch-end checkpoint; trailer-check command**  after: W0-01
- Files: `loom-code/skills/build/SKILL.md`, `loom-code/scripts/test_build_station_text.py`, `docs/loom/README.md` (row 15 attribution)
- Test: W0-01 probes (b) and (d) turn GREEN; new pins in
  `test_build_station_text.py` (memory section sits before the §7 hand-off
  and names the branch-end call; the trailer command is fenced and the wave-
  end paragraph runs it over `<reviewed_sha>..HEAD`); package suite green.
- Risk: the memory step needs a task id the push gate accepts —
  agent-decided: the plan's last wave carries a real task (here W2-02) whose
  implementer entry the orchestrator writes for itself (`fresh_context:
  false`), commits carry `Task: <that id>`; build's text says exactly this.
  The wave-end trailer check is a command, not a checker rule (Constraints).
  Existing paragraphs moved from ship keep their wording where the pins
  quote them (the six ship pins re-target here).

**W1-03 adversary and baseline: the prose-pin sentence**  after: W0-01
- Files: `loom-code/agents/adversary.md`, `loom-code/references/engineering-baseline.md`, `loom-code/scripts/test_prose_pin_rule_text.py` (new pin file)
- Test: W0-01 probe (c) turns GREEN; the new pin file asserts each file has
  one sentence with an affirmative verb before "affirmative"/"negation"
  vocabulary and no negation token, plus a self-test with a negated
  synthetic; caps: adversary ≤ 600 (556 today), baseline ≤ 1500 (1280).
- Risk: adversary.md's "You own" paragraph is under the six-sentence cap —
  the sentence goes next to the three-part-name sentence (line 53), not
  there. The baseline sentence is rule 8 of §5 "Working discipline"
  (agent-decided — the list is what the reviewer reads work against).

**W1-04 Graduated branch-scope probes from #791 skip once their change has shipped**  after: W0-01
- Files: `loom-code/scripts/test_probes_language_policy.py` (`test_branchdiff_scope_clean`), `loom-code/scripts/test_probes_language_policy_branch_end.py` (`test_BranchDiff_docsLoomPaths_scopedToChangeId`)
- Test: both tests fail on this branch today (W1-03's package run: they treat this change's own `docs/loom/2026-09-05-…/` files as foreign paths of the 2026-09-03 change); after the fix they `pytest.skip` with a stated reason when `docs/loom/intent/2026-09-03-artifact-language-policy.md` reads `status: closed`, and still run (and pass) when it does not; a self-test feeds both intent states to the guard.
- Risk: found during W1-03; a graduated probe that pins "this branch touches only its own change's docs" is only meaningful on that change's branch — every later branch adding a `docs/loom/<id>/` tree goes red on CI. Agent-decided: skip-on-closed, not delete (the pin stays alive for a reopened branch); the evidence originals are historical and are not edited. Added to the plan after the fact — noted in the wave report.

Wave 2 — release plumbing, then this change's own memory step.

**W2-01 Changelog 1.3.1, version, Codex manifest and scaffold stamps**  after: W1-01, W1-02, W1-03
- Files: `loom-code/CHANGELOG.md`, `loom-code/.claude-plugin/plugin.json` (1.3.0 → 1.3.1), `loom-code/.codex-plugin/plugin.json` via `scripts/sync_codex_manifests.py loom-code`, `README.md` version table, `.codex/hooks/**` via `codex_scaffold.py --repo .` if the stamp test demands it
- Test: `scripts/check_version_bump.py --base origin/main --head HEAD` and
  `scripts/sync_codex_manifests.py --check loom-code` exit 0; package suite
  green (the version-stamp agreement test).
- Risk: patch bump — station prose and contracts moved, no template or
  checker change (agent-decided).

**W2-02 This change's memory step, before the branch-end checkpoint**  after: W2-01
- Files: `loom-code/scripts/test_probes_memory_step.py` (byte copy of the
  W0-01 probe file, path lines only), `docs/loom/memory/<one entry>.md` +
  regenerated `docs/loom/memory/README.md`
- Test: `python3 scripts/check_loom_memory_integrity.py` exit 0; the
  graduated copy passes; no test-function name collides with an existing
  one in `loom-code/scripts/`.
- Risk: this is the first run of the new order, done by the orchestrator
  with its own dispatch entry (`fresh_context: false`). The store entry is
  the fact this change is built on ("the memory step belongs before the
  branch-end checkpoint; a post-review commit always costs a round"), one
  file. Commit by explicit paths including the new files — `git add` them
  first (the #791 gotcha).

Checkpoints: wave-end after wave 1 (three skill files plus pins, over 8
files) and the branch-end round after W2-02 — two of five, no `after-task`
markers. Before the branch-end checkpoint, run every CI job's check
locally: the KICKOFF package command, `python3 -m pytest loom-design/scripts/ -q`,
the doc-citation selection from `.github/workflows/loom-code-ci.yml`,
`check_loom_memory_integrity.py`, the version-bump and manifest-sync checks.

## Questions asked
1 — what — 你要的是——探針畢業與記憶庫條目改到最後一個 wave 結束、branch-end 審查之前做，審查看到的就是最終的樹，之後只剩關閉 intent 那一行；散文釘的「肯定句＋無否定詞＋正反自測」規則寫進 adversary 契約與 implementer 的基線；build 站對 `Task:` 尾標的檢查給出可複製的命令、wave 結束合併後跑一次。不加 checker 規則。對嗎？
1 — what — 這兩個 change 要不要都用 Codex 當第二位讀者？
<!-- the review station copies this section into review.json questions[] at the first checkpoint -->

## Risks
1. user-decided — Codex is the second reader.
2. The installed ship station (1.3.0) still describes the old order; for
   this change the orchestrator follows the branch's new text (W2-02
   before branch-end) and ship's step 3 finds nothing left to do — stated
   in the blind-run report. Agent-decided.
3. The six ship pins move to build; if a reviewer reads a moved pin as a
   deleted one, the commit body of W1-01/W1-02 says where each went.
4. No checker rule is added or changed (Constraints); the trailer check is
   a command in station text. The rule-level changes are the sibling intent
   `2026-09-05-checker-fix-rounds-and-tree-bound-probes`.
