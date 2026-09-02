# Non-monetary KPI carrier map — where operational KPIs actually live (1995–2025)

Distilled from the 2026-07-19 8-K-earnings-KPI-intake recon (volatile scratchpad
→ repo-permanent). Two evidence bases: a **71-filer RAW XBRL non-monetary fact
census** (six sector slices, edgartools 5.42.0, latest 10-K + 10-Q per filer) and
an **88-filer × 11-vintage carrier-map study** (SEC submissions full-history index
+ 8 companies read filing-by-filing + a cited regulatory timeline). Every example
value below carries the accession it was read from; nothing here is guessed — where
the recon recorded no per-fact accession the row says "see route-a-census*.md".

> **Canonical test-filer list lives elsewhere.** The "12-ticker validation set"
> referenced across the JNJ arc handoff and `docs/loom/BACKLOG.md` was a
> machine-local scratchpad, **never committed** (`route-a-census.md` §caveat). The
> committed, live-verified sampling universe of record is
> **`docs/loom/references/xbrl-verification-universe.md`** — use that file, not any
> uncommitted "12-ticker" mention, when a KPI probe needs a filer roster.

**One-line verdict.** The home of an operational KPI was never XBRL — it is the
**contemporaneous earnings-release carrier**: pre-2003 in the 10-K body (press
releases were not filed with the SEC at all), from 2004 the free-text **8-K EX-99
exhibit** (never structured in 22 years), with XBRL only sparsely capturing a
narrow **physical-footprint / capacity cluster** after 2011. Route A ("XBRL
non-monetary KPI extraction") is **not viable as a general mechanism**; Route B
(8-K table intake) owns the operational-KPI surface.

**Status legend:** ✅ genuine, recurring, cross-filer usable · ⚠️ real but
filer-scoped or needs a value-sanity gate · ❌ trap / absent-from-XBRL.

---

## (a) 71-filer XBRL non-monetary census — verdict + physical-footprint/capacity cluster

**Census scope.** 71 filers across six slices (12 tech-heavy + 12 financials/REIT
+ 10 consumer + 9 healthcare + 15 energy/utility/materials/industrial + 13
tech/semis/SaaS/fintech), each censused on its latest 10-K **and** latest 10-Q via
the RAW `filing.xbrl().facts.to_dataframe()`, filtering to facts whose `currency`
column is null — the exact inverse of the shipped `_is_currency_amount_fact` gate
(`sec_edgar_client.py` ~:1971). All 71 resolved, zero skips.

**Verdict.** Across every slice, **well under 1% of non-currency facts are a
genuine, quantifiable, recurring operational KPI** (0.13% in the healthcare slice,
the strongest a-priori hypothesis, which came back nearly empty on device
installed-base / procedure counts). The standard-taxonomy majority (~85–90% by
volume) is administrative: `dei:` cover-page metadata, `cyd`/`ecd` disclosure
flags, EPS share counts, tax-rate reconciliation ratios. The concrete KPIs the
arc was framed around — subscriber counts, unit/production volumes, headcount,
active accounts, TPV, wafer capacity, da Vinci installed base — are **absent from
XBRL entirely** for the large majority of filers; they live in prose or 8-K
exhibits. Two families survive scrutiny: a low-signal universal (segment count,
below) and a narrow **physical-footprint / capacity cluster**.

**Segment-count family (universal but structural).** `us-gaap:NumberOfReportable
Segments` / `us-gaap:NumberOfOperatingSegments` recur near-universally — 19/22
across the original+consumer slices, **9/9** healthcare, **13/13** tech-extension —
a bare integer (1–6) under filer-dialect units (`segment` / `U_Segment` /
`reportable_segment` / even KO's typo `segement`). Allowlist-able (stable standard
QName, correct integer semantics) but a structural reporting fact that rarely
moves quarter-over-quarter, not an investor-tracked operational quantity.

**Physical-footprint / capacity cluster** (the one genuine operational family;
standard concept where noted, else filer extension). Copy values exactly:

| Concept (QName) | NS | Filer | Value(s) & movement | Period / accession | Dimension / note |
|---|---|---|---|---|---|
| `us-gaap:NumberOfStores` | std | COST | 914 → 928 warehouses | 914 @ 2025-08-31 10-K `0000909832-25-000101`; 928 @ 10-Q `0000909832-26-000051` | `srt:StatementGeographicalAxis`, `country:` ISO members (US 629→637, CA 110→115, MX 42, JP 37, GB 29, KR 20, AU 15, TW 14, CN 7, ES 5, FR 2, SE 2, IS 1, NZ 1) |
| `us-gaap:NumberOfStores` | std | CVS | 9,000 stores | @ 2025-12-31 10-K `0000064803-26-000010`; @ 2026-03-31 10-Q `0000064803-26-000052` | `us-gaap:StatementBusinessSegmentsAxis` = `cvs:PharmacyAndConsumerHealthSegmentMember`, unit `store` |
| `us-gaap:NumberOfStores` | std | SBUX | ❌ 113 (TRAP — sub-brand, not total) | @ 2024-10-14 10-K `0000829224-25-000114` | see traps §(c); real ~40,000 total untagged |
| `us-gaap:NumberOfRestaurants` | std | MCD | 45,356 → 45,699 total | 45,356 @ 2025-12-31 10-K `0000063908-26-000035`; 45,699 @ 2026-03-31 10-Q `0000063908-26-000051` | undim total; split franchised 43,672 / company-operated 2,027 via `us-gaap:FranchisorDisclosureAxis`. Best-quality example in either census |
| `us-gaap:NumberOfRealEstateProperties` | std | O | 15,511 → 15,571 | 15,511 @ 2025-12-31 10-K `0000726728-26-000011`; 15,571 @ 2026-03-31 10-Q `0000726728-26-000030` | undimensioned company-wide total (clean, O-shape) |
| `us-gaap:NumberOfRealEstateProperties` | std | PLD | 2,480 (dim-sum only) | @ 2025-12-31 10-K `0001193125-26-051453` | **never undimensioned**; sum geo slice US 784 + OtherAmericas 393 + Europe 1058 + Asia 245 |
| `us-gaap:AreaOfRealEstateProperty` | std | O | 355,000,000 sqft | @ 2025-12-31 10-K only `0000726728-26-000011` | undim; not repeated in 10-Q |
| `us-gaap:AreaOfRealEstateProperty` | std | PLD | 647,904,000 sqft | @ 2025-12-31 10-K `0001193125-26-051453` | buildings-in-service (dimensioned) |
| `cvs:NumberOfWalkInMedicalClinics` | ext | CVS | 1,000 clinics | @ 2025-12-31 10-K `0000064803-26-000010`; @ 2026-03-31 10-Q `0000064803-26-000052` | `us-gaap:StatementBusinessSegmentsAxis` = `cvs:HealthServicesSegmentMember`, unit `clinic` |
| `cvs:NumberOfPharmacyPlanMembers` | ext | CVS | 87,000,000 → 88,000,000 | @ 2025-12-31 10-K `0000064803-26-000010`; @ 2026-03-31 10-Q `0000064803-26-000052` | unit `people`; the membership KPI the arc hunted for — but CVS-only (UNH/CI don't tag it) |
| `amt:LeasedAssetsNumberOfSites` | ext | AMT | 11,100 sites | @ 2025-12-31 10-K `0001053507-26-000035` | `srt:CounterpartyNameAxis`; tower-REIT bespoke, no standard backing |
| `amt:PropertyPlantAndEquipmentAdditionsDuringNoncashTransactionNumberOfTowers` | ext | AMT | 575 towers | period 2024-12-31, 10-K `0001053507-26-000035` | — |
| `us-gaap:ShortdurationInsuranceContractsNumberOfReportedClaims` | std | PGR / TRV / MET | PGR 885,914; TRV 21,090; MET ❌ 3,360→308,345,000,000 (TRAP) | PGR 10-K `0000080661-26-000086`; TRV 10-K `0000086312-26-000065`; MET 10-K `0001099219-26-000013` | `srt:ProductOrServiceAxis`; MET corruption → §(c) |
| `ci:ShortdurationInsuranceContractsNumberOfPaidClaims` | ext | CI | 5,300,000 (2024) → 4,900,000 (2025), a YoY decrease | 10-K `0001739940-26-000006` | `us-gaap:StatementBusinessSegmentsAxis` = `ci:CignaHealthcareMember`; ASU 2018-12-shaped, may generalize across insurers |
| utility nameplate capacity (MW) | ext | SO / NEE / DUK | SO `PublicUtilitiesApprovedAdditionalGeneratingCapacity`=9,885 MW (Georgia Power); NEE `WindElectricGeneratingFacilityCapability`=11,689 MW; DUK `PublicUtilitiesSolarGenerationCapacityPlantsInMegawatts`=749 MW | SO 10-K `0000092122-26-000006`; NEE 10-K `0000753308-26-000015`; DUK 10-K `0001326160-26-000014` (per-fact accession not stamped — see route-a-census-ext-industrial.md §3) | CAPACITY not output; MWh generated is NOT tagged (only hedge-notional) |
| BA program unit counts | ext | BA | `ServicesProbableOfBeingExercisedNumberOfAircrafts`=342; `NumberOfLowRateInitialProductionLot`=12; `NumberOfGenerationAerialRefuelingTanker`=4 | BA 10-K `0001628280-26-004357` (see route-a-census-ext-industrial.md §3) | `ba:ProgramAxis` (T-7A/KC-46A/MQ-25/VC-25B); NOT the headline total-delivered KPI (prose-only) |
| `NumberOfMiningOperations` / `ProvisionalSalesOutstandingUnits` | std/ext | NEM | 12 mining ops; 9M oz silver / 105M lb zinc | NEM 10-K `0001164727-26-000010` (see route-a-census-ext-industrial.md §3) | `srt:ProductOrServiceAxis`; gold ounces produced NOT tagged |
| `intc:NumberOfNewFactories` | ext | INTC | 2 | @ 2025-12-27 10-K `0000050863-26-000011` | `srt:ConsolidatedEntitiesAxis` = Arizona SCIP JV (entity-scoped, not company-wide) |

Cross-filer strength of the store/property family: **COST + MCD + CVS + O** carry
a clean, standard-concept, period-over-period-comparable location count (PLD
usable via dimension-sum); **SBUX carries the standard name but a trap value**;
**NKE, HD (~2,300 stores), WMT (~10,500 stores) tag nothing** despite huge physical
footprints. So even in retail the family is a per-filer-verified allowlist, never a
general "retail location-count extractor."

---

## (b) Carrier-map era table + regulatory timeline

Method: SEC EDGAR submissions API full-history index (88 filers, four parallel
batches) + 8 representative companies read filing-by-filing across 11 vintages
(1995, 1998, 2001, 2004, 2007, 2010, 2013, 2016, 2019, 2022, 2025) + a cited
EN/JA regulatory-timeline study.

**Regulatory timeline (6 claims — 5 confirmed, 1 refined; citations below).**

| Breakpoint | Event | Meaning for KPI location |
|---|---|---|
| 1993–1996/5 | EDGAR electronic filing phased-in mandate (Reg S-T) | 1995 sample: some filers still in paper transition |
| 2000/10 | Reg FD effective | forces broadcast disclosure (press wire) but still **not into SEC** |
| **2003/3/28** | Release 33-8176: earnings press release must be **furnished on 8-K** (then Item 12) | **KPI first becomes a SEC document** |
| 2004/8/23 | Release 33-8400: Item 12 → **renumbered 2.02**, deadline 5→4 business days | 8-K item machine-readable from here |
| 2009–2011 | XBRL phased-in mandate (financial statements + notes) | **EX-99 press release never in scope** (furnished-not-filed) |
| 2019–2021 | Inline XBRL | cover/statement tagging deepens; EX-99 still free text |
| (Japan contrast) 2008 | TSE mandates 決算短信 XBRL (TDnet) | Japan structured the **carrier itself**; the US never did — EX-99 is never XBRL-tagged |

Citations: SEC rulemaking history (EDGAR / Reg S-T); Reg FD release; Fed. Register
33-8176; 33-8400 final rule; Dorsey XBRL memo; sec-api.io EX-99 notes; JPX XBRL
沿革; FSA 決算短信 変遷 materials.

**8-K coverage cliff.** 88 filers with an earnings 8-K by vintage: 1995–2001 = **0**;
2004 = **52** (Item 12/2.02 mandate); then 54 / 56 / 58 / 59 / 62 / 64 / **65** in
2025. Post-2004 the shortfall from 88 is entirely "not yet public" (META/TSLA/SNOW/
PLTR/BX/NU…) or ADR (11 filers on the 6-K regime, zero 8-K all-history). Once the
mandate binds, **coverage of listed US filers is complete, no exception**.

**Era table — 8 representative companies read filing-by-filing.**

| Company (KPI) | 1995–2001 | 2004–2016 | 2019–2025 | XBRL |
|---|---|---|---|---|
| MCD (restaurant count) | 10-K | 8-K **EX-99.2 dedicated supplement** (from 2001) | same, continuous | from FY2011 |
| COST (warehouse / member count) | 10-K405 table | warehouse → 8-K EX-99.1; **member count stays in 10-K** | from 2025 both in new EX-99.2 | warehouse FY2016+; members never |
| UNH (medical member count) | 1995 in 8-K table; 1998–2004 back to 10-K/EX-13 | 8-K EX-99.1 "Customer Profile" table (from 2007) | 2025 moves to EX-99.2 stat supplement | never |
| WMT (store count) | 10-K | 8-K headline total (2010–2016) | **8-K degrades to round-number marketing; precise count withdrawn to 10-K Properties** | never |
| XOM (production) | 10-K prose (liquids/gas split) | 8-K EX-99.1 oil-equivalent koebd headline (from 2004) | same | never |
| BA (deliveries) | 10-K by-model table | 8-K EX-99.1 by-model table (from 2004) | same (30-yr structure unchanged) | partial (program axis) |
| AAPL (unit sales) | 10-K prose (1995 % only) | 8-K EX-99.1 → later EX-99.2 summary only | **stops disclosing from FY2019** (FY2018 10-K = last unit-sales table) | never |
| NFLX (subscriber count) | pre-IPO (2002) | 8-K press release → FY2010 shareholder-letter narrative | **stops reporting 2025/1** (8-K `0001065280-25-000033`: milestones only) | never |

**Cross-cutting rules.** Carrier migration is universal and **not monotonic**
(all 8 migrated 10-K→8-K in 2001–2007; WMT went 8-K→back to 10-K; COST/UNH added a
2025 EX-99.2 supplement); the **EX-99.2 "statistical supplement" is an
under-appreciated rich vein** (MCD/UNH/COST) that hits the 8-K extractor's current
≥2-exhibit `LOOM-SIMPLIFY` ceiling; **KPIs die** (AAPL FY2019, NFLX 2025 — same
issuer stops disclosing); the historical floor is 2003/3 (pre-that is a 10-K-prose
extraction problem, a separate arc).

---

## (c) Traps registry

| Trap | Instance(s) | Guard |
|---|---|---|
| **Decoy CIK** (ticker→CIK resolves to a new holding shell / subsidiary / successor, not the operating history) | XOM: use **34088**, not ticker-decoy **2115436** (2026 holding shell); BLK: use **1364742**, not **2012383** (2024 holding); BA: use operating **12927**, not leasing-subsidiary decoy **711513**; GOOGL: history under predecessor **1288776**, current-ticker **1652044** (Alphabet, 2015 reorg) truncates it; ORCL: history under predecessor **777676**, current-ticker **1341439** (2005 reincorp) truncates it | verify CIK continuity before any historical pull; record the discontinuity, **do not stitch across it** |
| **Sub-brand impersonates total** | SBUX `us-gaap:NumberOfStores`=**113** — only the "23.5 Degrees" acquisition sub-brand (matches `sbux:NumberOfStores23.5Degrees`=113); SBUX's real ~40,000 total is untagged | read the **dimensioned value** + cross-check the matching extension concept before allowlist promotion — never trust the standard QName alone |
| **Filer XBRL corruption** | MET `us-gaap:ShortdurationInsuranceContractsNumberOfReportedClaims` ranges **3,360 → 308,345,000,000** ("308B claims") within one filing `0001099219-26-000013`, same `us-gaap:GroupPoliciesMember` member — dollar/scaled subtotals mistagged under a claims-count concept | per-filer **value-sanity range gate**; a correctly-and-consistently-named QName is still not value-trustworthy |
| **Hedge-notional shares production units** | `us-gaap:DerivativeNonmonetaryNotionalAmountVolume` / `…EnergyMeasure` in bbl/bcf/mcf/mmbtu/mwh — **7 of 15** energy/utility filers (XOM, CVX, COP, NEE, DUK, SO, DOW); e.g. AMZN 200,000,000 `mwh` (`0001018724-26-000004`) | explicit **QName denylist**, not a unit-string heuristic — the same unit (`bbl`, `mwh`) serves both the hedge trap and real production, so unit alone cannot distinguish them |
| **Vesting milestone impersonates operating count** | TSLA `…OperationalMilestoneNumberOfDeliveredVehicles`=**20,000,000** — a share-based-comp **vesting threshold**, not cumulative deliveries (`0001628280-26-026673`) | read the **full QName** (`ShareBasedCompensationArrangement…NumberOfDeliveredVehicles`) |
| **2004-pre 8-K item undecidable** | all filers before Item 12/2.02 (items field empty / old numbering) | accept a **structural unknown**, do not guess whether an early 8-K is an earnings furnish |

Supporting note: **unit strings are open per-filer dialects** (`number`/`U_pure`/
`pure`; `segment`/`U_Segment`/`reportable_segment`; KO's typo `segement`) — any
classifier must key on the **concept QName**, never the unit string. This is
load-bearing for the hedge-notional denylist above.

---

## (d) Canonical test-filer list

The committed, live-verified filer universe of record for all KPI/XBRL probes is:

**`docs/loom/references/xbrl-verification-universe.md`**

The "12-ticker validation set" mentioned in the JNJ arc handoff, the
`12-ticker-validation-2.25.0.md` scratchpad, and `docs/loom/BACKLOG.md` was a
machine-local file **never committed to the repo** (`route-a-census.md` §caveat: a
grep across `docs/loom/`, `.claude/handoffs/`, and `investing-toolkit/tests/`
surfaced only scattered mentions — JNJ, INTC, AAPL, NVDA, COST, GOOGL, NFLX, MSFT,
AMZN, TSLA, ORCL — never a checked-in list). This section closes that gap: cite the
committed universe file, not any uncommitted "12-ticker" reference.

---

## (e) Durable store path — host research verdict (2026-07-19)

**Question.** Where can a skill durably persist a KPI store (e.g. an accumulated
8-K-intake KPI cache) such that the path is stable across reinstalls and works on
both Claude Code and Codex?

**Finding — neither host documents a skill-reachable durable-data directory:**

- **Claude Code `CLAUDE_PLUGIN_DATA`** is (i) **textual-substitution-only** for
  skill bodies — it is not a real environment variable a skill's bash sees (it
  expands to empty in a skill shell), (ii) **hook-only** for env-var access, and
  (iii) **splits per `{plugin}-{marketplace}`** on reinstall, so the path is not
  stable across a marketplace change. (Corroborated by repo memory:
  `feedback_claude_plugin_data_hook_only_or_default_bypass.md`,
  `feedback_claude_skill_dir_textual_substitution_not_env.md`.)
- **Codex `PLUGIN_DATA`** is **hook-only**, its path is **undocumented**, and it
  carries an **open interpolation bug (openai/codex#19582)**. Codex additionally
  **ignores XDG base-dir conventions (openai/codex#1980)**.

**Verdict.** A **host-neutral ladder** is the only cross-host-safe choice:

```
KPI_STORE_DIR  →  $XDG_DATA_HOME/investing-toolkit/kpi-store
               →  ~/.local/share/investing-toolkit/kpi-store
```

i.e. honor an explicit `KPI_STORE_DIR` override, else `$XDG_DATA_HOME`, else the
`~/.local/share/…` default. This matches uv's cache-dir-vs-data-dir precedent and
depends on neither host's plugin-data mechanism.

**Reversal condition.** Revisit this decision **iff** `PLUGIN_DATA` extends to
skill *script* invocations on **both** hosts **AND** openai/codex#19582 closes —
only then does a host-native plugin-data path become a safe primary.

---

## Provenance

- **XBRL non-monetary census (a, c):** 71 filers, edgartools 5.42.0,
  `set_identity(...)`, latest 10-K + 10-Q per filer via
  `filing.xbrl().facts.to_dataframe()`, non-currency = `currency` null (inverse of
  `_is_currency_amount_fact`, `sec_edgar_client.py` ~:1971). Six slices:
  `route-a-census.md` (12 tech/mega-cap), `route-a-census-ext-financials.md` (12
  banks/insurers/asset-mgrs/REITs), `route-a-census-ext-consumer.md` (10 retail/
  staples), `route-a-census-ext-healthcare.md` (9 pharma/medtech/managed-care),
  `route-a-census-ext-industrial.md` (15 energy/utility/materials/industrial),
  `route-a-census-ext-tech.md` (13 semis/SaaS/fintech). All 71 resolved, zero
  skips. Raw dumps: `route-a-census*.json`.
- **Carrier-map study (b):** `kpi-carrier-map-1995-2025.md` — 88-filer SEC
  submissions full-history index (four parallel batches) + 8 companies read
  filing-by-filing across 11 vintages (88/88 company-years verified) + EN/JA
  regulatory-timeline research. Matrix: `kpi-8k-matrix-88.csv`; spot-check evidence
  with accessions: `kpi-era-spotcheck-{a,b}.md`.
- **Host research (e):** 2026-07-19, cross-referenced against repo auto-memory
  feedback entries + openai/codex#19582 / #1980.
- Source artifacts were volatile scratchpad files; this doc is the repo-permanent
  distillation. Per-fact accessions transcribed exactly; rows without a per-fact
  accession in the recon cite the section (see route-a-census*.md) instead of
  inventing one.
