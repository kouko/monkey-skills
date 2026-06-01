---
name: wiki-merge
description: Consolidate a confirmed near-duplicate PAIR of wiki/ pages into one canonical page; human gates WHICH pair, the skill auto-executes the merge. Use when wiki-ingest STEP 4c or wiki-lint L15 flags a near-duplicate (e.g. `Thompson-Sampling` vs `Thompson-Sampling-MAB`) and you decide to merge it. Triggers: 「合併重複頁」「合併這兩頁」, 「重複ページ統合」「ページをマージ」, "merge duplicate pages" / "merge these two wiki pages". Do NOT use for wiki-ingest (which ADDS pages from source notes) or wiki-cross-linker (which LINKS existing pages without consolidating). wiki-merge WRITES — it collapses two pages into one and archives the absorbed page. Do NOT use for repo-wiki or dbt-wiki. Obsidian wiki 重複頁合併・近重複統合・知識圖譜去碎裂。
---

# Wiki Merge — Consolidate a Near-Duplicate Pair

Collapses a confirmed near-duplicate PAIR of `wiki/` pages — the same conceptual entity that two ingests named differently (e.g. `Thompson-Sampling` vs `Thompson-Sampling-MAB`) — into one canonical page. The **human decides WHICH pair to merge** (the trigger, gating against over-merge of distinct entities like John Doe / Doe Corp); the skill then **executes the merge automatically** (re-confirm same entity → consolidate content → archive the absorbed page → repoint inbound links). It handles **only the one triggered pair** — a third duplicate is left to wiki-ingest (forward) and wiki-lint L15 (audit), not chained inside a single merge.

## Pre-condition check

Read these BEFORE starting the merge:

1. **`wiki/` must exist** at the vault root (resolve via `.obsidian-wiki.config` → `OBSIDIAN_WIKI_VAULT_PATH`, same as wiki-ingest pre-flight). If `wiki/` is absent, instruct the user to run `/wiki-ingest` first and exit cleanly — there is nothing to merge.
2. **A candidate PAIR is required as input** — `wiki-merge` consolidates exactly two pages:
   - a **canonical-candidate** (the page that survives) and an **absorbed-candidate** (the page that is archived), or
   - **two slugs to reconcile**, in which case the skill picks the canonical one (more complete `## Summary` / higher `sources_count`) and surfaces that choice before writing.

   The pair normally arrives from a wiki-ingest STEP 4c prompt or a wiki-lint L15 finding that the human accepted.

   **If invoked with no pair** (plain `/wiki-merge`, no slugs / paths): do **not** guess a pair or scan for duplicates yourself (that is wiki-lint L15's job). Print the usage below and exit cleanly:

   ```
   wiki-merge consolidates ONE confirmed near-duplicate pair into a single canonical page.
   Usage: /wiki-merge <canonical-slug> <absorbed-slug>
          /wiki-merge <slug-a> <slug-b>   (skill picks the canonical one and confirms)

   No pair given. Find candidates first with /wiki-lint (L15 near-duplicate scan),
   then re-run /wiki-merge with the pair you want to consolidate.
   ```

<!-- The merge procedure (re-confirm → consolidate Summary/Key Facts/User Notes
     union → archive absorbed page to wiki/_archive/<date>/ → repoint inbound
     wikilinks → re-run cross-linker) is appended by a later step. -->
<!-- The safety invariants (User Notes union-preserve, non-destructive archive
     not hard-delete, old slug → canonical aliases, self-verify no fact loss,
     idempotent, log to wiki/log.md) are appended by a later step. -->

## Merge procedure

This runs **after** the human has already triggered the merge on a confirmed pair (the human gate happened upstream, at the wiki-ingest STEP 4c prompt or wiki-lint L15 finding the user accepted). The merge itself is **LLM-automatic** — no manual labor. Execute Steps A–D in order on the two pages of the triggered pair.

### Step A — re-confirm same entity

Even though the upstream flag may have been **HIGH**, re-verify before writing. Read both pages':

- `title` (frontmatter)
- `## Summary` body section
- `## Key Facts` body section

These are the same bounded, high-signal sections the near-duplicate judge reads (see `../wiki-ingest/references/near-duplicate-detection.md` §Stage 3). Decide: do these two pages describe **the same real-world entity**?

- **Same entity** → proceed to Step B.
- **NOT the same entity** (lexically close but content diverges — e.g. `John-Doe` the person vs `Doe-Corp` the company, contradictory Key Facts, different entity class) → **abort the merge**. Tell the user the pages are distinct and which evidence decided it; do **nothing** else (no archive, no link repoint, no write). When unsure, bias toward NOT merging (mirrors the upstream "human gates to block over-merge" posture).

### Step B — pick canonical

Choose the **surviving (canonical)** page; the other becomes the **absorbed** page. Apply this tie-break order:

1. **More inbound wikilinks** — the page that more `wiki/` pages already link to (fewer links to repoint, less graph disruption). Count inbound `[[slug]]` references across `wiki/`.
2. **Else higher frontmatter `sources_count`** — the page synthesized from more sources.
3. **Else the shorter / base-form slug** — prefer the qualifier-stripped name (`Thompson-Sampling` over `Thompson-Sampling-MAB`); the base form is the more stable canonical. (Deterministic from the slug itself — page-format frontmatter has no creation-date field.)

Surface the choice to the user before writing — state which page survives and which tie-break level decided it (e.g. *"keeping [[Thompson-Sampling]] over [[Thompson-Sampling-MAB]] — 4 inbound links vs 1"*).

### Step C — LLM drafts consolidated content

Draft the consolidated body + frontmatter for the canonical page (do not write yet — Step D applies):

- **`## Summary`** — take the **fuller / more-complete** Summary of the two, or write a merged rewrite that covers both. Keep the trailing confidence marker (`high | medium | unverified`) per the page-format spec.
- **`## Key Facts`** — **union** of both pages' bullets. Dedupe overlapping bullets (same claim stated twice → keep one). **Preserve provenance markers** (`^[inferred]` / `^[ambiguous]`) on the bullets that carry them — do not silently upgrade an inferred claim to a direct citation.
- **`## Sources`** — **union** of both pages' source links; dedupe identical entries.
- **frontmatter `sources_count`** — set to the **max** of the two pages' counts (or recount distinct contributing sources if the union of `## Sources` makes the true count clear).
- **frontmatter `updated`** — set to **today's date** (ISO `YYYY-MM-DD`).

Section names and frontmatter field semantics follow `../wiki-ingest/references/page-format.md` (the authoritative page-format spec — `## Summary`, `## Key Facts`, `## Sources`, `sources_count`, `updated`).

### Step D — apply

Write the consolidated content (Step C draft) to the **canonical** page chosen in Step B.

---

The remaining safety steps — preserving each page's User Notes, archiving the absorbed page non-destructively (not hard-delete), redirecting the old slug via `aliases`, repointing inbound wikilinks, self-verifying no fact was lost, and logging the merge — follow in **`## Safety invariants`** below.

## Safety invariants

These guardrails are what make the **LLM-automatic** merge (Steps A–D above) safe to run without manual labor. Honor every one; they are not optional polish.

### 1. User Notes always union-preserved

`## User Notes` is **user-authored** content under the override rule — it is the user's escape hatch for tribal knowledge that auto-generation must never overwrite (the same verbatim-preservation contract `wiki-ingest` honors; see `../wiki-ingest/references/delta-tracking.md` §User notes preservation). When you draft the consolidated body in **Step C**, the merged canonical page MUST contain the **UNION** of both source pages' `## User Notes`, copied **verbatim** — never dropped, never rewritten, never summarized. If only one page has a `## User Notes` section, carry it over unchanged; if both have one, concatenate both note blocks under a single `## User Notes` heading. If neither page has one, do not invent the section.

### 2. Self-verify before finalizing

After drafting the consolidated page in **Step C** and **before** the **Step D** write, re-read **both source pages and the draft** and confirm:

- **No fact was lost** — every `## Key Facts` bullet, every `## Sources` entry, and every `## User Notes` line from both source pages survives in the draft (or is a deliberate, justified dedupe of an identical claim).
- **No contradictory fact was silently dropped** — if the two pages assert mutually exclusive claims, the draft must surface the conflict (e.g. a `## Contradictions` section or a `[!warning]` callout per page-format spec), not quietly pick one side.

If self-verification **fails** → **ABORT**: do **not** perform the Step D write, do **not** archive, do **not** repoint links. Flag the failure to the user with exactly **what would be lost** (which bullet / source / note / contradiction), and let them decide.

### 3. Non-destructive archive (reversible)

In the archive step, the **absorbed** page (the non-canonical one from Step B) is **MOVED** to `wiki/_archive/<date>/` (ISO `YYYY-MM-DD` subfolder) — **NEVER hard-deleted**. The original file is preserved intact at its archive path, so any wrong merge is **one-step reversible** (move the file back, undo the canonical edits). This mirrors `wiki-ingest`'s "keep the entry for audit trail, never silently destroy" posture.

### 4. Old slug → canonical `aliases:`

Add the **absorbed page's slug** to the **canonical** page's frontmatter `aliases:` list (per the `aliases` field in `../wiki-ingest/references/page-format.md`). This is the **redirect analog**: old `[[absorbed-slug]]` wikilinks and Obsidian searches for the old name still resolve to the surviving canonical page. Append, do not replace — preserve any aliases the canonical page already carried.

### 5. Repoint inbound wikilinks

Update every `[[absorbed-slug]]` reference **across `wiki/`** to point at the **canonical** slug, so no inbound link dangles after the absorbed page moves to `_archive/`. This catches explicit wikilinks. Plain-text mentions of the absorbed page's name are **not** wikilinks and are out of scope here — re-running `/wiki-cross-linker` afterward catches those (it scans for plain-text mentions of existing page titles and converts them to `[[wikilinks]]`).

### 6. Idempotent (partial-failure safe)

**Commit order** (so partial state is recoverable): Step D write canonical → append absorbed slug to `aliases:` (#4) → repoint inbound wikilinks (#5) → **archive the absorbed page** (#3) → log (#7). Archiving is the **last** step, so "absorbed page no longer in live `wiki/` (now under `wiki/_archive/`)" is the single **completion signal**.

Re-run behavior keys on that completion signal, **not** on an OR of intermediate signals (which would falsely no-op a half-finished merge):
- **Absorbed page already archived** → fully merged → **no-op**, exit cleanly.
- **Absorbed page still live in `wiki/` but some steps already applied** (e.g. alias present from a crashed prior run) → **resume, do not no-op**: re-apply the remaining steps in order. Each step is individually idempotent — appending an alias that already exists, repointing an already-repointed link, and writing the same consolidated content are all no-ops — so resuming is safe and converges. Then archive + log to finish.

Never double-archive, double-append aliases, or corrupt the canonical page.

### 7. Audit log

Append a single line to `wiki/log.md` recording the merge — **which page was kept (canonical)**, **which was archived (absorbed)**, and the **date** — consistent with the logging convention `wiki-ingest` uses (`../wiki-ingest/references/delta-tracking.md` §Logging). Example:

```markdown
| 2026-06-01 | merge | kept Thompson-Sampling, archived Thompson-Sampling-MAB → _archive/2026-06-01/ |
```

### 8. Single-pair scope

Operate **only** on the one triggered pair. Do **NOT** cascade to a third page even if you notice another near-duplicate while merging — forward discovery is `wiki-ingest`'s job and audit-time discovery is `wiki-lint` L15's job. One invocation consolidates exactly one pair.

### NEVER / ALWAYS

| NEVER | ALWAYS |
|---|---|
| NEVER hard-delete the absorbed page | ALWAYS archive it (move to `wiki/_archive/<date>/`), not delete |
| NEVER drop or rewrite `## User Notes` | ALWAYS log the merge to `wiki/log.md` |
| NEVER write (Step D) on a failed self-verify — ABORT and flag | ALWAYS add the absorbed slug to the canonical page's `aliases:` |
| NEVER auto-merge without the upstream human trigger (wiki-ingest STEP 4c / wiki-lint L15 the user accepted) | |
