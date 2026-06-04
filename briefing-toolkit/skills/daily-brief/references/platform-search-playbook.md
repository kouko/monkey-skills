# 七平台搜索 Playbook（fan-out sub-agent prompt 範本）

> **這份檔案是 fan-out 階段的母體**：每個平台一個 sub-agent，並行搜索與「我」相關、可行動、近期的事，回傳結構化 markdown 供後續 triage / continuity-diff 消費。
>
> **時間軸方向**：本 skill 是**前瞻**型（今日 + 未來 N 天 + 近 48h 新事），與回顧型稽核相反。每個 agent 的搜尋窗都圍繞「現在 → 未來」與「剛剛發生、我可能還沒看到」。

---

## 1. 用法

在主對話**一次發出「全部 ✅就緒平台」的 Agent 呼叫並行**（general-purpose agent，各自獨立 context、互不阻塞）。**數量 = 通過 0-A Gate 的就緒平台數(最多 7,可更少)** —— ⚠️受阻 / ❌未連 的平台**不發 agent**(見本節末)。不要序列跑——序列會把多平台的延遲疊加成數倍。

每個 agent prompt 代入三個時間參數：

| 參數 | 預設 | 意義 |
|---|---|---|
| `{TODAY}` | 觸發當日（如 `2026-06-03`） | 今日窗的錨點；行程/到期日的「今天」 |
| `{FUTURE_N}` | `7` | 前瞻天數；未來窗 = `{TODAY}` → `{TODAY}+{FUTURE_N}` |
| 近 48h 窗 | `{TODAY}-2d` → now | 「剛發生、我可能還沒看到」的新事窗（未回 email、新 @mention、剛指派的 task、新開的 PR/review request） |

**三窗的分工**（每個 agent 都要同時覆蓋，不可只查其一）：
- **今日窗**：`{TODAY}` 當天的行程、到期、deadline。
- **未來窗**：`{TODAY}+1` → `{TODAY}+{FUTURE_N}`，抓需要提前準備的事（release、review、OKR、外部會議）。
- **近 48h 窗**：回頭看剛發生但「在等我」的——這是「不漏掉要回覆的事」的主力窗。

> 只有 **0-A 就緒 Gate 判為 ✅就緒** 的平台才發 agent。⚠️受阻 / ❌未連 的平台**不發 agent**，由主流程記入涵蓋聲明的盲區，不靜默跳過。

---

## 2. Pre-flight：就緒 Gate（fan-out 前）

fan-out 前對**每個已連平台**跑一次最小三關檢查，判定 **✅就緒 / ⚠️受阻 / ❌未連**。這道 Gate 是對抗「假完整」的核心——某平台讀不到卻照樣產一份看似完整的簡報，正是本 skill 要防的失敗模式。

**三關（每平台都要過）**：

1. **連線**：看系統提示該平台 MCP server（或 `gh` CLI）是否在線。斷線/未連的**不發 agent**。
2. **身份可讀**：取得「本人」身份——這是後續所有 `from:me` / `assigned to me` / `'me' in owners` 過濾的前提。身份取不到 = 無法判斷「與我相關」= 該平台降級為 ⚠️。
3. **讀取煙霧測試**：在今日窗內做「一次」最小查詢，確認讀得到且非被擋。

**處置表**：

| 判定 | 條件 | 處置 |
|---|---|---|
| ✅ 就緒 | 三關全過 | 發 fan-out agent |
| ⚠️ 受阻 | 連線 OK 但身份取不到 / 煙霧測試被擋（範圍未授權、權限不足、**內容被標籤封鎖**如 Google 檔的 AI-eligibility 標籤） | **不發 agent**；記入涵蓋聲明標「⚠️ 受阻（原因）」；該平台相關項目「可能不完整」 |
| ❌ 未連 | server 未連 / 斷線 | **不發 agent**；記入涵蓋聲明標「❌ 未連」 |

**身份煙霧測試 per platform（用什麼來確認本人）**：

| 平台 | 身份來源 | 讀取煙霧測試（今日窗一次最小查詢） |
|---|---|---|
| Gmail | 從寄件者 `me` 推得本人 email | search 近 24h 一封 thread |
| Slack | 本人 profile（name + user ID） | search 本人近期一則訊息 |
| Notion | `get-users` 找本人 | search 一頁近期頁面 |
| Asana | `get_me`（回 GID + workspace） | `get_my_tasks` 取一筆 |
| Google Drive | metadata 的 owner = 本人 | list recent 一個檔 |
| Google Calendar | `list_calendars` 取本人 primary email | list 今日一個 event |
| **GitHub** | `gh auth status` 回的 login，或 GitHub MCP 的 viewer/me | **全域** `@me` 讀取（`gh search prs --author=@me --limit 1`，**或** MCP viewer 列一筆）——**不要用 repo-local 指令**（見下「無目標 repo」陷阱）；**這關 GitHub 也納入 Gate**，不可跳過 |

> **GitHub 入 Gate 是本 skill 的關鍵設計**：工程角色的主證據（PR / review request / assigned issue）若不在 Gate 視野內，等於對 RD 結構性盲區。GitHub 用 `gh auth status` **或** GitHub MCP 任一條通路均可。

> **⚠️ 無目標 repo 陷阱（實測踩過）**：晨報是**跨 repo 的個人視角**,通常從任意 cwd 觸發，**那個 cwd 多半不是 git repo**。此時 `gh pr list` / `gh issue list` 這類 **repo-local 指令會 `fatal: not a git repository` 直接失敗**。Gate 與 fan-out 一律用**全域 `@me` search**(`gh search prs --author=@me` / `--review-requested=@me` / `gh search issues --assignee=@me`)——它不依賴本機 repo、且一次跨所有 repo。`gh auth status` 過了**不代表**任何 repo-local 指令可用,別把「auth OK」當成「repo 可讀」。

> **Gate ↔ Intake 循環依賴**（已知）：煙霧測試需要「今日窗」，但精確窗在 0-B Intake 才定。實作上先用粗略今日窗（`{TODAY}` 當天）跑 Gate，Intake 定案後 fan-out 再用精確窗。

> **🔑 身份 token 往下傳（省成本）**：Gate 第 2 關已取得每個平台的本人身份(Slack user ID、Asana GID + workspace、Notion self id、Gmail/Calendar/Drive email、GitHub login)。**把這些身份值直接寫進對應 fan-out agent 的 prompt**,agent 就不必再花一輪 round-trip 重抓身份(`get_me` / `get-users` / profile)。Gate 與 fan-out 對「本人是誰」只該問一次。fan-out 範本裡的「身份確認」步驟在身份已由 Gate 傳入時**可跳過**,只在 prompt 未帶身份時才現抓。

---

## 3. 共通 ToolSearch 雷區（每個 agent prompt 都要逐字寫進）

各平台 MCP 工具是 **deferred**——schema 未載入前無法呼叫。以下四條是每個 agent 都會踩的坑，**必須複製進每個 agent 的 prompt**：

1. **未先 ToolSearch 載 schema 直接呼叫 → InputValidationError**。deferred 工具只露出名字，沒有參數 schema；直接呼叫一定失敗。**先 ToolSearch 載入，再呼叫。**
2. **`select:工具全名` 精確載入優先**；失敗就退回**關鍵字搜尋**（`"slack"`, `"gmail"`, `"notion"`, `"asana"`, `"drive"`, `"calendar"`, `"github"`），把 `max_results` 開大（30–40）一次載齊一個平台的相關工具。
3. **server 前綴會因環境改變**——同一個 Gmail 工具在不同環境/帳號下前綴可能不同。**不要 hard-code 完整工具名當保證**；`select:` 找不到就一律退回關鍵字搜尋。本 playbook 各平台只列「工具用途 + 關鍵字」，**實際暴露的工具名以第一次跑時 ToolSearch 回傳為準**。
4. **斷線的 server 不再找**——系統提示會說明哪些 server 在線。對未連/斷線的 server 發 ToolSearch 是浪費 round-trip；Gate 已判 ❌未連的平台根本不該發 agent。

> **寫法建議**（放進每個 agent prompt 開頭）：「先 `ToolSearch` 用關鍵字 `"<平台>"` max_results 30 載入本平台工具；檢視回傳的工具名再呼叫。若某具名工具呼叫回 InputValidationError，表示 schema 未載——回去 ToolSearch 補載該工具全名。」

> **🧭 live 探索是「能做什麼」的唯一真相(總則 — 凌駕本檔所有負面註記)**:MCP 工具會改版。本 playbook 描述的是「**什麼有用**」和「**截至某日已知的怪癖/缺工具**」,**不是**永恆的能力邊界。**ToolSearch 當下回傳的工具清單,才是「現在能做什麼」的真相。** 規則:
> - 本檔說「某平台沒有 X 工具」時,那是**某個日期的快照**;若你這次 ToolSearch **看到了** X,**以 live 為準、用它**,別被舊註記擋住。
> - 反之本檔說「用某工具」但 live 沒有,也以 live 為準(該工具可能改名/下架)——退回關鍵字搜尋找替代。
> - WHY:負面斷言(「做不到 X」)過時會**靜默抑制**真實能力(你不會收到錯誤、只會默默少做);用「live 優先」當總則,就能保留有用的提示、又不被提示綁死。負面註記只是「省你今天空轉」的提示,不是天花板。

---

## 4. 七平台 sub-agent 範本

每個範本含：**載入字串 → 身份確認 → 搜尋策略 → 回傳結構化 markdown**。各平台另列**操作層 knowhow / 雷區**——這些是專家知識（踩過坑才知道），不是「Slack 是什麼」。

**共通回傳結構**（每個 agent 都用這個 markdown 骨架回傳，後續 triage 才好併）：

```markdown
## <平台> — fan-out 回傳
**身份**：<本人 email / user ID / login>（Gate ✅）
**涵蓋窗**：今日 {TODAY} + 未來 {FUTURE_N} 天 + 近 48h

### 相關項目（每筆含出處連結）
- [分類] <一句話事項> — <為何與我相關 / 為何現在重要> ｜ 連結：<canonical 深連結> ｜ 唯一識別碼：<id>
  - 分類 ∈ { 行程 · 要回覆 · 專案 · 未來 }

### 原始附錄
<撈到的原始紀錄精簡引文，供 triage 覆核，不進晨報>

### caveats
<本平台這次搜尋的偏誤 / 盲區 / 信心保留——如「Slack 搜尋偏近期」「Notion 作者不可靠」>
```

> **分類欄是給 triage 的 hint，不是最終定案**。fan-out 只負責「撈到 + 標出處 + 標原平台」；緊急度排序、升上晨報與否、跨日 delta 都交給 triage / continuity 步驟。

> **🧪 共用 Sanity-check(回傳前的合理性自檢，每個 agent 都套)**：這是一條**生成式規則**,取代「逐一窮舉雷區」——回傳前先問:
> 1. **「這平台平常活躍,今天卻回 0 / 異常少」→ 先當『查詢/過濾壞了』,換條件重試一次,不要當成『沒事』就回空。** (這一條同時涵蓋 Slack `after:` 回 0、Notion `created_by` 回 0,以及未來還沒踩到的同類查詢雷;比起列不完的雷區,這個自檢一條打一片。)
> 2. **數量爆量(某平台回上百筆)→ 多半是 query 太寬或撈到全員資料(非「我的」),收緊到「與我相關」再回。**
> 3. **「我確認不到的事」不要當事實**:讀取失敗、被截斷、身份比對不確定 → 降信心到「推論」並寫進 caveat(對應 prioritization-framework §3/§4)。
> 4. **連結要是真 URL**:回傳每筆的連結**必須是 `http(s)://...` 的真實網址**。若 API 回的是 **placeholder / 未解析的 token**(如字面 `htmlLink`、`<file-id>`、空字串)→ **不可當可點連結輸出**,改標「⚠️ 無直連」(對應 brief-templates 的無直連規則)。看到範本佔位符的形狀就送出 = 假的可點列。
> WHY:研究顯示 schema/格式約束只防得了「介面誤用」,防不了「**語意誤用**(搜錯東西、把空當沒事、把佔位符當連結)」——語意層才是真瓶頸,要靠這種「結果合不合理」的自檢補,不是靠更多欄位格式。

---

### 4.1 Gmail agent

**載入**：ToolSearch `"gmail"` max_results 30 → 取 search threads / get thread / list labels 用途的工具。
**身份確認**：從寄件者 `me` 推得本人 email（後續 `from:me` / `to:me` 過濾的基準）。

**搜尋策略**：
- **未回覆 thread（核心——「等我回的」）**：`to:me is:unread` 近 48h，以及 `to:me` 後我**沒有**回過的 thread（最後一封不是 `from:me`）。
- 近 48h 新進：`after:{TODAY}-2d`。
- 區分方向：`from:me`（我發出、可能在等對方）vs `to:me`（對方發來、可能等我）——**等我回的優先升級**。
- 未來窗：含日期/deadline 字樣的 thread（合約期限、會議邀請、release 時程）。

**Worked Example**(照抄這個形狀):
- 查詢:`to:me -in:sent newer_than:2d`(對方來信、近 48h)→ 過濾掉自動通知寄件者
- 回傳列:`[要回覆] <寄件者> — 合約條款待我確認(等 1 天) ｜ 連結:https://mail.google.com/mail/u/0/#inbox/<thread-id> ｜ 唯一識別碼:<thread-id>`

**操作層 knowhow / 雷區**：
- **過濾 newsletter / 自動通知雜訊寄件者**——電子報、`no-reply@`、`notifications@`、`support@`、HR/排程系統自動信會灌爆「要回覆」清單。建立黑名單 sender pattern，自動通知**不列入「要回覆」**（最多列「僅知會」）。
- **「未讀」≠「要回覆」,但可當弱補充訊號**：行銷信也未讀,所以要回覆 = 對方在 thread 裡向我提問 / 等我決定 / 指名我(靠語意判斷)。`is:unread` / 每封的 `labelIds` 帶 `UNREAD` 是**弱代理**——只代表「我還沒開過」,排序上**低於**語意判定的「指名我/問我」;過濾掉自動通知後可當「尚未處理」的補充訊號,不可單憑它判要回覆。(Gmail 已讀/未讀**可靠可查**:`is:read`/`is:unread` + labelIds,跟 Slack 取不到已讀狀態相反。)
- **同一 thread 多封**：以 thread 為單位回傳一筆，不要每封一筆灌量。

---

### 4.2 Slack agent

**載入**：ToolSearch `"slack"` max_results 30 → 取 search / read thread / read user profile 用途的工具。注意 search 通常有 **public-only** 與 **public+private(含 DM/Group DM)** 兩個工具——本 skill 要用**後者**(見下「DM/私訊優先」)。
**身份確認**：先讀本人 profile 取 name + user ID（`@mention` 比對要用 ID，不是顯示名）。

**搜尋策略**：
- **🔑 DM / 私訊也要搜,別只搜公開頻道(實測踩過,差點整份漏掉)**:單人晨報的「等我回」有很大一塊住在 **DM / Group DM / 私人頻道**。**預設就用 public+private 的 search 工具**(若該工具需使用者同意,在 Intake 一次取得授權);若只跑 public-only,很可能在私訊忙碌、公開頻道安靜的日子回**零命中**而交出「Slack 沒事」的假報告。
- **公開頻道同樣要看(不可只看私訊)**:**本人有加入的公開頻道**裡的訊息仍是主來源,尤其:① 那些頻道裡的 `@all` / `@channel` / `@here` 廣播(可能要你行動);② 公開頻道裡**直接 `@你`** 的訊息。public+private 工具會一起涵蓋這兩塊——重點是「私訊 + 我加入的公開頻道」都要搜,不是二選一。
- **對我提問的 @mention（核心）**：搜 `<@本人user ID>`——別人 at 我通常意味要我回應/決定。
- **未回 thread**：我被 at 的 thread 中，最後一則不是我發的 → 還沒回。
- **個人標記訊號(補充,訊號乾淨)**:用 `is:saved`(我**主動存的/稍後處理**)和 `has:pin`(置頂訊息)當補充來源——`is:saved` 尤其好,因為是我**自己標的「想處理」**,雜訊低,語意接近「等我回/要我處理」,可優先升。這兩個只是**補充**,核心仍是 @mention。
- 未來窗：含日期/release/排程字樣的訊息。

**Worked Example**(照抄這個形狀;注意:用 public+private 工具、**不帶 `after:`**):
- 查詢:public+private search `<@本人user ID>`(抓全量,回傳後程式端按時間過濾近 48h)
- 回傳列:`[要回覆] @你被問某數字能否今天確認(Group DM) ｜ 連結:https://<workspace>.slack.com/archives/<channel-id>/p<ts去點> ｜ 唯一識別碼:<ts>`

**操作層 knowhow / 雷區**：
- **⚠️ `after:` / `before:` 日期過濾不可信(實測踩過)**:帶 `after:<日期>` 的同一 query 可能回**零筆**,但拿掉日期就有結果——Slack 的 ts-based 日期過濾行為不穩,會**靜默漏尾**。可靠做法:**保留其他縮小範圍的條件**(`@你` / 關鍵字 / 頻道 scope / 結果上限 ~20 筆)、**只把 `after:`/`before:` 拿掉**,抓回那一小批後**在程式端按時間戳過濾到三窗**。注意這**不是**把整個 Slack 歷史搬回來——查詢本身仍受 @mention/關鍵字與預設筆數上限約束,量是有界的;只是別依賴日期運算子幫你框窗。
- **OR / boolean 不支援**:Slack search **沒有** AND/OR/NOT;空白分隔 = AND。多關鍵字 OR 查詢會回零命中。要查多個關鍵字就**拆成多次小查詢**,別寫 `A OR B`。
- **已讀/未讀 與 reminders:截至 2026-06 本 MCP 未暴露(別空轉,但以 live 為準)**:截至 2026-06,這個 Slack MCP 的工具清單裡**沒看到**「訊息已讀/未讀」狀態或 reminders(`/remind`)讀取工具(`slack_schedule_message` 是排「發訊息」,不是讀提醒)。**所以別花 round-trip 去硬找已讀狀態判「我看過沒」**——當下沒有。**但若你這次 ToolSearch 列出了已讀/reminders 類工具,以 live 為準、優先用它**(見 §3 live 探索總則)。能穩定用的個人標記是 `is:saved` 與 `has:pin`(見搜尋策略)。
- **搜尋近期偏誤**：Slack 搜尋偏重「近期 + 相關性」，近 48h 通常夠；但若要回看更早（早月）會被近期結果淹沒——需**逐頻道補 `during:<日期>`** 才撈得全。本 skill 多數窗是近 48h，影響小，但「未來窗」若含較早排定的事仍要注意。
- **permalink 形式**：回傳每筆都帶 permalink（見 §5），不要只給頻道名+時間——晨報要能一鍵點回那則訊息。
- **DM vs 頻道**：DM 裡的提問更可能「等我」；公開頻道的 @mention 要判斷是否真的需要我（有時只是 cc）。
- **thread 回覆深度 + 讀取失敗降級**：被 at 在一個 50 樓 thread 裡，要 read thread 看上下文才知道「在問我什麼」，不能只看那一則。**但 Group DM 的 `read_channel` / `read_thread` 可能回 Internal Server Error(實測踩過)**——讀不到完整 thread 時,改用「搜尋結果的時序」推斷「最後一則是否我發的」,並在 caveat 標明「未逐則翻完整 thread」;此時「等我回」只能掛**推論**信心,不可標確定(對應 prioritization-framework §3 的降級規則)。

---

### 4.3 Notion agent

**載入**：ToolSearch `"notion"` max_results 30 → 取 search / fetch / get-users 用途的工具。
**身份確認**：`get-users` 找本人。

**搜尋策略**：
- 近期 `edited` / `created` 時間戳落在三窗內的頁面。
- 與我相關 = 我是 owner、或我親建、或近期我編輯過的專案頁。

**Worked Example**(照抄這個形狀;靠 teamspace/owner,**不靠 created_by**):
- 查詢:`notion-search` query「<專案關鍵字>」+ `teamspace_id=<本人主場 teamspace>` → 用 ancestor/owner 判,不用作者欄
- 回傳列:`[專案] <某季度預算專案>(本人 owner) ｜ 連結:https://notion.so/<page-id> ｜ 唯一識別碼:<page-id>`

**操作層 knowhow / 雷區（作者陷阱——這是 Notion 最大坑）**：
- **⚠️ `created_by = 本人` 對「很少開新頁的人」本來就會回近 0(實測踩過)**：這**不是 API 壞掉**,而是**「相關 ≠ 我建立的」**——很多人在 Notion 是**協作 / owner / 編輯**,幾乎不自己開新頁。對這種使用者,用「我建立的」當主訊號會**抓到近乎空集合**,誤判成「沒有我的頁」。所以**別把 `created_by`(親建)當主要判定路徑**。(`last_edited_by` 也不宜當主訊號:一頁被誰最後碰過,不代表那是他的事。)
- **主策略改用 owner / teamspace / ancestor-path / 頁內署名 判讀**(親建只當「加分訊號」,不是門檻):
  - **本人主場 teamspace**：頁的 ancestor 落在「本人負責的 teamspace」(如個人的 Strategy & Data Team 空間)→ 高機率是你的事。
  - **owner / 頁內署名**：頁的 owner 屬性是本人、或頁內有「作者:本人」署名 → 以此判,**勝過** `created_by`。
  - **近期我編輯過**:在三窗內我實際編輯過的協作頁,也算相關(即使不是我建的)。
  - **明確剔除**:ancestor 落在**別人的 teamspace**(別的產品團隊)、或頁內署名是別人的——即使因關鍵字命中浮出、即使時間戳落窗,也**剔除並在 caveat 記一筆**(只看時間戳+命中度極易誤收)。
- **分兩類標清楚**:「(高信心)本人主場 / 親建 / owner」vs「(中信心)團隊撰、我協作或掛 owner」——對應 GitHub 的「本人作者 vs 本人 reviewer」(§4.7),triage 才能判「這是我的事還是我只是掛名」。
- 用 created/edited 時間戳過濾到三窗；別把半年前的老頁因為被誰碰一下就撈進來。
- **caveat 必標**:若本次 `created_by` 回近 0、改走 owner/teamspace 判讀,**在回傳的 caveat 明說**——讓使用者知道清單是用「擁有/協作/編輯」訊號建的,不是「我親手開的」。
- **❌ 無「瀏覽記錄」訊號可用**:不像 Google Drive 有 `viewedByMeTime`(§4.5),`notion-search` **只能**用 `created_date_range` / `created_by_user_ids` 過濾,**沒有「我最近造訪過哪些頁」的 per-user 瀏覽史**。所以「我常看的頁」這條在 Notion **無法**靠 API 取得;相關性只能靠 owner/teamspace/編輯時間 + 語意搜尋排序,別指望瀏覽記錄。

---

### 4.4 Asana agent

**載入**：ToolSearch `"asana"` max_results 40 → 取 get_me / get_my_tasks / search_tasks / get_project / get_task 用途的工具。
**身份確認**：`get_me` 回本人 GID + workspace + teams。

**搜尋策略**：
- **指派給我（核心）**：`get_my_tasks` 取**指派給本人**的 task。
- **即將到期 / 逾期**：due_on 落在今日窗 + 未來窗的；以及 due_on < `{TODAY}` 但 `completed = false`（逾期，最高緊急度）。
- **🔑 due 未維護的 fallback(實測踩過)**:很多人的 Asana **due date 普遍不維護**——`get_my_tasks` 可能回一堆 due 停在 1–2 年前、或 due=null 的進行中 task。**只靠 due_on 框窗會系統性漏掉「在做但沒設 due」的活躍工作**。所以除了 due_on,**也用 `modified_at` 近 N 天(預設近 7–14 天)抓最近真的有動的 task**,即使它沒有 due。把這類標「無 due、近期有動」交給 triage 判要不要升。
- 近 48h 新指派：assigned 時間或 created 在近 48h。
- `completed_on` 落在近 48h 的——用於 continuity-diff 判「✅已結」（昨天還在等、今天已完成）。

**Worked Example**(照抄這個形狀;due **和** modified_at 兩路都抓):
- 查詢:`get_my_tasks(completed_since="now")` 取未完成 → 再用 `modified_at` 近 14 天補抓「沒設 due 但有動」的
- 回傳列:`[要回覆] <某權限申請單> — 對方已完成、等你 close(due 已逾期) ｜ 連結:https://app.asana.com/0/0/<task-gid> ｜ 唯一識別碼:<task-gid>`

**操作層 knowhow / 雷區**：
- **`search_tasks` 上限 100 且不分頁**——一次查回最多 100 筆且**沒有翻頁游標**。若一個窗可能 >100 筆，**用多段日期窗序列查詢**（如未來 7 天拆成 `due_on` 逐 2–3 天一段），避免靜默漏尾。
- **due 普遍未維護要寫進 caveat**:若發現 task 的 due 多數停在過去/為 null,**在回傳 caveat 明說「時間窗策略對未維護 due 的看板無效,進行中工作可能漏列」**——這是誠實標盲區,不是靜默接受。
- **專案總任務數 ≠ 個人任務數**：`get_project` 回的是全員任務；要「我的事」必須自行 tally `assignee = 本人`。別把專案的 80 個 task 都當成我的待辦。
- **section / subtask**：to-do 可能藏在 subtask；母 task 顯示「進行中」不代表沒有指派給我的 subtask 到期。
- 回傳每筆帶 task URL（§5）。

---

### 4.5 Google Drive agent

**載入**：ToolSearch `"drive"` max_results 30 → 取 search files / list recent / get metadata / read content 用途的工具。
**身份確認**：用 metadata 的 owner 確認本人。

**搜尋策略**：
- 近期 `modifiedTime` 落在近 48h 且 **`'me' in owners`** + 工作關鍵字。
- **🔑 瀏覽記錄訊號(`viewedByMeTime`,實測可查)**:`search_files` 支援 `viewedByMeTime > '<近 N 天 RFC3339>'`。這撈出「**我最近一直在開、但不是我擁有、也不是我改的**」檔案——例如別人分享、我每天點進去看的 spec / 報表。這是 `owner=me` + `modifiedTime` 都會漏掉的**強相關訊號**(相關性 ≠ 擁有權 ≠ 編輯),對「協作型」使用者特別重要。把這類標「近期我常看、非我擁有」交給 triage。
- 與三窗相關的協作文件（會議筆記、spec、release doc）。

**Worked Example**(照抄這個形狀;含瀏覽記錄訊號):
- 查詢:`search_files` `viewedByMeTime > '2026-06-02T00:00:00Z' and not 'me' in owners`(我常看、非我擁有)
- 回傳列:`[專案] 我每天開的 release spec(非我擁有、近期常看) ｜ 連結:https://drive.google.com/file/d/<file-id> ｜ 唯一識別碼:<file-id>`

**操作層 knowhow / 雷區**：
- **被 AI-eligibility 標籤封鎖讀不到內容**：某些 Google 檔被組織標籤標記後，metadata 讀得到但 `read content` 被擋。此時**仍列入**該檔（標題+連結+「⚠️ 內容受標籤封鎖」），**不可因讀不到內容就靜默省略**——它仍是與我相關的存在，只是摘要不完整。
- **排除批次搬移誤觸時間戳**：整個資料夾被搬移/權限變更會把底下檔案的 `modifiedTime` 一起更新，造成「一堆舊檔看起來剛改」。**交叉看 `last modifying user`**——若不是我、且內容沒實質變化，多半是批次操作的假訊號，降權或排除。
- 排除圖片/影片/捷徑的雜訊；以「我近期實際在編的文件」為主。

---

### 4.6 Google Calendar agent

**載入**：ToolSearch `"calendar"` max_results 30 → 取 list_calendars / list_events / get_event 用途的工具。
**身份確認**：`list_calendars` 取本人 primary email。

**搜尋策略**：
- **今日 events**：`{TODAY}` 全天，照時間排序 → 晨報「當日行程」段的來源。
- **未來窗 events**：`{TODAY}+1` → `{TODAY}+{FUTURE_N}`，抓需提前準備的（外部會議、release、OKR review）。
- 每筆取 `htmlLink`（§5）。

**Worked Example**(照抄這個形狀;主動標重疊):
- 查詢:`list_events` timeMin={TODAY} timeMax={TODAY}+7,只看本人 primary、檢查 `responseStatus` 與時段重疊
- 回傳列:`[行程] <MM-DD> 10:30 週會 A(⚠️ 與 11:00 週會 B 重疊,需取捨) ｜ 連結:<htmlLink> ｜ 唯一識別碼:<event-id>`

**操作層 knowhow / 雷區**：
- **行程數 ≠ 出席**：受邀 ≠ 會去；要看 `responseStatus`（accepted / tentative / declined）。declined 的不該佔晨報行程版面。
- **排程時數 ≠ 實際（會議重疊）**：兩個會 `10:00` 撞時間 = 我只能去一個。**主動標出重疊** → 晨報提示「需取捨」（spec 示意的 `⚠️ 10:00 與 10:30 重疊`）。all-day / hold 區塊不要當成佔滿一天的會。
- **例行 vs 一次性**：standup / 1:1 / 週會 = 例行（標「例行」、低優先，除非當天有特殊議題）；一次性會議（決策會、外部 demo、release）= 高優先，常需準備 → 可能升上「今日焦點」。
- 空檔識別：抓出大塊無會空檔 → 晨報可建議「留給深度工作 / 焦點項」。

---

### 4.7 GitHub agent（核心平台）

> **GitHub 在本 skill 是核心，不是選配第七路**——給它與其他平台**對等的完整範本**。工程角色的主證據（PR / review / issue）必須進 fan-out 與 Gate。

**載入**：`gh` CLI 的**全域 search**(`gh search prs` / `gh search issues`)**或** ToolSearch `"github"` max_results 30 取 GitHub MCP 工具——兩條通路任一即可，以 Gate 通過的那條為準。
**身份確認**：`gh auth status` 回的 login，或 MCP 的 viewer。`@me` 在 `gh search` 裡可代本人。
**⚠️ 不要用 repo-local 指令**：`gh pr list` / `gh issue list` 需在 git repo 內執行;晨報從任意 cwd 跑、cwd 多半不是 repo,會 `fatal: not a git repository`。**一律用 `gh search ... --author=@me / --review-requested=@me / --assignee=@me`**——全域、跨 repo、不依賴 cwd。輸出加 `--json title,url,repository,updatedAt,number,state` 便於結構化回傳。

**搜尋策略（四類，對應不同「與我相關」語意）**：
- **我開的 PR**（`author:@me`，state:open）：等別人 review / 等 merge / CI 狀態 → 我的進行中產出。
- **等我 review（核心——「等我回的」）**：`review-requested:@me` + `reviewed-by:@me` 但仍 open 的 → 別人卡在我這關。**這是 GitHub 上最容易漏、最該升上焦點的一類。**
- **指派給我的 issue**：`assignee:@me state:open` → 我的待辦。
- **PR 待 merge / CI 狀態**：我開的 PR 若 CI 綠 + approved + 仍未 merge → 可能我自己卡著沒按 merge；CI 紅 → 我要修。

**Worked Example**(照抄這個形狀;全域 search、**非** repo-local):
- 查詢:`gh search prs --review-requested=@me --state=open --json title,url,repository,number`(別人等我 review,最該升焦點那類)
- 回傳列:`[要回覆](reviewer) owner/repo#48 等我 review ｜ 連結:https://github.com/owner/repo/pull/48 ｜ 唯一識別碼:owner/repo#48`

**操作層 knowhow / 雷區**：
- **區分「本人作者」vs「本人 reviewer」**（對應 Notion §4.3 親建 vs owner）：
  - `author:@me` = **我的產出**，等別人 → 我可能在等回饋（不一定要我立即動）。
  - `review-requested:@me` = **別人的產出等我** → **要我動**，升級為「要回覆/要處理」。
  - 這兩類在晨報的動作語意相反，**絕不可混為一筆**。
- **commit 數 ≠ 貢獻量**：squash / rebase merge 會把多個 commit 壓成一個——用 commit 數判「我做了多少」會嚴重失真。fan-out 以 **PR / review / issue 為單位**回傳，不以 commit 計量。
- **跨 repo 用全域 search**：`@me` 全域 search（`gh search prs --author=@me` 等）一次跨所有 repo,不需先知道 repo 名、不需在 repo 內——注意只納入我實際參與的 repo，排除我只是 watch 的。
- **mention 盲區**：`gh search` 不涵蓋「別人 @你但未正式 request review / 未 assign」的 PR 留言或 issue 提及。這類可能漏接;需要時另查 `--mentions=@me` 或通知串,並在 caveat 標明此盲區。
- 回傳每筆帶 PR/issue URL（§5）。

---

## 5. 各平台 canonical 深連結形式表

讓**完整事項表每一列都可點回原始紀錄**——這是「可點即處理」success criteria 的硬需求。fan-out 回傳時每筆都要附 canonical 深連結；**無單一直連的項目仍列入，連結欄標「⚠️ 無直連」，不靜默省略**。

| 平台 | canonical 深連結形式 | 備註 |
|---|---|---|
| Gmail | thread 永久連結，或 `rfc822msgid:<message-id>` 搜尋連結 | thread 永久連結最穩；`rfc822msgid:` 跨帳號可定位單封 |
| Slack | message permalink `https://<workspace>.slack.com/archives/<channel-id>/p<ts>` | `<ts>` 去掉小數點接在 `p` 後；thread 內訊息加 `?thread_ts=` 參數 |
| Notion | page URL `notion.so/<page-id>`（32 位 hex，可含 `-` slug 前綴） | fetch 回的 URL 直接用 |
| Asana | task URL `app.asana.com/0/<project-gid>/<task-gid>` 或 project URL | task GID 是 continuity join key 的一部分 |
| Google Drive | 檔案連結 `drive.google.com/file/d/<file-id>` 或 metadata 的 `webViewLink` | 內容被標籤封鎖時連結仍有效（人點得進去，只是 agent 讀不到） |
| Google Calendar | event `htmlLink`（`get_event` / `list_events` metadata 直接提供） | 不要自己拼——用 API 回的 `htmlLink` |
| GitHub | PR URL `github.com/<owner>/<repo>/pull/<n>`；issue URL `.../issues/<n>` | `gh` / MCP 回的 `html_url` 直接用 |

> **深連結即 join key 的一部分**：唯一識別碼（thread ID / message ts / page ID / task GID / file ID / event ID / PR number）是隔天 continuity-diff 的 JOIN 主鍵。fan-out 回傳時**連結 + 唯一識別碼都要帶**——連結給人點，識別碼給機器 join。

---

## 6. 同源去重提醒（fan-out 回傳時附原平台）

**一個事實常在多平台留下痕跡**，最典型：

- GitHub PR 開啟/合併 → **自動轉貼到 Slack** 某頻道 → 可能**同時觸發 Asana** 的關聯 task 狀態變化。
- Calendar 會議邀請 → 同時是 Gmail 裡的一封邀請信。
- Notion spec 更新 → Slack 通知 + Asana task 連結。

**fan-out 階段的責任邊界**：
- fan-out **不做去重**——每個 agent 只負責自己平台，照實回傳，**並在每筆附上「原平台」**。
- **不可因為跨平台都看到就灌高信心**——「GitHub + Slack 都提到這個 PR」若其實是 GitHub 自動轉貼到 Slack，那是**單一事實的回音**，不是兩個獨立來源的交叉印證。把它當成 ✅（2+ 平台印證）會虛報信心。
- **去重 / 信心判定交給後續 triage 的 continuity / dedup 步驟**——fan-out 只要保證「附了原平台 + 唯一識別碼」，後續就能識別「這三筆其實是同一個 PR 的三處回音」，合併為單一事實、給出正確信心（單一來源 = ⚠️，真·獨立雙來源才 = ✅）。

> **一句話**：fan-out 撈全、標源、不判重；triage 判重、定信心。把「是不是同一件事」的決定權留給有全局視野的 triage 步驟。

---

> **回到主流程**：就緒平台的 agent 全部回傳後，主流程進 triage（緊急度 × 相關性，見 `prioritization-framework.md`）→ continuity-diff（ID-join 昨日 CSV + live 重驗）→ 產出雙產物（見 `brief-templates.md`）。
