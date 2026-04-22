---
slug: zh-tw-li-xu-stylistic-siblings-analysis
status: research-only
type: cross-anchor-analysis (not single-candidate)
date: 2026-04-22
---

# Research Note: 李欣頻 ↔ 許舜英 Stylistic-Sibling Substitute Analysis

## Question

在 v2 anchor schema 下，`anchor-zh-tw-xu-shunying-ideological-definitional.md` 與 `anchor-zh-tw-lee-hsin-ping-literary-consumption.md` 是否任一方向可以宣告為對方的 `safe_substitute_for`？若不行，是否仍存在 v1.11.1 引入的 `tone_cue contamination upgrade` 類型的書面關係，應在 library 中明文記錄，而非維持目前的 silent reject 狀態？

v1.11.0 Phase C sweep 的 reject rationale（「both HIGH risk, mechanism-distinct」）太短，無法阻止未來 researcher 再度提案同一 pairing。v1.11.2 要求更深入的機制比對，並以三個選項收斂：Option V1（confirm reject with clearer doc）／Option V2（增列 cross-reference 欄位）／Option V3（識別出特定方向性 substitute case）。

## What was investigated

1. 兩個 anchor 檔案全文（voice direction / native critical read / prose mechanics / examples / don't-over-mimic / metadata）
2. `voice-anchor-meta-core.md §Safe-substitute lookup` 與 §Condition 5 (negation-of-axis) — 確認 v1.11.1 substitute 合格判準 = 「substitute 的 over-mimic risk 必須『嚴格低於』named master」
3. `docs/anchor-schema-v2.md §Safe substitute for` — 確認欄位只接受 frontmatter 陣列，且需通過三個 conditions（higher-risk 入 registry / 經驗證 adjacent / 嚴格低 risk）
4. 兩者 Over-mimic risk 都在 anchor body 標為 HIGH（許 line 49 `Over-mimic risk: HIGH`；李 line 49 `Over-mimic risk: MEDIUM` — **此處有一個關鍵 finding，見下**）

**關鍵發現**：原 prompt 斷言兩者皆為 HIGH-risk，但實際 anchor 檔案裡**李欣頻標為 MEDIUM，許舜英標為 HIGH**。這改變了 verdict 的邏輯前提，必須先處理此差異才能繼續討論 substitute 可行性。

## Findings: shared mechanics / differentiating mechanics

### 共享機制（why they read as 姊妹 register）

- **1990s 意識形態廣告/誠品一脈的 zh-TW Q2 center 文化批評傳統**：兩人皆以 commercial copy 為載體，輸送非 commercial payload（文化／存在主義／權力結構）
- **具名文化座標承重**：許用「梅蘭芳 / 寺山修司 / 港式素蠔油 / 祖母衣櫃」；李用「寺山修司 / 阿莫多瓦 / 徐四金 / 村上春樹 / 彼得梅爾」。兩者共用寺山修司，都把具名人物當讀者—作者對等關係的入場券
- **拒絕泛稱、拒絕 CTA 動詞、拒絕可愛化/驚嘆/emoji-adjacent 語氣**：兩 anchor 的 prose mechanics 第 3-4 條互為鏡像
- **句尾落在名詞/抽象概念**：皆明文禁用買/選/試/享作 closer
- **女性主義／商品即意識形態 傾向**：許有「女性主義就是失敗在愛情和衣服」；李在誠品 copy 承接波希米亞式女性閱讀主體

### 差異機制（why they fail each other's failure mode）

| 向度 | 許舜英 | 李欣頻 |
|---|---|---|
| 脊骨句型 | `X 是一種 Y` definitional inversion（一篇恰一次） | 排比枚舉 ≥4 項具名文化座標（一篇一組） |
| 權力語彙 | **強制** 政治/統治/殖民/禁慾/失敗/危險/虛妄 任一（缺即偽作） | 無此要求；用繁衍/別戀/拋開/遇見承擔情感，非 power-disparity |
| 與前文本的關係 | 具名文化座標當權力語彙的載體 | **強制** 與 antecedent work 對話（寺山修司 1967 是骨幹） |
| 結構 | assertion → inversion → coda（單一 assertion 即 hollow） | 命題宇宙（所有/每一/在…之間）→ 枚舉 → 名詞詞組封結 |
| 呼吸 | 整句 declarative、、和。chain | 排比 parallelism 的 beat-count test（抽名節奏壞則退回） |
| Payload | 文化批判／權力倒置 | 存在主義式生活命題／識別信號 |

### Over-mimic failure mode 交叉污染分析

- **許舜英 failure mode**：空洞箴言反轉（「咖啡就是一種生活」「旅行是一種態度」）＋ 具名座標被泛化成「書／音樂」＋ 只寫 assertion 不 inversion
- **李欣頻 failure mode**：排比句型保留但具名座標換成泛稱類別（「小說／詩／散文」）＋ 無 antecedent work ＋「繁衍／別戀」變裝飾形容詞

**關鍵交叉觀察**：李的 failure mode 第 (a) 項（具名座標泛化）與許的 failure mode 第三項（把具名文化座標泛化成「書／音樂」）**是同一個 LLM-default drift**，只是觸發結構不同。意即：一個 LLM 在仿李失敗時會落入「泛稱座標」，仿許失敗時也會落入「泛稱座標」，這是 **zh-TW Q2 center 整個 cluster 共同的 drift vector**，不是 pairing-specific 的污染。

反之，**模仿一方不會「順便」觸發另一方的招牌 failure mode**：
- 仿李不會產出「X 是一種 Y」箴言（李本身無此結構）
- 仿許不會產出無 antecedent work 的排比枚舉（許本身不靠排比）

換言之 **兩者的 failure modes 不會 cross-contaminate，反而是 zh-TW Q2 共同的 corpus-level drift 在兩邊都出現**。

## Verdict: Option V1 + 部分 Option V2 補強

### V1 confirm reject 的嚴格理由

1. **Schema v2 硬規則不放行**：許 = HIGH，李 = MEDIUM。依 v1.11.1 qualifying rule，合格 substitute 的 risk 必須「嚴格低於」named master。
   - **李 → 許方向**：李 (MEDIUM) < 許 (HIGH) ✓ 通過 risk 條件
   - **許 → 李方向**：許 (HIGH) > 李 (MEDIUM) ✗ 不通過

2. **但 risk 條件是必要非充分**：`anchor-schema-v2.md §Safe substitute for` 還要求 condition 2「substitute 遞送相鄰 register，empirically verified」。李與許雖同屬 zh-TW Q2 center 且共用文化批評傳統，**脊骨句型完全不重疊**：李移除定義反轉、許移除排比枚舉，voice 立即崩塌。user 指名許舜英 register 時若 Pass 3 auto-suggest 李，會失去「X 是一種 Y」這個 register-defining 結構；反之用許代李亦失去 antecedent-work dialogue。屬「相鄰但不可替換」。

3. **許 Metadata 自己的 Stylistic-sibling 欄位範例**：line 52 對張愛玲的描述「shares compressed-observation cadence but 張's register lacks power-disparity payload requirement」即同一 reject 模式。李 → 許 的關係屬同型。

4. **V3 方向性 case 不成立**：原 prompt 提出「許 → 李 works for shopping-culture briefs」，但 shopping-culture 本是許的 home turf（《購物日記》），brief 指名許時 downgrade 到李反而流失 register 核心。方向性 case 無 empirical support。

### V2 補強：記錄關係但不開 frontmatter 欄位

建議 **不** 啟用 `safe_substitute_for` frontmatter pairing（即使李→許方向通過 risk 條件），但在兩個 anchor 的 Metadata 區塊補上 `Stylistic-sibling (not transferability)` 互引，依許 anchor 對張愛玲既有寫法。這讓未來 researcher 看到 pairing 時直接讀到 reject rationale，不會再提案。

## Recommendation for v1.12.0+

依重要性排序，**≤3 個 actionable 建議**：

1. **【必做，低風險】修正兩 anchor 的 Metadata `Stylistic-sibling` 互引**
   - 李 anchor 新增一行：`Stylistic-sibling (not transferability): 許舜英 ideological-definitional (anchor-zh-tw-xu-shunying-ideological-definitional.md) — shares 1990s zh-TW Q2 文化批評 cluster + 具名文化座標 load，差在 李 缺 power-disparity payload requirement + 許 缺 antecedent-work dialogue requirement；脊骨句型不可互換。`
   - 許 anchor 現有對張愛玲的 stylistic-sibling 行下方加一行對李欣頻的平行敘述。
   - 落實「書面記錄 reject rationale」，防止 v1.13.0+ 再度誤提案。

2. **【建議】在 `voice-anchor-meta-core.md` §Safe-substitute lookup 末尾加一行 "Documented non-substitutes (reviewed + rejected)" 段落**
   - 列出至少兩個已 review 且 reject 的 pairing 案例（許↔李 + 許↔張愛玲）與 2-3 行機制差異說明。
   - 讓未來 reviewer 在同一個 hot-path 檔案看到 "哪些對看似可配但不成立" 而不用挖 research note。

3. **【可選，後續批次處理】統一兩 anchor 的 Over-mimic risk 標記 + 修正原 prompt 斷言**
   - 原 prompt 斷言「李、許 皆 HIGH」，實際李 = MEDIUM。若兩者在實務 empirical rewrite test 上 drift pattern 相當，應考慮把李升為 HIGH 與許對齊；若 corpus evidence 支持李確實較低（文化座標比許分散、rhetorical 風險較低），則保留 MEDIUM 並同步更新 v1.11.0 Phase C sweep 記錄、避免後續 researcher 延用錯誤前提。此項建議獨立 PR、獨立研究跑 E2E rewrite drift test 後再決定。
