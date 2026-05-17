# Systems Thinking Toolkit

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> 散文 → CLD 翻譯器 (carry-1) + 6 個下游消費 skill + 1 個 V1-weak 人格輔助 + 1 個 router。以 Dennis Sherwood《Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking》(Nicholas Brealey, 2002) 為基礎，封裝為 monkey-skills 的 `systems-thinking-toolkit` plugin。

## 包含 skill

| Slug | 角色 | 描述 |
|---|---|---|
| `cld-craft` | Carry-1 producer | 散文 → 完整註記的 Mermaid CLD（12 條 hygiene 規則 + Rule 7 模糊變數提升 + S/O signing + R/B classification，全部集中在 Step 11） |
| `cld-archetypes` | CLD consumer | 辨識 limits-to-growth (R+B coupling) 或 V/T/A (帶 delay 的 B-loop) 原型 + 對應介入 playbook（Branch L + Branch V） |
| `cld-overlay` | CLD consumer | 多 stakeholder CLD 疊加 + straddle-policy 抽取（對外衝突調解） |
| `team-mental-model` | CLD consumer | 心智模型和諧 + 4 個可觀察的 leadership-energy proxy（cadence / active-listening / value-revisitation / symbol-narrative）— 對內團隊 protocol |
| `simulation-modeling` | CLD extension | 純文字 CLD → stock-and-flow 轉換 + 「為學習而非預測而建模」紀律 |
| `strategy-lever-and-cascade` | Non-CLD strategy | lever 對 outcome 重塑 + 三時程 cascade + 3×N 情境表（v0.6 把 Martian-test perturbation 內嵌進 Step 5） |
| `manager-personality-quadrant` ⚠ V1-weak | Auxiliary | framing 對 analysis 分割 + Gods/Gamblers/Grinders/Guides 2×2；**僅作 facilitation vocabulary**（v0.6 強化 Boundary）；任何牽涉到人事的用途，DiSC / Big Five / Hogan 等都是更強的替代 |
| `using-systems-thinking-toolkit` | Entry / router | 意圖不明時的路由 |

## 為什麼有這個 plugin

**Carry-1 命題**：系統思考的價值絕大多數集中在上游翻譯這一步 — 把雜亂的散文轉成結構化的 causal loop diagram (CLD)。這正是 LLM 對人類優勢最大的步驟（在幾秒內把糾結的敘事拆成 nodes / links / signed loops）；而下游應用（工作坊、模擬、決策）反而是 LLM 相對弱項。所以這個 plugin 刻意把重心壓在上游這一步。

Sherwood 的操作貢獻全部集中在 `cld-craft`：12 條 hygiene 規則、Rule 7 模糊變數提升、S/O link signing、R/B 迴路分類 — 全部整合進 Step 11。輸出是完整註記的 Mermaid CLD，可讀、可分類、可直接交給任何下游消費 skill。

下游 skill（cld-archetypes / cld-overlay / team-mental-model / simulation-modeling）消費 `cld-craft` 產出的分類 CLD。`strategy-lever-and-cascade` 是唯一一個非 CLD skill — 處理 strategic reframe 系的動作（lever 對 outcome / cascade / scenarios），並包含 v0.6 吸收進來的 Martian-test perturbation。`manager-personality-quadrant` 保留下來但僅作 facilitation vocabulary — 真要做人事相關工作，應該轉去 Big Five / Hogan / DiSC / Hofstede 等。

## 怎麼用

1. 不確定要叫哪個 skill？用 `/systems-thinking-toolkit:using-systems-thinking-toolkit` 走意圖路由。
2. 有散文 / vicious cycle / death spiral 這類語言？直接呼叫 `/systems-thinking-toolkit:cld-craft`。
3. 已經有 CLD 了？看 `/stt` 內「I have a CLD — now what?」段落分流到 archetypes / overlay / simulation。
4. 在做策略 / 團隊作業？看 `/strategy-lever-and-cascade` 或 `/team-mental-model`。
5. 想系統性學習？依照 [`INDEX.md`](INDEX.md) 的順序 — 從 `cld-craft` 開始。

## 來源與限制

- 透過 `tsundoku:book-distill` RIA-TV++ pipeline 蒸餾（Adler → 5 並行抽取 → 三重驗證 → RIA++ 渲染 → Zettelkasten 連結 → 對抗性壓力測試）
- 原 14-skill Stage-3 蒸餾經 v0.4 R3 restructure + v0.6 sk13 吸收後整合為 7 機能 + 1 router（無內容流失；原 14 skill body 都可從整合後位置回溯 — 見 [`INDEX.md`](INDEX.md) 的對應表）
- V1-weak skill 剩 1 個：`manager-personality-quadrant`。v0.6 已強化為「僅作 facilitation vocabulary」的 Boundary；其 "Graduate beyond" 表把任何牽涉到人事的用途路由到 Big Five (NEO-PI-R) / Hogan / Heifetz / Edmondson / Klein / Hofstede / Tuckman / Lencioni
- Stage-0 (`BOOK_OVERVIEW.md`) / Stage-1.5 (`VERIFIED.md`) / Stage-3 原版 (`INDEX-original.md`) 稽核軌跡見 [`references/`](references/)
- v0.7+ 候選見 [`ROADMAP.md`](ROADMAP.md)
- 對原著的涵蓋度稽核（方法論 ~85% + 例示資料 ~70%）見 `docs/superpowers/audits/2026-05-13-systems-thinking-toolkit-vs-original-book.md`

## 授權

MIT
