# Changelog

All notable changes to `slides-toolkit` are documented in this file.

本檔案採 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 格式，
版本編號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [Unreleased]

### 即將 unblock（在 0.7.0 release 前，kouko 需完成）

- 跑 10 份真實 deck 驗 KR1（brief → URL ≤ 3 分鐘）+ `[ASSUMPTION-2]`
  Google predefined layouts 覆蓋率 ≥ 80%

## [0.6.0-i18n] - 2026-04-24

**Language strategy formalisation** — technical layers rewritten in
native English; design / content layer gains trilingual (EN / JP / ZH)
anchors at key terminology points. No functional change; entirely a
documentation-voice refactor. `docs/*` keeps its Chinese-primary
narrative per user directive (internal maintenance notes).

### Changed

- **Technical skills — English-native rewrite** (not translation):
  - `skills/google-slides-api/SKILL.md` + all 4 recipe protocols
    (`recipe-create-presentation.md`, `recipe-create-slides.md`,
    `recipe-insert-text.md`, `recipe-insert-image.md`) +
    `references/api-error-codes.md`
  - `skills/slides-builder/SKILL.md` +
    `checklists/pre-flight.md`
  - `skills/gws-setup/SKILL.md` +
    `protocols/gcp-console-walkthrough.md` +
    `protocols/issue-119-workaround.md` +
    `standards/credential-hygiene.md` +
    `checklists/setup-state.md`
- **Shell script header docstrings — English rewrite**:
  - `scripts/gws/bootstrap.sh`, `gws-wrap.sh`, `env-guard.sh`,
    `credential-check.sh`, `auto-setup.sh`, `refresh-auth.sh`
  - Script body code, function-level comments, variable / function
    names unchanged
- **Design / content layer — trilingual anchors added**:
  - `skills/slides-design/SKILL.md` + `references/minto-scqa.md` +
    `references/chart-selection.md` +
    `rubrics/slide-plan-self-check.md`
  - `skills/using-gws-toolkit/SKILL.md` routing table
  - Anchor format: `English term (日本語 / 中文)` at key concept
    points; downstream references reuse the English term
  - Anchor density: ~8 per slides-design SKILL.md, ~19 on
    minto-scqa.md, ~25 on chart-selection.md, ~8 in router routing
    table, ~4 on self-check rubric
- **PRODUCT-SPEC** — added `§6.4 Language strategy` formalising (A)
  technical EN-primary / (B) design trilingual / (C) frontmatter multi
  / (D) maintenance rules

### Preserved

- All SKILL.md frontmatter `description` fields (bilingual / trilingual
  keyword triggers for Claude Code auto-routing — unchanged)
- Technical facts (commands, exit codes, JSON shapes, file paths, EMU
  values) — all v0.5.0 live-validated semantics intact
- Primary source citations (Minto 1987, Cleveland & McGill 1984, Few
  2012, Duarte 2008/2010, Tufte 2001)
- `docs/*.md` — still Chinese-primary per user directive (internal
  maintenance notes / implementation journals)
- Version history and revision annotations in script headers (`v0.3`,
  `v0.3.1`, `v0.3.2`, `v0.5.1`)

### Rationale

Technical content is 95% code-surface terms (gws commands, JSON, API
fields) that are inherently English; Chinese translation noise
outweighs readability gain. Design / content layer meets the user in
natural-language conversation ("棒グラフ" / "長條圖" / "bar chart"
should all route to the same recipe), so trilingual anchors preserve
alignment without bloating the prose. `docs/*` stays Chinese-primary
because it serves as internal maintenance record where authorial
velocity > international reach.

## [0.5.1-smooth-reauth] - 2026-04-24

**UX refinement**（非 pivot；無 scope 變動）— 把「7 天 token 過期」的
recovery 從「使用者 copy-paste 長指令」提升為「Claude 偵測 exit 10 →
自動呼叫 helper → browser open → user 點 Allow → retry」，無痛體驗。

### Added

- `scripts/gws/refresh-auth.sh`（60 lines）— 一鍵 re-auth helper：
  - 自動 source `~/.config/gws/env.sh`（issue #119 workaround env vars）
  - 呼叫 `gws auth login --scopes=<presentations,drive.file>`（完整 URL，
    避免 `-s` service filter 陷阱）
  - Pre-flight 驗 `client_secret.json` / `env.sh` / `gws` binary 存在
  - Exit 0 success / 10 gws auth fail / 1 generic
  - `SLIDES_TOOLKIT_SCOPES` env override
  - 三個 entry point 共用：Claude orchestration / user alias
    (`gws-relogin`) / cron（未來若加）

### Changed

- `skills/slides-builder/SKILL.md` §Token expiry — 從 "passive
  detect + 告知使用者手動跑" 升級為「exit 10 recovery protocol」5-step
  明文（偵測 → 告知 → 自動觸發 refresh-auth.sh → retry 原 op → 失敗
  才 escalate）。加 zsh alias `gws-relogin` 建議。
- `skills/google-slides-api/references/api-error-codes.md` exit 10 section
  — Recovery 指令從 `gws auth login -s presentations,drive.file`（錯的
  scope 語法）改為推薦 `refresh-auth.sh` helper + 保留手動展開版供 fallback。
  指向 `slides-builder/SKILL.md §Token expiry` 為權威 orchestration
  protocol。

### Rationale

v0.5.0 live E2E 驗證後，唯一 recurring friction 是每 7 天重跑 `gws auth
login`——該指令含兩條完整 scope URL + 需先 source env.sh + export。複
製貼上易出錯（例：`-s` vs `--scopes=` 語法差異）。

v0.5.1 把這一長串收斂到單一 helper script：
- **Claude 偵測 exit 10 → 呼叫 helper**：無需 Claude 記住長指令
- **User 偏好手動**：alias 一個 `gws-relogin` 詞即可
- **未來 cron / launchd 自動提醒**：仍指向同一 helper（DRY）

唯一仍需使用者互動的是瀏覽器點「Allow」（Google OAuth policy 強制，
`docs/google-oauth-automation-limits.md` 已記錄為永久邊界），約 10 秒。

## [0.5.0-live-validated] - 2026-04-24

**Live E2E Validated**（非 pivot；無 scope 變動）— 首次在真實環境完整跑
過 4 recipes 端對端流程。OAuth 認證 + 建 deck + 建 slides + 填文字 +
插入圖片全綠。過程中暴露出 walkthrough / recipes 與真實 gws CLI 行為的
若干 drift，全數修正。同時新增 `auto-setup.sh` 把可自動化部分 codify。

### Added

- `scripts/gws/auto-setup.sh` — 535 行 shell script，idempotent
  7 步自動化：detect/install gcloud → gcloud auth → GCP project create
  → enable APIs → open Console URLs → wait for client_secret → install
  credentials + write env.sh → gws auth login → verify。支援
  `--dry-run` / `--force-reinstall`；`SLIDES_TOOLKIT_PROJECT_ID` env
  override；stdout JSON contract `{status, project_id, account, scopes,
  elapsed_sec, dry_run}`
- `skills/gws-setup/protocols/gcp-console-walkthrough.md` 重寫
  為雙路徑：**Path A (Fast, ~6-8 min)** 走 auto-setup.sh；**Path B
  (Manual, ~10-15 min)** 純 Console；共用 §Local 結尾
- 4 個 recipe md 檔尾加「## Live-tested behavior (2026-04-24)」區塊，引用
  實測出的 JSON 片段

### Changed

- `gcp-console-walkthrough.md` 全面更新為 Google Cloud Console **新 UI**
  語言：Google Auth Platform / Branding / Audience / Clients（舊版
  "APIs & Services → OAuth consent screen → Test users" → 新版
  "Google Auth Platform → Audience → Test users section"）。每步 URL
  帶 `?project=<PROJECT_ID>` placeholder
- `recipe-create-presentation.md` — default slide placeholder 更正為
  `CENTERED_TITLE` + `SUBTITLE`（非 TITLE），加 `presentations.get`
  正確呼叫示範（`presentationId` / `fields` 皆入 `--params`）
- `recipe-create-slides.md` — `batchUpdate` 呼叫修正為
  `--params '{"presentationId":"..."}'`（非獨立 flag）；加 layout →
  placeholder type 對照表（TITLE 用 `CENTERED_TITLE` + `SUBTITLE`；
  其他 layout 用 `TITLE` + `BODY` etc.）
- `recipe-insert-text.md` — 加 `{{TITLE}} → CENTERED_TITLE` fallback
  mapping rule；`batchUpdate` 呼叫改 `--params`；修正 reply object
  為 `{}`（非 `{"insertText":{}}`）；刪除不必要的 `insertionIndex: 0`
- `recipe-insert-image.md` — **最大 delta**：
  - 加 ⚠️ cwd sandbox 警示：`gws drive files create --upload` 要求檔案
    在 cwd 或其子目錄；absolute path 會被 reject
  - `--upload-file` → `--upload`（flag 名字錯）
  - `drive permissions create` 的 `fileId` 入 `--params`
  - Image URL 手動拼 `https://drive.google.com/uc?id=<FILE_ID>`（
    **不用** response 的 `webContentLink`，後者帶 `&export=download`
    會讓 Slides createImage render 失敗）
  - 加 Gotchas 表（7 條 trap + fix）
  - EMU 座標值更新為實測驗證過的數字

### Rationale

Live E2E 在 kouko 本機跑過（macOS arm64、個人 @gmail）：
- gcloud 首次裝 + auth + project create + enable APIs 全自動
- Console 手動 2 步（Audience 加 test user / Clients 建 Desktop client +
  download JSON）— 無法自動化（Google IAP OAuth Admin API 已 2025-01-22
  deprecated，證據見 gws source `setup.rs:913` 註解）
- gws auth login 走 `--scopes=<URL>,<URL>` 而非 `-s`（後者是 service
  filter 不是 scope 指定）
- 實測產物：<https://docs.google.com/presentation/d/1rCqdw0HvYow4Hr5l38Ark1ZzpDsGYptWtW-dHkYT6lY/edit>
  （含 2 slides + 1 image，全部 4 recipes 實證有效）

此 validation round 把過往「spec 內寫的 recipe」變成「spec 內寫的是**實測
驗證過的** recipe」，是 MVP 從 paper design → working system 的關鍵里程碑。

## [0.4.2-api-sibling-skill] - 2026-04-24

**Architectural layer split**（純 refactor；無 scope / 功能變動）— 把
`slides-builder/protocols/` 下的 4 個 per-op recipe 抽出成 sibling
skill `google-slides-api`，builder 變薄保留 pipeline orchestration 職責。

### Added

- `skills/google-slides-api/SKILL.md` — 低層入口（op list + composition
  pattern via placeholder_map + when-to-use boundary）
- `skills/google-slides-api/references/api-error-codes.md` — 10/11/12/
  13a/13b/14/15/16/18 exit code 語意 + 救援 playbook，集中於此 reference

### Changed

- `skills/google-slides-api/protocols/recipe-create-presentation.md` ←
  `git mv` from `slides-builder/protocols/`
- `skills/google-slides-api/protocols/recipe-create-slides.md` ← git mv
- `skills/google-slides-api/protocols/recipe-insert-text.md` ← git mv
- `skills/google-slides-api/protocols/recipe-insert-image.md` ← git mv
- `skills/slides-builder/SKILL.md` — 變薄：改為引用 sibling
  skill 的 recipes；Step 2-4 路徑改為 `../google-slides-api/protocols/*`
- `skills/slides-builder/checklists/pre-flight.md` — 下游 recipe
  連結改為 sibling skill 路徑
- `skills/using-gws-toolkit/SKILL.md` — routing table 加第 4 分支
  （「單一 API op / debug / 學 batchUpdate」→ `google-slides-api`）
- `PRODUCT-SPEC.md` §6.3.1 + `TECH-SPEC.md` §2.1 目錄樹更新
- `TECH-SPEC.md` Revision History 加 v0.3.2 條目

### Rationale

- **SRP**：per-op recipe（low-level API wrapping）與 pipeline
  orchestration（high-level slide-plan.json consumer）為兩種獨立變動
  維度。分離後各自演進；Slides API 升版只動 api skill，pipeline 設計
  改動只動 builder。
- **OCP**：Phase 2+ 出現 second consumer（e.g. slide-deck-auditor,
  deck-diff tool）時，可直接引用 `google-slides-api` 而不需經 builder
  的 slide-plan.json schema 層。
- **授權自主**：新 skill 為原創 MIT 內容，與 gws-slides（Apache-2.0
  SKILL.md，僅 44 行 API 目錄）**無程式碼依賴**。`gws` binary 仍為
  runtime 被動呼叫（subprocess），不入 repo。未來想引用 gws-slides 成
  optional cross-reference link，不需 NOTICE / attribution。
- **架構對照 gws-slides**：研究確認 gws-slides 只是 API discovery
  reference（44 lines, 無 recipes），我們的 4 recipe 對其**非 redundant**
  （~20% overlap）— builder 層的 orchestration + placeholder_map 組裝 +
  error handling 為我們獨有價值。詳見研究結論（conversation record
  2026-04-24）。

### Removed

- `skills/slides-builder/protocols/` 目錄（內容移至 sibling skill）

## [0.4.1-auto-refresh-binary] - 2026-04-24

**Runtime simplification**（非 pivot）— 消除 `GWS_VERSION` TODO；gws
binary 改為解析 GitHub `/releases/latest/download/` redirect；加入 TTL
based auto-refresh。jq 繼續 pin `1.7.1`（release 穩定）。

### Added

- `bootstrap.sh` TTL-based auto-refresh：`.version.installed_at` 超過
  `SLIDES_TOOLKIT_BINARY_TTL_DAYS`（預設 30）時，自動重抓 latest
- `bootstrap.sh` auto-refresh 安全網：refresh 失敗（網路 / 上游 503）
  **保留既有 binary**、印 stderr warning、exit 0，不阻斷日常使用
- `bootstrap.sh` 透過 GitHub REST API（`/repos/.../releases/latest`）
  解析實際 tag 並寫入 `.version.gws_tag`，供 debug / audit
- `.version.source` 欄：`env-pinned` / `auto-resolved` / `auto-resolve-failed`
- Env `GWS_VERSION=v0.X.Y`：pin 某版（停用 auto-refresh）— 用於救火
  或固守穩定版
- Env `SLIDES_TOOLKIT_BINARY_TTL_DAYS`：客製 TTL

### Changed

- `bootstrap.sh` 預設 URL：`/releases/download/<tag>/` →
  `/releases/latest/download/`（GitHub 原生 302 redirect）
- `.version` schema：`{gws, jq, written_at}` →
  `{gws_tag, jq_tag, source, installed_at}`
- `GWS_VERSION` 環境變數從必填 → **optional pin override**

### Removed

- `bootstrap.sh` 的 `GWS_VERSION="v0.0.0-TODO"` default（改為空字串
  表 auto-resolve）

### Rationale

- `GWS_VERSION` pin 是 v0.3 唯一剩下的 TODO；auto-resolve 消掉它
- 30 天 TTL 讓 binary 自動跟上 upstream bugfix，不需使用者手動操作
- Pin override 給「upstream breaking change」的救火窗口
- jq 不走 latest：jq 1.7.1 已穩定 > 12 個月，無需自動追蹤

### Phase 2+（trigger-gated；見 `PRODUCT-SPEC.md §3.5`）

- `html-builder` skill（首次 HTML 輸出需求觸發）
- `pptx-builder` skill（首次 `.pptx` 輸出需求觸發）
- `marp-builder` skill（首次 Marp 輸出需求觸發）
- Template-based workflow return（Google predefined layouts 視覺品質不足
  或需品牌一致性時觸發）
- SHA-256 supply-chain pin（publish / CI / 安全事件觸發）
- `helpers/build_plan.py`（shell 組 JSON 首次出現痛苦時觸發）
- slide-plan schema 正式 backend-agnostic / backend-specific 切分
  （第二個 backend 實作時觸發）

## [0.4.0-scope-refinement] - 2026-04-24

**Scope Refinement**（非 pivot）— 對齊 PRODUCT-SPEC v0.3 + TECH-SPEC v0.3。
Job Story、4 Big Risks、MVP validated-learning 核心假設、OKR / NSM 皆未動。

### Removed

- `skills/slides-builder/templates/`（整個目錄 + `registry.md`）
  — 使用者自備 template + Drive ID lookup 不再是 MVP 路徑
- `skills/slides-builder/protocols/recipe-copy-template.md`
  — `gws drive files copy` 流程不再需要
- `skills/slides-builder/protocols/recipe-replace-text.md`
  — 改名為 `recipe-insert-text.md`（new file）
- `bootstrap.sh` 的 SHA-256 驗證：`GWS_SHA256_*` / `JQ_SHA256_*` 4 個常數、
  `verify_sha256()` / `expected_sha_for()` 函式、exit code 17 `SHA mismatch`
  — 改以 HTTPS + `curl -fLSs` + URL pin 為 integrity 邊界

### Added

- `skills/slides-builder/protocols/recipe-create-presentation.md`
  — `gws slides presentations create --json '{"title":"..."}'` 建空 deck
- `skills/slides-builder/protocols/recipe-create-slides.md`
  — `batchUpdate createSlide` 搭配 `layout_hint` enum（7 個 Google 預設
  predefinedLayout 值）逐 slide 建構
- `skills/slides-builder/protocols/recipe-insert-text.md`
  — `batchUpdate insertText` 到 placeholder object ID（不再用
  `{{PLACEHOLDER}}` 文字錨點）
- slide-plan.json schema v1.1 → **v1.2**：新增 `slides[].layout_hint`
  （必填 enum）；刪除 `backend_config.template_ref`

### Changed

- `skills/slides-builder/SKILL.md` — 重寫 workflow 為 4-step
  （pre-flight → create → build slides → insert text/image）
- `skills/slides-builder/protocols/recipe-insert-image.md`
  — 從 `replaceAllShapesWithImage` 改為 `createImage` with explicit
  `pageElementProperties`，接 `placeholder_map` 對位
- `skills/slides-builder/checklists/pre-flight.md` — 10 項 check
  更新（刪 registry 檢查、加 `layout_hint` enum 檢查）
- `PRODUCT-SPEC.md` v0.2 → v0.3（Scope Refinement；+2 Non-Goals
  template/SHA + 2 Future Phases trigger + Principle 2 rewrite
  Template-based → Layout-based）
- `TECH-SPEC.md` v0.2 → v0.3（schema v1.2 + 4 recipes + SHA 移除 +
  C13 refactor commit）

### Rationale

個人使用閉環下：
- **Template overhead > 視覺品質邊際增益** — maintain template deck +
  registry.md + placeholder drift 的成本大於 Google 預設 layout 不精美
  帶來的微差
- **SHA 維護成本 > 邊際安全增益** — 個人 scope 下，HTTPS + `curl -f`
  + GitHub org 信任邊界足夠；SHA pin 每次 upstream release 都要更新
  的 overhead 不成比例

兩條都列 Phase 2+ trigger：publish 給外部 / CI / 視覺不足 / 安全事件
→ 隨時可恢復。

## [0.3.0-scaffold] - 2026-04-23

**Scaffold 交付**（Platform Pivot 後的首次 code 階段）— 依 TECH-SPEC v0.2
C1–C7 commits 建出 plugin 骨架。仍**未**真正可運作（含 TODO placeholder
待 kouko 於本機填入版本 pin + SHA-256 + Drive ID）。

### Added

- `.claude-plugin/plugin.json` + `README.md` + `CHANGELOG.md` + `.gitignore`
- `.claude/settings.json` deny rule（TECH-SPEC §8.1 完整 13 條：含
  `Read` / `Bash(cat|cp|git add)` / `Write` 防護）
- `scripts/gws/` 下 4 支 shell script：
  - `bootstrap.sh`（抓 gws + jq binary；SHA-256 pin + verify；idempotent）
  - `gws-wrap.sh`（pre-flight + retry with exponential backoff 5s/10s/20s）
  - `env-guard.sh`（issue #119 workaround，ISP 拆 `check` / `apply`）
  - `credential-check.sh`（Keychain silent-fail 偵測 + file backend fallback）
- `scripts/common/.gitkeep`（Phase 2+ 預留）
- `incidents/README.md`（on-demand playbook 入口）
- 4 個 SKILL.md：
  - `using-gws-toolkit`（backend-agnostic router）
  - `slides-design`（backend-agnostic 知識層）+ `references/minto-scqa.md`
    + `references/chart-selection.md` + `rubrics/slide-plan-self-check.md`
  - `gws-setup` + `protocols/gcp-console-walkthrough.md`（10 步）
    + `protocols/issue-119-workaround.md` + `standards/credential-hygiene.md`
    + `checklists/setup-state.md`
  - `slides-builder` + 3 recipe protocols（copy-template / replace-text
    / insert-image）+ `templates/registry.md` + `checklists/pre-flight.md`

### Known placeholders

所有 `TODO_FILL_REAL_SHA256_64HEX` / `v0.0.0-TODO` / `TODO: fill Drive ID`
必須由 kouko 在本機填入後才能跑通 E2E。Public repo commit 前應確認
`registry.md` 的 Drive ID 仍為 `TODO` 骨架，避免洩漏。

## [0.2.0-spec] - 2026-04-23

**Platform Pivot**（Ries 2011 Part Two pivot type #5）— 僅 spec 階段變更，
尚未 code。架構從「為單一輸出格式服務的 application」轉為「以設計知識層
為核心、可插拔多 backend 的 platform」。Job Story、4 Big Risks、MVP
validated-learning 假設、3 core recipe 均不變動。

### Changed

- `skills/slides-setup/` → `skills/gws-setup/`
  （backend-prefix 命名；Google Slides backend 專屬）
- `skills/slides-builder/` → `skills/slides-builder/`
  （backend-prefix 命名；Google Slides backend 專屬）
- `scripts/` 分子目錄 → `scripts/common/` + `scripts/gws/`
- `using-gws-toolkit`（router）與 `slides-design`（knowledge）
  **保持通用命名**，不加 backend 前綴

### Added

- Multi-backend architecture 擴充點預留（`scripts/common/`、phase 2+
  `html-builder` / `pptx-builder` / `marp-builder` 觸發條件）
- `slide-plan.json` schema v1 → v1.1：新增 `target`（e.g.
  `"target": "google-slides"`）+ `backend_config` 欄位，避免 Google
  Slides 特有 detail 污染通用 slide-plan contract
- `PRODUCT-SPEC.md` v0.2 Revision History 條目 + §3.5 新 trigger 條件
  （html / pptx / marp 各自觸發 + backend interface 正式化觸發）
- `TECH-SPEC.md` v0.2 Revision History 條目 + §9 OPEN-11 回答（slide-plan
  `target` field 的 MVP 最小處理）+ rename migration log 表

### Rationale

輸出格式會演化（今天 Google Slides，未來 HTML / PPTX / Marp），但 Minto
/ SCQA / chart-selection 等設計原則穩定。把兩者解耦可避免重寫知識層，
且讓 Phase 2+ 新 backend 不需改動既有 skill。**不動搖 MVP 範圍**：MVP
仍僅實作 Google Slides backend。

## [0.1.0-spec] - 2026-04-23

PRODUCT-SPEC + TECH-SPEC 初版交付（spec 階段；尚未 code）。
經 4 輪 deep research 凍結 MVP 方向後產出。

### Added

- `PRODUCT-SPEC.md`（planning-team 擁有）— 跨域願景 + MVP scope
  - §1 Background & Opportunity（當前痛點 5W2H + Why now + opportunity framing）
  - §2 Target Users（primary = kouko / Job Story per Adams 2016）
  - §3 Goals & Non-Goals（Doerr OKR 4 KRs + Ubl Non-Goals + Cagan 4 Big
    Risks + Bland & Osterwalder Assumption Mapping + Ries MVP definition）
  - §4 Core Concept（value prop + 3 scenarios + 6 design principles）
  - §5 UX Direction（flow diagram + CLI-only + constraints）
  - §6 跨域考量（business / design / technical direction with rationale）
  - §7 Success Criteria（Ellis & Brown North Star + supporting KRs）
  - §8 Open Questions（10 條留給 TECH-SPEC）
  - §9 Risks & Assumptions summary
  - §10 Downstream Handoff（團隊分工 + 5W2H final check）
- `TECH-SPEC.md`（code-team 擁有）— 技術模組設計 + 10 OPEN answers
  - §1 Scope & Constraints（goals / non-goals / hard constraints）
  - §2 Architecture（plugin layout + diagram + binary cache）
  - §3-§6 Module design / Interface / Data flow / Error handling
  - §7 Testing（dry-run + golden snapshot + fixture strategy）
  - §8 Security & Credential Hygiene（ASVS L1 mapping + deny rule
    + .gitignore + pre-commit + incident response playbook + character
    encoding）
  - §9 Answers to 10 PRODUCT-SPEC OPEN questions
  - §10 Implementation phases + commit split
  - §11 Module Readiness Summary
