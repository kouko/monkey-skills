# Setup State Checklist — google-slides-setup

> 跑完 setup 或回頭排查問題時，按順序跑以下 6 項 state check。**任一
> 項失敗即找對應 walkthrough 步驟修復，不要跳過。**

## 使用方法

依 1 → 6 順序跑；每項給你：

- **Check 命令**（可直接 copy-paste）
- **預期 output**（含成功判準）
- **失敗分支**（指向 `protocols/gcp-console-walkthrough.md` 對應步驟）

若要自動化，可把全部整合到 `scripts/google-slides/credential-check.sh`
的延伸版；本 checklist 走人工驗證版本，便於首次 setup + debug。

---

## 1. gws binary 是否已抓？

**Why**：`~/.cache/slides-toolkit/bin/gws` 是所有 Google Slides backend
操作的執行點。沒它就沒戲。

**Check**：

```bash
ls ~/.cache/slides-toolkit/bin/gws
```

**預期 output**：

```
/Users/<you>/.cache/slides-toolkit/bin/gws
```

並能跑：

```bash
~/.cache/slides-toolkit/bin/gws --version
# 預期：gws vX.Y.Z（版本號取決於 bootstrap.sh pin；TODO：填當前 pin 版本）
```

**失敗分支**：

- 檔案不存在 → `gcp-console-walkthrough.md` §7（跑 `bootstrap.sh`）
- 存在但不可執行（`Permission denied`）→ `chmod +x ~/.cache/slides-toolkit/bin/gws`，
  或重跑 `bash scripts/google-slides/bootstrap.sh --force`
- `--version` 報 SHA mismatch 類錯 → 重跑 bootstrap，若持續 exit 17 見
  SKILL.md [Error messages guide](../SKILL.md#error-messages-guide)

---

## 2. jq binary 是否已抓？

**Why**：issue #119 workaround 的 env var 設定靠 `jq` 從
`client_secret.json` 解欄位；builder pipeline 也靠 `jq` 驗 slide-plan
schema。

**Check**：

```bash
ls ~/.cache/slides-toolkit/bin/jq
~/.cache/slides-toolkit/bin/jq --version
# 預期：jq-1.7.1 或更新
```

**失敗分支**：

- 檔案不存在 → `gcp-console-walkthrough.md` §7（`bootstrap.sh` 會同時
  抓 gws + jq，通常兩個一起成功 / 一起失敗）
- 存在但版本 < 1.7.1 → `bash scripts/google-slides/bootstrap.sh --force`
- 版本正確但跑時 `command not found` → PATH 未包含
  `~/.cache/slides-toolkit/bin`；選一種：
  1. 臨時：`export PATH="$HOME/.cache/slides-toolkit/bin:$PATH"`
  2. 永久：加入 `~/.zshrc`
  3. 指令級：直接用絕對路徑 `~/.cache/slides-toolkit/bin/jq`

---

## 3. gcloud 是否已裝？（optional）

**Why**：**MVP 不依賴 gcloud**（runtime minimalism，PRODUCT-SPEC §4.4
principle 1）。本項列為 optional check —— **有 gcloud 可以加速某些
GCP Console 操作（例：切 project、看 quota）**，沒有也完全不影響本
skill 運作。

**Check**：

```bash
which gcloud && gcloud --version
```

**預期 output**（兩種情況皆可視為 pass）：

- Case A（**推薦**，對齊 runtime minimalism）：

  ```
  gcloud not found
  ```

  完全沒裝 = 符合 MVP 純 shell 路線。

- Case B（已裝）：

  ```
  /opt/homebrew/bin/gcloud
  Google Cloud SDK 4XX.0.0
  ...
  ```

  已裝無副作用，可保留。

**失敗分支**：無 —— 此項不會造成 setup 卡關。如未來 Phase 2+ 引入
gcloud 依賴，再更新本 check。

---

## 4. `~/.config/gws/client_secret.json` 是否存在？

**Why**：gws 需要讀這個檔才知道 Client ID / Client Secret；issue
#119 workaround 的 env var 也從這個檔撈（`protocols/issue-119-workaround.md`
§具體命令）。

**Check**：

```bash
ls -l ~/.config/gws/client_secret.json
```

**預期 output**：

```
-rw-------  1 <you>  staff  ~400  ...  client_secret.json
```

關鍵點：

- **存在**
- **權限 = `600`**（`-rw-------`）—— `standards/credential-hygiene.md` 規則 2

進階驗證（Client type 正確為 Desktop）：

```bash
~/.cache/slides-toolkit/bin/jq -r '.installed.client_id' ~/.config/gws/client_secret.json
# 預期：非空字串，通常結尾為 .apps.googleusercontent.com
```

如果 `jq` 回傳 `null` 或 `key "installed" not found` → 表示你下載的
是 Web 類型的 `client_secret.json`（內層是 `.web.client_id`），需回
`gcp-console-walkthrough.md` §4 重建為 Desktop 類型。

**失敗分支**：

- 檔案不存在 → `gcp-console-walkthrough.md` §5（下載 + mv + chmod）
- 權限非 600 → `chmod 600 ~/.config/gws/client_secret.json`；同時檢查
  `chmod 700 ~/.config/gws/`
- `jq ... .installed.client_id` 回 null → client type 錯（Web 而非
  Desktop），回 `gcp-console-walkthrough.md` §4 重建

---

## 5. issue #119 env vars 是否已 export？

**Why**：個人 Gmail 上 gws 內建 Client 踩 `invalid_scope` /
`invalid_client`；需 export `GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET`
覆寫（詳解：`protocols/issue-119-workaround.md`）。

**Check**：

```bash
# 若走 env-guard.sh 路線：
ls -l ~/.config/gws/env.sh
# 預期：存在且 chmod 600

# 或當前 shell 直接驗 env var：
echo "ID length: ${#GOOGLE_WORKSPACE_CLI_CLIENT_ID}"
echo "SECRET length: ${#GOOGLE_WORKSPACE_CLI_CLIENT_SECRET}"
# 預期：兩者長度都 > 20
```

或用 `env-guard.sh check`：

```bash
bash scripts/google-slides/env-guard.sh check
# 預期：{"workaround_needed":false}
```

**預期 output 判準**：

- 兩個 env var 在當前 shell 中長度 > 20，**且**
- `env-guard.sh check` 回 `workaround_needed: false`

**失敗分支**：

- env var 空 / 未 export → `protocols/issue-119-workaround.md` §具體命令
  （三種路線選一：一次性 export / 寫 shell profile / `env-guard.sh apply`）
- `env.sh` 存在但 Terminal session 中沒生效 → `source ~/.config/gws/env.sh`
  或重開 terminal（若寫進 `~/.zshrc`）
- `env.sh` 權限非 600 → `chmod 600 ~/.config/gws/env.sh`

---

## 6. `gws auth whoami` 回傳是否正常？

**Why**：這是整個 setup 的 **end-to-end 驗證**。whoami 能回 email =
Client Secret 配對正確、issue #119 workaround 生效、Test user 已加、
API 已啟用、refresh token 有效、Keychain / file backend 至少一種可讀。
**whoami 過 = setup 全綠。**

**Check**：

```bash
gws auth whoami
```

**預期 output**：

```
your_email@gmail.com
```

對比 expected：跟你在 `gcp-console-walkthrough.md` §3 加進 Test users
的 email 完全一致。

**失敗分支**（依錯誤訊息分流）：

| 錯誤 | 根因 | 回到 |
|---|---|---|
| `401 Unauthorized` / `token expired` | token 過期（>7 天沒用） | SKILL.md [Every 7 days maintenance](../SKILL.md#every-7-days-maintenance) |
| `403 access_denied` | 登入的 Gmail 不在 Test users | `gcp-console-walkthrough.md` §3 |
| `403` + `API not enabled` | Slides / Drive API 未啟用 | `gcp-console-walkthrough.md` §6 |
| `invalid_scope` / `invalid_client` | issue #119 env var 未生效 | check 5 失敗 + `protocols/issue-119-workaround.md` |
| `Keychain item not found` / `KeyError` | Keychain silent fail | SKILL.md [Workarounds](../SKILL.md#workarounds) Keychain 段（自動 fallback 到 file backend） |
| `No such file or directory` `gws` | gws 不在 PATH | check 1 失敗 |
| 命令沒輸出就 exit 0 | 狀態異常 / 舊版 gws | `bash scripts/google-slides/bootstrap.sh --force` 重抓 |

---

## Quick run-all

想一次跑完所有 6 項，可手動組合：

```bash
echo "--- 1. gws binary ---"      && ls ~/.cache/slides-toolkit/bin/gws && ~/.cache/slides-toolkit/bin/gws --version
echo "--- 2. jq binary ---"       && ls ~/.cache/slides-toolkit/bin/jq && ~/.cache/slides-toolkit/bin/jq --version
echo "--- 3. gcloud (optional) ---" && (which gcloud && gcloud --version 2>/dev/null) || echo "gcloud not installed (OK, MVP doesn't need it)"
echo "--- 4. client_secret.json ---" && ls -l ~/.config/gws/client_secret.json
echo "--- 5. env vars ---"        && bash scripts/google-slides/env-guard.sh check
echo "--- 6. gws auth whoami ---" && gws auth whoami
```

第一個報錯的地方 = 卡點。依上面的「失敗分支」欄修復，然後從卡點重跑。

## 相關檔案

- `../SKILL.md`（主流程 + error messages guide）
- `../protocols/gcp-console-walkthrough.md`（10 步 tutorial）
- `../protocols/issue-119-workaround.md`（env var workaround 詳解）
- `../standards/credential-hygiene.md`（`client_secret.json` / `env.sh` chmod 規則）
- `../../scripts/google-slides/credential-check.sh`（自動化版 state detection）
- `../../scripts/google-slides/env-guard.sh`（check / apply issue #119 workaround）
- TECH-SPEC §3.2（google-slides-setup state detection 契約）
- TECH-SPEC §4.2（credential-check.sh / env-guard.sh script contract）
