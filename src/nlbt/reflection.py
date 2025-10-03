"""Minimal 3-phase reflection engine."""

import os
from .llm import LLM
from .sandbox import Sandbox


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
    
    def _phase1_understanding(self, user_input: str) -> str:
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
        if has_ticker and has_period and has_capital and has_strategy:
            validation = self._validate_requirements_with_codebase()
            self.last_validation = validation
            if validation.get("implementable"):
                self.phase = "ready_to_implement"
                return f"""STATUS: READY
TICKER: {self.requirements['ticker']}
PERIOD: {self.requirements['period']}
CAPITAL: {self.requirements['capital']}
STRATEGY: {self.requirements['strategy']}

I have everything needed to proceed with the backtest.

✅ All requirements complete!

📋 IMPLEMENTATION PLAN:
I'll create a Python backtesting strategy with these components:
• Data fetching for {self.requirements['ticker']} in {self.requirements['period']}
• Strategy class implementing: {self.requirements['strategy']}
• Backtest execution with {self.requirements['capital']}
• Performance analysis and results

🤔 READY TO PROCEED?
• Type "yes", "go", or "proceed" to start implementation
• Type "change [requirement]" to modify anything
• Type "explain" for more details about the implementation approach"""
            else:
                clar = validation.get("clarifications") or []
                clar_block = "\n".join([f"- {c}" for c in clar]) if clar else "- Please clarify missing or vague details so I can proceed."
                return f"""⚠️ Before I can proceed, I need a few clarifications to ensure this strategy is implementable with the current system:\n{clar_block}\n\nPlease answer these in one message."""

        # Check if LLM says READY
        if "STATUS: READY" in response:
            self._extract_requirements(response)
            validation = self._validate_requirements_with_codebase()
            self.last_validation = validation
            if validation.get("implementable"):
                self.phase = "ready_to_implement"
                return response + f"""

✅ All requirements complete!

📋 IMPLEMENTATION PLAN:
I'll create a Python backtesting strategy with these components:
• Data fetching for {self.requirements.get('ticker', 'the stock')} in {self.requirements.get('period', 'the specified period')}
• Strategy class implementing: {self.requirements.get('strategy', 'your trading rules')}
• Backtest execution with {self.requirements.get('capital', 'your capital')}
• Performance analysis and results

🤔 READY TO PROCEED?
• Type "yes", "go", or "proceed" to start implementation
• Type "change [requirement]" to modify anything
• Type "explain" for more details about the implementation approach"""
            else:
                clar = validation.get("clarifications") or []
                clar_block = "\n".join([f"- {c}" for c in clar]) if clar else "- Please clarify missing or vague details so I can proceed."
                return f"""⚠️ Before I can proceed, I need a few clarifications to ensure this strategy is implementable with the current system:\n{clar_block}\n\nPlease answer these in one message."""
        
        return response
    
    def _handle_implementation_confirmation(self, user_input: str) -> str:
        """Handle user confirmation before starting implementation."""
        user_lower = user_input.lower().strip()
        
        # Check for proceed signals
        if any(word in user_lower for word in ["yes", "go", "proceed", "ok", "start", "continue"]):
            self.phase = "implementation"
            
            # Immediately start implementation instead of just showing a message
            implementation_result = self._phase2_implementation()
            return implementation_result
        
        # Check for change requests (including 'sorry')
        if any(word in user_lower for word in ["change", "modify", "update", "actually", "sorry"]):
            self.phase = "understanding"
            
            # Track old values for smart substitution
            old_ticker = self.requirements.get("ticker")
            old_capital = self.requirements.get("capital")
            
            # CRITICAL FIX: Clear requirements that user wants to change
            # Look for what they're changing
            if "period" in user_lower or "date" in user_lower or any(year in user_input for year in ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]):
                self.requirements.pop("period", None)
            
            if "ticker" in user_lower or "stock" in user_lower or any(ticker in user_input.upper() for ticker in ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "SPY", "QQQ", "AMZN", "META"]):
                self.requirements.pop("ticker", None)
            
            if "capital" in user_lower or "$" in user_input or "money" in user_lower:
                self.requirements.pop("capital", None)
            
            if "strategy" in user_lower:
                self.requirements.pop("strategy", None)
            
            # Re-extract from new input
            self._update_requirements_from_conversation(user_input)
            
            # SMART SUBSTITUTION: Update strategy text if ticker or capital changed
            if "strategy" in self.requirements:
                strategy = self.requirements["strategy"]
                
                # If ticker changed, replace old ticker with new ticker in strategy
                new_ticker = self.requirements.get("ticker")
                if old_ticker and new_ticker and old_ticker != new_ticker and old_ticker in strategy:
                    self.requirements["strategy"] = strategy.replace(old_ticker, new_ticker)
                
                # If capital changed, replace old capital with new capital in strategy
                new_capital = self.requirements.get("capital")
                if old_capital and new_capital and old_capital != new_capital and old_capital in strategy:
                    self.requirements["strategy"] = strategy.replace(old_capital, new_capital)
            
            return "Got it! Let me update that for you.\n\n" + self._phase1_understanding(user_input)
        
        # Check for explanation request
        if "explain" in user_lower:
            return f"""📝 DETAILED IMPLEMENTATION APPROACH:

🎯 STRATEGY BREAKDOWN:
{self.requirements.get('strategy', 'Your trading strategy')}

🔧 TECHNICAL IMPLEMENTATION:
1. **Data Setup**: Fetch OHLCV data for {self.requirements.get('ticker', 'ticker')} using yfinance
2. **Indicators**: Calculate RSI, daily returns, and any other required indicators
3. **Entry Logic**: Implement buy conditions (price drops + RSI threshold)
4. **Exit Logic**: Implement sell conditions (profit target, time limit, stop loss)
5. **Position Sizing**: Use {self.requirements.get('capital', 'specified capital')} for position calculation
6. **Backtesting**: Run simulation using backtesting.py library
7. **Analysis**: Generate performance metrics and statistics

💻 CODE STRUCTURE:
- Custom Strategy class inheriting from backtesting.Strategy
- init() method for indicator setup
- next() method for trading logic implementation
- Proper risk management and position sizing

🤔 Ready to proceed with this approach?
• Type "yes" or "go" to start implementation
• Type "change [aspect]" to modify requirements"""
        
        # Handle "no" explicitly
        if user_lower == "no":
            return f"""I understand you're not ready to proceed yet. 

📋 CURRENT PLAN:
• Ticker: {self.requirements.get('ticker', '?')}
• Period: {self.requirements.get('period', '?')}
• Capital: {self.requirements.get('capital', '?')}
• Strategy: {self.requirements.get('strategy', '?')}

What would you like to do?
• "change [requirement]" → Modify something (e.g., "change period to 2020-2023")
• "explain" → See more details about the implementation
• Or just tell me what's wrong and I'll help!"""
        
        # Default response for unclear input
        return f"""🤔 I need your confirmation to proceed.

📋 CURRENT PLAN:
• Ticker: {self.requirements.get('ticker', '?')}
• Period: {self.requirements.get('period', '?')}
• Capital: {self.requirements.get('capital', '?')}
• Strategy: {self.requirements.get('strategy', '?')}

Please choose:
• "yes" or "go" → Start implementation
• "change [requirement]" → Modify something
• "explain" → More details about implementation approach"""
    
    def _phase2_implementation(self, attempt: int = 1) -> str:
        """Phase 2: Producer generates, Critic evaluates."""
        if attempt > 3:
            return f"❌ Failed after 3 attempts.\n\nLast error:\n{self.last_error}"
        
        print(f"🔄 Attempt {attempt}/3 - Generating/Testing/Executing...")
        
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
3. Replace CASH_NUMBER with number from: {self.requirements.get('capital', '$10000')}
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
        
        if "PROCEED" in critique.upper():
            self.phase = "reporting"
            return f"""✅ Implementation successful!

📊 BACKTEST RESULTS:
{self.results}

{self._phase3_reporting()}"""
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
        write_prompt = f"""Write a professional backtest report:

Plan:
{plan}

Results:
{self.results}

Code:
{self.code}

Write in markdown format:"""

        draft = self.llm.ask(write_prompt)
        
        # Save
        import os
        from datetime import datetime
        os.makedirs("reports", exist_ok=True)
        filename = f"reports/backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w") as f:
            f.write(draft)
        
        self.phase = "complete"
        return f"""🎉 COMPLETE! All 3 phases finished successfully.

📄 PROFESSIONAL REPORT SAVED: {filename}

📈 WHAT YOU GOT:
• Complete backtest analysis with performance metrics
• Strategy insights and recommendations  
• Full Python code for reproducibility
• Professional markdown report ready to share

💡 NEXT STEPS:
• Check the report: {filename}
• Try another strategy with different parameters
• Ask me to explain any results you don't understand

✨ Thanks for using the Reflection Backtesting Assistant!"""
    
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
    
    def _update_requirements_from_conversation(self, user_input: str):
        """Extract requirements from natural conversation."""
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
            matches = re.findall(pattern, user_input)  # Find all, no IGNORECASE
            for potential_ticker in matches:
                potential_ticker = potential_ticker.upper()
                # Validate it's a common ticker
                if potential_ticker in ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "SPY", "QQQ", "AMZN", "META", "NFLX"] and not self.requirements.get("ticker"):
                    self.requirements["ticker"] = potential_ticker
                    break
            if self.requirements.get("ticker"):
                break

        # Also check for company names and map to tickers
        company_to_ticker = {
            "amazon": "AMZN",
            "apple": "AAPL",
            "microsoft": "MSFT",
            "tesla": "TSLA",
            "nvidia": "NVDA",
            "google": "GOOGL",
            "meta": "META",
            "netflix": "NFLX",
            "spy": "SPY",
            "qqq": "QQQ"
        }

        for company, ticker in company_to_ticker.items():
            if company in user_lower and not self.requirements.get("ticker"):
                self.requirements["ticker"] = ticker
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
        
        # Extract capital amounts
        capital_match = re.search(r'\$([0-9,]+(?:K|k)?)', user_input)
        if capital_match and not self.requirements.get("capital"):
            self.requirements["capital"] = f"${capital_match.group(1)}"
        
        # Extract strategy - look for complete trading descriptions
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

