# Brief: loom-code skill-mining 修正落地

來源證據：`docs/skill-mining/2026-06-22-loom-code-proposals.md`（distill-sessions 挖 8 條舊 code-toolkit session）

## Problem

distill-sessions 從真實使用挖出 loom-code 的兩類缺陷：(1) 一個會誤判合法輸入的 reviewer bug + 兩個 workflow 缺口；(2) 一群「orchestrator 在和 harness（dcg hook / Read-tool precondition / bash cwd）對抗」的 gotcha，跨 3+ session、4+ skill 重現，且其中 Read-precondition 規則已在 2 個 skill 各存一份過窄副本。JTBD：讓 orchestrator 在執行 loom-code pipeline 時，**不再重蹈這些已知 friction**，且修法本身**不製造新的 SSOT drift**。

## Users

執行 loom-code pipeline 的 orchestrator agent（含本人 dogfood 時）。情境：跑 SDD / tdd-iron-law / finishing / worktrees 時，反覆撞上同一批 harness 行為，每次即興繞過、浪費 1-2 個 blocked-command round-trip。

## Smallest End State

A 類修進各自 SKILL；B 類集中成**單一** `using-loom-code/references/environment-gotchas.md`，各 skill 以**一行 pointer**指向，**不走 distribute/drift-gate**。

具體：
1. **W1（真 bug）** `skills/writing-plans/references/plan-document-reviewer-prompt.md` L43 Check 11 文法補 `"Tasks N, M complete first"`，與 `plan-format.md` L57（SSOT）對齊。
2. **B1** SDD L21 capacity-error 段：補「容量恢復後」resume 路徑（retrospective 補派 reviewer 到已 commit 產物；NEEDS_REVISION → 新 fix commit 非 revert）。
3. **B2** SDD §Continuous execution（final-summary pause point, L17）：補「預設推薦 finishing-a-development-branch」。
4. **B4** SDD §Environment hygiene（L114-120）：補一條「parallel wave 內每次 commit 前 `git status --short` 確認只 stage 該 task 檔」（SDD-specific，留在 SDD）。
5. **新檔** `skills/using-loom-code/references/environment-gotchas.md`，內容涵蓋：
   - Read-precondition：任何 Bash 檢視（grep/jq/sed/cat/head）不滿足 Edit/Write 的 Read precondition（S1）
   - dcg：compound push+pr → 分兩次呼叫；`git checkout --` 被擋 → `git stash push`；commit body 含被擋字串 → `git commit -F /tmp/file`（S2）
   - bash cwd：`cd <subdir>` 會持續 → git 用絕對路徑或 `cd <repo-root> &&`（B3）
   - rebase 衝突：`Read`+`Edit`，非 `cat`+`Write`（D1）
   - 檔案改名：未 staged 的檔用 `mv` 非 `git mv`（E1）
6. **Pointer**（各一行，指向新 ref）：SDD（把 L112 grep/jq 措辭放寬為「任何 Bash 檢視」+ 指向 ref）、tdd-iron-law、finishing-a-development-branch、using-git-worktrees；並在 using-loom-code §Reference 清單登錄新檔。

## Current State Evidence

- **Forward（誰會讀到）**：orchestrator 執行 SDD/tdd/finishing/worktrees 時讀 SKILL.md body。新 ref 由 pointer 觸發讀取。
- **Reverse（SSOT 歸屬，已 Read `scripts/distribute.py`）**：`distribute.py` 只負責把 `domain-teams/code-team` 的 standards/rubrics/checklists 同步成 loom-code 內 byte-identical 副本（`verify-drift.py` 把關）。`_baseline.md` 是**嵌入 agent prompt** 的 SSOT。`using-loom-code/references/{continuous-mode,engineering-baselines,claude-code-tools,codex-tools}.md` 是**單一檔、orchestrator 閱讀型**、不經 distribute。→ environment-gotchas 屬後者，**單一檔 + 多 pointer**，不進 distribute ROUTE。
- **Error（現況痛點）**：`skills/subagent-driven-development/SKILL.md:112` Read-precondition 只列 `grep`/`jq`；`skills/finishing-a-development-branch/SKILL.md` 另存一份 read-precondition 字句 → 已雙重、措辭過窄、未及 tdd-iron-law。
- **Data**：`writing-plans/references/plan-format.md:57` = dependency 文法 SSOT（4 形式）；`plan-document-reviewer-prompt.md:43` Check 11 = 子集（3 形式）→ drift bug。
- **Boundary**：tdd-iron-law **無** §Cross-skill contract heading（proposal 引用的 anchor 不存在）→ pointer 改放既有 §See also 或 §Red-Green-Refactor 附近。SDD §Environment hygiene 是**粗體段非 `##` heading**。
- Evidence paths：`loom-code/scripts/distribute.py`、`loom-code/skills/using-loom-code/references/`、`loom-code/skills/subagent-driven-development/SKILL.md:21,112,114`、`loom-code/skills/writing-plans/references/{plan-format.md:57,plan-document-reviewer-prompt.md:43}`、`loom-code/skills/finishing-a-development-branch/SKILL.md:126`、`loom-code/skills/using-git-worktrees/SKILL.md:42`、`loom-code/skills/tdd-iron-law/SKILL.md`。

## 引用路徑穩定性研究（2026-06 補，回應「Plugin 是單位但確保路徑穩定」）

業界查證 — Anthropic 官方 skill 文件範例是「從 skill root 相對引用」`./references/FILE.md`（[Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)、[Claude Code Docs](https://code.claude.com/docs/en/skills)）；JA 提出 [symlink 共用法](https://zenn.dev/atamaplus/articles/6d8c3615ff3f33)（實體一處、各 skill 放連結）。

repo 內證據（決定性）：`../sibling-skill/references|rubrics|checklists/*.md` 形式**已用 30+ 次**（`requesting-code-review`→SDD 的 standards/rubrics/checklists；`writing-plans`→`brainstorming/references/handoff-brief-format.md`）。安裝快取每個版本（0.17/0.18/0.19）各是一棵完整樹，`../sibling/` 永遠落在同一 version dir → intra-plugin 相對路徑穩定。symlink 在 repo **零先例**（git/打包/Windows/folder-hook 皆未測）→ 否決。

**穩定性結論**：沿用已驗證的 `../sibling/references/` 慣例（不發明 symlink）；**真正缺口是 repo 無「跨引用連結存活檢查」**（`scripts/check-*.py` 家族有結構/drift 檢查，無 dead-link 檢查）→ 補一個 link-existence validator，把「靠慣例穩定」升級為「CI 把關穩定」，順帶保護現有 30+ 條跨引用。

## Decision

**會做**：W1 reviewer 文法修正；B1/B2/B4 SDD 三處補強；新增單一 `skills/using-loom-code/references/environment-gotchas.md`（與 continuous-mode.md 同位，涵蓋 S1/S2/B3/D1/E1）；5 處 pointer（SDD/tdd-iron-law/finishing/using-git-worktrees → `../using-loom-code/references/environment-gotchas.md`）+ using-loom-code §Reference 清單登錄；SDD L112 與 finishing 的過窄 read-precondition 措辭放寬並改為指向共用 ref（消除雙重）；**新增 `loom-code/scripts/check-skill-crossrefs.py`**——走訪每個 SKILL.md 的相對連結、斷言目標檔存在（exit 非 0 即失敗），加進 CI，確保此次新增 pointer 與既有 30+ 跨引用永不靜默斷裂。

**不會做**：不把 environment-gotchas 納入 `distribute.py`/drift-gate（它非 agent-prompt 嵌入內容）；不改 dcg hook 本身；不動 domain-teams canonical 層；不把 success 類（W2/B8/B9）改成新規則（它們是「維持現狀」，至多 B8 把 PYTHONDONTWRITEBYTECODE 也傳進 implementer prompt——列 Open Question）。

設計依據：environment-gotchas 沿用 `using-loom-code/references/` 既有「單一檔、orchestrator 閱讀型、跨切面」先例（continuous-mode.md / engineering-baselines.md），**單一來源 + 多 pointer** 從根本避開 synced-SSOT drift。

## Alternatives Considered

業界查證（WebSearch EN+JA，2026-06）— 主題：跨模組共用文件如何避免 drift。

EN 共識（DRY/SSOT 文件原則）：「每則知識在系統內須有單一、權威表述」；落地法明確 = **建立一份主文件，其他文件連回它**，「不要把同一份文件複製到多個檔」（[Secoda](https://www.secoda.co/glossary/dry-dont-repeat-yourself)、[Webel](https://www.webel.com.au/node/889)、[Faros](https://www.faros.ai/blog/ai-generated-code-and-the-dry-principle)）。Caveat：單一來源會帶來耦合，需衡量。
JA 共識（[Atlassian JA](https://www.atlassian.com/ja/work-management/knowledge-sharing/documentation/building-a-single-source-of-truth-ssot-for-your-team)、[Zenn Docs-as-Code](https://zenn.dev/dajiaji/articles/24086666031199)）：監査既有文件→把重複/矛盾**統合成一份**；Docs-as-Code 於 monorepo 一元管理。值得注意 [contextlint](https://zenn.dev/nozomi_cobo/articles/contextlint-introduction)：若仍選擇複製，需要一個「文件間一致性驗證工具」——這正對應 Option B 的 `verify-drift.py` 成本。
EN↔JA **無分歧**：single-source + reference 勝；複製則必須配一致性 gate（額外成本）。

- **(A) 單一檔 + pointer〔選〕**：一處內容、多處一行指向。零 drift（單一來源），符合 using-loom-code/references 既有先例，**正是 EN/JA 查證共識的「主文件+連回」做法**。Cons：跨 skill 相對路徑引用 + 輕度耦合（但 repo 內 SKILL 互引 `../sibling/SKILL.md` 已是常態）。
- **(B) SSOT in scripts/_*.md + distribute 成各 skill 副本**：沿用 baseline 機制。Cons：即「複製 + 一致性 gate」路線（業界視為次選，需 contextlint/verify-drift 類工具背書）；drift-gate + ROUTE 手維護；且該機制是為「嵌入 agent prompt」設計，這裡是 orchestrator 閱讀型 → 過度工程。
- **(C) 各 skill inline 各自補**：最直接。Cons：直接違反 DRY/SSOT；正是現在 read-precondition 雙重副本 + drift 的成因，被證據+查證雙否決。

**My take**：Recommend (A)。Why：EN+JA 查證一致指向「單一主文件 + 連回」，且 repo 已有 using-loom-code/references 同型先例，耦合成本最低、零 drift。Conditional reversal：若未來 environment-gotchas 需被**嵌入 agent system prompt**（如 baseline 那樣每個 subagent 都要內帶），才改走 (B) 的 distribute 機制。

## Out of Scope

- spec / interface-design / product-principles 三 plugin（零 session 證據）。
- success 類 W2/B9（維持現狀，不需改）。
- dcg hook / Read-tool precondition 等 harness 行為本身的修改。
- 把 environment-gotchas 反向推廣到 domain-teams 或其他 plugin。

## What Becomes Obsolete

- SDD L112 的「grep/jq」窄列舉 → 放寬措辭並由 pointer 取代細節。
- finishing 內重複的 read-precondition 字句 → 收斂為指向共用 ref。

## Open Questions

- B8：是否同時把 `PYTHONDONTWRITEBYTECODE=1` 寫進 implementer prompt 模板（讓 implementer 跑 pytest 也帶）？屬 success-強化，可併入或留待。
- tdd-iron-law pointer 放哪個既有 section 最自然（§See also vs §Red-Green-Refactor 尾）？實作時定。
