# Example research note (obsidian-research)

One finished note, shown to illustrate the checkpoints in SKILL.md Step 5. It is **not** a structure to copy: the chapters here follow this topic's dimensions (a market topic with a comparison), and another topic would get different chapters. Heading style follows the vault's recent notes (plain, numbered); a vault with a different style gets that style. The claims, figures, and URLs are placeholders, not research results, and the chapters and source list are abbreviated (`…`).

Topic leaning: a Taiwan market → 繁中 primary + English + 日本語. The user wrote in 繁中, so the note is in 繁中.

````markdown
---
title: 台灣電動機車換電網路的普及現況
type: research
date: 2026-09-23
tags:
  - research
  - electric-scooter
  - taiwan
status: completed
source_count: 11
source_languages: [zh-TW, en, ja]
---

# 台灣電動機車換電網路的普及現況

> 📌 換電網路在都會區已足以支撐日常通勤，但補助退場後的新車銷量是未來兩年的主要變數。

換電站密度在六都已高於一般通勤距離所需 [1][3]。成長放緩的主因是購車補助縮減，而不是站點不足 [2][5]。日本同類服務仍在試點規模，可參考之處有限 [8]。

## 目錄

- [[#一、市場規模與站點密度|市場規模與站點密度]]
- [[#二、補助政策與銷量|補助與銷量]]
- [[#三、與日本換電試點的比較|台日比較]]
- [[#四、分歧與未定論|分歧與未定論]]
- [[#五、研究方法與限制|研究方法與限制]]
- [[#六、建議與後續行動|建議]]
- [[#來源清單|來源清單]]

## 一、市場規模與站點密度

- 六都平均每 1 km² 有 X 座換電站 [1][3] — **信心度 High**（官方統計與業者公告一致，反向查證未找到反例）
- 偏鄉覆蓋仍有缺口 [4] — **信心度 Medium**（只有一份地方新聞）

## 二、補助政策與銷量

- 購車補助自 20XX 年起逐年縮減 [2] — **信心度 High**（官方公告，反向查證確認現行）
- 補助縮減後新車銷量連續兩季下滑 [5][6] — **信心度 Medium**（兩份來源統計口徑不同）

## 三、與日本換電試點的比較

| 維度 | 台灣 | 日本 |
|---|---|---|
| 規模 | 全國商用 [1] | 城市試點 [8][9] |
| 主導者 | 單一業者為主 [3] | 車廠聯盟 [8] |
| 主要障礙 | 補助退場 [5] | 法規與停車空間 [9] |

## 四、分歧與未定論

- 市占數字：業者公告與第三方調查相差約 N 個百分點 [3][6]，差異來自統計口徑
- 已查證為過時：「換電站數量將於 2025 年翻倍」的說法 [7]，實際成長未達此數
- 未定論：電池標準是否統一，目前沒有可信來源給出時程

## 五、研究方法與限制

- 章節結構：依主題面向（市場定義 → 規模 → 結構 → 驅動與風險）
- 研究角度：站點、補助、營運商、使用者評價、日本比較；缺口檢查補上「時間」（補助退場時程）
- 查證：關鍵說法 9 條，被推翻或過時 1 條
- 三種語言都有搜尋；日文來源只有試點新聞，缺乏使用數據
- 業者自身公告占來源的三成，可能偏向樂觀
- 補助政策每年調整，數字以存取日期為準

## 六、建議與後續行動

- [ ] 若評估購車：先查通勤路線上的站點分布，再看當年度補助
- [ ] 明年補助公告後重新確認銷量段落

這些建議依賴的假設：補助在明年仍存在；站點密度維持現況。最可能出錯的原因：營運商財務狀況惡化導致站點縮減。

## 來源清單

1. 電動機車換電站統計 — 交通部 — https://example.com/1 — zh-TW — accessed 2026-09-23
2. …
8. 電動バイク電池交換の実証事業 — 経済産業省 — https://example.com/8 — ja — accessed 2026-09-23
````
