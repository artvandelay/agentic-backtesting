# NLBT v2 — Promptification (3-Phase System)

This branch sketches a redesigned, prompt-first agent. The engine is a thin interface; LLMs drive decisions. A **triplet loop** in Phase 1 handles strategy refinement until implementable.

![NLBT v2 Flow](diagram.svg)

*Flow: User → Communicator ↔ Jr Coding Agent (loop) → Strong Coder (3 tries) → Reporter → TL;DR*

## Key Ideas
- **Phase 1 Triplet**: User → Communicator → Jr Coding Agent → Loop back until "CAN CODE"
- **Separation of concerns**: Communicator handles conversation; Jr Agent validates feasibility
- **Weak validator principle**: Jr agent (weak model) gates what strong coder attempts
- **Pure prompt-driven**: No hardcoded business logic; all behavior in prompts
- **Broad acceptance**: Users can ask anything trading-related; Jr agent decides implementability

## Phase 1 Flow Detail
1. **User**: Describes trading strategy (any complexity)
2. **Communicator**: Extracts requirements, asks clarifying questions
3. **Jr Coding Agent**: Reviews complete spec → "CAN CODE" or "NEED CLARIFICATION: [bullets]"
4. **Loop**: If clarification needed, Communicator asks user, repeat until "CAN CODE"
5. **Proceed**: Once Jr says "CAN CODE", move to Phase 2

## Next Steps
- Define prompt templates for: Communicator, Jr Coding Agent, Strong Coder, Critic, Reporter
- Implement minimal driver that wires these prompts
- Test triplet loop with various strategy complexities
