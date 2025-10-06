# AAPL 2024 Buy & Hold Strategy

****Initial Capital:** $10,000 → **Final Equity:** $13,887.79 → **Gain:** +$3,887.79 (+38.88%)**

# Backtest Report for MyStrategy

## 1. Summary
- **Initial Capital**: $10,000.00
- **Final Equity**: $13,887.79
- **Total Return**: 38.88%
- **Annualized Return**: 39.06%
- **Duration**: 363 days
- **Max Drawdown**: -15.26%
- **Sharpe Ratio**: 1.25
- **Win Rate**: Not applicable (no trades executed)

## 2. Strategy
- **Name of Strategy**: MyStrategy
- **Strategy Type**: Buy and Hold
- **Description**: The strategy involves purchasing AAPL stock and holding it throughout the backtest period without executing any additional trades. The goal is to evaluate the performance of a long-term investment approach in a specific timeframe.
- **Market / Asset Traded**: AAPL (Apple Inc.), relevant timeframe being the year 2024.
- **Exposure Time**: 0.0%

## 3. Results
### Backtesting Period
- **Start Date**: January 2, 2024
- **End Date**: December 30, 2024

### Performance Metrics
| Metric                       | Value               |
|------------------------------|---------------------|
| Final Equity                 | $13,887.79          |
| Value at Peak                | $14,261.56          |
| Return Percentage             | 38.88%              |
| Buy & Hold Return            | 36.52%              |
| Annualized Volatility        | 31.29%              |
| Compound Annual Growth Rate (CAGR)| 25.61%          |
| Sharpe Ratio                 | 1.25                |
| Sortino Ratio                | 2.76                |
| Calmar Ratio                 | 2.56                |
| Alpha                        | 2.74%               |
| Beta                         | 0.99                |

### Drawdown Analysis
| Metric                      | Value            |
|-----------------------------|------------------|
| Max Drawdown                | -15.26%          |
| Average Drawdown            | -3.40%           |
| Max Drawdown Duration       | 134 days         |
| Average Drawdown Duration    | 22 days          |

### Trades Summary
| Metric                     | Value      |
|----------------------------|------------|
| Number of Trades           | 0          |
| Win Rate                   | N/A        |
| Best Trade                 | N/A        |
| Worst Trade                | N/A        |
| Profit Factor              | N/A        |
| Expectancy                 | N/A        |
| System Quality Number (SQN)| N/A       |
| Kelly Criterion             | N/A       |

### Equity Curve
The equity curve is available, illustrating the growth of the investment over the backtesting period.

## 4. Insights
### Analysis of Performance
- The strategy generated a robust total return of 38.88% over the year, outperforming the buy and hold return of 36.52% on AAPL. This indicates the effectiveness of the buy and hold strategy in capturing the upward trend in AAPL's prices during 2024.
- The annualized return of 39.06% suggests that market conditions were favorable for AAPL, contributing to positive returns.

### Key Takeaways
- Holding AAPL stock for the entire duration yielded significant profits, implying that long-term investing in strong companies can be beneficial.
- A solid Sharpe Ratio of 1.25 indicates that the return obtained was reasonable in relation to the risk taken.

### Areas for Improvement
- The strategy can be expanded by incorporating a set of rules to capture profit-taking opportunities and manage risks more effectively, with an aim to improve upon the existing max drawdown of -15.26%.
- Evaluating the addition of stop-loss and take-profit parameters can provide insights into how these factors could improve the strategy's performance.

## 5. Code
### Description
The backtesting code utilized for this simulation employs a simple buy-and-hold strategy for AAPL stock.

### Implementation
```python
from backtesting import Backtest, Strategy

# Fetch data for backtesting
data = get_ohlcv_data('AAPL', '2024-01-01', '2024-12-31')

# Define the strategy
class MyStrategy(Strategy):
    def init(self):
        pass
    
    def next(self):
        if not self.position:
            self.buy()

# Execute the backtest
bt = Backtest(data, MyStrategy, cash=10000)
stats = bt.run()
print(stats)

# Reporting ...
```

### Reporting Artifacts
- **Trades Table**: No trades were executed during this period.
- **CSV Exports**: The structure for potential trades and equity output is as follows:
  - **TRADES_CSV** format includes: `Size, EntryBar, ExitBar, EntryPrice, ExitPrice, SL, TP, PnL, Commission, ReturnPct, EntryTime, ExitTime, Duration, Tag`
  - **EQUITY_CSV** structure contains: `Equity, DrawdownPct, DrawdownDuration`
  
- **Summary JSON** reflects key performance metrics.
```json
{"end": "2024-12-30 00:00:00", "initial": 10000.0, "equity_final": 13887.789035152855, "portfolio_final": 13887.789035152855, "pnl_abs": 3887.789035152855, "pnl_pct": 38.87789035152855}
```

This report comprehensively analyzes the backtest results of the MyStrategy for AAPL, providing clear insights into performance and areas for strategic enhancement.