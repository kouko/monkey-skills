# Handoff

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 結束 session 時把 10 格式的 HANDOFF 檔案寫入 `.claude/handoffs/`。
> 下次 session 開始時載入該檔案，逐字執行每一條驗證指令，確認無誤後再繼續。
> 冷啟動 AI，零 context 流失。

---

## 概要 — 這個 skill 是什麼

跨 session 接續 skill。當你結束一個工作 session、希望下一個 AI agent 能夠
不靠對話記憶從上次停下的地方精確繼續時，這個 skill 把狀態寫成結構化 10 格式
HANDOFF 檔案，儲存在 `.claude/handoffs/`。

兩種模式：

- **Prepare 模式（準備）** — session 結束時。Agent 透過 Bash 執行
  `git rev-parse HEAD`、`git status --short`、`git log --oneline -5`、
  `claude --version`，然後用 Write 工具建立
  `.claude/handoffs/HANDOFF-YYYY-MM-DD-HHMMSS-<slug>.md`，包含
  `references/handoff-schema.md` 定義的全部 10 個區塊。輸出精度優先——
  完整路徑、完整錯誤訊息、使用者每輪發言逐字記錄、可執行驗證指令。

- **Resume 模式（繼續）** — session 開始時。Agent 用
  `ls -t .claude/handoffs/ | head -1` 找到最新檔案，完整 Read，然後逐一
  透過 Bash 執行 Block 9 的每條驗證指令，並把期望輸出和實際輸出並列顯示。
  若有任何不符則拒絕繼續。所有驗證通過後，以 3〜5 條整理目前狀況、待完成
  工作、下一步（Synthesis-check），詢問使用者確認後才開始工作。

HANDOFF 檔案的讀者是冷啟動 AI——新 session、零前情脈絡。精度優先於可讀性：
技術路徑、精確識別符、完整指令輸出。

---

## 何時使用，以及與姐妹 skill `recap` 的差異

兩個 skill 都用來重新定向，但針對的情況不同：

| 情況 | 使用什麼 |
|---|---|
| **對話途中**迷失方向（還在同一個 session 裡） | `dev-workflow:recap`（L3 session 內，只輸出到對話） |
| **結束 session**；希望冷啟動 AI 稍後繼續 | `dev-workflow:handoff` prepare 模式 |
| **開始新 session**；要載入上次狀態 | `dev-workflow:handoff` resume 模式 |
| 回到一個離開很久的 session（內建功能） | Claude Code 內建 `/recap`（away summary） |
| 把子任務委派給平行 agent | OpenAI Agents SDK 等（不同問題） |

`dev-workflow:recap` 是 L3——不寫入任何檔案，給還在 session 內的人類讀者，
輸出 7 格式對話摘要。

`dev-workflow:handoff` 是 L2——把檔案寫入 `.claude/handoffs/`，給未來
session 的冷啟動 AI 讀者，在繼續工作前強制執行可驗證的狀態確認。

兩個 skill 並存、互補。

---

## 呼叫範例——怎麼說都行

### Prepare 模式 — session 結束時說以下任何一句

- 「收尾」
- 「明天繼續」
- 「保存狀態」
- 「先這樣」
- 「記錄一下進度」
- 「今天先到這」
- 「寫一份 handoff」
- 「把現在的狀態存下來」

### Resume 模式 — session 開始時說以下任何一句

- 「繼續上次」
- 「從上次說到哪裡」
- 「載入狀態」
- 「接著做」
- 「讀一下 handoff 檔案再繼續」
- 「從昨天繼續」
- 「載入上次的 handoff」

---

## `.gitignore` 建議

`dev-workflow:handoff` 一律把 HANDOFF 檔案寫入 `.claude/handoffs/`。
要不要把這些檔案加進 git 是你的策略選擇：

**選擇加入 `.gitignore`（不提交）** — 在 `.gitignore` 加入：
```
.claude/handoffs/
```
若 HANDOFF 檔案包含認證 token、內部路徑、或私人任務細節，或不希望把
session 產出物留在 git 歷史，可這樣設定。

**選擇不加入 `.gitignore`（保留在 git 歷史）** — 不把 `.claude/handoffs/`
加入 `.gitignore`。HANDOFF 檔案會隨 branch 移動；換機器或團隊成員都可以
`git checkout` 後從已知的良好狀態繼續。

v0.1 路徑固定：skill 一律寫入 `.claude/handoffs/`，resume 模式的探索指令
（`ls -t .claude/handoffs/ | head -1`）也依賴這個路徑。git 追蹤中立——
skill 不會新增或修改 `.gitignore`。

---

## v0.2 暫不包含的功能

這些是 v0.1 刻意不做的部分：

- **強制引き継ぎ觸發偵測** — 偵測隱式 session 結束訊號（context 壓力、
  長時間靜默、使用者說「掰掰」），不需要明確觸發詞。v0.1 需要明確呼叫。
- **Interruption Snapshot 區塊** — 專門處理任務中斷（非 session 結束）
  的 Block 11。v0.1 所有情況都用現有 10 格式。
- **各工具 init-prompt 變體** — Codex / Cursor / Gemini 的寫入路徑不同；
  v0.1 只支援 Claude Code 的 Write 工具。HANDOFF 檔案的讀取（resume 模式）
  已支援跨工具（任何能讀 markdown 的工具都可以）。
- **`test-prompts.json` + `trigger-eval.json` 骨架** — 觸發準確率和
  schema 完整性的結構化評估基盤。等真實 session 的 dogfood 建立出品質
  基準後再加入。

---

## Files

```
handoff/
├── README.md           <- English README
├── README.ja.md        <- 日本語 README
├── README.zh-TW.md     <- 本檔（繁體中文）
├── SKILL.md            <- 執行檔（給 Claude）
└── references/
    └── handoff-schema.md  <- 10 格式模板 + 5 共通核心原則
```
