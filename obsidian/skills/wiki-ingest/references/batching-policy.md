# Batching Policy — Cap, Order, and Date Resolution

`wiki-ingest` processes source notes in controlled batches. This reference defines how the batch is selected: which files are eligible, how they are ordered, how many are taken, and what happens to the rest. It is the authoritative spec for `STEP 3` of the ingest pipeline and for the `obsidian/skills/wiki-ingest/scripts/select-batch.py` implementation.

---

## 1. Purpose

Every `wiki-ingest` run must balance two competing concerns: ingesting as many stale notes as possible, and keeping each run small enough for a human to spot degraded output before it propagates. The cap policy answers the second concern; the batch order policy answers the first.

This document captures the decisions behind `OBSIDIAN_WIKI_MAX_PAGES_PER_INGEST` (cap), `BATCH_ORDER` (sort direction), `BATCH_CAP` (the internal env var the script consumes), and `TOPIC_FILTER` (post-bucket substring filter). It describes the date resolution algorithm that drives sorting, documents how NEW and MODIFIED files interact before the cap is applied, and explains what happens to files that have no deterministic date. Worked examples ground each rule in concrete test cases.

---

## 2. Date Resolution Algorithm

Every eligible source file is assigned a sort date via a 3-tier decision tree. Tiers are evaluated in order; the first successful match wins and lower tiers are not consulted.

```
For each candidate file abs_path:
  │
  ├─ Tier 1 — Filename prefix
  │    Does basename match /^(\d{4}-\d{2}-\d{2})/?
  │    YES → use that date string              (tier = "filename")
  │
  ├─ Tier 2 — Frontmatter field
  │    Read file text; extract YAML frontmatter block (--- ... ---)
  │    Scan block for first field matching:
  │      /^(?:date|upload_date|processed_at)\s*:\s*(\d{4}-\d{2}-\d{2})/
  │    Found → use that date string            (tier = "frontmatter")
  │
  └─ Tier 3 — mtime fallback
       No filename prefix AND no frontmatter date found
       → date = None                           (tier = "mtime")
         File is treated as "undated"; sort key = (1, file mtime)
         (see §6 — always sorted to tail)
```

**Frontmatter field precedence**: `date`, `upload_date`, `processed_at` — whichever appears first in the frontmatter block wins. These are the exact field names the regex `_FM_FIELD_RE` in `select-batch.py` matches; other field names (e.g. `created`, `modified`) are not recognised and do not contribute a date.

**Filename always beats frontmatter**: a file named `2020-01-01 conflicting.md` with `date: 2025-12-31` in its frontmatter is sorted at `2020-01-01`. The filename prefix is the most deterministic signal (user-controlled, filesystem-visible, no parse ambiguity), so it takes Tier 1 unconditionally.

**Date format**: ISO 8601 `YYYY-MM-DD`. Lexicographic sort on this format is identical to chronological sort, so no datetime parsing is required — the script compares date strings directly.

---

## 3. Cap Semantics

`BATCH_CAP` (runtime) / `OBSIDIAN_WIKI_MAX_PAGES_PER_INGEST` (config) counts **source files**, not wiki page outputs.

**Why source files, not wiki pages?**

One source note can contribute to multiple wiki pages — a paper on Thompson Sampling might update `entities/Thompson-Sampling.md`, `entities/UCB.md`, and `concepts/exploration-exploitation.md`. If the cap were denominated in wiki page outputs, the batch size would be unpredictable (it depends on how the LLM routes each source). Capping at source count keeps each batch deterministic and easy to review: a cap of 15 means exactly 15 source files enter `STEP 4`, regardless of how many wiki pages they each touch.

**Default**: 15. Configurable via `OBSIDIAN_WIKI_MAX_PAGES_PER_INGEST` in `.obsidian-wiki.config`; passed to the script as `BATCH_CAP`. The script validates that `BATCH_CAP` is a positive integer and exits `2` if not.

**Cap applies after sort**: the script sorts the full NEW + MODIFIED list first, then slices `sorted_items[:BATCH_CAP]` as `batch` and `sorted_items[BATCH_CAP:]` as `remaining`. There is no per-bucket sub-cap; the combined sorted list is truncated once.

---

## 4. NEW vs MODIFIED Interaction

NEW files (no manifest entry) and MODIFIED files (manifest entry exists but SHA-256 has changed) are treated as a single pool. They are concatenated into `to_process`, sorted together by the 3-tier date resolution algorithm, and the combined list is subject to the cap.

```
candidates (stdin)
  │
  ├── UNCHANGED → skipped_unchanged counter (not in batch, not in remaining)
  │
  └── NEW + MODIFIED → to_process[]
        │
        ├── dated   → sort by date asc or desc (per BATCH_ORDER)
        └── undated → sort by mtime asc (always tail)
              │
              combined sorted_items = dated + undated
                │
                ├── sorted_items[:BATCH_CAP]  → "batch"
                └── sorted_items[BATCH_CAP:]  → "remaining"
```

**Rationale (catch-up posture)**: treating NEW and MODIFIED as equal load reflects the design goal — `wiki-ingest` is for users with large backlogs who want to process notes in chronological order regardless of whether they have been seen before. A modified old note should not jump the queue ahead of newer notes simply because it was previously ingested; it re-enters the sorted list at its original date position.

**UNCHANGED files never enter the batch or remaining lists**. They are counted in `skipped_unchanged` in the JSON output but consume no cap slots.

---

## 5. Order Override Matrix

The sort direction for dated files is controlled by `BATCH_ORDER`. The value reaching the script is determined by a three-level priority chain:

| Priority | Source | Mechanism |
|---|---|---|
| 1 (highest) | Prompt hint | Claude maps time keywords to `BATCH_ORDER` value in STEP 1 |
| 2 | Config | `OBSIDIAN_WIKI_BATCH_ORDER` in `.obsidian-wiki.config` |
| 3 (default) | Hardcoded | `oldest-first` |

**STEP 1 decision table** (summarised from `SKILL.md`):

| Prompt pattern | `BATCH_ORDER` passed to script |
|---|---|
| Plain `/wiki-ingest` | from config (default `oldest-first`) |
| Path token (contains `/`, not `.md`) | from config |
| Single-file token (ends `.md`) | n/a — not batched |
| `latest` / `recent` / `newest` / `最新` / `近期` | `newest-first` (prompt override) |
| `oldest` / `backfill` / `最舊` / `從頭` / `舊筆記` | `oldest-first` (prompt override) |
| Topic word (no path, no time-keyword) | from config |

**`BATCH_ORDER` accepted values**: `oldest-first` or `newest-first`. Any other value causes the script to exit with code `2` and print an error to stderr.

**`TOPIC_FILTER` interaction**: `TOPIC_FILTER` is a case-insensitive substring filter applied to a file's basename, frontmatter tags, and frontmatter aliases. It is applied **after** the NEW/MODIFIED bucket is built and **before** the date sort + cap. Files that do not match the filter are excluded from `to_process` entirely (they are neither in `batch` nor `remaining`). The order override matrix is independent of `TOPIC_FILTER`; after filtering, the surviving files are sorted and capped normally.

```
candidates
  → bucket (NEW / MODIFIED / UNCHANGED)
  → [TOPIC_FILTER applied here, if set]
  → date sort (per BATCH_ORDER)
  → cap slice
  → batch + remaining
```

> **Note**: `TOPIC_FILTER` support is added in commit 2 of the feature branch. In commit 1, the env var is accepted but has no effect (the script currently does not implement the filter; it is a planned extension). See §6 of the design doc for the authoritative commit-2 contract.

---

## 6. Undated Files Behavior

A file is **undated** when both of the following hold:
1. Its basename does not begin with a `YYYY-MM-DD` prefix.
2. Its frontmatter block (if any) contains no `date`, `upload_date`, or `processed_at` field with a valid `YYYY-MM-DD` value.

**Sort key for undated files**: `(1, mtime)` — a 2-tuple where the first element is `1`. Dated files use `(0, date_str)`. Because `0 < 1`, all dated files sort before all undated files, regardless of `BATCH_ORDER`. Within the undated tail, files are sorted by `mtime` ascending, always — the `BATCH_ORDER` direction does not invert the undated sub-sort.

**Why mtime fallback?** It is the only per-file timestamp available without content parsing. It is used solely as a tiebreaker within the undated group; it is never used to compare an undated file against a dated one.

**Why always tail?** Undated files have no deterministic content date. Mixing them with dated files would contaminate a chronological oldest-first or newest-first ordering with filesystem-arbitrary timestamps. Sorting them to the tail keeps the dated portion of the batch chronologically clean and prevents a file with a recent mtime from jumping ahead of genuinely older dated notes.

**Practical implication**: if a vault has 50 dated files and 10 undated files, a cap of 15 will always pick the first 15 dated files (oldest-first) and none of the undated files, until all dated files are processed. Users who want to process undated files sooner should add a `date` frontmatter field or rename the file with a `YYYY-MM-DD` prefix.

---

## 7. Worked Examples

The following three examples are drawn directly from `obsidian/tests/wiki_ingest/test_select_batch.py`. Each corresponds to a named test case (CC-01, CC-03, CC-07).

---

### Example A — CC-01: All dated filenames, empty manifest

**Setup**:
- 8 source files, all with `YYYY-MM-DD` filename prefixes spanning 2019–2024.
- Manifest: `{}` (no prior entries) → all 8 files are NEW.
- `BATCH_CAP=15`, `BATCH_ORDER=oldest-first`.

**Files** (unsorted as created):
```
2019-06-01 alpha.md
2024-01-01 theta.md
2023-07-04 eta.md
2020-03-15 beta.md
2020-11-22 gamma.md
2021-04-07 delta.md
2021-09-30 epsilon.md
2022-02-14 zeta.md
```

**Expected output**:
```json
{
  "batch": [
    "2019-06-01 alpha.md",
    "2020-03-15 beta.md",
    "2020-11-22 gamma.md",
    "2021-04-07 delta.md",
    "2021-09-30 epsilon.md",
    "2022-02-14 zeta.md",
    "2023-07-04 eta.md",
    "2024-01-01 theta.md"
  ],
  "remaining": [],
  "skipped_unchanged": 0,
  "scope_summary": {
    "first_date": "2019-06-01",
    "last_date": "2024-01-01",
    "remaining_count": 0,
    "remaining_first_date": null,
    "remaining_last_date": null
  }
}
```

**What this demonstrates**:
- Tier 1 date resolution (filename prefix) works correctly for all 8 files.
- Lexicographic sort on ISO 8601 prefix produces correct chronological order.
- All 8 files fit within cap=15, so `remaining` is empty.
- `scope_summary.first_date` / `last_date` reflect the batch's date range, not remaining.

---

### Example B — CC-03: Mixed 50 dated + 10 undated, cap=15

**Setup**:
- 50 dated files: `2000-01-01 note-00.md` through `2000-02-19 note-49.md` (consecutive days).
- 10 undated files: `undated-00.md` through `undated-09.md`, with mtimes set to `1577836800 + (i+1)*60` (strictly ascending).
- Manifest: `{}` → all 60 files are NEW.
- `BATCH_CAP=15`, `BATCH_ORDER=oldest-first`.

**Expected output (abbreviated)**:
```json
{
  "batch": [
    "2000-01-01 note-00.md",
    "2000-01-02 note-01.md",
    "2000-01-03 note-02.md",
    "... (12 more dated files, through 2000-01-15 note-14.md)"
  ],
  "remaining": [
    "2000-01-16 note-15.md",
    "... (34 more dated files, through 2000-02-19 note-49.md)",
    "undated-00.md",
    "undated-01.md",
    "... (8 more undated files)"
  ],
  "skipped_unchanged": 0,
  "scope_summary": {
    "first_date": "2000-01-01",
    "last_date": "2000-01-15",
    "remaining_count": 45,
    "remaining_first_date": "2000-01-16",
    "remaining_last_date": "2000-02-19"
  }
}
```

**What this demonstrates**:
- With 60 eligible files and cap=15, only the 15 oldest dated files enter `batch`.
- All 10 undated files appear at the end of `remaining` (tail position, sorted by mtime asc).
- `scope_summary` dates are computed from dated items only; undated files do not contribute to `first_date` / `last_date` in either `batch` or `remaining`.
- `remaining_count` is 45 (35 dated + 10 undated), confirming the combined list is capped once, not per-bucket.

---

### Example C — CC-07: Cap squeeze — 3 MODIFIED + 13 NEW = 16 total, cap=15

**Setup**:
- 16 files: `2023-01-01 note-01.md` through `2023-01-16 note-16.md`.
- Manifest pre-populated with **stale hashes** for the first 3 files (`2023-01-01`, `2023-01-02`, `2023-01-03`) → those 3 are MODIFIED. The remaining 13 are NEW.
- `BATCH_CAP=15`, `BATCH_ORDER=oldest-first`.

**Expected output**:
```json
{
  "batch": [
    "2023-01-01 note-01.md",
    "2023-01-02 note-02.md",
    "2023-01-03 note-03.md",
    "2023-01-04 note-04.md",
    "2023-01-05 note-05.md",
    "2023-01-06 note-06.md",
    "2023-01-07 note-07.md",
    "2023-01-08 note-08.md",
    "2023-01-09 note-09.md",
    "2023-01-10 note-10.md",
    "2023-01-11 note-11.md",
    "2023-01-12 note-12.md",
    "2023-01-13 note-13.md",
    "2023-01-14 note-14.md",
    "2023-01-15 note-15.md"
  ],
  "remaining": [
    "2023-01-16 note-16.md"
  ],
  "skipped_unchanged": 0,
  "scope_summary": {
    "first_date": "2023-01-01",
    "last_date": "2023-01-15",
    "remaining_count": 1,
    "remaining_first_date": "2023-01-16",
    "remaining_last_date": "2023-01-16"
  }
}
```

**What this demonstrates**:
- NEW and MODIFIED files sort together by date; the 3 MODIFIED files occupy their natural date positions (oldest 3) in the combined list, not a separate bucket.
- Cap=15 squeezes exactly 1 file to `remaining` (the 16th, `2023-01-16`), confirming cap applies to the combined NEW+MODIFIED pool.
- `skipped_unchanged` is 0 because the manifest only has entries for the 3 MODIFIED files (stale hash), and there are no UNCHANGED files in this fixture.
- This is the only test case that requires a pre-populated manifest; it uses a dedicated test function (`test_select_batch_cc07`) because the shared parametrize harness always writes `{}` to the manifest.

---

## 8. `/loop` Integration Note

`wiki-ingest` does **not** currently support `/loop` integration for automatic multi-batch runs.

**Why not**: each batch processes up to `BATCH_CAP` source files (default 15), which typically generates ~15–30 wiki page writes and edits. The quality of those writes depends on LLM judgment applied to each source, and degraded output (wrong category routing, stale wikilinks, over-broad synthesis) is not detectable programmatically. Auto-looping without a human quality checkpoint between batches risks propagating degraded pages silently across the wiki.

The deliberate design choice is: one batch per invocation, with a human seeing the STEP 6 report before deciding whether to re-invoke. The STEP 6 report includes the `remaining_count` and date range of the next batch as a prompt for the user, reducing the friction of the next manual invocation without removing the quality checkpoint.

If a user's vault has thousands of NEW files and wants to process them in bulk, the recommended workflow is:
1. Run `/wiki-ingest` → review STEP 6 report.
2. Run `/wiki-lint` periodically to catch structural issues.
3. Re-invoke `/wiki-ingest` when satisfied with the previous batch.

A future `/loop` integration would require a programmatic quality gate (e.g. lint score, wikilink density threshold) before it could safely auto-continue. That is out of scope for this version.
