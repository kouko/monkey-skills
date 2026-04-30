# Protocol: Member-Comprehend — Comprehend an inherited team WIG (V1 ⚠️ partial)

> Loaded by SKILL.md orchestrator when scope detection identifies a
> team member who has been handed a team WIG by their leader and needs
> to understand what it says, why it was chosen, what the lead measures
> are, and what their personal contribution slice is. Agent voice =
> **personal coach to the member**: private, supportive, sends the
> member to ask the leader where the answer can only come from above.
>
> **V1 ⚠️ partial** — the source book is leader-POV throughout; member-
> side coaching is the symmetric inverse of leader-side guidance. See
> Audit metadata in SKILL.md.

## R — Reading (verbatim source quotes)

> Everyone on the team must know the team WIG and how each person
> personally contributes. … Without line of sight from the team WIG
> to the individual's daily work, execution will fragment.
>
> — McChesney/Covey/Huling, *4DX* 2nd ed., Ch. 7 (paraphrased — line-of-sight principle)

> Each team member, every day, must be able to answer one question:
> *"What is the most important thing I can do today to advance my
> team's lead measure?"*
>
> — *4DX* 2nd ed., Ch. 12 (operating question for individuals on a 4DX team)

## I — Interpretation (mode-specific)

The book is written for leaders. But every leader-side instruction has
a mirror-image member-side responsibility. If the leader is told "make
sure every team member can state the WIG verbatim and name their own
contribution," then every team member is implicitly being told *"you
must be able to state it, and if you can't, that's a signal something
is broken."* This protocol coaches the member side of that mirror.

A member of a 4DX team needs four things in their head:

1. **The team WIG verbatim, in *From X to Y by When* form.** If they
   can't state it, they cannot align to it. Vague paraphrases ("we're
   trying to improve customer satisfaction") are not WIGs and signal
   the leader's communication failed somewhere.

2. **The strategic rationale — why this WIG.** Knowing *what* without
   *why* produces compliance, not commitment. The book's leader-side
   guidance (Ch 6) is to engage the team in selection; if that didn't
   happen, the member needs to ask after the fact.

3. **The team's lead measures.** The lag (WIG) tells you whether
   you've already won. The lead is what you act on this week. A member
   who knows only the WIG but not the lead measures defaults to
   whirlwind behavior.

4. **Their own personal slice.** The team WIG decomposes into
   individual contributions — different members move different lead-
   measure components. The member needs to identify *their* slice and
   translate it into a recurring "every day / week I will ___"
   commitment that bridges to D2 / D4.

Voice contrast vs sibling protocols: personal-define coaches a solo
individual choosing their own WIG; team-select coaches a leader
running 2x2 across a leadership team; this protocol coaches one member
who did not pick the WIG, gently surfacing what they know vs what they
need to ask the leader. Coaching is Socratic; the agent does NOT
invent answers. Where the member's own knowledge has gaps, the agent's
job is to send them back to their leader or peers with a precise
question. Some answers can only come from the leader who chose the WIG.

## A1 — Past Application

### Case 1: Younger Brothers Construction — frontline operators rallied to a single team WIG (Ch 6 / Ch 12, leader-side)
- Leader-side: a construction firm leader had to convert a corporate-level WIG into a frontline team WIG every crew member could act on.
- Member-side mirror: crew members needed to know precisely what the team WIG was, why it was chosen over other plausible site-level priorities, and what specific behavior on their own work moved it. Members who didn't get this context kept defaulting to the whirlwind.
- Once members could state the WIG verbatim and name their personal contribution, the daily question replaced the whirlwind as the operating frame. The team hit its WIG.
- Lesson: leader-side is "communicate down"; member-side mirror is "if it didn't get communicated to you, ask."

### Case 2: Hospital food-service team — line-of-sight as comprehension test (Ch 7)
- Leader-side: hospital food-service leader was told to confirm every team member could draw a direct line from the team WIG to their own daily task.
- Member-side mirror: each food-service worker had to answer "what is the team trying to win, and what does my work today have to do with that win?" Inability is *diagnostic*, not blameworthy. Fix is a conversation, not self-flagellation.
- Outcome: once the line-of-sight conversation happened, individual contribution became visible and trackable on the scoreboard.

### Case 3: The daily question as member operating frame (Ch 12)
- Without an operating frame, individual members default to whatever screams loudest in the whirlwind — emails, escalations, last-minute requests.
- Ch 12 prescribes a single question to be carried by every team member each morning: *"What is the most important thing I can do today to advance my team's lead measure?"* This is the member-level translation of D1 + D2.
- Outcome: members carrying this question report whirlwind tasks still get done, but strategic time gets carved out and protected — execution stops fragmenting.

## A2 — Future Trigger

When a member needs this protocol:

1. User joined a team that's already running 4DX and doesn't have the context the original team had when the WIG was set.
2. User's leader announced a team WIG but user can't recite it back in *From X to Y by When* form.
3. User knows the team WIG verbatim but not why it was chosen — complying without understanding.
4. User knows the WIG and rationale but doesn't know the lead measures.
5. User knows the WIG and lead measures at team level but doesn't know which slice is *theirs*.
6. User wants to install the daily question but can't fill in the blanks yet.

EN: "I joined a team running 4DX; how do I understand my role in their WIG?" / "My manager set a team WIG but I don't know what I'm supposed to do." / "What does my work have to do with the team's goal?"
JP: 「チームの WIG が降りてきたけど自分の役割が分からない」「上司が WIG を決めたが自分が何をすればいいか分からない」「チームの目標と自分の仕事のつながりが見えない」
zh-TW: 「主管定了 WIG 但我不知道我這個位置該怎麼接」「團隊有 WIG 但我不知道我該做什麼」「團隊目標跟我的工作有什麼關係」

## E — Execution

When this protocol activates, the agent runs a Socratic coaching dialogue. **Do not invent the team WIG or rationale for the user — extract what they actually know, surface what they don't, send them to ask.**

1. **State the team WIG verbatim.** — see `../standards/from-x-to-y-by-when-grammar.md`
   - Ask: "What is your team's WIG? Say it as precisely as you can — ideally in *From X to Y by When* form."
   - Completion: user produces a sentence with measurable starting state, target, deadline.
   - Halt: if user can only paraphrase ("I think it's about improving sales"), stop coaching and assign homework: *"Before we go further, ask your leader: 'Can you give me our team's WIG in From X to Y by When form?' Come back with the exact words."* Do not proceed.

2. **Surface the strategic rationale.**
   - Ask: "Why did your team pick this WIG? What was the alternative they declined?"
   - Completion: user articulates at least one reason and ideally one rejected alternative.
   - Halt: if user shrugs, assign homework: *"Ask your leader (or a longer-tenured peer): 'What made this the team WIG instead of [other plausible candidates]?' This is a fair question — don't apologize for it."*

3. **Surface the team's lead measures.**
   - Ask: "What are the team's lead measures — the weekly behaviors the team committed to that should drive the WIG?"
   - Completion: user names at least one lead measure that is both predictive of the WIG and influenceable by the team.
   - Halt: if user names the WIG itself or a vague "work harder" answer, assign homework: *"Ask your leader: 'What are our team's lead measures? What are we doing each week that should move the WIG?'"*

4. **Locate the personal slice.** — see `../standards/ladder-up-test.md`
   - Ask: "If the team WIG hits Y on the deadline, what specifically did *you* do that made it possible? What's the part of the lead measure that's yours?"
   - Completion: user names a recurring, repeatable behavior they personally control that contributes to a team lead measure.
   - Halt: if user can't locate the slice — two possibilities: (a) the leader hasn't decomposed the lead measures by role yet (homework: ask), or (b) the team WIG genuinely doesn't depend on this person's role (alignment question is bigger than this skill).

5. **Translate into a daily/weekly commitment.**
   - Ask: "Translate that slice into the form: *'Every [day / week] I will [verb + measurable count]'*. Make it small enough to keep for a quarter."
   - Completion: user produces a verbalized commitment in that exact form. Quality check: (a) numeric or binary-checkable, (b) doable inside actual workweek given whirlwind, (c) directly tied to the team lead measure named in step 3.

6. **Install the daily question.**
   - Ask: "Each morning, can you carry this question — *'What is the most important thing I can do today to advance my team's lead measure?'* — and let it shape your first 30 minutes?"
   - Completion: user agrees and names the trigger (calendar block / sticky note / morning ritual) where the question will live.

7. **Escalation check (if WIG is unclear or wrong-shaped).**
   - Ask: "After this conversation — does the team WIG itself look well-formed (X / Y / When all explicit and lag-measurable), or does it look broken (vague, missing date, or really a strategy-line dressed up as a WIG)?"
   - If well-formed but unclear to the member: comprehension homework (steps 1-3 above) closes the gap.
   - If wrong-shaped (no measurable Y, no deadline, "total revenue"-style trap): name the gap explicitly — "It looks like the WIG itself may have a Trap-2 or Trap-3 issue. That's a leader conversation, not a member-side fix. Frame it as a clarifying question, not a verdict: 'Help me understand how we'll know on [date] whether we hit it.'" The member does not redefine; they raise the clarifying question and let the leader decide whether to reshape.

8. **Output the comprehension card.**
   - Write back to the user, in their own words:
     - **Team WIG (verbatim)**: …
     - **Why this WIG**: …
     - **Team lead measures**: …
     - **My personal slice**: …
     - **Every [day/week] I will**: …
     - **My daily question**: *What is the most important thing I can do today to advance my team's lead measure?*
   - Completion: user confirms the card; if any field is "I need to ask my leader," the card is honest — that's the correct output. Do not paper over gaps.

## B — Boundary (mode-specific)

### Do NOT use this protocol for:
- **Solo / individual goals** — if the user is picking their own WIG with no team context, load `protocols/personal-define.md`.
- **Leader-side WIG selection** — if the user is the manager choosing the team WIG, load `protocols/team-select.md`. This protocol assumes the choice has already been made by someone else.
- **As a substitute for asking the leader directly** — some questions (why this WIG, what the lead measures are, role decomposition) can only be authoritatively answered by the leader. The protocol's job is to surface gaps and route the user to ask, not invent plausible answers.
- **When the team isn't actually running 4DX** — if the team has a "goal" but no scoreboard, no lead measures, no weekly cadence, this protocol misroutes. Flag the mismatch — the team has a goal, not a WIG.
- **As an end-run around a misaligned WIG** — disagreement is a different conversation (1:1 with leader). The protocol comprehends; it does not litigate the choice. Step 7 escalates surface-shape issues; deeper disagreement goes elsewhere.

### Author-warned failure modes (member-side mirror)
- **WIG-recall failure (member side of CE-12)**: Book's leader-side warning: "if any team member can't state the WIG, communication failed." Member-side mirror: if you can't state it, do not pretend you can. Go ask.
- **Compliance-without-commitment**: Member knows the words but not the strategic reason. Will execute mechanically until the first conflict with whirlwind, then drop the WIG. The "why" matters.
- **WIG-as-personal-task confusion**: Member treats the team WIG as their personal to-do. The team WIG is the team's *lag* measure; the member's work is on a *lead measure slice*, not on the WIG directly.
- **Whirlwind-eats-slice**: Member identifies the slice but doesn't carve calendar time. Daily question (step 6) is the antidote.
- **Inferred-rationale risk**: Because the book is leader-POV, member-side coaching is partially inferred. Be explicit with the user: "this is a derived practice — book doesn't give you a member-side script, so I'm coaching the symmetric inverse." Don't oversell certainty.

### Author's blind spots
- **Member voice underrepresented**: All cited cases are leader-side. Book assumes if leaders communicate well, members will follow. Real-world member experience often includes leaders who *don't* communicate well — this protocol exists for that gap.
- **Hierarchical assumption**: 4DX assumes leader-decides / team-executes. In flat / peer-driven / self-managing teams, the "ask your leader" homework may not have a clear addressee. Route to "ask the team" or to a collective decision moment.
- **Single-WIG team assumption**: In matrix orgs the user may be on multiple teams with multiple WIGs — this protocol handles one team at a time and does NOT arbitrate between conflicting team WIGs (meta-strategy / capacity conversation).

### Easily-confused neighbours
- **OKR cascading** — OKRs cascade Os and KRs through layers. 4DX is structurally different — team WIG is the team's lag measure; individual contribution is on the *lead* side, not on a smaller-O / smaller-KR.
- **Generic "alignment" coaching** — many leadership books say "align your team to the goal." 4DX is more specific: alignment means each person can state the WIG verbatim, name their lead-measure slice, and answer the daily question.
- **MBO (Management by Objectives)** — assigns individuals their own objectives that roll up. 4DX assigns the team a single WIG and decomposes contribution on the lead side.

## Standards used

- `../standards/from-x-to-y-by-when-grammar.md` — Step 1 verbatim recall + grammar test
- `../standards/ladder-up-test.md` — Step 4 personal-slice line-of-sight upward; Step 7 wrong-shape escalation
- `../standards/wig-discipline.md` — implicit (member knows the cap so they don't ask leader to add a 4th WIG)

## References

See `../references/industry-grounding.md` sections **Edmondson** (psychological safety reframes "I need to ask my leader to restate the WIG" as a learning behavior, not an admission of inattention), **Grant** (productive-dissent script — ask about evidence and rejected alternatives, maps to Step 2), **Meyer** (cross-cultural calibration of the "ask your leader" homework — softer route in high-power-distance / high-face-loss-cost contexts).
