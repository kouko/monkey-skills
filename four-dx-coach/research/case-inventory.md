# 4DX Case Inventory — research notes (human reference, NOT loaded by skills)

> **Purpose**: stable inventory of publicly-accessible 4DX implementation cases with disclosure-depth assessment, so future case-bank decisions for `four-dx-coach` skills can be made from a known-good shortlist instead of re-researching each time.
>
> **Status**: this file lives in `research/`, NOT in any skill directory. Per Anthropic's plugin spec (verified 2026-05-01), skills cannot reference plugin-root paths via `${CLAUDE_SKILL_DIR}` — runtime resources must be skill-internal. This inventory is for **human authoring decisions** only; agents never load it.
>
> **Last updated**: 2026-05-01
>
> **Methodology**: web search across English / Japanese sources for 4DX implementation case studies disclosing actual WIG sentences, lead measures, scoreboards, cadences, and outcomes. Cases below are graded on disclosure depth across the 5 4DX layers (D1 / D2 / D3 / D4 / Ch 8 onboarding).

## Disclosure-grade legend

- **★★★ Full**: WIG句型 with X / Y / When verbatim, named lead measures, scoreboard description, cadence specifics, results
- **★★ Partial**: 2-3 of the above
- **★ Marketing-tier**: outcome narrative + context only; D1-D4 specifics not disclosed
- **❌ Insufficient**: too thin to anchor anything beyond Boundary mention

---

## Tier 1 — Anchor candidates (★★★ full disclosure)

### 1. Gaylord Opryland Hotel (FranklinCovey CFR research PDF)

**Source**: FranklinCovey Center for Advanced Research, "Guest Satisfaction at Gaylord Opryland" by Dean W. Collinwood Ph.D. (March 2007, rev July 2009). 5 pages.
**Public URL**: https://www.vidartop.no/uploads/9/4/6/7/9467257/cfr070815_oprlnd_casstu__r1.1.5__lr.pdf
**Cached at**: `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/d3a8448e-9700-4357-93f1-589640555d7a/tool-results/webfetch-1777588572915-6oslea.pdf`
**License note**: © FranklinCovey CFR. Designed for academic / external distribution. Cite verbatim with attribution; do not redistribute the PDF itself.

**Company**: Gaylord Opryland Resort & Convention Center, Nashville TN; 4000 employees / 75 departments / 2,881 rooms / $300M annual revenue / 1.5M guests/year.
**Date of study**: May 2006 – June 2009.

**Driver**: lowest guest satisfaction of all four Gaylord properties despite $80M room upgrades since 2003 + $400M expansion underway. October 2006 monthly score 43 (all-time low). xQ Survey June 2006 baseline = 25%.

**D1 — WIGs (verbatim)**:
- Org-level: "Hi Touch" (high guest satisfaction) + "Hi Volume" (high occupancy) — two WIGs at the org level
- Front-office team: **"raise their check-in efficiency score from 55 percent to 65 percent by year-end 2007"**
- Reservation Call Center: **"improve guest satisfaction by answering 95 percent of incoming calls"** (baseline 88%)
- Engineering team: weekly walk-through of the hotel for guidance signage (this is technically a lead-measure-as-WIG, useful as anti-pattern reference)
- Old Hickory Steakhouse (Nando Rodriguez): "implement universal service" — every waiter assists guests at any table

**D2 — Lead measures (verbatim or strongly implied)**:
- Universal service behavior change (Old Hickory)
- Weekly hotel walk-through (Engineering)
- "answering 95% of incoming calls" (Call Center — borderline lag)

**D3 — Scoreboards**: "Scoreboards to show goal accomplishment were displayed prominently in the meeting room." Hi Touch / Hi Volume division-level goals "prominently posted." Each division established their own goals contributing to the two org WIGs.

**D4 — Cadence**: "30-minute WIG Sessions" verbatim. Sheryl Chesnutt (Call Center & Reservations Manager) cited as having conducted **27 consecutive WIG Sessions** by April 2007. Quote: "We wouldn't think of missing a WIG meeting." Sessions described as "fun, positive, and efficiently executed" with "spirit of teamwork and open communication."

**Ch 8 — Onboarding**: 2-day exec session (June 2006) → 2-day sessions per division (Convention Services / Food & Beverage / Rooms) → cross-cutting departments (HR, Engineering) → 300 employees trained by in-house leaders → cascade so far that ground-crew + shuttle-bus drivers + shop clerks were "goal-aware" by April 2007 (vs national avg 54% goal-aware).

**Results (verbatim)**:
- Customer-Loyalty: "In the period June 2006-October 2007, the 22 months before the 4 Disciplines program was started, only 34 percent of the guests said they would enthusiastically recommend Opryland to others. In the 20 months since the 4 Disciplines, 58 percent said they would recommend the hotel: a **24-point increase**."
- Guest satisfaction scores: **+17 points** after 4D
- xQ score: 25% (Jun 2006) → ~45% sustained (Jan 2007 onward); overall company score 77 — 20 points higher than FranklinCovey average client; top 10% globally
- Recognition: First time Opryland achieved best guest satisfaction in entire Gaylord chain. Danny Jones nominated for Flywheel Award.

**Reinforcement**: "Public recognition and award items to display at home or in their offices" + "cash bonuses when goals were met."

**Cross-skill applicability**: this single case can anchor `4dx-d1-wig-formulation` (multi-WIG Hi Touch/Volume + division cascade), `4dx-d2-lead-measures` (universal service), `4dx-d3-scoreboard` (prominent display + cascade), `4dx-d4-cadence` (30-min / 27-consecutive), `4dx-meta-team-leader-onboarding` (Ch 8 4-stage rollout), and `4dx-d1-wig-cascade` (4000 employee × 75 dept ladder-up).

**Use this case when**: large org / hospitality / customer-experience WIG / multi-division cascade; full operational reference is needed.
**Do NOT generalize this case to**: small teams (< 50 ppl); contexts without clear lag metric; B2B with long sales cycle (Opryland's lag — guest survey — has fast feedback loop).

---

### 2. Bravelab.io — first 4DX implementation (failure-included)

**Source**: Mariusz Smenzyk (founder, Bravelab.io), "The very first attempt to implement 4DX in Bravelab.io" — LinkedIn post.
**Public URL**: https://www.linkedin.com/pulse/very-first-attempt-implement-4dx-bravelabio-mariusz-smenzyk
**License note**: LinkedIn post by author; cite with attribution. Author explicitly transparent ("90% of scoreboards fill out the date and value").

**Company**: Bravelab.io — Polish digital agency (small startup). Implementation date: 2020-2021.

**Driver**: 5 competing priorities; founder noticed they couldn't actually execute on any of them.

**D1 — WIGs (verbatim, after refinement from initial 5)**:
- **"To issue invoices for all contracted projects by the end of March 2021"**
- **"To decrease unpaid invoices from 84k to 0 by the end of March 2021"**

**D2 — Lead measures (FAILED — useful anti-pattern)**:
- Reused existing project spreadsheet (income/expenses financial data)
- Author quote: "**LEAD measures didn't work. Not everyone was able to define what he needs to do to bring our efforts closer to our LAG measure**"
- Direct evidence of book Ch 3 claim ("D2 is the most-misunderstood discipline")

**D3 — Scoreboard (PARTIAL)**:
- Tool: Google Sheets (no suitable commercial app found)
- Simple date + value entries; "90% of scoreboards fill out the date and value of measurement"

**D4 — Cadence (PARTIAL)**:
- Weekly sessions every Monday at 1pm
- 85% achievement threshold (not 100%)
- **Failure**: sessions exceeded 30-min window, sometimes reaching 1 hour
- **Failure**: members arrived unprepared with current measurements
- **Failure**: members lacked foundational 4DX knowledge beforehand

**Cross-skill applicability**: `4dx-d2-lead-measures` (canonical "leads didn't work" failure mode); `4dx-d4-cadence` (canonical session-creep + prep-failure mode); `4dx-meta-team-leader-onboarding` (canonical "skipped pre-onboarding training" failure).

**Use this case when**: user is in audit-mode and pasting an artifact that shows D2 collapse / D4 session-creep; small-org context (5-15 ppl); SaaS / digital / startup context.
**Do NOT generalize this case to**: large org cascade; established 4DX-experienced teams; cases where the lag itself is malformed (Bravelab's lags were fine; the failure was downstream at D2).

---

### 3. CSN College (College of Southern Nevada) — institutional 4DX rollout

**Source**: CSN 4DX Support & Guidance Packet, September 2024. 38 pages.
**Public URL**: https://news.csn.edu/wp-content/uploads/2024/10/4DX-Support-Guidance-Packet-September-2024.pdf
**Cached at**: `/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/d3a8448e-9700-4357-93f1-589640555d7a/tool-results/webfetch-1777588470712-ojpg7d.pdf`
**Extraction note**: WebFetch failed to render text from this PDF (compressed binary). Re-extract via Read tool's PDF support if used as case-bank source.

**Company**: College of Southern Nevada — public higher-education institution.

**D1 — WIGs (disclosed via search summary, verbatim)**:
- Primary: **"Increase certificate and degree completions from 4,673 to 6,000 by June 30, 2029"**
- Sub-WIG 1: **"Increase retention for all students Fall-to-Fall from 43% to 53% by June 20, 2029"**
- Sub-WIG 2: **"Eliminate equity gaps in successful course completion by 74.7% to 89.7% by June 30, 2029"**

**D2-D4 + Ch 8**: details should be in the 38-page packet but require deeper PDF extraction.

**Cross-skill applicability**: education context anchor; institutional / multi-year cascade; equity / DEI WIG framing (rare in book's anchors).

**Use this case when**: education / public institution context; multi-year horizon (rare — book typically shows quarterly WIGs); compound WIG with sub-targets.
**Do NOT generalize this case to**: short-cycle / quarterly contexts; private-sector commercial WIGs.

---

### 4. Methodist Le Bonheur Germantown Hospital

**Source**: Becker's Hospital Review article on 4DX in healthcare.
**Public URL**: https://www.beckershospitalreview.com/hospital-management-administration/how-the-4-disciplines-of-execution-can-change-healthcare/
**Extraction note**: WebFetch returned 403; data extracted via WebSearch summary.

**Company**: Methodist Le Bonheur Germantown Hospital, 309-bed full-service hospital. Pilot scope: 58-bed unit.

**D1 — WIG**: increase **bedturns** to create "virtual capacity" in the 58-bed unit. Focused on simple discharges (total joint patients) rather than complex (SNF patients).

**D2 — Lead measures (predictive)**: defined per book Ch 3 lead-vs-lag framing; specifics not disclosed in article.
**D3 — Scoreboard**: nurses self-built scorecards tracking how lead indicators affected bedturn rate.
**D4 — Cadence**: weekly meetings to discuss results, review lead indicators, evaluate plan.

**Cross-skill applicability**: healthcare anchor; team-built (D3 nurse self-built scorecards = book Ch 4 "team owns the board" principle); pilot-scope rollout pattern.

**Use this case when**: healthcare / clinical operations / patient-throughput WIG.
**Do NOT generalize this case to**: knowledge-work or creative-work contexts (clinical workflow is highly structured).

---

## Tier 2 — Useful supplements (★★ partial disclosure)

### 5. STEAM K-2 school (Leader In Me network)

- **WIG (verbatim)**: "80% of K-2nd teachers will lead a STEAM thinking activity in their classroom at least twice a month by December 2018"
- Lead measures: types of activities done, subject integration, student-product creation
- Scoreboard: % teachers applying STEAM activities + count of activities done
- Source: search summary on Leader-In-Me 4DX schools

**Use for**: education / behavioral-change WIG; threshold-based WIG ("80% of teachers will…") rather than count-based.

### 6. Third-grade reading (Leader In Me)

- **WIG**: improving % of students reading at grade level by end of school year (less specific X)
- **Lead measure (verbatim)**: "20 minutes per day, three times per week" of sustained silent reading

**Use for**: education / personal-behavior lead measures (time-on-task pattern).

### 7. Boy Scouts of America (Cub Scouting)

- **WIG**: increase Cub Scout membership from **8,355 to 8,750 by year end** + increase number of schools having boy talks from 210
- Source: Scouting org PDF

**Use for**: nonprofit / membership-growth WIG.

### 8. Marriott Hotels

- **WIG**: customer satisfaction (less specific X / Y)
- Result: rose from perpetual 2nd place to 1st place
- Source: logmi.jp transcript referencing FranklinCovey case

**Use for**: hospitality cross-reference to Opryland (same industry, same lag metric); high-level only.

### 9. Whirlpool

- **Result**: $5.7M incremental in first 90 days
- WIG details: not disclosed

**Use for**: outcome calibration only.

### 10. IT Lead Measures compilation (GitHub gist by meredian)

- **URL**: https://gist.github.com/meredian/cdb14e2ff214be0743fb3ccb400bede4
- 6 example sets of IT-context lead measures (App Support team, code refactoring, automation, incident-management %s, etc.)
- Source attribution: compiled from multiple articles

**Use for**: `4dx-d2-lead-measures` IT-context calibration; not real implementation but vetted compilation of typical IT 4DX leads.

### 11. Sales Tax Institute

- WIG / leads / scoreboard / cadence: NOT disclosed
- Only general principle: "Whether we are designing a webinar… we are always asking if this is what matters most"

**Use for**: ★ marketing-tier only; demonstrates "internalized D1 principle" voice.

---

## Tier 3 — Insufficient for case bank (★ marketing-tier only)

### 12. ノーリツ Vプラン23 (FranklinCovey JP × HRpro)

**Source**: form-gated download from `franklincovey.co.jp/?handout=noritz_casestudy`.
**Disclosure**: D1-D4 specifics absent; only context (中計 V プラン23) + Ch 8 onboarding pattern (パイロット → 階層別 Execution Design) + outcomes (118% / +285% / +4pt). Initial assessment overrated; reverted as case-bank source 2026-05-01 (see [memory note](file:///Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/feedback_marketing_cases_lack_d1_d4_specifics.md)).

**Use for**: JP-context vocabulary calibration only (中計 / 方針展開 / 営業統括 / 挑戦する風土); Ch 8 onboarding pattern reference. NOT for D1-D4 audit-mode case banks.

### 13. マルハン (FranklinCovey JP)

- Marketing summary only: "マルハンイズム浸透"
- D1-D4 not disclosed

### 14. 公益社 (FranklinCovey JP)

- Marketing summary only: "サービス品質向上 + 風土変革"
- 7 つの習慣 + 4DX 同時導入
- D1-D4 not disclosed

### 15. アスクレップ (FranklinCovey JP)

- Original PDF redirect to FCE-publishing 301; no longer accessible
- Was tagged "戦略実行リーダー育成"

### 16. 日本 NCH (FranklinCovey JP)

- Mention only; no detail page exists

### 17. Hashimoto note article (note.com)

- Author's team uses 4DX = OKR KR equivalence
- Actual WIG / leads / scoreboard NOT quoted
- Cadence: Mon 10:30-11:00 (good 30-min discipline)
- Author admits: "可視性の強化はおサボりさせてもらい、スプレッドシートをスコアボード代わりにしていました" (used spreadsheet as scoreboard shortcut)

**Use for**: JP small-team-implementation voice; not for case bank.

### 18. room8.co.jp practical guide

- Generic illustrations only ("月間売上 800万→1,000万"); not real Room8 case

---

## Tier 4 — Specialized / educational (worth keeping context, NOT case-bank material)

### Abdhi Famili General Hospital (Indonesia)

- Academic paper, but extraction failed (full PDF in Bahasa Indonesia)
- Outcome: significant association between 4DX implementation and patient satisfaction (p < 0.05)
- Operational details inaccessible without full PDF translation

### United Animal Health U-4DX Playbook

- Internal playbook PDF (40+ pages)
- WebFetch couldn't render text via standard extraction
- Use Read tool's PDF support if needed in future

### FranklinCovey video case studies

- Multiple short videos referenced (Marriott, Opryland video, etc.)
- Not transcribed publicly; would require manual transcription

---

## Decision rubric: when to use which tier

**For audit-mode-examples.md case banks** (agent runtime): only Tier 1 (★★★ full) cases qualify. Tier 2 is acceptable as supplementary anti-pattern reference but should not be the primary anchor.

**For boundary references / Don't-confuse-with neighbours** (agent runtime): Tier 2-3 are fine as one-line callouts.

**For human authoring decisions**: this whole inventory is the source of truth.

**For trigger-language calibration in description / activation**: Tier 3 JP cases provide vocabulary even though they fail as case-bank anchors (中計 / 方針展開 / 挑戦する風土 vocabulary already injected into v0.8.1 trigger phrases).

---

## Open questions for future research

1. **Are there more CFR PDFs?** Opryland is one; FranklinCovey CFR has produced multiple. Searching for "Center for Advanced Research" + "FranklinCovey" + case studies should surface more.
2. **Book PDF / paid ed?** The 4DX 2nd ed. has anchor cases (Younkers / Sydney accounting / others) inline. Already partially captured in skill bodies. A complete extraction would close the loop.
3. **Anonymized real client cases?** The user (kouko) running 4DX themselves and accumulating case data over time would produce the highest-value cases but doesn't exist yet.
4. **JP-context Tier 1?** No JP case currently meets ★★★ disclosure. If FranklinCovey JP ever publishes a CFR-style research PDF for a JP client, that would be the highest-value addition.

---

## Provenance note

This inventory was assembled 2026-05-01 from:
- 5 web searches across EN + JP keyword sets
- 8 WebFetch deep-dives into specific case URLs
- Cross-validation of cases mentioned in multiple sources
- Reading 1 PDF (Opryland CFR) for verbatim quotes
- 1 reverted experiment with the ノーリツ case (see memory note)

Total research time: ~1 session. Re-running this inventory annually is sensible if case-bank sourcing becomes active work.
