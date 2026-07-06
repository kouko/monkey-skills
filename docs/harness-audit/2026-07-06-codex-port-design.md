# Codex Port 設計書 — rules/ 制度層跨 host 化

> 日期：2026-07-06 · 狀態：設計完成，待排程執行
> 證據：三路偵察（dotfiles 機制實讀、repo 內 Codex 0.139.0 實測知識、
> developers.openai.com/codex 官方文件 2026 現況），關鍵事實逐條標注信度。
> 引用基準：[A0](2026-07-06-a0-institution-map.md)、
> [B 提案](2026-07-06-b-claude-md-proposal.md)（已核准落地 fc5da06 —
> **dotfiles repo** 的 commit，本 repo 解析不到）。
> 字母標籤解碼：C=model-dispatch.md、D=judgment-rubrics.md、
> F=institution-maintenance.md（沿用 A0 §3 缺口地圖的交付項編號）。

## 1. 事實基礎（決定架構的五件事）

| # | 事實 | 信度 | 出處 |
|---|---|---|---|
| 1 | dotfiles 同步是**嚴格整檔覆蓋**（pre-commit hook `_scripts/sync-agent-instructions.sh:50-58`＋stow 部署重灌；副本手改必毀）——per-host 路由文字不可能存在，此為 kouko 2026-06 明文決策（README.md:193-197「唯一真相」） | 實讀 | dotfiles 偵察 |
| 2 | Codex 讀全域 `~/.codex/AGENTS.md`（dotfiles stow 目標正確），多層 AGENTS.md 用 **concatenation** 合併，總量 32 KiB 上限——現行路由 4 行已抵達 Codex ✓ | 官方文件 | codex/guides/agents-md |
| 3 | Codex subagent = `multi_agent` feature（0.139.0 `stable true` 實測）；派工動詞 `spawn_agent`/`wait_agent`/`close_agent`（doc-sourced 未實跑）；**只能使用者顯式觸發，模型不能自主派工** | 混合 | codex-tools.md:89-107 |
| 4 | 模型選擇：**無 per-call model 參數**——經 `~/.codex/agents/*.toml` agent profile 綁定；effort 為 config 級 `model_reasoning_effort`（minimal→xhigh），非 per-call | doc-sourced | `dev-workflow/skills/distill-sessions/references/codex-tools.md:35-39`（model 綁 profile）＋官方 config-reference（effort 檔位；loom-code 的 codex-tools.md **不**覆蓋此題） |
| 5 | Codex 能 Read `~/.claude/rules/*.md`（普通磁碟檔）——**到達性缺口已由路由同步關閉**，剩內容缺口 | 推論（低風險） | — |

其他 load-bearing 細節：Codex skills 掃 `.agents/skills`（非 `.codex/skills`）；
skill description ≤1024 chars（rules 檔非 skill，不受限）；SessionStart hook
＋nested `additionalContext` 實測可用；PostToolUse on `apply_patch` 上游壞
（openai/codex#16732）→ 鏡射類 hook 在 Codex 惰性。

## 2. 架構（唯一可行形狀）

事實 1 鎖死：路由行共用（現狀），**分歧全部下沉到被指向的檔案層**。

```
~/dotfiles/claude/.claude/rules/        ← 5 檔，正好踩 F §4 上限
  model-dispatch.md          核心：host-neutral 派工邏輯
  judgment-rubrics.md        核心：已 ~90% neutral，微調
  institution-maintenance.md 核心：教訓路由＋權限（auto-memory 列標 host）
  hosts-claude-code.md       附錄：現三檔內所有 CC 專屬內容遷入
  hosts-codex.md             附錄：Codex 對應物＋結構性差異
```

- 每個核心檔頭的 host-scope 聲明改為 **host 偵測行**：
  「有 Agent/Workflow tool → 讀 hosts-claude-code.md；
  在 Codex（spawn_agent / codex exec）→ 讀 hosts-codex.md；
  其他 host（Gemini/Qwen）→ 只用核心檔，工具形規則跳過。」
- 遵循 repo 已驗證的 pattern：neutral 本體＋per-host mapping 檔
  （= dispatch-portability fix wave 的 codex-tools.md 模式，
  survey 判定為業界主流做法，與 obra/superpowers 一致）。

## 3. 三份核心檔各自怎麼拆

### model-dispatch.md（變動最大）
- **留在核心**（neutral）：§4 派工包三件套、§3 升降級「邏輯」（錯一次升、
  同任務兩敗帶軌跡升、2 次重派上限、批次粒度、降級批次套用）、
  §5 verify≠self-verify、§1 的 context 衛生半部（offset/limit、不重讀）。
- **遷 hosts-claude-code.md**：tier 表（sonnet/opus/haiku）、
  Explore/general-purpose 型別表、Workflow effort、name:/SendMessage gotcha。
- **hosts-codex.md 新寫**：
  - 派工三動詞＋`[features] multi_agent = true`＋agent profile
    （`~/.codex/agents/*.toml`：name/description/developer_instructions＋model）
  - **梯子的 Codex 語義**：升降級=切換 agent profile（事先備妥
    低/中/高三個 profile），非 per-call 換 model
  - **§1「指揮官不下場」的 Codex 降格**：模型不能自主 spawn →
    改寫為「主動向使用者**提議**派工＋理由」；context 衛生條款照用
  - 已知 gotcha：`.agents/skills` 路徑、apply_patch hook 上游壞、
    1024-char description 限制（寫 skill 時）
### judgment-rubrics.md（變動最小）
- 六條 rubric 全部本來就 host-neutral；只把 §1 例句裡的
  「sonnet/opus」改成「低階/高階 tier」＋host 檔給對照。
### institution-maintenance.md（中等）
- 決策樹 §1.1 的 auto-memory 是 CC 專屬 → 加一欄「Codex session：
  寫入 repo committed store（docs/ 或 git-memory trailers），無 auto-memory」。
- §3 cold-reader tax 在 Codex 的執行方式：`codex exec`（headless）跑盲測。

## 4. 驗證計畫（比照本次 dogfood 紀律）

1. **落檔前**：先實跑補證 doc-sourced 事實——`codex features list`、
   spawn_agent 動詞名、agent profile 綁 model（照 repo memory
   verify-agent-mechanisms-on-disk-not-self-report 的配方：unique marker
   ＋rollout log grep＋連續兩輪乾淨）。
2. **CC 側迴歸**：三核心檔改後照 F §3 各過一次 Sonnet 冷讀（判斷結果
   不得劣於本次 25/25 基線的對應題）。
3. **Codex 側首測**：`codex exec` 給「hosts-codex.md＋一個派工情境」，
   驗證它（a）讀對 host 檔（b）提議派工而非假裝自主派工（c）判斷題
   與 CC 側同答案。
4. **Gemini/Qwen 順帶**：host 偵測行的「其他 host」分支給一個煙霧測試
   （能正確只用核心、跳過工具形規則即可，不做深度）。

## 5. 成本／價值／時機（誠實條款）

- **價值排序**：D 核心化（任何 Codex session 即刻受益）＞ F（教訓不再
  只進 CC 專屬 auto-memory）＞ C（Codex 端因顯式觸發限制，只剩
  「提議派工＋梯子邏輯」的價值）。
- **成本**：一個專注 session（估 2-3 小時等級），大頭在驗證不在改寫。
- **風險**：五檔上限踩滿（第六題進不來）；hosts-codex.md 的半數事實
  是 doc-sourced——步驟 1 不做就落檔＝把制度建在未驗證地址上。
- **建議時機**：**等一個真實的 Codex 工作 session 出現再做**（cheap-
  experiment 原則）——現狀防呆已足（host-scope 擋誤套、路由已達），
  port 的邊際價值要有實際 Codex 用量才能兌現。若 Codex 用量始終低，
  這份設計書躺著也不虧。

## 6. 執行清單（給未來 session 的接手面）

1. 補證三件 doc-sourced 事實（§4.1）→ 更新本檔信度欄
2. 建 `~/.codex/agents/` 三檔 tier profiles（low/default/high）
3. 拆檔（§3）＋host 偵測行；host-scope 舊聲明刪除
4. 三層驗證（§4.2-4.4）全綠
5. dotfiles commit（rules 5 檔）＋per F §2 流程
6. 更新 A0 §2.4、auto-memory pending 項、本檔狀態欄

---
Changelog:
- 2026-07-06 初版（三路偵察合成；Fable 5 session 尾聲）。
