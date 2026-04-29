# slides-toolkit

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 透過 Claude Code skill 從 brief 一鍵生成 Google Slides deck。純 shell + `gws` CLI，免 Python / gcloud。

> ⚠️ **Cowork 相容性 — 僅支援 Claude Code CLI / Code tab。** Google
> Slides 與 Drive API 呼叫會被 Claude Desktop Cowork sandbox 的 URL
> allowlist blocked（與 `investing-toolkit` 同一限制；參考
> [investing-toolkit MCP setup retrospective](../investing-toolkit/docs/mcp-setup.md)）。
> 若你在 Cowork 環境，請改用 Claude Code CLI 或 Claude Desktop Code
> tab。

## Background

固定產出 Google Slides deck 的工作中，機械性勞動佔很大比重 ——
文字替換、圖片 upload、placeholder 對位。`slides-toolkit` 把這層
重複勞動 skill 化，讓時間與注意力落在內容與 design 判斷上，而不
是 deck 配管。

設計上採用 **Platform Pivot architecture**（PRODUCT-SPEC v0.2）—
backend-agnostic 的設計知識 layer（`slides-design`）與可插拔的
execution layer 解耦。MVP 僅實作 `google-slides` backend；
`html` / `pptx` / `marp` backend 屬 Phase 2+ trigger-gated 範圍。

## Status

| 項目 | 值 |
|---|---|
| Release | `0.1.0-mvp`（見 [`CHANGELOG.md`](CHANGELOG.md)） |
| Backends | `google-slides`（MVP）· `html` / `pptx` / `marp` 為 Phase 2+ trigger-gated |
| Platform | macOS（darwin-arm64 / darwin-x86_64） |
| Account scope | 個人 Google 帳號（`@gmail.com`）；Workspace 帳號屬 Phase 2+ |
| Runtime posture | shell + curl + 瀏覽器；toolkit 自動取得 `gws` / `jq` binary |
| License | MIT |

## 安裝

透過 `monkey-skills` marketplace 加入 plugin，然後重啟 Claude
Code 讓它讀取 skill。

```bash
# 在 Claude Code 內執行
/plugin install slides-toolkit@monkey-skills
```

## Quick start

兩階段流程。第一次 setup 為一次性，之後每次生 deck 只走第二階段。

### 1. 第一次 setup（目標：≤ 20 分鐘 — KR2）

```
> /google-slides-setup
```

route 到 `google-slides-setup` skill。它會偵測目前狀態，把 `gws` +
`jq` 抓到 `~/.cache/slides-toolkit/bin/`，引導你完成 GCP Console
的手動步驟（OAuth Client + Test User），如帳號需要的話會把 issue
#119 workaround 寫入 `~/.config/gws/env.sh`。

此流程受 Google OAuth policy（External + Testing mode）邊界限制，
哪些可自動化、哪些不行請參考
[`docs/google-oauth-automation-limits.md`](docs/google-oauth-automation-limits.md)。

### 2. 生成 deck（目標：≤ 3 分鐘 — KR1）

```
> /using-slides-toolkit
> 「把這份 outline 做成 6 頁的 product proposal」
```

router（`using-slides-toolkit`）判讀意圖，必要時委派
`slides-design` 給出 narrative 結構建議（Minto / SCQA / chart 選
型），然後把 `slide-plan.json` v1.2 交給 `google-slides-builder`。
builder 跑 4 步 pipeline（建空 deck → 用 predefined layout 建
slide → 插入文字 → 插入本機圖片），回傳 Drive URL。

`/using-slides-toolkit` 與 `/google-slides-setup` 都是 skill 的
auto-route（plugin 沒有 `commands/` shim，未提供 slash command）。
直接打 skill 名稱，Claude Code 就會 dispatch。

## Skills

plugin 提供 5 個 skill，分為 3 層。

| Skill | Layer | 角色 |
|---|---|---|
| `using-slides-toolkit` | Router（backend-agnostic） | 判讀意圖、讀 `slide-plan.target`、route 到對應 skill |
| `slides-design` | Knowledge（backend-agnostic） | Minto Pyramid + SCQA narrative、chart 選型；對所有 backend 通用 |
| `google-slides-setup` | google-slides backend | 第一次 GCP Console / OAuth / `gws` bootstrap，後續做 state detection |
| `google-slides-api` | google-slides backend | Low-level per-op recipe reference — `presentations.create`、`batchUpdate createSlide`、`insertText`、`createImage` |
| `google-slides-builder` | google-slides backend | High-level orchestration — `slide-plan.json` v1.2 → pre-flight → 4 recipe chain → deck URL |

`using-slides-toolkit` 與 `slides-design` 刻意設計為 backend-agnostic，
未來 `html-builder` / `pptx-builder` / `marp-builder` skill 可重用同
一個 routing 入口與設計 reference，不需修改。

## 前置條件

| 項目 | 要求 |
|---|---|
| OS | macOS 14+（darwin-arm64 / darwin-x86_64）；Linux / WSL 屬 Phase 2+ |
| Shell | zsh 或 bash（macOS 預設 zsh 即可） |
| 網路 tool | `curl`（macOS 預載） |
| 瀏覽器 | Chrome 或 Safari（GCP Console 步驟需要一次） |
| Google 帳號 | 個人 `@gmail.com`；Workspace 帳號屬 Phase 2+ |

**不需要**：Python、uv、gcloud、brew、npm。`gws` 與 `jq` binary 由
`scripts/google-slides/bootstrap.sh` 透過 HTTPS + `curl -f` 抓到
`~/.cache/slides-toolkit/bin/`。

## Architecture

3 層架構。router 與設計知識層 backend-agnostic；唯一綁定特定輸出
format 的是 execution 層。

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1 — Router（backend-agnostic）                       │
│  using-slides-toolkit                                       │
│  判讀意圖 · 讀 slide-plan.target · dispatch                 │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────────┐
        ▼                    ▼                        ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│  Layer 2 —      │  │  Layer 3 —      │  │  Layer 3 —           │
│  Design         │  │  Backend exec   │  │  Backend exec        │
│  knowledge      │  │ （onboarding）  │  │ （build pipeline）   │
│ （agnostic）    │  │                 │  │                      │
│  slides-design  │  │  google-slides- │  │  google-slides-      │
│                 │  │  setup          │  │  builder             │
│  Minto · SCQA · │  │                 │  │      ↓ 使用          │
│  chart 選型     │  │  GCP / OAuth /  │  │  google-slides-api   │
│                 │  │  gws bootstrap  │  │  (per-op recipes)    │
└─────────────────┘  └────────┬────────┘  └──────────┬───────────┘
                              │                      │
                              └──────────┬───────────┘
                                         ▼
                              scripts/google-slides/*.sh
                              gws CLI · ~/.cache binaries
                                         ▼
                              Google Slides + Drive API
                                         ▼
                                   Deck URL
```

Phase 2+ backend（`html-builder` / `pptx-builder` /
`marp-builder`）可作為 Layer 3 與 `google-slides-builder` 並列加
入，Layer 1 / Layer 2 不需更動。詳見 PRODUCT-SPEC §2.1 / §2.2 與
TECH-SPEC §2.1 / §2.2。

## 安全性

Credential 絕不入 repo。透過兩個互補機制守住此邊界（TECH-SPEC §8）：

**Claude tool layer block** — `.claude/settings.json` 拒絕任何接
觸 gws credential store 的 Read / Bash / Write：

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

**Repo-relative ignore** — `.gitignore` 阻擋可能落入 repo tree 的
credential 檔：

```
.config/gws/
*/keyring-file.json
*/env.sh
.cache/slides-toolkit/
```

`.gitignore` 無法 match `~/.config/gws/**`（git 只用 repo-relative
path、不展開 `~`），home directory 路徑由上方 `settings.json` deny
rule 負責。如果不慎洩漏 credential，請依 TECH-SPEC §8.4 的 incident
playbook 處理。

## 連結

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — product 方向、Job Story、OKR / KR、Non-Goals、Phase 2+ trigger
- [TECH-SPEC.md](TECH-SPEC.md) — module 設計、`slide-plan.json` v1.2、shell script 契約、安全性
- [CHANGELOG.md](CHANGELOG.md) — 版本歷史（`0.1.0-spec` → `0.6.0-i18n`）
- [docs/console-ui-reference.md](docs/console-ui-reference.md) — 目前的 Google Cloud Console UI walkthrough
- [docs/google-oauth-automation-limits.md](docs/google-oauth-automation-limits.md) — 哪些無法自動化、為什麼
- [docs/gws-cli-quirks.md](docs/gws-cli-quirks.md) — live test 中發現的 gws CLI 陷阱
- 母 repository：[`monkey-skills`](https://github.com/kouko/monkey-skills)

## 貢獻

本 plugin 屬 [`monkey-skills`](https://github.com/kouko/monkey-skills)
repository 的一部分。Issue / PR 請開在該 repo。skill 結構遵循 repo
root 的 `CLAUDE.md` 與 `domain-teams:skill-team` skill 的慣例。

## License

MIT — 詳見 repository root 的 [LICENSE](../LICENSE)。
