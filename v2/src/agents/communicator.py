"""Communicator agent - Phase 1 conversation handler."""

from ..llm import LLM
import re


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
        context = context or {}
        current_reqs = context.get("requirements", {})
        history = context.get("history", [])
        
        # Build and ask the LLM
        prompt = self._build_prompt(user_input, current_reqs, history)
        response = self.llm.ask(prompt)
        
        # Parse response
        return self._parse_response(response, current_reqs)
    
    def _build_prompt(self, user_input: str, current_reqs: dict, history: list) -> str:
        """Build prompt for requirement extraction."""
        history_text = "\n".join(history[-6:]) if history else "No prior conversation"
        
        return f"""You are a friendly trading strategy assistant helping users define their backtesting requirements.

CURRENT CONVERSATION:
{history_text}

USER MESSAGE: {user_input}

CURRENT REQUIREMENTS GATHERED:
- Ticker: {current_reqs.get('ticker', 'Not specified')}
- Period: {current_reqs.get('period', 'Not specified')}
- Capital: {current_reqs.get('capital', 'Not specified')}
- Strategy: {current_reqs.get('strategy', 'Not specified')}

YOUR TASK:
1. Extract any requirements from the user message
2. Determine if all 4 requirements are complete and clear
3. If missing info, ask ONE friendly question to gather it

RESPONSE FORMAT (strict):
TICKER: [extracted ticker or CURRENT]
PERIOD: [extracted period or CURRENT]
CAPITAL: [extracted capital or CURRENT]
STRATEGY: [extracted strategy or CURRENT]
COMPLETE: [YES or NO]
RESPONSE: [Your friendly response to the user]

EXAMPLES:
- If user says "test AAPL", extract TICKER: AAPL
- If user says "in 2024", extract PERIOD: 2024
- If user says "with $10k", extract CAPITAL: $10,000
- Keep CURRENT for unchanged fields

Be conversational and helpful!"""
    
    def _parse_response(self, response: str, current_reqs: dict) -> dict:
        """Parse LLM response into structured format."""
        # Extract fields
        ticker = self._extract_field(response, "TICKER", current_reqs.get("ticker"))
        period = self._extract_field(response, "PERIOD", current_reqs.get("period"))
        capital = self._extract_field(response, "CAPITAL", current_reqs.get("capital"))
        strategy = self._extract_field(response, "STRATEGY", current_reqs.get("strategy"))
        complete = "COMPLETE: YES" in response
        
        # Extract response text
        response_match = re.search(r"RESPONSE:\s*(.+)", response, re.DOTALL)
        response_text = response_match.group(1).strip() if response_match else "Let me help you define your strategy."
        
        # Build requirements dict
        requirements = {}
        if ticker and ticker != "CURRENT":
            requirements["ticker"] = ticker
        if period and period != "CURRENT":
            requirements["period"] = period
        if capital and capital != "CURRENT":
            requirements["capital"] = capital
        if strategy and strategy != "CURRENT":
            requirements["strategy"] = strategy
        
        return {
            "requirements": requirements,
            "complete": complete,
            "response": response_text
        }
    
    def _extract_field(self, response: str, field: str, current_value: str = None) -> str:
        """Extract a field value from response."""
        pattern = rf"{field}:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, response)
        if match:
            value = match.group(1).strip()
            if value == "CURRENT":
                return current_value
            return value
        return current_value
