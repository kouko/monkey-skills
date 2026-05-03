---
name: wiki-cross-linker
description: Scan wiki/ for unlinked mentions of existing pages and convert to [[wikilinks]]. Run after each wiki-ingest batch to catch newly-mintable links. Do NOT use to author new pages (use wiki-ingest). Obsidian wiki リンク補強・連結補強・圖譜增強。
---

# Wiki Cross-Linker — Strengthen the Knowledge Graph

After `wiki-ingest`, recently-created pages may be mentioned as plain text in older pages. This skill scans the wiki, finds plain-text mentions of existing page titles, and converts them to `[[wikilinks]]`.

## Pre-flight

1. Read `.env` for `OBSIDIAN_VAULT_PATH` (defaults `wiki/`).
2. If wiki/ doesn't exist or `wiki/index.md` is empty, exit and tell user to run `/wiki-setup` then `/wiki-ingest`.

## STEP 1 — Build the link inventory

Read `wiki/index.md` and gather all page titles. For each, also collect:
- Filename slug (canonical wikilink target)
- Frontmatter `title:` (display alias)
- Common variants (e.g., "qlib" / "Qlib" / "QLib"; capture all from page bodies)

Build an inventory: `{search_phrase → canonical_wikilink}`.

For example:
```
"Thompson Sampling" → [[Thompson-Sampling]]
"thompson sampling" → [[Thompson-Sampling]]
"qlib"              → [[qlib]]
"alpha factor"      → [[alpha-factor]]
```

## STEP 2 — Scan all wiki pages

For each page under `wiki/{entities,concepts,synthesis,skills,journal,references}/`:

1. Read full body
2. For each phrase in inventory, find plain-text mentions **not already inside a wikilink**
3. Record candidate replacements

### What to skip

Do NOT touch:
- Text already inside `[[...]]` (already linked)
- Text inside fenced code blocks ```` ``` ```` (code samples, command examples)
- Text inside inline code `` `like this` ``
- The page that owns the title being matched (don't link a page to itself)
- Frontmatter (only modify body)
- `## User Notes` section (user-owned, do not touch)
- **Inside callout headers** — `> [!note]` / `> [!warning]` / etc. on their own line (the syntax marker, not the callout body). Callout BODY content is fair game and should be linked normally.
- **Existing markdown links** — `[link text](url)` (don't transform display text into wikilink)
- **Existing wikilinks with anchors** — `[[Page#Section]]` already has a target; do not double-process
- **Headings** — text inside `## Heading` lines is structural, don't link

### Edge cases (informed decisions)

- **Callout body** — `> Some text mentioning qlib` → link the mention as usual
- **Block quotes** (without callout) — `> Text mentioning qlib` → link the mention as usual
- **Lists / tables** — link inline mentions as usual
- **Plain text in heading** is skipped, but if user wants link in heading they can hand-edit later

## STEP 3 — Apply matching policy

Use **conservative matching**:

- **First mention only** per page — if "qlib" appears 5 times in a page, link only the first occurrence
- **Whole-word match** — don't link "qlib" inside "qlibrary"
- **Case-sensitive primary, case-insensitive fallback** — prefer exact case match; fall back to case-insensitive for proper nouns
- **Skip ambiguous matches** — if a phrase could mean two pages, leave it unlinked and report

If the user's wiki has many mentions, ask before applying:

```
Found 47 candidate links across 12 pages.
Examples:
  entities/quant-investing.md:23  — "...uses qlib for backtesting" → [[qlib]]
  concepts/exploration-exploitation.md:8 — "Thompson Sampling balances..." → [[Thompson-Sampling]]

Apply all? (yes / review / specific pages only)
```

## STEP 4 — Apply edits

Use `Edit` with `replace_all: false` — apply one edit at a time, validating context.

For each accepted change:
- Append page to a touched-list

## STEP 5 — Update connections section

After linking is done, optionally update the `## Connections` section of pages where new outgoing links were added. Only add if the link is structurally meaningful (i.e., the linked page is closely related, not just incidentally mentioned).

Format:
```markdown
## Connections
- [[NewlyLinkedPage]] — relationship reason (one sentence)
```

If you can't articulate a one-sentence reason, the inline link is enough — don't pad `## Connections`.

## STEP 6 — Log and report

Append to `wiki/log.md`:

```markdown
| YYYY-MM-DD | cross-linker | scope=all | <N> links added across <M> pages |
```

Report to user:
```
Cross-linking complete:
  Pages scanned:  47
  Links added:    23
  Connections updated: 8

Skipped (ambiguous):
  - "factor" (could be entities/alpha-factor or concepts/factor-investing)
  - ...

Next steps:
  /wiki-lint  — verify no broken links were introduced
```

## Boundaries (what wiki-cross-linker does NOT do)

- ❌ Does not create new pages (only links to existing ones)
- ❌ Does not infer semantic relationships beyond mention-matching
- ❌ Does not modify frontmatter or `## User Notes`
- ❌ Does not link inside code blocks
- ❌ Does not update reference pages' `contributes_to:` (that's `wiki-ingest`'s domain)
