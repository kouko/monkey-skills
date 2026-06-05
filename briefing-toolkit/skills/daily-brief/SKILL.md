---
name: daily-brief
description: >-
  把散在 Gmail / Slack / Notion / Asana / Drive / Calendar / GitHub 的事整理成一份可信、每列可點處理的晨報,外加一張零省略行動表;每天累積、跨日延續(已結/仍在等你/新發生)。
  每天開工、想知道今天有什麼要處理、怕漏掉待回覆時用——before starting your workday。
  觸發詞:每日簡報、daily brief、morning brief、晨報、今天要做什麼、待回覆、要回的訊息、standup、今日まとめ、朝のブリーフィング。
  Do NOT use for 績效回顧/自評/專案盤點(那是 performance-evidence-audit,同機制反方向時間軸);Do NOT use 來寫回官方系統、代送或自動回覆(本 skill 唯讀 + 只寫本機草稿)。
metadata:
  tags: [daily-brief, morning-brief, aggregator, read-only, draft-only, cross-platform, triage, continuity, pdb]
  note: data/aggregator skill — 自包含 raw MCP fan-out。
---

# Daily Brief(每日跨平台晨報)

## 一句話定位

把散在 7 個平台(Gmail / Slack / Notion / Asana / Google Drive / Google Calendar / GitHub)的事,整理成一份**可信、每一列都能一鍵點回原始紀錄處理**的晨報,外加一張**零省略**的完整行動表。產物**每天累積**(日期前綴台帳),並**跨日延續**——今天的簡報會對照昨天,算出哪些已結、哪些還在等你、哪些是新發生。核心價值不是「撈到很多」,而是**交叉印證後標信心、標出處、誠實標盲區、不漏掉任何要你回覆或處理的事**。

## 何時用 / 何時不用

**用**:每天開工、想 60 秒讀回今天全貌、怕漏掉冷門平台的待辦、想知道有哪些訊息在等你回。

**不用**:
- **績效回顧 / 自評 / 盤點某段期間做了什麼** → 用 `performance-evidence-audit`(同一套跨平台機制,但時間軸朝過去、目標是證據而非 triage)。
- **要寫回官方系統 / 代送回覆 / 自動行動** → 本 skill **永久不做**(見下「Skill 分層」紅線)。停下,改交人工。
- **多人 / 團隊簡報** → 本 skill 是單一使用者視角。

## Skill 分層(HARD 紅線)

- **read-only**:全程跨平台**唯讀**(get_me / search / fetch / read / list)。不改、不刪、不送出、不標記、不回應任何平台資料。
- **draft-only**:只把產物寫進使用者**指定的本機資料夾**(MD + CSV)。**絕不**寫回 Notion 頁、Slack、Gmail、Asana 或任何官方系統,**絕不**代送或自動回覆。
- 任何「寫回 / 送出 / 自動回覆」都不在範圍。若使用者要求,停下並明說這超出 read-only/draft-only 邊界,改交人工。

> 這兩條是安全紅線,**無判斷空間**——不論使用者怎麼要求,fan-out 階段只讀,輸出階段只寫本機草稿。

## 核心原則(務必遵守)

1. **出處優先**:晨報與完整表的**每一列**都帶**可點的 canonical 深連結**(thread 永久連結 / Slack permalink / Notion page / Asana task / Drive 檔案 / Calendar htmlLink / GitHub PR/issue)。WHY:沒連結的簡報只是「又一個要你查的地方」,而非行動入口。無單一直連的項目**仍列入**,連結欄標「⚠️ 無直連」,**不靜默省略**。
2. **交叉印證標信心**:同一件事在 **2+ 平台**出現才標 ✅;單一來源標 ⚠️;由情境推得的標「推論」。WHY:跨 7 平台撈量大,沒有信心分級就會把噪音當事實往上推。注意 **GitHub PR → 自動發到 Slack → 又開 Asana task 是同一件事的回聲,不是 3 個來源**,別據此灌高信心。
3. **誠實標缺口與盲區**:撈不到、被截斷、日期不確定、作者無法確認,都明說,絕不臆造。Gate 結果(哪些平台已涵蓋 / 受阻 / 未連)寫進**兩份產物開頭**。WHY:某平台沒連卻照常產一份「看似完整」的簡報,正是本 skill 要防的「假完整」失敗模式。
4. **唯讀**:見上 Skill 分層。稽核只讀,寫只寫本機草稿。
5. **客觀為主**:報「是什麼 / 為何現在重要 / 接下來」,**不**替使用者打分、不美化、不淡化。「需回覆 / 需處理」只能**啟發式偵測**(@你的提問、等你回的 email、指派給你快到期的 task)——**必標信心,不可宣稱確定**。WHY:把「推測等你回」寫成確定,使用者會誤把推論當事實去行動。
6. **延續性以 live 平台重驗,不信昨日文字**:跨日 delta 時,昨日 CSV 只告訴你「要去重查哪些 ID」,**事實一律以今天 live 平台讀到的為準**。WHY:若昨日簡報夾帶幻覺項,信昨日文字會一路 carry-forward 把幻覺放大。
7. **動態焦點(門檻驅動)**:今日焦點**不固定 N**——納入條件是「今天到期 / 會卡住別人 / 不處理今天有後果 / 高槓桿決策」。下限**可為 0**(明說「今日無關鍵焦點,可專注深度工作」,**不硬湊**);軟上限 **~5**(超過加「⚠️ 高負載」橫幅,但**全列保留不靜默截斷**)。WHY:硬湊出 3 件焦點 = 稀釋真正重要的;靜默砍掉第 6 件 = 漏事。
8. **字數上限**:晨報設長度天花板,逐段控制。WHY:無上限 = AI 回一面牆,使用者讀不完就失去「60 秒讀回全貌」的價值(JP 實務圈反覆點名的最大坑)。

## 工作流

> 觸發後依序執行。標 **MANDATORY** 的步驟必須先讀對應 reference 再動手;標 **Do NOT load** 的檔案在該步**不要**載入(省 context)。

### 0-A 資料源就緒 Gate(第一次使用 / 換機 / 換帳號必做,不可略過)
對 7 個平台逐一驗 **連線 → 身份可讀(get_me / profile) → 內容可讀(一次最小查詢的讀取煙霧測試)**(精確涵蓋窗在 0-B 才定;Gate 此處先用粗略 `{TODAY}` 今日窗做煙霧測試,fan-out 再用精確窗),整理成就緒清單(✅ 就緒 / ⚠️ 受阻=連上但讀不到 / ❌ 未連)。受阻或未連的平台,用 AskUserQuestion 讓使用者選「去補齊後重跑 Gate」或「知情後略過(記進盲區)」。**未過 Gate 不得 fan-out**——否則產出「假完整」。
→ **MANDATORY:讀 `references/platform-search-playbook.md` 的 pre-flight 段**(各平台就緒檢查的精確做法)。

### 0-B Intake(先問清楚再動手)
用 AskUserQuestion 確認:**涵蓋期間**(今日 + 近 48h 新事)、**未來窗 N**(預設 **7** 天)、**排除主題**、**輸出資料夾**(本機路徑)、**emoji 分區開關**(預設開,可關成純文字)。

### continuity-load(fan-out 前)
在輸出資料夾定位「**日期 < 今天的最近一份**」CSV,讀其唯一識別碼(下一步的 join key)+ 焦點 / 未來段。無 prior → 標「首份簡報,無對照」並**跳過延續段**;跳天 → 讀最近一份並標「**距上次 N 天**」。
→ **MANDATORY:讀 `references/prioritization-framework.md` §延續性**(定位規則 + 首份 / 跳天降級)。

### 平行 fan-out(每平台一個 sub-agent,一次發出)
**在同一訊息發出全部就緒平台的 sub-agent(多個 Agent 呼叫並行,每平台一個、各自獨立 context)**,廣度優先。每個 sub-agent:**先用 ToolSearch 載入該平台 MCP 工具的 schema**(這些工具是 deferred,**不先載直接呼叫會 InputValidationError**),再在期間窗內多角度搜索,回傳結構化 markdown(項目 + 出處深連結 + caveats)。**把 0-A Gate 已取得的本人身份(Slack user ID、Asana GID、Notion self id、各 email、GitHub login)直接寫進每個 agent 的 prompt**——身份只該問一次,agent 拿到就不必重抓,省一輪 round-trip(見 playbook §2「身份 token 往下傳」)。**某平台過了 Gate 卻在 fan-out 中途失敗(rate-limit / timeout / token 過期)→ 標為 runtime 盲區寫進涵蓋聲明,不靜默吞掉、也不整份中止。**
→ **MANDATORY:讀 `references/platform-search-playbook.md`**(7 平台各自的 ToolSearch 查詢字串、搜索角度、雷區、canonical 連結形式)。
→ **Do NOT load** `references/brief-templates.md` 於此步——版型在產出階段才需要。

### triage(緊急度 × 相關性)
把 7 份報告依「專案 / 主題」歸併,套**緊急度 × 相關性**排序、套**動態焦點門檻**、跑「**需回覆**」啟發式偵測,標信心(✅ / ⚠️ / 推論)。
→ **MANDATORY:讀 `references/prioritization-framework.md`**(評分維度、動態焦點門檻、需回覆啟發式、信心模型)。

### continuity-diff(triage 後)
今日項目用**唯一識別碼 JOIN 昨日 CSV**,算四狀態:🆕 新發生 / ⏳ 仍在等你(已 N 天)/ ✅ 已結 / 🔄 狀態變化。**硬原則**:每個狀態都**以 ID 去 live 平台重驗**(原則 6),昨日 CSV 只給「要追哪些 ID」不給事實。首份 / 跳天依 continuity-load 的標記降級處理。

### 產出雙產物(draft-only,日期前綴)
寫進指定資料夾:`<YYYY-MM-DD>_晨報.md`(curated,PDB（President's Daily Brief）風格 6 段 + 動態焦點)+ `<YYYY-MM-DD>_完整事項.md`(零省略行動表,每列可點)+ `<YYYY-MM-DD>_完整事項.csv`(機讀,**唯一識別碼欄 = 隔天 delta 的 join key,不可省略**)。兩份開頭都放資料源涵蓋聲明。
→ **MANDATORY:讀 `references/brief-templates.md`**(晨報 6 段版型 + 完整表 / CSV schema + 涵蓋聲明 + 日期前綴命名規則)。

## 排程註記

本 skill 是 **on-demand**——觸發才跑。「每天早上自動跑」**不在 skill 內**,靠 harness 外掛:`/schedule`(scheduled remote agent)、系統 cron、或 Cowork scheduled task,排成每早觸發本 skill 即可。skill 只**註明**怎麼疊,不內建排程,也不負責遞送(不推 Slack / email)。

## 反模式(別這樣做)

- ❌ **沒過 0-A Gate 就 fan-out** → 某平台讀不到卻照產一份「看似完整」的簡報,使用者誤以為沒漏 = 假完整。
- ❌ **直接呼叫平台 MCP 工具卻沒先 ToolSearch 載 schema** → deferred 工具會直接 InputValidationError 失敗;每個 fan-out 一定先 ToolSearch。
- ❌ **延續性相信昨日簡報文字、不去 live 重驗** → 昨日的幻覺項會一路 carry-forward 被放大;ID 只是「要重查誰」,事實一律重驗。
- ❌ **硬湊焦點 / 靜默截斷** → 沒事硬擠 3 件焦點稀釋重點;超過軟上限就默默砍掉尾巴 = 漏事。下限 0 要明說,超限要加橫幅但全列。
- ❌ **把「需回覆」當確定** → 啟發式偵測只能標信心(✅/⚠️/推論),宣稱「David 在等你回」卻其實是推測,會誤導行動。
- ❌ **同源回聲當多來源灌高信心** → GitHub PR → bot 發 Slack → 又開 Asana task 是**同一件事**;當 3 個來源標 ✅ 是假交叉印證。
- ❌ **無連結的行動項** → 「合約要回」卻沒連結,使用者還要自己回去找,簡報變成「又一個要查的地方」。無直連的標「⚠️ 無直連」也比省略好。
- ❌ **一面牆、無字數上限** → 把撈到的全倒進晨報,使用者讀不完;晨報要狠取捨(完整表才零省略),逐段控字數。
- ❌ **某平台失敗就默默略過、照產完整報告** → 必須記進涵蓋聲明、在受影響結論標盲區,不可吞掉。

## 參考檔

- `references/platform-search-playbook.md` — **0-A Gate 與 fan-out 時讀**。7 平台(含 GitHub)各自的就緒檢查 pre-flight、ToolSearch 查詢字串、搜索角度、雷區、canonical 深連結形式表。**不要**在 triage / 產出階段載入。
- `references/prioritization-framework.md` — **continuity-load 與 triage 時讀**。緊急度 × 相關性評分、動態焦點門檻、「需回覆」啟發式、信心模型、延續性 diff(ID-join + live 重驗 + 4 狀態 + 首份 / 跳天降級)。
- `references/brief-templates.md` — **產出階段才讀**。晨報 6 段版型(含「自上次以來」延續段)+ 完整事項表版型 + CSV schema(含唯一識別碼 join key)+ 資料源涵蓋聲明 + 日期前綴命名 / 累積規則。
