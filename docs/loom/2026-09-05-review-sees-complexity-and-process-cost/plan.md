# review sees complexity and process cost: deletion-first in the docs and skill lenses, cap bumps pay, a cost block per change, dispatch records batched per wave and round — plan
intent: 2026-09-05-review-sees-complexity-and-process-cost@b64a27d4

## Current State Evidence
- Forward: `loom-code/skills/review/references/lenses.md:54` — the code lens
  defines `deletion-first` (a new abstraction needs two concrete users or an
  explicit request; a finding must name the smaller shape). `:56-64` the docs
  lens lists five dimensions (omission, ambiguity, inconsistency,
  incorrect-fact, missing-population) and `:78-84` the skill lens adds only
  `user-judgment-leak` — neither asks whether a new paragraph, mechanism or
  fallback path is needed. `loom-code/agents/reviewer.md:45` and `:49` carry
  the docs and skill rows of the lens table that reviewers score from.
- Reverse: the word caps are the only complexity proxy, and they only ever
  rise: `loom-code/scripts/test_reviewer_agent_single_contract.py:34`
  `AGENT_CAPS` pins reviewer.md at 1460 (probe files at
  `test_probes_positioning_branch_end.py:150-151` record the previous 1340);
  `test_write_plan_intake.py:26` and `test_reviewer_agent_single_contract.py:33`
  pin two stations at 4500. No station text asks for a reason when a cap
  rises; `docs/loom/memory/a-cap-raised-at-every-touch-is-not-a-cap.md` is the
  recorded failure.
- Error: `loom-code/skills/build/SKILL.md:188` — "Commit it on its own:
  `chore(loom): dispatch <task-id>`" reads as one commit per dispatch; the
  memory-step branch carried 56 commits, 16 of them dispatch records.
  `loom-code/skills/review/SKILL.md:144-149` already batches the adversary
  and blind-runner records into one commit; readers are recorded separately
  (`:209-216`). `loom-code/agents/adversary.md` says nothing about fixing a
  probe of its own (`:47-77`).
- Data: `loom-code/contract/templates/review.json:2-22` has no `cost` key;
  `docs/loom/KICKOFF-DEFAULTS.md:8` is the package-tests line, missing
  `loom-design/scripts/` (#791 went red in CI twice on the loom-design job);
  `loom-code/skills/ship/SKILL.md:277-318` is the PR-body template (`## Memory`
  must stay last, `:320-329`); `:225-244` §4 names only the checker `push` as
  a pre-push check — no list aligned with the CI jobs
  (`.github/workflows/loom-code-ci.yml:110-175`: pytest, standalone plugin
  boundaries, codex manifest sync, mechanisms baseline and measure, contract
  citations, doc-citation resolution, skill cross-refs).
- Boundary: `loom-code/skills/review/SKILL.md:431-444` §8a hands the third-round
  design re-look to `references/fix-rounds.md`, reader-trusted, with no
  required line in the verdict — #793's ship finding ran three rounds and the
  re-look happened only in a dispatch note. No checker rule is added or
  removed: `--list-rules` stays 27.

## Task DAG

Lane: full — SKILL.md and `agents/*.md` are skill-typed, so the checkpoints
run adversary, blind run and two readers; no task is gate-typed, so no task
is adversary-first (agent-decided from the manifest mapping). Second vendor:
Codex (user's answer at ①). The five wave-1 tasks touch disjoint files and
run in parallel, each in its own worktree. This change dogfoods its own
outcomes: dispatch records are committed once per wave and once per round,
`review.json` carries a `cost` block from the first checkpoint, and any cap
bump it needs is written with its reason and a deletion candidate.

**W1-01 Lenses: `deletion-first` for docs and skill; cap-bump candidate rule**  after: —
- Files: `loom-code/skills/review/references/lenses.md`,
  `loom-code/agents/reviewer.md`,
  `loom-code/scripts/test_lenses_deletion_first.py` (new),
  `loom-code/scripts/test_reviewer_agent_single_contract.py`
- Test: `test_lenses_deletion_first.py` — the docs lens table and the skill
  lens paragraph each name `deletion-first`, its definition carries an
  affirmative sentence requiring the smaller shape, and the "consecutive cap
  bumps" sentence names a deletion candidate; reviewer.md rows `:45`/`:49`
  end with `deletion-first`. RED today.
- Risk: reviewer.md sits at its 1460 cap — the row edit adds two words per
  row; the task compresses elsewhere in the file first, and a bump is
  written only with the reason in the commit body and a deletion candidate
  named in the same commit (agent-decided — the intent's outcome 2 applied
  to itself).

**W1-02 Review station: batched reader records, cap-bump reason, cost block, third-round line**  after: —
- Files: `loom-code/skills/review/SKILL.md`,
  `loom-code/skills/review/references/fix-rounds.md`,
  `loom-code/scripts/test_review_station_text.py`
- Test: four affirmative pins in `test_review_station_text.py` — §2: the
  round's adversary, blind-runner and reviewer records are appended once and
  committed once before any of them is dispatched; §7: a commit that raises a
  `*_CAP` constant is recorded with a one-line reason in the round's notes;
  §7: `cost` (rounds, dispatches, cap changes, hours from plan commit to PR)
  is updated at every checkpoint and the worked record shows the key;
  §8a/fix-rounds: the third round of one checkpoint carries a
  "design re-look:" line in its notes (continue fixing / change the design /
  accept as nit), and a verdict without it is not complete. RED today.
- Risk: review/SKILL.md is at 3,623 words under a 4,500 cap — room exists;
  the third-round line stays text-only (no checker rule, per Constraints).

**W1-03 Build station and adversary contract: records per wave; amend an unseen probe fix**  after: —
- Files: `loom-code/skills/build/SKILL.md`, `loom-code/agents/adversary.md`,
  `loom-code/scripts/test_build_station_text.py`,
  `loom-code/scripts/test_adversary_agent_contract.py` (new, or the existing
  adversary contract test if one pins its wording)
- Test: build §3 carries an affirmative sentence that one wave's implementer
  records are appended once and committed once before the first dispatch of
  that wave, replacing "Commit it on its own"; adversary.md carries an
  affirmative sentence that a fix to its own probe, not yet seen by any
  reader, is amended into the original probe commit. RED today.
- Risk: adversary.md cap is 600 words — one sentence fits; the gate marker
  `build.no-dispatch-without-a-record` keeps its id and its
  "record before dispatch" meaning (agent-decided — batching changes the
  commit count, not the ordering rule).

**W1-04 Ship station: process-cost section in the PR body; pre-push checklist aligned with CI**  after: —
- Files: `loom-code/skills/ship/SKILL.md`,
  `loom-code/scripts/test_ship_station_text.py`,
  `loom-code/scripts/test_ship_pr_body.py`
- Test: the PR-body template gains `## Process cost` between
  `## Closing log` and `## Memory` (pinned by index order, `## Memory` still
  last); §4 lists, before the push, one command per CI job of this repo's
  loom-code workflow with the sentence that the list mirrors the workflow's
  jobs. RED today.
- Risk: ship/SKILL.md is at 3,389 words under a 3,500 cap — the checklist is
  a fenced block of seven commands (~60 words); if the file overruns, the
  task moves the BLOCK→remedy table's prose into `references/` rather than
  bumping the cap (agent-decided — deletion before a bump).

**W1-05 Templates and defaults: `cost` in review.json; package-tests covers loom-design**  after: —
- Files: `loom-code/contract/templates/review.json`,
  `docs/loom/KICKOFF-DEFAULTS.md`, `scripts/test_kickoff_defaults.py` (new),
  `loom-code/scripts/test_review_json_template.py` (new)
- Test: the template parses and carries a `cost` object with `rounds`,
  `dispatches`, `cap_changes`, `hours_plan_to_pr`; KICKOFF's package-tests
  line contains `loom-design/scripts/` and its trailing note no longer claims
  CI runs the same paths. RED today.
- Risk: the recorded package command must equal KICKOFF byte for byte
  (`push.probes-package-tests`) — every checkpoint of this change records the
  new command; the CI workflow itself is not edited (out of the intent's
  scope: the checklist aligns to CI, CI does not move).

**W2-01 Version, changelog, README row, codex manifest sync**  after: W1-01, W1-02, W1-03, W1-04, W1-05
- Files: `loom-code/CHANGELOG.md`, `loom-code/.claude-plugin/plugin.json`,
  `loom-code/.codex-plugin/plugin.json`, `README.md`,
  `.codex/hooks/loom-checker`, `.codex/hooks/loom_checker.py`
- Test: `python3 scripts/sync_codex_manifests.py --check --all` exits 0 and
  the version bump test passes; `--list-rules` still prints 27 lines.
- Risk: minor bump 1.4.0 → 1.5.0 (agent-decided — two lenses gain a
  dimension and the record template gains a key; behaviour of no rule
  changes).

**W2-memory Memory step — graduated probes and store entries**  after: W2-01
- Files: byte copies of this change's `evidence/probes/test_*.py` under
  `loom-code/scripts/` (path lines adjusted only, names checked against
  every test in that directory); one `docs/loom/memory/` entry on batching
  dispatch records per wave and round, plus its README index line.
- Test: `python3 scripts/check_loom_memory_integrity.py` exits 0; the
  graduated copies pass; no test-function name collides.
- Risk: the closing round's own probes cannot graduate (written after this
  step) — they stay under evidence, as the memory entry
  `a-gate-that-binds-records-to-commit-ids-taxes-every-bookkeeping-commit`
  already records.

Checkpoints: wave-end:1 after W1 (five tasks, more than 8 files), then the
single closing round after W2-memory — two checkpoints.

## Questions asked
1 — what — 「你要的是：讓審查也「看得見複雜度」——現在只有審程式碼的鏡頭會問「這段有必要嗎、有沒有更小的寫法」，審站文字和契約的鏡頭不會問……做完後你可以：（六項）……對嗎？」
1 — consequence — 「不可逆的門：沒有——全是文字與紀錄欄位，舊 review.json 不用改。」（stated, not asked)
1 — what — 「這次要不要用 Codex 當第二位讀者？」（answer: codex）

## Risks
1. Caps: reviewer.md (1460) and ship/SKILL.md (3,500) are near their caps;
   two tasks may need words. The plan's order is compress, then extract to
   `references/`, then bump with a written reason and a deletion candidate —
   a bump here is the intent's outcome 2 exercised on itself.
2. The batched dispatch record for wave 1 names five implementers before
   any starts; if one worktree is abandoned, the record stays and the
   report says so (the record is the truth of what was dispatched).
3. This change's own `cost` block is filled by hand at each checkpoint;
   hours are wall-clock from the plan commit (`b64a27d4`'s successor) to
   `gh pr create`.
