---
name: 4dx-meta-whirlwind-triage
description: |
  Activate when the user says "I'm always firefighting / no time for the important stuff / day job eats my whole week" and wants a strategic goal anyway. JP: 「日常業務に追われて目標に手がつかない」「忙しすぎて目標が進まない」. zh-TW: 「每天都在救火」「日常雜事吃掉所有時間」. D1 prerequisite: surfaces whirlwind/WIG split via 7-day time audit before WIG-defining. Do NOT fire for productivity-tool requests, burnout, or reactive roles where firefighting IS the work (oncall SRE, ER, infant-care).
source_book: The 4 Disciplines of Execution — McChesney, Covey, Huling, Thele, Walker
source_chapter: Chapter 1 — The Real Problem with Execution
source_language: en
tags: [execution, focus, capacity-model, prerequisite, time-audit, 4dx, discipline-1]
related_skills: []
---

# 4DX D1 — Whirlwind Triage (prerequisite to WIG-defining)

## R — Reading

> The real enemy of execution is your day job! We call it the *whirlwind*.
>
> — McChesney et al., *The 4 Disciplines of Execution*, Ch. 1 "The Whirlwind"

---

## I — Interpretation

Before you can set a meaningful strategic goal, you need to see — concretely, in hours — that your week is already full. The "whirlwind" is the cumulative urgent work required to keep your operation alive day-to-day. It is not bad. It is not wasted. It cannot be eliminated by working harder, getting up earlier, or being more disciplined. It will absorb roughly 80% of your capacity by structural design, and any gap you carve out by force-of-will will be devoured by Parkinson's Law within hours.

What this skill does: it makes you tag every block of your week as **whirlwind / WIG-work / waste**, compute the actual ratio, and identify which whirlwind tasks are *non-negotiable BAU* versus *whirlwind theater* (looking busy without keeping operations alive). The output is a time-allocation map plus a committed minimum percentage for WIG work — the book recommends ~20% for individuals.

The reframe is architectural, not motivational. You are not learning to "be more disciplined." You are learning to design within structural capacity. Folk productivity wisdom says "carve out time and protect it"; this skill warns you that gray instantly fills any gap unless you have a black-block ritual (D4 WIG Session) defending it. Without this triage, every downstream 4DX discipline misfires — you will pick a WIG that is actually your whole job (CE-04 next-skill territory) or commit to lead measures you have no spare hours to execute.

---

## A1 — Past Application

### Case 1: Plant Manager of the Year — twelve priorities into one (Ch. 2)

- **Problem**: A plant manager at a large US consumer-products company was assigned twelve "performance priorities" for the year — none of which were optional, all of which competed with the existing whirlwind of running the plant.
- **Methodology applied**: Even without 4DX vocabulary, he recognized that twelve simultaneous strategic goals was structurally impossible inside the existing whirlwind. He picked the *one* objective most likely to deliver a breakthrough and concentrated his team's discretionary capacity there. He kept the whirlwind running normally — twelve priorities did not become zero, they became one-actively-pursued plus eleven-still-acknowledged.
- **Conclusion**: Capacity above the whirlwind is small and singular. Honoring that constraint, not denying it, was the move.
- **Outcome**: Best results in the company that year; named Plant Manager of the Year — independent rediscovery of D1's narrowing rule, made possible only because the manager first respected the whirlwind's claim on ~80% of his hours.

### Case 2: Towne Park Miami — the concrete wall (Ch. 5)

- **Problem**: A 4-foot concrete wall in a parking garage forced valets to park cars back-to-back, killing retrieval-time performance. The team had complained about it for months but never acted — every shift was consumed by the whirlwind of valet operations (greet, park, retrieve, repeat).
- **Methodology applied**: Once retrieval time was named as the lead measure (lifting it above whirlwind noise), an assistant account manager made a self-chosen WIG-Session commitment outside whirlwind hours: confirmed the wall wasn't load-bearing, borrowed a concrete saw, recruited teammates, removed several tons of concrete on a Saturday.
- **Conclusion**: Capacity above the whirlwind exists, but it is *small and Saturday-shaped* — not stolen from Tuesday afternoon. The team did not work harder during the whirlwind; they protected a separate slice for breakthrough work.
- **Outcome**: Retrieval-time lead measure improved sharply; customer satisfaction lag rose. The wall would never have come down without first acknowledging the whirlwind claimed Monday-Friday and the WIG slice had to live somewhere else.

---

## A2 — Future Trigger ★

### When will the user need this skill?

1. The user says they want to start a new strategic goal (learn a language, ship a side project, lose weight, write a dissertation chapter, build a portfolio) but immediately follows with "but I have no time" — they are already conceding the capacity problem without diagnosing it.
2. The user has tried 4DX (or OKRs / GTD / similar) and watched a previous WIG die — and is wondering whether the methodology is broken or whether they just need to "try harder this time."
3. The user is a manager assigning a new initiative to a team and wonders why the team isn't moving on it — they have not modelled the team's whirlwind capacity and the new work has nowhere structural to land.
4. The user explicitly asks for a time audit, productivity diagnosis, or "where does my week go" analysis with the framing of *enabling a strategic goal*, not just curiosity.
5. The user is about to invoke `4dx-d1-wig-formulation` but has never made the whirlwind/WIG distinction explicit — this skill should run first.

### Language signals (user phrasings that should activate)

- "I'm always firefighting."
- "I want to do X but I never have time."
- "Every week the important stuff gets pushed."
- "My day job eats my whole week."
- 「日常業務に追われて目標に手がつかない」
- 「忙しすぎて自分の目標が進まない」
- 「いつも雑用ばかりで本当にやりたいことが進まない」
- 「每天都在救火」
- 「日常雜事吃掉所有時間」
- 「想推進的事一直擱置」
- 「想設目標但根本沒空執行」

### Non-activation signals (do NOT fire when…)

- The user wants a productivity system / app recommendation / GTD setup — that's task-management, not WIG-vs-whirlwind triage.
- The user describes burnout, exhaustion, depression, or sustained overwork — that is a coaching / managerial / clinical issue, not a 4DX prerequisite. Refer out, do not run a time audit.
- The user's role is *intrinsically reactive* — oncall SRE, ER triage nurse, customer-support queue, parent of an infant — where the whirlwind IS the strategic value. CE-26 boundary applies; do not manufacture a sub-WIG that competes with the actual work.
- The user is asking about a one-off project that fits inside the whirlwind ("I just need to file taxes this weekend") — not a behavioral-change strategy, doesn't need 4DX at all.

### Distinction from neighboring skills

- vs. `4dx-d1-wig-formulation`: that skill assumes the user already accepts whirlwind/WIG capacity reality and is ready to write a *From X to Y by When* WIG. This skill runs *before* it, surfacing the capacity reality so the WIG isn't aspirational fantasy.
- vs. `4dx-meta-strategy-triage`: that skill asks "should you use 4DX at all" (stroke-of-pen / whirlwind-handleable / behavioral-change). This skill assumes 4DX is the right tool and asks "do you have spare capacity to use it."
- vs. enterprise `4DX rollout time audits`: organizations doing 4DX deployment run capacity audits across departments to set Primary WIGs. That's a different skill (organizational cadence-setting, not yet built). This skill is individual-scale only.

---

## E — Execution

When this skill activates, the agent (your mentor) walks you through these steps. Each step is Socratic — I ask, you record.

1. **Set up a 7-day time audit log.**
   - You will track every 30-minute block of your waking time for the next 7 days. Phone notes, paper notebook, calendar app — pick one and commit. Tag each block with one of three labels: `WHIRLWIND` (necessary BAU — your job exists because of this), `WIG` (strategic / behavior-change work toward the goal you want to pursue), `NEITHER` (waste — scrolling, theater, sunk meetings nobody needed).
   - **Completion criterion**: 7 consecutive days logged with ≥80% of waking blocks tagged. Gaps OK; fabrication not OK.
   - **Halt condition**: if after 2 days you can't log honestly because the work is too volatile (genuine reactive role), jump to step 5.

2. **Compute the ratio.**
   - Sum the hours by tag. Compute three percentages: WHIRLWIND%, WIG%, NEITHER%.
   - Then ask yourself: *what did I expect? what did I find?* The gap between the two is the data.
   - **Completion criterion**: three numbers written down + a one-sentence reaction.

3. **Audit the whirlwind for theater.**
   - Look at every block tagged WHIRLWIND. For each recurring category (e.g. email triage, status meetings, coordinating sub-tasks, internal Slack, "checking in"), ask: *if I stopped doing this for 2 weeks, would the operation actually break? Or would only my image of being-on-top-of-things break?* Tag those blocks `BAU-real` vs `BAU-theater`.
   - **Completion criterion**: every WHIRLWIND block re-tagged into one of the two sub-categories. At least one BAU-theater item identified, or you justify in writing why every block is real.

4. **Decide your minimum WIG allocation going forward.**
   - The book's anchor for individuals is ~20%. For a 50-hour work week, that's 10 hours; for a 40-hour week, 8 hours. Decide a number you can defend against the whirlwind for at least 12 weeks. Write it as a **commitment**, not an aspiration: "I will protect N hours per week for WIG work, scheduled in these specific blocks: \[Tue 9-11, Thu 9-11, Sat 9-12]."
   - **Completion criterion**: a numeric N + concrete calendar blocks + a named protector (a recurring calendar event, an accountability partner, or a WIG Session ritual).

5. **Hand off (or terminate).**
   - If steps 1–4 completed: you now have a time-allocation map and a defended WIG slot. The next skill in the chain is `4dx-d1-wig-formulation` — invoke it to formulate the actual *From X to Y by When* goal that fits inside the slot you just protected.
   - If you halted at step 1 because your role is genuinely reactive: this skill says 4DX may not be the right tool for this objective. Flag CE-26 (whirlwind-as-the-strategic-work) and either re-scope the goal or accept the methodology mismatch.
   - **Completion criterion**: explicit handoff to `4dx-d1-wig-formulation` *or* explicit decision to drop 4DX for this objective.

---

## B — Boundary ★

### Do NOT use this skill in:

- **Burnout / overwork / mental-health territory.** Time audits weaponize awareness of overload without solving it. If the user is exhausted, despondent, or describes sustained overwhelm, this is a coaching/clinical issue. Run away from "just track your week and you'll see."
- **Genuinely reactive roles.** Oncall SRE rotations, ER staff, frontline customer support, parenting an infant, crisis-response — these are domains where the whirlwind *is* the strategic value. (CE-26.) The 80/20 capacity model is invalid here; trying to manufacture a 20% WIG slice degrades the actual job.
- **One-off / stroke-of-the-pen tasks.** Filing taxes, booking a flight, replacing a broken laptop. These don't need 4DX at all, let alone its prerequisite. Don't over-fire.
- **Productivity-system shopping.** If the user wants to compare Notion vs. Sunsama vs. Things, this is a tool-selection task. The whirlwind triage is a diagnostic about *capacity*, not a tool recommendation.

### Author-warned failure modes

- **CE-26 (Whirlwind-as-the-strategic-work)**: 4DX assumes day-job-vs-strategic-goal as the master conflict. When the day-job IS the strategic value, separating a WIG above the whirlwind makes no sense. Author treats this implicitly via the stroke-of-pen / whirlwind / behavioral-change triage but does not name reactive-domain mismatch directly — this is a Stage-0 critical-step gap.
- **Parkinson's-Law devouring**: F-15 (black-and-gray week) warns that simply removing a whirlwind block does not produce free time — gray fills it within hours. Carving out hours without a *protector ritual* (recurring block + WIG Session + named commitment partner) reliably fails. Most popularizations of "carve out time" omit this.
- **Most-important confusion**: Even after a clean time audit, users often pick a WIG that is the *most important* part of their job (e.g. "do client work better"). That is whirlwind optimization, not breakthrough work. The downstream `4dx-d1-wig-formulation` skill enforces P-04 (where-breakthrough-needed, not what-is-most-important); this skill should warn the user the trap is coming.

### Author's blind spots / period limitations

- **Co-located industrial framing.** Authors' canonical case is a 70K-hotel-leader Marriott deployment; the whirlwind metaphor was designed for shift-based, co-located, schedule-able work. Modern remote knowledge-workers may have whirlwinds shaped differently (async Slack thread tax, context-switch tax, meeting-density tax) that the 30-minute time-block log captures imperfectly. The book does not engage this — apply the skill with the granularity that fits your work, not religious 30-min blocks.
- **High-individualism culture assumption.** Author's "say no to good ideas" framing (P-05) and protected-WIG-slot ritual assume the user has authority to refuse new whirlwind injections. In high-context cultures (JP / ZH / KR) and junior roles, refusing a manager's new urgent task is socially costly. The skill identifies the capacity problem; it does not solve the political problem of defending the slot.
- **FranklinCovey selection bias.** All ~4,000 case studies are paid clients. The 80/20 split is presented as a natural law; it may instead be a survivor-bias artifact of clients who could install 4DX in the first place. Treat 80/20 as a useful default, not a measured constant.

### Easily-confused neighboring methodologies

- **Time-blocking / Sunsama / Cal Newport "deep work"** schedule strategic blocks but typically don't enforce the *behavioral-change vs. BAU* distinction — they treat all important work uniformly. This skill specifically gates whether the goal *requires behavioral change* (only then does WIG/whirlwind triage matter).
- **GTD weekly review** processes inbox + projects without distinguishing strategic-breakthrough work from BAU. A clean GTD weekly review can leave you 100% efficient at the wrong level.
- **OKR check-ins** assume the WIG (Objective) is already correctly scoped and capacity is already negotiated. This skill is upstream of OKR-style cadences.
- **Enterprise 4DX time-audit during organizational rollout** ("我們公司開始導入 4DX 要先做時間稽核") is a different skill — organizational cadence-setting and Primary-WIG selection across departments. Do not fire this individual-scale skill on enterprise rollout queries.

### Industry-experience addendum (queueing, constraints, attention residue)

The book treats the whirlwind as a rhetorical antagonist; operations literature
treats it as a diagnosable system with three named mechanisms — primary
citations in `references/industry-grounding.md`:

- **Reinertsen, *Principles of Product Development Flow* (Celeritas, 2009; ISBN 978-1935401001)** — queue length grows non-linearly above ~80% utilization; the 80/20 rule is a queueing-theory consequence, not a heuristic. Defend the protected slot or the queue collapses it.
- **Goldratt, *The Goal* (North River Press, 1984/1992; revised eds. through 2014)** — Theory of Constraints: felt overload is usually one removable bottleneck masquerading as generalized whirlwind. Identify and elevate it before assuming 4DX is needed.
- **Newport, *Deep Work* (Grand Central, 2016; ISBN 978-1455586691)** — attention-residue from context-switching degrades a "calendar-protected" slot into ~5–8% strategic output unless attention is also protected (phone out, notifications off, single-task).

The whirlwind triage should pair the book's 80/20 capacity check with these three diagnostics: utilization probe, constraint probe, attention-protection probe. Calendar-only protection produces theatrical work that fails the lag test in 4 weeks.

---

## Related skills

- `4dx-meta-strategy-triage` — depends-on — gates whether 4DX is the right tool at all
- `4dx-d1-wig-formulation` — composes-with — protected slot + capacity number feed WIG formulation

---

## Audit metadata

- **Verification status**: V1 ✓ / V2 ✓ / V3 ✓
- **Test pass rate**: pending (see `test-prompts.json` and `test-results.md` after Stage 3)
- **Distilled at**: 2026-04-29
- **Output language**: body — English (source-book language); frontmatter `description` — multilingual (EN + JA + zh-TW); metadata — English
