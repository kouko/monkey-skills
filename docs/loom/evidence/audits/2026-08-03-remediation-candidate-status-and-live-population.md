# 改法候選的出貨狀態與尚存母體 — 回測的第二半

- **Date**: 2026-08-03
- **前作**: `docs/loom/audits/2026-07-31-a-class-interceptability-backtest.md`
  只評了候選 1 與候選 3，並在其收尾明寫：任何整體排序都要把其餘候選一起評，
  該文沒有做。本文做那件事。
- **母體**: `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`
  §8 的五個候選，加上前作 §候選 6 新提的一個。以下一律以**章節錨點**引用該稽核，
  不用行號——那是它的勘誤明令的形式。
- **成本**: 零 agent、零派工。逐條 grep 實作 ＋ 回讀既有卷宗。
- **繼承的限制**: 承接該稽核的勘誤三條與其三處未修內部矛盾
  （`docs/loom/backlog/2026-07-27-investing-toolkit-arc-defect-provenance-audit-internal-inconsistencies-n.md`，
  其 item 4 已 WITHDRAWN），以及前作的分析單位（9 個計畫層事實問題**條目**，
  不是 A 類缺陷個數；兩者不可直接相比）。

## Verdict（一句話）

六個候選裡**三個已經出貨**，而前作與 §8 就其今日的文字而言，仍把它們陳列為
未裁決選項——**不是**說那兩份文件曾在出貨之後還去推薦它們（§8 寫於任何一次出貨
之前，不可能；前作的推薦標的當時確實還開著，而且正是那份推薦促成了它出貨）。
真正還活著的是**候選 1 的未執行半邊、候選 5、候選 6**——其中候選 5 的招牌案例
已被已出貨的候選 2 蓋掉。

## 為什麼會發生：清單被下一條 arc 超車

該稽核 §8 寫於 2026-07-27。loom-code 0.39.0（PR #625，commit `a56e0261`）
在**隔天**出貨，一次做掉候選 2 與候選 4。前作寫於 07-31，但它問的是「候選打得到
哪些缺陷」，從未問「候選是不是已經做了」——所以它在一份已經過期的清單上做排序。

這是 `docs/loom/memory/` 已有規則的一個新形狀：宣稱功能缺失前先 grep 實作。
既有的那條談的是「說某功能不存在」；這裡是「說某**改法選項**還開著」。同一個
動作可以擋掉兩者。

## 逐候選出貨狀態

| 候選 | 內容（§8 原文摘要） | 狀態 | 證據 |
|---|---|---|---|
| 1 | 技術 PIN 強制標註 `file:line` ＋ 獨立 agent 對讀來源 | **半出貨** | 規則在 `loom-code/skills/writing-plans/references/plan-format.md:169`；**無任何 plan-document-reviewer 檢查驗證合規** |
| 2 | check 8 的取材從 `Smallest End State` ＋ `Decision` 擴大到 brief 全文的義務句 | **已出貨**（0.39.0） | `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md` Check 8 的 Obligation sweep，逐字寫著 "regardless of which brief section it sits in" |
| 3 | 重用既有 helper 的指令強制附語意適配聲明 | **已出貨**（v0.43.0） | Check 17（四部分評分：presence / marker / …）＋ backlog 條目 `2026-07-27-reuse-adequacy-got-the-gate-it-had-been-missing.md` 狀態為 SHIPPED，其 origin 明指 §8 候選 3 |
| 4 | 收緊 P5：post-PASS 修訂動到技術內容必須重審 | **已出貨**（0.39.0，同一 commit） | `loom-code/skills/writing-plans/SKILL.md` §Amending a PASS plan：三種豁免的**封閉清單**，其餘一律重審，「特別是…被引用的事實（`file:line`、數字、對既有行為的宣稱）」 |
| 5 | live dogfood 變成計畫的必填任務（可標 N/A ＋ 理由） | **未出貨、未立案** | `plan-format.md` 與 `writing-plans/SKILL.md` 皆無任何 dogfood 規定 |
| 6 | 把 implementer 拒工從自發行為變成制度化的偵測面 | **未出貨、已立案** | `docs/loom/backlog/2026-07-31-institutionalise-the-implementer-s-refusal-to-work.md`，狀態 OPEN |

### 附帶更正：一條承重證據已經過期

`docs/loom/backlog/2026-07-28-plan-stage-fact-grounding-what-0-39-0-does-not-close.md`
item 1 以「檢查表停在 16 列，且 `test_plan_obligation_sweep.py` 把上限釘在 16」
當作候選 1 未執行的證據。**檢查表現在有 17 列，那個常數也已是 17**
（Check 17 隨 `Reuse-adequacy` 硬化出貨，是被授權的 append）。

item 1 的**結論仍然成立**——沒有任何檢查驗證「每個可驗證主張都帶引用」——
但它引用的那個數字不再支持它。**本次已改**：該 entry 的 item 4
（`Reuse-adequacy` declarative-only）因 Check 17 出貨而標為 CLOSED，item 1 的
過期證據附上更正註記，且其修法處方原本寫「Check 17」——那個號碼現在已被佔用，
一併改為「新檢查，下一個可用號碼是 18」。**三處都在本分支內完成，但不在同一個
commit**：前兩處隨本稽核一起落地，第三處是第一輪審查後的修正。

## 逐案判定：尚存的三個機制

沿用前作的 9 條目與其「判準刻意窄」的做法：每個機制只算它**結構上**打得到的，
不算「做了之後也許有幫助」。

| # | 弧 | 計畫層事實問題 | 候選 1 執行半邊 | 候選 5 | 候選 6 |
|---|---|---|---|---|---|
| 1 | #619 | A-1 恆等式 PIN 寫三項，來源實為四項 | ✅ | ✅（真打會讓 17 家殘差顯形） | ❌ |
| 2 | #619 | A-2 重用 top-line 選擇器，新 lane 語意不相容 | ❌ | ✅（真打驗證正是實際抓到它的兩個機制之一） | ❌ |
| 3 | #619 | A-3 文件寫在已撤回的計畫文字上 | ❌ | ❌ | ❌ |
| 4 | #618 | brief 要求 live dogfood，計畫沒有這個任務 | ❌ | ✅（招牌案例） | ❌ |
| 5 | as-filed | 欄位綁定規則 brief 稱必要卻從未設計 | ❌ | ❌ | ✅（拒工的獨有射程：對讀看不見設計缺口） |
| 6 | as-filed | 計畫三處寫「15 欄位」，實際 14 | ✅（正是 item 1 點名的「未引用」形狀） | ❌ | ✅ |
| 7 | as-filed | RED 指定的 filer 沒有離線資料列 | ✅ | ❌ | ✅ |
| 8 | as-filed | RED 與 brief 對 DUK 的判斷互相矛盾 | ✅ | ❌ | ✅ |
| 9 | as-filed | RED 仍寫著測試檔已撤回的主張 | ✅ | ❌ | ✅ |

**候選 6 的 5 條全部落在同一個弧**，且前作已記下它的選擇效應：那 5 條之所以在
紀錄裡，正是因為拒工把它們攤開了；沒有被拒工攔下的缺陷不會以「拒工案例」的形式
留下紀錄。本文同樣不主張命中率，只複述射程。

## 候選 5 的招牌案例已經被已出貨的機制蓋掉

案例 4（#618）是候選 5 被提出的理由：brief 要求收尾跑 live dogfood，計畫沒有
對應任務，所以沒有人跑。

那句 brief 義務句是
`docs/loom/specs/2026-07-25-kpi-id-injective-identity.md:131`：

> claim still needs the live dogfood at close-out.

已出貨的候選 2 的 Obligation sweep，其 deferred-verification 片語清單**逐字
包含** `still needs` 與 `at close-out`——這一句同時命中兩個。也就是說：
**案例 4 今天會被 Check 8 攔下**，候選 5 在它自己的招牌案例上的邊際收益是 0。

候選 5 的剩餘收益因此只有案例 1 與 2，且兩者都在**收尾**才生效——而案例 2 在
該弧已經被兩個獨立機制各自撞到（真打驗證、whole-branch）。它買到的是「讓那次
好運變成不可省略」，不是新的偵測面。

**未驗**：Obligation sweep 的觸發詞全是英文（`must` / `needs to` / `has to` /
`required` / `should`，加上前述片語）。本 repo 的 brief 語料裡有一小部分帶
中文義務句（`docs/loom/specs/` 下含「必要／必須／需要／應該」的檔案是少數，
但非零）。**一句只用中文表達義務的 brief 句子是否會從 sweep 掉下去，本文沒有
測**——需要一次冷讀行為驗證，不是 grep 能回答的。

本文提出的新開缺口有兩個，這是第一個；第二個記在下方 §覆蓋範圍與限制：
Check 8 由 reviewer subagent 讀散文執行，**弱 tier 會不會真的掃出那一句，本文
同樣沒有測**。兩者都是執行面而非取材面的疑問。

## 排序建議

| 順位 | 機制 | 理由 |
|---|---|---|
| 1 | **候選 1 的執行半邊**（一條驗證「可驗證主張都帶引用」的檢查） | 打到 5 / 9，含案例 6 那個「乾脆不引用」的形狀；而不引用是更便宜的撰寫路徑。0.39.0-not-close item 1 已把修法寫明（新檢查 ＋ 同步那個常數）。附帶證據：0.39.0 那條分支自己的 commit 裡有五處引用不準確，第五處就在記錄引用修正的那一節裡——作者側自律不成立，有實測 |
| 2 | **候選 6**（制度化拒工） | 打到 5 / 9，且射程涵蓋對讀看不見的設計缺口（案例 5）。已立案，起始條件已寫。成本是一輪設計 ＋ 跨 tier 行為驗證 |
| — | **候選 5** | 招牌案例已被 Check 8 蓋掉；剩餘收益都在收尾且已被獨立機制撞到過。建議**不做**，並在 §8 註明已被超車 |

候選 1 與候選 6 在案例 6–9 上是**替代品**（前作已記）；兩者都做，第二個在那四條
上的邊際收益降到 0。若只做一個，候選 1 較便宜（一條檢查 vs 一輪設計加行為驗證），
候選 6 射程較寬（多打到案例 5）。

## 覆蓋範圍與限制

- 承接前作與母體稽核的全部限制。
- **本文判定的是結構可攔截性，不是實測**。與前作同一個限制：要真的證實，需要把
  機制裝上去再跑一次同型的弧。
- **沒有時數**。「便宜／貴」全部是位置推論或直接引自 §8 的成本評級，不是時間量測。
- 候選 5 的「已被蓋掉」是**觸發詞與 brief 原句的逐字比對**（兩個片語各自命中），
  不是把該 brief 真的餵給一次 Check 8 跑出來的結果。剩餘風險落在 sweep 的
  執行面而非其取材面：Check 8 由 reviewer subagent 讀散文執行，弱 tier 會不會
  真的掃出那一句，本文沒有測。
- 本文未評估 0.39.0-not-close 那份 13 項清單的其餘項目；其中 item 2
  （驗收條件必須能被被綁定的角色執行）自稱涵蓋案例 7 與 8，本文只複述其自稱，
  未獨立判定。
