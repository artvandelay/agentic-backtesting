# NLBT - Agentic Natural Language Backtesting Sandbox

A conversational, agentic system for backtesting trading strategies described in natural language. Uses the `llm` CLI (by Simon Willison) for model access.

## Features

- **Natural Language Strategy Description**: Describe strategies in plain English
- **Agentic Workflow**: AI agent asks clarifying questions, writes code, executes backtests
- **Multi-turn Conversations**: Session-based chat with full history
- **Safe Code Execution**: Sandboxed environment with financial tools preloaded
- **Flexible Data Sources**: Yahoo Finance integration with caching
- **Rich Reports**: Markdown reports with metrics and visualizations

## Quick Start

### Prerequisites

1. **Install `llm` CLI** (Simon Willison's tool):
   ```bash
   pip install llm
   ```

2. **Configure your LLM provider** (e.g., OpenRouter):
   ```bash
   llm keys set openrouter
   llm models default openrouter/anthropic/claude-3.5-sonnet
   ```

### Installation

```bash
# Clone and install
git clone <repo-url>
cd evaluate-trading-strategy
pip install -e .

# Or install dependencies directly
pip install llm backtesting pandas numpy ta yfinance python-dotenv
```

### Configuration

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` to set your preferences:
```bash
LLM_MODEL=claude-3-5-sonnet-20241022
CACHE_DIR=.cache
DEFAULT_TIMEOUT=60
MAX_RETRY_ATTEMPTS=5
MAX_AGENT_ITERATIONS=20
```

### Usage

Start a chat session:
```bash
nlbt
```

**How it works:**
- **Phase 1:** Agent asks questions until it has complete info
- **Phase 2:** Agent writes code, tests it, critiques it, refines it
- **Phase 3:** Agent plans and writes a professional report

**Example conversation:**
```
💭 You: Test a moving average strategy on Apple

🔍 Agent: What time period and capital? What MA periods?

💭 You: 2024, $10K, use 50/200 day crossover

⚙️ Agent: [Generates code → executes → critiques → ✓]

📊 Agent: [Plans report → writes → refines → ✓]
       
✅ Report saved to: reports/session_xyz.md
```

**Key Features:**
- ✅ Agent decides when it has enough information
- ✅ Self-correcting code generation (Producer-Critic pattern)
- ✅ Professional reports with insights
- ✅ Based on Agentic Design Patterns (Reflection)

## Architecture

**Three-Phase Reflection Engine:**
- **Phase 1 (Understanding):** LLM-driven requirement gathering
- **Phase 2 (Implementation):** Producer-Critic code generation loop
- **Phase 3 (Reporting):** Plan → Write → Refine workflow

**Components:**
- **LLM Client**: Model-agnostic (uses `llm` CLI)
- **Sandbox**: Safe code execution with financial libraries
- **Data Layer**: Yahoo Finance with caching
- **Report Renderer**: Professional markdown reports

## Sandbox Environment

The agent generates code with access to:
- **Data:** `get_ohlcv_data(ticker, start, end)` - Fetch price data
- **Backtesting:** `from backtesting import Backtest, Strategy`
- **Indicators:** `ta` library (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
- **Analysis:** `pandas`, `numpy`, `matplotlib`, `plotly`
- **Helpers:** `calculate_returns()`, `print_metrics()`, etc.

## 🎯 Examples

### Quick Start
```bash
💭 You: Buy and hold Apple stock in 2024 with $10,000
🤔 Agent: [Generates code, runs backtest, shows results]
```

### Bollinger Bands
```bash
💭 You: Test Tesla with Bollinger Bands strategy in 2024 using $15K
🤔 Agent: [Asks for parameters, generates strategy, executes]
```

### Moving Average Crossover
```bash
💭 You: Backtest 50/200 day MA crossover on SPY for 2024 with $25K
🤔 Agent: [Creates golden cross/death cross strategy]
```

### Multi-Indicator Strategy
```bash
💭 You: Test Microsoft: buy when MACD crosses up AND RSI < 50, 
        sell when MACD crosses down, 2024, $50K
🤔 Agent: [Combines indicators, generates complex strategy]
```

**See [EXAMPLES.md](EXAMPLES.md) for 13+ detailed examples!**  
**See [scripts/example_sessions.md](scripts/example_sessions.md) for real conversations!**

## Development

### Running Tests
```bash
pytest -q  # with progress bar
```

### Code Quality
```bash
ruff check src/
black src/
mypy src/
```

## Project Structure

```
src/nlbt/
├── cli.py          # Minimal CLI (uses llm CLI)
├── llm.py          # Minimal LLM wrapper
├── reflection.py   # 3-phase reflection engine
├── sandbox.py      # Code execution environment
└── __init__.py     # Version info
```

## Notes

- This tool executes generated Python locally. Do not paste untrusted code.

## License

MIT
