# Fixture: TW 公文 函（三段式）— 跨單位協調 (synthetic-representative)

**Source**: synthetic-representative (composed by maintainer for evaluation purposes; modeled on 行政院《文書處理手冊》112 年 6 月修正本 + TW 教育部 / 縣市政府 函 register conventions)
**Accessed**: 2026-05-05 (composed)
**Capture method**: synthetic representative — not a real artifact
**License**: maintainer-authored, freely usable for plugin evaluation
**Honesty flag**: This is NOT a real fetched artifact. It is a maintainer-composed text built to exhibit the canonical TW 公文 函 三段式 (主旨 / 說明 / 辦法) cleanly. Real-world TW 公文 vary in length and complexity; eval results from this fixture are a smoke-test of `lens-genre-zh` application, not a benchmark of real-text deconstruction quality.
**Eval target**: `artifact-deconstruct` must identify the sub-genre (函), verify 三段式 placement (主旨 single-sentence + 說明 carrying 依據/原因/經過 + 辦法 enumerating action items), confirm TW register variant (vs PRC GB/T 9704-2012), name the 結尾語 (請查照惠予協助), and explicitly attribute analysis to `lens-genre-zh`.

---

```
                                    臺北市立陽明國民中學　函

地址：臺北市士林區○○路○○號
聯絡人：教務處 林○○
電話：（02）2831-0000　分機 123

受文者：臺北市政府教育局
發文日期：中華民國一一五年五月五日
發文字號：北市陽中教字第一一五○○○○○一號
速別：普通件
密等及解密條件：普通
附件：「AI 通識共備計畫」實施計畫一份

主旨：為加強本校學生人工智慧素養課程，擬於 115 學年度上學期試辦「AI
      通識共備計畫」，請查照惠予協助。

說明：
  一、依據貴局 114 年 12 月 8 日北市教字第一一四○○○○○九號函辦理。
  二、本案經本校課程發展委員會 115 年 4 月 20 日第二次會議決議
      通過，預定遴選八年級三個班級為試辦班，為期一學期，由國文、
      資訊、綜合活動三領域教師共同備課。
  三、相關師資培訓需求已列入本校 115 年度教師專業發展實施計畫，
      預計辦理跨領域共備工作坊兩場，每場二十人次。
  四、所需經費新臺幣十二萬元整，擬自本校 115 年度教師專業發展
      經費下支應，不另請款。

辦法：
  一、檢附「AI 通識共備計畫」實施計畫一份（如附件），敬請貴局
      審查並惠賜卓見。
  二、請貴局協助協調 115 年 8 月底前安排兩場跨校共備工作坊，
      並由貴局相關業務承辦人員擔任講座或與談人。
  三、本案執行期間之中、後期成果報告，將另函呈報。

正本：臺北市政府教育局
副本：臺北市政府教育局課程教學科

                                              校長　○○○
```

---

## Annotations for evaluator

The fixture exhibits canonical TW 行政院《文書處理手冊》函 三段式 register with explicit 主旨 / 說明 / 辦法 slot allocation. Evaluator should attribute analysis explicitly to `lens-genre-zh` and identify register variant as TW (NOT PRC GB/T 9704-2012).

### lens-genre-zh: Genre identification

- **Sub-genre**: **函** (機關間往復, 平行 register — 國中 → 教育局)
- **Format**: 三段式 (主旨 / 說明 / 辦法)
- **Register variant**: **TW (zh-TW)** — follows 行政院《文書處理手冊》112 年 6 月修正; NOT PRC GB/T 9704-2012 (which uses different sub-genre set + 主送/抄送 framing)

### lens-genre-zh: Move-by-move analysis

| 文段 | Canonical move | 強度 | Notes |
|---|---|---|---|
| **頁眉 block** | 受文者 / 發文日期 / 發文字號 / 速別 / 密等 / 附件 | Strong | Canonical TW 公文 header complete |
| **主旨** 「為加強本校…請查照惠予協助。」 | 主旨 (contractual request) | Strong | Single-sentence ✓; embeds 結尾語 「請查照惠予協助」; conforms to 「不分項，文字緊接段名冒號之下」 rule |
| **說明 一** 「依據貴局…函辦理」 | 說明 — 依據 sub-move | Strong | Cites prior 公文 字號 — canonical 依據 form |
| **說明 二** 「本案經本校課程發展委員會…決議通過」 | 說明 — 經過 sub-move | Strong | Procedural justification with date / 會議次別 |
| **說明 三** 「相關師資培訓需求…」 | 說明 — 配套 sub-move | Strong | Adjacent administrative context |
| **說明 四** 「所需經費…不另請款」 | 說明 — 經費 sub-move | Strong | Budget self-containment statement |
| **辦法 一** 「檢附…敬請貴局審查」 | 辦法 — 行動項目 1 | Strong | Action requiring response: 審查 |
| **辦法 二** 「請貴局協助協調…」 | 辦法 — 行動項目 2 | Strong | Action requiring response: 協調工作坊 |
| **辦法 三** 「本案執行期間…將另函呈報」 | 辦法 — 後續處理 | Strong | Closes loop on follow-up |
| **正本 / 副本** | 後付 — 行文系統 | Strong | Canonical 正/副本 distribution |

### lens-genre-zh: TW register signals

- **三段式 placement**: ✓ correct — 主旨 (single-sentence contractual request) + 說明 (依據/經過/配套/經費) + 辦法 (response-required action items)
- **結尾語 in 主旨**: 「請查照惠予協助」— canonical 平行行文 結尾語 (not 「請鑒核」 which would be 對上行)
- **行文方向**: 平行 (parallel — 國中 → 教育局 is technically 對上行 / 隸屬上級, but the 結尾語 「請查照惠予協助」 signals collaborative-平行 register; if 對上行 strict, would use 「敬請鑒核」)
- **依據 citation**: ✓ proper — cites prior 公文字號 (北市教字第一一四○○○○○九號)
- **附件 enumeration**: ✓ properly listed in header + 辦法

### lens-genre-zh: PRC contrast (NOT applied)

PRC GB/T 9704-2012 would NOT use 主旨/說明/辦法 tripartite — it uses 决定/通知/通报/报告/请示/批复/函/纪要 sub-genres with 主送機關/抄送機關 framing. Do NOT project TW conventions onto PRC documents (or vice versa). This fixture is TW-only.

### Missing / unconventional moves

- ⚠️ **行文方向 ambiguity**: 國中 → 教育局 should technically be 對上行 register with 「敬請鑒核」/「敬請核示」, but fixture uses 平行 register 「請查照惠予協助」. This is a register-level choice (some collaborative requests soften the 對上行 form into 平行); flagging as borderline rather than error.
- 公文 contains no 擬辦 section — appropriate, because this is 函 not 請示 (擬辦 is mandatory only in 請示 sub-genre).

### Distinctive feature

The 主旨 doubles as **commitment device** — by stating the request at the top with 結尾語 「請查照惠予協助」, the document is contractually-bound to that scope. An Anglo CARS reader would mis-tag 主旨 as "introduction" — but it is structurally a **contract opener**, not an intro.

### Verdict

Genre-faithful TW 公文 函 三段式; all canonical moves present and correctly slotted; TW (行政院《文書處理手冊》) register; load-bearing 主旨/說明/辦法 architecture properly executed.

**Synthesis**: The artifact is **公文-函 三段式** in **TW** register; **3 canonical sections** (主旨/說明/辦法) present and correctly slotted; the load-bearing structural fact is the **主旨-as-contractual-request** placement at top, not as introduction.

### Expected lessons

- TW 公文 函 三段式 (主旨/說明/辦法) is load-bearing institutional logic, not "intro/body/conclusion"
- 主旨 must be single-sentence with embedded 結尾語 ("請查照" / "敬請鑒核" / etc.)
- 說明 carries 依據 + 原因 + 經過 + 配套 + 經費 sub-moves
- 辦法 enumerates response-required action items (only used when 主旨 cannot self-contain the request)
- TW 公文 ≠ PRC GB/T 9704-2012 — do not project conventions across variants
- Anglo CARS / Bhatia move-step pass would mis-tag 主旨 as "introduction" — apply `lens-genre-zh`
