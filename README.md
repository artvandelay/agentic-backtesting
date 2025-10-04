# NLBT — Natural Language Backtesting (WIP)

**Turn plain English into professional backtesting reports in minutes.**

Describe any trading strategy in natural language → Get Python code, backtest results, and a professional markdown report. No coding required.

**Cost**: <$1 to run all examples with OpenRouter  
**Time**: 2-3 minutes per strategy  
**Output**: Professional reports with metrics, code, and insights

## ⚠️ Safety Warning
**This tool runs generated Python code locally. Do not paste untrusted code or run on sensitive systems.**

## What You Get

**Input**: "Buy and hold AAPL in 2024 with $10,000"  
**Output**: Professional report with:
- 📊 Performance metrics (38.88% return, Sharpe 1.25, Max DD -15.26%)
- 📈 Full backtest results and analysis  
- 💻 Complete Python code for reproducibility
- 📄 Markdown report ready to share

**Sample outputs**: See `reports/EXAMPLE_*.md` for actual generated reports.

## Status
- WIP; APIs, prompts, and behavior may change without notice
- Expect errors; contributions and test reports welcome

## Requirements
- Python 3.8+
- OpenRouter account (recommended) or OpenAI/Anthropic
- 5 minutes for setup

## Install & Setup

### 1. Clone and install everything
```bash
git clone https://github.com/artvandelay/agentic-backtesting
cd agentic-backtesting
pip install -e .
```
*This installs all dependencies including `llm` CLI and `python-dotenv`*

### 2. Set up OpenRouter (recommended)
**Why OpenRouter?** Cost control, multiple models, spending limits

1. **Create account**: Go to https://openrouter.ai/
2. **Get API key**: Click "Keys" → "Create Key" 
3. **Add credits**: Add $5-10 (you'll use <$1 for examples)
4. **Set spending limit**: Optional but recommended
5. **Configure locally**:
```bash
llm keys set openrouter
# Paste your API key when prompted

llm models default openrouter/anthropic/claude-3.5-sonnet
```

### 3. Quick test
```bash
nlbt
```
**Try**: "Buy and hold AAPL in 2024 with $1000"

**What you should see**:
- Agent asks clarifying questions (if needed)
- Shows "Phase 1 - Understanding" → "Phase 2 - Implementation" → "Phase 3 - Reporting"  
- Saves report to `reports/backtest_YYYYMMDD_HHMMSS.md`
- Takes 2-3 minutes total

## How it works (3-phase conversation)

**Phase 1 - Understanding**: Agent gathers requirements:
- Ticker symbol (e.g., AAPL, SPY)
- Time period (e.g., "2024", "2020-2023") 
- Capital amount (e.g., "$10,000")
- Strategy description (your trading rules)

**Phase 2 - Implementation**: Agent generates Python code, runs it in sandbox, critiques results. Auto-retries up to 3 times if errors occur.

**Phase 3 - Reporting**: Agent plans and writes a professional markdown report with metrics and full code.

## Use
```bash
nlbt                    # Start interactive session
```

**In-chat commands:**
- `info` - Show current phase and gathered requirements
- `debug` - Show internal state for troubleshooting  
- `exit` - Quit

### I'm feeling lucky (no setup)
- Type `lucky` to run a built-in demo without any LLM calls.  
  It runs a Buy & Hold AAPL (2024, $10,000) backtest and saves a report to `reports/lucky_YYYYMMDD_HHMMSS.md`.

Reports are written to `reports/backtest_YYYYMMDD_HHMMSS.md`.

### India-friendly input
- Tickers: common aliases map to Yahoo Finance symbols (e.g., `reliance` → `RELIANCE.NS`, `tcs` → `TCS.NS`, `nifty` → `^NSEI`).
- Capital: accepts rupees (`₹10,00,000`, `INR 500000`) and dollars (`$10,000`).
- Language: set summary language via `lang hi`, `lang gu`, or `lang en` (default `en`).

### Reports output
- Each run saves under `reports/<TICKER>_<PERIOD>_<TIMESTAMP>/report.md`.
- If trades are present, the report includes a small `Trades` table (first 20 rows).

## Examples (realistic conversations)

**Simple Buy & Hold**
```
💭 You: Buy and hold AAPL in 2024 with $10,000
🤖 Agent: STATUS: READY - I have everything needed. Ready to proceed?
💭 You: yes
⚙️ Agent: [Generates code → executes → ✓] 
📊 Agent: [Writes report → saves to reports/]
✅ Report saved: reports/backtest_20241002_123456.md
```

**RSI Strategy** 
```
💭 You: Create RSI strategy for NVDA: buy when RSI < 30, sell when RSI > 70, 2023, $20,000
🤖 Agent: STATUS: READY - All requirements complete!
💭 You: go
⚙️ Agent: [Implementation → 45.75% return, 100% win rate]
📊 Agent: [Professional report with insights]
```

**If agent needs more info**:
```
💭 You: Test a moving average strategy
🤖 Agent: What ticker symbol? What time period? What capital amount? What MA periods?
💭 You: SPY, 2024, $25K, use 50/200 day crossover  
🤖 Agent: Perfect! Ready to proceed?
```

## Troubleshooting

### "Unknown model" error
```bash
llm models list                    # See available models
llm models default [model-name]    # Set default
```

### "LLM failed" or timeout
- Check API key: `llm keys list`
- Check OpenRouter credits/limits
- Try simpler strategy description
- Use `debug` command to see internal state

### "No data found" error  
- Verify ticker symbol (use Yahoo Finance format)
- Ensure date range is in the past
- Try different dates or ticker

### Code execution fails
- Agent will auto-retry up to 3 times
- If still failing, simplify your strategy
- Use `info` to see what requirements were gathered
- Check for typos in ticker/dates

### General debugging
- Use `info` command to see current phase
- Use `debug` command to see conversation history
- Check `reports/` folder for any partial outputs
- Restart with `exit` and try again

## Alternative LLM Providers

**OpenAI**:
```bash
llm keys set openai
llm models default gpt-4o-mini
```

**Anthropic**:
```bash
llm keys set anthropic  
llm models default claude-3-5-sonnet-20241022
```

## Project structure
```
src/nlbt/
├── cli.py          # Minimal CLI
├── llm.py          # LLM wrapper using `llm` CLI
├── reflection.py   # 3‑phase engine
├── sandbox.py      # Simple executor with data helper
└── __init__.py
```

## Developer notes
See `REPO_NOTES.md` for architecture, features, design principles, and roadmap.

## License
GPL-3.0-only. See `LICENSE`.