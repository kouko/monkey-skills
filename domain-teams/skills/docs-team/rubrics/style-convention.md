# Style Convention Gate

## Scope Boundary

Review the **prose style** of a documentation artifact against the style
conventions defined in `standards/style-conventions.md` (primary: Google
Developer Documentation Style Guide; secondary: Microsoft Writing Style Guide;
philosophical preamble: JTAP 第 1 原則 Reader-First Principle).

This gate is **judgment-based**, not mechanical. Vale and markdownlint cannot
run inside Claude Code, so this rubric approximates their checks through
structured scoring.

Do NOT review: content correctness, Diátaxis mode clarity, completeness, or
freshness — those belong to other gates.

## Flag Definitions

### Voice and Grammar

- 🔴 **Fatal**: Predominantly passive voice throughout; third person ("the user")
  used consistently instead of second person ("you"); past or future tense
  used for present behavior.
- 🟡 **Warning**: Occasional voice/grammar lapses (1-3 per 500 words) — e.g.,
  a few passive constructions where the actor matters, or "will return"
  instead of "returns" in a reference doc.
- 🟢 **Clear**: Active voice, second person, present tense throughout. Passive
  voice used only where the actor is genuinely unknown or irrelevant.

### Heading and Formatting Style

- 🔴 **Fatal**: Title Case Headings Throughout (not sentence case); skipped
  heading levels (H3 following H1); inconsistent heading hierarchy across
  sections.
- 🟡 **Warning**: Mostly correct sentence case but a few title-case headings
  slipped in; minor inconsistency in bullet vs numbered list usage (sequential
  content in bullets, or non-sequential in numbered).
- 🟢 **Clear**: Sentence case headings; proper hierarchy (H1 → H2 → H3);
  numbered lists for sequential content, bullets for non-sequential.

### Punctuation and Mechanics

- 🔴 **Fatal**: Missing serial commas throughout; multiple punctuation errors
  per paragraph; incorrect apostrophes, quotes, or dashes.
- 🟡 **Warning**: Occasional missing serial comma; minor mechanical
  inconsistencies.
- 🟢 **Clear**: Serial commas consistently used; one space after periods;
  proper punctuation.

### Link Text and Accessibility

- 🔴 **Fatal**: Uses "click here" or raw URLs as link text; images lack alt
  text; directional language ("see above", "as shown below") used as primary
  navigation.
- 🟡 **Warning**: Occasional non-descriptive link text; minor directional
  language.
- 🟢 **Clear**: All link text is descriptive; all images have alt text; uses
  explicit section references instead of directional language.

### Brevity and Reader-First

Reference: `standards/style-conventions.md` §Reader-First Principle.

- 🔴 **Fatal**: Verbose and padded throughout; "simply," "just," "easy," "obviously"
  used repeatedly (minimizes reader difficulty); "please" before instructions;
  long sentences (>40 words) are the norm.
- 🟡 **Warning**: Occasional verbosity, a few uses of "simply" or "just",
  sentences that could be trimmed.
- 🟢 **Clear**: Concise, respects reader time, no condescending minimizers,
  sentences are appropriately short.

### Parallel Structure

- 🔴 **Fatal**: List items use mixed grammatical structures (e.g., some
  imperative, some noun phrases, some questions in the same list).
- 🟡 **Warning**: Most lists parallel, one or two lists mixed.
- 🟢 **Clear**: All sibling headings and list items follow parallel grammatical
  structure.

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- **Judgment-based, not mechanical.** Because this gate approximates Vale,
  expect some variability in borderline cases. When in doubt about a specific
  construction, ask: does this narrow or widen the writer-reader gap?
- **Legitimate passive voice is not a failure.** "The file is overwritten" is
  acceptable if the actor (the system) is obvious from context and making it
  explicit would add noise.
- **Tone register flexibility.** Google style is more clinical; Microsoft
  style is more friendly. Either is acceptable if consistent. Penalize only
  for inconsistency within a single document, not for preferring one over
  the other.
- **This is a SHOULD gate.** Skippable with a stated reason (e.g., "This
  is an auto-generated reference doc, style gate skipped").

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: Quote 1-3 example lines that triggered each flag
3. **Fix instruction**: Specific rewrite suggestion or rule reference
4. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

## Sources

- `standards/style-conventions.md` — the primary/secondary style guide definitions
- [Google Developer Documentation Style Guide](https://developers.google.com/style) — primary source
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/) — secondary source
