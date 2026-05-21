---
name: gws-sheets-append
description: "Google Sheets: Append a row to a spreadsheet."
metadata:
  vendored_from: "googleworkspace/cli@705fb0ecac6f4249679958f6325b809b63fdde17"
  vendored_release: "v0.22.5"
  vendored_at: "2026-05-20"
  upstream_license: "Apache-2.0"
  version: 0.22.5
  openclaw:
    category: "productivity"
    requires:
      bins:
        - gws
    cliHelp: "gws sheets +append --help"
---

# sheets +append

> **PREREQUISITE:** Read `../gws-shared/SKILL.md` for auth, global flags, and security rules. If missing, run `gws generate-skills` to create it.

Append a row to a spreadsheet

## Usage

```bash
gws sheets +append --spreadsheet <ID>
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--spreadsheet` | ✓ | — | Spreadsheet ID |
| `--values` | — | — | Comma-separated values (simple strings) |
| `--json-values` | — | — | JSON array of rows, e.g. '[["a","b"],["c","d"]]' |

## Examples

```bash
gws sheets +append --spreadsheet ID --values 'Alice,100,true'
gws sheets +append --spreadsheet ID --json-values '[["a","b"],["c","d"]]'
```

## Tips

- Use --values for simple single-row appends.
- Use --json-values for bulk multi-row inserts.

> [!CAUTION]
> This is a **write** command — confirm with the user before executing.

## See Also

- [gws-shared](../gws-shared/SKILL.md) — Global flags and auth
- [gws-sheets](../gws-sheets/SKILL.md) — All read and write spreadsheets commands
