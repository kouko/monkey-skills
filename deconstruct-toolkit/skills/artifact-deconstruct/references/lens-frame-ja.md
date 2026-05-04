# Lens: Frame Analysis (Japanese register — Goffman + Lakoff + 建前/本音 + JP conceptual metaphors)

> **Sources**:
> - Erving Goffman, *Frame Analysis: An Essay on the Organization of Experience* (Harper & Row, 1974). Primary frameworks Ch 2; keying Ch 3 (definition p 44 — "an activity already meaningful in terms of some primary framework... transformed into something patterned on this activity but seen... to be quite something else"); fabrications Ch 4; vulnerabilities of experience and frame traps Ch 12.
> - George Lakoff & Mark Johnson, *Metaphors We Live By* (University of Chicago Press, 1980; 2003 afterword edition). Three-type taxonomy (Structural / Orientational / Ontological) introduced in Ch 1; orientational metaphors Ch 4; ontological metaphors Ch 6.
> - 土居健郎 (Doi Takeo), *「甘え」の構造* (弘文堂, 1971). English translation: *The Anatomy of Dependence* (Kodansha International, 1973, trans. John Bester). Canonical analysis of 甘え (amae) as the relational substrate from which 建前 (tatemae) / 本音 (honne) layered communication operates; Ch 3 on the emotional grammar of Japanese social life.
> - 山本七平 (Yamamoto Shichihei), *「空気」の研究* (文藝春秋, 1977). Canonical Japanese-language treatment of 空気 (kūki) as a collective frame-reading mechanism that overrides explicit argument; analyzes wartime decision-making as structurally 空気-driven.
> - Hazel Rose Markus & Shinobu Kitayama, "Culture and the Self: Implications for Cognition, Emotion, and Motivation," *Psychological Review* 98(2), 1991, pp 224-253. Establishes the **interdependent self-construal** characteristic of East Asian (and especially Japanese) contexts vs the **independent self** of WEIRD samples — the underlying frame-orientation difference that motivates dual-frame and 空気 analysis.

> **Synthesis note**: This file combines Goffman's frame analysis (1974), Lakoff & Johnson's conceptual metaphor (1980), Doi (1971), Yamamoto (1977), and Markus & Kitayama (1991). The combination is a methodological choice by `deconstruct-toolkit` — Goffman names the *social frame*, Lakoff names the *cognitive frame*, Doi/Yamamoto name the *layered + collective frame mechanisms* specific to Japanese register, and Markus & Kitayama supply the cross-cultural-psychology grounding for why those mechanisms differ from Anglo register. Not all sources address each other directly. See [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md) and [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md).

> **Cultural-register note**: Goffman's WEIRD frame examples (theater, conversation, deception) translate into Japanese contexts but JP register adds a **dual-frame layer** absent in Goffman — 建前 (public-facing frame) and 本音 (underlying frame) coexist openly and cooperatively, NOT as Goffman's frontstage/backstage split (which presumes a single "real" frame hidden behind a presented one). Lakoff's Anglo conceptual metaphors (UP=GOOD, ARGUMENT=WAR) have JP analogues but JP also carries frame-level metaphors absent from Lakoff's English corpus — 心 (kokoro) as unified heart-mind, 道 (michi/dō) as way-of-being-as-practice, 縁 (en) as karmic-relational tie, 場 (ba) as shared-context-as-frame.

## When to apply this lens

- Japanese political speech (国会演説 / 記者会見 / 党首討論)
- Japanese corporate communication (社長メッセージ / 決算説明会 / 謝罪会見)
- Japanese advertising and brand messaging (テレビCM / 新聞広告 / コーポレートサイト)
- Japanese social-policy and op-ed text (新聞社説 / 政府白書 / 政策提言)
- Japanese interpersonal correspondence in a public-register (ビジネスメール、公開書簡)

## When NOT to apply

- Pure technical reference written in Japanese (API documentation, 製品仕様書) — frame layers collapse in literal-register technical writing
- Translated artifacts (English → Japanese auto-translated marketing copy) — the source frame is Anglo; apply `lens-frame-anglo.md` to the original
- Casual private chat / SNS friend-group register — 建前/本音 layering is contextual; informal peer registers operate closer to a single frame
- Texts where the frame is openly disclosed (peer-reviewed JP academic work in 序論-本論-結論 format usually)

---

## Part 1: Goffman frame baseline (JP register adjustments)

A "frame" is the implicit world-view that makes a text meaningful. Same words inside different frames carry different weight. The Goffman vocabulary still applies in JP register, but each concept needs JP-specific surface signals.

| Concept | Question | JP surface signal |
|---|---|---|
| **Primary framework** | What world-view does the text presume? | Honorific register (敬語 vs 常体), in-group/out-group markers (うち vs そと), seasonal greeting conventions |
| **Keying** | What tone / register is in play? | Honorific shift mid-text (e.g. 丁寧語 → 尊敬語) often signals keying change; 体言止め and 倒置 mark literary-keying |
| **Fabrication** | Is the surface frame ≠ real intent? | In JP this overlaps but is **not identical** to 建前 — see Part 2. Goffman fabrication is strategic deception; 建前 is socially-functional layering |
| **Frame vulnerability / break** | Where does the text expose a frame trap? | 失言 moments (politician slips into 本音), 取材中の沈黙, awkward register shifts |

### Worked move: keying via honorific shift

In Anglo-register, keying is signaled by tone words ("seriously," "no joke"). In JP, keying often signals through **honorific level shift** — the same speaker dropping from 尊敬語 to 常体 mid-utterance frames the next sentence as confidential / 本音-leaking / off-the-record. Detect this before reading content.

---

## Part 2: 建前/本音 dual-frame analysis

The single most distinctive JP frame mechanism. Doi (1971) treats this as the surface expression of 甘え (amae) — the assumed relational substrate that lets two layers coexist without contradiction.

| Layer | Function | Surface signal |
|---|---|---|
| **建前 (tatemae)** | Publicly-acceptable frame; the position the speaker is **expected** to hold given role + audience | Formal register (です・ます・でございます), group-orientation language (我々 / 弊社 / 当方), deference markers (恐れ入りますが / 申し訳ございませんが), abstract nominalizations (〜という方向で / 〜の所存です) |
| **本音 (honne)** | Underlying personal frame; what the speaker actually thinks / feels / would do | Informal register (だ・である or plain 〜です), hedge words (まあ / 正直 / 本当のところ), modal-particle hesitation (〜けど / 〜なんですけど / 〜かな), strategic omission, 婉曲 leak phrases (〜とも言えなくはないですが) |

### Detecting 本音 leakage

The analytical move is **not** "find the lie" — it is "find where the 建前 layer thins and 本音 leaks through." Common leak signals:

1. **婉曲 leak** — the speaker reaches for an indirect phrase that hints at a position they cannot openly hold (「個人的には」「立場上は申し上げられませんが」).
2. **Modal-particle hesitation** — 〜けど / 〜なんですけど trailing off without completion. The unfinished sentence carries the 本音.
3. **Strategic omission** — a topic is conspicuously not addressed. Goffman would call this frame avoidance; in JP it is 触れない作法 and is itself frame-load-bearing.
4. **Honorific drop** — speaker briefly dropping 尊敬語 to 常体 in a parenthetical, then returning. The dropped segment is the 本音 register.
5. **Reported-speech buffer** — placing the 本音 in a quoted source ("〜という意見もあるようですが") to deniably surface it.

### Important: 建前 is NOT deception

A common Anglo-register error is reading 建前 as Goffman fabrication (strategic deception). In JP register, 建前 is **social-functional layering**, not lying. Both speaker and listener know the 建前 is the 建前. The honesty contract operates at a different level: speaker is honestly performing the role-appropriate position; listener is honestly receiving it as such; both understand 本音 may differ. Reading 建前 as deception imports an Anglo single-frame assumption that the JP register does not share. (Doi 1971, Ch 3, treats this as the 甘え-rooted assumption that role-appropriate layering is itself a form of relational honesty.)

---

## Part 3: 空気 (kūki) — collective-frame reading

Yamamoto (1977) frames 空気 as the situation where the collective frame-reading **overrides** explicit argument: a decision feels already made before anyone states it; dissenting analytical content cannot land because "空気が許さない." This is a frame phenomenon, not just social pressure.

### Surface signals that 空気 is doing the persuasive work

- **Pre-emptive consensus markers**: 〜ですよね / 〜ということで / 皆さんもご存じのとおり (presupposes shared frame before establishing it)
- **Vagueness as politeness**: a key claim is left structurally unstated; the audience is expected to fill it in via 空気
- **Conspicuous silence on a topic**: the unaddressed question is the load-bearing one
- **Group-affect appeals**: 我が国の / 国民の皆様の / 当社一同の — invokes a unified collective frame and discourages individual frame-challenge
- **Repetition without elaboration**: a phrase ("丁寧な説明") is repeated as 空気-anchor without semantic development; the repetition itself is the frame work

The analytical move: ask **"what is 空気 doing here that explicit argument is not?"** — the gap between the collective frame and the stated argument is where the persuasion lives. Yamamoto's wartime case studies (1977 Ch 1-2) show that 空気-driven decisions feel inevitable to participants and only become visible as frame-work in retrospect.

---

## Part 4: 間 (ma) — silence and negative space as frame element

In JP register, **silence is structurally meaningful**. Pauses, ellipses, 「…」, the held beat after a question — these are not gaps in the frame but **part of the frame**. In political press conferences, the speaker's 間 between question and answer signals frame-shift, hesitation, or 本音 surfacing. In business 謝罪会見, the bow's duration (お辞儀の長さ) is itself a frame-load-bearing variable. 剣持武彦『「間」の日本文化』(朝日新聞社) treats 間 as the structural negative space common to noh, calligraphy, conversation, and architecture; the same logic governs JP frame analysis. When deconstructing JP artifacts, **annotate the silences** — they are not absent content, they are present frame.

---

## Part 5: JP conceptual metaphors not in Lakoff's Anglo corpus

Lakoff's *Metaphors We Live By* sources its conceptual-metaphor inventory from English. Some metaphors transfer (TIME IS MONEY, ARGUMENT IS WAR appear in JP business register too). But JP carries primary metaphors that have no clean Anglo equivalent and that frame-analysis must surface.

| JP concept | Metaphor type | Surface signal | Anglo gap |
|---|---|---|---|
| **心 (kokoro)** | Heart-mind unity (no Cartesian body/mind dualism) | 「心が痛む」「心がこもる」「心を込めて」「真心」 | Anglo distinguishes head (cognition) from heart (emotion); 心 fuses them, so JP claims about 心 carry both registers simultaneously |
| **道 (michi / dō)** | Way-as-embodied-practice (vs. path-as-route) | 「〜の道」「道を究める」「道半ば」「武士道」「茶道」 | Anglo "path" is destination-oriented; 道 carries lifetime-practice + ethical-discipline + master-apprentice transmission, not just a route |
| **縁 (en)** | Karmic-relational tie (involuntary, non-transactional) | 「ご縁があれば」「縁がない」「腐れ縁」 | No direct Anglo equivalent; "connection" / "fate" / "rapport" each carry only a fragment |
| **場 (ba)** | Shared-context-as-frame | 「その場の空気」「場を読む」「場違い」「場をわきまえる」 | Overlaps Goffman frame but pre-Goffman in JP intellectual history; Nishida 西田幾多郎 develops 場所 (basho) philosophically pre-1945 |

### Pitfall

Forcing JP artifacts into Lakoff's Anglo metaphor inventory (UP=GOOD, ARGUMENT=WAR, TIME=MONEY) misses the frame-level metaphors above. A JP corporate apology that frames the company as walking 「再生への道」 is doing 道-metaphor work; reading it through Anglo "journey metaphor" loses the lifetime-practice + ethical-discipline weight. A JP politician invoking 「ご縁」 with a constituency is doing 縁-metaphor work that Anglo "connection" reading flattens.

---

## Worked example

A fictional but realistic JP corporate press conference snippet (謝罪会見 register) on a product-quality issue:

> 「えー、本日はお忙しい中お集まりいただき、誠にありがとうございます。
> このたびは、弊社製品におきまして、お客様にご不便をおかけする事態となり、
> 心よりお詫び申し上げます……（深く一礼、約 5 秒）。
> 原因につきましては、現在、第三者委員会を含めて鋭意調査中でございまして、
> 詳細につきましては、まあ、現時点では申し上げられないところもあるんですけれども、
> 弊社一同、再発防止に向けて、丁寧な説明と誠意ある対応に、その、努めてまいる所存でございます。」

**Goffman-only reading** would catch: formal keying, fabrication suspicion ("rigorously investigating" as boilerplate), frame break around the modal hedge. Misses: the 5-second bow, the 〜ですけれども trail-off, the 心 invocation, the 「丁寧な説明」 空気-anchor.

**Lakoff-only reading** would catch: ARGUMENT IS WAR is absent (which is itself notable); abstract nominalization. Misses: 心より (心 metaphor), 道-adjacent 「努めてまいる所存」 (practice-as-way), the 場 of the press conference itself as frame.

**Full JP-register reading** catches:

- **Goffman frame baseline**: primary frame is 謝罪会見 (apology press conference); keying shifts twice (formal opening → hedged middle → 所存 closing); no overt fabrication but 詳細...申し上げられない is a frame-restriction declaration
- **建前/本音 dual-frame**: 建前 layer = formal apology in です・ます; 本音 leaks at まあ and 〜なんですけれども; the 申し上げられないところもある is buffered 本音 (we know more than we can say)
- **空気 deployment**: 「丁寧な説明」「誠意ある対応」 are 空気-anchor phrases — repeated apology vocabulary that creates a collective frame of "the company is being responsible" without committing to specifics
- **間 work**: the 5-second bow is the heaviest frame element in the whole utterance; absence of 間 (a quick perfunctory bow) would have collapsed the frame entirely
- **JP conceptual metaphors**: 心より (heart-mind unity invoked to authenticate the apology); 努めてまいる所存 carries 道-metaphor weight (commitment-as-ongoing-practice); 弊社一同 invokes 場 (the unified 場 of the company)

The 5-second bow + the まあ trail-off + 「丁寧な説明」 repetition do at least half the frame work, and Anglo-only lenses miss all three.

---

## Combining Goffman + Lakoff + JP frame mechanisms

A strong JP frame analysis names:

1. The **Goffman social frame** (what kind of situation does this text assume — 謝罪会見 / 決算説明会 / 党首討論 / 社長年頭挨拶);
2. The **建前/本音 layered frame** (what is the public position; where does the underlying position leak);
3. The **空気 + 間 collective-frame moves** (where is collective frame doing the persuasion; what silences are load-bearing);
4. The **JP conceptual metaphors at work** (心 / 道 / 縁 / 場 — and any Anglo metaphors mapped onto them).

## Output format

```markdown
### Goffman frame baseline
- Primary framework: ...
- Keying (incl. honorific shifts): ...
- Fabrication (Goffman sense) detected? <yes / no — describe>
- Frame break(s): ...

### 建前/本音 dual-frame
- 建前 layer (public position): ...
- 本音 leakage signals: <婉曲 / 〜けど trail-off / honorific drop / strategic omission / reported-speech buffer>
- Reading: <where the public position thins>

### 空気 + 間 collective-frame moves
- 空気-anchor phrases: ...
- Conspicuous silences / 触れない: ...
- 間 elements (pauses, bows, ellipses): ...
- Reading: <what 空気 + 間 are doing that explicit argument is not>

### JP conceptual metaphors at work
- 心 / 道 / 縁 / 場 invocations: ...
- Anglo metaphors mapped on (war / journey / etc.): ...
- Reframe alternative: ... (what changes with a different metaphor)
```

End with 1-line synthesis: "The text positions the reader inside a **X** frame, performs **建前 Y** while leaking **本音 Z** at **W**, deploys **空気** through **V**, and grounds in **心/道/縁/場 metaphor U**."

---

## Pitfalls

- **Treating 建前 as deception** — it is social-functional layering, not strategic lying. Both parties know the layering is in play. Imports an Anglo single-frame assumption.
- **Forcing JP conceptual metaphors into Lakoff's Anglo corpus** (UP=GOOD, ARGUMENT=WAR) — JP has its own primary metaphors (心 / 道 / 縁 / 場) that frame analysis must surface in their own terms.
- **Missing 間 (silence as frame)** — pauses, bows, 「…」 are frame-load-bearing in JP register. Anglo-trained analysis treats silence as absence of content.
- **Reducing 空気 to "social pressure"** — it is a collective frame-reading mechanism per Yamamoto (1977), structurally distinct from peer-pressure. The persuasive work happens at frame level, not at compliance level.
- **Over-applying 建前/本音 to literal-register technical writing** — frame layers vary by genre; an API spec or product datasheet does not carry the same dual-frame load as a press conference or political speech. Match the analytical move to the register.
- **Reading honorific shifts as politeness only** — they are also frame-keying signals; a 尊敬語 → 常体 drop usually marks a frame move, not just a register slip.

## Cross-variant pointer

The same phenomenon — frame layering — is operationalized differently across variants:

- `lens-frame-anglo.md` treats frame layering as Goffman frontstage/backstage (single real frame hidden behind a presented one).
- `lens-frame-ja.md` (this file) treats it as 建前/本音 (two coexisting frames, both honest in their layer).
- `lens-frame-zh.md` treats it through 給面子 / 面子 (face-work as identity-frame in a relational matrix), which overlaps but is not identical to 建前/本音.

When analyzing a multi-language artifact, apply the variant matching the artifact's primary register, and note in the synthesis where the cross-variant readings would differ.
