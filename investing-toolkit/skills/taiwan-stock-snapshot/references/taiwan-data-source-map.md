# Taiwan Data Source Map

> **Note**: Taiwan data adapters (FinMind connector, `finmind_client.py`) ship in
> investing-toolkit v1.1.0. This reference documents the Taiwan data ecosystem
> for planning and manual workflows.

## Primary Statutory Sources

| Data | Source | URL | Statutory Basis |
|------|--------|-----|-----------------|
| 三大法人買賣超日報 | TWSE T86 | https://www.twse.com.tw/zh/trading/fund/T86.html | — |
| 月營收資訊系統 | MOPS | https://mops.twse.com.tw/mops/web/t05st10_ifrs | 證交法第36條 |
| 董監事持股及質押 | TWSE | https://www.twse.com.tw/zh/company/insiderHoldings.html | 證交法第25條 + 第22條之2 |
| 融資融券餘額 | TWSE | https://www.twse.com.tw/zh/trading/margin/MI_MARGN.html | — |
| 公司基本資料 | MOPS | https://mops.twse.com.tw/mops/web/t05st03 | — |
| 財務報表 (IFRS) | MOPS | https://mops.twse.com.tw/mops/web/t05st10_ifrs | — |

## FinMind API (v1.1.0)

| Dataset | FinMind Dataset ID | Notes |
|---------|-------------------|-------|
| 股票日線 | TaiwanStockPrice | OHLCV |
| 三大法人 | TaiwanStockInstitutionalInvestorsBuySell | 外資/投信/自營商各別 |
| 月營收 | TaiwanStockMonthRevenue | 截止日：每月10日 |
| 董監持股 | TaiwanStockHoldingSharesPer | 持股 % |
| 融資融券 | TaiwanStockMarginPurchaseShortSale | 融資餘額 + 融券餘額 |
| 財務報表 | TaiwanStockFinancialStatements | 季頻 |
| 損益表 | TaiwanStockProfitLossStatement | 季頻 |

**Auth**: `FINMIND_API_TOKEN` env var (optional; anonymous = 300 req/hr, token = 600 req/hr)

## CasualMarket MCP (Real-time)

CasualMarket is a Taiwan-specific MCP server providing live market data.
Install separately — **not bundled with investing-toolkit**:

```bash
# Install via Claude Code plugin marketplace
# See: https://github.com/sacahan/CasualMarket
claude plugin add casualmarket
```

When CasualMarket MCP is installed, skills can call it directly for:
- Real-time quotes (延遲15分鐘)
- 外資動向 (live 三大法人)
- Valuation multiples (PE, PB, EV/EBITDA for TWSE/OTC)

## Attribution Corrections (Taiwan)

1. **月營收截止日是每月10日（曆日）** — per 證交法第36條 + FSC 行政命令。不是月底，不是15日。
2. **融資 ≠ 融券方向相同**：融資餘額上升 = 散戶加碼多單（看漲信號）；融券餘額上升 = 放空部位增加（看跌信號）。兩者方向相反。
3. **三大法人分三類，特性不同**：外資 = 大型/趨勢跟隨；投信 = 較小/常逆外資；自營商 = 多為避險。不可合並為單一「法人」信號。
4. **董監持股質押率 > 50% 是治理紅旗** — 高質押率創造壓低股價的誘因，高風險。（葉銀華 2008）

## Taiwan Market Calendar Notes

- **月營收公布**：每月10日前（逾期申報有罰則）
- **季報公布**：Q1 (5/15), Q2 (8/14), Q3 (11/14), Q4 (翌年3/31)
- **除息除權**：通常在7-9月集中（Taiwan dividend season）
- **台股交易時間**：09:00-13:30 (TST, UTC+8)
- **台股代號格式**：上市 = 4碼數字.TW；上櫃 = 4碼數字.TWO
