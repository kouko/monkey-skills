# loom artifacts carry a charter: content boundaries and post-sign-off edit rights — plan
intent: 2026-09-05-artifact-charter-boundaries-and-edit-rights@1b3f9a10
charter: 1.0

## Current State Evidence
- Forward: `loom-code/contract/manifest.yaml:75-134` declares each artifact's fields only; no row says what a field must not hold or who may edit it after sign-off.
- Reverse: `loom-code/skills/build/SKILL.md:53-62` derives progress from git and names `claimed`/`blocked` as the only transient marks; nothing recomputes that, and `build/SKILL.md:356-360` adds `W<n>-memory` as the second allowed edit.
- Error: `loom-code/skills/review/references/lenses.md:60` defines omission as any missing obligation, so a reviewer can demand more plan prose; `loom-code/agents/reviewer.md:32` names the plan ground truth.
- Data: `loom-code/scripts/loom_checker.py:1570-1600` is the only rule reading plan text (`intake.after-task-budget`); `loom-code/scripts/loom_checker.py:2416-2442` checks review.json keys, not accretion; review `SKILL.md:345-354` says "never rewrite an earlier round" in prose only.
- Boundary: no artifact records which contract version it was confirmed under (checker `:4160-4179` checks only the floor), so grandfathering needs a stamp the new templates write.

## Task DAG
Wave 0 — the charter is the source of truth; every later task cites it.

**W0-01 Charter rows in the contract manifest, rendered by the checker**  after: —
- Files: `loom-code/contract/manifest.yaml`, `loom-code/contract/README.md`, `loom-code/scripts/loom_checker.py`, `loom-code/scripts/check_mechanisms.py`, `docs/loom/evidence/mechanisms.yaml`, new `loom-code/scripts/test_contract_charter.py`
- Test: `loom_checker.py charter` prints one row per artifact (intent, spec, plan, review, blind-run-report, memory, kickoff-defaults, dispatch) with must / must-not+goes-to / sign-off / edits-after all non-empty; rule `contract.charter-complete` blocks a row with an empty column.
- Risk: agent-decided — charter keys live under `artifacts.<name>.charter` in manifest.yaml, not a second markdown table, because the manifest is already the checker-read SSOT; the `charter` subcommand is the human view.

Wave 1 — recomputed rules behind the plan and review rows. Sequential: all three edit the `RULES` table.

**W1-01 Plan field caps**  after: W0-01
- Files: `loom-code/scripts/loom_checker.py`, `loom-code/contract/templates/plan.md`, new `loom-code/scripts/test_plan_field_caps.py`
- Test: a plan whose Test field runs 41 words is blocked by `plan.field-caps` naming the task and field; a 40-word one passes; a plan without `charter:` frontmatter is skipped.
- Risk: agent-decided — caps: Test ≤40 words, Risk ≤40, Files paths only ≤8 entries, Risks items ≤40, Current State Evidence lines ≤30; taken from the 215-word plan's one-line fields.

**W1-02 Plan edits after the plan commit**  after: W1-01  review: after-task
- Files: `loom-code/scripts/loom_checker.py`, new `loom-code/scripts/test_plan_edits_after_commit.py`
- Test: plan.md hunks since the `docs(loom): plan <id>` commit pass only as `blocked`/`claimed` marks, a `W<n>-memory` task, an un-landed task (no `Task:` trailer), or a Questions-asked append; an appended Risks item is blocked naming its goes-to.
- Risk: agent-decided — the baseline is the first plan commit on the branch, found by message, because no other sign-off stamp exists; rule runs at push and at `intake build`.

**W1-03 review.json accretion**  after: W1-02
- Files: `loom-code/scripts/loom_checker.py`, `loom-code/contract/templates/review.json`, new `loom-code/scripts/test_review_round_append_only.py`
- Test: between two review-only commits, `verdicts`/`probes`/`open_findings`/`dispatch` may only gain entries, existing entries byte-equal; `reviewed_sha`/`scope`/`cost` may be replaced; `questions` written once; a rewritten earlier verdict is blocked by `review.round-append-only`.
- Risk: agent-decided — enforcement keyed on a top-level `charter` stamp in review.json, absent in older changes, so open changes elsewhere keep passing.

Wave 2 — prose follows the rules. Parallel: disjoint files, each cites W0-01's rows by path.

**W2-01 write-plan station and plan template cite the charter**  after: W1-01, W1-02
- Files: `loom-code/skills/write-plan/SKILL.md`, `loom-code/contract/templates/plan.md`
- Test: `test_write_plan_intake.py` word cap still passes (≤4500); a cold sonnet reader given only SKILL.md writes a plan whose fields pass `plan.field-caps`; the spec-change path is one affirmative sentence in the plan template comment.
- Risk: agent-decided — SKILL.md gains ≤80 words; if over cap, the task-size paragraph moves to `references/`.

**W2-02 build, review, fix-rounds and lenses recompute from the charter**  after: W1-02, W1-03
- Files: `loom-code/skills/build/SKILL.md`, `loom-code/skills/review/SKILL.md`, `loom-code/skills/review/references/fix-rounds.md`, `loom-code/skills/review/references/lenses.md`, `loom-code/scripts/test_review_station_text.py`
- Test: lenses.md omission row for plan reads "the implementer cannot start"; must-not content is scored inconsistency citing the charter; fix-rounds.md names review.json as the record; station texts stay under their caps.
- Risk: agent-decided — one `<!-- gate: charter.plan-omission-narrow -->` marker registered in mechanisms.yaml; no other new prose gates.

**W2-03 Four agent contracts point at the charter**  after: W0-01
- Files: `loom-code/agents/reviewer.md`, `loom-code/agents/adversary.md`, `loom-code/agents/blind-runner.md`, `loom-code/agents/implementer.md`, `loom-code/scripts/test_probes_sentence_cap.py`
- Test: each agent file carries exactly one sentence naming `contract/manifest.yaml` charter rows as the artifact boundary; positioning paragraphs stay ≤6 sentences, ≤40 words each.
- Risk: agent-decided — one sentence per file, no rubric copied, because the charter is the only correct copy.

Wave 3 — evidence for the human acceptance lines, mirror, release.

**W3-01 A/B evidence: a long plan rewritten under the charter**  after: W2-01
- Files: `docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/ab-plan-original.md`, `evidence/ab-plan-charter.md`, `evidence/ab-implementer-runs.md`
- Test: the rewritten copy passes `plan.field-caps`; one cold implementer dispatch per version on the same task, status reports saved verbatim; NEEDS_CONTEXT count of the charter version ≤ original.
- Risk: agent-decided — sample is a kumiko plan (already cited in this repo's docs); the dbt project's plan is not copied here.

**W3-02 Codex mirror, version 1.6.0, changelog**  after: W2-01, W2-02, W2-03
- Files: `.codex/hooks/loom_checker.py`, `.codex/hooks/contract/**`, `loom-code/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `loom-code/CHANGELOG.md`, `loom-code/README*.md`
- Test: `test_codex_mirror_matches_checker.py` passes; `test_mirror_stamp_version_matches_plugin_manifest` passes at 1.6.0; package tests green.
- Risk: agent-decided — minor bump: new rules and a new contract section, no removed field.

**W3-memory Memory step — graduated probes and store entries**  after: W3-01, W3-02
- Files: graduated probe copies under `loom-code/scripts/test_probes_*.py`; `docs/loom/memory/` entries
- Test: store integrity check passes; graduated copies pass in the package run.
- Risk: agent-decided — implementer is the orchestrator (`fresh_context: false`), dispatch entry written before the work.

## Questions asked
① — what — 範圍：這次只管 plan.md，還是 review.json 也一起？（答：所有類型的文件，包含但不限 intent、spec、plan、review）
① — what — 「implementer 拿到縮短後的派工單，NEEDS_CONTEXT 不比現在高」要當 Acceptance 還是只當 Constraints？（答：當驗收條件）
① — what — 重述：你要的是每種 loom 文件都有憲章…對嗎？（答：重點是正負向都要寫，該寫什麼與不該寫什麼）
① — what — 重述（修正後）：每列正負向兩欄、定稿點、定稿後允許變動，checker 重算…對嗎？（答：對）
① — consequence — 新 checker 規則只對上線後 confirmed 的變更生效，舊變更照舊，可以嗎？（答：舊的照舊）
① — what — 這次要不要用 Codex 當第二位讀者？（答：用 Codex）

## Risks
1. user-decided — new rules apply only to artifacts carrying the new `charter:` stamp; older open changes keep passing (grandfathering by template stamp, not by date).
2. user-decided — Codex is the second reader for this change; `second_vendor: codex` goes into review.json at the first checkpoint.
3. Field caps may starve implementers of anchors; W3-01 measures it and Acceptance 4 decides, not this plan.
4. Three checker rules land in one wave; a shared helper for "plan commit baseline" must exist before W1-02 and W1-03 reuse it.
