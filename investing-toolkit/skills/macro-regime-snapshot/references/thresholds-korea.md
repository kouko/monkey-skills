# Korea / 한국 — Macro Regime Thresholds & Calibration

**Authority**: 한국은행 (Bank of Korea, BOK) + 통계청 (KOSTAT) |
**Currency**: KRW | **Calibration vintage**: 2026-Q1

---

## Inflation Target / 물가안정목표

- **Official target**: **2% CPI YoY** (소비자물가 전년동기대비, set 2019)
- **Tolerance band**: **none explicit** — BOK uses
  "목표수준을 지속적으로 상회하거나 하회할 위험을 균형있게 고려"
  ("balanced consideration of persistent overshoot/undershoot risk")
- **Target horizon**: medium-term (중기적 시계)
- **2026 CPI forecast** (BOK): **2.1%** — close to target
- **Recent readings (2026)**: settling near 2.0-2.1% after 2022-2023
  food/energy spike
- **Signal**:
  - `> 2.3%` Above target
  - `1.7% ≤ x ≤ 2.3%` At target (BOK's goal state, current regime)
  - `< 1.7%` Below target

---

## Labor Market Tightness (NAIRU / 자연실업률)

- **Academic estimates** (KDI + 한양대 Semi-Parametric Analysis + KIEP):
  - 1980s pre-crisis: ~3.7-4.0%
  - 1988-1997 (Miracle era): ~2.6-3.2%
  - Post-1997 IMF crisis peak: 4.0-5.3%
  - Post-2010 trending down: **~3.0-3.5%** current consensus
- **BOK does not publish official NAIRU** — relies on KDI / KIEP /
  academic literature.
- **Current unemployment** (통계청 2026-01/02): **~2.7%**
- **Implication**: unemp **below structural NAIRU** → **Tight** labor
  market (cross-check: wage growth accelerating 2024-2025 post
  "미니멈 웨이지" legal-hike effects).
- **Bands (NAIRU ~3.2% ± 0.4 pp)**:
  - `unemp < 2.8%` → Tight (current)
  - `2.8% ≤ unemp ≤ 3.6%` → Balanced
  - `unemp > 3.6%` → Slack

---

## Policy Rate Neutrality

- **Current BOK 기준금리 (base rate)**: **2.50%** (decided 2026-01-15
  금융통화위원회)
- **Nominal neutral estimate**: BOK has historically been reluctant to
  publish explicit r*. Academic estimates + market consensus:
  **nominal ~2.25-2.75%**, implying **real r\* ~0.25-0.75%** (lower
  than US but higher than JP).
- **Historical range**: BOK base rate 2000-2024 = 1.25% to 5.25%.
- **Post-2020**: peaked at 3.50%, now moderating back toward neutral.
- **BOK MPC framework**: more flexible forward-guidance-lite than Fed;
  decisions strongly tied to household-debt / FX / semi-cycle factors.

---

## Real Rate Decomposition

**Not available** for v1.9.0.

**Why**: Korea has **KTBi** (Korean Treasury Bonds — Inflation-linked)
issued by 기획재정부 since 2007, but:
1. BOK ECOS-KEYSTAT does NOT expose KTBi breakeven series
2. Full ECOS API (with free registration at ecos.bok.or.kr/api/#/AuthKeyApply)
   might have 국고채 물가연동 series but not confirmed
3. KTBi secondary market less liquid than US TIPS

**Deferred to v1.10.0+**: after BOK ECOS API key integration,
investigate whether KTBi breakeven series exposed; if so, calibrate
thresholds around KR r* ~0.25-0.75% real (wider bands than US given
thinner market):
- Tentative (draft for v1.10.0+): `< -0.5%` Accommodative / `-0.5% to 1.0%`
  Neutral / `1.0% to 2.0%` Moderately Restrictive / `≥ 2.0%` Clearly
  Restrictive.

---

## Structural Regime Notes

- **Export-dependent economy**: exports ~40-45% of GDP (highest in G20).
  **KR macro regime follows global semi + auto cycle** more than
  domestic demand.
- **Semi concentration**: Samsung Electronics + SK Hynix together ~30%
  of KOSPI weight; DRAM cycle turns drive BOK + Finance Ministry
  responses directly.
- **Household debt high**: ~105% of GDP (higher than US ~75% or JP ~65%)
  — BOK must consider household-debt stability alongside inflation +
  growth. Macroprudential policy often pre-empts monetary policy.
- **KRW managed**: KRW is free-floating but BOK intervenes in
  large-move episodes. KRW sensitivity to USD + CNY both important.
- **Demographic overhang**: KR on JP's aging path (fertility 0.72,
  lowest in OECD; aging-ratio rising fastest) — structurally lowers
  future growth and r*.

---

## Asset-Class Tilt Calibration

- **Equity index concentration — high**:
  - KOSPI dominated by Samsung Electronics (~20%) + SK Hynix (~10%)
  - Tech + semi ~35-40% weight
  - Chaebol concentration: top 10 chaebols = ~55% of KOSPI market cap
  - → Regime tilts dominated by **semi cycle** + **chaebol governance reforms**
- **KOSDAQ**: small-cap growth venue; more volatile, less regime-driven.
- **Fixed income**: KTB market reasonably deep; 10Y yield pays ~3%
  nominal (2026-Q1). KTB-vs-UST spread often tracks KRW direction.
- **FX**: KRW/USD primary, KRW/JPY (tourism + manufacturing competition
  with JP), KRW/CNY (tertiary but supply chain critical).

### Sector Tilts (KR-specific adjustments to IC cheatsheet)

| IC Phase | KR-specific Overweight | KR-specific Underweight |
|----------|------------------------|--------------------------|
| Recovery | Semi (Samsung, SK Hynix), autos (Hyundai/Kia), shippers | Utilities (KEPCO weak regulation), defensive |
| Overheat | Upstream semi, shipbuilders, chemicals, petrochems | Long-dated KTB |
| Stagflation | Cash, healthcare, food staples | Semi (inventory risk), real estate |
| Reflation | Financials (higher rates = better NIM), KTB, telecoms | Semi, export-oriented, autos |

**Heuristic**: KR cycle turns with DRAM cycle → `manufacturing` +
`exports` in korea-macro are the key pre-regime signals; `cycle`
(K253 K254) CI pair confirms.

---

## Primary-Source Verification URLs

- 한국은행 물가안정목표: https://www.bok.or.kr/portal/main/contents.do?menuNo=200291
- 한국은행 통화정책방향: https://www.bok.or.kr/portal/bbs/P0000559/
- 한국은행 홈페이지: https://www.bok.or.kr/
- 통계청 KOSTAT: https://kostat.go.kr/
- BOK ECOS API (회원가입 등록): https://ecos.bok.or.kr/api/#/AuthKeyApply
- KDI NAIRU 연구: https://kdijep.org/

## Sources (citations)

- 한국은행 물가안정목표제 공식 문서 (2019 설정)
- 한국은행 2026 통화정책방향 (2026-01-15 금통위)
- 신석하 (KDI) 2004 — 한국의 자연실업률 추정 (KDI JEP 26-2-3)
- 한양대 Repository — 한국의 자연실업률 NAIRU Semi-Parametric Analysis
- 조세일보 2026-01 "한은 물가 점차 2% 근방으로 낮아질 것"
- BBSI 뉴스 — 한국은행 내년 소비자물가 2.1% 전망
