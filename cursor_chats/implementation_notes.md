# NLBT Implementation Notes

## Architecture Overview

The agentic backtesting sandbox is built using:

- **PocketFlow**: Agent orchestration with ReAct pattern
- **LLM CLI**: Model-agnostic access via Simon Willison's `llm` tool
- **Sandbox Execution**: Safe Python code execution with financial libraries
- **Session Management**: Multi-turn conversation state
- **Data Abstraction**: Yahoo Finance with caching layer

## Key Components

### 1. Session Management (`session.py`)
- `BacktestSession`: Manages conversation state and history
- Routes messages to PocketFlow agent
- Handles user input callbacks for interactive mode

### 2. Agent Setup (`agent/setup.py`)
- `BacktestAgent`: PocketFlow agent with financial tools
- Integrates with LLM CLI wrapper
- Provides system prompts and examples

### 3. Agent Tools (`agent/tools.py`)
- `ask_user()`: Interactive clarification
- `get_historical_data()`: OHLCV data fetching
- `write_and_execute_strategy()`: Code execution with retry logic
- `save_report()`: Report generation and saving

### 4. Sandbox Execution (`sandbox/`)
- `executor.py`: Safe code execution with timeout
- `environment.py`: Module restrictions and safe globals
- `helpers.py`: Financial utility functions

### 5. Data Layer (`data/`)
- `abstraction.py`: Provider-agnostic data access
- `providers/yfinance.py`: Yahoo Finance integration
- `cache.py`: Parquet-based caching

### 6. CLI Interface (`cli/main.py`)
- Typer-based chat interface
- Rich console output
- Session management commands

## Usage Patterns

### Interactive CLI
```bash
nlbt chat
```

### Programmatic API
```python
from nlbt import BacktestSession

session = BacktestSession()
response = session.chat("Backtest AAPL buy and hold")
```

### Agent Workflow
1. User describes strategy in natural language
2. Agent asks clarifying questions (ticker, period, capital)
3. Agent writes Python backtesting code
4. Code executes in sandbox with financial tools
5. Results captured and report generated
6. Error handling with retry logic

## Configuration

Environment variables in `.env`:
- `LLM_MODEL`: Default model for agent
- `CACHE_DIR`: Data cache directory
- `DEFAULT_TIMEOUT`: Code execution timeout
- `MAX_RETRY_ATTEMPTS`: Max retries for failed code
- `MAX_AGENT_ITERATIONS`: Max agent reasoning steps

## Security Considerations

### Sandbox Restrictions (MVP)
- Read-only filesystem access from generated code
- Network access allowed for data fetching
- Restricted dangerous imports (os, subprocess, etc.)
- Timeout limits on execution
- Best-effort import blocking

### Future Hardening
- Docker containerization
- Seccomp syscall filtering
- Resource limits (memory, CPU)
- Network access restrictions

## Testing Strategy

- Unit tests for individual components
- Integration tests for full workflows
- Mock external dependencies (yfinance, llm CLI)
- Test error handling and edge cases

## Extension Points

### Data Providers
Add new providers in `data/providers/`:
```python
def fetch_ohlcv(ticker, start, end):
    # Implementation
    return dataframe
```

### Agent Tools
Add new tools in `agent/tools.py`:
```python
def new_tool(param):
    # Implementation
    return result
```

### Sandbox Helpers
Add utility functions in `sandbox/helpers.py`:
```python
def new_helper():
    # Implementation
    pass
```

## Performance Considerations

- Data caching reduces API calls
- Sandbox execution timeout prevents hanging
- Agent iteration limits prevent infinite loops
- Lazy loading of heavy dependencies

## Future Enhancements

### Phase 2: Gradio UI
- Web interface for conversational backtesting
- File upload for custom data
- Real-time progress updates
- Interactive visualizations

### Advanced Features
- Multi-asset portfolio strategies
- Walk-forward optimization
- Monte Carlo analysis
- Risk management tools
- Custom indicator library

## Recent UX improvements (2025-10)

- Lucky demo: `lucky` command runs a built-in Buy & Hold AAPL (2024, $10k) demo without any LLM calls; saves a report.
- India-friendly input: Aliases for common NSE/indices (e.g., `reliance` → `RELIANCE.NS`, `nifty` → `^NSEI`) and rupee parsing (`₹10,00,000`, `INR 500000`).
- Localized summary: `lang hi|gu|en` selects the language for the TL;DR summary (rest of report remains English for now).
- Report folders: Each run saves to `reports/<TICKER>_<PERIOD>_<TIMESTAMP>/report.md`.
- Trades table: If available, Phase 2 code prints a compact markdown table (first 20 trades) under the `TRADES_TABLE` marker; Phase 3 includes it verbatim in the report.
