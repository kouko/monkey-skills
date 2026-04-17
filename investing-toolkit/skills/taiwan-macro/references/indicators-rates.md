# Rates / 利率系

---

## rediscount-rate: 重貼現率 / Rediscount Rate

- **Series code**: EG2AM01en (CBC API)
- **Source**: CBC (Central Bank)
- **Unit**: Percent (%)
- **Frequency**: Monthly (changes at quarterly board meetings)
- **Publication lag**: Same day as policy announcement
- **History**: From 2000 (monthly)

**What it measures**: The rate at which the Central Bank of the Republic of
China (Taiwan) lends to commercial banks against eligible bills and notes.
This is Taiwan's primary policy rate, analogous to the Fed Funds Rate in the
US or the BOJ Policy Rate in Japan.

**How to interpret**:
- Rising → CBC is tightening monetary policy. Higher borrowing costs for
  banks, which flows through to corporate and consumer lending rates. Typically
  in response to inflationary pressures or overheating economy.
- Falling → CBC is easing to support growth. Lower borrowing costs encourage
  lending and investment.
- Flat → Policy on hold. The CBC tends to move in small increments (12.5 bps),
  much smaller than the Fed's typical 25 bps moves.

**Market significance**: ⭐⭐⭐
Taiwan's most important monetary policy signal. CBC rate decisions are made at
quarterly board meetings (March, June, September, December). The CBC is known
for its gradualist approach — rate changes are typically 12.5 bps (half a
standard Fed move), reflecting Taiwan's preference for policy stability. The
announcement moves TWD, Taiwan equity indices (TAIEX), and government bond
yields.

**When to use**: Investment Clock monetary policy axis, CBC rate cycle analysis, TWD direction assessment, Taiwan financial conditions baseline.

**Taiwan-specific context**:
- The CBC has historically maintained lower rates than the US Fed, reflecting
  Taiwan's export-oriented economy and structural current account surplus.
- Taiwan's monetary policy is heavily influenced by the TWD/USD exchange rate.
  The CBC often prioritizes currency stability over inflation targeting.
- The rediscount rate serves as the floor for Taiwan's interbank lending rates.
  The actual overnight call rate typically trades very close to the policy rate.

**Common pitfalls**:
- The CBC rate cycle is much slower than the Fed's. Do not expect matching
  pace or magnitude of rate changes.
- Historical data shows long plateaus — the rate can stay unchanged for years.
- The effective monetary stance also depends on the CBC's foreign exchange
  market operations, which are not captured by the policy rate alone.

---

## rates-daily: 央行利率（日頻） / CBC Interest Rates Daily

- **Series code**: EG28D01en (CBC API)
- **Source**: CBC (Central Bank)
- **Unit**: Percent (%)
- **Frequency**: Daily
- **Publication lag**: ~1 business day
- **History**: From 2000 (daily)

**What it measures**: Daily-frequency interest rate data from the CBC,
including various lending facility rates. Provides granular tracking of
rate changes between board meetings.

**How to interpret**:
- Changes in this series are rare and typically coincide with board meeting
  announcements. Between meetings, rates are flat.
- Use this series when you need to confirm the exact date a rate change
  took effect.

**Market significance**: ⭐
Mostly confirmatory — the rediscount rate (monthly) captures the same
policy signals. Daily frequency is useful for historical event studies
and precise date mapping.

**When to use**: CBC policy rate confirmation, interest rate event study, historical rate change date mapping.

**Common pitfalls**:
- Data may lag actual CBC announcements by 1-2 days.
- Some rate facilities tracked here are administrative rates with limited
  market impact.
