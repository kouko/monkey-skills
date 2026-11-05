---
name: defuddle
description: |
  Extract web pages and YouTube transcripts with Defuddle CLI. Use for articles, documentation, blog posts, and video transcript requests.
---

# Defuddle

Use Defuddle CLI to extract readable content from web pages. Prefer it over WebFetch for standard web pages; for URLs ending in `.md`, use WebFetch directly.

The examples below were verified with Defuddle 0.19.6. Check `defuddle --version` if an option is unavailable. If the CLI is missing, report that it is required; installation: `npm install -g defuddle`.

## Usage

Use `--md` for markdown output (quote URLs in the shell):

```bash
defuddle parse '<url>' --md
```

Save to file:

```bash
defuddle parse '<url>' --md -o content.md
```

Extract specific metadata:

```bash
defuddle parse '<url>' -p title
defuddle parse '<url>' -p description
defuddle parse '<url>' -p domain
```

Add `--frontmatter` to include metadata with markdown. Local HTML can be supplied as a file path, or via standard input using `defuddle parse - --md`.

## YouTube transcripts

For a video URL, request JSON to inspect the transcript and its language:

```bash
defuddle parse '<youtube-url>' --json --lang ja
```

`--lang` is a preference, not a translation request or a guarantee that a matching track exists. Omit it when no language was requested. The JSON `variables.transcript` contains the transcript when available; inspect the returned `language` and the text before reporting the actual language. The transcript can contain timestamps and chapters. Markdown output can also include the video link and description, so do not treat the entire page as the transcript. `-p transcript` does not retrieve the nested field in 0.19.6.

Check both the command result and `variables.transcript`: a successful parse may still have a missing or empty transcript. Report an extraction error, missing transcript, unknown language, or different returned language explicitly. Do not invent or translate transcript text to fill a gap; use another available source only if appropriate and identify it.

## Output formats

| Flag | Format |
|------|--------|
| `--md` | Markdown (default choice) |
| `--json` | JSON with both HTML and markdown |
| `--frontmatter` | Add metadata before output |
| `--lang <code>` | Preferred language for the page and transcript |
| (none) | HTML |
| `-p <name>` | Specific metadata property |
