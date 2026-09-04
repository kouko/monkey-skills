# Industry standards for SE-document terminology/phrasing — survey

## (A) Comparison table

| Source | What it standardizes | Scope it was written for | Access & licence | Fit for spec/plan/review-finding prose |
|---|---|---|---|---|
| Google developer documentation style guide (word list + highlights) | Phrasing rules (tense, voice, person) + an A–Z word list of preferred/avoided terms | Google's own developer-facing docs (API refs, guides) | Free, public, web-only; no formal reuse licence stated | **High** — general prose rules (active voice, 2nd person, present tense) map directly onto plan/review prose; word list is opinionated toward product docs, not requirements, so use selectively |
| Microsoft Writing Style Guide (A–Z word list + bias-free language) | Phrasing rules + word list + explicit "use the same word for the same thing" consistency rule + bias-free language | Microsoft docs/UI text, adopted widely by tech writers | Free, public, web (learn.microsoft.com) | **High** — the "consistent word choice" principle is exactly what an LLM-reviewer wants; word list itself is Microsoft-product-flavored |
| RFC 2119 + BCP 14 (RFC 2119 + RFC 8174) | Exactly the modal key words (MUST/SHOULD/MAY/etc.) and their normative force, plus the uppercase-only clarification | Internet protocol specifications | Free, public (IETF/RFC Editor); RFCs are open, citable, no licence barrier | **High** — this is the de facto standard for requirement-strength wording; trivial to adopt verbatim for spec.md "Design decision" / Acceptance lines |
| ISO/IEC/IEEE 24765 (SEVOCAB) | A definitional glossary of SE terms (nouns/concepts), not phrasing rules | Systems & software engineering generally | Free browsable database at computer.org/sevocab; definitions may be copied if source is cited; the formal ISO/IEC/IEEE standard document itself is paywalled | **Medium** — good as a term-definition reference to link/cite when a spec uses a jargon word, but it does not constrain sentence structure or verb choice, so it doesn't by itself reduce LLM-reviewer drift |
| ISO/IEC/IEEE 29148 (requirements engineering) + EARS (Mavin 2009) | Sentence-level syntax templates for requirement statements (condition/subject/action/object/constraint; EARS's 5 templates: Ubiquitous, Event-driven, State-driven, Optional feature, Unwanted behaviour) | Formal requirements specifications (systems/software) | 29148 itself is a paywalled ISO/IEEE standard; EARS is a conference paper (Mavin & Wilkinson, RE'09) and its templates are freely reproduced/used across the industry (no licence restriction found) | **High for EARS, Medium for 29148** — EARS templates are exactly the shape of "Acceptance"/requirement lines loom already writes; 29148 full text isn't freely fetchable so only its widely-quoted structure (condition/subject/action/object/constraint) is usable, not verified against the primary paywalled text |
| ASD-STE100 (Simplified Technical English) | A controlled dictionary (~900 approved words, one meaning/one part of speech each) + ~53 writing rules | Aerospace/defense maintenance manuals (procedural, safety-critical text for non-native readers) | Free to obtain (request official copy), but redistribution restricted to specific organisation categories — not a copy-paste-into-a-repo licence | **Low–Medium** — the "one word, one meaning" discipline is philosophically attractive for reducing LLM drift, but its ~900-word vocabulary is built for physical maintenance actions (remove, install, tighten), not software concepts (idempotent, race condition, rollback), so it would need heavy supplementing; also its redistribution licence is a real constraint for embedding into a repo's skill files |
| Apple Style Guide / Red Hat Supplementary Style Guide / GitLab Documentation Style Guide / Kubernetes docs style guide / Write the Docs style guide | Each is a general product/project documentation style guide (voice, grammar, terminology) | Their own product or project docs | Free, public (web, some GitHub-hosted) | **Low–Medium, one-line each** — useful precedent that "adopt a style guide" is normal industry practice, but none is purpose-built for spec/plan/review-finding prose; not deep-researched here beyond confirming existence and scope |
| Conventional Commits | A structured **format** for commit messages (type(scope): description), not vocabulary | Git commit messages across OSS projects | Free, public spec (conventionalcommits.org) | **High, narrowly** — directly answers loom's "commit messages" artifact type; doesn't help specs/plans/review findings |
| Diátaxis | Document **type** taxonomy (tutorial / how-to / reference / explanation), not vocabulary or phrasing | Any technical documentation set | Free, public (diataxis.fr) | **N/A for this task** — explicitly out of scope per the task itself: it standardizes document structure/purpose, not word choice or phrasing |

## (B) Per-source notes

### Google developer documentation style guide
- Word list index fetched: https://developers.google.com/style/word-list
- Highlights page fetched: https://developers.google.com/style/highlights
- Verbatim word-list entries (from developers.google.com/style/word-list):
  - **access (verb)**: "Avoid when you can. Instead, use friendlier words like *see*, *edit*, *find*, *use*, or *view*."
  - **allows you to**: "Don't use. Instead, use *lets you*."
  - **above**: "Don't use to refer to a position in a document" — use directional alternatives instead.
- Verbatim phrasing rules (from developers.google.com/style/highlights):
  - "Use active voice: make clear who's performing the action."
  - "Use second person: 'you' rather than 'we.'"
  - (Present-tense and "don't use please" rules are documented on linked sub-pages `/style/tense` and elsewhere; not independently re-fetched/quoted here — flagging as **unverified quote**, only the highlights-page summary was confirmed.)

### Microsoft Writing Style Guide
- Word-choice overview fetched: https://learn.microsoft.com/en-us/style-guide/word-choice/
- Verbatim: "To improve readability and comprehension, choose your words wisely and use them consistently. If you mean the same thing, use the same word."
- A–Z entry fetched verbatim: https://learn.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/a/above
  - **above**: "Don't use to mean *earlier*. Don't use as an adjective preceding a noun (*the above section*) or following a noun (*the code above*). Use a link, or use *previous, preceding,* or *earlier.*"
- Bias-free language page located (https://learn.microsoft.com/en-us/style-guide/bias-free-communication) but not fetched directly; findings below are from search-result snippets, **not independently verified against the primary page**:
  - avoid terms with unconscious bias (e.g., master/slave)
  - singular "they" is acceptable
  - disability language should be people-first
- Could not confirm a Microsoft-specific can/may/must rule set (search turned up nothing specific; treat as **not found**, not "doesn't exist").

### RFC 2119 / BCP 14 (RFC 2119 + RFC 8174)
- RFC 8174 fetched: https://www.rfc-editor.org/rfc/rfc8174.html
- Verbatim: "The words have the meanings specified herein only when they are in all capitals."
- Key words per RFC 2119 (from search, standard and widely cited, not independently re-fetched from rfc-editor.org/rfc/rfc2119 in this session — **flagging as secondary-sourced**): MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY, OPTIONAL.
- BCP 14 is the umbrella label under which both RFC 2119 and RFC 8174 are jointly cited (standard IETF citation practice: "BCP 14 [RFC2119] [RFC8174]").

### ISO/IEC/IEEE 24765 (SEVOCAB)
- Access point (from search, not directly fetched): the free browsable database is at www.computer.org/sevocab, hosted by IEEE Computer Society. **Not independently fetched/verified in this session** — treat the exact URL/copy terms as secondary-sourced.
- Copyright note (secondary-sourced): definitions may be copied if the source is cited.
- Two editions exist: ISO/IEC/IEEE 24765:2010 and :2017 (second edition); the formal PDF standard is paywalled via iso.org/ansi/ieee, only the SEVOCAB database is free.
- Usability as a glossary for spec writing: it is a **definitions** database (term → meaning), not a phrasing-rules or syntax standard — useful to pin down what a jargon term means, not how to phrase a requirement.

### ISO/IEC/IEEE 29148 + EARS
- EARS Wikipedia page fetched: https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax
- Five EARS templates (verbatim structure from the fetched page):
  1. **Ubiquitous**: "THE <system name> SHALL <system response>"
  2. **Event-driven**: "WHEN <trigger>, the <system name> SHALL <system response>"
  3. **State-driven**: "WHILE <precondition(s)>, the <system name> SHALL <system response>"
  4. **Optional feature**: "WHERE <feature is included>, the <system name> SHALL <system response>"
  5. **Unwanted behaviour**: "IF <trigger>, THEN the <system name> SHALL <system response>"
- Origin: Alistair Mavin et al., Rolls-Royce, first published IEEE RE'09 (2009). No licence/patent restriction found on the templates themselves — they are reproduced freely across the industry (tool vendors, blogs, arXiv papers).
- ISO/IEC/IEEE 29148:2018 (from search snippets, **not fetched from a primary/free source** — the standard PDF is paywalled at iso.org/ieee):
  - Recommends signalling key words: *shall, should, may, will*
  - Functional-requirement structure: [condition] [subject] [action] [object] [constraint], e.g. "Upon receiving signal x [Condition], the system [Subject] shall set [Action] the 'signal x received' bit [Object] within 2 seconds [Constraint]"
  - Best practice: positive statements, active voice, avoid "shall be able to"
  - **This content is secondary-sourced (search snippets/third-party summaries of the paywalled standard), not verified against the ISO/IEEE primary text.**

### ASD-STE100 (Simplified Technical English)
- Fetched: https://www.asd-ste100.org/about_STE.html
- Verbatim: "the approved words that a writer can use (approximately 900 words, each with one meaning and one part of speech)"
- Verbatim on scope creep beyond original purpose: "today, the success of STE is such that it is used well beyond its original purpose of maintenance documentation and outside the aerospace and defense domains."
- Free official copy obtainable by request (site prompts "Request your free official copy of ASD-STE100, Issue 9").
- Licence caveat (from search, on the Issue 9 PDF cover — **not independently re-verified by fetching the PDF itself**): "reproduction only with ASD's written authority, or by eight listed categories of organisation" — i.e., free to *read*, restricted to *redistribute/embed*.

### Other guides (one line each, confirmed to exist + scope only, not deep-fetched)
- **Apple Style Guide** — https://support.apple.com/guide/applestyleguide/welcome/web — Apple's own product/UI/doc voice guide.
- **Red Hat Supplementary Style Guide** — https://redhat-documentation.github.io/supplementary-style-guide/ — supplements IBM Style Guide for Red Hat product docs.
- **GitLab Documentation Style Guide** — https://docs.gitlab.com/development/documentation/styleguide/ — GitLab's own docs contribution style rules.
- **Kubernetes docs style guide** — https://kubernetes.io/docs/contribute/style/style-guide — Kubernetes project's own contribution style guide.
- **Write the Docs style guide** — https://www.writethedocs.org/style-guide/ — community-maintained meta style guide + a curated list of other orgs' style guides.
- **Conventional Commits** — https://www.conventionalcommits.org/en/v1.0.0-beta.2/ — commit-message **format** spec (`type(scope): description`), directly applicable to loom's "commit messages" artifact type.
- **Diátaxis** — https://diataxis.fr/ — a **document-type** taxonomy (tutorial/how-to/reference/explanation), not a vocabulary or phrasing standard; noted per the task's own framing as out of scope for terminology.

## (C) Evidence: does controlled/consistent terminology measurably help LLM comprehension or judge consistency?

Searched arXiv/ACL for "controlled natural language LLM", "terminology consistency LLM evaluation", "prompt wording sensitivity LLM-as-judge". Findings (all from search-result snippets — **none of these papers were fetched and read in full in this session**, so summaries below are secondary-sourced and should be re-verified before being cited as a load-bearing claim):

1. **JudgeSense** (arXiv 2604.23478) — a benchmark explicitly built to measure "judge stability across equivalent [i.e., paraphrased] prompts," and to identify which tasks are most sensitive to prompt wording. Directly relevant: it treats prompt/instruction wording as part of the evaluation protocol, implying wording *does* move LLM-judge verdicts, but the paper is a *measurement benchmark*, not proof that a specific controlled vocabulary reduces drift.
2. **"Flaw or Artifact? Rethinking Prompt Sensitivity in Evaluating LLMs"** (arXiv 2509.01790) — frames prompt sensitivity as sometimes methodological artifact rather than pure model flaw; relevant to interpreting any "consistency improved" result cautiously.
3. General finding echoed by several of the returned papers (Cross-Lingual Stability of LLM Judges, Evaluating the Consistency of LLM Evaluators, Coin Flip Judge): LLM-as-judge scores are demonstrably sensitive to how the instructions/prompt are worded, and researchers now argue "the judge is the model-prompt pair" — i.e., wording matters enough that some papers fix a rigid template specifically to control for it.
4. **No paper found that directly tests "adopting a controlled vocabulary / style guide in the *documents under review* reduces LLM-judge verdict variance."** All the surfaced evidence is about controlling the *judge's own prompt/instructions*, not about controlling the *vocabulary of the artifact being judged* (which is loom's actual question: does writing specs/plans in Google/Microsoft/EARS-style consistent wording reduce reviewer drift).
5. **Verdict: insufficient direct data.** There is solid, multi-paper evidence that prompt/instruction wording measurably affects LLM-judge consistency (supports the general intuition that word-choice consistency matters for LLMs). There is no evidence found — positive or negative — specifically isolating "controlled input-document vocabulary" as the causal factor in reviewer-verdict drift. This is an inference-by-analogy, not a directly measured effect; flag it as such if cited in the repo's rationale.

## (D) What a repo could adopt (combination only — no invented rules)

- **Key words for requirement/acceptance strength**: adopt RFC 2119 + RFC 8174 verbatim — MUST / MUST NOT / SHOULD / SHOULD NOT / MAY, uppercase-only, with the BCP 14 citation. This is free, short, and already the de facto SE standard; loom's Acceptance/Constraints lines can cite it directly.
- **Sentence shape for Acceptance / requirement lines**: adopt EARS's five templates (Ubiquitous / Event-driven / State-driven / Optional feature / Unwanted behaviour) for spec.md's `REQ-<n>` and intent.md's Acceptance lines — freely reusable, and structurally close to what loom already asks for ("each Acceptance line can be blind-run-proven").
- **General prose rules** (tense, voice, person, consistent word choice): combine Google's "active voice / second person / present tense" rules with Microsoft's explicit "if you mean the same thing, use the same word" principle — both are free, public, and general enough to apply to plans/review findings/commit prose without pulling in either company's product-specific word list wholesale.
- **Term definitions**: point to SEVOCAB (computer.org/sevocab) as an optional reference when a spec uses ambiguous SE jargon, rather than building a new glossary from scratch — cite-on-copy per its stated licence.
- **Commit message format**: adopt Conventional Commits' `type(scope): description` structure for the commit-message artifact type specifically (already closest match; the repo's CLAUDE.md already references a type whitelist per memory).
- **Explicitly not adopted**: ASD-STE100's ~900-word dictionary (aerospace-maintenance vocabulary, redistribution-restricted, poor fit for software concepts) and the full ISO/IEC/IEEE 24765/29148 standard texts (paywalled — only their freely-available derivative concepts, EARS and the RFC 2119 key words, are safe to embed verbatim in a repo).
- **Open question the sources don't answer**: no standard here fixes vocabulary for *review-finding* prose specifically (severity words, verdict words) — that would be a repo-specific extension, not something to attribute to an external standard.
