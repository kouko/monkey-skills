# Long-Horizon Fundamental Equity Analysis — Standard Process & Deliverables

Research date: 2026-07-19. Method: `deep-research` harness (6 angles, 23 sources
fetched, 100 claims → 25 adversarially verified 3-vote, 25 confirmed / 0 refuted).
Purpose: ground the design of a source-anchored narrative+KPI evidence layer by
mapping what the professional industry actually produces at each analysis stage.

## Bottom line

The industry's long-horizon deliverable is **not a one-shot memo** — it is a
**maintained, per-company "coverage" artifact** with a stable section skeleton,
refreshed every earnings cycle. The equity-research *process* is explicitly
longitudinal: 2 of the 5 canonical analyst role-areas are ongoing (monitoring
critical factors; updating forecasts). Qualitative/non-financial capture is a
**formally dedicated phase**, run separately from quantitative modeling. This is
the industry archetype of the "long-term底稿" our arc targets.

## Process × deliverable map

| Stage | Purpose | Sources mined | Deliverable | Buy vs sell | Evidence |
|---|---|---|---|---|---|
| Screen / idea-gen | narrow universe | screeners, industry data | screening list / idea one-pager | — | thin |
| Initiation / deep DD | full thesis | 10-K, industry, competitors | **Initiating Coverage report (50–100 pp, 8-section skeleton)** | sell = external; buy = internal thesis memo (no standard structure) | strong (sell) |
| Modeling | quantify + forecast | financial history | **operating model** (3-statement + valuation, refreshed quarterly) | Canalyst automates | strong |
| Qualitative insight (dedicated) | moat / critical factors | expert calls, scuttlebutt, IR, site visits | moat analysis + proprietary-source notes | sell = Porter/Buffett moat; buy = direct interviews + site visits for soft signals | strong |
| Decision | IC ratification | all of the above | **IC memo** | buy internal (no standard structure) | named only |
| Monitoring (ongoing) | is the thesis still true | quarterly reports, 8-K, calls | **Company Update / Note** (tied to earnings + events; page-1 rating/target/recent-results + KPI graphs) | sell = maintenance coverage; buy = thesis-tracker "living doc" | strong |
| Thesis review / update | forecast refresh vs actuals | new quarter data | forecast refresh / thesis-tracker reconciliation | ongoing role-area | strong (process) |
| Exit / post-mortem | learn | — | post-mortem | — | named only |

**Sell-side 8-section skeleton (CFA Institute, strongest source):** Front
Matter / Recommendation + target price → Company/Business Description → Industry
Overview & Competitive Positioning (Porter's Five Forces + moat) → Financial
Analysis & Model (historical + forecast + earnings-quality scrutiny) → Valuation
(DCF/DDM + comps) → ESG → Risks.

## Two structural insights (most design-relevant)

1. **The process is longitudinal by doctrine.** Valentine's *Best Practices for
   Equity Research Analysts* (CFA Research Challenge text) defines 5 role-areas,
   2 of which are continuous: "identifying and MONITORING critical factors" and
   "creating and UPDATING financial forecasts." → our artifact must be **updatable
   per quarter**, not a snapshot.
2. **Qualitative capture is a first-class, separate phase.** Valentine Part 2
   "Generating Qualitative Insights" = (a) identify/monitor critical factors,
   (b) build proprietary sources, (c) interview for insights — run separately
   from quantitative modeling. → the narrative-evidence layer is legitimate as
   its own workstream, independent of the number pipeline.

## Japan divergence (time-caveated)

JP buy-side analyst owns the **full end-to-end chain** incl. post-investment
monitoring + engagement (エンゲージメント). BUT the "定性 disclosure under-used
because output must be a target price (目標株価)" finding is from a **2005–06 METI
survey**, predating 伊藤レポート 2014 / Corporate-Governance & Stewardship Codes /
人的資本開示 2023 — treat as **historical structural driver, not current fact**.
Horizon splits by role: sell-side skews short, buy-side skews long.

## Modern tooling

AlphaSense/Canalyst automate the operating-model layer via a library of ~4,500
drivable KPI-driver models, and unify structured financials + qualitative content
(transcripts/research/filings) in one queryable interface — the commercial version
of what our arc builds. (Vendor-marketing source; descriptive capability only.)

## Honest gaps = our spec's design decisions

Verification could NOT establish (surviving claims too thin / no source):
1. **Concrete section structure of the buy-side internal deliverables** (thesis
   memo / IC memo / tearsheet / thesis-tracker / post-mortem). "No surviving
   source specifies their sections" — the exact gap our design must fill.
2. **How many years of history** the maintained artifacts span. This deep run did
   NOT re-confirm the 10yr / 15–20yr norm (an earlier lighter pass found the 10yr
   full-cycle norm via Nomura AM + Shiller CAPE — treat as a **parameter to set**,
   not established fact).
3. **The concrete quarterly UPDATE mechanic** (how the model/tracker is refreshed
   and reconciled vs actuals each cycle).

## Design implications for our arc

- Output target = a **maintained per-company coverage file** (stable skeleton +
  quarterly refresh), two layers: quantitative (our shipped quarterly XBRL KPI
  series = operating-model seed) + qualitative (new narrative-evidence layer:
  moat / management commentary / critical factors, source-anchored).
- Memo and a future tearsheet are **readers** of that file, not the file itself.
- The 3 gaps above are the spec fan-out's design questions (coverage-file schema,
  capture taxonomy, retention-years parameter, quarterly-update mechanic).

## Sources

Primary: [CFA — Equity Research Report Essentials](https://www.cfainstitute.org/sites/default/files/-/media/documents/support/research-challenge/challenge/rc-equity-research-report-essentials.pdf) ·
[CFA — Valentine, Best Practices for Equity Research Analysts](https://www.cfainstitute.org/sites/default/files/-/media/documents/support/research-challenge/challenge/best-practices-equity-sample.pdf).
Secondary: [CFI](https://corporatefinanceinstitute.com/resources/valuation/equity-research-report/) ·
[AnalystPrep](https://analystprep.com/cfa-level-1-exam/equity/elements-of-company-research-report/) ·
[M&I](https://mergersandinquisitions.com/equity-research-report/) ·
[WallStreetPrep](https://www.wallstreetprep.com/knowledge/sample-equity-research-report/) ·
[Sleep Well Investments — thesis tracker](https://www.sleepwellinvestments.com/p/thesis-tracker).
JP: [Asset Management One](https://www.am-one.co.jp/warashibe/article/chiehako-20190621-1.html) ·
[METI intellectual-assets ch3](https://www.meti.go.jp/policy/intellectual_assets/pdf/shitenn/ch3.pdf) ·
[JAC buy-side analyst](https://www.jac-recruitment.jp/market/knowhow/resume/buy-side-investment-analyst-resume/).
Tooling: [AlphaSense](https://www.alpha-sense.com/press/alphasense-innovations-in-end-to-end-ai-workflows/).
