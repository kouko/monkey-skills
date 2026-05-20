# Plan: salesforce-toolkit v0.1.0 — part 1 (scaffold + MCP wiring)

**Source brief**: docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-20 round 2, 14/14 checks)
**Prerequisites**: none (this is the first plan part of the v0.1.0 branch)

Part 1 scope：plugin scaffold + cross-cutting registration（root marketplace + root README plugin table）+ MCP 動態派發 shim + TTY guard helper。Part 2 蓋 setup automation；Part 3 蓋 skills + specs + CI；Part 4 蓋 tri-language READMEs。四 part 同分支 `feat/salesforce-toolkit-v0.1.0`，順序 ship。

## Execution wave 圖

```
Wave 1:  T1 (plugin scaffold)
            ↓
Wave 2:  T2 (cross-cutting registration)
            ↓
Wave 3:  T3 (.mcp.json) ∥ T4 (sf-mcp-launcher.sh) ∥ T5 (tty-guard.sh)
```

---

## Task 1 — Plugin scaffold (`plugin.json` + `CHANGELOG.md` + `LICENSE-MIT.txt`)

- **Description**: 建立 `salesforce-toolkit/.claude-plugin/plugin.json`（含 name `salesforce-toolkit` / version `0.1.0` / description / author / homepage / repository / license MIT / keywords `["mcp", "salesforce", "read-only", "soql", "report"]`）；建立 `salesforce-toolkit/CHANGELOG.md` 初版（v0.1.0 entry）；建立 `salesforce-toolkit/LICENSE-MIT.txt`（沿用 monkey-skills MIT 風格，與 gws-toolkit/LICENSE-APACHE-2.0.txt 慣例對齊每個 plugin 自帶 license）
- **Module**: `salesforce-toolkit/.claude-plugin/`
- **Files touched**: `salesforce-toolkit/.claude-plugin/plugin.json`, `salesforce-toolkit/CHANGELOG.md`, `salesforce-toolkit/LICENSE-MIT.txt`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/.claude-plugin/plugin.json
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/.claude-plugin/plugin.json
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/LICENSE-APACHE-2.0.txt
  - /Users/kouko/GitHub/monkey-skills/LICENSE
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/.claude-plugin/plugin.json` exits non-zero
  - **GREEN**: `jq -e '.name == "salesforce-toolkit" and .version == "0.1.0" and .license == "MIT"' salesforce-toolkit/.claude-plugin/plugin.json` exit 0；`test -f salesforce-toolkit/CHANGELOG.md`；`test -f salesforce-toolkit/LICENSE-MIT.txt`；`grep -cE '^## \[0\.1\.0\]' salesforce-toolkit/CHANGELOG.md` ≥ 1 (Keep-a-Changelog convention per gws/collab sibling precedent)
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: Smallest End State `.claude-plugin/plugin.json` + `CHANGELOG.md`；plugin-level license convention（與 gws-toolkit 對齊，brief 未顯式列出 LICENSE-MIT.txt 但 monkey-skills convention 要求 per-plugin license — 採 monorepo 慣例）

---

## Task 2 — Cross-cutting registration (`marketplace.json` entry + root README plugin table row)

- **Description**: 在 root `.claude-plugin/marketplace.json` `plugins` array 末加 `{"name": "salesforce-toolkit", "source": "./salesforce-toolkit"}`；在 root `README.md` `## Plugins` table 加一行（| salesforce-toolkit | 0.1.0 | 2 | 1 | description verbatim from plugin.json |）；`description` 須 verbatim 同 plugin.json（CI `scripts/check-marketplace-description-sync.py` 強制）
- **Module**: `.claude-plugin/` (repo root)
- **Files touched**: `.claude-plugin/marketplace.json`, `README.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.claude-plugin/marketplace.json
  - /Users/kouko/GitHub/monkey-skills/README.md
  - /Users/kouko/GitHub/monkey-skills/scripts/check-marketplace-description-sync.py
- **Acceptance**:
  - **RED**: `jq -e '.plugins[] | select(.name == "salesforce-toolkit")' .claude-plugin/marketplace.json` exit non-zero（無 entry）
  - **GREEN**: `jq -e '.plugins[] | select(.name == "salesforce-toolkit" and .source == "./salesforce-toolkit")' .claude-plugin/marketplace.json` exit 0；`python3 scripts/check-marketplace-description-sync.py` exit 0（description verbatim sync 過）；`grep -c '| salesforce-toolkit' README.md` ≥ 1
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State root `.claude-plugin/marketplace.json` entry；What Becomes Obsolete row 3「monkey-skills 主 README plugin list 加 salesforce-toolkit」（brief Open Question 確認結果：root README 確有 `## Plugins` table，必須加 row）

---

## Task 3 — `.mcp.json` static config 走 shim

- **Description**: 建立 `salesforce-toolkit/.mcp.json` — stdio mode + `command: "bash"` + `args: ["${CLAUDE_PLUGIN_ROOT}/bin/sf-mcp-launcher.sh", "--orgs", "DEFAULT_TARGET_ORG", "--toolsets", "data,metadata"]`；加 bats 驗證檔結構（jq schema check）
- **Module**: `salesforce-toolkit/`
- **Files touched**: `salesforce-toolkit/.mcp.json`, `salesforce-toolkit/tests/test_mcp_config.bats`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/.claude-plugin/plugin.json
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
- **Acceptance**:
  - **RED**: `bats salesforce-toolkit/tests/test_mcp_config.bats` fail（檔案不存在）
  - **GREEN**: `jq -e '.salesforce.type == "stdio" and .salesforce.command == "bash"' salesforce-toolkit/.mcp.json` exit 0；`jq -e '.salesforce.args[0] | contains("sf-mcp-launcher.sh")' salesforce-toolkit/.mcp.json` exit 0；`jq -e '.salesforce.args | index("--toolsets") as $i | .[$i+1] == "data,metadata"' salesforce-toolkit/.mcp.json` exit 0；bats 全 pass
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State `.mcp.json`；Decision Q1 Path D shim；Decision Q2 toolsets `data,metadata`

---

## Task 4 — `bin/sf-mcp-launcher.sh` brew→npx 動態派發 + bats

- **Description**: 建立 `bin/sf-mcp-launcher.sh`（bash, set -euo pipefail）— `command -v salesforce-mcp` 有就 `exec salesforce-mcp "$@"`；否則 `command -v npx` 有就 `exec npx -y @salesforce/mcp "$@"`；都沒則 stderr 印「跑 /salesforce-toolkit:sf-setup」+ exit 127。權限 755。Bats 驗 3 個 code path（PATH 操控模擬 salesforce-mcp / npx 存在或不存在）
- **Module**: `salesforce-toolkit/bin/`
- **Files touched**: `salesforce-toolkit/bin/sf-mcp-launcher.sh`, `salesforce-toolkit/tests/test_launcher.bats`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/scripts/gws/gws-wrap.sh
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
- **Acceptance**:
  - **RED**: `bats salesforce-toolkit/tests/test_launcher.bats` fail（檔案不存在）
  - **GREEN**: 三個 bats case 全 pass：(a) `PATH=mockdir-with-salesforce-mcp` → launcher exec salesforce-mcp with args；(b) `PATH=mockdir-with-npx-only` → launcher exec `npx -y @salesforce/mcp` with args；(c) `PATH=empty-mockdir` → exit 127 + stderr 含 `sf-setup`；`shellcheck salesforce-toolkit/bin/sf-mcp-launcher.sh` exit 0
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State `bin/sf-mcp-launcher.sh`；Decision Q1 Path D 派發邏輯；Decision Q7 brew 缺席 fallback

---

## Task 5 — `scripts/common/tty-guard.sh` TTY check helper + bats

- **Description**: 建立 `scripts/common/tty-guard.sh` — 提供 shell function `require_tty()` 內含 `tty -s` 檢查；不通則 `printf '%s\n' "auto-setup.sh requires a controlling terminal" >&2; exit 10`。可被 `source` 進其他 script。Bats 驗：(a) interactive TTY 下 return 0；(b) `</dev/null` redirect 下 fail with stderr message + exit 10
- **Module**: `salesforce-toolkit/scripts/common/`
- **Files touched**: `salesforce-toolkit/scripts/common/tty-guard.sh`, `salesforce-toolkit/tests/test_tty_guard.bats`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/scripts/gws/auto-setup.sh
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/scripts/common/
- **Acceptance**:
  - **RED**: `bats salesforce-toolkit/tests/test_tty_guard.bats` fail（檔案不存在）
  - **GREEN**: bats 兩 case 全 pass；`shellcheck salesforce-toolkit/scripts/common/tty-guard.sh` exit 0；script 可被其他 script `source` 後 `require_tty` 函式可呼叫
- **Dependencies**: Task 2 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State `scripts/common/tty-guard.sh`；Current State Evidence「TTY handoff 規矩」

---

## Notes

- Wave 3 三任務（T3 / T4 / T5）`Independent: true` 且 `Files touched` 完全 disjoint（`.mcp.json` / `bin/sf-mcp-launcher.sh` / `scripts/common/tty-guard.sh` 三個獨立目錄）— 符合 `dispatching-parallel-agents` 觸發條件，SDD 可在一條 assistant message 內 3 個 Agent calls 並行 dispatch implementer。
- T1 是 scaffold 起點，T2 是 cross-cutting registration（root marketplace + root README 同 logical「toolkit 註冊」單元）；兩者 sequential 確保 T2 引用的 plugin.json description 已 final。
- 本 plan 不含 setup automation（part-2）、skills（part-3）、tri-language READMEs（part-4）。四 part 同分支 sequential commit + 最後一次 push + 單一 PR。
