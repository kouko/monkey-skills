# incidents/

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

Credential-leak incident playbook output location. **On-demand** — 僅在
實際發生 credential-leak incident 時才於此目錄新增 markdown 檔案，每
起 incident 一份。平時此目錄只保留本 README。

## 觸發條件

發現以下任一情況即啟動 playbook：

- `gws` OAuth client ID / secret 已被 `git commit` 到 work tree
- `git log -p` 或 `gitleaks` 掃到任一 credential pattern
- GCP Console 告警（unauthorized API calls / quota spike）
- 本人或協作者誤將 `~/.config/gws/*` 拷到 repo 路徑

## 檔名慣例

```
incidents/YYYY-MM-DD-<short-slug>.md
```

範例：`incidents/2026-05-12-leaked-client-secret.md`

## 檔案內容框架

對照 `TECH-SPEC.md §8.4 Credential 洩漏 incident response playbook` 的 7
步驟。每份 incident markdown **絕對不可包含實際 secret 值**（ASVS V16
audit log 合規要求），只記錄：

1. 發現時間 + 發現途徑（e.g. `gitleaks protect` / code review / GCP 告警）
2. 影響範圍（哪些 commit / branch / remote）
3. 已執行步驟（對映 `TECH-SPEC.md §8.4` 7 步；含完成時間 + 執行人）
4. Rotate 清單（OAuth Client ID、Keychain / file-backend 舊 token、7
   天內衍生資源）
5. 跟進 action item（pre-commit hook 強化、新增 deny rule、協作者通知
   rebase 狀態）
6. Post-mortem（預防下次：哪條 defence-in-depth 失效？為什麼？）

## 與其他目錄的關係

- `.gitignore` + `.claude/settings.json` deny rule 是**事前防護**
- `incidents/` 是**事後記錄** + 改進循環
- `scripts/install-pre-commit.sh`（Phase 2 trigger-gated）是介於中間
  的 shift-left 偵測

事前防護無法保證 100% 覆蓋（home-dir credential、外部工具誤動作），
所以事後 playbook 是必要補網。
