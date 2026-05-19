# TECH-SPEC — slides-toolkit

Technical specification for the `slides-toolkit` plugin in the
`monkey-skills` repository. Scope: module design, data flow,
interface contracts, implementation plan. Product-level direction
(goals, users, scenarios, non-goals) lives in `PRODUCT-SPEC.md`
and is referenced by `§` number.

- Spec type: TECH-SPEC (code-team ownership)
- Target plugin: `slides-toolkit`
- Upstream PRODUCT-SPEC: `./PRODUCT-SPEC.md` (v0.3 — **Scope Refinement**
  on top of v0.2 Platform Pivot)
- Written against `code-team/protocols/spec-writing.md` (5-phase
  house template: Scope → Architecture → Module → Interface → Testing)
- Compliance: OWASP ASVS v5.0.0 L1 (V1, V2, V5, V13, V14, V16);
  naming / pragmatic / SOLID / TDD / refactoring code-team standards
- Status: implementation-ready (all remaining `[OPEN]` questions from
  PRODUCT-SPEC §8 are resolved in §9 below; v0.3 已解決 / 退休 OPEN-5 /
  OPEN-6 的 SHA 面向、退休 OPEN-10)

### Revision History

| Date | Revision | Scope |
|---|---|---|
| 2026-04-?? | v0.1 — Initial MVP TECH-SPEC | Single-backend (Google Slides only); 4 skills = `using-gws-toolkit` / `slides-setup` / `slides-design` / `slides-builder` |
| 2026-04-23 | **v0.2 — Platform Pivot alignment** | 對齊 PRODUCT-SPEC v0.2。`slides-setup` → `gws-setup`；`slides-builder` → `slides-builder`（通用 router / 知識層不變）。目錄分 `scripts/common/` + `scripts/gws/`。`slide-plan.json` schema v1 → v1.1（新增 `target` + `backend_config`）。Phase 2+ backend（html / pptx / marp）保留擴充點，MVP 僅實作 `target: "google-slides"`。新增 OPEN-11 回答（§9） |
| 2026-04-23 | **v0.3 — Scope Refinement alignment** | 對齊 PRODUCT-SPEC v0.3：**移除 template-based workflow + SHA-256 binary pin 兩塊 MVP scope**。`slide-plan.json` schema v1.1 → v1.2（刪除 `backend_config.template_ref`、`layout_hint` 從自由字串改為 Google Slides API predefined layout enum）。Recipe 表重寫：由 `copy-template / replace-text / insert-image` 改為 `create-presentation / create-slides / insert-text / insert-image`（以 `presentations.create` + `batchUpdate createSlide` 指定 `predefinedLayout` 建 deck，不再 copy template deck）。`bootstrap.sh` 移除 SHA-256 pin 邏輯（exit 17 自 exit code 表移除），改用 HTTPS + `curl -f`。刪除 `skills/slides-builder/templates/registry.md` 與 `recipe-copy-template.md`。§9 OPEN-5 / OPEN-6 的 integrity 面向、OPEN-2（registry format）、OPEN-10（template schema fingerprint）均隨 scope 移除而退休。**不做** schema v1.1 → v1.2 backward compat（MVP 無既有 user）。**Because** PRODUCT-SPEC v0.3 把個人使用情境下「template 管理 overhead > 視覺品質邊際」「SHA pin 維護成本 > 邊際安全增益」兩條 trade-off 解為刪除，本 TECH-SPEC 同步移除對應模組。原兩塊範圍改為 Phase 2+ trigger-gated（PRODUCT-SPEC §3.5） |
| 2026-04-24 | **v0.3.2 — Architectural layer split** | 抽出 sibling skill `google-slides-api` 作為低層 per-op recipe reference 層；`slides-builder` 保留為高層 orchestration（讀 `slide-plan.json` v1.2、pre-flight、串接 4 recipes）。4 個 recipe 檔 `git mv` 自 `slides-builder/protocols/` 至 `google-slides-api/protocols/`；新建 `google-slides-api/SKILL.md` 與 `references/api-error-codes.md`。Router `using-gws-toolkit` 加第 4 分支（低層 API 學習 / debug → google-slides-api）。**Because** (1) SRP 架構更乾淨：per-op recipe 與 pipeline orchestration 為兩種變動維度，分離後各自獨立演進（OCP）；(2) 授權自主：新 skill 全為我們原創 MIT，不需引用 `gws-slides` Apache-2.0 SKILL 內容（`gws` binary 仍為 runtime dep，不影響 repo licensing）；(3) 為 Phase 2+ 潛在 second consumer（e.g. slide-deck-auditor, deck-diff tool）預留低耦合入口。無 scope 變動、無 API 功能變動、無 4 Big Risks 變動（非 pivot、非 scope refinement；純 refactor） |

---

## 1. Scope & Constraints

### 1.1 Delivery form

CLI-style **Claude Code skill plugin**（四 skills，依 monkey-skills
plugin convention 放在 `slides-toolkit/`）。Platform Pivot 架構
下的四 skill 分為兩層：
- **Backend-agnostic layer**（通用）：`using-gws-toolkit`（router）、
  `slides-design`（knowledge）
- **Google Slides backend layer**（MVP 唯一 backend）：
  `gws-setup`、`slides-builder`

無 GUI、無 daemon、無 web server；每次由 user 在 Claude Code 內透過
slash command / skill invocation 觸發，Claude 以 Bash tool 呼叫本地
shell script。Phase 2+ 可插拔新 backend（html / pptx / marp）屬對應
builder skill 的獨立交付物，不改動 backend-agnostic layer。

### 1.2 Goals（技術目標；PRODUCT-SPEC §3.1 KRs 對映）

| 技術目標 | 對映 KR / Principle |
|---|---|
| brief → Google Slides URL ≤ 3 分鐘（測量起點：使用者提交 brief 的時刻） | KR1 |
| 全新機器 `gws-setup` bootstrap ≤ 20 分鐘（含 GCP Console 4 步） | KR2 |
| 零 Python / uv / gcloud / brew runtime 依賴 | §4.4 Runtime minimalism |
| Credential 絕不入 repo（ASVS V14 + V13 baseline） | §4.4 Credential never in repo |
| 所有 binary 由 skill 自抓到 `~/.cache/slides-toolkit/bin/` | §4.4 Runtime minimalism |
| Shell script 皆支援 `--dry-run` 模式，可在無網路、無 credential 下跑通 pipeline | §7 Testing |

### 1.3 Non-Goals（技術層面明列拒絕，非明顯 out-of-scope）

| Non-Goal | Rejected because |
|---|---|
| 自撰 OAuth flow / 自呼 `accounts.google.com` | gws CLI 已處理；重做會違反 §4.4 Runtime minimalism 並增加 ASVS V6 attack surface |
| JSON Schema 嚴謹校驗（ajv / pydantic） | MVP 用 `jq` 寬鬆校驗即可；Phase 2 trigger 見 PRODUCT-SPEC §3.5 |
| Binary 自 build（不用官方 release） | 官方 release 為 Rust 靜態 binary，自 build 不增安全保證（仍需信任原始碼 + toolchain）卻引入跨平台 build matrix；違反 runtime minimalism。ASVS V13 supply-chain 防線 v0.3 改以 HTTPS + 版本 pin + 官方 org 信任邊界替代 SHA-256 shasum（詳見 §8.6） |
| 跨平台 Linux / Windows 支援 | MVP macOS only（PRODUCT-SPEC §5.3）；Linux 差異主要在 Keychain fallback，留 Phase 2 |
| Persistent state / local DB | MVP 無結構化持久狀態（v0.3 起 `registry.md` 亦隨 template workflow 移除）；multi-deck 歷史查詢非 MVP |
| Template-based deck generation（使用者自備 template deck + Drive copy + placeholder replaceAllText） | v0.3 PRODUCT-SPEC §3.2 已列為 Non-Goal；改用 `presentations.create` + predefined layout。Phase 2+ trigger 見 PRODUCT-SPEC §3.5 |
| Binary SHA-256 shasum verification | v0.3 PRODUCT-SPEC §3.2 已列為 Non-Goal；改用 HTTPS + `curl -f` + version pin。Phase 2+ trigger（publish / CI / supply-chain incident）見 PRODUCT-SPEC §3.5 |
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
slides-toolkit/
├── .claude-plugin/
│   └── plugin.json                # plugin manifest
├── PRODUCT-SPEC.md                # (existing; v0.3.2 Architectural split)
├── TECH-SPEC.md                   # this file (v0.3.2 Architectural split)
├── README.md                      # user-facing entry (docs-team)
├── CHANGELOG.md
├── commands/                      # optional slash-command shims
│   └── slides.md
├── scripts/                       # plugin-scoped shell helpers（依 backend 分子目錄）
│   ├── common/                    # 跨 backend 共用（MVP 暫無；預留 Phase 2+）
│   └── google-slides/             # Google Slides backend 專屬
│       ├── bootstrap.sh           # fetch gws + jq binaries (HTTPS + curl -f; v0.3 無 SHA-256 pin)
│       ├── gws-wrap.sh            # thin wrapper: token ping + retry + JSON parse
│       ├── env-guard.sh           # issue-#119 env var detection + fallback
│       └── credential-check.sh    # Keychain / file-backend state detect
├── tests/
│   ├── dry_run/                   # no-network fixtures
│   ├── golden/                    # expected output snapshots
│   └── fixtures/                  # sample slide-plan.json v1.2 (v0.3: 無 registry.md fixture)
├── incidents/                     # on-demand（平時不建立；§8.4 觸發時每起一份）
└── skills/
    ├── using-gws-toolkit/      # router（通用；依 target 選 backend skill）
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
    ├── gws-setup/       # [renamed from slides-setup]
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
    ├── google-slides-api/         # [v0.3.2] 低層 per-op recipe reference
    │   ├── SKILL.md                 # entry + op list + composition (placeholder_map) + when-to-use
    │   ├── protocols/               # (自 slides-builder 移至此 sibling skill)
    │   │   ├── recipe-create-presentation.md
    │   │   ├── recipe-create-slides.md
    │   │   ├── recipe-insert-text.md
    │   │   └── recipe-insert-image.md
    │   └── references/
    │       └── api-error-codes.md  # HTTP → exit code 對映 + 救援 playbook
    └── slides-builder/     # [renamed from slides-builder; v0.3: no templates/; v0.3.2: no protocols/]
        ├── SKILL.md                 # execution layer；slide-plan.json v1.2 consumer
        ├── checklists/
        │   └── pre-flight.md               # target + schema + layout_hint enum + token + quota + image + env
        ├── standards/
        │   └── slide-plan-schema.md        # schema v1.2（target + layout_hint enum；無 backend_config.template_ref）
        └── references/
            ├── predefined-layouts-map.md   # Google Slides API predefined layout enum 對照
            └── gws-command-map.md

# Phase 2+（trigger-gated per PRODUCT-SPEC §3.5；MVP 不建立）
# ├── scripts/{html,pptx,marp}/
# └── skills/{html,pptx,marp}-builder/
```

**Rename migration log（TECH-SPEC v0.1 → v0.2）**：

| 舊名 | 新名 |
|---|---|
| `skills/slides-setup/` | `skills/gws-setup/` |
| `skills/slides-builder/` | `skills/slides-builder/` |
| `scripts/bootstrap.sh` | `scripts/gws/bootstrap.sh` |
| `scripts/gws_wrap.sh` | `scripts/gws/gws-wrap.sh` |
| `scripts/env_guard.sh` | `scripts/gws/env-guard.sh` |
| `scripts/credential_check.sh` | `scripts/gws/credential-check.sh` |

**v0.3 removed paths**（對應 PRODUCT-SPEC v0.3 scope refinement）：

| 移除路徑 | 原因 |
|---|---|
| `skills/slides-builder/templates/registry.md` | template workflow 退場，不再維護 template Drive ID registry |
| `skills/slides-builder/protocols/recipe-copy-template.md` | 取代為 `recipe-create-presentation.md` + `recipe-create-slides.md` |
| `skills/slides-builder/protocols/recipe-replace-all-text.md` | 取代為 `recipe-insert-text.md`（直接 `insertText` 至 `createSlide` 回傳的 placeholder object ID） |
| `skills/slides-builder/references/registry-format.md` | registry 不再存在 |

`using-gws-toolkit`（通用 router）與 `slides-design`（backend-agnostic
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
- v0.3 起**無 `registry.md` / `templates/` 目錄**：MVP 改用 Google 內建
  predefined layouts（`TITLE` / `TITLE_AND_BODY` / `SECTION_HEADER` 等），
  不再維護 template Drive ID registry（PRODUCT-SPEC v0.3 §3.2）。未來 Phase
  2+ backend 若有 template / asset registry 需求，由對應 backend skill 自行
  於其內部定義（例：`pptx-builder/templates/` 放本機 pptx template），不
  污染通用層。
- `incidents/` 目錄為 **on-demand 建立**（非預設骨架一部分）：僅在
  §8.4 incident response playbook 實際觸發時才建
  `slides-toolkit/incidents/`，平時不佔目錄樹。
- `scripts/common/` 為 **預留目錄**：MVP 無跨 backend 共用 shell；Phase 2+
  第二個 backend 落地時才填入實際共用工具（見 §5.1 C12 deferred note）。

### 2.2 Architecture diagram（Platform Pivot — MVP: google-slides backend only）

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Claude Code (user session)                                             │
│  /using-gws-toolkit → router（依 slide-plan.target 路由到 backend）    │
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
        │               │                     │ slide-plan.json v1.2 (stdin)
        │               │                     │   ├ target: "google-slides"
        │               │                     │   ├ slides[].layout_hint  (predefined layout enum)
        │               │                     │   └ slides[]  (backend-agnostic)
        │               │                     ▼
        │               │   ┌────────────────────────────────────────┐
        │               │   │ scripts/gws/gws-wrap.sh      │
        │               │   │   ├ env-guard.sh check (issue #119)    │
        │               │   │   ├ credential-check.sh (keychain)     │
        │               │   │   └ retry 429 ↻                        │
        │               │   └───────────────┬────────────────────────┘
        │               │                   │
        │               ▼                   ▼
        │     ┌────────────────────────┐  ┌──────────────────────────┐
        │     │ scripts/gws/ │  │ ~/.cache/slides-toolkit/ │
        │     │   bootstrap.sh         │  │   bin/gws                │
        │     │   (HTTPS + curl -f;    │  │   bin/jq                 │
        │     │    v0.3 無 SHA pin)     │  └──────────┬───────────────┘
        │     └────────────┬───────────┘             │
        │                  ▼                         ▼
        │          ~/.cache/slides-         Google Slides / Drive API
        │          toolkit/bin/                      │
        │                                            ▼
        └─→ (read-only design knowledge; no I/O;     Google Slides URL
             對所有 backend 通用)
```

**Backend boundary**（MVP 僅 google-slides，Phase 2+ 擴充）：
- **Backend-agnostic layer**：`using-gws-toolkit`（router）、
  `slides-design`（knowledge）、`slide-plan.json` 頂層 schema（`target` +
  `slides[]`）
- **Google Slides backend layer**：`gws-setup`、
  `slides-builder`、`scripts/gws/*.sh`；v0.3 起**無**
  `registry.md`、**無** `backend_config.template_ref`（刪除於 schema v1.2）
- **Phase 2+ backend layers**（deferred；虛線框）：`{html,pptx,marp}-builder`
  + `scripts/{html,pptx,marp}/*.sh`，各自有對應 setup skill（若需要）

### 2.3 Binary distribution strategy（自抓模型；ASVS V13 supply chain）

- **Where**：`~/.cache/slides-toolkit/bin/{gws,jq}`。使用 XDG-like path
  但遵循 macOS 慣例（`~/.cache/` 而非 `~/Library/Caches/`，因為 shell
  script 跨機器相容性優先）。
- **How**：`scripts/gws/bootstrap.sh` 由 `gws-setup` 在首次執行時呼叫（Google Slides backend 專屬）。
  - `gws`（v0.3.1 起 auto-resolve latest）：URL 預設為
    `github.com/googleworkspace/cli/releases/latest/download/gws-<platform>`，
    由 GitHub 原生 302 redirect 到當前 latest release；bootstrap 額外
    呼叫 GitHub REST API（`/repos/googleworkspace/cli/releases/latest`）
    解析實際 tag 並寫入 `.version.gws_tag`（debug / audit 用）。使用者
    可 `GWS_VERSION=v0.X.Y` override 停用 auto-resolve、固守特定版
    （用於 upstream breaking change 救火）。
  - `jq`：從 `github.com/jqlang/jq/releases/download/jq-1.7.1/` 下載；
    版本 pin 於 `jq-1.7.1`（jq release 穩定，不走 latest）。
- **Integrity (v0.3 mitigation replacement)**：HTTPS 傳輸信任 + `curl -f`
  失敗即 abort（exit 1）+ URL pin 到固定 release tag + GitHub official
  org 信任邊界（`googleworkspace/cli`、`jqlang/jq`）。**不做** SHA-256
  shasum 比對（PRODUCT-SPEC v0.3 §3.2 Non-Goal；個人使用閉環下 SHA pin
  維護成本 > 邊際安全增益）。**Because** PRODUCT-SPEC v0.3 §6.3.2 將
  binary integrity 的 mitigation 從 SHA pin 改為「HTTPS + version pin +
  官方 org scope + `curl -f`」；此四項足以防禦「下載錯誤 / 網路中斷」
  等常見失效模式；唯一未防禦的是「GitHub release 本身被植入惡意 binary」
  這類低機率威脅，屬 Phase 2+ trigger（publish / CI / 安全事件；見
  PRODUCT-SPEC §3.5）才恢復 SHA pin。
- **Upgrade (v0.3.1 auto-refresh)**：bootstrap 讀 `.version.installed_at`
  計算年齡；若 > `SLIDES_TOOLKIT_BINARY_TTL_DAYS`（預設 30）且未設
  `GWS_VERSION` pin，則自動重抓 latest。Auto-refresh 失敗（網路 / 上游
  503）**保留既有 binary**、印 stderr warning、exit 0（不阻斷日常
  skill 使用）。使用者可 `--force` 隨時強制重抓。無 SHA 比對步驟。
  jq 不走 auto-refresh（JQ_VERSION pin 穩定）。

### 2.4 External dependencies

**MVP（Google Slides backend 啟用）**

| Dep | Backend scope | Version pin | License | Acquisition | Integrity (v0.3) |
|---|---|---|---|---|---|
| `gws` (googleworkspace/cli) | google-slides | `v0.X.Y`（具體版本於 C2 commit 時 pin，以 `.version` file 單鎖；當下為 TBD，release commit 會填入） | Apache-2.0 | GitHub release（靜態 Rust binary） | HTTPS + `curl -f` + URL pin + 官方 org |
| `jq` | common（MVP 僅 google-slides 用；Phase 2+ 其他 backend 也可能用） | `1.7.1+` | MIT | GitHub release | HTTPS + `curl -f` + URL pin + 官方 org |
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
下載腳本（URL + version pin），不 redistribute binary。v0.3 起不再 bundle
SHA-256 pin（改為 Phase 2+ trigger）。

**MVP No-deps 承諾**：**No** Python runtime, **no** uv, **no** gcloud,
**no** brew, **no** npm。符合 PRODUCT-SPEC §4.4 principle 1
（runtime minimalism）。

### 2.5 Cross-skill dependency graph（one-level-deep；Platform Pivot layers）

```
[Backend-agnostic layer — 通用]
using-gws-toolkit  ─┬─► slides-design          (knowledge; backend-agnostic)
                       ├─► gws-setup    (if target=google-slides, 未設定)
                       └─► slides-builder  (if target=google-slides, 已設定)
                           └─► (Phase 2+) html-builder / pptx-builder / marp-builder

slides-design         ──► (no I/O; references/ only; 對所有 backend 適用)

[Google Slides backend layer]
gws-setup   ──► scripts/gws/bootstrap.sh
                      ──► scripts/gws/credential-check.sh
                      ──► scripts/gws/env-guard.sh   (issue #119)

slides-builder ──► scripts/gws/gws-wrap.sh
                      ──► scripts/gws/env-guard.sh
                      ──► ~/.cache/slides-toolkit/bin/{gws,jq}
                      (v0.3: 無 templates/registry.md 引用)
```

符合 CLAUDE.md「Reference files 從 SKILL.md 直接引用，one level deep」。
跨 skill 不直接 import 其他 skill 的 protocol；共用邏輯全部下沉到
plugin root 的 `scripts/<backend>/` 或 `scripts/common/`，以相對路徑
`../../scripts/gws/` 引用。

**Protocol ↔ script mapping**（補強：讓 protocol 與 shell 實作的對應顯
式化，避免 reader 在 skill 目錄 / scripts 目錄來回追蹤）：

| Protocol | 呼叫 script (subcommand) |
|---|---|
| `gws-setup/protocols/first-time-setup.md` | `scripts/gws/bootstrap.sh`, `scripts/gws/credential-check.sh` |
| `gws-setup/protocols/state-detection.md` | `scripts/gws/credential-check.sh`, `scripts/gws/env-guard.sh check` |
| `gws-setup/protocols/issue-119-workaround.md` | `scripts/gws/env-guard.sh check`, `scripts/gws/env-guard.sh apply` |
| `slides-builder/protocols/plan-to-deck.md` | `scripts/gws/gws-wrap.sh`（內含 `env-guard.sh check` pre-flight + `target == "google-slides"` + `layout_hint` enum validation） |
| `slides-builder/protocols/recipe-create-presentation.md` | `scripts/gws/gws-wrap.sh slides presentations create --json '{"title": "..."}'` |
| `slides-builder/protocols/recipe-create-slides.md` | `scripts/gws/gws-wrap.sh slides presentations batchUpdate`（`createSlide` + `slideLayoutReference.predefinedLayout` enum） |
| `slides-builder/protocols/recipe-insert-text.md` | `scripts/gws/gws-wrap.sh slides presentations batchUpdate`（`insertText` 到 `createSlide` 回傳的 placeholder object ID） |
| `slides-builder/protocols/recipe-insert-image.md` | `scripts/gws/gws-wrap.sh drive files upload` + `batchUpdate`（`createImage` + 顯式 `pageElementProperties`，不用 `replaceAllShapesWithImage`） |

**Because** 讓 §2.5 dependency graph 從「靜態目錄關聯」升級為「語意
protocol→action mapping」，降低 onboarding 成本（pragmatic-principles
knowledge locality）；同時顯式標示 backend layer，為 Phase 2+ 新 backend
提供映照範本。

---

## 3. Module Design

> 每模組標示：I/O / deps / errors / edge cases / readiness。

### 3.1 `using-gws-toolkit`（router skill — backend-agnostic）

- **Role**：使用者 entry + **target backend 決策**。讀 user intent，解析
  `target` 意圖（MVP 預設 `"google-slides"`），路由到對應 backend skill：
  - 設計諮詢（no target needed）→ `slides-design`
  - `target == "google-slides"` + 未設定 → `gws-setup`
  - `target == "google-slides"` + 已設定 → `slides-builder`
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

### 3.2 `gws-setup`（onboarding skill — Google Slides backend only）

> Renamed from `slides-setup` (TECH-SPEC v0.1). 內容保持不變；命名加
> backend prefix 以對齊 Platform Pivot。

- **Role**：Google Slides backend 的首次機器設定。涵蓋：(1) bootstrap
  binary、(2) GCP Console 4 步手動（checklist 引導）、(3) `gws auth` +
  issue #119 workaround、(4) credential hygiene 驗證、(5) post-setup smoke test
- **Input**：無結構化輸入；只依賴 state detection（`scripts/gws/credential-check.sh`）
- **Output**：
  - 人讀 progress（Claude 透過 TaskUpdate 回報）
  - `~/.config/gws/` 生成 credential files
  - `~/.cache/slides-toolkit/bin/{gws,jq}` 生成
  - `.version` 標記檔
- **Deps**：
  - `scripts/gws/bootstrap.sh`
  - `scripts/gws/credential-check.sh`
  - `scripts/gws/env-guard.sh`（issue #119 偵測）
  - 外部：curl、gws binary、Google OAuth 頁面（瀏覽器）
- **Errors**：
  - `binary 下載失敗（curl -f 非 0）` → abort，exit 1（v0.3：不再有 exit 17 SHA-256 mismatch）
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

### 3.4 `slides-builder`（execution skill — Google Slides backend only）

> Renamed from `slides-builder` (TECH-SPEC v0.1). 內容保持不變；命名加
> backend prefix，並新增 `target` validation 以對齊 slide-plan schema。
> v0.3：schema 升到 v1.2（移除 `backend_config.template_ref`、`layout_hint`
> 升為 predefined layout enum）。

- **Role**：Google Slides backend 核心執行層。讀 `slide-plan.json` v1.2
  （見 §4.1 schema），validate `target == "google-slides"`（否則 exit 12）
  + 每頁 `layout_hint` 屬於 Google Slides predefined layout enum（否則 exit 15），
  再呼叫 `scripts/gws/gws-wrap.sh`，執行 4 core recipe（create
  presentation / create slides with predefined layout / insert text / insert
  local image），回傳 Drive URL。
- **Input**：
  - `slide-plan.json`（schema v1.2，見 §4.1）—— 必含 `target: "google-slides"`；
    每頁 `layout_hint` 為 Google 內建 predefined layout enum（`TITLE` /
    `TITLE_AND_BODY` / `TITLE_AND_TWO_COLUMNS` / `SECTION_HEADER` /
    `MAIN_POINT` / `BIG_NUMBER` / `BLANK`）
  - v0.3 **無** template Drive ID 查找（registry.md 不再存在）
- **Output**：
  - stdout：JSON `{"deck_url": "...", "deck_id": "...", "operations": [...]}`
  - stderr：人讀 progress（TaskUpdate 對應事件）
  - exit code：見 §4.2
- **Deps**：
  - `scripts/gws/gws-wrap.sh`
  - `scripts/gws/env-guard.sh`
  - `~/.cache/slides-toolkit/bin/{gws,jq}`
  - Google Slides / Drive API（via gws；`presentations.create` +
    `batchUpdate` `createSlide` / `insertText` / `createImage`）
- **Errors**（結構化 JSON to stderr + exit code）：
  - `target` 未設定或不等於 `"google-slides"` → exit 12，訊息內含「backend
    `<value>` 尚未實作，請改用 `google-slides`」並指向 PRODUCT-SPEC §3.5
    Phase 2+ trigger
  - token 過期 → exit 10，提示跑 `gws auth`
  - 429 rate limit → 指數退避重試，最多 5 次；全敗後 exit 11
  - `presentations.create` 或 `batchUpdate` 回 Google not-found → exit 12
  - `createSlide` 回傳的 placeholder object ID 找不到（`insertText` 時）
    → exit 13 subcode 13b（warning，非 fatal；builder 回報 user）
  - local image path 不存在 → exit 14
  - slide-plan.json schema 錯（如 `layout_hint` 不在 enum、缺 `target`） → exit 15
- **Edge cases**：
  - `slide-plan.json` 空 `slides[]` → 只 `presentations.create` 空 deck，回 URL
  - `slides[].images[].local_path` 含 `~` / 相對路徑 → 解析規則見 §9 OPEN-8
  - `createSlide` 回傳多個 placeholder object ID，而 `replacements` key 不對
    映任何 placeholder → exit 13 subcode 13b，列出可用 placeholder ID
    供 user 修正
- **Readiness**：READY

---

## 4. Interface & Data Flow

### 4.1 `slide-plan.json` schema v1.2（寬鬆 JSON，jq 驗證；Scope Refinement）

MVP 採 **flat 寬鬆 schema**；不引入 JSON Schema 工具鏈。欄位以 `jq`
verify（exit 15 on failure）。

**Schema version jump v1.1 → v1.2**（對齊 PRODUCT-SPEC v0.3 Scope
Refinement）：
- **刪除** `backend_config.template_ref`（template workflow 移除）
- **刪除** `backend_config` 整個 object（MVP google-slides backend
  不再有 per-backend config；Phase 2+ 第二個 backend 落地時再依需復活）
- `slides[].layout_hint` 從**自由字串**改為**必填 enum**（對齊 Google
  Slides API predefined layout values；見
  https://developers.google.com/slides/api/reference/rest/v1/presentations.pages/layouts ），
  允許值：`TITLE` / `TITLE_AND_BODY` / `TITLE_AND_TWO_COLUMNS` /
  `SECTION_HEADER` / `MAIN_POINT` / `BIG_NUMBER` / `BLANK`
- `target` 保持必填 `"google-slides"`（不變）

**Backward compat**：**不**做 v1.1 → v1.2 backward compat（MVP 無既有
user，直接 v1.2；若有 stale v1.1 fixture 由 C13 refactor commit 一併升版）。

```json
{
  "version": "1.2",
  "target": "google-slides",
  "output_title": "2026-W17 Weekly Report",
  "dry_run": false,
  "slides": [
    {
      "slide_index": 0,
      "layout_hint": "TITLE",
      "replacements": {
        "{{title}}": "2026-W17 Progress",
        "{{subtitle}}": "2026-04-23"
      },
      "images": []
    },
    {
      "slide_index": 1,
      "layout_hint": "SECTION_HEADER",
      "replacements": {
        "{{heading}}": "This Week"
      },
      "images": []
    },
    {
      "slide_index": 2,
      "layout_hint": "TITLE_AND_BODY",
      "replacements": {
        "{{title}}": "Shipped v1.14.0",
        "{{body}}": "- anchor autonomy\n- format unification\n- CI lint gate"
      },
      "images": [
        {
          "placeholder_id": "BODY",
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
| `version` | string | yes | `== "1.2"` | top（backend-agnostic） |
| `target` | string | yes | MVP 只允許 `"google-slides"`；其他值 → builder exit 12 | top（backend-agnostic） |
| `output_title` | string | yes | non-empty, UTF-8 | top（backend-agnostic） |
| `dry_run` | bool | no (default `false`) | if `true` → 只跑 schema + `layout_hint` enum + local image 存在性檢查，不呼 Google API（§7.3） | top（backend-agnostic） |
| `slides` | array | yes | allow empty → only `presentations.create` 空 deck | top（backend-agnostic） |
| `slides[].slide_index` | int | yes | `>= 0` | backend-agnostic |
| `slides[].layout_hint` | string | **yes** (google-slides) | **必須屬 Google Slides predefined layout enum**：`TITLE` \| `TITLE_AND_BODY` \| `TITLE_AND_TWO_COLUMNS` \| `SECTION_HEADER` \| `MAIN_POINT` \| `BIG_NUMBER` \| `BLANK`；違反 → exit 15 | google-slides |
| `slides[].replacements` | object | no | keys 建議以 `{{...}}` 包（對應 `createSlide` 回傳的 placeholder object ID，見 §4.3 recipe-insert-text） | backend-agnostic |
| `slides[].images[].placeholder_id` | string | if images present | non-empty；對應 `createSlide` 回傳的 placeholder object ID | backend-agnostic |
| `slides[].images[].local_path` | string | if images present | file exists（builder pre-flight check） | backend-agnostic |

**Backend-agnostic vs per-backend 切分原則**（v0.3 更新）：
- **Top-level + `slides[]`** 是跨 backend 通用 contract；新 backend 不
  得改此部分欄位語意
- **`backend_config` v0.3 暫時移除**：MVP google-slides backend 無 per-
  backend config；Phase 2+ 第二個 backend 落地時依需復活（trigger 見
  PRODUCT-SPEC §3.5 Backend interface 正式化）
- `layout_hint` 在 MVP（google-slides）**強制 enum** 對應 Google 內建
  predefined layout；Phase 2+ 第二個 backend 落地時，`layout_hint` 會
  升為「各 backend 自行定義 enum 集合」的 per-backend 切分

**MVP unsupported target 處理**：`slides-builder` 在 pre-flight
檢查 `target != "google-slides"` → exit 12 + 訊息「backend `<value>`
尚未實作，請改用 google-slides」。詳見 §9 OPEN-11。

**Phase 2 trigger**：
- 手寫 JSON 變痛苦（PRODUCT-SPEC §3.5）→ 升 Pydantic / JSON Schema 做
  嚴謹校驗
- 第二個 backend（html / pptx / marp）實際落地（PRODUCT-SPEC §3.5 trigger）
  → 正式化「backend-agnostic 核心 vs backend-specific extension」切分，
  復活 `backend_config` per-backend schema fragment
- Template-based workflow return（PRODUCT-SPEC §3.5）→ 復活
  `backend_config.template_ref` + `recipe-copy-template.md` + `registry.md`

### 4.2 Shell script contracts

通用約定：

- **stdin**：JSON（若有）
- **stdout**：JSON（machine-readable result）
- **stderr**：人讀 progress（Claude 讀此做 TaskUpdate）
- **exit code 表**：

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | generic error（usage / args / binary download fail [curl -f 非 0]） |
| 10 | token expired / unauthenticated |
| 11 | rate limit exhausted after retry |
| 12 | Google resource not found (deck) / unsupported `target` |
| 13 | placeholder mismatch — warning 類；2 子語意 (13a/13b) 見下表，non-fatal if caller overrides |
| 14 | local file not found (image) |
| 15 | schema validation failed（含 `layout_hint` 不在 predefined layout enum） |
| 16 | gws issue #119 / invalid_scope（需切 env var workaround） |
| 18 | Keychain unavailable and file-backend also failed |

**v0.3 removed**：~~exit 17 (SHA-256 mismatch)~~ — v0.3 起 binary 不做
SHA-256 pin 比對（PRODUCT-SPEC v0.3 §3.2 Non-Goal），下載失敗一律由
`curl -f` 轉 exit 1。

**Exit 13 sub-semantics**（stderr JSON 的 `subcode` 欄位帶值；exit code
仍為 13，方便 Claude 做 TaskUpdate 訊息分流）：

| Subcode | Meaning | 發生點 |
|---|---|---|
| 13a | `insertText` 指定的 placeholder object ID 在 `createSlide` 回傳結果中找不到 | recipe-insert-text |
| 13b | `createImage` 指定的 placeholder object ID 不存在於當前 slide | recipe-insert-image |

**v0.3 removed subcodes**：~~13c (replaceAllShapesWithImage)~~、~~13d
(template schema drift)~~ — 兩者皆依賴 template workflow，v0.3 起不再存在。

**Because** 2 種情境對 user 的修補動作不同（改 placeholder ID mapping
vs 改 image target）；subcode 讓 Claude 給出具體下一步，又不破壞 exit
code 語意穩定。

Per-script contracts：

#### `scripts/gws/bootstrap.sh`

| 項 | 內容 |
|---|---|
| Args | `--force`（可選，重新下載；預設只在 `.version` 不符時下載）；`--dry-run`（只測連線 + HEAD request 驗 URL reachable，不寫 binary，見 §7.3）；`--platform <darwin-arm64\|darwin-x86_64>`（override auto-detect，主要用於 CI / 跨機器測試） |
| Stdin | none |
| Stdout | `{"gws_version":"...","jq_version":"...","cache_dir":"..."}` |
| Errors | exit 1（`curl -f` 下載失敗 / 網路中斷 / 未知 platform）。**v0.3 removed**：~~exit 17 (SHA-256 mismatch)~~ |
| Pseudo-code intent | detect platform (或讀 `--platform`) → `curl -fL <pinned URL>` → chmod +x → write `.version`（v0.3 無 SHA-256 verify 步驟） |

#### `scripts/gws/gws-wrap.sh`

| 項 | 內容 |
|---|---|
| Args | `<subcommand>` `<args...>`（轉傳 gws）；`--dry-run`（不呼 gws，只印出即將執行的命令 + args，見 §7.3） |
| Stdin | raw JSON（若 subcommand 需要） |
| Stdout | gws 回傳的 JSON，原樣 passthrough |
| Behavior | (1) `env-guard.sh check` pre-flight（不 apply，見 §6.1）；(2) 呼叫前 `gws auth status` ping；(3) 429 指數退避 retry（1s, 2s, 4s, 8s, 16s）；(4) 解析 structured error |
| Errors | exit 10/11/12/16 |

#### `scripts/gws/env-guard.sh`

| 項 | 內容 |
|---|---|
| Args | `check` \| `apply` |
| Stdin | none |
| Stdout | `{"workaround_needed":true/false}` |
| Behavior | `check` 測一次 `gws auth` 看 `invalid_scope`；`apply` 設 `GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET` env var（由 user 在 `gws-setup` 補入 `~/.config/gws/env.sh`） |
| Errors | exit 16 |

#### `scripts/gws/credential-check.sh`

| 項 | 內容 |
|---|---|
| Args | none |
| Stdin | none |
| Stdout | `{"backend":"keychain"\|"file","token_valid":bool,"expires_in_days":int,"account_type":"personal"\|"workspace"\|"unknown"}` (v0.6.0+ added `account_type` field; v0.5.x renamed `expires_in_sec` → `expires_in_days`) |
| Behavior | 偵測 Keychain 可讀 → fallback `KEYRING_BACKEND=file`；讀 gws token 到期時間 |
| Errors | exit 18 |

### 4.3 gws CLI 呼叫模式（google-slides backend only）

> 本節 recipe 全部屬 **Google Slides backend**；`target != "google-slides"`
> 時 builder 在 pre-flight 已 exit 12，不進入本節。Phase 2+ backend 的
> recipe 集將由對應 builder skill 自行定義。

MVP 使用以下 gws 命令（對映 4 core recipe；v0.3 起全部以 create-from-
scratch 為模型，無 template copy）：

| Recipe | gws command (intent) | 失敗策略 |
|---|---|---|
| Create presentation | `gws slides presentations create --json '{"title":"<output_title>"}'` 建立空白 deck | exit 12 on unexpected not-found；429 retry |
| Create slides | `gws slides presentations batchUpdate` with `createSlide` requests；每頁帶 `slideLayoutReference.predefinedLayout: <layout_hint enum>` | exit 15 on invalid enum（應已在 pre-flight 攔到）；429 retry。回傳 response 需保留每頁的 placeholder object ID clipping，供下游 `recipe-insert-text` / `recipe-insert-image` 對位 |
| Insert text | `gws slides presentations batchUpdate` with `insertText` requests，直接針對 `createSlide` 回傳的 placeholder object ID 填字（**不**再用 `replaceAllText` + template marker） | exit 13 subcode 13a on placeholder object ID 找不到；429 retry |
| Insert local image | `gws drive files upload` → get fileId → 設 `anyoneWithLink`（透過 drive.file scope；upload 時可同步設定 permission，不需 `drive` 全權限）→ `presentations batchUpdate` with `createImage` **顯式指定 `pageElementProperties`**（pageObjectId + size + transform），**不**使用 `replaceAllShapesWithImage` | exit 14 on local missing；exit 13 subcode 13b on placeholder object ID 不存在 |

**Recipe ordering in a run**：`create-presentation` → `create-slides`（一次
batchUpdate 建立全部 slides + 解析 response 得 placeholder map）→
`insert-text`（一次 batchUpdate 填全部 text）→ `insert-image`（per-image
sequential upload + batchUpdate）。三次 batchUpdate 對應 §4.6 data flow。

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
| `https://www.googleapis.com/auth/presentations` | `presentations.create` / `batchUpdate`（createSlide / insertText / createImage） | 唯一能建立 + 改 Slides 的 scope |
| `https://www.googleapis.com/auth/drive.file` | upload image（`drive.files.upload`）+ 新建 deck 的 Drive file 中繼操作 | `drive.file` 限制為「本 app 建立 / 開啟的 file」，比 `drive` 全權限安全；符合 ASVS V1 principle of least privilege。v0.3 起 **不再用於 template copy**（template workflow 移除），僅用於圖片上傳與新建 deck 本身的 Drive 檔案權限設定 |

**不要求** `drive`（full read）、`drive.readonly`、`userinfo.email`
等非必要 scope。**Because** OWASP ASVS v5.0.0 V1 + V13 要求最小權限；
多要 scope 擴大 credential 洩漏時的 blast radius。

### 4.5 Claude Code 互動介面

- **Slash command**：`/using-gws-toolkit` → router；後續子命令
  `/gws-setup`, `/slides-design`, `/slides-builder` 由
  Claude 路由或 user 直接呼。Phase 2+ 新 backend 引入 `/html-builder`,
  `/pptx-builder`, `/marp-builder` 等；router 依 `target` 分派。
- **Skill invocation pattern**：每個 SKILL.md 遵循 monkey-skills
  convention：self-contained、≤ 6k tokens、bundled files 相對路徑。
- **TaskUpdate 使用**：
  - `gws-setup`：phase transitions（bootstrap / GCP check /
    auth / smoke test），milestones，heartbeat ≤60s
  - `slides-builder`：每個 recipe 開始 / 結束；429 retry 時發一次；
    `target` validation 失敗即刻發一次並 exit 12
  - `slides-design`：不發（純知識層）
  - 規範依 Visibility Convention（本 task 附註）

### 4.6 End-to-end data flow（slides-builder 主路徑；v0.3 rewritten）

```
Claude Code
   │  (user paste slide-plan.json v1.2; 每頁帶 layout_hint enum)
   ▼
slides-builder SKILL.md
   │  Read protocols/plan-to-deck.md
   ▼
[pre-flight] checklists/pre-flight-check.md
   │  ├─ jq: validate version == "1.2"  (else exit 15)
   │  ├─ jq: validate target == "google-slides"  (else exit 12)
   │  ├─ jq: validate each slides[].layout_hint ∈
   │  │    {TITLE, TITLE_AND_BODY, TITLE_AND_TWO_COLUMNS,
   │  │     SECTION_HEADER, MAIN_POINT, BIG_NUMBER, BLANK}
   │  │    (else exit 15)
   │  ├─ token ping  (credential-check.sh)
   │  ├─ local image files exist
   │  └─ jq schema validate slides[] (backend-agnostic 部分)
   ▼
[recipe 1] gws slides presentations create --json '{"title":"<output_title>"}'
   │  → new_deck_id (空 deck，無 slides)
   ▼
[recipe 2] gws slides presentations batchUpdate
   │    requests: [ createSlide × N with slideLayoutReference.predefinedLayout ]
   │  → response 解析每頁 placeholder object ID
   │  → placeholder_map  (slide_index → { placeholder_id → object_id })
   ▼
[recipe 3] gws slides presentations batchUpdate
   │    requests: [ insertText × M，對 placeholder_map 內每個 object_id ]
   │  (v0.3: 不用 replaceAllText；直接 insertText 到 placeholder object ID)
   │  → exit 13 subcode 13a 若有未對映的 replacement key
   ▼
[recipe 4] for each image in slides[].images[]:
   │    gws drive files upload → upload_file_id (with anyoneWithLink)
   │    gws slides presentations batchUpdate
   │      requests: [ createImage with explicit pageElementProperties ]
   │  → exit 13 subcode 13b 若 placeholder object ID 不存在
   ▼
stdout JSON:
  {"deck_url": "https://docs.google.com/presentation/d/<id>/edit",
   "deck_id": "<id>",
   "operations": [...]}
```

**Because** create-from-scratch 模型（recipe 1 → 4）以 `presentations.create`
+ `createSlide` + `insertText` + `createImage` 四個穩定 Google Slides API
操作為 backbone，避免 template copy 路徑的 placeholder drift 風險，同時
能用 Google 內建 predefined layout 覆蓋 PRODUCT-SPEC §2.4 Scenario A/B/C
多數場景（待 `[ASSUMPTION-2]` revalidation）。

### 4.7 Credential flow（ASVS V14）

> v0.3 note：原 §4.7 `registry.md` format 段落**已整段刪除**——template
> workflow 於 PRODUCT-SPEC v0.3 §3.2 列為 Non-Goal，對應 runtime artifact
> `skills/slides-builder/templates/registry.md` 同步移除。若 Phase
> 2+ trigger（§3.5 Template-based workflow return）達成，此段與
> `schema_fingerprint` 概念會一併復活。Credential flow 遞補本節編號。

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
| C1 | `docs(slides-toolkit): add TECH-SPEC v0.3 (Scope Refinement on Platform Pivot)` | 本檔案 | spec-review skill manual |
| C2 | `feat(slides-toolkit): plugin scaffold + manifest` | `.claude-plugin/plugin.json`、`README.md` stub、目錄骨架（含 `scripts/common/` + `scripts/gws/` + `skills/` 空殼） | `plugin.json` 通過 JSON parse |
| C3 | `feat(slides-toolkit): google-slides binary bootstrap (gws + jq via HTTPS + curl -f)` | `scripts/gws/bootstrap.sh`（URL + version pin；v0.3 無 SHA256SUMS fixture） | dry-run 跑 bootstrap、驗 cache dir、驗 `curl -f` 失敗路徑 |
| C4 | `feat(slides-toolkit): google-slides credential + env guard scripts` | `scripts/gws/credential-check.sh`、`scripts/gws/env-guard.sh`、`scripts/gws/gws-wrap.sh` | 無 credential 下跑 `--dry-run` 看分支 |
| C5 | `feat(slides-toolkit): gws-setup skill` | `skills/gws-setup/` 全部 | bats smoke test；manual GCP Console 4 步 walkthrough |
| C6 | `feat(slides-toolkit): slides-design skill (knowledge only; backend-agnostic)` | `skills/slides-design/` 全部 | SKILL.md token budget check（≤ 6k） |
| C7 | `feat(slides-toolkit): add slides-builder skill (create/layout/text/image recipes)` | `skills/slides-builder/` 全部：SKILL.md、`protocols/recipe-create-presentation.md` + `recipe-create-slides.md` + `recipe-insert-text.md` + `recipe-insert-image.md`、checklists/pre-flight-check.md（含 `target == "google-slides"` + `layout_hint` enum 驗證）、`standards/slide-plan-schema.md`（v1.2）、`references/predefined-layouts-map.md`、`references/gws-command-map.md`。**v0.3 note**：無 `templates/registry.md`、無 `protocols/recipe-copy-template.md`、無 `references/registry-format.md` | golden-path dry-run 測四 recipe；錯 target 驗 exit 12；錯 `layout_hint` enum 驗 exit 15 |
| C8 | `feat(slides-toolkit): using-gws-toolkit router with target-based dispatch` | `skills/using-gws-toolkit/` | manual route test（含 `target` 解析） |
| C9 | `chore(slides-toolkit): add bats tests + CI type-lint allowlist` | `tests/` bats scripts、CI config（若 repo 有） | local `bats tests/` green |
| C10 | `docs(slides-toolkit): README + predefined layout guide + GCP screenshots` | 文件；docs-team handoff。v0.3：無 registry example，改為 Google 內建 predefined layout 對照表（`TITLE` / `TITLE_AND_BODY` / ... 的視覺預覽）| markdown lint |
| C11 | `chore(slides-toolkit): settings.json deny rule + .gitignore` | credential hygiene | `grep` 模擬 leak 測試（見 §8） |
| C12 | *(Phase 2+ deferred)* `chore(slides-toolkit): backend interface formalization` | 當第二個 backend（html / pptx / marp）實際落地時，把 slide-plan schema 正式切為「backend-agnostic 核心 vs backend-specific extension」；可能同時 populate `scripts/common/` | trigger 見 PRODUCT-SPEC §3.5；MVP **不**實作 |
| C13 | `refactor(slides-toolkit): remove template workflow + SHA verification (v0.3 scope refinement)` | 對齊 PRODUCT-SPEC v0.3：**刪** `skills/slides-builder/templates/registry.md`、**刪** `skills/slides-builder/protocols/recipe-copy-template.md`、**刪** `skills/slides-builder/references/registry-format.md`；**改寫** `skills/slides-builder/protocols/recipe-replace-all-text.md` → `recipe-insert-text.md`（直接 insertText 到 `createSlide` 回傳的 placeholder object ID）；**新增** `skills/slides-builder/protocols/recipe-create-presentation.md` + `recipe-create-slides.md`；**改** `scripts/gws/bootstrap.sh`（刪 SHA-256 verify 段，改 `curl -fL`）；**改** `skills/slides-builder/checklists/pre-flight-check.md`（刪 registry lookup、刪 `schema_fingerprint` 比對、加 `layout_hint` enum 驗證）；**改** `skills/slides-builder/SKILL.md`（反映 create-from-scratch workflow 與 schema v1.2）；**改** `skills/slides-builder/standards/slide-plan-schema.md` (v1.1 → v1.2) | golden-path dry-run 重跑、驗 schema v1.2 fixture、驗 bootstrap `curl -f` 失敗分支、驗 `recipe-copy-template.md` 已不存在（`git ls-files` 斷言）|

**Because** 依 MEMORY.md「feedback_commit_split_detection」規則：新
standards 觸發 mandatory 3-commit；此 spec 無新 standards（只引 code-team
既有 standards），故不需 3-commit split。Commit type 皆屬白名單
（refactor/feat/fix/chore/docs）；test + CI 用 `chore`（合規）。C13 為
scope refinement refactor，屬 `refactor`（刪功能 + 改 workflow）。**C13
適用情境**：若 C1–C12 已按 v0.2 流程部分落地（含 `recipe-copy-template.md`
/ `registry.md` / SHA256SUMS fixture），則 C13 作為單一 refactor commit
把 repo state 拉齊到 v0.3；若 C7 起即以 v0.3 形式新建（如本 spec 呈現），
C13 仍作為 **scope-refinement 對齊 commit** 存在，內容會縮為「確認已無
v0.2 殘留 + 更新 CHANGELOG v0.3 entry」，不會變成 no-op（至少 CHANGELOG
記錄依賴 C13）。C12 為
**Phase 2+ deferred note**，不在 MVP commit sequence——MVP 僅 C1–C11。

### 5.2 End-to-end 測試策略

| 階段 | 測試項 | 方法 |
|---|---|---|
| Phase 1 | bootstrap dry-run | `scripts/gws/bootstrap.sh --dry-run --platform darwin-arm64` → 驗 `curl -I` / HEAD request reachable、驗版本 pin URL 可解析（v0.3：無 SHA-256 fixture 比對） |
| Phase 2 | credential hygiene 驗證 | 放假 credential 進 work tree → `git status` 驗 `.gitignore` 擋；`git diff --cached` 驗 settings.json deny rule |
| Phase 3 | golden-path deck（create-from-scratch） | 跑 `slide-plan.golden.json`（v1.2；涵蓋 7 種 predefined layout enum 的 representative sample）→ 驗 `presentations.create` 回傳新 deck_id、驗 `createSlide` response 含預期 placeholder object ID、驗 `insertText` / `createImage` 呼叫 sequence、驗最終 deck URL 可開啟 |
| Phase 4 | predefined layout enum validation | `slide-plan.json` 內故意放 `layout_hint: "TITLE_AND_THREE_COLUMNS"`（不存在的 layout）/ `layout_hint: "title-body"`（v1.1 風格的自由字串） → 驗 pre-flight exit 15 + stderr 指出 allowed enum set |
| Phase 5 | error paths | 故意給錯 image path / 過期 token / `target: "html"`（未實作 backend） → 驗 exit code 14/10/12 |
| Phase 6 | 429 retry | mock（用一個 401→429→200 sequence 的 local stub）驗指數退避 |
| Phase 7 | GCP Console 4 步人工驗收 | 乾淨 macOS 機器 + 新 Google 帳號跑一次首次設定（`gws-setup`），計時 ≤ 20 分鐘（KR2） |
| Phase 8 | `target` validation | slide-plan 缺 `target` / `target: "html"` / `target: "pptx"` / `target: "marp"` → 驗 `slides-builder` exit 12 + 人讀訊息指向 Phase 2+ trigger |

**v0.3 removed**：~~Template copy 測試~~（原 Phase 3 子項的 template deck
copy 驗證）— template workflow 移除。

---

## 6. Risks & Workaround Implementation

### 6.1 gws issue #119 workaround（`[ASSUMPTION-3]`）

**Caller 釐清**：`env-guard.sh` 為共用 script，兩位 caller 走不同
subcommand（SOLID / ISP：各 caller 僅依賴自己需要的介面）：
- `gws-setup` → `env-guard.sh check` + `env-guard.sh apply`：
  首次設定時偵測並寫入 `~/.config/gws/env.sh` workaround 檔
- `slides-builder` → `env-guard.sh check`（pre-flight 唯一用途）：
  每次 builder 執行前跑一次，確認 env var 已載入且 gws auth 通過；若
  check 失敗 → exit 16，交回 `gws-setup` 處理，builder 不自行
  apply。

**Because** DRY（共用 script 邏輯不複製兩份）+ ISP（builder 不觸碰
mutation 路徑，避免 setup/runtime 邊界模糊）。

**偵測**：`scripts/gws/env-guard.sh check` 在首次 `gws auth`
前跑一次 dry-auth；若回 `invalid_scope` 或 `invalid_client`，flag 為需要
workaround。

**套用**：
1. `gws-setup` 引導 user 在 GCP Console 產 OAuth Client ID +
   Secret（checklist step 3）
2. 寫入 `~/.config/gws/env.sh`（chmod 600）：
   ```
   export GOOGLE_WORKSPACE_CLI_CLIENT_ID=...
   export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET=...
   ```
3. `scripts/gws/gws-wrap.sh` 每次呼叫前 `source ~/.config/gws/env.sh`
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

**偵測**：`scripts/gws/credential-check.sh` 跑
`security find-generic-password` 針對 gws keychain item；若 exit 非 0 且
stderr 含 `could not be found` → 轉 file backend。

**套用**：
1. 設 `KEYRING_BACKEND=file`（export 至 `~/.config/gws/env.sh`）
2. gws 改用 `~/.config/gws/keyring-file.json`（自動生成）
3. chmod 600 該檔；`.gitignore` 擋
4. `gws-setup` 的 post-setup smoke test 會確認 token 可讀

### 6.3 7 天 token 過期 UX

**策略：passive 告知，非 auto-prompt**。**Because** 每週 3–5 份使用
頻率（PRODUCT-SPEC §2.1）下，user 有節奏感；強制 auto-prompt 會在
非必要時段打斷。

- `slides-builder` pre-flight check 跑 `credential-check.sh`
- 若 `expires_in_days < 0` → exit 10，stderr 印：
  ```
  Your gws refresh token has expired (Google External + Testing policy:
  7-day lifetime). Please run: `gws auth` then retry.
  ```
- Claude 讀到 exit 10 → 自動呼叫 `gws-setup` 的 re-auth sub-protocol

### 6.4 Rate limit (429) 指數退避實作

在 `scripts/gws/gws-wrap.sh` 內：

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
  - `scripts/gws/bootstrap.sh`：platform detection / `curl -f` 失敗路徑 / force flag / `.version` 比對（v0.3：無 SHA verify 測試）
  - `scripts/gws/env-guard.sh`：issue #119 detection branches
  - `scripts/gws/credential-check.sh`：keychain vs file fallback branches
  - `scripts/gws/gws-wrap.sh`：retry count / exit code mapping / `target` pre-flight / `layout_hint` enum pre-flight

**Because** `tdd-standard.md` 要求 security-critical code（credential
handling、binary integrity）有 failing test first。v0.3 起 binary integrity
防線改為 HTTPS + `curl -f`，第一個 bats 測試即為「mock 404 URL →
`curl -fL` → exit 1」確保下載失敗路徑被明確處理；credential handling
仍保留 silent-fail fallback 測試。

### 7.2 Golden-path 測試

- `tests/fixtures/test_template_drive_id.txt`（placeholder；真實
  Drive ID 不入 repo，由 user 於本地測試時補）
- `tests/fixtures/slide-plan.golden.json`
- `tests/golden/expected_operations.json`：預期 gws API call sequence

golden-path 測試為 integration level，需真 Google 帳號；不在 CI 跑，
只在 release 前手動 gate。

### 7.3 Dry-run 模式設計

所有 shell script 支援 `--dry-run`：

- `scripts/gws/bootstrap.sh --dry-run`：只測 URL reachable（HEAD
  request）+ 版本 pin URL 可解析，不寫 binary（v0.3：無 SHA check 步驟）
- `scripts/gws/gws-wrap.sh --dry-run`：不呼 gws，只印出即將執行的命令 + args
- `slides-builder` SKILL 支援 user 在 slide-plan.json 加
  `"dry_run": true` 頂層 flag → 只驗 schema（含 `target` + `layout_hint`
  enum）+ local image 存在性，不呼 Google API（v0.3：無 registry lookup
  步驟）

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
| 4 core recipe 各自可用（create presentation / create slides / insert text / insert image） | bats + golden-path 綠 |
| `target` validation 可用 | slide-plan `target: "html"` / `"pptx"` / `"marp"` → `slides-builder` exit 12 + 人讀訊息含 Phase 2+ trigger 指引 |
| All slides use valid predefined layout enum | 所有 `slides[].layout_hint` ∈ {TITLE, TITLE_AND_BODY, TITLE_AND_TWO_COLUMNS, SECTION_HEADER, MAIN_POINT, BIG_NUMBER, BLANK}；違反 → pre-flight exit 15 |

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
7. 記 incident log 於 `slides-toolkit/incidents/YYYY-MM-DD.md`（不含 secret；`incidents/` 為 on-demand 目錄，首次觸發時建立，對齊 §2.1 無 `docs/` 的設計）

**Because** ASVS V16 要求 audit；V14 要求 rotate-on-compromise。

### 8.5 Character encoding security（本 project 的 JP 注意點）

本 project shell 環境**強制 UTF-8**：

- 所有 shell script 首行：`export LC_ALL=en_US.UTF-8`
- `slide-plan.json` 必為 UTF-8；`jq` 預設 UTF-8

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
| V13 Configuration & Supply Chain | §2.3 binary integrity（v0.3：HTTPS + version pin + 官方 release scope + `curl -f`，取代 SHA-256 pin；SHA pin 恢復觸發條件見 PRODUCT-SPEC §3.5 Phase 2+ trigger：publish / CI / supply-chain incident）、§8.1 deny rule |
| V14 Data Protection | §4.7 credential flow、§8.2 .gitignore |
| V16 Logging & Error Handling | §4.2 exit code 表、§6.3 不印 secret |

---

## 9. Answers to PRODUCT-SPEC §8 Open Questions

> **v0.3 note**：編號對映 PRODUCT-SPEC §8 的 `[OPEN-1]..[OPEN-12]`；本
> spec v0.3 退休 OPEN-2 / OPEN-10（整條）與 OPEN-5 / OPEN-6 的 integrity
> 面向（保留來源 + version pin 面向）；新增 OPEN-12 答覆（bats 是否強制）。

| # | Question | Answer | Because |
|---|---|---|---|
| OPEN-1 | Slide plan 格式？JSON schema 嚴謹度？ | **JSON**；flat 寬鬆 `schema v1.2`（§4.1，Scope Refinement 後：移除 `backend_config.template_ref`、`layout_hint` 升為 Google Slides predefined layout enum）；以 `jq` 驗證必填欄位 + 型別 + enum；不引入 JSON Schema / Pydantic | YAML 會引入 yaml parser 依賴（多 runtime）；Markdown front-matter 對結構化 slides 陣列不自然；JSON 是 gws 本身溝通格式，shell + jq 是 MVP runtime minimalism 的唯一自然選擇。Phase 2 升 Pydantic 的 trigger 已定義在 PRODUCT-SPEC §3.5。v0.3 起 schema 全檔引用統一為 `v1.2`（§2.1 / §3.4 / §4.1 / §5.2 / §11）|
| OPEN-2 | ~~`registry.md` 資料結構？~~ | **v0.3 退休**：PRODUCT-SPEC v0.3 §3.2 將 template-based workflow 列為 Non-Goal，`registry.md` 不再存在。此問題在 Phase 2+ trigger「Template-based workflow return」達成時會重開 | PRODUCT-SPEC v0.3 scope refinement 判定：個人使用閉環下 template 管理 overhead > 視覺品質邊際增益 |
| OPEN-3 | gws 呼叫：單一 function vs 多 recipe script？ | **單一 wrapper + 多 recipe protocol**（§2.1、§4.2）。`scripts/gws/gws-wrap.sh` 是唯一 shell entry；`skills/slides-builder/protocols/recipe-*.md`（v0.3 起為 `create-presentation / create-slides / insert-text / insert-image` 四份）是各 recipe 的 intent spec；builder SKILL 按需 compose | 執行層統一 retry + env guard + error mapping（DRY）；recipe 層放 intent 讓知識可迭代而不動 shell（SOLID OCP） |
| OPEN-4 | state detection 實作？ | `scripts/gws/credential-check.sh` 三分支（§4.2）：(1) `which gws` 有無 → 未裝 / 已裝；(2) `gws auth status` → 未登入 / 已登入；(3) token `expires_in_days` 比對 → 有效 / 過期。每種狀態回對應 JSON + exit code 供 `gws-setup` 分支 | State machine 顯式化；一次性線性 10 步違反 PRODUCT-SPEC §4.4 principle 5（state-aware onboarding） |
| OPEN-5 | jq binary 自抓策略？（integrity 面向 v0.3 退休） | **來源 + version pin 部分保留**：從 `github.com/jqlang/jq/releases` pin `jq-1.7.1+`；放 `~/.cache/slides-toolkit/bin/jq`。**Integrity 改由 HTTPS + `curl -f` + URL pin + 官方 org 信任邊界保證**，不做 SHA-256 shasum 比對 | jqlang 是官方 fork（2023 takeover after upstream stagnation）；SHA-256 改由 Phase 2+ trigger 恢復（publish / CI / supply-chain incident；PRODUCT-SPEC v0.3 §3.5） |
| OPEN-6 | gws binary 自抓 vs 手動裝？（integrity 面向 v0.3 退休；v0.3.1 auto-refresh） | **由 `gws-setup` 自動抓**（§2.3）；URL 預設 `/releases/latest/download/`，GitHub 原生 302 redirect + 旁呼 API 解析實際 tag 寫入 `.version`；**TTL 30 天自動重抓**（env `SLIDES_TOOLKIT_BINARY_TTL_DAYS` 客製；失敗有安全網保留既有 binary）；**`GWS_VERSION=v0.X.Y` env 可 override 停用 auto-refresh**（用於 upstream breaking change 救火） | 「純 shell + curl + 瀏覽器」的 runtime minimalism（PRODUCT-SPEC §4.4 principle 1）；手動裝違反 KR2（≤ 20 分鐘）；官方 release 是 Rust 靜態 binary，自抓成本極低。v0.3.1 消掉最後一個 `GWS_VERSION` TODO；auto-refresh 讓 binary 跟上 upstream bugfix 但不強制即時（TTL + pin override 提供彈性）。Integrity 改由 HTTPS + `curl -f` 保證（同 OPEN-5） |
| OPEN-7 | Error handling：structured JSON vs stderr+exit code？ | **Hybrid**：exit code 為 machine signal（§4.2 表），stderr 為 structured JSON + 人讀訊息，stdout 保留給 success JSON | Unix convention（stdout = result, stderr = diag）；Claude 讀 stderr 做 TaskUpdate；exit code 不撞 `sysexits.h` 常見值（1/2/64–78） |
| OPEN-8 | `slides[].images[].local_path` 解析？ | 支援三種，按順序：(1) absolute path；(2) `~` 展開（`eval echo`，**only** on `slides[].images[].local_path` value，不 eval content）；(3) Claude Code working dir 相對路徑（由 `slides-builder` pre-flight 把 `$PWD` 拼上） | 個人使用頻繁在 `~/Desktop/` / `~/Downloads/`；絕對路徑是 safest canonical form；相對路徑便於 project-scoped 使用。不支援 URL fetch → Non-Goal（MVP 要 local only，PRODUCT-SPEC §3.2） |
| OPEN-9 | settings.json deny rule pattern？ | 見 §8.1 完整清單 | ASVS V14 要求 secrets-at-rest 防護；deny list 覆蓋 Read / Bash（cat / cp / git add）/ Write；`gws` 自己寫 credential 的路徑繞過 Claude 工具層，不受影響 |
| OPEN-10 | ~~Template schema fingerprint？~~ | **v0.3 退休**：對應 PRODUCT-SPEC v0.3 §8 [OPEN-10] 已劃線標記「已解決」——MVP 移除 template-based workflow，fingerprint 問題不再存在 | template workflow 退場，自然 obsolete；Phase 2+ Template-based workflow return trigger 達成時與 OPEN-2 一併重開 |
| OPEN-11 | slide-plan `target` field 的 MVP 最小處理？ | **三段式最小處理**：(1) JSON schema v1.2 加 `target: "google-slides"` 為必填欄位（§4.1）——router 與 builder 都依此做路由 + validation；(2) `slides-builder` 在 pre-flight validate `target === "google-slides"`，否則 exit 12 + stderr JSON `{"error":"unsupported_target","target":"<value>","hint":"backend <value> 尚未實作，請改用 google-slides；Phase 2+ trigger 見 PRODUCT-SPEC §3.5"}`；(3) **不**做 backend registry / dispatch table——`using-gws-toolkit` router 以簡單 if-else 判斷 `target` 字串即可；backend registry 延遲到 Phase 2+ 第二個 backend 實際落地時才 formalize（見 §5.1 C12 deferred） | **Because** 三段式處理用最小代價達成 Platform Pivot 承諾：(a) `target` 欄位存在 = contract 已為多 backend 預留位置、未來新 backend 無 schema migration 成本；(b) exit 12 + 明確 hint = user 踩到未實作 backend 時不會困惑，直接看到「該怎麼做」；(c) 不 premature 引入 dispatch table = YAGNI（PRODUCT-SPEC §6.3.2 技術選型 rationale 的「MVP 只實作一個分支、contract 先留欄位」原則）——只有一個 backend 時，registry 就是「if target == 'google-slides' then builder else exit 12」，extract 成 table 只會徒增 indirection。第二個 backend 落地時自然浮現「哪些 backend-agnostic / 哪些 per-backend」的正式切分邊界，到時才 formalize，不會在 MVP 階段做錯 |
| OPEN-12 | `tests/` bats 測試在 MVP 是否強制？ | **非強制，放 `tests/` 但不納入 MVP 硬性規格**（§7.1）。Bats 屬額外 runtime（雖可自抓 binary），多數 script 靠 `--dry-run` + 手動驗證已能覆蓋 `[ASSUMPTION-3]` 的 regression 防護。MVP acceptance criteria（§7.4）不把「bats 綠」列為必要條件；但保留 bats smoke test 給 security-critical code（`curl -f` 下載失敗路徑、credential fallback 分支）作為 optional CI gate | **Because** MVP 驗證的是 pipeline 可用性（Ries 2011 validated learning），不是完整 regression 保護；強制 bats 會把 tests 從 optional 安全網變成 MVP 硬邊界，讓 tests 不綠時無法 ship，對個人使用閉環是 over-engineering。Phase 2+ trigger（publish / 真實 regression）達成時可升為強制 |

---

## 10. Feedback to PRODUCT-SPEC（上游調整建議）

以下是在撰寫 TECH-SPEC 過程中發現的 PRODUCT-SPEC 可改善點。**本
TECH-SPEC 不自行修改 PRODUCT-SPEC**（planning-team ownership），僅
列建議。PRODUCT-SPEC v0.2（Platform Pivot）+ v0.3（Scope Refinement）
已吸收多數建議，狀態如下：

| # | 位置 | 建議 | 理由 | 狀態（2026-04-23 post-v0.3） |
|---|---|---|---|---|
| F1 | §6.3.3 risk 表 | 補一列「SHA-256 mismatch on binary fetch」對應 mitigation「pin + verify + exit 17」 | 目前 risk 表未涵蓋 supply-chain integrity；顯式列出有助 docs-team 寫 README warning | **v0.3 Resolved（by deletion）**：PRODUCT-SPEC v0.3 §3.2 將 SHA-256 shasum 列為 Non-Goal，§6.3.3 risk 表以「HTTPS + `curl -f` + URL pin + 官方 org」取代；原 F1 的 exit 17 mitigation 在 v0.3 不再適用 |
| F2 | §3.2 Non-Goals | 明列「binary 自 build / compile from source」為 Non-Goal | 目前 implicit；顯式列更好 audit | **v0.3 Resolved**：PRODUCT-SPEC v0.3 §3.2 已新增「從原始碼編譯 `gws` / `jq` binary（build-from-source）」Non-Goal 列 |
| F3 | §5.3 key constraints 表 | 補「字元編碼：UTF-8 only」一列 | 目前只在 §6.3 disguise；constraint 表應明列以配合 `character-encoding-security.md` | **ABSORBED**（PRODUCT-SPEC v0.2 §5.3 已加字元編碼行） |
| F4 | §3.2 Non-Goals | 「Image URL fetch（HTTP download）」明列為 Non-Goal | 避免 TECH-SPEC 層歧義；暗示 Phase 2 trigger | **ABSORBED**（PRODUCT-SPEC v0.2 §3.2 已加 URL-input Non-Goal 列） |
| F5 | §8 OPEN | 補一個 `[OPEN]` 「tests/ 目錄的 bats 測試是否作 MVP 強制依賴？」 | 本 TECH-SPEC §7 決定為「非強制，放 tests/」；PRODUCT-SPEC 層應 echo | **ABSORBED → OPEN-12**（PRODUCT-SPEC v0.3 已加 `[OPEN-12]`；本 spec §9 OPEN-12 已答）|
| F6 | §6.3.1 | PRODUCT-SPEC §6.3.1 的 `docs/` 目錄在 TECH-SPEC 移除，改為 plugin root 直放 SPEC / registry；`incidents/` 為 on-demand 目錄 | DRY 與一致性原則 | **ABSORBED**（PRODUCT-SPEC v0.2 §6.3.1 已移除 `docs/`、`incidents/` 標為 on-demand；v0.3 進一步移除 registry，改為 Google 內建 predefined layouts）|
| F7 | §6.3.4 | 顯式列 Phase 2+ backend（html / pptx / marp）的 runtime impact 欄位；現有 §6.3.4 已有但可強化 | 讓 reader 對應 TECH-SPEC §2.4 的 dep 表更直接 | **partial**（PRODUCT-SPEC v0.2 §6.3.4 已列 Phase 2+ 表；TECH-SPEC §2.4 已映照） |
| F8 | §3.5 | 「Backend interface 正式化」trigger 條列加 concrete 目標（e.g. slide-plan schema formalize `backend_config` per-backend fragment） | 現有 trigger 描述略抽象，缺具體 deliverable | **ABSORBED**（PRODUCT-SPEC v0.2 §3.5 最後列已含此描述） |

**處理建議**：F1 / F2 / F5 於 PRODUCT-SPEC v0.3 Scope Refinement 過程中
全部 resolved（F1 / F2 以刪除方式解；F5 升為 OPEN-12 答覆）；F3 / F4 /
F6 / F8 先前已由 PRODUCT-SPEC v0.2 吸收，v0.3 未回退。本 TECH-SPEC v0.3
已對齊所有 F1-F8。

---

## 11. Module Readiness Summary

| Module | Backend scope | Readiness | Notes |
|---|---|---|---|
| `using-gws-toolkit` | backend-agnostic | READY | 純路由，無外部依賴；target-based dispatch |
| `slides-design` | backend-agnostic | READY | MVP 只覆蓋 Minto + SCQA + chart-selection；Tufte / 高橋 deferred |
| `gws-setup` | google-slides | READY | issue #119 workaround 方案已定；Keychain fallback 已定；v0.3：bootstrap 不再做 SHA verify |
| `slides-builder` | google-slides | READY | 4 recipe（create presentation / create slides / insert text / insert image）+ schema v1.2 皆定義完整；含 `target` + `layout_hint` enum pre-flight validation |
| `scripts/gws/bootstrap.sh` | google-slides | READY | v0.3：HTTPS + `curl -f` + URL/version pin（無 SHA-256 shasum 比對）|
| `scripts/gws/gws-wrap.sh` | google-slides | READY | retry + env guard + error mapping 已定 |
| `scripts/gws/env-guard.sh` | google-slides | READY | 偵測 + 套用兩模式已定 |
| `scripts/gws/credential-check.sh` | google-slides | READY | 三分支 state detection 已定 |
| `scripts/common/*` | common | DEFERRED | MVP 無跨 backend 共用；Phase 2+ 第二個 backend 落地時 populate（C12 deferred） |
| Phase 2+ `{html,pptx,marp}-builder` | per-backend | DEFERRED | Trigger-gated per PRODUCT-SPEC §3.5 |

**v0.3 removed modules**（隨 scope refinement 一併退場；Phase 2+ template-
based workflow return trigger 達成時恢復）：

| 已移除 module | 原位置 | 取代方案（v0.3） |
|---|---|---|
| ~~`skills/slides-builder/templates/registry.md`~~ | Google Slides backend | 改用 Google 內建 predefined layouts；無需 template Drive ID registry |
| ~~`skills/slides-builder/protocols/recipe-copy-template.md`~~ | Google Slides backend | 拆為 `recipe-create-presentation.md` + `recipe-create-slides.md` |
| ~~`skills/slides-builder/protocols/recipe-replace-all-text.md`~~ | Google Slides backend | 改為 `recipe-insert-text.md`（直接 insertText 到 `createSlide` 回傳的 placeholder object ID）|
| ~~`skills/slides-builder/references/registry-format.md`~~ | Google Slides backend | registry 不再存在；相關知識改為 `references/predefined-layouts-map.md` |

MVP scope 所有現存 module 皆 READY，無 PARTIAL / BLOCKED。v0.3 總模組數
較 v0.2 少 4 個（一個 runtime artifact + 一個 recipe protocol + 一個改名
取代 recipe + 一個 reference），對應 PRODUCT-SPEC v0.3 Scope Refinement
的兩塊刪除。可直接進入 C1–C11 implementation commits（若從 v0.2 baseline
起跑，需加 C13 refactor commit；見 §5.1）。C12 為 Phase 2+ deferred 條件
式 commit。

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
- `standards/tdd-standard.md` — security-critical code（credential
  handling、binary 下載失敗路徑 `curl -f`）先寫失敗測試（v0.3：不再
  包含 SHA-256 驗證測試，隨 scope refinement 移除）
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
   `using-gws-toolkit`（router）、`slides-design`（knowledge）、
   `gws-setup`、`slides-builder`
2. code-team 依 §5.1 C2–C11 切 commit 實作（C12 為 Phase 2+ deferred；
   若從 v0.2 baseline 升級至 v0.3，加 C13 refactor commit 做 scope
   refinement 對齊）
3. docs-team 依 §2.2 architecture diagram + §4 interfaces 寫 README +
   GCP Console 逐步截圖 + Google 內建 predefined layout 對照表；README
   需寫明「MVP 僅 google-slides backend；其他 target 會報 exit 12」+
   「每頁 `layout_hint` 必須是 `TITLE` / `TITLE_AND_BODY` / ... 七個
   enum 之一」
4. planning-team：§10 F1-F8 於 v0.3 後全部 resolved / absorbed；下次
   PRODUCT-SPEC minor revision 可聚焦在 `[ASSUMPTION-2]` revalidation
   結果（predefined layout 覆蓋率）與 Phase 2+ trigger 監控

> 🔄 CHECKPOINT: This artifact is raw output. Pipeline: consult your workflow for the next gate.
