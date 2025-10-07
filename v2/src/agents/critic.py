"""Critic agent - Phase 2 code evaluator."""

from ..llm import LLM


class Critic:
    """Evaluates generated code and results."""
    
    def __init__(self):
        self.llm = LLM(model_type="default")
    
    def evaluate(self, code: str, results: str, error: str = None) -> dict:
        """
        Evaluate code execution results.
        
        Returns:
            {
                "status": "pass" | "retry" | "fail",
                "feedback": str  # For retry
            }
        """
        # For now, simple logic
        if error:
            return {
                "status": "retry",
                "feedback": f"Fix this error: {error}"
            }
        
        return {
            "status": "pass",
            "feedback": None
        }
    
    def _build_prompt(self, code: str, results: str, error: str) -> str:
        """Build evaluation prompt."""
        return f"Evaluate this backtest: {results}"
