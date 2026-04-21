# Apply-Rewrite Findings — Does the anchor actually change the draft?

**Date**: 2026-04-21
**Scope**: 2 briefs × 2 arms (baseline no-anchor vs anchor-applied), agent rewrites draft (not just rationale).

This follow-up empirical test answers the gap raised after the first 4 tests — those only verified that **rationale** cited native vocab, not that the **draft itself** changed register.

---

## Method

Both arms run Phase 6 on identical envelope + identical Phase 4 draft. Only difference:

- **Baseline**: Pass 1 + Pass 2 only. No Pass 3. No anchor file read. Agent trusts general Q3 sensibility.
- **Applied**: Pass 1 + Pass 2 + Pass 3 Register Signal. Load anchor file. Apply anchor's Voice signature to rewrite.

---

## Brief A — zh-TW Q3 center — 老蘇打古早味汽水

### Original Phase 4 draft
> 阿嬤家的冰箱，最下層永遠有一瓶冰冰的汽水。不是什麼特別的日子，就是想喝。現在長大了，走進便利商店還是會找那個熟悉的瓶身。老味道沒有變，變的是我們。但喝下去的那一口，還是把我們拉回小時候那個熱得要命的下午。

### Arm A1 — Baseline (no anchor)
> 阿嬤家的冰箱，最下層永遠冰著一瓶汽水。不是什麼特別的日子，就是想喝。現在自己出門在外，走進便利商店，手還是會往那個熟悉的瓶身伸過去。不是懷舊，也不是要回到小時候。是今天加班完的晚上、是下班騎車回家的紅綠燈、是週末睡到中午的那杯。熱到受不了的下午還在過，阿嬤冰的那瓶汽水，我們自己接著冰。

### Arm A2 — Applied (全聯 格言體 primary + 糸井 cross-ref + 吳念真 stance)
> 阿嬤家的冰箱，最下層永遠冰著一瓶汽水。沒什麼特別的日子，就是想喝。長大以後走進便利商店，還是會繞去找那個熟悉的瓶身。味道沒有變，變的是我們；但那口氣吞下去，玻璃瓶口的涼、後頸的汗，還是把人拉回放學路上那個沒什麼煩惱的下午。古早味不是懷舊，是我們今天還在過的日常。

### Shape delta
- A2 加入身體感官（玻璃瓶口的涼、後頸的汗） vs A1 靠時間列舉
- A2 保留並強化對仗（不是X是Y），thesis 直接收尾為 state-proposal
- 動詞更台味（繞去找、那口氣吞下去）vs A1 較平實
- **但 A2 引入 thesis conflict**:「放學路上沒什麼煩惱的下午」是懷舊 frame，thesis「不是懷舊」被 anchor register 拉回來
- A1 反而更徹底對齊 thesis（列舉今天的情境）

**Verdict**: anchor 提供了 discipline（身體感 + 對仗），但引入了 thesis 漂移 bug。Shape 接近、差異在細節層。

---

## Brief B — JP Q3 center — 伊藤園お茶

### Original Phase 4 draft
> 朝、まだ誰も起きていないキッチンで、お湯を沸かす音だけが聞こえる。いつもの急須、いつもの茶葉。忙しい一日が始まる前の、たった五分間。お茶を淹れる時間は、一日のうちで一番静かな時間かもしれない。家族が起きてきて、それぞれのマグカップに注ぐとき、この五分間が家族みんなの朝を支えていることを思い出す。

### Arm B1 — Baseline (no anchor)
> 朝、まだ誰も起きていないキッチンで、お湯を沸かす音だけが聞こえる。いつもの急須、いつもの茶葉。一日が動き出す前の、五分間。お茶を淹れる時間は、一日のうちでいちばん静かな時間かもしれない。やがて家族が起きてきて、それぞれのマグカップに注ぐ。湯気の向こうに、それぞれの朝がある。お茶のある風景は、いつのまにか、家族の風景になっていく。

### Arm B2 — Applied (向田邦子 真打ち随筆 anchor)
> まだ誰も起きてこない台所。やかんの音だけがする。いつもの急須、いつもの茶葉。湯を注ぐ。立ちのぼる湯気。五分。やがて階段の音、冷蔵庫を開ける音、眠そうな声。それぞれのマグカップに、少しずつ注ぎ分ける。湯気の向こうで、夫がひとくち。娘が両手で包む。息子はまだ半分眠っている。朝のお茶は、家族の風景の一部になっている。

### Shape delta — 明顯顯著
- B2 完全刪除「一日のうちで一番静かな時間かもしれない」（心理推量）— 向田「心理描写を省く」rule
- 「忙しい一日が始まる前の、たった五分間」（説明句）→「湯を注ぐ。立ちのぼる湯気。五分。」（動作 + 体言止め chain）
- 具體動作枚舉大幅增加：階段の音、冷蔵庫を開ける音、眠そうな声、夫がひとくち、娘が両手で包む、息子はまだ半分眠っている
- 文末從「〜を思い出す」（內省）→「〜になっている」（觀察）
- B2 讀起來像向田邦子散文節奏；B1 讀起來像一般溫暖廣告文

**Verdict**: anchor shape 影響**強**。ROI 明顯值得。

---

## Cross-brief 結論

| 面向 | zh-TW Q3 center | JP Q3 center |
|---|---|---|
| Shape 改變幅度 | 細節層 | 結構層 |
| Anchor signature distinctive? | 否（Q3 peer-warm generic） | 是（向田 ト書き register 高度特異） |
| Thesis conflict risk | ⚠️ 出現（懷舊 re-intro） | 未觀察到 |
| 無 anchor baseline 品質 | 已可用（Q3 sensibility 預設夠） | 平庸（缺 discipline） |
| Anchor ROI | 低 | 高 |

**一般規律（hypothesis）**：
- Anchor ROI 與該 register 的 **distinctiveness** 正相關
- High-distinctive anchors（向田邦子 / 許舜英 / 王家衛 / 糸井 state-proposal）→ anchor 注入明顯
- Generic center anchors（Q3 peer-warm、Q4 peer-helpful 通用）→ anchor 邊際收益低
- **Thesis drift 風險 與 anchor register 強度 正相關** — 越強的 anchor 越容易把 draft 拉向 register-canonical imagery，忽視 thesis 特殊訴求

---

## 直接產出的 actions（併入此輪 commit）

1. **Dimension 7 — Thesis Alignment**（新增至 `rubrics/voice-consistency-gate.md`）— 專門抓 anchor-induced thesis drift（如 A2 的「懷舊」bug）
2. 此 findings doc 留作 empirical baseline，未來 anchor 改版可回跑同 brief 看 regression

---

## 未解 / 下一輪可測

- Q2 craft-gate（許舜英 / 李欣頻）apply-rewrite 的 ROI 是否高於 Q3 Register Signal？（hypothesis：high，因為 Q2 craft-gate register distinctive）
- Q4 helpful-practical anchor ROI？
- Native reviewer 盲評 — 真 TW/JP copywriter 看 A1 vs A2、B1 vs B2 哪個更 fit brief？（本輪未做）
- Anchor skip-optimization for registers where LLM baseline already covers（需先做 Tier 1 自動化評估 pipeline；v1.3.5 stub 已於 v1.3.6 reverted 為 premature optimization）
