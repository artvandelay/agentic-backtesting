# NLBT — Natural Language Backtesting (WIP)

Experimental, work‑in‑progress tool. Not verified or production‑ready.

Describe a trading strategy in plain English. NLBT uses the `llm` CLI (Simon Willison) to:
- Ask clarifying questions
- Generate Python backtesting code
- Run it locally and save a markdown report in `reports/`

## ⚠️ Safety Warning
**This tool runs generated Python code locally. Do not paste untrusted code or run on sensitive systems.**

## Status
- WIP; APIs, prompts, and behavior may change without notice
- Expect errors; contributions and test reports welcome

## Requirements
- Python 3.8+
- `llm` CLI and an API key (OpenAI, Anthropic, or OpenRouter)

## Install

### 1. Clone and install
```bash
git clone https://github.com/artvandelay/agentic-backtesting
cd agentic-backtesting
pip install -e .
```

### 2. Install additional dependencies
```bash
pip install llm python-dotenv
```

### 3. Configure LLM provider
```bash
# Recommended: OpenRouter (cost control, multiple models)
llm keys set openrouter
llm models default openrouter/anthropic/claude-3.5-sonnet

# Alternatives:
# llm keys set openai
# llm keys set anthropic
```

**Cost note**: Running all examples costs <$1 with OpenRouter. Set spending limits in your provider dashboard.

### 4. Optional: Environment setup
```bash
cp env.example .env
# Edit .env to set LLM_MODEL if desired
```

### 5. Quick test
```bash
nlbt
# Try: "Buy and hold AAPL in 2024 with $1000"
# Should ask clarifying questions, generate code, save report
```

## Use
```bash
nlbt                    # Start interactive session
```

**In-chat commands:**
- `info` - Show current phase and gathered requirements
- `debug` - Show internal state for troubleshooting  
- `exit` - Quit

Reports are written to `reports/backtest_YYYYMMDD_HHMMSS.md`.

## How it works (3-phase conversation)

**Phase 1 - Understanding**: Agent asks questions until it has:
- Ticker symbol (e.g., AAPL, SPY)
- Time period (e.g., "2024", "2020-2023") 
- Capital amount (e.g., "$10,000")
- Strategy description (your trading rules)

**Phase 2 - Implementation**: Agent generates Python code, runs it in sandbox, critiques results. Up to 3 attempts if errors occur.

**Phase 3 - Reporting**: Agent plans and writes a professional markdown report with metrics and full code.

## Examples (curated)

Buy & Hold
```
💭 You: Buy and hold AAPL in 2024 with $10,000
🤖 Agent: I have everything needed. Ready to proceed? (yes/go)
💭 You: yes
⚙️ Agent: [Generates code → executes → ✓]
📊 Agent: [Writes report → saves to reports/]
```

Moving Average Crossover
```
💭 You: Backtest a 50/200 day MA crossover on SPY for 2024 with $25,000
🤖 Agent: [Same flow - understand → implement → report]
```

Bollinger Bands
```
💭 You: Test TSLA with Bollinger Bands in 2024, buy lower band, sell upper band, $15,000
```

RSI Mean Reversion
```
💭 You: Create RSI strategy for NVDA: buy when RSI < 30, sell when RSI > 70, 2023, $20,000
```

More: see developer notes in `REPO_NOTES.md`.

## Troubleshooting

### "Unknown model" error
```bash
llm models list                    # See available models
llm models default [model-name]    # Set default
```

### "LLM failed" or timeout
- Check API key: `llm keys list`
- Try simpler strategy description
- Use `debug` command to see internal state
- Check rate limits with your provider

### "No data found" error  
- Verify ticker symbol (use Yahoo Finance format)
- Ensure date range is in the past
- Try different dates or ticker

### Code execution fails
- Agent will auto-retry up to 3 times
- If still failing, simplify your strategy
- Check for typos in ticker/dates
- Use `info` to see what requirements were gathered

### General debugging
- Use `info` command to see current phase
- Use `debug` command to see conversation history
- Check `reports/` folder for any partial outputs
- Restart with `exit` and try again

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