# Delta Tracking — `.manifest.json` Contract

`wiki-ingest` must avoid reprocessing unchanged sources. The `.manifest.json` file at `wiki/.manifest.json` is the source of truth for "what has been ingested at what state".

## Structure

```json
{
  "<vault-relative-source-path>": {
    "sha256": "<hex digest of file content>",
    "last_ingested": "YYYY-MM-DDTHH:MM:SSZ",
    "wiki_pages": ["entities/qlib.md", "concepts/quantitative-investing.md"]
  },
  "...": { ... }
}
```

## Algorithm

For each candidate source file under the vault (whole-vault scan minus exclusions per `OBSIDIAN_WIKI_EXCLUDE_DIRS` in `.obsidian-wiki.config` and the hardcoded blacklist; see [source-scope.md](source-scope.md)):

1. **Hash** — compute SHA-256 of the file content (not metadata)
2. **Lookup** — read `.manifest.json` for prior entry
3. **Decide**:
   - No prior entry → **NEW** → ingest fully
   - Prior entry, hash matches → **UNCHANGED** → skip
   - Prior entry, hash differs → **MODIFIED** → re-ingest, update affected wiki pages, append to `wiki_pages` (don't replace — sources can grow contributions over time)
4. **Record** — after successful ingest, update the manifest entry

## Bash one-liner for hashing

```bash
shasum -a 256 "$source_file" | awk '{print $1}'
```

## Why content hash, not mtime

- mtime changes from filesystem operations (cp, mv) without content change
- mtime is unreliable across machines and cloud sync
- Content hash makes ingest **idempotent** — a critical property

## Update flow

After ingest of a single source `S`:

```python
# pseudo-code for the manifest update
new_entry = {
    "sha256": sha256_of(S),
    "last_ingested": now_iso8601(),
    "wiki_pages": existing_pages + newly_touched_pages  # union, not overwrite
}
manifest[S] = new_entry
write_manifest(sorted_keys=True, indent=2)
```

Sort keys for git-friendly diffs even though `.manifest.json` is gitignored — useful for ad-hoc inspection.

## When to invalidate the manifest

User-triggered scenarios:
- `/wiki-setup --force` resets manifest to `{}`
- Page format spec changes materially → `wiki-lint` may flag stale pages, ingest re-processes affected sources
- Source folder is reorganized → manifest entries are pruned for paths that no longer exist

`wiki-ingest` never silently invalidates; always logs to `wiki/log.md`.

## Edge cases

| Scenario | Handling |
|---|---|
| Source deleted | Manifest entry kept (audit trail); affected wiki pages flagged by `wiki-lint` as `stale-source` |
| Source moved (rename) | Treated as delete + new (manifest grows). User can manually reconcile if desired |
| Source is a folder | Recurse, hash each file; entry per file |
| Binary files (PDFs, images) | Hash binary content; ingest defers to user (out of scope for wiki-ingest unless paired with `obsidian-file-intel`) |
| Wiki page is hand-edited after ingest | Manifest still says ingested; next ingest of same source overwrites. **User-edits live in body's `## User Notes` section, which `wiki-ingest` preserves verbatim** |

## User notes preservation

`wiki-ingest` MUST preserve any `## User Notes` section in an existing wiki page. This is the user's escape hatch for tribal knowledge that shouldn't be overwritten by re-ingest.

```markdown
## Key Facts
... auto-generated, freely overwritable ...

## User Notes
<!-- preserved verbatim across ingest cycles -->
- Manual annotation here
- Another note
```

If `## User Notes` doesn't exist, do not create it. Only preserve if present.

## Logging

After each ingest run, append to `wiki/log.md`:

```markdown
| 2026-05-03 | ingest | references/2026-04-20-台積電財報.md | entities/TSMC.md (new), concepts/CoWoS.md (updated) |
```
