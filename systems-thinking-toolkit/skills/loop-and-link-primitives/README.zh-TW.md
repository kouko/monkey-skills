# Loop-and-Link Primitives — R/B 判別 + S/O 鏈結符號標註

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

先以可逆性測試與 Sterman 終極檢定為後備，為每條因果箭頭標註 S/O 符號，再沿閉合迴路數 O 的個數，將迴路分類為 R 或 B。

## 適用時機

- 從零繪製因果迴路圖，每條箭頭都會卡在「這是 S 還是 O」的判斷上
- KPI（NPS、留存率、股價）緩慢漂移或非線性加速，懷疑背後存在回饋迴路
- 出現「惡性循環」「死亡螺旋」「泡沫」等說法，需要診斷目前的旋轉方向與反轉觸發點
- 變異 KPI（目標 vs 實際）的定義被改寫，既有圖上的標籤可能在無人察覺下變成錯誤

## 呼叫方式

`/systems-thinking-toolkit:link-primitives`

或透過路由器：`/systems-thinking-toolkit:stt`

## 產出

- 每條鏈結的 S 或 O 標籤，附可逆性 / Sterman 檢定紀錄，單向流（uniflow）情況特別標示
- 每個迴路的 R（O 數為偶數，含 0）或 B（O 數為奇數）分類；R 標出當前旋轉方向 + 可信的反轉觸發點，B 標出目標 + 延遲量級
- 一句話的動態預測（例：「目前為良性旋轉的 R 迴路；除非觸發 X，否則將持續複利成長」）

## 邊界

- 不適用於沒有閉合回饋的單次決策（偶數 O / 奇數 O 規則無定義）
- 不適用於純統計相關性的標註（未主張因果方向），也不適用於因果推論用的 DAG 邊（依設計就不帶符號）
- 體制依存的鏈結（在閾值處符號翻轉）應交給 `cld-craft` 的 split-fuzzy-variable 技巧處理 — 不要硬挑單一標籤

完整流程（R/I/A1/A2/E/B）請見 [SKILL.md](SKILL.md)。

## 來源

Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002)，第 4、5、6、12 章。
