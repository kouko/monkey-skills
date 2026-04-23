# TECH-SPEC — slides-toolkit

Technical specification for the `slides-toolkit` plugin in the
`monkey-skills` repository. Scope: module design, data flow,
interface contracts, implementation plan. Product-level direction
(goals, users, scenarios, non-goals) lives in `PRODUCT-SPEC.md`
and is referenced by `§` number.

- Spec type: TECH-SPEC (code-team ownership)
- Target plugin: `slides-toolkit`
- Upstream PRODUCT-SPEC: `./PRODUCT-SPEC.md` (v0.2 — **Platform Pivot**
  multi-backend architecture)
- Written against `code-team/protocols/spec-writing.md` (5-phase
  house template: Scope → Architecture → Module → Interface → Testing)
- Compliance: OWASP ASVS v5.0.0 L1 (V1, V2, V5, V13, V14, V16);
  naming / pragmatic / SOLID / TDD / refactoring code-team standards
- Status: implementation-ready (all 11 `[OPEN]` questions from
  PRODUCT-SPEC §8 are resolved in §9 below)

### Revision History

| Date | Revision | Scope |
|---|---|---|
| 2026-04-?? | v0.1 — Initial MVP TECH-SPEC | Single-backend (Google Slides only); 4 skills = `using-slides-toolkit` / `slides-setup` / `slides-design` / `slides-builder` |
| 2026-04-23 | **v0.2 — Platform Pivot alignment** | 對齊 PRODUCT-SPEC v0.2。`slides-setup` → `google-slides-setup`；`slides-builder` → `google-slides-builder`（通用 router / 知識層不變）。目錄分 `scripts/common/` + `scripts/google-slides/`。`slide-plan.json` schema v1 → v1.1（新增 `target` + `backend_config`）。Phase 2+ backend（html / pptx / marp）保留擴充點，MVP 僅實作 `target: "google-slides"`。新增 OPEN-11 回答（§9） |

---

## 1. Scope & Constraints

### 1.1 Delivery form

CLI-style **Claude Code skill plugin**（四 skills，依 monkey-skills
plugin convention 放在 `plugins/slides-toolkit/`）。Platform Pivot 架構
下的四 skill 分為兩層：
- **Backend-agnostic layer**（通用）：`using-slides-toolkit`（router）、
  `slides-design`（knowledge）
- **Google Slides backend layer**（MVP 唯一 backend）：
  `google-slides-setup`、`google-slides-builder`

無 GUI、無 daemon、無 web server；每次由 user 在 Claude Code 內透過
slash command / skill invocation 觸發，Claude 以 Bash tool 呼叫本地
shell script。Phase 2+ 可插拔新 backend（html / pptx / marp）屬對應
builder skill 的獨立交付物，不改動 backend-agnostic layer。

### 1.2 Goals（技術目標；PRODUCT-SPEC §3.1 KRs 對映）

| 技術目標 | 對映 KR / Principle |
|---|---|
| brief → Google Slides URL ≤ 3 分鐘（測量起點：使用者提交 brief 的時刻） | KR1 |
| 全新機器 `google-slides-setup` bootstrap ≤ 20 分鐘（含 GCP Console 4 步） | KR2 |
| 零 Python / uv / gcloud / brew runtime 依賴 | §4.4 Runtime minimalism |
| Credential 絕不入 repo（ASVS V14 + V13 baseline） | §4.4 Credential never in repo |
| 所有 binary 由 skill 自抓到 `~/.cache/slides-toolkit/bin/` | §4.4 Runtime minimalism |
| Shell script 皆支援 `--dry-run` 模式，可在無網路、無 credential 下跑通 pipeline | §7 Testing |

### 1.3 Non-Goals（技術層面明列拒絕，非明顯 out-of-scope）

| Non-Goal | Rejected because |
|---|---|
| 自撰 OAuth flow / 自呼 `accounts.google.com` | gws CLI 已處理；重做會違反 §4.4 Runtime minimalism 並增加 ASVS V6 attack surface |
| JSON Schema 嚴謹校驗（ajv / pydantic） | MVP 用 `jq` 寬鬆校驗即可；Phase 2 trigger 見 PRODUCT-SPEC §3.5 |
| Binary 自 build（不用官方 release） | 破壞 integrity verification，違反 ASVS V13 (supply chain) |
| 跨平台 Linux / Windows 支援 | MVP macOS only（PRODUCT-SPEC §5.3）；Linux 差異主要在 Keychain fallback，留 Phase 2 |
| Persistent state / local DB | `registry.md` 是 runtime artifact，無結構化 DB；multi-deck 歷史查詢非 MVP |
| Retry queue / background job | 每次呼叫 synchronous；429 用指數退避 inline retry，不做 queue |

### 1.4 Hard constraints

| 面向 | 約束 | 來源 |
|---|---|---|
| 平台 | macOS 14+（darwin-arm64 / darwin-x64） | PRODUCT-SPEC §5.3 |
| Runtime | shell (zsh/bash) + curl + 瀏覽器，其餘 skill 自抓 | PRODUCT-SPEC §4.4 principle 1 |
| 實作語言 | 純 shell script + `jq` | PRODUCT-SPEC §6.3.2 |
| Binary cache | `~/.cache/slides-toolkit/bin/{gws,jq}` | 本 spec §2.3 |
| Credential | 存於 `~/.config/gws/`（gws 官方預設），Keychain 優先；**禁** commit | ASVS V14；PRODUCT-SPEC §6.3.2 |
| SKILL.md 長度 | 每份 ≤ 6,000 tokens（約 4,500 words） | CLAUDE.md |
| CI commit type 白名單 | `refactor / feat / fix / chore / docs`（test/ci 用 `chore`） | MEMORY.md `feedback_cc_type_whitelist` |
| 字元編碼 | UTF-8 only（pipeline 所有輸入 / 輸出 / 檔案 IO） | `character-encoding-security.md` §Verification |

---

## 2. Architecture

### 2.1 Plugin layout（target state — Platform Pivot multi-backend）

```
plugins/slides-toolkit/
├── .claude-plugin/
│   └── plugin.json                # plugin manifest
├── PRODUCT-SPEC.md                # (existing; v0.2)
├── TECH-SPEC.md                   # this file (v0.2)
├── README.md                      # user-facing entry (docs-team)
├── CHANGELOG.md
├── commands/                      # optional slash-command shims
│   └── slides.md
├── scripts/                       # plugin-scoped shell helpers（依 backend 分子目錄）
│   ├── common/                    # 跨 backend 共用（MVP 暫無；預留 Phase 2+）
│   └── google-slides/             # Google Slides backend 專屬
│       ├── bootstrap.sh           # fetch gws + jq binaries (SHA-256 verified)
│       ├── gws-wrap.sh            # thin wrapper: token ping + retry + JSON parse
│       ├── env-guard.sh           # issue-#119 env var detection + fallback
│       └── credential-check.sh    # Keychain / file-backend state detect
├── tests/
│   ├── dry_run/                   # no-network fixtures
│   ├── golden/                    # expected output snapshots
│   └── fixtures/                  # sample slide-plan.json, registry.md
├── incidents/                     # on-demand（平時不建立；§8.4 觸發時每起一份）
└── skills/
    ├── using-slides-toolkit/      # router（通用；依 target 選 backend skill）
    │   ├── SKILL.md
    │   └── references/
    │       └── skill-routing-map.md
    ├── slides-design/             # knowledge layer（backend-agnostic；通用）
    │   ├── SKILL.md
    │   ├── references/
    │   │   ├── minto-pyramid.md
    │   │   ├── scqa-opening.md
    │   │   └── chart-selection-table.md
    │   └── rubrics/
    │       └── design-self-check.md
    ├── google-slides-setup/       # [renamed from slides-setup]
    │   ├── SKILL.md                 # onboarding (gws + GCP + auth)；Google Slides backend 專屬
    │   ├── protocols/
    │   │   ├── first-time-setup.md
    │   │   ├── state-detection.md
    │   │   └── issue-119-workaround.md
    │   ├── checklists/
    │   │   ├── gcp-console-4-steps.md
    │   │   ├── credential-hygiene.md     # ASVS V14 + character-encoding
    │   │   └── post-setup-smoke-test.md
    │   ├── standards/
    │   │   └── minimum-scope-principle.md   # ASVS V1 least-privilege
    │   └── references/
    │       ├── gws-install.md
    │       ├── keychain-fallback.md
    │       └── token-lifecycle.md
    └── google-slides-builder/     # [renamed from slides-builder]
        ├── SKILL.md                 # execution layer；Google Slides backend 專屬
        ├── protocols/
        │   ├── plan-to-deck.md
        │   ├── recipe-copy-template.md
        │   ├── recipe-replace-all-text.md
        │   └── recipe-insert-image.md
        ├── checklists/
        │   ├── pre-flight-check.md         # target==google-slides validate + token + quota + template
        │   └── error-triage.md
        ├── standards/
        │   └── slide-plan-schema.md        # schema v1.1（target + backend_config）
        ├── templates/
        │   └── registry.md                 # Drive ID registry（Google Slides backend only；§4.7）
        └── references/
            ├── registry-format.md
            └── gws-command-map.md

# Phase 2+（trigger-gated per PRODUCT-SPEC §3.5；MVP 不建立）
# ├── scripts/{html,pptx,marp}/
# └── skills/{html,pptx,marp}-builder/
```

**Rename migration log（TECH-SPEC v0.1 → v0.2）**：

| 舊名 | 新名 |
|---|---|
| `skills/slides-setup/` | `skills/google-slides-setup/` |
| `skills/slides-builder/` | `skills/google-slides-builder/` |
| `scripts/bootstrap.sh` | `scripts/google-slides/bootstrap.sh` |
| `scripts/gws_wrap.sh` | `scripts/google-slides/gws-wrap.sh` |
| `scripts/env_guard.sh` | `scripts/google-slides/env-guard.sh` |
| `scripts/credential_check.sh` | `scripts/google-slides/credential-check.sh` |
| `skills/slides-builder/templates/registry.md` | `skills/google-slides-builder/templates/registry.md` |

`using-slides-toolkit`（通用 router）與 `slides-design`（backend-agnostic
知識層）**不改名**。shell script 檔名由 `_` 改為 `-`（hyphen-case）對齊
PRODUCT-SPEC v0.2 的目錄結構示例。

**Because** 四 skill 切分對應四種關注點（入口 / 首次設定 / 知識 / 執行）；
backend-prefix 命名（`google-slides-*`）對齊 PRODUCT-SPEC v0.2 §6.3.1
的 Platform Pivot 架構——同一 backend 的 skill 群組一目了然；未來加
`html-builder` / `pptx-builder` / `marp-builder` 不污染現有命名空間。
檔案結構遵循 CLAUDE.md「bundled files 從 skill 目錄相對解析、one level
deep」規則，所有 reference files 由各自 SKILL.md 直接引用，不巢狀。

**Layout 注記**：
- 本 TECH-SPEC 採「plugin root 直放 SPEC 檔」設計，不建立 `docs/` 子目錄；
  `PRODUCT-SPEC.md` / `TECH-SPEC.md` / `README.md` / `CHANGELOG.md` 皆於
  plugin root。**Because** DRY 與一致性原則（pragmatic-principles）：
  monkey-skills 其他 plugin 已慣用 plugin-root flat 放置。PRODUCT-SPEC v0.2
  §6.3.1 已對齊此設計（F6 已吸收）。
- `registry.md` 實際路徑為 `skills/google-slides-builder/templates/registry.md`
  （屬於 `google-slides-builder` skill 的 Google-Slides-backend-only runtime
  artifact；非 plugin root）。未來新 backend 若有類似 registry 需求，放於
  對應 backend skill 內，不污染通用層。
- `incidents/` 目錄為 **on-demand 建立**（非預設骨架一部分）：僅在
  §8.4 incident response playbook 實際觸發時才建
  `plugins/slides-toolkit/incidents/`，平時不佔目錄樹。
- `scripts/common/` 為 **預留目錄**：MVP 無跨 backend 共用 shell；Phase 2+
  第二個 backend 落地時才填入實際共用工具（見 §5.1 C12 deferred note）。

### 2.2 Architecture diagram（Platform Pivot — MVP: google-slides backend only）

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Claude Code (user session)                                             │
│  /using-slides-toolkit → router（依 slide-plan.target 路由到 backend）    │
└────────────────────────┬────────────────────────────────────────────────┘
                         │ (skill routing; no shared state)
        ┌────────────────┼────────────────────┬─────────────────┐
        ▼                ▼                    ▼                 ▼
 ┌──────────────┐  ┌───────────┐     ┌──────────────────┐  (Phase 2+
 │ slides-design│  │ google-   │     │ google-slides-   │   deferred)
 │ (knowledge;  │  │ slides-   │     │ builder          │  ┌──────────┐
 │  backend-    │  │ setup     │     │ (execute;        │  │ html/pptx│
 │  agnostic)   │  │ (onboard; │     │  target ==       │  │ /marp    │
 │              │  │  gs       │     │  "google-slides")│  │ builder  │
 │              │  │  backend) │     │                  │  └──────────┘
 └──────┬───────┘  └────┬──────┘     └────────┬─────────┘
        │               │ env-guard check+apply│ env-guard check (pre-flight)
        │               │                     │
        │               │                     │ slide-plan.json v1.1 (stdin)
        │               │                     │   ├ target: "google-slides"
        │               │                     │   ├ backend_config.template_ref
        │               │                     │   └ slides[]  (backend-agnostic)
        │               │                     ▼
        │               │   ┌────────────────────────────────────────┐
        │               │   │ scripts/google-slides/gws-wrap.sh      │
        │               │   │   ├ env-guard.sh check (issue #119)    │
        │               │   │   ├ credential-check.sh (keychain)     │
        │               │   │   └ retry 429 ↻                        │
        │               │   └───────────────┬────────────────────────┘
        │               │                   │
        │               ▼                   ▼
        │     ┌────────────────────────┐  ┌──────────────────────────┐
        │     │ scripts/google-slides/ │  │ ~/.cache/slides-toolkit/ │
        │     │   bootstrap.sh         │  │   bin/gws                │
        │     │   (fetch gws + jq,     │  │   bin/jq                 │
        │     │    SHA-256 verified)   │  └──────────┬───────────────┘
        │     └────────────┬───────────┘             │
        │                  ▼                         ▼
        │          ~/.cache/slides-         Google Slides / Drive API
        │          toolkit/bin/                      │
        │                                            ▼
        └─→ (read-only design knowledge; no I/O;     Google Slides URL
             對所有 backend 通用)
```

**Backend boundary**（MVP 僅 google-slides，Phase 2+ 擴充）：
- **Backend-agnostic layer**：`using-slides-toolkit`（router）、
  `slides-design`（knowledge）、`slide-plan.json` 頂層 schema（`target` +
  `slides[]`）
- **Google Slides backend layer**：`google-slides-setup`、
  `google-slides-builder`、`scripts/google-slides/*.sh`、`registry.md`、
  `backend_config.template_ref`
- **Phase 2+ backend layers**（deferred；虛線框）：`{html,pptx,marp}-builder`
  + `scripts/{html,pptx,marp}/*.sh`，各自有對應 setup skill（若需要）

### 2.3 Binary distribution strategy（自抓模型；ASVS V13 supply chain）

- **Where**：`~/.cache/slides-toolkit/bin/{gws,jq}`。使用 XDG-like path
  但遵循 macOS 慣例（`~/.cache/` 而非 `~/Library/Caches/`，因為 shell
  script 跨機器相容性優先）。
- **How**：`scripts/google-slides/bootstrap.sh` 由 `google-slides-setup` 在首次執行時呼叫（Google Slides backend 專屬）。
  - `gws`：從 `github.com/googleworkspace/cli/releases` 下載對應
    平台 binary（`darwin-arm64` / `darwin-x86_64`）；版本 pin 於
    `slides-toolkit` 發版時的最新 stable。
  - `jq`：從 `github.com/jqlang/jq/releases` 下載；版本 pin
    於 `jq-1.7.1` 或更新。
- **Integrity**：每個 release 下載 `SHA256SUMS` 比對；mismatch 則
  abort 並回傳 exit 17（見 §4.2 exit code 表）。**Because** ASVS
  V13 要求外部依賴須 integrity verification。
- **Upgrade**：bootstrap 檢查 `~/.cache/slides-toolkit/bin/.version`
  檔對比 pin 版本；升級時覆寫並重新驗 SHA-256。

### 2.4 External dependencies

**MVP（Google Slides backend 啟用）**

| Dep | Backend scope | Version pin | License | Acquisition | Integrity |
|---|---|---|---|---|---|
| `gws` (googleworkspace/cli) | google-slides | `v0.X.Y`（具體版本於 C2 commit 時 pin，以 `.version` file + SHA-256 雙鎖；當下為 TBD，release commit 會填入） | Apache-2.0 | GitHub release（靜態 Rust binary） | SHA-256 |
| `jq` | common（MVP 僅 google-slides 用；Phase 2+ 其他 backend 也可能用） | `1.7.1+` | MIT | GitHub release | SHA-256 |
| Google Slides API v1 | google-slides | stable | Google T&C | 透過 gws | OAuth2 Bearer |
| Google Drive API v3 | google-slides | stable | Google T&C | 透過 gws | OAuth2 Bearer |

**Phase 2+ backend 預期依賴**（trigger-gated per PRODUCT-SPEC §3.5 §6.3.4；
**不**在 MVP 實作，列於此僅供 forward-looking review）：

| Phase 2+ Backend | 可能 dep | Runtime impact |
|---|---|---|
| `html-builder` | pandoc / handlebars / 純 shell template | 可能維持純 shell（符合 runtime minimalism）；視 HTML 風格（reveal.js / remark / 純靜態）選 |
| `pptx-builder` | python-pptx（Python runtime）或 LibreOffice headless | **破壞 MVP runtime minimalism**；觸發時須 scope 到該 skill 內部，不污染其他 backend |
| `marp-builder` | marp-cli | 引入 Node.js runtime；scope 同 pptx |

**Because** 新 backend 的 runtime dep 可能違反 MVP 的 "pure shell + gws
binary" 原則；觸發 Phase 2+ 實作時，每個 backend 在對應 builder skill 內
獨立評估，**既有 `google-slides-*` skill 不受影響**（Backend pluggability
principle，PRODUCT-SPEC §4.4 principle 6）。

**Plugin license**：本 `slides-toolkit` plugin 本身採 MIT（對齊
PRODUCT-SPEC §6.1，monkey-skills repo 整體 license）。外部 binary
（gws / jq）license 列於上表，不變更其原 license；plugin 僅 bundle
SHA-256 pin + 下載腳本，不 redistribute binary。

**MVP No-deps 承諾**：**No** Python runtime, **no** uv, **no** gcloud,
**no** brew, **no** npm。符合 PRODUCT-SPEC §4.4 principle 1
（runtime minimalism）。

### 2.5 Cross-skill dependency graph（one-level-deep；Platform Pivot layers）

```
[Backend-agnostic layer — 通用]
using-slides-toolkit  ─┬─► slides-design          (knowledge; backend-agnostic)
                       ├─► google-slides-setup    (if target=google-slides, 未設定)
                       └─► google-slides-builder  (if target=google-slides, 已設定)
                           └─► (Phase 2+) html-builder / pptx-builder / marp-builder

slides-design         ──► (no I/O; references/ only; 對所有 backend 適用)

[Google Slides backend layer]
google-slides-setup   ──► scripts/google-slides/bootstrap.sh
                      ──► scripts/google-slides/credential-check.sh
                      ──► scripts/google-slides/env-guard.sh   (issue #119)

google-slides-builder ──► scripts/google-slides/gws-wrap.sh
                      ──► scripts/google-slides/env-guard.sh
                      ──► ~/.cache/slides-toolkit/bin/{gws,jq}
                      ──► skills/google-slides-builder/templates/registry.md
```

符合 CLAUDE.md「Reference files 從 SKILL.md 直接引用，one level deep」。
跨 skill 不直接 import 其他 skill 的 protocol；共用邏輯全部下沉到
plugin root 的 `scripts/<backend>/` 或 `scripts/common/`，以相對路徑
`../../scripts/google-slides/` 引用。

**Protocol ↔ script mapping**（補強：讓 protocol 與 shell 實作的對應顯
式化，避免 reader 在 skill 目錄 / scripts 目錄來回追蹤）：

| Protocol | 呼叫 script (subcommand) |
|---|---|
| `google-slides-setup/protocols/first-time-setup.md` | `scripts/google-slides/bootstrap.sh`, `scripts/google-slides/credential-check.sh` |
| `google-slides-setup/protocols/state-detection.md` | `scripts/google-slides/credential-check.sh`, `scripts/google-slides/env-guard.sh check` |
| `google-slides-setup/protocols/issue-119-workaround.md` | `scripts/google-slides/env-guard.sh check`, `scripts/google-slides/env-guard.sh apply` |
| `google-slides-builder/protocols/plan-to-deck.md` | `scripts/google-slides/gws-wrap.sh`（內含 `env-guard.sh check` pre-flight + `target == "google-slides"` validation） |
| `google-slides-builder/protocols/recipe-copy-template.md` | `scripts/google-slides/gws-wrap.sh drive files copy` |
| `google-slides-builder/protocols/recipe-replace-all-text.md` | `scripts/google-slides/gws-wrap.sh slides presentations batchUpdate` |
| `google-slides-builder/protocols/recipe-insert-image.md` | `scripts/google-slides/gws-wrap.sh drive files upload` + `batchUpdate` |

**Because** 讓 §2.5 dependency graph 從「靜態目錄關聯」升級為「語意
protocol→action mapping」，降低 onboarding 成本（pragmatic-principles
knowledge locality）；同時顯式標示 backend layer，為 Phase 2+ 新 backend
提供映照範本。

---

## 3. Module Design

> 每模組標示：I/O / deps / errors / edge cases / readiness。

### 3.1 `using-slides-toolkit`（router skill — backend-agnostic）

- **Role**：使用者 entry + **target backend 決策**。讀 user intent，解析
  `target` 意圖（MVP 預設 `"google-slides"`），路由到對應 backend skill：
  - 設計諮詢（no target needed）→ `slides-design`
  - `target == "google-slides"` + 未設定 → `google-slides-setup`
  - `target == "google-slides"` + 已設定 → `google-slides-builder`
  - `target ∈ {"html","pptx","marp"}` → Phase 2+ 未實作；回訊息並指向
    PRODUCT-SPEC §3.5 trigger
- **Input**：自然語言（Claude Code session text）；若 user 已備
  `slide-plan.json` 則讀其頂層 `target` 欄位
- **Output**：建議下一步 skill 呼叫 + 理由（一段話），or 直接呼叫目標 skill
- **Deps**：無 shell script 呼叫；純文字路由
- **Errors**：N/A（純 routing；未支援 target 時由 builder 層報 exit 12，見 §9 OPEN-11）
- **Edge cases**：
  - user 同時提及 setup + builder → 先建議 setup，再 builder（state-aware
    onboarding，PRODUCT-SPEC §4.4 principle 5）
  - slide-plan 缺 `target` → router 假設 `"google-slides"`（MVP 唯一 backend）
    並告知 user；Phase 2+ 引入第二個 backend 時升級為強制要求
- **Readiness**：READY

### 3.2 `google-slides-setup`（onboarding skill — Google Slides backend only）

> Renamed from `slides-setup` (TECH-SPEC v0.1). 內容保持不變；命名加
> backend prefix 以對齊 Platform Pivot。

- **Role**：Google Slides backend 的首次機器設定。涵蓋：(1) bootstrap
  binary、(2) GCP Console 4 步手動（checklist 引導）、(3) `gws auth` +
  issue #119 workaround、(4) credential hygiene 驗證、(5) post-setup smoke test
- **Input**：無結構化輸入；只依賴 state detection（`scripts/google-slides/credential-check.sh`）
- **Output**：
  - 人讀 progress（Claude 透過 TaskUpdate 回報）
  - `~/.config/gws/` 生成 credential files
  - `~/.cache/slides-toolkit/bin/{gws,jq}` 生成
  - `.version` 標記檔
- **Deps**：
  - `scripts/google-slides/bootstrap.sh`
  - `scripts/google-slides/credential-check.sh`
  - `scripts/google-slides/env-guard.sh`（issue #119 偵測）
  - 外部：curl、gws binary、Google OAuth 頁面（瀏覽器）
- **Errors**：
  - `SHA-256 mismatch` → abort，exit 17
  - `GCP Console 未設定` → 停在 checklist，等 user 完成 4 步後 `continue`
  - `issue #119 invalid_scope` → 偵測到即切 env var workaround 分支
  - `Keychain silent fail` → fallback `KEYRING_BACKEND=file`
- **Edge cases**：
  - User 已半裝完（binary 有、token 無）→ state detect 跳到 auth 步
  - 過去 7 天未用，token 過期 → `gws auth` re-login（passive 告知，非
    自動 prompt；見 §6.3）
- **Readiness**：READY（issue #119 workaround 可行，已在 PRODUCT-SPEC
  §6.3.3 確認）

### 3.3 `slides-design`（knowledge skill — backend-agnostic）

- **Role**：Claude 生成 slide plan 時的設計 reference。提供 Minto
  Pyramid / SCQA 敘事結構 + chart-selection 對照表。**知識對所有 backend
  適用**（Google Slides / Phase 2+ html / pptx / marp），因此不含任何
  backend-specific 元素（Drive ID、gws 命令、OAuth scope 皆屬 builder 層）。
- **Input**：Claude 自行讀 `references/*.md`
- **Output**：設計建議文字（header / chart type / narrative order）
- **Deps**：無 shell script，無外部 API
- **Errors**：N/A
- **Edge cases**：
  - User 要 Tufte / 高橋メソッド 深度 → 回「Phase 2 trigger 條件
    未達」（PRODUCT-SPEC §3.5）並提供現有 baseline
- **Readiness**：READY

### 3.4 `google-slides-builder`（execution skill — Google Slides backend only）

> Renamed from `slides-builder` (TECH-SPEC v0.1). 內容保持不變；命名加
> backend prefix，並新增 `target` validation 以對齊 slide-plan schema v1.1。

- **Role**：Google Slides backend 核心執行層。讀 `slide-plan.json` v1.1
  （見 §4.1 schema），validate `target == "google-slides"`（否則 exit 12），
  再呼叫 `scripts/google-slides/gws-wrap.sh`，執行 3 core recipe
  （copy template / replaceAllText / insert local image），回傳 Drive URL。
- **Input**：
  - `slide-plan.json`（schema v1.1，見 §4.1）—— 必含 `target: "google-slides"`
    + `backend_config.template_ref`
  - `registry.md` 內的 template Drive ID（由 `backend_config.template_ref` 查出）
- **Output**：
  - stdout：JSON `{"deck_url": "...", "deck_id": "...", "operations": [...]}`
  - stderr：人讀 progress（TaskUpdate 對應事件）
  - exit code：見 §4.2
- **Deps**：
  - `scripts/google-slides/gws-wrap.sh`
  - `scripts/google-slides/env-guard.sh`
  - `~/.cache/slides-toolkit/bin/{gws,jq}`
  - Google Slides / Drive API（via gws）
- **Errors**（結構化 JSON to stderr + exit code）：
  - `target` 未設定或不等於 `"google-slides"` → exit 12，訊息內含「backend
    `<value>` 尚未實作，請改用 `google-slides`」並指向 PRODUCT-SPEC §3.5
    Phase 2+ trigger
  - token 過期 → exit 10，提示跑 `gws auth`
  - 429 rate limit → 指數退避重試，最多 5 次；全敗後 exit 11
  - template Drive ID not found → exit 12
  - placeholder key 在 template 中不存在 → exit 13（warning，非 fatal）
  - local image path 不存在 → exit 14
  - slide-plan.json schema 錯（含 `backend_config.template_ref` 缺失） → exit 15
- **Edge cases**：
  - `slide-plan.json` 空 slides 陣列 → 只 copy template，回 URL
  - `slides[].images[].local_path` 含 `~` / 相對路徑 → 解析規則見 §9 OPEN-8
  - template 被使用者改動 placeholder key → 回 exit 13 warning 列
    具體 missing keys，由 user 判斷繼續或中止
- **Readiness**：READY

---

## 4. Interface & Data Flow

### 4.1 `slide-plan.json` schema v1.1（寬鬆 JSON，jq 驗證；Platform Pivot）

MVP 採 **flat 寬鬆 schema**；不引入 JSON Schema 工具鏈。欄位以 `jq`
verify（exit 15 on failure）。

**Schema version jump v1 → v1.1**：新增頂層 `target` + `backend_config`
以對齊 PRODUCT-SPEC v0.2 Platform Pivot。**不**做 v1 backward-compat
（MVP 無既有 user；直接 v1.1 省除 migration 複雜度）。`slides[]` 陣列
**保持 backend-agnostic**（對任何 backend 適用），backend-specific 設定
（template Drive ID 等）集中於 `backend_config`。

```json
{
  "version": "1.1",
  "target": "google-slides",
  "output_title": "2026-W17 Weekly Report",
  "dry_run": false,
  "backend_config": {
    "template_ref": "weekly_report"
  },
  "slides": [
    {
      "slide_index": 0,
      "layout_hint": "title-body",
      "replacements": {
        "{{title}}": "2026-W17 Progress",
        "{{date}}": "2026-04-23"
      },
      "images": []
    },
    {
      "slide_index": 3,
      "layout_hint": "headline-image",
      "replacements": {
        "{{headline}}": "Shipped v1.14.0"
      },
      "images": [
        {
          "placeholder_id": "IMG_MAIN",
          "local_path": "~/Desktop/chart.png"
        }
      ]
    }
  ]
}
```

欄位定義：

| Field | Type | Required | Validation (jq) | Layer |
|---|---|---|---|---|
| `version` | string | yes | `== "1.1"` | top（backend-agnostic） |
| `target` | string | yes | MVP 只允許 `"google-slides"`；其他值 → builder exit 12 | top（backend-agnostic） |
| `output_title` | string | yes | non-empty, UTF-8 | top（backend-agnostic） |
| `dry_run` | bool | no (default `false`) | if `true` → 只跑 schema + registry + local image 存在性檢查，不呼 Google API（§7.3） | top（backend-agnostic） |
| `backend_config` | object | yes | 各 backend 自定；MVP（google-slides）必含 `template_ref` | per-backend |
| `backend_config.template_ref` | string | yes (google-slides) | 需對應 `registry.md` 內一筆 entry | google-slides only |
| `slides` | array | yes | allow empty → only copy template | top（backend-agnostic） |
| `slides[].slide_index` | int | yes | `>= 0` | backend-agnostic |
| `slides[].layout_hint` | string | no | 通用 layout hint（e.g. `title-body` / `headline-image` / `bullets` / `quote`）；各 backend 自行解讀、無強制對應 | backend-agnostic |
| `slides[].replacements` | object | no | keys 建議以 `{{...}}` 包 | backend-agnostic |
| `slides[].images[].placeholder_id` | string | if images present | non-empty | backend-agnostic |
| `slides[].images[].local_path` | string | if images present | file exists（builder pre-flight check） | backend-agnostic |

**Backend-agnostic vs per-backend 切分原則**：
- **Top-level + `slides[]`** 是跨 backend 通用 contract；新 backend 不
  得改此部分欄位語意
- **`backend_config`** 是 per-backend escape hatch；每個 backend 在自
  己的 builder skill 文件中定義 `backend_config.*` 欄位（例：
  `html-builder` 可能需 `theme`, `revealjs_config` 等）
- `layout_hint` 為通用 hint（非強制對應）；google-slides backend 目前
  忽略此欄（template-driven），Phase 2+ backend 可用來選 HTML section
  結構或 Marp layout 指令

**MVP unsupported target 處理**：`google-slides-builder` 在 pre-flight
檢查 `target != "google-slides"` → exit 12 + 訊息「backend `<value>`
尚未實作，請改用 google-slides」。詳見 §9 OPEN-11。

**Phase 2 trigger**：
- 手寫 JSON 變痛苦（PRODUCT-SPEC §3.5）→ 升 Pydantic / JSON Schema 做
  嚴謹校驗
- 第二個 backend（html / pptx / marp）實際落地（PRODUCT-SPEC §3.5 trigger）
  → 正式化「backend-agnostic 核心 vs backend-specific extension」切分，
  定義 `backend_config` 的 per-backend schema fragment

### 4.2 Shell script contracts

通用約定：

- **stdin**：JSON（若有）
- **stdout**：JSON（machine-readable result）
- **stderr**：人讀 progress（Claude 讀此做 TaskUpdate）
- **exit code 表**：

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | generic error（usage / args） |
| 10 | token expired / unauthenticated |
| 11 | rate limit exhausted after retry |
| 12 | Google resource not found (template / deck) |
| 13 | placeholder / template mismatch — warning 類；4 子語意 (13a/13b/13c/13d) 見下表，non-fatal if caller overrides |
| 14 | local file not found (image) |
| 15 | schema validation failed |
| 16 | gws issue #119 / invalid_scope（需切 env var workaround） |
| 17 | SHA-256 mismatch on binary fetch |
| 18 | Keychain unavailable and file-backend also failed |

**Exit 13 sub-semantics**（stderr JSON 的 `subcode` 欄位帶值；exit code
仍為 13，方便 Claude 做 TaskUpdate 訊息分流）：

| Subcode | Meaning | 發生點 |
|---|---|---|
| 13a | `replaceAllText` 零 replacement — 要替換的文字在 template 中一個也找不到 | recipe-replace-all-text |
| 13b | `createImage` 找不到 placeholder object id — 指定的 shape/placeholder id 不存在於 template | recipe-insert-image |
| 13c | `replaceAllShapesWithImage` 找不到 placeholder text — 指定的 placeholder 文字 token 在 template shape 內找不到 | recipe-insert-image (fallback path) |
| 13d | Template schema drift — 使用者改動 template placeholder key，與 `registry.md` 內 `schema_fingerprint` 不符（§4.7、OPEN-10） | pre-flight check |

**Because** 4 種情境對 user 的修補動作不同（改文字 / 改 placeholder id /
改 registry fingerprint / 重新 approve template），單一 exit 13 難以
TaskUpdate 分流；subcode 讓 Claude 給出具體下一步，又不破壞 exit code
語意穩定。

Per-script contracts：

#### `scripts/google-slides/bootstrap.sh`

| 項 | 內容 |
|---|---|
| Args | `--force`（可選，重新下載；預設只在 `.version` 不符時下載）；`--dry-run`（只 fetch + SHA check，不寫 binary，見 §7.3）；`--platform <darwin-arm64\|darwin-x86_64>`（override auto-detect，主要用於 CI / 跨機器測試） |
| Stdin | none |
| Stdout | `{"gws_version":"...","jq_version":"...","cache_dir":"..."}` |
| Errors | exit 17（SHA-256 mismatch），exit 1（network / 未知 platform） |
| Pseudo-code intent | detect platform (或讀 `--platform`) → download release → SHA-256 verify → chmod +x → write `.version` |

#### `scripts/google-slides/gws-wrap.sh`

| 項 | 內容 |
|---|---|
| Args | `<subcommand>` `<args...>`（轉傳 gws）；`--dry-run`（不呼 gws，只印出即將執行的命令 + args，見 §7.3） |
| Stdin | raw JSON（若 subcommand 需要） |
| Stdout | gws 回傳的 JSON，原樣 passthrough |
| Behavior | (1) `env-guard.sh check` pre-flight（不 apply，見 §6.1）；(2) 呼叫前 `gws auth status` ping；(3) 429 指數退避 retry（1s, 2s, 4s, 8s, 16s）；(4) 解析 structured error |
| Errors | exit 10/11/12/16 |

#### `scripts/google-slides/env-guard.sh`

| 項 | 內容 |
|---|---|
| Args | `check` \| `apply` |
| Stdin | none |
| Stdout | `{"workaround_needed":true/false}` |
| Behavior | `check` 測一次 `gws auth` 看 `invalid_scope`；`apply` 設 `GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET` env var（由 user 在 `google-slides-setup` 補入 `~/.config/gws/env.sh`） |
| Errors | exit 16 |

#### `scripts/google-slides/credential-check.sh`

| 項 | 內容 |
|---|---|
| Args | none |
| Stdin | none |
| Stdout | `{"backend":"keychain"\|"file","token_valid":bool,"expires_in_sec":int}` |
| Behavior | 偵測 Keychain 可讀 → fallback `KEYRING_BACKEND=file`；讀 gws token 到期時間 |
| Errors | exit 18 |

### 4.3 gws CLI 呼叫模式（google-slides backend only）

> 本節 recipe 全部屬 **Google Slides backend**；`target != "google-slides"`
> 時 builder 在 pre-flight 已 exit 12，不進入本節。Phase 2+ backend 的
> recipe 集將由對應 builder skill 自行定義。

MVP 使用以下 gws 命令（對映 3 core recipe）：

| Recipe | gws command (intent) | 失敗策略 |
|---|---|---|
| Copy template | `gws drive files copy` with `parents` + `name` | exit 12 on not-found；429 retry |
| Replace all text | `gws slides presentations batchUpdate` with `replaceAllText` requests | exit 13 warning on zero replacements；429 retry |
| Insert local image | `gws drive files upload` → get fileId → `presentations batchUpdate` with `createImage` | exit 14 on local missing；exit 13 on placeholder id 不存在 |

**Retry policy**：429 指數退避 `1s → 2s → 4s → 8s → 16s`，jitter
`±20%`，最多 5 次；其他 5xx 也適用。4xx（401/403/404）不 retry，
直接 exit code。

**Because** 指數退避 + jitter 是 Google 官方建議（`docs/reference/retry.md`
in Google Cloud client libraries），MVP 不引入第三方 retry lib，
inline shell loop 即可。

### 4.4 Google API scope 清單（google-slides backend only；least-privilege，ASVS V1）

> 本節 scope / auth 模型屬 **Google Slides backend**。Phase 2+ 其他
> backend 有各自 scope / auth 模型（例：`marp-builder` 若用 marp-cli 通常
> 無需 OAuth；`html-builder` 若輸出到 S3 / GitHub Pages 需另外 token；
> `pptx-builder` 本地輸出通常無需 scope）——各 backend 在其 builder skill
> 文件內獨立列明。


| Scope | Needed by | Because |
|---|---|---|
| `https://www.googleapis.com/auth/presentations` | replaceAllText / createImage batchUpdate | 唯一能改 Slides 的 scope |
| `https://www.googleapis.com/auth/drive.file` | copy template / upload image | `drive.file` 限制為「本 app 建立 / 開啟的 file」，比 `drive` 全權限安全；符合 ASVS V1 principle of least privilege |

**不要求** `drive`（full read）、`drive.readonly`、`userinfo.email`
等非必要 scope。**Because** OWASP ASVS v5.0.0 V1 + V13 要求最小權限；
多要 scope 擴大 credential 洩漏時的 blast radius。

### 4.5 Claude Code 互動介面

- **Slash command**：`/using-slides-toolkit` → router；後續子命令
  `/google-slides-setup`, `/slides-design`, `/google-slides-builder` 由
  Claude 路由或 user 直接呼。Phase 2+ 新 backend 引入 `/html-builder`,
  `/pptx-builder`, `/marp-builder` 等；router 依 `target` 分派。
- **Skill invocation pattern**：每個 SKILL.md 遵循 monkey-skills
  convention：self-contained、≤ 6k tokens、bundled files 相對路徑。
- **TaskUpdate 使用**：
  - `google-slides-setup`：phase transitions（bootstrap / GCP check /
    auth / smoke test），milestones，heartbeat ≤60s
  - `google-slides-builder`：每個 recipe 開始 / 結束；429 retry 時發一次；
    `target` validation 失敗即刻發一次並 exit 12
  - `slides-design`：不發（純知識層）
  - 規範依 Visibility Convention（本 task 附註）

### 4.6 End-to-end data flow（google-slides-builder 主路徑）

```
Claude Code
   │  (user paste slide-plan.json v1.1 + pick backend_config.template_ref)
   ▼
google-slides-builder SKILL.md
   │  Read protocols/plan-to-deck.md
   ▼
[pre-flight] checklists/pre-flight-check.md
   │  ├─ jq: validate version == "1.1"  (else exit 15)
   │  ├─ jq: validate target == "google-slides"  (else exit 12)
   │  ├─ jq: validate backend_config.template_ref present  (else exit 15)
   │  ├─ token ping  (credential-check.sh)
   │  ├─ registry.md lookup  (jq '.entries[] | select(.ref==$r) | .drive_id')
   │  ├─ local image files exist
   │  └─ jq schema validate slides[] (backend-agnostic 部分)
   ▼
[recipe 1] gws drive files copy
   │  → new_deck_id
   ▼
[recipe 2] gws slides presentations batchUpdate (replaceAllText ×N)
   │
   ▼
[recipe 3] for each image:
   │    gws drive files upload → upload_file_id
   │    gws slides presentations batchUpdate (createImage)
   ▼
stdout JSON:
  {"deck_url": "https://docs.google.com/presentation/d/<id>/edit",
   "deck_id": "<id>",
   "operations": [...]}
```

### 4.7 `registry.md` format（google-slides backend only；OPEN-2 解；見 §9）

> 路徑：`skills/google-slides-builder/templates/registry.md`。此檔為
> **Google Slides backend runtime artifact**——Drive ID 是 Google-native
> 概念；Phase 2+ 其他 backend 若需 template registry，各自於對應 builder
> skill 內定義（例：`pptx-builder` 可能記本機 `.pptx` 路徑，`marp-builder`
> 可能記 markdown template 路徑）。

純 markdown table + 可選 YAML front-matter 記 metadata：

```markdown
---
version: 1
owner: kouko
---

# slides-toolkit template registry

| ref | drive_id | schema_fingerprint | notes |
|---|---|---|---|
| weekly_report | 1AbC...XyZ | sha1:a1b2c3... | 12 pages; placeholders in `references/weekly-report-placeholders.md` |
| client_pitch | 1DeF...UvW | sha1:d4e5f6... | 18 pages; title / agenda / 3 sections / 6 content / closing |
```

`schema_fingerprint` 為可選欄位（OPEN-10 解，見 §9），MVP 用 sha1
hash template 的 placeholder 清單；偵測 template 被改時 warn user。

### 4.8 Credential flow（ASVS V14）

```
[Primary path: macOS Keychain]
~/.config/gws/config.yaml  (non-secret; account, client_id ref)
     │
     ▼
macOS Keychain  ← gws 預設寫入 (refresh_token)
     │  (silent-fail risk)
     ▼
[Fallback: file backend]
~/.config/gws/keyring-file.json  (chmod 600; refresh_token)

[Issue #119 workaround layer]
~/.config/gws/env.sh  (chmod 600)
     │  export GOOGLE_WORKSPACE_CLI_CLIENT_ID=...
     │  export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=...
     ▼
env guard source 之前再呼 gws
```

所有 credential 檔案須 chmod 600；`.gitignore` 明確排除；
`settings.json` 加 deny rule（見 §8）。

---

## 5. Implementation Plan

### 5.1 Commit 切分（遵循 CC CI type 白名單：refactor/feat/fix/chore/docs）

| # | Commit type + scope | Content | Validation |
|---|---|---|---|
| C1 | `docs(slides-toolkit): add TECH-SPEC v0.2 (Platform Pivot alignment)` | 本檔案 | spec-review skill manual |
| C2 | `feat(slides-toolkit): plugin scaffold + manifest` | `.claude-plugin/plugin.json`、`README.md` stub、目錄骨架（含 `scripts/common/` + `scripts/google-slides/` + `skills/` 空殼） | `plugin.json` 通過 JSON parse |
| C3 | `feat(slides-toolkit): google-slides binary bootstrap (gws + jq, SHA-256 verified)` | `scripts/google-slides/bootstrap.sh`、SHA256SUMS fixture | dry-run 跑 bootstrap、驗 cache dir |
| C4 | `feat(slides-toolkit): google-slides credential + env guard scripts` | `scripts/google-slides/credential-check.sh`、`scripts/google-slides/env-guard.sh`、`scripts/google-slides/gws-wrap.sh` | 無 credential 下跑 `--dry-run` 看分支 |
| C5 | `feat(slides-toolkit): google-slides-setup skill` | `skills/google-slides-setup/` 全部 | bats smoke test；manual GCP Console 4 步 walkthrough |
| C6 | `feat(slides-toolkit): slides-design skill (knowledge only; backend-agnostic)` | `skills/slides-design/` 全部 | SKILL.md token budget check（≤ 6k） |
| C7 | `feat(slides-toolkit): google-slides-builder 3 core recipes + target validation` | `skills/google-slides-builder/`、protocols/recipe-* 、`target == "google-slides"` pre-flight | golden-path dry-run 測三 recipe；錯 target 驗 exit 12 |
| C8 | `feat(slides-toolkit): using-slides-toolkit router with target-based dispatch` | `skills/using-slides-toolkit/` | manual route test（含 `target` 解析） |
| C9 | `chore(slides-toolkit): add bats tests + CI type-lint allowlist` | `tests/` bats scripts、CI config（若 repo 有） | local `bats tests/` green |
| C10 | `docs(slides-toolkit): README + registry example + GCP screenshots` | 文件；docs-team handoff | markdown lint |
| C11 | `chore(slides-toolkit): settings.json deny rule + .gitignore` | credential hygiene | `grep` 模擬 leak 測試（見 §8） |
| C12 | *(Phase 2+ deferred)* `chore(slides-toolkit): backend interface formalization` | 當第二個 backend（html / pptx / marp）實際落地時，把 slide-plan schema 正式切為「backend-agnostic 核心 vs backend-specific extension」；可能同時 populate `scripts/common/` | trigger 見 PRODUCT-SPEC §3.5；MVP **不**實作 |

**Because** 依 MEMORY.md「feedback_commit_split_detection」規則：新
standards 觸發 mandatory 3-commit；此 spec 無新 standards（只引 code-team
既有 standards），故不需 3-commit split。Commit type 皆屬白名單
（refactor/feat/fix/chore/docs）；test + CI 用 `chore`（合規）。C12 為
**Phase 2+ deferred note**，不在 MVP commit sequence——MVP 僅 C1–C11。

### 5.2 End-to-end 測試策略

| 階段 | 測試項 | 方法 |
|---|---|---|
| Phase 1 | bootstrap dry-run | `scripts/google-slides/bootstrap.sh --dry-run --platform darwin-arm64` → 驗 SHA-256 fixture 對比通過 |
| Phase 2 | credential hygiene 驗證 | 放假 credential 進 work tree → `git status` 驗 `.gitignore` 擋；`git diff --cached` 驗 settings.json deny rule |
| Phase 3 | golden-path deck | 預先人工建一個 test template（`tests/fixtures/test_template_id.txt` 存 Drive ID）→ 跑 `slide-plan.json`（含 `target: "google-slides"` + `backend_config.template_ref`）→ 驗回傳 URL、驗 replaceAllText count、驗 image upload |
| Phase 4 | error paths | 故意給錯 `backend_config.template_ref` / 錯 image path / 過期 token / `target: "html"`（未實作 backend） → 驗 exit code 12/14/10/12 |
| Phase 5 | 429 retry | mock（用一個 401→429→200 sequence 的 local stub）驗指數退避 |
| Phase 6 | GCP Console 4 步人工驗收 | 乾淨 macOS 機器 + 新 Google 帳號跑一次首次設定（`google-slides-setup`），計時 ≤ 20 分鐘（KR2） |
| Phase 7 | `target` validation | slide-plan 缺 `target` / `target: "html"` / `target: "pptx"` / `target: "marp"` → 驗 `google-slides-builder` exit 12 + 人讀訊息指向 Phase 2+ trigger |

---

## 6. Risks & Workaround Implementation

### 6.1 gws issue #119 workaround（`[ASSUMPTION-3]`）

**Caller 釐清**：`env-guard.sh` 為共用 script，兩位 caller 走不同
subcommand（SOLID / ISP：各 caller 僅依賴自己需要的介面）：
- `google-slides-setup` → `env-guard.sh check` + `env-guard.sh apply`：
  首次設定時偵測並寫入 `~/.config/gws/env.sh` workaround 檔
- `google-slides-builder` → `env-guard.sh check`（pre-flight 唯一用途）：
  每次 builder 執行前跑一次，確認 env var 已載入且 gws auth 通過；若
  check 失敗 → exit 16，交回 `google-slides-setup` 處理，builder 不自行
  apply。

**Because** DRY（共用 script 邏輯不複製兩份）+ ISP（builder 不觸碰
mutation 路徑，避免 setup/runtime 邊界模糊）。

**偵測**：`scripts/google-slides/env-guard.sh check` 在首次 `gws auth`
前跑一次 dry-auth；若回 `invalid_scope` 或 `invalid_client`，flag 為需要
workaround。

**套用**：
1. `google-slides-setup` 引導 user 在 GCP Console 產 OAuth Client ID +
   Secret（checklist step 3）
2. 寫入 `~/.config/gws/env.sh`（chmod 600）：
   ```
   export GOOGLE_WORKSPACE_CLI_CLIENT_ID=...
   export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=...
   ```
3. `scripts/google-slides/gws-wrap.sh` 每次呼叫前 `source ~/.config/gws/env.sh`
   （若存在）
4. home-dir credential 防護靠 §8.1 `settings.json` deny rule（Read /
   Bash `cat` / `cp` / `git add` / Write 皆 deny `~/.config/gws/**`），
   **不**靠 `.gitignore`（git 不展開 `~`，home-dir 路徑無法被 .gitignore
   擋）。**Because** repo-relative vs home-dir 兩層防線責任單一化，避免
   「.gitignore 有寫就安全」的誤解（與 §8.2 note 一致）

**若 workaround 在未來 gws 版本被修掉**：`env-guard.sh` 用 feature flag
（讀 `~/.cache/slides-toolkit/bin/.version` 比對一個 known-fixed version）
自動停用。

### 6.2 Keychain silent fail fallback

**偵測**：`scripts/google-slides/credential-check.sh` 跑
`security find-generic-password` 針對 gws keychain item；若 exit 非 0 且
stderr 含 `could not be found` → 轉 file backend。

**套用**：
1. 設 `KEYRING_BACKEND=file`（export 至 `~/.config/gws/env.sh`）
2. gws 改用 `~/.config/gws/keyring-file.json`（自動生成）
3. chmod 600 該檔；`.gitignore` 擋
4. `google-slides-setup` 的 post-setup smoke test 會確認 token 可讀

### 6.3 7 天 token 過期 UX

**策略：passive 告知，非 auto-prompt**。**Because** 每週 3–5 份使用
頻率（PRODUCT-SPEC §2.1）下，user 有節奏感；強制 auto-prompt 會在
非必要時段打斷。

- `google-slides-builder` pre-flight check 跑 `credential-check.sh`
- 若 `expires_in_sec < 0` → exit 10，stderr 印：
  ```
  Your gws refresh token has expired (Google External + Testing policy:
  7-day lifetime). Please run: `gws auth` then retry.
  ```
- Claude 讀到 exit 10 → 自動呼叫 `google-slides-setup` 的 re-auth sub-protocol

### 6.4 Rate limit (429) 指數退避實作

在 `scripts/google-slides/gws-wrap.sh` 內：

```
# Pseudo-code intent (not actual code):
attempt=0
max=5
base=1
while attempt < max:
  out = gws ...
  if exit == 0: echo out; exit 0
  if http_code == 429:
    sleep $((base * 2**attempt))  # 1,2,4,8,16s
    attempt++
    continue
  break
exit 11
```

加 jitter `± 20%` 避免 thundering herd。

---

## 7. Testing & Verification

### 7.1 Shell script 單元測試（bats-core）

- 工具：`bats-core`（user 可自抓 binary；非 MVP 強制依賴，放 `tests/`）
- 覆蓋：
  - `scripts/google-slides/bootstrap.sh`：platform detection / SHA-256 verify / force flag
  - `scripts/google-slides/env-guard.sh`：issue #119 detection branches
  - `scripts/google-slides/credential-check.sh`：keychain vs file fallback branches
  - `scripts/google-slides/gws-wrap.sh`：retry count / exit code mapping / `target` pre-flight

**Because** `tdd-standard.md` 要求 security-critical code（credential
handling、binary integrity）有 failing test first。
`scripts/google-slides/bootstrap.sh` SHA-256 驗證屬 security-critical，
第一個 bats 測試即為 SHA mismatch → exit 17。

### 7.2 Golden-path 測試

- `tests/fixtures/test_template_drive_id.txt`（placeholder；真實
  Drive ID 不入 repo，由 user 於本地測試時補）
- `tests/fixtures/slide-plan.golden.json`
- `tests/golden/expected_operations.json`：預期 gws API call sequence

golden-path 測試為 integration level，需真 Google 帳號；不在 CI 跑，
只在 release 前手動 gate。

### 7.3 Dry-run 模式設計

所有 shell script 支援 `--dry-run`：

- `scripts/google-slides/bootstrap.sh --dry-run`：只 fetch + SHA check，不寫 binary
- `scripts/google-slides/gws-wrap.sh --dry-run`：不呼 gws，只印出即將執行的命令 + args
- `google-slides-builder` SKILL 支援 user 在 slide-plan.json 加
  `"dry_run": true` 頂層 flag → 只驗 schema（含 `target` + `backend_config`）
  + registry lookup + local image 存在性，不呼 Google API

**Because** dry-run 模式讓 kouko 在 token 過期日 / 離線 / debug 時
仍可驗 pipeline 邏輯；符合 `pragmatic-principles.md` 的「fail fast,
cheaply」。

### 7.4 Acceptance criteria（MVP done）

| 條件 | 驗證 |
|---|---|
| KR1 單份 ≤ 3 分鐘 | 手錶計時 10 份 deck 的平均值 ≤ 180s |
| KR2 首次設定 ≤ 20 分鐘 | 乾淨機器 + 新帳號計時 |
| 零 Python / uv / gcloud | `which python3 uv gcloud` 應不影響 skill 可用性；`unset PATH` 後只保留 `/usr/bin:/bin` 仍能跑（除了 curl + 瀏覽器） |
| Credential 不入 repo | `git log -p -- ~/.config/gws/*` 應無 match（repo 不追 home） + 模擬 `git add ~/.config/gws/auth.json` 應被 settings.json deny rule 擋 |
| 3 core recipe 各自可用 | bats + golden-path 綠 |
| `target` validation 可用 | slide-plan `target: "html"` / `"pptx"` / `"marp"` → `google-slides-builder` exit 12 + 人讀訊息含 Phase 2+ trigger 指引 |

---

## 8. Security & Credential Hygiene

### 8.1 `settings.json` deny rule（OPEN-9 解）

在 plugin 或 user 的 `.claude/settings.json` 加入：

```json
{
  "permissions": {
    "deny": [
      "Read(~/.config/gws/**)",
      "Read(~/.cache/slides-toolkit/bin/.version)",
      "Bash(cat ~/.config/gws/*)",
      "Bash(cat ~/.config/gws/**)",
      "Bash(cp ~/.config/gws/* *)",
      "Bash(git add ~/.config/gws/*)",
      "Write(~/.config/gws/**)"
    ]
  }
}
```

**Because** ASVS V14 要求 secrets-at-rest 防護；deny rule 阻止 Claude
意外讀 / 印 credential（ASVS V16 error handling 要求 logs 不含 secret）。
`Write` 也 deny 的理由：避免 Claude 誤寫覆蓋。gws 本身寫 credential 的
路徑由 shell script 外部跑，不經 Claude 工具，不受此 deny 影響。

### 8.2 `.gitignore` pattern

Plugin root `.gitignore`：

```
# credentials — never commit（皆為 repo-relative pattern）
.config/gws/
*/keyring-file.json
*/env.sh
# Note: home-dir credential files (~/.config/gws/**) cannot be
# protected by .gitignore (git uses repo-relative paths only and
# does not expand ~). Home-dir credential read access is blocked by
# the settings.json deny rule in §8.1.

# binary cache
.cache/slides-toolkit/

# runtime artifacts
tests/fixtures/*.drive_id.txt
tests/fixtures/*.local

# macOS
.DS_Store
```

**Because** `.gitignore` 採 repo-relative 比對且不展開 `~`，原先
`~/.config/gws/**` 一行實際無效（`git check-ignore` 不會吻合 home-dir
絕對路徑）；改由 §8.1 `settings.json` deny rule 阻擋 Claude 工具層
對 home-dir credential 的讀取，credential-at-rest 防護責任單一化
（ASVS V14）。上表其餘條目（`.config/gws/` / `*/keyring-file.json`
/ `*/env.sh` / `.cache/slides-toolkit/` / `tests/fixtures/*.local`
等）皆為 repo-relative，符合 `.gitignore` 語意。

### 8.3 Pre-commit hook 建議

- `gitleaks`（`gitleaks protect --staged`）— 擋 Google OAuth token
  / client secret pattern
- 可選：`trufflehog filesystem` 全 repo scan，每週跑一次

提供 `scripts/install-pre-commit.sh`（Phase 2 trigger：首次發現真實
near-miss leak）。MVP 不強制，docs 內 recommend。

### 8.4 Credential 洩漏 incident response playbook

若發現 credential 已 commit / push：

1. **立即 revoke**：GCP Console → APIs & Services → Credentials → 刪
   該 OAuth Client ID
2. **重產** Client ID + Secret（issue #119 需重跑 workaround）
3. **清 git 歷史**：`git filter-repo --path <file> --invert-paths`；
   **不** 用 `git rm --cached` 單獨（歷史仍殘）
4. **Force push**（如 repo 已 push）+ 通知所有 clone 過的協作者 rebase
5. **Keychain / file backend** 清掉舊 token：
   `security delete-generic-password -s gws-cli` + `rm ~/.config/gws/keyring-file.json`
6. **Rotate** 7 天內有用到的任何衍生資源（雖然 OAuth scope 最小，仍檢查）
7. 記 incident log 於 `plugins/slides-toolkit/incidents/YYYY-MM-DD.md`（不含 secret；`incidents/` 為 on-demand 目錄，首次觸發時建立，對齊 §2.1 無 `docs/` 的設計）

**Because** ASVS V16 要求 audit；V14 要求 rotate-on-compromise。

### 8.5 Character encoding security（本 project 的 JP 注意點）

本 project shell 環境**強制 UTF-8**：

- 所有 shell script 首行：`export LC_ALL=en_US.UTF-8`
- `slide-plan.json` 必為 UTF-8；`jq` 預設 UTF-8
- `registry.md` UTF-8

**JP 注意點**：若 user 的 template deck 含 Shift_JIS 編碼的舊資
料（極少見但可能，e.g. 從舊日本客戶拿到的 .pptx 轉進 Slides 後），
替換文字若含日文半形假名 / 「表」字，**pipeline 不做 byte-level
escape**，全部靠 gws + Google API 的 UTF-8 layer 處理。**Because**
`character-encoding-security.md` §Verification 要求「Unified
encoding across the full pipeline」；我們就是走 UTF-8-only，避免
5C 問題的唯一正確方法。

若未來出現真實 Shift_JIS 輸入需求（Phase 2 trigger），再加
`iconv -f shift-jis -t utf-8` 前置步驟 + Ch.6 verification
checklist。

### 8.6 ASVS v5.0.0 L1 mapping（本 spec 觸及；MVP = google-slides backend only）

> 以下 ASVS mapping 皆屬 **Google Slides backend** 的實作範疇。Phase 2+
> 新 backend（html / pptx / marp）各自有獨立 ASVS posture——例：
> `pptx-builder` 若本地輸出無 auth 需求，V6 / V7 不適用；`html-builder`
> 若 publish 到 GitHub Pages 會引入新的 V14（token 保管）面向——各 backend
> 在其 builder skill 文件內獨立補 ASVS mapping。


| ASVS chapter | 本 spec 對應處 |
|---|---|
| V1 Encoding & Sanitization | §4.4 scope least-privilege；§8.5 UTF-8 unification |
| V2 Validation & Business Logic | §4.1 slide-plan.json schema（jq 驗證） |
| V5 File Handling | §4.2 `slides[].images[].local_path` 解析、pre-flight 驗 file exists |
| V6 Authentication | gws 官方 OAuth；本 spec 不自實作 |
| V7 Session Management | 7-day refresh token（Google policy，§6.3） |
| V11 Cryptography | 由 Google OAuth + TLS 處理；本 spec 不自造 |
| V13 Configuration | §2.3 binary SHA-256、§8.1 deny rule |
| V14 Data Protection | §4.8 credential flow、§8.2 .gitignore |
| V16 Logging & Error Handling | §4.2 exit code 表、§6.3 不印 secret |

---

## 9. Answers to PRODUCT-SPEC §8 Open Questions

| # | Question | Answer | Because |
|---|---|---|---|
| OPEN-1 | Slide plan 格式？JSON schema 嚴謹度？ | **JSON**；flat 寬鬆 `schema v1.1`（§4.1，Platform Pivot 後加 `target` + `backend_config`）；以 `jq` 驗證必填欄位 + 型別；不引入 JSON Schema / Pydantic | YAML 會引入 yaml parser 依賴（多 runtime）；Markdown front-matter 對結構化 slides 陣列不自然；JSON 是 gws 本身溝通格式，shell + jq 是 MVP runtime minimalism 的唯一自然選擇。Phase 2 升 Pydantic 的 trigger 已定義在 PRODUCT-SPEC §3.5。**Because** 全檔其他引用（§2.1 / §3.4 / §4.1 / §11）皆已用 `v1.1`，此列曾停留在 v0.1 的 `v1` 屬 outdated 字樣，對齊避免讀者誤判 schema 版次 |
| OPEN-2 | `registry.md` 資料結構？ | **Markdown table + optional YAML front-matter**（§4.7）；欄位最小集 `ref / drive_id / schema_fingerprint / notes` | 純 markdown 人類可讀可編輯，符合個人生產力工具精神；front-matter 給 `version` / `owner` metadata 便於未來遷移；全 YAML 讓手改變痛 |
| OPEN-3 | gws 呼叫：單一 function vs 多 recipe script？ | **單一 wrapper + 多 recipe protocol**（§2.1、§4.2）。`scripts/google-slides/gws-wrap.sh` 是唯一 shell entry；`skills/google-slides-builder/protocols/recipe-*.md` 是各 recipe 的 intent spec；builder SKILL 按需 compose | 執行層統一 retry + env guard + error mapping（DRY）；recipe 層放 intent 讓知識可迭代而不動 shell（SOLID OCP） |
| OPEN-4 | state detection 實作？ | `scripts/google-slides/credential-check.sh` 三分支（§4.2）：(1) `which gws` 有無 → 未裝 / 已裝；(2) `gws auth status` → 未登入 / 已登入；(3) token `expires_in_sec` 比對 → 有效 / 過期。每種狀態回對應 JSON + exit code 供 `google-slides-setup` 分支 | State machine 顯式化；一次性線性 10 步違反 PRODUCT-SPEC §4.4 principle 5（state-aware onboarding） |
| OPEN-5 | jq binary 自抓策略？ | 從 `github.com/jqlang/jq/releases` pin `jq-1.7.1+`；下載 `SHA256SUMS` 同 release 驗 SHA-256；放 `~/.cache/slides-toolkit/bin/jq` | jqlang 是官方 fork（2023 takeover after upstream stagnation）；SHA-256 符合 ASVS V13 supply chain |
| OPEN-6 | gws binary 自抓 vs 手動裝？ | **由 `google-slides-setup` 自動抓**（§2.3）；版本 pin 於 `scripts/google-slides/bootstrap.sh`；升級需 PR 改 pin + 更新 SHA256SUMS | 「純 shell + curl + 瀏覽器」的 runtime minimalism 強制要求（PRODUCT-SPEC §4.4 principle 1）；手動裝違反 KR2（≤ 20 分鐘）；官方 release 已經是 Rust 靜態 binary，自抓成本極低 |
| OPEN-7 | Error handling：structured JSON vs stderr+exit code？ | **Hybrid**：exit code 為 machine signal（§4.2 表），stderr 為 structured JSON + 人讀訊息，stdout 保留給 success JSON | Unix convention（stdout = result, stderr = diag）；Claude 讀 stderr 做 TaskUpdate；exit code 不撞 `sysexits.h` 常見值（1/2/64–78） |
| OPEN-8 | `slides[].images[].local_path` 解析？ | 支援三種，按順序：(1) absolute path；(2) `~` 展開（`eval echo`，**only** on `slides[].images[].local_path` value，不 eval content）；(3) Claude Code working dir 相對路徑（由 `google-slides-builder` pre-flight 把 `$PWD` 拼上） | 個人使用頻繁在 `~/Desktop/` / `~/Downloads/`；絕對路徑是 safest canonical form；相對路徑便於 project-scoped 使用。不支援 URL fetch → Non-Goal（MVP 要 local only，PRODUCT-SPEC §3.2） |
| OPEN-9 | settings.json deny rule pattern？ | 見 §8.1 完整清單 | ASVS V14 要求 secrets-at-rest 防護；deny list 覆蓋 Read / Bash（cat / cp / git add）/ Write；`gws` 自己寫 credential 的路徑繞過 Claude 工具層，不受影響 |
| OPEN-10 | Template schema fingerprint？ | **MVP 採 optional sha1 fingerprint**（§4.7 `schema_fingerprint` 欄位）。builder pre-flight check 若 registry 有 fingerprint，比對 template 當前 placeholder set 的 sha1，不合 → exit 13 warning（非 fatal，user 判斷） | 「MVP 靠 kouko 人工判斷」（PRODUCT-SPEC §6.3.3 risk 表）；fingerprint 是低成本早期告警，讓人工判斷有資訊；非 fatal 避免 false positive 卡 pipeline。計算方式：`gws slides presentations get <id> \| jq '[..\|objects\|.objectId?] \| sort \| .[]' \| sha1sum` |
| OPEN-11 | slide-plan `target` field 的 MVP 最小處理？ | **三段式最小處理**：(1) JSON schema v1.1 加 `target: "google-slides"` 為必填欄位（§4.1）——router 與 builder 都依此做路由 + validation；(2) `google-slides-builder` 在 pre-flight validate `target === "google-slides"`，否則 exit 12 + stderr JSON `{"error":"unsupported_target","target":"<value>","hint":"backend <value> 尚未實作，請改用 google-slides；Phase 2+ trigger 見 PRODUCT-SPEC §3.5"}`；(3) **不**做 backend registry / dispatch table——`using-slides-toolkit` router 以簡單 if-else 判斷 `target` 字串即可；backend registry 延遲到 Phase 2+ 第二個 backend 實際落地時才 formalize（見 §5.1 C12 deferred） | **Because** 三段式處理用最小代價達成 Platform Pivot 承諾：(a) `target` 欄位存在 = contract 已為多 backend 預留位置、未來新 backend 無 schema migration 成本；(b) exit 12 + 明確 hint = user 踩到未實作 backend 時不會困惑，直接看到「該怎麼做」；(c) 不 premature 引入 dispatch table = YAGNI（PRODUCT-SPEC §6.3.2 技術選型 rationale 的「MVP 只實作一個分支、contract 先留欄位」原則）——只有一個 backend 時，registry 就是「if target == 'google-slides' then builder else exit 12」，extract 成 table 只會徒增 indirection。第二個 backend 落地時自然浮現「哪些 backend-agnostic / 哪些 per-backend」的正式切分邊界，到時才 formalize，不會在 MVP 階段做錯 |

---

## 10. Feedback to PRODUCT-SPEC（上游調整建議）

以下是在撰寫 TECH-SPEC 過程中發現的 PRODUCT-SPEC 可改善點。**本
TECH-SPEC 不自行修改 PRODUCT-SPEC**（planning-team ownership），僅
列建議。PRODUCT-SPEC v0.2（Platform Pivot）已吸收部分建議，狀態如下：

| # | 位置 | 建議 | 理由 | 狀態（2026-04-23） |
|---|---|---|---|---|
| F1 | §6.3.3 risk 表 | 補一列「SHA-256 mismatch on binary fetch」對應 mitigation「pin + verify + exit 17」 | 目前 risk 表未涵蓋 supply-chain integrity；顯式列出有助 docs-team 寫 README warning | **pending**（v0.2 未處理） |
| F2 | §3.2 Non-Goals | 明列「binary 自 build / compile from source」為 Non-Goal | 目前 implicit；顯式列更好 audit | **pending** |
| F3 | §5.3 key constraints 表 | 補「字元編碼：UTF-8 only」一列 | 目前只在 §6.3 disguise；constraint 表應明列以配合 `character-encoding-security.md` | **ABSORBED**（PRODUCT-SPEC v0.2 §5.3 已加字元編碼行） |
| F4 | §3.2 Non-Goals | 「Image URL fetch（HTTP download）」明列為 Non-Goal | 避免 TECH-SPEC 層歧義；暗示 Phase 2 trigger | **ABSORBED**（PRODUCT-SPEC v0.2 §3.2 已加 URL-input Non-Goal 列） |
| F5 | §8 OPEN | 補一個 `[OPEN]` 「tests/ 目錄的 bats 測試是否作 MVP 強制依賴？」 | 本 TECH-SPEC §7 決定為「非強制，放 tests/」；PRODUCT-SPEC 層應 echo | **pending**（PRODUCT-SPEC v0.2 新增的 OPEN-11 是 `target` field，非 bats；本條待下一輪 minor edit） |
| F6 | §6.3.1 | PRODUCT-SPEC §6.3.1 的 `docs/` 目錄在 TECH-SPEC 移除，改為 plugin root 直放 SPEC / registry；`incidents/` 為 on-demand 目錄 | DRY 與一致性原則 | **ABSORBED**（PRODUCT-SPEC v0.2 §6.3.1 已移除 `docs/`、`incidents/` 標為 on-demand、registry 放於 `skills/google-slides-builder/templates/`） |
| F7 | §6.3.4 | 顯式列 Phase 2+ backend（html / pptx / marp）的 runtime impact 欄位；現有 §6.3.4 已有但可強化 | 讓 reader 對應 TECH-SPEC §2.4 的 dep 表更直接 | **partial**（PRODUCT-SPEC v0.2 §6.3.4 已列 Phase 2+ 表；TECH-SPEC §2.4 已映照） |
| F8 | §3.5 | 「Backend interface 正式化」trigger 條列加 concrete 目標（e.g. slide-plan schema formalize `backend_config` per-backend fragment） | 現有 trigger 描述略抽象，缺具體 deliverable | **ABSORBED**（PRODUCT-SPEC v0.2 §3.5 最後列已含此描述） |

**處理建議**：F1, F2, F5 仍為 pending；建議 planning-team 以
update-product-spec protocol 做 minor edit（非重開 spec），或累積到下
次 product-spec minor version 一次併入。F3, F4, F6, F8 已由 PRODUCT-SPEC
v0.2 吸收，本 TECH-SPEC v0.2 已對齊。

---

## 11. Module Readiness Summary

| Module | Backend scope | Readiness | Notes |
|---|---|---|---|
| `using-slides-toolkit` | backend-agnostic | READY | 純路由，無外部依賴；target-based dispatch |
| `slides-design` | backend-agnostic | READY | MVP 只覆蓋 Minto + SCQA + chart-selection；Tufte / 高橋 deferred |
| `google-slides-setup` | google-slides | READY | issue #119 workaround 方案已定；Keychain fallback 已定 |
| `google-slides-builder` | google-slides | READY | 3 recipe + schema v1.1 皆定義完整；含 `target` pre-flight validation |
| `scripts/google-slides/bootstrap.sh` | google-slides | READY | SHA-256 pin 策略已定 |
| `scripts/google-slides/gws-wrap.sh` | google-slides | READY | retry + env guard + error mapping 已定 |
| `scripts/google-slides/env-guard.sh` | google-slides | READY | 偵測 + 套用兩模式已定 |
| `scripts/google-slides/credential-check.sh` | google-slides | READY | 三分支 state detection 已定 |
| `scripts/common/*` | common | DEFERRED | MVP 無跨 backend 共用；Phase 2+ 第二個 backend 落地時 populate（C12 deferred） |
| Phase 2+ `{html,pptx,marp}-builder` | per-backend | DEFERRED | Trigger-gated per PRODUCT-SPEC §3.5 |

MVP scope 所有 module 皆 READY，無 PARTIAL / BLOCKED。可直接進入
C1–C11 implementation commits。C12 為 Phase 2+ deferred 條件式 commit。

---

## Appendix — Primary Source Trace

本 TECH-SPEC 的技術決策錨定於以下 code-team standards（已讀並遵循）：

- `standards/naming-and-functions.md` — 命名（scripts 以動詞 + 名詞、
  exit code 表具意義）
- `standards/pragmatic-principles.md` — fail fast cheaply（dry-run）、
  trade-off dimensions（security explicit axis）
- `standards/solid-principles.md` — OCP（`gws-wrap.sh` single entry +
  recipe protocols 可擴展；Platform Pivot 下 builder backend 可插拔）、
  SRP（四 skill + 四 google-slides script 各司其職；backend-agnostic vs
  google-slides layer 界線清楚）
- `standards/tdd-standard.md` — security-critical code（SHA-256 /
  credential handling）先寫失敗測試
- `standards/refactoring-standard.md` — commit 粒度（C1–C11 可逆、
  可 bisect）
- `standards/app-security-standard.md` — ASVS v5.0.0 L1：V1 / V2 /
  V13 / V14 / V16 mapping（§8.6 表）
- `standards/character-encoding-security.md` — UTF-8-only pipeline
  承諾（§8.5）

本 TECH-SPEC 與 PRODUCT-SPEC §6.3 技術選型、§4.4 design principles、
§3.3 top-3 assumptions 一致；跨引用皆使用 `§X.Y` 標號。

---

**End of TECH-SPEC.md — slides-toolkit**

下一步：
1. skill-team 依 §3 每 skill 的 I/O + deps + errors 寫 4 份 SKILL.md（每份 ≤ 6k tokens）——
   `using-slides-toolkit`（router）、`slides-design`（knowledge）、
   `google-slides-setup`、`google-slides-builder`
2. code-team 依 §5.1 C2–C11 切 commit 實作（C12 為 Phase 2+ deferred）
3. docs-team 依 §2.2 architecture diagram + §4 interfaces 寫 README + GCP Console 逐步截圖；README 需寫明「MVP 僅 google-slides backend；其他 target 會報 exit 12」
4. planning-team 考慮 §10 的 F1 / F2 / F5 pending 回饋調整 PRODUCT-SPEC（F3 / F4 / F6 / F8 已在 v0.2 吸收）

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
