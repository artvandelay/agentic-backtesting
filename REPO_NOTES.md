# REPO NOTES — Architecture, Features, and Roadmap

This document consolidates developer‑facing notes from root markdown files.

## Architecture

Three‑phase reflection engine:
- Phase 1: Understanding — requirement extraction via LLM prompts
- Phase 2: Implementation — producer code generation → sandbox execution → critic evaluation
- Phase 3: Reporting — plan → write markdown → save to `reports/`

Key modules:
- `src/nlbt/llm.py`: LLM wrapper using `llm` CLI; loads `.env` if present
- `src/nlbt/sandbox.py`: Minimal executor; exposes `get_ohlcv_data()` using yfinance
- `src/nlbt/reflection.py`: Orchestrates phases, generates code and report
- `src/nlbt/cli.py`: Minimal CLI entry point (`nlbt`)

## Features (current)
- Natural‑language backtest requests
- Minimal prompt flow for requirement gathering
- Code generation for `backtesting.py` strategies
- Indicator patterns using `ta` library
- Markdown report with results and code

## Design principles
- Minimal, simple code — avoid overengineering
- Prefer clear errors to heavy validation
- Keep user‑facing CLI straightforward
- Local execution; never run untrusted code

## Known limitations
- Experimental prompts; may fail or need retries
- Sandbox is minimal; not hardened for untrusted code
- No session persistence or web UI (yet)

## Rebuild notes (summary)
- Single‑file focus per concern (cli, llm, sandbox, engine)
- Simplified error handling; rely on natural failures
- Reports saved to `reports/` for traceability

## Dev references
- Examples: `EXAMPLES.md` (full showcase)
- Quick start snippets: `QUICK_START.md`
- Sessions: `scripts/example_sessions.md`
- Additional design notes: `REPO_CONTENT.md`, `REBUILD_NOTES.md`

## Roadmap (suggested)
- Improve prompt robustness and retries
- Add simple session persistence
- Optional: basic UI for running conversations
- Optional: curated examples runner script

## License
GPL‑3.0‑only. See `LICENSE`.
