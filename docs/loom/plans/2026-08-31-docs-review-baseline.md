# Plan: docs review baseline

**Source brief**: docs/loom/specs/2026-08-31-docs-review-baseline.md
Goal: 交付第一個可重算的 historical replay baseline，用弱模型分辨文件初稿、修復與 review 各自造成的成本 — serves map docs-review-efficiency: 建立後續改善的可比較起點
Stage: 使用者核准 pivot：停止 production-grade runner 加固，完成 metrics 與受控 Luna replay
Steps:
  1. 建立不可改寫的實驗記錄與弱模型邊界
  2. 完成單一責任的行為與指標驗證
  3. 接成可重播的端到端實驗、公開指令並跑完 package gate
**Total tasks**: 21
**Critical-path depth**: 3 (≤5)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PENDING (review-batch derivation after user cost challenge)

## Task-flow diagram

```mermaid
flowchart LR
    T1[1 基礎記錄] --> L2[2–20 規格行為]
    L2 --> T21[21 端到端 replay、指令面與 package gate]
```

## Open Questions

N/A — no unresolved question: 實驗政策中必須由人裁定的值會作為輸入，不是 implementation fork。

## Complexity assessment

- Added complexity: three stdlib modules, one thin CLI, immutable JSON records, and explicit weak-host execution adapters.
- Why it is worthwhile: without durable inputs, attempts, attributions, and denominators, the experiment cannot distinguish upstream defects from reviewer variance.
- Removed or avoided complexity: no `loom-docs` plugin, database, web service, UI, pricing conversion, automatic prompt tuning, or generalized RBAC platform.
- Downstream risk: provider identity and usage telemetry may be unavailable; the runner must fail closed for scoring while preserving attempted-run evidence.

## Controlled-experiment pivot

The user-approved 2026-09-01 pivot removes production-runner work from this plan. Historical runner commits remain in Git history, but Tasks 5, 8, 13, 14, 16, 17, and 18 and the runner-boundaries Batch are no longer part of the delivery graph. The retained scope is the immutable record and metric core plus one fixed Luna experiment; no generalized CLI, resource database, lease, takeover, or crash-recovery service ships.

## Task 1 — 建立 immutable record 核心

- **Description**: Add canonical JSON serialization, SHA-256 identity, atomic publish, and append-only revision primitives for baseline records.
- **Module**: `loom-code/scripts/docs_review_baseline_store.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_store.py`, `loom-code/scripts/test_docs_review_baseline_store.py`, `loom-code/scripts/test_gate_scripts_fail_loud_on_unreadable_input.py`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/proposal.md`
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/scripts/review_context.py`
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/scripts/test_gate_scripts_fail_loud_on_unreadable_input.py`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_store.py::test_canonical_record_publish_is_atomic_and_content_addressed` fails before the module exists.
  - **GREEN**: The test proves deterministic digests, atomic single-winner publication, idempotent same-digest retry, and refusal of conflicting bytes.
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: none — shared implementation foundation required by every active record-oriented requirement.
- **Review disposition**: individual
- **Status**: done(892c118c3cfd8975bf9e0a18013d3e8e6480cdb3)
- **Gloss**: 每個結果都能重算且不會被後來修改偷偷改寫。

## Task 2 — 驗證 historical case 可重播性

- **Description**: Implement historical case admission with immutable bytes, source and evidence locators, digest verification, and explicit unscoreable reasons.
- **Module**: `loom-code/scripts/docs_review_baseline_store.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_store.py`, `loom-code/scripts/test_docs_review_baseline_store.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_store.py::test_req_99_historical_case_admission` fails for recoverable and narrative-only cases.
  - **GREEN**: Recoverable bytes become digest-bound candidates; narrative-only incidents remain unscoreable with named missing evidence.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: canonical record publisher; owner: Task 1; probe: `test_docs_review_baseline_store.py::test_req_99_historical_case_admission`
- **Independent**: false
- **Brief item covered**: REQ-119
- **Review disposition**: batch(store-records)
- **Status**: done(38d5ef5710a0289265493bc45440f1de5d61cd94)
- **Gloss**: 只有真的找得回當時文件的案例，才能成為考題。

## Task 3 — 凍結人工 oracle revision

- **Description**: Implement named oracle ratification, correction-child lineage, negative-control intent, and refusal of in-place frozen edits.
- **Module**: `loom-code/scripts/docs_review_baseline_store.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_store.py`, `loom-code/scripts/test_docs_review_baseline_store.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_store.py::test_req_100_oracle_ratification_is_immutable` fails on ratification and correction cases.
  - **GREEN**: Ratified oracle bytes remain unchanged; every correction is a reason-bearing child revision with a new digest.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: canonical record publisher; owner: Task 1; probe: `test_docs_review_baseline_store.py::test_req_100_oracle_ratification_is_immutable`
- **Independent**: false
- **Brief item covered**: REQ-120
- **Review disposition**: batch(store-records)
- **Status**: done(9dc0cdcdbd8551e0e4ef378ddaca176f0e2bda2f)
- **Gloss**: 人工答案先凍結，實驗後才不會因結果而改題。

## Task 4 — 凍結 corpus manifest

- **Description**: Implement non-empty corpus manifests that bind one case, snapshot digest, and ratified oracle revision per deterministic entry.
- **Module**: `loom-code/scripts/docs_review_baseline_store.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_store.py`, `loom-code/scripts/test_docs_review_baseline_store.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_store.py::test_req_101_corpus_manifest_binds_one_exact_exam` fails on valid, duplicate, empty, and digest-mismatch manifests.
  - **GREEN**: Only a deterministic non-empty manifest of matching ratified bindings freezes; floating or mismatched bindings are refused.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: canonical record publisher; owner: Task 1; probe: `test_docs_review_baseline_store.py::test_req_101_corpus_manifest_binds_one_exact_exam`
- **Independent**: false
- **Brief item covered**: REQ-121
- **Review disposition**: batch(store-records)
- **Status**: done(804922851b975077d904400891a0ddb1dae43fc4)
- **Gloss**: 每次弱模型重跑都面對同一份不會漂移的考卷。

## Task 6 — 保留每一次 dispatch attempt

- **Description**: Persist run identity before dispatch and preserve raw bytes, digest, failure, interruption, malformed output, and new-id retry semantics.
- **Module**: `loom-code/scripts/docs_review_baseline_store.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_store.py`, `loom-code/scripts/test_docs_review_baseline_store.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_store.py::test_req_103_dispatch_attempts_never_become_zero_findings` fails for usable, failed, and retried attempts.
  - **GREEN**: Every attempt remains immutable evidence; failure never synthesizes zero findings and every retry receives a new identity.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: append-only attempt record; owner: Task 1; probe: `test_docs_review_baseline_store.py::test_req_103_dispatch_attempts_never_become_zero_findings`
- **Independent**: false
- **Brief item covered**: REQ-123
- **Review disposition**: batch(store-records)
- **Status**: done(9e2b13dd4ae7867b5a6f32c5ac337c5f45e0e9c1)
- **Gloss**: 失敗與中斷也會算進成本，不會被假裝成 reviewer 沒找到問題。

## Task 7 — 分離 observation 與人工 attribution

- **Description**: Preserve reviewer observations losslessly and implement append-only human attribution revisions with unknown and disputed exclusions.
- **Module**: `loom-code/scripts/docs_review_baseline_store.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_store.py`, `loom-code/scripts/test_docs_review_baseline_store.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_store.py::test_req_104_observation_and_attribution_are_separate` fails for parsed, unmatched, unknown, and corrected findings.
  - **GREEN**: Raw observations remain unchanged while named attribution revisions carry matching, origin, dispute, and correction lineage.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: immutable observation and revision records; owner: Task 1; probe: `test_docs_review_baseline_store.py::test_req_104_observation_and_attribution_are_separate`
- **Independent**: false
- **Brief item covered**: REQ-124
- **Review disposition**: batch(store-records)
- **Status**: done(d87da21d13948d450bdd46f21764da1d48f7c708)
- **Gloss**: 模型說了什麼與人最後判定什麼分開，才能看出 false alarm。

## Task 9 — 計算帶 population 的 metrics

- **Description**: Calculate finding and false-alarm metrics as value-or-null records with numerator, denominator, formula version, availability, and exclusions.
- **Module**: `loom-code/scripts/docs_review_baseline_metrics.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_metrics.py`, `loom-code/scripts/test_docs_review_baseline_metrics.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_metrics.py::test_req_106_every_metric_carries_its_population` fails for present and missing denominators.
  - **GREEN**: Every metric exposes its arithmetic and exclusions; missing populations yield null rather than zero.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: immutable metric input records; owner: Task 1; probe: `test_docs_review_baseline_metrics.py::test_req_106_every_metric_carries_its_population`
- **Independent**: false
- **Brief item covered**: REQ-126
- **Review disposition**: batch(metric-reporting)
- **Status**: done(cf0e48f3eb428540b3e9663df5c03f733e64eeaa)
- **Gloss**: 每個百分比都會顯示它算了誰、排除了誰。

## Task 10 — 顯示 invalid 與 unknown populations

- **Description**: Report failed, interrupted, malformed, unparseable, unscoreable-model, unknown, and disputed counts without mixing incompatible usage units.
- **Module**: `loom-code/scripts/docs_review_baseline_metrics.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_metrics.py`, `loom-code/scripts/test_docs_review_baseline_metrics.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_metrics.py::test_req_107_invalid_and_unknown_populations_stay_visible` fails for malformed output and cross-host units.
  - **GREEN**: Excluded populations remain counted; invalid attempts never enter quality rates and incompatible units remain separate.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: immutable attempt and attribution populations; owner: Task 1; probe: `test_docs_review_baseline_metrics.py::test_req_107_invalid_and_unknown_populations_stay_visible`
- **Independent**: false
- **Brief item covered**: REQ-127
- **Review disposition**: batch(metric-reporting)
- **Status**: done(afc6eb419292d7cfa522c07c074b4cf26bef2702)
- **Gloss**: 實驗的失敗與不確定會出現在報告，不被分母洗掉。

## Task 11 — 凍結 baseline report lineage

- **Description**: Freeze reports against exact corpus, oracle, attribution, contract, runtime, parser, execution-profile, and metric-definition revisions.
- **Module**: `loom-code/scripts/docs_review_baseline_metrics.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_metrics.py`, `loom-code/scripts/test_docs_review_baseline_metrics.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_metrics.py::test_req_108_baseline_reports_are_revision_bound` fails for partial telemetry and later oracle correction.
  - **GREEN**: Partial reports freeze with limitations; later corrections produce new lineage without changing baseline bytes.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: canonical frozen report publisher; owner: Task 1; probe: `test_docs_review_baseline_metrics.py::test_req_108_baseline_reports_are_revision_bound`
- **Independent**: false
- **Brief item covered**: REQ-128
- **Review disposition**: batch(metric-reporting)
- **Status**: done(15321124cd32b9b66ac37c9e3561a2a86774b32c)
- **Gloss**: 日後更正人工答案時，原始 baseline 仍然可重現。

## Task 12 — 以 revision chain 支撐 defect origin

- **Description**: Represent document revisions and remediation events so origin claims require exact parent, child, diff, actor-stage, and evidence bindings.
- **Module**: `loom-code/scripts/docs_review_baseline_store.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_store.py`, `loom-code/scripts/test_docs_review_baseline_store.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/discovery/2026-08-31-docs-review-cost/research/writer-versus-reviewer-attribution.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_store.py::test_req_109_origin_requires_document_revision_evidence` fails for introduced and final-only defects.
  - **GREEN**: Inspectable before-after evidence supports fix-introduced attribution; missing lineage forces origin unknown.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: document revision records; owner: Task 1; probe: `test_docs_review_baseline_store.py::test_req_109_origin_requires_document_revision_evidence`
- **Independent**: false
- **Brief item covered**: REQ-129
- **Review disposition**: batch(store-records)
- **Status**: done(01c1020981243c4b6a963e1cb9d7b00c1b278f54)
- **Gloss**: 初稿問題與修復後新增問題會由 diff 證據分開，不靠印象。

## Task 15 — 執行 authority 與 ratifier independence

- **Description**: Validate campaign action authority, conflicts, independent ratification, denial audit events, and disputed exclusion without building generalized RBAC.
- **Module**: `loom-code/scripts/docs_review_baseline_store.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_store.py`, `loom-code/scripts/test_docs_review_baseline_store.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/proposal.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_store.py::test_req_112_authority_and_independence_are_explicit` fails for unauthorized and conflicted actors.
  - **GREEN**: Unauthorized actions leave state unchanged and audited; conflicts without an independent ratification remain disputed outside affected denominators.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: campaign policy and append-only audit events; owner: Task 1; probe: `test_docs_review_baseline_store.py::test_req_112_authority_and_independence_are_explicit`
- **Independent**: false
- **Brief item covered**: REQ-132
- **Review disposition**: batch(store-records)
- **Status**: done(9d448314087f0b273bca6a113944daf7dfdc1b9b)
- **Gloss**: 寫文件、寫答案與裁決的人是誰會被記錄，避免自己給自己過關。

## Task 19 — 分開 zero 與 partial populations

- **Description**: Model negative controls, zero expected findings, explicit no-findings, suspicious empty, extraction failure, mixed parse, partial output, and missed findings distinctly.
- **Module**: `loom-code/scripts/docs_review_baseline_metrics.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_metrics.py`, `loom-code/scripts/test_docs_review_baseline_metrics.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_metrics.py::test_req_116_zero_and_partial_populations_have_explicit_meaning` fails across negative, empty, mixed, partial, and missed cases.
  - **GREEN**: Every boundary retains a distinct state; none becomes a normal zero-percent quality metric.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: immutable observation and oracle populations; owner: Task 1; probe: `test_docs_review_baseline_metrics.py::test_req_116_zero_and_partial_populations_have_explicit_meaning`
- **Independent**: false
- **Brief item covered**: REQ-136
- **Review disposition**: batch(metric-reporting)
- **Status**: done(28cb0dec6262ed55c8c884c672c7d54e7dd7742d)
- **Gloss**: 真的沒問題、沒輸出、解析失敗與漏抓不再共用同一個零。

## Task 20 — 原子凍結 report population manifest

- **Description**: Freeze one single-winner manifest of exact runs, observations, attributions, parser, and metric definitions before report calculation.
- **Module**: `loom-code/scripts/docs_review_baseline_metrics.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_metrics.py`, `loom-code/scripts/test_docs_review_baseline_metrics.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/proposal.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_metrics.py::test_req_117_report_population_is_frozen_before_calculation` fails for concurrent calculators and later corrections.
  - **GREEN**: One complete manifest digest wins per report id; corrections or different populations require a new report lineage.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: atomic population-manifest publisher; owner: Task 1; probe: `test_docs_review_baseline_metrics.py::test_req_117_report_population_is_frozen_before_calculation`
- **Independent**: false
- **Brief item covered**: REQ-137
- **Review disposition**: batch(metric-reporting)
- **Status**: done(cd638100e35ce14636d14bff24bfcbe1eb49f80d)
- **Gloss**: 報告開始計算後不會途中吸入新裁決，造成分子分母不同時點。

## Task 21 — 發布受控 historical replay

- **Description**: Publish the fixed three-document corpus, byte-exact Luna stdin and prompt, two raw outputs, human oracle, revision attribution, population-bearing metrics, and the bounded conclusion about initial-draft versus review cost. Do not add a generalized runner.
- **Module**: `docs/loom/dogfood/2026-09-01-docs-review-luna-controlled-experiment/`
- **Files touched**: `docs/loom/dogfood/2026-09-01-docs-review-luna-controlled-experiment/README.md`, `input.txt`, `prompt.txt`, `corpus-manifest.json`, `run-1.json`, `run-2.json`, `oracle.json`, `metrics.json`
- **Acceptance**:
  - **RED**: The experiment is incomplete when any frozen input, raw output, repeat, oracle, revision evidence, metric population, or limitation cannot be inspected and recomputed.
  - **GREEN**: The committed directory preserves every named artifact, all recorded digests recompute, both run outputs parse, metric arithmetic recomputes, and the conclusion remains explicitly limited to this corpus.
  - Verify stdin identity with `shasum -a 256 docs/loom/dogfood/2026-09-01-docs-review-luna-controlled-experiment/input.txt`.
  - Verify metric JSON syntax with `python3 -m json.tool docs/loom/dogfood/2026-09-01-docs-review-luna-controlled-experiment/metrics.json`.
- **Dependencies**: Tasks 4, 9 complete first
- **Seam**:
  - from Task 4: payload: frozen corpus manifest; owner: Task 4; probe: `shasum -a 256 docs/loom/dogfood/2026-09-01-docs-review-luna-controlled-experiment/input.txt`
  - from Task 9: payload: population-bearing quality metrics; owner: Task 9; probe: `python3 -m json.tool docs/loom/dogfood/2026-09-01-docs-review-luna-controlled-experiment/metrics.json`
- **Independent**: false
- **Brief item covered**: Smallest End State — one fixed historical corpus yields a reproducible controlled Luna report that separates initial-authoring defects from reviewer sampling cost.
- **Review disposition**: individual
- **Status**: pending
- **Gloss**: 固定考卷、原始輸入輸出、人工答案與重跑成本都能獨立重算。

## Review Batches

### Review Batch: store-records
- **Members**: Task 2, Task 3, Task 4, Task 6, Task 7, Task 12, Task 15
- **Verdict question**: Do the shared store primitives preserve immutable, attributable, authority-checked historical evidence across case, oracle, corpus, attempt, revision, and conflict records?
- **Review lane**: full
- **Aggregate verification**: Run the complete store test file plus the resolved package suite against the exact member commits.
- **Boundary**: capability: immutable historical-evidence records; exclusions: none; consumable: yes


### Review Batch: metric-reporting
- **Members**: Task 9, Task 10, Task 11, Task 19, Task 20
- **Verdict question**: Do metrics and reports expose exact populations, invalid and partial states, false alarms, lineage, and frozen inputs without rewriting history?
- **Review lane**: full
- **Aggregate verification**: Run the complete metrics test file plus the resolved package suite against the exact member commits.
- **Boundary**: capability: attributable baseline metrics and reports; exclusions: none; consumable: yes

## Notes

Map part: docs-review-efficiency / Part: establish-docs-review-baseline

- observed reviewer fan-outs: N/A — no dispatch log
- adversarial audit: N/A — header=absent; base=09608cabfbaf51a6363d06673845648c78130024; changed=27; guarded-hits=0; prose-hits=0
- cold reader: N/A — base=09608cabfbaf51a6363d06673845648c78130024; changed=27; prose-hits=0
- User-approved pivot (2026-09-01): this arc is a controlled internal experiment, not a production-grade runner. Preserve the frozen corpus, Luna model argument, prompt, raw input/output evidence, repeat runs, human oracle, and revision attribution; do not continue runner-boundary hardening. Task 21 publishes the controlled experiment record and conclusion; the retired runner tasks and runner Batch are absent from the active delivery graph. `.transactions/` remains untouched.
- User-approved intervention boundary: checklist-enabled authoring starts after `2026-08-31T14:20:27Z`; the untreated baseline corpus may include only exact document snapshots and authoring/review events at or before that UTC cutoff, bounded by repository commit `82b6adf798b4d3745242669b2885c0ee92a56869`. Any first-authored or modified document after the cutoff belongs to a treated/post-intervention population. Task 21 must persist this cutoff and boundary commit in the frozen corpus/report rather than relying on session memory.
- User-approved identity evidence policy A (2026-09-01): the internal baseline may score a Codex/Luna run without backend-reported actual-model identity only through one atomic, store-local, one-time runner operation binding the approved model argument, exact CLI version and closed-tool argv, input/output digests, and subprocess result. Reports must label it requested-model CLI evidence and explicitly state that the backend did not attest the actual model. This supersedes the earlier fail-closed no-attestation wording in REQ-135; forged, replayed, drifted, or caller-supplied records remain unscoreable.
- Kickoff decision: tracked-byte fingerprint re-pin → after each Task's final `loom-code/` edit, recompute the `loom-code candidate SHA-256` with `scripts/test_stage_specific_complexity_behavior_evidence.py::_tracked_worktree_fingerprint` and update `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md` in the same commit; source: `docs/loom/memory/tracked-byte-pin-tests-repin-in-the-same-commit-as-the-bytes.md` phrase `re-pin belongs in the wave's final content commit`.
- Tasks 2–20 remain sequential for implementation because they share one of three module/test-file pairs, but their atomic commits park at `implemented(<sha>)` until the corresponding module-level review Batch is complete.
- Task 1 and Task 21 remain individual checkpoints: the first establishes the shared storage seam, while the last crosses all three modules plus external command boundaries.
- User-approved drop: `2026-08-31-docs-review-baseline / REQ-138 / Scenario: a future check reduces visible findings by masking evidence` is deferred by the ratified spec and the user's 2026-08-31 `OK`; this baseline plan must measure a repeatable defect class before selecting or implementing that follow-on check.
