"""Minimal LLM client using llm CLI - v2 with weak/strong model support."""

import subprocess
import os
from typing import List, Dict

# Auto-load .env if available (non-fatal if missing)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


class LLM:
    """Simple LLM wrapper with weak/strong model support."""
    
    def __init__(self, model: str = None, model_type: str = "default"):
        """
        Initialize LLM client.
        
        Args:
            model: Explicit model name (overrides environment)
            model_type: One of "default", "weak", "strong"
        """
        if model:
            self.model = model
        elif model_type == "weak":
            self.model = os.getenv("LLM_WEAK_MODEL") or os.getenv("LLM_MODEL") or self._get_default()
        elif model_type == "strong":
            self.model = os.getenv("LLM_STRONG_MODEL") or os.getenv("LLM_MODEL") or self._get_default()
        else:
            self.model = os.getenv("LLM_MODEL") or self._get_default()
    
    def _get_default(self) -> str:
        """Get default model from llm CLI."""
        try:
            result = subprocess.run(
                ["llm", "models", "default"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        return "gpt-4o-mini"
    
    def ask(self, prompt: str) -> str:
        """Ask LLM a question, get response."""
        result = subprocess.run(
            ["llm", "-m", self.model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"LLM failed: {result.stderr}")
        
        return result.stdout.strip()
