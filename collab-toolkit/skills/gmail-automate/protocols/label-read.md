---
name: label-read
purpose: Read messages under a Gmail label. Supports single-level nesting.
---

## Inputs
- `label_name`: required. Top-level or `parent/child`.
- `limit`: optional, default 20.
- `--json`: optional.

## Output
```
## <label_name> (N messages)

- <YYYY-MM-DD> <from>: <subject> — <snippet>
```

## Localized labels

Labels themselves are user-defined (no translation table). Only UI affordances:

| Element | en | zh-TW | ja |
|---|---|---|---|
| Expand-parent twisty button | (varies — no explicit name; identified by position) | (same) | (same) |

## Procedure

1. ```bash
   abx open https://mail.google.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Sidebar labels appear as `[link]` with name = label name (user-defined; matches in all locales).

3. **For nested `parent/child`**:
   - Find `[link] "<parent>"` — note sibling `[button]` (expand twisty)
   - Click the expand button (NOT the parent link itself; clicking the link navigates):
     ```bash
     abx click @eN   # expand twisty
     abx wait 500
     abx snapshot -i
     ```
   - Now look for `[link] "<parent>/<child>"` (Gmail uses `/` in label paths regardless of locale)

4. Click target label link:
   ```bash
   abx click @eM
   abx wait --load networkidle
   abx snapshot -i
   ```

5. **Read filtered mail list**. Same row structure as inbox-summary. Extract first `limit` rows.

6. Format Markdown.

## Failure modes

- **Label not in sidebar** → collapsed under parent (expand) OR hidden in label settings.
- **Multi-level nesting** (`parent/child/grandchild`) → v0.1.6 supports single-level only. Use `mail-search.md` with `label:<full path>` for deeper.
- **Login wall** → reauth.

## Notes

- **v0.1.6 nesting limit**: single-level (`parent/child`). For deeper: expand sidebar manually or use `mail-search.md` with `label:` operator.
- Label paths use `/` separator regardless of UI language.

## Examples

`label_name = "Work/Projects"` → messages with that label.
