# slides-toolkit

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> ⚠️ **Cowork 相容性**：僅支援 Claude Code CLI / Code tab。Cowork tab 被 sandbox URL allowlist 擋住 Google Slides API 呼叫。完整 retrospective 見 [`investing-toolkit/docs/mcp-setup.md`](../investing-toolkit/docs/mcp-setup.md)。

**Version**: 0.1.0-mvp
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT

Google Slides 產生 toolkit — 將結構化 brief（outline + tables +
本地圖片）透過 Claude Code skills 轉成完成的 Google Slides 簡報。
單指令 pipeline：`brief → deck URL ≤ 3 min`。

Backend-agnostic 的設計知識層（`slides-design`）加上可插拔的
backend builders。MVP 僅內建 Google Slides backend；HTML / PPTX /
Marp backends 屬 Phase 2+ 並採 trigger-gated（見 `PRODUCT-SPEC.md §3.5`）。

## Status

- **Release**：MVP v0.1.0-mvp（pre-release；Platform-Pivot spec 於 2026-04-23 凍結）
- **Backends**：僅 `google-slides`
- **Platform**：macOS 14+（darwin-arm64 / darwin-x64）
- **Primary user**：kouko（個人生產力工具）
- **Runtime posture**：純 shell + `curl` + 瀏覽器；`gws` / `jq` binary
  自動下載到 `~/.cache/slides-toolkit/bin/` 並驗證 SHA-256

## Quick Start

從全新機器到第一份 deck 共三步。

### 1. 安裝

```bash
# 透過 monkey-skills Claude Code marketplace 加入此 plugin
# （在 marketplace.json 註冊後 plugin 會自動啟用）
```

### 2. Setup（首次 onboarding，約 20 分鐘）

於 Claude Code 內呼叫 setup skill：

```
/google-slides-setup
```

會引導你完成：

- `gws` binary 下載 + SHA-256 驗證
- Google Cloud Console 4 步驟 OAuth client 設定（External + Testing 模式）
- Keychain / file-backend credential 儲存方式偵測
- Issue-119 workaround 環境變數 guard（`GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET`）
- 首次登入授權 + token smoke test

預算：乾淨 macOS 機器上 **≤ 20 分鐘**（KR2）。

### 3. 產出第一份 deck

```
/using-slides-toolkit
```

若想先取得敘事 + chart-type 指引，挑 `slides-design`，
再交由 `google-slides-builder` 建立 deck。或者若你已有
`slide-plan.json` 並註冊好 template Drive ID，可直接走
builder。

預算：從 brief 提交到 Drive URL **≤ 3 分鐘**（KR1）。

## Skills Inventory

| Skill | Layer | 用途 |
|-------|-------|------|
| `using-slides-toolkit` | router（backend-agnostic） | 入口點 — 依 `target` 路由到 setup / design / builder |
| `slides-design` | knowledge（backend-agnostic） | Minto Pyramid + SCQA + chart-selection reference；適用任一 backend |
| `google-slides-setup` | google-slides backend | 首次 onboarding（gws + GCP + auth）；具狀態感知分支 |
| `google-slides-builder` | google-slides backend | 執行層 — 透過 gws 進行 copy template / replaceAllText / insert-image |

Phase 2+（trigger-gated；不在 MVP 內）：`html-builder`、`pptx-builder`、
`marp-builder`。

## Prerequisites

macOS 14+ 內建：

- `zsh` / `bash`
- `curl`
- 任一現代瀏覽器（Google OAuth 同意流程）

Toolkit 自行下載其餘元件：

- `gws` binary → `~/.cache/slides-toolkit/bin/gws`（SHA-256 pinned）
- `jq` binary → `~/.cache/slides-toolkit/bin/jq`（SHA-256 pinned）

**不需要**：Python、uv、gcloud、Homebrew、Node.js。除 shell 外
零語言 runtime。

## Architecture

三層設計（完整內容見 `PRODUCT-SPEC.md §6.3.1` + `TECH-SPEC.md §2.1-§2.2`）：

```
┌──────────────────────────────────────────────────────┐
│ Layer 1 — Router (backend-agnostic)                  │
│   using-slides-toolkit                               │
│     → dispatches by slide-plan target field          │
└────────┬─────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────┐
│ Layer 2 — Design knowledge (backend-agnostic)        │
│   slides-design                                      │
│     → Minto / SCQA / chart-selection                 │
│     → applies to google-slides / html / pptx / marp  │
└────────┬─────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────┐
│ Layer 3 — Backend execution (backend-specific)       │
│   google-slides-setup     [MVP]                      │
│   google-slides-builder   [MVP]                      │
│   html-builder            [Phase 2+]                 │
│   pptx-builder            [Phase 2+]                 │
│   marp-builder            [Phase 2+]                 │
└──────────────────────────────────────────────────────┘
```

**因為**設計原則（敘事結構、chart 選擇）跨輸出格式皆穩定，
而執行技術（gws / pandoc / python-pptx / marp-cli）每個 backend
各自演進。解耦可避免每新增一個 backend 就動到知識層。

跨域產品觀點（願景 + MVP 範圍 + Job Story + 4 Big Risks）見
`PRODUCT-SPEC.md`；模組設計、資料流、interface contract 見
`TECH-SPEC.md`。

## Security Notes

Credentials 絕不進入 repository。雙層防護：

1. **`.claude/settings.json` deny rule** — 阻擋 Claude 工具層級對
   credential 檔案（home-dir + repo-relative）的 Read /
   Bash / Write 存取。Repo-relative `.gitignore` 無法保護
   `~/.config/gws/**`，因為 git 不會展開 `~`；deny rule 用以填補
   此缺口。
2. **`.gitignore`** — 排除 repo-relative 的祕密 pattern：
   `.config/gws/`、`**/client_secret*.json`、`**/credentials.enc`、
   `**/.encryption_key`、`.env*`、`.cache/`、本地測試 fixture。

完整威脅模型（OWASP ASVS v5.0.0 L1 — V1 / V2 / V5 / V13 / V14 / V16
mapping）、pre-commit hook 建議、credential 洩漏 incident response
playbook 見 `TECH-SPEC.md §8 Security & Credential Hygiene`。

Incident log（若有觸發）依需求放在 `incidents/` — 不預先建立。
Playbook 條目格式見 `incidents/README.md`。

## License

MIT — 與 parent `monkey-skills` repository 一致。詳見 repo root 的
`/LICENSE`。

## Links

- [PRODUCT-SPEC.md](./PRODUCT-SPEC.md) — planning-team spec（願景、使用者、
  目標、非目標、Platform Pivot 理由）
- [TECH-SPEC.md](./TECH-SPEC.md) — code-team spec（架構、模組、
  介面、測試、安全性、OPEN answers）
- [CHANGELOG.md](./CHANGELOG.md) — 版本歷程
- [parent repo](https://github.com/kouko/monkey-skills)
