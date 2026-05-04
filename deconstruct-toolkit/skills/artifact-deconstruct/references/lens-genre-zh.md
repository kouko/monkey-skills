# Lens: Genre Analysis (Chinese register — 學術 / 公文 / 八股 legacy + Swales scaffolding)

> **Sources**:
> - John M. Swales, *Genre Analysis: English in Academic and Research Settings* (Cambridge University Press, 1990) — CARS 3-move model used as universal scaffolding under which ZH-specific moves are tabulated.
> - Vijay K. Bhatia, *Analysing Genre: Language Use in Professional Settings* (Longman, 1993) — move-step methodology applied to ZH 公文 sub-genres below.
> - 行政院《文書處理手冊》(中華民國 112 年 6 月 8 日修正本) — TW canonical reference for 公文 sub-genres (函 / 通知 / 報告 / 請示 / 公告) and the 主旨 / 說明 / 辦法 tripartite. Public PDF at `ey.gov.tw`.
> - 《公文程式條例》(全國法規資料庫 PCode A0030018) — TW statutory definition of 公文 ("處理公務之文書") and the legally-required document classes.
> - Loi & Evans (2010), "Research article introductions in Chinese and English: A comparative genre-based study" (*Journal of Pragmatics*, ScienceDirect 1475158510000573) — empirical evidence that Swales CARS moves appear in ZH research-article introductions but at lower frequencies + different orderings than English.
> - Andy Kirkpatrick & Zhichang Xu, *Chinese Rhetoric and Writing* (WAC Clearinghouse 2012) — Ch 4 "The Ba Gu Wen 八股文"; scholarly source on 八股 modern legacy ("contemporary baguwen, if they reappear, will capture only an overall argument structure rather than a strict linguistic style").
> - 台大寫作教學中心「論文寫作的法門：寫作結構」+ AsiaEdit 論文前三章寫作指南 — modern TW academic 緒論 sub-move conventions (研究背景 → 研究利基 → 研究目的 → 研究問題 → 研究價值 → 章節安排).

> **Synthesis note**: This file combines Swales's CARS move-analysis (1990) and Bhatia's professional-genre move-step methodology (1993) with **ZH-specific genre repertoire** that those two authors did not cover: TW 公文 sub-genres per 行政院《文書處理手冊》, the modern TW academic 緒論-本論-結論 hybrid, the 八股 legacy in modern argument structure, and ZH formal-letter 提稱語 conventions. Unlike the `-anglo` variant where Swales→Bhatia is a unified school, here Swales/Bhatia is **scaffolding** under which native ZH genre canons are mapped. See [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md) for the synthesis-disclosure policy and [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md) for the cultural-variant pattern.

> **Cultural-register statement**: This variant grounds in modern TW Mandarin (繁體) academic + administrative register, with cross-references to HK and PRC where conventions diverge. ZH genres span pre-modern formula-locked tradition (八股, 公文 ancestors) and modern Western-influenced academic. **TW vs HK vs PRC differ** — TW 公文 follows 行政院《文書處理手冊》, PRC follows GB/T 9704-2012《党政机关公文格式》, HK retains British colonial-administrative residue. Reader is treated as **institutional actor** in 公文 register (隸屬 / 平行 / 對下 relationships are baked into the form).

## When to apply this lens

- ZH academic paper / thesis (碩博士論文 / 期刊投稿)
- ZH 公文 (TW 行政院 函 / 通知 / 報告 / 請示 / 公告)
- ZH formal business letter (敬啟者 register)
- ZH op-ed / 社論 / 論說文 (where 八股 legacy 起承轉合 surfaces)
- ZH 報告 / 簽呈 (upward-reporting genre)
- ZH 請示 / 建議書 (request-for-ruling genre)

## When NOT to apply

- ZH literary fiction / 散文 — lens-rhetoric-zh (六觀) is the better tool
- ZH consumer marketing copy — lens-persuasion-zh
- Translated text where the ZH is a translation OF an Anglo original — apply `-anglo` to the source register and note translation overlay
- 文言 classical text without modern reception context — outside this lens's scope

## Part 1: ZH Academic — 緒論-本論-結論 + IMRaD overlay

Modern TW + HK academic writing uses a hybrid: **Western IMRaD overlay** (Introduction / Methods / Results / Discussion) on a 緒論-本論-結論 macro-structure. The 緒論 sub-moves are more elaborated than Anglo CARS:

| 緒論 sub-move (canonical TW thesis order) | Function | Approx Anglo parallel |
|---|---|---|
| 研究背景 | situate the topic in real-world / disciplinary context | CARS Move 1 step 1B (topic generalization) |
| 文獻回顧 (often own chapter in thesis) | survey prior work, identify positions | CARS Move 1 step 1C (reviewing prior research) |
| 研究利基 / 研究缺口 | locate the gap | CARS Move 2 step 2B (indicating a gap) |
| 研究目的 | state intent | CARS Move 3 step 3A (outlining purposes) |
| 研究問題 (RQ) | enumerate specific questions, often Q1/Q2/Q3 numbered | usually merged into Move 3 in Anglo |
| 研究方法概述 | brief methodology preview | (rare in Anglo intros — appears in §Methods) |
| 研究價值 / 研究貢獻 | claim significance | Anglo "contribution" claim |
| 章節安排 | enumerate chapters ("第二章 X，第三章 Y…") | CARS Move 3 step 3C, but **far more explicit** in TW thesis |

Empirical ZH-EN comparison (Loi & Evans 2010): the same Swales moves are present, but ZH papers use **fewer total move-steps**, are **more likely to skip Move 2 niche-claiming**, and treat 章節安排 as load-bearing in a way Anglo intros do not.

**本論** is the analytical core, often chapter-divided. **結論** in TW thesis convention is typically split into 結論 (findings restated) + 建議 (recommendations / future research) — the 建議 sub-section is **expected**, not optional, in TW master's-thesis register.

## Part 2: ZH 公文 — TW 行政院 sub-genres

Per 行政院《文書處理手冊》(112 年 6 月修正), 公文 ("處理公務之文書") has **6 statutory classes**: 令 / 呈 / 咨 / 函 / 公告 / 其他公文. The 5 working sub-genres encountered in non-presidential institutional life:

| Sub-genre | Direction / when used | Required moves | Surface marker |
|---|---|---|---|
| **函** | 機關間往復 + 人民與機關往復 (default workhorse) | 主旨 / 說明 / 辦法 (三段式), or 主旨 / 說明 (二段式), or 主旨 only (一段式) | "主旨：" header line; 受文者 + 發文字號 block |
| **通知** | 對下行 instruction / announcement to subordinates | 主旨 / 說明 (二段式 typical) | header bar with 機關名稱 + "通知"; often shorter than 函 |
| **報告** | 對上行 status / progress report (subordinate → superior) | 主旨 / 說明 (二段式); 說明 carries the substance | "謹查" / "茲將……敬陳" framing in 說明; ends "謹報請鑒核" |
| **請示** | 對上行 request for ruling / decision (subordinate → superior) | 主旨 / 說明 / 擬辦 (三段式 mandatory) | 擬辦 section enumerates options; closes with "敬請鑒核" / "敬請核示" |
| **公告** | 對外 public-facing notice | 主旨 / 依據 / 公告事項 | header "公告"; legal-citation in 依據 is mandatory |

**Load-bearing structural fact**: in 函 and 請示, 主旨 must be **single sentence, no enumeration** ("不分項，文字緊接段名冒號之下"). 說明 carries the case background (依據 / 原因 / 經過). 辦法 holds the action items requiring response (only used when 主旨 cannot self-contain the request). 擬辦 (請示-only) enumerates 甲 / 乙 / 丙 alternative dispositions for the superior to pick from. Misplacing content across these slots is the single most common 公文 error.

**PRC contrast**: GB/T 9704-2012 defines a different sub-genre set (决定 / 通知 / 通报 / 报告 / 请示 / 批复 / 函 / 纪要), uses 主送机关 / 抄送机关 framing, and does **not** use the TW 主旨/說明/辦法 tripartite. Do not project TW conventions onto PRC documents.

## Part 3: 八股 legacy in modern argument

The Ming-Qing examination form 八股文 had 8 structural moves: 破題 → 承題 → 起講 → 入題 → 起股 → 中股 → 後股 → 束股 (plus 大結 in some accounts). The form was abolished with the 1905 科舉 abolition, but Kirkpatrick & Xu (2012) and Mainland scholars argue its **structural skeleton** survives in two registers:

1. **Modern ZH op-ed / 論說文 / 高考議論文**: collapses to **起承轉合** (起 = broach topic / 承 = develop / 轉 = turn or counter / 合 = synthesize). The 轉 move is load-bearing — explicit transition markers (然而 / 但是 / 可是 / 反觀 / 不過) signal the move boundary in a way English argument prose handles via paragraph-rhetoric instead of lexical signposting.
2. **對偶 (parallelism) + 排比 (parallel structure clusters)**: the 起股 / 中股 / 後股 / 束股 inner moves required parallel-couplet construction. Modern descendants — TW 高中作文, PRC 高考議論文, formal speeches, op-eds — still treat dense parallel-structure clusters as a **register signal of authority and seriousness**, not as decoration. Reading parallel-prose as "rhetorical flourish" misses that it is performing 八股-descended authority-marking.

When analyzing ZH op-ed or formal essay, look for: explicit 轉 marker, clustered 對偶 / 排比 in the middle moves, and a 合 paragraph that returns to the 破題. The closer the artifact tracks 起承轉合 + parallel-structure middle, the more it is signaling 八股-legacy authority register.

## Part 4: ZH formal letter — 提稱語 + 結尾敬辭 register table

Formal correspondence (商業書信 / 公務書信 / 學界往復) opens with 稱謂 + 提稱語 and closes with 結尾敬辭 + 末啟詞. The choice is **not interchangeable**; it encodes the recipient's institutional role and the writer's relative position.

| 提稱語 (opening, after recipient name) | Recipient | Pairs with closing |
|---|---|---|
| 鈞鑒 / 鈞啟 | 至尊長輩 / 父母 / 高階長官 | 敬請鈞安 / 肅請鈞安 |
| 尊鑒 / 尊前 | 上司 / 尊長 (general superior) | 敬請尊安 |
| 道鑒 / 道啟 | 教職人員 / 學者 / 宗教人士 (any teacher-class recipient) | 敬請道安 / 順頌道祺 |
| 大鑒 / 台鑒 | 平輩 / 一般往復 (default formal-business letter) | 順頌台安 / 順頌商祺 (commercial register) / 此致 (closing only) |
| 惠鑒 / 雅鑒 | 平輩文人往復 (literary register) | 順頌文祺 |
| 敬啟者 (no name above) | "to whom it may concern" — opens the letter body, not a 提稱語 per se | 此致 + 收信機關名 |

Pairing rules: the opening sets the closing. Mixing a 鈞鑒 opener with a 順頌商祺 closing is a register-jumping error that signals the writer doesn't control the form. In TW business correspondence, the **default safe pair** is `大鑒` / `台鑒` + `順頌商祺`. In academic correspondence with a teacher, `道鑒` + `敬請道安` is the safe pair.

## Worked examples

### Example 1 — TW 公文 函 (invented, three-section format)

```
受文者：本市政府教育局
發文日期：中華民國一一五年五月五日
發文字號：北市教字第一一五〇〇〇〇〇一號
速別：普通件
密等及解密條件：普通
附件：附件一份

主旨：為加強本市國中人工智慧素養課程，擬於 115 學年度上學期試辦「AI 通識
      共備計畫」，請查照惠予協助。
說明：
一、依據貴局 114 年 12 月 8 日北市教字第一一四○○○○○九號函辦理。
二、本案經本校課程發展委員會 115 年 4 月 20 日會議決議通過，預定遴選
    八年級三個班級為試辦班，為期一學期。
三、相關師資培訓需求已列入本校 115 年度教師專業發展計畫。
辦法：
一、檢附「AI 通識共備計畫」實施計畫一份，敬請貴局審查。
二、請貴局協助協調 115 年 8 月底前安排兩場跨校共備工作坊。
此致
臺北市政府教育局
                                                校長　○○○
```

**Move analysis**: 主旨 is single-sentence, names the request and includes the 結尾語 "請查照"; 說明 carries 依據 (item 1) + 經過 (item 2) + 配套 (item 3); 辦法 enumerates concrete action items that the receiver must respond to. This is canonical 三段式 函 register. A reader trained on Anglo CARS would mis-tag 主旨 as "introduction" — it is actually a **commitment device**: the request is contractually-bound at the top, not in a conclusion.

### Example 2 — TW 學術論文 緒論 開頭段 (invented, undergraduate thesis register)

```
近年來，隨著生成式人工智慧（generative AI）在教育場域的快速擴散，
教師如何在課堂中重新定位其知識中介角色，已成為教學研究關注的核心議題
（陳，2024；Loi & Evans, 2010）。然而，現有研究多集中於英語教學場域，
對於華語文教學中的教師角色變化，尚缺乏系統性的實徵探究。本研究即在
此背景下，以臺北市三所國中華語文教師為對象，探討其在導入生成式 AI
工具後的教學調整歷程。
本研究欲回答之研究問題如下：
（一）國中華語文教師在導入 AI 工具後，課堂提問策略產生何種轉變？
（二）此轉變如何影響學生的書寫表現？
本論文共分五章。第一章為緒論……
```

**Move analysis**: 研究背景 (sentence 1) → 研究利基/缺口 ("然而……尚缺乏系統性的實徵探究" — explicit 轉 marker) → 研究目的 + 對象 (sentence 3) → 研究問題 (numbered Q1/Q2 — load-bearing in TW thesis register) → 章節安排 ("本論文共分五章……"). The "然而" 轉 marker doing niche-staking work is the **八股 legacy 起承轉合 surfacing inside a Western-IMRaD outer shell** — a hybrid signature. Anglo CARS Move 2 (gap) is present but realized lexically via 轉 rather than via Swales-style "however, little research has examined…" phrasing.

## Output format

```markdown
### Genre identification (ZH register)
<學術 / 公文-函 / 公文-請示 / 公文-公告 / 商業書信 / 論說文 / 報告 / hybrid>
<TW / HK / PRC register fork — note which conventions apply>

### Move-by-move analysis
| 文段 | Canonical move | 強度 | Notes |
|---|---|---|---|
| ... | ... | strong / adequate / weak / missing | ... |

### TW / HK / PRC register signals
- 提稱語 / 結尾敬辭 pairing: <observed pair> — <consistent / mismatched>
- 公文 三段式 placement: <主旨 / 說明 / 辦法 / 擬辦 — correct / misplaced>
- 八股 legacy markers: <起承轉合 explicit? 對偶 / 排比 density?>
- IMRaD vs 緒論-本論-結論 overlay: <pure / hybrid / mismatch>

### Missing / unconventional moves
- <e.g. 請示 missing 擬辦 — the receiver cannot rule without options>
- <e.g. 緒論 lacks 章節安排 — TW thesis convention violation>
```

End with 1-line synthesis: "The artifact is **<genre>** in **<TW/HK/PRC>** register; **<N>** canonical moves are present; the load-bearing deviation is **<missing or misplaced move>**."

## Pitfalls

- **Forcing PRC GB/T 9704-2012 format onto TW 公文 (or vice versa)** — the sub-genre sets and tripartite slot names differ; never analyze a TW 函 with PRC 报告 expectations.
- **Missing 主旨 / 說明 / 辦法 tripartite as "structure" rather than load-bearing** — that *is* the structure of TW 函 and 請示; collapsing it to "intro / body / conclusion" loses the institutional logic (主旨 = contractual request; 辦法 = response-required action items).
- **Treating 對偶 / 排比 as decoration** — they signal 八股 legacy authority register. Dense parallel-structure clusters in an op-ed are doing the same work as Anglo passive-voice + nominalization in academic prose: marking institutional voice. Reading them as "florid style" misses the function.
- **Applying Anglo CARS to ZH 緒論 directly** — works partially (Loi & Evans 2010 confirm CARS moves are present) but misses the **章節安排** load-bearing role and the elaborated 研究背景 → 研究利基 → 研究目的 → 研究問題 → 研究價值 sub-move chain. Tag the additional ZH moves explicitly.
- **Mistaking 敬請鑒核 / 敬請核示 for filler** — these are the canonical **request-marker** in 請示 and upward 報告. Their absence means the document is not actually requesting a ruling. Their presence is contractual, not ornamental.
- **Mismatched 提稱語 + 結尾敬辭 pairs** — `鈞鑒` opener with `順頌商祺` closing signals writer doesn't control the form; flag as register-control failure rather than treating as stylistic variation.

## Cross-variant pointer

The same artifact may yield different findings under [`lens-genre-anglo.md`](lens-genre-anglo.md) (Swales CARS + Bhatia sales-letter) and [`lens-genre-ja.md`](lens-genre-ja.md) (序論-本論-結論 + 起承転結 dual-mode + 拝啓-時候-主文-末文-敬具 letter formula). For multilingual or translated artifacts, apply two variants and contrast — particularly informative for TW 公文 translated into English (the 主旨 / 說明 / 辦法 tripartite usually collapses to a single Anglo-business-letter shape, losing the institutional layering).
