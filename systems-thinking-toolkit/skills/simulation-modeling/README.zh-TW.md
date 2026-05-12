[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# simulation-modeling

把定性 CLD 翻譯成定量的存量流量配管圖，然後用模擬結果學習 — 不是用來做點預測。

## 使用時機

- CLD 已備好量化條件 — 變數已界定、S / O 符號已驗證 — 而你需要數值量，不只是方向。
- 你懷疑有指數陷阱（小漂移複利累積），需要倍增時間對應答延遲診斷，判斷線性外推是否危險地誤導。
- 模型已建好，但團隊把它的輸出當成預測，你需要把模型重新框架為學習工具。

## 啟動方式

`/systems-thinking-toolkit:simulation` 或透過路由器 `/systems-thinking-toolkit:stt`。

## 你會得到

- 從定性 CLD 導出的存量流量配管圖 — 變數依 time-freeze 測試分類成存量 / 流量、偵測 uniflow / biflow、完成 lever→flow 與 outcome→stock 對映。
- 每個 R 迴路都浮現「倍增時間 vs 應答延遲」診斷，並把模擬明確框架為學習產出物（不是預測產出物）。

## 邊界條件

- 不適合做點預測 — 模型揭露的是結構驅動行為；若你把它的數字當預測去承諾，必然失準。
- 不是真實模擬器的替代品 — v0.1.0 只交付翻譯紀律；數值執行得用 Vensim / iThink / Stella / 試算表 / Python（配套腳本延到 v0.2+）。
- 不適合一次性校準 — 學習迴圈比快照重要。資料精煉時要重新跑。

## 參照

- 技能本體規格：[SKILL.md](SKILL.md)

## 來源

Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002) — 第 11 章（stock-flow translation）與第 12 章（models for learning, not answers）。數值系統動力學 Forrester / Sterman / Meadows 譜系。
