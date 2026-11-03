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

## Re-run on 2026-11-03, at 29309db6

Tried on 2026-11-03, in a clean copy of the project at 29309db6.

### Setup and evidence limits

- Exact tested HEAD: `29309db69ea08e7d68790daa07b337c2aa035be8`. Fresh `git clone --no-hardlinks --no-checkout` from active repair tree into `/private/tmp/monkey-skills-acceptance-29309db6`, then detached checkout of this SHA. Initial/final clean status verified. Original user checkout never edited.
- Read latest acceptance-tester role/template from installed loom-code3.57.0, current intent/spec/plan, and `evidence/claude-followup-reassessment.md`. README clean-checkout setup rechecked; existing interpreter `/Users/kouko/.conda/envs/dbt-redshift/bin/python3` loaded the commands/tests without package installation. No plugin installation, host setting change, real model or provider call.
- Inspected fix range `343483314d22d28f3981a23733d75094834c717a..29309db6` and changed consumers. Checked `834668cce..29309db6` for all retained-row surfaces. Only metadata/report files are written back to active repair tree after testing.
- Previous evidence is historical: successful exception propagation in stubbed entry tests did not establish actual process-pool/backend behavior. Earlier missing-token=zero assertions were wrong for unavailable capture and are superseded below.
- Outside review disposition handed by parent: one Claude review ran with observed modelUsage `claude-opus-5-5`, requested high effort but effective effort unobserved. It is not this tester's execution or renewed approval. The outside fatal claim of wrong adoption across invocations was limited before this test: a new invocation displays/decodes its own map correctly, `--pick` is a testing option, and wrong supported interactive adoption was not demonstrated. The real same-round clarification gap was retained and fixed. Other handed important findings were not dismissed.
- No complete repository/toolkit suite run by this tester. Build log inspected: `/private/tmp/toolkit-wave6-package-tests.txt` ends `715 passed in56.31s`; graduated probe log ends `5 passed in0.11s`. These are handed Build results; they do not override the independent failure below. Finalizer remains required and will execute `python3 -m pytest scripts/ -q`; no skipped-by-instruction markers or skipped finalization were handed.
- New confirmed finding is important, not dismissed. Acceptance1 and7 fail on the exact tested SHA. No source/test repair was made.

### 1. Re-tested in full — creator commands; FAIL on real EOF lifecycle

Focused command using the existing interpreter:
```sh
-m pytest skill-dev-toolkit/tests/test_creator_commands.py skill-dev-toolkit/tests/test_blind_harness.py skill-dev-toolkit/tests/test_preference_export.py skill-dev-toolkit/tests/test_creator_metadata_contract.py skill-dev-toolkit/tests/test_refactor_policy.py skill-dev-toolkit/tests/test_tuning_policy.py skill-dev-toolkit/skills/skill-refactor/scripts/test_package_mode_contract.py skill-dev-toolkit/skills/dogfood-skill-testing/test_skill_structure.py skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py skill-dev-toolkit/skills/skill-consistency-check/scripts/test_skill_text.py scripts/test_preferences_single_choice.py -q
```
Output `127 passed in3.53s`, exit0.

- Actual packager valid archive/invalid input and corrected module help passed.
- Aggregation's old_skill/without_skill direction, real token metrics independent of duration, honest repetition populations and all missing/invalid token input variants passed. Independent real CLI zero/unknown/partial reproduction below also passed.
- Optimizer main/evaluator tests now exercise backend error/nonzero/incomplete/timeout/explicit-abort conditions, completed-output buffers, eligible-only selection and invalid baseline exclusion. Existing unit fixtures substitute threads and Popen streams, so independent real process-pool/Popen evidence was also required.
- Description generator prompts include the complete current authority, neutral third-person voice and contextual bands. The independent fake-executable test captures actual subprocess stdin, without patching generator functions. Normal long descriptions need existing colocated justification; ordinary domain noun router in KEEP text is not a role; declared router needs firing evidence; admitted exception max500 enforced. Raw skill bytes unchanged.
- Applying-agent semantic check executed: candidate "Use this skill for CSV." passes the mechanical checker but is imperative rather than neutral third person, so the informed pre-apply interpretation rejects it. The synthetic firing-note fixture proves mechanical admission only; the metric/corpus must be verified before actual application. No semantic-quality or firing-evidence claim is inferred from fabricated fixture notes.

Independent command:
```sh
/Users/kouko/.conda/envs/dbt-redshift/bin/python3 -m pytest /private/tmp/test_acceptance_wave6.py -q -s
```
Recorded final result: `1 failed, 5 passed in1.79s`.

The fake `claude` executable is the ONLY backend: a temporary bin directory is prepended to PATH; PYTHONPATH points to the tested creator package; cwd is a temporary directory with its own .claude. Real ProcessPoolExecutor workers and real subprocess.Popen remain intact. Nothing reaches a provider.

```text
REAL_POOL nonzero exit1 no score; no results
REAL_POOL error exit1 no score; no results
REAL_POOL incomplete exit1 no score; no results
REAL_POOL aborted_streaming exit1 no score; no results
REAL_POOL aborted_tools exit1 no score; no results
REAL_POOL success_line exit0 score1/1 saved1
EOF_FRAMING success_line exit0 summary {total:1,passed:1,failed:0}
EOF_FRAMING success exit1 RuntimeError: Query backend ended without a conclusive result
EOF_FRAMING success exit1 RuntimeError: Query backend ended without a conclusive result
EOF_FRAMING success exit1 RuntimeError: Query backend ended without a conclusive result
```

`success_line` and `success` emit the SAME successful result JSON and exit0; only the terminal newline differs. The no-newline case was independently run three times in each of two executions and consistently failed. Direct evaluator and optimizer entrypoints both encountered this condition. The five failure modes correctly never became successful negative observations, but a valid successful negative result also failed.

**Finding A8 — important (blocking)**

- Anchor: `skill-dev-toolkit/skills/skill-creator-advance/scripts/run_eval.py:117-119`.
- Issue: EOF may be observed while poll still returns None. The code raises immediately on an empty read, leaving an already accumulated successful terminal JSON without a newline unparsed. The completed-process branch's tail handling is therefore bypassed in a real subprocess lifecycle. This contradicts the claimed completed-buffer support and interrupts valid evaluations/optimization.
- Reproduction: `test_backend_eof_framing_success_expected` in replay source below; real process pool + fake local executable; positive control with newline succeeds1/1, same no-newline result fails3/3.
- Fix direction: on EOF, establish process completion/status, drain/parse buffered terminal output including a final unterminated line, then reject only genuine failure/incomplete/timeout. Preserve fail-closed error behavior and add a real-subprocess EOF positive control.
- No repair by tester. Other local test fixture error was excluded: the first fake generator incorrectly treated output-format=text as stream evaluation, producing the wrong response. Correcting that fixture's format detection made the generator probe pass; it is not a product finding.

### 2. Carried over — ordered structural equivalence unchanged

- Full `834668cce..29309db6` path check: comparator, ordered protocol and order tests unchanged. Creator backend/aggregation, golden optional comparison and tuning interaction changes do not consume/produce structural trace order.
- Retain initial14 trace fixtures: allowed one-call count tolerance and no-trace behavior; reorders/vocabulary changes rejected. No new execution claim for this row.

### 3. Re-tested in full — blind display, full inspection and same-round clarification

- All15 focused real harness CLI cases passed, covering truncated/untruncated display, five locked choice types, invalid one-shot input, clarification, empty input/EOF and identity-free pending records.
- Independent stdin sequence `m\ninvalid\na+b\n` in ONE subprocess: one TEST PROMPT display, three input prompts, one neutral viewing directory, ordinary A.md/B.md copies byte-identical to their selected source under the final map. Final multiple choice identities match that same A/B mapping.
- Copy path, randomization and lock-in are unchanged during clarification; invalid/EOF does not publish hidden identity mapping. Another invocation intentionally starts a new display/map.
- This supports repaired interactive recovery; it does not retroactively establish the outside unsupported cross-invocation wrong-adoption claim.

### 4. Re-tested in full — preference eligibility, readiness consumers and data preservation

- Re-ran all explicit candidate/baseline preference export/trainer cases, invalid record shapes, ambiguous/contradictory labels and graduated multi-choice rejection in the127-case command.
- Independent valid labelled A/baseline DROP and B/candidate ADOPT actual CLI exports each:1 usable record,1 correctly oriented pair, original bytes unchanged.
- All-unlabelled compatibility remains; any supplied label mapping must resolve picked identity uniquely. Readiness counts usable single-choice records, not derived pairs.
- Read all three tuning README readiness paragraphs/limit rows/stub captions and NOTICE against shared schema: valid baseline DROP now counts, None/multiple/refine/invalid records do not, each record counts once, pair count separate, threshold does not activate training. Runtime trainer remains explicitly unimplemented.
- Evidence: existing preference tests plus `test_labelled_preferences_both_choices_expected` in adapted prior independent replay. No user preference file used.

### 5. Re-tested in full — description, metadata, votes, extraction, human choices and audit ownership

- Eight current policy surfaces checked with actual representative executions and focused tests, not static grep alone.
- Description generation actual prompt/normal/justified-normal/router exception cases and Phase4 contextual interpretation executed as recorded under1. Grader dispatch now explicitly supplies shared case metadata path; both shared-case and no-run-local-metadata contract tests passed.
- Actual vote CLI replay: EEU ->PASS_MODERATE; EEN ->FLAG_TIER_2; concrete warning-loss dissent ->FLAG_TIER_2; low vague equivalence ->FAIL.
- Actual golden comparator positive control: candidate exactly matches anchor, similarity1.0 versus baseline0.257, returns legacy TIER_2_PASS, exit0. This is synthetic local comparison data, not a newly human-curated production anchor or an LLM judgment.
- Informed execution of current golden protocol: EEN's FLAG_TIER_2 remains HOLD for human review despite that positive result. EEU PASS_MODERATE and EEE PASS_HIGH may optionally add comparison evidence; original Q1/Q2/Q3 still apply. No auto-adoption inferred from legacy comparison label. Both shared copies match; cumulative-three-moderate safeguard remains.
- Actual whole-package extraction accounting on tested package: target words2894->2488(-406), package words23743->23743(0), package bytes197482->197482(0); measurement PASS, whole-package Q2 REJECT. No source candidate applied.
- Actual harness pick parsing + informed dispositions remain DEFER/no edit for multiple, DROP/no edit for none/baseline, REFINE/no edit, ADOPT only for locked candidate single. Human70% threshold:2/3 escalates,3/4 can form majority.
- Prior discriminating R4 omitted-output-criterion/skipped-required-gate fixture is carried as a SUBCASE with reason: whole range leaves dogfood role/rubric/trajectory instruction and template/taxonomy unchanged. Previously executed artifactA omission was caught independently twice by rubric/artifact-only fresh auditors; informed transcriptA skipped declared gate3; positiveB passed both. Golden optional-vote clarification does not modify evidence ownership. Exact packets/transcripts/results remain in preceding29309db6-predecessor section (834668cce).
- No new native auditor or outside Claude call was made in this re-run; exact model pin/full activation boundaries remain unverified.

### 6. Carried over — grouping, nominal warning and limits unchanged

- `834668cce..29309db6` leaves planner, merger, size/coverage documentation and planner/report tests unchanged. One consistency-check test-text edit only simplifies redundant CI path filters; it does not change grouping or report behavior.
- Initial exact25000/25001/28000/30000/30001 boundaries and real25135-token retained corpus remain backing evidence; no new accuracy validation claimed.

### 7. Re-tested — detection is meaningful but unresolved positive-control failure blocks acceptance

-127 criterion-focused cases passed; independent offline commands5 passed/1 failed, plus adapted policy/export/accounting4 passed in0.33s.
- `python3 scripts/check-skill-structure.py skill-dev-toolkit`: six skills allPASS; `python3 scripts/check-shared-conventions-drift.py`:3 conventions0 drift/read failures; `python3 scripts/sync_codex_manifests.py --check skill-dev-toolkit`: exit0.
- Relevant CI routing remains scripts/**, toolkit/** and workflow itself. Removed redundant child-path filters do not reduce triggers. Graduated preference regression still selected; current reference-authority tests pass.
- Existing green focused tests and handed package715 result fail to catch A8; independent real EOF positive control DOES catch it. Row7 is fails rather than calling the change fully verified. Acceptance cannot advance on a green suite alone while this real behavior fails.
- Full suite `python3 -m pytest scripts/ -q` remains finalizer's required blocking check; tester did not run it. No paid provider, installed plugin or real host activation result claimed.

### Independent Wave6 CLI replay source

Save to an external temporary file, adjust ROOT to an independent exact-SHA clone, and run with the existing interpreter. It writes only pytest's temporary fixtures, never product code; fake backend is explicitly offline. The failing EOF assertion is intentional acceptance evidence, not repaired.

```python
"""Independent bounded offline CLI probes; no real provider or host activation."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path('/private/tmp/monkey-skills-acceptance-29309db6')
CREATOR=ROOT/'skill-dev-toolkit/skills/skill-creator-advance'
PY='/Users/kouko/.conda/envs/dbt-redshift/bin/python3'

def backend(tmp_path):
    """Place a fake executable before PATH, keeping real pool and Popen intact."""
    folder=tmp_path/'bin'
    folder.mkdir()
    executable=folder/'claude'
    executable.write_text('#!'+PY+'\n'+'''import json, os, sys
mode=os.environ.get('OFFLINE_MODE','success')
if 'text' in sys.argv:
    prompt=sys.stdin.read()
    open(os.environ['PROMPT_CAPTURE'],'a').write(prompt+'\\n---CAPTURE---\\n')
    print('<new_description>'+os.environ['OFFLINE_DESCRIPTION']+'</new_description>')
    raise SystemExit(0)
if mode=='nonzero': raise SystemExit(7)
if mode=='incomplete': print(json.dumps({'type':'system'}),end=''); raise SystemExit(0)
event={'type':'result','subtype':'success','is_error':False}
if mode=='error': event.update(subtype='error_during_execution',is_error=True)
if mode.startswith('aborted_'): event['terminal_reason']=mode
print(json.dumps(event),end='\\n' if mode=='success_line' else '')
''')
    executable.chmod(0o755)
    (tmp_path/'.claude').mkdir()
    skill=tmp_path/'example'
    skill.mkdir()
    (skill/'SKILL.md').write_text('---\nname: example\ndescription: Converts CSV when JSONL output is needed.\n---\nBody\n')
    evaluation=tmp_path/'eval.json'
    evaluation.write_text(json.dumps([{'query':'negative unrelated query','should_trigger':False}]))
    env={**os.environ,'PATH':str(folder)+os.pathsep+os.environ['PATH'],
         'PYTHONPATH':str(CREATOR),'PROMPT_CAPTURE':str(tmp_path/'captured.txt')}
    return skill,evaluation,env

def test_backend_real_pool_failure_never_scores(tmp_path):
    """Real process-pool workers invoke only the local fake backend executable."""
    skill,evaluation,env=backend(tmp_path)
    for mode in ['nonzero','error','incomplete','aborted_streaming','aborted_tools','success_line']:
        env['OFFLINE_MODE']=mode
        results=tmp_path/('results-'+mode)
        args=[PY,'-m','scripts.run_loop','--eval-set',str(evaluation),'--skill-path',str(skill),
              '--num-workers','1','--runs-per-query','1','--timeout','3','--max-iterations','1',
              '--holdout','0','--model','offline','--report','none','--results-dir',str(results)]
        p=subprocess.run(args,cwd=tmp_path,env=env,capture_output=True,text=True,timeout=15)
        saved=list(results.rglob('results.json'))
        if mode=='success_line':
            assert p.returncode==0,p.stderr
            out=json.loads(p.stdout)
            assert out['best_score']=='1/1' and out['exit_reason']=='all_passed (iteration 1)'
            print('REAL_POOL',mode,'exit',p.returncode,'score',out['best_score'],'saved',len(saved))
        else:
            assert p.returncode!=0,(mode,p.stdout,p.stderr)
            assert not saved and not p.stdout and 'all_passed' not in p.stdout
            print('REAL_POOL',mode,'exit',p.returncode,'no score; no results; exception',p.stderr.strip().splitlines()[-1])
        assert not list((tmp_path/'.claude/commands').glob('*.md'))

def test_description_real_prompt_policy_expected(tmp_path):
    """Capture actual generator subprocess prompts; never apply unreviewed text."""
    skill,evaluation,env=backend(tmp_path)
    evaluation.write_text(json.dumps({'description':'old','summary':{'passed':0,'failed':1,'total':1},'results':[]}))
    cases=[('normal','Converts CSV when JSONL output is needed.','',True),
           ('normal-too-long','x'*251,'',False),
           ('domain-noun','x'*251,'# KEEP: Retains CSV and router configuration trigger surfaces\n',True),
           ('router-absent','x'*251,'# Router: CSV selection\n',False),
           ('router-evidence','x'*500,'# Firing evidence: 87% match rate from support-ticket A/B corpus\n',True),
           ('router-over','x'*501,'# Firing evidence: 87% match rate from support-ticket A/B corpus\n',False),
           ('semantic-only','Use this skill for CSV.','',True)]
    for name,description,comment,eligible in cases:
        content='---\nname: example\n'+comment+'description: Original description\n---\nBody\n'
        (skill/'SKILL.md').write_text(content)
        env['OFFLINE_DESCRIPTION']=description
        p=subprocess.run([PY,'-m','scripts.improve_description','--eval-results',str(evaluation),
                          '--skill-path',str(skill),'--model','offline'],cwd=tmp_path,env=env,
                         capture_output=True,text=True,timeout=10)
        assert (p.returncode==0)==eligible,(name,p.stderr)
        assert (skill/'SKILL.md').read_text()==content
        if eligible: assert json.loads(p.stdout)['description']==description
        print('DESCRIPTION',name,'mechanically eligible',eligible,'source unchanged')
    captured=(tmp_path/'captured.txt').read_text()
    authority=(CREATOR/'references/description-design.md').read_text()
    assert authority in captured and 'neutral third-person' in captured
    assert '100-200 words' not in captured and 'phrased in the imperative' not in captured
    # Phase4 is the applying agent's contextual review, not a promised static NLP checker.
    print('PHASE4 semantic-only: mechanical PASS but imperative voice -> REJECT; no apply')
    print('PHASE4 router-evidence: verify actual metric/corpus before admission; fixture note is not real firing evidence')
    print('PROMPT authority captured; contextual justification and voice remain informed pre-apply checks')

def test_backend_eof_framing_success_expected(tmp_path):
    """Compare successful terminal results with and without a final newline."""
    skill,evaluation,env=backend(tmp_path)
    failed=[]
    for mode in ['success_line','success','success','success']:
        env['OFFLINE_MODE']=mode
        p=subprocess.run([PY,'-m','scripts.run_eval','--eval-set',str(evaluation),
                          '--skill-path',str(skill),'--num-workers','1','--runs-per-query','1',
                          '--timeout','3'],cwd=tmp_path,env=env,capture_output=True,text=True,timeout=15)
        print('EOF_FRAMING',mode,'exit',p.returncode,'output',p.stdout.strip() or p.stderr.strip().splitlines()[-1])
        if p.returncode: failed.append(mode)
        else: assert json.loads(p.stdout)['summary']['passed']==1
    assert failed==[],failed

def test_tokens_real_cli_unknown_zero_partial(tmp_path):
    """Recompute Markdown/JSON under complete zero, missing and partial capture."""
    for config in ['with_skill','old_skill']:
        for index in [1,2]:
            path=tmp_path/f'eval-1/{config}/run-{index}'
            path.mkdir(parents=True)
            (path/'grading.json').write_text(json.dumps({'summary':{'pass_rate':1,'passed':1,'failed':0,'total':1},'timing':{'total_duration_seconds':2},'execution_metrics':{'output_chars':9999}}))
            (path/'timing.json').write_text(json.dumps({'total_tokens':10}))
    for values in [[0,0],[None,None],[0,None],[10,None]]:
        for index,value in enumerate(values,1):
            (tmp_path/f'eval-1/with_skill/run-{index}/timing.json').write_text(json.dumps({} if value is None else {'total_tokens':value}))
        p=subprocess.run([PY,'-m','scripts.aggregate_benchmark',str(tmp_path)],cwd=CREATOR,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        out=json.loads((tmp_path/'benchmark.json').read_text())
        stats=out['run_summary']['with_skill']['tokens']
        delta=out['run_summary']['delta']['tokens']
        assert stats['sample_count']==sum(v is not None for v in values) and stats['total_count']==2
        assert delta==('-10' if values==[0,0] else None)
        print('TOKENS',values,'stats',stats,'delta',delta)

def test_interactive_clarification_same_round(tmp_path):
    """One process asks again without redisplay, relabeling or replacing copies."""
    for identity in ['baseline-private','candidate-private']:
        p=tmp_path/identity/'output.md';p.parent.mkdir();p.write_text(identity+' authored content\nsecond line\n')
    viewing=tmp_path/'view';viewing.mkdir()
    session=tmp_path/'session.json'
    script=ROOT/'skill-dev-toolkit/skills/skill-tuning/scripts/ab_harness.py'
    p=subprocess.run([PY,str(script),'--variants-dir',str(tmp_path),'--prompt','Compare',
                      '--session-out',str(session),'--max-display-lines','1'],input='m\ninvalid\na+b\n',
                     capture_output=True,text=True,env={**os.environ,'TMPDIR':str(viewing)})
    assert p.returncode==0,p.stderr
    out=json.loads(session.read_text())
    assert p.stdout.count('TEST PROMPT')==1 and p.stdout.count('Your pick:')==3
    assert len(list(viewing.iterdir()))==1
    paths=re.findall(r'full output: ([^\n]+)\]',p.stdout)
    assert len(paths)==2
    for path in paths:
        f=Path(path);label=f.stem
        assert not f.is_symlink() and f.read_bytes()==(tmp_path/out['label_assignment'][label]/'output.md').read_bytes()
    assert out['pick']['identities']==[out['label_assignment'][label] for label in ['A','B']]
    print('INTERACTIVE one display; 3 prompts; same ordinary A/B copies; same mapping; final multiple pick')

def test_golden_positive_cannot_clear_dissent(tmp_path):
    """Execute actual comparison then interpret its limited authority for real vote outputs."""
    golden=tmp_path/'golden';golden.mkdir()
    anchor='Six skills checked; all six passed.'
    (golden/'one.md').write_text('---\nid: fixture\nprompt_pattern: structure\n---\n# Anchor Output\n'+anchor+'\n')
    (tmp_path/'base.md').write_text('Unrelated old text')
    (tmp_path/'candidate.md').write_text(anchor)
    script=ROOT/'skill-dev-toolkit/skills/skill-refactor/scripts'
    p=subprocess.run([PY,str(script/'golden_compare.py'),'--golden-dir',str(golden),
                      '--baseline-output',str(tmp_path/'base.md'),'--candidate-output',str(tmp_path/'candidate.md'),
                      '--prompt-pattern','structure'],capture_output=True,text=True)
    comparison=json.loads(p.stdout)
    assert p.returncode==0 and comparison['verdict']=='TIER_2_PASS'
    print('GOLDEN actual comparison',comparison)
    for votes,want in [('EEN','FLAG_TIER_2'),('EEU','PASS_MODERATE'),('EEE','PASS_HIGH')]:
        names={'E':'equivalent','N':'not_equivalent','U':'uncertain'}
        file=tmp_path/f'{votes}.json';file.write_text(json.dumps({'judges':[{'verdict':names[v],'reason':'different emphasis'} for v in votes]}))
        p=subprocess.run([PY,str(script/'multi_judge.py'),'--ensemble',str(file)],capture_output=True,text=True)
        result=json.loads(p.stdout);assert result['consensus']==want
        action='HOLD for human review' if want=='FLAG_TIER_2' else 'optional anchor supplement; existing Q1/Q2/Q3 still apply'
        print('GOLDEN',votes,want,'positive comparison =>',action)

```

### Adapted prior policy replay

The complete source is preserved in the prior re-run's independent replay section. For this execution only ROOT was changed to `/private/tmp/monkey-skills-acceptance-29309db6` and OUT to unused `/private/tmp/acceptance-wave6-policy-fixtures`; the four test bodies were unchanged. Command: existing interpreter `-m pytest /private/tmp/test_acceptance_wave6_policies.py -q -s`. Result: `4 passed in0.33s`; token/extraction counts are recorded under5 above.

## Re-run on 2026-11-03, at 65619dbd

Tried on 2026-11-03, in a clean copy of the project at 65619dbd.

### Clean setup and scope

- Exact HEAD: `65619dbd616a8fc5cd80cdca8d9a63b32914441f`. Created independent local clone `/private/tmp/monkey-skills-acceptance-65619dbd` with `git clone --no-hardlinks --no-checkout`, then detached at that exact SHA.
- Re-read current installed acceptance role/template (loom-code3.57.0) and README clean-checkout setup. Reused existing `/Users/kouko/.conda/envs/dbt-redshift/bin/python3` and available dependencies as authorized; no installs or host changes. Packager, aggregator, evaluator/optimizer CLI and focused tests loaded successfully in the clean clone. Initial/final clone status empty.
- Inspected complete `29309db69ea08e7d68790daa07b337c2aa035be8..65619dbd616a8fc5cd80cdca8d9a63b32914441f` diff. It contains prior report metadata, bounded spec/plan/reassessment updates, and only TWO product/test files: `run_eval.py` and `test_creator_commands.py`.
- Product fix waits for completion within remaining deadline on stdout EOF, checks exit status, and parses final buffered JSON including an unterminated line. Added six real-CLI regression cases control stdout close before actual exit for evaluator and optimizer, newline/no-newline success and nonzero exit.
- No new important/fatal dismissals. Previously handed external-review severity limitation remains disclosed in report. A8 was fixed, not dismissed; previous failed results and complete reproducer remain above.
- No full repository or full toolkit suite run by this tester. Package-tests/finalize-review are not skipped; acceptance cites the future blocking automated suite rather than predicting its result. Declared finalizer command: `python3 -m pytest scripts/ -q`.
- No real provider/model calls, plugin installation, live host activation, training or user-data changes. Fake executable remains clearly identified as an offline backend; real process pool and Popen transport remain intact.

### 1. Re-tested in full — all creator commands and complete EOF cases

Focused command (existing interpreter):
```sh
-m pytest skill-dev-toolkit/tests/test_creator_commands.py skill-dev-toolkit/tests/test_blind_harness.py skill-dev-toolkit/tests/test_preference_export.py skill-dev-toolkit/tests/test_creator_metadata_contract.py skill-dev-toolkit/tests/test_refactor_policy.py skill-dev-toolkit/tests/test_tuning_policy.py skill-dev-toolkit/skills/skill-refactor/scripts/test_package_mode_contract.py skill-dev-toolkit/skills/dogfood-skill-testing/test_skill_structure.py skill-dev-toolkit/.claude-plugin/test_skill_description_standard.py skill-dev-toolkit/skills/skill-consistency-check/scripts/test_skill_text.py scripts/test_preferences_single_choice.py -q
```
Recorded `133 passed in5.14s`, exit0.

- Actual packaging success archive/content inclusion, missing-input no archive and current module help passed.
- Actual aggregation current-before-old/without-skill direction, duration/token separation, zero/unknown/partial token counts and suppressed incomplete deltas, uniform/unequal/empty observed repetition counts passed.
- Optimizer valid bounded progression, heldout evidence isolation, eligible-only description selection, invalid baseline exclusion, captured authority/normal/contextual exception boundaries and failed backend/invalid-input branches passed. Semantic compliance remains the applying agent's responsibility, as previously tested and disclosed.
- New `test_creator_real_eof_completion` ran evaluator AND optimizer through real subprocess and process-pool transport with stdout deliberately closed before child exit; newline and no-newline success passed, no-newline exit7 failed without score/results.
- Re-ran the independent tester's SAME real-Popen/process-pool reproducer, changing ONLY ROOT from the failed29309db6 clone to the clean65619dbd clone. No fixture assertions or fake-output behavior changed. New local replay name `/private/tmp/test_acceptance_eof_recheck.py`; complete original source is retained in preceding Wave6 section.
- Command:
```sh
/Users/kouko/.conda/envs/dbt-redshift/bin/python3 -m pytest /private/tmp/test_acceptance_eof_recheck.py -q -s
```
Recorded `6 passed in2.22s`, exit0.

Actual trimmed output:
```text
REAL_POOL nonzero exit1 no score; no results; RuntimeError: Query backend exited with status7
REAL_POOL error exit1 no score; no results; RuntimeError: Query backend returned an unsuccessful result
REAL_POOL incomplete exit1 no score; no results; RuntimeError: Query backend ended without a conclusive result
REAL_POOL aborted_streaming exit1 no score; no results; RuntimeError: Query backend aborted before completing
REAL_POOL aborted_tools exit1 no score; no results; RuntimeError: Query backend aborted before completing
REAL_POOL success_line exit0 score1/1 saved1
EOF_FRAMING success_line exit0 summary total1 passed1 failed0
EOF_FRAMING success exit0 summary total1 passed1 failed0
EOF_FRAMING success exit0 summary total1 passed1 failed0
EOF_FRAMING success exit0 summary total1 passed1 failed0
```
All three previously failing no-newline controls now pass as legitimate negative observations. Failure modes still never become passing scores. This closes A8 on this SHA within the local offline lifecycle boundary; historical failure at29309db6 is retained.

The same independent file also reran generator actual stdin capture/normal and router qualification cases, zero/unknown/partial aggregation, interactive same-map clarification and golden comparison interpretation; all passed. These incidental unchanged checks supply additional consistency evidence but do not imply any live-model quality or activation validation.

### 2. Carried over — ordered structural trace policy unchanged

- Diff has no comparator, ordered protocol, trace schema or order-test edits. EOF repair belongs to creator's trigger evaluator, not refactor's structural trace comparator.
- Retain earlier positive/tolerance and reordered-call rejection evidence and works verdict.

### 3. Carried over — blind rendering, full-copy inspection and clarification unchanged

- Diff has no harness, protocol, source-output copy or blind-test edits. Creator evaluator EOF does not control tuning stdin or its random label map.
- Retain29309db6 full CLI coverage and independent same-round clarification evidence. Incidental replay above also passed, with one display/three prompts and same ordinary A/B copies/map.

### 4. Carried over — preference selection/export/readiness unchanged

- Diff has no eligibility, exporter, trainer, log schema or readiness consumer edits. Creator child-completion status cannot alter recorded human preference joins/counts.
- Retain valid candidate/baseline, ambiguous/contradictory label, usable-record/pair-count and unchanged-input evidence; no model training claimed.

### 5. Carried over — all eight repaired rule surfaces unchanged

- No description authority/generation/selection/application policy, grader metadata contract, ensemble/ablation/extraction/golden policy, human choice policy or dogfood evidence ownership edit.
- Creator EOF change preserves valid observations but does not modify those policy decisions or audit context boundaries. Retain actual vote/deferral/extraction/golden and discriminating R4 omitted-artifact-criterion/skipped-gate evidence with its recorded native-model limits.
- Extra generator/golden replay above passed; no new auditor or external review invoked.

### 6. Carried over — grouping, nominal size notices and limits unchanged

- No planner, report merger, group/size/coverage prose or relevant tests changed. EOF status handling in creator does not feed consistency grouping.
- Retain original boundary fixtures and25135-token corpus evidence; no new empirical accuracy claim.

### 7. Re-tested in full — executable regression coverage and existing checks

-133 focused tests passed, including prior defect negative cases, current resolved authorities, six new real EOF command cases and graduated single-choice regression.
- Independent reproducer6 passed, including the exact previously failing no-newline positive control and failed-backend cases; A8 no longer open.
- `python3 scripts/check-skill-structure.py skill-dev-toolkit`: six skills PASS.
- `python3 scripts/check-shared-conventions-drift.py`:3 conventions checked,0 drift failures,0 read errors.
- `python3 scripts/sync_codex_manifests.py --check skill-dev-toolkit`: exit0.
- Workflow/declared package routing unchanged; no obsolete inline-placement check substitutes for current authority checks. Full package execution remains finalizer's future blocking automated check; no new full-suite result claimed by acceptance.
- Result works under the role's prescribed focused-tests plus blocking-final-suite contract. Findings: none remaining from this re-run. Report's previous A8 failure remains historical, not silently replaced.

