---
name: page-backlinks
purpose: Find all pages linking to a target Notion page.
---

## Inputs
- `page_url`: required.
- `--json`: optional.

## Output
```
## Pages linking to <target>

- **<linking page title>** — <path>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| Backlinks region | `[region] "Backlinks"` | `[region] "反向連結"` | `[region] "バックリンク"` |
| More-options button | `[button] "More options"` or `"..."` | `[button] "更多選項"` or `"..."` | `[button] "その他のオプション"` or `"..."` |
| Show-backlinks menuitem | `[menuitem] "Show backlinks"` | `[menuitem] "顯示反向連結"` | `[menuitem] "バックリンクを表示"` |

## Procedure

1. ```bash
   abx open <page_url>
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Look for Backlinks region (locale-dependent). If present, extract `[link]` children: name + href.

3. **If Backlinks region NOT present**:
   - Find More-options button (locale-dependent). Click + re-snapshot.
   - Find Show-backlinks menuitem (locale-dependent). Click + re-snapshot.
   - Now find Backlinks region.

4. If still absent → zero backlinks (valid empty).

## Failure modes

- **More-options button missing** → page UI changed.
- **Show-backlinks menuitem missing** → option moved / disabled.

## Notes

- Backlinks visibility is per-page (page settings toggle).
- Sub-pages count as backlinks if they link back.

## Examples

Input: `page_url = ...` → Markdown list of linking pages.
