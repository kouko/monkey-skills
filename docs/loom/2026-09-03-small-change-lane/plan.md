# Small-change lane — plan
intent: 2026-09-03-small-change-lane@aa776507

## Current State Evidence
- Forward: `loom-code/scripts/loom_checker.py:3023` `check_verdicts` — `len(reviewers) < 2` is the whole floor; no notion of a lane. `check_second_vendor_honoured` (`:2967`) reads KICKOFF `second-vendor` (`<cli> | none`, manifest `:132`) and demands that vendor or a dated `fallback`. Lane inputs already exist: `artifact_types` (`:2427`, manifest §6 mapping `:139-154`), `interface_surfaces` (`:360`), `changed_paths` (`:492`).
- Reverse: `_cmd_push` (`:1653`) calls every `push.*` rule; the station text that tells the orchestrator how many readers to dispatch is `loom-code/skills/review/SKILL.md` §2 ("two fresh-context reviewers at minimum"); the second-vendor question wording lives in `loom-code/skills/write-plan/SKILL.md` step 3 and `loom-design/skills/capture-intent/SKILL.md` step 4; severity vocabulary (fatal/important/nit) is defined in `loom-code/skills/review/references/lenses.md` and `loom-code/agents/reviewer.md`.
- Error: the second real change (package-tests-run-in-parallel) — 7 review rounds for four sentences of wording, 85 min for a one-flag change; review.json rounds 2–7 of that change are the evidence. Codex backend 404 ×3 forced the documented fallback.
- Data: review.json (contract/templates/review.json, 1.0.0) has `vendors[]`, `verdicts[]` with `fallback`, `dispatch[]`, `open_findings[]` with `severity`; no top-level field for a per-change vendor answer. KICKOFF-DEFAULTS grammar list is `manifest.yaml:125-137`.
- Boundary: `--list-rules` stays 27 (no new rule id; `push.verdicts-ge-2` keeps its id and message shape, its floor becomes lane-dependent). `contract/templates/**` untouched. Probe dedup, probe graduation, language policy are other intents.

## Task DAG

**W0-01 Adversary-first probes for the checker changes**　after: —　(adversary, dispatched before W0-02 per intent §4)
- 檔：`docs/loom/2026-09-03-small-change-lane/evidence/probes/test_abuse_change_lane.py` — executable cases against the NOT-yet-written behaviour: lane recompute (each pre-authorised class passes; one non-test `.py` line, one `hooks/**` file, one `SKILL.md`, one `templates/**` file, two plugins → full lane), `push.verdicts-ge-2` accepting one verdict only in the small lane, `second-vendor: ask` honoured by the review.json answer, `docs-lint` grammar accepted. Written against the temp-repo helpers of `loom-code/scripts/test_loom_checker_push.py`.
- 測：the file itself; at W0-01 commit most cases FAIL (that is the RED for W0-02); at least three are marked with the expected pre-change outcome so the adversary's own run is honest.
- 風：agent-decided — probes name the function `change_lane(repo, reviewed_id) -> "small"|"full"` and the review.json field `second_vendor: "<cli>|none"`; W0-02 implements those names.

**W0-02 Checker: lane recompute, lane-dependent verdict floor, `second-vendor: ask`, `docs-lint` grammar**　after: W0-01　review: after-task
- 檔：`loom-code/scripts/loom_checker.py` (`change_lane`; `check_verdicts` floor = 1 when small, 2 otherwise, message says which lane and why; `check_second_vendor_honoured`: KICKOFF `ask` → the answer is review.json top-level `second_vendor` (`<cli>` or `none`); missing answer blocks; `none` means single-vendor is complete); `loom-code/contract/manifest.yaml` (`second-vendor` grammar `<cli> | none | ask`; new line `docs-lint: <command> | none`; review.json field `second_vendor` documented); `loom-code/contract/templates/review.json` is NOT touched (field optional); `loom-code/scripts/test_loom_checker_push.py` (unit tests mirroring the probes).
- 測：W0-01 probes go green; new unit tests; `--list-rules` prints 27; package suite green.
- 風：lane definition is mechanical: small iff every changed path (excluding `docs/loom/<change-id>/**` records) maps to artifact type in {docs, memory, evidence, intent, plan, standing} or is a test file (`test_*.py`, `*_test.py`, `tests/**`) or a CI/config file (`.github/**`, `requirements*.txt`, `*.toml`, `*.yml`, `*.yaml`, `*.json` outside `contract/`), AND touches no interface surface, AND all paths sit under one top-level plugin dir (or none). agent-decided: manifest-typed `code` that is not a test → full lane, even one line.

**W1-01 Review station text: lane, stateful fix rounds, severity by consequence, nit batch, docs-lint clause**　after: W0-02
- 檔：`loom-code/skills/review/SKILL.md` (§1 lane table; §2 reader count by lane; new §8a "fix rounds": delta from the previous round's reviewed commit, resumed reader with its own finding list, no new findings outside the fix, no probe re-run, rebuttal → dismissed, third round → design re-look by a higher tier; §6 severity: important = a reader would act wrongly or a checker/CI-relied fact is wrong, else nit; nits never open a round, batched before ship); `loom-code/skills/review/references/lenses.md` (severity definitions); `loom-code/agents/reviewer.md` (severity rule; docs-lint declared → no style findings; not declared → style ≤ nit; never re-flag outside a fix round's delta). Word caps: SKILL.md ≤ 4,500 words — move the fix-round procedure to `references/fix-rounds.md` if needed.
- 測：`python3 -m pytest loom-code/scripts/test_skill_word_caps.py -q` (or the CI word-cap check) green; a cold sonnet reader given only review/SKILL.md answers "how many readers for a docs-only change" and "what happens on the third NEEDS_REVISION" correctly (record in evidence).
- 風：prose gates get `<!-- gate: review.fix-round-scope -->` markers only if the mechanism population check requires it — check `mechanisms.yaml` and keep the net count unchanged (replace, don't add).

**W1-02 Build / ship / write-plan / capture-intent text: probes-first, nit batch, second-vendor ask**　after: W0-02
- 檔：`loom-code/skills/build/SKILL.md` (a plan task whose files map to `gate` → dispatch the adversary first; the implementer's RED is one of its probes); `loom-code/skills/ship/SKILL.md` (§3.5 nit batch: one commit before the push, confirmed by the original reader in one line, no new round); `loom-code/skills/write-plan/SKILL.md` step 3 and `loom-design/skills/capture-intent/SKILL.md` step 4 (`second-vendor: ask` → one plain sentence per change: "這次要不要用 Codex 當第二位讀者？" recorded in Questions asked; small lane → not asked; answer written to review.json `second_vendor` at the first checkpoint); `loom-code/skills/write-plan/SKILL.md` (docs-lint: never installed or asked on first contact; KICKOFF absent = none).
- 測：word-cap check green; cold reader test as in W1-01 for build ("what do you do first for a gate task").
- 風：capture-intent lives in loom-design → that plugin's version bumps too (W1-03).

**W1-03 Versions, changelogs, mirrors**　after: W1-01, W1-02
- 檔：`loom-code/.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` (1.1.0), `loom-design/...` (1.0.2), both CHANGELOG.md, root `README.md` version lines, `scripts/sync_codex_manifests.py --check`, `.codex/hooks/` refresh via `codex_scaffold.py --repo .` (content-bound exemption applies).
- 測：`python3 scripts/check_version_bump.py`, `sync_codex_manifests.py --check loom-code loom-design`, package suite green.
- 風：root README version list is the 15th-time trap — grep every carrier.

**W1-04 This repo's KICKOFF and the cost note**　after: W1-03
- 檔：`docs/loom/KICKOFF-DEFAULTS.md` (`second-vendor: ask — …`, `docs-lint: none — loom docs are Traditional Chinese here; see 2026-09-03-artifact-language-policy`); `docs/loom/2026-09-03-small-change-lane/evidence/cost.md` (timestamps of this change: confirmed → PR; rounds per checkpoint).
- 測：`loom_checker.py standing` and `push` still exit 0 with the new KICKOFF lines.
- 風：none.

## Questions asked
1 — what — 你要的是讓小改動在 20 分鐘內走完 loom：預授權類別自動走小車道（一位讀者＋測試＋探針，Acceptance 全機械免盲跑）；修正輪只讀修正 commit、原讀者帶清單複核、不重跑探針、第 3 輪重看設計；嚴重度看後果，nit 不擋不開輪、ship 前批次修；gate 類 task 探針先寫；second-vendor 多 `ask`；docs-lint 可宣告不阻擋；量測下一個小 change ≤20 分。對嗎？（答：對，確認）
1 — what — 這次包含哪幾條 intent？（答：只有 small-change-lane，吸收三條；language-policy、B、C 另跑）

## Risks
1. This change itself touches `gate` and `skill` → full lane under its own rule; but the user asked that the NEW rules apply to this change's process now: stateful fix rounds (only fix commits, resumed reader, no findings outside the delta), severity by consequence, nits batched, probes-first for W0-02. Probes are still re-run at each reviewed sha because the shipped checker requires it (35 s).
2. Two checkpoints: after-task W0-02 (code+gate lens, the risky part) and branch-end (skill+docs). Budget 2/5.
3. `push.verdicts-ge-2` keeps its id; its message now names the lane so a single-verdict record in the full lane is still explained.
4. Word caps on four SKILL.md files: W1-01/W1-02 may push review/SKILL.md over the soft cap — extract to references, never compress rule semantics.
