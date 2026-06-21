# daily-brief v0.1 — brainstorming brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff)
> **Date**: 2026-06-03
> **Author**: kouko + Claude (Opus 4.8 / 1M) session
>
> **Consumes**:
> - `~/kouko-obsidian-vault/research/2026-06-01 performance-evidence-audit skill 結構與框架研究.md` — 機制與框架研究來源(就緒 Gate / 平行 fan-out / 查證鏈 / 信心分級的設計分析;第七章 GitHub 盲區的批判)
> - `~/Downloads/performance-evidence-audit/{SKILL.md, references/*}` — **機制母體**:本 skill 鏡像其跨平台存取設計(0-A Gate、ToolSearch deferred 載入、6 平台 fan-out、出處引用鏈、read-only/draft-only 分層)
>
> **Status**: 5-axis exploration 完成;架構分岔已由 user 拍板(raw MCP self-contained);輸出產物格式(雙產物 + 動態焦點 + **跨日延續性**)已逐輪收斂定版。**跨日延續性(文件累積機制)已由 user 拍板折進 v0.1**(2026-06-03)。等 user 過目後進 `writing-plans`。

---

## Problem (Axis 1 — JTBD)

**Job story**: 當我(kouko)每天開工時,工作脈絡散在 7 個系統(Gmail / Slack / Notion / Asana / Google Drive / Google Calendar / GitHub)——我想要 agent **自動掃過每個我有連 MCP 的平台,把與我相關的事整理成一份可信、附可點連結的單一晨報**,讓我在 60 秒內讀回今天的全貌,**不漏掉任何需要我回覆或處理的事**,且每條都能一鍵點回原始紀錄直接處理。

**這個 skill 要防的失敗模式**:
1. **開工前要切 4+ 次脈絡**(信箱→行事曆→任務→Slack→…),啟動成本高,且容易漏掉冷門平台的待辦。
2. **「假完整」**:某平台沒連上或讀不到,卻照樣產一份看似完整的簡報,讓使用者誤以為沒有遺漏(performance-evidence-audit 用 0-A Gate 對抗的正是這個)。
3. **無出處的摘要**:給了一句「David 在等你回合約」卻沒連結,使用者還要自己回去找——簡報變成「又一個要查的地方」而非「行動入口」。
4. **PDB 的張力**:純 curated 簡報會「狠下心省略」(PDB 原則:客戶買的是分析不是功課),但使用者怕漏 → 用**雙產物**(curated 晨報 + 零省略完整表)化解。

## Users (Axis 2)

- **Primary (v0.1 dogfood)**: kouko 本人,工程/管理混合角色,每日開工時。
  - **工程角色 ⇒ GitHub 是核心而非選配**:研究筆記第七章點出 source skill 把 GitHub 設為「選配第七路」對 RD 是結構性盲區(主證據 PR/commit/review 不在 Gate 視野內)。本 skill v0.1 **把 GitHub 拉進核心 7 平台**。
  - 工作語言 zh-TW / JP / EN — 觸發詞與輸出需多語。
  - 環境:Claude Code,連了部分或全部上述 MCP server。
- **Secondary (v0.2+)**: 其他 monkey-skills 使用者。**Zero-config / 優雅降級**是核心設計——只要連了某平台 MCP 就納入,沒連就在涵蓋聲明標盲區,不硬要求全部 7 平台。
- **User non-goal**:
  - NOT 績效回顧/自評(那是 source skill `performance-evidence-audit` 的回顧型用途——同機制、反方向時間軸)。
  - NOT 自動回覆/代送(read-only + draft-only,只給連結讓人去處理)。
  - NOT 多人/團隊簡報(單一使用者視角)。

## Smallest End State (Axis 3) — v0.1

**One-paragraph summary**: 使用者觸發(slash 或自然語言:「今天的簡報」/「daily brief」/「morning brief」/「今日まとめ」)→ skill 先跑 **0-A 就緒 Gate**(對每個已連平台驗 連線/身份/讀取煙霧測試)+ **0-B Intake**(確認未來窗 N、排除主題、輸出位置)→ **平行 fan-out**(每個就緒平台一個 Agent,各自 ToolSearch 載 deferred 工具、廣度搜索近 48h + 今日 + 未來 N 天)→ **triage**(緊急度 × 相關性)→ 在指定資料夾產出**兩個檔案**(draft-only):curated 晨報 + 零省略完整事項表(+ 選配 CSV)。

**v0.1 納入**:

| 項目 | 說明 |
|---|---|
| 0-A 就緒 Gate + 0-B Intake | 直接搬 source skill;Gate 清單加 GitHub |
| 7 平台 raw MCP 平行 fan-out | Gmail / Slack / Notion / Asana / Drive / Calendar / **GitHub**;各 agent 自行 ToolSearch 載 deferred 工具 |
| **雙產物輸出**(日期前綴累積) | `2026-06-03_晨報.md`(curated)+ `2026-06-03_完整事項.md`(零省略表)+ `2026-06-03_完整事項.csv`(**核心機讀 — 隔天 delta 的 join key**) |
| 晨報 6 段 + **動態焦點** | **自上次以來(延續性)** / 今日焦點(門檻驅動,非固定 N)/ 當日行程 / 要回覆·要處理 / 進行中專案現況 / 未來 N 天 |
| **跨日延續性**(文件累積) | fan-out 前讀「日期<今天的最近一份」CSV → 用唯一識別碼 JOIN → 算 🆕新增/⏳仍在等(已N天)/✅已結/🔄狀態變化;**以 live 平台重驗為準,不信昨日文字** |
| 出處可點深連結 | **每一列**都帶 canonical 深連結(無單一來源→列入但標「⚠️ 無直連」,不靜默省略) |
| 信心標 | ✅ 2+ 平台交叉印證 / ⚠️ 單一來源 / 推論 |
| 字數上限 | 晨報設長度天花板(JP 實務圈反覆點名:無上限 = AI 回一面牆) |
| read-only / draft-only | 只讀、寫單一本機資料夾、不代送、不自動回覆、不寫回官方系統 |

**Success criteria**:
1. **零省略**:完整事項表涵蓋 fan-out 撈到的每一筆,過濾只決定「誰被升上晨報」,不決定誰被丟棄。
2. **可點即處理**:每列深連結點下去直接開到那條原始紀錄/對話。
3. **誠實涵蓋**:Gate 結果寫進兩份檔案開頭;盲區明標。
4. **動態焦點不硬湊也不靜默截斷**:0 件就明說「可專注深度工作」;>軟上限就加「高負載」橫幅但全列。
5. **優雅降級**:沒連的平台不報錯,記盲區照常產出其餘。
6. **延續性 grounded**:延續狀態以 ID 去 live 平台重驗,不相信昨日文字(防幻覺 carry-forward);首次跑無對照則跳過延續段、跳天標「距上次 N 天」。

**Non-criteria(v0.1 明確不做)**:
- ❌ 獨立 state 檔(last-run + seen-IDs)——改用**文件累積 + 讀最近一份 CSV** 達成跨日 delta,不另設 state 格式(真 delta 已折進 v0.1)。
- ❌ 排程「每天早上」——harness 層(`/schedule` / cron / Cowork),不在 skill 內。
- ❌ 推送到 Slack/Notion/email、多格式(Docs/Office)輸出。
- ❌ self-eval / 品質迴圈。
- ❌ 寫回任何官方系統、代送回覆。

## Current State Evidence

`N/A — greenfield`(新 skill,不修改任何現有檔案;純加法)。但有明確 touchpoints 與模板基礎:

- **Forward(機制模板)**: `~/Downloads/performance-evidence-audit/SKILL.md` + `references/{platform-search-playbook,analysis-framework,output-templates}.md` — 本 skill 鏡像其 0-A Gate(L36-56)、fan-out(L66-71)、ToolSearch 雷區(playbook L13-18)、出處引用鏈(output-templates 全文)。**不是 fork**:時間軸與分析目標不同,版型重寫。
- **Forward(repo skill 結構先例)**: monkey-skills 內既有 toolkit 的扁平結構(SKILL.md + 單層 references/)。frontmatter 慣例:data/CLI 型 skill(collab-toolkit / gws-toolkit)只用 `name`+`description`(+`allowed-tools`);framework 型才加 `source_book`。本 skill 屬 data/aggregator 型 → 不需 `source_book`,但建議加 `tags` + `related_skills`。
- **Forward(房屋風格)**: read-only、locale-independent、zh-TW/JP/EN 描述、反模式清單、hard-gate ——整個 monkey-skills 家族慣例。
- **Reverse(SSOT/歸屬未定)**: skill 放哪裡 = **Open Question**(見下)。候選:新 toolkit `briefing-toolkit`、或併入既有 toolkit。**不**複合 collab/gws-toolkit(user 已選 raw MCP 自包含)。
- **Error**: fan-out agent 對「平台讀不到」要降級(記盲區),不是丟例外——沿用 source skill Gate 處置表(✅/⚠️/❌)。
- **Data**: 全程 read-only 跨平台讀;寫單一本機資料夾(MD + CSV);v0.1 無跨次持久化(delta 延後)。
- **Boundary**: 7 個 MCP server 邊界(各自 OAuth/權限);唯一寫入邊界 = 本機檔案系統(draft-only)。
- **Evidence paths**:
  - `~/Downloads/performance-evidence-audit/SKILL.md`(機制母體)
  - `~/Downloads/performance-evidence-audit/references/platform-search-playbook.md`(fan-out 範本 + ToolSearch 雷區)
  - `~/kouko-obsidian-vault/research/2026-06-01 performance-evidence-audit skill 結構與框架研究.md`(設計分析 + 第七章 GitHub 批判)
  - monkey-skills `CLAUDE.md` §Skill Structure(扁平 subfolder 規則、~6k token 預算)

## Alternatives Considered (Axis 4 — research-grounded)

### 架構分岔(已拍板)

| 方向 | 取捨 | 判定 |
|---|---|---|
| **A. 自包含 raw MCP + ToolSearch**(鏡像 source skill) | ＋任何人連了 MCP 就能用、可獨立發布、各平台優雅降級;－與 collab/gws-toolkit 部分功能重疊 | ✅ **user 選定(2026-06-03)** |
| B. 複合既有 toolkit(collab + gws) | ＋DRY;－綁死此 repo、使用者須先裝 toolkit、GitHub 無對應 toolkit 仍要 raw MCP → 變混合 | ❌ |

### 業界做法(WebSearch,EN + JA,2026-06-03)

1. **President's Daily Brief(撰寫 tradecraft)** — 決策者簡報黃金標準。
   - **BLUF**:開頭即「是什麼/為何現在/為何重要/接下來」,不埋。
   - **狠取捨**:約一頁、6–7 短目;「客戶買分析不是功課」。
   - 每條先答 key intelligence question(對你、現在為何重要)。顯式標信心。零容錯。
   - 來源:[Cipher Brief — What I Learned Writing for the PDB](https://www.thecipherbrief.com/column_article/what-i-learned-writing-for-the-presidents-daily-brief)、[Wikipedia — PDB](https://en.wikipedia.org/wiki/President%27s_Daily_Brief)
2. **Anthropic 官方 Cowork recipe「Build a daily briefing across your tools」** — 分區:儀表板告警(紅/下滑)/ 被 @ threads(含完整對話)/ 沒被 tag 但與你任務相關的 threads / 本週任務與 blockers(到期日+依賴);平行查詢、在地處理、每條連回 thread。
   - 來源:[claude.com — Build a daily briefing across your tools](https://claude.com/resources/use-cases/build-a-daily-briefing-across-your-tools)
3. **商用品類**(alfred_ / digest.ai / DailyStack / Gemini Daily Brief)收斂四件套:收件匣 triage + 緊急度評分 + 任務抽取 + 行事曆脈絡 → 單一晨報,跨 20+ 工具。
   - 來源:[alfred_ — Best AI Daily Briefing Tools 2026](https://get-alfred.ai/blog/best-ai-daily-briefing-tools)、[Composio — Top Cowork Skills 2026](https://composio.dev/content/top-cowork-skills)
4. **日本實務圈 knowhow**(note.com 多篇實戰):
   - **必設字數上限**(每段 ≤300 字 / 全文 ≤5000 字),否則 AI 回一面牆——反覆被點名的最大坑。
   - 收斂「今日 3 件聚焦」;6 段(差分/今日行程/要對應郵件/案件狀態/聚焦 3 件/學習備忘);條列、丟 Slack DM。
   - 來源:[note.com — 始業前ブリーフィングを15分で構築](https://note.com/nobu_0215/n/n7e711b1737c9)、[note.com — 朝起きたらSlackにAIのブリーフィング](https://note.com/sabori_ai/n/n374517e9ac89)

**EN/JA 一致性**:兩語都指向「BLUF + 狠取捨 + 字數上限 + 連回原始 + 收斂焦點」。**分歧點**:JP 圈幾乎都把產物推到 Slack DM(排程外掛),EN 商用工具多為獨立 dashboard/email——印證「排程/遞送是 skill 外的 harness 層」這個切分。

**My take**: 採 PDB 的「狠 + BLUF + 信心標」當晨報紀律,採 Cowork recipe 的分區當骨架,採 JP 的字數上限當硬規則;用**雙產物**化解 PDB「省略」與 user「零省略」的張力。Conditional reversal:若 dogfood 發現 7 平台量太大讀不完,先收緊晨報門檻(而非砍完整表)。

## Decision

**Build `daily-brief` v0.1** 為自包含 skill,鏡像 `performance-evidence-audit` 的跨平台存取機制(0-A Gate + 0-B Intake + 7 平台 raw MCP 平行 fan-out + ToolSearch deferred 載入 + 出處引用鏈 + read-only/draft-only),但**時間軸翻轉為前瞻**(今日 + 未來 N 天 + 近 48h)、**分析目標改為 triage**(緊急度 × 相關性)、**輸出改為雙產物**(curated 晨報 + 零省略完整事項表 + **核心 CSV**),並以**文件累積**達成跨日延續性(每次讀「日期<今天的最近一份」CSV,用唯一識別碼 JOIN 算 delta,**以 live 平台重驗為準**)。GitHub 從 source skill 的「選配第七路」**升為核心平台**。今日焦點採**動態門檻**(非固定 N):下限 0(明說無焦點)、軟上限 ~5(超過加高負載橫幅但全列、不截斷)。晨報設字數上限。每列帶可點深連結。

**不做**:獨立 state 檔(改文件累積)、排程(harness 層)、推送/多格式、self-eval、寫回官方系統。

**Skill 結構**:
```
daily-brief/
├── SKILL.md                         入口 + 核心原則 + 工作流(Gate→Intake→fan-out→triage→雙產物)
└── references/
    ├── platform-search-playbook.md  7 平台(含 GitHub)fan-out 範本 + ToolSearch 雷區
    ├── prioritization-framework.md  ★新:緊急度×相關性 triage + 動態焦點門檻 + 「需回覆」啟發式 + 延續性 diff(ID-join + live 重驗)
    └── brief-templates.md           ★新:晨報版型 + 完整事項表版型 + 涵蓋聲明
```

## Out of Scope (v0.1)

- **獨立 state 檔**(last-run + seen-IDs)— 改用**文件累積 + 讀最近一份 CSV** 達成跨日延續性(已折進 v0.1),不另設 state 格式。
- **排程「每天早上」** — harness 層(`/schedule` / cron / Cowork scheduled task);SKILL.md 只**註明**怎麼疊,不內建。
- **遞送**(推送到 Slack/Notion/email DM)— v0.1 只產本機檔。
- **多格式輸出**(Google Docs / Office)— v0.1 只 MD + CSV。
- **self-eval / 品質迴圈、A/B 版型測試** — dogfood 後再說。
- **寫回官方系統 / 代送回覆 / 自動行動** — 永久 out of scope(read-only + draft-only 是安全紅線)。
- **多人/團隊簡報** — 單一使用者視角。

## What Becomes Obsolete (Axis 5)

- **每天手動切 7 個工具開工的習慣** — 這是 JTBD 要消滅的「啟動成本」。**非 same-PR 可刪**(在使用者肌肉記憶裡,不在 code);skill 上線 + 養成觸發習慣後自然退役。
- **臨時「幫我看一下今天有什麼事」式 prompt** — 同上,靠 skill description 收編路由。
- 注意:本 skill 基本是**純加法**(新能力),無現有 code 變 obsolete——這在 Axis 5 是個旗標,但此處成立(是新能力,非補既有 API 缺陷),非 YAGNI。

## Output Artifact Specs(定版 — writing-plans 直接用)

### 文件累積 + 延續性模型
輸出資料夾 = append-only 每日台帳(日期前綴,扁平):
```
<專案資料夾>/
├── 2026-06-01_晨報.md  + 2026-06-01_完整事項.md / .csv
├── 2026-06-02_晨報.md  + ...
└── 2026-06-03_晨報.md  ← 今天;產生前讀「日期<今天的最近一份」
```
工作流新增兩步:
1. **continuity-load**(fan-out 前):定位日期<今天的最近一份 → 讀其 `.csv`(join key)+ 焦點/未來段。無 prior → 標「首份簡報,無對照」並跳過延續段;跳天 → 讀最近一份並標「距上次 N 天」。
2. **continuity-diff**(triage 後):今日項目用唯一識別碼 JOIN 昨日 CSV → 🆕新增 / ⏳仍在等你(已 N 天)/ ✅已結 / 🔄狀態變化。**硬原則:以 ID 去 live 平台重驗為準,不信昨日文字(防幻覺 carry-forward)。**

### `01_晨報.md`(curated,PDB 風格)

填示意資料的長相(非真實資料):

```markdown
# ☀️ 每日簡報 — 2026-06-03(週三)
> 收件人:kouko ・ 產生:08:00 ・ 涵蓋窗:今日 + 未來 7 天 + 近 48h 新事
> 資料源涵蓋:✅ Gmail / Slack / Asana / Calendar / GitHub　⚠️ Notion(被 AI-eligibility 標籤擋)　❌ Drive(未連)
> ⚠️/❌ 平台為今日盲區,相關項目可能不完整。

## 📈 自上次以來(對照 06-02,1 天前)
- ✅ 已結:`payments-api#482` 昨日請你 review → 今天已 merged
- ⏳ 仍在等你(已 2 天):#design logo 改版確認 — 還沒回
- 🆕 新發生:法務 NDA 用印(推測等你)

## 🎯 今日焦點(門檻驅動 — 動態)
1. **10:00 路線圖定案前先拍板 Q3 優先序** — 三提案未收斂,會上要你定。 [Asana ↗](url) ✅
2. **回 David 合約條款(已等 1 天)** — 他卡在你這條才能往下。 [Gmail ↗](url) ✅
3. **`payments-api#482` 等你 review** — CI 綠、阻擋 Bob 部署。 [GitHub ↗](url) ✅

## 📅 當日行程
- `09:30–09:45` Daily standup(例行) [Cal ↗](url)
- `10:00–11:00` **Q3 路線圖定案**(要準備→焦點①) [Cal ↗](url)
- ⚠️ `10:00` 與 `10:30 客戶 demo` 重疊 — 需取捨 [Cal ↗](url)
- 🟢 空檔 `11:00–14:00` — 建議留給焦點③ + 深度工作

## ✉️ 要回覆・要處理(依緊急度)
| 來源 | 事項 | 動作 | 🔗 | 信心 |
|---|---|---|---|---|
| Gmail | David — 合約條款 Q(等 1 天) | 需回覆 | [↗](url) | ✅ |
| Slack | #design @你 — logo 改版要你確認 | 需回覆 | [↗](url) | ✅ |
| Gmail | 法務 — NDA 用印(推測等你) | 需確認 | [↗](url) | 推論 |

## 🚧 進行中專案現況
- **結帳改版**:API PR 待你 review(焦點③);前端進行中。 [GitHub ↗](url) [Asana ↗](url) ✅
- **Logo 改版**:等你在 #design 確認方向。 [Slack ↗](url) ⚠️

## 🔭 未來 7 天重要事項
- `06-05(五)` 結帳改版上線 — 你是 release owner。 [Asana ↗](url) ✅
- `06-09(一)` 季度 OKR review — 需準備團隊進度。 [Cal ↗](url) ✅

---
> 📋 完整 N 筆事項(零省略、可點處理)→ `02_完整事項.md`
> 信心:✅ 2+ 平台交叉印證 ・ ⚠️ 單一來源 ・ 推論=由情境推得
```

**動態焦點規則**(寫進 prioritization-framework):
- 納入條件(任一):今天是 deadline / 會卡住別人 / 不處理今天有後果 / 高槓桿決策。
- 下限可為 0 → 明說「今日無關鍵焦點,可專注深度工作」,**不硬湊**。
- 軟上限 ~5 → 超過加「⚠️ 今日高負載:N 件」橫幅,**全部保留不靜默截斷**;低於門檻的下推到各分段。

### `02_完整事項.md`(零省略,可點處理)

依「重要度」降序的 markdown data table,**每一列都帶可點深連結**:

```
# | 重要度 | 分類 | 平台 | 標題 | 🔗連結 | 日期/期限 | 動作 | 一句話 | 信心
```
- 分類:行程 / 要回覆 / 專案 / 未來 N 天
- 動作:需回覆 / 需準備 / 僅知會
- 信心:✅ / ⚠️ / 推論
- 硬規則(鏡像 source skill「無出處不寫」):無單一來源的項目仍列入,連結欄標「⚠️ 無直連」,不省略。

### `02_完整事項.csv`(**核心 — 隔天 delta 的 join key**)
鏡像 source skill 索引 CSV:`編號,重要度,分類,平台,標題,唯一識別碼,連結,日期,動作,一句話,信心`(逗號分隔,避免值內逗號)。**唯一識別碼欄 = 隔天延續性分析的 JOIN 主鍵 → 不可省略。**

### 每個平台的 canonical 深連結形式(寫進 playbook)
| 平台 | 連結形式 |
|---|---|
| Gmail | thread 永久連結 / `rfc822msgid:` |
| Slack | message permalink `https://<ws>.slack.com/archives/<ch>/p<ts>` |
| Notion | page URL `notion.so/<id>` |
| Asana | task / project URL |
| Drive | 檔案連結 |
| Calendar | event `htmlLink` |
| GitHub | PR / issue URL `github.com/<repo>/pull/<n>` |

## Key Risks / 難點

1. **相關性過濾**是核心品質問題。回顧型有「期間」當邊界;每日跨 7 平台會爆量,必須狠過濾到「與我相關、可行動、近期」。**雙產物 + 字數上限**已降此風險(完整表零省略,過濾只決定升上晨報者)。
2. **「需回覆」偵測**只能啟發式(對我提問的 @mention、等我回的 email、指派給我快到期的 task),**必標信心,不可宣稱確定**。
3. **延續性的幻覺 carry-forward**:若昨日簡報有幻覺項,今日恐一路 carry-forward。緩解 = continuity-diff 以 ID 去 live 平台重驗(昨日 CSV 只給「要追哪些 ID」,不給事實)。跳天 / 首次跑需優雅處理(已列 success criteria 6)。
4. **成本/延遲**:7 平行 agent 每早跑,比偶爾稽核重;可接受但需註明。
5. **Gate ↔ Intake 循環依賴**(source skill 既有):Gate 煙霧測試需「期間」,但期間在 Intake 才問 → 實作上先有粗略今日窗才驗。

## Open Questions(進 writing-plans 前需 user 簽核)

1. **Skill 放哪裡?** 新 toolkit `briefing-toolkit`(若預期之後會長出 weekly-brief / inbox-zero 等姊妹)vs 暫放某既有 toolkit。**建議**:單一 skill 不開新 toolkit(比照 recap 併入既有的決策),除非預期家族成長。← 需 user 定。
2. **晨報純文字 vs emoji 分區圖示** — 示意用了 emoji;有些人偏好純文字。**建議**:emoji 區隔(掃讀快),可加 SKILL.md 選項關閉。← 需 user 確認。
3. **未來窗 N 預設值** — 示意用 7 天。**建議** 7,Intake 可改。← 低風險,預設即可。
4. ~~動態焦點~~ — **RESOLVED**:門檻驅動 + 下限 0 + 軟上限 ~5 不截斷。
5. ~~架構~~ — **RESOLVED**:raw MCP 自包含。
6. ~~完整表是否含連結~~ — **RESOLVED**:每列必含可點深連結。
7. **輸出資料夾佈局** — 扁平日期前綴(`2026-06-03_晨報.md`)vs 每日子資料夾。**建議**扁平(好 grep、好排序、continuity-load 好定位「最近一份」);user 在 Intake 指定根資料夾。← 低風險,預設即可。
8. ~~跨日延續性~~ — **RESOLVED**:文件累積機制折進 v0.1;CSV 升核心(join key);晨報加「自上次以來」段;工作流加 continuity-load + continuity-diff;硬原則 live 重驗防幻覺。

## Handoff to writing-plans

Open Questions 1–3(+7)解決後,`writing-plans` 消費本 brief。預期原子任務數:**~7–10**(>5 → SDD 適用)。建議拆解:

1. `daily-brief/SKILL.md` — frontmatter(多語觸發)+ 核心原則 + 工作流骨架(Gate→Intake→**continuity-load**→fan-out→triage→**continuity-diff**→雙產物)+ 反模式。
2. `references/platform-search-playbook.md` — 7 平台(含 GitHub)fan-out 範本 + ToolSearch 雷區 + canonical 連結形式表。
3. `references/prioritization-framework.md` — 緊急度×相關性 triage + 動態焦點門檻 + 「需回覆」啟發式 + 信心模型 + **延續性 diff(ID-join + live 重驗 + 4 狀態)**。
4. `references/brief-templates.md` — 晨報版型(含「自上次以來」段)+ 完整事項表版型 + CSV schema(含唯一識別碼 join key)+ 涵蓋聲明 + **日期前綴命名/累積規則**。
5. GitHub fan-out agent 範本(`author:@me` / `reviewed-by:@me` / assigned issues / PR 待 review;區分本人作者 vs reviewer)。
6. 0-A Gate 加 GitHub 就緒檢查(`gh auth status` 或 MCP + 目標 repo 讀取煙霧測試)。
7. 多語 README(EN / JA / zh-TW)— 比照 repo 新 skill 慣例(若 user 決定要)。
8. SKILL.md 註記排程外掛方式(`/schedule` / cron / Cowork)。
9. **continuity-load + continuity-diff 工作流**(SKILL.md 內):定位最近一份、讀 CSV、ID-join、4 狀態判定、live 重驗、首次/跳天降級。
10. Dogfood:對 kouko 真實帳號跑**連兩天** v0.1,驗證雙產物 + 連結可點 + 涵蓋聲明 + **第二天的「自上次以來」延續性正確**(已結/仍在等/新發生)。
