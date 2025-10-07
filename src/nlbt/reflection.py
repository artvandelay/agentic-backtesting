"""Minimal 3-phase reflection engine."""

import os
import logging
import glob
from datetime import datetime
from .llm import LLM
from .sandbox import Sandbox


def setup_run_logging(run_dir):
    """Setup debug and agent loggers for this run."""
    # Developer trace logger
    debug = logging.getLogger(f'debug_{run_dir}')
    debug.setLevel(logging.INFO)
    debug.addHandler(logging.FileHandler(f'{run_dir}/debug.log'))
    
    # Agent context logger
    agent = logging.getLogger(f'agent_{run_dir}')
    agent.setLevel(logging.INFO)
    agent.addHandler(logging.FileHandler(f'{run_dir}/agent.log'))
    
    return debug, agent


class ReflectionEngine:
    """
    3-phase autonomous backtest workflow.
    
    Phase 1: Understanding - LLM asks until STATUS: READY
    Phase 2: Implementation - Producer/Critic loop
    Phase 3: Reporting - Plan/Write/Refine
    """
    
    def __init__(self, model: str = None):
        self.llm = LLM(model)
        # Use strong model for code generation
        # Use advanced model for code generation - try Claude first, fallback to GPT-4.5
        # Allow environment override; prefer Claude if explicitly set
        code_model = (
            os.getenv("LLM_CODE_MODEL")
            or "openrouter/anthropic/claude-3.5-sonnet"
        )
        try:
            self.code_llm = LLM(code_model)
        except Exception:
            # Fallback to an advanced OpenAI model if available
            self.code_llm = LLM("gpt-4.5-preview")
        self.sandbox = Sandbox()
        self.phase = "understanding"
        self.history = []
        self.requirements = {}
        self.code = ""
        self.results = ""
        self.last_error = ""
        # Last validator decision for debugging
        self.last_validation = None
        # Loggers (initialized in phase 3 when run_dir is created)
        self.debug_logger = None
        self.agent_logger = None
    
    def chat(self, user_input: str) -> str:
        """Process user message, return agent response."""
        
        # CRITICAL: Don't process empty or whitespace-only inputs
        if not user_input or not user_input.strip():
            return "Please provide a message."
        
        user_input = user_input.strip()
        self.history.append(f"User: {user_input}")
        
        # Check if user wants to change requirements during implementation
        if self.phase == "implementation" and any(word in user_input.lower() for word in ["sorry", "actually", "i mean", "change"]):
            # Go back to understanding phase
            self.phase = "understanding"
            return "I see you want to change the requirements. Let me understand what you need.\n\n" + self._phase1_understanding(user_input)
        
        if self.phase == "understanding":
            response = self._phase1_understanding(user_input)
        elif self.phase == "ready_to_implement":
            response = self._handle_implementation_confirmation(user_input)
        elif self.phase == "implementation":
            # Implementation should not be triggered by user input anymore
            # It's handled directly in _handle_implementation_confirmation
            return "✅ Implementation already completed. Type 'info' to see current status or start a new strategy."
        elif self.phase == "reporting":
            # Reporting should execute immediately, not wait for input
            return self._phase3_reporting()
        elif self.phase == "complete":
            # Reset to understanding for new conversation
            self.phase = "understanding"
            response = "🎯 Previous conversation completed! Ready for new strategy. What would you like to backtest?"
        else:
            response = "All done!"
        
        self.history.append(f"Agent: {response}")
        return response
    
    def _phase1_understanding(self, user_input: str, from_confirmation: bool = False) -> str:
        """Phase 1: Gather requirements until LLM says READY."""
        
        # First, try to extract requirements from the conversation
        self._update_requirements_from_conversation(user_input)
        
        prompt = f"""You are helping gather backtesting requirements. Have a natural conversation.

CONVERSATION HISTORY:
{self._get_history()}

CURRENT USER MESSAGE: {user_input}

REQUIRED INFO (track what you have):
- Ticker symbol (e.g., AAPL, MSFT, SPY)
- Time period (e.g., "2020 to 2024", "last 2 years", "2023")  
- Initial capital (e.g., "$10,000", "$25K", "50000")
- Strategy description (trading rules and logic)

CRITICAL INSTRUCTIONS:
1. Have a NATURAL conversation - don't repeat the same format
2. NEVER make up or imagine user messages - only respond to what they actually said
3. If you have some info already, acknowledge it and ask for what's missing
4. Be conversational: "Great! I have the ticker as TSLA and strategy as buying on Mondays. What time period and capital should I use?"
5. When you have ALL 4 requirements (ticker, period, capital, strategy), IMMEDIATELY output STATUS: READY format
6. Don't ask for unnecessary details if you already have enough info
7. If user provides a complete strategy description, don't ask for more details unless absolutely needed

STATUS FORMAT (use ONLY when you have everything):

STATUS: READY
TICKER: [value]
PERIOD: [value] 
CAPITAL: [value]
STRATEGY: [complete description]

I have everything needed to proceed with the backtest.

💡 USER TIP: You can say "yes", "go", or "proceed" when ready, or make changes anytime!

RESPOND ONLY to the current user message. Do NOT create fake conversations."""

        response = self.llm.ask(prompt)
        
        # Clean the response - remove any fake "User:" or "Agent:" prefixes that LLM might add
        response = response.strip()
        if response.startswith("User:") or response.startswith("Agent:"):
            # LLM is hallucinating - extract just the actual response
            lines = response.split('\n')
            clean_lines = []
            for line in lines:
                if not line.strip().startswith("User:") and not line.strip().startswith("Agent:"):
                    clean_lines.append(line)
            response = '\n'.join(clean_lines).strip()
        
        # Check if we have all 4 requirements from extraction
        has_ticker = bool(self.requirements.get('ticker'))
        has_period = bool(self.requirements.get('period'))
        has_capital = bool(self.requirements.get('capital'))
        has_strategy = bool(self.requirements.get('strategy'))

        # If we have all requirements, validate against scaffold before READY
        # BUT skip auto-proceed if we're coming from confirmation step
        if has_ticker and has_period and has_capital and has_strategy and not from_confirmation:
            validation = self._validate_requirements_with_codebase()
            self.last_validation = validation
            if validation.get("implementable"):
                # Auto-proceed immediately (agentic flow)
                self.phase = "implementation"
                return self._phase2_implementation()
            else:
                clar = validation.get("clarifications") or []
                # Synthesize concrete clarifications if missing
                if not clar:
                    missing = []
                    for k in ["ticker", "period", "capital", "strategy"]:
                        if not self.requirements.get(k):
                            missing.append(k)
                    for k in missing:
                        if k == "ticker":
                            clar.append("Specify a single ticker (e.g., AAPL or RELIANCE.NS)")
                        elif k == "period":
                            clar.append("Provide a concrete period (e.g., 2023 or 2020-2024)")
                        elif k == "capital":
                            clar.append("Provide initial capital with currency (e.g., $10,000 or ₹10,00,000)")
                        elif k == "strategy":
                            clar.append("Describe entry and exit rules with numeric thresholds")
                clar_block = "\n".join([f"- {c}" for c in clar]) if clar else "- Please clarify missing or vague details so I can proceed."
                return f"""⚠️ Before I can proceed, I need a few clarifications to ensure this strategy is implementable with the current system:\n{clar_block}\n\nPlease answer these in one message."""

        # Check if LLM says READY
        if "STATUS: READY" in response:
            self._extract_requirements(response)
            validation = self._validate_requirements_with_codebase()
            self.last_validation = validation
            if validation.get("implementable"):
                # Auto-proceed directly
                self.phase = "implementation"
                return self._phase2_implementation()
            else:
                clar = validation.get("clarifications") or []
                if not clar:
                    missing = []
                    for k in ["ticker", "period", "capital", "strategy"]:
                        if not self.requirements.get(k):
                            missing.append(k)
                    for k in missing:
                        if k == "ticker":
                            clar.append("Specify a single ticker (e.g., AAPL or RELIANCE.NS)")
                        elif k == "period":
                            clar.append("Provide a concrete period (e.g., 2023 or 2020-2024)")
                        elif k == "capital":
                            clar.append("Provide initial capital with currency (e.g., $10,000 or ₹10,00,000)")
                        elif k == "strategy":
                            clar.append("Describe entry and exit rules with numeric thresholds")
                clar_block = "\n".join([f"- {c}" for c in clar]) if clar else "- Please clarify missing or vague details so I can proceed."
                return f"""⚠️ Before I can proceed, I need a few clarifications to ensure this strategy is implementable with the current system:\n{clar_block}\n\nPlease answer these in one message."""
        
        return response
    
    def _handle_implementation_confirmation(self, user_input: str) -> str:
        """Handle user confirmation before starting implementation."""
        # Use LLM to determine if user wants to proceed
        if self._should_proceed(user_input):
            # Proceed with implementation
            self.phase = "implementation"
            implementation_result = self._phase2_implementation()
            return implementation_result
        
        # Everything else goes back to understanding phase
        # The understanding phase LLM is smart enough to handle:
        # - "change ticker to TSLA" 
        # - "explain how RSI works"
        # - "actually use 2023 instead"
        # - "reset everything"
        # - "what does this strategy do?"
        self.phase = "understanding"
        return "Got it! Let me help you with that.\n\n" + self._phase1_understanding(user_input, from_confirmation=True)
    
    def _phase2_implementation(self, attempt: int = 1) -> str:
        """Phase 2: Producer generates, Critic evaluates."""
        if attempt > 3:
            if self.debug_logger:
                self.debug_logger.info(f"Failed after 3 attempts. Last error: {self.last_error}")
            
            # Return to understanding phase with full context
            self.phase = "understanding"
            error_msg = f"❌ Failed after 3 attempts.\n\nLast error:\n{self.last_error}\n\nLet's try a different approach."
            return error_msg + "\n\n" + self._phase1_understanding("I need help fixing this strategy", from_confirmation=True)
        
        print(f"🔄 Attempt {attempt}/3 - Generating/Testing/Executing...")
        if self.debug_logger:
            self.debug_logger.info(f"Attempt {attempt}/3 - Generating/Testing/Executing...")
        
        # Producer: Generate code with BULLETPROOF template
        if attempt == 1:
            code_prompt = f"""Generate complete Python backtesting code. Copy this EXACT pattern:

REQUIREMENTS:
{self._format_requirements()}

BULLETPROOF CODE TEMPLATE (copy this structure exactly):

```python
from backtesting import Backtest, Strategy

# Get data (NEVER redefine get_ohlcv_data - it exists!)
data = get_ohlcv_data('TICKER', 'START_DATE', 'END_DATE')

class MyStrategy(Strategy):
    def init(self):
        # For indicators, use this EXACT pattern:
        # Step 1: Define helper that returns numpy array
        def sma(values, n):
            import pandas as pd
            return pd.Series(values).rolling(n).mean().to_numpy()
        
        # Step 2: Wrap with self.I
        # self.sma20 = self.I(sma, self.data.Close, 20)
        # self.sma50 = self.I(sma, self.data.Close, 50)
        
        pass
    
    def next(self):
        # Trading logic here
        if not self.position:
            self.buy()

bt = Backtest(data, MyStrategy, cash=CASH_NUMBER)
stats = bt.run()
print(stats)

# Emit structured artifacts for reporting
import json
try:
    # Trades preview table
    import pandas as pd
    print("TRADES_TABLE")
    print(stats._trades.head(50).to_markdown(index=False))
except Exception:
    pass

# Full CSVs for optional charts/tables
try:
    import pandas as pd
    print("TRADES_CSV"); print(stats._trades.to_csv(index=False))
    print("EQUITY_CSV"); print(stats._equity_curve.to_csv(index=False))
except Exception:
    pass

# Compact summary for TL;DR
try:
    end_date = str(stats.get('End', '')) or (str(data.index[-1].date()) if hasattr(data, 'index') and len(data.index) else '')
    equity_final = float(stats.get('Equity Final [$]', 0))
    initial_cap = float(CASH_NUMBER)
    pnl_abs = equity_final - initial_cap
    pnl_pct = float(stats.get('Return [%]', 0))
    print("SUMMARY_JSON"); print(json.dumps(dict(
        end=end_date,
        initial=initial_cap,
        equity_final=equity_final,
        portfolio_final=equity_final,
        pnl_abs=pnl_abs,
        pnl_pct=pnl_pct
    )))
except Exception:
    pass
```

PATTERN FOR INDICATORS (copy exactly):

RSI:
```
def rsi(values, n=14):
    import pandas as pd
    import numpy as np
    delta = pd.Series(values).diff()
    gain = (delta.where(delta > 0, 0)).rolling(n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).to_numpy()

self.rsi = self.I(rsi, self.data.Close, 14)
```

SMA:
```
def sma(values, n):
    import pandas as pd
    return pd.Series(values).rolling(n).mean().to_numpy()

self.sma20 = self.I(sma, self.data.Close, 20)
```

MACD:
```
def ema(values, n):
    import pandas as pd
    return pd.Series(values).ewm(span=n, adjust=False).mean().to_numpy()

def macd(values):
    ema12 = ema(values, 12)
    ema26 = ema(values, 26)
    return ema12 - ema26

def macd_signal(values):
    import pandas as pd
    macd_line = macd(values)
    return pd.Series(macd_line).ewm(span=9, adjust=False).mean().to_numpy()

self.macd = self.I(macd, self.data.Close)
self.macd_signal = self.I(macd_signal, self.data.Close)
```

CROSSOVER (for MA strategies):
```
# In next():
if self.sma20[-2] <= self.sma50[-2] and self.sma20[-1] > self.sma50[-1]:
    if not self.position:
        self.buy()
```

YOUR TASK:
1. Replace TICKER with: {self.requirements.get('ticker', 'AAPL')}
2. Replace START_DATE, END_DATE based on: {self.requirements.get('period', '2024')}
   IMPORTANT: If using indicators with long windows (200-day SMA, etc.), START EARLIER to allow warmup.
   Example: For "2023-2024", use '2022-01-01' to '2024-12-31' to ensure 200-day SMA has data.
3. Replace CASH_NUMBER with a pure number (e.g., 10000). If capital is given as text like '₹10,00,000' or '$10,000', convert to number.
4. Implement strategy: {self.requirements.get('strategy', 'buy and hold')}
5. Use indicator patterns above if needed

Write ONLY the complete code (no markdown, no explanations):"""
            
            response = self.code_llm.ask(code_prompt)
            if "```python" in response:
                self.code = response.split("```python")[1].split("```")[0].strip()
            else:
                self.code = response.strip()
        
        # Execute
        result = self.sandbox.run(self.code)
        
        if self.debug_logger:
            self.debug_logger.info(f"Execution result: {'SUCCESS' if result['success'] else 'FAILED'}")
            if result["success"]:
                self.debug_logger.info(f"Output:\n{result['output']}")
            else:
                self.debug_logger.info(f"Error:\n{result['error']}")
        
        if not result["success"]:
            self.last_error = result["error"]
            
            # Fix prompt with specific error context
            fix_prompt = f"""Fix this error. Use the indicator patterns from before.

ERROR:
{result['error']}

CODE:
{self.code}

REQUIREMENTS:
{self._format_requirements()}

CRITICAL FIXES:
1. NEVER redefine get_ohlcv_data - it exists!
2. cash must be a number: cash=10000 NOT cash='$10,000'
3. Dates: '2024-01-01' format
4. For indicators, use the helper function pattern shown earlier
5. All indicators must return .to_numpy()
6. At the end, print TRADES_CSV and EQUITY_CSV exactly as shown:
   print("TRADES_CSV"); print(stats._trades.to_csv(index=False)); print("EQUITY_CSV"); print(stats._equity_curve.to_csv(index=False))

Write the COMPLETE fixed code:"""
            
            response = self.code_llm.ask(fix_prompt)
            if "```python" in response:
                self.code = response.split("```python")[1].split("```")[0].strip()
            else:
                self.code = response.strip()
            
            return self._phase2_implementation(attempt + 1)
        
        # Critic: Evaluate
        self.results = result["output"]
        
        critique_prompt = f"""Evaluate: Did the backtest run successfully?

Requirements: {self._format_requirements()}
Results: {self.results}

PASS if: 
- Shows stats (Return %, Equity Final, etc.)
- Uses correct ticker/period/capital
- No crashes or errors
- Even if # Trades = 0 (strategy may not trigger signals in this period)

FAIL if: 
- Crashed with errors
- Wrong ticker/period/capital
- No stats shown

DECISION: [PROCEED or RETRY]"""

        critique = self.code_llm.ask(critique_prompt)
        
        if self.debug_logger:
            self.debug_logger.info(f"Critic decision: {'PROCEED' if 'PROCEED' in critique.upper() else 'RETRY'}")
        
        if "PROCEED" in critique.upper():
            self.phase = "reporting"
            # Lightweight LLM TL;DR from stats
            summary_line = self._llm_tldr(self.results)
            # Generate report but keep CLI output minimal
            report_msg = self._phase3_reporting()
            # Extract folder path line for concise echo
            folder_line = ""
            for ln in report_msg.splitlines():
                if ln.startswith("📄 REPORT FOLDER:"):
                    folder_line = ln
                    break
            return f"🧾 {summary_line}\n{folder_line}"
        else:
            return self._phase2_implementation(attempt + 1)
    
    def _create_implementation_plan(self) -> dict:
        """Create a detailed implementation plan before coding."""
        planning_prompt = f"""You are a senior backtesting engineer creating a detailed implementation plan.

REQUIREMENTS:
{self._format_requirements()}

Following the Agentic Design Patterns principles, create a comprehensive plan:

1. STRATEGY ANALYSIS (Pattern: Planning):
   - Strategy type: buy-and-hold, mean reversion, momentum, breakout, etc.
   - Entry conditions: precise logic for when to buy
   - Exit conditions: precise logic for when to sell/close positions
   - Risk management: stop losses, position sizing, etc.

2. INDICATOR REQUIREMENTS (Pattern: Tool Use):
   - Technical indicators needed with exact parameters
   - How to calculate each in backtesting.py context
   - Alternative implementations if libraries differ

3. CODE ARCHITECTURE (Pattern: Reflection):
   - Strategy class structure following backtesting.py patterns
   - init() method: indicator initialization with error handling
   - next() method: trading logic with position management
   - Helper methods for complex calculations

4. IMPORT STRATEGY (Pattern: Tool Use):
   - Correct imports from backtesting library
   - Correct imports from ta library (ta.momentum, ta.trend, etc.)
   - Any additional libraries needed

5. RISK ANALYSIS (Pattern: Exception Handling):
   - Common failure modes for this strategy type
   - Edge cases: market closures, data gaps, extreme volatility
   - Recovery strategies for each failure mode

6. TESTING APPROACH (Pattern: Evaluation):
   - Component testing before full backtest
   - Expected behavior validation
   - Performance metrics to validate

Provide a structured, actionable plan that follows agentic patterns:"""

        try:
            response = self.code_llm.ask(planning_prompt)
            # Store the plan for reference
            self.implementation_plan = response
            return {"success": True, "plan": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_code_from_plan(self, attempt: int) -> str:
        """Generate code based on the implementation plan."""
        if attempt == 1:
            # First attempt: use the detailed plan
            code_prompt = f"""You are a senior backtesting engineer implementing a strategy following agentic design patterns.

DETAILED IMPLEMENTATION PLAN:
{getattr(self, 'implementation_plan', 'No plan available')}

REQUIREMENTS:
{self._format_requirements()}

FOLLOWING AGENTIC PATTERNS:
• Use proper imports from ta library (ta.momentum, ta.trend, etc.)
• Structure code with clear Strategy class following backtesting.py patterns
• Include error handling and edge case management
• Use proper indicator calculations with ta library
• Implement position management and risk controls

CODE REQUIREMENTS:
1. EXACT imports: Use ta.momentum for RSI, ta.trend for SMA/MACD
2. Data handling: Use existing get_ohlcv_data() function
3. Strategy structure: Proper init() and next() methods
4. Error handling: Handle data issues, calculation errors
5. Risk management: Implement stop losses, position sizing

INDICATOR INTEGRATION WITH backtesting.Strategy:
- In init(), ALWAYS create indicators via self.I with a lambda that returns a NumPy array
- Convert pandas Series to numpy with .to_numpy()
- Example SMA:
  from ta.trend import SMAIndicator
  import pandas as pd
  self.sma20 = self.I(lambda c: SMAIndicator(close=pd.Series(c), window=20).sma_indicator().to_numpy(), self.data.Close)
  self.sma50 = self.I(lambda c: SMAIndicator(close=pd.Series(c), window=50).sma_indicator().to_numpy(), self.data.Close)
- Example RSI:
  from ta.momentum import RSIIndicator
  import pandas as pd
  self.rsi = self.I(lambda c: RSIIndicator(close=pd.Series(c), window=14).rsi().to_numpy(), self.data.Close)
- Example MACD (returns MACD line):
  from ta.trend import MACD
  import pandas as pd
  self.macd = self.I(lambda c: MACD(close=pd.Series(c), window_slow=26, window_fast=12, window_sign=9).macd().to_numpy(), self.data.Close)
  self.macd_signal = self.I(lambda c: MACD(close=pd.Series(c), window_slow=26, window_fast=12, window_sign=9).macd_signal().to_numpy(), self.data.Close)
  # In next(), detect cross without importing backtesting.lib:
  # bullish_cross = (self.macd[-2] <= self.macd_signal[-2]) and (self.macd[-1] > self.macd_signal[-1])

CRITICAL FIXES:
- Use 'from ta.trend import MACD' NOT 'from backtesting.test import MACD'
- Use 'from ta.momentum import RSIIndicator' NOT 'from backtesting.test import RSI'
- MACD calculation: macd = MACD(close=data.Close, window_slow=26, window_fast=12, window_sign=9).macd()
- RSI calculation: rsi = RSIIndicator(close=data.Close, window=14).rsi()
- Do NOT use pandas_ta — use the 'ta' library imports shown above

Generate ONLY the complete, executable Python code:"""
        else:
            # Retry attempts: focus on fixing the specific error
            code_prompt = f"""Fix the code based on this error:

PREVIOUS CODE:
{self.code}

ERROR:
{self.last_error}

REQUIREMENTS:
{self._format_requirements()}

COMMON FIXES:
- ImportError for RSI: Use 'from ta.momentum import RSIIndicator' and integrate via self.I, e.g. in init():
    self.rsi = self.I(lambda c: RSIIndicator(close=pd.Series(c), window=14).rsi().to_numpy(), self.data.Close)
- ImportError for SMA: Use 'from ta.trend import SMAIndicator' and compute with ta, integrated via self.I
- ImportError for MACD: Use 'from ta.trend import MACD' and integrate via self.I, e.g.:
    self.macd = self.I(lambda c: MACD(close=pd.Series(c), window_slow=26, window_fast=12, window_sign=9).macd().to_numpy(), self.data.Close)
- Cash error: Ensure cash=NUMBER (not cash='$10,000')
- Date format: Use 'YYYY-MM-DD' strings
- Never import from 'backtesting.test' - use 'ta' library instead
 - Do NOT use pandas_ta; only use the 'ta' package

Write the COMPLETE corrected code:"""

        try:
            response = self.code_llm.ask(code_prompt)
            # Extract code from markdown
            if "```python" in response:
                code = response.split("```python")[1].split("```")[0].strip()
            else:
                code = response.strip()
            
            self.code = code
            return code
        except Exception as e:
            self.last_error = str(e)
            return None
    
    def _test_code_components(self, code: str) -> dict:
        """Test basic code components before full execution."""
        try:
            # Basic syntax check
            compile(code, '<string>', 'exec')
            
            # Check for common issues
            issues = []
            if 'def get_ohlcv_data' in code:
                issues.append("Code redefines get_ohlcv_data() - should use existing function")
            
            forbidden = [
                'from backtesting.test import RSI',
                'from backtesting.test import MACD',
                'from backtesting.test import SMA',
                'import pandas_ta',
                'from pandas_ta',
            ]
            for bad in forbidden:
                if bad in code:
                    issues.append("Do not import indicators from backtesting.test - use ta library")
                
            if issues:
                return {"success": False, "error": "; ".join(issues)}
                
            return {"success": True}
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Code validation error: {e}"}

    def _get_scaffold_context(self) -> str:
        """Assemble minimal scaffold context for validator prompt."""
        import os
        base_dir = os.path.dirname(__file__)
        parts = []
        # sandbox.py (short, safe to include entirely)
        try:
            with open(os.path.join(base_dir, 'sandbox.py'), 'r', encoding='utf-8') as f:
                parts.append("SANDBOX.PY:\n" + f.read())
        except Exception:
            pass
        # reflection head and _test_code_components
        try:
            with open(os.path.join(base_dir, 'reflection.py'), 'r', encoding='utf-8') as f:
                refl = f.read()
            head = "\n".join(refl.splitlines()[:150])
            parts.append("REFLECTION.PY (HEAD):\n" + head)
            marker = "def _test_code_components"
            idx = refl.find(marker)
            if idx != -1:
                snippet = refl[idx:]
                parts.append("REFLECTION.PY (_test_code_components):\n" + "\n".join(snippet.splitlines()[:120]))
        except Exception:
            pass
        return "\n\n".join(parts)

    def _validate_requirements_with_codebase(self) -> dict:
        """Use LLM to validate whether current requirements are implementable.

        Returns: {"implementable": bool, "clarifications": list[str], "raw": str}
        """
        scaffold = self._get_scaffold_context()
        req = self.requirements.copy()
        prompt = (
            "You are validating if the strategy is implementable using this scaffold.\n"
            "Respond concisely with deterministic headers.\n\n"
            "# VALIDATION RULES (code-like, hard constraints)\n"
            "supports_single_ticker = True\n"
            "supports_multi_asset = False\n"
            "supports_options = False\n"
            "requires_numeric_thresholds = True  # e.g. 'dips' must include % or window\n\n"
            "# Heuristics (pseudo)\n"
            "def contains_multiple_tickers(text):\n"
            "    import re\n"
            "    # two distinct tickers like 'GLD and SPY'\n"
            "    return bool(re.search(r'\\b[A-Z]{2,5}\\b.*\\b[A-Z]{2,5}\\b', text)) and (' & ' in text or ' and ' in text or ',' in text)\n\n"
            "def mentions_options(text):\n"
            "    t = text.lower()\n"
            "    return any(w in t for w in ['option', 'iron condor', 'straddle', 'strangle', 'call', 'put', 'spread'])\n\n"
            "def vague_without_numbers(text):\n"
            "    import re\n"
            "    t = text.lower()\n"
            "    vague_terms = ['dip', 'dips', 'momentum', 'breakout', 'retrace', 'bounce']\n"
            "    has_vague = any(v in t for v in vague_terms)\n"
            "    has_numbers = bool(re.search(r'\\d+\\s*%|\\d+\\s*(day|bar|period|window)', t))\n"
            "    return has_vague and not has_numbers\n\n"
            "def clearly_numeric_strategy(text):\n"
            "    t = text.lower()\n"
            "    # Examples: 'RSI < 30 and > 70', 'EMA 10 crosses 20', '5% drop'\n"
            "    return any(k in t for k in ['rsi', 'ema', 'sma', '%'])\n\n"
            f"REQUIREMENTS:\n{req}\n\n"
            f"SCAFFOLD:\n{scaffold}\n\n"
            "# DECISION LOGIC\n"
            "# If multi-asset or options mentioned → IMPLEMENTABLE: NO\n"
            "# If vague triggers without numeric thresholds → IMPLEMENTABLE: NO, but suggest concrete defaults\n"
            "# If single ticker and rules are clearly numeric/precise → IMPLEMENTABLE: YES\n\n"
            "Output exactly this format:\n"
            "IMPLEMENTABLE: YES|NO\n"
            "If NO, then follow with:\n"
            "CLARIFICATIONS:\n"
            "- Ask to choose a single ticker if multiple tickers are present\n"
            "- Ask to avoid options/derivatives; propose stock-based alternative\n"
            "- Ask for numeric thresholds/windows for vague terms (e.g., dips %)\n"
            "- Provide one concrete suggestion when helpful (e.g., 'dip = 5% below 10-day EMA; sell on cross above')\n"
            "- Up to 5 bullets total\n"
        )
        try:
            resp = self.llm.ask(prompt)
        except Exception as e:
            return {"implementable": False, "clarifications": ["Please confirm ticker, period, capital, and concrete entry/exit rules."], "raw": str(e)}

        text = resp.strip()
        implementable = False
        clarifications = []
        for line in text.splitlines():
            up = line.upper().strip()
            if up.startswith("IMPLEMENTABLE:"):
                if "YES" in up:
                    implementable = True
                break
        if not implementable:
            lines = text.splitlines()
            start = False
            for ln in lines:
                if start:
                    s = ln.strip()
                    if not s:
                        break
                    if s.startswith(('-', '•', '*')) or (len(s) > 1 and s[0].isdigit()):
                        clarifications.append(s.lstrip('-•* ').strip())
                        if len(clarifications) >= 5:
                            break
                    else:
                        break
                elif ln.upper().startswith("CLARIFICATIONS:"):
                    start = True

        return {"implementable": implementable, "clarifications": clarifications, "raw": text}
    
    def _execute_backtest(self, code: str) -> dict:
        """Execute the backtest code."""
        # Execute code in sandbox and return raw result
        return self.sandbox.run(code)
    
    def _handle_code_error(self, test_result: dict, attempt: int) -> str:
        """Handle code validation errors."""
        self.last_error = test_result["error"]
        return self._phase2_implementation(attempt + 1)
    
    def _handle_execution_error(self, result: dict, attempt: int) -> str:
        """Handle execution errors."""
        self.last_error = result["error"]
        return self._phase2_implementation(attempt + 1)
    
    def _critique_results(self, result: dict) -> dict:
        """Critique the backtest results."""
        return self._critique_results_llm(result)
    
    def _critique_results_llm(self, result: dict) -> dict:
        """LLM-based result validation with structured output."""
        prompt = f"""Evaluate this backtest result:

REQUIREMENTS: {self._format_requirements()}
CODE: {self.code}
OUTPUT: {result['output']}

Is this backtest ACCEPTABLE? Respond only with JSON:
{{"acceptable": true/false, "reason": "brief explanation"}}"""
        
        try:
            validation_llm = LLM("gpt-4o-mini")
            response = validation_llm.ask(prompt).strip()
            
            # Extract JSON
            import json
            if response.startswith('```'):
                response = response.split('```')[1].strip()
                if response.startswith('json'):
                    response = response[4:].strip()
            
            data = json.loads(response)
            return {
                "proceed": data.get("acceptable", False),
                "critique": data.get("reason", "No reason provided")
            }
        except Exception:
            # Fallback to original logic
            return self._critique_results_original(result)
    
    def _critique_results_original(self, result: dict) -> dict:
        """Original critique logic (fallback)."""
        critique_prompt = f"""Evaluate this backtest result:

REQUIREMENTS:
{self._format_requirements()}

CODE:
{self.code}

RESULTS:
{result['output']}

EVALUATION:
✓ Code executed without errors
✓ Shows backtest results (Return %, Equity Final, etc.)
✓ Uses correct ticker, period, capital
✓ Implements the requested strategy

DECISION: [PROCEED or RETRY]

If results are shown and requirements met, say PROCEED."""

        try:
            critique = self.code_llm.ask(critique_prompt)
            proceed = "PROCEED" in critique.upper()
            return {"proceed": proceed, "critique": critique}
        except Exception as e:
            return {"proceed": False, "critique": f"Critique error: {e}"}
    
    def _phase3_reporting(self) -> str:
        """Phase 3: Plan, write, refine report."""
        # Try to extract structured outputs from results
        trades_csv = None
        equity_csv = None
        summary_json = None
        if isinstance(self.results, str):
            text = self.results
            if "SUMMARY_JSON" in text:
                try:
                    summary_json = text.split("SUMMARY_JSON", 1)[1].strip().splitlines()[0]
                except Exception:
                    pass
            if "TRADES_CSV" in text:
                try:
                    trades_csv = text.split("TRADES_CSV", 1)[1].strip()
                    # Keep until next marker if present
                    if "EQUITY_CSV" in trades_csv:
                        trades_csv = trades_csv.split("EQUITY_CSV", 1)[0].strip()
                except Exception:
                    pass
            if "EQUITY_CSV" in text:
                try:
                    equity_csv = text.split("EQUITY_CSV", 1)[1].strip()
                except Exception:
                    pass

        # Save assets folder
        import os
        from datetime import datetime
        os.makedirs("reports", exist_ok=True)
        ticker_slug = (self.requirements.get('ticker') or 'TICKER').replace('^','').replace('.','_')
        period_slug = (self.requirements.get('period') or 'PERIOD').replace(' ','').replace(':','-')
        run_dir = f"reports/{ticker_slug}_{period_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(run_dir, exist_ok=True)
        
        # Setup logging for this run
        self.debug_logger, self.agent_logger = setup_run_logging(run_dir)

        # Try generating charts using matplotlib if equity CSV exists
        equity_png = None
        trades_table_md = None
        try:
            import pandas as pd  # type: ignore
            import matplotlib.pyplot as plt  # type: ignore
            if equity_csv:
                from io import StringIO
                eq_df = pd.read_csv(StringIO(equity_csv))
                # Find best equity column via LLM
                ycol = self._find_best_column(list(eq_df.columns), "equity")
                x = eq_df.index if 'index' in eq_df.columns else range(len(eq_df))
                plt.figure(figsize=(8,4))
                plt.plot(eq_df[ycol])
                plt.title('Equity Curve')
                plt.grid(True, alpha=0.3)
                equity_png = os.path.join(run_dir, 'equity.png')
                plt.tight_layout()
                plt.savefig(equity_png, dpi=150)
                plt.close()
            if trades_csv:
                from io import StringIO
                tr_df = pd.read_csv(StringIO(trades_csv))
                # Build a compact markdown table of first 20 trades
                cols = [c for c in tr_df.columns]
                head = tr_df.head(50)
                trades_table_md = "| " + " | ".join(cols) + " |\n" + "|" + "---|"*len(cols) + "\n"
                for _, row in head.iterrows():
                    trades_table_md += "| " + " | ".join(str(row[c]) for c in cols) + " |\n"
        except Exception:
            pass
        # Plan
        plan_prompt = f"""Plan a backtest report structure:

Results:
{self.results}

Code:
{self.code}

Create outline with sections:
1. Summary
2. Strategy
3. Results
4. Insights
5. Code"""

        plan = self.llm.ask(plan_prompt)
        
        # Write
        selected_language = (self.requirements.get('lang') or 'English').strip()
        write_prompt = f"""Write a professional backtest report following this plan:

Plan:
{plan}

Results:
{self.results}

Code:
{self.code}

Requirements:
{self._format_requirements()}

CRITICAL INSTRUCTIONS:
- Write in clean, professional markdown format
- Use actual numbers from the results, not placeholders
- DO NOT include placeholder URLs like "URL_to_equity_curve_image"
- DO NOT include "WIP" or "placeholder" text
- If equity curve data exists, just mention it without placeholder links
- Focus on concrete metrics and clear analysis
- Use bullet points and tables for readability
- Keep sections concise and informative
 - Use this language for the entire report body: {selected_language}

Write the complete report now:"""

        draft = self.llm.ask(write_prompt)
        
        # Generate title via LLM (with fallback to f-string)
        title = self._generate_title()
        summary_title = title

        # Compute TL;DR via LLM so it follows the selected language
        tldr_line = self._llm_tldr(self.results if isinstance(self.results, str) else str(self.results))
        final_md = f"# {summary_title}\n\n**{tldr_line}**\n\n" + draft
        
        # Generate section headings via LLM
        lang = self.requirements.get('lang', 'English')
        if trades_table_md:
            trades_heading = self._generate_section_name("trades", lang)
            final_md += f"\n\n## {trades_heading}\n\n" + trades_table_md
        if equity_png:
            equity_heading = self._generate_section_name("equity_curve", lang)
            final_md += f"\n\n## {equity_heading}\n\n![]({os.path.basename(equity_png)})\n"

        # Save markdown and assets into run directory
        md_path = os.path.join(run_dir, 'report.md')
        with open(md_path, 'w') as f:
            f.write(final_md)
        
        # Save strategy.py (generated code)
        strategy_path = os.path.join(run_dir, 'strategy.py')
        with open(strategy_path, 'w') as f:
            f.write(f"# Generated by NLBT on {datetime.now()}\n")
            f.write(f"# {self._format_requirements()}\n\n")
            f.write(self.code)
        
        # Save agent.log (full context for LLM)
        if self.agent_logger:
            # Metadata
            self.agent_logger.info("=== METADATA ===")
            self.agent_logger.info(f"timestamp: {datetime.now()}")
            self.agent_logger.info(f"run_dir: {run_dir}")
            try:
                import subprocess
                git_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
                self.agent_logger.info(f"git_sha: {git_sha}")
            except:
                pass
            self.agent_logger.info("")
            
            # Codebase snapshot
            self.agent_logger.info("=== CODEBASE ===")
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            for pattern in ["src/**/*.py", "*.toml", "README.md"]:
                for file_path in glob.glob(os.path.join(base_dir, pattern), recursive=True):
                    rel_path = os.path.relpath(file_path, base_dir)
                    self.agent_logger.info(f"--- {rel_path} ---")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self.agent_logger.info(f.read())
                    except:
                        self.agent_logger.info("[Could not read file]")
                    self.agent_logger.info("")
            
            # Conversation history
            self.agent_logger.info("=== CONVERSATION ===")
            self.agent_logger.info("\n".join(self.history))
            self.agent_logger.info("")
            
            # Generated code
            self.agent_logger.info("=== GENERATED CODE ===")
            self.agent_logger.info(self.code)
            self.agent_logger.info("")
            
            # Backtest output
            self.agent_logger.info("=== BACKTEST OUTPUT ===")
            self.agent_logger.info(self.results)
            self.agent_logger.info("")

        # Convert markdown to PDF
        try:
            # Try using pandoc first (best quality)
            import subprocess
            pdf_path = os.path.join(run_dir, 'report.pdf')
            result = subprocess.run([
                'pandoc', md_path, '-o', pdf_path,
                '--pdf-engine=xelatex',
                '--variable', 'geometry:margin=1in'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"Pandoc failed: {result.stderr}")
                
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            # Fallback: Try weasyprint
            try:
                import weasyprint
                from markdown import markdown
                
                # Convert markdown to HTML first
                with open(md_path, 'r') as f:
                    md_content = f.read()
                
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                              line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                        h2 {{ color: #34495e; margin-top: 30px; }}
                        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        code {{ background-color: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
                        pre {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                    </style>
                </head>
                <body>
                {markdown(md_content, extensions=['tables', 'fenced_code'])}
                </body>
                </html>
                """
                
                pdf_path = os.path.join(run_dir, 'report.pdf')
                weasyprint.HTML(string=html_content).write_pdf(pdf_path)
                
            except ImportError:
                # Final fallback: Simple matplotlib PDF (current implementation)
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_pdf import PdfPages
                
                pdf_path = os.path.join(run_dir, 'report.pdf')
                with PdfPages(pdf_path) as pdf:
                    # Page 1: Title and summary
                    plt.figure(figsize=(8.27, 11.69))
                    plt.axis('off')
                    plt.text(0.5, 0.95, 'NLBT Backtest Report', ha='center', va='top', fontsize=18, weight='bold')
                    
                    # Add the report content as text (first 2000 chars)
                    with open(md_path, 'r') as f:
                        content = f.read()[:2000] + "..." if len(f.read()) > 2000 else f.read()
                    
                    plt.text(0.05, 0.85, content, ha='left', va='top', fontsize=8, 
                            family='monospace', wrap=True)
                    pdf.savefig()
                    plt.close()
        
        self.phase = "complete"
        return f"""🎉 COMPLETE! All 3 phases finished successfully.

📄 REPORT FOLDER: {run_dir}
• User report: report.md, report.pdf
• Developer trace: debug.log, strategy.py
• Agent context: agent.log

📈 WHAT YOU GOT:
• Complete backtest analysis with performance metrics
• Strategy insights and recommendations  
• Full Python code for reproducibility
• Professional markdown report ready to share
• Debug logs and full context for iteration

💡 NEXT STEPS:
• Check the report: {md_path}
• Try another strategy with different parameters
• Ask me to explain any results you don't understand

✨ Thanks for using the Reflection Backtesting Assistant!"""

    def _llm_tldr(self, results_text: str) -> str:
        """Produce a single-line summary: strategy, end date, cash, equity, portfolio."""
        strategy = (self.requirements.get('strategy') or '').strip()
        capital = (self.requirements.get('capital') or '').strip()
        selected_language = (self.requirements.get('lang') or 'English').strip()
        prompt = (
            "You will receive: strategy text, initial capital, and raw backtest stats.\n"
            "Output ONE line only, exactly in this format (no extra words).\n"
            "Write the output in this language: " + selected_language + "\n"
            "Format: Strategy: <STRATEGY> · End: <YYYY-MM-DD> · Initial: <INITIAL> · Equity: <EQUITY> · Portfolio: <PORTFOLIO>\n"
            "Rules:\n"
            "- STRATEGY: use the given strategy text as-is (shorten only if extremely long).\n"
            "- INITIAL: echo the provided initial capital (keep currency symbol/commas if present).\n"
            "- End: extract from stats (field 'End' or similar date). Use YYYY-MM-DD.\n"
            "- Equity and Portfolio: use the ending equity from stats (e.g., 'Equity Final [$]').\n"
            "- If multiple numeric formats appear, choose the clearest currency-labelled value.\n"
            "- No newlines, no explanations, one single line.\n\n"
            f"STRATEGY:\n{strategy}\n\n"
            f"CAPITAL:\n{capital}\n\n"
            f"STATS:\n{results_text}\n\n"
            "ONE-LINE OUTPUT:"
        )
        try:
            line = self.llm.ask(prompt).splitlines()[0].strip()
            return line if line else "Summary unavailable"
        except Exception:
            return "Summary unavailable"
    
    def _generate_title(self) -> str:
        """Generate report title via LLM."""
        ticker = self.requirements.get('ticker', 'Unknown')
        period = self.requirements.get('period', 'Unknown')
        strategy = self.requirements.get('strategy', 'Strategy')
        lang = self.requirements.get('lang', 'English')
        
        prompt = f"""Generate a concise report title (max 10 words).
Ticker: {ticker}
Period: {period}
Strategy: {strategy}
Language: {lang}

Output only the title, no quotes or punctuation at end."""
        
        try:
            # Use fast model (gpt-4o-mini for speed)
            title_llm = LLM("gpt-4o-mini")
            title = title_llm.ask(prompt).strip().strip('"\'.')
            if title and len(title) < 100:
                return title
        except Exception as e:
            pass
        
        # Fallback
        return f"{ticker} {period} Trading Strategy"
    
    def _should_proceed(self, user_input: str) -> bool:
        """Check if user wants to proceed with implementation via LLM."""
        prompt = f"""User said: "{user_input}"

Context: User has confirmed requirements and is being asked if they want to proceed with implementation.

Does the user want to proceed? Answer ONLY with YES or NO.

YES means: User agrees, confirms, wants to start (e.g., "yes", "go", "ok", "proceed", "let's do it")
NO means: User wants to change something, ask questions, or wait (e.g., "change ticker", "explain first", "wait")

Answer:"""
        
        try:
            # Use fast model
            proceed_llm = LLM("gpt-4o-mini")
            response = proceed_llm.ask(prompt).strip().upper()
            return "YES" in response and "NO" not in response
        except:
            pass
        
        # Fallback to simple keyword matching
        import re
        user_lower = user_input.lower().strip()
        proceed_words = ["yes", "go", "proceed", "ok", "start", "continue"]
        proceed_pattern = r'\b(' + '|'.join(proceed_words) + r')\b'
        conflict_words = ["but", "change", "explain", "first", "wait", "think", "over", "else"]
        has_conflict = any(word in user_lower for word in conflict_words)
        return re.search(proceed_pattern, user_lower) and not has_conflict
    
    def _generate_section_name(self, section_type: str, language: str = "English") -> str:
        """Generate section heading via LLM."""
        prompt = f"""Generate a section heading for a financial backtest report.
Section type: {section_type}
Language: {language}

Output only the heading text (2-4 words), no markdown ##, no punctuation at end."""
        
        try:
            section_llm = LLM("gpt-4o-mini")
            heading = section_llm.ask(prompt).strip().strip('#').strip()
            if heading and len(heading) < 50:
                return heading
        except:
            pass
        
        # Fallback
        fallbacks = {
            "trades": "Trades (first 50)",
            "equity_curve": "Equity Curve"
        }
        return fallbacks.get(section_type, section_type.title())
    
    def _find_best_column(self, df_columns: list, target_type: str) -> str:
        """Find best column name via LLM."""
        columns_str = ", ".join(df_columns)
        prompt = f"""Given these DataFrame columns: {columns_str}

Which column likely contains {target_type} data? Answer with ONLY the exact column name.

{target_type} typically contains values like equity, portfolio value, or account balance over time."""
        
        try:
            col_llm = LLM("gpt-4o-mini")
            response = col_llm.ask(prompt).strip().strip('"\'')
            if response in df_columns:
                return response
        except:
            pass
        
        # Fallback logic
        if target_type == "equity":
            for col in df_columns:
                if 'equity' in col.lower():
                    return col
            return df_columns[-1]  # Last column as fallback
        
        return df_columns[0] if df_columns else "Value"
    
    def _get_history(self) -> str:
        """Get recent conversation with better context."""
        if not self.history:
            return "No previous conversation."
        
        # Get last 6 exchanges (3 back-and-forth)
        recent = self.history[-6:]
        
        # Format nicely and include any requirements we've gathered
        formatted = "\n".join(recent)
        
        if self.requirements:
            formatted += f"\n\nCURRENT REQUIREMENTS GATHERED:\n"
            for key, value in self.requirements.items():
                formatted += f"- {key.title()}: {value}\n"
        
        return formatted
    
    def _extract_requirements_llm(self, user_input: str) -> dict:
        """Extract requirements via LLM with structured JSON output."""
        prompt = f"""Extract trading requirements from this user message: "{user_input}"

Output ONLY valid JSON with these fields (use null if not found):
{{
  "ticker": "stock symbol (e.g. AAPL, RELIANCE.NS, ^NSEI)",
  "period": "time period (e.g. 2024, 2023, 2020-2024)", 
  "capital": "initial capital with currency (e.g. $10000, ₹500000)",
  "strategy": "trading strategy description",
  "lang": "language preference (e.g. English, Spanish, Hindi)"
}}

Examples:
- "Buy AAPL in 2024 with $10K" → {{"ticker": "AAPL", "period": "2024", "capital": "$10000", "strategy": "buy", "lang": null}}
- "NVDA RSI strategy, 2023, ₹50000, lang Hindi" → {{"ticker": "NVDA", "period": "2023", "capital": "₹50000", "strategy": "RSI strategy", "lang": "Hindi"}}

JSON:"""
        
        try:
            extract_llm = LLM("gpt-4o-mini")
            response = extract_llm.ask(prompt).strip()
            
            # Extract JSON from response
            import json
            if response.startswith('```'):
                response = response.split('```')[1].strip()
                if response.startswith('json'):
                    response = response[4:].strip()
            
            data = json.loads(response)
            return {k: v for k, v in data.items() if v is not None}
        except:
            return {}
    
    def _update_requirements_from_conversation(self, user_input: str):
        """Extract requirements from natural conversation."""
        # Try LLM extraction first
        llm_extracted = self._extract_requirements_llm(user_input)
        
        # Update requirements with LLM results (only if not already set)
        for key, value in llm_extracted.items():
            if not self.requirements.get(key) and value:
                self.requirements[key] = value
        
        # Fallback to regex parsing for any missing fields
        if not self.requirements.get("ticker") or not self.requirements.get("period") or not self.requirements.get("capital") or not self.requirements.get("strategy"):
            self._regex_fallback_extraction(user_input)
    
    def _regex_fallback_extraction(self, user_input: str):
        """Fallback regex extraction (original logic)."""
        user_lower = user_input.lower()
        
        # Extract ticker symbols with improved logic
        import re

        # Look for ticker patterns in the entire input (more flexible)
        ticker_patterns = [
            r'\b([A-Z]{2,5})\b',  # Standard ticker format
            r'ticker[:\s]+([A-Z]{2,5})',  # Explicit ticker mentions
            r'stock[:\s]+([A-Z]{2,5})',   # Stock mentions
        ]

        for pattern in ticker_patterns:
            matches = re.findall(pattern, user_input)
            for potential_ticker in matches:
                potential_ticker = potential_ticker.upper()
                if not self.requirements.get("ticker"):
                    self.requirements["ticker"] = potential_ticker
                    break
            if self.requirements.get("ticker"):
                break
        
        # Extract periods
        if "2024" in user_input and not self.requirements.get("period"):
            self.requirements["period"] = "2024"
        elif "2023" in user_input and not self.requirements.get("period"):
            self.requirements["period"] = "2023"  
        elif re.search(r'20\d{2}\s*to\s*20\d{2}', user_input) and not self.requirements.get("period"):
            period_match = re.search(r'(20\d{2}\s*to\s*20\d{2})', user_input)
            if period_match:
                self.requirements["period"] = period_match.group(1)
        
        # Extract capital amounts: support $ and ₹ / INR and Indian commas
        if not self.requirements.get("capital"):
            import re as _re
            cap_num = None
            m_usd = _re.search(r'\$\s*([0-9,]+(?:K|k)?)', user_input)
            m_inr = _re.search(r'(?:₹|INR)\s*([0-9,]+)', user_input, _re.IGNORECASE)
            if m_usd:
                cap = m_usd.group(1).replace(',', '')
                if cap.lower().endswith('k'):
                    cap_num = int(float(cap[:-1]) * 1000)
                else:
                    cap_num = int(cap)
                self.requirements["capital"] = f"${cap_num}"
            elif m_inr:
                cap = m_inr.group(1).replace(',', '')
                cap_num = int(cap)
                self.requirements["capital"] = f"₹{cap_num}"

        # Extract language preference (e.g., "lang hi", "language: Spanish")
        if not self.requirements.get("lang"):
            try:
                import re as _re2
                m_lang = _re2.search(r'\blang(?:uage)?[:\s]+([A-Za-z\-]+)', user_input, _re2.IGNORECASE)
                if m_lang:
                    self.requirements["lang"] = m_lang.group(1).strip()
            except Exception:
                pass
        
        # Extract strategy - look for complete trading descriptions
        if not self.requirements.get("strategy"):
            strategy_patterns = [
                r'buy.*?stop.*?loss.*?take.*?profit',  # Buy with stop loss and take profit
                r'buy.*?open',  # Buy at open
                r'sell.*?close',  # Sell at close
                r'moving.*?average',  # Moving average strategies
                r'rsi.*?buy.*?sell',  # RSI strategies
                r'ema.*?buy.*?sell',  # EMA strategies
                r'sma.*?buy.*?sell',  # SMA strategies
            ]

            # Also check for any mention of trading rules
            if any(word in user_lower for word in ["buy", "sell", "stop loss", "take profit", "entry", "exit", "hold"]):
                # Extract the full strategy description if it contains trading terms
                words = user_input.split()
                if len(words) >= 2:  # At least 2 words (e.g., "buy hold")
                    # Find the FIRST part with trading terms (could be at the beginning)
                    strategy_start = -1
                    for i, word in enumerate(words):
                        if word.lower() in ["buy", "sell", "enter", "exit", "stop", "take", "profit", "test", "trading", "hold"]:
                            strategy_start = i
                            break

                    if strategy_start != -1:
                        strategy_text = ' '.join(words[strategy_start:])
                        if len(strategy_text) >= 5 and not self.requirements.get("strategy"):  # At least 5 chars
                            self.requirements["strategy"] = strategy_text.strip()
                    else:
                        # If no clear start found, check if the whole input looks like a strategy
                        if len(user_input) > 5 and not self.requirements.get("strategy"):
                            self.requirements["strategy"] = user_input.strip()
                elif len(words) == 1 and len(user_input) >= 5:
                    # Single word that's a strategy keyword
                    if any(kw in user_lower for kw in ["buy", "sell", "hold"]):
                        self.requirements["strategy"] = user_input.strip()

            # Special case: if we have most requirements but strategy seems incomplete, use full input
            if (self.requirements.get("ticker") and self.requirements.get("period") and
                self.requirements.get("capital") and not self.requirements.get("strategy")):
                if len(user_input) > 20:
                    self.requirements["strategy"] = user_input.strip()

            # Legacy keyword extraction for backup
            strategy_keywords = []
            if "buy" in user_lower and "monday" in user_lower:
                strategy_keywords.append("buy on Monday")
            if "rsi" in user_lower:
                strategy_keywords.append("RSI strategy")
            if "moving average" in user_lower or "ma" in user_lower:
                strategy_keywords.append("moving average")
            if "bollinger" in user_lower:
                strategy_keywords.append("Bollinger Bands")

            if strategy_keywords and not self.requirements.get("strategy"):
                self.requirements["strategy"] = ", ".join(strategy_keywords)
    
    def _extract_requirements(self, response: str):
        """Parse requirements from LLM response."""
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if "TICKER:" in line and "MISSING" not in line and "?" not in line:
                self.requirements["ticker"] = line.split("TICKER:")[1].strip()
            elif "PERIOD:" in line and "MISSING" not in line and "?" not in line:
                self.requirements["period"] = line.split("PERIOD:")[1].strip()
            elif "CAPITAL:" in line and "MISSING" not in line and "?" not in line:
                self.requirements["capital"] = line.split("CAPITAL:")[1].strip()
            elif "STRATEGY:" in line and "MISSING" not in line and "?" not in line:
                self.requirements["strategy"] = line.split("STRATEGY:")[1].strip()
    
    def _format_requirements(self) -> str:
        """Format current requirements for display with better context."""
        if not self.requirements:
            return "No requirements gathered yet."
        
        formatted = []
        for key, value in self.requirements.items():
            formatted.append(f"- {key.title()}: {value}")
        return "\n".join(formatted)

