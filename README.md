# NLBT — Natural Language Backtesting

**Turn plain English into professional backtesting reports in minutes.**

Describe any trading strategy in natural language → Get Python code, backtest results, and a professional markdown report. No coding required.

**Cost**: <$0.50 per strategy with OpenRouter  
**Time**: 2-3 minutes per strategy  
**Output**: Professional reports with metrics, code, and insights

## ⚠️ Safety Warning
**This tool runs AI-generated Python code locally. Use in trusted environments only.**

## What You Get

**Input**: "Buy and hold AAPL in 2024 with $10,000"  
**Output**: Three-tier checkpoint system:
- 📊 **User reports**: Professional markdown/PDF with metrics and insights
- 💻 **Developer files**: Executable Python code + debug logs
- 🤖 **Agent context**: Complete LLM-ready checkpoint for iteration
- 📈 Full backtest results and trade analysis

**Sample outputs**: See `reports/EXAMPLE_simple_buy_hold_AAPL_2024.md` and `reports/EXAMPLE_RSI_strategy_NVDA_2023.md`

## Status & Limitations
- ✅ **Functional**: Successfully generates backtests for single-ticker strategies
- ⚠️ **WIP**: APIs, prompts, and behavior may change without notice  
- 🔄 **Active Development**: Expect bugs; contributions and test reports welcome
- 📈 **Best Results**: Works best with clear, specific strategy descriptions
- 🎯 **Single Asset**: Multi-asset portfolio strategies not yet supported

## Requirements
- Python 3.8+
- OpenRouter account (recommended) or OpenAI/Anthropic
- 5 minutes for setup

## Install & Setup

### 1. Clone and install everything
```bash
git clone https://github.com/yourusername/nlbt
cd nlbt
pip install -e .
```
*This installs all dependencies including `llm` CLI, `backtesting`, `ta`, and more*

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
- Saves report to `reports/<TICKER>_<PERIOD>_<TIMESTAMP>/report.md` (+ PDF)
- Takes 2-3 minutes total

## How it works (3-phase agentic architecture)

NLBT uses a **Reflection Pattern** with **Producer-Critic** loops for robust code generation:

**Diagram Color Key:**
- **Purple** - User actions/input
- **Yellow** - LLM actions (AI reasoning/generation)
- **Green** - System/sandbox (code execution)
- **Orange** - Automatic decisions (code logic)
- **Teal** - Phase states
- **Gray** - Final outputs

```mermaid
graph TD
    Start([User describes strategy]) --> P1[Phase 1: Understanding]
    P1 --> Extract[Extract requirements from conversation]
    Extract --> Check{Complete &<br/>implementable?}
    
    Check -->|Missing/unclear| Ask[Ask clarifying questions]
    Ask --> P1
    
    Check -->|Complete & valid| Ready[Ready to Implement]
    Ready --> Present[Present plan to user]
    Present --> Response{User response}
    
    Response -->|Anything else| BackToP1[Return to understanding]
    BackToP1 --> P1
    Response -->|Yes/Go| P2[Phase 2: Implementation]
    
    P2 --> Plan[Plan: LLM creates implementation plan]
    Plan --> Code[Producer: Generate Python code]
    Code --> Test[Test: Validate syntax & imports]
    Test --> Execute[Execute: Run in sandbox]
    Execute --> Critic[Critic: Evaluate results]
    Critic --> Decision{Critic decision}
    
    Decision -->|PASS| P3[Phase 3: Reporting]
    Decision -->|RETRY| Count{Attempt < 3?}
    Count -->|Yes| Plan
    Count -->|No| FailBack[Show error & return to understanding]
    FailBack --> P1
    
    P3 --> ReportPlan[Plan: Structure report]
    ReportPlan --> Write[Write: Generate markdown]
    Write --> Refine[Refine: Polish & save]
    Refine --> Done([Report saved])

    %% Role-based styling
    classDef user fill:#d1c4e9,stroke:#7e57c2,color:#4a148c;
    classDef llm fill:#fff9c4,stroke:#fbc02d,color:#6d4c41;
    classDef system fill:#e8f5e9,stroke:#43a047,color:#1b5e20;
    classDef decision fill:#ffccbc,stroke:#e64a19,color:#bf360c;
    classDef userInput fill:#e1bee7,stroke:#8e24aa,color:#4a148c;
    classDef state fill:#b2dfdb,stroke:#00897b,color:#004d40;
    classDef output fill:#eceff1,stroke:#90a4ae,color:#37474f;

    %% Assign roles
    class Start user;
    class P1,P2,P3,Ready state;
    class Extract,Ask,Plan,Code,Critic,ReportPlan,Write,Refine llm;
    class Test,Execute,Present system;
    class Check,Decision,Count decision;
    class Response userInput;
    class Done output;
    class BackToP1,FailBack system;
```

### Phase Details

**Phase 1 - Understanding** 🔍
- Conversational requirement extraction using LLM
- Gathers: Ticker, Period, Capital, Strategy description
- Asks clarifying questions until all 4 requirements are complete
- Transitions to "ready" state for user confirmation

**Phase 2 - Implementation** ⚙️ (Producer-Critic Pattern)
1. **Plan**: LLM creates detailed implementation plan
2. **Producer**: Strong model (Claude 3.5 Sonnet) generates Python code
3. **Test**: Validates syntax, imports, and structure
4. **Execute**: Runs code in isolated sandbox with financial libraries
5. **Critic**: Separate LLM evaluates results (PASS/RETRY)
6. **Loop**: Auto-retries up to 3 times with error feedback
7. **Failure Recovery**: After 3 failed attempts, returns to understanding phase with error context for user to modify strategy

**Phase 3 - Reporting** 📊 (Plan-Write-Refine)
1. **Plan**: Structure report sections
2. **Write**: Generate comprehensive markdown analysis
3. **Refine**: Polish and save to `reports/<TICKER>_<PERIOD>_<TIMESTAMP>/`

### Simplified Confirmation Flow

At the ready state, the system uses **smart conflict detection**:

- **Proceed words**: `yes`, `go`, `proceed`, `ok`, `start`, `continue`
- **Conflict words**: `but`, `change`, `explain`, `first`, `wait`, `think`, `over`, `else`

**Logic**: If user input contains a proceed word AND no conflict words → proceed to implementation. Otherwise → return to understanding phase for natural conversation.

**Examples**:
- ✅ `"yes"` → Implementation
- ✅ `"go for it"` → Implementation  
- ✅ `"proceed with implementation"` → Implementation
- 🔄 `"yes but change the ticker"` → Understanding (conflict: "but")
- 🔄 `"go ahead and explain first"` → Understanding (conflict: "first")
- 🔄 `"change to TSLA"` → Understanding (no proceed word)

## Use
```bash
nlbt                    # Start interactive session
```

**In-chat commands:**
- `info` - Show current phase and gathered requirements
- `debug` - Show internal state for troubleshooting  
- `lucky` - Quick demo: "Buy and hold AAPL in 2024 with $10,000"
- `exit` - Quit

### Reports output
Each run saves to `reports/<TICKER>_<PERIOD>_<TIMESTAMP>/` with **three-tier output**:

**For Users** 👥
- `report.md` - Professional markdown report with metrics and insights
- `report.pdf` - PDF version (auto-generated)

**For Developers** 🔧
- `strategy.py` - Complete executable Python code with requirements header
- `debug.log` - Execution trace and debugging information

**For Agents** 🤖
- `agent.log` - Full context dump for LLM iteration (codebase + conversation + execution)
- ~6,000-8,000 words, fits easily in modern LLM contexts
- Another LLM can recreate the entire run from this checkpoint

## Examples (realistic conversations)

**Simple Buy & Hold**
```bash
💭 You: Buy and hold AAPL in 2024 with $10,000

🤖 Perfect! I have everything needed:
   • Ticker: AAPL
   • Period: 2024
   • Capital: $10,000
   • Strategy: Buy and hold
   
   Ready to implement? (yes/no/change/explain)

💭 You: yes

🤖 ⚙️ Phase 2: Implementation
   [Attempt 1/3] Planning implementation...
   [Attempt 1/3] Generating Python code...
   [Attempt 1/3] Testing code...
   [Attempt 1/3] Executing backtest...
   [Attempt 1/3] Results: Return 38.88%, Sharpe 1.25, Max DD -15.26%
   ✅ Critic: PASS - Proceeding to reporting

🤖 📊 Phase 3: Reporting
   Planning report structure...
   Writing comprehensive analysis...
   ✅ Report saved: reports/AAPL_2024_20241002_123456/report.md
```

**RSI Strategy** 
```bash
💭 You: NVDA with RSI: buy when RSI < 30, sell when RSI > 70, 2023, $20K

🤖 STATUS: READY
   • Ticker: NVDA
   • Period: 2023  
   • Capital: $20,000
   • Strategy: RSI mean reversion (buy <30, sell >70)
   
   Proceed? (yes/no/change/explain)

💭 You: yes

🤖 [Generates → Tests → ✓ PASS]
   ✅ Report: reports/NVDA_2023_20241002_143012/report.md
```

**Progressive Disclosure** (provide info gradually)
```bash
💭 You: Test a moving average crossover

🤖 I'll help you backtest a moving average strategy! I need:
   • Which ticker? (e.g., AAPL, SPY, TSLA)
   • Time period? (e.g., 2024, 2020-2023)
   • Initial capital? (e.g., $10,000)
   • Which MA periods? (e.g., 50/200 day)

💭 You: SPY, 2024, $25K

🤖 Great! Which moving average periods? (e.g., 20/50, 50/200)

💭 You: use 50/200 day crossover

🤖 Perfect! All set. Ready to proceed?

💭 You: yes
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
├── __init__.py
├── cli.py              # Interactive CLI with rich formatting
├── reflection.py       # 3-phase reflection engine (1,251 lines)
│                       # - Phase 1: Understanding (requirement extraction)
│                       # - Phase 2: Implementation (Producer-Critic loop)
│                       # - Phase 3: Reporting (Plan-Write-Refine)
├── llm.py              # Simple LLM wrapper using `llm` CLI
├── llm/
│   └── client.py       # Enhanced LLM client
└── sandbox.py          # Safe code execution + get_ohlcv_data()

reports/                # Generated backtest reports
├── <TICKER>_<PERIOD>_<TIMESTAMP>/
│   ├── report.md       # User: Professional markdown report
│   ├── report.pdf      # User: PDF version (auto-generated)
│   ├── strategy.py     # Developer: Executable Python code
│   ├── debug.log       # Developer: Execution trace
│   └── agent.log       # Agent: Full context for LLM iteration
└── EXAMPLE_*.md        # Sample output reports

cursor_chats/           # Development notes & architecture docs
tests/                  # Unit and integration tests
scripts/                # Setup and demo scripts
```

## Architecture & Design

This project implements several **Agentic Design Patterns**:

- **Reflection Pattern**: 3-phase autonomous workflow with LLM controlling transitions
- **Producer-Critic Pattern**: Separate models for generation (Producer) and evaluation (Critic) to avoid confirmation bias
- **Planning Pattern**: Phase 2 plans before coding; Phase 3 plans before writing
- **Tool Use Pattern**: Sandbox execution, data fetching, indicator calculations
- **Prompt Chaining**: Phase transitions chain prompts with context
- **Error Recovery**: Auto-retry loop (max 3 attempts) with error feedback
- **Checkpoint Pattern**: Three-tier output (user/developer/agent) for complete reproducibility and iteration

See `cursor_chats/Agentic_Design_Patterns_Complete.md` for detailed pattern documentation.

## Contributing

Contributions welcome! Areas of interest:
- Multi-asset portfolio backtesting
- Additional technical indicators
- Parameter optimization
- Risk management strategies
- Interactive visualizations

## License
MIT License. See `LICENSE`.