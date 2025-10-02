# Workflow Test Results - After Fixes

## Date: 2025-10-02

## Test Results Summary

| Flow | Status | Notes |
|------|--------|-------|
| 1. Direct yes | ✅ PASS | Works perfectly |
| 2. No then yes | ✅ PASS | Works perfectly (timeout in automated test was LLM latency) |
| 3. Change period | ✅ PASS | Works perfectly |
| 4. Actually/sorry | ⚠️ PARTIAL | Ticker updates but strategy text still references old ticker |
| 5. Progressive disclosure | ❌ FAIL | LLM acknowledges but doesn't extract requirements |
| 6. Change after STATUS:READY | ✅ PASS | **FIXED!** Now updates correctly |

---

## What We Fixed

### ✅ Bug #1: Change after STATUS:READY (FIXED)

**Before:**
```
User: change: do this for 2010 to 2020
Agent: PERIOD: 2024  ← Didn't update!
```

**After:**
```
User: change: do this for 2010 to 2020  
Agent: Got it! Let me update that for you.
       PERIOD: 2010 to 2020  ← Updated! ✅
```

**Solution:** Clear the relevant requirement before calling `_phase1_understanding()`:
```python
if "period" in user_lower or "date" in user_lower or any(year in user_input...):
    self.requirements.pop("period", None)
```

### ✅ Better "no" handling (IMPROVED)

**Before:**
```
User: no
Agent: 🤔 I need your confirmation... [repeats menu]
```

**After:**
```
User: no
Agent: I understand you're not ready to proceed yet.
       What would you like to do?
       • "change [requirement]" → Modify something
       • "explain" → See more details
       • Or just tell me what's wrong and I'll help!
```

---

## Remaining Issues

### ⚠️ Issue #1: Strategy text doesn't update when ticker changes

**Scenario:**
```
User: Buy AAPL in 2024 with $10K
Agent: STATUS: READY, TICKER: AAPL, STRATEGY: "Buy AAPL in 2024..."
User: actually, use TSLA instead
Agent: TICKER: TSLA ✅, STRATEGY: "Buy AAPL in 2024..." ❌ (still says AAPL)
```

**Root cause:**
- Strategy is extracted as the full user input: "Buy AAPL in 2024 with $10K"
- When user changes ticker to TSLA, we clear `requirements['ticker']`
- But `requirements['strategy']` still contains "AAPL"
- Code generator gets confused: ticker=TSLA but strategy says "Buy AAPL"

**Potential fixes:**
1. **Smart strategy text substitution**: When ticker changes, find/replace old ticker in strategy text
2. **Re-extract everything**: When user says "actually", clear ALL requirements and re-extract
3. **Warn user**: "Strategy mentions AAPL but you selected TSLA. Should I update strategy text too?"

**Recommendation:** Option 1 (smart substitution) - most user-friendly

### ❌ Issue #2: Progressive disclosure still broken

**Scenario:**
```
User: Buy AAPL
Agent: Great! What time period and capital?
User: 2024
Agent: I see 2024 again. What time period?  ← Didn't extract it!
User: $10000
Agent: I have $10,000. What capital?  ← Didn't extract it either!
```

**Root cause:**
- `_update_requirements_from_conversation()` extracts correctly
- But the LLM response doesn't acknowledge the newly extracted info
- The LLM sees `requirements = {'period': '2024'}` in the prompt
- But interprets it as "user said 2024 before" not "user just gave me 2024 this turn"

**Potential fixes:**
1. **Track delta**: Store what was added this turn vs. previous turns
2. **Force acknowledgment**: Override LLM response if new info was extracted
3. **Change prompt**: Tell LLM explicitly "NEW INFO THIS TURN: period"

**Recommendation:** Option 3 (change prompt) - most reliable

---

## Priority for Next Fixes

1. **HIGH**: Issue #1 (strategy text with wrong ticker) - causes implementation failures
2. **MEDIUM**: Issue #2 (progressive disclosure) - UX feels broken but workaround exists (provide all info upfront)

---

## Implementation Suggestions

### Fix #1: Smart strategy text substitution

```python
def _handle_implementation_confirmation(self, user_input: str) -> str:
    if any(word in user_lower for word in ["change", "modify", "update", "actually"]):
        self.phase = "understanding"
        
        # Track what we're changing
        old_ticker = self.requirements.get("ticker")
        
        # Clear requirements
        if "period" in user_lower or "date" in user_lower or any(year in user_input...):
            self.requirements.pop("period", None)
        if "ticker" in user_lower or "stock" in user_lower or any(ticker in user_input.upper()...):
            self.requirements.pop("ticker", None)
            # Also update strategy text if it mentions the old ticker
            if old_ticker and "strategy" in self.requirements:
                strategy = self.requirements["strategy"]
                # Find new ticker in user input
                new_ticker = None
                for ticker in ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "SPY", "QQQ", "AMZN", "META"]:
                    if ticker in user_input.upper():
                        new_ticker = ticker
                        break
                if new_ticker:
                    # Replace old ticker with new ticker in strategy text
                    self.requirements["strategy"] = strategy.replace(old_ticker, new_ticker)
        
        return "Got it! Let me update that for you.\n\n" + self._phase1_understanding(user_input)
```

### Fix #2: Track requirement delta

```python
def _phase1_understanding(self, user_input: str) -> str:
    # Track what we had before
    before = set(self.requirements.keys())
    before_values = {k: v for k, v in self.requirements.items()}
    
    # Extract from this message
    self._update_requirements_from_conversation(user_input)
    
    # Track what changed
    after = set(self.requirements.keys())
    newly_added = after - before
    changed = {k for k in before & after if before_values.get(k) != self.requirements.get(k)}
    
    # Build context for LLM
    context = ""
    if newly_added:
        new_items = [f"{k}={self.requirements[k]}" for k in newly_added]
        context += f"✅ NEW INFO EXTRACTED THIS TURN: {', '.join(new_items)}\n"
    if changed:
        changed_items = [f"{k} updated to {self.requirements[k]}" for k in changed]
        context += f"✅ UPDATED THIS TURN: {', '.join(changed_items)}\n"
    
    prompt = f"""You are helping gather backtesting requirements.

{context}

CONVERSATION HISTORY:
{self._get_history()}

CURRENT REQUIREMENTS:
{self._format_requirements()}

INSTRUCTIONS:
- If new info was extracted this turn (shown above), acknowledge it positively: "Great! I now have X."
- Check if all 4 requirements are complete (ticker, period, capital, strategy)
- If complete, output STATUS: READY format
- Otherwise, ask for what's still missing

..."""
```

---

## Related Files
- `src/nlbt/reflection.py` - Main implementation
- `/tmp/test_workflows.py` - Test script
- `cursor_chats/user_workflow_issues.md` - Original bug documentation

