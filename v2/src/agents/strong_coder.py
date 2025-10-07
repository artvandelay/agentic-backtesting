"""Strong Coding Agent - Phase 2 implementation."""

from ..llm import LLM
from ..sandbox import Sandbox
import re


class StrongCoder:
    """Generates and tests backtesting code."""
    
    def __init__(self):
        self.llm = LLM(model_type="strong")  # Use strong model for code generation
        self.sandbox = Sandbox()
    
    def generate_and_test(self, requirements: dict, attempt: int = 1, feedback: str = None) -> dict:
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
        # Generate code
        prompt = self._build_prompt(requirements, attempt, feedback)
        code = self.llm.ask(prompt)
        
        # Clean code (remove markdown fences)
        code = self._clean_code(code)
        
        # Test in sandbox
        result = self.sandbox.run(code)
        
        return {
            "success": result["success"],
            "code": code,
            "results": result["output"],
            "error": result["error"]
        }
    
    def _build_prompt(self, requirements: dict, attempt: int, feedback: str = None) -> str:
        """Build code generation prompt."""
        # Extract dates from period
        period = requirements.get('period', '2024')
        dates = self._parse_period(period)
        
        # Clean capital amount
        capital = requirements.get('capital', '$10,000')
        capital_num = self._parse_capital(capital)
        
        base_prompt = f"""Generate Python code for backtesting this trading strategy.

REQUIREMENTS:
- Ticker: {requirements.get('ticker', 'AAPL')}
- Period: {period} (use dates {dates['start']} to {dates['end']})
- Capital: {capital} (use {capital_num} as number)
- Strategy: {requirements.get('strategy', 'Buy and hold')}

IMPORTANT RULES:
1. Use the backtesting.py library structure exactly
2. Use get_ohlcv_data(ticker, start, end) to fetch data
3. Create a Strategy class inheriting from Strategy
4. Implement init() and next() methods
5. Print the full stats object at the end
6. Add helpful comments

CODE STRUCTURE:
from backtesting import Backtest, Strategy

# Fetch data
data = get_ohlcv_data('TICKER', 'START_DATE', 'END_DATE')

class MyStrategy(Strategy):
    def init(self):
        # Initialize indicators here
        
    def next(self):
        # Trading logic here
        
# Run backtest
bt = Backtest(data, MyStrategy, cash=CAPITAL)
stats = bt.run()
print(stats)

Generate ONLY the Python code, no explanations."""

        if attempt > 1 and feedback:
            base_prompt += f"\n\nPREVIOUS ATTEMPT FAILED:\n{feedback}\n\nFix the issue and generate corrected code."
            
        return base_prompt
    
    def _clean_code(self, code: str) -> str:
        """Remove markdown fences and clean code."""
        # Remove ```python and ``` markers
        code = re.sub(r'^```\w*\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'\n```$', '', code, flags=re.MULTILINE)
        return code.strip()
    
    def _parse_period(self, period: str) -> dict:
        """Parse period string into start/end dates."""
        # Handle various formats
        if 'to' in period.lower():
            parts = period.lower().split('to')
            start_year = re.search(r'\d{4}', parts[0])
            end_year = re.search(r'\d{4}', parts[1])
            if start_year and end_year:
                return {
                    'start': f"{start_year.group()}-01-01",
                    'end': f"{end_year.group()}-12-31"
                }
        
        # Single year
        year_match = re.search(r'\d{4}', period)
        if year_match:
            year = year_match.group()
            return {
                'start': f"{year}-01-01",
                'end': f"{year}-12-31"
            }
        
        # Default
        return {'start': '2024-01-01', 'end': '2024-12-31'}
    
    def _parse_capital(self, capital: str) -> int:
        """Parse capital string into number."""
        # Remove currency symbols and commas
        clean = re.sub(r'[$,₹]', '', capital)
        # Extract number
        num_match = re.search(r'\d+', clean)
        if num_match:
            value = int(num_match.group())
            # Handle K notation
            if 'k' in capital.lower():
                value *= 1000
            return value
        return 10000  # Default
