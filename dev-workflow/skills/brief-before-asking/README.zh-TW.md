# Brief Before Asking

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Agent 在任何非簡單 engineering decision question **之前**（或
> 作為直接回應）交付的 6 block 結構化簡報。Mental Model 領銜 —
> 在任何 code reference 或 metric 之前先建立 plain-English 的
> abstraction bridge。User 可以在幾秒內讀完、push back 或確認 —
> 不用從零開始反推 agent 在問什麼。

主動觸發的 **agent 端 skill**：當 Claude 即將就複雜的 engineering
decision（race condition、perf bottleneck、refactor 方向、tech
selection、bug root cause）詢問 user 時，此 skill 強制 6 block
簡報結構 — 防止 Claude 預設掉進零 context 的 yes/no（「OK to
proceed?」）或 jargon 先行的 technical dump。當 user 對 *問題*
（Mode B）或 *說明*（Mode C）表達困惑時也會反應式啟動。

本 README 給在 GitHub 上閱讀的人類。Claude 實際載入的 operational
檔案是 [`SKILL.md`](SKILL.md)。

---

## 為什麼存在這個 skill？

反覆出現的失敗模式 **不是** 「agent 講太少」也不是「agent 講太
多」。幾乎都是 **agent 從錯誤的 abstraction level 起頭**。Claude
預設掉進帶 jargon 的 implementation-level 細節。User 需要從
business semantics 的 system-level 理解起頭。沒有 bridge，再多
細節都無法落地 — 細節越多 gap 越大。

目前的 6 block + 3 mode 設計是經過 **4 次迭代** 才落定。每次前次
迭代修正了不同的失敗模式，但都漏掉 abstraction bridge 這個問題。
完整故事見 [`references/DESIGN.md`](references/DESIGN.md)。
短版：

| 迭代 | 嘗試的設計 | 為何失敗 |
|---|---|---|
| **1** | 堆 SCQA + MECE + LLM-bias defense + human-bias alert（8 程序步驟）| Ceremony 壓過 value。在抵達實際內容前產生 ~1500 token 的結構性 overhead。「Framework stack」感覺嚴謹；產生的是 ritual。 |
| **2** | 5 欄位 "Minimum Viable Question"（Where / Fork / Options / Default / Escape）+ 4 階 stakes calibration | 誤讀實際痛點。為高頻低 stakes 的 fork 而設計。真痛點是真正複雜的 fork，沒有乾淨的 default。 |
| **3** | 5 block briefing（Situation / Why-this-fork / Options / My take / Open ends）+ 嚴格 depth rules | 從錯的 abstraction level 起頭。Situation block 要求 code refs 與 metrics，但這些只有在 user 已知「ref 住在系統哪裡」時才能落地。 |
| **4**（現在）| 6 block + **Mental Model** 領銜 + 3 trigger mode（Proactive / Reactive-on-Question / Reactive-on-Explanation）| Mental Model 直接對應 abstraction-level mismatch。迭代 3 的 depth rules 保留給 block 2-6。Mode C 收住「解釋很長但仍困惑」這個迭代 1-3 全部漏掉的失敗。 |

姍姍來遲的核心 insight：**abstraction-level matching 勝過 word
count**。Plain English 2 句的 Mental Model 解鎖 200 行 technical
detail。沒有它，200 行只會把困惑加深。

---

## 它如何運作？

### 3 個 trigger mode

| Mode | 觸發條件 | 輸出形態 |
|---|---|---|
| **A — Proactive** | Agent 自我偵測「我正要就一個非自明 decision 問 user」| 完整 6 block briefing → 以 specific request 結尾 |
| **B — Reactive on Question** | User 訊號顯示沒看懂 *問題*（「我不懂」「沒頭沒尾」"clarify"）| Bridge → 完整 6 block briefing → **以 briefing-grounded 的具體形重問原問題** |
| **C — Reactive on Explanation** | User 訊號顯示沒跟上 *說明*（「跟不上」「太多術語」"ELI5" "in plain English"）| Bridge → **僅 Mental Model block** + 定義前一輪的 jargon → **暫停** 問 user 要往哪鑽 |

Mode C 在結構上跟 Mode B 不同。User 已經在 jargon 裡溺過一次 —
再丟 6 個 block 只會再溺一次，重排順序也一樣。修正是先讓 Mental
Model 落地，再讓 user 自己選 drill 方向。

### 6 個 block

```
Mental Model     1-2 句 plain-English：系統哪一塊 + 為何重要（無 jargon）
Situation        Technical state：code refs、metrics、做過的 investigation
Why-this-fork    Trigger 條件 + constraint + 沒問會發生什麼
Options          2-4 個 real option 含 depth（具體 diff、非抽象 pros/cons）
My take          Lean（A/B/C）+ ≥3 步 reasoning chain + conditional reversal
Open ends        Agent 不知道的事 / 會 flip 答案的條件 / 需 user value call 的事
```

每個 block 有自己的 depth 要求與 forbidden pattern。完整 ruleset
在 [`SKILL.md`](SKILL.md)；短版：

- **Mental Model** — 無 code refs、無 metric、無未定義 jargon。必須回答「系統哪一塊」（用 business semantics）與「user 視角為何重要」。Inline 定義或 flag 任何 user 可能不熟的 term。
- **Situation** — ≥1 code ref（filename:lineno）、≥1 quantitative metric、做過的 investigation。禁：「looks complex」/「seems slow」。
- **Why-this-fork** — trigger（為何現在問）、constraint（為何 agent 不能單獨決定）、不問的 cost。
- **Options** — 最少 2 個、最多 4 個、等深度對待（禁「A 5 行、B 1 行」）。每個 option 要 concrete approach、quantitative impact、trade-off、reversibility（two-way vs one-way door）、downstream implications。禁：「simpler」/「modern」/「industry standard」。
- **My take** — 明確 lean（A / B / C）、≥3 因果步的 reasoning chain、conditional reversal（「但若 X 成立則 switch 到 Y」）。禁：「either works」/「your call」/「no preference」（agent 讀過 code；裝中立是說謊）。
- **Open ends** — agent 缺的 context（user 持有的 info）、會 flip 答案的條件、需 user value judgement 的事。禁：「need more context」（含糊）、agent 自己能答的 fake question、disclaimer fluff。

### Mental Model First（承重的 insight）

每個 agent 都想跳過的 block。讓其他所有東西能落地的 block。
「before」失敗模式長這樣：

> ❌ "OrderService has a race condition under high concurrency and needs idempotency."
> （3 個 jargon、零 plain English、無系統定位。）

「after」長這樣：

> ✅ "This is the async 'deduct inventory after checkout' flow: once an order is written, a message is sent to InventoryService to deduct stock. Problem: the same message sometimes gets processed twice, causing the same order to deduct stock twice (oversells)."
> （Business semantics、無 jargon、後果可抓住。）

Agent 仍然得談 race condition、saga pattern、idempotency key —
但這些落地在 Situation / Options / My take，在 user 拿到地圖之後。

---

## Worked Example（Mode A、壓縮版）

**設定**：agent 即將就一個慢的 orders-list endpoint 的
index-vs-pagination refactor 問 user。

> **Mental Model**：我們的 orders-list 頁慢，是因為 database 在掃每一列，而不是直接跳到近期 pending 的那幾列。
>
> **Situation**：`OrderRepository.findRecentPending`（orders.ts:142）prod p95 = 12s；orders table 4.2M 列；只有 PK index；`EXPLAIN` 顯示 Seq Scan。
>
> **Why-this-fork**：明天 deploy window；index 選擇限制 Q2 要加的 2 個 mirror table。
>
> **Options**：
> - **A.** Composite index `(status, created_at DESC)` — 320 MB storage / read p95 → <100 ms / two-way door。
> - **B.** `created_at` 上的 cursor pagination — query rewrite ~40 行 / 0 storage / one-way door（API contract change）。
>
> **My take**：傾向 **A**。(1) Deploy 壓力有利 low-blast-radius；(2) 使用 log 顯示 read-heavy access pattern 6+ 個月穩定；(3) 320 MB storage cost 對比 API contract churn 微不足道。**但若** orders-list endpoint 反正 Q3 要被 deprecate，B 的 one-way-door cost 就消失 — 改成 B。
>
> **Open ends**：Q3 deprecation timeline 確認了？Dev DB storage ceiling？Contract-stability vs storage 的 trade-off 看你的 call。

User 現在可 (a) 確認 A、(b) 提供 deprecation timeline 後 flip 到
B、(c) 對某個具體數字 push back — 3 種回應，都比從零反推問題快。

Worked Mode C example（saga / outbox、ELI5）在
[`references/EXAMPLES.md`](references/EXAMPLES.md)。

---

## 何時該使用？

### Trigger（agent 端）

- **Mode A — Proactive**：agent 即將就非自明 decision 問 user：
  race condition、perf bottleneck、service boundary change、
  refactor 方向、tech selection、bug root cause。
- **Mode B — Reactive on Question**：user 說「我不懂」「看不懂」
  「不理解」「什麼意思」「你在問什麼」「沒頭沒尾」「資訊太少」
  「給我完整脈絡」/「I don't understand」/「clarify」/「what?」。
- **Mode C — Reactive on Explanation**：user 說「我跟不上」
  「太多術語」「能不能簡單講」「降低 level」「我需要 mental
  model」/「I'm lost」/「ELI5」/「in plain English」/「too much
  jargon」/「where in the system are we」。

長解釋後曖昧的「more context」/「補充一下」預設為 **Mode C**
（較安全，因為 Mode C 會 pause）。

### 在以下情境**不**使用…

- **Trivial decision** — 私有 code 命名、formatting、log level、
  ≤5 行、可逆、無 public-API surface 變動。直接做；註記選擇。
- **純 factual query** — 「X 是什麼」/ "what is X"。直接答。
- **User 已經明說「just decide, don't ask」** — trivial-ize、
  直接做、在 commit/response 註記選擇。
- **已在 cross-team architecture review mode** — 升到更重的
  framework（Minto SCQA / formal RFC）。brief-before-asking 是
  個別複雜 decision 的 **daily middleweight**，不是 cross-team
  consultation 的 heavyweight。

---

## 差異化

### vs SCQA / Minto Pyramid

SCQA 以 Situation → Complication → Question → Answer 開場。
適合 consulting report。對 engineering decision 偏弱 — user 可能
沒有 parse Situation 的前置 context。**brief-before-asking 在前
面加 Mental Model** — 讓 Situation 能落地的 plain-English
abstraction bridge。其餘結構類似。SCQA 風格的 heavyweight review
仍有其位置；brief-before-asking 是 middleweight 預設，user 要求
（"give me the full analysis"）時升到 SCQA。

### vs 簡單的「ask before doing」

樸素的「ask before doing」會產生零 context 的 yes/no 問題
（"Should we proceed?" / "OK to refactor?"）。User 被迫在回答前
反推 agent 的 reasoning。6 block 結構強迫 agent 把已知的攤開來 —
user 拿到的是 briefing-grounded 的提問，不是猜謎遊戲。

### vs `superpowers:brainstorming`

Brainstorming 是 **task-start ideation** — 不知道要做什麼時打開
option space。brief-before-asking 是 **task-progress decision** —
做完工作需要 fork 解決時收斂 option space。不同 phase、不同形態。

### vs `dev-workflow:proposal-critique`

Proposal-critique 是對既有 list 或 plan 的 one-shot KEEP /
DEFER / DROP triage。brief-before-asking 開啟一個 decision；
不 critique。兩者可組合：agent 用 brief-before-asking surface 出
decision，若 options list 太長則 user 用 proposal-critique。

---

## 反模式

跨 block / 跨 mode 的失敗模式（per-block 反模式在 [`SKILL.md`](SKILL.md)
各 block 章節）：

- **跳過 Mental Model 直奔 Situation** — 殺掉 abstraction
  bridge。最致命的失敗模式。
- **零 context yes/no**："Should we proceed?" / "OK?" — 沒有
  block 承重。
- **沒 reasoning 的結論先行**："I recommend Redis, OK?" — 6
  block 被壓縮成 1 個提問。
- **多個 fork 綁進同一份 briefing** — 一份 briefing 一個 fork；
  3 個 fork 就交付 3 份 briefing。
- **觸發 Mode C 卻 dump 完整 6 block 而非 pause** — 把 user 再
  淹一次。Mode C 結構上不同是有意的。
- **表演式中立**："Both options have merit" — agent 讀過 code，
  有 lean；裝中立是說謊。"My take" block 就是為了強迫誠實。

---

## 它與其他 skill 的關係？

- **`dev-workflow:complexity-critique`** — one-shot deletion-first
  gate。正交 — 對單一 proposal 的 critique，不是對 decision 的
  briefing。
- **`dev-workflow:proposal-critique`** — 對既有 list / plan 的
  triage。當 brief-before-asking 產出的 Options list 本身太長時
  下游組合使用。
- **`skill-dev-toolkit:skill-creator-advance`** — 用來迭代此 skill
  （test-prompts.json + eval loop）。
- **`superpowers:brainstorming`** — task-start ideation；
  brief-before-asking 是 task-progress decision。
- **`superpowers:verification-before-completion`** — task-finish
  evidence；brief-before-asking 是 task-progress decision。

---

## Pre-shipped — 此為 v1.0 draft

| Phase | 狀態 |
|---|---|
| **Phase 1 — 設計** | 完成。4 次迭代記錄於 [`references/DESIGN.md`](references/DESIGN.md)。 |
| **Phase 2 — SKILL.md 撰寫** | 完成。6 block + 3 mode 結構、各 block depth rules、Mode Detection Heuristics 表。 |
| **Phase 3 — Description 優化** | **待辦。** 預計透過 `skill-creator-advance` 的 description-A/B loop 調 router triggering accuracy。 |
| **Phase 6 — Worked examples + tests** | 完成。[`references/EXAMPLES.md`](references/EXAMPLES.md)、[`test-prompts.json`](test-prompts.json)、[`trigger-eval.json`](trigger-eval.json)。 |
| **Phase 7 — 輸出品質 A/B** | **待辦。** Phase 3 完成後再透過 `skill-dev-toolkit:skill-tuning` 跑。Mode A briefing 風格是 taste-sensitive（簡潔度、lean 的肯定強度、jargon-flag 策略）— 純規則遵循無法 surface 出最佳版本。 |

Skill 已可作為 v1.0 出貨，會在 feedback 下持續改進。Mode C 是設計
面最年輕的部分；預期在實際 session 使用後會 refine。

---

## Files

```
brief-before-asking/
├── README.md           ← English README
├── README.ja.md        ← 日本語 README
├── README.zh-TW.md     ← 本檔（繁體中文）
├── SKILL.md            ← operational 檔（給 Claude）
├── test-prompts.json   ← Phase 6 — Mode A/B/C 評估 prompt
├── trigger-eval.json   ← router-trigger accuracy probe
└── references/
    ├── DESIGN.md                  ← 4 次迭代設計 rationale（author-only）
    ├── EXAMPLES.md                ← block 級 bad-vs-good worked example（runtime conditional load）
    └── IMPLEMENTATION-CHECKLIST.md ← author phase checklist（author-only）
```

---

## Bottom line

```
Briefing depth = decision speed。
價值是 abstraction bridge（Mental Model）+ 強迫 agent 把已知攤開
的 depth rules — 不是結構本身。
```
