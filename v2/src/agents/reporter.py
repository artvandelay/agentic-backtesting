"""Reporter agent - Phase 3 report generator."""

from ..llm import LLM
import os
from datetime import datetime
import re


class Reporter:
    """Generates professional reports from backtest results."""
    
    def __init__(self):
        self.llm = LLM(model_type="default")
    
    def generate_report(self, requirements: dict, code: str, results: str, conversation_history: list = None) -> dict:
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
        
        # Save report with v1 naming convention
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ticker_slug = (requirements.get('ticker', 'UNKNOWN')).replace('^','').replace('.','_')
        period_slug = (requirements.get('period', 'UNKNOWN')).replace(' ','').replace(':','-').replace('to','-')
        report_dir = f"reports/{ticker_slug}_{period_slug}_{timestamp}"
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = f"{report_dir}/report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        # Save agent.log (agent-readable format)
        agent_log_path = f"{report_dir}/agent.log"
        self._save_agent_log(agent_log_path, requirements, code, results, tldr)
        
        # Save debug.log (everything for developers)
        debug_log_path = f"{report_dir}/debug.log"
        self._save_debug_log(debug_log_path, requirements, code, results, 
                           conversation_history or [], report)
        
        # Generate PDF if possible
        pdf_path = self._generate_pdf(report_dir, report, code, results)
        
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
    
    def _save_agent_log(self, path: str, requirements: dict, code: str, results: str, tldr: str):
        """Save agent-readable log with structured data."""
        import json
        
        agent_data = {
            "requirements": requirements,
            "tldr": tldr,
            "code": code,
            "results_summary": {
                "success": True,
                "metrics": self._extract_metrics(results)
            }
        }
        
        with open(path, 'w') as f:
            json.dump(agent_data, f, indent=2)
    
    def _save_debug_log(self, path: str, requirements: dict, code: str, results: str, 
                       conversation: list, report: str):
        """Save comprehensive debug log for developers."""
        import json
        from datetime import datetime
        
        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "requirements": requirements,
            "conversation_history": conversation,
            "generated_code": code,
            "execution_results": results,
            "final_report": report,
            "system_info": {
                "engine": "v2-triplet",
                "models": {
                    "communicator": "default",
                    "jr_coder": "weak", 
                    "strong_coder": "strong",
                    "reporter": "default"
                }
            }
        }
        
        with open(path, 'w') as f:
            json.dump(debug_data, f, indent=2)
    
    def _extract_metrics(self, results: str) -> dict:
        """Extract key metrics from results text."""
        import re
        
        metrics = {}
        patterns = {
            "final_equity": r'Equity Final \[\$\]\s+([\d.]+)',
            "return_pct": r'Return \[%\]\s+([\d.-]+)',
            "max_drawdown": r'Max\. Drawdown \[%\]\s+([\d.-]+)',
            "sharpe_ratio": r'Sharpe Ratio\s+([\d.-]+)',
            "trades": r'# Trades\s+(\d+)',
            "win_rate": r'Win Rate \[%\]\s+([\d.]+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, results)
            if match:
                metrics[key] = float(match.group(1))
        
        return metrics
    
    def _generate_pdf(self, report_dir: str, report: str, code: str, results: str) -> str:
        """Generate PDF report with charts."""
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_pdf import PdfPages
            import textwrap
            
            pdf_path = f"{report_dir}/report.pdf"
            
            with PdfPages(pdf_path) as pdf:
                # Page 1: Title and summary
                fig = plt.figure(figsize=(8.5, 11))
                fig.text(0.5, 0.8, "Backtest Report", size=24, ha='center', weight='bold')
                
                # Extract TL;DR from report
                tldr_match = re.search(r'## TL;DR\n(.+)', report)
                if tldr_match:
                    tldr_text = tldr_match.group(1)
                    fig.text(0.5, 0.7, tldr_text, size=12, ha='center', wrap=True)
                
                # Add metrics summary
                metrics = self._extract_metrics(results)
                y = 0.5
                for key, value in metrics.items():
                    fig.text(0.3, y, f"{key.replace('_', ' ').title()}:", size=10)
                    fig.text(0.6, y, f"{value}", size=10)
                    y -= 0.05
                
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
                
                # Page 2: Code
                fig = plt.figure(figsize=(8.5, 11))
                fig.text(0.5, 0.95, "Implementation Code", size=16, ha='center', weight='bold')
                
                # Wrap code text
                wrapped_code = textwrap.fill(code, width=80)
                fig.text(0.1, 0.1, wrapped_code[:2000], size=8, family='monospace', va='bottom')
                
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
            
            return pdf_path
            
        except Exception as e:
            # PDF generation is optional, don't fail
            print(f"PDF generation skipped: {e}")
            return None
