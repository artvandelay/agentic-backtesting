# ⚡ Quick Start Guide

## 30-Second Setup

```bash
# 1. Install
pip install -e .

# 2. Configure LLM (one time)
llm keys set openrouter  # or your provider
llm models default gpt-4o-mini

# 3. Run
nlbt chat
```

## 60-Second First Backtest

```bash
nlbt chat --model gpt-4o-mini
```

```
💭 You: Buy and hold Apple in 2024 with $10K

🤔 Agent: [Generates code, executes, shows results]

=== Backtest Metrics ===
Initial Capital: $10,000.00
Final Capital: $12,341.00
Total Return: 23.41%
...

Report saved to: reports/...
```

**Done!** Your first backtest complete in under a minute.

---

## Command Cheat Sheet

```bash
nlbt chat              # Start chat
nlbt chat -m gpt-4o    # Specify model
nlbt info              # System info
```

### In-Chat Commands
```
exit     # Quit
info     # Show current phase & requirements
info     # Session info
```

---

## Strategy Templates

### 1. Buy & Hold
```
Buy and hold [TICKER] in [YEAR] with $[AMOUNT]
```

### 2. Moving Average
```
Test [20/50] MA crossover on [TICKER] for [YEAR] with $[AMOUNT]
```

### 3. Bollinger Bands
```
Backtest [TICKER] with Bollinger Bands: 
buy at lower band, sell at upper band, 
[YEAR], $[AMOUNT]
```

### 4. RSI Strategy
```
Create RSI strategy for [TICKER]:
buy when RSI < 30, sell when RSI > 70,
[YEAR], $[AMOUNT]
```

### 5. Stop Loss & Take Profit
```
Buy [TICKER], [X]% stop loss, [Y]% take profit,
[YEAR], $[AMOUNT]
```

### 6. Multi-Indicator
```
Backtest [TICKER]:
- Buy when: [CONDITION 1] AND [CONDITION 2]
- Sell when: [CONDITION 3] OR [CONDITION 4]
[YEAR], $[AMOUNT]
```

---

## Common Indicators

| Indicator | Name | Use Case |
|-----------|------|----------|
| SMA/EMA | Moving Average | Trend following |
| RSI | Relative Strength | Overbought/oversold |
| MACD | Moving Avg Conv/Div | Momentum & trend |
| BB | Bollinger Bands | Volatility & mean reversion |
| ATR | Average True Range | Volatility measurement |
| Stochastic | Stochastic Oscillator | Momentum |
| OBV | On-Balance Volume | Volume analysis |

---

## Tips & Tricks

### ✅ DO
- Be specific: "2024" not "last year"
- Mention capital upfront
- Use standard indicator names
- Ask for help when stuck
- Start simple, iterate

### ❌ DON'T
- Use vague dates like "recently"
- Forget to mention capital
- Overcomplicate first try
- Expect perfection on try #1

---

## Troubleshooting

### "Unknown model" error
```bash
llm models list  # See available models
llm models default [model-name]
```

### "No data found" error
- Check ticker symbol (use Yahoo Finance format)
- Verify date range is in the past
- Try different dates

### "Execution failed" error
- Agent will try to auto-fix
- If not, simplify your strategy
- Check for typos in ticker/dates

---

## Next Steps

1. ✅ Run your first backtest (see 60-second guide above)
2. 📚 Read [EXAMPLES.md](EXAMPLES.md) for inspiration
3. 💬 Check [scripts/example_sessions.md](scripts/example_sessions.md) for real conversations
4. 🚀 Build your own strategies!

---

## Quick Demo

```bash
./scripts/demo.sh
```

This launches the CLI with example queries shown.

---

## Help & Support

- 📖 Full docs: [README.md](README.md)
- 🎯 Examples: [EXAMPLES.md](EXAMPLES.md)
- 💬 Sessions: [scripts/example_sessions.md](scripts/example_sessions.md)
- 🐛 Issues: Open a GitHub issue

**Happy backtesting!** 🚀

