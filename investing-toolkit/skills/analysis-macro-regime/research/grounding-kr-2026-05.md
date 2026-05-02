# Korea Macro Regime — Grounding Delta Refresh 2026-05-02

**Type**: Partial recalibration per [recalibration-protocol.md](../references/recalibration-protocol.md) — short delta from prior vintage; full audits covered separately.

**Prior full grounding**: 2026-04-18 (v1.9.0, KR section of `research/grounding-v1.9.0.md`).
**Prior partial refresh**: 2026-04-19 (v1.11.0 addendum embedded in `references/thresholds-korea.md`).
**This refresh**: 2026-05-02 (PR-5 of v2.1.0 Phase 1 per ADR-0004).

## Status

**No mandatory recalibration trigger fired between 2026-04-19 and 2026-05-02.**

| Trigger (per recalibration-protocol.md §Mandatory) | Fired? |
|---|---|
| FOMC SEP update | n/a (KR scope) |
| BOK 경제전망보고서 (semi-annual Feb/Aug) | ❌ next: 2026-08 |
| BOK MPC base-rate change | ❌ 7 회 연속 동결 유지 (2026-04-10 직전; 5월 14일/28일 회의 예정) |
| Major regime shift | ❌ |

**Conclusion**: `thresholds-korea.md` 2026-Q1 vintage carries forward into `calibrations/kr.yaml` with one cosmetic update (concentration ratio refreshed from 40.90% → 40.96% per 2026-04-23 KOSPI close — within band, no calibration band shift).

## Native-language web verification (한국어 primary sources)

Native 한국어 grounding searches executed 2026-05-02 to verify thresholds-korea.md vintage 2026-Q1 still current.

### 1. BOK 기준금리 — confirmed 2.50% / 7회 연속 동결

- **Search**: `한국은행 기준금리 2026 5월 동결 금통위`
- **Finding**: 4 月 10 日 7 번째 연속 회의에서 정책 금리 2.50% 동결. 5 월 14 일 + 5 월 28 일 회의 예정. v1.11.0 의 "7 회 연속 동결" 진단 유효.
- **Primary source**: [한국은행 기준금리 추이 (BOK)](https://www.bok.or.kr/portal/singl/baseRate/list.do?dataSeCd=01&menuNo=200643), [BOK Home](https://www.bok.or.kr/portal/main/main.do)
- **Calibration impact**: ✅ no change. `policy_rate_level: 2.50` remains.

### 2. ESI (경제심리지수) — NEW data point 2026-04 = 91.7 (-2.3p MoM)

- **Search**: `한국은행 경제심리지수 ESI 2026년 4월 발표`
- **Finding**: 2026-04 ESI = **91.7** (전월대비 -2.3p). 제조업 CBSI 99.1 (+2.0p), 비제조업 92.1 (+0.1p), 전산업 CBSI 94.9 (+0.8p — 4 개월 만 최대 상승폭). 단, 재고 효과 제거 시 실적 + 5월 전망 모두 소폭 하락 — sentiment 약화의 underlying tone.
- **Primary source**: [한국은행 ESI snapshot](https://snapshot.bok.or.kr/?en=y), [ECOS](https://ecos.bok.or.kr/), [공공데이터포털 ESI 시리즈](https://www.data.go.kr/data/15059639/openapi.do)
- **Secondary**: [헤럴드경제 — 4월 기업심리지수 0.8P 올랐지만 재고 효과 빼면 악화](https://biz.heraldcorp.com/article/10726832)
- **Calibration impact**: ESI is a **band overlay**, not in calibration thresholds. Used by classify_kr.py if fdr fetch succeeds. ESI < 95 conventionally read as "below long-run average" — current 91.7 confirms cautious/contracting business sentiment despite headline CBSI uptick.

### 3. 가계부채/GDP — confirmed 89.4% (BIS 2025-Q3); NEW: 정부 80% by-2030 target

- **Search**: `한국 가계부채 GDP 비율 2026 BIS 89.4%`
- **Finding**: BIS 2025-Q3 89.4% confirmed; 2021-Q3 피크 99.1% 에서 ~10pp 하락. **NEW** (2026-03-24 단독 보도): 정부 2030 까지 가계부채/GDP **80%** 까지 낮추는 공식 목표 검토. BOK 분석: 80% 초과 시 소비 위축으로 성장 제약.
- **Primary source**: [BOK GDP-vs-가계부채 snapshot](https://snapshot.bok.or.kr/?en=y), [지표 GDP 대비 가계신용비율](https://www.index.go.kr/unity/potal/indicator/IndexInfo.do?idxCd=F0140)
- **Secondary**: [Herald 단독 — 2030 까지 가계부채 GDP 80%](https://biz.heraldcorp.com/article/10702162)
- **Calibration impact**: ✅ no change to `household_debt_overlay` thresholds. **Add note**: 정부 80% target by 2030 reinforces macroprudential concern band — calibration `macroprudential_concern_threshold: 80%` aligns with stated policy floor.

### 4. KOSPI 시총 집중도 — refreshed 40.90% → 40.96% (2026-04-23)

- **Search**: `KOSPI 시가총액 비중 삼성전자 SK하이닉스 2026 4월 40%`
- **Finding**: 2026-04-23 11:30 기준 삼성전자 + SK하이닉스 = ~2,173 兆 원 / KOSPI 5,304 兆 원 = **40.96%**. 4 월 7 일 첫 40% 돌파, 4 월 21 일 장중 41.11% 까지 확대.
- **Primary source**: [Daum 코스피 시가총액](https://finance.daum.net/domestic/market_cap)
- **Secondary**: [econmingle — 삼성전자 + SK하이닉스 2,173 兆](https://econmingle.com/economy/samsung-skhynix-kospi-market-cap-2173-trill/)
- **Calibration impact**: minor refresh from 40.90% (v1.11.0) → 40.96%. Within concentration risk band; no threshold change. Calibration carries 0.4096 (latest).

### 5. BOK 물가안정목표 2% — confirmed 무기한 적용

- **Search**: `한국은행 물가안정목표 2% 2026 무기한 적용`
- **Finding**: 2019- 적용 2% point target, 2 년 주기 점검 + 정부 협의 (운영 개선); 적용기간 무기한 (2018-12-26 합의 후 변경 없음).
- **Primary source**: [BOK 물가안정목표제 — 목표 및 운영체계](https://www.bok.or.kr/portal/main/contents.do?menuNo=200291), [BOK 물가안정목표제(inflation targeting)란 무엇인가?](https://www.bok.or.kr/portal/bbs/P0002897/view.do?nttId=226036&menuNo=200788&pageIndex=1)
- **Calibration impact**: ✅ no change. `inflation_target: 2.0`, `inflation_target_type: point`, `inflation_target_authority_date: 2018-12-26`.

### 6. 청년실업률 7.7% (2026-02) — confirmed

- **Search**: `한국 청년실업률 2026년 2월 7.7% 통계청`
- **Finding**: 청년층(15-29세) 2026-02 실업률 = **7.7%** (전년 동월대비 +0.7p). 2021-02 (10.1%) 이후 5 년 만 최고. 청년 고용률 43.3% (-1.0p YoY, 22 개월 연속 하락). 제조업 + 건설업 각각 20 개월, 22 개월 연속 감소 — 신입 채용 축소 + AI 도입 영향 복합.
- **Primary source**: [통계청 KOSTAT 고용동향](https://www.kostat.go.kr/board.es?mid=a10301010000&bid=210), [e-나라지표 청년실업률](https://www.index.go.kr/unify/idx-info.do?idxCd=5028)
- **Secondary**: [파이낸셜뉴스 — 청년 실업률 7.7% 5 년만 최고치](https://www.fnnews.com/news/202603180835167687)
- **Calibration impact**: ✅ no change. `youth_unemployment_pct: 7.7` carried forward as overlay. Headline NAIRU 3.0-3.5% structural anchor unchanged.

### 7. 동행지수 순환변동치 (KOSTAT) — methodology confirmed

- **Search**: `한국 동행지수 순환변동치 2026 KOSTAT 경기종합지수`
- **Finding**: 동행지수 순환변동치 = 동행지수에서 추세변동분 제거 → 현재 경기 국면 및 전환점 파악. **기준치 100 = 추세선**: ≥100 → 확장 국면, <100 → 수축 국면. Fixture latest 100.1 (선행 103.5 / 동행 100.1) = 확장 경계.
- **Primary source**: [KOSTAT 경기종합지수](https://kostat.go.kr/statDesc.es?act=view&mid=a10501010000&sttr_cd=S010001), [k-stat 경기종합지수 해설](https://www.k-stat.go.kr/comb100/file-download?fileDnKey=shqgb/2dKgD6Dn6g47FE9Zrkqqt1NSfKicMHnzOiv3k%3D)
- **Calibration impact**: ✅ confirms cycle phase mapping. `cycle_threshold: 100.0` for K253 동행지수 순환변동치.

## ESI fetch attempt (PR-5 best-effort)

Per ADR-0004 PR-5 spec: **best-effort fetch BOK 경제심리지수 (ESI)** via `fdr_client.py` (BOK ECOS-KEYSTAT K269). If fetch succeeds, wire into pack.py `sentiment` group; else mark `esi_status: "unavailable_via_fdr"` and proceed with confidence: medium.

**Status (this PR)**: `economic-sentiment` (K269) preset already exists in `fdr_client.py` (line 217), and `pack.py` `REGIME_GROUPS["sentiment"]` already includes it. No new wiring needed at the data layer — `pack.py` regime-pack with `--indicators all` already pulls ESI.

The current `data-kr-regime-pack-sample.json` fixture omits `sentiment` group (only rates / inflation / growth / cycle / fx). classify_kr.py treats ESI as **optional structural overlay**: surfaces `esi_status: "fetched"` + value when `economic-sentiment` series present in the pack; surfaces `esi_status: "unavailable_via_fdr"` when absent (does NOT fail country chain).

## Calibration carry-over (verbatim from thresholds-korea.md)

| Field | Value | Source vintage |
|---|---|---|
| `inflation_target` | 2.0 | BOK 2018-12-26 (2019- 무기한 적용) |
| `inflation_target_type` | point | BOK |
| `inflation_target_framework` | inflation_targeting (FIT-style, point target) | BOK |
| `policy_rate_level` | 2.50 | BOK 2025-05-29 인하 후 7 회 연속 동결 (2026-04-10 가장 최근) |
| `policy_rate_path_note` | "7 회 연속 동결 since 2025-05" | BOK 통화정책방향 누적 |
| `nairu.point_estimate` | 3.2 | KDI / 한양대 / KIEP 학술 컨센서스 (3.0-3.5% 범위 중점) |
| `household_debt_overlay.ratio_bis` | 0.894 | BIS 2025-Q3 |
| `household_debt_overlay.ratio_bok` | 0.923 | BOK 2025-09 |
| `household_debt_overlay.peak_2021q3` | 0.991 | BIS 2021-Q3 historical peak |
| `household_debt_overlay.govt_target_2030` | 0.80 | 2026-03 단독 보도 (정부 정책 검토) |
| `kospi_concentration_overlay.samsung_skhynix` | 0.4096 | 2026-04-23 (refreshed from 0.4090 v1.11.0) |
| `kospi_concentration_overlay.samsung_sk_groups` | 0.6129 | 2026-02 (전체 그룹) |
| `youth_unemployment_pct` | 7.7 | KOSTAT 2026-02 (5 년 최고) |
| `cycle_threshold` | 100.0 | KOSTAT 동행지수 순환변동치 추세선 |

## Anchored Quotes (verified currency)

> "현재 정책 금리 수준(2.50%)에서 통화정책을 운용하기로 결정"
> — BOK 통화정책방향 결정문 2026-04-10 (7 회 연속 동결)

> "물가안정목표를 소비자물가 상승률(전년동기대비) 기준 2% 로 한다 — 적용기간 무기한"
> — BOK 물가안정목표제 (2018-12-26 정부 합의 이후 유지)

> "GDP 대비 가계부채 비율이 80% 를 초과하면 소비 위축으로 경제성장이 제약된다"
> — BOK 분석 (Herald 2026-03-24 단독 보도 인용)

These anchor `classify_kr.py`'s qualitative annotations: `cycle_phase` annotation references KOSTAT 동행지수 100 threshold; `household_debt_overlay.macroprudential_concern` triggers when ratio > 80% (currently 89.4% → flagged).

## Phase 1 PR-5 Implementation Notes

- `calibrations/kr.yaml` extracts `thresholds-korea.md` numeric values as YAML keys for machine-readable consumption by `classify_kr.py`.
- `classify_kr.py` reads YAML calibration via `load_calibration("kr")` and applies:
  - **BOK 2% target alignment** (gap = current_cpi_yoy − 2.0)
  - **KOSTAT 동행지수순환변동치 cycle phase** (≥100 expansion / <100 contraction; with `rising/falling` modifier from latest vs prior 3-mo avg)
  - **Household debt overlay** (BIS + BOK readings + macroprudential concern flag at >80%)
  - **KOSPI concentration overlay** (Samsung+SK Hynix, 그룹 전체)
  - **Youth unemployment overlay** (단순 surface; aggregate NAIRU comparison)
  - **ESI** (best-effort: surfaces value if present, marks `unavailable_via_fdr` otherwise)
  - **IC quadrant legacy** (parity with `_legacy_ic.classify_country` for backward compat — populates the comparable axis Phase 2 may need)
- ESI handling rule: `esi_status` ∈ {`"fetched"`, `"unavailable_via_fdr"`}. When `unavailable_via_fdr`, confidence floor = "medium" (not "low") — KEYSTAT 54-indicator subset already in regime-pack delivers enough signal for medium-confidence verdict per ADR-0004 PR-5 acceptance criteria.

## Next Recalibration Triggers

Watch for:
- **BOK MPC 2026-05-14 / 2026-05-28** — 동결 vs 인하 변곡 (mandatory; ~14-day latency for off-path)
- **BOK 경제전망보고서 2026-08** (mandatory; ~30-day latency target) — semi-annual full review
- **2026-Q1 GDP 잠정치 (BOK 2026-06)** — confirms cycle phase
- **Samsung / SK Hynix 2026-Q1 실적 + HBM 가이던스** — KOSPI concentration validation
- **국토부 가계부채 80% by-2030 정책 정식 발표** — would tighten macroprudential overlay
- **KOSTAT 청년실업률 — 2026-Q2 회복 vs 추가 악화** — labor overlay refresh

If any fires, update `thresholds-korea.md` first, then re-extract numeric values into `calibrations/kr.yaml`. CI drift-detection test (planned for later PR) will catch numeric mismatches.
