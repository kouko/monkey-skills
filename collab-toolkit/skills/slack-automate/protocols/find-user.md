---
name: find-user
purpose: Search Slack users by name / email / handle.
---

## Inputs
- `query`: required.
- `--json`: optional.

## Output
```
## Slack users matching "<query>"

**<Display Name>** · @<handle> · <email>
Status: <Active | Away>
Title: <job title>
```

## Localized labels

| Element | en | zh-TW | ja |
|---|---|---|---|
| People sidebar link | `[link] "People"` or `"More"` | `[link] "成員"` or `"更多"` | `[link] "メンバー"` or `"その他"` |
| People grid heading | `[grid] "People"` | `[grid] "成員"` | `[grid] "メンバー"` |
| Search input within People | `[textbox]` or `[combobox]` | `[textbox]` or `[combobox]` | `[textbox]` or `[combobox]` |

## Procedure

1. ```bash
   abx open https://app.slack.com
   abx wait --load networkidle
   abx snapshot -i
   ```

2. **Read snapshot**. Find People link (locale-dependent). NOTE: free Slack may lack People view → see Failure modes.

3. Click + re-snapshot:
   ```bash
   abx click @eN
   abx wait --load networkidle
   abx snapshot -i
   ```

4. **Find People grid search input**. Fill + submit:
   ```bash
   abx fill @eM "<query>"
   abx press Enter
   abx wait 1000
   abx snapshot -i
   ```

5. **Read results**. User cards as `[row]` / `[listitem]`. Extract name / handle / email / title / status.

6. Format Markdown.

## Failure modes

- **No People link** → free Slack tier. **Fallback**: open any channel, type `@<query>` in composer (DON'T send), snapshot typeahead.
- **Empty results** → valid.
- **Login wall** → reauth.

## Notes

- Slack hides email per privacy settings — may be `(hidden)`.
- Activity status (Active/Away) shifts in real time.

## Examples

`query = "alice"` → Markdown list of matching users.
