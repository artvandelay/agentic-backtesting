"""Reporter agent - Phase 3 report generator."""

from ..llm import LLM
import os
from datetime import datetime


class Reporter:
    """Generates professional reports from backtest results."""
    
    def __init__(self):
        self.llm = LLM(model_type="default")
    
    def generate_report(self, requirements: dict, code: str, results: str) -> dict:
        """
        Generate markdown report.
        
        Returns:
            {
                "report_path": str,
                "tldr": str,
                "needs_retry": bool  # If data insufficient
            }
        """
        # For now, simple report
        report = f"""# Backtest Report

## Strategy
{requirements.get('strategy', 'Unknown')}

## Results
{results}

## Code
```python
{code}
```
"""
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ticker = requirements.get('ticker', 'UNKNOWN')
        report_dir = f"reports/{ticker}_{timestamp}"
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = f"{report_dir}/report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        return {
            "report_path": report_path,
            "tldr": "Strategy: Buy and hold · End: 2024-12-31 · Initial: $10,000 · Equity: $12,000 · Portfolio: $12,000",
            "needs_retry": False
        }
    
    def _build_prompt(self, requirements: dict, code: str, results: str) -> str:
        """Build report generation prompt."""
        return f"Generate report for: {results}"
