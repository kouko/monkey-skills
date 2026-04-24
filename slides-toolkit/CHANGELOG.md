# Changelog

All notable changes to `slides-toolkit` are documented in this file.

本檔案採 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 格式，
版本編號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [Unreleased]

### 即將 unblock（在 0.5.0 release 前，kouko 需完成）

- 跑 `google-slides-setup` 完成首次 GCP Console OAuth
- 實測 end-to-end：brief → URL ≤ 3 分鐘（KR1）；Google 內建 predefined
  layouts 覆蓋率 ≥ 80%（`[ASSUMPTION-2]` revalidation）

## [0.4.2-api-sibling-skill] - 2026-04-24

**Architectural layer split**（純 refactor；無 scope / 功能變動）— 把
`google-slides-builder/protocols/` 下的 4 個 per-op recipe 抽出成 sibling
skill `google-slides-api`，builder 變薄保留 pipeline orchestration 職責。

### Added

- `skills/google-slides-api/SKILL.md` — 低層入口（op list + composition
  pattern via placeholder_map + when-to-use boundary）
- `skills/google-slides-api/references/api-error-codes.md` — 10/11/12/
  13a/13b/14/15/16/18 exit code 語意 + 救援 playbook，集中於此 reference

### Changed

- `skills/google-slides-api/protocols/recipe-create-presentation.md` ←
  `git mv` from `google-slides-builder/protocols/`
- `skills/google-slides-api/protocols/recipe-create-slides.md` ← git mv
- `skills/google-slides-api/protocols/recipe-insert-text.md` ← git mv
- `skills/google-slides-api/protocols/recipe-insert-image.md` ← git mv
- `skills/google-slides-builder/SKILL.md` — 變薄：改為引用 sibling
  skill 的 recipes；Step 2-4 路徑改為 `../google-slides-api/protocols/*`
- `skills/google-slides-builder/checklists/pre-flight.md` — 下游 recipe
  連結改為 sibling skill 路徑
- `skills/using-slides-toolkit/SKILL.md` — routing table 加第 4 分支
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

- `skills/google-slides-builder/protocols/` 目錄（內容移至 sibling skill）

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

- `skills/google-slides-builder/templates/`（整個目錄 + `registry.md`）
  — 使用者自備 template + Drive ID lookup 不再是 MVP 路徑
- `skills/google-slides-builder/protocols/recipe-copy-template.md`
  — `gws drive files copy` 流程不再需要
- `skills/google-slides-builder/protocols/recipe-replace-text.md`
  — 改名為 `recipe-insert-text.md`（new file）
- `bootstrap.sh` 的 SHA-256 驗證：`GWS_SHA256_*` / `JQ_SHA256_*` 4 個常數、
  `verify_sha256()` / `expected_sha_for()` 函式、exit code 17 `SHA mismatch`
  — 改以 HTTPS + `curl -fLSs` + URL pin 為 integrity 邊界

### Added

- `skills/google-slides-builder/protocols/recipe-create-presentation.md`
  — `gws slides presentations create --json '{"title":"..."}'` 建空 deck
- `skills/google-slides-builder/protocols/recipe-create-slides.md`
  — `batchUpdate createSlide` 搭配 `layout_hint` enum（7 個 Google 預設
  predefinedLayout 值）逐 slide 建構
- `skills/google-slides-builder/protocols/recipe-insert-text.md`
  — `batchUpdate insertText` 到 placeholder object ID（不再用
  `{{PLACEHOLDER}}` 文字錨點）
- slide-plan.json schema v1.1 → **v1.2**：新增 `slides[].layout_hint`
  （必填 enum）；刪除 `backend_config.template_ref`

### Changed

- `skills/google-slides-builder/SKILL.md` — 重寫 workflow 為 4-step
  （pre-flight → create → build slides → insert text/image）
- `skills/google-slides-builder/protocols/recipe-insert-image.md`
  — 從 `replaceAllShapesWithImage` 改為 `createImage` with explicit
  `pageElementProperties`，接 `placeholder_map` 對位
- `skills/google-slides-builder/checklists/pre-flight.md` — 10 項 check
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
- `scripts/google-slides/` 下 4 支 shell script：
  - `bootstrap.sh`（抓 gws + jq binary；SHA-256 pin + verify；idempotent）
  - `gws-wrap.sh`（pre-flight + retry with exponential backoff 5s/10s/20s）
  - `env-guard.sh`（issue #119 workaround，ISP 拆 `check` / `apply`）
  - `credential-check.sh`（Keychain silent-fail 偵測 + file backend fallback）
- `scripts/common/.gitkeep`（Phase 2+ 預留）
- `incidents/README.md`（on-demand playbook 入口）
- 4 個 SKILL.md：
  - `using-slides-toolkit`（backend-agnostic router）
  - `slides-design`（backend-agnostic 知識層）+ `references/minto-scqa.md`
    + `references/chart-selection.md` + `rubrics/slide-plan-self-check.md`
  - `google-slides-setup` + `protocols/gcp-console-walkthrough.md`（10 步）
    + `protocols/issue-119-workaround.md` + `standards/credential-hygiene.md`
    + `checklists/setup-state.md`
  - `google-slides-builder` + 3 recipe protocols（copy-template / replace-text
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

- `skills/slides-setup/` → `skills/google-slides-setup/`
  （backend-prefix 命名；Google Slides backend 專屬）
- `skills/slides-builder/` → `skills/google-slides-builder/`
  （backend-prefix 命名；Google Slides backend 專屬）
- `scripts/` 分子目錄 → `scripts/common/` + `scripts/google-slides/`
- `using-slides-toolkit`（router）與 `slides-design`（knowledge）
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
