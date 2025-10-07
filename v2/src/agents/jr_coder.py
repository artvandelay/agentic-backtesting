"""Junior Coding Agent - Phase 1 feasibility validator."""

from ..llm import LLM


class JrCoder:
    """Validates if strategy is implementable with current scaffold."""
    
    def __init__(self):
        self.llm = LLM(model_type="weak")  # Use weak model for cost efficiency
    
    def validate(self, requirements: dict) -> dict:
        """
        Validate if requirements are implementable.
        
        Returns:
            {
                "implementable": bool,
                "clarifications": list[str]  # If not implementable
            }
        """
        # For now, return hardcoded response
        return {
            "implementable": True,
            "clarifications": []
        }
    
    def _build_prompt(self, requirements: dict) -> str:
        """Build validation prompt with scaffold context."""
        # TODO: Inject scaffold code context
        return f"Validate if implementable: {requirements}"
