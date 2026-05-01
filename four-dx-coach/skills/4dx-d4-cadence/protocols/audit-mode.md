# Protocol: Audit-Mode — Diagnose a *running-but-malformed* WIG cadence from artifacts

> Loaded by SKILL.md orchestrator when the user provides existing
> artifacts (past WIG-Session minutes / weekly-meeting agendas /
> commitment logs / cadence pattern) and asks for a diagnosis — often
> with a stakeholder critique attached ("boss says meetings are
> pointless", "team feels the session is just a status report"). Agent
> voice = consultant-from-artifacts. Output = structured per-rule
> findings + revised agenda template + onward route.
>
> **Premise**: cadence is **currently running** (a session happens most
> weeks). If cadence has *collapsed* (multi-week skip), this protocol
> hands off to `4dx-sustain-momentum-rescue`. Audit-mode is for
> "running but malformed", not "stopped".

## R — Reading (verbatim source quotes)

> The standard agenda for the WIG Session has just three items: 1. Account: Report on commitments. 2. Review the scoreboard: Learn from successes and failures. 3. Plan: Clear the path and make new commitments.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 5

> The whirlwind is never allowed into a WIG Session.
>
> — *4DX* 2nd ed., Ch. 5

> Hold WIG Sessions to the same day at the same time in the same place every week (including electronically), regardless of the whirlwind.
>
> — *4DX* 2nd ed., Ch. 15

## I — Interpretation (mode-specific)

A "pointless" or "useless-feeling" weekly WIG meeting is almost never
*about* the time — it's about a malformation in the session's grammar.
Audit-mode reads the artifacts, runs a 4-rule diagnostic against the
canonical D4 standards, maps the user's (or stakeholder's) critique to
the rule the critique implicitly invokes, and prescribes a per-rule fix
with a revised agenda template.

The four diagnostic lenses (one per standard):

1. **Agenda grammar** (`account-review-plan-agenda.md`) — does each
   session have all 3 segments, in order, with Plan as centre of
   gravity? Common malformations: Account-only ("status report"),
   Account+Review-no-Plan ("we talked about it but no one committed"),
   Plan-without-Account ("commitments made but never accounted for"),
   Account-bloated (Account >50% of meeting time = report-out shape).
2. **Commitment shape** (`commitment-shape.md`) — for commitments
   captured in minutes: are they specific / lead-moving / own-control /
   self-chosen / capped at 1-2 per person? Common malformations:
   leader-dictated ("Alice, this week I want you to…"), vague ("work
   on the project"), boss-pleasing, dependency-laden, >2 per person.
3. **Whirlwind exclusion** (`whirlwind-exclusion.md`) — did sessions
   stay on the WIG + lead measures, or did operational discussion
   hijack? Common malformations: war-room-mode, status-on-everything,
   crisis-response-discussion, generic "what are you working on" round.
4. **Sacred cadence** (`sacred-cadence.md`) — same day, same time,
   same length, every week? Common malformations: drifting time,
   variable length (20 min one week, 75 min the next), occasional
   skips. **Hard threshold**: if >2 weeks skipped in last 8 weeks → flag
   *approaching rescue territory*; if multi-week consecutive skip →
   route to `4dx-sustain-momentum-rescue` and end audit.

**Critique-to-rule mapping** (the audit's interpretive move):

| Critique phrase | Most likely rule violated |
|---|---|
| "meetings are pointless" / 「会議意味ない」 / 「沒效果」 | No commitment captured → Plan-segment absent or Account-only |
| "feels like a status report" / 「ステータス会議」 | Account-bloated; Whirlwind invasion; Plan absent |
| "we never finish anything" | Commitment-shape: vague / un-specific / dependency-laden |
| "boss tells us what to do" / 「上司が決めている」 | Commitment-ownership: leader-dictated, not self-chosen |
| "we talk about everything except the goal" | Whirlwind exclusion failure |
| "the meeting keeps moving / running long" | Sacred cadence drift |

Voice contrast: agent is **consultant-from-artifacts**. Unlike coach-
mode protocols (Socratic, dialogue-driven, single-week scope), audit-
mode is **synthesis-from-evidence**, multi-week scope, output is a
written report with onward route — not a live coaching session.

## A1 — Past Application

### Case 1: Marriott — D4 cadence diagnosis at scale (Ch. 15 composite)
- 700+ properties. Many ran "weekly meetings" pre-4DX that the book
  characterizes as Account-only / status-update shape. Audit lens:
  segment-grammar fail (no Plan = no commitment-forward), whirlwind
  invasion (operational topics dominated), self-chosen-commitment
  absent (leader assigns tasks). Fix: install 3-segment grammar with
  Plan as centre of gravity, exclude whirlwind explicitly, shift
  commitment authority to members (veto-not-dictate).

### Case 2: CNRL field operations (Ch. 15 composite)
- Field-ops weekly meetings drowned in safety / equipment /
  scheduling whirlwind. Audit finding: whirlwind-exclusion violated;
  WIG-related discussion <20% of meeting time. Fix: hard-park
  whirlwind to a separate operational meeting; WIG Session
  whirlwind-free + capped 25 min.

### Case 3: Susan-Marcus dialogue (Ch. 10)
- West Team's WIG Session, week 4. Audit-shaped reading of the
  artifact: cadence sacred (running on time), agenda grammar present
  (Account-Review-Plan all three), but commitment-shape failed
  (Marcus's commitments un-specific, lead-measure-disconnected, and
  he himself ran teammates' urgent tasks over his own commitment —
  CE-23). Fix: redesign Marcus's commitment shape; protect his slot
  from teammate-rescue pattern. **Lesson for audit-mode**: a
  cadence that *runs* can still be malformed; running ≠ working.

## A2 — Future Trigger

When a user needs this protocol:

1. User provides past WIG-Session minutes / weekly meeting agendas /
   commitment logs and asks "what's wrong?"
2. User reports a stakeholder critique ("boss says these meetings are
   pointless", "team thinks weekly review is useless") and wants to
   diagnose before defending or changing the format.
3. User suspects their cadence is "going through the motions" but
   can't name what's missing.

EN: "Audit our weekly WIG meetings — here are the last 4 weeks of
notes", "Team says meetings are pointless, can you diagnose?", "Here
are 4 weeks of session notes — what's wrong?"
JP: 「うちの WIG Session 機能してない、診断して」「会議録を見て何がダメか教えて」「過去 4 週分の議事録を見て、agenda 設計が正しいか audit して」
zh-TW: 「我們的 weekly meeting 沒效果，幫看哪裡有問題」「老闆說週會浪費時間，幫我診斷」「過去四週的會議記錄，幫我看 4DX 角度哪裡走樣了」

## E — Execution

Output target: a written audit report with per-rule findings, a
revised agenda template, and an explicit onward route.

1. **Inventory what the user provided**
   - List artifacts: e.g. "4 weeks of meeting minutes, 1 commitment
     log, 1 stakeholder-critique line".
   - If user mentions artifacts but hasn't provided them, ask ONCE
     and stop — don't invent content.

2. **Read stakeholder/team critique if provided**
   - Capture the exact phrase ("pointless", "status report",
     「意味ない」). Hold it for the critique-to-rule mapping in step 7.

3. **Apply Account/Review/Plan grammar check**
   - For each session: which segments present? In what order? Time
     allocation (or proxy from minute-count / topic-headers)?
   - Label: `well-formed` / `Account-only` / `Account-bloated` /
     `Plan-absent` / `out-of-order`.

4. **Apply commitment-shape check**
   - Pull commitments from minutes/log. For each: specific?
     lead-moving? own-control? self-chosen (or leader-assigned)?
     ≤2 per person?
   - Flag any pattern (e.g. "5 of 8 commitments use the verb
     'work on' — vague-shape pattern").

5. **Apply whirlwind-exclusion check**
   - Topic-scan minutes: % of time on WIG + lead vs operational /
     status / crisis. If <60% on WIG, flag `whirlwind-invaded`.

6. **Apply sacred-cadence check**
   - Count last-8-weeks: skipped weeks, time drift, length variance.
   - **Decision gate**: if multi-week consecutive skip OR >2 skipped
     in last 8 weeks → STOP audit; route immediately to
     `4dx-sustain-momentum-rescue`. Audit-mode assumes cadence is
     *running*; collapsed cadence is rescue territory.

7. **Map critique to rule(s)**
   - Use the table from §I. Name the rule the critique implicitly
     invokes. ("'Pointless' typically maps to Plan-absent /
     commitment-not-captured. Let's check.")
   - If multiple rules violated, list in priority order (highest-
     leverage fix first — usually agenda-grammar before commitment-
     shape before whirlwind before cadence-drift).

8. **Recommend per-rule fix + revised agenda template**
   - For each violated rule, prescribe a concrete fix citing the
     standard's exact language ("install Plan segment as ≥40% of
     time per `account-review-plan-agenda.md`").
   - Output a **revised 25-minute agenda template** the team can
     adopt next session: 0:00-7:00 Account · 7:00-12:00 Review ·
     12:00-22:00 Plan · 22:00-25:00 close + recognition.

9. **Offer onward route** (end the audit)
   - "For a single missed-commitment debrief: run coach-mode
     `member-debrief`."
   - "For multi-week cadence collapse: route to
     `4dx-sustain-momentum-rescue`."
   - "For coach-mode dialogue rebuild of the session itself: run
     `team-leader-session` (if leader) or `solo-session` (if solo)."
   - "For cross-discipline audit (WIG / leads / scoreboard / cadence
     all at once): use `4dx-audit`."

## B — Boundary (mode-specific)

### Do NOT use this protocol for:

- **First-time cadence setup with no artifact** — there's nothing
  to audit yet → load `protocols/solo-session.md` or
  `protocols/team-leader-session.md` to *set up* the cadence.
- **Cross-layer audit** (WIG + leads + scoreboard + cadence
  diagnosed together) — use `4dx-audit`. Audit-mode here is **D4-
  layer-only**; it presumes WIG / leads / scoreboard are already
  in place.
- **Multi-week collapsed cadence** (>2 consecutive skipped weeks,
  team disengaged, "we haven't done this in a month") — route to
  `4dx-sustain-momentum-rescue`. Audit-mode assumes cadence is
  running but malformed; collapse is a different problem class.
- **Daily standup / sprint review / agile retro audit** — wrong
  cadence + wrong format; out of 4DX scope. Hand off via
  `using-four-dx-coach`.
- **Single missed-commitment debrief** — that's coach-mode
  `protocols/member-debrief.md`, not audit. Audit-mode is multi-
  week, pattern-level; member-debrief is single-week, single-person.
- **Leader 1:1 / performance review** — not a WIG-Session artifact.

### Author-warned failure modes (audit-specific)

- **Forced-fit diagnosis** — not every "pointless" complaint is a
  D4 problem. If artifacts show a sales pipeline meeting or QBR,
  say so: "this isn't a WIG Session — it's a [other] meeting; D4
  audit doesn't apply".
- **Recommendation overload** — limit to top 2-3 rule violations;
  one revised agenda template; one onward route. More than that
  collapses into noise.
- **Confusing running-but-malformed with collapsed** — if cadence
  collapsed, audit-mode is the wrong skill. Step 6 is the hard
  gate; respect it.
- **Over-trusting minutes** — meeting minutes are an optimistic
  artifact (people record what worked, not what derailed). Cross-
  check with the stakeholder critique; if the two disagree, the
  critique is usually closer to ground truth.

## Standards used

- `../standards/account-review-plan-agenda.md` — segment-grammar
  diagnostic in Step 3
- `../standards/commitment-shape.md` — commitment-quality diagnostic
  in Step 4
- `../standards/whirlwind-exclusion.md` — topic-scope diagnostic in
  Step 5
- `../standards/sacred-cadence.md` — cadence-consistency diagnostic
  in Step 6 (with the rescue-territory hard gate)

## References

See `../references/industry-grounding.md` — **Lencioni** (*Death by
Meeting* Weekly Tactical taxonomy validates the segment-grammar
diagnostic), **Reinertsen** (Cadence Principle F6 grounds the sacred-
cadence threshold), **Edmondson** (psychological-safety lens for
"feels pointless" critique that often masks discomfort with public
accountability rather than mechanism failure), and **Source 11:
Bravelab.io / Smenżyk** (real-world D4 failure verbatim anchors —
quote *"WIG Sessions required more than 30 minutes. Sometimes up to
1h"* for session-creep finding, and *"Everyone has to be prepared
before the WIG Session"* for member-prep failure finding; cite when
audit reveals 30-min ceiling violations or members arriving without
their measurements).
