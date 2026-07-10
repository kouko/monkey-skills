# PRINCIPLES.md — macOS Meeting Transcriber

## North Star

**Goal:** 讓 macOS 用戶自動、準確地將會議錄音轉錄成標注講者名稱的完整逐字稿，無需人工逐次標註講者。

**Success:** 一場 30 分鐘～2 小時的企業會議轉錄準確率達到 ≥95%（包含企業內部名詞 + 講者識別），新講者首次出現時自動識別無需人工標註。

---

## Product Principles

1. 轉錄品質優先於功能廣度 — check: 產品規劃中的每個功能都能直接支持「會議錄音轉錄為帶講者標注的逐字稿」這個核心任務；無關功能（如跨會議 AI 摘要、即時會議分析、會議行動項提取、逐字稿版本控制）在 v1 版本範圍內明確不納入

2. 準確性是 Must-be 基線 — check: 轉錄準確率目標 ≥95%（企業內部名詞 + 講者識別）；任何新功能若測試發現威脅這個準確率基線，寧可延遲發布該功能也要保護基線

3. 講者識別、名詞自訂、和用戶修正反饋是持續學習循環 — check: 自動講者識別無需人工逐次標註；應用提供客製化的企業名詞庫機制；用戶的所有手動修正（錯字、講者名變更）被記錄並作為模型再訓練或微調的反饋信號，以提升後續轉錄準確率；每一個用戶修正都是系統學習該用戶語境的一部分

4. 用戶體驗的深度自訂優先於開箱即用速度 — check: 產品允許進階用戶針對講者語音和企業名詞進行配置和訓練，即使初次完整設定需要超過 5 分鐘；功能設計上不簡化為「一鍵開始」而損失自訂能力

5. 離線轉錄優先，模型可按需下載 — check: 實際的轉錄、講者識別、名詞識別推理運行在 macOS 本地機器，應用可在完全離線狀態下工作；語音模型和名詞模型可選擇從網路下載（因應 App Store app 大小限制），下載完成後本地化存儲後續無需網路

6. 多語言特化優先於通用模型 — check: 支持英文、台灣中文、日文各自的特化語音識別模型（可能來自不同上游引擎或模型），而非單一多語言通用模型；用戶可按會議語言選擇特化模型以獲得最佳準確率

7. 精確的企業內容優先於廣泛的場景涵蓋 — check: 產品優化場景限制在「30 分鐘～2 小時的企業會議」（含線上會議音檔、本地錄音），不擴展到工作坊、演講廳錄音、播客、有背景音樂的內容等其他音訊場景

---

## Design Principles

1. macOS 平台一致性優先 — check: 應用的所有互動模式（按鈕、菜單、窗口行為、鍵盤快捷鍵）必須遵循 Apple Human Interface Guidelines 2025 版本；如發現與 HIG 的偏差，需在 Deviation Ledger 記錄理由

2. 可用性啟發式優先於裝飾 — check: 遵循 Nielsen's 10 Usability Heuristics，特別是「系統可見性」（用戶隨時知道系統狀態）、「錯誤預防與恢復」、「用戶控制與自由」；任何視覺元素或互動都必須直接服務於這些可用性原則，而非為了視覺創意

3. 視覺簡潔性遵循 Apple Design Language — check: 色彩、排版、間距、深度感都遵循 Apple Design Language（Liquid Glass 時代）；限制色彩調色盤（最多 3-4 個語義色）、使用系統字體、透過層級和留白而非裝飾來建立視覺結構

4. 信息層級明確，避免認知過載 — check: 轉錄介面的信息架構必須有清晰的主次層級；任何畫面不超過 3-5 個視覺焦點區域；文案簡潔直接，避免技術術語或冗長說明

5. 滑鼠優先進行導航和標註，文字輸入用鍵盤 — check: 核心工作流程（播放控制、講者標註、逐字稿編輯、名詞庫管理）優先設計為滑鼠操作（點擊、拖拽、選取）；文字輸入欄位用鍵盤自然支持；不要求用戶達到全鍵盤操作的超高效率；滑鼠路徑要直觀，不超過 3 次點擊完成常見操作

---

## Engineering Principles

1. 用戶數據完全本地所有 — check: 核心轉錄、講者標籤、企業名詞庫、用戶修正記錄全部儲存在 macOS 本地檔案系統；應用永不向任何遠端伺服器發送音檔內容或轉錄文本；用戶可檢查檔案系統確認所有數據在本機

2. 模組邊界明確，核心邏輯隔離 — check: 代碼組織為清晰的模組（AudioModule / TranscriptionModule / SpeakerIdentificationModule / NomenclatureModule / UI Module），每個模組有明確的責任邊界；核心邏輯（模型推理、轉錄處理、講者識別）與 SwiftUI 視圖層隔離，便於單元測試和未來重用

3. 最優效能優先，不妥協於可逆性 — check: 關鍵決策（例如：選擇本地 ML 框架、模組邊界設計）一旦決定就要最優化，即使後來改動成本高；開發者接受這個成本作為換取長期效能和穩定性的代價

4. macOS 原生框架優先 — check: 優先使用 Swift 標準庫、SwiftUI、Core ML 等 macOS 原生框架，而非跨平台框架或第三方依賴；模型推理優先考慮 Core ML 或 Create ML，其次才考慮 PyTorch / ONNX Runtime 等

5. 充分測試是打磨基線 — check: 核心模組（轉錄、講者識別、名詞庫匹配）必須有單元測試和集成測試；任何新功能發布前必須在多種會議場景（不同人數、語言、背景音）進行手工驗證；不接受低於 95% 準確率的轉錄發布

6. 架構決策事前參與與事後審計 — check: 架構層級決策（模組分割、框架選擇、API 設計、本地 ML 框架選擇）在決定前提交草案討論和反饋；決定後記錄在設計文檔或代碼註解中，說明 why；進化過程透明且可追蹤

---

## Anchors

| Canon | Pinned version/edition |
| --- | --- |
| Jobs-to-be-Done (JTBD) | Christensen/Ulwick framework, 2003+ (narrative + ODI schools) |
| Kano Model | Kano, Seraku, Takahashi, Shinobu (1984); operational form: Matzler & Hinterhuber 1998 |
| Apple Human Interface Guidelines | 2025 edition (macOS 15) |
| Nielsen's 10 Usability Heuristics | Nielsen Norman Group, 1994 (refined 2020) |
| Apple Design Language | Liquid Glass era (macOS 14+) |
| Local-First Architecture | Ink & Switch / Kleppmann, 2019 (data ownership principle) |
| Modular Monolith | Simon Brown, 2015 (clear module boundaries) |
| Swift / SwiftUI | Apple official architecture MV/MVVM + @Observable, 2023+ (macOS 14+) |
| Core ML | Apple ML framework, current version (for on-device inference) |

---

## Open Questions

**Q3 — Cost Posture（成本立場）：待定**

- **原因：** 「目前缺少詳細資料無法判斷」
- **未決問題：** 月度基礎設施預算上限、超過預算時是否加錢
- **何時決定：** 一旦有實際的模型下載成本、雲端備份需求等具體資料，需要重新評估並補充 Engineering Principles（例如：可能新增「成本約束」原則）
- **當前行動：** v1 假設本地端零成本；如未來擴展（雲端模型倉庫、備份服務）再定策略

此項將在 Engineering Principles 有初步成本數據後重新評估並記錄。
