# Research: length-limit unit for positioning paragraphs

Goal: pick a cap unit (words vs sentences vs share-of-file) for two ~80-word
positioning paragraphs, so drift ("one more sentence per fix round") gets
caught while "how many things the paragraph asserts" — not raw length — is
what's actually guarded.

## Q1 — Paragraph limit in SENTENCES?

- **GOV.UK** [standard]: "Paragraphs should have no more than 5 sentences
  each." Fetched and directly quoted from the primary source page.
  https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
- **ASD-STE100** [standard, secondary source]: a third-party rules digest
  states "Maximum ~6 sentences per paragraph" under "Paragraph and document
  structure," but the digest gives no numbered rule ID for it (the numbered
  ASD-STE100 rules cover word choice / verb form, not paragraph length; the
  paragraph-length line looks like the digest author's own summary of
  general STE guidance, not a cited clause). Treat the "~6" as directional,
  not as an ASD-STE100 rule-number citation.
  https://github.com/danyuchn/asd-ste100-skill/blob/master/references/writing-rules.md
  I could not reach the official ASD-STE100 FAQ page to confirm a numbered
  rule — insufficient data to cite an exact rule id for STE.
- **Microsoft Style Guide** [standard]: qualitative only — "write short
  headings, short sentences, and short paragraphs" — no number given.
  https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips
- **JIS / 日本語技術文書規格**: searched (JIS X 4051, 日本語組版処理の要件,
  パラグラフ・ライティング資料) — these cover typographic layout and
  topic-sentence placement, not a numeric per-paragraph sentence cap.
  Insufficient data — no Japanese standard found with a numeric
  sentences-per-paragraph limit.

**Convergent standards number: ~5 sentences/paragraph** (GOV.UK is a primary,
directly-quoted source; ASD-STE100's "~6" is close but secondary/unverified).

## Q2 — Paragraph limit in WORDS?

Addendum (2026-09-04, checked after the user asked about Google): the
**Google developer documentation style guide** [standard] gives no numeric
sentence or paragraph limit either — `style/tone` says only to avoid
"choppy or long-winded sentences", `style/sentence-structure` and
`style/highlights` carry no length guidance, and `style/paragraphs` does
not exist (404). Qualitative only; adds nothing to the numbers below.
https://developers.google.com/style/tone ;
https://developers.google.com/style/sentence-structure

Insufficient data. None of GOV.UK, Microsoft, or ASD-STE100 state a
paragraph limit in words — all three that give paragraph guidance express it
in sentences or only qualitatively ("short"). Sentence-length caps in words
exist (GOV.UK "over 25 words," ASD-STE100 word-count-per-sentence rules) but
that's a per-sentence cap, not a per-paragraph one. This is itself evidence
for the recommendation below: the standards converge on counting sentences,
not words, at the paragraph level.

## Q3 — Does instruction-following degrade with instruction COUNT or TOKEN length?

- **IFScale (Jaroslawicz et al., 2025)** [standard/paper, verified via
  primary PDF]: benchmark of up to 500 keyword-inclusion instructions;
  degradation is measured explicitly as a function of **instruction count**
  ("instruction density"), not token length — the paper's central variable
  is number of instructions, and top frontier models drop to ~68% accuracy
  at 500 instructions. Three degradation shapes found across models
  (threshold decay, linear decay, exponential decay), plus an early-position
  bias (earlier instructions favored over later ones — cites
  "Order Matters: Investigate Position..." on ordering effects).
  https://arxiv.org/pdf/2507.11538
- **"Same Task, More Tokens" (Levy et al., ACL 2024)** [paper]: degradation
  measured as a function of **input TOKEN length** (padding experiments on
  FLenQA), independent of instruction count — reasoning accuracy drops well
  before the model's max context, even when the added tokens are irrelevant
  padding. https://aclanthology.org/2024.acl-long.818/
- **Lost in the Middle (2023)** [paper]: positional effect — a U-shaped
  curve, best performance for content at the start/end of context, worst in
  the middle — a positional, not purely a count or token-length, effect.
  https://arxiv.org/abs/2307.03172 (via secondary summaries; not
  re-fetched from primary arXiv this round)
- **Context Rot (Hong et al., 2025)** [paper, secondary summary only]:
  performance degrades with input length even on simple tasks, non-uniformly,
  worsened by distractors and structure — token-length-driven, found via
  search summary, not fetched from primary source this round.

**Shape**: the evidence is mixed but leans toward BOTH axes mattering
independently — IFScale isolates instruction-COUNT as the dominant driver at
constant/short token length per instruction, while Levy et al. and Context
Rot isolate token-LENGTH as a dominant driver independent of instruction
count. For "how many things does this paragraph assert" (i.e., how many
independent claims/instructions a reader must retain), IFScale's count-based
framing is the closer analogue — each sentence in the positioning paragraph
functions like one keyword-instruction/claim. This favors **sentence count**
as the proxy for "how much the paragraph asserts," with a per-sentence word
cap (GOV.UK's 25-word rule) as the guard against a single sentence smuggling
in multiple claims disguised as one long sentence.

## Q4 — Does a paragraph's SHARE of the whole file affect LLM weighting?

Insufficient data. No paper or standard was found addressing paragraph share
of total document length as an independent variable on reader/model
attention. The closest related findings are purely positional (Lost in the
Middle: start/end vs middle) or purely length-based (Levy et al., Context
Rot), not share-based. Do not build a file-share-relative cap on this
evidence — no standard or study measures that variable.

## Q5 — Is a sentence-splitting rule deterministically testable?

- **Simple regex rule** [practitioner consensus]: split on `. ` / `? ` /
  `! ` when not immediately followed by a lowercase letter and not inside
  backticks/parentheses/quotes; treat this as the baseline for CI-checkable
  prose. Known failure cases, confirmed via NLTK's own punkt documentation
  and issue tracker:
  - **Abbreviations** ("e.g.", "vs.", "No." meaning "number", honorifics
    like "Mr."/"Sr." before a name) — a period after an abbreviation is not
    a sentence boundary; naive regex over-splits.
    https://github.com/nltk/nltk/issues/2154
  - **Decimals** ("3.14", "v1.2") — a period between digits is not a
    sentence boundary.
  - **Em-dash / parenthetical clauses** — not a punkt-specific failure, but
    a known false-negative case for naive splitters: a paragraph can read as
    "fewer sentences" by regex while still packing multiple independent
    claims into one em-dash-joined clause, silently defeating a
    sentence-count cap.
  - **NLTK punkt itself** is a trained unsupervised model (not a fixed
    rule); it handles abbreviations/decimals/quoted dialogue better than a
    naive split BUT its accuracy depends on training-data coverage of
    domain-specific abbreviations — not deterministic out of the box across
    domains. https://www.askpython.com/python-modules/nltk-punkt
  - For a CI/checker use case (this repo's positioning paragraphs), a
    **fixed regex with an explicit abbreviation-exception list** is more
    deterministic and auditable than shipping NLTK/punkt as a dependency,
    but the checker must also guard against the em-dash/clause-stuffing
    failure mode (e.g., also cap words-per-sentence, since GOV.UK's 25-word
    rule catches a sentence that dodges the split regex by using em-dashes
    instead of full stops).

## Recommendation for the unit

Use **sentence count with a per-sentence word cap**, not raw paragraph word
count and not file-share: standards converge on ~5 sentences/paragraph
(GOV.UK, directly quoted) as the "how much does this paragraph assert" unit,
and IFScale's LLM evidence shows degradation tracks instruction/claim
*count*, which sentences approximate better than raw words. Pure word count
(the current ≤80-word rule) is exactly what forced the cut — it lets one
extra long sentence blow the budget even when it's the sentence structure
that carries meaning, not the word total. File-share has no supporting
evidence (Q4) — do not adopt it. Concretely: cap at **≤5 sentences per
paragraph, ≤25 words per sentence** (GOV.UK's own two numbers, reused
together), checked deterministically via a regex splitter with an
abbreviation-exception list plus an em-dash/word-cap backstop per Q5, so a
"one more sentence" drift is caught at the sentence-count boundary rather
than only when the aggregate word total happens to tip over.
