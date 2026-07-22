# brief-before-asking 觸發率 baseline — ask-triage A/B 前置量測

> 日期：2026-07-22 · 作者：Fable 5 session（i-have-adhd 對照評估 arc）
> 證據基礎：2026-07-01 ~ 07-22 全專案 transcript 掃描
> （`~/.claude/projects/**/*.jsonl`，mtime 初篩；主 session 500 檔、
> subagent 轉錄 4,389 檔）。量測方法與侷限見文末。
> 用途：`docs/loom/BACKLOG.md`〈loom-code ask-triage 0.30.0 — live
> telemetry A/B〉的 pre-A/B baseline。A/B 開跑前先讀本檔；再量測時
> 沿用同一 pattern 定義以保可比性。

## 結論（三行）

1. **覆蓋率 ~15%**：125 次 AskUserQuestion 事件裡只有 19 次落在
   bba 觸發過的 session；抽樣顯示無 bba 的提問**多數本來就該直接問**，
   真正疑似漏簡報約佔抽樣 1/4。
2. **skill 呼叫數不可當 A/B 指標**：抽樣發現「問句自帶 stakes＋mental
   model 的 inline 簡報」灰色案例——簡報行為正脫離 skill 之名擴散，
   數呼叫次數會系統性低估。指標必須是**裸問率**（BACKLOG 原定義的
   bare "X or Y?" vs cites-research/recommendation，本檔給它可比的分母）。
3. **簡報內容結構不是問題**：11 次有機觸發中零次「太長／跳過鋪陳」
   抱怨；歷史失敗全在送達紀律（07-03 前的同回合 AskUserQuestion 埋沒，
   已修）。A/B 該量觸發面，不該動 Mental-Model-first 結構。

## 分母量測（2026-07-01 ~ 07-22）

| 項目 | 數字 |
|---|---|
| 含 AskUserQuestion tool_use 的 session | 44 檔 / 125 事件（全在主 session） |
| 含 bba 觸發標記的 session | 12 檔（≈ 有機觸發 11 次；差 1 疑為 resume 重播行） |
| Ask ∩ bba | 8 檔 / 19 事件 |
| 有 Ask 無 bba | 36 檔 / 106 事件 |
| 覆蓋率 | 檔級 8/44 ≈ 18%；事件級 19/125 ≈ 15% |
| bba 無 Ask | 4 檔（bba 後純文字收問／使用者中途裁決） |

觸發標記 pattern：`"skill":"dev-workflow:brief-before-asking"`（精確
字串；裸 grep `brief-before-asking` 會被 MEMORY.md 索引行污染，
幾乎每個 monkey-skills session 都命中）。

### 抽樣分類（「有 Ask 無 bba」36 檔各抽第 1 例，取 12 例跨 11 專案）

- **(a) 疑似漏簡報 3 例（~25%）**——架構／範圍×成本／設計方向分岔被裸問：
  - youtube-summarize-scraper/867713a8:101（區網多台 LM Studio 行為抉擇）
  - loom-dogfood/7ae5c0f9:66（e2e 測試深度，最大成本驅動）
  - git-memory-r3/b9e375b5:378（Phase 3 重寫方向，裸問）
- **(b) 正確跳過 7 例**——品味／intake／debug 重現條件／消歧義／
  user-only 事實／irreversible 確認：
  dotfiles/65e0721d:109（背景亮度，純品味）、
  komado-Viewfinder/57b2eda1:50（debug 重現條件，user-only fact）、
  xbrl-tw/dc2f29df:26（任務起點 intake）、
  monkey-skills/9a2009d9:231（措辭小確認）、
  obsidian-skill-r1/25858c77:297（拼法消歧義）、
  obsidian-vault/97b96682:164（user-only 事實收集）、
  monkey-skills/033aefba:537（irreversible 確認，規則本就直接問）。
- **(c) 灰色 2 例＝inline 簡報**——問句自帶 stakes 與 mental model，
  實質簡報但未走 skill：finacial-analytics-r2/62c8354e:204、
  komado-Refs/76cd6848:137。**此類是「呼叫數≠簡報行為」的直接證據。**

粗估外推：106 個無 bba 事件 × ~25% ≈ **26 個漏網分岔 vs 觸發 11 次**
——觸發偏少的主因是裸問還在漏，不是分岔本來就少。

### ask-triage hook（PR#564，07-08 前後出貨）攔截痕跡

- 真 hook 攔截（attachment 型卡片）：10 個主 session / ≈19 次觸發
  （與分母表 Ask∩bba 的 19 事件是**不同度量的數字巧合**——檔數 10 vs 8，
  兩者相互獨立，勿混同）。
- 約 15% 的 Ask 事件有 triage 卡前置；hook 出貨前的窗前半段本來就無，
  **不可把 15% 直接讀成 hook 失敗率**——A/B 應以 07-08 後為 hook 腿窗口。
- 另 23 檔字面命中是開發該 hook 的 session 自身內容，需排除
  （區分法：attachment 型行 vs 一般內容行）。

## 有機觸發的效果面（11 案，07-01 ~ 07-22）

分布：monkey-skills ×3、finacial-analytics-r2 ×3、komado-Viewfinder ×2、
xbrl-tw / obsidian-skill-r1 / more-visualization 各 1；主動 10 / reactive 1。

| 型 | 案例（transcript:行號） | 判讀 |
|---|---|---|
| 有效高效（≤3 分定案） | more-viz 33a48df1:127、Viewfinder 8f9652da:43、monkey-skills 33c99c63:378 | 全都有 Mental-Model 鋪陳；8f9652da 是「一行結論→短鋪陳→單一裁決點」混合形態，效果最佳 |
| 有效（送達風險形態未爆） | Viewfinder 814cc765:625 | 六段式簡報與 AskUserQuestion 同回合堆疊（07-03 埋沒事故的同型前身），使用者仍選推薦項無抱怨——結果有效，形態高風險 |
| 有效（高複雜） | fin-r2 edd3fcfc:157、b4a88d18:346 | 簡報讓使用者當場指定更便宜的量測路（前者直接引出推翻 Route A 的探測） |
| 內容有缺可救 | xbrl-tw 48c7d0c8:306（範圍框錯）、monkey-skills a9d7879e:164（缺使用者視角差別，追問一輪補表格） | 失敗在取材不在結構 |
| 送達失敗（皆 07-03 前） | obsidian 6e739422:292（兩連抱怨，第三次純文字簡報才成功）、monkey-skills ff13f714:726（簡報被跳過）、fin-r2 4c87497c:347（觸發後無簡報無提問） | 皆「簡報未送達」；memory 修正（briefing-buried）後未再發生 |

橫向：**零次「太長」抱怨；Mental-Model-first 在真實記錄裡是幫的**；
唯一結構性啟示是混合形態（conclusion-first + 短 Mental Model）與
「Mental Model 須含使用者視角實際差別」兩條（後續刀的素材，非 A/B 範圍）。

## 對 A/B 設計的三條 implication

1. **主指標＝裸問率**（bare ask ÷ 全部裁決 ask），非 bba 呼叫數；
   (c) 類 inline 簡報計入「帶脈絡」腿。
2. **腿切分**：pre-0.30.0（hook 前）vs post-07-08（hook 後）；本檔
   07-01~07-22 混窗數字只作總 baseline，不作 hook 前腿。
3. **B 腿硬化候選**（triage 卡加「裸問且非瑣碎→先給一行 stakes」的
   可驗證動作句）：須設計成 **merge 後步驟**——marketplace 抓 GitHub
   main，feature branch 上的 hook 卡 A/B 測不到（見 memory：
   marketplace-github-source-blocks-premerge-deploy-ab）。

## 量測方法與侷限

- 方法：grep/sed/jq 逐行抽取，絕不整檔載入；AskUserQuestion 以
  `"name":"AskUserQuestion"` 計事件；抽樣僅取每檔第一個 Ask 事件。
- 暗數：純文字問句裁決（不經 AskUserQuestion 工具）機械抓不到——
  實際分岔數 > 125，真實漏網率只高不低。
- AskUserQuestion 次數 ≠ 分岔次數：一分岔可連問多次、一次呼叫可含多題。
- (c) 類判定僅憑問句自帶脈絡，未回讀前文確認。
- 效果面 11 案的逐案完整前後文抽取產於量測 session 的 scratchpad
  （session 結束即失效）；本檔表格內的 transcript 檔名:行號為持久引用，
  重驗時以 pattern 重掃即可（transcript 目錄名以 `-` 開頭，路徑需加
  `./` 前綴或用絕對路徑）。
