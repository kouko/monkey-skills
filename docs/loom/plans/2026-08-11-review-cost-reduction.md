# Plan: review-cost reduction (Option B)

**Source brief**: docs/loom/specs/2026-08-11-review-cost-reduction.md
Goal: docs review narrows to contract-class `.md` with a single-round-plus-delta-confirmation
    loop (aggregation thresholds unchanged — 2026-08-11 user decision), reviewer arms ship
    sonnet defaults with a mechanical upgrade rule, and plan-document-reviewer routing becomes
    substitution-proof — one loom-code version bump.
Stage: finishing
Steps:
  1. 歷史抽查與五件獨立前置修正
  2. 範圍收窄 SSOT（rcr 路由）＋docs-reviewer frontmatter pin
  3. 各站迴圈與範圍連鎖、閘門機制、升級規則與冷讀探針
  4. carve-out 同步與跨檔 lockstep
  5. 版本 bump 與鏡射
**Total tasks**: 18
**Critical-path depth**: 5 (≤5 ✓, counted in nodes — longest chain: 1→8→7→13→16)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-08-11, round 2 + three delta confirmations by the same reviewer, incl. the option-1 rescope; final: CONFIRMED_RESOLVED / plan_verdict: PASS)

## Task 1 — History-check sampling: were past 2+🟡 verdicts load-bearing?

- **Description**: Sample every reachable 2+🟡-driven NEEDS_REVISION docs verdict since requesting-docs-review shipped (2026-07-30, PR #629): enumerate merged PRs via `gh pr list --state merged --search "merged:>=2026-07-30" --json number,body,title --limit 100`, plus `git log --grep "review" --since 2026-07-30` gate-marker commits, extract every verdict whose NEEDS_REVISION was caused by the 2+🟡 rule (no 🔴), and classify each cited 🟡 as load-bearing (an instruction a weak model would execute wrongly / a fact that misleads) vs conventional (label/format/style). Write the sample table + load-bearing fraction to `docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md`. STOP condition (verbatim from brief §Decision conditional reversal): if the load-bearing fraction is material (>20% of sampled 🟡s), surface to the user BEFORE the aggregation change proceeds. [RESOLVED 2026-08-11: STOP tripped (14/14); user chose option 1 — aggregation relaxation dropped, original Task 6 removed from this plan; Task 8 is now gated on this task.]
- **Module**: `docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md` (new)
- **Files touched**: `docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md`
- **Context paths**:
  - `docs/loom/backlog/2026-08-10-yellow-findings-should-default-to-debt-not-revision-loops.md` (the sampling duty: "sample past 2+🟡 verdicts and confirm how many 🟡s turned out load-bearing")
  - `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` (classification precedent for 🟡 accuracy vs consequence)
- **Acceptance**:
  - **RED**: diagnostic — `test -f docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md` fails (file absent)
  - **GREEN**: file exists with a per-verdict sample table, a per-🟡 load-bearing/conventional classification with one-line reasons, a computed load-bearing fraction, and an explicit verdict line "PROCEED" or "STOP — surface to user" per the >20% threshold
- **External surfaces**:
  - CLI flag: `gh pr list --state merged --search --json` — grounding: `gh pr list --help` (captured 2026-08-11)
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "History-check duty (seed entry): sample past 2+🟡 NEEDS_REVISION verdicts for load-bearing 🟡s BEFORE the relaxation lands — plan MUST include this task"
- **Status**: done(2b7dc1bb)
- **Gloss**: 先驗證「過去被 2+🟡 擋下的發現裡有多少是真承重的」——比例太高整個放寬就要先收窄，這是放寬規則前的安全網。

## Task 2 — writing-plans misroute fix: plan-document-reviewer is a prompt file, never a registry lookup

- **Description**: In `loom-code/skills/writing-plans/SKILL.md`: (a) §Self-review — add explicit sentences: plan-document-reviewer is a PROMPT FILE (`references/plan-document-reviewer-prompt.md`) dispatched via a generic subagent; it is NEVER an agent-registry lookup; no other reviewer agent (docs-reviewer included) may substitute; dispatch defaults to `model: sonnet` with dispatch-time upward override. (b) SKILL.md:9 SUBAGENT-STOP block — disambiguate: mark plan-document-reviewer as a prompt-file role, not a registered agent type (current text lists it alongside registered roles — the likelier confusion source per brief). Do NOT disturb the revision-delta sentence at :109 or its pins in `scripts/test_wp_extraction_pointers.py`. Word cap is 4099 (current 4081); a net-positive edit takes a sanctioned ratchet raise to 4200 with the reason recorded in the cap test's assertion message (precedents 4023→4047→4099).
- **Module**: `loom-code/skills/writing-plans/SKILL.md`
- **Files touched**: `loom-code/skills/writing-plans/SKILL.md`, `loom-code/scripts/test_wp_selfreview_routing.py`, `loom-code/scripts/test_wp_extraction_pointers.py`
- **Context paths**:
  - `loom-code/skills/writing-plans/SKILL.md`
  - `docs/loom/backlog/2026-08-10-plan-document-reviewer-misrouted-as-agent-type.md` (fix sketch + incident)
  - `loom-code/scripts/test_wp_extraction_pointers.py` (cap + :109 pins)
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_wp_selfreview_routing.py::test_prompt_file_never_registry_never_substitute` (new) — asserts the three routing sentences present in §Self-review and the SUBAGENT-STOP disambiguation present
  - **GREEN**: new test passes; `test_wp_extraction_pointers.py` passes (ratchet raised with recorded reason if needed); full `pytest loom-code/scripts/` green
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "§4 Misroute fix — plan-document-reviewer is a PROMPT FILE for a general-purpose subagent, NEVER an agent-registry lookup; no other reviewer agent may substitute. Disambiguate SKILL.md:9's SUBAGENT-STOP role listing. Dispatch guidance gains model: sonnet default"
- **Status**: done(d270b2f5)
- **Gloss**: 把外部 repo 實際發生的「查無此 agent → 錯用 docs-reviewer 空轉 3 輪」路斷根——冷操作者照字面走也不會走錯。

## Task 3 — claude-code-tools.md: fix "4 plugin-level agents" → 5

- **Description**: In `loom-code/skills/using-loom-code/references/claude-code-tools.md`, replace the stale count "4 plugin-level agents" with "5 plugin-level agents" and ensure docs-reviewer is named in the agent enumeration (brief: "actual is 5 (omits docs-reviewer)"). Add one sentence noting reviewer agents may carry a `model:` frontmatter key (host-native default; dispatch-time `model` param overrides upward).
- **Module**: `loom-code/skills/using-loom-code/references/claude-code-tools.md`
- **Files touched**: `loom-code/skills/using-loom-code/references/claude-code-tools.md`
- **Context paths**:
  - `loom-code/skills/using-loom-code/references/claude-code-tools.md`
- **Acceptance**:
  - **RED**: diagnostic — `grep -c "4 plugin-level agents" loom-code/skills/using-loom-code/references/claude-code-tools.md` returns 1 (stale fact present)
  - **GREEN**: same grep returns 0; "5" count present; docs-reviewer named; model-frontmatter note present
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: prose
- **Brief item covered**: "Rider (stale fact): claude-code-tools.md '4 plugin-level agents' → 5"
- **Status**: done(2098b1ef)
- **Gloss**: 修掉會誤導 host 對照表讀者的陳舊數字，順帶記上模型預設鍵的存在。

## Task 4 — codex-tools.md: Codex-side model mapping + silent-fallback gotcha

- **Description**: In `loom-code/skills/using-loom-code/references/codex-tools.md` (dispatch re-binding section, :111-115 area anchored by "spawn_agent with the corresponding loom-code/agents/<role>.md content"), add a Codex model-mapping subsection: (a) per-subagent `.codex/agents/<name>.toml` with `model =` / `model_reasoning_effort =` (file value takes precedence; project `.codex/agents/` overrides personal `~/.codex/agents/`); (b) suggested defaults mirroring the Claude Code frontmatter (checklist reviewer roles → a mid-tier model; judgment roles inherit); (c) the MANDATORY gotcha (brief: "MUST document"): under Multi Agent V2, `hide_spawn_agent_metadata=true` silently ignores per-agent model config — workaround `hide_spawn_agent_metadata = false` under `[features.multi_agent_v2]`; (d) one line recording the plan-time decision: `.codex/agents/*.toml` is documentation-only this arc — `sync_codex_manifests.py` emission filed as debt in the PR body. Host-native alias values only; no Claude model names in this file's Codex examples.
- **Module**: `loom-code/skills/using-loom-code/references/codex-tools.md`
- **Files touched**: `loom-code/skills/using-loom-code/references/codex-tools.md`
- **Context paths**:
  - `loom-code/skills/using-loom-code/references/codex-tools.md`
  - `docs/loom/specs/2026-08-11-review-cost-reduction.md` (§Alternatives — Codex mechanism facts + sources)
- **Acceptance**:
  - **RED**: diagnostic — `grep -c "hide_spawn_agent_metadata" loom-code/skills/using-loom-code/references/codex-tools.md` returns 0 (gotcha absent)
  - **GREEN**: same grep ≥1; toml keys documented; documentation-only decision line present
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: prose
- **Brief item covered**: "Codex: `.codex/agents/<name>.toml` `model=` / `model_reasoning_effort=` ... MUST document the JP-sourced gotcha ... Emission-vs-documentation decided at plan time" (decision: documentation-only, debt-filed)
- **Status**: done(590952db)
- **Gloss**: Codex 使用者拿到原生的模型設定法＋那個會讓設定靜默失效的坑的解法——不寫這個坑，整個機制在 Codex 上可能無聲空轉。

## Task 5 — `model: sonnet` frontmatter on spec-reviewer.md

- **Description**: In `loom-code/agents/spec-reviewer.md` frontmatter, insert the exact literal line `model: sonnet` immediately below the existing `description:` key (frontmatter today carries ONLY `name:` + `description:` — brief Boundary). No other changes.
- **Module**: `loom-code/agents/spec-reviewer.md`
- **Files touched**: `loom-code/agents/spec-reviewer.md`
- **Context paths**:
  - `loom-code/agents/spec-reviewer.md`
- **Acceptance**:
  - **RED**: diagnostic — `grep -c "^model: sonnet" loom-code/agents/spec-reviewer.md` returns 0
  - **GREEN**: same grep returns 1, line sits inside the frontmatter block (durable pin lands in Task 18)
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical
- **Brief item covered**: "Claude Code: `model:` frontmatter in loom-code/agents/*.md — spec-reviewer / code-quality-reviewer / docs-reviewer → sonnet"
- **Status**: done(90ed8bff)
- **Gloss**: spec-reviewer 臂的預設模型落地為 sonnet——464 次零事故的實證安全案例寫進機器可讀的預設值。

## Task 7 — docs-reviewer agent contract: scope + delta-confirmation duty (aggregation untouched)

- **Description**: Rewrite `loom-code/agents/docs-reviewer.md`: (a) scope contract — the agent reviews CONTRACT-CLASS `.md` only, defined by the path rule (this plan is the authoring source for the literal; the SAME literal ships in Task 8's rcr SSOT, and Task 13's cross-file lockstep assertion enforces the two stay byte-equal regardless of which lands first): contract-class = paths matching `<plugin>/skills/**/*.md`, `<plugin>/agents/*.md`, `<plugin>/hooks/*.md`, `<plugin>/scripts/*.md` excluding any `README*`/`CHANGELOG*` basename; record-class (everything else, incl. `docs/**`) is out of the agent's jurisdiction — if handed record-class files, state N/A per file, loudly, and review only the contract-class remainder; (b) NEW delta-confirmation duty: after a gating NEEDS_REVISION verdict, the orchestrator sends the revision delta via SendMessage — respond with a delta-scoped confirmation verdict (CONFIRMED_RESOLVED / STILL_BLOCKING + reason), scoped to the delta only, never a fresh whole-corpus re-sample. The aggregation section (:465-477) is UNTOUCHED — thresholds survive per the 2026-08-11 user decision. Add `test_review_scope_and_loop.py::test_docs_reviewer_scope_and_confirmation`; touch `scripts/test_docs_reviewer_agent.py` only if the insertions shift its pinned lines (:180,194).
- **Module**: `loom-code/agents/docs-reviewer.md`
- **Files touched**: `loom-code/agents/docs-reviewer.md`, `loom-code/scripts/test_docs_reviewer_agent.py`, `loom-code/scripts/test_review_scope_and_loop.py`
- **Context paths**:
  - `loom-code/agents/docs-reviewer.md`
  - `docs/loom/specs/2026-08-11-review-cost-reduction.md` (§1 Scope narrowing, §2 loop shape)
  - `loom-code/scripts/test_docs_reviewer_agent.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_review_scope_and_loop.py::test_docs_reviewer_scope_and_confirmation` (new) fails
  - **GREEN**: new test passes (+ `test_docs_reviewer_agent.py` still green); aggregation section :465-477 shows NO hunk in the task's diff; scope path-rule + N/A-loudly duty + confirmation-duty sections present
- **Dependencies**: Tasks 8, 18 complete first
- **Independent**: false
- **Brief item covered**: "§1 Contract-class (reviewed) ... Record-class (exempt)" + "§2 Gating verdict → fix → delta confirmation by the SAME reviewer via SendMessage ... not a fresh dispatch, not a re-sample"
- **Status**: done(dc23ae01)
- **Gloss**: 執行審查的 agent 本體換上新契約：只管契約類文本、修正後只驗 delta——不重抽樣就不會再自產缺陷螺旋（聚合門檻依你的裁決原封不動）。

## Task 8 — requesting-code-review routing: contract/record classification + record-only delegation

- **Description**: In `loom-code/skills/requesting-code-review/SKILL.md` routing sites (:38,44 triviality carve-out "authored prose"; :92 docs-only branch delegation; :93 mixed-branch per-file split): (a) install the classification SSOT — the same path rule verbatim as Task 7 (contract-class globs excluding README*/CHANGELOG*; record-class = everything else); this section is the ONE place the rule text lives — Task 7's agent copy and Task 14's Python encoding both cite it; (b) :92-93 — the docs arm receives contract-class files ONLY; record-class files are exempt from review at any mix; a branch whose changed files are ALL record-class `.md` runs NO docs arm and satisfies the push gate via the record-only continuity mechanism (name Task 14's marker verb); (c) keep worse-of-two-arms verdict join for mixed branches (unchanged). Extend `test_review_scope_and_loop.py` with `test_rcr_scope_classification` asserting the glob rule + record-exemption + continuity-mechanism sentences. Word cap 3935 with current count 3934 — 1-word margin (`scripts/test_rcr_extraction_pointers.py:153,157`): net additions REQUIRE the sanctioned ratchet raise to 4150 with the reason recorded in the assertion message (precedents 4023→4047→4099). The §Aggregation rule text :167-176 is UNTOUCHED (2026-08-11 user decision).
- **Module**: `loom-code/skills/requesting-code-review/SKILL.md`
- **Files touched**: `loom-code/skills/requesting-code-review/SKILL.md`, `loom-code/scripts/test_review_scope_and_loop.py`, `loom-code/scripts/test_rcr_extraction_pointers.py`, `loom-code/scripts/test_review_scope_stations.py`
- **Context paths**:
  - `loom-code/skills/requesting-code-review/SKILL.md`
  - `loom-code/scripts/test_review_scope_stations.py` (13 routing assertions shared with code arm — update only docs-arm-scope ones)
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_review_scope_and_loop.py::test_rcr_scope_classification` (new) fails
  - **GREEN**: new test passes; `test_review_scope_stations.py` updated + green; word-cap test green with recorded ratchet reason; §Aggregation rule region shows NO hunk in the task's diff
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: "Classification is PATH-BASED (mechanical, weak-model-safe); exact glob list fixed at plan time" + "Record-only branches: zero docs-review dispatches"
- **Status**: done(152bf197)
- **Gloss**: 「哪些文件要審」變成一條路徑規則寫死在單一源頭——記錄類文件（審查量的 57%）從審查管線整個退場。

## Task 9 — requesting-docs-review: scope statement + single-round-with-confirmation loop

- **Description**: Rewrite `loom-code/skills/requesting-docs-review/SKILL.md`: (a) scope — cite Task 8's classification SSOT (point, don't copy: "scope per requesting-code-review §<classification heading>"); (b) aggregation cascade :65-69 — UNTOUCHED (thresholds survive per the 2026-08-11 user decision; do not touch :67/:69); (c) REPLACE the bounded-convergence design (2 rounds + qualifying auto-delta round) with the single-round contract: round 1 whole-artifact is the ONLY full review; no gating findings → done (non-gating findings → debt, thresholds unchanged); gating verdict → fix → delta confirmation by the same reviewer (CONFIRMED_RESOLVED / STILL_BLOCKING); STILL_BLOCKING after one fix cycle → STOP, surface to user; terminal state is "no gating findings", never "clean"; session death before confirmation → one fresh single round; (d) update the SKILL.md frontmatter `description:` (currently advertises "bounded convergence cap: 2 rounds plus at most one qualifying-shape ... auto-delta round" — stale after this task). The companion reference `references/convergence-contract.md` is rewritten by Task 19 (this task keeps the existing link line pointing at it). Update pins: `scripts/test_docs_review_mode.py` (:189-190,:467-489,:660-661,:776-810,:1093-1098), `test_docs_review_blocking_class.py:146,163` (relocation pin — keep "instruction-class findings only" ABSENT from rdr SKILL.md), `test_rdr_extraction_pointers.py`, `test_reviewer_r3_conditional.py`, `test_requesting_docs_review_skill.py`. Word cap 4430 (current 3326 — room; no ratchet expected).
- **Module**: `loom-code/skills/requesting-docs-review/SKILL.md`
- **Files touched**: `loom-code/skills/requesting-docs-review/SKILL.md`, `loom-code/scripts/test_docs_review_mode.py`, `loom-code/scripts/test_docs_review_blocking_class.py`, `loom-code/scripts/test_rdr_extraction_pointers.py`, `loom-code/scripts/test_reviewer_r3_conditional.py`, `loom-code/scripts/test_requesting_docs_review_skill.py`, `loom-code/scripts/test_review_scope_and_loop.py`
- **Context paths**:
  - `loom-code/skills/requesting-docs-review/SKILL.md`
  - `loom-code/skills/requesting-docs-review/references/convergence-contract.md`
  - `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` (delta-scope validation — design evidence)
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_review_scope_and_loop.py::test_rdr_single_round_confirmation` (new function added by this task) fails
  - **GREEN**: new function + all five updated pin files pass; frontmatter description no longer mentions the 2-round cap; old cap strings absent from SKILL.md (convergence-contract.md is Task 19's own GREEN)
- **Dependencies**: Task 8 completes first
- **Independent**: false  # shares scripts/test_review_scope_and_loop.py with sibling cascade tasks
- **Brief item covered**: "§2 Loop shape replaces round-counting: Round 1 = whole-artifact ... the ONLY full review ... Still-blocking after one fix cycle → STOP, surface to user. Terminal state is 'no gating findings', never 'clean'"
- **Status**: done(65862104)
- **Gloss**: 文件審查站的迴圈合約整個換血：一輪整檔、修了只驗 delta、驗不過就交回給你——「審到乾淨」這個數學上到不了的終點從契約裡消失。

## Task 10 — finishing-a-development-branch Step 3 cascade

- **Description**: In `loom-code/skills/finishing-a-development-branch/SKILL.md`: verdict thresholds at :117/:119/:135-136 are UNTOUCHED (2026-08-11 user decision). Update ONLY the docs-arm loop-mechanism language: wherever Step 3 / the dispatch table (:83) / cap-STOP surfacing describes the docs arm's 2-round-plus-auto-delta cap, re-point to the single-round + same-reviewer delta-confirmation contract (STILL_BLOCKING → surface to user). Update `scripts/test_finishing_step3_autoproceed.py` / `test_finishing_docs_arm.py` only if the loop-language edit shifts their pinned lines. Guard: file is 4485 words with NO pin cap but CI CHK-SKL-010 blocks ~4500 (brief Boundary) — the edit must be net-neutral-or-negative; if impossible, split wording to a reference file rather than crossing the CI cap.
- **Module**: `loom-code/skills/finishing-a-development-branch/SKILL.md`
- **Files touched**: `loom-code/skills/finishing-a-development-branch/SKILL.md`, `loom-code/scripts/test_finishing_step3_autoproceed.py`, `loom-code/scripts/test_finishing_docs_arm.py`, `loom-code/scripts/test_review_scope_and_loop.py`
- **Context paths**:
  - `loom-code/skills/finishing-a-development-branch/SKILL.md`
  - `loom-code/scripts/test_finishing_step3_autoproceed.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_review_scope_and_loop.py::test_finishing_confirmation_stop` (new function) fails
  - **GREEN**: new function + pins pass; :117 threshold parenthetical byte-unchanged in the task's diff; word count ≤4500 (CHK-SKL-010)
- **Dependencies**: Task 8 completes first
- **Independent**: false  # shares scripts/test_review_scope_and_loop.py with sibling cascade tasks
- **Brief item covered**: "Cascade sites re-worded to match" (finishing Step 3 rows of brief §Current State Evidence Forward)
- **Status**: done(4d07c4fd)
- **Gloss**: 收尾站的 docs 臂改掛單輪確認制——門檻照舊，但「修了重審整輪」的老路從流程圖裡拿掉。

## Task 11 — subagent-driven-development: prose-weight record-class scope (verdict table untouched)

- **Description**: In `loom-code/skills/subagent-driven-development/SKILL.md`: (a) §Verdict resolution table :139-144 — UNTOUCHED (2026-08-11 user decision; row :144 already ships task-level 🟡/🟢 as debt, no edit needed); (b) prose review-weight substitution (:121,127) — when a `Review-weight: prose` task's `Files touched` are ALL record-class `.md` (per Task 8's classification SSOT — point, don't copy), the docs-reviewer substitution is N/A: dispatch spec-reviewer only and record "code-quality slot: N/A — record-class prose" in the task summary; contract-class prose keeps the substitution unchanged. Update `test_review_weight_prose.py:193` + `test_sdd_needs_context_cap.py:4,45` heading refs if the section heading changes (prefer keeping the heading verbatim to avoid the churn). Word cap 4175 with current count 4175 — ZERO margin (`scripts/test_sdd_extraction_pointers.py:85,399`): any net-positive edit REQUIRES a ratchet raise (to 4250) with the reason recorded in the assertion message.
- **Module**: `loom-code/skills/subagent-driven-development/SKILL.md`
- **Files touched**: `loom-code/skills/subagent-driven-development/SKILL.md`, `loom-code/scripts/test_sdd_extraction_pointers.py`, `loom-code/scripts/test_review_weight_prose.py`, `loom-code/scripts/test_review_scope_and_loop.py`
- **Context paths**:
  - `loom-code/skills/subagent-driven-development/SKILL.md`
  - `loom-code/scripts/test_sdd_extraction_pointers.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_review_scope_and_loop.py::test_sdd_prose_weight_record_class_scope` (new function) fails
  - **GREEN**: new function passes; ratchet raised with recorded reason if net-positive; `test_review_weight_prose.py` green; §Verdict resolution table shows NO hunk in the task's diff
- **Dependencies**: Task 8 completes first
- **Independent**: false  # shares scripts/test_review_scope_and_loop.py with sibling cascade tasks
- **Brief item covered**: "Cascade sites re-worded to match" + "§1 ... Record-class ... exempt from the docs arm" (SDD per-task substitution is the docs arm's task-level face)
- **Status**: done(17954dd9)
- **Gloss**: 任務級審查同步收窄：純記錄類的散文任務不再派 docs-reviewer——省下的每一次派工都是實打實的額度。

## Task 12 — M3 mechanical upgrade rule in requesting-code-review dispatch guidance

- **Description**: In `loom-code/skills/requesting-code-review/SKILL.md` (docs-arm dispatch guidance, adjacent to the Task 8 routing section): add the M3 upgrade rule as three mechanical sentences: (1) a branch whose changed contract-class files include any `agents/*.md` → dispatch the docs arm with `model: opus` (dispatch-time override); (2) a branch changing ≥10 contract-class `.md` files → same upgrade; (3) a contested 🔴 (writer disputes the finding) → second opinion one tier up. Include the honesty note verbatim from the brief: catch-quality-by-tier is UNMEASURED — the upgrade rule is the hedge. Extend `test_review_scope_and_loop.py` with `test_rcr_m3_upgrade_rule` asserting the three triggers + the literal 10. Word cap: rides Task 8's 4150 ratchet (same file, same test; cumulative reason).
- **Module**: `loom-code/skills/requesting-code-review/SKILL.md`
- **Files touched**: `loom-code/skills/requesting-code-review/SKILL.md`, `loom-code/scripts/test_review_scope_and_loop.py`
- **Context paths**:
  - `loom-code/skills/requesting-code-review/SKILL.md`
  - `docs/loom/specs/2026-08-11-review-cost-reduction.md` (§3 M3)
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_review_scope_and_loop.py::test_rcr_m3_upgrade_rule` (new function) fails
  - **GREEN**: function passes; three triggers + literal threshold present; honesty note present
- **Dependencies**: Task 8 completes first
- **Independent**: false
- **Brief item covered**: "Mechanical upgrade rule (named, path-based): branch touches agents/*.md ... or exceeds a contract-file-count threshold → dispatch that docs review at opus; a contested 🔴 → second opinion one tier up ... must be a literal number in shipped text"
- **Status**: done(c8c7f934)
- **Gloss**: sonnet 省錢的保險絲：碰到審查者自己的契約檔或大面積契約改動時，機械規則自動把該次審查升回貴檔——升級條件照路徑判，弱模型也不會用錯。

## Task 13 — Reviewer-discipline carve-out: contract-class qualifier + resync functional copies

- **Description**: In `loom-code/scripts/_reviewer-discipline.md:8` (SSOT for the shared carve-out sentence naming docs-reviewer — functional copies live in `agents/code-reviewer.md:54`, `agents/spec-reviewer.md:62`, `agents/code-quality-reviewer.md:66` per brief §Forward), add the contract-class qualifier: authored-prose routing to docs-review applies to CONTRACT-CLASS `.md` only (cite Task 8's SSOT heading; record-class prose is review-exempt). Then re-run the distribution sync (`loom-code/scripts/distribute.py` — AGENT_BASELINE_TARGETS / AGENT_REVIEWER_DISCIPLINE_TARGETS lists at :193,:211) and commit the synced agent files unmodified. Update `scripts/test_reviewer_carve_out_wording.py`, ADDING the cross-file lockstep assertion: the contract-class glob literal in `requesting-code-review/SKILL.md` (Task 8's SSOT) and its copy in `agents/docs-reviewer.md` (Task 7) are byte-equal — this is the pin that makes Tasks 7/8's authoring order irrelevant.
- **Module**: `loom-code/scripts/_reviewer-discipline.md` (SSOT; agent files are sync output)
- **Files touched**: `loom-code/scripts/_reviewer-discipline.md`, `loom-code/agents/code-reviewer.md`, `loom-code/agents/spec-reviewer.md`, `loom-code/agents/code-quality-reviewer.md`, `loom-code/agents/docs-reviewer.md`, `loom-code/scripts/test_reviewer_carve_out_wording.py`
- **Context paths**:
  - `loom-code/scripts/_reviewer-discipline.md`
  - `loom-code/scripts/distribute.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_reviewer_carve_out_wording.py::test_contract_class_qualifier_and_lockstep` (new function: contract-class qualifier present in SSOT + all synced copies; rcr↔docs-reviewer glob literal byte-equal) fails
  - **GREEN**: updated test passes; sync-drift check clean (synced copies byte-match SSOT block)
- **Dependencies**: Tasks 5, 7, 8, 17 complete first
- **Independent**: false
- **Brief item covered**: "shared carve-out sentence in agents/{code-reviewer:54,spec-reviewer:62,code-quality-reviewer:66} + scripts/_reviewer-discipline.md:8" (brief §Forward — cascade site)
- **Status**: done(55143dda)
- **Gloss**: 四個 agent 共用的那句「散文路由到 docs-review」補上契約類限定——從單一源頭改一次、同步腳本鋪到全部副本，不留半套規則。

## Task 14 — loom_gate_markers: record-only branch continuity (mechanically-validated exemption)

- **Description**: Extend `loom-code/scripts/loom_gate_markers.py` with a record-only exemption verb: `mint --review-na-record-only` mints a review-N/A marker that `validate` (and thereby `hooks/git-guard.py`, which is arm-agnostic per brief §Error) accepts as satisfying the review-pass requirement IFF every file changed on the branch vs the merge-base with main (`git diff --name-only <merge-base>`) is record-class per the SAME path rule as Task 8's SSOT (encode the globs in Python with a comment citing the rcr SKILL.md heading — doc-mirrors-code lockstep); any contract-class or non-`.md` file in the diff → refuse to mint, loudly, naming the offending paths. Integrate with the existing docs-arm dimension logic (:170-198 dimension sets, :803-823, :1083-1093 origin-exemption — brief §Error: structural, not a pointer). TDD via `scripts/test_loom_gate_markers.py` additions: mint-accepts (all-record fixture), mint-refuses (mixed fixture, names offender), validate-accepts minted marker.
- **Module**: `loom-code/scripts/loom_gate_markers.py`
- **Files touched**: `loom-code/scripts/loom_gate_markers.py`, `loom-code/scripts/test_loom_gate_markers.py`
- **Context paths**:
  - `loom-code/scripts/loom_gate_markers.py`
  - `loom-code/hooks/git-guard.py`
  - `loom-code/scripts/test_loom_gate_markers.py`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_loom_gate_markers.py::test_record_only_exemption_mints_and_validates` (new) fails
  - **GREEN**: new tests pass (accept/refuse/validate trio); full `pytest loom-code/scripts/test_loom_gate_markers.py` green
- **Dependencies**: Task 8 completes first
- **Independent**: true
- **Brief item covered**: "Push-guard continuity requirement: such branches must still satisfy the arm-agnostic push guard — mechanism ... decided at plan time; the requirement (no docs-only push may dead-end at the guard) is fixed here" (decision: mechanically-validated exemption marker)
- **Status**: done(a6928d83)
- **Gloss**: 純記錄類分支免審之後 push 不會被自家閘門卡死——豁免標記由程式對照分支 diff 機械驗證，不靠任何人自由心證。

## Task 15 — Cold-reader probes: misroute fix + classification rule

- **Description**: Dispatch two haiku cold-reader probes (institution quality floor: "a cold agent executes it blind on one real case"): (a) misroute probe — a fresh-context haiku agent given ONLY the post-Task-2 writing-plans §Self-review text + a realistic "dispatch the plan reviewer" task; PASS iff it dispatches the prompt file via a generic subagent and does NOT search an agent registry or substitute docs-reviewer; (b) classification probe — a fresh-context haiku agent given ONLY Task 8's classification section + a 10-path mixed file list; PASS iff it classifies all 10 correctly. Write both transcript summaries + PASS/FAIL to `docs/loom/dogfood/2026-08-11-review-cost-probes.md`. A FAIL means the wording is wrong — fix the wording (route back to the owning task's file), not the reader.
- **Module**: `docs/loom/dogfood/2026-08-11-review-cost-probes.md` (new)
- **Files touched**: `docs/loom/dogfood/2026-08-11-review-cost-probes.md`
- **Context paths**:
  - `loom-code/skills/writing-plans/SKILL.md` (post-Task-2)
  - `loom-code/skills/requesting-code-review/SKILL.md` (post-Task-8)
- **Acceptance**:
  - **RED**: diagnostic — `test -f docs/loom/dogfood/2026-08-11-review-cost-probes.md` fails (report absent)
  - **GREEN**: report exists recording BOTH probes with PASS outcomes (a FAIL loops back to wording first; the task completes only on double PASS)
- **Dependencies**: Tasks 2, 8 complete first
- **Independent**: true
- **Brief item covered**: "Cold-reader (haiku) probe verifies routing" (§4) — extended per institution quality floor to the new classification rule (§1 "mechanical, weak-model-safe" is a testable claim)
- **Status**: done(958cd68e)
- **Gloss**: 兩條新規則各拿一個「只讀規則文本的冷 haiku」實測——弱模型照字面走也不出錯，規則才算真的機械化。

## Task 16 — Version bump 0.75.0 + mirrors + CHANGELOG

- **Description**: Bump `loom-code/.claude-plugin/plugin.json` version 0.74.0 → 0.75.0; run `python3 scripts/sync_codex_manifests.py loom-code` and commit the synced `.codex-plugin/plugin.json` unmodified; update `.claude-plugin/marketplace.json` loom-code version; add a `loom-code/CHANGELOG.md` 0.75.0 entry covering the shipped items (contract-class scope narrowing + record-only exemption / single-round + delta-confirmation loop / M3 model defaults / misroute fix — noting explicitly that aggregation thresholds are unchanged per the 2026-08-11 user decision, evidence: the yellow-finding load-bearing sample audit). Files-touched note: the repo hook enforces the `.codex-plugin` mirror as part of any plugin.json bump (auto-memory precedent). Close-out pointer (brief §What Becomes Obsolete "at close-out" duty — see Notes): the finishing flow retires/shrinks the three named backlog entries.
- **Module**: `loom-code/.claude-plugin/plugin.json`
- **Files touched**: `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `loom-code/CHANGELOG.md`
- **Context paths**:
  - `loom-code/.claude-plugin/plugin.json`
  - `scripts/sync_codex_manifests.py`
- **Acceptance**:
  - **RED**: `python3 scripts/sync_codex_manifests.py --check loom-code` exits non-zero after the plugin.json edit (mirror drift detected)
  - **GREEN**: same check exits 0; marketplace + CHANGELOG carry 0.75.0
- **Dependencies**: Tasks 9, 10, 11, 12, 13, 14, 15, 19 complete first
- **Independent**: false
- **Brief item covered**: "Four coupled changes, one loom-code version bump"
- **Status**: done(2ff18d58)
- **Gloss**: 版本與三面鏡射一次到位——沒有 bump，marketplace 更新就是靜默 no-op，全部改動等於沒出貨。

## Task 17 — `model: sonnet` frontmatter on code-quality-reviewer.md

- **Description**: In `loom-code/agents/code-quality-reviewer.md` frontmatter, insert the exact literal line `model: sonnet` immediately below the existing `description:` key. No other changes.
- **Module**: `loom-code/agents/code-quality-reviewer.md`
- **Files touched**: `loom-code/agents/code-quality-reviewer.md`
- **Context paths**:
  - `loom-code/agents/code-quality-reviewer.md`
- **Acceptance**:
  - **RED**: diagnostic — `grep -c "^model: sonnet" loom-code/agents/code-quality-reviewer.md` returns 0
  - **GREEN**: same grep returns 1, line sits inside the frontmatter block (durable pin lands in Task 18)
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical
- **Brief item covered**: "Claude Code: `model:` frontmatter in loom-code/agents/*.md — spec-reviewer / code-quality-reviewer / docs-reviewer → sonnet"
- **Status**: done(32587bb5)
- **Gloss**: code-quality-reviewer 臂的預設模型落地為 sonnet——與 Task 5 同型的一行機械插入。

## Task 18 — `model: sonnet` frontmatter on docs-reviewer.md + the five-file pin test

- **Description**: In `loom-code/agents/docs-reviewer.md` frontmatter, insert the exact literal line `model: sonnet` immediately below the existing `description:` key. Then author `loom-code/scripts/test_agent_model_frontmatter.py::test_checklist_arms_default_sonnet_judgment_arms_inherit` asserting: `model: sonnet` present in the frontmatter of exactly `spec-reviewer.md`, `code-quality-reviewer.md`, `docs-reviewer.md`; NO `model:` key in `implementer.md` or `code-reviewer.md` (they inherit — brief §3).
- **Module**: `loom-code/agents/docs-reviewer.md`
- **Files touched**: `loom-code/agents/docs-reviewer.md`, `loom-code/scripts/test_agent_model_frontmatter.py`
- **Context paths**:
  - `loom-code/agents/docs-reviewer.md`
  - `loom-code/agents/implementer.md`
  - `loom-code/agents/code-reviewer.md`
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_agent_model_frontmatter.py::test_checklist_arms_default_sonnet_judgment_arms_inherit` (new) fails
  - **GREEN**: test passes — three checklist arms carry the key, two judgment arms carry none
- **Dependencies**: Tasks 5, 17 complete first
- **Independent**: false
- **Brief item covered**: "spec-reviewer / code-quality-reviewer / docs-reviewer → sonnet; implementer + code-reviewer (whole-branch judgment) → unset (inherit)"
- **Status**: done(2b043aed)
- **Gloss**: 第三個臂補上預設值，並用一個測試把「三臂有、兩臂無」整組釘死——之後誰動 frontmatter 都會被抓。

## Task 19 — Rewrite convergence-contract.md to the single-round contract

- **Description**: Rewrite `loom-code/skills/requesting-docs-review/references/convergence-contract.md` (39 ln) to the single-round-with-confirmation contract, mirroring the SAME plan-authored contract text Task 9 installs in the SKILL.md (both derive from this plan's Task 9 Description item (c) — authoring source is the plan, so Task 9/19 ordering is not load-bearing): round 1 whole-artifact only full review; no gating findings → done (non-gating → debt, thresholds unchanged); gating verdict → fix → same-reviewer delta confirmation (CONFIRMED_RESOLVED / STILL_BLOCKING); STILL_BLOCKING after one fix cycle → STOP to user; terminal state "no gating findings"; session death before confirmation → one fresh single round. Delete the 2-round-cap + qualifying auto-delta-round machinery.
- **Module**: `loom-code/skills/requesting-docs-review/references/convergence-contract.md`
- **Files touched**: `loom-code/skills/requesting-docs-review/references/convergence-contract.md`
- **Context paths**:
  - `loom-code/skills/requesting-docs-review/references/convergence-contract.md`
  - `docs/loom/specs/2026-08-11-review-cost-reduction.md` (§2 loop shape)
- **Acceptance**:
  - **RED**: diagnostic — `grep -c "auto-delta" loom-code/skills/requesting-docs-review/references/convergence-contract.md` returns ≥1 (old machinery present)
  - **GREEN**: same grep returns 0; file states the single-round + confirmation contract incl. the "no gating findings" terminal state
- **Dependencies**: Task 8 completes first
- **Independent**: false  # doc-mirrors-doc with Task 9's SKILL.md contract text (shared authoring source in the plan)
- **Brief item covered**: "Consequences absorbed: the auto-delta third-round mechanism and most of convergence-contract.md become obsolete" (brief §2)
- **Status**: done(d57b1122)
- **Gloss**: 舊迴圈契約的參考檔整篇換成單輪確認制——不換掉它，SKILL.md 的新契約旁邊就躺著一份教人走老路的說明。

## Notes

- **Amendment note**: verdict stamped post-PASS (kind 1 — stamping the reviewer's already-returned verdict; no technical content changed). Stage flips are runtime ledger state.
- Kickoff decision: record-only push continuity mechanism → mechanically-validated exemption marker in loom_gate_markers.py (Task 14), not a guard-side path check — two-way door, Decision-Log tier.
- Kickoff decision: Codex per-agent toml delivery → documentation-only in codex-tools.md this arc; sync-script emission filed as PR-body debt (Task 4) — two-way door.
- Kickoff decision: M3 contract-file-count upgrade threshold → literal 10 (Task 12); admittedly arbitrary within a sane band, reversible — two-way door.
- Kickoff decision: 🟡 load-bearing sampling frame → all merged PRs since 2026-07-30 + gate-marker commits, STOP threshold >20% (Task 1) — two-way door.
- Kickoff sweep result: zero one-way-door decisions found (all mechanism changes are text-layer, git-revertible; the option-B scope itself was user-ratified at brief sign-off) — no §c briefing owed. Appetite read: no docs/loom/PRINCIPLES.md in this repo → default posture, nothing suppressed.
- **Attribution disclosure (shared-module staging race, execution record)**: commit `b23a5c0f` (Task 12) carries a third hunk beyond its declared scope — the extension of `test_sdd_prose_weight_record_class_scope` (two assertions: "spec-reviewer's verdict alone" / "N/A by construction"), which is Task 11's review-🔴 fix content, swept in by the in-place shared-checkout staging race on `test_review_scope_and_loop.py`. Disclosed in Task 11's fix commit `17954dd9` body and verified content-correct by Task 11's code-quality reviewer. Recorded here (and to be restated in the PR body) instead of amending/splitting `b23a5c0f`: rewriting stacked SHAs would break this ledger's `done(<sha>)` references and the review-trail commit citations (repo precedent: rebase orphans ledger SHAs).
- **Close-out duty (brief §What Becomes Obsolete, "at close-out")**: the finishing flow of THIS branch retires/shrinks three backlog entries: `2026-08-04-directive-1-does-not-say-what-follows-a-failed-authorized-round` (answered by the STOP rule), `2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session` (moot — no round-2 dispatch exists), `2026-08-04-out-of-scope-deferrals-have-no-durable-record` (partially retired; re-file the narrower contract-class remainder). Task 16's Description carries the pointer.
- **Change-folder detection (layer ii)**: two non-archived folders found (`2026-07-12-us-sec-primary-source-layer`, `2026-07-19-8k-prose-kpi-intake`); NOT bound — backlog entry `2026-07-26-loom-docs-two-stale-change-folders-belong-to-shipped-arcs` records both as shipped-arc residue (documented decision cited in lieu of asking). Input is the brainstorming brief only.
- **Plan-time decisions** (brief Open Questions resolved here): OQ1 → mechanically-validated exemption marker (Task 14); OQ2 → Codex toml documentation-only, emission filed as PR-body debt (Task 4); OQ3 → threshold literal 10 (Task 12; reversible, Decision-Log-grade — the exact number is admittedly arbitrary within a sane band, stated per honesty rubric); OQ4 → sampling frame = all merged PRs since 2026-07-30 (docs verdicts exist only after #629) + gate-marker commits (Task 1).
- **Classification glob SSOT chain**: the PLAN carries the authoring literal (Task 7's Description); shipped SSOT = rcr SKILL.md (Task 8); copies: docs-reviewer.md (Task 7, byte-equal — pinned by Task 13's cross-file lockstep assertion), gate-markers Python encoding (Task 14, doc-mirrors-code comment), SDD pointer (Task 11, point-don't-copy), carve-out qualifier (Task 13). The shared `test_review_scope_and_loop.py` module accumulates one pin function per file so partial cascades fail loudly.
- **Ratchet plan**: rcr cap 3935 → 4150 once (Tasks 8/12 cumulative, reason recorded); SDD 4175 → 4250 (Task 11, if net-positive); writing-plans 4099 → 4200 (DONE, Task 2); finishing must stay ≤4500 (CI CHK-SKL-010, no pin cap). Precedent: sanctioned raises 4023→4047→4099→4200.
- **Current contract governs this arc's own reviews**: PASS_WITH_NOTES auto-proceeds, 2+🟡 loops — and per the option-1 decision this now stays the contract permanently; only the loop SHAPE changes at 0.75.0.
- **OPTION-1 RESCOPE (2026-08-11, user decision)**: the 🟡-as-debt-at-any-count relaxation was DROPPED after Task 1's history-check tripped the plan's own STOP condition (14/14 load-bearing; audit `docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md`). Former Task 6 REMOVED from this plan (numbering keeps the gap deliberately — done-task references stay stable); aggregation thresholds ship UNCHANGED everywhere; the Goal line was updated as part of this user-ratified rescope (the Goal-freeze rule yields to an explicitly re-reviewed amendment, noted here for the cold reader).
- **Parallelism**: L1 leaves Tasks 1-5 + 17 all `Independent: true` (disjoint files, all DONE); L3 leaves Tasks 14/15 likewise; Tasks 9/10/11 stay sequential (`Independent: false` — they share `scripts/test_review_scope_and_loop.py`); Tasks 8→12 chain on the shared rcr file; Task 18 joins 5+17 (DONE); Task 7 joins 8+18; Task 13 joins 5/7/8/17; Task 16 joins all content tasks.
