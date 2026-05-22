# salesforce-toolkit v0.1.0 — Salesforce DX MCP plugin with brew-first auto-setup

Brainstorming brief produced 2026-05-20 from a 6-turn design session（research → feasibility → planning → 6-question lock）。No upstream research note — feasibility 與設計決議直接 grounded in this brief。

## Problem

Salesforce DX MCP Server（[salesforcecli/mcp](https://github.com/salesforcecli/mcp), v0.30.9+, Apache-2.0）已經 ship 為 `@salesforce/mcp` npm package 與 `salesforce-mcp` brew formula，提供 60+ MCP tools 跨 orgs/metadata/data/users/code-analyzer 等 toolsets。但**從零到能在 Claude Code 內讀自己 Salesforce org**仍要：(1) 裝 `sf` CLI（brew formula `sf`，依賴 Node 26）；(2) 裝 `salesforce-mcp`；(3) 跑 `sf org login web` 完成 OAuth；(4) 設 alias / default org；(5) 手動編輯 `~/.claude.json` 或 plugin MCP config。每一步出錯 → 上一輪 cleanup → 再來。

**JTBD**：當 kouko 想在 Claude Code 內以自然語言查詢 Salesforce org（query / report 分析），要從「裝完一個 plugin → 跑一個 setup 指令 → 完成 browser OAuth → 立刻可用」的單線流程，不需要記 5 套 CLI 指令、不需要編 JSON、不需要排查 brew formula 改版（如 `salesforce-cli` cask 2026-09-01 disable）。

## Users

- **唯一 confirmed user**：kouko 對自己工作的 Salesforce instance（`acme.my.salesforce.com`，Acme 餐廳 POS SaaS）做 read-only 資料查詢分析
- **次要 user 想像**：其他 Salesforce dev / business analyst macOS 使用者，把 plugin 從 monkey-skills marketplace install 起來就能用
- **既有條件**：macOS（darwin）、Homebrew 已裝、終端機可開 browser、有 Salesforce org credentials

## Smallest End State

Phase 1（本 PR）落地以下 11 個檔案 + 1 個 CI workflow，達成「install plugin → `/salesforce-toolkit:sf-setup` → 自然語言問 SF」的乾淨流程：

```
salesforce-toolkit/
├── .claude-plugin/plugin.json             # plugin metadata + marketplace entry sync
├── .mcp.json                              # 靜態 ship + shim 派發
├── bin/sf-mcp-launcher.sh                 # brew→npx 動態 fallback
├── scripts/
│   ├── common/tty-guard.sh                # TTY check helper
│   └── sf/
│       ├── alias-infer.sh                 # 3-layer alias inference function lib
│       ├── credential-check.sh            # 探測 sf+brew+mcp 現況，JSON 輸出
│       ├── auto-setup.sh                  # 6-step idempotent installer (orchestrator)
│       └── refresh-auth.sh                # token 過期 standalone re-auth
├── commands/sf-setup.md                   # /salesforce-toolkit:sf-setup slash command
├── skills/
│   ├── sf-query/SKILL.md + README.{md,ja.md,zh-TW.md}    # SOQL/SOSL 自然語言查詢
│   └── sf-report/SKILL.md + README.{md,ja.md,zh-TW.md}   # Dashboard/Report 拉取分析
├── README.md + README.ja.md + README.zh-TW.md            # plugin top-level tri-lang
├── PRODUCT-SPEC.md + TECH-SPEC.md
├── CHANGELOG.md
└── .github/workflows/salesforce-toolkit-ci.yml  # shellcheck + bats
```

外加 root `.claude-plugin/marketplace.json` 加一筆 `{"name": "salesforce-toolkit", "source": "./salesforce-toolkit"}`。

**不做（Phase 2+）**：寫操作 skill（sf-deploy）、Hosted MCP 路徑、sandbox/scratch 特殊 alias 邏輯、Linux/Windows 支援、自訂 Connected App、`/refresh-auth` slash command（仍可直接跑 `bash scripts/sf/refresh-auth.sh`）、Anthropic 官方 marketplace 投稿。

## Current State Evidence

- **Plugin 慣例 reference**：[`collab-toolkit/.claude-plugin/plugin.json`](../../../collab-toolkit/.claude-plugin/plugin.json) 顯示 monkey-skills 已用 `mcpServers` field（HTTP 範例），salesforce-toolkit 沿用同欄位但走 stdio + shim
- **Setup 自動化 reference**：[`gws-toolkit/commands/gws-setup.md`](../../../gws-toolkit/commands/gws-setup.md) + [`gws-toolkit/scripts/gws/auto-setup.sh`](../../../gws-toolkit/scripts/gws/auto-setup.sh) 為 brew-first idempotent installer 範本（8-step）；本 toolkit 簡化為 6-step（去掉 GCP project create + OAuth Consent screen 流程）
- **Skill 結構 convention**：[`CLAUDE.md`](../../../CLAUDE.md) §Skill Structure 明定 subfolder 單層、`<plugin>/.claude-plugin/plugin.json` 位置、`marketplace.json` 描述 verbatim sync（CI 強制 `scripts/check-marketplace-description-sync.py`）
- **Tri-language README**：memory `feedback_skill_readme_i18n_required` + PR #150 規定每個 `skills/<skill>/README.md` 必須 ship `en/ja/zh-TW`；plugin top-level README 同
- **TTY handoff 規矩**：memory `feedback_plugin_metadata_conventions` 規定「TTY-bound skill actions MUST hand off to user's terminal, never run via Bash tool」— `sf org login web` 屬 TTY-bound（開 browser + 等 callback）
- **CC plugin MCP 支援 stdio**：[code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp) verbatim — `type: stdio` + `command` + `args` + `env`（支援 `${CLAUDE_PLUGIN_ROOT}` 替換）
- **brew formula 現況**：[`brew install sf`](https://formulae.brew.sh/formula/sf)（formula，binary=`sf`，Node 26 deps）與 [`brew install salesforce-mcp`](https://formulae.brew.sh/formula/salesforce-mcp)（v0.30.9，Apache-2.0，Node 26 deps）皆 GA；舊 `--cask salesforce-cli` 2026-09-01 disable

## Decision

Phase 1 採以下 7 個操作層決議：

| # | 議題 | 決議 | 理由 |
|---|------|------|------|
| Q1 | MCP 啟動模式 | **Path D — Shim launcher** (`bin/sf-mcp-launcher.sh` brew → npx auto-fallback) | Plugin install 當下 `.mcp.json` 已有效，不依賴 setup 是否跑過；brew 有就 <1s 冷啟，沒有就 fallback npx；環境破洞時錯誤訊息明確指 setup command |
| Q2 | MCP toolsets default | `data,metadata` | Read-only data + report 查詢分析涵蓋；deploy/users/code-analyzer Phase 1 不需 |
| Q3 | Alias 策略 | 3-layer infer：(1) `--alias=` flag → (2) `https://<sub>.my.salesforce.com` subdomain 解析 → (3) well-known endpoint fallback (`login.salesforce.com` → `prod`, `test.salesforce.com` → `sandbox`) → (4) omit | 不寫死 `acme`；URL 多數 case 自動推得乾淨 alias |
| Q4 | Alias confirm UX | Enter-to-accept inferred；可輸入 override 或 `-` omit；`--no-prompt` skip 互動 | 順流但允許否決；與 `gws-setup` ENTER pattern 一致 |
| Q5 | Phase 1 skills | `sf-query`（SOQL/SOSL）+ `sf-report`（Dashboard/Report 拉取） | 讀路徑兩條清楚 affordance；sf-deploy 寫操作 Phase 2+ |
| Q6 | Sandbox/prod alias 預設名 | `prod` / `sandbox`（簡短 CLI-friendly） | 對應 `login.salesforce.com` / `test.salesforce.com` |
| Q7 | brew 缺席 fallback | shim 自動 fallback `npx -y @salesforce/mcp`；setup script 也支援 `--skip-mcp-brew` 顯式跳過 brew install salesforce-mcp | 「brew 優先但不強制」— 跨環境韌性 |

**setup steps (6, idempotent)**：
1. OS + TTY guard（macOS only + `tty -s`）
2. `command -v brew || curl install`（若用戶無 brew 才裝；prompt 確認）
3. `command -v sf || brew install sf`
4. `command -v salesforce-mcp || brew install salesforce-mcp`（除非 `--skip-mcp-brew`）
5. `sf org login web` + Enter-to-accept inferred alias
6. Verify `sf org list --json` + emit `{status, sf_version, mcp_version, org_alias, instance_url, oauth_expiry, elapsed_sec, dry_run}`

## Out of Scope

### 本 PR 不做

- 寫操作 skill（sf-deploy / Apex push / metadata push）— Phase 2
- Salesforce Hosted MCP 路徑（HTTP + per-org URL） — 受眾與 license 不匹配，Enterprise Edition+ 才有
- Linux / Windows 支援 — Phase 2+（兩平台都有 brew 替代但流程不同）
- 自訂 Connected App（用 `sf` CLI 內建公開 OAuth client）
- `/refresh-auth` slash command（user 直接 `bash scripts/sf/refresh-auth.sh` 即可；不另設 command 避免命名空間污染）
- Anthropic 官方 marketplace（`claude-plugins-community`）投稿
- 自然語言查詢 → SOQL 的 schema-aware grammar / validation（依賴 MCP 自己的 tool 設計）
- Multi-org 切換 helper（`sf config set target-org` 直接用，不另寫 wrapper）
- Acme-specific 預設 alias / 預設 instance URL 寫死

### Future triggers（記錄避免遺忘）

| 觸發條件 | 升級項目 |
|---------|---------|
| 有用戶要 deploy Apex / metadata push | Phase 2 加 `sf-deploy` skill + 擴 toolsets 到 `metadata,data,users` |
| Acme 開啟 Hosted MCP（Enterprise+ license） | 加第二條 path 走 HTTP `https://acme.my.salesforce.com/mcp/v1` |
| brew formula `salesforce-mcp` upstream 停更 | 自動 fallback npx 即可，無 panic |
| `sf` CLI 大版本 breaking change | refresh-auth 與 alias-infer 需 regression test |
| Linux 用戶請求 | Phase 2 加 apt / dnf 偵測；同 brew 邏輯 |

## Alternatives Considered

### Path 選擇

| 選項 | 機制 | 拒絕原因 |
|------|------|---------|
| **A: brew binary 寫死** `.mcp.json` 直 call `salesforce-mcp` | command="salesforce-mcp" | Plugin install 當下 brew 還沒裝 → MCP load fail → user 看到謎之錯誤；race condition |
| **B: npx 寫死** `.mcp.json` 直 call `npx -y @salesforce/mcp` | command="npx" | 冷啟動 10-30s 每次；brew 路徑 perf 紅利浪費 |
| **C: auto-setup 結束時動態寫 `.mcp.json`** | setup script 偵測後寫 | Plugin install 載入 .mcp.json 早於 setup 跑；race condition；MCP load fail |
| **D: Shim launcher（採用）** | `command="bash" args=["${CLAUDE_PLUGIN_ROOT}/bin/sf-mcp-launcher.sh", ...]` | 靜態 ship + 動態派發；brew 有 → 直跑；brew 沒 → fallback npx；都沒 → 明確錯誤訊息 |

### Alias 策略對比

| 選項 | 拒絕原因 |
|------|---------|
| 寫死 `acme` | 跟 Acme 綁太死；公開 plugin 不合適 |
| 強制每次手輸 | 流程卡 |
| 純 well-known fallback (`prod`/`sandbox`) | 沒利用到 my.salesforce.com subdomain 的天然 identity 訊號 |
| 3-layer infer + Enter accept（採用） | 多數 case 推得乾淨 alias + 保留否決權；自然語言 UX |

### Toolsets 範圍對比

| 選項 | 拒絕原因 |
|------|---------|
| Dev-core (`orgs,metadata,data,users`) | 含 user 寫操作 + org 管理，超過 Phase 1 read-only scope |
| Dev-full + code-analyzer | 同上 + Phase 1 沒 Apex use case |
| All toolsets | MCP context 肥；Claude 工具選擇不聚焦 |
| Read-only minimal (`data,metadata`)（採用） | 對應 Q2「資料與報表查詢分析」；Phase 2 隨 sf-deploy 擴 |

## What Becomes Obsolete

| 變更 | 同 PR 處理 |
|------|-----------|
| 無既有 salesforce-* 模組（greenfield plugin） | n/a |
| `.claude-plugin/marketplace.json` 加新 entry | ✅ part-1 T1 |
| monkey-skills 主 README plugin list 加 salesforce-toolkit | ⚠️ 確認是否有 plugin list 區段需更新（部分 toolkit README 不維護總表） |

## Open Questions

無未決事項。7 個 Q 全部 resolved。Plan-stage 微確認項：
- ⚠️ 確認 monkey-skills root README 是否需加 plugin entry（plan 階段 grep）
- ⚠️ 確認 `${CLAUDE_PLUGIN_ROOT}` 在 `.mcp.json` `args[]` 內是否真會替換（doc 只 verbatim 提到 env field；plan T2 寫測試 + 必要時 fallback 用 `bash -c "$CLAUDE_PLUGIN_ROOT/bin/..."` 形式）

---

**下一站**：`writing-plans` 切原子任務 → 5 個 part-plans（part-1 scaffold + MCP、part-2 setup automation、part-3 skill SKILLs + specs + CI、part-4a en authoritative READMEs、part-4b ja+zh-TW translation pairs）。每 part ≤5 atomic tasks 以符合 plan ceiling；翻譯 pair 自然 unit 每 task 2 檔。
