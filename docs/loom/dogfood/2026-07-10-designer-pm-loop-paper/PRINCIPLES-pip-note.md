# PRINCIPLES.md — PIP 陪跑便條（paper-dogfood 產出工件）

> Produced 2026-07-10 by the paper dogfood of the PRINCIPLES construction
> flow (`instrument.md` in this folder). Language: Traditional Chinese —
> the artifact was authored in the session's conversation language; a real
> product repo would set its own convention. All content passed per-section
> read-back + final total read-back with the user.

## 北極星

陪跑便條——當你在其他 app 全螢幕工作時，常用的指令、片段、資訊隨時在手邊、一瞬可及。

## 錨定（釘版本）

| 層 | 錨 | 版本釘 |
|---|---|---|
| 範圍紀律 | Shape Up appetite 概念 | Basecamp, *Shape Up*, 2019 版 |
| 投資分配語彙 | Kano 品質分類 | 狩野紀昭, 1984 |
| 互動身分哲學 | Calm Technology | Case 原則版, 2015 |
| 平台規範 | Apple HIG | Liquid Glass 世代（OS 26, 2025-26） |
| 互動定律工具箱 | Laws of UX | Yablonski, 活文件（設計階段逐條引用） |
| 視覺哲學 | 原研哉「空」 | 《白》2008 系譜 |
| 排印操作規範 | 瑞士字體排印傳統＋Bringhurst | *The Elements of Typographic Style*, 4th ed., 2012 |
| 工程升級判準 | Two-way door 決策框架 | Bezos, 2015 股東信 |

## Product 原則

1. **PIP 是存在理由，不是賣點。** 類 PIP 陪跑顯示的品質高於一切其他投資；任何功能與 PIP 體驗衝突時，PIP 贏。做不好 PIP，產品不出貨。
2. **顯示純淨 > 編輯方便。** 版面永遠留給內容；為編輯方便而常駐的 UI 一律拒絕。瞬態輔助（自動完成）合法。已用這條犧牲掉：GUI 表格編輯、GUI mermaid 編輯——永不回頭。
3. **理所當然品質，及格即止**（Kano）。iCloud 原生同步（不自建同步、不自建伺服器）、Bear 同級效能、markdown 高相容（表格＋code 上色＋mermaid 預覽）——達到業界及格線後停止投資，預算集中到原則 1。
4. **每個功能先定胃口**（Shape Up）。塞不下砍範圍，不加時間、不加複雜度。目前胃口為零：提醒/通知系統、GUI 編輯、知識庫級組織（標籤、反向連結、全文檢索之外的檢索）。
5. **捕捉，不提醒。** 對 Reminders 的取代只發生在捕捉入口；提醒機能封存。再議條件：捕捉上線後，使用者本人仍持續回 Reminders 設提醒時。
6. **規模上限是特性，不是缺陷。** 定位介於便條紙與簡單筆記本之間；數百張卡以上的組織需求明文不是本產品的工作。資料夾樹允許但刻意淺（深度上限於設計階段定案）。
7. **成功＝你自己換掉它們。** 成功訊號：日常真實地以本產品取代 Bear 與 Reminders 的捕捉用途。失敗訊號：回流 Bear/Obsidian 記臨時便條。商業形狀（低價買斷或最低訂閱、App Store 標準）服務於此，不反過來驅動功能。

## Design 原則

1. **住在注意力的邊緣**（Calm Tech）。PIP 永不搶焦點、永不彈出、永不發通知；使用者召喚才進入中心，用完即退。任何主動吸引注意的設計提案，預設違憲。
2. **語法即介面。** 鍵盤是第一輸入裝置；樣式一律由 markdown 語法產生，輔以 IDE 級自動完成（瞬態、可關閉）；顯示端 inline 即時渲染。
3. **容器不說話**（原研哉）。UI 文字與圖標降到可用性底線；最大面積永遠屬於便條內容。曖昧與明確衝突時，無障礙底線（Design 7）裁決。
4. **視覺系統＝字體排印**（瑞士傳統全收——客觀冷靜的工具氣質）。標題階層、表格、code block、行距節奏是視覺設計的全部主體；design token 從字階與間距節奏（8pt 網格）推導，不從裝飾推導。
5. **平台角色不對稱，能力不閹割。** macOS 是完整編輯器；iOS/iPadOS 以查看＋輕量捕捉為第一目的，但完整編輯能力必須存在——效率可受硬體限制，能力不允許移除。
6. **內容面不透明，控件可玻璃。** PIP 視窗內容背景一律不透明；視窗內部控件可採 Liquid Glass 材質。
7. **無障礙是理所當然品質。** VoiceOver 標籤、對比度、觸控目標尺寸依 HIG＋WCAG 2.2 達標——及格即止，但必須及格。

## Engineering 原則

1. **學習優先，出貨是閘門。** 自用期以驗證速度為先，粗糙合法；上架 App Store 是穩健性關卡（完整測試＋商店級打磨），不是日常開發標準。
2. **可逆優先。** agent 工程預設：在「可逆但次佳」與「最佳但承諾」之間選可逆；單向門是例外，必須浮上開工簡報。
3. **零伺服器、零月費結構。** 同步走使用者自己的 iCloud（CloudKit 私有庫）；任何需要伺服器的未來功能自動觸發開工簡報，不得默默引入。
4. **零收集。** 筆記只存在使用者的 iCloud 私有庫；無分析、無遙測、無第三方 SDK；崩潰報告僅用 Apple 內建 opt-in 機制。
5. **升級口味＝只看開工簡報。** 單向門決策（含「使用者感覺不到但難逆」類）批次上桌；其餘 agent 自決＋留產品語言決策日誌，可事後翻案。
6. **Tech stack（單向門，明文聲明）**：原生 Swift/SwiftUI；CloudKit 系同步（具體持久層方案屬 agent 裁量）；WidgetKit；PIP 浮窗視窗層級控制走 AppKit 級 API。鎖定理由：Product 1——類 PIP 品質與 Bear 級效能排除跨平台框架。

## 偏離帳本

| # | 偏離 | 理由 |
|---|---|---|
| D1 | Kano 會把 PIP 歸「魅力品質」，本產品抬到「存在理由」層級 | Product 1——PIP 是唯一結構性差異，非錦上添花 |
| D2 | Shape Up 只取 appetite 紀律，不採 betting table／六週週期 | 獨立開發無組織可對齊，制度部分 N/A |
| D3 | HIG Liquid Glass 世代以半透明材質為視窗預設，本產品內容面改不透明 | Design 6／Product 2——文字可讀性讓渡不得；內部控件採 LG 作為對平台的讓步 |
| D4 | HIG 預設標準控件與工具列，本產品近零 chrome | Design 3——「空」哲學；衝突時無障礙底線優先 |

（D5 曾提案「瑞士客觀性不全收、對標 Bear 親和感」——使用者裁決刪除，瑞士傳統全收。記錄於 report FINDING-04。）
