# 🎯 NLBT Examples & Showcase

> Natural Language Backtesting - Show, don't tell

## 🚀 Quick Examples

### Example 1: Simple Buy & Hold
```
💭 You: Test a simple buy and hold strategy for Apple stock in 2024 with $10,000
```

**What happens:**
- Agent fetches AAPL data for 2024
- Generates Strategy class with buy-on-first-day logic
- Shows you total return, Sharpe ratio, max drawdown
- Saves detailed report in `reports/`

---

### Example 2: Moving Average Crossover
```
💭 You: Backtest a 50/200 moving average crossover strategy on SPY for the last 2 years with $25,000 capital
```

**What the agent does:**
- Asks for clarification on exact dates
- Writes code using SMA indicators from `ta` library
- Buy when 50-day crosses above 200-day (golden cross)
- Sell when 50-day crosses below 200-day (death cross)
- Shows win rate, number of trades, profit/loss

---

### Example 3: Bollinger Bands Strategy
```
💭 You: I want to trade Tesla with Bollinger Bands. 
        Buy when price touches lower band, sell at upper band.
        Use $15K, test it on 2024 data.
```

**Agent generates:**
- 20-period Bollinger Bands with 2 standard deviations
- Entry signal: price < lower band
- Exit signal: price > upper band
- Full backtest with metrics and equity curve

---

### Example 4: RSI Mean Reversion
```
💭 You: Create an RSI strategy for NVDA. Buy when RSI drops below 30 
        (oversold), sell when RSI goes above 70 (overbought). 
        Test from Jan to Dec 2023 with $20,000.
```

**What you get:**
- RSI indicator calculation (14-period default)
- Mean reversion logic
- Trade-by-trade breakdown
- Performance metrics

---

### Example 5: Multi-Indicator Strategy
```
💭 You: Backtest Microsoft with this strategy:
        - Buy when: MACD crosses above signal line AND RSI < 50
        - Sell when: MACD crosses below signal line OR price drops 5%
        - Capital: $50,000
        - Period: 2024
```

**Agent combines:**
- MACD indicator
- RSI indicator
- Stop loss logic
- Complex entry/exit conditions
- All in one coherent Strategy class

---

### Example 6: Stop Loss & Take Profit
```
💭 You: Test buying Amazon at market open, 
        5% stop loss, 10% take profit, $10K capital, 2024
```

**Features:**
- Risk management built-in
- Automatic position sizing
- Shows risk/reward ratio
- Calculates actual vs theoretical performance

---

### Example 7: Portfolio Comparison
```
💭 You: Compare buy-and-hold performance of AAPL vs GOOGL vs MSFT 
        in 2024 with $10K each
```

**Agent creates:**
- Three separate backtests
- Side-by-side comparison
- Best/worst performer analysis
- Correlation insights

---

## 🎨 Advanced Examples

### Example 8: Seasonal Trading
```
💭 You: Backtest the "Sell in May and go away" strategy on SPY.
        Buy on November 1st, sell on May 1st each year.
        Test from 2020-2024 with $100,000.
```

### Example 9: Volatility Breakout
```
💭 You: Create a volatility breakout strategy for Bitcoin (BTC-USD).
        Buy when daily range exceeds 5% of price.
        Exit after 3 days or 10% profit, whichever comes first.
        Test 2023 with $25K.
```

### Example 10: Sector Rotation
```
💭 You: Test a simple sector rotation: 
        Hold XLK (tech) when it outperforms SPY,
        switch to SPY otherwise.
        Monthly rebalancing, 2023-2024, $50K.
```

---

## 🔥 Power User Examples

### Example 11: Custom Risk Management
```
💭 You: Backtest TSLA with these rules:
        - Buy on any Monday
        - Position size: 2% of portfolio per trade
        - Stop loss: 8% or if price gaps down
        - Take profit: 15%
        - Max 3 positions at once
        - Test 2024 with $100K
```

### Example 12: Event-Driven Strategy
```
💭 You: Test buying the dip on AAPL:
        - Buy when price drops 3% in a single day
        - Hold for exactly 5 trading days
        - Capital: $20K
        - Period: 2024
```

### Example 13: Mean Reversion with Confirmation
```
💭 You: Backtest a mean reversion strategy on QQQ:
        - Entry: Price is 2 standard deviations below 50-day SMA 
                 AND volume is 1.5x average
        - Exit: Price returns to SMA
        - Capital: $30K
        - Test full year 2024
```

---

## 💡 What Makes This Cool?

### 1. **Natural Language → Working Code**
You describe the strategy in plain English, the agent writes professional backtesting code.

### 2. **Any Ticker, Any Strategy**
- US stocks (AAPL, TSLA, GOOGL, etc.)
- ETFs (SPY, QQQ, etc.)
- Even crypto if available on Yahoo Finance (BTC-USD, ETH-USD)

### 3. **Flexible Time Periods**
- "last year"
- "2024"
- "January to March 2023"
- "past 6 months"

### 4. **Rich Indicators Built-In**
- Moving Averages (SMA, EMA)
- Bollinger Bands
- RSI, MACD, Stochastic
- ATR, ADX, OBV
- 100+ indicators from `ta` library

### 5. **Professional Metrics**
Every backtest shows:
- Total Return & CAGR
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Number of Trades
- Average Trade P/L
- Exposure Time

### 6. **Automatic Error Handling**
If the code fails, the agent:
- Sees the error
- Understands what went wrong
- Rewrites the code
- Tries again

---

## 🎓 Learning Examples

### For Beginners
```
💭 You: I'm new to backtesting. Show me the simplest possible strategy on Apple stock.
```

### Understanding Indicators
```
💭 You: Explain and backtest how RSI works using Tesla stock
```

### Risk Management
```
💭 You: Show me the difference between a strategy with and without stop losses on NVDA
```

---

## 📊 Output Examples

Each backtest generates:

```markdown
# Backtest Report

## Results
=== Backtest Metrics ===
Initial Capital: $10,000.00
Final Capital: $12,450.00
Total Return: 24.50%
CAGR: 24.50%
Sharpe Ratio: 1.23
Max Drawdown: -8.45%
Total Trades: 23
Win Rate: 65.2%
Average Trade: $106.52

## Code
[Full Python code included for reproducibility]

Generated by NLBT
```

---

## 🚀 Try These Now!

**Beginner:**
```bash
python -m nlbt.cli
> buy and hold Tesla for 2024 with $10K
```

**Intermediate:**
```bash
python -m nlbt.cli
> test a 20/50 MA crossover on Apple, 2024, $25K
```

**Advanced:**
```bash
python -m nlbt.cli
> backtest a mean reversion strategy: buy NVDA when it drops 5% in a day 
  and RSI < 30, sell when it rises 8% or after 10 days, $50K, 2024
```

---

## 🎯 Pro Tips

1. **Be specific about dates**: "2024" is better than "last year"
2. **Mention capital upfront**: Saves a back-and-forth
3. **Use standard indicator names**: "RSI", "Bollinger Bands", "MACD"
4. **Ask for help**: "Explain this strategy" or "What's wrong with this approach?"
5. **Iterate**: Start simple, then add complexity

---

## 🔮 What's Possible

This is just scratching the surface. The agent can:
- ✅ Combine multiple indicators
- ✅ Implement complex entry/exit logic
- ✅ Handle position sizing and risk management
- ✅ Test on any US stock or ETF
- ✅ Generate publication-ready reports
- ✅ Compare multiple strategies
- ✅ Optimize parameters (just ask!)

**The only limit is your imagination!** 🚀

