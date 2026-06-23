-- Query 1: Total Companies
SELECT COUNT(*) AS total_companies
FROM companies;

-- Query 2: Top 10 Companies by Market Cap
SELECT company_id,
       market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;

-- Query 3: Companies with Highest ROE
SELECT company_id,
       return_on_equity_pct
FROM financial_ratios
ORDER BY return_on_equity_pct DESC
LIMIT 10;

-- Query 4: Companies with Lowest Debt-to-Equity
SELECT company_id,
       debt_to_equity
FROM financial_ratios
ORDER BY debt_to_equity ASC
LIMIT 10;

-- Query 5: Average Net Profit Margin
SELECT AVG(net_profit_margin_pct)
FROM financial_ratios;

-- Query 6: Companies with Positive Free Cash Flow
SELECT company_id,
       free_cash_flow_cr
FROM financial_ratios
WHERE free_cash_flow_cr > 0
ORDER BY free_cash_flow_cr DESC;

-- Query 7: Number of Companies by Sector
SELECT broad_sector,
       COUNT(*)
FROM sectors
GROUP BY broad_sector
ORDER BY COUNT(*) DESC;

-- Query 8: Stock Price Records
SELECT COUNT(*)
FROM stock_prices;

-- Query 9: Companies having ROE > 20%
SELECT company_id,
       return_on_equity_pct
FROM financial_ratios
WHERE return_on_equity_pct > 20;

-- Query 10: Companies with Highest EPS
SELECT company_id,
       earnings_per_share
FROM financial_ratios
ORDER BY earnings_per_share DESC
LIMIT 10;