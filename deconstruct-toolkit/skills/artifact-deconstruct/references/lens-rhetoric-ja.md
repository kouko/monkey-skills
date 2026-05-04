# Lens: Rhetorical Analysis (Japanese tradition — Hinds + kishōtenketsu)

> **Sources**:
> - John Hinds, "Contrastive Rhetoric: Japanese and English," *Text — Interdisciplinary Journal for the Study of Discourse*, vol. 3, no. 2 (1983), pp. 183–196 (Mouton de Gruyter). DOI 10.1515/text.1.1983.3.2.183. Establishes 起承転結 (kishōtenketsu) as the canonical 4-part organizational pattern in Japanese expository prose and argues English readers misread it as "digressive" because they expect inductive or deductive paragraph order.
> - John Hinds, "Reader versus Writer Responsibility: A New Typology," in Ulla Connor & Robert B. Kaplan (eds.), *Writing Across Languages: Analysis of L2 Texts* (Reading, MA: Addison-Wesley, 1987), pp. 141–152. Introduces the *reader-responsible* vs *writer-responsible* typology: in writer-responsible languages (English) the writer must make transitions and warrants explicit; in reader-responsible languages (Japanese) the reader is expected to bridge gaps, and explicit signposting is read as condescension.
> - Gabriel Oh, "Kishōtenketsu and Its Potential Applications to Prose Writing," *TEXT* (Australia), vol. 29, no. 2 (2025) — open-access at textjournal.scholasticahq.com. Reads contemporary Japanese novels (Eto Mori *Colorful*, Emi Yagi *A Diary of a Void*) to argue that kishōtenketsu is not a conflict-driven Aristotelian arc but an *inductive* structure where 転 (turn) introduces a juxtaposed element that recontextualizes 起 + 承 without resolving them through victory/defeat.

> **Synthesis note**: This file combines (a) kishōtenketsu as a literary/op-ed organizational pattern (classical Sinitic origin via 漢詩 absolute verse, naturalized in Japanese expository tradition); (b) Hinds' reader-responsibility typology (linguistic-pragmatic, 1983/1987); and (c) the modern Japanese academic 序論-本論-結論 (jōron-honron-ketsuron) hybrid documented in handbooks such as 甲田直美『大学で学ぶアカデミック・ライティングの教科書』(ひつじ書房). The three were not co-developed and target different registers. Combining them is a methodological choice by `deconstruct-toolkit` — register-aware analysis requires switching between modes within a single artifact. See [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md) and [ADR-0004](../../../docs/adr/0004-cultural-lens-variants.md).

> **Cultural register note**: Japanese rhetoric resolved a different problem than the Anglo tradition. Per Hinds (1987), Japanese is *reader-responsible*: the writer leaves space, the reader infers. The absence of an explicit thesis statement, the absence of an explicit warrant, and the use of 婉曲表現 (en'kyoku hyōgen, "indirect / softened expression") are **features, not defects**, in the Japanese register. Applying Toulmin's "surface the hidden warrant" move directly to a Japanese op-ed will systematically misread virtuous indirection as evasive logic. Use this lens, not the Anglo one, when the artifact's source register is Japanese.

---

## When to apply this lens

- Japanese-language op-eds, 社説 (newspaper editorials), コラム (columns), 解説 (explanatory pieces)
- Japanese political 演説 (speeches), 所信表明 (policy statements)
- Japanese long-form 論考 (essays), business 論文, 企画書 prose sections
- Translated-from-Japanese English text where the underlying structure is still 起承転結 (translation does not flatten rhetoric)
- Japanese academic papers — but switch to 序論-本論-結論 mode (Part 3 below)

## When NOT to apply

- English-original artifacts even if topic is "Japan-related" — use `lens-rhetoric-anglo.md`
- Pure-narrative Japanese fiction without persuasive intent — kishōtenketsu describes structure but rhetoric-as-deconstruction needs an argument target
- Single-line tagline / short copywriting — needs a different lens (see `lens-persuasion-ja.md`)
- Modern Japanese academic writing in STEM (almost universally adopts 序論-本論-結論 IMRaD-style) — Part 3 mode, not Part 1

---

## Part 1: 起承転結 (kishōtenketsu) — the 4-part structure

Origin: classical Chinese 絶句 (jueju, 4-line absolute verse). Naturalized in Japanese expository prose, op-eds, business memos, and literary fiction. The defining feature versus Aristotelian / Toulmin structure: **転 is not a climax-of-conflict; it is a juxtaposition that reframes the reader.** Per Oh (2025), kishōtenketsu is *inductive* — meaning emerges from the relationship between 転 and the preceding 起+承, not from resolution of a conflict introduced in 起.

| Part | Reading | What it does | Analytical question |
|---|---|---|---|
| **起** | ki — "introduce / raise" | Establishes the topic, situation, or premise. Often deceptively concrete. | What world is the reader being placed into? What is presented as given? |
| **承** | shō — "develop / receive" | Extends 起. Adds detail, depth, examples. Reader settles in. | What does 承 add that 起 alone did not? Does it accumulate evidence, or just elaborate atmosphere? |
| **転** | ten — "turn / pivot" | Introduces an apparently unrelated element, viewpoint shift, or counter-image. **The argumentative unit lives here.** | What is being juxtaposed against 起+承? Is the new element factual, emotional, or perspectival? Does it contradict, complicate, or simply reframe? |
| **結** | ketsu — "conclude / tie" | Resolves the juxtaposition by showing what 起+承 and 転 mean *together*. Frequently leaves the explicit claim unstated. | What relationship between 起+承 and 転 does 結 propose? Is the claim stated, implied, or left to the reader? |

### How 転 functions as the argumentative unit (vs Toulmin warrant)

In the Anglo Toulmin model, the warrant is a *bridging proposition* — "because X is true of all cases of this type, the grounds support the claim." The reader is asked to validate logical entailment.

In kishōtenketsu, 転 is *not* a warrant. It is a juxtaposed element whose relevance is initially unclear. The argumentative move is to make the reader *feel* the relevance and supply the bridge themselves. The "claim" of the piece is whatever connection the reader is led to construct — and skilled writers leave multiple valid connections accessible.

This is why kishōtenketsu artifacts often appear "claim-less" to Anglo readers: there is no thesis sentence, no "therefore." The conclusion is the *configuration* of 起+承+転+結, not a proposition extractable from any one of them.

### Worked example: 5-sentence newspaper op-ed (synthetic-representative)

> 起 ：少子化が進み、地方の小学校の統廃合が相次いでいる。
> 承 ：今年度だけで全国百校以上が閉校予定で、跡地の利用方針も定まらない自治体が多い。
> 転 ：先日訪れた長野の山間部では、閉校した木造校舎を改装した小さなパン屋に、地元住民が朝早くから列をなしていた。
> 結 ：失われたのは校舎ではなく、人々が集まる理由なのかもしれない。

- **起**: Demographic decline → school closures (premise, given as fact).
- **承**: Quantitative extension — 100+ closures, no clear repurposing plan (accumulates the problem space).
- **転**: A specific scene — a converted bakery, residents queuing at dawn (juxtaposition: not a logical counter-claim, an *image* of community gathering).
- **結**: Reframes what was lost — not the building, but the *reason for gathering* (claim is implied, not asserted; "perhaps" / かもしれない softens it further).

A Toulmin reading would mis-tag this as "missing warrant + missing rebuttal." The correct Japanese-register reading: 転 supplied the persuasive force by image-juxtaposition, and 結 named the reframe at exactly the indirection level the register requires.

---

## Part 2: Hinds reader-responsibility analysis

Per Hinds (1987), Japanese discourse is *reader-responsible*: comprehension burden sits with the reader. The writer's job is to provide enough material; the reader's job is to construct the connection. Surface signals of this register — which Anglo-trained readers reflexively flag as defects — are functioning correctly when present.

| Signal | Anglo reading | JP-register reading |
|---|---|---|
| **No explicit topic sentence** | "Writer buried the lede" | Topic emerges from 起+承; pre-stating it would patronize the reader |
| **No explicit warrant linking grounds to claim** | "Hidden assumption — surface it" | Bridge is reader's to construct from 転; making it explicit would foreclose interpretation |
| **Paragraph-level 転 move (sudden topic shift)** | "Digression / non-sequitur" | Standard kishōtenketsu pivot; juxtaposition is the argument |
| **婉曲表現 — かもしれない / と言えるだろう / のではないか** | "Hedging / lack of conviction" | Conventional softening; in JP register, an unhedged claim reads as crude or even rude |
| **Conclusion that doesn't name the claim** | "Failed to deliver" | 結 proposes a relationship; the *claim* is the relationship, not a proposition |

### Procedure

1. Mark the 4 parts (起 / 承 / 転 / 結) in the artifact, even if paragraph boundaries don't align cleanly. Note where 転 sits — it can occupy a single sentence or an entire paragraph.
2. For each of the 5 surface signals above, locate occurrences. Tally them.
3. Resist the impulse to "translate" the artifact into Toulmin form. Ask instead: what does each signal *do* for the reader-writer contract this register assumes?
4. If you must surface a "claim" (because downstream analysis demands one), state it as the *relationship 結 proposes*, not as a proposition extracted from any single sentence.

---

## Part 3: Mode selection — academic vs literary register

Modern Japanese academic writing has largely adopted the Western 序論-本論-結論 (jōron-honron-ketsuron, "introduction-body-conclusion") tripartite structure, especially in STEM and social-science papers since the post-war 学術論文 reforms. This is documented in modern academic-writing handbooks (e.g. 甲田直美『大学で学ぶアカデミック・ライティングの教科書』ひつじ書房) and discussed in Hinds' contrastive work as the academic exception to the literary 起承転結 norm.

| Register | Default mode | Apply |
|---|---|---|
| 社説 / コラム / op-ed / 随筆 | 起承転結 | Part 1 + Part 2 (this file) |
| 政治演説 / 所信表明 | 起承転結 (often with rhetorical inversions) | Part 1 + Part 2 |
| 企画書 prose / 提案書 narrative | Mixed — body often 序論-本論-結論, sections may use 起承転結 internally | Part 1 + Part 2 for sections; Part 3 for overall |
| 学術論文 (humanities) | Mixed — often 序論-本論-結論 with 起承転結 in introductions | Mostly Part 3; check intro for Part 1 |
| 学術論文 (STEM / social sciences) | 序論-本論-結論 (IMRaD) | **Use `lens-rhetoric-anglo.md` (Toulmin)** — modern JP academic STEM is functionally Anglo-rhetorical |
| ビジネスメール / 公文書 | Formula-driven (拝啓 / 時候 / 主文 / 末文 / 敬具) | See `lens-genre-ja.md` — not this lens |

**Rule of thumb**: if the artifact has explicit 序論 / 本論 / 結論 section headings (or numbered sections that map to them), apply Anglo Toulmin analysis. The author has chosen the writer-responsible contract.

---

## Output format

```markdown
### Mode selected
- 起承転結 mode / 序論-本論-結論 mode / mixed
- Reason: <register cue that triggered the choice>

### Kishōtenketsu structure
- 起 (introduce): <text span / 1-line summary>
- 承 (develop): <text span / 1-line summary>
- 転 (turn): <text span / 1-line summary>
- 結 (conclude): <text span / 1-line summary>
- **What 転 juxtaposes against 起+承**: <description>
- **Relationship 結 proposes** (the implicit claim): <1 sentence>

### Reader-responsibility surface
| Signal | Present? | Notes |
|---|---|---|
| No explicit topic sentence | yes/no | ... |
| No explicit warrant | yes/no | ... |
| Paragraph-level 転 move | yes/no | ... |
| 婉曲表現 hedges | count + examples | ... |
| Claim left to reader | yes/no | ... |

### Synthesis (1 line)
The artifact uses <mode> register; persuasive force lives in <転 juxtaposition / 序論 framing / both>; the implicit claim is <X>, accessed by reader via <surface signal Y>.
```

If the artifact is in 序論-本論-結論 mode (Part 3 trigger), additionally apply `lens-rhetoric-anglo.md` Toulmin analysis to the 本論 section and report both.

## Pitfalls

- **Treating absence of explicit warrant as a defect.** It's a feature in JP register. Per Hinds (1987), explicit warrants are *condescending* in reader-responsible discourse. The deconstruction is to name what the reader is being asked to bridge, not to flag the bridge as missing.
- **Forcing 転 to map onto Toulmin warrant.** They are different moves. A warrant is a logical bridge between grounds and claim; 転 is a juxtaposition whose relevance the reader constructs. Mapping them flattens the analysis.
- **Applying kishōtenketsu to JP academic STEM writing.** Modern JP academic writing (especially STEM) uses 序論-本論-結論 / IMRaD; trying to find a 転 in a methods section will produce nonsense. Check section headings before choosing mode.
- **Reading 婉曲表現 hedges as low-conviction.** Conventional softening (かもしれない / と言えよう / ではないか) is required register, not author uncertainty. Counting hedges is descriptive, not evaluative.
- **Translating "the claim" into a proposition.** If the artifact's claim is the relationship 結 proposes, force-extracting a single-sentence thesis is *itself* the deconstruction error — the analysis should name the relationship, not collapse it.
- **Cross-variant projection.** Findings from this lens do not transfer to `lens-rhetoric-anglo.md` artifacts. A "missing warrant" in an Anglo op-ed *is* a defect; in a JP op-ed it is normal register. See `lens-rhetoric.md` (universal-core router) for variant selection.
