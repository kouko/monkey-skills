# macro-regime-snapshot Recalibration Protocol

**Purpose**: specify **when and how** to re-verify the per-country
threshold files (`thresholds-{us,japan,taiwan,korea,china}.md`)
against primary sources. Macro regime thresholds drift with each
policy cycle — a static threshold file becomes stale within ~12-18
months without active maintenance.

This protocol inherits the spirit of `domain-teams` grounding
practice (see `domain-teams/skills/skill-team/protocols/grounding-research.md`)
adapted for investing-toolkit's data/aggregation layer.

---

## Recalibration Triggers

Run a **partial** or **full** recalibration when any of the following
events occur:

### Mandatory (MUST recalibrate)

| Event | Scope | Max latency |
|-------|-------|-------------|
| FOMC updates SEP long-run dot plot (quarterly, Mar/Jun/Sep/Dec) | US only | 30 days |
| NY Fed publishes new HLW vintage (typically 1×/year Q1) | US only | 30 days |
| BOJ 展望レポート released (quarterly, Jan/Apr/Jul/Oct) | JP only | 30 days |
| BOK 경제전망보고서 released (semi-annual, Feb/Aug) | KR only | 30 days |
| 国务院 政府工作报告 released (annually, early March) | CN only | 30 days |
| 中央銀行 CBC 理監事聯席會議 (quarterly policy statement) | TW only | 30 days |
| Policy-rate change outside forecasted path | Affected country | 14 days |
| Major regime shift (ZLB entry/exit, YCC adoption/end, target change) | Affected country | 30 days |

### Recommended (SHOULD recalibrate)

| Event | Scope | Max latency |
|-------|-------|-------------|
| Annual review (every 2026-Q1 onwards) | All 5 countries | 90 days |
| Academic r* working paper from major central bank | Affected country | 60 days |
| CBO Budget & Economic Outlook update | US only | 60 days |
| Significant CPI print surprise (±50 bp from consensus) | Affected country | 30 days |
| Large unemployment-rate regime break (±1 pp in 3 months) | Affected country | 30 days |

### Optional (MAY recalibrate)

| Event | Scope | Max latency |
|-------|-------|-------------|
| Index-composition change (e.g. TSMC weight crosses 45% of TAIEX) | Affected country | Next quarter |
| Sector-tilt framework revision (post-regime-change learning) | Affected country | Next quarter |

---

## Recalibration Procedure

### For a single country (partial recalibration)

1. **Open** the relevant `thresholds-{country}.md` file.
2. **Identify** the claims affected by the triggering event
   (e.g., FOMC SEP → only the "Policy Rate Neutrality" section;
   BOJ 展望 → only "Inflation Target" + "Policy Rate Neutrality").
3. **Fetch primary source** (PDF / HTML) via `WebFetch` — do NOT rely
   on news / sell-side summaries for load-bearing numbers.
4. **Cross-check against** the consolidated grounding note
   `research/grounding-v1.9.0.md` (and successors). If the new value
   changes the threshold bands meaningfully (> 10% shift), document
   the change in a **Grounding Status update block** at top of the
   threshold file:

   ```
   ## Grounding Status (as of YYYY-MM-DD)
   **Last full verification**: 2026-04-18 (grounding-v1.9.0.md)
   **Last partial update**: 2026-06-20 — FOMC Jun SEP long-run dot
     revised from median 3.0% to 3.1% nominal; §"Policy Rate
     Neutrality" updated; downstream 4-tier real-rate bands
     unchanged (still 0 / 1.0 / 1.75%).
   ```

5. **Add new primary-source URL** to the file's "Primary-Source
   Verification URLs" section if it wasn't already listed.
6. **Commit** with message pattern:
   `docs(macro-regime): recalibrate thresholds-{country}.md — {trigger}`

### For all countries (full recalibration, annual)

Follow the per-country procedure for each of US / JP / TW / KR / CN in
sequence or parallel. At end:

1. **Write a new grounding note**
   `research/grounding-v{X.Y.Z}.md` (next semantic version) covering
   all 5 countries' changes since the last grounding vintage.
2. **Bump `last_full_verification_date` at top of each
   `thresholds-*.md`** to today's date.
3. **Update `investment-clock-cheatsheet.md` §"Threshold provenance"**
   if any of the r* / NAIRU sources gained new 2026+ data.
4. **Open a single PR** titled
   `docs(macro-regime): annual recalibration v{X.Y.Z}` with all 5
   threshold file updates + new grounding note + cheatsheet update.

---

## Minimum Acceptable Source Tiers

When verifying claims, enforce this authority hierarchy:

### Tier A (PREFERRED — primary authority direct publication)

- Central bank official statements, speeches, WPs, MPC minutes
- National statistics bureau direct publications
- CBO / OMB / government fiscal authorities
- Academic journal articles from the authority (e.g., NY Fed Liberty
  Street Economics from Fed economists)

### Tier B (ACCEPTABLE — established institutional cross-checks)

- IMF / BIS / OECD country assessments (Article IV, ECOS surveys)
- Major sell-side macro research with explicit source citations
- NRI / DLRI / IIE / KIEP / KIET — national policy think tanks
  (often best native-language synthesis)

### Tier C (SUPPLEMENTARY — context only, NOT load-bearing)

- General news (Bloomberg, Nikkei, CNA, 新华社) — use for
  date/context cross-reference; do not cite as single source for a
  numeric claim
- Market-data aggregators (MacroMicro, TradingEconomics, CEIC) —
  good for historical charts but must cross-verify point values
  against Tier A

### Tier D (REJECT for regime thresholds)

- Generic financial blogs / YouTube explanations
- Crowdsourced encyclopedias without citations (Wikipedia without
  traceable primary-source cites)
- Social-media threads, even from domain experts (links-to-primary
  only)

---

## Native-Language Source Priority

For each country, **primary sources in the country's native language
are preferred over English translations**:

| Country | Preferred language | Fallback |
|---------|-------------------|----------|
| US | English (n/a) | — |
| Japan | 日本語 | English translations of BOJ/内閣府 WP when available |
| Taiwan | 繁體中文 | English CBC/DGBAS summaries |
| Korea | 한국어 | English BOK/KOSTAT press releases |
| China | 简体中文 | English CEIC / IMF Article IV cross-checks |

Rationale: native-language primary sources avoid translation drift
(especially important for 自然利子率 / 潜在成長率 / 景氣燈號 /
기준금리 terminology where English translations may be imprecise).

---

## Logging Recalibration Events

Each recalibration MUST leave an audit trail:

- **Git commit** — per standard commit message pattern above
- **Grounding Status block** in the updated `thresholds-*.md` file
- **Grounding note** `research/grounding-v{X.Y.Z}.md` for
  semver-qualifying changes (≥1 country threshold meaningfully shifted)

Do NOT silently update threshold numbers without leaving a visible
trail — the whole point of this protocol is auditability across time
as the underlying r* / NAIRU / policy-target landscape evolves.

---

## Suggested Annual Cadence

| Month | Action |
|-------|--------|
| **February** | Full recalibration: incorporate Q4 FOMC SEP + CBO early-year update + NBS 经济发展 报告 + 国务院 政府工作报告 drafts |
| **April** | Partial: Q1 SEP + BOJ 展望 Q1 + PBOC Q1 货币政策委员会例会 |
| **July** | Partial: Q2 SEP + BOK 통화정책방향 mid-year + mid-year policy reviews |
| **October** | Partial: Q3 SEP + BOJ 展望 Q3 + CBC Q3 理監事 |

**Designate one person as recalibration owner** (rotates quarterly
if repo has multiple contributors, otherwise maintainer by default).
The owner ensures the per-quarter partial or full recalibration
ships on time.

---

## Escalation: When Sources Disagree

When primary sources disagree (e.g., HLW says r* = 1.42% but
Lubik-Matthes says 2.15%; or BOJ WP24-J-09 vs sell-side), DO NOT
pick one arbitrarily. Instead:

1. **Document both in the relevant threshold file** under
   "Policy Rate Neutrality" (pattern already established in
   `thresholds-us.md`).
2. **Set the working band to span both** (e.g., tier Neutral = 0 - 1.0%
   respects HLW lower + FOMC lower; tier Clearly Restrictive ≥ 1.75%
   respects LM minus term premium).
3. **Note the disagreement** in the grounding note with both citations.
4. **Revisit at next annual recalibration** — once 2-3 years of new
   data clarifies the debate, the band can tighten.

This is the spirit of the 4-tier real-rate framework: we do not claim
to know r* to bp precision. We acknowledge the genuine academic
debate and structure the thresholds to be robust across it.

---

## Cross-References

- `references/investment-clock-cheatsheet.md` § "Threshold provenance"
- `research/grounding-v1.9.0.md` — initial grounding audit trail
  (all 5 countries)
- `../../../domain-teams/skills/skill-team/protocols/grounding-research.md`
  — analogous but for domain-teams (not identical; domain-teams owns
  standards, we own calibration snapshots)
- `../../../domain-teams/skills/skill-team/standards/grounding-principle.md`
  — cold-query / parametric-tier rationale; we borrow the
  primary-source anchoring ethos
