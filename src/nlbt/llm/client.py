"""LLM CLI wrapper for PocketFlow integration."""

import json
import subprocess
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Wrapper around `llm` CLI for model access."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize LLM client.
        
        Args:
            model: Model to use. If None, uses LLM_MODEL from .env
        """
        self.model = model or self._get_default_model()
    
    def _get_default_model(self) -> str:
        """Get default model from environment or llm CLI default."""
        import os
        import subprocess
        
        # First check env var
        env_model = os.getenv("LLM_MODEL")
        if env_model:
            return env_model
        
        # Fall back to llm CLI default
        try:
            result = subprocess.run(
                ["llm", "models", "default"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        
        # Last resort: use a common model
        return "gpt-4o-mini"
    
    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send messages to LLM and get response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            
        Returns:
            Dict with 'type' ('text' or 'tool_call') and response content
        """
        # Build complete prompt from messages
        prompt_parts = []
        for msg in messages:
            if msg['role'] == 'system':
                prompt_parts.append(f"System: {msg['content']}")
            elif msg['role'] == 'user':
                prompt_parts.append(f"User: {msg['content']}")
            elif msg['role'] == 'assistant':
                prompt_parts.append(f"Assistant: {msg['content']}")
        
        full_prompt = "\n\n".join(prompt_parts)
        
        # Build llm CLI command
        cmd = [
            "llm",
            "-m", self.model
        ]
        
        try:
            # Run llm CLI
            process = subprocess.run(
                cmd,
                input=full_prompt,
                text=True,
                capture_output=True,
                timeout=120  # 2 minute timeout for LLM calls
            )
            
            if process.returncode != 0:
                raise RuntimeError(f"llm CLI failed: {process.stderr}")
            
            # Parse response
            response_text = process.stdout.strip()
            if not response_text:
                raise RuntimeError("Empty response from llm CLI")
            
            return {"type": "text", "content": response_text}
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("LLM call timed out")
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {e}")
    
    def _build_system_prompt(self, tools: Optional[List[Dict]] = None) -> str:
        """Build system prompt with tool definitions."""
        base_prompt = """You are a financial backtesting assistant. You help users backtest trading strategies by asking clarifying questions, writing Python code, and executing backtests."""
        
        if tools:
            tools_desc = "\n".join([
                f"- {tool['name']}: {tool.get('description', 'No description')}"
                for tool in tools
            ])
            base_prompt += f"\n\nYou have access to these tools:\n{tools_desc}"
        
        return base_prompt
