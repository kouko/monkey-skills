> REQ-9 正式驗收（W4-01，2026-09-03）：fresh sonnet 只讀 capture-intent/SKILL.md＋references/，開檔 2，猜測 0，約 1–2 分鐘。

# Cold Read — REQ-9 Task B（capture-intent，未見過 loom）

閱讀範圍：僅 `loom-design/skills/capture-intent/SKILL.md` 及其相對連結
`references/interview.md`。無其他檔案、無指令、無 subagent。

開始時間：2026-09-02 21:08:53
結束時間：2026-09-02 21:09:57（讀檔階段；含寫檔總耗時見第 8 節）

---

## 1. 產生哪些檔（順序、確切路徑、change-id）

change-id 取法：`<YYYY-MM-DD>-<slug>`，日期＝開工當日。SKILL.md 第 22–24
行給的 worked example 剛好就是這個題目本身：

> for "CLI todo gains a due date" started on 2026-09-02,
> `2026-09-02-cli-todo-due-date`.

所以 change-id = `2026-09-02-cli-todo-due-date`（假設今天就是開工日
2026-09-02，這是環境日期，非我猜測）。

依 SKILL.md 步驟順序，capture-intent 這一站會產生／更動：

1. `docs/loom/intent/2026-09-02-cli-todo-due-date.md`
   — Step 2 先寫 `status: open`；Step 4「使用者答 yes」後改寫為
   `status: confirmed <date>`。
2. `PRINCIPLES.md`（repo 根目錄）— **會產生**。理由：Task B 是
   `kind: product`（CLI 使用者輸入/輸出的行為改變），且題目明講
   「無 PRINCIPLES.md」。Step 3 執行 `standing` checker 時會撞上
   `standing.product-principles-reject`（product + 無 ratified
   PRINCIPLES.md → 擋）。撞到後，本站必須**當場**（同一次對話內）跑
   `loom-code` 的 `PRINCIPLES-interview.md`，寫出 `PRINCIPLES.md`，
   `ratified-by:` 先留空；使用者在 Step 4 答 yes 後才補上
   `ratified-by: <name> <date>`。
3. Git commit：訊息 `docs(loom): intent 2026-09-02-cli-todo-due-date
   confirmed`，commit body 必須逐字含 `needs-design:` 那一行（checker
   會做字元級比對）。
4. `docs/loom/KICKOFF-DEFAULTS.md` — **條件式，不確定會不會產生**（見
   第 7 節）。SKILL.md 297–287 行：只有在（本檔尚無 `second-vendor:`
   行 **且** 偵測到非本 host 廠商的第二方 CLI 存在且 `--version` 可跑
   通）時才會問使用者、才會寫這個檔。題目只講「Host: Claude Code，
   loom-design 與 loom-code 已裝」，沒講這台機器有沒有裝 `codex` 或
   `gemini` CLI——這是 runtime 探測結果，SKILL.md 本身沒有回答，所以
   我不猜是否產生。
5. `DESIGN.md` — **不會**在 capture-intent 這一站產生。表格把它列為
   `capture-intent` artifact 欄的「side output」，但那是指它呼叫的
   下游工具的輸出；本站自己的步驟（Step 0–5）完全沒有寫
   `DESIGN.md` 的動作。Task B 因為 `needs-design: yes`，Step 5 會把
   change 交給 `loom-design:write-spec`，`DESIGN.md` 若要出現，是在
   那一站（本站看不到的地方）才會發生。

## 2. 誰決定什麼

**Decision point ①**（Step 4，capture-intent 本站，唯一一次停下）：
一則訊息裡合併問完，原句：

> 你要的是 ___，做完後你可以 ___、___、___。對嗎？

同一則訊息還會附：
- 目前找到的 one-way doors（consequence 形式，例如「Option A: 之後只能
  跑在 ___，每月花 ___，換掉要重寫 ___」）——Task B 本身沒有明顯的框架
  /付費服務/資料格式改動，SKILL.md 也沒替我判定 Task B 會不會冒出
  one-way door（例如既有 todo 儲存格式若要改動以塞入 due date，可能
  觸發 class (c)/(e)），這要靠訪談當場判斷，本檔不預先給答案。
- 第二方審查者建議（至多問一次，見第 3、7 節條件）。
- 若 Step 3 觸發了 PRINCIPLES 訪談，principles 確認也併入同一則訊息。

**Decision point ②**：不在本站。發生在 `write-spec`（Task B 因
`needs-design: yes` 會被交去那一站），原句形式：「你打 ___ 你看到
___」，只問 product 類（Task B 是 product，所以適用）。

**Decision point ③**：不在本站，發生在 `ship`，使用者讀 blind-run
report 後說 OK / not OK。

**agent-decided 的點**：
- `needs-design:` 的初判由本站 agent 依規則 (a)/(b) 自己決定並寫下理由
  句，**使用者不被問**；但 checker 之後會用
  `intent.needs-design-recompute` 重算校驗，agent 沒有最終話語權。
- `write-plan` 站：`agent-decided`（若 loom-design 不存在則它自己補跑
  decision point ①，但本題 loom-design 已裝，所以不會）。
- `build` 站：`agent-decided`。
- one-way door 的分類（四道閘 check/measure/threshold/merge）由本站
  agent 執行，只有「未被 Constraints/PRINCIPLES.md 釘住」的才真的問
  使用者；已釘住的只用 consequence 形式告知，不停下問。

## 3. 哪個 checker 在何時擋（指令與 rule id）

- **Step 0**：
  `python3 <loom-code>/scripts/loom_checker.py contract --require 1.0`
  — rule `contract.requires`。非 exit 0 → 印出 checker 訊息、要求使用者
  更新 `loom-code`、**停**，不可繞過或亂猜路徑。
- **Step 3**：
  `python3 <loom-code>/scripts/loom_checker.py standing docs/loom/intent/2026-09-02-cli-todo-due-date.md`
  — 這裡 Task B 會撞上 **`standing.product-principles-reject`**（唯一
  會擋的 standing 結果）：`kind: product` 且無 ratified
  `PRINCIPLES.md` → 擋，逼出 PRINCIPLES 訪談。其餘 WARN 只逐字印出，
  不擋。
- **Step 4（yes 之後的驗證）**：
  `python3 <loom-code>/scripts/loom_checker.py intent docs/loom/intent/2026-09-02-cli-todo-due-date.md`
  — 檢查 `intent.schema`、`intent.product-no-identifiers`、
  `intent.needs-design-reason`、`intent.needs-design-recompute`。非
  exit 0 就照 checker 指名的問題修，重跑到 exit 0。

（表格另列了 write-spec/write-plan/build/review/ship/maintain 各自的
checker，但那些不在 capture-intent 這一站的執行範圍內，只是路線圖。）

## 4. 審查何時跑、review.json 誰建、哪一站跑決策點②

`review.json` **不是**由 capture-intent 產生，也不在本站的時間軸內。
依表格，`review.json`（連同 `blind-run-report.md`）是 **review 站**的
artifact，由「兩個以上 fresh-context reviewers（不平均）」決定內容，
在 build 之後才跑。

Decision point ② 在 **write-spec** 站跑（product 類必經），不是 review
站；write-spec 也是 capture-intent Step 5 因 `needs-design: yes` 而
交棒的下一站。

本站唯一留給 review 的東西：Step 4 要求把訪談時問過的每個問題記成
`{decision_point, text, type}`，在 Step 5 的 hand-off 訊息裡逐字傳給
下一站（寫入 plan 的 `## Questions asked`），之後在 review 第一個
checkpoint 時被複製進 `review.json` 的 `questions[]`。capture-intent
本身完全不碰 `review.json`。

## 5. needs-design 的判定與依據句

規則 (a)：改動了使用者讀/打的介面（GUI/TUI/CLI 參數與輸出/外部 API），
且沒有既有 `DESIGN.md` 或 ui-flows 文件涵蓋該介面。

Task B 完全對應 SKILL.md 162–165 行給的逐字 worked example（本題就是
照抄這個例子出的）：

> Worked example — "CLI todo gains a due date": adding a due date
> changes the arguments the user types and the list they read back, and
> no ui-flows document covers due dates, so (a) holds →
> `needs-design: yes — CLI surface changes, no ui-flows cover due
> dates`.

所以 intent 檔會寫：
`needs-design: yes — CLI surface changes, no ui-flows cover due dates`。

## 6. 工作在哪個分支

**本檔沒有回答這一題**。capture-intent 全程（Step 0–5）沒有任何建立
或切換 git 分支的動作，只在 Step 4「使用者答 yes」後做**一次 commit**
（訊息 `docs(loom): intent <change-id> confirmed`），但沒說這個 commit
落在哪個分支上——沒有 `git checkout -b` 或類似指令。表格裡 build 站的
artifact 欄提到「commits on **the change branch**」，暗示到 build 站時
已經有一個「change branch」存在，但誰、在哪一步建立它，capture-intent
這份文件完全沒交代。因此答案是：**不明——本站文件未定義**，不是我能從
這份檔案推出的資訊。

## 7. 猜測清單（目標零）

零個無依據猜測。以下三點是**明確標記為「本檔未回答／待 runtime 決定」**
的項目，不是我替它們填答案：

1. `docs/loom/KICKOFF-DEFAULTS.md` 是否被建立——取決於這台機器是否裝有
   `codex`/`gemini` 這類非本 host 廠商 CLI，且 `<cli> --version` 能
   exit 0；題目沒給這項資訊，SKILL.md 也沒替我假設，我沒有猜。
2. Task B 是否含 one-way door（例如既有 todo 儲存格式改動）——SKILL.md
   要求訪談當場判定，不是文件裡預先寫死的答案，我沒有替它編一個。
3. commit 落在哪個分支——如第 6 節，本檔未定義，我標記為未知而非猜測。
4. `originator:` 欄要填的使用者名字——題目沒給使用者名字，SKILL.md 只
   說填「the user's name」，我沒有杜撰一個。

## 8. 開檔數與耗時

開檔數：**2**（`SKILL.md` + `references/interview.md`；另有一次
`ls` 目錄列表，不算開檔）。

耗時：讀檔＋分析階段 21:08:53 → 21:09:57，約 **1 分鐘**；含撰寫本回答
檔案的總耗時約 **2 分鐘**。
