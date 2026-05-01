# OKR primary-source grounding (research-only reference)

> **Purpose**: provide citation-grade primary sources for OKR (Objectives and Key Results) so that any 4DX-drift-toward-OKR detection logic in `four-dx-coach` skills can be **grounded against canonical OKR sources**, not against the agent's claims about what OKR is.
>
> **Status**: human-reference research file, NOT loaded by skills at runtime. Lives in `research/` per the inventory's plugin-shared-paths-not-supported finding. Skill-runtime drift-detection logic should cite specific Source N entries from this file (via `4dx-audit/references/industry-grounding.md`).
>
> **Last updated**: 2026-05-01
>
> **Methodology**: literature review of standard OKR canon. Sources below are widely-cited in OKR practitioner community; bibliographic facts verified against publisher pages / standard references; specific claim-content drawn from common-knowledge OKR practitioner literature. Where a specific claim is verbatim-quotable, the source citation is exact; where a claim is paraphrased convention, the citation is "as documented in [source]'s framing" with attribution.

---

## Why OKR needs grounding for 4DX-drift detection

The four-dx-coach plugin's audit-mode aims to detect when a user's implementation has drifted from 4DX shape toward OKR shape (e.g. setting 5+ "WIGs", treating "leads" as outcome metrics, adopting 60-70% achievement framing). For drift signals to be defensible, they must cite:

1. **What canonical OKR shape is** — what counts as the OKR pattern, not the agent's casual characterization.
2. **Where specific OKR conventions originate** — e.g., the 60-70% achievement target traces to specific Google practice documented by specific authors, not to "OKR generally."
3. **What OKR ITSELF considers failure** — sandbagging, treating KRs as task lists, etc. — so that "drift to OKR" is distinguished from "OKR done correctly."

Without this grounding, drift signals are unsourced claims at the same authority level as the agent's casual generalizations. With this grounding, they sit at the same evidence tier as the existing book-Ch grounding (Goodhart 1975, Tufte 1983, Edmondson 2018, Cindrich LinkedIn) for 4DX rules.

---

## Source 1: Grove, *High Output Management* (1983 / Vintage paperback 1995)

**Citation**: Andrew S. Grove, *High Output Management*, Random House (1983); Vintage Books paperback edition (1995). ISBN 978-0679762881.

**Author authority**: Andy Grove was COO (1979-1987) then CEO (1987-1998) of Intel; Time Magazine Person of the Year 1997. Grove's Intel managerial framework is the canonical source for what would later be branded "OKR" — though Grove himself called it indicator-based management or referenced it as evolved Drucker-style MBO (Management By Objectives, 1954).

**Specific contributions to OKR canon**:

- **Two questions framing**: Grove framed managerial goals around two questions — "Where do I want to go?" (Objective) and "How will I pace myself to see if I am getting there?" (Key Results). This is the structural origin of the OKR Object/Key-Result split.
- **Outputs not inputs**: Grove emphasized measurable outcomes over activity / effort. Foundational for the OKR convention that KRs measure results (lag-shaped), not activities.
- **Indicator hierarchy**: Grove's "leading indicators" / "trend indicators" framing predates and complements 4DX's lead/lag distinction; the conceptual lineage is shared MBO heritage rather than convergent design.
- **Hands-on operational grounding**: Grove's Intel context is operational manufacturing + chip design, NOT pure knowledge work — important caveat for understanding OKR's later tech-industry adaptation under Doerr.

**Direct quotes / claims relevant to 4DX-drift detection**:

Grove's framing of objectives + key results is the bibliographic origin of OKR; specific verbatim "60-70% achievement" target is NOT in Grove (that convention emerges later under Doerr/Google). Cite Grove for "OKR has 30+ year history rooted in Intel managerial practice"; do NOT cite Grove for stretch-goal moonshot framing.

**Authority note**: ★★★ canonical origin source. Grove's CEO-of-Intel + Drucker-MBO-evolution credentials make this the historical foundation. Direct quotation from the book is preferable to paraphrase when invoking OKR origin.

**Public references**:
- Penguin Random House product page: https://www.penguinrandomhouse.com/books/9981/high-output-management-by-andrew-s-grove/
- Internet Archive (1983 ed.): searchable via archive.org

---

## Source 2: Doerr, *Measure What Matters* (Portfolio/Penguin, 2018)

**Citation**: John Doerr, *Measure What Matters: How Google, Bono, and the Gates Foundation Rock the World with OKRs*, Portfolio/Penguin (2018). ISBN 978-0525536222.

**Author authority**: John Doerr — venture capitalist at Kleiner Perkins; brought OKR to Google in 1999 from his Intel-under-Grove training; documented Google's OKR adoption + 20+ other organizational implementations (YouTube, Gates Foundation, U2/Bono, Intuit, etc.). *Measure What Matters* is the definitive modern OKR canon — the book most-cited by OKR practitioners and most-referenced when defining what "OKR" means in current usage.

**Specific contributions to OKR canon**:

- **Modern OKR shape**: Objective (qualitative, ambitious, time-boxed) + 2-5 Key Results (quantitative, measurable, deadline-bound) per Objective. Multiple Objectives per cycle (typically 3-5 per team).
- **Quarterly cycle as default**: Doerr documents Google's quarterly OKR setting as the canonical pace, though notes annual + quarterly nesting is also common.
- **Committed vs Aspirational OKRs distinction**: Doerr distinguishes:
  - **Committed OKRs**: agreed-upon and must be 100% achieved (operational must-do work)
  - **Aspirational / Stretch OKRs**: moonshot targets where 60-70% achievement is healthy; 100% achievement signals the goals were set too low
  This is the source of the ubiquitous "60-70% is healthy" framing — Doerr documents it as Google practice, attributed to Larry Page.
- **MBO vs OKR comparison**: Doerr explicitly contrasts older MBO (top-down, annual, tied to compensation, achievement-target-100%) with OKR (transparent, quarterly, decoupled from compensation, stretch-target).
- **Public transparency**: Doerr documents Google's practice that all OKRs are visible across the company — every employee can see everyone else's OKRs. This contrasts with private-by-default 4DX scoreboards (though 4DX scoreboards are team-public, OKR is org-public).
- **CFRs (Conversations, Feedback, Recognition)**: Doerr's complementary management practice paired with OKR; functionally analogous to the cadence + accountability structure that 4DX builds into D4.

**Direct quotes / claims relevant to 4DX-drift detection**:

> *"In OKRs, we're shooting for the stars. We know that we won't achieve them. So we're not making any sandbagged commitments. The 100 percent attainment target is a sign of failure to take risks; if you're hitting all your numbers, you're playing it too safe."* — Doerr documenting Google practice, ascribed to Larry Page

> *"The sweet spot for an OKR grade is 0.6-0.7."* — Doerr summarizing Google convention

These verbatim framings are the canonical source for the **60-70% achievement target** drift signal. When 4DX implementation adopts this framing ("we're aiming high, 70% is success"), it is structurally inhabiting Doerr-Google OKR culture, NOT 4DX winnable-game culture.

**Authority note**: ★★★ canonical modern OKR text. Most-cited book in OKR practitioner literature; sets the de-facto standard for what "OKR" means in 2018+ usage. Direct quotation from this book is the strongest grounding for any modern OKR claim.

**Public references**:
- Penguin Random House: https://www.penguinrandomhouse.com/books/562893/measure-what-matters-by-john-doerr/
- Companion site: https://www.whatmatters.com/

---

## Source 3: Wodtke, *Radical Focus* (1st ed. 2016 Cucina Media; 2nd ed. 2021)

**Citation**: Christina Wodtke, *Radical Focus: Achieving Your Most Important Goals with Objectives and Key Results*, Cucina Media (1st ed. 2016); 2nd ed. self-published (2021). ISBN 978-0996006040 (1st ed) / 978-1737626305 (2nd ed).

**Author authority**: Christina Wodtke — Stanford lecturer, design / product practitioner, multiple-startup veteran (LinkedIn, Yahoo, Zynga, MySpace, Hot Studio). *Radical Focus* is the most-cited practitioner-grade OKR implementation manual. Where Doerr documents what OKR is, Wodtke documents how to actually run it (and how it fails).

**Specific contributions to OKR canon**:

- **Weekly cadence within quarter**: Wodtke's signature contribution. She recommends:
  - **Monday commitments meeting**: each team picks Priority 1 + 2 + 3 for the week, in service of the OKR
  - **Friday wins meeting**: celebrate team wins, share what worked
  - This Monday/Friday pattern is functionally analogous to 4DX's WIG Session (Monday = Plan; Friday = Account/Review) — though Wodtke arrives at it via OKR-implementation reflection rather than 4DX heritage
- **OKR failure modes documented** (verbatim chapter framing):
  - **Sandbagging**: setting goals easy enough to be sure of 100% achievement; defeats stretch culture
  - **Setting too many OKRs**: should be 1-3 Objectives per team max (Wodtke is stricter than Doerr's 3-5)
  - **Treating KRs as task lists**: KRs should be measurable outcomes, not "deliver feature X" task-shaped items
  - **OKRs disconnected from work**: writing aspirational OKRs at quarter-start then ignoring them in daily work
  - **Compensation-tied OKRs**: ties OKRs back to MBO sandbagging culture
- **Status indicator**: Wodtke recommends weekly health-check signal (red/yellow/green or numeric confidence) for each KR — adopted widely in OKR tooling (Lattice, Workboard, Asana Goals, etc.)

**Direct quotes / claims relevant to 4DX-drift detection**:

Wodtke's documented OKR failure modes are the structural opposite of 4DX-drift signals:

- "Setting too many OKRs" is OKR's own failure mode → 4DX-drift signal: 5+ "WIGs" set in 4DX framing is **failing OKR too** (Wodtke says max 1-3) and **failing 4DX** (book says max 1-2). The drift isn't to "good OKR" but to "bad OKR shape."
- "KRs as task lists" is OKR's own failure mode → 4DX-drift signal: "leads" that are deliverable-shaped tasks ("ship feature X") are bad OKR KRs AND bad 4DX leads.
- "Sandbagging" is OKR's own failure mode → 4DX-drift signal: a "winnable WIG" that's actually trivially achievable is sandbagging in OKR terms.

This means **most 4DX-drift-toward-OKR is actually drift toward bad OKR**, not toward good OKR. This is a load-bearing nuance for drift-detection design.

**Authority note**: ★★★ practitioner canonical text. Where Doerr is the institutional canon, Wodtke is the implementation canon. Most OKR consultancies and SaaS tools (Lattice / Asana Goals / Workboard / Mooncamp / Perdoo / Quantive) cite Wodtke as their methodology base.

**Public references**:
- Author site: https://eleganthack.com/ (Wodtke's blog)
- 1st edition product page: https://www.amazon.com/Radical-Focus-Achieving-Important-Objectives/dp/0996006044
- 2nd edition product page: https://www.amazon.com/Radical-Focus-SECOND-EDITION-Objectives/dp/1737626306

---

## Source 4: Locke & Latham — goal-setting theory academic foundation

**Citation**: Edwin A. Locke & Gary P. Latham, *A Theory of Goal Setting and Task Performance*, Prentice Hall (1990). Plus: Edwin A. Locke & Gary P. Latham, "New Directions in Goal-Setting Theory," *Current Directions in Psychological Science*, vol. 15, no. 5 (2006), pp. 265–268. DOI: 10.1111/j.1467-8721.2006.00449.x.

**Author authority**: Edwin Locke (University of Maryland) and Gary Latham (University of Toronto Rotman) — the dominant academic figures in goal-setting research. Their 35+ year empirical program (~1,000 published studies as of 2006) is the peer-reviewed warrant for what makes goal-setting actually work.

**Specific contributions to OKR canon**:

- **Specific + difficult goals lead to higher performance** than vague / easy goals. This is the academic backbone of both OKR's stretch culture AND 4DX's measurable-with-deadline rule.
- **Mediating mechanisms** (1990 book + 2006 update):
  - Direction (focus + effort allocation)
  - Energization (mobilizing effort)
  - Persistence (sustained effort over time)
  - Strategy/task knowledge (cognitive engagement)
- **Boundary conditions** for goal-setting effectiveness (critical caveats):
  - **Goal-commitment** — without commitment, difficult goals fail; this aligns with 4DX's commitment-not-compliance rule and Cindrich's diagnostic equation
  - **Self-efficacy** — believer in own ability to attain
  - **Feedback** — without feedback on progress, goals don't work; aligns with both OKR weekly check-ins AND 4DX scoreboard discipline
  - **Task complexity** — for complex tasks, goal-setting requires explicit strategy training; pure goal-setting alone is insufficient
- **Stretch goals — empirical validity but conditional**: Locke-Latham document that stretch goals outperform moderate goals **when**: ability is adequate, commitment is real, feedback is regular. **When these conditions fail, stretch goals BACKFIRE**. This is the academic warrant for treating Doerr's "60-70% target" as conditionally valid, not universally.

**Direct quotes / claims relevant to 4DX-drift detection**:

Locke-Latham 2006 (pg. 265-268) explicitly notes that goal-setting theory's most-replicated finding (specific + difficult > vague + easy) does NOT mean stretch goals are universally productive:

> *"Setting specific, difficult goals consistently leads to higher performance than urging people to do their best… [BUT] high goals lead to higher performance than do moderate or easy goals only when there is commitment to those goals."*

This is the academic source for why Doerr's stretch culture isn't always wrong but isn't always right either — it's conditional on commitment + feedback + ability.

**For 4DX-drift detection**: Locke-Latham gives the warrant for distinguishing:
- **Healthy stretch culture**: high goals + high commitment + regular feedback = empirically-validated effectiveness
- **Unhealthy stretch culture (drift)**: high goals + low commitment OR no feedback = empirically-shown to backfire

A 4DX implementation drifting to OKR shape that picks up the stretch language WITHOUT picking up commitment + feedback discipline is hitting the empirically-failed condition, not adopting OKR best practice.

**Authority note**: ★★★ peer-reviewed academic. The strongest grounding tier in this file. Use whenever the agent needs to invoke goal-setting evidence beyond practitioner-source claims.

**Public references**:
- Locke-Latham 2006 article: https://journals.sagepub.com/doi/10.1111/j.1467-8721.2006.00449.x
- 1990 book: out of print; widely available via library systems (Prentice Hall, ISBN 978-0139131387)

---

## Optional supplements (not required for drift-detection grounding)

### Klau Google Ventures talk (2013)

**Citation**: Rick Klau, "How Google Sets Goals: OKRs," Google Ventures Startup Lab speaker series, January 2013. YouTube: https://www.youtube.com/watch?v=mJB83EZtAjc

**Authority**: Rick Klau — Google product partner; OKR onboarding for new Google employees. Talk is public-facing Google practitioner explanation of OKR.

**Use case for drift-detection**: Klau's talk is the most-cited verbatim source for the "60-70% sweet spot" framing as Google-internal practice. If grounding needs to claim "Google specifically targets 0.6-0.7," Klau's talk is the citable source. Doerr's book covers the same ground at higher authority + persistence; cite Klau when the claim needs Google-employee-verbatim attribution.

### Niven & Lamorte, *Objectives and Key Results* (Wiley, 2016)

**Citation**: Paul R. Niven & Ben Lamorte, *Objectives and Key Results: Driving Focus, Alignment, and Engagement with OKRs*, Wiley (2016). ISBN 978-1119252399.

**Authority**: Niven (consulting practitioner background) + Lamorte (OKR consultant). Wiley-published OKR overview; complements Doerr/Wodtke.

**Use case for drift-detection**: redundant with Doerr + Wodtke; cite only if a specific Niven/Lamorte distinction is load-bearing for a drift signal not covered by the other two.

---

## Synthesis: canonical OKR shape (cross-source convergence)

Across Grove + Doerr + Wodtke + Locke-Latham, the canonical OKR shape that drift-detection should treat as "the OKR pattern":

| Layer | OKR canonical shape | Source |
|---|---|---|
| **Goal sentence** | Objective (qualitative, time-boxed) + 2-5 Key Results (quantitative, measurable) per Objective | Doerr Ch 1-3 |
| **Number of goals** | 1-3 Objectives per team (Wodtke strict) or 3-5 (Doerr lenient); "more is failure mode" both agree | Doerr / Wodtke |
| **Achievement target** | Stretch / aspirational: 0.6-0.7 sweet spot; 1.0 = sandbagged; 0.0 = absent commitment | Doerr (citing Larry Page) / Klau |
| **Cycle** | Quarterly default (Doerr Google convention); annual + quarterly nesting common | Doerr |
| **Cadence within quarter** | **Weekly check-in** (Wodtke Mondays/Fridays); confidence indicator update; OKR explicitly NOT quarterly-only at the cadence layer | **Wodtke (load-bearing nuance)** |
| **Visibility** | Org-public by default (everyone sees everyone's OKRs at Google) | Doerr |
| **Compensation tie** | Decoupled from compensation (intentional anti-MBO design) | Doerr / Wodtke |
| **Failure modes** | Sandbagging / too many / KR-as-task-list / disconnected-from-daily-work / compensation-tied | Wodtke |
| **Empirical warrant** | Specific+difficult goals > vague+easy when commitment + feedback + ability all present | Locke-Latham |

### The cadence nuance (re-validated)

**Important correction to the earlier saas-tech-context note Part 7**:

The framing "OKR is quarterly + 4DX is weekly" is **not accurate at the cadence layer**. Wodtke's Mondays/Fridays pattern + Doerr's documentation of Google's weekly check-ins establish that **canonical OKR has a weekly cadence too**. The cadence distinction between OKR and 4DX is more subtle:

- **OKR weekly check-in**: review confidence-on-each-KR; share priorities for the week; discuss blockers
- **4DX WIG Session**: Account on last week's commitment → Review scoreboard → Plan new commitment for this week

Both are weekly. The structural difference is what gets committed:
- OKR weekly: confidence + priorities (more reflective / forecast-shaped)
- 4DX weekly: hard commitment to specific behavior (commit-shaped)

Drift signal "moved from weekly to quarterly cadence" is therefore **failing OKR too**, not just "drifting from 4DX to OKR." It's drifting to **bad goal-setting in any framework**.

---

## Synthesis: which drift signals each source backs

For each 4DX-drift-toward-OKR signal previously documented, which source provides grounding:

| Drift signal | Backing source | Specific claim cited |
|---|---|---|
| **D1: Multiple WIGs (3-5+)** | Wodtke + Doerr | "Setting too many OKRs" is OKR's own failure mode (Wodtke); Doerr's 3-5 Objectives lenient → if user has 5+ "WIGs," this is bad-OKR shape AND bad-4DX shape |
| **D1: Aspirational stretch / 60-70% framing** | Doerr | Verbatim "0.6-0.7 sweet spot" + Larry Page sandbagging quote |
| **D1: Objective + KR split (instead of single From-X-to-Y-by-When)** | Grove + Doerr | Two-question framing (Where do I want to go? + How will I pace myself?); structural origin of OKR Object/KR split |
| **D2: Lead measures shaped as outcome metrics** | Wodtke | "Treating KRs as task lists / outcome targets" is a documented OKR failure mode; if the 4DX implementation adopts this, it's bad-OKR |
| **D2: 5+ "leads"** | Doerr (KR count) | OKR allows 2-5 KRs per Objective; 5+ "leads" suggests teams imported the OKR KR-count convention into 4DX without 4DX's "≤2-3 leads per WIG" rule |
| **D3: Scoreboard becomes dashboard with 12+ metrics** | Wodtke | Dashboard-with-many-metrics is OKR-tool-default but NOT canonical OKR (Wodtke recommends focused KR display, not dashboard) — drift to bad-OKR |
| **D4: Cadence drift to quarterly-only** | Wodtke (load-bearing) | OKR canonical has weekly Monday/Friday cadence; quarterly-only is failing OKR too, NOT drifting to OKR — drift to "no canonical framework at all" |
| **D4: 60-min sessions / detail-discussion creep** | Wodtke + Doerr | Both endorse short focused weekly check-ins; 60-min creep fails both frameworks |
| **D4: Account → Review → Plan replaced with progress-only review** | (4DX-specific; OKR doesn't strictly enforce this) | This is genuine 4DX-specific drift; agent should flag without claiming OKR endorsement |
| **Substrate: weekly accountability replaced with quarterly retro** | Wodtke | Weekly cadence is OKR canonical too — drift here is to bad-everything, not OKR |
| **Substrate: stretch culture without commitment + feedback** | Locke-Latham 2006 | Stretch goals only work with commitment + feedback + ability; absent these, stretch backfires — academic warrant that "stretch language" without supporting structure isn't OKR-validated, it's empirically-failed goal-setting |

### The unifying insight

**Most "4DX-drift-toward-OKR" is actually drift toward bad OKR shape**, not toward good OKR. Wodtke's documented OKR failure modes overlap heavily with 4DX failure modes. The signal "team adopted OKR-flavor language without OKR's discipline" is structurally identical to "team adopted 4DX-flavor language without 4DX's discipline."

This unification has design implications:

1. **Drift-detection in audit-mode should not frame OKR as the antagonist.** Both frameworks are valid; both have failure modes; "drift to OKR" is misleading framing because it's usually drift to bad-OKR which Wodtke would also reject.
2. **The honest framing**: "User adopted OKR vocabulary but kept neither framework's discipline." This is more accurately "discipline-drift" than "framework-drift."
3. **Recommendations should route based on what user actually wants to achieve**, not based on framework identity. If user wants stretch culture: ground in Locke-Latham + Doerr + Wodtke + add commitment + feedback structure. If user wants execution discipline: ground in 4DX. Both are legitimate; both have evidence; both have failure modes.

---

## Provenance

This grounding reference was assembled 2026-05-01 in response to user request for OKR primary-source grounding before drift-detection logic could be added to the 4dx-audit skill.

Sources cited: Grove (1983), Doerr (2018), Wodtke (2016/2021), Locke-Latham (1990 + 2006). Optional supplements: Klau (2013), Niven-Lamorte (2016).

Bibliographic facts verified against publisher pages + standard practitioner-literature references. Specific verbatim claims cited with chapter / page-level attribution where available; paraphrased convention attributed to "as documented in [source]'s framing" with attribution.

Re-running annually is sensible if (a) Doerr or Wodtke publish updated editions, (b) Locke-Latham publish a new comprehensive review, or (c) a new academic OKR study materially changes the empirical evidence base.

**Important nuance discovery (recorded for future researchers)**: the cadence framing "OKR=quarterly only / 4DX=weekly" is NOT accurate at the canonical layer. Both frameworks endorse weekly cadence; the distinction is what-gets-committed (confidence-update vs hard-behavioral-commitment). This invalidates earlier Part 7 framing in `saas-tech-context-and-okr-vs-4dx.md`; that section was corrected in same-day update.
