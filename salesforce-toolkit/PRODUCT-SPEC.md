# PRODUCT-SPEC — salesforce-toolkit

Cross-domain product spec for the `salesforce-toolkit` plugin in the
`monkey-skills` repository. Scope: business + design + engineering
direction at the product level. Technical module design, interface
contracts, and data flow live in `TECH-SPEC.md` (code-team ownership).

- Spec type: PRODUCT-SPEC (planning-team ownership)
- Target plugin: `salesforce-toolkit` (v0.1.0, greenfield)
- Upstream brief:
  [`docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md`](../docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md)
- Status: implementation-in-progress (part-3 of 5-part plan series)

---

## Users

### Primary user — kouko (個人)

| 維度 | 描述 |
|---|---|
| 角色 | iChef 工程師；對自己工作的 Salesforce instance（`ichef.my.salesforce.com`，iChef 餐廳 POS SaaS）做 read-only 資料查詢分析 |
| 平台 | macOS (darwin-arm64 / darwin-x64) |
| 技術能力 | Python / TypeScript proficient、熟 shell、已是 Claude Code 深度使用者 |
| Salesforce 角色 | org member（非 admin），無 Connected App 自訂權限；用 `sf` CLI 內建公開 OAuth client |
| 既有條件 | Homebrew 已裝、終端機可開 browser、有 Salesforce org credentials |
| 動機 | 把「裝完一個 plugin → 跑一個 setup 指令 → 立刻在 Claude Code 內查 SF」的單線流程跑通，不再記 5 套 CLI 指令、不再手編 JSON |

### Secondary users — Phase 2+（明列，非 v0.1.0 承諾）

- 其他 Salesforce dev / business analyst macOS 使用者，把 plugin 從
  monkey-skills marketplace install 起來就能用
- 觸發條件：kouko 用 v0.1.0 跑 ≥ 5 次真實查詢並判定 plugin 值得對外公開
  之後，才進入 Phase 2+ 的外部可用化（含 Linux/Windows 支援、Hosted
  MCP path、多 org 切換 helper）

### 誰決策 / 誰付費

- v0.1.0：kouko 既是 user、也是 decision maker、也是 maintainer
- 不存在付費角色 — monkey-skills repo 採 MIT license

---

## JTBD（Job-To-Be-Done）

> Adams 2016 Intercom Job Story 模板。底層 JTBD 理論錨定 Christensen
> & Raynor (2003) *The Innovator's Solution* Ch.3。

**Primary Job Story**

> **When** 我想在 Claude Code 內以自然語言查詢自己工作的 Salesforce
> org（SOQL/SOSL 查詢、Dashboard/Report 拉取），**I want to** 從
> 「裝完一個 plugin → 跑一個 setup 指令 → 完成 browser OAuth → 立刻
> 可用」的單線流程把所有 CLI / OAuth / MCP 設定一次跑完，**so I can**
> 不需要記 5 套 CLI 指令、不需要編 JSON、不需要排查 brew formula 改
> 版（如 `salesforce-cli` cask 2026-09-01 disable）。

**Supporting Job Story（再認證面）**

> **When** OAuth token 過期、Claude Code 再也叫不動 SF MCP 時，
> **I want to** 跑一個 `refresh-auth.sh` 就重新拿到 token，**so I can**
> 不需要重跑全部 6-step setup、不需要重裝 brew bottle、不需要再次手
> 編 `.claude.json`。

---

## Scope

### Phase 1（v0.1.0，本 PR）

落地以下 11 個檔案 + 1 個 CI workflow，達成「install plugin →
`/salesforce-toolkit:sf-setup` → 自然語言問 SF」乾淨流程：

```
salesforce-toolkit/
├── .claude-plugin/plugin.json
├── .mcp.json                              # 靜態 ship + shim 派發
├── bin/sf-mcp-launcher.sh                 # brew→npx 動態 fallback
├── scripts/
│   ├── common/tty-guard.sh
│   └── sf/
│       ├── alias-infer.sh                 # 3-layer alias inference
│       ├── credential-check.sh            # 探測 sf+brew+mcp 現況，JSON 輸出
│       ├── auto-setup.sh                  # 6-step idempotent installer
│       └── refresh-auth.sh                # token 過期 standalone re-auth
├── commands/sf-setup.md                   # /salesforce-toolkit:sf-setup
├── skills/
│   ├── sf-query/SKILL.md + README.{md,ja.md,zh-TW.md}    # SOQL/SOSL
│   └── sf-report/SKILL.md + README.{md,ja.md,zh-TW.md}   # Dashboard/Report
├── README.md + README.ja.md + README.zh-TW.md            # plugin top-level
├── PRODUCT-SPEC.md + TECH-SPEC.md
├── CHANGELOG.md
└── .github/workflows/salesforce-toolkit-ci.yml  # shellcheck + bats
```

外加 root `.claude-plugin/marketplace.json` 加一筆
`{"name": "salesforce-toolkit", "source": "./salesforce-toolkit"}`。

**MCP toolsets default**：`data,metadata`（read-only data + report
查詢分析涵蓋；deploy/users/code-analyzer v0.1.0 不需）。

**Read-only by default**：v0.1.0 skill 只暴露讀路徑（SOQL/SOSL +
Dashboard/Report 拉取）；MCP `data,metadata` toolsets 雖含寫操作 tool
但 skill prompt 不教 Claude 主動呼叫，由 user 顯式要求時 Claude 才會
走「user-typed write request」路徑（非預設行為）。

**Two install paths（互為 fallback）**：

| Path | 觸發方式 | 適合 | TTY 需求 |
|---|---|---|---|
| **Claude-orchestrated（default）** | `/salesforce-toolkit:sf-setup` 在 Claude Code 對話內 | 一般 user — 不想離開 conversation | ❌ 不需 TTY；Claude 用 `AskUserQuestion` 處理互動、`Bash run_in_background` 處理 OAuth callback wait |
| **Terminal power-user** | `bash $CLAUDE_PLUGIN_ROOT/scripts/sf/auto-setup.sh` 在自己 terminal | 想 debug step-by-step / 想看 brew install y/N prompt 細節 | ✅ 需要 TTY；走 `/dev/tty` Enter-to-accept pattern |

兩條 path 收斂到同一個 end state（`sf` CLI 已 OAuth 完成 + `salesforce-mcp` 已 installed + default org alias 已設）。User 任選其一。

**Homebrew 是唯一外部一次性 step**：brew installer 內含 `sudo` 要 user macOS 密碼，不能從 Claude Code 的 Bash tool 跑（無 TTY、無 root 提權路徑）。User 必須先在自己 Terminal.app 跑一次 brew installer 一行 curl，再重啟 Claude Code 讓 brew 進 PATH。`/sf-setup` Step 1 偵測 brew 缺席會 halt 並提示這條一行指令。

### Phase 2+（deferred；明列 trigger 條件，非 v0.1.0 承諾）

| Phase 2+ 項目 | Trigger 條件 |
|---|---|
| `sf-deploy` skill（寫操作：Apex push / metadata push） | kouko 出現首次真實寫操作需求；同時 toolsets 擴到 `metadata,data,users` |
| Salesforce Hosted MCP path（HTTP + per-org URL） | iChef 開啟 Enterprise Edition+ license 且 Hosted MCP 啟用 |
| Linux / Windows 支援 | 外部用戶請求 + 有人願意 maintain 平台差異（brew 替代偵測、Keychain fallback） |
| 自訂 Connected App | 公開 OAuth client 配額不足 / 出現 client_id 衝突 |
| `/refresh-auth` slash command | user 直接跑 `bash scripts/sf/refresh-auth.sh` 痛苦到需要 namespace 化 |
| Anthropic 官方 marketplace 投稿 | v0.1.0 在外部用戶跑通 ≥ 3 次成功 setup |
| Multi-org 切換 helper | kouko 出現第二個 SF org（目前僅 iChef instance） |
| 自然語言 → SOQL schema-aware grammar validation | MCP 自家 tool 設計覆蓋不足，外部要 Claude side 補強 |

---

## Non-goals

> 依 Ubl 2020 規則：以下**是合理的候選目標**，但 v0.1.0 期間**明確拒
> 絕**，連同拒絕理由：

| Non-goal | Rejected because |
|---|---|
| Deploy / Apex push / metadata push skill（寫操作 path） | v0.1.0 read-only scope；寫操作 = 非冪等 / 不可逆風險；先驗 read pipeline 可用 |
| Salesforce Hosted MCP 路徑（HTTP + per-org URL） | 受眾與 license 不匹配 — Enterprise Edition+ 才有；kouko iChef instance 未開通 |
| Multi-org 切換 helper / wrapper | kouko 僅一個 SF org（iChef）；`sf config set target-org` 直接用足夠；多 org 切換抽象屬外部用戶需求 |
| 自然語言查詢 → SOQL 的 schema-aware grammar / validation | 依賴 MCP 自身 tool 設計（`@salesforce/mcp` 的 query tool 已內建 schema 推導）；plugin 側再做 grammar 驗證 = duplication + drift surface |
| iChef-specific 預設 alias / 預設 instance URL 寫死 | 跟 iChef 綁太死；公開 plugin 不合適；改 3-layer alias infer + Enter accept |
| 強制每次手輸 alias | 流程卡；多數 case 可從 my.salesforce.com subdomain 推得乾淨 alias |
| 自訂 Connected App（自家 client_id / client_secret） | `sf` CLI 內建公開 OAuth client 已夠用；自訂 Connected App 需 SF admin 權限（kouko 無） |
| Linux / Windows 支援 | v0.1.0 macOS only；兩平台都有 brew 替代但流程不同（apt / dnf / winget），分散驗證焦點 |
| `/refresh-auth` slash command | user 直接跑 `bash scripts/sf/refresh-auth.sh` 即可；不另設 command 避免 namespace 污染 |
| Anthropic 官方 marketplace（`claude-plugins-community`）投稿 | 先在 monkey-skills marketplace 跑通；外部投稿 = 信任邊界擴大，PHP 2+ trigger |

---

## Competitive positioning

> 三條路徑共存，v0.1.0 選 DX MCP（Path A）。理由：對個人 SF org 讀路
> 徑、無 Enterprise license、最低 setup 成本三條同時為真時是唯一明
> 顯選項。

| 路徑 | 機制 | 適用場景 | v0.1.0 立場 |
|---|---|---|---|
| **A. Salesforce DX MCP**（採用） | brew install `sf` + `salesforce-mcp`（Apache-2.0, `salesforcecli/mcp`, v0.30.9+）；stdio MCP transport；用 `sf` CLI 已有的 OAuth token | 個人 SF org 讀路徑（kouko、外部 dev / business analyst）；無 Enterprise license；最低 setup cost | **採用**。60+ MCP tools 覆蓋 orgs/metadata/data/users/code-analyzer；read-only 場景 `data,metadata` 兩 toolsets 已足 |
| **B. Salesforce Hosted MCP** | HTTP MCP transport + per-org URL；SF 自家託管 | Enterprise Edition+ license；多人協作；不想跑本機 daemon | **Phase 2+**。受眾不對（kouko iChef instance 未開通 Enterprise），license 邊界與 v0.1.0 用戶不匹配 |
| **C. Third-party community MCPs** | 例如 [`@modelcontextprotocol/server-salesforce`](https://github.com/modelcontextprotocol) 等社群 MCP | 非官方 schema 覆蓋（自定 query DSL） | **拒絕**。官方 DX MCP 已 GA + Apache-2.0；社群 MCP 缺乏官方 schema 同步保證 + supply-chain 信任邊界較弱 |

**Path A 的差異化**（vs Path B/C）：
- **License**：Apache-2.0（DX MCP）+ MIT（本 plugin） — 商用 + 個人都 OK
- **Setup cost**：< 5 min 第一次（brew + sf login web）；後續 < 1s 冷啟（brew bottle）；token expired 時 30s re-auth
- **Toolset 覆蓋**：60+ MCP tools，data/metadata/orgs/users/code-analyzer 全可選；本 v0.1.0 default 開 `data,metadata`
- **Cross-org switching**：透過 `sf` CLI 內建 alias 切換（`sf config set target-org`）

---

## Success criteria

### KR — v0.1.0 ship 後 30 天內 kouko 自評

| KR | 指標 | Target |
|---|---|---|
| KR1 | 首次 install → setup → first query 端到端時間 | < 5 min（含 brew install + OAuth browser flow） |
| KR2 | `auto-setup.sh` 重複執行（已 setup 過的狀態）是否 idempotent，且 stderr 印 `already done: <step>` | 100%（6 step 全部跳過 `brew install` / `sf login web`） |
| KR3 | MCP 預設 toolsets 為 read-only 範圍（`data,metadata`），無寫操作 tool 出現在 Claude tool list 直到 user 顯式請求 | 100% read-only by default |
| KR4 | OAuth token 過期後跑 `refresh-auth.sh` 重新拿 token | < 30s + 1 次 browser confirm |
| KR5 | brew 缺席時 `.mcp.json` 仍可載入（shim fallback 到 `npx -y @salesforce/mcp`） | 100% load 成功 |
| KR6 | v0.1.0 期間 kouko 實際做的 SF 查詢數 | ≥ 5 次（驗證「裝完即可用」） |
| KR7 | v0.1.0 期間需要重寫 skill / setup script（非 bug fix、是設計錯誤） | 0 次 |

### Quality gates（CI 守住）

- **shellcheck**：所有 `scripts/sf/*.sh` 與 `bin/sf-mcp-launcher.sh` 全 pass（POSIX-compatible warning level）
- **bats**：每個 shell script 至少有一條 happy-path + 一條 dry-run + 一條 error-path 測試
- **`marketplace.json` 與 `plugin.json` description sync**（CI script `scripts/check-marketplace-description-sync.py` 強制）
- **CI commit type whitelist**：`refactor / feat / fix / chore / docs / test`（test/CI workflow 用 `chore`，**不**用 `ci:`）

---

## Open questions

無 v0.1.0 blocking 未決事項。Brief §Open Questions 7 個 Q 全部 resolved
（見 brief Decision table Q1–Q7）。Plan-stage 微確認項：

- ⚠️ monkey-skills root README 是否需加 plugin entry — 部分 toolkit
  README 不維護總表；plan T1 grep 後決定
- ⚠️ `${CLAUDE_PLUGIN_ROOT}` 在 `.mcp.json` `args[]` 內是否真會替換
  — Claude Code MCP 文件只 verbatim 提到 `env` field 支援；plan T2
  寫測試，必要時 fallback 用 `bash -c "$CLAUDE_PLUGIN_ROOT/bin/..."`

---

## Downstream handoff

- **TECH-SPEC.md** 對應本檔，覆蓋 module design / data flow / interface
  contracts / setup flow 細節
- **Implementation plans**：[`docs/code-toolkit/plans/2026-05-20-salesforce-toolkit-v0.1.0-part-{1,2,3,4a,4b}.md`](../docs/code-toolkit/plans/)
  — 5-part plan series，原子任務 ≤ 5 min / unit
- **Brief**：[`docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md`](../docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md)
  — brainstorming brief、Decision Q1–Q7、Out of Scope、Alternatives
