# Repository Content for GitHub

## Suggested Repo Name: `backtesting-agent`

---

## README.md

```markdown
# 🤖 Backtesting Agent

> **Tell me your trading strategy in plain English, and I'll evaluate it for you.**

An AI-powered backtesting assistant that converts natural language trading strategies into professional backtest reports. No coding required.

![Demo](demo.gif)

## ✨ What It Does

Describe your strategy in plain English:
```
"Backtest a 50/200 moving average crossover on SPY for 2023-2024 with $25,000"
```

Get a complete backtest report with:
- 📊 Performance metrics (Return %, Sharpe Ratio, Max Drawdown)
- 📈 Trade-by-trade analysis
- 💻 Full Python code for reproducibility
- 📄 Professional markdown report

**No coding required. Just describe your strategy.**

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/backtesting-agent.git
cd backtesting-agent

# Set up environment (requires Python 3.8+)
pip install -r requirements.txt

# Configure LLM (uses llm CLI - https://llm.datasette.io/)
llm keys set openai
# OR
llm keys set openrouter

# Run the assistant
python -m nlbt.cli
```

### First Strategy

```bash
$ python -m nlbt.cli

💭 You: Test a simple buy and hold strategy for Apple stock in 2024 with $10,000

🤖 Agent: [Extracts requirements, asks clarifying questions if needed]

💭 You: yes

🤖 Agent: [Generates code, runs backtest, creates report]

✅ Done! Report saved to: reports/backtest_20241002_120000.md
```

---

## 🎯 Example Strategies

### Beginner
```
Buy and hold Tesla for 2024 with $10K
```

### Intermediate  
```
Backtest a 20/50 MA crossover on Apple, 2024, $25K
```

### Advanced
```
Test NVDA with RSI: buy when RSI < 30, sell when RSI > 70, 
from Jan-Dec 2023 with $20K
```

### Complex Multi-Indicator
```
Backtest Microsoft: buy when MACD crosses above signal AND RSI < 50,
sell when MACD crosses below signal OR price drops 5%, 2024, $50K
```

**[See more examples →](EXAMPLES.md)**

---

## 🧠 How It Works

The agent uses a **3-phase agentic workflow**:

### Phase 1: 🔍 Understanding
- Conversational requirement gathering
- Asks clarifying questions until it has:
  - Ticker symbol (e.g., AAPL, SPY)
  - Time period (e.g., 2024, 2020-2023)
  - Initial capital (e.g., $10,000)
  - Strategy description

### Phase 2: ⚙️ Implementation
- **Producer:** Generates Python backtesting code
- **Executor:** Runs the code in a safe sandbox
- **Critic:** Evaluates results and retries if needed
- Uses `backtesting.py` library with proper indicators

### Phase 3: 📊 Reporting
- Plans report structure
- Writes comprehensive analysis
- Refines and saves markdown report

**Powered by:** Reflection pattern + Producer-Critic architecture from Agentic Design Patterns

---

## 🎨 Features

### ✅ Natural Language Interface
- Describe strategies in plain English
- Change requirements mid-conversation ("actually, use Tesla instead")
- Progressive disclosure (provide info gradually)

### ✅ Rich Technical Indicators
- Moving Averages (SMA, EMA)
- RSI, MACD, Bollinger Bands
- 100+ indicators from `ta` library
- Custom indicator support

### ✅ Robust Error Handling
- Automatic code retry (up to 3 attempts)
- Self-correcting LLM prompts
- Sandbox execution for safety

### ✅ Professional Reports
- Markdown format with metrics
- Full code included for reproducibility
- Trade-by-trade breakdown
- Performance statistics

### ✅ Any Ticker, Any Period
- US stocks (AAPL, TSLA, GOOGL, etc.)
- ETFs (SPY, QQQ, etc.)
- Crypto (BTC-USD, ETH-USD via Yahoo Finance)
- Any date range with historical data

---

## 📋 Requirements

- Python 3.8+
- `llm` CLI tool ([install guide](https://llm.datasette.io/))
- API key for OpenAI, Anthropic, or OpenRouter
- See `requirements.txt` for Python dependencies

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              User (Natural Language)            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Phase 1: Understanding Engine           │
│  • Requirement extraction                       │
│  • Clarifying questions                         │
│  • Validation                                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      Phase 2: Implementation (Reflection)       │
│  ┌──────────────────────────────────────────┐  │
│  │ Producer: Generate Python code           │  │
│  │ ↓                                         │  │
│  │ Sandbox: Execute safely                  │  │
│  │ ↓                                         │  │
│  │ Critic: Evaluate & decide                │  │
│  │   • PROCEED → Phase 3                    │  │
│  │   • RETRY → Producer (max 3x)            │  │
│  └──────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Phase 3: Report Generation              │
│  • Plan structure                               │
│  • Write analysis                               │
│  • Save markdown report                         │
└─────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

Contributions welcome! Areas of interest:
- [ ] Additional indicator patterns
- [ ] Multi-asset portfolio backtesting
- [ ] Parameter optimization
- [ ] Risk management strategies
- [ ] Interactive visualizations

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get running in 5 minutes
- **[Examples](EXAMPLES.md)** - 15+ strategy examples
- **[Architecture](cursor_chats/lessons_learned_llm_code_generation.md)** - How it works under the hood
- **[API Reference](docs/API.md)** - Programmatic usage

---

## 🙏 Acknowledgments

Built with:
- [backtesting.py](https://kernc.github.io/backtesting.py/) - Fast backtesting library
- [llm](https://llm.datasette.io/) - CLI for LLM interactions
- [yfinance](https://github.com/ranaroussi/yfinance) - Financial data
- [ta](https://github.com/bukosabino/ta) - Technical indicators
- Inspired by [Agentic Design Patterns](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## ⭐ Star History

If you find this useful, consider giving it a star! ⭐

---

**Made with ❤️ by [Your Name]**

*Describe your strategy in plain English. Get professional backtests in seconds.*
```

---

## Short Description (for GitHub repo)

```
AI agent that converts natural language trading strategies into professional backtest reports. 
Tell me your strategy in plain English, I'll evaluate it for you. No coding required.
```

---

## Topics/Tags (for GitHub)

```
trading
backtesting
ai-agent
natural-language-processing
quantitative-finance
algorithmic-trading
llm
python
technical-analysis
portfolio-management
agentic-ai
trading-strategies
financial-analysis
```

---

## Social Preview Text (for sharing)

```
🤖 Backtesting Agent: Describe your trading strategy in plain English, 
get professional backtest reports with metrics, code, and analysis. 
No coding required. Powered by AI agents.
```

---

## .github/ISSUE_TEMPLATES/

### Bug Report
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Strategy you described:
```
[Your strategy text]
```

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened (include error messages).

**Environment:**
- OS: [e.g., macOS, Ubuntu]
- Python version: [e.g., 3.9]
- LLM model used: [e.g., gpt-4o-mini]
```

### Feature Request
```markdown
**Feature Description**
What feature would you like to see?

**Use Case**
Why would this be useful?

**Example**
How would you use it?
```

---

## Additional Files to Create

1. **`.github/workflows/tests.yml`** - CI/CD for automated testing
2. **`CONTRIBUTING.md`** - Contribution guidelines
3. **`CODE_OF_CONDUCT.md`** - Community guidelines
4. **`CHANGELOG.md`** - Version history
5. **`.gitignore`** - Already exists, verify it includes:
   ```
   .env
   __pycache__/
   *.pyc
   reports/
   .DS_Store
   ```

---

## Pre-Push Checklist

- [ ] Update README.md with accurate installation steps
- [ ] Verify all examples in EXAMPLES.md work
- [ ] Create demo.gif (record terminal session)
- [ ] Add LICENSE file (suggest MIT)
- [ ] Update .gitignore to exclude .env, reports/, etc.
- [ ] Test installation from scratch in clean environment
- [ ] Remove any API keys or secrets from code/configs
- [ ] Add badges (build status, license, Python version)


