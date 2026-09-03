# Investing-toolkit 出貨弧 — 缺陷溯源稽核（arc-by-arc）

- **Date**: 2026-07-27
- **Scope**: investing-toolkit 連續七個出貨弧（PR #605 / #610 / #611 / #612 / #616 / #618 / #619）＋一個進行中的弧（`as-filed-statement-reconstruction`，branch `feat-sec-submissions-pagination`）。鏡頭：**每一個 review 缺陷的來源在哪一個階段**（計畫 / 測試證據 / 實作），不是缺陷本身的技術內容。
- **Method**: 讀 3 個 worktree project dir 底下 8 個 session transcript（約 35 MB，2026-07-22 → 07-27），機械抽取 reviewer verdict 行與 🔴/🟡 finding 行，再逐案回讀上下文；交叉比對 `docs/loom/plans/*` 的計畫檔、`docs/loom/memory/*` 的耐久教訓、以及 `git log`。
- **Status**: 只有觀察，未修任何東西。§8 的改法候選**未裁決**。
- **Relation to prior audits**: EXTENDS `2026-07-20-loom-mechanism-weakness-audit.md`。那份的核心判詞是「機關驗形狀（schema / exit-code / heading 有無），幾乎從不驗出處」。本稽核是同一句話在**七個真實出貨弧**上的田野證據——只是這次驗不到出處的那份文件是**計畫本身**。

> **勘誤（2026-07-27，`feat-plan-fact-grounding` 收尾時加註）**：本文有
> **三處已確認的內部矛盾尚未修正**，其中 §5 的「A 類的偵測面只有兩個，都在收尾」一句
> 是**錯的**——本文自己的 §3.7、§3.8、§6 都記錄了更早的攔截（逐任務審查者的自發對讀、
> implementer 動工前的拒絕、以及 §6 把該次拒絕列為正面反例）。該句是下游 brief
> 問題陳述的承重點，**引用本文前請先讀** `docs/loom/BACKLOG.md` 的
> "investing-arc defect-provenance audit — internal inconsistencies" 條目，
> 那裡列出三處矛盾的逐條出處與調解方法。矛盾未就地修正是刻意的：稽核是一份有日期的
> 田野觀察，更正它需要重讀 35 MB transcript；PCE 基線已明文卡在該調解完成之前。
>
> 本勘誤與下游文件一律以**章節錨點**（§N）引用本文，不用行號：加註這段勘誤本身就把
> 其下每一行都往後推，一次示範了為什麼行號引用在會被插入的文件上撐不住
> （見 BACKLOG "Plan-stage fact grounding — what 0.39.0 does NOT close" 第 3 項）。
> 這段刻意不寫推移了幾行——寫了就等於再立一個每次編輯都要重新量測的宣稱，而收尾
> 補救就是這樣失手的：在編目引用錯誤的條目裡寫錯引用，在示範計數會漂移的
> 句子裡寫錯計數。自我指涉的量值不要寫（含輪次計數）。

## Verdict（一句話）

計畫的**格式**每一份都通過（14/14 或多輪修到通過），但計畫同時承載了**技術事實**（恆等式公式、「重用某個 helper」的指令、引用的實測數字、欄位數量），而**沒有任何關卡驗證這些事實為真**——所以計畫一旦寫錯，下游每一關都會忠實地「確認」它是對的（spec-reviewer 的職責就是拿產出對計畫），缺陷只能等跨任務機制（whole-branch review、真打 dogfood）在**收尾階段**引爆，那是全流程最貴的位置。

---

## 1. 計分板

verdict 數字由 transcript 機械抽取後去重，屬**近似值**（同一輪 verdict 可能被摘要重述）；缺陷欄則是逐案回讀確認過的。

| Arc | PR | 計畫審查 | 任務級 verdict（PASS / PWN / NR）| 確認缺陷（A=計畫 / B=測試證據 / C=實作）| 最貴的一個在哪裡被抓到 |
|---|---|---|---|---|---|
| KPI tearsheet | #605 | 2 輪（R1 gap：`--out` flag 無實作任務）| 15 / 3 / 6 | **B×4**（全部被 fixture 遮蔽）| 逐任務對抗式品質審查（3 個）＋ whole-branch（1 個跨模組接縫）|
| TW 背書保證 iXBRL | #610 | — | 14 / 0 / 1 | C×3（編碼、概念 fallback、寫死 report-id）| 真打 MOPS dogfood ＋ 審查 |
| US XBRL→store producer | #611 | 2 輪 | 6 / 1 / 1 | C×1（守衛 key 比消費端身分更細）| whole-branch（1 🟡，判 ship + next-touch）|
| TW store producer | #612 | 1 輪 14/14 | 16 / 4 / 3 | C（數個）| 真打台積電四季 dogfood |
| 公司總營收兩線 | #616 | **5 輪，3 次 NR** | 5 / 5 / 1 | **B×4**、C×2 | 逐任務品質審查 |
| kpi_id injective | #618 | 2 輪（R1 NR：Task 7 的 RED 不可執行）| 5 / 1 / 3 | **A×1**、C×3（同族三輪）| whole-branch ×3 輪 ＋ 補跑的真打 dogfood |
| US as-reported 線 | #619 | PASS，**但 post-PASS 修訂了四處、re-review 被跳過** | 19 / 7 / 10 | **A×2**、B×2、C×2 | 真打驗證 ＋ whole-branch（兩者各自撞到同一個規格錯）|
| as-filed 重建（進行中）| — | PASS | — / — / 1 | **A×3** | implementer 拒工並停下來提問 |

---

## 2. 根因分類法

| 類 | 定義 | 誰抓得到 | 抓到的時點 |
|---|---|---|---|
| **A — 計畫事實錯** | 計畫寫下的技術主張本身為假：公式寫錯、指示重用一個語意不相容的 helper、引用的證據數字不支持結論、欄位數量與程式碼不符、brief 要求的任務沒進計畫 | 只有 whole-branch review、真打 dogfood，或運氣好的品質審查者自發去對讀來源 | **收尾**（最貴） |
| **B — 測試無鑑別力** | 測試通過但什麼都沒證明：fixture 恰好遮蔽 bug、fixture 是人手推導來配合實作、斷言在跟常數比自己、正確性論證依賴別的模組擁有且無人釘住的不變式 | 逐任務對抗式品質審查（會做突變測試）**很有效** | 任務級（便宜） |
| **C — 一般實作錯** | 程式碼沒照計畫寫，或漏了邊界情況 | spec-reviewer ＋ 品質審查，正常運作 | 任務級（便宜） |

**A 類是這次稽核的主題**，因為它有一個結構性質：**它會被下游每一關確認為正確**。spec-reviewer 拿產出對計畫，計畫是錯的，所以「符合計畫」＝「通過」。B 和 C 類則是流程正常運作的證據，數量多不代表流程壞掉。

---

## 3. Arc-by-arc 卷宗

### 3.1 KPI tearsheet — PR #605（2.32.0）

計畫 2 輪過（R1 抓到 `--out` flag 沒有對應任務）。四個真 bug **全部是 B 類**，全部被通過的 fixture 遮蔽，全部只有對抗式審查逼得出來：

1. **排序鍵解包寫反** `end, start = key` —— 被「期別起迄同步遞增」的 fixture 完美遮蔽；遇到非常規期間（如 14 個月過渡財年）欄序就錯。
2. **分組順序相依** —— `same_period` 可證明非遞移（instant 與 duration 共享同一日期對時 A~B、B~C 但 A≁C），錨定式分組讓**同一批資料因磁碟迭代順序不同而分出不同組數**。
3. **既存 reader 崩潰**（非 dict 的 JSON envelope 讓「never raises」承諾破功）。
4. **跨模組期別身分接縫** —— store 用吸附分組、formatter 用原始日期對；**只有 whole-branch 看得到**。修法是讓 store 產出權威 `period_axis_key` 當對欄鍵。

> 這個弧是「逐任務對抗式審查值回票價」的最佳範例，而且**沒有 A 類缺陷**。

### 3.2 TW 背書保證 iXBRL — PR #610（2.33.0）

C 類為主，三個都進了 repo store：宣告 big5 實為 UTF-8 的智慧解碼、同一經濟事實不同 concept 字串的 first-present fallback、`pack_tw` 寫死 `--report-id C` 讓 fallback 失效（審查抓到）。真打 MOPS（國泰金 / 彰銀 / 三商壽）乾淨。

### 3.3 US XBRL→store producer — PR #611（2.34.0）

whole-branch PASS_WITH_NOTES，唯一的 🟡：碰撞守衛用 `_signature_key` 的**原始 consolidation** 判相異，比 store 身分**更細**，理論上會對合法輸入誤報。reviewer 明判 ship ＋ 記 next-touch。耐久教訓進 store：守衛要 key 在**消費端的身分正規化**上。

### 3.4 TW store producer — PR #612（2.35.0）

計畫首輪 14/14。以真打台積電四季 dogfood 收尾，數值對實績（營收 2.89 兆）。C 類為主。

### 3.5 公司總營收兩線 — PR #616（2.36.0）

**計畫階段最扎實的一個**：5 輪審查、3 次 NEEDS_REVISION，第 5 輪還額外裁決並支持了計畫作者對第 4 輪建議修法的**拒絕**。

缺陷則幾乎全是 **B 類**，而且是同一家族——Task 5 一輪三個 🟡：一個在比較常數跟自己、一個重構的理由沒有任何測試涵蓋、一個正確性論證建立在別的模組擁有且無人釘住的不變式上（`kpi_xbrl.py:556` 寫死 `scale: 1`）。Task 4 另有一個人手推導的假 fixture（修正做法值得記：不手打修正後的資料列，而是真的呼叫 `build_top_line_backfill`、只 stub 抓取，把真實輸出逐字複製進 fixture）。Task 11 的 🟡 是**這次改動自己弄壞的一份文件，長在一道信任閘上**（`attest_source` docstring 逐一列舉信任清單成員，新加的那個沒進去）。

> 註記：計畫審查輪數多 ≠ 缺陷少。#616 的 5 輪計畫審查全在修**結構**（DAG、任務映射、RED 可執行性），它們與後續抓到的 B 類缺陷沒有因果關係。

### 3.6 kpi_id injective — PR #618（2.37.0）

**A 類首例，而且 finding 直接指到計畫檔的行號。**

- whole-branch 的 🟡：`where: docs/loom/plans/2026-07-25-kpi-id-injective-identity.md:9-172`（Tasks 1–7，**無 dogfood 任務**）。brief 自己寫「pipeline 主張仍需收尾的 live dogfood」，計畫沒有這個任務，也就沒有人跑。先前那 47 家的數字全部來自**重放選擇器迴圈**，不是真的 `ingest_pack` ＋ 寫入 store。
- 補跑真打之後才發現：kpi_id 加了 14 bytes digest → 某家的序列檔名 243 → **257 bytes，撞 255 上限，整包 ingest abort**。當下 **1084 個測試全綠**。
- 另外三輪 whole-branch **每一輪都抓到同一個缺陷類別在不同的站點**（prefix 排序 → suffix 大小寫匹配 → axis 成員資格），每一次的修正都正確，每一次的收尾句（「兩者再也不會彼此漂移」）都比修法**實際 earned 的範圍更寬**，下一輪就住在宣稱與修法的落差裡。

### 3.7 US as-reported 線 — PR #619（2.38.0）

**A 類最集中的弧，也是缺陷代價最高的弧。** 計畫拿到 PASS，但之後有一段 `Post-PASS amendment note (re-review skipped, per SKILL.md §Self-review)`——四處追加修訂，未再送審。

**A-1｜計畫的 PIN 把恆等式公式寫錯。** 計畫引用「探針量到 30/32 精確平衡」當證據，但那個數字來自**四項**公式（優先取含非控制權益的權益概念，退回母公司單獨權益時**再加上少數股權**）；計畫的 PIN 卻把權益鏈寫成「母公司單獨權益優先」，T7 照著寫成**三項**、不加少數股權。實作者引用「30/32」當三項公式的證據——那個數字是四項公式的證據。後果：32 家可驗公司裡 **17 家**（GE、福特、通用、聯合健康、花旗、摩根士丹利…）殘差恰好等於少數股權，會被誤判「帳不平」；而且探針每家只驗一個時點，視圖是逐期驗，暴露面更大。
> 抓到它的方式**不在任何關卡的職責裡**：T7 的品質審查者自發把探針腳本裡實際計算恆等式的那段程式碼，拿去跟計畫的 PIN 對讀。修法是**先修計畫的規格文字（錯的源頭），再派修正**。

**A-2｜計畫指示 statement 線重用 top-line 線的選擇器。** 三條同時收斂的災情同一根因：真打驗證發現**沃爾瑪失去營收、淨利、每股盈餘**；whole-branch 發現 **17 家公司失去權益**（連帶讓對帳檢查在生產環境走不到）；真打對帳**六家有四家誤報**。
> **1165 個測試 ＋ 19 輪逐任務審查全部看不見它**——因為每個任務的測試在自己的切片內都是正確的。兩個獨立機制（真打資料、直接執行 shipped 模組）各自從不同角度撞到同一個規格錯。耐久教訓已入 store：`a-shared-helper-can-be-right-in-one-lane-and-destructive-in-another`。

**A-3｜文件寫在被撤回的計畫文字上。** Task 10（文件）依據的是 Task 6 CORRECTION 已經退休的數字，導致 `analysis-kpi/SKILL.md:200-201` 出貨時仍寫「GOOGL from 2014, DIS from 2018」，而 fixture 與程式碼 docstring 都已是 2012 / 2016。

**其他**：T9 一個 🔴——永久 store 的**半截寫入**，兩位審查者各自獨立命中同一點（writer≠judge 分工買到的東西）；T3、T4 各一個當場修掉的 🟡（包內同科目同期間同申報靜默丟一筆；docstring 承諾「絕不與呼叫端共用物件」但實為淺複製）。

### 3.8 as-filed 重建（進行中）

**A 類三連，而且這次擋在最便宜的點**——implementer 拒絕動工並回報四項量測：

1. 「把 15 欄位從重建推導出來」需要一條**把 filer 自己的科目行綁到具名欄位**的規則；**brief 稱這層「必要且不可避免」卻從未設計，計畫也沒設計**。那不是一條斷言，是每個欄位一條。
2. RED 指定的 filer 沒有離線資料列（DUK/O/KO-2026 只有普查、PLD/PSX 缺席）——任何它自己發明的規則，其**鑑別性案例**都只能靠它自己寫來配合的 fixture 釘住。
3. **RED 與 brief 對 DUK 的判斷互相矛盾**（brief 說 unresolvable → 依 kickoff 決議應為具名缺口；RED 卻要求它產出值）。
4. 計畫三處寫「15 欄位」，實際只有 **14** 個（模組 docstring 從出貨起就寫 14）。

另有一處：計畫的 RED 條款仍寫著已被證偽、測試檔裡已撤回的主張（「CL/COST/MSFT/O/PGR/TRV 是實測到的合併表公司」）——**測試撤回了，計畫沒有，所以計畫還在把假前提往下游帶**。

---

## 4. 跨弧模式

| # | 模式 | 證據 |
|---|---|---|
| **P1** | **計畫是技術 SSOT，但沒有事實關卡。** 計畫承載公式、重用指令、實測數字、欄位數；`plan-document-reviewer` 的 16 條檢查**全是形式檢查**（欄位有無、DAG 深度 ≤5、RED/GREEN 具體性、brief 映射、`Files touched` 互斥、mechanical 權重）——沒有一條問「這個技術主張是真的嗎」 | #619 A-1／A-2、進行中弧 |
| **P2** | **brief 的義務句只要沒落在 `Smallest End State` 或 `Decision` 兩節，就會從計畫掉下去。** check 8 只映射這兩節 | #618（「收尾需 live dogfood」寫在 §Probe evidence，合法逃逸）|
| **P3** | **「重用某個 helper」是跨任務語意風險，逐任務審查結構上看不見。** 重用複製的是語意不只是程式碼 | #619 A-2（1165 測試 ＋ 19 輪任務審查全盲）|
| **P4** | **修正的宣稱範圍常常大於修法 earned 的範圍**，下一輪就住在落差裡 | #618 三輪同族缺陷 |
| **P5** | **計畫可以在 PASS 之後被改而不必重審**（`re-review skipped, per SKILL.md §Self-review`），而 A 類缺陷最集中的弧正好用了這條 | #619 |
| **P6** | **探針 ≠ 管線 dogfood。** 取樣資料回答「我要的形狀存在嗎」，永遠不回答「管線撐得住這個輸入嗎」 | #618（47 家探針全清、首次 e2e 就 abort）；已入 store |

---

## 5. 為什麼逐任務審查結構上看不見 A 類

```
brief ──► plan ──► task ──► implementer ──► spec-reviewer   （對「計畫」判合格）
                                        └─► quality-reviewer（對「rubric」判合格）
```

spec-reviewer 的裁決基準**就是計畫**。計畫錯 → 忠實實作 → 判 PASS。quality-reviewer 用 rubric（安全 / 架構 / 正確性 / 命名 / 測試 / 重構 / 外部介面接地），rubric 裡沒有「計畫的技術主張是否為真」這個維度——T7 那次抓到，是審查者**自發**越界去對讀探針原始碼，這是運氣不是制度。

因此 A 類的偵測面只有兩個，都在收尾：
- **whole-branch review**（唯一有 cross-task-coherence 維度的關卡）
- **真打 dogfood**（唯一會讓真實資料流過整條管線的關卡）

而 #618 顯示了第三種失效：**當計畫根本沒有 dogfood 任務時，這兩個偵測面只剩一個。**

## 6. 什麼是有效的（避免把結論讀成「流程壞了」）

- 逐任務對抗式品質審查對 **B 類極有效**——會做突變測試逐項驗證，#605 四個真 bug、#616 一輪三個 🟡 都是它抓的。
- **writer≠judge 買到了東西**：#619 T9 的 🔴（永久 store 半截寫入）是兩位審查者各自獨立命中。
- **implementer 有能力拒工**：進行中的弧，A 類在最便宜的點被擋下。
- 每一個 A 類缺陷**都在合併前被抓到了**。問題不是漏出去，是**抓到的位置太貴**。

## 7. 覆蓋範圍與限制

- verdict 計數為機械抽取後去重的**近似值**；缺陷條目本身逐案回讀確認。
- #612 / #610 的細節取自 transcript 摘要與 repo memory，未逐輪回讀全部審查輸出——這兩弧的分類信心低於其餘五弧。
- 只看 investing-toolkit 的弧。同期的 loom-* 自身開發弧（wiki-update loop、bba trigger 等）未納入，因此**不能**由本稿推論「A 類只發生在 investing 弧」。
- 未量測：A 類缺陷造成的實際 rework 時數。所有「最貴」的說法是位置推論（收尾 vs 任務級），不是時間量測。

## 8. 改法候選（未裁決）

| # | 候選 | 針對 | 成本 / 爆炸半徑 |
|---|---|---|---|
| 1 | 計畫裡每一條技術 PIN（公式、重用指令、引用的實測數字、欄位數）**強制標註來源 `file:line`**，並由一個獨立 agent 對讀來源——把 T7 那次的運氣制度化 | P1 | 中；改 `plan-format.md` ＋ 加一條計畫審查檢查 |
| 2 | check 8 的來源節從「`Smallest End State` ＋ `Decision`」擴大到 brief 全文的義務句；或要求 brief 把驗證義務寫進 `Smallest End State` | P2 | 低；改一條檢查的取材範圍 |
| 3 | 計畫裡任何「重用既有 helper X」的指令，強制附一行**語意適配聲明**（X 在新 lane 的行為是否與舊 lane 一致、不一致處為何可接受） | P3 | 低；格式加一欄 |
| 4 | 收緊 P5：post-PASS 修訂若動到**技術內容**（非純格式 / 戳記）必須重審 | P5 | 低；改 `SKILL.md §Self-review` 的豁免範圍 |
| 5 | 把「本弧的 live dogfood 任務」變成計畫的**必填任務**（可標 N/A ＋ 理由，但不能沉默省略） | P2 / P6 | 中；改計畫格式 ＋ 檢查 |

候選 2 與 4 最便宜且可逆；候選 1 直接打在最貴的缺陷類上，但需要一輪設計。
