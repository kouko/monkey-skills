# REQ-10 replay ③：PR #775（推導 replay，寫到 Task DAG 為止）

對象：`01e4fe54` "feat(loom-code): implementer prose-edit self-sweep — rule 14,
evidence + A/B apparatus (0.110.0) (#775)"。做法與理由同 `replay-772.md`（agent-decided 偏離）。
素材：`git log -1 --format=%B 01e4fe54` 與 `git show --stat 01e4fe54`（24 檔、1936 insertions）。

## intent（新模型會寫成的樣子）

```
# 讓 implementer 改完散文自己再掃一次
originator: kouko
kind: engineering
needs-design: no — 一條 implementer 契約規則加一支內部量測腳本；
                   沒有使用者讀或輸入的表面，量測腳本是開發自用不是對外介面
status: confirmed <date>

## Problem
文件審查抓到的缺陷，跨四個專案 104 條裡有 72% 不是「漏寫」，而是「改了這裡沒改那裡」——
旁邊那句話變舊了、自己宣稱自己做了其實沒做、放錯段落、沒有證據。
原本想加的「缺漏清單」對準的是另一類問題。

## Proposed outcome
implementer 在交回之前，對純散文的 task 自己做五個可查證的動作（找出被複述與被依賴的說法、
重新查證自己宣稱的事、走一次閱讀路徑、對照 schema、不適用要寫理由），不輸出清單。
另外做一支 A/B 量測工具，用來判斷這條規則到底有沒有效——而且要誠實登記「量不到」。

## Acceptance
1. 我派一個純 `.md` 的 task 出去，回來的東西不會再有「旁邊那句話變舊了」這種缺陷……
   而如果量出來沒有變好，我要在紀錄裡看到「沒有變好」，不是看到一句好聽的宣稱。
2. 這條規則的措辭改動，每一次都有 A/B 數字撐著或者被判定為 null。
3. 量測工具自己會在輸入壞掉時吵，不會靜靜給我一個好看的數字。

## Constraints
- 不得把 A/B 的 null 結果寫成「有效」。

## Open questions
- none
```

**決策點**：engineering ＝ 2。今天的實測也是 2（isolation hold 解除、PR merge）。

## plan 的 Task DAG（6 個 task，2 個 wave）

沿用原 SDD plan 的 6 個 task（同一條尺寸規則）。

```
Wave 1 — 規則與工具（三個 task）
  W1-01 implementer.md 規則 14 ＋ 釘住它的契約測試            after: —
  W1-02 prose_selfsweep_tally.py 的 parser（instruction-class 才算）after: —
  W1-03 prose_selfsweep_tally.py 的計數與 fail-loud 行為      after: W1-02

Wave 2 — 證據與收尾（三個 task）
  W2-01 audits/2026-09-01-docs-review-finding-causes.md（104 條的歸因） after: —
  W2-02 dogfood/2026-09-01-prose-selfsweep-ab/{protocol,cases,results} after: W1-03
  W2-03 版本 bump 0.109.0 → 0.110.0、CHANGELOG、BACKLOG 條目   after: W1-01, W2-02
```

checkpoint：`needs-design: no` → 沒有 spec 鏡頭。
wave 1 的 delta（規則檔＋腳本＋兩份測試，約 500 行）已越過 8 檔／400 行門檻 → 1 次；
wave 2 是最後一個 wave → 1 次，兼作 branch-end。**共 2**。

**一個要寫明的邊界**：今天的 14 次派工**明確排除**了 A/B 量測本身的 16 次
implementer＋judge 派工（原 plan 寫「session work AFTER this plan's tasks complete」）。
推導這一側同樣排除——A/B 是 W2-02 這個 task 產出的**資料**，
在新模型裡屬於該 task 內部的工作，不是 plan 的 task，也不進 `dispatch[]`。
兩側用同一條界線，這是本 change 唯一需要對齊的定義。

## 推導

修紅數 F：1（#771 的比例套在 6 個 task 上）。

| | W4-03 原規則 | 校準後規則 |
|---|---|---|
| commit | 6 ＋ 2 ＋ 2 ＝ **10** | 3 ＋ 6 ＋ 2 ＋ 6 ＋ 1 ＝ **18** |
| 派工 | 6 ＋ 2×4 ＝ **14** | 8 ＋ 8 ＝ **16** |
| 決策點 | **2** | **2** |

校準後 commit 的 3 ＝ intent ＋ plan ＋ review.json 建檔；6 ＝ 兩個 checkpoint × 3。
派工的 8 ＝ 6 個計畫 task ＋ 2 個「落地本輪 regression 案例」task；8 ＝ 兩個 checkpoint × 4。

## 對照今天

| 欄 | 今天（實測） | v10 推導（校準後） | 通過？ |
|---|---|---|---|
| commit | 28 | **18** | ✓ |
| 派工 | 14 | **16** 全部／**8** 審查子集 | 全部：✗／子集：✓ |
| 人類決策點 | 2 | **2** | ✓（持平） |

**派工這一欄要說清楚**（與 #771 同一個定義問題，不是為了讓它過）：
`ceremony-cost-old-vs-new.md` §(iii) 的 b 列自己寫明 14 ＝
「plan-review 2 輪＋task 級 fan-out 8＋whole-branch ≥2 輪＋站自審 2」，**全是審查派工**，
不含 6 個 SDD implementer。逐字對齊今天的定義，v10 是 **8**，8 ≤ 14 ✓。
兩邊都改成「全部派工」，今天 ≈ 20（14 ＋ 6），v10 是 16，16 ≤ 20 ✓。
只有「今天算審查、v10 算全部」這種不一致的比法才會 ✗。
