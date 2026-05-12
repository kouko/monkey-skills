[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# cld-archetypes

輸入一張帶 R/B 註記的 Mermaid 因果迴路圖，辨識它呈現的是哪一個 Sherwood 原型（成長極限的 R+B 耦合，或帶延遲的 B 迴路 V/T/A），並套用對應的介入範本。

## 使用時機

- 投入更多預算或人力，成長率卻在減速，團隊的反射動作是「同一根槓桿再踩深一點」時 — 在加倍預算之前需要先做成長極限診斷。
- 某個 KPI 一季又一季來回擺盪，每次介入反而把振幅拉大時 — 在下一次修正之前需要先做 V/T/A 診斷。
- 因果迴路圖已經畫好（透過 `loop-and-link-primitives` 完成 R/B 分類），需要在選擇介入哲學前先命名原型時。

## 啟動方式

`/systems-thinking-toolkit:archetypes`，或透過路由 `/systems-thinking-toolkit:stt`。

## 產出

- 因果迴路圖上命名好的原型（`limits-to-growth` 或 `V/T/A`），成長極限側附上正在拘束的約束、V/T/A 側附上回饋延遲的估計值。
- 對應的介入規則 — 對拘束的 B 迴路「解除約束」，或讓 B 迴路自行收斂時「整整一個回饋週期都不要動」 — 附上成本、時程與可被否證的預測。
- 指向下游技能的指引（要決定下一根動的槓桿就指向 `strategy-lever-and-cascade`，需要定量驗證就指向 `simulation-modeling`），附加在 `%% Archetype: ...` Mermaid 註解之下。

## 邊界

- 不適用於真正在發散的系統（往無窮大狂奔的惡性 R 迴路） — 在這裡套用「無為而治」是誤判，請退回 `loop-and-link-primitives` 的 R 迴路診斷。
- 不是「先解除約束再說」的免責牌 — 在未確認到底是哪一條 B 迴路在拘束之前就解約束，可能反而加速崩潰（復活節島 ce07 失敗模式）。
- 不適用於尚未達成 PMF 還沒有成長引擎在運轉的情況、一次性不重複的決策、偵測延遲為零的即時控制、或落在管制範圍內的隨機雜訊（請改用 SPC／管制圖工具）。

## 參考

- 完整技能規格：[SKILL.md](SKILL.md)

## 出處

Dennis Sherwood, *Seeing the Forest for the Trees* — 第 6 章（平衡迴路、時間延遲、振盪）、第 8 章（成長極限與解除約束）、第 13 章（汽車經銷商案例的定量驗證）。
