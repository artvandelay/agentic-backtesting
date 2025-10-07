"""Minimal orchestration engine for v2 triplet architecture."""

from .agents.communicator import Communicator
from .agents.jr_coder import JrCoder
from .agents.strong_coder import StrongCoder
from .agents.critic import Critic
from .agents.reporter import Reporter


class Engine:
    """Orchestrates the 3-phase workflow with triplet loop."""
    
    def __init__(self):
        # Initialize all agents
        self.communicator = Communicator()
        self.jr_coder = JrCoder()
        self.strong_coder = StrongCoder()
        self.critic = Critic()
        self.reporter = Reporter()
        
        # State
        self.phase = "phase1"  # phase1, phase2, phase3
        self.requirements = {}
        self.code = ""
        self.results = ""
        self.conversation_history = []
    
    def process(self, user_input: str) -> str:
        """Process user input and return response."""
        self.conversation_history.append(f"User: {user_input}")
        
        if self.phase == "phase1":
            return self._phase1_triplet(user_input)
        elif self.phase == "phase2":
            return self._phase2_implementation()
        elif self.phase == "phase3":
            return self._phase3_reporting()
        else:
            # Reset for new conversation
            self.phase = "phase1"
            self.requirements = {}
            return self._phase1_triplet(user_input)
    
    def _phase1_triplet(self, user_input: str) -> str:
        """Phase 1: User → Communicator → Jr Coder loop."""
        
        # Step 1: Communicator processes user input
        comm_result = self.communicator.process(user_input, {
            "history": self.conversation_history,
            "requirements": self.requirements
        })
        
        # Update requirements
        self.requirements.update(comm_result["requirements"])
        
        # If communicator doesn't have complete info, ask user
        if not comm_result["complete"]:
            response = comm_result["response"]
            self.conversation_history.append(f"Agent: {response}")
            return response
        
        # Step 2: Jr Coder validates feasibility
        validation = self.jr_coder.validate(self.requirements)
        
        if validation["implementable"]:
            # Move to Phase 2
            self.phase = "phase2"
            response = "✅ Strategy validated! Generating code..."
            self.conversation_history.append(f"Agent: {response}")
            # Auto-proceed to implementation
            return self._phase2_implementation()
        else:
            # Need clarifications - loop back
            clarifications = "\n".join([f"- {c}" for c in validation["clarifications"]])
            response = f"I need some clarifications:\n{clarifications}"
            self.conversation_history.append(f"Agent: {response}")
            return response
    
    def _phase2_implementation(self) -> str:
        """Phase 2: Strong Coder → Critic loop."""
        
        # Try up to 3 times
        for attempt in range(1, 4):
            # Generate code
            coder_result = self.strong_coder.generate_and_test(
                self.requirements, 
                attempt=attempt
            )
            
            if not coder_result["success"]:
                # Evaluate error
                critic_eval = self.critic.evaluate(
                    coder_result["code"],
                    coder_result["results"],
                    coder_result["error"]
                )
                
                if critic_eval["status"] == "retry" and attempt < 3:
                    continue  # Try again
                elif critic_eval["status"] == "fail":
                    return f"❌ Failed to implement strategy: {coder_result['error']}"
            else:
                # Success! Save results
                self.code = coder_result["code"]
                self.results = coder_result["results"]
                self.phase = "phase3"
                # Auto-proceed to reporting
                return self._phase3_reporting()
        
        return "❌ Failed to implement strategy after 3 attempts."
    
    def _phase3_reporting(self) -> str:
        """Phase 3: Reporter generates final output."""
        
        # Generate report
        report_result = self.reporter.generate_report(
            self.requirements,
            self.code,
            self.results
        )
        
        # Check if reporter needs more data
        if report_result["needs_retry"]:
            # One retry allowed - go back to coder
            self.phase = "phase2"
            return self._phase2_implementation()
        
        # Complete!
        self.phase = "complete"
        response = f"""
✅ Report generated!

{report_result['tldr']}

📄 Full report: {report_result['report_path']}
"""
        return response
