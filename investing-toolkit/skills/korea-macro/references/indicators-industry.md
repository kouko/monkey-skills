# Industry / 산업 (Monthly Sector Activity)

Monthly sector-activity indicators from Statistics Korea (통계청) published
jointly with BOK in the **산업활동동향** (Industrial Activity Trends) report.
Served via BOK ECOS KEYSTAT. This is the **monthly activity layer** —
distinct from the `growth` group which tracks quarterly GDP expenditure
components (private consumption, equipment/construction investment).

These series collectively describe month-to-month sector pulse:
manufacturing (production/inventory/shipment/operating rate),
services, retail/wholesale, credit card usage, machinery orders,
capital goods output, and construction (completion/orders).

**Cross-market parity**:
- JP japan-macro `activity` group: IPI / inventory / shipment / operating-rate
- TW taiwan-macro: 工業生產 / 商業營業額
- CN china-macro: `industrial-yoy` / `retail-yoy` / `services-production-yoy`
- KR (this group): 11 presets covering the equivalent span

---

## manufacturing-inventory: 제조업 재고지수 / Manufacturing Inventory Index

- **Series code**: K202 (ECOS-KEYSTAT)
- **Source**: Statistics Korea (통계청) via BOK ECOS
- **Unit**: Index (2020 = 100), seasonally adjusted
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after month-end
- **History**: From 2000

**What it measures**: Month-end stocks of finished goods held by
manufacturing firms. Combined with the shipment index, it gives the
inventory-to-shipment ratio — a classic mid-cycle indicator.

**How to interpret**:
- Rising inventory + flat/falling shipment → demand weakening,
  firms about to cut production → recession warning.
- Falling inventory + rising shipment → demand firming, early-cycle
  restocking → production recovery imminent.

**Market significance**: ⭐⭐⭐ — a leading signal for manufacturing KOSPI
names (semi, auto, steel, chem). Inventory overhangs in semis have
historically preceded KOSPI drawdowns.

**When to use**: pair with `manufacturing-shipment` to form the
inventory-to-shipment ratio; combine with `manufacturing` (K201)
production index for full activity cycle.

---

## manufacturing-shipment: 제조업 출하지수 / Manufacturing Shipment Index

- **Series code**: K203 (ECOS-KEYSTAT)
- **Unit**: Index (2020 = 100), seasonally adjusted
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after month-end
- **History**: From 2000

**What it measures**: Physical volume of factory shipments — i.e. what
manufacturers sold (ex-warehouse) during the month. Paired with
production and inventory to identify demand/supply imbalance.

**How to interpret**:
- Shipment > production → drawing down inventory → demand strong
  relative to supply.
- Shipment < production → inventory building → demand softening.

**Market significance**: ⭐⭐ — less market-moving than the production
index itself but diagnostic for whether production is demand-driven or
inventory build.

**When to use**: inventory-to-shipment ratio; consumption momentum
cross-check.

---

## manufacturing-operating-rate: 제조업 가동률지수 / Manufacturing Operating Rate Index

- **Series code**: K204 (ECOS-KEYSTAT)
- **Unit**: Index (2020 = 100), seasonally adjusted
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after month-end
- **History**: From 2000

**What it measures**: Share of manufacturing capacity actively producing
(as an index rebased to 2020 = 100; the official absolute rate is
separately published). Indicates demand pressure relative to installed
capacity.

**How to interpret**:
- Rising → demand pressing against capacity → pricing power, capex
  upcycle → positive for capital-goods sector.
- Falling below 100 for extended periods → excess capacity, capex
  downcycle.

**Market significance**: ⭐⭐⭐ for capex/machinery/semi capex-sensitive
names. Korea's chip cycle and operating rate are tightly correlated.

**When to use**: chip-capex timing, industrial allocation (machinery,
construction equipment).

---

## services-production: 서비스업 생산지수 / Services Production Index

- **Series code**: K205 (ECOS-KEYSTAT)
- **Unit**: Index (2020 = 100), seasonally adjusted
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after month-end
- **History**: From 2000

**What it measures**: Aggregate output of the services sector (wholesale,
retail, transportation, accommodation, finance, real estate, business
services, education, healthcare, arts). Services = ~60% of Korea GDP;
this is the monthly counterpart to services contribution in quarterly
GDP.

**How to interpret**:
- Diverging from manufacturing index → tells you whether the cycle is
  domestic-demand-led (services leading) or export-led (manufacturing
  leading).
- Combined with `manufacturing` (K201) for full industry production
  picture.

**Market significance**: ⭐⭐⭐ — cross-reference to test whether a
manufacturing slowdown is localised to goods or bleeding into services.

**When to use**: domestic-demand monitor; REIT / retail / consumer
discretionary sector context.

---

## retail-sales: 소매판매액지수 / Retail Sales Index

- **Series code**: K206 (ECOS-KEYSTAT)
- **Unit**: Index (2020 = 100), seasonally adjusted
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after month-end
- **History**: From 2000

**What it measures**: Total retail sales volume across department stores,
specialty stores, supermarkets, convenience stores, online channels.
The monthly proxy for household consumption (whose quarterly
counterpart is `private-consumption` K259).

**How to interpret**:
- Sustained rise → household consumption robust → positive for retail,
  consumer discretionary, credit card issuers.
- Flat/falling despite wage growth → savings rate rising or debt
  deleveraging cycle.

**Market significance**: ⭐⭐⭐ for consumer-facing KOSPI names
(Hyundai Dept, Lotte Shopping, Emart, Coupang-linked).

**When to use**: consumer-sector allocation; cross-check with
`consumer-sentiment` (K252) for survey vs. hard-data divergence.

---

## wholesale-retail: 도매 및 소매업 생산 / Wholesale & Retail Production

- **Series code**: K207 (ECOS-KEYSTAT)
- **Unit**: Index (2020 = 100), seasonally adjusted
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after month-end
- **History**: From 2000

**What it measures**: Sub-component of services production covering
wholesale + retail trade specifically. More stable than `retail-sales`
because it includes wholesale channels that smooth out consumer-level
volatility.

**How to interpret**:
- Leading signal for retail margins — if wholesale is strong and retail
  weak, inventory is building at the retail layer.
- Use as a confirmation lens for `retail-sales`.

**Market significance**: ⭐⭐ — most analytical overlap with
`retail-sales` but adds a wholesale layer for the distribution
industry.

**When to use**: logistics, distribution, B2B retail sector context.

---

## credit-card-usage: 개인카드 이용금액 / Credit Card Individual Usage

- **Series code**: K210 (ECOS-KEYSTAT)
- **Unit**: Million KRW (nominal)
- **Frequency**: Monthly
- **Publication lag**: ~6 weeks after month-end
- **History**: From 2003

**What it measures**: Aggregate monthly credit-card transaction value by
individuals (non-corporate cards). The highest-frequency proxy for
private consumption available in ECOS-KEYSTAT.

**How to interpret**:
- YoY growth > nominal wage growth → consumption supported by credit
  expansion (watch for household-debt risk).
- Sharp MoM drops outside typical seasonals → consumer caution /
  confidence shock.

**Market significance**: ⭐⭐ — especially relevant for KB/Shinhan card
subsidiaries, consumer finance, and cyclical retail.

**When to use**: real-time consumption nowcast (runs ahead of
`retail-sales`); cross-check with `household-credit` K007 for debt
sustainability.

**Korea-specific context**: Korea has one of the world's highest
credit-card penetration rates (nearly all point-of-sale transactions
include card option), so this series is a cleaner proxy for total
retail spend than equivalent series in lower-penetration markets.

---

## machinery-orders: 국내기계수주 선박제외 / Machinery Orders (Domestic ex-Ship)

- **Series code**: K213 (ECOS-KEYSTAT)
- **Unit**: Million KRW (nominal)
- **Frequency**: Monthly
- **Publication lag**: ~6-7 weeks after month-end
- **History**: From 2000

**What it measures**: New orders received by domestic machinery
manufacturers, excluding shipbuilding (which dominates and distorts the
series). Parallels the JP 機械受注 (core machinery orders) — widely
regarded as **the leading indicator for capex** in both markets.

**How to interpret**:
- Rising orders precede machinery shipments by 3-6 months, which in
  turn precede IPI expansion → classic leading indicator chain.
- Watch for 3-month moving average to filter noise (order series are
  lumpy due to large contracts).

**Market significance**: ⭐⭐⭐ — leading signal for capital-goods
companies (Doosan, Hanwha Aerospace, Hyundai Heavy). Paired with the
CI leading index for business-cycle turning points.

**When to use**: capex cycle positioning; early-cycle allocation to
industrial machinery names.

**Why ex-ship**: Korea's shipbuilding orders are so large and lumpy
(one LNG carrier contract can shift the total) that including them
obscures the underlying machinery cycle. The ex-ship variant is the
analytically clean version.

---

## capital-goods-output: 기계설비류 생산 선박제외 / Capital Goods Output (ex-Ship)

- **Series code**: K215 (ECOS-KEYSTAT)
- **Unit**: Index (2020 = 100), seasonally adjusted
- **Frequency**: Monthly
- **Publication lag**: ~5-6 weeks after month-end
- **History**: From 2000

**What it measures**: Physical volume of capital-goods production
(machinery, equipment) ex-shipbuilding. Complements `machinery-orders`
(K213) — orders lead, output confirms.

**How to interpret**:
- Output rising after orders have risen → capex cycle is in delivery
  phase → revenue recognition window for capital-goods firms.
- Output rising without orders rising → inventory build risk.

**Market significance**: ⭐⭐ — mostly confirmatory for K213.

**When to use**: capex cycle phase identification (order vs. delivery
vs. absorption); capital-goods margin analysis.

---

## construction-completion: 건설기성액 / Construction Completion Value

- **Series code**: K216 (ECOS-KEYSTAT)
- **Unit**: Million KRW (nominal)
- **Frequency**: Monthly
- **Publication lag**: ~6-7 weeks after month-end
- **History**: From 2000

**What it measures**: Monetary value of construction work *actually
completed* during the month (i.e. progress billings). The
backward-looking counterpart to construction orders — it lags orders
by 12-18 months as construction projects move from contract to
handover.

**How to interpret**:
- Rising completion with falling orders → backlog is being drawn down
  → construction sector heading into trough phase next cycle.
- Rising completion and rising orders → mid-expansion in construction.

**Market significance**: ⭐⭐ — primary driver of realised revenue at
construction firms (GS E&C, Daewoo E&C, Samsung C&T). Matters more
for quarterly earnings than for early-cycle signals.

**When to use**: construction revenue nowcasting; cross-check against
`construction-orders` (K217) for backlog dynamics.

---

## construction-orders: 건설수주액 / Construction Orders Value

- **Series code**: K217 (ECOS-KEYSTAT)
- **Unit**: Million KRW (nominal)
- **Frequency**: Monthly
- **Publication lag**: ~6-7 weeks after month-end
- **History**: From 2000

**What it measures**: Monetary value of new construction contracts
signed during the month. Breakdown by private/public and building/civil
is available on the ECOS site for deeper analysis.

**How to interpret**:
- Leading indicator for construction output (K216) by 12-18 months.
- A sharp drop in orders → expect `construction-completion` to decline
  ~1 year later → E&C margin compression.

**Market significance**: ⭐⭐⭐ — the **earliest** construction-sector
leading indicator available monthly. Particularly important for
housing market (apartment pre-sale) analysis and E&C equity cycle
timing.

**When to use**: housing/real-estate allocation; cross-check with
`housing-price` (K407) for supply-demand framing; E&C equity early
cycle signals.

**Korea-specific context**: Korea's housing cycle is tightly regulated
(안전규제, 분양가 상한제), so construction orders reflect both
private pre-sale activity and public infrastructure contracting. The
series is noisy month-to-month; 3-month moving averages are standard.

---

## Bundled usage

```bash
# Full monthly industry pulse (11 indicators)
uv run fdr_client.py --indicators industry

# Manufacturing core trio (production + inventory + shipment)
uv run fdr_client.py --preset manufacturing,manufacturing-inventory,manufacturing-shipment

# Consumption nowcast stack (monthly)
uv run fdr_client.py --preset retail-sales,wholesale-retail,credit-card-usage

# Capex cycle leading/coincident pair
uv run fdr_client.py --preset machinery-orders,capital-goods-output

# Construction cycle lead/lag pair
uv run fdr_client.py --preset construction-orders,construction-completion
```

---

## Cross-reference

- Growth (quarterly national-accounts components): `indicators-growth.md`
- Cycle (monthly GDP proxy CI pair): `indicators-cycle.md`
- Sentiment (survey-based): `indicators-sentiment.md`
- Full KEYSTAT catalogue: `../docs/bok-ecos-keystat-catalog.md`
