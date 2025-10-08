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
        # Generate TL;DR
        tldr = self._generate_tldr(requirements, results)
        
        # Generate full report with LLM
        report_prompt = f"""Generate a professional markdown backtest report.

REQUIREMENTS:
{requirements}

RESULTS:
{results}

CODE:
{code}

FORMAT:
# Backtest Report

## TL;DR
{tldr}

## Strategy Overview
[Brief description of the strategy]

## Performance Summary
[Key metrics in a readable format]

## Detailed Results
```
{results}
```

## Implementation
```python
{code}
```

## Observations
[Any notable patterns or insights]

Generate a clean, professional report."""

        report = self.llm.ask(report_prompt)
        
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
            "tldr": tldr,
            "needs_retry": False
        }
    
    def _generate_tldr(self, requirements: dict, results: str) -> str:
        """Generate one-line TL;DR summary."""
        # Extract key metrics from results
        import re
        
        # Try to extract final equity
        equity_match = re.search(r'Equity Final \[\$\]\s+([\d.]+)', results)
        equity = f"${float(equity_match.group(1)):,.2f}" if equity_match else "Unknown"
        
        # Extract return
        return_match = re.search(r'Return \[%\]\s+([\d.-]+)', results)
        returns = f"{float(return_match.group(1)):.2f}%" if return_match else "Unknown"
        
        # Extract max drawdown
        dd_match = re.search(r'Max\. Drawdown \[%\]\s+([\d.-]+)', results)
        max_dd = f"{float(dd_match.group(1)):.2f}%" if dd_match else "Unknown"
        
        # Build TL;DR
        strategy = requirements.get('strategy', 'Unknown strategy')
        capital = requirements.get('capital', 'Unknown')
        
        if "Unknown" not in returns:
            verdict = "📈 Profitable" if float(returns[:-1]) > 0 else "📉 Loss"
        else:
            verdict = "Results"
            
        return f"{verdict} · {strategy} · Return: {returns} · Max DD: {max_dd} · Final: {equity}"
    
    def _build_prompt(self, requirements: dict, code: str, results: str) -> str:
        """Build report generation prompt."""
        return f"Generate report for: {results}"
