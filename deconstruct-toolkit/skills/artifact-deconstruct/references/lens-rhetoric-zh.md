# Lens: Rhetorical Analysis (Chinese tradition — 文心雕龍 六觀)

> **Sources**:
> - 劉勰 (Liú Xié, c. 465–c. 532 CE)《文心雕龍·知音》篇 (*Wénxīn Diāolóng*, "The Literary Mind and the Carving of Dragons," ch. 48 「知音」"Zhī Yīn / The One Who Knows the Tones"), composed during the 南朝梁 (Southern Liang) dynasty, late 5th–early 6th century CE. The 六觀 (liù guān, "six perspectives / six observations") framework is stated in the chapter's prescriptive core: 「是以將閱文情，先標六觀：一觀位體，二觀置辭，三觀通變，四觀奇正，五觀事義，六觀宮商。斯術既形，則優劣見矣。」
> - Standard modern critical editions: 周振甫《文心雕龍注釋》(里仁書局, 1984); 王運熙、周鋒《文心雕龍譯注》(上海古籍出版社, 1998; 2012 reissue, 國學經典譯注叢書).
> - English-language scholarship: Cai Zong-qi (ed.), *A Chinese Literary Mind: Culture, Creativity, and Rhetoric in Wenxin Diaolong* (Stanford University Press, 2001).

> **Synthesis note**: 六觀 is a 1,500-year-old framework originally formulated for *literary* criticism (poetry, rhapsody 賦, classical prose). This file extends it to general artifact analysis as a methodological choice by `deconstruct-toolkit`, on the grounds that 劉勰 himself treats the framework as a general rubric for assessing any verbal artefact's craft. Modern Chinese-language academic and op-ed writing typically uses the Western-influenced 緒論-本論-結論 (xùlùn / běnlùn / jiélùn — introduction / main body / conclusion) macro-structure; the 六觀 lens still applies inside that container. Per [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md), this extension-of-scope is disclosed explicitly so the reader can judge fit.

> **Cultural register note**: The Chinese rhetoric tradition is fundamentally **relational** — excellence is measured by an artefact's relation to the canon (allusion / 事義), to genre tradition (位體 + 通變), and to cosmic-aesthetic proportion (宮商). This differs sharply from Anglo Toulmin warrant-based logic, where excellence is measured by the *defensibility of the inferential leap from grounds to claim*. A skilled ZH artefact may be considered rhetorically *excellent* while bypassing a Toulmin-style warrant entirely — because its authority comes from precedent-borrowing (用典) and genre-fidelity (體製) rather than from explicit warrant defense. Imposing Anglo warrant-checking on a ZH op-ed misreads the artefact's claim to authority.

---

## When to apply this lens

- Chinese-language op-eds (社論 / 評論), columns, manifestos — especially literary or political register
- Classical-literary register: 散文 / 雜文 / 隨筆 / 序跋
- Political speeches in the ZH tradition (TW / HK / PRC) — heavy 用典 + 排比
- Long-form ZH cultural criticism, public letters (公開信)
- Any ZH artefact where the author is performing membership in a literary lineage

## When NOT to apply

- Modern technical / engineering / scientific ZH writing — these consciously adopt Western conventions; lens-rhetoric-anglo lighter pass is more apt
- Modern ZH business writing in TW / HK targeting international audiences — often Western-moves dominant
- ZH translations of Anglo originals — the source register is Anglo; analyse against -anglo, then note any TW/HK localisation moves separately
- ZH consumer marketing / e-commerce copy — better served by `lens-persuasion-zh.md` (Cialdini + face/guanxi)
- Single-line headlines / taglines — too short for genre-positioning analysis

---

## Part 1: 六觀 (The Six Perspectives)

劉勰's six-point rubric for assessing any verbal artefact. Each 觀 (guān, "to observe / a perspective") asks one structured question.

| 觀 | What it surfaces | Question to ask the artefact |
|---|---|---|
| **位體** (wèitǐ, "positioning of form / genre placement") | genre + register positioning | What genre tradition does this claim membership in? What are the formal expectations of that genre, and does the artefact honour or strain them? |
| **置辭** (zhìcí, "deployment of phrasing") | phrasing / lexical choices / diction | What word-choice register does the prose use (literary 文言 leaning, colloquial 白話, journalistic, literary-modern)? What does the diction signal about intended audience and the author's self-positioning? |
| **通變** (tōngbiàn, "continuity-and-change") | tradition-innovation balance | What is preserved from the genre's tradition? What is updated for the present moment? Is the balance proportional, or does the artefact lean too far into either antiquarianism (all 通, no 變) or novelty (all 變, no 通)? |
| **奇正** (qízhèng, "the unconventional and the orthodox") | innovation-vs-orthodoxy stylistic axis | Is the work hewing close to canonical norms (正, "correct / orthodox") or pushing convention (奇, "unusual / striking")? Is the 奇 earned by mastery of 正, or is it novelty without grounding? |
| **事義** (shìyì, "events and their significance / use of precedent") | allusion / use of precedent | What earlier texts, historical figures, or canonical events are invoked? What is the citational economy — are allusions decorative, structurally load-bearing, or doing argumentative work the artefact never makes explicit? |
| **宮商** (gōngshāng, "gong and shang notes" — by extension, prose rhythm) | rhythm / sound / cadence | What is the prose rhythm? Where does cadence accelerate (短句 staccato), where does it pause (長句 / 對偶 balance)? Are tonal patterns (平仄) used? Does sound reinforce or undercut sense? |

### How to apply 六觀 to a non-classical artefact

The original frame was 5th-century literary; for modern artefacts, treat each 觀 as a question about *craft*, not a test for canonical compliance:

- **位體** — substitute "what modern genre is this?" (op-ed / manifesto / brand essay / 雜文)
- **置辭** — what register does word-choice signal? (e.g. mixing 文言 phrases into a modern op-ed signals authorial pretension to the literary lineage)
- **通變** — what's the artefact's stance toward its genre's history?
- **奇正** — is the unusual move a flourish on top of mastery, or a substitute for it?
- **事義** — modern allusions count: 引用 (yǐnyòng, direct quotation) of 魯迅 / 余光中 / 龍應台 / 柏楊 is the contemporary equivalent of 用典
- **宮商** — modern ZH prose rhythm is real, especially in 社論 register. Listen to the sentence-length pattern.

---

## Part 2: ZH-specific moves not captured by Anglo lens

Surfaces that an Anglo-Toulmin-Burke pass will systematically miss in ZH artefacts:

- **對偶** (duì'ǒu, "parallelism / parallel-couplet structure") — *Where does the artefact deploy syntactically-mirrored clause pairs? Are the parallels load-bearing (carrying argument) or ornamental (carrying register)?*
- **排比** (páibǐ, "anaphoric series / triadic-or-greater repetition") — *Where do you see 3+ structurally-parallel clauses or sentences? In ZH political register, 排比 often performs the work that Anglo argument assigns to enumerated bullet points — its presence is rhetorical, not just stylistic.*
- **比興** (bǐxìng, "metaphor-as-evocation / image-as-mood-trigger") — *What concrete image opens or anchors the piece? In the 詩經 tradition 興 evokes mood before claim is made; modern op-eds often open with an image or scene that pre-shapes the reader's interpretive stance before the explicit thesis appears.*
- **用典** (yòngdiǎn, "use of allusion / borrowing-from-precedent") — *What canonical text or historical figure is invoked, and what authority is being borrowed? In ZH register 用典 functions as authority-borrowing equivalent to Toulmin's "backing" — but the borrowed authority is the canon itself, not an empirical study.*

---

## Part 3: Mode selection — when to apply full 六觀 vs lighter pass

ZH artefacts span a wide register. Match analytical depth to register:

| Register | Mode | Notes |
|---|---|---|
| Literary / 雜文 / 散文 / 序跋 | **Full 六觀** | All 6 觀 + Part 2 ZH-specific moves; 用典 + 對偶 likely heavy |
| Political speech / 社論 / op-ed | **Full 六觀, weighted 事義 + 通變 + 宮商** | 排比 + 用典 doing political work |
| Modern academic 緒論-本論-結論 ZH paper | **Lighter pass: 位體 + 置辭 + 事義** | Genre is Western-influenced; full 六觀 over-fits |
| Business writing TW / HK targeting domestic audience | **Lighter pass + Anglo-influenced moves** | Apply -anglo Toulmin lens *and* 用典 / 排比 detection |
| Translated-from-Anglo content | **-anglo first, then check 置辭 for localisation** | Don't apply full 六觀 — register is borrowed |

### TW / HK / PRC variation

- **TW (zh-TW)**: 繁體 register; modern academic + journalism heavily influenced by JP-via-Meiji conduits as well as direct Anglo influence; literary register preserves 文言 markers more than PRC
- **HK (zh-HK)**: distinct register mixing 文言 + 粵語 + Anglo-business calques; political writing in the post-2020 period has its own coded register
- **PRC (zh-CN)**: 簡體 register; 党八股 (officialese) is its own distinct genre with formulaic 排比 and 用典 structure; 自媒體 (we-media) register diverges sharply from 黨報 register

For zh-TW analysis (the maintainer's primary register), default register assumptions follow TW academic + 聯合報 / 中時 op-ed conventions.

---

## Worked example (zh-TW op-ed paragraph)

A representative 社論 paragraph (synthesised composite, illustrative not from any single real op-ed):

> 「台灣半導體產業之所以能立於世界，不在於我們發明了什麼，而在於我們守住了什麼。三十年磨一劍，從竹科到南科，從工程師的加班燈到夜半實驗室的茶香——這不是奇蹟，這是日日的守成。古人云：『不積跬步，無以至千里』；今日我們所站的高處，正是無數個未眠之夜累積而成。」

Applying 六觀:

- **位體**: 社論 register, performing the "industrial-policy reflection" sub-genre; claims membership in the lineage of TW newspaper editorials that frame economic events as moral narratives.
- **置辭**: literary-leaning modern ZH — 「立於世界」「守成」「守住了什麼」are 文言-flavoured choices over plain 「站穩」「保持」; signals seriousness and addresses an educated readership.
- **通變**: preserves the classical move of grounding present-day argument in 古訓 (古人云); updates by attaching that move to a modern industrial subject (semiconductors, 竹科 / 南科).
- **奇正**: 正 dominates — the structure is canonical 社論 pattern; the only 奇 move is the sensory image 「夜半實驗室的茶香」inserted between abstract clauses.
- **事義**: invokes 《荀子·勸學》(「不積跬步，無以至千里」) as authority — 用典 is doing the argumentative heavy lifting. The implicit warrant ("守成 is virtuous because the canon says incremental accumulation reaches 千里") is borrowed from the canon, not defended on its own terms.
- **宮商**: rhythm is balanced — 「從竹科到南科，從工程師的加班燈到夜半實驗室的茶香」is a 排比 triad with accelerating-then-pausing cadence; the closing 古文 quotation breaks the modern rhythm, signalling that the argument is now resting on canonical authority.

**ZH-specific moves**:
- 對偶: 「不在於我們發明了什麼，而在於我們守住了什麼」(antithetical couplet)
- 排比: 「從竹科到南科，從工程師的加班燈到夜半實驗室的茶香」(triadic series)
- 比興: opens with abstract claim, pivots to sensory image (茶香) to evoke mood
- 用典: 《荀子》quotation transferred wholesale as backing

**Synthesis**: the paragraph's persuasive force comes from genre-fidelity (位體 正) + canonical authority-borrowing (事義 / 用典) + cadence (宮商 排比), not from a defended warrant. An Anglo-Toulmin pass would flag "warrant undefended" — but in the ZH register, the warrant is *the canon itself*, and challenging it requires challenging the canon's authority, which is a different kind of move than a Toulmin rebuttal.

---

## Output format

```markdown
### 六觀 analysis
| 觀 | Finding |
|---|---|
| 位體 | <genre claimed + how strained / honoured> |
| 置辭 | <register diagnosis from diction> |
| 通變 | <tradition-vs-update balance> |
| 奇正 | <orthodox or unusual; 奇 earned or unearned> |
| 事義 | <allusions + what authority is borrowed> |
| 宮商 | <prose rhythm + cadence pattern> |

### ZH-specific moves
- 對偶: <where + load-bearing or ornamental>
- 排比: <where + triadic / quadratic / longer; what work it does>
- 比興: <opening image / mood-pre-shaping>
- 用典: <which canonical source + what authority is borrowed>

### Mode + register
- Mode applied: <full 六觀 / lighter pass>
- Register: <literary / 社論 / academic / business / translated>
- Variant: <zh-TW / zh-HK / zh-CN>
```

End with a 1-2 sentence synthesis: "The artefact's authority comes from `<位體 + 事義 + 宮商>`; the move that an Anglo lens would mis-flag is `<X>`, which in ZH register is `<canonical-authority / genre-fidelity / rhythmic-completion>` not `<undefended warrant>`."

---

## Pitfalls

- **Mapping 通變 onto "precedent" alone**. 通變 is *balance* between continuity and change, not just citation. An artefact that only preserves (all 通) fails 通變 just as an artefact that only innovates (all 變) does. The lens question is *proportion*, not *presence*.
- **Treating 用典 as decorative**. In ZH register 用典 is authority-borrowing equivalent to Toulmin's *backing*. If you skip it as "ornament" you miss where the argument's weight is actually being carried.
- **Applying full 六觀 to modern technical writing**. ZH technical / scientific / engineering prose consciously adopts Western register; full 六觀 over-fits and produces false findings ("低 用典!" — yes, that's the genre). Use the lighter pass per Part 3.
- **Confusing TW / HK / PRC register conventions**. 党八股 (PRC officialese) and TW 社論 share some surface features (排比, 用典) but the function of those features differs sharply. Mark register variant explicitly before analysing.
- **Imposing Anglo warrant-checking as the default rubric**. ZH excellence often bypasses explicit warrant defense in favour of canonical-authority borrowing. Flagging this as a weakness reveals lens-misfit, not artefact-flaw.
- **Reading 文言 borrowings as antiquarian affectation**. In modern ZH op-ed register, selective 文言 diction is a *register signal* (educated, serious, literary-aware), comparable to how Anglo journalism uses Latinate vocabulary. Read it as register-positioning, not as failure-to-modernise.
- **Forcing 比興 where there is none**. Not every ZH op-ed opens with image-as-mood. Modern journalistic register often opens with a hard-news lead. Don't invent 比興.

## See also

- [`lens-rhetoric.md`](lens-rhetoric.md) — universal-core router
- [`lens-rhetoric-anglo.md`](lens-rhetoric-anglo.md) — Toulmin + Burke variant; useful for translated content or TW/HK business register with Anglo influence
- [`lens-rhetoric-ja.md`](lens-rhetoric-ja.md) — Japanese variant (Hinds + kishōtenketsu); useful for comparing ZH and JP East Asian rhetoric traditions
- [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md) — cultural-lens-variant pattern
- Sister lenses with ZH variants: `lens-persuasion-zh.md` (面子 / 關係 + Cialdini), `lens-genre-zh.md` (緒論-本論-結論 / 公文), `lens-frame-zh.md` (面子 / 陰陽 / 集體)
