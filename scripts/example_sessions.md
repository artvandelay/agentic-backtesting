# 📝 Real Example Sessions

> Actual conversations showing what NLBT can do

## Session 1: Complete Beginner

```
💭 You: I want to test a strategy but I'm new to this

🤔 Agent: No problem! Let me help you get started. To create a backtest, I'll need:

1. Which stock do you want to test? (e.g., AAPL for Apple, TSLA for Tesla)
2. What's your strategy? (e.g., "buy and hold", "buy when price drops")
3. How much money would you invest? (e.g., $10,000)
4. What time period? (e.g., "2024", "last year")

What would you like to try?

💭 You: Let's try Apple, just buy and hold, $10K, test it on 2024

🤔 Agent: Perfect! Here's your backtest...

[Agent generates and runs code]

🤔 Agent: Backtest complete!

=== Backtest Metrics ===
Initial Capital: $10,000.00
Final Capital: $12,341.00
Total Return: 23.41%
CAGR: 23.41%
Sharpe Ratio: 1.45
Max Drawdown: -12.30%

Report saved to: reports/abc123_20250101_120000.md

Your buy-and-hold strategy would have gained $2,341 (23.41%) in 2024!
```

---

## Session 2: Bollinger Bands Strategy

```
💭 You: Backtest Bollinger Bands on Tesla for 2024 with 10K

🤔 Agent: Great! A few questions about your Bollinger Bands strategy:

1. What period for the moving average? (typically 20 days)
2. How many standard deviations? (typically 2)
3. Entry signal: Buy when price touches which band? (lower/upper)
4. Exit signal: Sell when price touches which band? (lower/upper)

💭 You: Use standard settings (20 and 2). Buy when price hits lower band, sell at upper band.

🤔 Agent: Perfect! Running backtest...

[Generates code with Bollinger Bands using ta library]

🤔 Agent: Backtest complete!

=== Backtest Metrics ===
Initial Capital: $10,000.00
Final Capital: $11,850.00
Total Return: 18.50%
CAGR: 18.50%
Sharpe Ratio: 0.92
Max Drawdown: -15.67%
Total Trades: 47
Win Rate: 55.3%
Average Trade: $39.36

Your Bollinger Bands strategy made 47 trades with a 55% win rate!
Report saved to: reports/def456_20250101_120500.md
```

---

## Session 3: Risk Management Focus

```
💭 You: I want to test a strategy with strict risk management on NVDA

🤔 Agent: Excellent! Risk management is crucial. Tell me:

1. What's your entry strategy? (e.g., "buy on dips", "breakout", etc.)
2. Stop loss percentage or amount?
3. Take profit target?
4. Position sizing? (% of portfolio per trade)
5. Time period and capital?

💭 You: Buy when stock drops 3% in a day. 5% stop loss, 12% take profit. 
       Risk 2% per trade. Test on 2024 with $50K.

🤔 Agent: Great risk management! Let me code this up...

[Generates strategy with proper position sizing and risk controls]

🤔 Agent: Backtest complete!

=== Backtest Metrics ===
Initial Capital: $50,000.00
Final Capital: $58,920.00
Total Return: 17.84%
CAGR: 17.84%
Sharpe Ratio: 1.67
Max Drawdown: -6.23%
Total Trades: 28
Win Rate: 64.3%
Average Trade: $318.57
Max Risk Per Trade: $1,000 (2%)

Your risk-managed strategy limited drawdown to just 6.23% while gaining 17.84%!
Stop loss triggered: 10 times (saved you from bigger losses)
Take profit hit: 18 times (captured gains)

Report saved to: reports/ghi789_20250101_121000.md
```

---

## Session 4: Multi-Indicator Strategy

```
💭 You: Create a complex strategy for Microsoft:
       - Buy when: 50-day MA crosses above 200-day MA AND RSI is below 60
       - Sell when: 50-day MA crosses below 200-day MA OR price drops 8%
       - Test 2023-2024 with $25,000

🤔 Agent: Interesting multi-condition strategy! This combines:
- Golden Cross/Death Cross (MA crossover)
- RSI filter to avoid overbought entries
- Stop loss for protection

Running backtest...

[Generates comprehensive strategy with all conditions]

🤔 Agent: Backtest complete!

=== Backtest Metrics ===
Initial Capital: $25,000.00
Final Capital: $31,450.00
Total Return: 25.80%
CAGR: 12.19% (annualized over 2 years)
Sharpe Ratio: 1.34
Max Drawdown: -9.12%
Total Trades: 8
Win Rate: 75.0%
Average Trade: $806.25
Exposure: 67% (in market 67% of the time)

Your multi-indicator approach had high win rate (75%) with only 8 trades.
The MA crossover filter kept you out of choppy markets.
RSI filter helped avoid buying into overbought conditions.

Report saved to: reports/jkl012_20250101_121500.md
```

---

## Session 5: Strategy Comparison

```
💭 You: I want to compare three strategies on SPY for 2024:
       1. Buy and hold
       2. 50/200 MA crossover
       3. RSI mean reversion (buy <30, sell >70)
       All with $20K

🤔 Agent: Great idea to compare! I'll run all three and show you the results.

[Runs three separate backtests]

🤔 Agent: Comparison Results:

**Strategy 1: Buy and Hold**
- Return: 19.2%
- Sharpe: 1.52
- Max DD: -8.3%
- Trades: 1

**Strategy 2: MA Crossover**
- Return: 14.7%
- Sharpe: 1.12
- Max DD: -6.1%
- Trades: 6

**Strategy 3: RSI Mean Reversion**
- Return: 22.5%
- Sharpe: 1.38
- Max DD: -11.2%
- Trades: 34

**Winner: RSI Mean Reversion** (highest return)
**Safest: MA Crossover** (lowest drawdown)
**Simplest: Buy and Hold** (fewest trades, good Sharpe)

Key Insights:
- Buy-and-hold worked well in 2024's uptrend
- MA crossover reduced drawdown but missed some gains
- RSI strategy had best returns but more trades and higher drawdown

Reports saved to: reports/comparison_*_20250101_122000.md
```

---

## Session 6: Learning & Iteration

```
💭 You: Test a momentum strategy on Tesla but I'm not sure how to define it

🤔 Agent: No problem! Momentum strategies typically buy when price is trending up. 
Here are some options:

1. **Price-based**: Buy when price makes a new 20-day high
2. **MA-based**: Buy when price is above rising moving average
3. **ROC-based**: Buy when Rate of Change is positive
4. **Mixed**: Combine multiple momentum signals

Which approach interests you? Or I can test a standard one to show you how it works.

💭 You: Show me the MA-based one

🤔 Agent: Perfect! I'll create a strategy that:
- Buys when price is above 50-day MA AND the MA is sloping upward
- Sells when price drops below the MA

Testing on TSLA 2024 with $15K...

[Runs backtest]

🤔 Agent: Results for MA-based momentum:

Initial: $15,000
Final: $18,750
Return: 25.0%
Trades: 12
Win Rate: 58.3%

Now, would you like to try tweaking it? We could:
- Change the MA period (try 30 or 100 days)
- Add a stop loss
- Add an RSI filter
- Test a different year

💭 You: Let's add a 7% stop loss

🤔 Agent: Good idea! Adding risk management...

[Runs modified backtest]

🤔 Agent: With 7% stop loss added:

Initial: $15,000  
Final: $17,250 (vs $18,750 without stop)
Return: 15.0% (vs 25.0%)
Max DD: -8.5% (vs -16.2%)
Trades: 15 (vs 12)

Trade-off analysis:
- Lower returns (gave up 10%)
- Much safer (half the drawdown)
- More trades (stop loss triggered 3 times)

The stop loss protected you during Tesla's volatile periods!
Which version do you prefer?
```

---

## Key Takeaways

1. **Start Simple**: Begin with basic strategies to understand the flow
2. **Be Specific**: More detail = better results
3. **Iterate**: Test, analyze, refine, repeat
4. **Ask Questions**: The agent can explain concepts and suggest improvements
5. **Compare**: Run multiple variations to find what works

**Ready to try?** Run `./scripts/demo.sh` to start!

