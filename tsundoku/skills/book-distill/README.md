# book-distill

> Distill a book (already converted to chunked Markdown by
> [`book-extract`](../book-extract)) into a coherent set of executable agent
> skills via the **RIA-TV++ pipeline**.

Part of the [tsundoku](../..) plugin. Skill spec Claude loads is
[`SKILL.md`](SKILL.md); this README is for humans.

> ⚠️ **Status (v0.8.1)**: pipeline structure landed; **trilingual
> glossaries are scheduled for a research-grounded revision** (current
> entries are direct translations rather than each language community's
> canonical technical terms). See "Known limitations" below.

## What it does (and doesn't)

- ✅ **Distill**: methodologies / decision frameworks / checklists /
  principles / conceptual systems → atomic, reusable agent skills
- ❌ **Skip**: book summaries / book reviews / author-as-persona role-play

## RIA-TV++ pipeline

```
Stage 0:    Adler analytical read           → BOOK_OVERVIEW.md
Stage 1:    5 parallel sub-agent extractors → candidates/
            (framework / principle / case / counter-example / glossary)
Stage 1.5:  Triple verification filter       → verified.md (~30-50% pass)
            V1 cross-domain / V2 predictive / V3 exclusivity
Stage 2:    RIA++ skill render               → <skill-slug>/SKILL.md
            R / I / A1 / A2 / E / B six fields
Stage 3:    Zettelkasten linking              → INDEX.md + cross-refs
Stage 4:    Adversarial pressure test         → test-prompts.json
```

The ITSELF distillation is **Claude-driven** — the skill spec instructs
Claude to spawn sub-agents per stage. There is no monolithic Python
orchestrator; the only shell script is `book_distill_init.sh` which
bootstraps the working directory.

## Pre-conditions

Source book must already be processed by [`book-extract`](../book-extract):

```bash
ls ~/.tsundoku/cache/markdown/<book-slug>-<id8>/
# expected: index.md / metadata.json / NN-chapter.md files
```

Without these, `book_distill_init.sh` aborts and routes you to
`book-extract`.

## Quick start

```bash
# 1. Bootstrap a working directory from extracted markdown
bash scripts/book_distill_init.sh 一九八四-b9152ffe

# Output: ~/.tsundoku/cache/distilled/一九八四-b9152ffe/
#   ├── BOOK_OVERVIEW.md.draft
#   ├── metadata.snapshot.json
#   ├── chapters.list
#   ├── candidates/
#   ├── rejected/
#   └── .book-distill-state

# 2. Then have Claude follow this skill's SKILL.md from Stage 0 onward.
#    Claude reads chapters, fills BOOK_OVERVIEW.md, spawns 5 parallel
#    extractors, runs triple verification, etc.
```

## When to invoke

User says something like:
- "Distill *Poor Charlie's Almanack* into skills"
- "把《思考的快與慢》蒸餾成 skill"
- "この本の方法論を skill にして"

## Output structure

```
~/.tsundoku/cache/distilled/<book-slug>/
├── BOOK_OVERVIEW.md            # Stage 0 — thesis / skeleton / glossary / critique
├── INDEX.md                    # Stage 3 — skill overview + reference graph
├── candidates/                 # Stage 1 raw candidate pool (audit trail)
│   ├── frameworks.md
│   ├── principles.md
│   ├── cases.md
│   ├── counter-examples.md
│   └── glossary.md
├── rejected/                   # Stage 1.5 cuts + reasons (audit trail)
├── verified.md                 # Stage 1.5 survivors
└── <skill-slug-N>/             # one dir per shipped skill
    ├── SKILL.md                # RIA++ render: R / I / A1 / A2 / E / B
    └── test-prompts.json       # Stage 4 test cases (≥3 trigger + ≥2 lure + ≥1 edge)
```

## Per-skill schema (RIA++ six fields)

| Field | Content |
|---|---|
| **R** Reading | verbatim source quote ≤150 chars + chapter citation |
| **I** Interpretation | methodology skeleton in your own words, 5-15 lines |
| **A1** Past Application | author-documented cases of this methodology |
| **A2** Future Trigger ★ | when user needs this; becomes frontmatter `description` |
| **E** Execution | numbered runtime steps with completion criteria |
| **B** Boundary | when NOT to apply, sourced from counter-examples + critique |

## Output language rule

This skill is language-adaptive:

- **R quotes**: VERBATIM source language; never translate
- **I / A / E / B body**: match source book's language
- **YAML field names + slugs**: English (machine identifiers)
- **frontmatter `description`**: source language (so user-query trigger
  matching works naturally)
- **Audit metadata**: English

## Files in this folder

| Path | Role |
|---|---|
| [`SKILL.md`](SKILL.md) | Top-level orchestrator Claude loads (~270 lines) |
| [`ATTRIBUTION.md`](ATTRIBUTION.md) | Upstream credits (cangjie-skill, nuwa-skill, Adler, RIA, Zettelkasten) + license |
| [`methodology/`](methodology) | 7 files: design rationale + per-stage detail |
| [`extractors/`](extractors) | 5 sub-agent prompts (framework / principle / case / counter-example / glossary) |
| [`templates/`](templates) | BOOK_OVERVIEW / SKILL / INDEX / test-prompts |
| [`scripts/book_distill_init.sh`](scripts/book_distill_init.sh) | Bootstrap working dir from `book-extract` output |

## Lineage

Adapted from [`kangarooking/cangjie-skill`](https://github.com/kangarooking/cangjie-skill)
(蒼頡-skill, MIT). See [`ATTRIBUTION.md`](ATTRIBUTION.md) for full credits and
the list of upstream → tsundoku changes.

The whole architecture comes from cangjie-skill; tsundoku contributes:
1. English-canonical instructions + adaptive output language rule
2. **Trilingual glossaries** (EN / 日本語 / 繁體中文) — *being revised*
3. tsundoku-specific entry hook (`book_distill_init.sh`) so the upstream's
   biggest friction point ("user must supply book + metadata") disappears

## Why "book-*" not "kobo-*"?

This skill is **format-agnostic**: it consumes any chunked Markdown,
regardless of source. Future `paper-distill` (academic papers) or
`transcript-distill` (podcast transcripts) would join the `book-*` /
processing layer. Only `kobo-auth` and `kobo-library` are bound to the
Kobo platform.

## Known limitations

- **Trilingual glossaries** in `methodology/*.md` and `extractors/*.md`
  contain direct translations rather than each language community's
  canonical technical terms. **Pending revision** with researched
  domain-specific equivalents (e.g. for cognitive-bias / decision-theory
  / philosophy / 認知行動学 / 認識論 vocabulary).

- **No coverage proof** — distillation may miss the book's most important
  framework. Roadmap item: TOC reconstruction test (given the distilled
  skill, can a fresh agent rebuild the chapter outline?).

- **No CJK fidelity benchmark** — quantitative validation across the
  226 zh-TW / 7 ja books in the test library is a roadmap item.

- **No automated regression** — `test-prompts.json` is darwin-skill
  format-compatible but no orchestrator pulls it; that's left to a
  future evolution skill or manual run.

## See also

- [`book-extract`](../book-extract) — produces the chunked Markdown this
  skill consumes
- [`tsundoku` README](../..) — full pipeline overview
- [Cangjie design rationale](https://github.com/kangarooking/cangjie-skill)
- [Nuwa Skill](https://github.com/alchaincyf/nuwa-skill) — sibling persona
  distillation (different scope, same Triple Verification primitive)
