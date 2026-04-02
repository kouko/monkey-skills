## Video Info

| Field | Value |
|-------|-------|
| **Title** | Every Level of Claude Code Skills in 27 mins |
| **Channel** | Simon Scrapes |
| **Duration** | 27:10 |
| **Views** | 2,829 |
| **Upload Date** | 2026-03-19 |
| **Subtitle** | auto-generated (en) |
| **URL** | https://www.youtube.com/watch?v=-u_igSQHAIo |

## Content Summary

#### 簡介：Claude Code Skills 的 7 個層次

- 大多數人在建立 Claude Code skills 時會卡在第 2 或第 3 層，無法突破
- 作者花了數百小時研究 Anthropic 完整的 skill 建構指南，並建立了超過 20 個生產級 skills
- 這些 skills 目前每天在其行銷策略與業務運營中實際運作

#### Level 1：了解什麼是好的 Skill

- Skill 的本質是一個知識資料夾，核心是 skill.md 檔案（相當於標準作業程序 SOP）
- 範例：「最近 30 天」trending 研究 skill，可從 Reddit 和 X 收集熱門討論（含按讚數、轉推數等）
- Skill 的三個可選資料夾：
  - scripts：執行程式碼（如 API 呼叫）
  - references：按需載入的文件與範本
  - assets：模板、字型、圖示等
- 三層漸進式揭露（Progressive Disclosure）：
  - Tier 1：YAML front matter — 永遠載入，Claude 用來判斷是否啟用此 skill（上限 15,000 字元）
  - Tier 2：skill.md 主體 — 只在 skill 被啟用時載入
  - Tier 3：references/scripts/assets — 只在執行對應步驟時才載入

#### Level 2：Skill 建構的黃金法則

- 常見錯誤：把所有資訊塞進一個龐大的 skill.md，導致 context window 爆炸（5,000–7,000 行同時載入）
  - 後果：執行緩慢、偏離指令、Claude 忽略明顯的指示
- 黃金法則：skill.md 控制在 200 行以內，作為「目錄」指向 references 資料夾
  - 200 行限制基於 LLM 有效掃描的最佳範圍設計
- YAML front matter 技術描述的三步驟框架：
  - 觸發條件：哪些關鍵字/情境啟用 skill
  - 排除條件：哪些情境不應觸發
  - 輸出結果：skill 產生什麼，及可供其他 skills 使用的格式
- Marketplace skills 的平均觸發率僅 20%（五次中只觸發一次）

#### Level 3：從任何來源匯入並改進 Skills

- 許多 marketplace skills 內容好但結構差（1,000 行單一 skill.md、無 progressive disclosure）
- 解法：使用 Anthropic 的 skill creator skill 進行重構
  - 範例：將 400 行的 AI SEO skill 重構至 148 行（減少 60%）
  - 建立 4 個新 references 檔案（authority signals、AI visibility audits、content type optimization 等）
- Claude Code 在執行不同步驟時可動態載入/卸載 references，節省 token 並提升準確性
- 流程：安裝 skill → 用 skill creator 重構至 200 行 → 將詳細資訊移至 references 資料夾

#### Level 4：將 Skills 個人化到你的業務

- 沒有業務情境的 skill 幾乎沒有價值；加入品牌情境後輸出才真正有競爭力
  - 差異舉例：通用 AI SEO skill vs. 了解你品牌聲音、受眾、內容支柱的 AI SEO skill
- 作者的「Agentic OS」：行銷、策略、運營、視覺的生產級 skill 套組
  - 共享 brand context 資料夾：包含 ICP（理想客戶輪廓）、定位、聲音特徵
- 四步驟流程：
  - 識別要建構的 skill
  - 用 skill creator 生成基礎結構
  - 加入業務情境至 references 資料夾
  - 對照實際工作成果測試輸出

#### Level 5：用數據測量與優化 Skills

- Anthropic 在 skill creator skill 中加入評估（eval）與基準測試（benchmarking）功能
- 解決痛點：以往只能憑感覺判斷 skill 品質，無法客觀衡量版本差異
- Eval 功能運作方式：
  - 定義 3–5 個具體評估標準（例：文章是否有明確目標查詢？是否有作者簡介？是否有內部連結？）
  - 執行 5 次測試並打分，產生結構化報告
  - 範例結果：93% 通過率；去掉部分 references 後 token 大幅降低但品質不變
- A/B 測試：可比較「有/無某個 references 檔案」的品質差異，找出真正有貢獻的檔案
- 可對個別輸出提供回饋，直接驅動 skill 改進並重新測試

#### Level 6：讓 Skills 自我改進

- 核心概念：skills 應在每次互動後學習並持續進步，關鍵是建立回饋迴路
- 機制：在 skill 中加入 rules/learnings 檔案，每次執行後捕捉觀察結果
  - 範例：「開頭段落直接回答搜尋查詢的文章，在 AI 搜尋中被收錄得更快」
- Wrap-up skill：每次工作階段結束時自動將回饋寫入各 skill 的 learnings.md 檔案
- 連結 Level 5：可用 eval 驗證 learnings 是否真的提升了輸出品質（前後基準比較）
- 每週定期整理 learnings 檔案，避免它本身變成 context window 問題

#### Level 7：建立 AI 勞動力（AI Workforce）

- 最終層次：讓各 skills 相互協作，形成完整的自動化工作流
  - 範例：copywriting skill 在儲存前自動通過 humanizer skill 處理，確保文字更像人寫的
  - 另一例：content repurposing skill 在無法取得 YouTube 逐字稿時，自動呼叫另一個 skill 協作
- 整合後系統具備：專業知識 + 品牌個人化 + 自我測試（eval）+ 自我學習 + 跨 skill 協作
- 作者誠實提醒：基礎 skills（聲音特徵、定位、ICP）必須先建好，整套系統才能發揮效用
- 技術門檻低：不需技術背景，業務擁有者了解自己的流程即可；skills 處理複雜度，你提供情境與回饋

## Key Takeaways

- skill.md 必須控制在 200 行以內，作為指向 references 的「目錄」，而非塞滿所有資訊的大檔案
- 三層漸進式揭露（Progressive Disclosure）是 Claude Code skills 效能的核心設計原則
- YAML front matter 的描述品質直接影響 skill 觸發率，marketplace skills 平均觸發率僅 20%
- 沒有業務情境的 skill 只能產出通用內容；加入品牌聲音、受眾、定位後輸出才真正有競爭力
- Anthropic 的 eval 功能讓 skill 測試從「憑感覺」進化到可量化的 A/B 測試與基準比較
- 透過 learnings 檔案建立回饋迴路，skills 可在每次互動後自我改進，3 個月後的版本將大幅優於初版
- 最終目標是讓 skills 相互協作形成完整 AI 工作流，而非各自獨立運作的工具集合
- 不需技術背景即可建立這套系統，業務邏輯和品牌情境的輸入才是最關鍵的貢獻
