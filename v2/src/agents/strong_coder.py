"""Strong Coding Agent - Phase 2 implementation."""

from ..llm import LLM
from ..sandbox import Sandbox


class StrongCoder:
    """Generates and tests backtesting code."""
    
    def __init__(self):
        self.llm = LLM(model_type="strong")  # Use strong model for code generation
        self.sandbox = Sandbox()
    
    def generate_and_test(self, requirements: dict, attempt: int = 1) -> dict:
        """
        Generate code and test it.
        
        Returns:
            {
                "success": bool,
                "code": str,
                "results": str,
                "error": str  # If failed
            }
        """
        # For now, return hardcoded response
        code = """
from backtesting import Backtest, Strategy

data = get_ohlcv_data('AAPL', '2024-01-01', '2024-12-31')

class BuyAndHold(Strategy):
    def init(self):
        pass
    
    def next(self):
        if not self.position:
            self.buy()

bt = Backtest(data, BuyAndHold, cash=10000)
stats = bt.run()
print(stats)
"""
        
        return {
            "success": True,
            "code": code,
            "results": "Backtest results here...",
            "error": None
        }
    
    def _build_prompt(self, requirements: dict) -> str:
        """Build code generation prompt."""
        # TODO: Include downstream reporter requirements
        return f"Generate backtesting code for: {requirements}"
