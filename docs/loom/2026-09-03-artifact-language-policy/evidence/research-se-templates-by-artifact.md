# Research round 2 — sentence templates & writing rules by artifact type

Builds on prior round (Google/MS style guides, RFC 2119/8174, SEVOCAB, EARS,
ISO 29148, ASD-STE100, Conventional Commits) — not repeated here.

## A. Summary table

| Artifact type | Candidate template(s) | Verbatim shape (short) | Source URL | Licence/free? | Mechanically checkable? |
|---|---|---|---|---|---|
| Requirements | INCOSE Guide to Writing Requirements (rules, 14 characteristics) | "The [system/subsystem] shall [do X] within [performance criteria]." | incose.org/.../incose_rwg_gtwr_v4_summary_sheet.pdf | Summary sheet free; full guide free-to-members, ~€25 non-members | Partly (banned-word list, "shall"-count are checkable; ambiguity/testability need judgment) |
| Requirements | Gherkin (Cucumber) Given/When/Then | `Given <context> When <event> Then <outcome>` (+And/But) | cucumber.io/docs/gherkin/reference/ | Free, open (Cucumber OSS) | Partly (keyword presence checkable; semantic correctness not) |
| Requirements / stories | Mike Cohn user story + INVEST | "As a [role], I want [function], so that [business value]" | mountaingoatsoftware.com/agile/user-stories | Free (book concept, widely republished) | Partly (regex-checkable shape; INVEST qualities not) |
| Requirements (quantified) | Gilb Planguage (Tag/Scale/Meter) | Tag; Scale: "<units of measure>"; Meter: "<practical measurement method>" | modernanalyst.com (Specifying Quality Requirements With Planguage) | Free article; book commercial | Partly (presence of Scale/Meter fields checkable) |
| AI SDD tool — requirements | AWS Kiro `requirements.md` (EARS) | "WHEN [condition/event] THE SYSTEM SHALL [expected behavior]" + user story header "As a [role], I want [function], so that [benefit]" | kiro.dev/docs/specs/feature-specs/ | Free docs (product commercial) | Partly (keyword regex checkable) |
| AI SDD tool — spec | GitHub spec-kit `spec.md` | Sections: "User Scenarios & Testing", "Functional Requirements" (`**FR-[###]**: System MUST [capability]`), "Success Criteria" (`**SC-[###]**: [metric]`), Given/When/Then scenarios, `[NEEDS CLARIFICATION: ...]` flag | github.com/github/spec-kit/blob/main/templates/spec-template.md | Free, open source (MIT-family, GitHub) | Partly (ID prefixes, MUST-count, unresolved-clarification-flag all greppable) |
| Design decision | Nygard ADR (original) | Sections: Title / Status / Context / Decision / Consequences | adr.zone/adr-template (secondary; Nygard original at cognitect blog, unfetched here — mark unverified for exact wording) | Free, public blog format | Partly (section-presence checkable) |
| Design decision | Y-statement (Zimmermann) | "In the context of \<use case/user story\>, facing \<concern\>, we decided for \<option\> and neglected \<other options\>, to achieve \<system qualities/desired consequences\>, accepting \<downside/undesired consequences\>, because \<additional rationale\>." | unverified — pieced from search snippet, not a single fetched primary page (see notes) | Free (OSS pattern, widely republished) | Partly (regex on sentence connectives checkable; content not) |
| Review finding / comment | Conventional Comments | `<label> [decorations]: <subject>` + optional discussion; labels: praise, nitpick, suggestion, issue, todo, question, thought, chore, note; decorations: (non-blocking), (blocking), (if-minor) | conventionalcomments.org | Free, open (CC-style spec site) | Yes (label/decoration vocabulary is a closed enum — regex-checkable) |
| Review finding / comment | Google eng-practices "How to write code review comments" | Severity prefixes: "Nit:", "Optional:", "FYI:" | google.github.io/eng-practices/review/reviewer/comments.html | Free (Google OSS docs) | Partly (prefix presence checkable; courtesy/tone not) |
| Commit message | Chris Beams' seven rules | 1 blank-line-separated subject/body, 2 ≤50-char subject, 3 capitalized subject, 4 no trailing period, 5 imperative mood ("If applied, this commit will _subject_"), 6 wrap body at 72 chars, 7 body explains what/why not how | cbea.ms/git-commit/ | Free, public blog | Yes (length, capitalization, trailing-period, blank-line all regex-checkable; imperative mood partly) |
| Commit message | Angular commit convention | Header `<type>(<scope>): <subject>` + blank line + body + blank line + footer; header ≤100 chars; body mandatory except `docs`, ≥20 chars if present | github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md | Free, open source | Yes (structure/length checkable) |
| Test name / docstring | Osherove naming standard | `[UnitOfWork]_[StateUnderTest]_[ExpectedBehavior]`, e.g. `Sum_NegativeNumberAs1stParam_ExceptionThrown` | osherove.com/blog/2005/4/3/naming-standards-for-unit-tests.html | Free, public blog | Yes (three-underscore-segment shape is regex-checkable) |
| Bug / finding report | Mozilla Bug Writing Guidelines | Summary (<60 chars, no proposed solution) / Steps to Reproduce / Actual Results / Expected Results | bugzilla.mozilla.org/page.cgi?id=bug-writing.html | Free, open (Mozilla) | Partly (section presence + summary length checkable; content quality not) |
| Grammar / controlled language | INCOSE banned-vague-terms rule | Ban: "some, any, allowable, several, many, a lot of, a few, almost always, very nearly, nearly, about, close to" + vague adverbs "usually, approximately, sufficiently, typically" | incose.org (rule set, summary sheet + secondary syntheses — see notes, PDF fetch 403'd, treat wording as unverified pending re-fetch) | Free summary sheet | Yes (closed word-list, grep/regex) |
| Grammar / controlled language | GOV.UK "Use clear language" | Active voice ("We reviewed the data", not "The data was reviewed"); sentence length ~15–20 words, never >25; banned buzzwords list (drive, unlock, deep dive, robust, key, ring-fence, hub, portal, landscape, ecosystem, going forward, agenda, advance, deliver, deploy, facilitate) | guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/ | Free, UK Crown/OGL | Yes (word list + sentence-length are mechanically checkable) |

## B. Per-source notes (fetched URL + verbatim quotes)

### Conventional Comments — https://conventionalcomments.org/
- "The suggested labels are: praise, nitpick, suggestion, issue, todo, question, thought, chore, and note." (paraphrase of fetched page; page also lists typo/polish/quibble as extras)
- Example (verbatim): `praise: Beautiful test!`
- Example (verbatim): `issue (ux,non-blocking): These buttons should be red, but let's handle this in a follow-up.`
- Decorations: `(non-blocking)`, `(blocking)`, `(if-minor)`.

### Chris Beams, "How to Write a Git Commit Message" — https://cbea.ms/git-commit/
- Verbatim seven rules:
  1. Separate subject from body with a blank line
  2. Limit the subject line to 50 characters
  3. Capitalize the subject line
  4. Do not end the subject line with a period
  5. Use the imperative mood in the subject line
  6. Wrap the body at 72 characters
  7. Use the body to explain what and why vs. how
- Verbatim test: "A properly formed Git commit subject line should always be able to complete the following sentence: If applied, this commit will _your subject line here_."

### Cucumber Gherkin Reference — https://cucumber.io/docs/gherkin/reference/
- Verbatim: "`Given` steps are used to describe the initial context of the system - the _scene_ of the scenario. It is typically something that happened in the _past_."
- Verbatim: "`When` steps are used to describe an event, or an _action_."
- Verbatim: "`Then` steps are used to describe an _expected_ outcome, or result."
- Example (verbatim):
  ```
  Scenario: Dr. Bill posts to his own blog
    Given I am logged in as Dr. Bill
    When I try to post to "Expensive Therapy"
    Then I should see "Your article was published."
  ```

### Google eng-practices — https://google.github.io/eng-practices/review/reviewer/comments.html
- Verbatim: "Nit: This is a minor thing. Technically you should do it, but it won't hugely impact things." (paraphrased close to source wording per fetch)
- Verbatim-ish: "Optional (or Consider): I think this may be a good idea, but it's not strictly required."
- Verbatim-ish: "FYI: I don't expect you to do this in this CL, but you may find this interesting to think about for the future."
- Note: exact original prefix casing/text should be re-verified against page HTML directly if used as a hard mechanical rule — current wording came through an intermediary fetch summarizer, not raw HTML; treat literal casing as **unverified**.

### Mozilla Bug Writing Guidelines — https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
- Verbatim: "Steps to Reproduce: Minimized, easy-to-follow steps that will trigger the bug."
- Verbatim: "Actual Results: What the application did after performing the above steps."
- Verbatim: "Expected Results: What the application should have done, were the bug not present."
- Summary rule: "less than 60 characters ... not your suggested solution" (paraphrase of fetched content — **unverified exact wording**, re-check raw page for literal text).

### Roy Osherove — https://osherove.com/blog/2005/4/3/naming-standards-for-unit-tests.html
- Pattern: `[UnitOfWork_StateUnderTest_ExpectedBehavior]`
- Verbatim example: `Public void Sum_NegativeNumberAs1stParam_ExceptionThrown()`
- Verbatim example: `Public void Sum_simpleValues_Calculated()`

### AWS Kiro — https://kiro.dev/docs/specs/feature-specs/
- EARS example (as fetched, likely paraphrase of doc, **mark unverified for exact casing**): "WHEN a user submits a form with invalid data THE SYSTEM SHALL display validation errors next to the relevant fields"
- Three-file structure confirmed: requirements.md / design.md / tasks.md.

### GitHub spec-kit — https://github.com/github/spec-kit/blob/main/templates/spec-template.md
- Section headings (fetched, treat as accurate since sourced from the raw template file): "User Scenarios & Testing (mandatory)", "Requirements (mandatory)", "Functional Requirements", "Success Criteria (mandatory)".
- Templates: `**FR-[###]**: System MUST [specific capability]`, `**SC-[###]**: [Measurable metric description]`, `[NEEDS CLARIFICATION: description of what requires clarification]`, Given/When/Then acceptance scenarios.
- **Unverified**: exact bracket/bold Markdown syntax should be re-confirmed by opening the raw file directly (fetch here went through a summarizing intermediary, not the raw markdown).

### ADR templates (Nygard / Y-statement) — https://www.adr.zone/adr-template (secondary), plus search snippet for Y-statement
- Nygard sections (secondary source, **unverified against Nygard's original Cognitect post**, which was not directly fetched this round): Title / Status / Context / Decision / Consequences.
- Y-statement (from search snippet only, **unverified — no primary page fetched**): "In the context of \<use case/user story\>, facing \<concern\>, we decided for \<option\> and neglected \<other options\>, to achieve \<system qualities/desired consequences\>, accepting \<downside/undesired consequences\>, because \<additional rationale\>."

### INCOSE Guide to Writing Requirements — summary PDF fetch returned HTTP 403
- Rule content below is from search-engine synthesis of the summary sheet, **not a directly fetched primary page — mark unverified**:
  - "R1 — Structured Statements": one sentence, one subject, one main verb, one object.
  - "R2 — Active Voice": use active rather than passive voice.
  - "R7 — Avoid Vague Terms": avoid "some, any, allowable, several, many, a lot of, a few, almost always, very nearly, nearly, about, close to" and vague adverbs "usually, approximately, sufficiently, typically."
  - Guide states ~14 characteristics and ~49 rules total (version-dependent: V3.1 = 42 rules, V4 different count per secondary sources — **unverified exact current count, re-check the PDF directly with a different fetch method**).

### GOV.UK clear language — https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
- Verbatim-ish: "Use the active voice. Say who does what. Write 'We reviewed the data', not 'The data was reviewed'."
- Sentence length: "about 15 to 20 words, never more than about 25."
- Banned buzzwords list includes: drive, unlock, deep dive, robust, key, ring-fence, hub, portal, landscape, ecosystem, going forward.

### Angular commit convention — https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md
- Header format: `<type>(<scope>): <subject>`, header ≤100 chars, body mandatory except for `docs` type, body ≥20 chars if present, footer optional (issue references).

## C. Checkable-rules list (item 8), source per rule

1. Banned vague-word list ("some/any/several/a lot of/almost always/nearly/about" etc.) — INCOSE Guide to Writing Requirements (unverified exact source page, see notes).
2. Banned vague adverbs ("usually/approximately/sufficiently/typically") — INCOSE (same caveat).
3. Active voice required — INCOSE R2; also GOV.UK "Use clear language" (independently corroborating, both fetched/searched).
4. One requirement/one thought per sentence — INCOSE R1 ("one subject, one main action verb, one object").
5. Sentence length cap ~15–20 words, never >25 — GOV.UK clear-language guidance.
6. Banned buzzword/jargon list (drive, unlock, deep dive, robust, key, ring-fence, hub, portal, landscape, ecosystem, going forward, agenda, advance, deliver, deploy, facilitate) — GOV.UK A-Z / clear-language style guide.
7. Commit subject ≤50 chars, capitalized, no trailing period, imperative mood, blank line before body, body wrapped at 72 chars — Chris Beams, cbea.ms/git-commit/.
8. Commit header ≤100 chars, body ≥20 chars unless type=docs — Angular commit-message-guidelines.md.
9. Review-comment severity vocabulary closed to {Nit, Optional, FYI} — Google eng-practices comments.html.
10. Review-comment label vocabulary closed to {praise, nitpick, suggestion, issue, todo, question, thought, chore, note} + decorations {non-blocking, blocking, if-minor} — conventionalcomments.org.
11. Bug summary <60 chars, must not contain a proposed solution — Mozilla bug-writing.html (wording unverified, see notes).
12. Test name = three underscore-delimited segments (UnitOfWork_StateUnderTest_ExpectedBehavior) — Osherove.

## D. Evidence (item 9)

- **arXiv 2508.20744**, "From Law to Gherkin: A Human-Centred Quasi-Experiment on the Quality of LLM-Generated Behavioural Specifications from Food-Safety Regulations" (fetched abstract). Finding: human-rated quality of LLM-generated Gherkin specs from regulatory text scored >91% across relevance/clarity/completeness/singularity/time-savings dimensions, clarity near-perfect — but reviewers still found omissions, hallucinations, and conflated requirements, so the paper's conclusion is LLMs accelerate the conversion but human review remains necessary. This measures **output quality of LLMs producing Gherkin**, not whether feeding Gherkin-templated *input* improves an LLM's downstream code-generation quality — a different (though adjacent) question from the repo owner's hypothesis.
- **arXiv 2509.11446**, "Large Language Models (LLMs) for Requirements Engineering (RE): A Systematic Literature Review" (74 primary studies, 2023–2024). Abstract fetched but content did not surface a direct finding on whether structured/templated requirements reduce LLM output variance or improve quality — **insufficient data** from what was fetched; the review's focus is elicitation/validation tasks generally, not a controlled EARS-vs-freeform or Gherkin-vs-prose comparison.
- Search for a direct "EARS + LLM output quality/consistency" controlled study, and for "Gherkin-as-LLM-input vs prose-as-LLM-input" controlled comparison, did not surface a paper measuring exactly the repo owner's hypothesis (fixed sentence shapes → lower reviewer-verdict variance). **Insufficient data — no direct evidence found either way; do not claim proven or disproven.**
- One secondary/tertiary claim surfaced in search snippets (not independently fetched/verified): "using Gherkin syntax as an intermediate step between requirements and code generation yields better results compared to direct code generation" — this is about Gherkin as a generation *intermediary*, not as reviewer-facing structured *input for variance reduction*; treat as **unverified / tangential**, not evidence for the stated hypothesis.

## E. What fits which loom artifact (mapping — sources only, no invented rules)

- **intent.md Acceptance lines**: EARS (`WHEN <trigger> THE SYSTEM SHALL <response>`, prior round) + Gherkin Given/When/Then (this round, cucumber.io) both fit — EARS for trigger-driven behavior, Given/When/Then where a scenario narrative helps; Osherove-style "one behavior per line" discipline reinforces one-Acceptance-per-line.
- **spec.md REQ-\<n\> lines**: INCOSE R1 (one subject/one verb/one object per statement) + banned-vague-word list; spec-kit's `**FR-[###]**: System MUST [capability]` ID-prefix pattern is a directly reusable shape (github.com/github/spec-kit template).
- **plan.md tasks**: no artifact-type-specific template surfaced this round beyond spec-kit's `tasks.md` (task list derived from design docs, grouped by user story) — reuse that grouping-by-story shape; INVEST (Independent/Estimable/Negotiable/Small/Valuable/Testable, Cohn) is the closest fit for judging whether a task/story is well-cut.
- **review findings**: Conventional Comments `<label> [decorations]: <subject>` is the strongest direct fit — closed vocabulary is mechanically checkable; Google eng-practices' Nit/Optional/FYI severity prefixes can layer on as decorations or replace them.
- **commit messages**: already covered by Conventional Commits (prior round); this round adds Chris Beams' seven rules and Angular's header-length/body-length rules as *additional* mechanically-checkable constraints layered on top of the Conventional Commits `type(scope): subject` shape — not a replacement.
- **probe/test docstrings**: Osherove's `UnitOfWork_StateUnderTest_ExpectedBehavior` fits blind-run/adversarial probe naming directly; Gherkin Given/When/Then fits probe docstrings/bodies where a scenario narrative is clearer than a compressed name.
- **evidence/bug-style notes** (e.g. blind-run findings, adversarial probe failures): Mozilla's Summary/Steps-to-Reproduce/Actual/Expected shape is a direct fit for any loom artifact that records "this failed" — blind-run reports and adversarial probes both currently write free-form failure narratives that this shape would structure.
- **ADR-shaped decisions** (design-decision entries currently free-prose in spec.md's "Design decision" field): Nygard's Status/Context/Decision/Consequences or the more compact Y-statement sentence are both candidates — flagged **unverified exact wording** above, so verify primary sources before adopting verbatim.
