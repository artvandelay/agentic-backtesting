"""Minimal LLM client using llm CLI."""

import subprocess
import os
from typing import List, Dict


class LLM:
    """Simple LLM wrapper."""
    
    def __init__(self, model: str = None):
        self.model = model or os.getenv("LLM_MODEL") or self._get_default()
    
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

