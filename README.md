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

## Project structure
```
src/nlbt/
├── cli.py          # Minimal CLI
├── llm.py          # LLM wrapper using `llm` CLI
├── reflection.py   # 3‑phase engine
├── sandbox.py      # Simple executor with data helper
└── __init__.py
```

## Notes
- Runs generated code locally; do not paste untrusted code
- Repo contains WIP docs in root and `cursor_chats/` for context

## License
GPL-3.0-only. See `LICENSE`.
