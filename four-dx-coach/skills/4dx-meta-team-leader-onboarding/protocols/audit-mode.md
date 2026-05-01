# Protocol: Audit-Mode — Diagnose a *past* leader-onboarding attempt from artifacts

> Loaded by SKILL.md orchestrator when the user has already run an
> onboarding rollout and the team isn't bought in — and provides
> artifacts (rollout email, kickoff slides, leader 1:1 transcripts,
> team-feedback quotes) plus a critique ("team isn't bought in",
> "looks like another corporate initiative", "leaders are complying
> not committing"). Agent voice = consultant-from-artifacts.
> Output = per-rule findings + per-leader recovery plan + revised
> conversation for the highest-leverage missed leader + onward route.
>
> **Premise**: an onboarding *has happened*; the question is what
> failed. If no onboarding has happened yet (the user is preparing
> the conversation), this protocol hands off to `coach-mode.md`.
> Audit-mode is for "ran but malformed", not "haven't started".

## R — Reading (verbatim source quotes)

> "Had the leaders of leaders spent their energy trying to convince or
> control the resistant leaders of the frontline teams, they would have
> received begrudging compliance at best and open defiance at worst."
>
> — McChesney et al., *Chapter 8: Getting Your Leaders on Board*

> "The key to influence is first to be influenced."
>
> — McChesney et al., *Chapter 8* (understanding mindset)

> "You can veto, but not dictate."
>
> — McChesney et al., *Chapter 8* (involvement mindset, citing Chapter 2)

## I — Interpretation (mode-specific)

A "team isn't bought in" complaint after onboarding is almost never
*about* the team — it's about a malformation in the leader-of-leaders'
onboarding move. Audit-mode reads the artifacts, runs a 4-rule
diagnostic against the canonical Chapter-8 onboarding rules, maps the
critique to the rule it implicitly invokes, and prescribes a per-leader
recovery move with a revised conversation for the highest-leverage
missed case.

The four diagnostic lenses (one per onboarding rule):

1. **Commitment-vs-compliance check** — did the onboarding earn buy-in
   or impose? Anchor: Argyris double-loop learning (HBR 1991) +
   Ryan-Deci Self-Determination Theory (autonomy / competence /
   relatedness). Common malformation: rollout email frames 4DX as
   "we are doing this" rather than "here's the gap, here's the
   operating system that fits — does this land?"; kickoff slides
   sell 4DX rather than the team's outcome; no opt-out path offered.
2. **Kotter Stage-1 urgency check** — was urgency *established* or
   just *announced*? Kotter (*Leading Change*, 1996/2012, Stage 1)
   distinguishes the two. Common malformation: rollout copy lists
   business reasons but does not connect to the leader's own team's
   stalled outcome — urgency-by-fiat, not urgency-by-recognition.
3. **Per-leader steel-manning check** — did the user genuinely engage
   each leader's strongest objection, or strawman / dismiss them?
   Common malformation: 1:1 transcripts show the user countering
   weak objections ("we're too busy") while ignoring strong ones
   ("we already tried OKRs and it fizzled — what's different?");
   clarifying-question step (book Step 2) skipped entirely.
4. **Pilot-vs-hold-back check** — was the rollout staged or
   all-at-once? Common malformation: org-wide mandate on day 1
   (CE-36 — conscripting resisters), or every leader getting the
   same script (no per-leader differentiation).

**Critique-to-rule mapping** (the audit's interpretive move):

| Critique phrase | Most likely rule violated |
|---|---|
| "team isn't bought in" / 「チームが買ってない」 / 「團隊不買單」 | Commitment-vs-compliance — onboarding imposed, not invited |
| "looks like another corporate initiative" / 「また流行りの施策」 / 「又一個流行 KPI 工具」 | Kotter Stage-1 — urgency announced, not established |
| "leaders complying not committing" / 「表面的に従ってるだけ」 / 「表面配合心裡抗拒」 | Self-chosen-commitment absent — Team WIG dictated, not chosen |
| "leader X resented the meeting" | Per-leader steel-manning — strongest objection ignored or strawmanned |
| "we mandated it across all teams" / 「全社一斉」 / 「一次推全部」 | Pilot-vs-hold-back — all-at-once instead of voluntary pilot |
| "Step 2 / clarifying questions felt rushed" | CE-33 — clarifying questions skipped to save time |

Voice contrast: agent is **consultant-from-artifacts**. Unlike
coach-mode (Socratic, dialogue-driven, single-conversation prep),
audit-mode is **synthesis-from-evidence**, multi-leader scope, output
is a written report with onward route — not a live coaching session.

## A1 — Past Application

### Case 1: Imposed corporate rollout post-mortem (Marriott counterfactual)
- A division mandates 4DX on day 1 across all properties; rollout email
  emphasizes "this is critical" and "the only effective option" (CE-32 —
  advocacy disguised as transparency). Audit lens: commitment-vs-
  compliance fail (no opt-out), Kotter Stage-1 fail (urgency announced
  via memo, not surfaced from each property's stalled outcome),
  pilot-vs-hold-back fail (all-at-once). Recovery: pause mandate,
  identify 2-3 willing properties as voluntary pilots, re-open
  clarifying-questions round with the rest.

### Case 2: Skipped Step 2 (book CE-33 in onboarding)
- A leader presents draft Primary + Key Battle WIGs in a single
  meeting, jumps from "ensure understanding" straight to "give us your
  feedback", skipping clarifying questions. Audit lens: per-leader
  steel-manning fail (no space for the leader's strongest concern
  to surface); commitment-vs-compliance at risk (Argyris single-loop
  mode — feedback within unchanged frame). Recovery: schedule a
  separate clarifying-questions round, private 1:1 in high-context
  cultures.

### Case 3: Wrong-leader pilot (book CE-36)
- A leader-of-leaders adds a hard-no skeptic to the first pilot wave
  to "win them over". Pilot underperforms publicly; remaining leaders
  conclude 4DX doesn't work. Audit lens: pilot-vs-hold-back fail
  (resister conscripted into pilot). Recovery: pull the resister
  from the pilot, do not re-recruit them; let willing-pilot evidence
  accumulate first.

## A2 — Future Trigger

When a user needs this protocol:

1. User has already run an onboarding rollout (email / slides /
   kickoff meeting / 1:1s) and the team / leader-cohort isn't
   bought in — and provides artifacts asking "what went wrong?"
2. User reports a stakeholder critique ("team isn't bought in",
   "looks like another corporate initiative", "leaders complying
   not committing") and wants to diagnose before defending or
   re-launching.
3. User suspects the onboarding was "going through the motions"
   but can't name what's missing.

EN: "Audit our onboarding — team isn't bought in",
    "Leaders complying not committing — what went wrong?",
    "Here's the rollout email + 4 weeks of leader feedback — diagnose."
JP: 「チーム導入したが反発が強い、何が間違ってた？」
    「リーダー陣が表面的に従ってるだけ、何が抜けた？」
    「ロールアウトメールとリーダー 1:1 議事録、見て診断して」
zh-TW: 「導入了 4DX 但團隊不買單，幫我診斷」
       「下屬 leader 表面配合心裡抗拒，問題在哪？」
       「rollout 信件加上幾週的 leader 回饋，幫我看哪裡走樣」

## E — Execution

Output target: a written audit report with per-rule findings, a
per-leader recovery plan, a revised conversation for the highest-
leverage missed leader, and an explicit onward route.

1. **Inventory what the user provided.**
   - List artifacts: e.g. "rollout email, kickoff deck, 3 leader
     1:1 transcripts, 1 team-feedback summary, 1 stakeholder-critique
     line".
   - If the user mentions artifacts but hasn't provided them, ask
     ONCE and stop — don't invent content.

2. **Read stakeholder / team critique if provided.**
   - Capture the exact phrase ("team isn't bought in", "looks like
     another corporate initiative", 「表面配合」). Hold it for the
     critique-to-rule mapping in step 7.

3. **Apply commitment-vs-compliance check.**
   - Read rollout copy + kickoff framing. Did onboarding **invite**
     ("here's the gap, here's the operating system that fits — does
     this land?") or **impose** ("we are doing this")? Look for
     opt-out path, "Team WIG is yours" language, "I can veto but
     won't dictate" phrasing.
   - Cite the mechanism (Argyris double-loop / Ryan-Deci SDT
     autonomy) when flagging.
   - Label: `invited` / `imposed` / `mixed`.

4. **Apply Kotter Stage-1 urgency check.**
   - Read the urgency framing. Was urgency **established** (each
     leader's own team's stalled outcome named, recognized,
     felt) or just **announced** (memo lists business reasons,
     no per-team grounding)?
   - Label: `urgency-recognized` / `urgency-announced` / `urgency-absent`.

5. **Apply per-leader steel-manning check.**
   - Read 1:1 transcripts and feedback. For each named leader: was
     the strongest objection **engaged** in their own words, or
     **strawmanned** / dismissed / countered with a weaker
     version?
   - Flag any leader whose strongest objection went unanswered —
     they are likely the recovery-priority case.
   - Cross-check: was Step 2 (clarifying questions) run as a
     separate, unhurried round, or compressed into the same
     meeting as Step 3 (feedback)? CE-33 flag if compressed.

6. **Apply pilot-vs-hold-back check.**
   - Was the rollout staged (2-3 willing leaders first, others
     watching) or **all-at-once** (org-wide mandate day 1)?
   - If a hard-no leader was conscripted into the pilot wave
     "to win them over", flag CE-36.
   - Label: `voluntary-pilot` / `all-at-once` / `mixed-with-CE-36`.

7. **Map critique to rule(s).**
   - Use the table from §I. Name the rule the critique implicitly
     invokes. ("'Team isn't bought in' typically maps to
     commitment-vs-compliance — onboarding imposed rather than
     invited. Let's check.")
   - If multiple rules violated, list in priority order
     (highest-leverage fix first — usually commitment-vs-compliance
     before urgency-establishment before per-leader steel-manning
     before pilot-staging).

8. **Recommend per-leader recovery plan + revised conversation.**
   - Per-leader recovery table:
     ```
     LEADER       FAILURE-MODE              RECOVERY MOVE                              BUCKET
     [Name 1]     strongest obj ignored     re-open Step 2 1:1; let them speak first   re-engage
     [Name 2]     conscripted into pilot    pull from pilot wave; no re-recruit yet    hold-back
     [Name 3]     dictated Team WIG         hand Team WIG back; offer to redraft       reset-WIG
     ...
     ```
   - For the **highest-leverage missed leader**, write a revised
     conversation script (same 5-step shape as `coach-mode.md` Step
     6: acknowledge skepticism by name → frame as their problem →
     show involvement boundary → sell outcome not 4DX → offer
     voluntary opt-in). Cite which onboarding rule the original
     conversation violated and how the revision repairs it.

9. **Offer onward route** (end the audit).
   - "For a fresh onboarding plan from scratch (different leader,
     different cohort, or a re-launch after recovery): run
     `coach-mode`."
   - "For multi-week post-cascade cadence collapse: route to
     `4dx-sustain-momentum-rescue`."
   - "For cross-discipline audit (WIG / leads / scoreboard /
     cadence diagnosed together): use `4dx-audit`."
   - "For pre-fit-decision rethink (the onboarding failed because
     4DX didn't fit the org in the first place): route to
     `4dx-meta-strategy-triage`."

## B — Boundary (mode-specific)

### Do NOT use this protocol for:

- **First-time onboarding from scratch with no past attempt** —
  there's nothing to audit yet → load `coach-mode.md` to *prepare*
  the conversation.
- **Cross-layer audit** (WIG / leads / scoreboard / cadence
  diagnosed together) — use `4dx-audit`. This protocol is
  **onboarding-layer-only**.
- **General team conflict / interpersonal friction unrelated to
  4DX rollout** — out of scope; recommend a different help.
- **Multi-week cadence collapse post-onboarding** — that's
  `4dx-sustain-momentum-rescue` (cadence already broke); this
  protocol is upstream of that (the buy-in itself was malformed).
- **Frontline-team-member buy-in audit** — this protocol is
  leader-of-leaders → leaders-of-frontline-teams scope; member
  buy-in is the D1 Team-WIG-choosing process.
- **Pre-fit-decision rethink** — if the audit reveals 4DX didn't
  fit the org, route to `4dx-meta-strategy-triage`; this protocol
  doesn't run the fit triage itself.

### Author-warned failure modes (audit-specific)

- **Forced-fit diagnosis** — not every "team isn't bought in"
  complaint is an onboarding-rule failure. If artifacts show the
  WIG itself was wrong (not the onboarding), say so: "the
  Primary WIG is mis-scoped; onboarding can't repair an upstream
  fit problem".
- **Recommendation overload** — limit to top 2-3 rule violations,
  one revised conversation, one onward route. More than that
  collapses into noise.
- **Confusing imposed-but-running with collapsed** — if the
  cadence has stopped (multi-week skip), audit-mode here is the
  wrong skill (route to `4dx-sustain-momentum-rescue`); this
  protocol assumes onboarding *happened* and the problem is
  malformation, not collapse.
- **Over-trusting the leader-of-leaders' self-report** — rollout
  emails and kickoff slides are optimistic artifacts (people
  record what they intended to say, not what landed). Cross-check
  with team-feedback quotes; if the two disagree, the team
  feedback is usually closer to ground truth.

## Standards used

This protocol does not have a standalone `standards/` directory —
the rules it audits against are the same rules `coach-mode.md`
applies (commitment-vs-compliance, Kotter Stage-1, per-leader
steel-manning, pilot-vs-hold-back). Treat `coach-mode.md` §E and §B
as the canonical rule set; this protocol diagnoses violations of
those rules from past artifacts.

## References

See `../references/industry-grounding.md` — **Ryan & Deci** (SDT;
autonomy / competence / relatedness lens for commitment-vs-
compliance), **Argyris** (HBR 1991, double-loop learning lens for
clarifying-questions skip), plus secondary anchor: **Kotter**
(*Leading Change*, 1996/2012, Stage 1 — establish urgency)
implicitly invoked when the rollout email reads as "another
corporate initiative", and **Chesapeake Energy IT (anonymous, 2017)**
— frontline-voice failure anchor for mandatory-rollout-under-coercion.
Quote *"we are punished by having to act like 4DX is cool, when the
REST OF THE COMPANY does not have to do this silly program… we are
going to fake smile our way though this junk"* when audit reveals (a)
silo'd target department with peer exemption (Ch 8 voluntary-opt-in
violation), (b) frontline wrong-fit language ("won't work in our
function" — escalate to `4dx-meta-strategy-triage` CE-26 check), or
(c) verbatim "going through the motions" / 「形だけ」 / 「表面的に
従う」 compliance-theater signals.
