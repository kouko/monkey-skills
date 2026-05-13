# Systems Thinking Toolkit

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

9 個從 Dennis Sherwood《Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking》（Nicholas Brealey, 2002）萃取的系統思考 skill，封裝為 monkey-skills 的 `systems-thinking-toolkit` plugin。

## 包含的 skill

| Skill | 用途 |
|---|---|
| `using-systems-thinking-toolkit` | 依情境路由到最佳方法 |
| `loop-and-link-primitives` | 基礎：R/B 迴路診斷 + S/O 連結標記 (sk01+sk02) |
| `cld-craft` | 以工作坊紀律繪製因果迴路圖 — 12 規則 + 模糊變數提升 (sk03+sk04) |
| `limits-to-growth-take-the-brakes-off` | R 迴路被 B 迴路煞住的原型；解除約束而非踩油門 (sk05) |
| `variance-target-action-template` | 通用 B 迴路控制模板 + 振盪時的「不作為」診斷 (sk06) |
| `strategy-lever-and-cascade` | 槓桿對結果重塑 + 三時程瀑布 + 3×N 情境規劃 (sk07+sk08) |
| `stakeholder-and-team-thinking` | 多視角 CLD 疊加 + 心智模型和諧 (sk09+sk10) |
| `simulation-modeling` | 存量流量轉換 + 「為學習而非預測而建模」紀律 (sk11+sk12) |
| `manager-personality-quadrant` ⚠ V1-weak | 主管人格 2×2；**v0.6 強化「僅作 facilitation vocabulary」邊界**；DiSC / Big Five / Hogan 為更強的替代品（人事相關用途絕對不要用本 skill） |

> v0.6 把 `innovaction-martian-test` 吸收進 `strategy-lever-and-cascade` Step 5（Martian-test 特徵擾動），單獨 skill 已廢止。
> 注：本 README 上方表格仍含 v0.4 之前的舊 skill 名。v0.7 規劃完整 v0.6 同步 rewrite。

## 為什麼有這個 plugin

系統思考不只是畫圖 — 它是診斷**結構**而非歸咎於**事件**的紀律。Sherwood 的貢獻是操作層面：因果迴路圖可以化約為兩種迴路類型（強化型 / 平衡型），用 O 的數量分類，virtuous 與 vicious 的旋轉方向由同一結構驅動。本 plugin 把他著作中面向經理人的部分蒸餾為 9 個原子化、可組合的 skill。

從原 14 個 Stage-3 蒸餾用 Profile-B 合併而成。5 個 compose-with 配對合併為單一 skill（保留 source-unit 引用軌跡），4 個保持獨立（sk05/sk06 在認知框架層次相對；sk13/sk14 V1-weak 依 user override 保留，待 v0.2 重新評估）。

## 怎麼用

1. 不確定該用哪個 skill？用 `/systems-thinking-toolkit:stt` 透過意圖表路由。
2. 已知情境？直接用 per-skill 命令（完整清單見 [`INDEX.md`](INDEX.md)）。
3. 想系統性學習？跟隨 [`INDEX.md`](INDEX.md) 的推薦學習順序 — 從 `loop-and-link-primitives` 開始。

## 來源與限制

- 用 `tsundoku:book-distill` RIA-TV++ pipeline 蒸餾（Adler → 5 並行抽取 → 三重驗證 → RIA++ 渲染 → Zettelkasten 連結 → 對抗性壓力測試）
- 原 14 Stage-3 skill 用 Profile-B 合併為 9 個（5 個 compose-with 配對 + 4 個獨立）
- V1-weak skill 剩 1 個（`manager-personality-quadrant`）。v0.6 強化「僅作 facilitation vocabulary」邊界。`innovaction-martian-test` 已於 v0.6 吸收進 `strategy-lever-and-cascade` Step 5。人格相關更強的先驗技術：DiSC, Big Five (NEO-PI-R), Hogan, Situational Leadership。
- Stage-0 (`BOOK_OVERVIEW.md`) / Stage-1.5 (`VERIFIED.md`) / Stage-3 原版 (`INDEX-original.md`) 稽核軌跡見 [`references/`](references/)
- v0.7+ 候選（PR #271 audit 的 6 件 body fix；CI 檢查 desc ↔ skill folder 漂移；stock-flow 模擬 Python 配套；Edmondson teaming-safety hand-off）見 [`ROADMAP.md`](ROADMAP.md)

## 授權

MIT
