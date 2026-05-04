# Lens: Frame Analysis (Chinese register — Goffman + Lakoff + 面子/關係 + ZH conceptual metaphors)

> **Sources**:
> - Erving Goffman, *Frame Analysis: An Essay on the Organization of Experience* (Harper & Row, 1974). Primary frameworks Ch 2; keying Ch 3; fabrications Ch 4; vulnerabilities of experience Ch 12.
> - George Lakoff & Mark Johnson, *Metaphors We Live By* (University of Chicago Press, 1980; 2003 afterword edition). Three-type taxonomy (Structural / Orientational / Ontological) Ch 1; orientational metaphors Ch 4; ontological metaphors Ch 6.
> - Hu Hsien-chin, "The Chinese Concepts of 'Face'", *American Anthropologist* 46(1), 1944, pp. 45-64. Distinguishes 面子 (mianzi) — public dignity tied to social position — from 臉 (lian) — moral character integrity.
> - Hwang Kwang-Kuo, "Face and Favor: The Chinese Power Game", *American Journal of Sociology* 92(4), 1987, pp. 944-974. Tripartite tie-typology (情感性 / 工具性 / 混合性 ties) governing reciprocity rules; face as embedded in 關係 (guanxi) structure.
> - Kaiping Peng & Richard E. Nisbett, "Culture, Dialectics, and Reasoning About Contradiction", *American Psychologist* 54(9), 1999, pp. 741-754. Documents Chinese dialectical-thinking style (change / contradiction / holism principles, traceable to 陰陽 / 道家 / 儒家 sources) versus Anglo-Western non-contradiction reasoning.

> **Synthesis note**: This file combines Goffman frame (1974) + Lakoff conceptual metaphor (1980) with ZH-specific frame mechanisms — Hu's 面子/臉 dual-face distinction (1944), Hwang's 關係 tie-typology (1987), and Peng & Nisbett's empirically documented 陰陽 dialectical metaphor (1999). The combination is a methodological choice by `deconstruct-toolkit`: Goffman + Lakoff supply universal scaffolding; Hu + Hwang + Peng & Nisbett supply the ZH register that the Anglo sources do not name. See [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md).

> **Cultural register note**: Goffman's frame analysis applies cross-culturally, but the **face-as-frame** mechanism is foregrounded far more in ZH register than in Anglo. Goffman/Brown-Levinson treat "face" as a politeness phenomenon at the utterance level; Hu 1944 documents 面子 / 臉 as a **structural frame** organizing social standing across multi-year arcs. Lakoff/Johnson's metaphor inventory is built on Anglo corpus that overwhelmingly uses **binary** conceptual metaphors (UP/DOWN, IN/OUT, GOOD/BAD); Peng & Nisbett (1999) document that Chinese cognitive style instead favors **complementary-dyad** metaphors (陰陽, 有無, 動靜, 剛柔) where opposites co-define rather than exclude. Reading ZH artifacts with Anglo binary defaults produces systematic misreadings.

## When to apply this lens

- ZH political speech (TW / PRC / HK — note regional differences)
- ZH corporate / CSR communication
- ZH advertising and brand messaging
- ZH social-policy documents
- 公文 (official documents) and 公告 (public notices)
- Texts where face-management or 關係-signaling is doing argumentative work

## When NOT to apply

- ZH technical reference / API docs (no framing work)
- Pure data tables or 統計年報
- Translations from Anglo originals where the ZH text preserves source-language framing (use `-anglo` instead)
- Code / formula-heavy 學術論文 where rhetoric is suppressed

---

## Part 1: Goffman frame baseline (ZH register adjustments)

A "frame" is the implicit world-view that makes a text meaningful. Goffman's primary-framework / keying / fabrication apparatus applies in ZH register, but several surface signals shift.

| Concept | Question | ZH-register surface signal |
|---|---|---|
| **Primary framework** | What world-view does the text presume? | Often signaled by stance toward 道 / 公義 / 民意 / 和諧 — invoking which carries normative weight |
| **Keying** | What tone / register is in play? | Address-form shift (您 / 你 / 閣下 / 諸位); literary-classical insertion (引古典 / 用四字成語) keys formal / authoritative |
| **Fabrication** | Surface frame ≠ real intent? | 表面客氣 / 暗藏批評; 「順便」「不揣冒昧」 polite hedges hiding pointed asks |
| **Frame vulnerability** | Where is the frame trap? | Ritual phrases (套話) deployed to close off challenge; "為大局著想" framing pre-empts dissent |

### Worked move 1: Primary framework detection (ZH)

Ask: "If a reader from outside this 文化圈 picked up this text, what would they need to know to begin understanding it?"

Example: A TW 縣市政府 公告 assumes a primary framework of **行政程序法 + 公務員倫理 + 為民服務** triad. Inside that frame: passive-construction ("經查⋯⋯") signals procedural neutrality, not evasion. **Outside** that frame, the same passive reads as bureaucratic dodge.

### Worked move 2: Keying via address-form

ZH keying is heavily carried by pronominal and titular choice:

- 「您好，敬請指教」— deferential / subordinate-to-superior keying
- 「你看這事兒」— intimate / peer keying
- 「諸位先進」— formal / addressing-elders keying
- 「各位夥伴」— horizontal / community-of-practice keying

A re-keying analysis asks: if the speaker switched 您 → 你, what implicit relation collapses?

### Worked move 3: Fabrication detection (ZH)

A fabrication is when the surface frame differs from the actual frame.

| Surface frame | Actual frame |
|---|---|
| 「廣納民意」(public consultation) | 決策已定，僅走程序 |
| 「以客為尊」(customer-first) | KPI-first, customer is metric input |
| 「同心協力」(unity) | 統一口徑，不容異議 |
| 「為您好」(it's for your benefit) | 為我方便 |

---

## Part 2: 面子 / 臉 dual-face frame analysis

Hu 1944 distinguishes two ZH face concepts that English "face" conflates. This distinction is **structural**, not stylistic — they obey different repair rules and operate on different timescales.

| Term | Pinyin | Function | Surface signal |
|---|---|---|---|
| **面子** | mianzi | social-status face / public dignity tied to position, achievement, network | Titles invoked (「李董」「王處長」), 抬頭 / 落款 honorifics, status-display, 給面子 / 賞光 / 賞臉 / 不給面子 |
| **臉** | lian | moral-character face / integrity reputation; loss is community-wide moral judgment | Invocations of 良心 / 信用 / 道德 / 廉恥 / 沒臉見人 / 丟臉 / 臉皮厚 |

### Why this matters for frame analysis

Goffman's frontstage/backstage performance model treats face as **what the actor performs in the moment**. Hu/Hwang treat 面子 + 臉 as **reciprocal credit ledgers** maintained across the relationship's lifespan:

- Giving someone 面子 in public creates an obligation they will repay (even years later)
- Causing someone to 丟臉 may be unforgivable — repair is structurally hard, not merely awkward
- 面子 can be lent ("看在某某的面子上"); 臉 cannot — it is non-transferable moral capital

### Frame-analytic moves

For each 面子 / 臉 invocation in the artifact:

1. **Which face is at stake?** — 面子 (status) or 臉 (integrity)?
2. **Whose face?** — speaker's, addressee's, third-party invoked-by-name?
3. **What ledger move is happening?** — giving / withholding / repaying / damaging?
4. **What does Goffman miss here?** — what would Western politeness theory say, and how does it fall short?

### Common ZH face-frame patterns

| Pattern | Signal | What's framed |
|---|---|---|
| **借面子 / 抬轎** | Invoking a senior's name to legitimize a request | Speaker borrows 面子-credit |
| **不給面子** | Public refusal of a routine request | Speaker is signaling relation-rupture |
| **留面子 / 留個台階** | Allowing graceful retreat for the other party | Speaker preserves future-relation option |
| **撕破臉** | Open conflict that abandons face-management entirely | Frame-break — relationship is being ended |

---

## Part 3: 關係 (guanxi) and 圈子 (quanzi) as in-group frame

Hwang 1987 maps 關係 onto a tripartite tie-typology that governs which reciprocity rules apply. This is **not** equivalent to Anglo "network" or "connections" — those are weak Anglo glosses that miss the structural force.

| Tie type | Pinyin | Reciprocity rule | Anglo gap |
|---|---|---|---|
| **情感性** | qing-gan-xing | 需求法則 (need-rule) — give without expectation | "Family / closest friends" — but Anglo doesn't tie this to economic exchange the same way |
| **工具性** | gong-ju-xing | 公平法則 (equity-rule) — strict balanced exchange | "Strangers / one-off transactions" — closer match |
| **混合性** | hun-he-xing | 人情法則 (renqing-rule) — cycle of favors with implicit accounting | No clean Anglo analogue — Anglo "favor" lacks the structural-debt connotation |

### 圈子 (quanzi) — circle / clique as nested frame

Beyond 關係, ZH register frames interactions through **圈子 / 內外圈** distinctions that are 3-tier, not Anglo binary in/out:

| Tier | Term | Signal | Reciprocity expectation |
|---|---|---|---|
| **自己人** | zi-ji-ren | 「咱們自己人」「不是外人」 | 情感性 ties; need-rule applies |
| **熟人** | shou-ren | 「老朋友」「老同學」 | 混合性 ties; renqing-rule applies — favors tracked with face-currency |
| **外人 / 陌生人** | wai-ren / mo-sheng-ren | Formal address only | 工具性 ties; equity-rule applies — strict exchange |

### Frame-analytic moves

For each artifact, locate:

- **Who is being framed as 自己人?** — in-group invitation; readers asked to suspend equity-rule scrutiny
- **Who is framed as 外人?** — out-group; equity-rule applies, transactional posture justified
- **Where do 圈子 boundaries get drawn?** — 我們 vs 他們; 本土 vs 外來; 自家人 vs 「那些人」
- **Regional dimension** — TW / PRC / HK each frame 自家人 differently (本省/外省 / 本土/大陸 / 港人/內地). A TW artifact's 「我們」 may exclude PRC readers without saying so.

---

## Part 4: 陰陽 dialectical metaphor — challenges Lakoff binary assumption

Lakoff & Johnson 1980 derived their structural / orientational metaphors from Anglo English corpus. Many of those — UP/DOWN, IN/OUT, GOOD/BAD, US/THEM — are **binary oppositions** where the two poles exclude each other.

Peng & Nisbett 1999 document that Chinese cognitive style — empirically traceable to 陰陽 / 道家 / 儒家 textual traditions — operates on three principles that **diverge from Anglo non-contradiction logic**:

| P&N 1999 principle | ZH source | Implication for metaphor |
|---|---|---|
| **Change (變化)** | 易經 / 道家 | Reality is in flux; opposites transition into each other; static binary mappings misrepresent |
| **Contradiction (矛盾)** | 道家 / 儒家 | Apparent opposites can both be true simultaneously; "either/or" forces false choice |
| **Holism / Relationalism (整體)** | 儒家 / 道家 | Things are defined by their relations, not by isolable essences |

### How this shows up in ZH metaphor

ZH register systematically uses **complementary-dyad** metaphors where opposites co-exist and define each other:

| Dyad | Pinyin | Domain | Key feature |
|---|---|---|---|
| **陰陽** | yin-yang | cosmology, balance | Each contains the seed of the other (太極圖) |
| **有無** | you-wu | being / nothing | 道德經: 「有無相生」 |
| **動靜** | dong-jing | activity / stillness | Both required — 「動中有靜，靜中有動」 |
| **剛柔** | gang-rou | hard / soft | Strategic complementarity, not strength-vs-weakness |
| **虛實** | xu-shi | empty / full | Both productive — 兵法、書法、商場皆用 |

### Frame-analytic move: dialectical-metaphor check

Before applying Lakoff's binary metaphor templates, ask:

1. **Is the artifact framing its argument as binary opposition?** (X vs Y, must-choose)
2. **Or is it framing as complementary balance?** (兼顧 X 與 Y, 平衡, 調和, 「既⋯⋯又⋯⋯」)
3. **If the latter, applying Anglo binary templates will misread the artifact** — the text is NOT failing to take a side; it is operating on dialectical register where "both" is the position.

Practical implication: an artifact that says 「兼顧效率與公平」「平衡發展與環保」「既要⋯⋯也要⋯⋯」 is using 陰陽 register, not Anglo equivocation. A Lakoff-only reading will mistake dialectical synthesis for fence-sitting.

---

## Part 5: ZH conceptual metaphors not in Lakoff's Anglo corpus

These are live ZH conceptual metaphors with no clean Anglo mapping. Reducing each to its nearest Anglo gloss systematically loses content.

| ZH concept | Pinyin | Metaphor | Surface signal | Anglo gap |
|---|---|---|---|---|
| **道** | dao | way-as-cosmic-order | 「順其道」「天道」「商道」「為政之道」 | Anglo "way" lacks normative-cosmic content; 道 carries ought-from-is |
| **氣** | qi | vital-force as energy / atmosphere | 「氣勢」「人氣」「士氣」「景氣」「客氣」 | No direct Anglo equivalent; "atmosphere" misses the agentive force |
| **緣** | yuan | karmic-relational tie | 「有緣」「結緣」「緣分」「擦肩而過的緣」 | No direct Anglo equivalent; "fate / chance" misses the relational-merit accumulation |
| **心** | xin | heart-mind unity | 「用心」「心意」「同心」「將心比心」 | Anglo distinguishes mind (cognition) from heart (emotion); ZH 心 collapses both |
| **圈子** | quanzi | circle / clique-as-frame | 「進圈子」「不同圈子」「演藝圈」「政治圈」 | Anglo "network" lacks the tightness / boundary connotation; "clique" is pejorative-only |
| **面** | mian | front / face / surface | 「給個面子」「場面」「面上過得去」 | See Part 2 — Anglo "face" conflates 面子 / 臉 |
| **根** | gen | root-as-origin / legitimacy | 「根本」「根基」「在地紮根」「沒根的人」 | Anglo "root" is neutral; ZH 根 carries belonging / legitimacy weight |

---

## Worked example (zh-TW corporate-CSR communication snippet)

> 各位同仁，本公司去年在永續發展上有了長足的進步。我們秉持「兼顧獲利與社會責任」的經營理念，與在地社區建立深厚的緣分。董事長一向強調，做企業要對得起良心，更要給員工和股東一個交代。今年公司將擴大「自己人圈子」的關懷範圍，把上下游夥伴一起納入照顧。我們深知，企業的「氣」來自員工，員工的「心」繫於公司——這是一個不可分割的整體。期盼各位繼續支持，讓我們共同為下一個十年打好根基。

### Goffman-only reading (misses what's happening)

Goffman would identify: corporate-internal-communication primary framework, instructional-warm keying, possible fabrication around "永續發展" if metrics don't match. **What it misses**: the entire face / 關係 / 陰陽 architecture doing the persuasive work.

### Lakoff-only reading (forces binary onto dialectical text)

Lakoff would search for source-target metaphor mappings. The text uses 「兼顧 A 與 B」 dialectical complementarity — Lakoff's UP/DOWN / IN/OUT binaries find no purchase. A naive Lakoff reading might code "獲利 vs 社會責任" as Anglo competing-domains, misreading the 陰陽-style synthesis as compromise.

### ZH-register reading (full)

- **Goffman frame baseline (ZH adjusted)**: 公司內部訓示 primary framework; 諸位 + 同仁 keying signals horizontal-collective register (not 您 hierarchical, not 你 intimate); fabrication risk: if "兼顧" is performative without metrics, this is 套話 deployment.
- **面子/臉 face-frame analysis**: 「對得起良心」 invokes 臉 (moral integrity); 「給員工和股東一個交代」 invokes 面子 (status-position obligation). Both faces enlisted to legitimize leadership.
- **關係/圈子 in-group frame**: 「自己人圈子」 explicitly invoked as 3-tier — 同仁 (内圈) → 上下游夥伴 (擴大內圈) → implied 外人 (out-of-frame). This is structural in-group construction, not Anglo "stakeholder" mapping.
- **陰陽 dialectical metaphor check**: 「兼顧獲利與社會責任」、「企業的氣⋯⋯員工的心⋯⋯不可分割的整體」 — full 陰陽 dialectical structure. Reading as Anglo trade-off misses the framing.
- **ZH conceptual metaphors at work**: 緣分 (relational-merit tie with community), 氣 (organizational vital-force from employees), 心 (heart-mind unity of employees with company), 根基 (root-legitimacy for next decade), 圈子 (in-group nested frame).

**Synthesis**: The text positions readers as **自己人 inside an expanding 圈子 anchored by leadership 臉/面子 credit**, using **陰陽 complementary structure** to make **profit-and-responsibility-as-unified** feel natural. The unstated alternative — Anglo trade-off framing where one must concede to the other — is rhetorically excluded by the dialectical register itself.

---

## Output format

```markdown
### Goffman frame baseline (ZH adjusted)
- Primary framework: ...
- Keying (address-form / register): ...
- Fabrication detected? <yes / no — describe>
- Frame break(s): ...

### 面子/臉 face-frame analysis
- 面子 invocations: ... (whose, what ledger move)
- 臉 invocations: ... (whose, what moral-credit move)
- What Goffman / Brown-Levinson would miss: ...

### 關係/圈子 in-group frame
- 自己人 framing: ...
- 熟人 / 外人 boundary: ...
- 圈子 nesting (regional / professional / political): ...
- Reciprocity rule invoked (need / equity / renqing): ...

### 陰陽 dialectical metaphor check
- Binary-vs-complementary: <which register>
- Dyads in play (陰陽 / 有無 / 動靜 / 剛柔 / 虛實): ...
- If Lakoff binary applied naively, what would be misread: ...

### ZH conceptual metaphors at work
- 道 / 氣 / 緣 / 心 / 圈子 / 根 invocations: ...
- Anglo-gap risk: ...
```

End with 1-line synthesis: "The text positions the reader as **X** inside a **Y 圈子 / face-relation**, using **Z dialectical-or-binary** metaphor to make **W** feel natural. The unstated alternative is **V**."

---

## Pitfalls

- **Treating 面子 as the same as Goffman "face" / Brown-Levinson politeness face** — Hu 1944 distinguishes 面子 (status) from 臉 (integrity); Goffman/Brown-Levinson conflate them, missing the dual ledger
- **Forcing binary Anglo conceptual metaphors onto ZH text** — read for dialectical / 陰陽 patterns first; "兼顧" / "平衡" / "既⋯⋯又⋯⋯" are NOT Anglo equivocation
- **Treating 關係 as "connections" (Anglo network sense)** — guanxi is structural, multi-year, reciprocity-bearing per Hwang 1987 tie-typology; "connections" misses the renqing-debt mechanism
- **Reducing ZH-specific metaphors (道 / 氣 / 緣 / 心) to nearest Anglo word** — each carries content the gloss loses; better to leave romanized + brief gloss than translate
- **Missing 圈子 in-group / out-group framing** — TW / PRC / HK regional-circle dynamics matter; a 「我們」 in TW media may silently exclude PRC readers (or vice versa). Read 自家人 / 自己人 invocations against the audience the artifact actually targets
- **Treating WEIRD-sample Goffman defaults as universal** — frontstage / backstage performance model presumes individualized identity; ZH face-as-ledger operates across multi-year reciprocity arcs, not in-the-moment performance
- **Confusing 陰陽 dialectical synthesis with fence-sitting** — Anglo argumentative norms read "both A and B" as evasion; in ZH register this is the position
