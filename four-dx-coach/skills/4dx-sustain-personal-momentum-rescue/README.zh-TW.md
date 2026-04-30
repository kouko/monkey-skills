# 4DX Sustain & Momentum Rescue

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 診斷四 discipline stack 實際是在哪一層斷掉（D1 / D2 / D3 / D4 / whirlwind / substrate），然後 route 到對應的 restart，而不是叫使用者「再努力一次」。

## 何時觸發這個 skill

- 「我的 4DX 已經幾週沒做了」「lost momentum on my goal」「WIG session 都沒在開」
- 「scoreboard 看了空虛」「我一直記但沒變化」
- 「我覺得自己沒紀律」「想重啟但不知道從哪開始」
- lead measure 之前有一段時間在記，但 lag 一直不動，使用者結論「這目標根本不可能」
- lead 達成率 90%+ 但已經對 WIG 沒感覺了 — 這個 goal 對我已經不再「wildly important」
- 真的有外部負荷尖峰（換工作 / 生病 / 家裡的事）把 WIG 擠出去，使用者現在在自責「沒紀律」

## 它做什麼（protocol 摘要）

非評判式的 Socratic 對話，倒著走整個 stack；每一步定位破損層並 route。**不會在壞掉的上游層上面重啟 D4**：

1. **不評判地打開話題** — 「cadence 是什麼時候開始斷的？那時候你的生活在發生什麼？」
2. **D1 — WIG 自己現在還算 wildly important 嗎？** — 不是就 route 去 `4dx-d1-wig-formulation`，不要在死掉的 WIG 上面重啟 D4
3. **D2 — lead** — 它真的同時 predictive 且 influenceable 嗎？lead 綠但 lag 平 = lead 選錯，route 去 `4dx-d2-lead-measures`
4. **D3 — scoreboard** — 5 秒看得出勝負嗎？被收起來 / 變成 coach's-style 了 → route 去 `4dx-d3-scoreboard`
5. **D4 — cadence** — 是什麼把 session 擠掉？覺得「沒意義」= 上游有問題（回到 D1-3）；whirlwind 把它擠掉 = 下週直接 resume（不補課）
6. **whirlwind 升級 check** — 真的有外部負荷尖峰嗎？有的話 route 到 `4dx-d1-personal-whirlwind-triage` 重設容量，或者明確 pause WIG（明確的 pause 不算失敗）
7. **substrate check（off-ramp）** — burnout / 憂鬱 / 哀悼 / 長期過勞 → 停止 4DX rescue，建議休息 / 諮商 / 治療
8. **不羞辱地 recognition** — 在這次中斷前，使用者 *確實* 做到的事，具體列 1-3 件（不要套公式式的「你好棒」）
9. **以最小 scope 再 commitment** — *don't skip, don't catch up*。是 resume 不是 repair。下個 7 天就一個小 commitment

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| 第一次 setup 4DX | `4dx-meta-strategy-triage` → `4dx-d1-wig-formulation` |
| 組織級 engagement survey / 企業診斷 | scope 之外，這個 skill 是個人尺度的 rescue |
| 臨床憂鬱 / 長期 burnout / 哀悼 | 找專業支援；method 在 care 的下游 |
| reactive / 緊急應變領域，whirlwind 本身就是工作 | 改去 `4dx-d1-personal-whirlwind-triage`。cadence 中斷未必是問題 |

## 出處

蒸餾自 *The 4 Disciplines of Execution* 第 10 章「Sustaining 4DX Results and Engagement」+ 結尾「The Missing Ingredient」。四個 anchor case：Store 334（單純加上 D4 就把垂死的 D1-3 救起來）、Stengel 在北京 2 AM 開 WIG Session（cadence-sacred 本身就是領導信號）、Mike Crisafulli（拒絕承認解釋不了的勝利 — 謙虛當作診斷紀律）、Susan / Bianca / Marcus（不指責的 accountability 對話）。

完整 RIA++ 渲染（含 catch-up trap、Marcus pattern（operator 把 architect 劫持了）、誠實承認「這個季節 4DX 根本不對」的 substrate off-ramp）見 [`SKILL.md`](SKILL.md)。
