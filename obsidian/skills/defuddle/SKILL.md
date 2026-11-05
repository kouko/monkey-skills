---
name: defuddle
description: |
  Extract web pages and YouTube transcripts with Defuddle CLI. Use for articles, documentation, blog posts, and video transcript requests.
---

# Defuddle

Use Defuddle CLI to extract readable content from web pages. Prefer it over WebFetch for standard web pages; for URLs ending in `.md`, use WebFetch directly.

If the CLI is missing, report that it is required; install with `npm install -g defuddle`. Prefer the latest version for YouTube fixes, including those in 0.19.6; use `defuddle --version` to check the installed version.

## Usage

Use `--md` for markdown output (quote URLs in the shell):

```bash
defuddle parse '<url>' --md
```

Save to file:

```bash
defuddle parse '<url>' --md -o content.md
```

Extract a metadata property (`title`, `description`, or `domain`):

```bash
defuddle parse '<url>' -p title
```

Defuddle 0.19.0+ supports `--frontmatter` and standard input (`defuddle parse - --md`).

## YouTube transcripts

Release notes introduced YouTube transcripts in 0.12.0 and preferred transcript language handling in 0.15.0.

Use Markdown for a video URL:

```bash
defuddle parse '<youtube-url>' --md
```

To request a preferred language, add `--lang ja`. This is a preference, not a guarantee or a translation request. Verify that the output contains a transcript, check its actual language from the text, and report missing captions, a different language, or command failure. If the language cannot be determined, report it as unknown; video descriptions are not transcripts.

For structured output, use `--json`: `variables.transcript` holds the transcript when available. The top-level `language` may come from page metadata and is only a clue.

Without `--md` or `--json`, output is HTML.
