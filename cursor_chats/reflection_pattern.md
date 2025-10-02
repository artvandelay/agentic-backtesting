# Reflection Pattern Implementation

## What It Is

A **3-phase autonomous workflow** where the LLM controls phase transitions through structured decision-making.

## The Three Phases

### Phase 1: Understanding
- LLM asks questions until it decides it has sufficient information
- LLM outputs: `STATUS: READY` or `STATUS: INCOMPLETE`
- Extracts: ticker, period, capital, strategy

### Phase 2: Implementation
- **Producer:** Generates Python backtest code
- **Executor:** Runs code in sandbox
- **Critic:** Evaluates if results match requirements
- LLM outputs: `DECISION: PROCEED` or `DECISION: RETRY`
- Max 3 attempts with refinement

### Phase 3: Reporting
- **Plan:** LLM creates report structure
- **Write:** LLM writes draft report
- **Refine:** Critic reviews and improves
- Saves professional markdown report

## Key Pattern: Producer-Critic

From Agentic Design Patterns textbook (Chapter 4):

> "The separation of Producer and Critic prevents cognitive bias of an agent reviewing its own work."

We use **separate prompts** for generation vs. evaluation:
- Producer: "You are a Python expert. Generate code."
- Critic: "You are a senior engineer. Find flaws."

## How LLM Controls Flow

Instead of hardcoded logic:
```python
if ticker and period and capital:
    proceed()
```

We let the LLM decide:
```python
analysis = llm.analyze("Do I have sufficient info?")
if "STATUS: READY" in analysis:
    proceed()
```

## Files

- `src/nlbt/reflection_engine.py` - Core 3-phase engine (460 lines)
- `src/nlbt/core_reflection.py` - Simple wrapper (60 lines)
- `src/nlbt/cli/main.py` - Clean CLI interface

## Usage

```bash
nlbt chat
```

The agent autonomously goes through all 3 phases based on its own decisions.

---

**Archived docs:** See `.archive_*` files in `cursor_chats/` for detailed analysis.

