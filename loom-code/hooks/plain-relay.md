# Plain-Relay Contract (loom family)

Scope: every user-visible CHAT message produced while a loom skill is active.
Machine-facing artifacts (briefs, verdicts, commits, plan docs) are exempt and
stay machine-precise. Render all meanings in the live conversation language.

1. FIRST LINE = plain conclusion. One sentence: what just happened + what it
   means for the user. Never open with a stage name, a score fraction
   ("PASS 14/14"), a token cost, or process meta.
2. TRANSLATE every internal token via the glossary below before it reaches
   the user. Raw tokens never appear untranslated in chat.
3. HARD CAPS: default reply ≤10 lines; one idea per sentence; ≤3 bullets per
   group. Anything beyond the cap: offer "want the details?" and hold it.
4. ONE decision per ask: ≤3 options + a named default recommendation.
   Stakes line first (what changes for the user), options after.
5. NEVER lead with a raw gate/error string. Plain words first (what happened,
   what the options are); verbatim text last, and only if useful.
6. ANNOUNCE stages in outcome language ("next I'll confirm the requirement
   boundary"), never internal markers ("— Phase ① USM backbone —",
   "Stage 1 = brainstorming (Axis 0…)").
7. STATUS SYMBOLS carry their meaning inline ("🟡 = worth fixing, doesn't
   block merge") or are dropped.

## Shared glossary (token → meaning to render)
| Token | Meaning |
|---|---|
| PASS | review passed; safe to proceed |
| PASS_WITH_NOTES | can proceed; N suggestions worth a look |
| NEEDS_REVISION | review failed; N issues to fix first |
| DONE / BLOCKED / NEEDS_CONTEXT | this task is done / stuck, needs your call on X / missing info X |
| 🔴 / 🟡 / 🟢 | must fix / worth fixing / FYI only |
| Wave N / fan-out | the Nth batch of tasks running in parallel |
| Axis N / Phase ① / Stage N | (never printed — say what this step checks instead) |

## Calibration pair (from dispatch-hygiene-notes.md — keep in sync)
✅ 「前三項做完也驗過了——解析器、新旗標、錯誤路徑。下一項需要你決定：
   標籤格式錯誤時，要只警告、還是直接讓建置失敗？」
❌ 「Wave 1 DONE: T1/T3/T4 PASS 3/3, reviewers green. T5 BLOCKED —
   NEEDS_CONTEXT on malformed-tag policy. 下一步？」