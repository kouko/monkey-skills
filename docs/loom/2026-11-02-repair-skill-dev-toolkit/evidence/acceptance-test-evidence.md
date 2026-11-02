# Repair skill-dev-toolkit — acceptance test evidence

Tried on 2026-11-03, in a clean copy of the project at 8b174cd17.

## Environment and setup

- Tested full SHA: `8b174cd175da25fe53837489ed8a979c528da0c0`.
- Independent tester did not implement the change. Original user checkout was not edited.
- Attempted `git worktree add --detach /private/tmp/monkey-skills-acceptance-8b174cd 8b174cd175da25fe53837489ed8a979c528da0c0`; sandbox refused writing the original repository's worktree metadata. Fallback: `git clone --no-hardlinks --no-checkout /private/tmp/monkey-skills-repair-qnf38yi7 /private/tmp/monkey-skills-acceptance-8b174cd`, then `git checkout --detach 8b174cd175da25fe53837489ed8a979c528da0c0`.
- README clean-checkout setup was read. Dependency installation and host plugin changes were excluded by the station. Reused existing interpreter `/Users/kouko/.conda/envs/dbt-redshift/bin/python3` with pytest and PyYAML; no packages were installed. Local package imports, actual CLI subprocesses, and structure checks loaded successfully. This is source-checkout usability, not marketplace installation or host activation validation.
- Initial and final `git status --short` were empty in the tested clone. The report is written only to the active repair worktree after testing.
- No external provider/model service was called. Optimizer evaluator/improver are explicitly offline stubs. Report merger model strings in fixtures are test input, not proof of a model run.
- No skipped-by-instruction marker appears in committed intent Constraints or plan Risks. No important-or-worse dismissed findings were handed to this tester.
- Full package suite declared for finalize-review: `python3 -m pytest scripts/ -q`. Never run by this tester. The complete toolkit suite was also not run; only criterion-specific files below.

## Focused commands and recorded results

Command A, interpreter above followed by:
```sh
-m pytest skill-dev-toolkit/tests/test_creator_commands.py skill-dev-toolkit/tests/test_equivalence_order.py skill-dev-toolkit/tests/test_blind_harness.py skill-dev-toolkit/tests/test_preference_export.py scripts/test_preferences_single_choice.py -q
```
Output: `46 passed in 1.22s`, exit 0.

Command B, same interpreter:
```sh
-m pytest skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py skill-dev-toolkit/tests/test_creator_metadata_contract.py skill-dev-toolkit/tests/test_refactor_policy.py skill-dev-toolkit/tests/test_tuning_policy.py skill-dev-toolkit/skills/skill-refactor/scripts/test_package_mode_contract.py skill-dev-toolkit/skills/dogfood-skill-testing/test_skill_structure.py skill-dev-toolkit/skills/skill-consistency-check/scripts/test_plan_groups.py skill-dev-toolkit/skills/skill-consistency-check/scripts/test_merge_report.py skill-dev-toolkit/skills/skill-consistency-check/scripts/test_skill_text.py -q
```
Output: `83 passed in 1.89s`, exit 0.

Independent realistic local execution, same interpreter:
```sh
-m pytest /private/tmp/test_acceptance_repair_behavior.py -q -s
```
Output: `3 passed in 0.28s`, exit 0. Full replay source is preserved below. This combines actual commands with explicit tester interpretation of prose-only adoption policies; it does not invent a product human-tally API.

## 1. 既有技能打包、評估彙整與描述優化入口可完成其已宣告的職責，不再因入口內容無法解析而中斷。

- How I tried it: Command A's six parameterized creator command cases.
- What came back: actual packaging CLI produced a ZIP-readable .skill archive containing SKILL.md and bundled reference data, excluding evals/cache; invalid path returned nonzero without archive. Aggregator CLI recomputed four runs into JSON/Markdown: with-skill mean .75, stddev .3536, duration mean 3, tokens mean 15, delta +.50; missing input returned nonzero. Optimization ran three bounded iterations with two improved descriptions; held-out inputs were absent from improvement history; backend error propagated before improvement.
- Evidence: `test_creator_commands_valid[package_skill|aggregate_benchmark|run_loop]`, `test_creator_commands_invalid[package_skill|aggregate_benchmark|run_loop]` in `skill-dev-toolkit/tests/test_creator_commands.py`.
- Boundary: optimizer backends were stubs; no paid backend or actual triggering-quality result. Restored orchestration and input/error handling are what passed.

## 2. 結構等價檢查能拒絕不符合既定呼叫順序的結果，同時保留已定義的合法容許差異。

- How I tried it: Command A's 14 order/tolerance cases, plus a historical comparison against pre-repair code.
- What came back: identical traces and one compatible insertion/deletion retained PASS; reordered Read/Write, multiple extra calls, changed vocabulary and incompatible deletion rejected. Missing-trace existing behavior retained.
- Evidence: `test_ordered_trace_tolerance`, `test_reordered_trace_rejected` in `skill-dev-toolkit/tests/test_equivalence_order.py`. On the same Read,Write versus Write,Read fixture, `check_tool_calls` from `3b1b225d` returned True while tested HEAD returned False.
- Boundary: deterministic structural comparison does not establish Layer 2 semantic equivalence.

## 3. 盲測的截短顯示及選擇前全文檢視不會從工具附加資訊洩漏版本身分，選擇仍對應原來的盲標籤。

- How I tried it: Command A's ten real harness CLI rounds across truncated/untruncated output, choices a/b/multiple/none/refine, invalid input, and clarification.
- What came back: complete ordinary A.md/B.md copies had source-identical bytes; no symlinks; neutral new directory each round; printed metadata omitted identity-bearing source names; decoded choices matched the same display labels. Invalid/unlocked records omitted label assignment and identity. Source bytes remained unchanged.
- Evidence: `test_blind_full_view_same_choice`, `test_identity_path_not_displayed` in `skill-dev-toolkit/tests/test_blind_harness.py`.
- Boundary: authored output content remains authored content, including fixture text containing the word baseline; the repaired guarantee concerns tool-added metadata. No live host UI was claimed.

## 4. 有效的原始版本偏好可正確匯出；有效紀錄、衍生比較資料與準備條件的計數定義一致。

- How I tried it: Command A's 11 export/trainer cases and five graduated single-choice regression cases.
- What came back: ADOPT candidate and DROP explicit baseline each used one record to emit two correctly oriented pairs; inactive trainer recognized one usable record, reported unimplemented training and wrote no model. None/multiple/refine, missing identity/hash/prompt hash, equal hashes, malformed variants and duplicate identity did not become winners. One usable record with 1002 pairs still failed the default 1000-record readiness threshold; both consumers reported 1 usable, 1 skipped, 1002 pairs. Original JSONL byte content remained identical.
- Evidence: `test_explicit_single_preferences_export`, `test_unusable_preferences_not_ready` in `skill-dev-toolkit/tests/test_preference_export.py`; `scripts/test_preferences_single_choice.py::test_preferences_nonsingle_rejected` rejected A+B, A,C, padded multiple/none/refine.
- Boundary: no training activated, no existing user preference file opened.

## 5. 獨立複核保留的八項規則衝突或資訊不足已消除，同一適用情境不再產生相反要求。

- How I tried it: Command B checks all eight retained rule surfaces, followed by fresh interpretation and execution of representative cases (not merely grep results).
- Description authority: read `references/description-design.md`; positive specific triggers first, at most 2–3 adjacent-skill exclusions, optional <=50-character belt only for mixed-language prompts. Creator/judge resolved-authority tests passed; judge whole-file `wc -w` = 4472, below 4500.
- Metadata: shared case metadata ownership and explicitly supplied grader path retained; run outputs remain local. `test_shared_case_metadata` and `test_run_local_metadata_not_required` passed. This is instruction/schema consistency, not a paid grader execution.
- Voting and ablation: actually invoked bundled `multi_judge.py --ensemble <fixture>`. E,E,U -> PASS_MODERATE exit 0; E,E,N vague dissent -> FLAG_TIER_2 exit 2; E,N,U concrete warning loss -> FLAG_TIER_2 exit 2; E,N,U vague -> FAIL exit 1. Current ablation consumes those three-judge outcomes; the dated two-judge example is historical, not current executable guidance. Native judges were not fabricated by these fixture votes.
- Extraction: exported real creator package at tested HEAD using bundled package_gate API; isolated candidate moved an actual whole section into a new bundled reference. Target words 2894 -> 2488 (-406), package words 22783 -> 22783 (0), package bytes 188205 -> 188205 (0). Accounting PASS means measurement valid; interpreted whole-package Q2 as REJECT (0% reduction), so no application. This used genuine repository prose, not invented source skill data.
- Human agreement: directly parsed a+b -> multiple, n -> none, r -> refine, a -> locked baseline single, b -> locked candidate single. Applied the read rule: DEFER/no edit, DROP/no edit, REFINE/no edit, DROP/no edit, ADOPT/edit, respectively. 2/3=.6667 <.70 -> ESCALATE; 3/4=.75 -> majority. Those tally/adoption dispositions are tester execution of instructions, not an unimplemented product reducer.
- Audit evidence separation: two fresh native auditor contexts received ONLY the prompts below (rubric + source/artifacts), no full skill, author rationale or executor trajectory. Both judged Artifact A PASS; the second correctly rejected the intentionally wrong Artifact B. On the informed side, I compared the native-call packets and returned judgments to Probe B's requirement: artifacts and rubric went blind; invocation/dispatch sequence stayed informed. Every observed call is recorded here; no unseen executor procedure was inferred. These synthetic arithmetic cases test audit separation and domain-error detection only, not full skill dogfood or triggering fidelity.
- Evidence: `test_refactor_policy_consistent`, `test_unsafe_refactor_policy_rejected`, `test_human_decision_policy`, `test_ties_never_adopt`, dogfood structure tests; independent probe source below; native audit records below.
- Boundary: exact host model/version is unobservable. Packaged dispatch oracle explicitly returned inheritance, and no version pin or cross-provider generalization is claimed. This repairs evidence ownership without pretending all legacy dogfood guardrails have been empirically validated.

## 6. 大小警示與報告宣告的驗證範圍相符，保留既有分組政策並正確表達證據限制。

- How I tried it: Command B's planner/report CLI tests against exact 25000/25001/28000/30000/30001 sizes, small/large/core-overlimit cases, the real retained 25135-token corpus, and report merge/coverage/model cases.
- What came back: no split at <=30000, split above 30000; groups exceeding nominal 25000 warn even unsplit. Retained corpus remained one group, 25135 tokens, over_limit true. Report explains approximate 25k scope and conservative nominal bound, explicitly avoids proven accuracy-cliff claims, records uncovered pairs and Markdown-only coverage, and qualifies unmatched model strings.
- Evidence: `test_nominal_notice_and_split_boundaries`, `test_T_validated_package_reads_whole`, `test_over_limit_warning_is_cause_neutral`, `test_markdown_only_coverage_note`, `test_limits_and_models_listed` in bundled planner/report tests.
- Boundary: planner token estimates and historical corpus evidence are not new empirical model-accuracy validation.

## 7. 驗證能實際檢出本次已確認的缺陷；過時的文件位置檢查不再取代行為檢查，相關套件與既有倉庫檢查通過。

- How I tried it: executed Commands A/B and independent probes, plus repository checks listed below. Read relevant workflow routing and verified graduated preference regression is selected.
- What came back: 46+83 focused tests passed, independent probe 3 passed; structure checker scanned all six toolkit skills, all PASS; shared conventions 3 checked, 0 drift failures, 0 read errors; manifest drift checker exit 0. Historical command content at 3b1b225d produced SyntaxError line 3 in all three modules; original order comparator accepted the reordered trace while tested code rejected it, demonstrating observable regression sensitivity.
- Commands: `python3 scripts/check-skill-structure.py skill-dev-toolkit`; `python3 scripts/check-shared-conventions-drift.py`; `python3 scripts/sync_codex_manifests.py --check skill-dev-toolkit`.
- Evidence: `.github/workflows/skill-dev-toolkit-ci.yml` routes toolkit and scripts changes into focused toolkit discovery, explicit hidden-description suite, declared repository package suite, structure, shared drift and manifest checks. `test_skill_text.py` current reference checks passed.
- Full-suite boundary: acceptance's works verdict cites successful criterion tests and the automated test suite that runs before acceptance and blocks it on failure; `finalize-review` is responsible for `python3 -m pytest scripts/ -q`. No full package result is claimed here. GitHub CI execution, installation and host activation remain unverified by this report.

## Native audit packets and results

Dispatch resolver was run as a local stdlib command with:
```json
{"event":"initial","main_profile":{"model":null,"effort":null},"task_evidence":{"trust_boundary":true},"capabilities":{},"inheritance_guaranteed":true,"completed_redispatches":0}
```
Output:
```json
{"completed_redispatches":0,"effective_profile":"inherited","outcome":"dispatch","overrides":null,"reason":"unobservable-main-profile","requested_profile":null,"task_class":"complex","uncertainty":null}
```
Oracle: `/Users/kouko/.codex/plugins/cache/loom/loom-code/3.56.0/scripts/dispatch_profile.py`.
Both `collaboration.spawn_agent` calls used `fork_turns:"none"`, omitted model/effort overrides, and prohibited tools/external services.

Run 1 prompt, supplied in full:
> Judge this artifact against the supplied rubric; you have NO context about how it was produced. This is an isolated native auditor, no external provider/model service, no tools needed. Rubric: output must list exactly all account totals from source rows and correct sum; columns account and total_usd; no unsupported accounts. Source rows: Tea 12, Tea 8, Ink 7. Artifact: account,total_usd / Tea,20 / Ink,7 / TOTAL,27. Return coarse verdict PASS/FAIL/UNVERIFIED, arithmetic, and only evidence actually given. Do not infer or claim procedure compliance, tool usage, or prior gates.

Run 1 response:
> PASS. Columns: account,total_usd. Tea: 12+8=20. Ink:7. Sum:20+7=27, matching TOTAL summary. Account rows contain only Tea and Ink, both supported by source.

Run 2 prompt, supplied in full:
> Judge this artifact against the supplied rubric; you have NO context about how it was produced. Isolated native auditor, no tools or external services. Rubric: output must list all account totals computed from source rows, plus optional TOTAL summary; columns account,total_usd; no unsupported account rows. Source rows: Tea 12, Tea 8, Ink 7. Artifact A: account,total_usd / Tea,20 / Ink,7 / TOTAL,27. Artifact B: account,total_usd / Tea,21 / Ink,7 / TOTAL,28. Return coarse PASS/FAIL/UNVERIFIED for each, arithmetic and only supplied evidence. Do not infer or claim producer procedure, tool usage, or gate compliance.

Run 2 response:
> Artifact A: PASS — Tea 12+8=20; Ink=7; optional TOTAL=27. No unsupported accounts.
> Artifact B: FAIL — Tea should be 20, not 21; TOTAL should be 27, not 28. Ink=7 is correct.

Informed check: the observed trajectory is rule read -> resolver -> fresh rubric/artifact-only dispatch -> results -> informed comparison. There is no claimed real executor workflow behind the intentionally manufactured arithmetic artifacts. Procedure compliance beyond this visible isolation sequence is UNVERIFIED. Exact model pinning is UNVERIFIED; these native samples establish no provider/host activation claim.

## Independent probe replay source

Save the following code to a temporary file and invoke it with the existing pytest interpreter after adjusting ROOT to an independent clone at the tested SHA and OUT to an unused temporary directory. No product files are modified; extraction edits only its isolated candidate.

```python
"""Independent offline acceptance probes, not a live-provider dogfood run."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('/private/tmp/monkey-skills-acceptance-8b174cd')
PY = sys.executable
OUT = Path('/private/tmp/acceptance-repair-fixtures')
OUT.mkdir(exist_ok=True)

def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_vote_cases_real_cli_expected():
    """Read the current rule and execute its representative vote outcomes."""
    script = ROOT/'skill-dev-toolkit/skills/skill-refactor/scripts/multi_judge.py'
    for label, votes, reason, expected, code in [
        ('uncertain','EEU','same observable behavior','PASS_MODERATE',0),
        ('dissent','EEN','different emphasis','FLAG_TIER_2',2),
        ('specific','ENU','drops the warning','FLAG_TIER_2',2),
        ('weak','ENU','different emphasis','FAIL',1)]:
        names = {'E':'equivalent','U':'uncertain','N':'not_equivalent'}
        path = OUT / f'{label}.json'
        path.write_text(json.dumps({'judges':[{'verdict':names[v],'reason':reason} for v in votes]}))
        proc = subprocess.run([PY,str(script),'--ensemble',str(path)],capture_output=True,text=True)
        result=json.loads(proc.stdout)
        print(label, proc.returncode, json.dumps(result,sort_keys=True))
        assert (result['consensus'],proc.returncode)==(expected,code)

def test_human_deferral_interpretation_expected():
    """Execute the harness parser then apply the read instruction's adoption rule."""
    harness=load('acceptance_harness','skill-dev-toolkit/skills/skill-tuning/scripts/ab_harness.py')
    labels={'A':{'identity':'baseline'},'B':{'identity':'candidate'}}
    expected={'a+b':'DEFER','n':'DROP','r':'REFINE','a':'DROP','b':'ADOPT'}
    for raw,want in expected.items():
        pick=harness.parse_pick(raw,labels)
        verdict=({'multiple':'DEFER','none':'DROP','refine':'REFINE'}.get(pick['type'])
                 or ('DROP' if pick['identity']=='baseline' else 'ADOPT'))
        print('human pick',raw,pick,'=>',verdict,'edit=',verdict=='ADOPT')
        assert verdict==want
    # Policy has no executable human tally reducer: execute this interpretation
    # explicitly and disclose that boundary rather than inventing a product API.
    for winners,total,expected in [(2,3,'ESCALATE'),(3,4,'majority')]:
        result='majority' if winners/total>=.70 else 'ESCALATE'
        print('agreement',winners,total,winners/total,result)
        assert result==expected

def test_extraction_accounting_real_package_expected():
    """Actually relocate repository prose and account immutable original bytes."""
    gate=load('acceptance_package_gate','skill-dev-toolkit/skills/skill-refactor/scripts/package_gate.py')
    workspace=OUT/'extraction'
    manifest=gate.export_baseline(ROOT,workspace,'skill-dev-toolkit/skills/skill-creator-advance','HEAD')
    digest=hashlib.sha256(manifest.read_bytes()).hexdigest()
    candidate=workspace/'candidate'
    shutil.copytree(manifest.parent/'skill',candidate)
    target=candidate/'SKILL.md'
    before=target.read_text()
    start=before.index('\n## ')
    end=before.index('\n## ',start+1)
    moved=before[start:end]
    target.write_text(before[:start]+before[end:])
    (candidate/'references/acceptance-extracted.md').write_text(moved)
    result=gate.account_package(manifest,digest,candidate,'SKILL.md')
    print('extraction',json.dumps(result,sort_keys=True))
    assert result['verdict']=='PASS'
    assert result['target']['words']['delta']<0
    assert result['package']['words']['delta']==0
    reduction=1-result['package']['words']['candidate']/result['package']['words']['baseline']
    print('whole-package reduction',reduction,'overall Q2 REJECT')
    assert reduction<.05

```
## Captured independent probe output

```text
uncertain 0 PASS_MODERATE (2 equivalent, 1 uncertain)
dissent 2 FLAG_TIER_2 (2 equivalent, 1 not_equivalent)
specific 2 FLAG_TIER_2 (specific-behavior-diff dissent overrides majority)
weak 1 FAIL (1 equivalent, 1 not_equivalent, 1 uncertain)
human pick a+b multiple => DEFER edit=False
human pick n none => DROP edit=False
human pick r refine => REFINE edit=False
human pick a baseline single => DROP edit=False
human pick b candidate single => ADOPT edit=True
agreement 2/3 = 0.6666666666666666 ESCALATE
agreement 3/4 = 0.75 majority
extraction: target words 2894 -> 2488, package words 22783 -> 22783
whole-package reduction 0.0 overall Q2 REJECT
3 passed in 0.28s
```

## Re-run on 2026-11-03, at 834668cce

Tried on 2026-11-03, in a clean copy of the project at 834668cce.

### Setup, scope and correction

- Exact tested HEAD: `834668cce32659ec24c8f997fc9f267840248d62`.
- Fresh local clone `/private/tmp/monkey-skills-acceptance-834668cce`, detached at that exact SHA; initial and final tracked/untracked status empty. README setup rechecked. No dependency installs or host changes: reused `/Users/kouko/.conda/envs/dbt-redshift/bin/python3`, which loaded the commands and focused tests successfully.
- Read the complete fix diff `35d507e2a33759a29b7990b4ab4b1a2e0275e14a..834668cce32659ec24c8f997fc9f267840248d62`, including all 13 changed paths and their consumers. Also checked `8b174cd17..834668cce` for every carried-over surface; relevant paths had no diff.
- No important/fatal findings were dismissed. Code and skill review findings were repaired, including the extra translated extraction examples found by the parent.
- Correction to first-run evidence: the arithmetic-only audit above proved rubric delivery and arithmetic judgment, but did NOT prove detection of an omitted artifact criterion or a skipped declared gate. Its earlier claim of sufficient acceptance #5 evidence was too broad. The bounded discriminating fixture below supplies the missing evidence and supersedes that claim.
- No complete package/toolkit suite was run by this tester. Finalize-review is not skipped and will execute the declared package suite before accepting. Handed Build logs inspected: `/private/tmp/toolkit-round2-package-tests.txt` ends `715 passed in 53.39s`; adversarial log ends `5 passed in 0.10s`. These are Build's runs, not this tester's independent executions.

### 1. Re-tested — all three creator entrypoints and aggregation boundaries

- Command, existing interpreter:
```sh
-m pytest skill-dev-toolkit/tests/test_creator_commands.py skill-dev-toolkit/tests/test_preference_export.py skill-dev-toolkit/tests/test_creator_metadata_contract.py skill-dev-toolkit/tests/test_refactor_policy.py skill-dev-toolkit/tests/test_tuning_policy.py skill-dev-toolkit/skills/skill-refactor/scripts/test_package_mode_contract.py skill-dev-toolkit/skills/dogfood-skill-testing/test_skill_structure.py skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py skill-dev-toolkit/skills/skill-consistency-check/scripts/test_skill_text.py scripts/test_preferences_single_choice.py -q
```
- Output: `81 passed in 2.15s`, exit 0.
- Packaging archive inclusion/exclusion and invalid-input no-output branches reran. Offline optimizer bounded progress/heldout separation/backend-failure branches reran.
- Actual aggregation CLI tested BOTH without_skill and old_skill baselines: current rate .75, baseline .25 -> delta +.50; Markdown current-first columns; grading duration mean 3 retained despite different sibling duration; captured tokens 10/20 -> mean15 independently of duration and output_chars; zero/missing captured tokens remain0 rather than treating characters as tokens.
- Observed uniform populations2 -> metadata2/Markdown2, two-eval uniform2 ->2; unequal population ->null/qualified Markdown, including zero missing-eval/configuration cells; no grading runs ->0/Markdown0.
- Evidence: expanded `test_creator_commands_valid` parameterizations and `test_creator_commands_invalid`.
- Boundaries unchanged: optimizer uses offline stubs, no provider or triggering-quality inference.

### 2. Carried over — ordered equivalence surfaces unchanged

- Same result as initial section2. Checked whole `8b174cd17..834668cce`: `equivalence_check.py`, `equivalence-check-protocol.md` and order tests unchanged. New aggregator, preference export and prose consumers do not feed structural traces.
- No rerun result fabricated; initial 14 deterministic trace fixtures remain the backing evidence.

### 3. Carried over — blind display and lock-in surfaces unchanged

- Same result as initial section3. Whole-range comparison showed no changes to `ab_harness.py`, blind harness protocol or blind CLI tests.
- New shared export validation consumes already-recorded picks; it does not change printed paths, label assignment, full-output copies or pick parsing. Initial ten CLI rounds remain backing evidence.

### 4. Re-tested — all preference consumers, compatibility and counts

- Focused command above reran explicit candidate/baseline exports and inactive trainer, all unusable cases, readiness population and graduated regression.
- New contradictory label A=baseline / recorded candidate winner is rejected; duplicate normalized picked labels and incomplete mappings missing picked label are rejected. Both exporter and trainer share eligibility and give no usable-record credit; all-unlabelled records retain compatibility.
- Consistent labelled picks with whitespace/case normalization remain usable. Labelled and identity-only usable-record readiness still counts records, not1002 derived pairs; source bytes unchanged; trainer still inactive.
- Independent CLI replay for BOTH valid labelled choices:
```text
labelled A baseline 1 usable 1 pair preferred base raw unchanged
labelled B candidate 1 usable 1 pair preferred candidate raw unchanged
1 passed, 3 deselected in 0.15s
```
- Command: existing interpreter `-m pytest /private/tmp/test_acceptance_repair_rerun.py -q -s -k labelled`.
- This also tests the valid labelled baseline branch directly, rather than inferring it from candidate-only fixtures.

### 5. Re-tested — eight policy surfaces and discriminating audit fixture

- Creator/judge description authority and word budget, case-metadata ownership, refactor dependency/extraction, ensemble voting/ablation, human agreement/multi-pick and dogfood evidence ownership all reran via focused files above.
- Re-read ensemble reference, NOTICE and three README Tier2 rows: only FLAG_TIER_2 escalates. Actual E,E,U CLI -> PASS_MODERATE exit0; E,E,N ->FLAG_TIER_2 exit2; concrete warning loss overrides low-equivalence count ->FLAG_TIER_2; vague E,N,U ->FAIL exit1.
- Translated extraction examples now all REJECT a12.4% entry-only relocation without whole-package savings. Fresh real-package export/account replay: target words2894->2488(-406), package words22879->22879(0), package bytes189020->189020(0), valid accounting PASS but whole-package Q2 REJECT. No candidate applied.
- Actual harness parsing followed by informed policy execution: a+b DEFER/no edit; none DROP/no edit; refine REFINE/no edit; baseline single DROP/no edit; candidate single ADOPT/edit. 2/3<.70 ESCALATE;3/4>.70 majority. No product tally API invented.
- Command: existing interpreter `-m pytest /private/tmp/test_acceptance_repair_rerun.py -q -s` before labelled case was added: `3 passed in0.32s`. The separate added labelled test passed as recorded under4.
- R4 fixture execution and exact independent-context packets/results follow below. It used real repository structure output and real unchanged-source checks with intentionally omitted evidence, not a paid executor or a whole live-host dogfood run.

### 6. Carried over — planner and report evidence surfaces unchanged

- Whole-range comparison showed no changes to consistency-check planner, merger, user-facing size/coverage documentation or their tests.
- Initial boundary fixtures and real25135-token corpus results remain backing evidence. New refactor example prose cannot change group membership, nominal warning or rendering.

### 7. Re-tested — focused detection, current authorities and repository checks

- 81 focused cases passed; the independent voting/deferral/extraction cases3 passed plus valid labelled preferences1 passed. They exercise the repaired negative branches and current resolved references rather than asserting obsolete inline placement.
- `python3 scripts/check-skill-structure.py skill-dev-toolkit`: all6PASS.
- `python3 scripts/check-shared-conventions-drift.py`:3 conventions,0 drift failures,0 read errors.
- `python3 scripts/sync_codex_manifests.py --check skill-dev-toolkit`: exit0.
- Workflow and graduated test route unchanged; graduated5-case program passed in the focused run. Parent's Build package715 result inspected separately; acceptance does not relabel it as its own suite run.
- Finalizer still must run `python3 -m pytest scripts/ -q`; failures block acceptance. No steps skipped, no host installation or activation claim.

### R4 declared contract and executed informed workflow

The intentionally failing and positive-control fixture uses an ordered procedure and genuine repository validator output. Its scripted executor writes fixture artifacts only outside the source tree.

Declared procedure (informed-only):
```json
[
  "1. Enumerate all toolkit skill directories containing SKILL.md.",
  "2. Run the repository structure validator on the toolkit and require success.",
  "3. Before reporting, run git diff --exit-code and require unchanged tracked source.",
  "4. Write the report with title, observed skill count, and mandatory scope limitation."
]
```

Exact executed transcript A (informed-only):
```json
[
  {
    "step": 1,
    "operation": "glob skill-dev-toolkit/skills/*/SKILL.md",
    "result": [
      "dogfood-skill-testing",
      "skill-consistency-check",
      "skill-creator-advance",
      "skill-judge",
      "skill-refactor",
      "skill-tuning"
    ]
  },
  {
    "step": 2,
    "command": [
      "python3",
      "scripts/check-skill-structure.py",
      "skill-dev-toolkit"
    ],
    "exit": 0,
    "output": "check-skill-structure: scanned 6 skills under /private/tmp/monkey-skills-acceptance-834668cce/skill-dev-toolkit/skills\nPASS  dogfood-skill-testing\nPASS  skill-consistency-check\nPASS  skill-creator-advance\nPASS  skill-judge\nPASS  skill-refactor\nPASS  skill-tuning\n\nAll 6 skills PASS\n"
  },
  {
    "step": 4,
    "operation": "write report",
    "artifact": "artifact-A.md"
  }
]
```

Exact executed transcript B (informed-only):
```json
[
  {
    "step": 1,
    "operation": "glob skill-dev-toolkit/skills/*/SKILL.md",
    "result": [
      "dogfood-skill-testing",
      "skill-consistency-check",
      "skill-creator-advance",
      "skill-judge",
      "skill-refactor",
      "skill-tuning"
    ]
  },
  {
    "step": 2,
    "command": [
      "python3",
      "scripts/check-skill-structure.py",
      "skill-dev-toolkit"
    ],
    "exit": 0,
    "output": "check-skill-structure: scanned 6 skills under /private/tmp/monkey-skills-acceptance-834668cce/skill-dev-toolkit/skills\nPASS  dogfood-skill-testing\nPASS  skill-consistency-check\nPASS  skill-creator-advance\nPASS  skill-judge\nPASS  skill-refactor\nPASS  skill-tuning\n\nAll 6 skills PASS\n"
  },
  {
    "step": 3,
    "command": [
      "git",
      "diff",
      "--exit-code"
    ],
    "exit": 0,
    "output": ""
  },
  {
    "step": 4,
    "operation": "write report",
    "artifact": "artifact-B.md"
  }
]
```

Command: `python3 /private/tmp/acceptance_r4_fixture.py`, exit0.
```text
informed {"artifact": "A", "verdict": "FAIL", "missing_declared_steps": [3]}
informed {"artifact": "B", "verdict": "PASS", "missing_declared_steps": []}
```
Informed finding: transcript A jumps from required step2 to reporting step4, skipping step3 `git diff --exit-code`. B runs step3 with exit0 and no output, satisfying the required unchanged-tracked-source gate. This is distinct from the artifact criterion and was not sent to either auditor.

### Exact blind packets and returned judgments

Before EACH native auditor dispatch, ran packaged `dispatch_profile.py` locally with:
```json
{"event":"initial","main_profile":{"model":null,"effort":null},"task_evidence":{"trust_boundary":true},"capabilities":{},"inheritance_guaranteed":true,"completed_redispatches":0}
```
Both resolver outputs:
```json
{"completed_redispatches":0,"effective_profile":"inherited","outcome":"dispatch","overrides":null,"reason":"unobservable-main-profile","requested_profile":null,"task_class":"complex","uncertainty":null}
```
Both calls used `fork_turns:"none"`, omitted model/effort overrides, no external provider tools. Exact payload for EACH of the two isolated calls:
```text
Judge the artifacts ONLY against the supplied rubric. You have no context about how they were produced; no tools, external services or inference about producer steps. Return coarse PASS/FAIL/UNVERIFIED per artifact and cite the specific missing criterion. RUBRIC: Report requires title Toolkit structure check; the observed count is six skills; report all six passed; explicitly state that structural validation does not prove live host activation. Judge only these artifact requirements, not producer steps. ARTIFACT A:
# Toolkit structure check

Six skills checked; all six passed.

ARTIFACT B:
# Toolkit structure check

Six skills checked; all six passed.

Structural validation does not prove live host activation.
```

Run1 exact response:
> Artifact A: FAIL — Missing the explicit statement that structural validation does not prove live host activation.
> Artifact B: PASS — Includes the required title, count of six skills, all six passing, and the required limitation.

Run2 exact response:
> Artifact A: FAIL — Missing the required statement that structural validation does not prove live host activation.
> Artifact B: PASS — Meets all four artifact requirements.

Observed separation: both blind auditors catch the omitted required limitation, with no procedure/transcript present in either packet. The informed tester separately catches the skipped source-integrity gate from the ordered procedure/transcript. Positive control B passes both checks. Exact model/version pin remains UNVERIFIED; two native inherited-context samples do not establish provider activation, full skill routing, or full live-host workflow fidelity.

### R4 replay source

```python
"""Execute two bounded fixture workflows; keep blind and informed packets separate."""
import json
from pathlib import Path
import subprocess

ROOT=Path('/private/tmp/monkey-skills-acceptance-834668cce')
OUT=Path('/private/tmp/acceptance-r4-rerun')
OUT.mkdir(exist_ok=True)
PROCEDURE=[
    '1. Enumerate all toolkit skill directories containing SKILL.md.',
    '2. Run the repository structure validator on the toolkit and require success.',
    '3. Before reporting, run git diff --exit-code and require unchanged tracked source.',
    '4. Write the report with title, observed skill count, and mandatory scope limitation.',
]
RUBRIC=('Report requires title Toolkit structure check; the observed count is six skills; '
        'report all six passed; explicitly state that structural validation does not prove '
        'live host activation. Judge only these artifact requirements, not producer steps.')
for name,skip in [('A',True),('B',False)]:
    transcript=[]
    found=sorted(p.parent.name for p in (ROOT/'skill-dev-toolkit/skills').glob('*/SKILL.md'))
    transcript.append({'step':1,'operation':'glob skill-dev-toolkit/skills/*/SKILL.md','result':found})
    cmd=['python3','scripts/check-skill-structure.py','skill-dev-toolkit']
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0
    transcript.append({'step':2,'command':cmd,'exit':p.returncode,'output':p.stdout})
    if not skip:
        p=subprocess.run(['git','diff','--exit-code'],cwd=ROOT,capture_output=True,text=True)
        assert p.returncode==0
        transcript.append({'step':3,'command':['git','diff','--exit-code'],'exit':0,'output':p.stdout})
    artifact='# Toolkit structure check\n\nSix skills checked; all six passed.\n'
    if not skip:
        artifact+='\nStructural validation does not prove live host activation.\n'
    (OUT/f'artifact-{name}.md').write_text(artifact)
    transcript.append({'step':4,'operation':'write report','artifact':f'artifact-{name}.md'})
    (OUT/f'transcript-{name}.json').write_text(json.dumps(transcript,indent=2))
    missing=[step for step in range(1,5) if step not in [r['step'] for r in transcript]]
    result={'artifact':name,'verdict':'FAIL' if missing else 'PASS','missing_declared_steps':missing}
    print('informed',json.dumps(result))
    assert missing==([3] if skip else [])
    print('artifact',name,repr(artifact))
(OUT/'procedure.json').write_text(json.dumps(PROCEDURE,indent=2))
(OUT/'rubric.txt').write_text(RUBRIC)
print('rubric',RUBRIC)

```

### Independent local re-run replay source

```python
"""Independent offline acceptance probes, not a live-provider dogfood run."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('/private/tmp/monkey-skills-acceptance-834668cce')
PY = sys.executable
OUT = Path('/private/tmp/acceptance-repair-rerun-fixtures')
OUT.mkdir(exist_ok=True)

def test_labelled_preferences_both_choices_expected():
    """Consistent labelled baseline and candidate picks export their actual winner."""
    scripts=ROOT/'skill-dev-toolkit/skills/skill-tuning/scripts'
    for choice,identity,verdict in [('A','baseline','DROP'),('B','candidate','ADOPT')]:
        record={'skill':'acceptance','verdict':verdict,'user_pick':choice,
                'user_pick_identity':identity,'test_prompt_hash':'prompt',
                'variants_shown':[{'label':'A','identity':'baseline','skill_md_hash':'base'},
                                  {'label':'B','identity':'candidate','skill_md_hash':'candidate'}]}
        log=OUT/f'{choice}.jsonl'
        raw=json.dumps(record)+'\n'
        log.write_text(raw)
        output=OUT/f'{choice}-pairs.json'
        p=subprocess.run([PY,str(scripts/'preference_log.py'),'export-for-training',str(log),
                          '--skill','acceptance','--out',str(output),'--min-entries','1'],
                         capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        result=json.loads(output.read_text())
        preferred='base' if identity=='baseline' else 'candidate'
        assert result['n_entries_used']==result['n_training_pairs']==1
        assert result['training_pairs'][0]['preferred_skill_md_hash']==preferred
        assert log.read_text()==raw
        print('labelled',choice,identity,'1 usable 1 pair preferred',preferred,'raw unchanged')

def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_vote_cases_real_cli_expected():
    """Read the current rule and execute its representative vote outcomes."""
    script = ROOT/'skill-dev-toolkit/skills/skill-refactor/scripts/multi_judge.py'
    for label, votes, reason, expected, code in [
        ('uncertain','EEU','same observable behavior','PASS_MODERATE',0),
        ('dissent','EEN','different emphasis','FLAG_TIER_2',2),
        ('specific','ENU','drops the warning','FLAG_TIER_2',2),
        ('weak','ENU','different emphasis','FAIL',1)]:
        names = {'E':'equivalent','U':'uncertain','N':'not_equivalent'}
        path = OUT / f'{label}.json'
        path.write_text(json.dumps({'judges':[{'verdict':names[v],'reason':reason} for v in votes]}))
        proc = subprocess.run([PY,str(script),'--ensemble',str(path)],capture_output=True,text=True)
        result=json.loads(proc.stdout)
        print(label, proc.returncode, json.dumps(result,sort_keys=True))
        assert (result['consensus'],proc.returncode)==(expected,code)

def test_human_deferral_interpretation_expected():
    """Execute the harness parser then apply the read instruction's adoption rule."""
    harness=load('acceptance_harness','skill-dev-toolkit/skills/skill-tuning/scripts/ab_harness.py')
    labels={'A':{'identity':'baseline'},'B':{'identity':'candidate'}}
    expected={'a+b':'DEFER','n':'DROP','r':'REFINE','a':'DROP','b':'ADOPT'}
    for raw,want in expected.items():
        pick=harness.parse_pick(raw,labels)
        verdict=({'multiple':'DEFER','none':'DROP','refine':'REFINE'}.get(pick['type'])
                 or ('DROP' if pick['identity']=='baseline' else 'ADOPT'))
        print('human pick',raw,pick,'=>',verdict,'edit=',verdict=='ADOPT')
        assert verdict==want
    # Policy has no executable human tally reducer: execute this interpretation
    # explicitly and disclose that boundary rather than inventing a product API.
    for winners,total,expected in [(2,3,'ESCALATE'),(3,4,'majority')]:
        result='majority' if winners/total>=.70 else 'ESCALATE'
        print('agreement',winners,total,winners/total,result)
        assert result==expected

def test_extraction_accounting_real_package_expected():
    """Actually relocate repository prose and account immutable original bytes."""
    gate=load('acceptance_package_gate','skill-dev-toolkit/skills/skill-refactor/scripts/package_gate.py')
    workspace=OUT/'extraction'
    manifest=gate.export_baseline(ROOT,workspace,'skill-dev-toolkit/skills/skill-creator-advance','HEAD')
    digest=hashlib.sha256(manifest.read_bytes()).hexdigest()
    candidate=workspace/'candidate'
    shutil.copytree(manifest.parent/'skill',candidate)
    target=candidate/'SKILL.md'
    before=target.read_text()
    start=before.index('\n## ')
    end=before.index('\n## ',start+1)
    moved=before[start:end]
    target.write_text(before[:start]+before[end:])
    (candidate/'references/acceptance-extracted.md').write_text(moved)
    result=gate.account_package(manifest,digest,candidate,'SKILL.md')
    print('extraction',json.dumps(result,sort_keys=True))
    assert result['verdict']=='PASS'
    assert result['target']['words']['delta']<0
    assert result['package']['words']['delta']==0
    reduction=1-result['package']['words']['candidate']/result['package']['words']['baseline']
    print('whole-package reduction',reduction,'overall Q2 REJECT')
    assert reduction<.05

```

