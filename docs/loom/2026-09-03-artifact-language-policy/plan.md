# Internal artifacts in English, three checkable templates — plan
intent: 2026-09-03-artifact-language-policy@e43d894f

This plan is written in English on purpose: the intent's hard cutover
starts "with the next change", and this change is that change. Its own
plan, evidence notes, review findings, probe names and commit messages
are the first sample the blind run checks against Acceptance 1 and 5
(agent-decided — the intent says "a new change"; waiting for a later
change would leave Acceptance 1 unprovable inside this branch, and the
next change re-verifies it anyway).

## Current State Evidence
- Forward: `loom-code/agents/reviewer.md:103-108` — the `docs-lint` style
  clause tells the reviewer to raise no finding, not even a `nit`, for
  wording or terminology when the repo declares a lint command. Language
  and template shape must be carved out of that clause or the new nit
  dimension is silenced the moment a repo adds `docs-lint`.
- Reverse: `loom-code/skills/review/references/blind-run-report.md` and
  `loom-code/contract/templates/intent.md` are the two user-facing
  carriers whose language rule already exists (user's language); nothing
  in this change may move them to English.
- Error: `loom-code/scripts/test_reviewer_agent_single_contract.py:34` —
  `AGENT_CAPS = {"reviewer.md": 1340, "blind-runner.md": 600, "adversary.md": 600}`;
  body word counts today 1338 / 503 / 523. Adding one clause to
  reviewer.md exceeds its cap; the cap moves with the clause (standing
  authorisation: the agent decides compress vs extract vs cap bump).
- Data: `grep -cP '[\x{4e00}-\x{9fff}]'` over `loom-code/contract/templates/`
  today: `intent.md` 9 lines, `plan.md` 13, `spec-minimal.md` 13,
  `PRINCIPLES-interview.md` 11, the other four 0. Existing Chinese docs
  under `docs/loom/2026-09-0*/` and `docs/loom/intent/` stay untouched
  (Acceptance 4). `docs/loom/KICKOFF-DEFAULTS.md:12` carries
  `docs-lint: none — loom docs in this repo are Traditional Chinese for now`
  and names this intent; its reason line goes stale when this lands.
- Boundary: `loom-code/skills/build/SKILL.md:104,130` reads the plan
  template's `檔 / 測 / 風` bullet labels by name; `loom_checker.py` parses
  none of them (no CJK in its parsers), and `--list-rules` prints 27 lines
  today (Acceptance 3: unchanged). Station text is pinned by
  `test_*_station_text.py`; the sentences this change adds get their own
  pin file, not edits to those.

## Task DAG

Lane: full — `SKILL.md` and `agents/*.md` are skill-typed, so two readers,
a blind run and an adversary at every checkpoint. Second vendor: Codex
(user's answer at decision point ①).

Wave 0 — the adversary writes the probes before any text moves, the same
shape as the positioning-cap change: every Acceptance line becomes an
executable check that is RED today.

**W0-01 Adversarial probes for the language policy**  after: —
- Files: `docs/loom/2026-09-03-artifact-language-policy/evidence/probes/test_abuse_language_policy.py`
- Test: the probe file itself — RED today on (a) CJK present in the four
  templates, (b) no language sentence in the six station `SKILL.md`
  files, (c) reviewer.md lacking the language/template nit clause,
  (d) `spec-minimal.md` REQ example not in an EARS form, (e) adversary.md
  and blind-runner.md silent on the three-part probe name; GREEN today
  on (f) `--list-rules` line count = 27 and (g) `git diff` against the
  branch base touching no file under `docs/loom/2026-09-0*/` or
  `docs/loom/intent/` other than this change's own — (f) and (g) are
  regression pins. Function names follow `test_<unit>_<state>_<expected>`
  from the first commit — the probes are the first artifact the new
  naming rule applies to.
- Risk: probes that grep for exact sentences over-fit the implementer's
  wording; agent-decided — pin the *facts* (a CJK count of zero, a
  sentence containing both "English" and the artifact list, an EARS
  keyword at the head of the REQ example) rather than verbatim text, as
  the positioning probes did.

Wave 1 — the contract: templates and the three agent contracts. Three
tasks, disjoint files, run in parallel in their own worktrees.

**W1-01 Templates in English; EARS example; plan labels**  after: W0-01
- Files: `loom-code/contract/templates/intent.md`, `plan.md`,
  `spec-minimal.md`, `PRINCIPLES-interview.md`;
  `loom-code/skills/build/SKILL.md` (lines 104 and 130 only — the label
  names it quotes)
- Test: W0-01's CJK-count probe and EARS-example probe turn GREEN;
  `python3 -m pytest loom-code/scripts/ -q` stays green (the
  template-shape tests in `test_reviewer_agent_single_contract.py` and
  the station-text pins read these files).
- Risk: field *meaning* must not move — `intent.md`'s fields and
  `plan.md`'s `## Questions asked` / `review: after-task — <reason>` line
  are read by the checker (`intent.schema`, `intake.after-task-budget`);
  translate the comments, keep every key, heading and marker byte-for-byte.
  Plan bullet labels become `Files:` / `Test:` / `Risk:` (agent-decided —
  the three labels are the only template tokens another station names by
  string, so they change together with the one file that names them;
  existing plans keep their old labels and are never re-read by a
  parser). `PRINCIPLES-interview.md`'s questions are asked to the user in
  the user's language at run time — the template holds the English
  source and the station localises, as it already does for the
  restatement sentence (agent-decided — Acceptance 2 admits no exception).
  The `spec-minimal.md` REQ example shows one EARS form with the
  `→ Acceptance #<n>` suffix kept.

**W1-02 Reviewer contract: language and template shape are a nit, not style**  after: W0-01
- Files: `loom-code/agents/reviewer.md`,
  `loom-code/scripts/test_reviewer_agent_single_contract.py` (`AGENT_CAPS`)
- Test: W0-01's reviewer-clause probe turns GREEN; the word-cap test
  passes at the new cap.
- Risk: the clause must sit *outside* the `docs-lint` carve-out — one
  paragraph stating that an internal artifact of the delta not in
  English, a `REQ-<n>` line outside the five EARS forms, a finding `text`
  not opening with a Conventional Comments label, or a probe function
  name not in the three-part shape, is a `nit` regardless of `docs-lint`,
  and never more than a `nit`. The output contract's `text:` line gains
  the label prefix. Cap 1340 → whatever the body needs, rounded up to the
  next ten (agent-decided — compression of the existing positioning
  paragraph was ruled out last change; extraction to a reference would
  hide a severity rule from the reader who applies it).

**W1-03 Adversary and blind-runner contracts: probe names, English notes, Acceptance walk**  after: W0-01
- Files: `loom-code/agents/adversary.md`, `loom-code/agents/blind-runner.md`,
  `loom-code/scripts/test_reviewer_agent_single_contract.py` (`AGENT_CAPS`
  for the two, only if a cap is exceeded — coordinate with W1-02 by
  editing distinct dict entries; the merge is textual)
- Test: W0-01's probe-name probe turns GREEN; caps pass.
- Risk: adversary.md's "You own" paragraph is under the six-sentence /
  forty-word cap from the positioning change — the new sentence goes in
  the probe-shape section, not that paragraph. blind-runner.md already
  says the report is in the user's language; it gains one sentence that
  evidence files and probe docstrings are English, and one that the
  report lists, per artifact, whether the language and template rules
  held (that is how Acceptance 1 and 5 get their line in the report).

Wave 2 — station text, then release plumbing. W2-01 waits for wave 1 so
its sentences name the contract clauses that now exist.

**W2-01 One language sentence per station, six stations**  after: W1-01, W1-02, W1-03
- Files: `loom-code/skills/write-plan/SKILL.md`, `build/SKILL.md`,
  `review/SKILL.md`, `ship/SKILL.md`,
  `loom-design/skills/capture-intent/SKILL.md`, `write-spec/SKILL.md`;
  `loom-code/scripts/test_language_station_text.py` (new pin file)
- Test: `test_language_station_text.py` RED first — one test per station
  asserting a sentence that names English and the station's own
  artifact(s); the review station's sentence also names the Conventional
  Comments label on finding `text`; write-spec's also names EARS for
  `REQ-<n>` lines; capture-intent's and ship's state what stays in the
  user's language (intent; blind-run report and PR body). Then W0-01's
  station probe turns GREEN.
- Risk: SKILL.md token caps (soft 5,000 / hard 6,000 tokens) —
  write-plan and review are the heavy ones; one sentence each fits, and
  the pin test reads the sentence rather than a paragraph, so no
  restructuring. Two plugins change in one task: the sentences are
  parallel and a single implementer keeps them parallel (agent-decided).

**W2-02 Changelogs, versions, Codex manifests, KICKOFF reason line**  after: W2-01
- Files: `loom-code/CHANGELOG.md`, `loom-code/.claude-plugin/plugin.json`
  (1.2.4 → 1.3.0), `loom-code/.codex-plugin/plugin.json` via
  `scripts/sync_codex_manifests.py loom-code`; `loom-design/CHANGELOG.md`,
  `loom-design/.claude-plugin/plugin.json` (1.0.3 → 1.0.4) and its Codex
  mirror; `docs/loom/KICKOFF-DEFAULTS.md:12` (the `docs-lint: none` reason
  becomes "no lint adopted yet; internal loom docs are English from
  2026-09-05 — see intent 2026-09-03-artifact-language-policy")
- Test: `scripts/check_version_bump.py` and
  `scripts/sync_codex_manifests.py --check` both exit 0 against the
  branch; the package suite stays green.
- Risk: minor bump for loom-code because contract templates changed
  (consumers scaffold from them); patch for loom-design because only
  station prose moved (agent-decided). The KICKOFF line keeps `none` —
  adopting a lint is out of scope.

Checkpoints: wave-end after wave 1 (the delta is well past 8 files) and
the branch-end round after W2-02 — two of the five, no `after-task`
markers.

Ship-time rule carried from the last two changes: before the branch-end
checkpoint, run `loom-code/scripts/check_doc_citations.py` and every
graduated probe in a depth-1 single-branch clone — CI has no local `main`
ref, and a red there after branch-end costs a fix round plus a
close-commit rebuild.

## Questions asked
1 — what — 你要的是——流程裡給機器讀的產物（spec、plan、審查紀錄、evidence、探針註解、commit、站文字、模板註解）一律英文；給你讀的（intent、三個決策點的對話、盲跑報告、PR 內文）維持你的語言；新 change 起硬切換、舊的不翻；違反只記 nit 不擋。對嗎？
1 — what — 這組用詞規範要不要併進這個 change 的驗收（多一條：「內部文件遵守 RFC 2119 ＋ EARS ＋ 三條通用規則，寫進契約」），還是先只做「一律英文」、用詞規範另開？
1 — what — 這次要不要用 Codex 當第二位讀者？
<!-- the review station copies this section into review.json questions[] at the first checkpoint -->

## Risks
1. user-decided — the templates are folded into this change, limited to
   the three mechanically checkable ones (EARS for `REQ-<n>` lines,
   Conventional Comments labels on finding `text`, three-part probe
   function names); ADR, INVEST, the Mozilla bug shape and the INCOSE
   vague-word list stay out (they need judgement to check).
2. user-decided — Codex is the second reader for this change.
3. The reviewers that run this change's checkpoints are dispatched from
   the *installed* plugin (1.2.4), not from the branch, so the new
   reviewer clause does not govern them; the dispatch input states the
   Conventional Comments label requirement explicitly so this change's
   own review.json satisfies Acceptance 5. Agent-decided.
4. intent Acceptance lines stay in the user's words and are not put into
   EARS (the intent is user-language by contract; EARS binds the English
   `REQ-<n>` lines only). Agent-decided, stated at decision point ①.
5. "Consistent phrasing makes review verdicts drift less" is recorded in
   the intent as a hypothesis, not a claim; nothing in this change
   asserts it. The two evidence files under `evidence/` carry the
   sources and mark every secondary-sourced item.
