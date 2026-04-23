# Changelog

All notable changes to `slides-toolkit` are documented in this file.

本檔案採 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 格式，
版本編號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [Unreleased]

### 即將 unblock（在 0.3.0 release 前，kouko 需完成）

- `scripts/google-slides/bootstrap.sh` 的版本 pin + SHA-256 常數
  （目前為 `TODO_FILL_REAL_SHA256_64HEX` placeholder）
- `skills/google-slides-builder/templates/registry.md` 加入 kouko 實際
  template 的 Drive ID（目前 3 筆 `client_proposal_v3` / `weekly_report`
  / `tech_talk` 皆為 `TODO` 骨架）
- 跑 `google-slides-setup` 完成首次 GCP Console OAuth
- 實測 end-to-end：brief → URL ≤ 3 分鐘（KR1 驗證）

### Phase 2+（trigger-gated；見 `PRODUCT-SPEC.md §3.5`）

- `html-builder` skill（首次 HTML 輸出需求觸發）
- `pptx-builder` skill（首次 `.pptx` 輸出需求觸發）
- `marp-builder` skill（首次 Marp 輸出需求觸發）
- `helpers/build_plan.py`（shell 組 JSON 首次出現痛苦時觸發）
- slide-plan schema 正式 backend-agnostic / backend-specific 切分
  （第二個 backend 實作時觸發）

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
