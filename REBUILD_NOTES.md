# Minimal Reflection Pattern - Rebuild

## What Was Built

A **minimal** 3-phase reflection engine in ~200 lines of code total.

## Files Created

```
src/nlbt/
├── __init__.py          # Package init
├── llm.py              # LLM client (40 lines)
├── sandbox.py          # Code executor (65 lines)
├── reflection.py       # 3-phase engine (220 lines)
└── cli.py              # CLI interface (65 lines)
```

**Total: ~390 lines** (vs 1000+ before)

## How It Works

### Phase 1: Understanding
- LLM asks questions
- Outputs: `STATUS: READY` or `INCOMPLETE`
- Extracts ticker, period, capital, strategy

### Phase 2: Implementation
- Producer generates code
- Sandbox executes code
- Critic evaluates results
- Outputs: `DECISION: PROCEED` or `RETRY`
- Max 3 attempts

### Phase 3: Reporting
- Plans report structure
- Writes draft
- Saves to `reports/`

## Usage

```bash
# Install
pip install -e .

# Run
python -m nlbt.cli

# Or after install:
nlbt
```

## Testing

```bash
# Structure test (no LLM)
python test_minimal.py

# Live test (uses LLM)
python -m nlbt.cli
```

## Example Session

```
💭 You: Test Apple stock

🔍 Agent: [asks for period, capital, strategy]

💭 You: 2024, $10K, buy and hold

⚙️ Agent: [generates code → executes → critiques]

📊 Agent: [plans → writes → saves report]

✅ Done!
```

## Key Simplifications

1. **Single file per concern** - No deep nesting
2. **No complex state management** - Just simple attributes
3. **Direct LLM CLI calls** - No abstraction layers
4. **Minimal error handling** - Let things fail naturally
5. **No config files** - Uses environment or defaults

## What's Missing (Intentionally)

- Complex validation
- Multi-turn conversation management
- Session persistence
- Advanced error recovery
- Logging/debugging tools
- Type hints everywhere

**Philosophy:** Keep it minimal. Add only when needed.

## Next Steps

1. Test with real LLM
2. Iterate on prompts based on behavior
3. Add features only if they solve real problems

---

**Total rebuild time:** ~30 minutes  
**Complexity:** Minimal ✓  
**Represents idea:** Yes ✓

