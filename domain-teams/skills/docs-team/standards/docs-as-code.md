# Docs as Code (Shared Standard)

Operational philosophy for technical documentation. Documentation is a
first-class engineering artifact, managed with the same tools and discipline
as source code.

Primary source: [Write the Docs — Docs as Code](https://www.writethedocs.org/guide/docs-as-code/)

## Definition

From the Write the Docs community:

> "Docs as Code refers to a philosophy that you should be writing documentation
> with the same tools as code… following the same workflows as development
> teams, and being integrated in the product team."

Docs-team writes documentation under this philosophy. There is no separate
"docs team silo" — documentation lives with code, is reviewed with code, and
degrades with code when not maintained.

## Eight Operational Principles

1. **Plain text markup** — Markdown, reStructuredText, or AsciiDoc. Not proprietary formats (Google Docs, Notion, Confluence). Plain text is diffable, versionable, and grep-able.
2. **Version control** — Documentation lives in the same git repository as the code it documents, or in a dedicated docs repo with explicit version links.
3. **Peer review** — Documentation changes go through pull requests with code review tooling. Reviewers check for correctness, clarity, and Diátaxis mode consistency.
4. **Automated testing** — Prose linters (Vale), markdown linters (markdownlint), link checkers, and inclusive language checkers (Alex) run in CI on every documentation change.
5. **Build pipelines** — Static site generators (Sphinx, MkDocs, Docusaurus, Hugo) build docs in CI/CD and publish to a known URL on each merge.
6. **Issue tracking** — Documentation bugs are tracked in the same issue tracker as code bugs, with equivalent priority and labels.
7. **Named ownership** — Every doc has a maintainer named in frontmatter or a `CODEOWNERS` file. "Documentation is owned by everyone" is a failure mode.
8. **Collaboration** — Writers and developers share ownership. No docs silo. Developers write first drafts; technical writers improve them. Both review each other's work.

Sources: [writethedocs.org docs-as-code](https://www.writethedocs.org/guide/docs-as-code/), [konghq.com docs-as-code](https://konghq.com/blog/learning-center/what-is-docs-as-code), [blog.cloudflare.com docs-as-code approach](https://blog.cloudflare.com/our-docs-as-code-approach/).

## Directory Layout Convention

Docs-team recommends this directory structure for projects adopting docs-as-code:

```
docs/
├── tutorials/           # Diátaxis: Tutorial quadrant (learning-oriented)
├── how-to/              # Diátaxis: How-to quadrant (task-oriented)
├── reference/           # Diátaxis: Reference quadrant (information-oriented)
├── explanation/         # Diátaxis: Explanation quadrant (understanding-oriented)
├── adr/                 # Architecture Decision Records (Nygard/MADR)
│   ├── 0001-record-architecture-decisions.md
│   └── 0002-use-markdown-for-adrs.md
└── README.md            # Composite: Standard README spec
```

Each Diátaxis subdirectory contains files of only that mode. Mode-mixing across
directories is caught by the `rubrics/diataxis-mode-clarity.md` MUST gate.

ADRs follow the MADR convention: `docs/adr/NNNN-title.md` with sequential
numbering. See `protocols/write-adr.md`.

## Write the Docs Documentation Principles

Complementary to the operational principles, Write the Docs maintains a set
of writing principles:

- **ARID** — Acceptable to Repeated Information Duplication. Unlike strict DRY
  in code, some repetition in docs is desirable because readers don't read
  linearly. Repeat critical facts in multiple modes if needed.
- **Skimmable** — Write like a newspaper, not a novel. Descriptive headings,
  scannable structure, meaningful link text. Most readers scan before reading.
- **Consistent** — Use the same words for the same concepts. Inconsistent
  terminology forces the reader to re-learn.
- **Canonical (Up-to-date)** — "Incorrect documentation is worse than missing
  documentation." Stale docs actively mislead. See `standards/freshness-metadata.md`
  for the docs-rot mitigation approach.

Source: [writethedocs.org — Documentation principles](https://www.writethedocs.org/guide/writing/docs-principles/)

## Review Checklist (for PR reviewers)

When reviewing a documentation PR, check:

1. **Correctness** — Claims are accurate; code samples run as shown
2. **Mode clarity** — Document sits in exactly one Diátaxis quadrant (or labels each section for composite READMEs)
3. **Style** — Follows `standards/style-conventions.md`
4. **Links** — All links resolve; internal links use relative paths
5. **Examples** — Examples are minimal, runnable, and match current API
6. **Freshness** — Frontmatter `last_reviewed` updated if the file structure changed
7. **Completeness** — No "TODO" or "TBD" in production branches

## Sources

- [Write the Docs — Docs as Code](https://www.writethedocs.org/guide/docs-as-code/) — primary philosophy
- [Write the Docs — Documentation principles](https://www.writethedocs.org/guide/writing/docs-principles/) — ARID, Skimmable, Consistent, Canonical
- [Cloudflare — our docs-as-code approach](https://blog.cloudflare.com/our-docs-as-code-approach/) — enterprise case study
- [Kong — What is Docs as Code](https://konghq.com/blog/learning-center/what-is-docs-as-code) — community summary
