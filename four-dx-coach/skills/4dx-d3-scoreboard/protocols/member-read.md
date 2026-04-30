# Protocol: Team-Member — Read an inherited team scoreboard (V1 ⚠️ partial)

> Loaded by SKILL.md orchestrator when scope detection identifies a team
> member reading a scoreboard their leader has already designed. Voice =
> personal coach to member. Verification status: V1 ⚠️ partial — the
> book is leader-POV; this protocol inverts the four design criteria into
> read criteria, and adds two member-only steps (locate-my-contribution,
> escalate-if-broken) absent from the source.

## R — Reading (verbatim source quote)

> If you can't tell within five seconds whether you're winning or losing, you haven't passed this test.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 4 (compelling players' scoreboard, criterion 4)

## I — Interpretation (mode-specific)

The book's scoreboard rubric is written for the leader designing the
artifact. The same four criteria — simple, visible, shows lead + lag
with where-you-should-be, 5-second winning test — read perfectly well
as a member's *diagnostic checklist* on a scoreboard they did not
build.

A member standing in front of an existing team scoreboard has a
narrower job than the leader: not "is this the right scoreboard?"
but **"can I extract signal from this scoreboard, this week, about
whether my work is lifting the lead my team chose?"** A focused
diagnostic, not a redesign exercise.

Five things have to be true at once for the read to work:

1. **The scoreboard passes the 5-second test for the member.** If
   the member glances and can't tell, the artifact is failing — the
   failure is the leader's to fix, not the member's to compensate
   for. Member's job: notice and surface.
2. **The member can locate their own contribution.** For each lead,
   where does daily work plug in? "I have no idea" = upstream-D2
   gap, not a scoreboard problem.
3. **The member can read the trend.** Status alone isn't a read;
   status-vs-pacing-line is. If the lead bar moved last week and
   not this week, why? Member traces it back to *their own* per-lead
   activity in the same window.
4. **The member spots calibration drift.** Scoreboards die slowly.
   A week-three pacing line set against week-one assumptions can
   quietly become wrong. The member, who works the lead daily, often
   sees the drift before the leader does.
5. **The member surfaces breakage.** If the scoreboard fails the
   5-second test for the *team* (not just the member), or pacing
   has clearly drifted, the member raises it — psychological-safety
   dependent. Step 6a gives a non-confrontational script.

This protocol is **not** "design my own scoreboard." It is "read the
one you already have, weekly, in under 5 minutes, before any
commitment-making." Small in scope by design — most use overlaps
with d4-member skills which consume this read.

Voice contrast: agent is **personal coach to member** — psych-safety
dependent; the read produces signal, the member chooses whether and
how to surface.

## A1 — Past Application

### Case 1: Younger Brothers — six observable safety leads, posted on-site
- Six safety-compliance behaviors displayed as a visible team
  scoreboard so any worker on any crew could see the running
  compliance rate per lead.
- Member-side read: a framer glancing at the board could tell within
  seconds whether the crew was winning on "scaffolding compliance"
  — and could trace yesterday's tick to a specific shift action ("I
  rebuilt that brace before lunch"). The board enabled the read; the
  read enabled the move.
- The 57 → 12 serious-incidents drop is leader-attributed in the
  book, but the daily mechanism — frontline workers checking the
  board, locating their own move, adjusting — is the symmetric
  member-side read this protocol codifies.

### Case 2: Towne Park valet — retrieval-time board
- Retrieval time was the lead, posted at the valet stand for all on
  shift.
- Member-side read: a valet glancing at the board mid-shift could
  ask "did my last retrieval add or subtract from the running
  average?" The self-question is only possible because the board
  passes the 5-second test *and* the valet knows where their own
  work plugs in.
- One valet's identification of the wall-bottleneck shortcut came
  from reading the board against their own lived shift, not from
  leader prompting.

### Case 3: Northrop Grumman — the blown-down stadium analogy
- Author's diagnostic image — fans go silent when the scoreboard
  blows down because no one can tell the score — applies
  symmetrically. A member on a team whose scoreboard has gone
  hidden, decorative, or stale is the silent fan.
- Member-side: when you can't read the score, the right move is not
  "guess harder." It is to surface back: "I came to read our
  scoreboard for prep and I couldn't tell if we're winning. Can we
  look at it together?"
- The member's inability to read is *signal about the scoreboard*,
  not a competence problem.

## A2 — Future Trigger

When a team member needs this protocol:

1. Member is on a 4DX team with a scoreboard already designed by the
   leader, and wants to know how to actually read it before a WIG
   Session, before writing a commitment, or as a weekly check-in.
2. Member looks at the team scoreboard and can't tell within 5
   seconds whether the team is winning — wants to know whether
   that's their own gap or a real scoreboard problem.
3. Member can read the scoreboard fine but doesn't know where their
   own work shows up on it — wants to locate personal contribution.
4. Member notices the pacing line / target line seems wrong relative
   to current reality (decorative, stale) and wants a structured way
   to confirm and surface.
5. Member is about to prep a D4 commitment but realizes they haven't
   read the scoreboard first.

EN: "How do I read my team's scoreboard?", "Where do I show up on
the team scoreboard?", "Our scoreboard hasn't moved in weeks — is
that real?"
JP: 「team の scoreboard をどう読む？」「scoreboard を見ても勝ってるのか分からない」
zh-TW: 「我們 team 的 scoreboard 怎麼看」「scoreboard 跟我有什麼關係不知道」

## E — Execution

Voice is **personal coach to member**. Run a brief Socratic read —
typically under 5 minutes for a known scoreboard. **Do not redesign
the scoreboard.** If the artifact is broken, surface and route, do
not patch.

1. **Comprehension gate — confirm the scoreboard exists.**
   - Ask: "Where is your team's scoreboard, and can you see it right
     now? Wall, screen, doc, app, channel-pinned?"
   - Completion: member names medium and confirms current visibility.
   - Halt: if team has *no* scoreboard, this is a leader-side gap.
     Output: "Your team is missing D3. Surface to your leader and
     route them to the team-lead-design protocol of this skill.
     Member-side reading is impossible without an artifact." Halt.

2. **5-second test (member-side).** — see `../standards/5-second-test.md`
   - Ask member to glance at the scoreboard *now* and answer in 5
     seconds: "Are we winning or losing on the team WIG?"
   - Completion: clear yes/no, OR explicit "I can't tell."
   - Branch: "I can't tell" → flag as **scoreboard-fails-5-second-
     test** and continue (failure is data; do not abort).

3. **Locate-my-contribution per lead.**
   - For each lead displayed, ask: "Where does *your* work plug
     into this lead? In one sentence."
   - Completion: a one-line answer per lead, or explicit "I don't
     know" per lead.
   - Halt: if member can't locate themselves on *any* lead, this is
     a D2 influence-mapping gap. Route to
     `4dx-d2-lead-measures` and stop.

4. **Trend read — week-over-week, per focus lead.** — see
   `../standards/lead-lag-pacing-elements.md`
   - For the member's 1-2 focus leads, read displayed trend: "Did
     this lead move last week vs the prior? Up, flat, or down? On
     or off the pacing line?"
   - Then: "What did *you* do on this lead in that window? Does
     your activity *plausibly* explain the movement?"
   - Completion: per focus lead, one-line trend statement plus
     one-line member-activity statement.

5. **Calibration check — has the scoreboard drifted?**
   - Ask: "Looking at the pacing line / target / where-we-should-be
     marker — does it still match current reality? Was it set weeks
     ago against assumptions that no longer hold?"
   - Completion: explicit yes (still calibrated) / no (drifted, with
     one-line why) / not sure.
   - If drifted or unsure: flag as **calibration-drift-suspected**.
     The member does not fix this — the leader does.

6. **Decide: reading complete, or escalate?**
   - If steps 2-5 produced clean answers: read complete; move to
     step 7.
   - If any flag fired (5-second-fails / calibration-drift / hidden
     / stale): move to step 6a.

   **6a. Escalation script (if a flag fired).**
   - Help member draft a short, non-confrontational ask. Template:
     > EN: "I came to read our scoreboard before [WIG Session /
     > prep]. I noticed [X — e.g., I can't tell from a glance whether
     > we're winning / pacing line looks stale relative to the
     > headcount change]. Can we look at it together for 10 minutes?
     > I'd rather flag it than guess."
     > JP: 「次の WIG Session の前に scoreboard を読みに来たんですが、
     > [X — 例: 一目で勝ってるか分からない / pacing line が現実と
     > 合ってない気がする] のに気づきました。10 分一緒に見てもらえます？
     > 推測するより flag したほうがいいと思って。」
     > zh-TW: 「我來讀 scoreboard 準備 [下次 WIG Session]，發現 [X —
     > 例：一眼看不出在贏 / pacing line 跟現況對不上]。可以一起看 10 分鐘
     > 嗎？我寧願先 flag 也不要用猜的。」
   - Completion: member confirms they will send the ask (timing:
     before next WIG Session is the default).
   - Note: this step depends on psychological safety. If member
     says "I can't surface this to my leader," capture as a signal
     in the output card — do not push.

7. **Output the read card.**
   - Write back, in member's own words:
     - **Scoreboard medium / location**: …
     - **5-second read**: winning / losing / can't tell
     - **My contribution per lead**: lead 1 → …, lead 2 → …
     - **Focus-lead trend** (last vs prior): up / flat / down; on /
       off pace
     - **My activity plausibly explains the trend?**: yes / no /
       unclear
     - **Calibration status**: intact / drifted / unsure
     - **Flags raised**: (5-sec-fails / calibration-drift / hidden /
       stale / none)
     - **Escalation drafted?**: yes / no / blocked-on-safety
   - Completion: member confirms the card.
   - Hand-off: "Carry this card into D4 commitment-prep (forward) or
     account-debrief (backward). The read is the input, not the
     output."

## B — Boundary (mode-specific)

### Do NOT use this protocol for:

- **Scoreboard *design* contexts** — solo → `protocols/personal-
  design.md`; leader-of-team → `protocols/team-lead-design.md`. This
  protocol only reads existing artifacts.
- **No-scoreboard contexts** — halt at step 1 and route to
  team-lead-design (via the leader). Do not invent a personal
  substitute.
- **Forward commitment-prep contexts** — route to
  `4dx-d4-cadence` (member-prep mode). Prep consumes a read; this
  produces it.
- **Backward debrief contexts** — route to `4dx-d4-cadence`
  (member-debrief mode).
- **D2 influence-mapping gap** — if member can't locate work on any
  lead, route to `4dx-d2-lead-measures` first.
- **BI / KPI dashboards / executive scorecards** — different
  purpose. The 5-second / locate-contribution / pacing-line frame
  doesn't apply.
- **As a substitute for talking to the leader** — fix is leader-
  side. Member reads and *surfaces*; doesn't redesign by stealth.

### Author-warned failure modes (member-side mirror)
- **Coach's-as-players' substitution (CE-08, member-side)** —
  multi-tab Notion / Tableau / 14-page Gantt sold as "scoreboard."
  Reading produces fatigue, not signal. Flag and surface.
- **Status-without-trajectory (CE-09, member-side)** — board shows
  state but no pacing line / target. Member sees a number but can't
  tell if it's winning. Flag and surface.
- **Hidden scoreboard** — lives in an app the team doesn't open
  daily. The member's "I can't see it without effort" is signal.
- **Decorative / stale scoreboard** — posted weeks ago, hasn't been
  updated. Surface as calibration-drift.
- **Scoreboard-as-trophy (vanity-metric drift)** — board curated for
  visitors, hides leads that aren't moving. Hard to surface without
  political cost — capture as private signal even if escalation is
  blocked.
- **Member-substitution failure** — member compensates for broken
  team board by reading their personal tracker instead. Personal
  tracker answers "am *I* winning?" not "is the *team* winning?"
- **Reading-as-procrastination** — member reads and re-reads instead
  of acting. Reading should take ≤5 minutes weekly.

### Author's blind spots / period limitations
- **Leader-POV authoring** — Ch. 4 + Ch. 14 codify scoreboard
  *design*, not *reading*. The four design criteria invert cleanly
  into read criteria, but the book never walks through a member
  doing the read. This protocol fills the gap by symmetric inversion;
  treat conclusions accordingly.
- **Co-located visible-board assumption** — distributed / remote
  members read through screens; "I keep forgetting to check" is
  partly a remote-context signal, not pure motivation.
- **Psychological-safety assumption** — step 6a presumes the member
  can raise a concern without political cost. In low-safety teams
  (Edmondson 2018) this fails; capture the read as a private signal
  and do not pressure surface.
- **High-context-culture caveat** — in JP / ZH / KR cultures,
  telling a leader their scoreboard is broken can read as face-loss.
  Step 6a's framing ("I'd rather flag it than guess") is calibrated
  to be Model-II / non-attributing (Argyris 1986); even so, surface
  via 1:1 rather than session-floor when possible.
- **No "stale calibration" protocol in book** — Ch. 4 covers initial
  design quality; Ch. 14 doesn't separately handle pacing-line
  drift over a 6-12 month WIG cycle. Step 5 is a member-side
  addition based on Tufte / Few dashboard-maintenance literature.

### Easily-confused neighbours
- **OKR check-ins** — confidence rolls (yellow / green / red); much
  coarser than 4DX scoreboard reading.
- **Generic "data review" / dashboard review** — BI dashboards
  optimize for analysis (drill-down, slicing). Scoreboard-reading
  optimizes for one question: "are we winning, and where do I plug
  in?" 5 minutes, not 30.
- **Project status reports** — answer "where is each task?";
  scoreboard reading answers "is the lead lifting the lag?"
- **Burn-down / burn-up charts (Scrum)** — track sprint scope, not
  lead-against-lag with a pacing line on a behavior-change WIG.

## Standards used

- `../standards/5-second-test.md` — Step 2 read criterion
- `../standards/lead-lag-pacing-elements.md` — Step 4 trend read;
  Step 5 calibration check
- `../standards/players-vs-coaches-board.md` — Step 2 flag if board
  is a coach's view in disguise

## References

See `../references/industry-grounding.md` sections **Tufte** /
**Few** (perception basis for "I can't read it" being artifact
failure not member competence), **Eurich 2017** (95/15 self-
awareness gap behind step 4's "plausibly" prompt), and
**Argyris 1986** (Model-II inquiry script in step 6a).
