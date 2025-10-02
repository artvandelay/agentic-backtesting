# NLBT — Natural Language Backtesting (WIP)

Experimental, work‑in‑progress tool. Not verified or production‑ready.

Describe a trading strategy in plain English. NLBT uses the `llm` CLI (Simon Willison) to:
- Ask clarifying questions
- Generate Python backtesting code
- Run it locally and save a markdown report in `reports/`

## Status
- WIP; APIs, prompts, and behavior may change without notice
- Expect errors; contributions and test reports welcome

## Requirements
- Python 3.8+
- `llm` CLI and an API key (OpenAI, Anthropic, or OpenRouter)

## Install
```bash
git clone https://github.com/artvandelay/agentic-backtesting
cd agentic-backtesting
pip install -e .
```

### Configure
```bash
# LLM
llm keys set openrouter           # or: openai, anthropic
llm models default openrouter/anthropic/claude-3.5-sonnet

# Environment
cp env.example .env               # optional; can set LLM_MODEL
```

## Use
```bash
nlbt
```
Reports are written to `reports/backtest_YYYYMMDD_HHMMSS.md`.

## Examples (curated)

Buy & Hold
```
💭 You: Buy and hold AAPL in 2024 with $10,000
```

Moving Average Crossover
```
💭 You: Backtest a 50/200 day MA crossover on SPY for 2024 with $25,000
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

## How it works
- Phase 1 (Understanding): conversational requirement gathering until STATUS: READY
- Phase 2 (Implementation): generate Python, run in a sandbox, critique; up to 3 attempts
- Phase 3 (Reporting): plan → write → save a professional markdown report

## Project structure
```
src/nlbt/
├── cli.py          # Minimal CLI
├── llm.py          # LLM wrapper using `llm` CLI
├── reflection.py   # 3‑phase engine
├── sandbox.py      # Simple executor with data helper
└── __init__.py
```

## Safety
- Runs generated code locally; do not paste untrusted code

## Developer notes
See `REPO_NOTES.md` for architecture, features, design principles, and roadmap.

## License
GPL-3.0-only. See `LICENSE`.
