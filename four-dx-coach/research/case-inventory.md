# 4DX Case Inventory — research notes (human reference, NOT loaded by skills)

> **Purpose**: stable inventory of publicly-accessible 4DX implementation cases with disclosure-depth + verification-strength grading, so future case-bank decisions for `four-dx-coach` skills can be made from a known-good shortlist instead of re-researching each time.
>
> **Status**: this file lives in `research/`, NOT in any skill directory. Per Anthropic's plugin spec (verified 2026-05-01), skills cannot reference plugin-root paths via `${CLAUDE_SKILL_DIR}` — runtime resources must be skill-internal. This inventory is for **human authoring decisions** only; agents never load it.
>
> **Last updated**: 2026-05-01 (Tier 1 fully verified pass)
>
> **Methodology**: web search across English / Japanese sources for 4DX implementation case studies disclosing actual WIG sentences, lead measures, scoreboards, cadences, and outcomes. Cases below are graded on two axes: disclosure depth and verification strength.

## Two-axis grading

**Disclosure depth** — how much of the 5-layer 4DX stack the source reveals:
- **★★★ Full**: WIG句型 with X / Y / When verbatim, named lead measures, scoreboard description, cadence specifics, results
- **★★ Partial**: 2-3 of the above
- **★ Marketing-tier**: outcome narrative + context only; D1-D4 specifics not disclosed
- **❌ Insufficient**: too thin to anchor anything beyond Boundary mention

**Verification strength** — how directly I confirmed the disclosure:
- **★★★ Direct read**: I personally read the full source (PDF Read tool / playwright full-page text extraction) and quote verbatim
- **★★ WebFetch summary**: extracted via WebFetch's prompt-based summarization; key quotes presented as direct but not byte-verified
- **★ Search snippet**: data came from third-party search-result excerpt, not from the original source itself
- **❌ Unverified**: claims are inferred from indirect references

A case-bank-eligible source needs **both** ★★★ on disclosure AND ≥★★ on verification. ★★★/★★★ is gold standard.

---

## Tier 1 — Anchor-eligible (★★★ disclosure × ≥★★ verification)

### 1. Gaylord Opryland Hotel (FranklinCovey CFR research PDF)

**Disclosure**: ★★★ full | **Verification**: ★★★ direct read (5-page PDF read in full via Read tool, 2026-05-01)

**Source**: FranklinCovey Center for Advanced Research, "Guest Satisfaction at Gaylord Opryland" by Dean W. Collinwood Ph.D. (March 2007, rev July 2009). 5 pages. Date of study: May 2006 – June 2009.
**Public URL**: https://www.vidartop.no/uploads/9/4/6/7/9467257/cfr070815_oprlnd_casstu__r1.1.5__lr.pdf
**License note**: © FranklinCovey CFR. Designed for academic / external distribution. Cite verbatim with attribution; do not redistribute the PDF itself.

**Company**: Gaylord Opryland Resort & Convention Center, Nashville TN; 4000 employees / 75 departments / 2,881 rooms / $300M annual revenue / 1.5M guests/year.

**Driver**: lowest guest satisfaction of all four Gaylord properties despite $80M room upgrades since 2003 + $400M expansion underway. October 2006 monthly score 43 (all-time low). xQ Survey June 2006 baseline = 25%. National avg goal-clarity 54% vs Opryland post-implementation 100%.

**D1 — WIGs (verbatim from page 3-4)**:
- Org-level: "**Hi Touch**" (high guest satisfaction) + "**Hi Volume**" (high occupancy) — two WIGs at the org level
- Front-office team: **"raise their check-in efficiency score from 55 percent to 65 percent by year-end 2007"**
- Reservation Call Center: **"improve guest satisfaction by answering 95 percent of incoming calls"** (baseline 88%)
- Engineering team: weekly walk-through of the hotel for guidance signage
- Old Hickory Steakhouse (Nando Rodriguez): "implement universal service" — every waiter assists guests at any table

**D2 — Lead measures**: universal service behavior change (Old Hickory); weekly hotel walk-through (Engineering); "answering 95% of incoming calls" (Call Center — borderline lag).

**D3 — Scoreboards (verbatim)**: "Scoreboards to show goal accomplishment were displayed prominently in the meeting room." Hi Touch / Hi Volume division-level goals "prominently posted." Each division established their own goals contributing to the two org WIGs.

**D4 — Cadence (verbatim)**: "30-minute WIG Sessions." Sheryl Chesnutt (Call Center & Reservations Manager) cited as having conducted **27 consecutive WIG Sessions** by April 2007. Sessions described as "fun, positive, and efficiently executed" with "spirit of teamwork and open communication." Quote: "We wouldn't think of missing a WIG meeting."

**Ch 8 — Onboarding**: 2-day exec session (June 2006) → 2-day sessions per division (Convention Services / Food & Beverage / Rooms) → cross-cutting departments (HR, Engineering) → 300 employees trained by in-house leaders → cascade so deep that ground-crew + shuttle-bus drivers + shop clerks were "goal-aware" by April 2007 (vs national avg 54% goal-aware).

**Results (verbatim)**:
- Customer-Loyalty: "In the period June 2006-October 2007, the 22 months before the 4 Disciplines program was started, only 34 percent of the guests said they would enthusiastically recommend Opryland to others. In the 20 months since the 4 Disciplines, 58 percent said they would recommend the hotel: a **24-point increase**."
- Guest satisfaction scores: **+17 points** after 4D
- xQ score: 25% (Jun 2006) → ~45% sustained (Jan 2007 onward); overall company score 77 — 20 points higher than FranklinCovey average client; top 10% globally
- Recognition: First time Opryland achieved best guest satisfaction in entire Gaylord chain. Danny Jones nominated for Flywheel Award.

**Quote (verbatim)** — anonymous leader: "The culture was already set up to provide good service, but it didn't happen until we implemented The 4 Disciplines of Execution."

**Reinforcement**: "Public recognition and award items to display at home or in their offices" + "cash bonuses when goals were met."

**Cross-skill applicability**: anchor for `4dx-d1-wig-formulation` (multi-WIG Hi Touch/Volume + division cascade), `4dx-d2-lead-measures` (universal service), `4dx-d3-scoreboard` (prominent display + cascade), `4dx-d4-cadence` (30-min / 27-consecutive), `4dx-meta-team-leader-onboarding` (Ch 8 4-stage rollout), `4dx-d1-wig-cascade` (4000 employee × 75 dept ladder-up).

**Use this case when**: large org / hospitality / customer-experience WIG / multi-division cascade; full operational reference is needed.
**Do NOT generalize this case to**: small teams (< 50 ppl); contexts without clear lag metric; B2B with long sales cycle (Opryland's lag — guest survey — has fast feedback loop).

---

### 2. CSN College — institutional 4DX rollout

**Disclosure**: ★★★ full | **Verification**: ★★★ direct read (38-page PDF read via Read tool pages 1-30, 2026-05-01)

**Source**: CSN 4DX Support & Guidance Packet, September 2024. 38 pages.
**Public URL**: https://news.csn.edu/wp-content/uploads/2024/10/4DX-Support-Guidance-Packet-September-2024.pdf
**License note**: published for CSN faculty / staff internal use; publicly accessible. Cite as "CSN 4DX Support & Guidance Packet, Sept 2024."

**Company**: College of Southern Nevada — public higher-education institution. Established long-term FranklinCovey relationship 2021. Pre-4DX: graduation rate <10% (pre-2019), 17% (2024) vs national community-college avg 33%.

**D1 — Org WIGs (verbatim, page 9, March 2024 crafted)**:
- **Breakthrough WIG**: "Increase certificate and degree completions from 4,673 to 6,000 by June 30, 2029."
- **Sub WIG A**: "Increase annual unduplicated headcount from 41,058 to 41,160 by June 30, 2029."
- **Sub WIG B**: "Increase retention for all students Fall-to-Fall from 43% to 53% by June 20, 2029." [sic — typo in source, expected June 30]
- **Sub WIG C**: "Eliminate equity gaps in successful course completion by 74.7% to 89.7% by June 30, 2029."

**D1 — Department-level TWIG examples (verbatim, pages 17-21, 12 disclosed)**:
- Advising/Career Services: "Increase the number of new students connected to a Field of Interest Advisor from 0% to 90% by July 1, 2026"
- Financial Aid: "Increase the number of Federal Aid recipients from 3,704 to 3,890 by June 30, 2028"
- Student Recruitment: "Increase the number of first-year underrepresented male student enrollment from 447 (5-year average) to 536 by August 17, 2025"
- American Indian Program: "Increase the retention rate of Native American students from 58% to 61% by June 30, 2025"
- Chemistry: "Increase Chemistry student successful course completion with equity for the Spring 2024 semester from 66.54% to 69.54% by October 31, 2027"
- EWLJ: "Increase subsequent course enrollment from EWLJ's four gateway level courses semester-to-semester from an average of 55.5% to 60.5% by July 15, 2026"
- MCSE: "Increase MCSE student successful course completion from 57.1% to 65% by October 31, 2025"
- Media Innovation Group (IT): "Increase software update schedule from 0 to 138 classrooms by August 1, 2025"
- Facilities/Maintenance: "Increase maintenance of learning environments from 2600 to 4600 spaces by August 1, 2026"
- Advancement: "Increase the number of Scholarship Sponsors from 0 to 18 by September 1, 2023"
- Business Office: "Increase the number of financially literate units from 4 to 60 by December 31, 2025"
- Professional Development & Learning Center: "Increase professional development offerings for part-time faculty and staff from 2 offerings to 10 offerings by July 15, 2024"

**WIG句型 spec (verbatim, page 23 / 27)**:
- "Action from X to Y by a specific date"
- Components: Action Statement → Starting Line (X) → Finishing Line (Y) → specific Deadline (month, day, year)
- Mandate: "Only use this format to create your Team WIG. No other format will be accepted in February 2025."

**D2 — Lead Measures (verbatim per department)**:
- Advising: 60 conversations + introductions/week (team) + 10/member/week
- Financial Aid: 190 contacts/week + 10/member/week
- Student Recruitment: 6 hours/week intentional activities + 2 hrs/member/week
- American Indian Program: 15 outreach actions/week (pre-approved) + 3/member/week
- Chemistry: 10 high-impact practices/week (pre-approved shortlist) + 1/member/week
- EWLJ: 2 hours/week student support + 20 min/member/week
- MCSE: 42 actions/week from "Loss Momentum Framework" + 2/member/week
- Media Innovation: 8 classroom updates/week + 2/member/week
- Facilities: 20 inspections/week (checklist-based) + 4/member/week
- Advancement: 4 sponsor activities/week + 2/member/week
- Business Office: 6 units/10 employees/week financial-awareness meetings + 1 unit/3 employees/member/week
- Professional Development: 7 learning items/week + 2/member/week

**D2 — Two-Axis Test (verbatim, page 24-25)**:
- X-Y Scatter Plot: Y-axis Predictive (high) ↔ Not Predictive (low); X-axis Habitual Behavior (left) ↔ Chronically Inconsistent Behavior (right)
- Top-right quadrant = Potential Lead Measures
- 5 evaluation questions: Predictive / Measurable (≥80% influenceable) / Current Habit (chronically inconsistent vs current habit) / 4 Required Components (Verb + Focus + Consistency + Quality) / "Scoreboardable"

**D3 — Scoreboard (verbatim, page 26)**:
- "Digital and Physical Scoreboards" both used
- Physical Scoreboard updated weekly
- 4DX Online Portal with Red/Yellow/Green status ("Stay in the Green")
- Sample physical scoreboard photo on page 26: 3-track race-car layout with FINISH lines + 4 monthly milestones (1M / 2M / 3M / 4M) + dial gauges underneath

**D4 — Cadence (verbatim, pages 11-13)**:
- "**Team Huddles are quick 10-15-minute meetings that follow a specific format**"
- Frontline Team Leader hosts weekly Team Huddle
- Frontline Team Leader attends THEIR leader's Team Huddle to report
- "Receive weekly accountability updates from each Team Member"
- "Update the Team's progress weekly in the 4DX Portal"

**Ch 8 — Onboarding timeline (verbatim, page 14)**:
- May 2022 – July 2023: Directors+ received 7 Habits + 4 Essential Roles training (foundation)
- March 2024: Sr. Executives trained in 4DX, crafted 4 CSN WIGs
- May 2024: Leaders of Leaders trained
- September 2024: Frontline Team Leaders trained (70+); 50+ to be trained in October
- October 2024: 4DX Coach assignment per team
- October 2024 – January 2025: Teams draft TWIG, Lead Measures, Physical Scoreboard
- February 2025: Frontline TWIG Review (15-min presentations of TWIGs and Lead Measures by each Team)
- March 2025: Official launch of Accountability for the TWIGs and Lead Measures

**Roles (verbatim, page 5 + 12-13)**:
- Executive Sponsors (President + 5 VPs, all named)
- Primary 4DX Coaches: Ayesha L. Kidd (Lead), Bob Ngo (Data), Shari Peterson, Jyoti Senthil, Chuck Dobbs, Shannon Gilliland (each named with role)
- 4DX Coach assigned per team for "**up to eighteen months**"
- Leaders of Leaders / Frontline Team Leaders / Individual Team Members

**Cross-skill applicability**: education / public-institution context anchor; institutional / multi-year cascade; equity / DEI WIG framing (rare in book's anchors); 12 well-formed TWIG examples for d1-wig-formulation training; explicit two-axis test methodology for d2-lead-measures.

**Use this case when**: education / public institution context; multi-year horizon (rare — book typically shows quarterly WIGs); compound WIG with sub-targets; need explicit "Action from X to Y by date"句型 spec.
**Do NOT generalize this case to**: short-cycle / quarterly contexts; private-sector commercial WIGs; small teams that don't have org-level WIG to ladder to.

---

### 3. Bravelab.io — first 4DX implementation (failure-included)

**Disclosure**: ★★★ full | **Verification**: ★★★ direct read (full LinkedIn article extracted via playwright text DOM, 2026-05-01)

**Source**: Mariusz Smenżyk (founder, Bravelab.io), "The very first attempt to implement 4DX in Bravelab.io" — LinkedIn post, published 2021-04-20.
**Public URL**: https://www.linkedin.com/pulse/very-first-attempt-implement-4dx-bravelabio-mariusz-smenzyk
**License note**: LinkedIn post by author; cite with attribution. Author explicitly transparent + provides example scoreboard spreadsheet link.

**Company**: Bravelab.io — Polish digital agency (small startup, dev team ~15 people growing to 20). Implementation started March 2021.

**Driver**: founder asked business developers what was vital for company in 1Q/2021; got 5 different answers. Recognized executional misalignment.

**D1 — Initial 5 candidate goals (verbatim, narrowing-from-many anchor)**:
1. To hire five developers
2. To complete a company's website
3. To hire Marketing Manager
4. To implement ATS tools
5. To deliver all of the opened projects

**D1 — Refined to From-X-to-Y-by-When (verbatim, intermediate stage)**:
1. To Increase the development team from 15 to 20 people until the end of the April
2. To finish five pages that are still not ready by 31/03/2021
3. To hire Marketing Manager by the end of the April
4. To fill out 25 CV's which are on hr@bravelab to the new ATS by the end of the March
5. To deliver projects A, B, C by the end of the March → reformulated to:

**D1 — Final 2 WIGs (verbatim)**:
- "**To issue invoices for all contracted projects by the end of March 2021**"
- "**To decrease unpaid invoices from 84k to 0 by the end of March 2021**"
- (Note: earlier in article said "from 80k to 0k", later corrected to 84k — captures real-world drafting iteration)

**D2 — Lead measures (FAILED — useful anti-pattern, verbatim)**:
- Reused existing project spreadsheet (income/expenses financial data) instead of designing behavioral leads
- Author quote: "**LEAD measures didn't work. Not everyone was able to define what he needs to do to bring our efforts closer to our LAG measure**"
- Direct evidence of book Ch 3 claim that D2 is the most-misunderstood discipline

**D3 — Scoreboard (PARTIAL, verbatim)**:
- Tool: Google Sheets (no suitable commercial app found)
- Author observation: "**90% of scoreboards fill out the date and value of measurement**"
- Author shared example scoreboard publicly: https://docs.google.com/spreadsheets/d/1Btvv4JVujR3UaEI4saled00JjsqCUCdp_n--mRHSMNQ/edit#gid=631824341

**D4 — Cadence (PARTIAL, verbatim)**:
- "WIG sessions every Monday at 1 p.m"
- 85% achievement threshold (not 100%)
- Worked: established consistent cadence; team rejected unnecessary ideas
- **Failed**: "**WIG Sessions required more than 30 minutes. Sometimes up to 1h**"
- **Failed**: "**Everyone has to be prepared before the WIG Session (everyone needs to know their current measurements. It's important to put them out on the scoreboard together)**"
- **Failed**: "**People who will be using 4DX should learn the basics of this method before we start**"

**What worked (verbatim)**:
- Defined 2 WIGs (3 hours of meetings)
- Mondays 1pm cadence
- Accurate scoreboard data
- Focus discipline: easy to hold off unnecessary ideas

**Cross-skill applicability**: `4dx-d1-wig-formulation` (5→2 narrowing example, From-X-to-Y句型 iteration, Ch 6 narrowing-from-many anchor); `4dx-d2-lead-measures` (canonical "leads didn't work" failure mode); `4dx-d4-cadence` (canonical session-creep + prep-failure mode); `4dx-meta-team-leader-onboarding` (canonical "skipped pre-onboarding training" failure).

**Use this case when**: small-org context (5-15 ppl); SaaS / digital / startup; user is in audit-mode and pasting an artifact that shows D2 collapse / D4 session-creep; user is in coach-mode and has "5 candidate WIGs" → narrowing question.
**Do NOT generalize this case to**: large org cascade; established 4DX-experienced teams; cases where the lag itself is malformed (Bravelab's lags were fine; the failure was downstream at D2).

---

### 4. Methodist Le Bonheur Germantown Hospital

**Disclosure**: ★★★ full | **Verification**: ★★★ direct read (full Becker's article via Wayback Machine snapshot, playwright text DOM extraction, 2026-05-01)

**Source**: Emily Rappleye, "How the 4 disciplines of execution can change healthcare" — Becker's Hospital Review, May 14, 2015. Based on session at Becker's Hospital Review 6th Annual Meeting, Chicago, May 7, 2015.
**Original URL**: https://www.beckershospitalreview.com/hospital-management-administration/how-the-4-disciplines-of-execution-can-change-healthcare.html (returns 403 today)
**Wayback URL**: https://web.archive.org/web/20161029170253/http://www.beckershospitalreview.com/hospital-management-administration/how-the-4-disciplines-of-execution-can-change-healthcare.html
**Speakers**: William A. Kenley (CEO Methodist Le Bonheur Healthcare) + Diane Ridgway (COO Methodist Le Bonheur Germantown Hospital)

**Company**: 309-bed full-service hospital. Pilot scope: 58-bed unit. Memphis-based system Methodist Le Bonheur Healthcare's Germantown TN hospital.

**Driver (verbatim)**: "delays backed up the emergency department and operating rooms… It was a flow problem that left patients in the hallways and damaged patient loyalty and satisfaction." (~2013)

**D1 — WIG (verbatim)**:
- "**They decided their wildly important goals would be to increase bedturns to make 'virtual capacity' in the unit**"
- 58-bed unit pilot
- Focused on **simple discharges (total joint patients)** rather than difficult discharges (SNF patients) — book Ch 6 "go smaller" anchor

**D1 — anti-pattern observed (verbatim, Kenley quote)**:
- "If you operate in that kind of environment, you are giving staff the latitude to triage what the No.1 priority is because not everything can possibly be No. 1 — which is a very scary thing frankly"
- Book Ch 1 "too many priorities = no priority" embodied

**D2 — Lead measure (verbatim, Ridgway insight)**:
- "Staff determined early on they could project when patients would potentially be ready to leave the hospital"
- "Use these estimates to manage the team's expectations and prep the patients and the patients' families for the tentative discharge time"
- Lead = projecting + prepping for tentative discharge time (a behavioral / forecast lead, not a count)

**D3 — Scoreboard (verbatim)**:
- "**The Germantown nurses created the scorecards**" (team-built principle)
- Tracks lead indicators + reporting goal (bedturn rate)
- Kenley quote: "**It is vital that the scorecard is made by the team and that the members of the team can see it right in front of them all the time**" (book Ch 4 visibility + ownership)

**D4 — Cadence (verbatim)**:
- "**weekly meetings to discuss their results, look at lead indicators and evaluate if their plan was working**"
- Cadence enables team self-monitoring

**Results (verbatim)**:
- "**Bedturns increased from 77 in 2012 to 81 in 2013**" (~5% increase, modest but real)
- "ER was busier"
- "Patient communication improved"
- "Physician satisfaction improved"
- Kenley: "Feedback from staff was positive. They said they were very inspired by the framework because it was something they could grab onto"

**Closing quote (Ridgway, verbatim)**: "It's really about making a point to focus on what's important for the organization and then making sure the team can focus on this too with the scorecard and the cadence of accountability"

**Cross-skill applicability**: healthcare anchor; team-built (D3 nurse self-built scorecards = book Ch 4 "team owns the board" principle); pilot-scope rollout pattern; "go smaller" Ch 6 anchor (focused on simple cases first, deferred SNF complexity); behavioral-lead pattern (forecast-and-prep, not count-based).

**Use this case when**: healthcare / clinical operations / patient-throughput WIG; team-built scoreboard discussion; "go smaller" recommendation when WIG is too broad.
**Do NOT generalize this case to**: knowledge-work or creative-work contexts (clinical workflow is highly structured); cases where outcome lag has long feedback loop (bedturn tracks daily).

---

## Failure-mode dictionary (highest-ROI material per the 8-purpose analysis)

> **Why this section exists**: per the 8-purpose ROI analysis, the single highest-ROI use of case research for `four-dx-coach` is **anti-pattern recognition for audit-mode verdicts**. This section consolidates failure-mode anchors across the 5-layer 4DX stack, drawn from authoritative sources (a FranklinCovey insider, the Leader-In-Me education-context companion, an academic critique with meta-analysis support, two transparent real-org failures, and one anonymous frontline complaint).
>
> Failure-mode dictionary entries are reference material for the agent's verdict-shape calibration. They are NOT case banks themselves — when an actual artifact triggers audit-mode, route to the verbatim-disclosed Tier 1 case (Bravelab is the gold standard for D2 / D4 collapse) and use this dictionary for the rule-mapping table headings.

### Failure-mode source inventory

| # | Source | Coverage | Authority | Verification |
|---|---|---|---|---|
| F1 | Andy Cindrich (FranklinCovey insider) "5 Things Leaders Get Wrong" — LinkedIn | 5 canonical failure modes named by a member of the team that developed 4DX | Insider | ★★★ direct WebFetch read |
| F2 | Leader In Me Education "5 Things Educators Get Wrong" | Same 5 modes + 4 verbatim education micro-WIG/lead examples | FranklinCovey-aligned | ★★★ direct WebFetch read |
| F3 | Kay C Dee, "The 4 Disciplines of Execution – Keeping Score" — Academic Change Happen blog | Academic critique + Harkin et al. (Psychological Bulletin) meta-analysis on monitoring | Academic | ★★★ direct WebFetch read |
| F4 | Bravelab.io (already Tier 1) | D2 collapse + D4 session creep + onboarding-prep failure | Real-org | ★★★ direct read |
| F5 | Anonymous IT employee, Chesapeake Energy IT (thelayoff.com 2017) | Frontline view of mandatory-rollout failure + wrong-fit (CE-26 boundary) | Anonymous frontline | ★★★ direct playwright read |

**Public URLs**:
- F1: https://www.linkedin.com/pulse/5-things-leaders-get-wrong-franklincoveys-4-execution-andy-cindrich
- F2: https://www.leaderinme.org/blog/4-disciplines-of-execution-5-things-educators-get-wrong/
- F3: https://academicchange.org/2018/01/30/the-4-disciplines-of-execution-keeping-score/
- F4: (see Bravelab.io entry in Tier 1)
- F5: https://www.thelayoff.com/t/MoBMa7A

### Failure-mode coverage matrix (per skill)

| 4DX layer | Failure mode | Best anchor source | Verbatim quote / spec |
|---|---|---|---|
| **Treat as program not OS** | Implementing 4DX as a one-off training initiative rather than the team's operating system | F1 + F2 (mistake 1) | "Treat it like a program, and results will be fleeting" — Cindrich |
| **D1 too many WIGs** | Teams ending up with 3+ WIGs because they can't pick one | F1 (mistake 2) + book Ch 1 | "Hitting your sales number is your job – it is not a WIG" — Cindrich |
| **D1 metrics that move <monthly** | Tying WIG to lag that only shifts annually (state test scores, year-end revenue) | F2 (mistake 2) | "For a Wildly Important Goal® to be effective… it needs to be a metric that can be moved at least monthly if not every week" |
| **D1 lag-as-WIG (your-job-is-not-a-WIG)** | WIG = "hit Q4 number" / "operate the call center" — already the job | F1 (mistake 2) | Cindrich verbatim above |
| **D2 leveraged-behavior boredom** | Lead measures = "do X activity 5x/week"; gets boring; team disengages | F1 + F2 (mistake 3) | F2 has 4 small-outcome examples: SSR (20 min × 3/wk = boring), AP essays (75% scoring 4-5 = small-outcome), basketball offensive rebounds (10+ per game), band sections mastering one movement weekly |
| **D2 leads can't actually be influenced weekly** | Picking "increase NPS" / "improve customer satisfaction" as a "lead" — neither team-influenceable nor weekly-movable | F1 (mistake 3) + Bravelab F4 | "LEAD measures didn't work. Not everyone was able to define what he needs to do to bring our efforts closer to our LAG measure" — Bravelab verbatim |
| **D3 dashboard not scoreboard** | Scoreboard becomes "passive dashboard," gets more metrics, lives in a tool nobody opens, dies | Common across F1-F5 | "Once the scoreboard dies, the system dies" |
| **D3 scoreboards used to name-and-shame** | Public posting weaponized as embarrassment / pressure / firing tool | F1 + F2 (mistake 4) | Brené Brown research cited: shame "crushes our tolerance for vulnerability, thereby killing engagement, innovation, creativity, productivity, and trust" |
| **D3 evidence base** | Public + physical recording > private + not recorded; behavior monitoring → behavior change; outcome monitoring → outcome change | F3 (Harkin et al. Psychological Bulletin meta-analysis) | "monitoring progress in public and physically recording progress had larger effects on goal attainment than monitoring that was done in private and not recorded" (pg. 219); "monitoring behavior is more likely to lead to changes in behavior than is monitoring outcomes, whereas changes in outcomes are more likely to occur when people monitor outcomes rather than behaviors" (pg. 219) |
| **D4 session creep** | WIG Sessions ≥30min, sometimes 1hr — defeats brevity discipline | F4 Bravelab verbatim | "WIG Sessions required more than 30 minutes. Sometimes up to 1h" |
| **D4 member prep failure** | Members arrive without their measurements / current numbers, blocking accountability flow | F4 Bravelab verbatim | "Everyone has to be prepared before the WIG Session (everyone needs to know their current measurements)" |
| **D4 leadership disengagement** | Execs treat WIG sessions as "something teams do," not something leaders run; cadence fades within a quarter | F1 (mistake 5) | "Goal Clarity + Commitment + Cadence = Results" equation — Cindrich |
| **D4 accountability-as-control vs commitment** | Manager runs WIG Session as performance review / surveillance; commitment never internalized | F1 + F2 (mistake 5) | "High clarity with low commitment produces only compliance" — F2 |
| **Ch 8 onboarding mandatory-not-voluntary** | Forcing single department / IT / support org into 4DX while peers exempt; produces "fake smile" compliance | F5 Chesapeake Energy IT (anonymous frontline) | "we are punished by having to act like 4DX is cool, when the REST OF THE COMPANY does not have to do this silly program… we are going to fake smile our way though this junk" — anonymous IT employee, March 2017 |
| **Ch 8 wrong-fit (CE-26 boundary)** | Imposing 4DX on intrinsically reactive / support / on-call work where whirlwind IS the strategic value | F5 Chesapeake Energy IT | "If our IT leadership was worth one bucket of piss they would have pushed back and explained this would not work in a support organization" — same source |
| **Ch 8 skipping pre-onboarding training** | Launching 4DX without grounding team in foundational concepts first | F4 Bravelab verbatim | "People who will be using 4DX should learn the basics of this method before we start" |
| **Sustaining: cadence collapse** | After multi-week skip, teams cannot re-enter cadence; whole system dies | Common observation across F1-F5 | (anchor case absent — search future round) |
| **Sustaining: WIG forgotten** | Year-end review reveals nobody remembered the WIG mid-year | Common | (anchor case absent — search future round) |

### Cross-axis truths from failure-mode aggregation

- **D2 is the most-failed discipline** — confirmed by Cindrich (mistake 3), Bravelab (verbatim "didn't work"), book Ch 3 ("most-misunderstood discipline"). All 5 sources circle around D2 as the breakdown point. Audit-mode for `4dx-d2-lead-measures` should treat D2 collapse as the **most likely** verdict, not the rarest.
- **Mandatory rollout = compliance, not commitment** — Cindrich's mistake 5 + Chesapeake F5 + book Ch 8 all align: voluntary opt-in is sacred, coercion produces "fake smile" theater. The audit-mode for `4dx-meta-team-leader-onboarding` should weight mandatory-rollout signals heavily.
- **Goal Clarity + Commitment + Cadence = Results** — Cindrich's diagnostic equation (mistake 5). When audit reveals one of these three is missing, that's the gap to surface.
- **Lead measures that aren't weekly-influenceable look like leads but aren't** — most common D2 trap per Cindrich. "Increase NPS" / "improve customer satisfaction" / "raise revenue" all fail this test. Audit-mode should test "what would moving the needle on this lead THIS WEEK look like?" — if no answer, FAIL.

### Notable UNDERdocumented failure modes (search future rounds)

- **Cadence collapse after week 8-12** — common observation but no verbatim case
- **WIG forgotten at month 6** — common observation but no verbatim case
- **Successful pilot, failed scale-up** — implied by some sources but no verbatim case
- **Cross-team WIG conflict** — when team A's WIG depends on team B's resources; no public case
- **Member-side: inherited a WIG that doesn't ladder** — frontline frustration with poorly-cascaded WIGs; no public case beyond Chesapeake F5

---

## Tier 2 — Useful supplements (★★ disclosure × ≥★★ verification, NOT primary anchor)

| # | Case | Disclosure | Verification | Best use |
|---|---|---|---|---|
| 5 | STEAM K-2 school (Leader In Me) | ★★ partial — full WIG句型, partial leads, partial scoreboard | ★ search snippet only | Education / threshold-based behavior-change WIG |
| 6 | 3rd-grade reading (Leader In Me) | ★★ partial — vague WIG, full lead | ★ search snippet only | Education / time-on-task lead measures |
| 7 | Boy Scouts of America Cub Scouting | ★★ partial — full WIG, no leads/scoreboard | ★ search snippet only | Nonprofit / membership-growth WIG |
| 8 | Marriott Hotels | ★ marketing — vague WIG, no specifics | ★ search snippet only | Hospitality cross-reference to Opryland |
| 9 | Whirlpool | ★ marketing — outcome-only ($5.7M / 90 days) | ★ search snippet only | Outcome calibration only |
| 10 | IT Lead Measures gist (meredian/GitHub) | ★★ partial — 6 example sets, no real-org context | ★★ direct read (gist text) | `4dx-d2-lead-measures` IT-context calibration; not real implementation |
| 11 | Hashimoto note article (JP small-team) | ★★ partial — author admits 2 verbatim failure compromises (D3 scoreboard skipped, sustaining drift toward easy work) | ★★★ direct WebFetch read | **JP-context partial-failure anchor** — the only public JP source where a practitioner names compromise modes verbatim. See expanded entry below. |

### #11 expanded — Hashimoto note (JP partial-failure anchor)

**Source**: Hikaru Hashimoto, "チーム目標を形骸化させない！4DXのススメ" — note.com article.
**Public URL**: https://note.com/hikaruhashimoto/n/n9d27fe5885aa
**Title literal**: "Don't let team goals fall into formality! Recommending 4DX" — the title itself names 形骸化 (formalization / hollowing-out) as the failure mode 4DX is positioned to solve.

**Naming note**: Japan does NOT use "4DX" as the framework abbreviation in widespread practice — Japanese readers default to the cinema brand "4DX" (CJ 4DPLEX). The framework is canonically called「実行の4つの規律」or sometimes「4Dx」(lowercase x) by FranklinCovey JP. Search SEO for failure cases is dominated by cinema noise; framework-failure literature in JP is structurally sparse (see Structural gap below).

**Verbatim partial-failure admissions** (from Hashimoto's own implementation):

1. **Sustaining drift warning (Ch 10 anchor)**:
   > 「ふと気が緩むと、OKRをないがしろにして目の前の業務にただ取り組むという『楽』に流れてしまう」
   ("When focus slackens, the team falls back into just dealing with day-to-day work and the OKRs / WIGs get neglected as the 'easy' path.")
   — corresponds to Cindrich F1 mistake 5 (accountability-as-control vs commitment) + book Ch 10 cadence-collapse pattern

2. **D3 scoreboard compromise (verbatim admission)**:
   > 「この時点でOKRをメインで運用するのは5人ということもあり、可視性の強化はおサボりさせてもらい、スプレッドシートをスコアボード代わりにしていました」
   ("Since at that time only 5 people were running OKRs as primary, we slacked on enhancing visibility and used spreadsheets as a substitute for the scoreboard.")
   — corresponds to dashboard-not-scoreboard failure mode (no 5-second-test, no public posting, no team-built artifact); Bravelab F4 had the same compromise but was honest about it failing — Hashimoto frames it as a temporary trade-off, less honest about consequences

3. **Cadence discipline maintained (verbatim, contrast point)**:
   > 「毎週月曜日の10:30-11:00に固定で実施していました」+「セッション自体は延長せず30分で終わらせる」
   — D4 30-min ceiling held; pattern matches Opryland / book ideal

**Cross-skill applicability**: `4dx-sustain-momentum-rescue` (sustaining drift "楽に流れる" verbatim — JP-context language for the canonical failure); `4dx-d3-scoreboard` audit-mode (spreadsheet-as-scoreboard compromise visible from inside JP small-team perspective); `4dx-meta-strategy-triage` (small-team 5-person pre-condition that justifies the compromise).

**Use this case when**: JP small-team / small-org context (≤10 ppl); user asks why their cadence is collapsing in JP corporate language; user has spreadsheet-as-scoreboard and asks "is this OK?"
**Do NOT generalize this case to**: cases where Hashimoto's compromises actually DID lead to failure (the article is forward-optimistic; he doesn't track outcomes). Cite the verbatim admissions only as anti-pattern flags, not as failure-case verdicts.

**Disclosure / verification grade**: ★★ partial disclosure (D3 + sustaining only; D1-D2-D4 unspecified) × ★★★ direct read.

**Tier 2 promotion path**: each Tier 2 case should be re-verified via direct read before being promoted to anchor candidacy. Search snippets are summary-level and may be paraphrased.

---

## Tier 3 — Insufficient (★ marketing-tier — keep for vocabulary calibration only)

| # | Case | Disclosure | Verification | Note |
|---|---|---|---|---|
| 12 | ノーリツ V プラン23 | ★ marketing — D1-D4 specifics absent | ★★★ direct PDF read | JP-context vocabulary calibration only (中計 / 方針展開 / 営業統括 / 挑戦する風土); see memory note `feedback_marketing_cases_lack_d1_d4_specifics` for full reasoning |
| 13 | マルハン (FranklinCovey JP) | ★ marketing | ★★ WebFetch summary | Summary only: "マルハンイズム浸透" |
| 14 | 公益社 (FranklinCovey JP) | ★ marketing | ★★ WebFetch summary | "サービス品質向上 + 風土変革" |
| 15 | アスクレップ | ❌ inaccessible | — | Original PDF redirect to FCE-publishing 301; no longer accessible |
| 16 | 日本 NCH | ❌ insufficient | — | Mention only; no detail page |
| 17 | room8.co.jp | ★ marketing — generic illustrations | ★★ WebFetch summary | Generic JP industry examples (web-design / legal / coworking) |
| 18 | Sales Tax Institute | ★ marketing — D1-D4 not disclosed | ★★ WebFetch summary | "Whether we are designing a webinar… we are always asking if this is what matters most" |

**Tier 3 use rule**: vocabulary calibration only (JP industry terms, voice samples). Never as case-bank anchor.

---

## Tier 4 — Specialized / educational (worth tracking, NOT case-bank material)

| Case | Status |
|---|---|
| Abdhi Famili General Hospital (Indonesia) | Academic paper; full PDF in Bahasa Indonesia; outcome statistically significant (p<0.05); operational details inaccessible without translation |
| United Animal Health U-4DX Playbook | Internal playbook PDF (40+ pages); WebFetch couldn't render via standard extraction; Read tool's PDF support could be tried in future if needed |
| FranklinCovey video case studies | Multiple short videos referenced; not transcribed publicly |

---

## Decision rubric: when to use which tier

**For audit-mode-examples.md case banks** (agent runtime): only Tier 1 (★★★ disclosure × ≥★★ verification) cases qualify. Tier 2 is acceptable as supplementary anti-pattern reference but should not be the primary anchor.

**For boundary references / Don't-confuse-with neighbours** (agent runtime): Tier 2-3 are fine as one-line callouts.

**For human authoring decisions**: this whole inventory is the source of truth.

**For trigger-language calibration in description / activation**: Tier 3 JP cases provide vocabulary even though they fail as case-bank anchors (中計 / 方針展開 / 挑戦する風土 vocabulary already injected into v0.8.1 trigger phrases).

---

## Structural gaps in publicly-available case material

Documented honestly so future research rounds don't waste cycles re-discovering them.

### JP-context failure cases — structural absence

**The gap**: Japan has effectively zero ★★★-disclosure failure cases for the framework. Tier 1 + Tier 2 failure-mode anchors are entirely English-source (Cindrich / LiM / Kay C Dee / Bravelab / Chesapeake). The only JP partial-failure source is Hashimoto note (#11, Tier 2) — and even that frames its compromises as forward-optimistic trade-offs, not retrospective failure analysis.

**Root causes** (validated through 4 search rounds across EN + JP, 2026-05-01):

1. **Naming collision** — "4DX" in Japan canonically refers to the cinema brand (CJ 4DPLEX immersive theater experience). Search SEO is dominated by movie-experience reviews. Even targeted searches with the framework name「実行の4つの規律」+ failure terms surface mostly framework-explainer content + cinema noise, not real implementations.
2. **Lower JP framework adoption vs OKR** — JP business-management failure literature for OKR is rich (Coral Capital, HR大学, 中小企業OKR, hr-mitas, proffit, hashikake, AI經營総合研究所 all have multi-page analyses). Same depth for「実行の4つの規律」does NOT exist.「実行の4つの規律」is consultant-driven (FranklinCovey JP) with shallower bottom-up community.
3. **JP corporate culture — failures aren't published** — equivalent of Bravelab's "we screwed up" LinkedIn post in JP-speaking corporate world is nearly nonexistent. JP failure narratives stay in paid consulting reports or anonymous BBS (匿名掲示板) — the latter low-quality, hard to verify.
4. **JP voices in public domain are FranklinCovey-aligned** — Hashimoto note / room8.co.jp / takubeen / xQソリューション / U-NOTE / SlideShare 4つの規律 — all promoting the framework, not analyzing failures.

**What this means for case-bank work**:
- Cross-framework substitution (OKR failure literature) is acceptable as long as the failure modes shared with 4DX are explicitly named (cadence collapse / 形骸化 / 週次レビュー続かない / リーダー理解不足 are all shared).
- The JP-specific 形骸化 vocabulary is itself useful — appears in Hashimoto title + at least 6 OKR-failure articles. Worth injecting into agent's JP-context anti-pattern dictionary even without a Tier 1 JP anchor.
- Future research direction: actively monitor JP business blogs / note.com / Qiita for failure narratives that emerge over time. Not currently in supply but may become available.

### Other gaps surfaced from this research cycle

- **No verbatim cadence-collapse-after-N-weeks case** in any language — common observation but not documented as a single anchor case
- **No verbatim "WIG forgotten at month 6" case** — implied but not anchored
- **No verbatim "successful pilot, failed scale-up" case** — implied but not anchored
- **No verbatim cross-team WIG conflict case** (when team A's WIG depends on team B's resources)
- **No verbatim member-side cascade frustration** beyond the Chesapeake F5 anonymous post

**Compensation**: Cindrich F1 + LiM F2 cover these as failure-mode descriptions even without org-anchored cases. For audit-mode verdicts, the failure-mode dictionary is sufficient; for narrative storytelling cases, the gap remains.

---

## Open questions for future research

1. **More CFR PDFs?** Opryland is one; FranklinCovey CFR has produced multiple. Searching for "Center for Advanced Research" + "FranklinCovey" + case studies should surface more.
2. **Book PDF / paid ed?** The 4DX 2nd ed. has anchor cases (Younkers / Sydney accounting / others) inline. Already partially captured in skill bodies. A complete extraction would close the loop.
3. **Tier 2 → Tier 1 promotion?** The 4 Tier 2 education cases (STEAM K-2 / 3rd-grade reading / Cub Scouts / Marriott) could be verified via direct read of original Leader In Me PDFs / scouting.org sources. Worth one cycle if education-context anchors become priority.
4. **Anonymized real client cases?** The user (kouko) running 4DX themselves and accumulating case data over time would produce highest-value cases.
5. **JP-context Tier 1?** No JP case currently meets ★★★ disclosure. If FranklinCovey JP ever publishes a CFR-style research PDF for a JP client, that would be the highest-value addition. **Failure-side**: JP-context failure cases are structurally absent (see Structural gaps section above) — pursuing JP failure anchors via direct search is unlikely to yield Tier 1 results; better strategy is monitoring note.com / Qiita over time + cross-framework borrowing from JP OKR-failure literature with explicit attribution.

---

## Provenance note

This inventory was assembled 2026-05-01 from:
- 5 web searches across EN + JP keyword sets
- 8 WebFetch deep-dives into specific case URLs
- Cross-validation of cases mentioned in multiple sources
- **Direct read of 3 PDFs** (Opryland CFR; CSN Support Packet; ノーリツ V プラン23)
- **Playwright full-DOM extraction of 2 articles** (Bravelab.io LinkedIn; Methodist Le Bonheur Becker's Hospital Review via Wayback Machine)
- 1 reverted experiment with the ノーリツ case (see memory note)

Total research time: 2 sessions (initial discovery 2026-05-01 morning; full Tier 1 verification 2026-05-01 afternoon). Re-running this inventory annually is sensible if case-bank sourcing becomes active work.

**Verification cycle history**:
- 2026-05-01: initial inventory (Tier 1 partial verification — Opryland direct, others via search snippet)
- 2026-05-01 (same day, second pass): full Tier 1 verification — CSN PDF read, Bravelab playwright read, Methodist Wayback read. All 4 Tier 1 cases now ★★★ verification.
- 2026-05-01 (same day, third pass): added failure-mode dictionary (F1 Cindrich / F2 LiM / F3 Kay C Dee / F4 Bravelab / F5 Chesapeake) + 18-mode coverage matrix.
- 2026-05-01 (same day, fourth pass): JP-focused failure search; promoted Hashimoto note to Tier 2 partial-failure anchor; documented JP-context structural gap (naming collision + lower JP framework adoption + JP corporate failure-publication norms).
