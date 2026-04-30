# 4dx-d4-cadence（topic router）

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> D4 週次 cadence 的 topic-router。當 role（solo / leader / member）和 timing（前 / 中 / 後）都不明確時觸發。

## 這個 router 做什麼

捕捉「WIG Session 怎麼跑」這種 role + timing 都沒講清楚的問題，用 Socratic 的 (role, timing) 一問釐清後，分派到 4 個 atomic D4 skill 之一。本身不跑 session protocol。

## 何時觸發

- "Help with my WIG Session" / "Weekly cadence advice" / "WIG Session prep" / "Set up the cadence"
- 「WIG Session のこと」「weekly cadence の運営」「毎週の WIG ミーティング」「週次レビューの相談」
- 「WIG Session 怎麼跑」「每週節奏」「WIG 週會」「每週 review」「weekly 開會」
- 任何 role + timing 沒講清楚的 cadence 詢問

## 不要在這些情境使用

| 情境 | 改去 |
|---|---|
| 「我自己一個人跑 session」 | 直接 `4dx-d4-personal-wig-session` |
| 「我帶團隊跑 session」 | 直接 `4dx-d4-team-wig-session-lead` |
| 「明天 session 我要準備 commitment」 | 直接 `4dx-d4-member-commitment-prep` |
| 「剛開完 session，我這週沒做到」 | 直接 `4dx-d4-member-account-debrief` |
| cadence 已經斷好幾週 | `4dx-sustain-personal-momentum-rescue`（先 rescue 再 restart） |
| 還沒有 WIG / lead / scoreboard | 先做 D1 / D2 / D3，D4 沒東西可跑 |
| sprint review / OKR check-in / 1-on-1 | 4DX 範圍外 — `using-four-dx-coach` |

## 配下的 atomic skill

| Slug | Role | Timing | 產出 |
|---|---|---|---|
| `4dx-d4-personal-wig-session` | Solo（agent = peer-witness） | 進行中 | 20-30 分鐘 Account → Review → Plan，自選 1-2 個 commitment |
| `4dx-d4-team-wig-session-lead` | Team-leader（facilitator） | 進行中 | commitments-not-assignments + veto-not-dictate 規範下的 agenda + Socratic 問句 |
| `4dx-d4-member-commitment-prep` | Team-member | 開會前 | 具體、influenceable、single-step 的 commitment，準備口頭發言 |
| `4dx-d4-member-account-debrief` | Team-member | 開會後 | 誠實 self-account: 達成 / 部分 / 未達 + 診斷（餵回下次 prep） |

## 延伸

- [`SKILL.md`](SKILL.md) 完整 routing logic + Socratic 決策樹 + hand-off scripts
- plugin router [`using-four-dx-coach`](../using-four-dx-coach/) 處理 cold-start / 4DX 範圍外問題
