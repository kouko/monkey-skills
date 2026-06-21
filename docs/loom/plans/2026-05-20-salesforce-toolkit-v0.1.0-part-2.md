# Plan: salesforce-toolkit v0.1.0 — part 2 (setup automation)

**Source brief**: docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
**Total tasks**: 5 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-20 round 2, 14/14 checks)
**Prerequisites**: part-1 merged (plugin scaffold + tty-guard.sh + launcher 已存在)

Part 2 scope：`auto-setup.sh` 6-step idempotent installer + alias inference + credential-check + refresh-auth + `/sf-setup` slash command。

## Execution wave 圖

```
Wave 1:  T1 (alias-infer.sh)
            ↓
Wave 2:  T2 (credential-check.sh)
            ↓
Wave 3:  T3 (auto-setup.sh orchestrator)
            ↓
Wave 4:  T4 (refresh-auth.sh) ∥ T5 (commands/sf-setup.md)
```

T4 + T5 並行：refresh-auth standalone 不依賴 auto-setup runtime；sf-setup.md 只 reference auto-setup.sh 的 path 與 flags（T3 已 final）。

---

## Task 1 — `scripts/sf/alias-infer.sh` 3-layer infer function library + bats

- **Description**: 建立 `scripts/sf/alias-infer.sh` — 純 shell function `infer_alias(instance_url, user_alias)` 實作 3-layer：(1) `--alias=X` 顯式 wins；(2) regex 解析 `^https?://([a-zA-Z0-9_-]+)\.(my\.salesforce\.com|lightning\.force\.com|sandbox\.my\.salesforce\.com)` subdomain，lowercase + collapse `--` → `-`；(3) `login.salesforce.com` → `prod`，`test.salesforce.com` → `sandbox`，其他 → empty。Bats 驗 8 case：explicit override / acme → acme / `acme--devsbx.sandbox.my.salesforce.com` → `acme-devsbx` / MIXED-Case → lowercase / login → prod / test → sandbox / 空 URL → prod / `https://random.example.com` → empty
- **Module**: `salesforce-toolkit/scripts/sf/`
- **Files touched**: `salesforce-toolkit/scripts/sf/alias-infer.sh`, `salesforce-toolkit/tests/test_alias_infer.bats`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
- **Acceptance**:
  - **RED**: `bats salesforce-toolkit/tests/test_alias_infer.bats` fail（檔案不存在）
  - **GREEN**: 8 bats case 全 pass；`shellcheck salesforce-toolkit/scripts/sf/alias-infer.sh` exit 0；script 可被其他 script `source` 後 `infer_alias` 函式可呼叫
- **Dependencies**: none
- **Independent**: false
- **Brief item covered**: Decision Q3 3-layer alias inference；Smallest End State `scripts/sf/alias-infer.sh`

---

## Task 2 — `scripts/sf/credential-check.sh` 現況探測 + JSON 輸出 + bats

- **Description**: 建立 `scripts/sf/credential-check.sh` — 純查不改：輸出 JSON `{"brew": "installed|missing", "sf_cli": "installed|missing", "sf_version": "<ver>|null", "salesforce_mcp": "installed|missing", "mcp_version": "<ver>|null", "node": "installed|missing", "default_org": "<alias>|null", "default_org_status": "active|expired|null"}` to stdout；exit 0 永遠（純診斷）。實作 `command -v` + `sf --version 2>/dev/null` + `sf org display`。Bats mock 各 PATH 配置驗 JSON 結構
- **Module**: `salesforce-toolkit/scripts/sf/`
- **Files touched**: `salesforce-toolkit/scripts/sf/credential-check.sh`, `salesforce-toolkit/tests/test_credential_check.bats`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/scripts/gws/credential-check.sh
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
- **Acceptance**:
  - **RED**: `bats salesforce-toolkit/tests/test_credential_check.bats` fail（檔案不存在）
  - **GREEN**: 4 bats case 全 pass：(a) 全裝齊 → JSON 各 field "installed"；(b) brew 缺 → `.brew == "missing"`；(c) sf 缺 → `.sf_cli == "missing"` 且 `.sf_version == null`；(d) JSON 永遠 valid（`jq .` parse 成功）；exit code 永遠 0；`shellcheck salesforce-toolkit/scripts/sf/credential-check.sh` exit 0
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Brief item covered**: Smallest End State `scripts/sf/credential-check.sh`；setup steps Step 6 verify 的查詢依據

---

## Task 3 — `scripts/sf/auto-setup.sh` 6-step orchestrator + dry-run bats

- **Description**: 建立 `scripts/sf/auto-setup.sh` — sources `scripts/common/tty-guard.sh` + `scripts/sf/alias-infer.sh`；解析 `$@` flags（`--dry-run` / `--alias=X` / `--no-alias` / `--no-prompt` / `--force-reauth` / `--instance-url=URL` / `--skip-mcp-brew`）；跑 6 步驟（OS+TTY guard / brew install / sf install / salesforce-mcp install / `sf org login web` + Enter-to-accept alias / verify + emit JSON）。每步 idempotent — 先 probe 現況、skip 已完成、emit 「already done」stderr line。最終 stdout 印 `{status, sf_version, mcp_version, org_alias, instance_url, oauth_expiry, elapsed_sec, dry_run}` JSON。Bats 只測 `--dry-run` mode（不跑真 brew install / OAuth）
- **Module**: `salesforce-toolkit/scripts/sf/`
- **Files touched**: `salesforce-toolkit/scripts/sf/auto-setup.sh`, `salesforce-toolkit/tests/test_auto_setup.bats`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/scripts/gws/auto-setup.sh
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/scripts/common/tty-guard.sh
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/scripts/sf/alias-infer.sh
- **Acceptance**:
  - **RED**: `bats salesforce-toolkit/tests/test_auto_setup.bats` fail（檔案不存在）
  - **GREEN**: 6 bats case 全 pass（皆 `--dry-run`）：(a) 純 `--dry-run` 印出 6-step plan；(b) `--dry-run --alias=foo` 用 foo；(c) `--dry-run --instance-url=https://acme.my.salesforce.com` 推得 `acme`；(d) explicit alias wins over instance-url infer；(e) `--no-alias` 印 alias omit；(f) 最終 stdout `jq -e '.dry_run == true'` exit 0；`shellcheck salesforce-toolkit/scripts/sf/auto-setup.sh` exit 0
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false
- **Brief item covered**: Smallest End State `scripts/sf/auto-setup.sh`；Decision Q1-Q7 在 orchestrator 體現；setup steps 6-step 完整實作

---

## Task 4 — `scripts/sf/refresh-auth.sh` standalone re-auth + bats

- **Description**: 建立 `scripts/sf/refresh-auth.sh` — sources `scripts/common/tty-guard.sh`；驗 `sf` CLI 在；接受 `--alias=X`（default 用 `sf config get target-org` 結果）；直接 `sf org login web --alias=X --set-default`；完成後 print `{"status": "ok", "alias": "X", "instance_url": "...", "expiry": "..."}` JSON。Bats 只測 dry-run / arg-parse / TTY guard 路徑（不跑真 OAuth）
- **Module**: `salesforce-toolkit/scripts/sf/`
- **Files touched**: `salesforce-toolkit/scripts/sf/refresh-auth.sh`, `salesforce-toolkit/tests/test_refresh_auth.bats`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/scripts/gws/refresh-auth.sh
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/scripts/common/tty-guard.sh
- **Acceptance**:
  - **RED**: `bats salesforce-toolkit/tests/test_refresh_auth.bats` fail（檔案不存在）
  - **GREEN**: 3 bats case 全 pass：(a) `--dry-run` 不呼叫 `sf org login`；(b) `--alias=foo` 解析正確；(c) no TTY → exit 10 with stderr message；`shellcheck salesforce-toolkit/scripts/sf/refresh-auth.sh` exit 0
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State `scripts/sf/refresh-auth.sh`；Out of Scope「`/refresh-auth` slash command」對應的 standalone script 形式

---

## Task 5 — `commands/sf-setup.md` slash command

- **Description**: 建立 `commands/sf-setup.md` — frontmatter (`name`, `description ≤200 chars` 對應 `/salesforce-toolkit:sf-setup`, `allowed-tools` whitelist `Bash(bash:*), Bash(brew:*), Bash(sf:*), Bash(curl:*), Bash(command:*)`)；body 含 `$ARGUMENTS` 接受的 flag table；Run section 為單行 `bash "${CLAUDE_PLUGIN_ROOT}/scripts/sf/auto-setup.sh" $ARGUMENTS`；含 6-step 行為表、Prerequisites（macOS / TTY required / SF org credentials）、Re-run 行為、Troubleshooting table、See also 連結到 brief 與 auto-setup.sh path
- **Module**: `salesforce-toolkit/commands/`
- **Files touched**: `salesforce-toolkit/commands/sf-setup.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/commands/gws-setup.md
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/scripts/sf/auto-setup.sh
  - /Users/kouko/GitHub/monkey-skills/docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/commands/sf-setup.md` fail
  - **GREEN**: 檔案存在；YAML frontmatter 含 `name: sf-setup` + `description` + `allowed-tools`；`grep -c 'auto-setup.sh' salesforce-toolkit/commands/sf-setup.md` ≥ 1；`grep -c '\-\-dry-run\|--alias\|--force-reauth' salesforce-toolkit/commands/sf-setup.md` ≥ 3；`grep -ci 'Troubleshooting\|prerequisites' salesforce-toolkit/commands/sf-setup.md` ≥ 1
- **Dependencies**: Task 3 completes first
- **Independent**: true
- **Brief item covered**: Smallest End State `commands/sf-setup.md`；Setup steps 描述對外 surface

---

## Notes

- Wave 4 T4 + T5 `Independent: true`，Files touched 完全 disjoint（scripts/sf/refresh-auth.sh + tests vs commands/sf-setup.md）。
- Wave 1-3 sequential 因為 auto-setup.sh source alias-infer + tty-guard，需要它們先 final；credential-check.sh 同 module 慣例排第二。
- Bats 在 CI / 本機都不跑真 brew install 與 OAuth — 全測 `--dry-run` path。真實 setup 由 user 在自己終端 dogfood 驗證（finishing-a-branch 階段）。
