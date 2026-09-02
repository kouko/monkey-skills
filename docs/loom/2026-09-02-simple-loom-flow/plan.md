# loom 重設計 — plan
intent: 2026-09-02-simple-loom-flow@be19b961
spec: docs/loom/2026-09-02-simple-loom-flow/spec.md@0974e7cd（review.json PASS）
kind: engineering　needs-design: yes（spec 已 PASS，本段不含 Current State Evidence）
決策：agent-decided；理由附在各 task。使用者不審 plan（concept-model §4）。

## 0. 形狀與帳本

- 硬切換：舊 plan／spec／brief／batch 原地封存不轉換；新機制一次落地在同一個 PR。
- 五個 wave＝五次 checkpoint（build 上限 5，concept-model §5）；`review: after-task` 兩處（上限 2）。
- 進度＝commit 的 `Task: <id>` trailer；沒有 Status 帳。
- 版本：loom-code 0.110.0 → **1.0.0**、loom-design 0.6.0 → **1.0.0**、loom-workflow 3.2.0 → **4.0.0**（皆 breaking）。三表面各 bump：`plugin.json`、CHANGELOG、root README 的該列（版本＋skill 數欄＋描述句都要改；歷史上第 13 次漏掉的表面）＋ `.claude-plugin/marketplace.json` 三段描述（loom-design 現寫「deterministic pipeline conductor」）。
- 基線（落地時寫進 `docs/loom/KICKOFF-DEFAULTS.md`）：`session-start-baseline: 923fb84a 5281`（merge-base `923fb84a`，命令 `bash loom-code/hooks/session-start </dev/null | wc -w`，cwd 為空 git repo，本 plan 撰寫時實測 5281）。目標 ≤ 2640。

### skill 收斂表（36 → 17，另 2 個不計數）

| plugin | 今天（數） | 落地後 | 去向 |
|---|---|---|---|
| loom-code | 14 | **5 站**：write-plan、build、review、ship、maintain | brainstorming→capture-intent（design）／write-plan 收件；writing-plans→write-plan；subagent-driven-development＋dispatching-parallel-agents＋using-git-worktrees→build（後兩者為 action）；requesting-code-review＋requesting-docs-review＋verification-before-completion＋ui-verification→review（後兩者為 action）；finishing-a-development-branch→ship；loom-memory→ship／maintain 的 memory 步驟＋`docs/loom/memory/` 慣例留在 contract package；tdd-iron-law＋systematic-debugging→`references/engineering-baseline.md`；using-loom-code 刪（無 router） |
| loom-design | 10 | **2 站＋2 工具**：capture-intent、write-spec；product-principles、design-system | user-insights＋business-value→capture-intent 的訪談段；spec-expansion＋interaction-flows→write-spec；completeness-critic＋design-critic→review 站的 spec 鏡頭（docs 5 維＋design-conformance）；using-loom-design、using-loom-pipeline 刪 |
| loom-workflow | 12 | **8 工具**：decision-map、handoff、recap-state、cot-explain、distill-sessions、git-memory、independent-advisor、critique（＋2 個不計數的獨立 skill：goal-create、dbt-model-style） | proposal-critique＋complexity-critique→critique（`mode:` 選鏡頭）；brief-before-asking 刪（判斷型岔路定義移進 contract package 的單向門 action）；goal-create、dbt-model-style 原樣保留 |

計數規則（kouko 2026-09-02 裁定，user-decided）：goal-create 與 dbt-model-style 獨立於 loom 自動流程之外，**不計入** skill 數；manifest 以 `standalone: true` 標記，`check_mechanisms.py` 的 skill 計數排除 standalone。計數＝7＋8＋2＝**17**（≤18）。W3-06 把這條計數規則寫進 concept-model §3。

### 名詞
本 plan 不承諾 ≤40（spec REQ-8 註）；W3-06 用 §3 計數規則手數一次並記進 concept-model §3，作 Open question 的基線。

## 1. Task DAG

依賴以 `after:` 標示；同 wave 內無依賴者可平行（build 站的 parallel action）。每個 task：檔案／測試／風險。「測試」欄的 pytest 全部先寫失敗再實作（engineering-baseline）。

### W0 — contract package 與決定性層（loom-code）
checkpoint：W0 結束必跑（新增檔 > 8）。

**W0-01 contract manifest 與 schema**
- 檔：`loom-code/contract/manifest.yaml`（version、stations[7]、tools[11]、actions[]、artifact schemas 的欄位表：intent／spec／plan／review.json，逐字對 concept-model §2b／2c／2d／2e；派工記錄併入 review.json 的 `dispatch[]`（`{task, role, agent_id, model, started, fresh_context}`），不另開檔——W0 wave-end 審查指出第六個檔違反 REQ-5；W0-04 的 `push.reviewer-ne-implementer` 讀它）；`loom-code/contract/templates/{intent.md,spec-minimal.md,plan.md,review.json,KICKOFF-DEFAULTS.md,PRINCIPLES-interview.md,memory-README.md,PURPOSE.md}`（既有 `loom-code/scripts/templates/` 以 `git mv` 移入；`backlog-README.md` 留到 W1-06 與 loom_init.py 一起刪（其測試家族互相牽連，W0 不拔）、`ATTACK-CATALOGUE.md` 交 W1-06 移到 evidence/；`scripts/templates/` 目錄消失，不留第二個漂移面）；`loom-code/contract/README.md`（消費者：design／workflow 只讀不寫）。
- 測：`loom-code/scripts/test_contract_manifest.py`——manifest 可解析、每個 station 帶 `owner: loom-code|loom-design`，owner 為 loom-code 的站名＝`loom-code/skills/*` 目錄集合（W1 後才綠，先標 xfail 到 W1-06）、每個 action 有一段 owner station、schema 欄位與 templates 一致。
- 風：manifest 是 §11 五類之一的可重算面，欄位一旦命名就是名詞；命名前先對 §3 計數規則過一遍。

**W0-02 loom checker：骨架與 `--list-rules`**　after: W0-01
- 檔：`loom-code/scripts/loom_checker.py`（單一入口；子命令 `intent <path>`、`intake <station> <change-id>`、`push [--hook]`、`standing`、`contract --require`、`--list-rules` 輸出 rule id 表）；`loom-code/scripts/git_exec.py` 沿用。
- 測：`test_loom_checker_cli.py`——`--list-rules` 輸出穩定排序、每條 rule 有 id＋一句描述；未知子命令 exit 2（fail-closed）。
- 風：rule id 是 mechanisms.yaml 的鍵，改名＝機制淨數波動；id 用 `intent.schema` 這種 `<area>.<name>` 形式一次定好。

**W0-03 checker 規則：intent 與收件**　after: W0-02　`review: after-task`
- 規則：`intent.schema`、`intent.product-no-identifiers`（Problem 段禁路徑／識別字／腳本檔名）、`intent.needs-design-reason`（行帶理由且 commit message 含同一行）、`intent.needs-design-recompute`（讀 KICKOFF-DEFAULTS 的介面表面 glob，`no` 而 diff 碰到→擋）、`intake.confirmed`（write-spec／write-plan 只收 `status: confirmed`）、`intake.spec-pass`（needs-design: yes 時 review.json 對 spec 的 scope 有 PASS）、`intake.confirmed-behavior`（product 時 spec 有該行）。
- 測：每條規則一組 pass／fail fixture（`test_loom_checker_intent.py`、`test_loom_checker_intake.py`），含「agent 宣稱 `no` 但 diff 碰 glob」的重算案例。
- 風：介面表面 glob 的預設值（KICKOFF-DEFAULTS 缺時）要保守——預設 `**/cli/**, **/api/**, **/commands/**, **/*.tsx, **/templates/**`，並印出用了哪組。

**W0-04 checker 規則：push 與 standing docs**　after: W0-02
- 規則（含 spec 對抗後追加：`push.probes-package-tests` 由 checker 在乾淨工作樹自行執行 command；`push.dismissed-by-reviewer`；`standing.product-principles-reject` 另重算 Non-negotiables ≥3 條；新增 `contract.requires` 供 design／workflow 站啟動時比對 manifest 版本）：`push.review-only-head`（HEAD 只動 review.json）、`push.reviewed-sha`（== HEAD^）、`push.open-findings-closed`、`push.probes-package-tests`（probes[] 有本 branch package 測試且 pass）、`push.verdicts-ge-2`、`push.reviewer-ne-implementer`（比對 dispatch 記錄檔 `docs/loom/<id>/review.json.dispatch`——由 build／review 站寫，格式進 manifest）、`standing.warn`（固定三行）、`standing.product-principles-reject`、`standing.silence`（KICKOFF-DEFAULTS `standing-docs: waived`）。
- 測：`test_loom_checker_push.py`（含 amend 後 reviewed_sha 失效、review-only commit 動到第二個檔）、`test_loom_checker_standing.py`（product 缺 ratified 行→拒；waived 只靜音 WARN 不解除拒收）。
- 風：`reviewer ≠ implementer` 只能查記錄，記錄本身可造（§0 明說不防）；測試只驗「有記錄且不同」。

**W0-05 host hooks：Claude Code 接線＋Codex scaffold**　after: W0-04
- 檔：`loom-code/hooks/hooks.json` 重寫（SessionStart→新 session-start；PreToolUse Bash 匹配 `git push`／`gh pr create`／`gh pr merge`→`loom_checker.py push`；刪 ask-triage、language-stop-check、git-guard、family-reception、family-relay、plain-relay、router-card；**保留 language-anchor＋lang_detect**（理由見風）；連同 `loom-code/scripts/test_ask_triage_hook.py`、`test_git_guard.py`、`test_language_stop_check_hook.py`、`test_family_relay_artifact_routing.py`、`test_reception_onramp_choice.py`、`test_continuous_mode_router.py` 與 `loom-code/tests/integration/test-router-card-slim.sh` 一併 `git rm`）；`loom-code/hooks/session-start`（重寫，≤2640 words，只印：站序一行、三個決策點、KICKOFF-DEFAULTS 摘要）；`loom-code/scripts/codex_scaffold.py`（寫 `.codex/hooks.json` 固定 command `.codex/hooks/loom-checker` ＋ checker 副本含版本戳；`--self-test` 自己叫起副本派假 push 必被擋（只證明副本跑得起來，不證明信任）；未擋→exit 2。信任由站自己發一道必敗的 `git push loom-trust-probe HEAD`「誰回答」來判，答的是 git→印「請在 Codex 跑 /hooks」）。
- 測：`test_hooks_json.py`（matcher 集合、無舊 hook）、`test_session_start_words.py`（≤2640，cwd 空 repo）、`test_codex_scaffold.py`（command 字串不含版本、重跑冪等、self-test 未擋 exit 2）。
- 風：language-anchor／stop-check 是使用者語言守則（不是 loom 機制），刪掉會失去對話語言錨；**agent-decided：保留 language-anchor＋lang_detect 兩檔**（非 loom 流程機制，登進 mechanisms.yaml 標 `class: host-hygiene`），刪 language-stop-check（與 anchor 重複）。盲跑報告揭露。relay 散文（family-relay／plain-relay）刪除與 concept-model §1「仍需同步的副本」清單衝突——由 W3-06 把 §1 清單改為只剩 checker（§10 已刪 family-reception 契約，relay 是它的配件）。

**W0-06 mechanisms.yaml 與 CI 重算**　after: W0-02, W0-05
- 檔：`docs/loom/evidence/mechanisms.yaml`（五類；每項 `id / class / eval:`）；`loom-code/scripts/check_mechanisms.py`（重算五類：skill 目錄、`--list-rules`、hooks.json、manifest.yaml、`<!-- gate: id -->` grep；四種紅：漏登／殘留／淨增無 budget-exception／無 eval；`--baseline <ref>` 比淨數）；`.github/workflows/loom-code-ci.yml` 新增一步；量測步（skill 數、artifact 種類、session-start 字數 vs KICKOFF-DEFAULTS 基線）。
- 測：`test_check_mechanisms.py` 四種紅各一 fixture；`budget-exception:` 行 grammar 測試。
- 風：W1／W2 刪舊 skill 前，重算會抓到 36 個未登 skill——CI 這一步在 W3 之前先以 `continue-on-error` 掛著，W3-04 拿掉。

### W1 — loom-code 五站
checkpoint：W1 結束必跑。
執行註記（agent-decided，W0 經驗）：W1-01～05 只**新增**站與 agents／references，不刪舊 skill 目錄與舊測試；所有刪除集中到 W1-06 序列做。理由：舊測試家族互相牽連（拔一支連鎖紅），三個平行 implementer 若各自刪會在共用測試檔（gate-script 分類帳、cross-ref 檢查）互撞。W0-13（intake.spec-pass 未按 lens 過濾）併入 W1-03。

**W1-01 write-plan 站**　after: W0-03　`review: after-task`
- 檔：`loom-code/skills/write-plan/SKILL.md`（收件：讀 intent→未 confirmed 時執行「覆述並確認」action（決策點①，含單向門合併問法、second-vendor 一次建議、product 缺 PRINCIPLES 時接訪談）→needs-design 判定→code-only 且 yes 時用 `spec-minimal.md` 自動產 spec 並送 review 站 spec 鏡頭→Task DAG；**站序摘要表**（REQ-9：完整站序含上游、各站產物與決策者、checker 時機、checkpoint 時機）；`<!-- gate: … -->` 只標真閘）；`loom-code/skills/write-plan/references/one-way-door.md`（(a)–(d)＋四道閘＋後果形問法，逐字自 concept-model §4）；刪 `writing-plans/`、`brainstorming/`，連同 `loom-code/scripts/test_brainstorming_*.py`、`test_brief_*.py`、`test_plan_*.py`、`test_writing_plans*`、`test_anchor_primary_*.py`、`test_check_onramp_choice.py`、`test_asking_user_briefing_escalation.py`、`test_request_derived_authorization.py`、`test_authorization_boundary_regressions.py` 一併 `git rm`。
- 測：`test_station_summary_table.py`（每站 SKILL.md 有表且欄位齊）、`test_write_plan_intake.py`（SKILL.md 引用的 checker 子命令存在於 `--list-rules`）。
- 風：writing-plans 的 20 條 reviewer check 全部作廢；其中 Check 22（direction 曝光）與 Check 23（batch 觀測）曾是實證機制——決定不保留（直接與 §10 衝突），記進 CHANGELOG 的刪除清單。

**W1-02 build 站**　after: W0-04
- 檔：`loom-code/skills/build/SKILL.md`（每 task：implementer 派工（fresh context、`Task: <id>` trailer 義務、conventional commit 型別白名單）、worktree／parallel 為 action 段、after-task 觸發、wave 結束算 delta 決定是否叫 review 站、寫 `review.json.dispatch`）；`loom-code/agents/implementer.md` 精簡（保留 12 條 baseline 指向 reference）；刪 `subagent-driven-development/`、`dispatching-parallel-agents/`、`using-git-worktrees/`、`tdd-iron-law/`、`systematic-debugging/`，連同 `test_dispatching_parallel_agents_compaction.py`、`test_dispatch_hygiene_worktree_section.py`、`test_dispatch_profile_contract.py`、`test_implementer_req_tag_guard.py`、`test_packet_validate_stations.py`、`test_task_batch_*`、`test_batch_review_cli.py`、`test_propose_review_batches.py`、`test_plan_card*.py` 一併 `git rm`；新 `loom-code/references/engineering-baseline.md`（tdd＋systematic-debugging 合併，≤1500 words）。
- 測：`test_build_dispatch_record.py`（dispatch 記錄格式＝manifest 宣告）、`test_engineering_baseline_reference.py`（implementer.md 引用路徑存在）。
- 風：SDD 的 spec-reviewer／code-quality-reviewer 兩臂消失，build 期間沒有任何審查直到 checkpoint——這是 §5 明寫的邊界；wave 大小預設 ≤ 6 task。

**W1-03 review 站**　after: W0-04, W1-02
- 檔：`loom-code/skills/review/SKILL.md`（checkpoint 演算法：delta since reviewed_sha＋跨任務一致性＋回歸 probe；≥2 fresh reviewer；鏡頭表（code 11 維／docs 5 維／spec-conformance／design-conformance／principles-conformance）；三種驗證動作按型別對映；盲跑報告格式；second-vendor 只讀 KICKOFF-DEFAULTS、不建議；verdict→review.json→review-only commit）；`loom-code/agents/reviewer.md`（一份契約，`lens:` 參數；合併 code-reviewer／code-quality-reviewer／docs-reviewer／spec-reviewer）；`loom-code/agents/blind-runner.md`、`loom-code/agents/adversary.md`；`loom-code/skills/review/references/{lenses.md,blind-run-report.md,adversarial.md}`；刪 `requesting-code-review/`、`requesting-docs-review/`、`verification-before-completion/`、`ui-verification/`、舊四份 agent，連同 `test_rcr_*.py`、`test_rdr_*.py`、`test_requesting_code_review_*.py`、`test_docs_review*.py`、`test_docs_reviewer_*.py`、`test_code_reviewer_*.py`、`test_code_quality_reviewer_*.py`、`test_adjudication_*.py`、`test_adversarial_station_contract.py`、`test_finding_origin_attribution.py`、`test_post_pass_amendment_gate.py`、`test_check16_prose_row.py`、`test_oracle_capability_claims.py` 一併 `git rm`。
- 測：`test_review_json_schema.py`（write 端與 checker 同一 schema）、`test_reviewer_agent_single_contract.py`（agents/ 只剩 implementer、reviewer、blind-runner、adversary）。
- 風：docs-reviewer 的 delta 封包協定與 adjudication_* 家族（~20 支 script）整組作廢；`_rule-sheet.md`／`_baseline.md` 併進 lenses.md 前先 diff 一次確認 11 維沒少。

**W1-04 ship 站**　after: W1-03
- 檔：`loom-code/skills/ship/SKILL.md`（順序：確認 review.json PASS→memory 步（trailer＋`docs/loom/memory/`，沿 git-memory 工具）→push（checker 擋）→PR（body 從 review.json 與盲跑報告生成，尾附原始 trailer footer）→merge 後 `verify-merged`→intent `status: closed`）；刪 `finishing-a-development-branch/`、`loom-memory/`（memory 慣例文件移到 `loom-code/contract/templates/memory-README.md`），連同 `test_finishing_*.py`、`test_loom_memory_*.py`、`test_post_pr_ci.py`、`test_freeze_changefolder.py`、`test_archive_change_folder.py`、`test_backlog_index.py` 一併 `git rm`。
- 測：`test_ship_pr_body.py`（PR body 含 trailer footer；memory-verify-merged workflow 的 grep 仍命中）。
- 風：memory-verify-merged CI 依賴 trailer 格式；ship 站的 commit 模板行先 grep 白名單（CI 型別坑第 11 次）。

**W1-05 maintain 站**　after: W1-01
- 檔：`loom-code/skills/maintain/SKILL.md`（alert／事故→找同題 open intent→有則只追加 evidence，無則以 `originator: maintenance-loop` 開 intent→事故變 eval（進 mechanisms.yaml 對應機制的 `eval:`）→交 write-plan）。
- 測：`test_maintain_intent_dedupe.py`（同題 open intent 存在時不開第二份——用 fixture 目錄）。
- 風：「同題」判定是 agent 判斷；規則寫成「標題 slug 相同或 evidence 指向同一 alert id」，避免散文閘。

**W1-06 loom-code 收尾**　after: W1-01..05
- 檔：checker 新規則 `push.probes-adversarial`（artifact 型別要求對抗時 ≥3 筆 adversarial probe，逐筆自跑）＋ review.json `questions[]` 欄位（模板、schema 測試）；implementer.md 補回 prose-edit self-sweep（PR#775 實證 +0.75 的規則，W1-02 精簡時掉了）；刪 `loom-code/scripts/` 作廢家族（adjudication_*、batch_review_cli、review_batch、review_context、review_scope、propose_review_batches、task_batch_replay、check_review_batches、loom_gate_markers、loom_init、live_gate_*、living_spec_*、check-living-spec-index、check_onramp_choice、check_north_star_link、check_proposal_status、check_queue_relation、check_scenario_coverage、check_seam_coverage、check_attack_catalogue、plan_card、backlog_index、archive_change_folder、distribute、post_pr_ci、prose_selfsweep_tally、loom_firing_harness、`_baseline.md`／`_reviewer-discipline.md`／`_rule-sheet.md`／`canonical/`）與其 test_*；保留：git_exec、sibling_import、heading_window、check_contract_citations、check_doc_citations、check_field_microstructure、check-skill-crossrefs、check_open_questions（改讀 intent）、lang_detect；刪 `loom-code/tests/*-pressure`（散文閘的舊 eval；由 W4 冷讀 dogfood 取代，登進 mechanisms.yaml）、`tests/integration/test-command-surface-*`、`test-rule-sheet-drift`、`test-router-card-slim.sh`（若 W0-05 未刪）、`test-complexity-critique-delegation.sh`；`integration/` 其餘（superpowers×2、code-team-coexistence、git-memory-delegation）**保留**並 grep 舊站名逐檔改；`loom-code/{PRODUCT-SPEC,TECH-SPEC,ROADMAP}.md` 改寫為指向 concept-model；`loom-code/docs/`（announcement、code-toolkit、example-runs、examples、superpowers）與 `loom-code/research/`：grep 舊站名，引用被刪機制的檔加 ARCHIVED 標頭一行，其餘逐檔改；README×3、CHANGELOG（含刪除清單、`budget-exception` 無——本 change 淨數大降）；plugin.json 1.0.0；`docs/loom/ATTACK-CATALOGUE.md` 移至 `docs/loom/evidence/attack-catalogue.md`（成為 review 站對抗動作的目錄）。**偏離本行清單一處（agent-decided）**：`check_field_microstructure` 原列「保留」，實際刪除——它唯一的 SSOT 是 writing-plans 的 `plan-format.md`，該檔隨 writing-plans 站一併刪除，留著等於留一支對照不存在格式的檢查。
- 測：整個 `pytest loom-code/scripts/` 綠；`check_contract_citations.py` 的 DEBT_LIST 只變短。
- 風：刪除量 ~150 個檔；用 `git rm` 逐路徑，不用 `git add -A`（repo 守則）。W0-01 的 xfail 在此轉綠。

### W2 — loom-design 兩站兩工具
checkpoint：W2 結束必跑。

**W2-01 capture-intent 站**　after: W1-01
- 檔：`loom-design/.claude-plugin/plugin.json` 加 `requires-contract: ">=1.0"`，SKILL.md 開頭一步 `loom_checker.py contract --require 1.0`（不符→BLOCK）；`loom-design/skills/capture-intent/SKILL.md`（訪談→intent.md（contract template）→「覆述並確認」action（同 W1-01，含單向門合併、second-vendor 一次建議、缺 PRINCIPLES 接訪談）→needs-design 判定→交 write-spec 或 loom-code；**站序摘要表**（Task B 路徑））；訪談問法自 user-insights／business-value 精選成 `references/interview.md`（≤1200 words）；刪 `using-loom-design/`、`using-loom-pipeline/`、`user-insights/`、`business-value/`。
- 測：`loom-design/scripts/test_capture_intent_contract.py`（SKILL.md 引用的 template／checker 路徑存在於 loom-code contract package；摘要表欄位齊）。
- 風：cross-plugin 路徑只能用 plugin name 引用（官方：plugin 不可跨引用檔案）；SKILL.md 寫「loom-code 的 contract package」並列出相對於該 plugin 的路徑，checker 由 loom-code hook 觸發、design 側不直接執行。

**W2-02 write-spec 站**　after: W2-01
- 檔：`loom-design/skills/write-spec/SKILL.md`（載 PRINCIPLES／DESIGN→REQ-<n> 對回 Acceptance→Design decision 含 agent-decided／user-decided 標記→Current state evidence 五條→UI flows→**決策點②**（product：白話呈現 Requirements＋UI flows，`confirmed-behavior:`）→交 review 站 spec 鏡頭）；`references/{spec-forms.md（表／圖形式自 spec-expansion）,ui-flows.md（自 interaction-flows）}`；刪 `spec-expansion/`、`interaction-flows/`、`completeness-critic/`、`design-critic/`（其鏡頭併入 W1-03 lenses.md 的 design-conformance）。
- 測：`test_write_spec_contract.py`（REQ id grammar 與 loom-code `test_contract_manifest` 同一 regex——用 sibling_import 讀 manifest 不複製）。
- 風：critic 的「provenance-tagged 增補」豁免（repo CLAUDE.md）隨 critic 刪除而失效；CLAUDE.md 該段在 W3-04 改。

**W2-03 product-principles／design-system 工具**　after: W2-01
- 檔：兩個 SKILL.md 精簡：產出加 `ratified-by: <name> <date>`；訪談模板與 loom-code `PRINCIPLES-interview.md` 同一份（design 側引用，不複製）；`replay_matrix`／`improve_loop` 流程刪；design-system 的 `design_md_spec_keys.py` 留作 DESIGN.md schema。
- 測：`test_principles_ratified_line.py`、既有 `test_design_md_schema_keys.py` 調整。
- 風：product-principles 有五份 CHANGELOG／README 分檔（discovery／interface／pipeline／principles／spec）——W2-04 合成一份。

**W2-04 loom-design 收尾**　after: W2-02, W2-03
- 檔：`loom-design/scripts/` 只留 `principles/`、`interface/`、`spec/` 的 validator＋測試；刪 `discovery/`、`pipeline/`（driver_*.js、batch_queue、queue_*）、`test_unified_pytest_root.py` 調整；README／CHANGELOG 五分檔合一；`loom-design/examples/` grep 舊站名逐檔改或刪；plugin.json 1.0.0；`loom-pipeline-ci.yml` 改名 `loom-design-ci.yml`（branch protection 綁 job 顯示名：先 `gh api` 查再改）。
- 測：`pytest loom-design/scripts/` 綠。
- 風：branch protection 的必經檢查名若含 `loom-pipeline`，改名前先查（memory：改 name 前先 gh api）。

### W3 — loom-workflow、docs、CI、standing docs
checkpoint：W3 結束必跑。

**W3-01 decision-map：delivery ticket → intent**　after: W1-01
- 檔：`loom-workflow/.claude-plugin/plugin.json` 加 `requires-contract`；綁舊 brief 的 DA 改指 `retired — 硬切換`；`loom-workflow/skills/decision-map/SKILL.md`（`start_delivery` 改為「寫 intent.md 帶 `map:`，MAP.md 列 change-id」；狀態由 intent §2b 派生；open intent 阻擋 DA、withdrawn 記 retired）；對應 script／test 修。
- 測：既有 decision-map 測試調整＋`test_decision_map_intent_binding.py`。
- 風：`docs/loom/maps/` 現有 7 檔含舊 ticket 格式——原地封存，MAP.md 加一行「舊 ticket 不轉換」。

**W3-02 critique 合併、recap→handoff、brief-before-asking 刪**　after: W1-01
- 檔：`loom-workflow/skills/critique/SKILL.md`（`mode: proposal | complexity`，兩份 body 合成、共用段去重）；刪 `proposal-critique/`、`complexity-critique/`、`brief-before-asking/`；recap-state、handoff、goal-create、dbt-model-style 不動；`hooks/hooks.json` 若引用 bba 則清；`loom-workflow/docs/`、`loom-workflow/tests/*.sh` grep 舊 skill 名逐檔改；`loom-code/tests/integration/test-complexity-critique-delegation.sh` 在此刪（若 W1-06 未刪）。
- 測：對應 `test_*_compaction.py` 改名合併；`test_skill_count.py`（loom-workflow 恰 10 個目錄，其中 2 個 standalone）。
- 風：brief-before-asking 被 kouko 的全域 CLAUDE.md 點名為預設路徑——這是使用者側設定，不在本 repo；PR body 提醒一句。

**W3-03 docs/loom 收斂**　after: W1-06, W2-04
- 檔：`docs/loom/evidence/`（repo 級：mechanisms.yaml、attack-catalogue.md、自 `audits/`、`research/`、`dogfood/`、`firing-corpus/`、`task-batch-review/`、`outcome-map-v3/`、`references/` 七處**移入**——`git mv` 保留歷史；各子目錄名保留一層）；`plans/`、`specs/`、`backlog/`、`design/` **原地封存**（各加 `ARCHIVED.md` 一行：「loom 1.0 起不再讀寫，新 change 見 `docs/loom/intent/`」）；`BACKLOG.md` 凍結不轉換（agent-decided，偏離本行原文：184 條逐條轉 intent 是一個 session 的量，硬切換原則本就是原地封存；再犯的項目由 maintain 站重新開 intent）；`INDEX.md`、`README.md`、`PURPOSE.md` 改寫；`codex-verification.md` 併進 `evidence/q4-codex-hooks-live-test.md`；`archive/`、`2026-07-12-us-sec-primary-source-layer/`、`2026-07-19-8k-prose-kpi-intake/` 原地不動（舊 change 資料夾，各加 `ARCHIVED.md`）。
- 測：`check_doc_citations.py` 綠；W0-06 的重算對 `**/evidence/**` 型別無誤判。
- 風：`docs/loom/memory/` 258 檔不動（memory 不是 per-change artifact）；BACKLOG 轉換是判斷型工作，逐條列在 commit body。

**W3-04 repo 級守則與 CI**　after: W3-03
- 檔：W2-04 殘留：`AGENTS.md` 引用已刪的 `loom-design/scripts/pipeline/{build_driver,batch_queue}.py`；`loom-code/hooks/lang_detect.py:251` 註解引用 `comms_metrics.py`；`scripts/phase2-loop/` 整包為已刪 batch queue 起草 TOML（整體重估：刪或 ARCHIVED）；`scripts/canonical/loom-family/{family-relay,plain-relay}.md` 已無路由、僅兩支測試在讀（刪＋測試）；`CLAUDE.md`（Agent Behavioral Rules 的 critic 豁免段刪；Quality Gates 段改為三種驗證動作；Contract Citations 不變）；`.github/workflows/loom-code-ci.yml`（刪 living-spec 三步、attack_catalogue、command-surface、rule-sheet-drift；加 `check_mechanisms.py` 與量測步；W0-06 的 continue-on-error 拿掉）；`loom-workflow-ci.yml`、`check-script-sync.yml`、`skill-structure.yml` 對刪除的路徑調整；`scripts/sync_codex_manifests.py` 對三個 plugin 的 codex 鏡射跑一次；`.claude-plugin/marketplace.json` 三段描述改寫，`check-plugin-description-skill-coherence.yml` 與 `check-marketplace-description-sync.py` 本地跑綠。
- 測：本地 `act` 不可用→以 `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/` ＋逐步手跑 workflow 內每個 `run:` 命令代替，結果記進 review.json probes[]。
- 風：branch protection 必經檢查名（先查）；`.claude/hooks/validate-skill-folder-structure.sh` 對新目錄（`loom-code/contract/templates/`）是單層，合規。

**W3-05 standing docs 與 KICKOFF-DEFAULTS**　after: W0-04
- 檔：`docs/loom/KICKOFF-DEFAULTS.md` 重寫成新 grammar（`session-start-baseline: 923fb84a 5281`、`second-vendor:`（本 repo：`codex — kouko 2026-09-02`，依本 change 已用 Codex 審 spec 的事實）、`standing-docs:`、介面表面 glob、型別對映覆寫）；`loom-code/contract/templates/KICKOFF-DEFAULTS.md` 同 grammar；本 repo 的 `PRINCIPLES.md`：原寫「不新建」，但本 change 的 intent 是 `kind: product`，新 standing 閘正確拒收 → 由 orchestrator 依 §0 與 kouko 歷次裁定代填、kouko 決策點①確認後簽 `ratified-by`（2026-09-03，agent-decided 推翻原句）。
- 測：`test_kickoff_defaults_grammar.py`（每行 `key: value — reason (date)`）。
- 風：無。

**W3-06 concept-model／spec 對齊**　after: W3-02
- 檔：`concept-model.md` §1（loom-workflow 欄註明 goal-create／dbt-model-style 為不計數的獨立 skill；「仍需同步的功能副本」改為只剩 checker）、§2e（刪 `.git/loom/ready.json` 本機鏡像子句——plan 不建鏡像，review.json 入版控已足，agent-decided：少一個機制）、§3（加 standalone 計數規則、總數 17、名詞手數結果）、§7a／§11 若落地時措辭有變逐字對齊；`spec.md` 不動（已 PASS；若 W 期間發現 spec 必須改，走 review 站 spec 鏡頭再 PASS，不靜默改）。
- 測：無（docs 鏡頭在 W3 checkpoint 審）。
- 殘：§1 copies line updated for one-way-door (W2)。
- 風：改 spec 會使 review.json 的 scope PASS 失效——規則寫死在上面。
- done（2026-09-03）：§1 工具清單改用完整 skill 名＋standalone 註記（copies 行 checker＋one-way-door 措辭核對無誤，未動）；§2c 補 `confirmed-behavior: <date> @<sha7>`；§2e 刪 `.git/loom/ready.json` 子句、probes 補 `scope`、verdicts 補 `spec_sha`；§3 換計數句、記名詞手數 61（2026-09-03）；§4 補 `intent.kind-recompute` 一句；§7 26 條規則按 area 分組列 id（intent 5／intake 4／contract 1／spec 2／push 11／standing 3，非 plan 原估的 6/10 分法，已用 `--list-rules` 實測校正）；§7a 補 scaffold 檔案層（shim＋`loom_checker.py`＋`git_exec.py`＋`contract/`）；§12 加 W0–W2 落地列。`spec.md` 未動；發現 spec.md 既有 `confirmed-behavior: 2026-09-02` 缺 `@<sha7>`，與 manifest／概念模型的新 grammar 不符，留待 review 站處理，見 review record。

### W4 — 驗收（REQ-9／REQ-10／REQ-2）與盲跑報告
checkpoint：branch 結束必跑（＝W4 checkpoint，含盲跑與對抗）。

**W4-01 冷讀 Task A／Task B（REQ-9）**　after: W1-06, W2-04
- 做：兩個 fresh-context sonnet，各只拿一份 SKILL.md（A：write-plan；B：capture-intent）＋任務句，回答四項；計時；任何「需要猜」的規則記 finding→修 SKILL.md→重跑到零猜測。
- 檔：結果寫 `docs/loom/2026-09-02-simple-loom-flow/evidence/cold-read-{A,B}.md`。
- 風：每輪 ~10 分鐘；上限三輪，仍有猜測→列進盲跑報告的不確定項。

**W4-02 REQ-2 Codex 實走 Task A**　after: W0-05, W1-06
- 做：scratch repo（scratchpad，非本 repo），`codex exec` 走 write-plan 站：確認 scaffold 寫入→未授信 probe BLOCK 訊息→`--dangerously-bypass-hook-trust` 模擬授信後 probe 通過→產出檔案集合與 Claude Code 同一任務的檔案集合 diff 為空（只比路徑與 frontmatter 欄位）。獨立 advisor 的 egress checkpoint 適用（送出的是 scratch repo，不含本 repo 內容）。
- 檔：`evidence/req2-codex-walk.md`。
- 風：Codex 額度；`codex exec` 需 `< /dev/null`。

**W4-03 REQ-10 replay ×3**　after: W1-06, W3-05
- 做（三個 change 分開呈現，不合計；同時量「首輪 vs 後續輪找到的 finding 比例」作門檻判準）（agent-decided，理由：#772 今天 67 commit 是站級新功能，真重建等於重做一個 change，而且舊機制在本 PR 已刪，「今天的做法」無法在同一棵樹上對照）：
  - #771（最小、純工程）**真 replay**：取其 PR 標題與描述寫成 intent（engineering、needs-design: no）、走 write-plan→build→review→ship 到 PR-ready（不開 PR），數 commit／派工／決策點。
  - #772、#775 **推導 replay**：以同樣方式寫 intent 與 plan（agent 產 Task DAG 但不 build），用 #771 實測校準的計數規則（commit＝task 數＋review-only commit 數；派工＝implementer 數＋每 checkpoint 2 reviewer＋盲跑 1＋對抗 1；決策點＝2）推算，並附 #771 的實測／推導誤差。
  - 三者逐項對比今天基線（31/22/2、67/58/2、28/14/2）；任一超出→這是 §0 意義的失敗，記進盲跑報告，不調整計數規則來過。
- 檔：`evidence/replay-{771,772,775}.md`；`ceremony-cost-old-vs-new.md` 加一段「v10 實測」取代過時的 New model 欄。
- 風：這個 agent-decided 偏離會在盲跑報告「我替你決定了」段揭露；使用者不接受時的替代＝三個都真 replay（估三個 session）。

**W4-04 量測與 mechanisms 收尾**　after: W3-04, W4-03
- 做：`check_mechanisms.py --baseline 923fb84a` 淨數；skill 數（17，排除 standalone）；artifact 種類（≤5）；session-start 字數（≤2640）；名詞手數；`needs-design` intent 數等記錄項——結果寫 `evidence/measurements.md` 並貼進盲跑報告。
- 風：淨數基線在 923fb84a 沒有 mechanisms.yaml——`--baseline` 對舊 ref 用「skill 目錄＋hooks.json 條目」兩類近似，寫明。

**W4-05 盲跑報告（決策點③）**　after: W4-01..04
- 做：blind-runner agent（≠ 任何 implementer）在乾淨 clone 裝三個 plugin（本 branch 路徑），對 intent Acceptance 1–7 逐條「怎麼試、結果、證據」；固定行「對你既有的資料做了什麼」；「我替你決定了」段列：language-anchor 保留、replay 方式、Check 22/23 不保留、BACKLOG 逐條處置；不確定項列成問題。
- 檔：`docs/loom/2026-09-02-simple-loom-flow/blind-run-report.md`；review.json 收尾（reviewed_sha 推進、probes[] 含 package 測試與 Codex walk）。
- 風：Acceptance #1 的「基本知識使用者」無法由 agent 扮演證明——盲跑報告如實寫「由 W4-01 冷讀＋決策點措辭審查間接證明」。

## 2. 全 plan 風險

1. **過渡期的舊守衛**：本 session 裝的是 loom-code 0.110.0 的 git-guard（讀 `.git/loom/*.json`），會擋本 branch 的 push。ship 站落地前不 push；到 W4 結束一次 push 時，若舊 guard 仍擋，請使用者以 `!` 前綴 push（memory：guard 用 shell cwd）；不鑄舊 marker、不 `--no-verify`。
2. **plugin cache 是 GitHub main**：本 branch 的新站在 merge 前無法透過 `/reload-plugins` 試；W4 一律用「本 branch 路徑直接 Read SKILL.md」與 scratch repo 的 `--plugin-dir` 型安裝做盲跑。
3. **刪除量**：~150 檔＋~200 個測試。每個 wave 結尾 `pytest` 全綠才算 wave 結束；刪除型 task 會撞 SDD 的 cat-file 檢查——SDD 本身在 W1 被刪，W0 期間的刪除延到 W1-06 一次做。
4. **REQ-8 字數**：session-start 減半是硬條件；若站序表放進 session-start 就超——只放一行指向 write-plan／capture-intent。
5. **Codex 額度**：W4-02 一次、若 KICKOFF-DEFAULTS 記 `second-vendor: codex` 則每個 checkpoint 多一個 Codex reviewer（五次）。額度不足時該 checkpoint 記 `vendors: [anthropic]`，不 WARN。
