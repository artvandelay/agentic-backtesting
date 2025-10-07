"""Communicator agent - Phase 1 conversation handler."""

from ..llm import LLM


class Communicator:
    """Handles user conversation and requirement extraction."""
    
    def __init__(self):
        self.llm = LLM(model_type="default")
        self.conversation_history = []
    
    def process(self, user_input: str, context: dict = None) -> dict:
        """
        Process user input and extract requirements.
        
        Returns:
            {
                "requirements": {
                    "ticker": str,
                    "period": str,
                    "capital": str,
                    "strategy": str
                },
                "complete": bool,
                "response": str  # What to tell the user
            }
        """
        # For now, return hardcoded response
        return {
            "requirements": {
                "ticker": "AAPL",
                "period": "2024",
                "capital": "$10,000",
                "strategy": "Buy and hold"
            },
            "complete": True,
            "response": "I understand you want to test a buy-and-hold strategy. Let me validate this..."
        }
    
    def _build_prompt(self, user_input: str) -> str:
        """Build prompt for requirement extraction."""
        # TODO: Implement actual prompt
        return f"Extract requirements from: {user_input}"
