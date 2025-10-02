# NLBT Documentation

This document consolidates quick start info, example highlights, rebuild notes, and repo guidance for the main branch.

## Quick Start

See `README.md` for installation and usage. The CLI command is `nlbt`.

## Examples

See `EXAMPLES.md` on the `dev` branch for the full set of examples. Highlights include:
- Buy & Hold
- Moving Average Crossover
- Bollinger Bands
- RSI strategies
- Stop Loss & Take Profit
- Multi-Indicator strategies

## Rebuild Notes

Minimal reflection engine:
- Modules: `llm.py`, `sandbox.py`, `reflection.py`, `cli.py`
- Phases: Understanding → Implementation → Reporting
- Reports saved to `reports/`

## Repository Guidance

- Keep `reports/` out of version control on `main`
- Use `dev` for detailed notes and design docs
- README stays concise; `DOCS.md` links to deep content on `dev`

## License

GPL-3.0-only. See `LICENSE`.
