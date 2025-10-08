# NLBT v2 — Promptification Architecture

A clean, prompt-driven backtesting system using the **triplet architecture** for natural language trading strategies.

![NLBT v2 Flow](diagram.svg)

## 🎯 Key Innovation: Triplet Loop

**Phase 1**: User → Communicator ↔ Jr Coding Agent (validation loop)  
**Phase 2**: Strong Coder → Critic (retry loop, max 3 attempts)  
**Phase 3**: Reporter → Professional outputs

## 🚀 Quick Start

```bash
# From v2 directory
cd v2
python cli.py

# Examples:
# Simple: "Buy and hold AAPL in 2024 with $10K"
# Complex: "Test RSI strategy on SPY: buy when RSI < 30, sell when RSI > 70, use 2023 data with $20K"
# Vague: "Buy SPY on dips" → Will ask for clarifications
```

## 📂 Output Structure

Each run creates a folder: `reports/TICKER_PERIOD_YYYYMMDD_HHMMSS/`

```
reports/AAPL_2024_20251008_054806/
├── report.md      # Human-readable markdown with TL;DR
├── report.pdf     # Professional PDF with charts
├── agent.log      # Agent-readable structured JSON
└── debug.log      # Developer-readable complete dump
```

## 🏗️ Architecture

### Agents
- **Communicator** (default model): Extracts requirements, handles conversation
- **Jr Coding Agent** (weak model): Validates feasibility with scaffold context
- **Strong Coder** (strong model): Generates backtesting code with indicators
- **Critic** (default model): Evaluates results and provides retry feedback
- **Reporter** (default model): Creates professional reports and logs

### Key Design Principles
1. **Pure prompt-driven**: No business logic in code, only orchestration
2. **Model efficiency**: Weak model for validation, strong for code generation
3. **Natural flow**: Auto-proceeds when ready, no manual state management
4. **Comprehensive logging**: Different formats for different audiences

## 🛠️ Configuration

### Environment Variables
```bash
# Model selection (optional)
export LLM_MODEL="gpt-4o-mini"           # Default for most agents
export LLM_WEAK_MODEL="gpt-3.5-turbo"    # For Jr Coding Agent
export LLM_STRONG_MODEL="gpt-4o"         # For Strong Coder
```

### Supported Strategies
- ✅ Single ticker strategies (stocks, ETFs, crypto)
- ✅ Technical indicators (RSI, SMA, EMA, MACD, Bollinger Bands)
- ✅ Date ranges and custom capital amounts
- ✅ Buy/hold, momentum, mean reversion patterns
- ❌ Multi-asset rotation (will ask to pick one ticker)
- ❌ Options/futures (not supported by scaffold)

## 📊 Example Reports

### Buy & Hold (Simple)
```
📈 Profitable · Buy and hold · Return: 37.19% · Max DD: -12.59% · Final: $13,718.58
```

### RSI Strategy (Complex)
```
📈 Profitable · Buy when RSI < 30, sell when RSI > 70 · Return: 7.28% · Max DD: -5.81% · Final: $21,455.66
```

## 🔧 Development

### File Structure
```
v2/
├── cli.py                    # Entry point
├── src/
│   ├── engine.py            # Orchestrator (146 lines)
│   ├── llm.py              # LLM wrapper with model types
│   ├── sandbox.py          # Safe code execution
│   └── agents/
│       ├── communicator.py # Requirement extraction
│       ├── jr_coder.py     # Feasibility validation
│       ├── strong_coder.py # Code generation
│       ├── critic.py       # Result evaluation
│       └── reporter.py     # Report generation
└── reports/                # Generated reports
```

### Adding New Indicators
Update the prompt in `strong_coder.py` to include examples:
```python
INDICATOR EXAMPLES (define helper functions in init):
def your_indicator(values, n=14):
    return ta.your_module.YourIndicator(pd.Series(values), window=n).your_method().to_numpy()
```

## 🎉 v2 Advantages over v1

1. **Clean separation**: Each agent has exactly one responsibility
2. **Prompt-driven**: Change behavior by updating prompts, not code
3. **Natural conversation**: No forced states or explicit "proceed" commands
4. **Smart validation**: Jr agent prevents wasted compute on invalid strategies
5. **Comprehensive logging**: Multiple output formats for different audiences
6. **Efficient models**: Uses cheaper models where possible

## 📝 License

Same as parent project (GPL-3.0)
