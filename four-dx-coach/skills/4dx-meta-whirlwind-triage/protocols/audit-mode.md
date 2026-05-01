# Protocol: audit-mode — Diagnose existing time log against 4DX whirlwind/WIG model

> Loaded by SKILL.md orchestrator when the user provides a time-log
> artifact (calendar export / past-week time tracker output / chat
> transcript of "I'm always firefighting" with attached schedule) AND
> asks for a diagnostic, optionally with a stakeholder critique
> ("boss says I'm wasting time", 「上司に時間の使い方ダメ出しされた」,
> 「老闆說我在亂忙」). Agent voice = **consultant**: per-block tag,
> per-rule verdict, evidence-cited, terse. Distinct from coach-mode,
> which runs Socratic dialogue from zero with no artifact.

## R — Reading (verbatim source quote)

> The whirlwind devours all the time and energy you have. Your strategy,
> on the other hand, demands time and energy that you don't have to
> spare. So your real challenge is to execute your most important
> goals in the midst of the whirlwind.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 1 "The Whirlwind"

## I — Interpretation (mode-specific)

The user has already produced a time-log artifact (calendar export, time
tracker dump, retrospective week summary) and wants the agent to
*diagnose against 4DX whirlwind/WIG capacity rules*, not Socratically
walk them through a fresh 7-day audit. Three things differ from
coach-mode:

1. **Posture is consultant, not coach.** Output is a per-block tag table
   (WHIRLWIND / WIG / NEITHER, then BAU-real / BAU-theater for
   whirlwind blocks), a computed ratio, a critique-to-rule mapping, and
   a recommended protected-slot redesign. Not Socratic dialogue.
2. **Single-skill scope.** Audit-mode here is whirlwind-triage-only —
   capacity model + ~20% WIG anchor + BAU-real vs theater. For
   downstream WIG/lead/scoreboard/cadence diagnostics, route to
   sibling skills (`4dx-d1-wig-formulation` audit-mode, `4dx-audit`
   full-stack).
3. **4DX-considering premise.** The user has a time log, so they are
   already willing to look. Audit-mode does NOT re-litigate "should
   you use 4DX at all" — but it WILL flag CE-26 (genuinely reactive
   role) if the artifact reveals every block is reactive whirlwind by
   design.

When a stakeholder critique is provided ("wasting time" / 「ダメ出し」/
「亂忙」), the consultant translates the everyday complaint into the
whirlwind/WIG rule the stakeholder is implicitly invoking. "Wasting
time on the wrong stuff" usually maps to either (a) **no protected WIG
slot** (~0% WIG visible in the log) or (b) **whirlwind theater
dominance** (high WHIRLWIND% but most of it is BAU-theater, not
BAU-real). Rarely it maps to NEITHER% being high — that's actual
waste, but stakeholders rarely see it as the primary issue when WIG
work is also missing.

Voice contrast vs coach-mode: coach-mode runs Steps 1-5 Socratically
over 7 days. Audit-mode runs the same five-step logic on a finished
artifact in one pass and returns a structured verdict card.

## A1 — Past Application

### Case 1: Plant Manager retrofitted as audit (Ch. 2 framing)

- The Plant Manager's "twelve performance priorities" memo was an
  artifact a consultant could have audited directly: spotted the
  one-WIG-per-individual rule was already broken (twelve = FAIL Rule
  1), and recommended demoting eleven priorities to monitored metrics
  before the manager even started running steps 2-4.
- Audit-mode equivalent: paste a calendar showing twelve initiative
  blocks + zero protected WIG block. Consultant verdict in one pass:
  "WIG% = 0; you have twelve simultaneous candidate WIGs and no
  defended slot for any. Recommend: pick one, demote eleven to
  monitored, protect 8 hr/wk for the picked one." That diagnosis
  should take 5 minutes from a clean log.

### Case 2: "Boss says I'm wasting time" rescue

- A mid-level operator brings a 1-week calendar export plus a
  paraphrased manager critique: "boss says I'm focused on the wrong
  things." Audit-mode steps:
  - Tag every block (WHIRLWIND / WIG / NEITHER).
  - Compute: 78% whirlwind, 4% WIG, 18% NEITHER.
  - Sub-tag whirlwind: 38% BAU-real (incident response, customer
    delivery), 40% BAU-theater (status meetings, internal Slack
    "checking in", reply-all email triage).
  - Map critique: stakeholder is not seeing strategic output. WIG% = 4
    explains it. Likely targets: collapse half the BAU-theater (40% →
    20%) and route the 20% recovered into a defended WIG slot.
  - Recommend: 8 hr/wk protected WIG slot (Tue 9-11, Thu 9-11, Sat
    9-12) + cancel two recurring status meetings + decline reply-all
    threads not addressed to user.
- Lesson: the critique was correct *and* the operator wasn't lazy —
  the schedule was structurally hostile to WIG work. Audit named the
  fix; coaching from zero would have taken 7 days.

## A2 — Future Trigger

When the user needs this protocol:

1. User pastes / attaches / references a time log, calendar export,
   time-tracker dump, or week summary AND asks for diagnostic /
   feedback / verdict.
2. User provides a time log plus a stakeholder critique ("boss says
   I'm wasting time", "manager flags I'm not focused", 「上司に時間の
   使い方ダメ出しされた」, 「老闆說我亂忙」) and wants the complaint
   translated to whirlwind/WIG rules.
3. User has historic time-tracker data (RescueTime / Toggl / Sunsama
   export) and wants a 4DX-rule diagnostic before deciding whether to
   start D1.
4. User has been running 4DX informally and wants to audit whether
   their current week actually shows ~20% WIG protection.

EN: "Audit my time log against 4DX", "Boss says I'm wasting time on
the wrong stuff — here's my calendar", "Diagnose my last 2 weeks of
calendar — am I in whirlwind theater?", "Check my time log: do I
actually have a protected WIG slot?"

JP: 「カレンダーを 4DX 視点で診断して」「上司に時間の使い方ダメ出しさ
れた、何が違う？」「直近 2 週間の予定表を見て whirlwind 比率を出して」
「protected WIG slot 実際にあるか確認して」

zh-TW: 「老闆看我時間紀錄說亂忙，幫我用 4DX 診斷」「我的 calendar 在
這，幫我看 whirlwind 比例」「過去兩週的時間表幫我審 4DX 角度看哪裡走樣」
「protected WIG slot 我實際上真的有嗎？」

## E — Execution

When this protocol activates, the agent runs a structured audit. **Do
not Socratically rebuild the week — diagnose, then recommend.**

1. **Read the time-log / calendar / chat-history artifact.**
   - Extract every distinct time block (or recurring meeting) verbatim.
     Note the granularity available (30-min blocks, hour blocks,
     full-day labels) — do not invent finer granularity than the
     artifact provides.
   - If the artifact spans <5 days, flag as "insufficient sample" and
     recommend either expanding the window or running coach-mode for a
     fresh 7-day audit.

2. **Read stakeholder critique (if provided).**
   - Note the verbatim complaint ("wasting time" / "not focused on the
     right stuff" / 「亂忙」 / 「ダメ出し」).
   - Hold it aside for step 6 — the per-block tagging runs first
     unbiased, then critique gets mapped after.

3. **Apply whirlwind / WIG / waste classification per block.**
   - Tag each block: `WHIRLWIND` (necessary BAU — the operation
     requires it), `WIG` (strategic / behavior-change work toward a
     stated goal), `NEITHER` (waste — scrolling, sunk meetings nobody
     needed, attention-residue gaps).
   - Compute three percentages: WHIRLWIND%, WIG%, NEITHER%.
   - If the user has not stated a strategic goal, mark WIG% = 0 by
     default and flag: "WIG% requires a stated goal — confirm or run
     `4dx-d1-wig-formulation` first."

4. **Apply the ~20% WIG protected-slot rule.**
   - Does the user have any block tagged WIG that is *recurring* and
     *protected* (not displaceable by whirlwind)? If WIG% < 15%: FAIL.
     If WIG blocks exist but are scattered / displaceable: PARTIAL.
     If WIG ≥ 15% with recurring defended blocks: PASS.
   - Cite the book's anchor: "individuals = ~20% (8 hr on a 40-hr
     week)" — this is the comparison baseline.

5. **Apply BAU-real vs whirlwind-theater distinction.**
   - For every block tagged WHIRLWIND, sub-tag: `BAU-real` (operation
     would visibly break in 2 weeks if stopped) vs `BAU-theater`
     (only the user's image of being-on-top-of-things would break).
   - Compute BAU-real% and BAU-theater% within the WHIRLWIND total.
   - If BAU-theater > 30% of total time: FAIL — this is the lever
     that frees up the WIG slot.

6. **Map stakeholder critique to rule.**
   - Translate the verbatim complaint to the rule it implicitly
     invokes:
     - "wasting time" / 「ダメ出し」/「亂忙」 → most often (a) WIG% ≈ 0
       (no protected slot) AND/OR (b) whirlwind-theater dominance.
     - "not focused on the right stuff" / 「優先順位がおかしい」/
       「重點抓錯」 → WIG% present but on a most-important-confusion
       target (whirlwind optimization disguised as breakthrough work).
     - "you're always reacting" / 「いつも対応」/「一直在救火」 → 100%
       whirlwind log; flag CE-26 if every block is reactive by role
       design (route to `4dx-meta-strategy-triage`).
   - Cite the rule explicitly in the audit output so the user can
     bring the diagnosis back to the stakeholder.

7. **Recommend protected-slot redesign + theater-reduction targets.**
   - Output a numeric N (target weekly WIG hours) + concrete calendar
     blocks ("Tue 9-11, Thu 9-11, Sat 9-12") + a named protector
     (recurring calendar event, accountability partner, WIG Session
     ritual).
   - Output a list of BAU-theater blocks recommended for collapse,
     with the freed hours routed to the protected WIG slot.
   - Flag any assumption you had to make (e.g. "I assumed the 'sync
     with manager' block is BAU-real — confirm" or "I inferred WIG =
     book-writing from your earlier message — confirm").

8. **Offer route.**
   - "If the protected-slot redesign above is enough, run it for 12
     weeks and re-audit."
   - "If you want a guided 7-day live audit instead of working from
     this static log, run coach-mode (sibling protocol)."
   - "If the audit reveals every block is reactive by role design
     (CE-26), 4DX may be the wrong tool — route to
     `4dx-meta-strategy-triage`."
   - "If the protected slot is in place and you're ready to define the
     WIG, route to `4dx-d1-wig-formulation`."
   - "If clinical burnout / chronic overwork is visible in the log
     (60+ hr/wk for sustained periods, no recovery time), route to
     professional support — this skill is not the right tool."

### Output format (audit card)

```markdown
# Whirlwind Triage Audit — [user name / scope]

## Artifact
> [time-log summary: window, granularity, source]

## Stakeholder critique (if provided)
> [verbatim complaint] → maps to **[rule]**

## Tag distribution
| Tag | Hours | % |
|---|---|---|
| WHIRLWIND | … | … |
| - BAU-real | … | … |
| - BAU-theater | … | … |
| WIG | … | … |
| NEITHER | … | … |

## Rule-check
| Rule | Verdict | Evidence |
|---|---|---|
| ~20% WIG protected slot | PASS / PARTIAL / FAIL | … |
| BAU-theater ≤ 30% | PASS / FAIL | … |
| WIG block recurring + defended | PASS / PARTIAL / FAIL | … |
| Not a CE-26 reactive role | PASS / FAIL | … |

## Recommended redesign
- **Protected WIG slot**: N hr/wk in [specific blocks], protector = [ritual]
- **BAU-theater to collapse**: [list]
- **Hours freed → routed to**: [WIG slot]

## Assumptions to confirm
- …

## Next steps
- …
```

## B — Boundary (mode-specific)

### Do NOT use this protocol for:

- **First-time triage without artifact** — no time log, no calendar
  export, just a vague "I'm always firefighting" complaint → coach-mode
  (sibling protocol). Audit-mode requires a concrete artifact to tag.
- **Cross-layer audit** — if the user provides WIG / lead measure /
  scoreboard / cadence context alongside the time log and wants a
  full-stack diagnostic → `4dx-audit`. This protocol is
  whirlwind-triage-only.
- **Strategy-fit questions** — "should I even use 4DX for this?" →
  `4dx-meta-strategy-triage`. Audit-mode assumes a time log exists, so
  the user is at least curious; but if the artifact reveals genuinely
  reactive role (CE-26), flag once and route out.
- **Clinical burnout / chronic overwork** — if the log shows 60+ hr/wk
  sustained, no recovery time, weekend bleed, or the user describes
  exhaustion / despondency / sleep collapse → professional support
  (coaching / clinical / managerial), not 4DX. Time-log audits
  weaponize awareness of overload without solving it.
- **Pure venting without artifact or critique** — "boss is
  unreasonable" with no calendar attached → not this skill.
- **Productivity-tool comparison** — "is RescueTime better than Toggl
  for this audit?" → tool-selection task, not capacity diagnosis.

### Author-warned failure modes

- **Verdict-without-evidence** — every PASS / FAIL must cite specific
  blocks from the artifact. "FAIL because WIG% is too low" is not
  evidence; "FAIL: 4% WIG over 5-day window vs ~20% anchor; only WIG
  block was Sat morning, displaced 2 of 5 weeks" is.
- **Inventing a stated goal** — if the user has not named a strategic
  goal, do not infer one to compute WIG%. Mark WIG% = 0 with the flag
  "requires stated goal" and route to `4dx-d1-wig-formulation`.
- **Theater-vs-real overreach** — the consultant cannot reliably tag
  BAU-real vs BAU-theater for unfamiliar blocks (e.g. "1:1 with
  manager"). Flag uncertain blocks under "Assumptions to confirm,"
  do not silently classify.
- **Coaching drift** — if the agent finds itself asking Socratically
  "what would you tag this block?", it has slipped into coach-mode.
  Stop, return to the verdict table.
- **CE-26 misfire** — if every block is reactive whirlwind by role
  design (oncall SRE rotation, ER shift, infant-care 24/7), do not
  recommend a 20% WIG slot. Flag CE-26 once and route to
  `4dx-meta-strategy-triage`.

### Easily-confused neighbours

- **Coach-mode (sibling)** — Socratic, 7-day live audit from zero,
  personal-coach voice; this protocol is consultant on existing
  artifact.
- **`4dx-d1-wig-formulation` audit-mode** — diagnoses an existing WIG
  draft against grammar / one-per-individual / Battles-win-the-war
  rules; this protocol diagnoses time *capacity* before the WIG.
- **`4dx-audit` (full-stack)** — covers all 5 layers (WIG / lead /
  scoreboard / cadence / substrate); this protocol is
  whirlwind-triage-only.
- **`4dx-meta-strategy-triage`** — gate for "is 4DX the right tool";
  audit-mode flags CE-26 and routes here, but does not re-run the
  fit-check by default.

## Standards used

- (No skill-internal standards file extracted yet; protocol relies on
  inline rules from coach-mode Steps 1-4 and the ~20% / BAU-real
  framing from Ch. 1.)

## References

See `../references/industry-grounding.md` for grounding. Most relevant
for audit-mode:

- **Reinertsen** (queueing theory) — supports the BAU-theater verdict:
  utilization above ~80% collapses queue stability; theater work
  inflates utilization without delivering throughput.
- **Goldratt** (Theory of Constraints) — supports the
  recommended-redesign step: identify the one removable bottleneck
  before assuming "I just need more discipline."
- **Newport** (*Deep Work*, attention residue) — supports the
  protector-ritual recommendation: a calendar-protected WIG slot
  without attention protection (phone out, notifications off,
  single-task) degrades to ~5–8% strategic output.
