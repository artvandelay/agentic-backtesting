"""Junior Coding Agent - Phase 1 feasibility validator."""

from ..llm import LLM
import re


class JrCoder:
    """Validates if strategy is implementable with current scaffold."""
    
    def __init__(self):
        self.llm = LLM(model_type="weak")  # Use weak model for cost efficiency
    
    def validate(self, requirements: dict) -> dict:
        """
        Validate if requirements are implementable.
        
        Returns:
            {
                "implementable": bool,
                "clarifications": list[str]  # If not implementable
            }
        """
        prompt = self._build_prompt(requirements)
        response = self.llm.ask(prompt)
        return self._parse_response(response)
    
    def _build_prompt(self, requirements: dict) -> str:
        """Build validation prompt with scaffold context."""
        # Get scaffold capabilities
        scaffold_context = self._get_scaffold_context()
        
        return f"""You are a junior coding agent validating if a trading strategy can be implemented.

STRATEGY REQUIREMENTS:
- Ticker: {requirements.get('ticker', 'Not specified')}
- Period: {requirements.get('period', 'Not specified')}
- Capital: {requirements.get('capital', 'Not specified')}
- Strategy: {requirements.get('strategy', 'Not specified')}

SCAFFOLD CAPABILITIES:
{scaffold_context}

VALIDATION RULES:
1. Single ticker only (no portfolio rotation)
2. Must use backtesting.py library structure
3. Entry/exit rules must be clearly defined
4. Supported indicators: SMA, EMA, RSI, MACD, Bollinger Bands, ATR
5. Yahoo Finance data availability required

OUTPUT FORMAT (strict):
CAN CODE
or
NEED CLARIFICATION:
- [specific issue 1]
- [specific issue 2]

EXAMPLES OF CLARIFICATIONS:
- "Define 'drops 5%' - is this from previous close or intraday?"
- "Specify exact RSI periods and thresholds"
- "This requires multiple tickers - please choose one"

Be specific and actionable in clarifications!"""
    
    def _parse_response(self, response: str) -> dict:
        """Parse validation response."""
        if "CAN CODE" in response:
            return {
                "implementable": True,
                "clarifications": []
            }
        
        # Extract clarifications
        clarifications = []
        if "NEED CLARIFICATION:" in response:
            lines = response.split('\n')
            capture = False
            for line in lines:
                if "NEED CLARIFICATION:" in line:
                    capture = True
                    continue
                if capture and line.strip().startswith('-'):
                    clarifications.append(line.strip()[1:].strip())
        
        return {
            "implementable": False,
            "clarifications": clarifications if clarifications else ["Please provide more specific details about your strategy"]
        }
    
    def _get_scaffold_context(self) -> str:
        """Return scaffold capabilities summary."""
        return """
AVAILABLE FUNCTIONS:
- get_ohlcv_data(ticker, start_date, end_date) → DataFrame with Open/High/Low/Close/Volume

AVAILABLE LIBRARIES:
- backtesting: Main framework (Backtest, Strategy classes)
- ta: Technical indicators library
- pandas, numpy: Data manipulation

STRATEGY CLASS STRUCTURE:
class MyStrategy(Strategy):
    def init(self):
        # Initialize indicators
        
    def next(self):
        # Trading logic (if not self.position: self.buy())
        
KEY LIMITATIONS:
- Single ticker per backtest (BUT correlation-based signals are OK if they use one primary ticker)
- No options/futures  
- No intraday data (daily bars only)
- No custom order types (market orders only)

CORRELATION-BASED STRATEGIES (SUPPORTED):
✅ "SPY strategy using VIX correlation" → Use SPY as primary ticker, VIX correlation as signal
✅ "Trade AAPL based on SPY momentum" → Use AAPL as primary ticker, SPY as signal
✅ "QQQ mean reversion with market sentiment" → Use QQQ as primary ticker

MULTI-ASSET ROTATION (NOT SUPPORTED):
❌ "Rotate between AAPL, GOOGL, TSLA" → Requires portfolio rotation
❌ "Equal weight SPY and QQQ" → Requires multiple positions"""
