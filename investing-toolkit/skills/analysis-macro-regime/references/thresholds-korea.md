# Korea / 한국 — Macro Regime Thresholds & Calibration

**Authority**: 한국은행 (Bank of Korea, BOK) + 통계청 (KOSTAT) |
**Currency**: KRW | **Calibration vintage**: 2026-Q1

## Grounding Status (as of 2026-04-18)

**Last full verification**: 2026-04-18 via `../research/grounding-v1.9.0.md`
(5-country parallel grounding note; KR section).

**Verified (✅)**: 현재 물가안정목표 2% single-point, 2026 CPI 전망 2.1%,
BOK 물가목표 "균형있게 고려" 정성적 언어.

**Corrected (🔴 in prior draft → fixed below)**:
1. **2018-12-26 발표 / 2019 이후 적용** (prior draft "2019 설정" 애매);
   이전 3 년 주기 재설정 관행 폐기, 적용기간 무기한화.
2. **2004-2006 과 2007-2009 목표 지표 顛倒** —
   - 2004-2006: core CPI 2.5-3.5%
   - 2007-2009: **headline CPI 3% ± 0.5%** (prior draft 반대로 기록)
3. **NAIRU 1998-2004 (외환위기 피크 구간)** — NOT 1998-2000. 이후 하락 추세.
4. **삼성전자 + SK하이닉스 = 39.88%** (2026-02) → **40.90%** (2026-04 중).
   삼성그룹 + SK그룹 전체 **61.29%** (1 년 전의 2 배). Prior draft 의 ~30%
   는 1 년 전 (2025-02) vintage.
5. **가계부채/GDP ~90%** (BIS 2025-Q3 89.4%; BOK 92.3% @ 2025-09).
   **105% 는 2021 피크** (실제 99.1%), 이미 ~10 pp 하락. Prior draft wrong.

**Partial (⚠️)**:
- 2.50% 인하 날짜: **2025-05-29 인하**, 이후 5 회 연속 동결 (2026-01-15 포함).
- 현재 실업률: 2.7% 는 2026-03 계절조정; 원계열 2026-01 = 4.1%, 2026-02 = 3.4%;
  청년실업 2026-02 = 7.7% (5 년 최고).
- r\* 추정: BOK 연구원 Do/Ahn/Jung 2024 multi-model real ~0-1% (prior draft
  "0.25-0.75% real" 은 상단만 반영).

**New sources added**: SSRN 5009627 (Do/Ahn/Jung 2024 BOK 연구원 r\* paper),
Seoul Economic Daily 2026-02 (KOSPI 集中度), BIS 2025-Q3 data.

**New discovery**: KR 2026-01 from BIS 재분류 to **advanced economy**
(ex-emerging) — 시계열 그룹 변경.

### v1.11.0 addendum (2026-04-19)

Delta refresh since v1.9.0 (2026-04-18) vintage. Not a full re-audit
— only changes captured.

🔴 None — no material corrections required.

⚠️ **BOK 2026-04-10 금통위 — 기준금리 2.50% 7연속 동결 (만장일치)**:
v1.9.0 draft 은 "5회 연속 동결" (2026-01-15 까지) 기준. 이후 2026-02-26,
2026-04-10 두 차례 더 추가되어 **7회 연속** 동결이 공식 수치. 금통위
결정문은 **중동전쟁으로 인한 공급충격**을 핵심 변수로 명시: (1) 유가 상승
→ 인플레이션 상방압력 확대, (2) 성장 하방압력 증대, (3) 금융·외환시장
변동성 확대. 완화 사이클 재개 시점 불확실성 증가 (시장 컨센서스 2026-H2
로 이연). (Source: https://www.bok.or.kr/portal/bbs/P0000559/view.do?nttId=10097452)

⚠️ **삼성전자 + SK하이닉스 비중 — AI/HBM 랠리로 40%+ 유지**: SK하이닉스
2026-04-14 주가 113 만 원 신고가, 시가총액 ~110 조 원 (코스피 2 위 공고).
삼성전자 + SK하이닉스 합산 2026-02 39.88% → 2026-04 중 40.90% (v1.9.0
기록). 2026-04 중순 이후는 추가 확대 여지 (HBM 경쟁력 + AI 데이터센터
수요). Phase 2 Overheat / 반도체 사이클 정점 근접 위험 주시 요인 — 다만
v1.9.0 threshold 와 일관된 방향성, 밴드 재조정 불필요.

⚠️ **가계부채/GDP — 하락 추세 지속**: BIS 2025-Q1 89.5%, Q3 2025 BOK
기준 92.3% (2025-Q2 92.7% 에서 소폭 하락). v1.9.0 의 "2021 피크 99.1%
에서 지속 하락" 진단 유효. BIS 2025-05 리포트에서 "다음 금융위기 촉발
가능성이 높은 국가 중 하나" 경고 유지 — 매크로프루덴셜 규제 지속 필요.

**Verified unchanged**:
- 물가안정목표 2% (2019- 적용기간 무기한)
- 2026 CPI 전망 2.1% (BOK)
- NAIRU 3.0-3.5% 학술 컨센서스
- 현행 실업률 2.7% (2026-03 계절조정) 구조적 NAIRU 하회 → Tight
- BOK r\* ~0-1% real (Do/Ahn/Jung 2024 추정 범위)
- 삼성그룹 + SK그룹 전체 61.29% 집중도 (2026-02 기준)
- KRW 관리변동환율 / 원화 16년 저점 근접 유지
- BIS 2026-01 advanced economy 재분류

**New primary-source URLs**:
- https://www.bok.or.kr/portal/bbs/P0000559/view.do?nttId=10097452
  (BOK 통화정책방향 2026-04-10 결정문)
- https://www.fntimes.com/html/view.php?ud=202604101058544858179ad43907_18
  (2026-04-10 7연속 동결 보도)

See `../research/grounding-v1.11.0.md` (to be written in next commit)
for consolidated cross-country audit.

**Next recalibration**: July 2026 (BOK 경제전망 하반기 + 7월 MPC;
중동상황 관련 완화 재개 시점 재평가).

---

---

## Inflation Target / 물가안정목표

- **Official target**: **2% CPI YoY** (소비자물가 전년동기대비)
- **Framework**: 2018-12-26 BOK-정부 합의로 "2019년 이후 적용 물가안정목표"
  설정; 이전 3 년 주기 재설정 관행 폐기, **적용기간 무기한화**
  ("특별한 이유가 없으면 디폴트로 2% 유지" — 정규일 부총재보). 2016년부터
  이미 2% point target 운영, 2018-12 개정은 **목표 유지 + 적용기간 무기한
  + 운영방식 개선**.
- **Tolerance band**: **none explicit** — BOK uses
  "목표수준을 지속적으로 상회하거나 하회할 위험을 균형있게 고려"
  ("balanced consideration of persistent overshoot/undershoot risk")
- **Target horizon**: medium-term (중기적 시계)

### Historical targets (20-year, grounding-v1.9.0.md KR §20-year trajectory)

| 기간 | 지표 | 수준 |
|------|------|------|
| 2004-2006 | **core CPI** | 2.5-3.5% band |
| 2007-2009 | **headline CPI** | **3% ± 0.5%** |
| 2010-2012 | headline CPI | 3% ± 1% |
| 2013-2015 | headline CPI | 2.5-3.5% band |
| 2016-2018 | headline CPI | 2% point |
| **2019-현재** | headline CPI | **2% (적용기간 무기한)** |
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
  - **NOTE**: Prior draft incorrectly stated 1998-2000 peak; correct
    peak interval per 신석하 2004 is **1998-2004** (wider, 반영 IMF 이후
    hysteresis; 이후 하락 추세 시작).
- **BOK does not publish official NAIRU** — relies on KDI / KIEP /
  academic literature.
- **Current unemployment** (통계청 2026-03 계절조정): **2.7%**
  (2023-08 이후 최저 근접). **원계열 기준**: 2026-01 = 4.1%, 2026-02 = 3.4%
  (계절성 때문에 Q1 초반이 연중 고점). 청년실업 (15-29세) 2026-02 = **7.7%**
  (5년 최고) — 전체 실업률과 괴리 주시.
- **Implication**: unemp **below structural NAIRU** → **Tight** labor
  market (cross-check: wage growth accelerating 2024-2025 post
  "미니멈 웨이지" legal-hike effects).
- **Bands (NAIRU ~3.2% ± 0.4 pp)**:
  - `unemp < 2.8%` → Tight (current)
  - `2.8% ≤ unemp ≤ 3.6%` → Balanced
  - `unemp > 3.6%` → Slack

---

## Policy Rate Neutrality

- **Current BOK 기준금리 (base rate)**: **2.50%** (2025-05-29 인하 이후
  유지; 2026-01-15, 2026-02-26 포함 **5회 연속 만장일치 동결** — 2026-Q1
  기준 완화 사이클 일시 중단, 원화 16년 저점 + Fed 불확실성 고려)
- **Nominal neutral estimate**: BOK has historically been reluctant to
  publish explicit r\*. **BOK 연구원 최신 multi-model 추정**
  (Do, Ahn, Jung 2024, SSRN 5009627): **실질 r\* ~0-1%** (2010년대
  변동범위 내); 2% 물가 가정시 **nominal ~2.0-3.0%**. Prior draft
  "0.25-0.75% real" 은 범위의 상단 — 실제 분포는 더 넓고 **하단은
  마이너스 근접 가능**.
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
- **Household debt high but easing**: ~**90% of GDP** (2025-Q3 BIS
  기준 89.4%; BOK 기준 92.3% @ 2025-09). 2021-Q3 피크 99.1% 에서
  **지속 하락 중**. OECD 31 국 중 6 위권 (스위스/호주/캐나다/
  네덜란드/뉴질랜드 다음). 장기 평균 (2010-) 83.7%. 여전히 US (~75%)
  / JP (~65%) 대비 높음 — 매크로프루덴셜 compulsion 유지.
- **KRW managed**: KRW is free-floating but BOK intervenes in
  large-move episodes. KRW sensitivity to USD + CNY both important.
- **Demographic overhang**: KR on JP's aging path (fertility 0.72,
  lowest in OECD; aging-ratio rising fastest) — structurally lowers
  future growth and r*.

---

## Asset-Class Tilt Calibration

- **Equity index concentration — 歷史 최고**:
  - 삼성전자 + SK하이닉스 = **39.88%** (2026-02-27) → **40.90%**
    (2026-04 중순), **S&P500 Mag-7 (33.41%) 초과**
  - 삼성그룹 + SK그룹 전체 = **61.29%** (2026-02), 1 년 전 30.56% 의 약 2 배
  - 변동성 주의: 2025-06 에는 삼성전자 단독 14.53% (9 년 저점) →
    HBM 경쟁력 회복으로 9 개월간 급반등
  - → Regime tilts는 **DRAM 사이클 = KR 지수 사이클**; 기재부 정책 반응
    이 directly driven by 반도체
- **BIS 재분류 (2026-01 from)**: Korea reclassified to "advanced economy" —
  EM 집계와 break; 비교 대상국 그룹 변경 주시.
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
