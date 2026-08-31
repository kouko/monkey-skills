# Plan: docs review baseline

**Source brief**: docs/loom/specs/2026-08-31-docs-review-baseline.md
Goal: 交付第一個可重算的 historical replay baseline，用弱模型分辨文件初稿、修復與 review 各自造成的成本 — serves map docs-review-efficiency: 建立後續改善的可比較起點
Stage: execution — store-records aggregate re-review
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
- **Brief item covered**: REQ-99
- **Review disposition**: batch(store-records)
- **Status**: implemented(33bedfbdac68351f9e284f62196efe7d2f71dc1b)
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
- **Brief item covered**: REQ-100
- **Review disposition**: batch(store-records)
- **Status**: implemented(9dc0cdcdbd8551e0e4ef378ddaca176f0e2bda2f)
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
- **Brief item covered**: REQ-101
- **Review disposition**: batch(store-records)
- **Status**: implemented(01e57790f383eec56ccf0a30ceacc6f416d9136c)
- **Gloss**: 每次弱模型重跑都面對同一份不會漂移的考卷。

## Task 5 — 綁定弱模型 execution profile

- **Description**: Resolve and record economy host, exact model, effort, contract, runtime, and configuration identities; refuse stronger or unknown scored bindings.
- **Module**: `loom-code/scripts/docs_review_baseline_runner.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_runner.py`, `loom-code/scripts/test_docs_review_baseline_runner.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/skills/using-loom-code/references/dispatch-profile.md`
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/scripts/loom_firing_harness.py`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_runner.py::test_req_102_scored_replay_uses_explicit_weak_bindings` fails for economy, unknown, and stronger mappings.
  - **GREEN**: Current haiku and gpt-5.6-luna economy bindings score only with exact identities; stronger and unknown mappings remain unscoreable.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: immutable binding record; owner: Task 1; probe: `test_docs_review_baseline_runner.py::test_req_102_scored_replay_uses_explicit_weak_bindings`
- **Independent**: false
- **Brief item covered**: REQ-102
- **Review disposition**: batch(runner-boundaries)
- **Status**: pending
- **Gloss**: 實驗只比較真正可確認的弱模型，不讓強模型偷混進來。

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
- **Brief item covered**: REQ-103
- **Review disposition**: batch(store-records)
- **Status**: implemented(6a654d644297b7708dc4395104b66adc737c577b)
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
- **Brief item covered**: REQ-104
- **Review disposition**: batch(store-records)
- **Status**: implemented(d87da21d13948d450bdd46f21764da1d48f7c708)
- **Gloss**: 模型說了什麼與人最後判定什麼分開，才能看出 false alarm。

## Task 8 — 建立可比較 repeat cohorts

- **Description**: Admit at least two runs only when corpus, contract, runtime, configuration, host, model, tier, and effort identities are identical.
- **Module**: `loom-code/scripts/docs_review_baseline_runner.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_runner.py`, `loom-code/scripts/test_docs_review_baseline_runner.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_runner.py::test_req_105_repeat_cohorts_never_mix_execution_identities` fails for identical and cross-host runs.
  - **GREEN**: Same-identity repeats form a cohort; Claude and Codex or drifted identities never pool.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: identity-bound run records; owner: Task 1; probe: `test_docs_review_baseline_runner.py::test_req_105_repeat_cohorts_never_mix_execution_identities`
- **Independent**: false
- **Brief item covered**: REQ-105
- **Review disposition**: batch(runner-boundaries)
- **Status**: pending
- **Gloss**: 只有同模型、同設定的重跑才能回答 reviewer 穩不穩。

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
- **Brief item covered**: REQ-106
- **Review disposition**: batch(metric-reporting)
- **Status**: pending
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
- **Brief item covered**: REQ-107
- **Review disposition**: batch(metric-reporting)
- **Status**: pending
- **Gloss**: 實驗的失敗與不確定會出現在報告，不被分母洗掉。

## Task 11 — 凍結 baseline report lineage

- **Description**: Freeze reports against exact corpus, oracle, attribution, contract, runtime, parser, execution-profile, and metric-definition revisions.
- **Module**: `loom-code/scripts/docs_review_baseline_metrics.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_metrics.py`, `loom-code/scripts/test_docs_review_baseline_metrics.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/specs/docs-review-baseline/spec.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_metrics.py::test_req_108_frozen_reports_do_not_rewrite_history` fails for partial telemetry and later oracle correction.
  - **GREEN**: Partial reports freeze with limitations; later corrections produce new lineage without changing baseline bytes.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: canonical frozen report publisher; owner: Task 1; probe: `test_docs_review_baseline_metrics.py::test_req_108_frozen_reports_do_not_rewrite_history`
- **Independent**: false
- **Brief item covered**: REQ-108
- **Review disposition**: batch(metric-reporting)
- **Status**: pending
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
- **Brief item covered**: REQ-109
- **Review disposition**: batch(store-records)
- **Status**: implemented(01c1020981243c4b6a963e1cb9d7b00c1b278f54)
- **Gloss**: 初稿問題與修復後新增問題會由 diff 證據分開，不靠印象。

## Task 13 — 凍結 reviewer contract 與 runtime

- **Description**: Version reviewer instructions independently from skill, package, and runtime implementation; separate cohorts whenever either digest changes.
- **Module**: `loom-code/scripts/docs_review_baseline_runner.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_runner.py`, `loom-code/scripts/test_docs_review_baseline_runner.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/skills/requesting-docs-review/SKILL.md`
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/agents/docs-reviewer.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_runner.py::test_req_110_contract_and_runtime_are_independent_inputs` fails for same-contract runtime drift.
  - **GREEN**: Contract and runtime retain separate immutable lineage; either digest change splits repeatability cohorts.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: immutable contract and runtime revision records; owner: Task 1; probe: `test_docs_review_baseline_runner.py::test_req_110_contract_and_runtime_are_independent_inputs`
- **Independent**: false
- **Brief item covered**: REQ-110
- **Review disposition**: batch(runner-boundaries)
- **Status**: pending
- **Gloss**: prompt 變了還是 skill package 變了會被分開，不會被算成隨機性。

## Task 14 — 隔離 untrusted replay content

- **Description**: Enforce per-snapshot classification and deny artifact instructions, secrets, external files, tools, connectors, and network outside the approved boundary.
- **Module**: `loom-code/scripts/docs_review_baseline_runner.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_runner.py`, `loom-code/scripts/test_docs_review_baseline_runner.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/agents/docs-reviewer.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_runner.py::test_req_111_replay_content_is_untrusted_and_data_bound` fails for prompt injection, unclassified, and sensitive snapshots.
  - **GREEN**: Artifact instructions never gain authority; unapproved data or capabilities block transmission without leaking sensitive values.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: classification and audit records; owner: Task 1; probe: `test_docs_review_baseline_runner.py::test_req_111_replay_content_is_untrusted_and_data_bound`
- **Independent**: false
- **Brief item covered**: REQ-111
- **Review disposition**: batch(runner-boundaries)
- **Status**: pending
- **Gloss**: 歷史文件裡的指令只是待審內容，不能操作電腦或外送資料。

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
- **Brief item covered**: REQ-112
- **Review disposition**: batch(store-records)
- **Status**: implemented(a80a9e99292fb4cc5ea81ce6e6d878d5eb9b6b25)
- **Gloss**: 寫文件、寫答案與裁決的人是誰會被記錄，避免自己給自己過關。

## Task 16 — 限制 run 與 campaign 成本

- **Description**: Enforce finite run, retry, concurrency, wall-time, input, output, and usage limits with deterministic whole-artifact fit checks.
- **Module**: `loom-code/scripts/docs_review_baseline_runner.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_runner.py`, `loom-code/scripts/test_docs_review_baseline_runner.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/scripts/loom_firing_harness.py`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_runner.py::test_req_113_campaign_resource_use_is_bounded` fails for exhausted budgets and context overflow.
  - **GREEN**: Exhausted limits refuse work; unsupported whole artifacts never truncate silently or become scored partial results.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: policy-bound attempt identity; owner: Task 1; probe: `test_docs_review_baseline_runner.py::test_req_113_campaign_resource_use_is_bounded`
- **Independent**: false
- **Brief item covered**: REQ-113
- **Review disposition**: batch(runner-boundaries)
- **Status**: pending
- **Gloss**: 重跑不會因超時、無限 retry 或過長文件變成無底洞。

## Task 17 — 保證 crash-safe dispatch 與 capture

- **Description**: Implement single-owner dispatch, fencing takeover, acknowledgement uncertainty, partial and late bytes, cancellation uncertainty, and atomic capture.
- **Module**: `loom-code/scripts/docs_review_baseline_runner.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_runner.py`, `loom-code/scripts/test_docs_review_baseline_runner.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/docs/loom/2026-08-31-docs-review-baseline/proposal.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_runner.py::test_req_114_dispatch_and_capture_are_crash_safe` fails for concurrent, partial, late, cancelled, and revived-owner attempts.
  - **GREEN**: One fenced owner dispatches; uncertain and late outcomes preserve bytes and never overwrite or enter scoring implicitly.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: atomic attempt and raw-output publisher; owner: Task 1; probe: `test_docs_review_baseline_runner.py::test_req_114_dispatch_and_capture_are_crash_safe`
- **Independent**: false
- **Brief item covered**: REQ-114
- **Review disposition**: batch(runner-boundaries)
- **Status**: pending
- **Gloss**: 當 host 斷線或回應晚到，每筆成本與輸出仍有正確落點。

## Task 18 — 在 dispatch 與 capture 驗證實際 model identity

- **Description**: Compare prepared economy identity with dispatch-time and host-reported execution identity; preserve mismatches and unknown attestations as unscoreable.
- **Module**: `loom-code/scripts/docs_review_baseline_runner.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline_runner.py`, `loom-code/scripts/test_docs_review_baseline_runner.py`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/skills/using-loom-code/references/dispatch-profile.md`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline_runner.py::test_req_115_execution_identity_is_verified_at_point_of_use` fails for drift and unattested execution.
  - **GREEN**: Drifted or unattested attempts retain evidence but never enter scored cohorts or silently update their bindings.
- **Dependencies**: Task 1 completes first
- **Seam**:
  - from Task 1: payload: immutable prepared and captured identities; owner: Task 1; probe: `test_docs_review_baseline_runner.py::test_req_115_execution_identity_is_verified_at_point_of_use`
- **Independent**: false
- **Brief item covered**: REQ-115
- **Review disposition**: batch(runner-boundaries)
- **Status**: pending
- **Gloss**: 記錄的弱模型必須和真正跑的一樣，否則只保留不計分。

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
- **Brief item covered**: REQ-116
- **Review disposition**: batch(metric-reporting)
- **Status**: pending
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
- **Brief item covered**: REQ-117
- **Review disposition**: batch(metric-reporting)
- **Status**: pending
- **Gloss**: 報告開始計算後不會途中吸入新裁決，造成分子分母不同時點。

## Task 21 — 接成可執行 historical replay

- **Description**: Add a thin stdlib CLI that validates a campaign directory, dispatches configured weak-host commands, captures attempts, and emits a frozen JSON and Markdown report.
- **Module**: `loom-code/scripts/docs_review_baseline.py`
- **Files touched**: `loom-code/scripts/docs_review_baseline.py`, `loom-code/scripts/test_docs_review_baseline.py`, `claude/.claude/CLAUDE.md`, `AGENTS.md`, `docs/loom/INDEX.md`, `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/scripts/docs_review_baseline_store.py`
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/scripts/docs_review_baseline_runner.py`
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/loom-code/scripts/docs_review_baseline_metrics.py`
  - `/Users/kouko/GitHub/monkey-skills/.worktrees/codex-docs-review-baseline/scripts/sync-agent-instructions.sh`
- **Acceptance**:
  - **RED**: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared` fails before CLI wiring and command documentation exist.
  - **GREEN**:
    - A real historical fixture produces immutable run and report artifacts, and the documented command succeeds.
    - The report separates document-creation defects, remediation-introduced defects, reviewer misses, false alarms, and unknown origin instead of collapsing them into one rate.
    - Technical, business-analysis, and strategy case coverage and insufficiencies are explicit; a hard-case corpus is labelled non-representative of routine work.
    - Claude Code and Codex economy cohorts expose scored, invalid, and unavailable populations separately; every evidence insufficiency becomes a named Map fog handback.
- **External surfaces**: subprocess adapters invoke user-configured local Claude Code and Codex CLIs; tests use deterministic fake commands, while live execution records exact executable, model identity, exit status, elapsed time, and available usage without sending secrets to third parties beyond the user-approved hosts.
- **Dependencies**: Tasks 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 parallel
- **Seam**:
  - from Task 2: payload: admitted case; owner: Task 2; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 3: payload: ratified oracle; owner: Task 3; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 4: payload: corpus manifest; owner: Task 4; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 5: payload: weak-model binding; owner: Task 5; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 6: payload: run attempt; owner: Task 6; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 7: payload: observations and attributions; owner: Task 7; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 8: payload: repeat cohorts; owner: Task 8; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 9: payload: quality metrics; owner: Task 9; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 10: payload: invalid populations; owner: Task 10; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 11: payload: report lineage; owner: Task 11; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 12: payload: origin evidence; owner: Task 12; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 13: payload: contract and runtime revisions; owner: Task 13; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 14: payload: data boundary decision; owner: Task 14; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 15: payload: authority decision; owner: Task 15; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 16: payload: resource policy; owner: Task 16; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 17: payload: crash-safe outcome; owner: Task 17; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 18: payload: execution identity; owner: Task 18; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 19: payload: zero and partial states; owner: Task 19; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
  - from Task 20: payload: population manifest; owner: Task 20; probe: `test_docs_review_baseline.py::test_historical_fixture_runs_end_to_end_and_command_surface_is_declared`
- **Independent**: false
- **Brief item covered**: Smallest End State — one real historical case must produce an end-to-end immutable report with three-document coverage, hard-case limitations, separate weak-host populations, stage attribution, and Map-fog handback.
- **Review disposition**: individual
- **Status**: pending
- **Gloss**: 所有量測能力最後接成一個可複製指令，真正跑出基準報告。

## Review Batches

### Review Batch: store-records
- **Members**: Task 2, Task 3, Task 4, Task 6, Task 7, Task 12, Task 15
- **Verdict question**: Do the shared store primitives preserve immutable, attributable, authority-checked historical evidence across case, oracle, corpus, attempt, revision, and conflict records?
- **Review lane**: full
- **Aggregate verification**: Run the complete store test file plus the resolved package suite against the exact member commits.
- **Boundary**: capability: immutable historical-evidence records; exclusions: none; consumable: yes

### Review Batch: runner-boundaries
- **Members**: Task 5, Task 8, Task 13, Task 14, Task 16, Task 17, Task 18
- **Verdict question**: Does the runner execute only bounded, identity-verifiable weak-model cohorts while preserving every unsafe, failed, or uncertain attempt outside scoring?
- **Review lane**: full
- **Aggregate verification**: Run the complete runner test file plus the resolved package suite against the exact member commits.
- **Boundary**: capability: bounded weak-model execution; exclusions: none; consumable: yes

### Review Batch: metric-reporting
- **Members**: Task 9, Task 10, Task 11, Task 19, Task 20
- **Verdict question**: Do metrics and reports expose exact populations, invalid and partial states, false alarms, lineage, and frozen inputs without rewriting history?
- **Review lane**: full
- **Aggregate verification**: Run the complete metrics test file plus the resolved package suite against the exact member commits.
- **Boundary**: capability: attributable baseline metrics and reports; exclusions: none; consumable: yes

## Notes

- Kickoff decision: tracked-byte fingerprint re-pin → after each Task's final `loom-code/` edit, recompute the `loom-code candidate SHA-256` with `scripts/test_stage_specific_complexity_behavior_evidence.py::_tracked_worktree_fingerprint` and update `docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md` in the same commit; source: `docs/loom/memory/tracked-byte-pin-tests-repin-in-the-same-commit-as-the-bytes.md` phrase `re-pin belongs in the wave's final content commit`.
- Tasks 2–20 remain sequential for implementation because they share one of three module/test-file pairs, but their atomic commits park at `implemented(<sha>)` until the corresponding module-level review Batch is complete.
- Task 1 and Task 21 remain individual checkpoints: the first establishes the shared storage seam, while the last crosses all three modules plus external command boundaries.
- User-approved drop: `2026-08-31-docs-review-baseline / REQ-118 / Scenario: a future check reduces visible findings by masking evidence` is deferred by the ratified spec and the user's 2026-08-31 `OK`; this baseline plan must measure a repeatable defect class before selecting or implementing that follow-on check.
