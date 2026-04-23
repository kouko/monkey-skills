# PRODUCT-SPEC — slides-toolkit

Cross-domain product spec for the `slides-toolkit` plugin in the
`monkey-skills` repository. Scope: business + design + engineering
direction at the product level. Technical module design, interface
contracts, and data flow live in `TECH-SPEC.md` (code-team ownership).

- Spec type: PRODUCT-SPEC (planning-team ownership)
- Target plugin: `slides-toolkit`
- Status: MVP direction, frozen after 4-round deep research;
  **Revised 2026-04-23: Platform Pivot for multi-backend architecture**
  (Ries 2011 Part Two pivot type #5)
- Primary user: kouko (個人)
- Written against `planning-team` protocol `product-spec-writing.md`
  (standards: `planning-frameworks.md`, `discovery-frameworks.md`,
  `goals-and-metrics.md`, `spec-completeness-standards.md`)

---

## Revision History

| Date | Revision | Pivot type | Scope |
|---|---|---|---|
| 2026-04-?? | v0.1 — MVP direction (4-round deep research frozen) | — | Single-backend (Google Slides only) |
| 2026-04-23 | v0.2 — **Platform Pivot** | Ries 2011 Part Two #5 (Platform Pivot) | Multi-backend architecture. 設計知識層與執行層解耦；Google Slides 降為可插拔 backend 之一（renamed to `google-slides-setup` / `google-slides-builder`）；未來可加 `html-builder` / `pptx-builder` / `marp-builder`. **未動搖**：Job Story、4 Big Risks、MVP validated-learning 假設、3 core recipe 均不變。**Why Platform Pivot**：Ries 2011 Part Two 列出 10 種 pivot type，其中 Platform Pivot 指「從 single application 轉為 platform，或反之」。本次變更的本質是：架構從「為單一輸出格式服務的 application」轉為「以設計知識層為核心、可插拔多 backend 的 platform」，使用者需求（Job Story）與核心風險（4 Big Risks）未變，因此不屬於 Customer Segment Pivot / Problem Pivot / Zoom-in Pivot 等其他類型。 |

---

## 1. Background & Opportunity

### 1.1 當前痛點 (Why — 5W2H)

kouko 每週要做 **3–5 份 Google Slides**（工作報告、客戶提案、內部分
享）。現行流程：

```
打開 Slides → 複製舊檔 template → 手動逐張改文字
            → 本機生圖片 → 手動上傳 → 手動插入
            → 調整排版 → 反覆微調
```

單份耗時 **40–90 分鐘**，其中約 **70% 是重複性勞動**（文字替換、圖
片上傳、placeholder 對位）。這段時間**不產生設計判斷價值**——真正
load-bearing 的內容決策（what to say、which chart fits、資訊層級）
只佔剩下 30%。

### 1.2 Why now（timing）

- `monkey-skills` repo 已有兩個 toolkit plugin 先例（`investing-toolkit`、
  `copywriting-toolkit`）驗證 **toolkit pattern 可被個人工作流採納**。
- `googleworkspace/cli` (gws) 在 2025 年成熟到可用狀態：官方維
  護、Rust 靜態 binary、免 gcloud / 免 Python 運行時。
- kouko 已是 Claude Code 深度使用者，具備 Python/TS 能力，具備自
  建 skill 的 muscle memory。

### 1.3 Opportunity framing

將 Google Slides 生產力這條私人工作流 skill 化，把 70% 重複勞動自動
化，讓 kouko 的時間重新落到內容與設計判斷上。同時，此 toolkit 的
toolkit pattern 沿用既有先例，**為 Phase 2+ 其他 monkey-skills 用
戶建立一條可複製的路徑**（次要，非 MVP 目標）。

**Platform Pivot（2026-04-23 追補）**：同時建立可擴展的 **multi-backend
架構**——把**設計知識層**（`slides-design`，backend-agnostic）與**執
行層**（目前的 `google-slides-builder`，未來可加 `html-builder` /
`pptx-builder` / `marp-builder`）解耦，讓未來新增輸出格式不需重構既
有 skill。**Because** 輸出格式會演化（今天 Google Slides，未來 HTML
/ PPTX / Marp），但 Minto / SCQA / chart-selection 等設計原則穩定，
把兩者解耦可避免重寫知識層。**不動搖 MVP 範圍**：MVP 仍僅實作 Google
Slides backend，multi-backend 擴充屬 Phase 2+ trigger-based（見 §3.5）。

---

## 2. Target Users

### 2.1 Primary user — kouko (個人)

| 維度 | 描述 |
|---|---|
| 角色 | 個人生產力使用者（非組織內的 IT / 產品） |
| 平台 | macOS |
| 技術能力 | Python / TypeScript proficient、熟 shell、已是 Claude Code 深度使用者 |
| 頻率 | Google Slides 每週 3–5 份 |
| 帳號類型 | 個人 `@gmail.com`（非 Google Workspace 企業帳號） |
| 動機 | 把 70% 重複勞動壓到 Claude Code 自動執行 |

### 2.2 Secondary users — Phase 2+（明列，非 MVP 承諾）

- 其他 `monkey-skills` repo 用戶（通常技術背景、願意做一次性 GCP
  Console 設定）
- 觸發條件：kouko 用 MVP 跑 ≥ 10 份真實 deck 並判定 toolkit 值得
  publish 之後，才進入 Phase 2+ 的外部可用化。

### 2.3 誰決策 / 誰付費

- MVP：kouko 既是 user、也是 decision maker、也是 maintainer。
- 不存在付費角色——此 toolkit 屬個人生產力公共資產，monkey-skills
  repo 採 MIT license，不計價。

### 2.4 Job Story（Adams 2016 Intercom template）

> Job Story 模板出自 Paul Adams (2016) "How we accidentally invented
> Job Stories" *Intercom Blog*，**非** Christensen。底層 JTBD 理論
> 錨定 Christensen & Raynor (2003) *The Innovator's Solution* Ch.3
> 與 Christensen et al. (2016) HBR。

**Primary Job Story**

> **When** 我有結構化資料（文字大綱、表格、本機圖片）需要做成
> Google Slides 簡報時，**I want to** 透過 Claude Code skill 把資料
> 自動填入我預備的 template deck，**so I can** 把 70% 的重複勞動
> （文字替換、圖片上傳、placeholder 對位）省掉，只需聚焦內容與設
> 計判斷。

**Supporting Job Story**（資訊設計面）

> **When** 我決定每張投影片要放什麼內容時，**I want to** 拿到一份
> 可落地的資訊設計 / 敘事結構 reference（Minto / SCQA / chart-type
> 選擇），**so I can** 在不離開 Claude Code 的情況下決定「這張投
> 影片該放什麼、用哪種圖表」。

---

## 3. Goals & Non-Goals

> Goals / Non-Goals 慣例錨定 Malte Ubl (2020) "Design Docs at Google"
> `industrialempathy.com`。Non-Goals 依 Ubl 規則，必須是 **合理、
> 被考慮過、而明確拒絕**的目標；非明顯 out-of-scope 的事物。

### 3.1 Goals（MVP 版本）

> OKR 寫法錨定 Grove (1983) *High Output Management*（origin）+ Doerr
> (2018) *Measure What Matters*（modern operational canonical）。
> Grove 是 origin，Doerr 是 Intel 1975 trainee、1999 帶 OKR 進
> Google。

**Objective**（Doerr 格式 "I will [Objective] as measured by [KRs]"）

> I will **讓 kouko 能在 Claude Code 內用 skill 把結構化資料轉成
> Google Slides deck，把單份耗時從 40–90 分鐘壓到 ≤ 3 分鐘**，as
> measured by：

**Key Results**（4 項；aspirational，目標 0.7 per Doerr 2018）

| KR | 指標 | Target |
|---|---|---|
| KR1 | 單份 deck 生成時間（brief → Google Slides URL） | ≤ 3 分鐘 |
| KR2 | 全新機器首次設定（GCP OAuth + gws auth） | ≤ 20 分鐘 |
| KR3 | MVP 期間 kouko 實際產出的 deck 數 | ≥ 10 份 |
| KR4 | MVP 期間需要重寫 skill（非 bug fix、是設計錯誤） | 0 次 |

### 3.2 Non-Goals（被考慮但明確拒絕，非明顯 out-of-scope）

依 Ubl 2020 規則：以下**是合理的候選目標**，但 MVP 期間**明確拒絕**，
連同拒絕理由：

| Non-Goal | Rejected because | Phase 2 trigger |
|---|---|---|
| 動態圖表生成（CSV → PNG via matplotlib） | 需 Python runtime，違反「純 shell + gws binary」核心限制；MVP 用本機預先產好的 PNG | 出現首次真實 chart-generation 需求 |
| Excel / XLSX 輸入 | 需 Python openpyxl 或其他 runtime；MVP 用 JSON / plain text 結構化輸入 | 出現首次 XLSX-only 資料源 |
| 圖片前處理（resize / crop / format convert） | 需 ImageMagick 或 Python Pillow runtime；MVP 要求圖片預先調整好 | 使用者回饋「每張圖都要手動預處理」痛苦 |
| Form-specific 子 skill（pitch deck / report deck / tutorial deck） | 過早分裂、破壞 MVP 驗證焦點；先用一個通用 skill 收集訊號 | 設計知識層在真實使用中出現 form-specific divergence |
| Tufte / Duarte / 高橋メソッド 深度 reference | 設計深度不是 MVP validated-learning 重心；先驗證 pipeline 可用 | 外部使用者回饋設計知識不夠深 |
| `slide-plan.json` JSON schema 嚴謹驗證 | 用 shell + jq 做寬鬆驗證即可；MVP 不需 JSON Schema 工具鏈 | shell 組 JSON 痛苦到必須上 Python |
| design-quality-gate（品質 gate） | MVP 期間 kouko 親自當 gate；人工 review 比 skill gate 快 | Phase 2+ 外部使用者需要不依賴 kouko 判斷 |
| 多帳號切換支援 | kouko 僅使用一個 `@gmail.com`；多帳號是外部使用者需求 | Phase 2+ 外部 adoption |
| Google Workspace 企業帳號 OAuth 流程 | 企業帳號 consent screen 要 Admin Console 配置，和個人 Gmail 分支不同；MVP 只處理個人 Gmail | 出現 Workspace user 回饋 |
| Claude Code 以外 runtime（Cursor / Aider / Codex） | `monkey-skills` convention 綁 Claude Code skill model；跨 runtime 抽象會稀釋 MVP 焦點 | Phase 2+ 明確跨 runtime 需求 |
| Google Slides 以外 backend（html / pptx / marp） | MVP 要先驗證 pipeline（設計知識 → slide-plan → backend builder）可用；同時實作多 backend 會稀釋 validated-learning 焦點、拖慢 MVP 驗證週期。架構上已**預留**多 backend 擴充點（slides-design backend-agnostic、slide-plan 帶 `target` field），但**不**實作第二個 backend | 首次出現真實 HTML / PPTX / Marp 輸出需求（見 §3.5） |
| `slide-plan.json` 支援 image URL 形式輸入（而非本機檔案路徑） | gws 的 `insert-image` 在 MVP 驗證中以**本機圖片上傳**為 core recipe；URL 輸入需額外處理 auth、CORS、fetch retry，稀釋 MVP 焦點；kouko 實際場景本機圖片 ≥ 95% | 出現首次需要引用外部 URL 圖片的場景（e.g. 引用他人公開圖表） |
| 從原始碼編譯 `gws` / `jq` binary（build-from-source） | MVP 使用**官方 GitHub release 的預編譯 binary** + SHA-256 pin；自編不增加安全保證（仍需信任原始碼 + toolchain），卻引入 Rust / C toolchain 與跨平台 build matrix 的依賴，違反「runtime minimalism」與「純 shell」核心限制 | 出現 supply-chain 信任事件需要 reproducible build、或 upstream release 嚴重延遲 |

### 3.3 Assumption Discovery — 4 Big Risks（Cagan 2017）

> Cagan (2017) *Inspired* 2nd ed Part III。4-axis = Value /
> Usability / Feasibility / Business Viability。**不是** Bland &
> Osterwalder 2020（那是 3-axis DVF）。

| Risk | 評估 | 證據 |
|---|---|---|
| Value | **低** — kouko 每週 3–5 次 simulation case 明確；toolkit pattern 已驗證（investing-toolkit 自用 3 個月） | 使用者本人 = PM = 實際使用者，單人閉環 |
| Usability | **中** — 首次 ~15 分鐘 GCP Console 設定是硬邊界（Google OAuth policy，4 步手動不可繞） | state detect + 分支引導緩解 |
| Feasibility | **低** — gws CLI 可用；前置研究確認純 shell + jq 足以處理 template merge | gws 官方 CLI、Rust 靜態 binary |
| Business Viability | **低** — 個人生產力 toolkit、MIT license、沒有付費 / 合規壓力；僅需符合 Google OAuth policy | toolkit pattern 已有 investing / copywriting 先例 |

#### Assumption Mapping（Bland & Osterwalder 2020）

> Impact × Evidence 2×2；top 3 high-impact × weak-evidence 標 `[ASSUMPTION]`。

- `[ASSUMPTION-1]`（Usability，high impact / weak evidence）
  「使用者（包含 kouko 自己）能在 ≤ 20 分鐘跑完首次 GCP Console
  4 步設定 + gws auth 流程。」
  - **Validation**：MVP 交付後 kouko 自己在一台乾淨的 macOS 機
    器實跑，錄時間；若 > 20 分鐘則分支引導要重寫。
- `[ASSUMPTION-2]`（Value，high impact / medium evidence）
  「把 40–90 分鐘的工作壓到 ≤ 3 分鐘是可達成的——即『template deck
  + replaceAllText + insert local image』三個 core recipe 足以覆
  蓋 kouko 實際簡報的 ≥ 80% 場景。」
  - **Validation**：MVP 期間 kouko 實跑 ≥ 10 份真實 deck，記錄哪
    些場景 fallback 到手動。若 ≥ 3 份需要手動，重評 scope。
- `[ASSUMPTION-3]`（Feasibility，high impact / weak evidence）
  「gws issue #119（個人 Gmail invalid_scope / invalid_client）
  可用 `GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET` env var
  workaround 穩定規避，且此 workaround 不會在 gws 後續 release 破
  掉。」
  - **Validation**：MVP 實裝時先驗 workaround，並在 `google-slides-setup`
    內做 version pinning + 明確版本提示；若 workaround 被修復
    （或破掉），用 feature flag 分支。

### 3.4 MVP Definition（Ries 2011）

> Ries (2011) *The Lean Startup* Part Two："the minimum product
> that lets a team collect the **maximum validated learning** about
> customers with the **least effort**." MVP **不是**「最小 shippable
> feature set」。每個 MVP 定義必須明寫**要驗證什麼假設**。

**MVP 要驗證的核心假設**（What is the MVP trying to learn?）

> 「透過純 shell + gws binary + template-based merge，能在不裝
> Python / uv / gcloud / brew 的前提下，把 kouko 的結構化資料
> （文字大綱 + 表格 + 本機圖片）轉成可用的 Google Slides deck，
> 且時間壓到 ≤ 3 分鐘 / 份，首次設定 ≤ 20 分鐘。」

**MVP 內容**（minimum to enable Build-Measure-Learn loop）

- ✅ 3 個 core recipe：copy template / replaceAllText / insert local
  image
- ✅ Minto Pyramid + SCQA narrative 基礎 reference（來源錨定於
  設計知識層；見 §6.2）
- ✅ Chart-selection 對照（哪種資料用哪種圖表；不含生成）
- ✅ 使用者自備 template deck，用 `registry.md` 記錄 Drive ID
- ✅ 4 skills 架構（router / google-slides-setup / slides-design /
  google-slides-builder；後兩者 backend-agnostic / Google Slides-
  specific 的分工見 §6.3.1）
- ✅ credential 防外洩機制（`settings.json` deny rule + `.gitignore`）

**MVP 不涵蓋**（見 §3.2 Non-Goals、§9.2 Future Phases）

**Build-Measure-Learn loop in this MVP**
- Build → `slides-toolkit` MVP 四 skill
- Measure → kouko 實產 deck 時間、實測首次設定時間、fallback 次數
- Learn → 哪些場景 recipe 不夠、shell 組 JSON 何時變痛、設計知識
  層哪塊需要深化

### 3.5 Future Phases（非承諾，僅 trigger 條件）

| Phase 2 項目 | Trigger 條件 |
|---|---|
| `helpers/build_plan.py` | 第一份真實 deck 時 shell 組 JSON 過於痛苦 |
| `helpers/chart_gen.py`（matplotlib） | 首次出現真實的動態圖表生成需求 |
| `helpers/xlsx_reader.py` | 出現 XLSX-only 資料源 |
| `slides-design` 分裂為 `slides-info-design` + `slides-composition` | 設計知識超過 6k tokens SKILL.md 上限 |
| Tufte / Duarte / 高橋メソッド 深度 reference | 外部使用者回饋設計知識不夠深 |
| Form-specific skills（pitch / report / tutorial） | 真實使用出現 form-specific divergence |
| copywriting-team delegation（潤飾文案） | kouko 在 `slides-design` 裡明確缺少文案能力、且 copywriting-toolkit 已驗證 delegation contract |
| `html-builder` skill（HTML / reveal.js / remark 等輸出） | 首次 HTML 輸出需求（e.g. kouko 想把 deck publish 成 web page） |
| `pptx-builder` skill（`.pptx` 輸出，可能透過 python-pptx 或 LibreOffice headless） | 首次 `.pptx` 輸出需求（e.g. 交付給 MS Office-only 收件人） |
| `marp-builder` skill（Marp CLI 輸出 PDF / HTML / PPTX） | 首次 Marp 輸出需求（e.g. engineering tech talk、markdown-native workflow） |
| Backend interface 正式化（slide-plan schema formalize backend-agnostic 核心 + backend-specific extension） | 第二個 backend（任一 html / pptx / marp）實際落地時。MVP 期間 slide-plan 帶 `target` field 但不強制 schema；第二個 backend 會觸發「哪些 field 是 backend-agnostic、哪些是 backend-specific」的正式切分 |

---

## 4. Core Concept

### 4.1 Value proposition（one sentence）

**讓 kouko 在 Claude Code 內用單一 slash command 把結構化資料 +
template deck 合成 Google Slides**，把 40–90 分鐘的手工重複勞動壓
到 ≤ 3 分鐘，**because** 現有方案（Google Slides GUI、Slides API
直用、Google Apps Script）都要 kouko 自己串 OAuth + 自己寫 boilerplate，
而 `gws` CLI + skill 化 pipeline 同時解決了 runtime 輕量（純 shell）
與 Claude Code 介面整合兩個問題。

### 4.2 Core user scenarios（narrative）

**Scenario A — 每週客戶提案（最常見，~60% 場景）**

kouko 已有一份 12 頁的簡報 template（title / agenda / 3 個 section
divider / 6 張內容頁 / closing），Drive ID 記錄在 `registry.md`。本
週提案是某 SaaS 產品建議書：在 Claude Code 打 `/slides`，貼上 JSON
形式的 slide plan（title + 6 張內容的 headline/body/local image path），
skill 自動：(1) 複製 template，(2) replaceAllText 填入所有文案，
(3) insert local image 到每張的 placeholder，(4) 回傳 Drive URL。
kouko 打開 URL 做最後 5 分鐘的排版微調。**總耗時：3 分鐘 skill 執
行 + 5 分鐘人工微調 = 8 分鐘**（vs 原本 60 分鐘）。

**Scenario B — 工作週報（~25% 場景）**

規格化重複：kouko 有「週報 template」專用 Drive ID，每週只需把本週
progress 條列成 JSON，skill 輸出 URL，幾乎無需後續微調。**總耗時：
2 分鐘**（vs 原本 40 分鐘）。

**Scenario C — 對外分享 / 技術 talk（~15% 場景）**

kouko 需要一份內容設計更精細的簡報：先用 `slides-design` 拿到 Minto
/ SCQA 結構建議 + chart-type 對照，再自己組 slide plan JSON，最後
用 `google-slides-builder` 合成。**總耗時：12 分鐘**（vs 原本 90 分鐘；設
計部分仍需人工判斷，只省了機械勞動）。

### 4.3 Key differentiators

- **純 shell + gws binary**，不要求使用者裝 Python / uv / gcloud / brew
  — 降低首次設定摩擦（vs Google Apps Script 或 Python 直呼 Slides API）
- **Template-based merge**（使用者自備 deck）— 繞開「AI 自動設計投
  影片」這個 MVP 不打算解的難題，聚焦 replaceAllText + insert
  image 兩個可靠操作
- **Skill 化 + 知識層分離** — `slides-design`（知識，backend-agnostic）
  / `google-slides-builder`（執行，Google Slides backend）解耦，讓
  設計判斷可以獨立迭代；未來新 backend（html / pptx / marp）沿用同
  一份 `slides-design`
- **遵循既有 toolkit convention**（`investing-toolkit` /
  `copywriting-toolkit`）— 降低 kouko 的認知成本
- **Claude Code 原生整合** — 使用者不需離開 Claude Code session
- **Backend-agnostic 設計知識層** — `slides-design` 的 Minto / SCQA /
  chart-selection reference 對任何輸出格式（Google Slides / HTML /
  PPTX / Marp）都適用；**只有執行層綁定特定 backend**。**Because**
  設計原則跨輸出格式穩定，執行技術會演化——解耦兩層，未來新增 backend
  不需改動知識層

### 4.4 Design principles（3–5 guiding principles）

1. **Runtime minimalism** — 只依賴 shell + curl + 瀏覽器；`jq` 由
   skill 自抓。Zero Python / uv / gcloud / brew。**Because** 首
   次設定摩擦是最大 usability risk；runtime 越少、越快上手。
2. **Template-based，不自動生成** — 使用者自備 deck；skill 只做
   merge，不做 layout 判斷。**Because** 自動生成 layout 是開放難題，
   超出 MVP scope。
3. **知識層與執行層分離** — `slides-design`（reference / rubric，
   backend-agnostic）與 `google-slides-builder`（gws 呼叫 + merge，
   Google Slides backend）獨立。**Because** 知識會長期迭代，執行層
   會依 backend 分裂且相對穩定；耦合會拖慢兩邊、且阻礙未來多 backend。
4. **Credential never in repo** — `settings.json` deny rule +
   `.gitignore` pattern 雙重防護。**Because** 最小化 credential 外
   洩風險是硬邊界。
5. **State-aware onboarding** — `google-slides-setup` 能偵測目前狀態
   （已裝 gws？已 auth？token 過期？）並給對應分支。**Because**
   一次性線性 10 步對首次 / 回頭 / debug 使用者都不友善。
6. **Backend pluggability（後端可插拔）** — 設計知識層
   （`slides-design`）與執行層（`google-slides-builder` 及未來的
   `html-builder` / `pptx-builder` / `marp-builder`）解耦；新增
   backend 不需改 router 或知識層。**Because** 輸出格式會演化（今
   天 Google Slides，未來 HTML / PPTX / Marp），但設計原則穩定；
   解耦讓新 backend 可獨立插入，既有 skill 不受影響。

---

## 5. UX Direction

### 5.1 Core user flow（entry → primary task → outcome）

```
┌──────────────────────────────────────────────────────────────┐
│  Entry: Claude Code 內 /using-slides-toolkit                 │
│         (router skill — 通用；依需求選 backend)                │
└───────────────────────┬──────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────────────────┐
        ▼               ▼                           ▼
┌───────────────────┐ ┌──────────┐   ┌──────────────────────────┐
│ google-slides-    │ │ slides-  │   │ google-slides-builder    │
│ setup             │ │ design   │   │ (執行層；MVP 唯一 backend) │
│ (首次 onboarding)  │ │ (知識層;  │   │                          │
└────────┬──────────┘ │ backend- │   └──────────┬───────────────┘
         │            │ agnostic)│              │
         ▼            └────┬─────┘              ▼
   gws 安裝 +              │                 gws 呼叫
   GCP Console             ▼                 copy template
   + OAuth auth       Minto/SCQA             + replaceAllText
                     + chart-type            + insert image
                       reference                   │
                     (對任何 backend 適用)          ▼
                                           Google Slides URL

Phase 2+ (trigger-gated, 不承諾)：
   ├── html-builder/     → 同一份 slide-plan → HTML 輸出
   ├── pptx-builder/     → 同一份 slide-plan → .pptx 輸出
   └── marp-builder/     → 同一份 slide-plan → Marp (PDF/HTML/PPTX)
```

### 5.2 Interaction model

- **CLI（Claude Code slash command）** — skill 由 user 在 Claude
  Code 內叫；Claude 透過 Bash tool 呼叫 gws + jq
- **無 GUI** — MVP 不做任何 web UI
- **無 persistent agent** — 每次呼叫為一個 session，不維持背景服務

### 5.3 Key design constraints

| 面向 | 約束 | 原因 |
|---|---|---|
| 平台 | macOS（MVP） | kouko 唯一平台；Linux 是 Phase 2 |
| Runtime | shell + curl + 瀏覽器，其餘由 skill 自抓 | Runtime minimalism 原則 |
| Credential | 絕不入 repo | 安全硬邊界 |
| Token 生命週期 | 接受每 7 天重登（10 秒操作） | External + Testing mode 的 Google policy，無法繞 |
| 首次設定時間 | ≤ 20 分鐘 | KR2（含 GCP Console 4 步手動） |
| 單次執行時間 | ≤ 3 分鐘 | KR1 |
| SKILL.md 長度 | 每份 ≤ 6k tokens | `monkey-skills` CLAUDE.md 規定 |
| 文字編碼 | UTF-8 only（input slide-plan / template placeholder / output URL 相關路徑） | Google Slides API、gws CLI、`jq` 皆以 UTF-8 為預設；混入 Shift_JIS / Big5 / GBK 會在 replaceAllText 造成 mojibake。MVP 不做自動偵測與轉碼 |

---

## 6. 跨域考量

### 6.1 商業面（Business direction）

**當前定位：個人生產力工具，非商業產品**

- **收益模式**：無；MIT license，免費 / open source。屬 kouko 個人
  公共資產。
- **Business Model Canvas / Lean Canvas**：**不適用於 MVP**——
  Maurya 2022 的 Lean Canvas 針對 pre-PMF startup，問「should we
  build this at all」；本 toolkit 答案已確認（個人使用閉環驗證），
  跳過 pre-PMF 階段直接進 build。**Because** 本專案的經濟模型是
  「kouko 時間節省 × 每週 3–5 份」，不是 revenue model。
- **分發策略**：沿用 `monkey-skills` 既有 plugin 分發（GitHub repo
  + marketplace.json）；不另行推廣。
- **AARRR 不適用**：`goals-and-metrics.md` §AARRR（McClure 2007）
  5-stage 針對 SaaS / consumer app / marketplace 的 conversion
  funnel；個人生產力 toolkit 沒有 funnel，**不引用 AARRR**。

**Phase 2+ 若 publish 給外部使用者**

- `goals-and-metrics.md` 的 AARRR 才會適用（Acquisition = repo
  install、Activation = 首份 deck 成功、Retention = 週使用率等）
- 需補 Lean Canvas（Maurya 2022）—— 該節點重新問「外部使用者
  value prop 是否站得住」
- **Multi-backend 架構擴大 addressable 使用情境**：Phase 2+ 若
  publish，可讓外部使用者選擇輸出格式（不強迫綁定 Google Slides），
  例如 engineer 社群偏 Marp / Markdown-native、企業用戶偏 `.pptx`
  交付、Web 原生場景偏 HTML deck。**Because** 輸出格式偏好與所在生
  態（Google Workspace / Microsoft 365 / OSS）強相關；單一 backend
  會在 Phase 2+ 成為 adoption 瓶頸

### 6.2 設計面（Design direction）— 資訊設計 + 簡報設計知識層

**`slides-design` 角色：Claude 在生成 slide plan 時的設計 reference**

MVP 的設計知識層聚焦兩塊：

**(A) 敘事結構（narrative structure）**

| 結構 | 適用 | Primary source |
|---|---|---|
| Minto Pyramid | 商業報告 / 提案 / 週報 | Barbara Minto (1987) *The Pyramid Principle* |
| SCQA | 開場結構（Situation–Complication–Question–Answer） | Minto 1987（SCQA 是 Minto 體系內的 introduction template） |

**(B) 資訊視覺化（chart selection）**

MVP 提供 chart-type 對照表（Bar / Line / Pie / Scatter / Table 何時
用），**不含圖表生成**（Non-Goal）。主要 reference 來源 deferred
to Phase 2+（Tufte, Cleveland, Few 等深度 reference 是 trigger-gated）。

**為什麼不把 Duarte / Tufte / 高橋メソッド 放進 MVP**

- MVP 要驗證的是**pipeline 可用性**（Ries 2011 validated learning），
  不是**設計深度**
- 過度工程化知識層會讓 `slides-design` SKILL.md 在第一版就超過 6k
  tokens 上限
- **Trigger**：外部使用者首次回饋「設計建議不夠深」→ 加深 reference

### 6.3 技術面（Technical direction）

> 技術模組設計、資料流、介面定義歸 `TECH-SPEC.md`（code-team）。
> 本節只做 PRODUCT-SPEC 層級的方向與 rationale。

#### 6.3.1 架構方向

**Platform 架構（MVP = 1 個 backend；Phase 2+ = 可插拔多 backend）**

```
slides-toolkit (plugin root)
├── PRODUCT-SPEC.md                      # 本檔（planning-team 擁有）
├── TECH-SPEC.md                         # 技術規格（code-team 擁有）
├── README.md                            # plugin 入口文件
├── skills/
│   ├── using-slides-toolkit/            # router（通用；依需求選 backend）
│   ├── slides-design/                   # 設計知識層（backend-agnostic）
│   ├── google-slides-setup/             # [renamed] gws + GCP Console onboarding
│   │                                    #   (Google Slides backend 專屬)
│   └── google-slides-builder/           # [renamed] gws 呼叫 + template merge
│       └── templates/
│           └── registry.md              # 使用者 template deck 的 Drive ID registry
│                                        #   (Google Slides backend 專屬 runtime artifact)
├── scripts/
│   ├── common/                          # 跨 backend 共用 shell helpers (e.g. jq fetcher)
│   └── google-slides/                   # gws 相關 shell (Google Slides backend 專屬)
├── incidents/                           # on-demand post-mortem 記錄目錄
│                                        #   (初期空；遇 prod incident 才新增，每起一份)
└── (Phase 2+, trigger-gated)
    ├── skills/html-builder/             # HTML / reveal.js / remark 輸出
    ├── skills/pptx-builder/             # .pptx 輸出
    ├── skills/marp-builder/             # Marp CLI 輸出
    └── scripts/{html,pptx,marp}/        # 對應 backend 專屬 shell
```

**Because（架構切分 rationale）**：
- **設計知識層與執行層解耦** — `slides-design` backend-agnostic，對
  任何輸出格式都適用；backend builder（目前只有 `google-slides-builder`）
  綁特定執行技術。知識會長期迭代、執行層會依輸出格式分裂，解耦讓兩
  邊可獨立演進。
- **Google Slides backend 內的 skill 前綴統一 `google-slides-`** —
  `google-slides-setup` + `google-slides-builder`。Because 未來新
  backend（html / pptx / marp）需要自己的 setup 與 builder（或只有
  builder 即可），命名前綴讓哪些 skill 屬於哪個 backend 一目了然。
- **通用 skill 不加 backend 前綴** — `using-slides-toolkit` 與
  `slides-design` 不隨 backend 變化，保持通用命名。
- **`docs/` 不另設目錄** — PRODUCT-SPEC.md / TECH-SPEC.md 直接放
  plugin root；`registry.md` 屬於 Google Slides backend 的 runtime
  artifact，放 `skills/google-slides-builder/templates/registry.md`
  貼近其使用者。**Because** monkey-skills 其他 plugin 也採 plugin
  root 直放 SPEC 檔的慣例，一致性優先於分類整齊。
- **`incidents/` on-demand** — 初期為空目錄（或 `.gitkeep`）；遇到
  prod incident（e.g. gws workaround 被修復導致 OAuth 斷線）時才每
  起新增一份 post-mortem markdown。**Because** 預先堆砌空殼 incident
  模板對 MVP 無價值；等實際 incident 發生時再按需記錄更精準。

#### 6.3.2 關鍵技術選型（每條都附 "because"）

| 決策 | 選擇 | Because |
|---|---|---|
| 執行層 | `googleworkspace/cli` (gws) 官方 CLI，Rust 靜態 binary | 官方維護、免 gcloud、免 runtime；同類替代（直呼 REST / Google Apps Script / Python client）都引入更重的前置依賴 |
| 實作語言 | 純 shell + `jq` | Runtime minimalism 原則；使用者只需 shell + curl + 瀏覽器 |
| JSON 處理 | `jq`（由 skill 自抓 binary） | 使用者不需預裝；`jq` 靜態 binary 極小 |
| 帳號模型 | 個人 `@gmail.com`，External + Testing mode | kouko 唯一帳號；Workspace 企業流程歸 Phase 2+ |
| Token 策略 | 接受 refresh token 7 天過期，每週重登（~10 秒） | External + Testing 是 Google policy 硬邊界；產線 OAuth app 需過審，超出 MVP scope |
| Credential 儲存 | 預設 macOS Keychain，fallback `KEYRING_BACKEND=file` | macOS Keychain silent fail 是已知風險；file fallback 是 gws 官方支援 |
| Template 模型 | 使用者自備 template deck + `registry.md` 記 Drive ID | 自動生成 layout 超出 MVP；template-based 可靠性高 |
| Core recipe | copy template / replaceAllText / insert local image | 覆蓋 ≥ 80% 場景、且三者都是 gws 穩定命令 |
| 架構 | Multi-backend platform — slide-plan 帶 `target` field（e.g. `"target": "google-slides"`），router 依此路由到對應 backend builder | 避免 Google Slides 特有 detail（Drive ID、template Drive copy、replaceAllText）污染通用 slide-plan contract；未來 backend（html / pptx / marp）插入時不需改動既有 skill。MVP 只實作 `target: google-slides` 分支，但 contract 先留欄位 |

#### 6.3.3 Technical risks & mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| gws issue #119（個人 Gmail invalid_scope） | 高（已確認） | 高（阻斷 OAuth） | `GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET` env var workaround，在 `google-slides-setup` 提供分支引導 |
| macOS Keychain silent fail | 中 | 中 | Fallback 到 `KEYRING_BACKEND=file`，在 `google-slides-setup` state detect |
| Refresh token 7 天過期 | 100%（policy） | 低（10 秒重登） | 文件明說；`google-slides-builder` 呼叫前先 ping token |
| 使用者誤 commit credential | 中 | 高（credential 外洩） | `settings.json` deny rule + `.gitignore` pattern 雙重 |
| gws 未來 breaking change | 低（官方維護） | 中 | Version pinning；Phase 2+ 觀察 |
| Template deck schema 不穩定（使用者改 template 破壞 placeholder） | 中 | 中 | `google-slides-builder` 回傳 structured error；MVP 靠 kouko 人工判斷 |
| Binary supply-chain integrity（抓到被竄改的 gws / jq binary） | 低（GitHub release 被動） | 高（執行惡意 binary） | 所有 binary 下載附 SHA-256 pin + verify；mismatch 時 `bootstrap.sh` 回 exit 17 並 abort；詳見 TECH-SPEC §4.2 |

#### 6.3.4 External dependencies

**MVP（Google Slides backend 唯一啟用）**

- `gws` binary（Rust 靜態 binary，official releases）
- Google Cloud Console（一次性 OAuth 設定——4 步手動）
- Google Slides / Drive API（via gws）
- `jq`（由 skill 自抓 binary）

**Phase 2+（trigger-gated；非 MVP 承諾）**

新 backend 引入對應 external dep，但**不影響 MVP 也不影響既有 Google
Slides backend**：

| Backend | 可能 external dep | 備註 |
|---|---|---|
| `html-builder` | pandoc 或 handlebars 或純 shell template 工具 | 視 HTML 輸出風格選（reveal.js / remark / 純靜態） |
| `pptx-builder` | python-pptx（需 Python runtime）或 LibreOffice headless | 需跨 runtime 考量；觸發時重評 runtime minimalism 原則 |
| `marp-builder` | marp-cli（Node.js runtime） | Marp 生態綁 npm ecosystem |

**Because** 新 backend 的 runtime dep 可能違反 MVP 的 "pure shell +
gws binary" 原則；觸發 Phase 2+ 實作時，需在對應 builder skill 內
單獨評估是否引入 runtime（例如 `pptx-builder` 若需 Python，應 scope
到該 skill 內部，不污染其他 backend）。

---

## 7. Success Criteria

### 7.1 North Star Metric（Ellis & Brown 2017）

> NSM 錨定 Sean Ellis & Morgan Brown (2017) *Hacking Growth* Part I。
> **非** Facebook / Airbnb origin；那些是 canonical examples。

**Current-lifecycle NSM**（pre-PMF → 內部驗證）

> **Weekly deck-generation count by kouko**（kouko 每週用 skill
> 產出的 deck 數）

依 Ellis 2017 選擇準則：
- ✅ Reflect core value — deck 數 = 實際取代手動勞動次數
- ✅ Predict future growth — 週使用率 > 0 代表 toolkit 真實可用；
  走向 stagnation 代表退化
- ✅ Measurable — 可從 `registry.md` + git log 粗估
- ✅ Customer activity — 不是 revenue

**Target**：≥ 3 份 / 週，持續 ≥ 3 週 = PMF-for-kouko 訊號。

**Phase 2+ NSM**（若 publish）：sequence 會進到 "external active
users producing ≥ 1 deck / week"。

### 7.2 Supporting metrics（KR 對映）

- 時間：KR1（單份 ≤ 3 分鐘）、KR2（首次設定 ≤ 20 分鐘）
- 採用：KR3（≥ 10 份 MVP 期間）
- 設計錯誤：KR4（0 次重寫）

### 7.3 Anti-metrics（明列，避免 goodhart）

- 不以「skill 呼叫次數」為目標——重複 debug 會膨脹此指標
- 不以「程式碼行數」為目標——shell + jq 越精簡越好

---

## 8. Open Questions（留給 TECH-SPEC）

> 以下 `[OPEN]` 問題 **刻意不在 PRODUCT-SPEC 答**，交由 code-team
> 的 TECH-SPEC.md 決定。PRODUCT-SPEC 只負責框定方向與拒絕項。

- `[OPEN-1]` Slide plan 輸入格式：JSON vs YAML vs Markdown front-matter？
  JSON schema 要多嚴謹？（MVP 已定：寬鬆 JSON + jq 驗證；schema 嚴
  謹度細節歸 TECH-SPEC）
- `[OPEN-2]` `registry.md` 資料結構：純 markdown table 還是
  YAML front-matter？欄位最小集？
- `[OPEN-3]` `google-slides-builder` 的 gws 呼叫：是否包裝成單一
  shell function，還是分多個 recipe script？
- `[OPEN-4]` `google-slides-setup` 的 state detection 實作：如何
  檢測 token 過期 / 未登入 / 未裝 gws 三種狀態的分支？
- `[OPEN-5]` `jq` binary 自抓的來源、版本 pin、integrity check
  （shasum）策略？
- `[OPEN-6]` gws binary 自抓策略：讓使用者手動裝，還是由
  `google-slides-setup` 自動抓？若自動抓，version pinning 策略？
- `[OPEN-7]` Error handling convention：structured error JSON 返回
  Claude，還是 stderr + exit code？
- `[OPEN-8]` Image path 解析：支援相對路徑 / `~` 展開 /
  Claude Code working dir 的哪一種？
- `[OPEN-9]` Credential 防洩的 `settings.json` deny rule 具體 pattern？
- `[OPEN-10]` Template deck schema 校驗：MVP 是否需要 schema
  fingerprint 機制，偵測使用者改 template 後 placeholder 對不上？
- `[OPEN-11]` slide-plan `target` field 的 MVP 最小處理：是否強制
  要求 `target: "google-slides"`（明示），還是允許缺省？router 在
  缺省時要走預設還是 reject？（此問題 Phase 2+ 引入第二個 backend
  時會升級為「slide-plan schema backend-agnostic vs backend-specific
  的正式切分」）
- `[OPEN-12]` `tests/` 目錄的 bats 測試在 MVP 是否作為 **強制依
  賴**？bats 屬額外 runtime（雖可自抓 binary），且多數 script 靠
  dry-run + 手動驗證已能覆蓋；TECH-SPEC §7 傾向「非強制、放於
  `tests/` 但不納入 MVP 硬性規格」。本條 echo 至 PRODUCT-SPEC
  層請 TECH-SPEC 明確 answer（影響 `[ASSUMPTION-3]` workaround
  的 regression 防護力度）。

---

## 9. Risks & Assumptions（summary）

### 9.1 Top-3 assumptions（重申，含 validation approach）

見 §3.3 Assumption Mapping：`[ASSUMPTION-1]`（20 分鐘首次設定）、
`[ASSUMPTION-2]`（3 分鐘 / 份 + 80% 場景覆蓋）、`[ASSUMPTION-3]`（gws
issue #119 workaround 穩定）。

### 9.2 Known risks（含 mitigation）

見 §6.3.3 技術風險表。

### 9.3 Out-of-MVP triggers

見 §3.5 Future Phases trigger 表。

---

## 10. Downstream Handoff

### 10.1 團隊分工

| 下游團隊 | 負責產出 | 主要 input |
|---|---|---|
| `code-team` | `TECH-SPEC.md`（模組設計、資料流、介面定義） | 本 PRODUCT-SPEC §6.3 + §8 Open Questions |
| `skill-team` | 4 份 SKILL.md：`using-slides-toolkit`（router，不變）/ `slides-design`（知識層，不變，backend-agnostic）/ `google-slides-setup`（renamed from `slides-setup`）/ `google-slides-builder`（renamed from `slides-builder`） | 本 PRODUCT-SPEC §4 §5 §6.2 §6.3 |
| `docs-team` | README.md / `registry.md` template / GCP Console 逐步截圖 | 本 PRODUCT-SPEC §5.1 §6.3 |
| `research-team` | Phase 2+ 設計 reference 深化（Tufte / Duarte / 高橋） | Trigger 條件達成後才啟動；MVP 不需 |
| `design-team` | MVP **不需**（toolkit 無 GUI）；Phase 2+ 若加 web UI 才啟動 | — |

### 10.2 Handoff format

- 本檔 `PRODUCT-SPEC.md` 為 entry；`TECH-SPEC.md` 由 code-team 撰
  寫並 reference 本檔
- 各 SKILL.md 由 skill-team 撰寫，每份控制在 ≤ 6k tokens
- `registry.md` 為 runtime artifact（非 spec 層級）

### 10.3 5W2H Final Cross-Check

> Per `spec-completeness-standards.md` §5W2H — Per-Letter Checks。
> 5W2H 正確譜系：Kipling (1902) *Just So Stories* "Elephant's
> Child"（5W1H 詩源）→ 1960s JUSE 日本品質運動（+2H = How much）
> → 大野耐一 (1978)『トヨタ生産方式』ダイヤモンド社（book-form
> canonical popularization）。**非**單源「日本商業習慣」。

| 字母 | 問題 | 本 spec 回答位置 |
|---|---|---|
| Why（なぜ） | 為什麼做？動機？ | §1.1 §1.2（kouko 每週 3–5 份、70% 重複勞動、gws 2025 成熟） |
| What（何を） | 做什麼？核心價值？ | §4.1 §4.2（skill 化 template merge、3 core recipe、4 skills） |
| Who（誰に） | 誰用？誰做？ | §2.1 primary = kouko；§2.2 secondary Phase 2+；§10.1 team 分工 |
| When（いつ） | 時程？里程碑？ | §3.1 KR2 / KR3；§3.5 Future Phases trigger（非固定日期——trigger-based） |
| Where（どこで） | 平台？分發？ | §5.3 macOS；§6.1 monkey-skills repo + marketplace.json |
| How（どのように） | 技術？怎麼做？ | §6.3 純 shell + gws + jq；4 skills 架構 |
| How much（いくらで） | 資源？成本？ | §6.1 無收益、MIT；kouko 時間成本：MVP 建置 ~2–3 週 part-time，Phase 2+ trigger-based |

所有 7 字母皆有具體回答——5W2H 完整性通過。

---

## Appendix — Primary Source Bibliography

所有框架引用錨定於以下一級來源（planning-team `standards/` 規範）：

**JTBD / Job Story**
- Christensen & Raynor (2003) *The Innovator's Solution* Ch.3. HBS Press.
- Christensen, Hall, Dillon, Duncan (2016) "Know Your Customers' 'Jobs
  to Be Done'" *HBR* Sep–Oct 2016.
- Adams (2016) "How we accidentally invented Job Stories"
  *Intercom Blog* 2016-06-28. ← **Job Story 模板 origin**

**4 Big Risks / Product Discovery**
- Cagan (2017) *INSPIRED* 2nd ed Part III. Wiley. ← 4-axis（**非** Bland）
- Cagan (2017) Parts III–IV（discovery vs delivery）

**Assumption Mapping**
- Bland & Osterwalder (2020) *Testing Business Ideas*. Wiley.

**Lean Startup / MVP**
- Ries (2011) *The Lean Startup* Parts One–Two. Crown Business.
  ← MVP + BML + Validated Learning origin（**非** Blank）
- 大野耐一 (1978)『トヨタ生産方式』ダイヤモンド社 ← Lean TPS genealogy

**OKR / North Star / Non-Goals**
- Grove (1983) *High Output Management*. Random House. ← OKR origin
- Doerr (2018) *Measure What Matters*. Portfolio/Penguin. ← 現代 canonical
- Ellis & Brown (2017) *Hacking Growth* Part I. Crown Business.
  ← North Star Metric origin（**非** Facebook / Airbnb）
- Ubl (2020) "Design Docs at Google" industrialempathy.com.
  ← Goals / Non-Goals 慣例（community convention，**非** Google 官方）

**5W2H genealogy**
- Kipling (1902) "The Elephant's Child" in *Just So Stories*. Macmillan.
- 大野耐一 (1978)『トヨタ生産方式』ダイヤモンド社 / Ohno (1988)
  English. ← 5W1H 問答 discipline popularizer

---

**End of PRODUCT-SPEC.md — slides-toolkit**

下一步：code-team 依本 spec §6.3 + §8 Open Questions 產出 `TECH-SPEC.md`；
skill-team 依 §4 §5 §6 產出 4 份 SKILL.md。

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
