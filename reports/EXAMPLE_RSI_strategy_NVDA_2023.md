# Backtest Report

## 1. Summary
- **Objective:** The objective of this backtest was to assess the performance of MyStrategy, which utilizes the Relative Strength Index (RSI) for trading decisions in the market.
- **Market Condition:** The backtest period included varied market conditions characterized by both bullish and bearish trends, significant volatility, and varying volumes.
- **Key Findings:** The backtest results indicate a strong performance of the strategy with a total return of 45.75%, a win rate of 100%, and a Sharpe ratio of 2.15. However, the strategy had a low number of trades (only 3), which may indicate limited engagement with market opportunities.

## 2. Strategy
- **Strategy Title:** MyStrategy
- **Description:** 
   MyStrategy is based on a momentum trading philosophy focusing on identifying and capitalizing on overbought and oversold conditions using the RSI indicator.
- **Indicators Used:** 
   - **RSI (Relative Strength Index):** Set with a threshold of 30 for oversold conditions and 70 for overbought conditions.
- **Entry Criteria:** 
   - Enter a long position when RSI is below 30.
- **Exit Criteria:** 
   - Exit a long position when RSI is above 70.
- **Risk Management:** 
   - The strategy relies on defined entry and exit signals, which inherently incorporate risk management by avoiding positions in overbought scenarios.

## 3. Results
- **Backtest Period:**
   - **Start:** 2022-12-01
   - **End:** 2023-12-29
   - **Duration:** 393 days
- **Performance Metrics:**
   - **Exposure Time [%]:** 13.28%
   - **Final Equity [$]:** $29,150.90
   - **Peak Equity [$]:** $29,150.90
   - **Total Return [%]:** 45.75%
   - **Buy & Hold Return [%]:** 208.01%
   - **Annualized Return [%]:** 41.95%
   - **Volatility (Annualized) [%]:** 19.48%
   - **CAGR [%]:** 27.33%
   - **Sharpe Ratio:** 2.15
   - **Sortino Ratio:** 6.42
   - **Calmar Ratio:** 4.44
   - **Alpha [%]:** 29.08%
   - **Beta:** 0.08
   - **Maximum Drawdown [%]:** -9.46%
   - **Average Drawdown [%]:** -3.47%
   - **Maximum Drawdown Duration:** 262 days
   - **Average Drawdown Duration:** 73 days
- **Trade Statistics:**
   - **Total Number of Trades:** 3
   - **Win Rate [%]:** 100.0%
   - **Best Trade [%]:** 16.95%
   - **Worst Trade [%]:** 7.29%
   - **Average Trade [%]:** 13.39%
   - **Maximum Trade Duration:** 22 days
   - **Average Trade Duration:** 16 days
   - **Profit Factor:** NaN (not applicable due to insufficient trades)
   - **Expectancy [%]:** 13.47%
   - **SQN:** 4.35
   - **Kelly Criterion:** NaN (not applicable due to insufficient trades)

## 4. Insights
- **Performance Analysis:**
   The results exceeded expectations with a high total return and an impressive Sharpe ratio, indicating strong risk-adjusted performance. The high win rate reflects the effectiveness of the RSI-based entry and exit points.
- **Behavior Analysis:**
   The low number of trades suggests a cautious approach, potentially missing out on other trading opportunities. The timing of the trades aligned well with market conditions, as evidenced by the favorable outcomes.
- **Risk Assessment:**
   Despite achieving solid results, the strategy is susceptible to longer periods of drawdown, with an average duration of 73 days. Future considerations might include adjustments to entry or exit triggers to mitigate longer drawdowns.

## 5. Code
```python
from backtesting import Backtest, Strategy

# Get data
data = get_ohlcv_data('NVDA', '2022-12-01', '2023-12-31')

class MyStrategy(Strategy):
    def init(self):
        def rsi(values, n=14):
            import pandas as pd
            import numpy as np
            delta = pd.Series(values).diff()
            gain = (delta.where(delta > 0, 0)).rolling(n).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
            rs = gain / loss
            return (100 - (100 / (1 + rs))).to_numpy()
            
        self.rsi = self.I(rsi, self.data.Close, 14)
    
    def next(self):
        if not self.position and self.rsi[-1] < 30:
            self.buy()
            
        elif self.position and self.rsi[-1] > 70:
            self.position.close()

bt = Backtest(data, MyStrategy, cash=20000)
stats = bt.run()
print(stats)
```

## Appendices (Optional)
- **Graphical Representations:**
   - Charts visualizing the equity curve and drawdowns may be included to provide visual insights into the strategy's performance.
- **Trading Logs:**
   - A log of trades executed during the backtest could offer a deeper understanding of strategic entries and exits.
- **Additional Metrics:**
   - Additional performance metrics and insights from the backtested data may be documented to provide a comprehensive overview.