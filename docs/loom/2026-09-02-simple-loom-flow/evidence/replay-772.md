# REQ-10 replay ②：PR #772（推導 replay，寫到 Task DAG 為止）

對象：`3ef8922a` "feat(loom-code): adversarial audit station — Step 3.5, attack
catalogue, signal command (0.109.0) (#772)"。
做法（W4-03 明定的 agent-decided 偏離）：寫出 intent 與 plan 的 Task DAG，**不 build**，
用 `replay-771.md` 實測校準的規則推算 commit／派工／決策點。
理由：#772 今天 67 個 commit 是站級新功能，真重建等於重做一個 change；而且舊機制在本 PR 已刪，
「今天的做法」無法在同一棵樹上對照。這個偏離會出現在盲跑報告的「我替你決定了」段。

素材：`git log -1 --format=%B 3ef8922a`（Summary／Test plan／Noted debt／Memory 齊全）
與 `git show --stat 3ef8922a`（45 檔、5056 insertions、39 deletions）。

## intent（新模型會寫成的樣子）

```
# 合併前先讓機器對這支 branch 自己動手打一次
originator: kouko
kind: engineering
needs-design: yes — 新增一個使用者會輸入的 CLI 子命令（signal）與它的四種結束碼，
                    且沒有既有 DESIGN.md 或 ui-flows 涵蓋這個表面
status: confirmed <date>

## Problem
三層審查（每 task 一次、批次一次、整支 branch 一次）都是「讀」。讀只找得到作者想像得到的洞。
loom 自己加的閘門一路被自己繞過：十一個 per-task 審查臂與兩輪批次審查放行的程式，
一次對抗審計就重現了七個繞法；補完那七個之後又有六個。而且 marketplace 從 main 出貨，
合併後才審計＝洞已經上線。

## Proposed outcome
在 close-out 流程裡加一個**條件觸發**的對抗站：一個可執行的命令算出這支 branch 的訊號
（plan 的標頭、被守衛路徑的命中、散文契約的命中），訊號亮了才派零上下文的對抗審計與冷讀者。
重現得出來的繞法會 STOP，直到有一個 RED 測試把它釘住。

## Acceptance
1. 我在一支「有守衛路徑改動」的 branch 上收尾時，機器會自己決定要不要開對抗審計，我不必記得。
2. 只在 plan 標頭寫「沒有安全考量」不能讓它閉嘴——只要動到被守衛的路徑，它照樣開。
3. 對抗審計重現得出來的每一個繞法，都有一個測試釘著它，而且清單裡指得到那個測試。
4. 這支 branch 自己要被它審過，而且審出來的東西要被修掉。

## Constraints
- 不加 git hook（`--no-verify` 有六種繞法）。
- 命令壞掉、清單壞掉、base 算不出來時一律 STOP，不得 fail-open。

## Open questions
- none
```

**決策點**：engineering ＝ 2（① intent 確認、③ 驗收）。
`needs-design: yes` 不會多開停點——② 是 product 專屬（spec REQ-1）；
engineering 的 spec 由 agent 決定，只過 review 站的 spec 鏡頭。
今天的實測也是 2（kickoff 的 ATTACK-CATALOGUE 命名 ＋ PR merge）。

## plan 的 Task DAG（16 個 task，3 個 wave）

task 數直接沿用原 SDD plan 的 16——新模型的 task 尺寸規則（能點名一個今天會失敗的測試、
只碰一個模組邊界）與舊 SDD 的「一個 failing test、≤1 module」是同一條，同樣的工作切出同樣的數目。

```
Wave 1 — 清單與檢查器（六個 task，彼此獨立）
  W1-01 store 語法與 check_attack_catalogue.py 的 parser      after: —
  W1-02 `pinned by` 解析：指到的測試必須存在                  after: W1-01
  W1-03 被守衛路徑的 glob 引擎                                after: W1-01
  W1-04 templates/ATTACK-CATALOGUE.md 與 loom_init 的 scaffold after: W1-01
  W1-05 plugin 層 attack-catalogue.md（六個類別）             after: —
  W1-06 check_contract_citations 對新路徑的放行               after: —

Wave 2 — signal 命令與 plan 標頭（六個 task）
  W2-01 signal：plan 標頭訊號                                 after: W1-01
  W2-02 signal：guarded-hits（含 merge-base 算不出來就 STOP） after: W1-03
  W2-03 signal：prose-hits                                    after: W1-03
  W2-04 signal：結束碼 0/1/2/3 的路由                         after: W2-01, W2-02, W2-03
  W2-05 plan_card.py 的 Safety-bearing: 標頭（五種壞寫法都要吵）after: —
  W2-06 plan_card.py Batch-CAS：全員替換被誤判成 finalize     after: —

Wave 3 — 站的散文與收尾（四個 task）
  W3-01 finishing SKILL.md 的 Step 3.5                        after: W2-04
  W3-02 adversarial-audit-packet.md（零上下文派工包）         after: W2-04
  W3-03 cold-reader-packet.md（一個情境、一個誘惑）           after: W2-04
  W3-04 code-reviewer 的 attack-class: 標記＋plan-format 文法   after: W2-05
  （版本 bump／CHANGELOG／CI 併進 W3-04 的收尾，不另開 task）

checkpoint：spec 鏡頭 1 次（needs-design: yes）＋ 三個 wave 尾各 1 次
（每個 wave 的 delta 都遠超過 8 檔／400 行；最後一次兼作 branch-end）＝ **4**，
build 期間 3 次，在 ≤5 的上限內。
```

## 推導

修紅數 F：#771 是 16 個 task 出 2 次；#772 的 diff 約三倍（5056 vs 792 行），取 **F = 3**。

| | W4-03 原規則 | 校準後規則（`replay-771.md` 末節） |
|---|---|---|
| commit | 16 ＋ 3 ＋ 4 ＝ **23** | 6 ＋ 16 ＋ 3 ＋ 9 ＋ 3 ＝ **37** |
| 派工 | 16 ＋ 4×4 ＝ **32** | 19 ＋ 16 ＝ **35** |
| 決策點 | **2** | **2** |

校準後 commit 的 6 ＝ intent 1 ＋ spec 1 ＋ review.json 建檔 1 ＋ spec checkpoint 2
（dispatch review、review-only；spec 的對抗是 red-team 閱讀，不落檔，所以少一個
checkpoint-artifacts commit）＋ plan 1。
9 ＝ 三個 build checkpoint × 3 個 commit。
派工的 19 ＝ 16 個計畫 task ＋ 3 個「落地本輪 regression 案例」task（每個 build checkpoint 一個）；
16 ＝ 四個 checkpoint × 4 個審查角色。

## 對照今天

| 欄 | 今天（實測） | v10 推導（校準後） | 通過？ |
|---|---|---|---|
| commit | 67 | **37** | ✓ |
| 派工 | 58 | **35** 全部／**16** 審查子集 | ✓（兩種定義都過） |
| 人類決策點 | 2 | **2** | ✓（持平） |

今天的 58 同樣只算審查派工（plan-review 8 輪＋task 級 fan-out 34＋whole-branch ≤12＋
站自審 2＋冷讀 1），不含 16 個 implementer；即使把 implementer 補進去（≈74），v10 的 35 仍較輕。
主要節省來自 §5 把「每 task 審＋每批次審＋whole-branch＋每次 DL 修訂重審」收成
四個 checkpoint：**task 級 fan-out 34 → 0**。
