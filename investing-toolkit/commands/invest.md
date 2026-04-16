# /invest

**Trigger**: `/invest`

Route to the right investing-toolkit skill or slash command. Displays available
capabilities and asks what you want to do.

## What This Does

Invokes `skills/using-investing-toolkit/SKILL.md` — the router skill.

If you have a specific intent, use the more direct commands:
- `/invest-macro` — macro regime call (IC + FRED)
- `/invest-memo {ticker}` — full investment memo pipeline
- `/invest-screen {ticker}` — quick stock screen (v1.2.0)
- `/invest-portfolio` — portfolio review (v1.2.0)

## Examples

```
/invest
/invest What can you do for Taiwan stocks?
/invest I want to analyze 2330.TW
```
