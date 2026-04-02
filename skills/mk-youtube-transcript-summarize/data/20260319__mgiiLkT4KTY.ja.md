## Video Info

| Field | Value |
|-------|-------|
| **Title** | 【9.6万⭐】世界中が熱狂する怪物！Claude Codeを完全制御する神ツール「Superpowers」【ゆっくり解説】 |
| **Channel** | ゆっくりテックウォッチ |
| **Duration** | 8:22 |
| **Views** | 659 |
| **Upload Date** | 2026-03-19 |
| **Subtitle** | auto-generated (ja) |
| **URL** | https://www.youtube.com/watch?v=mgiiLkT4KTY |

## Content Summary

#### 開場與倉庫介紹

- Superpowers 是控制 AI 編程 Agent 行為的框架，並非傳統的編碼工具
- 主要語言為 Shell Script 與 Markdown，授權為 MIT
- 從公開至今僅 5 個月，獲得 96,000 顆星

#### AI 程式碼的品質問題

- AI 生成的程式碼「表面上看起來可以運作」，但缺乏測試，重構後容易出現 Regression
- AI Agent 習慣省略設計步驟，直接跳進實作
- 正確的開發流程應是：確認需求 → 設計 → 先寫測試 → 再實作

#### 爆炸性成長軌跡

- 2025 年 10 月公開，2026 年 1 月中旬開始爆發式成長
- 高峰時期單日獲得超過 2,400 顆星
- 背景：AI 編程 Agent 快速普及，品質管理問題開始浮現

#### AI 開發的三大課題

- 課題 1：AI 不會主動寫測試，除非被明確要求
- 課題 2：AI 省略設計步驟，直接跳進實作，導致整體一致性崩潰
- 課題 3：團隊中每個人使用 AI 的方式各異，開發流程無法標準化

#### Superpowers 的主要功能

- 7 個階段的工作流程：從腦力激盪開始，AI 不會立即產出程式碼
- Skill 依場景自動觸發：設計階段啟動 Brainstorming，實作階段啟動 TDD
- Git Worktree 隔離作業環境：實驗失敗也不影響主專案
- TDD 鐵則：必須先寫測試才能實作；違反者整段程式碼全數刪除，連「參考留存」也被禁止
- Sub-agent 驅動開發：每個任務呼叫全新 AI，避免因上下文過長導致判斷力下降
- 2 段式 Code Review：先驗功能規格符合度，再驗程式碼品質，兩關都通才能進入下一任務

#### 使用情境 1：新創工程師

- 導入前：每次 Release 都發生 Regression，深夜不斷修 Bug
- 導入後：TDD 被強制執行，無測試的程式碼無法存在
- 結果：Regression 幾乎消失；手工返工減少，整體開發速度反而加快

#### 使用情境 2：大企業技術主管

- 10 人團隊各自使用 AI 工具，指令方式五花八門
- 導入後：所有人統一採用相同的 7 階段工作流程
- 結果：Code Review 標準統一，程式碼品質的落差消失

#### 使用情境 3：AI 研究學生

- 分析 Superpowers 的 14 種 Skill 設計並撰寫論文
- 例：Systematic Debugging Skill 以 4 步驟系統性找出 Bug 根本原因（非表面修補）
- 如何控制 AI Agent 是目前熱門研究課題

#### 與競品的比較

- CLAUDE.md：靜態指令書，規則固定後直接套用，無動態調整
- Superpowers：Skill 依場景動態觸發，如智慧家居（回家自動開燈）般自適應
- Aider 等編程輔助工具：協助單一編碼任務
- Superpowers：管理從設計到測試、Review 的完整開發流程
- 支援 5 大平台：Claude Code、Cursor、Codex、Open Code、Gemini

#### 安裝與啟動方式

- Claude Code：透過官方 Marketplace，一條指令完成安裝（`/plugin install superpowers`）
- Cursor：在 Plugin Marketplace 搜尋「superpowers」即可安裝
- 安裝後無需任何額外設定，Skill 自動觸發，立即生效

## Key Takeaways

- Superpowers 是讓 AI Agent 自動遵循正確開發流程的框架，5 個月獲得 96,000 顆星，驗證了市場需求
- TDD 鐵則嚴格執行：先寫測試才能實作，違反者整段程式碼全刪，連參考都不允許留存
- Skill 依場景動態觸發（設計 → Brainstorming，實作 → TDD），而非靜態指令，這是核心差異所在
- Sub-agent 驅動開發：每個任務新開 AI，防止長上下文導致判斷力下降
- Superpowers 不是讓 AI 更聰明的魔法，而是讓 AI 遵守人類工程師本應有的正確開發流程
- 適合多種場景：新創（防 Regression）、大企業（開發流程標準化）、研究者（分析 Skill 設計）
- 支援 5 大主流平台，安裝即自動運作，無需任何額外設定
