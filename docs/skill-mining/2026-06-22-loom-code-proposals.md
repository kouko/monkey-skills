# loom-code skill-mining 提案（2026-06-22）

來源：distill-sessions Stage 1-3,挖舊名 `code-toolkit:*`（→ loom-code）的 8 條高 friction session
（4742d08c / c809d497 / a83bdc52 / 86e5835a / 854149d8 ×2 / 06e68673 / 3d998518）。
其餘 3 個 loom plugin（spec / interface-design / product-principles）在可見 transcript 裡零 session，無可挖證據。

每條 memory item 由獨立 Sonnet 4.6 subagent 對照「現在的」loom-code SKILL.md 產生（已剔除 session 當時存在、現已修掉的問題）。

---

## 跨 session 升級訊號（N≥2）

### ⭐ S1 — Bash 內容檢視不滿足 Read tool precondition（3 sessions）

最強訊號。同一個 root cause 在 3 條獨立 session、3 個不同情境重現：

| Session | 情境 | 形式 |
|---|---|---|
| 4742d08c | tdd-iron-law 直接批次 refactor 7 個 provider 檔 | `grep` 迴圈掃 → Edit（5 連續 "File has not been read yet"） |
| 86e5835a | SDD 後 scrub worktree | `sed -n` 預覽 4 檔 → Edit（4 連續同錯） |
| c809d497 | finishing rebase 衝突 | `cat` 看衝突 → Write（"File has been modified since read"） |

**現況**：規則只存在於 `subagent-driven-development` §Environment hygiene，且只列舉 `grep`/`jq`。
`sed`/`cat`/`head` 與「SDD 以外的直接路徑（tdd-iron-law / finishing）」都沒覆蓋。

**建議**：把規則措辭從「grep/jq」放寬為「**任何 Bash 檢視指令**（grep/jq/sed/cat/head…）—— precondition 是 tool 層級（Read tool，不是 shell stdout）」,並讓 tdd-iron-law 與 finishing-a-development-branch 也能取用同一條（見下方「結構建議」）。

### S2 — 與 dcg 安全 hook 對抗的 gotcha 群（≥2 sessions）

| 形式 | Session | 現況 |
|---|---|---|
| compound `git push && gh pr create` 觸發 "push to main" 守衛 | 4742d08c | SDD §Env hygiene 已記;finishing 未記 |
| `git checkout -- <files>` 被 dcg 擋（reset 部分產出） | 854149d8 | 未記 |
| commit message body 含 `shutil.rmtree` 等字串被 heredoc scanner 擋 → 改 `git commit -F` | 854149d8 | 未記 |
| `cd <subdir>` 在 Bash 持續 → 後續 git 相對路徑加倍 exit 128 | 06e68673 | 未記 |

---

## 依 skill 分組的全部 item

### loom-code:writing-plans

- **⭐ W1（verification-class，建議立即修）** `references/plan-document-reviewer-prompt.md` 的 Check 11 列舉文法是 `plan-format.md`（SSOT）的子集——漏了第四種合法形式 `"Tasks N, M complete first"`（多前置 sequential）。`plan-format.md` L57 與 `writing-plans/SKILL.md` L148 都有此語法。結果：同一 session 的 part 2/3/4 各被誤判 NEEDS_REVISION 一次（13/14,Check 11），各多一輪 rewrite+re-review。
  - 證據：events 121/125/128,reviewer 對 `"Tasks 2, 3, 4 complete first"` 判 "free-form dependency description"。
  - 修法:把 `"Tasks N, M complete first"` 加進 Check 11 合法形式,使 reviewer 文法與 SSOT 同步。
- **W2（success / 維持）** depth ceiling ≤5 正確驅動「拆成 N 個 brief-paired part 檔」而非單檔多 `## Part` 段落。負面範例措辭使路徑明確,值得保留。

### loom-code:subagent-driven-development（最密集）

- **B1（doc gap）** §Subagent capacity errors 把 "wait for capacity to recover" 列為選項,但沒寫**容量恢復後**要做什麼。本 session orchestrator 即興出正確 pattern（retrospective 補派 reviewer 到已 commit 的產物;NEEDS_REVISION → 新 fix commit 而非 revert）。建議把這段 resume 路徑寫進去。(events 298-306)
- **B2（workflow seam）** 全部 task DONE 後,orchestrator 問開放式 "what next?"(把 whole-branch review / push now 當平級選項),使用者得以繞過 finishing-a-development-branch 的 pre-push gate（含 data-leakage scan）。建議在 final-summary pause point 預設推薦 finishing-a-development-branch。finishing 那側已有對應 proactive trigger,SDD 這側該對齊。(events 309-311)
- **B3（harness）** `cd <subdir>` 在 Bash 持續 → 下個 git 相對路徑加倍 exit 128。(events 348/366)
- **B4（data-integrity，建議修）** parallel wave 中各 implementer 各自 `git add`,orchestrator 再 `git add <單檔>` commit 時,sibling 已 staged 的檔被一起帶進去 → 違反 per-task atomic commit。建議每次 wave 內 commit 前先 `git status --short` 確認只有該 task 檔。(events 372-374)
- **B5（harness/dcg）** reset 部分產出用 `git stash push -m`,不要用 `git checkout --`（被 dcg 擋）。(events 161-170)
- **B6（harness/dcg）** commit message body 含被擋字串 → 寫到 /tmp 用 `git commit -F`。(events 501-507)
- **B7（= S1）** Read-precondition 放寬到所有 Bash 檢視。(events 449-462)
- **B8（success / 維持+強化）** §Environment hygiene 的 `PYTHONDONTWRITEBYTECODE=1` 是 T2 R2 partial-fail 復原關鍵;建議強化:把該 env var 也傳進 implementer prompt（讓 implementer 跑 pytest 時用,不只 orchestrator）。
- **B9（success / 維持）** §Asking the user 的 `(Recommended)` + state anchor 內嵌於 `question` field,讓「warm-but-interrupted」使用者一次答完。兩處 checkpoint 都正確觸發。

### loom-code:tdd-iron-law

- **C1（= S1）** grep 掃多檔後直接 Edit 不滿足 Read precondition;此規則只在 SDD 有,tdd-iron-law 直接實作路徑沒有。應在 §Cross-skill contract 補一條（或共用 S1 的集中規則）。(events 174/181-191)

### loom-code:finishing-a-development-branch

- **D1（harness）** rebase 衝突解決用 `Read`+`Edit`,不要 `cat`+`Write`（後者 "File has been modified since read",因 rebase 在最後一次 Read 後又改了檔)。(events 529-540)
- **D2（= S2）** compound push+pr-create 觸發 dcg 守衛;SDD §Env hygiene 已有這句,應同樣出現在 finishing 的 push step。(events 1163-1167)

### loom-code:using-git-worktrees

- **E1（harness）** 重命名尚未 staged 的新檔用 `mv` 不是 `git mv`（後者 "not under version control"）。(events 107-110)

---

## Bitter-Lesson 分流（依使用者 two-kinds-of-scaffolding 原則）

> 留下「檢查模型輸出」的結構(verification-class),刪掉/集中「替模型思考」的結構(crutch-class)。

**A. Verification / design 類 — 值得直接修進 SKILL（持久價值）**
- W1（reviewer 文法 vs SSOT drift）← 真 bug,最高優先
- B1（capacity 恢復路徑 doc gap）
- B2（SDD→finishing workflow seam）
- B4（parallel-wave commit data-integrity）

**B. Harness / 工具機制類 — 真 friction 但 Bitter-Lesson 脆弱**
- S1/B7/C1（Read precondition）、S2/B3/B5/B6/D2（dcg + cwd）、D1（rebase）、E1（mv）

**關鍵觀察**:12 個 failure item 裡約 8 個是**同一類**——agent 在和 dcg 安全 hook、Read-tool precondition、bash cwd 對抗,且跨 session、跨 skill 重現。
與其把 8 條近重複警語散進 4 個 SKILL.md(drift 風險高、且 harness 一改就過時),更高槓桿的做法是**集中成一處** loom-code 共用的「environment / harness gotchas」reference(或併入 SDD §Environment hygiene 並以單一廣義陳述涵蓋),讓 router 指向它、可整塊刪除。這本身就是 Bitter-Lesson 取捨:這些是會衰減的 crutch,放一處、可刪。

---

## 建議下一步(供選擇)

1. **只修 A 類 4 項**(W1/B1/B2/B4)—— 持久、低爭議。其中 W1 是真 bug。
2. **A 類 + 把 B 類集中成一個 shared environment-gotchas reference** —— 解決跨 skill 重複,但需設計 reference 結構與 router 指向。
3. **全部不動,只留此文件** 當 backlog。

> 任何實際改 SKILL.md 的動作,走 loom-code pipeline(brainstorm→plan→SDD→review)。
