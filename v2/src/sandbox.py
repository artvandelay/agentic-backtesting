"""Minimal sandbox for code execution."""

import io
import sys
from contextlib import redirect_stdout, redirect_stderr


class Sandbox:
    """Execute code safely."""
    
    def run(self, code: str) -> dict:
        """Execute Python code, return results."""
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Build safe globals with required libraries
        safe_globals = self._get_globals()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, safe_globals)
            
            return {
                "success": True,
                "output": stdout_capture.getvalue(),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": stdout_capture.getvalue(),
                "error": f"{type(e).__name__}: {str(e)}\n{stderr_capture.getvalue()}"
            }
    
    def _get_globals(self) -> dict:
        """Get safe global namespace with libraries."""
        import importlib
        
        globals_dict = {"__builtins__": __builtins__}
        
        # Allow these libraries
        for lib in ["pandas", "numpy", "backtesting", "ta"]:
            try:
                globals_dict[lib] = importlib.import_module(lib)
            except ImportError:
                pass
        
        # Add helper function
        globals_dict["get_ohlcv_data"] = self._get_data
        
        # Intentionally no indicator fallbacks — coding agent must use libraries (ta, etc.)
        
        return globals_dict
    
    def _get_data(self, ticker: str, start: str, end: str):
        """Helper to fetch OHLCV data for backtesting.py library."""
        import yfinance as yf
        import pandas as pd
        
        # Download data
        data = yf.download(ticker, start=start, end=end, progress=False)
        
        # Remove timezone if present
        if data.index.tz:
            data = data.tz_localize(None)
        
        # Handle MultiIndex columns (yfinance returns (column_name, ticker))
        # We need to keep just the column names: Open, High, Low, Close, Volume
        if isinstance(data.columns, pd.MultiIndex):
            # Drop the ticker level (level 1), keep column names (level 0)
            data.columns = data.columns.droplevel(1)
        
        return data
