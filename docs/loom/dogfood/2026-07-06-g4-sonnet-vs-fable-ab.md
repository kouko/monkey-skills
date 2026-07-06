# G4 — Sonnet-vs-Fable whole-branch review quality A/B (2026-07-06)

**One-line answer: a single Sonnet review is NOT a trustworthy gate
(50% verdict miss in this sample), but a 2×Sonnet panel with
union-aggregation IS — and Sonnet surfaced real findings Fable missed.
Zero false positives on either tier.**

- Origin: `docs/loom/BACKLOG.md` G4 entry; executed as
  `docs/harness-audit/2026-07-06-iteration-roadmap.md` item 1
  (time-boxed: the Fable arm's availability window).
- Test material: PR #501's pre-fix state `1b8e2a5b` (base `03d8312c`) in
  a detached worktree — chosen because it carries **disk-verifiable
  ground truth**: 5 findings (2🟡+3🟢) from the original in-session
  review, each independently checkable and later fixed, plus a known
  correct verdict (NEEDS_REVISION, 2🟡 rule).
- Arms: 2× Sonnet (S1, S2) + 2× Fable (F1, F2), all
  `loom-code:code-reviewer`, **byte-identical prompts**, blind to the
  ground truth and to each other.

## Scorecard

| | S1 | S2 | F1 | F2 |
|---|---|---|---|---|
| Verdict (expect NEEDS_REVISION) | ✅ N_R | ❌ PASS_WITH_NOTES | ✅ N_R | ✅ N_R |
| GT1 README trio 🟡 | ✗ | ✗ | ✅（還多抓一處 using-loom-code/README.md:13） | ✅（＋status v0.23.0 順帶） |
| GT2 PRODUCT-SPEC:145 🟡 | ✅ | ✗ | ✗ | ✗ |
| GT3 codex probe prompt 🟢 | ✗ | ✗ | ✗ | ✗ |
| GT4 size gate bound 🟢 | ✗ | ✗ | ✅ | ✅ |
| GT5 dual-copy drift 🟢 | ✗ | ✗ | ✗ | ✅ |
| GT recall | 1/5 | 0/5 | 2/5 | 3/5 |
| Novel REAL findings | 2 | 1 | 1 | 1 |
| False positives | 0 | 0 | 0 | 0 |
| Ran deterministic tests | no (R3) | yes | no (R3) | yes＋spot-checked A/B raw JSONL |
| Tokens | 107K | 101K | 95K | 91K |

Novel real findings（全部磁碟裁決為真；原審與本場其他審查都沒抓到）：
- **BACKLOG entry born-stale**（S1、F1、F2 三臂同抓，🟡）：同 branch 出貨
  了 slimming 卻新增 Status:OPEN＋前瞻語態條目，違反 BACKLOG 自己的
  「completed 即刪」章程。
- **反合理化清單掉了「先問再說」**（S2 獨抓）：router card 違反 plan 的
  verbatim-or-tightened 契約——正好對應規則 5 的合理化樣態。
- **規則 5 掉了 brainstorming Axis 4 指標**（S1 獨抓）：plan KEEP 條款
  說 skill 名要留。

## 判讀

1. **單一 Sonnet review 不可靠**：S2 給了 PASS_WITH_NOTES（漏掉全部
   5 個已知發現）——若它是唯一 gate，這條 NEEDS_REVISION branch 會
   被放行。同 tier 內部變異巨大（S1 與 S2 的 verdict 都不同）。
2. **2×Sonnet panel＋聯集聚合可修復 verdict**：S1∪S2 = 2 個 🟡
   （GT2＋BACKLOG）→ 按 quality-gate 規則聚合 = NEEDS_REVISION ✓。
   個體不可靠、panel 可靠——與 completeness-critic 的 panel 設計
   同構，現在有了 review 側的實證。
3. **Fable 較穩、recall 較高（結構性 doc-drift 軸）**：2/2 verdict 正確、
   GT 聯集 3/5，且兩臂發現高度重疊（一致性佳）。但 GT2（PRODUCT-SPEC）
   兩臂都漏——Fable 也不是全知。
4. **Sonnet 看到不同的東西**：兩個字面保真度發現（「先問再說」、Axis 4
   指標）都是 Sonnet 獨得，Fable 四臂（含原審）全漏。tier 差異不是
   純粹的強弱序，是**視角分布不同**——跨 tier 混合 panel 有真實價值。
5. **零誤報 ×4**：兩個 tier 的 precision 都是滿分——任一 tier 回報的
   發現都可信，差別全在 recall。這對制度設計是好消息：不用怀疑
   弱模型 reviewer 的發現，只需要補它的覆蓋。
6. **Review 本質是抽樣**：GT3（codex probe prompt）今天四臂全漏（原審
   有抓）；含原審在內 5 次 review 的聯集才達到 6/6 已知+3 novel。
   「一次 review = 完整覆蓋」的假設本來就不成立，panel 與多輪才是解。
7. **二值 verdict 通膨**：未觀察到系統性通膨——S2 的錯是 finding-recall
   造成，聚合規則本身運作正常。
8. **成本**：Fable 臂 token 反而較省（~93K vs ~104K，探索較收斂）；
   但以單價計 2×Sonnet panel 仍遠廉於 1×Fable。

## 對制度的建議（落點）

- **requesting-code-review 在弱模型環境的預設改為 2-reviewer panel＋
  聯集聚合**（loom-code next-touch；本報告為依據）。單 Sonnet review
  當 gate 的風險已量化：50% verdict miss（n=2，樣本小但方向明確）。
- 高風險 branch 可加第三臂（跨 tier 或第三個 Sonnet）；發現不需去重
  裁決成本——零誤報意味聯集安全。
- GT3 類（測試檔內的過時 prompt 文字）四臂全漏 → 這類適合機械 lint
  而非 review（roadmap item 3 的論據 +1）。

## 誠實條款（限制）

- n=1 branch、diff 偏 docs（程式碼本身乾淨）——結論對 code-heavy diff
  的外推未經驗證；GT 分布偏 doc-coherence 軸，可能低估 tier 在
  邏輯/安全軸的差距。
- 每臂單次抽樣；S1/S2 的巨大變異本身說明單次結果有運氣成分——
  panel 建議正是對此的對沖。
- Fable 臂 = claude-fable-5、Sonnet 臂 = 當前 sonnet alias；
  模型代際變動後數字需重測（方法可完整重放：worktree 釘 commit＋
  同 prompt ×N）。

---
Changelog:
- 2026-07-06 初版（roadmap item 1 執行紀錄；Fable 窗口內完成）。
