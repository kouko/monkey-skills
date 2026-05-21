# Pre-flight checklist — slides-builder

10 項檢查；任一 fail 則依指定 exit code 中止 pipeline，**不**進 recipe 階段。每項提供 shell-runnable check 或明確判定準則。

**使用方式**：builder 依序跑這 10 項，全通過才進 Step 2（recipe-create-presentation）。失敗訊息均為 stderr + structured JSON（stderr 一行 JSON + 一行人讀 hint）。

v0.3 change：移除 template registry lookup；新增 `layout_hint` enum 驗證；schema version 升為 `1.2`。

---

## 1. [ ] `slide-plan.json` `target == "google-slides"`

```bash
jq -e '.target == "google-slides"' slide-plan.json > /dev/null
```

- Fail → **exit 12** + hint：`unsupported target "<value>"; MVP only supports google-slides (Phase 2+ trigger: PRODUCT-SPEC §3.5)`

## 2. [ ] `slide-plan.json` `version == "1.2"`

```bash
jq -e '
  .version == "1.2"
  and (.output_title | type == "string" and length > 0)
  and (.slides | type == "array")
' slide-plan.json > /dev/null
```

必填頂層欄位皆備、型別正確。Fail → **exit 15**。

## 3. [ ] 每個 slide 的 `layout_hint` 屬於 7 enum 之一

```bash
jq -e '
  [.slides[].layout_hint] |
  all(. == "TITLE"
      or . == "TITLE_AND_BODY"
      or . == "TITLE_AND_TWO_COLUMNS"
      or . == "SECTION_HEADER"
      or . == "MAIN_POINT"
      or . == "BIG_NUMBER"
      or . == "BLANK")
' slide-plan.json > /dev/null
```

- Fail → **exit 15** + hint：`invalid layout_hint; allowed: {TITLE, TITLE_AND_BODY, TITLE_AND_TWO_COLUMNS, SECTION_HEADER, MAIN_POINT, BIG_NUMBER, BLANK} (see Google Slides API predefinedLayout)`

（TECH-SPEC §4.1 schema v1.2）

## 4. [ ] 所有 `slides[].images[].local_path` 檔案存在 + 大小合格

對每個 image entry 跑：
- Path 解析（absolute / `~` 展開 / cwd-relative；見 TECH-SPEC §9 OPEN-8）
- `[[ -f "$resolved" ]]`
- Size：`find "$resolved" -size -50M | grep -q .`
- Extension：`.png` / `.jpg` / `.jpeg` / `.gif`

```bash
jq -r '.slides[].images[]?.local_path' slide-plan.json | while read -r p; do
  resolved=$(eval echo "$p")
  [[ "$resolved" != /* ]] && resolved="$PWD/$resolved"
  [[ -f "$resolved" ]] || { echo "missing: $resolved" >&2; exit 14; }
  size=$(stat -f%z "$resolved" 2>/dev/null || stat -c%s "$resolved")
  [[ "$size" -lt 52428800 ]] || { echo "too big: $resolved" >&2; exit 14; }
done
```

- Fail → **exit 14**（缺檔 or 過大 or 格式不支援）

## 5. [ ] `gws auth whoami` 正常（token 未過期）

```bash
scripts/gws/credential-check.sh
```

回傳 `{"backend":"...","token_valid":true,"expires_in_days":N,"account_type":"personal"|"workspace"|"unknown"}` 且 `N > 0`。

- `token_valid == false` 或 `expires_in_days <= 0` → **exit 10** + hint：`Your gws refresh token has expired (Google External + Testing policy applies to personal accounts; Workspace Internal apps don't hit this). Run: bash scripts/gws/refresh-auth.sh`
- `account_type == "workspace"` → 7-day expiry doesn't apply; token validity check should still pass but the "refresh every 7 days" expectation is personal-only
- Keychain + file backend 都失敗 → **exit 18**

## 6. [ ] 所需 scope 已 grant（`presentations` + `drive` + `documents` + `spreadsheets`）

```bash
gws auth scopes 2>/dev/null | grep -q 'presentations' && \
  gws auth scopes 2>/dev/null | grep -qE 'auth/drive(\b|[^.])'
```

未 grant → **exit 10** + hint：`missing required scopes (need presentations + drive + documents + spreadsheets). Run gws-setup and re-authorize`

（TECH-SPEC §4.4：所需 4 個 scope `presentations` + `drive` + `documents` + `spreadsheets`；least-privilege 由 toolkit 的 `safe-delete.sh` 三層防護 wrapper 在應用層 enforce，而非由 OAuth scope 邊界 enforce）

## 7. [ ] 網路可通 `googleapis.com`

```bash
curl -sSf --max-time 5 -o /dev/null https://www.googleapis.com/discovery/v1/apis
```

- Fail（DNS / 封鎖 / proxy）→ **exit 1** + hint：`network unreachable to googleapis.com; check connectivity / proxy`

## 8. [ ] `~/.cache/gws-toolkit/bin/gws` 存在 + executable

```bash
[[ -x "$HOME/.cache/gws-toolkit/bin/gws" ]] && \
[[ -x "$HOME/.cache/gws-toolkit/bin/jq" ]]
```

- Fail → **exit 1** + hint：`gws/jq binary missing — run gws-setup (scripts/gws/bootstrap.sh)`

（TECH-SPEC §2.3 + §4.2：由 `gws-setup` 的 `bootstrap.sh` 自動下載（HTTPS + `curl -f`；v0.3 不做 SHA-256 pin）；builder 不自己抓）

## 9. [ ] issue #119 env vars 已 export（若 workaround 仍需要）

```bash
scripts/gws/env-guard.sh check
```

回傳 `{"workaround_needed": true/false}`。

- `workaround_needed == true` 且 env var 未設 → **exit 16** + hint：`issue #119 workaround not active; run gws-setup to apply (env-guard.sh apply)`
- `workaround_needed == false` → pass（gws 版本已修）

（TECH-SPEC §6.1：builder 只 `check`、不 `apply`；mutation 路徑歸 `gws-setup`）

## 10. [ ] Dry-run 模式確認

```bash
dry=$(jq -r '.dry_run // false' slide-plan.json)
```

- 若 `dry_run == true` → builder 跑本 checklist 1–9 + path 解析 + local image 存在性，**不**進 recipe、**不**呼 Google API
- 完成後 stdout 印：`{"url":null,"presentation_id":null,"slides_count":0,"warnings":[],"dry_run":true}`
- 人讀訊息：`Dry-run complete. Pre-flight passed. Re-run with "dry_run": false to actually generate the deck.`

---

## Summary：exit code 對映

| Check # | 失敗 → exit |
|---|---|
| 1 | 12（unsupported target） |
| 2 | 15（schema version / 基本欄位 fail） |
| 3 | 15（`layout_hint` 不在 7 enum） |
| 4 | 14（local image missing / too big / bad format） |
| 5 | 10（token expired） / 18（credential backend all fail） |
| 6 | 10（scope not granted） |
| 7 | 1（network） |
| 8 | 1（binary missing — setup 未跑） |
| 9 | 16（issue #119 workaround 未 apply） |
| 10 | — (dry_run 為設定，不 fail；成功後 short-circuit) |

**全通過** → 進 Step 2：`../protocols/recipe-create-presentation.md`。

## v0.3 removed checks

- ~~`backend_config.template_ref` 非空~~（template workflow 移除）
- ~~`template_ref` 在 `templates/registry.md` 找得到~~（registry 不存在）
- ~~SHA-256 binary verification~~（bootstrap 不做）
- ~~Template schema fingerprint 比對~~（template 不存在）

## See also

- TECH-SPEC §4.1（schema v1.2）、§4.2（完整 exit code 表）、§4.6（E2E data flow v0.3）、§9 OPEN-8（path 解析）
- `scripts/gws/credential-check.sh`、`env-guard.sh`、`bootstrap.sh`
- 下游 recipe（v0.4 α-trim 後內附於本 skill）：`../protocols/recipe-create-presentation.md` → `recipe-create-slides.md` → `recipe-insert-text.md` → `recipe-insert-image.md`
