# User Workflow Issues - Test Results

## Date: 2025-10-02

## Test Results Summary

| Flow | Status | Issue |
|------|--------|-------|
| 1. Direct yes | ✅ PASS | Works perfectly |
| 2. No then yes | ✅ PASS | Works perfectly |
| 3. Change period | ✅ PASS | Works perfectly |
| 4. Actually/sorry | ✅ PASS | Works perfectly |
| 5. Progressive disclosure | ❌ FAIL | LLM recognizes inputs but doesn't extract to requirements |
| 6. Change after STATUS:READY | ❌ FAIL | Detects change intent but doesn't update requirements |

---

## Bug #1: Change after STATUS:READY doesn't update requirements

### Symptom
```
User: Backtest MSFT... Period 2024
Agent: STATUS: READY, PERIOD: 2024
User: change: do this for 2010 to 2020
Agent: I see you want to change the requirements... PERIOD: 2024  ← STILL 2024!
```

### Root Cause
In `_handle_implementation_confirmation()`:
```python
if any(word in user_lower for word in ["change", "modify", "update", "actually"]):
    self.phase = "understanding"
    return "I see you want to change..." + self._phase1_understanding(user_input)
```

**The problem:** 
- It calls `_phase1_understanding(user_input)` with the new input
- But `_phase1_understanding()` calls `_update_requirements_from_conversation()` FIRST
- Then asks the LLM to evaluate STATUS
- The LLM sees the OLD requirements (already set) and just returns STATUS: READY again
- The **extraction happens but requirements are already set**, so the check `if not self.requirements.get("period")` fails
- Result: Requirements never update

### Fix Required
When user requests a change at ready_to_implement phase:
1. **Clear the specific requirement** they're changing
2. **Then** call `_update_requirements_from_conversation()`
3. OR: Force the LLM to re-extract all requirements

---

## Bug #2: Progressive disclosure doesn't extract requirements

### Symptom
```
User: Buy AAPL
Agent: Great! What time period and capital?
User: 2024
Agent: I see 2024 again, but still need the capital...  ← Didn't extract it!
User: $10000
Agent: I have $10,000, but still need strategy...  ← Didn't extract it either!
```

### Root Cause
In `_phase1_understanding()`:
```python
# First, try to extract requirements from the conversation
self._update_requirements_from_conversation(user_input)

# Then ask LLM
prompt = f"""...
CURRENT USER MESSAGE: {user_input}
CURRENT REQUIREMENTS GATHERED:
{self.requirements}
..."""

response = self.llm.ask(prompt)
```

**The problem:**
- When user says just "2024", `_update_requirements_from_conversation()` extracts it
- But then the LLM prompt shows it already has `period: '2024'`
- The LLM says "I see you mentioned 2024 again" instead of acknowledging it's new
- The STATUS: READY check at the end works:
  ```python
  if has_ticker and has_period and has_capital and has_strategy:
      self.phase = "ready_to_implement"
  ```
- But the **conversation feels broken** because LLM acts like it didn't receive the info

### Fix Required
- Make the LLM response **acknowledge newly extracted requirements**
- Add logic to detect "this turn added new info" vs "this turn repeated info"
- Update prompt to say "Great! I now have [X]. Still need [Y, Z]."

---

## Bug #3: "no" response handling is unclear

### Current Behavior
```
User: Buy AAPL in 2024 with $10K
Agent: STATUS: READY... Ready to proceed?
User: no
Agent: 🤔 I need your confirmation... [shows same menu]
```

### Not technically broken, but could be better
- "no" should prompt: "What would you like to change?" instead of just repeating the menu
- Currently it works (user can then say "change X") but the UX is clunky

---

## Proposed Fixes

### Fix 1: Update `_handle_implementation_confirmation()` for changes

```python
def _handle_implementation_confirmation(self, user_input: str) -> str:
    user_lower = user_input.lower().strip()
    
    # Check for change requests
    if any(word in user_lower for word in ["change", "modify", "update", "actually"]):
        self.phase = "understanding"
        
        # CRITICAL FIX: Clear requirements that user wants to change
        # Look for what they're changing
        if "period" in user_lower or "date" in user_lower or any(year in user_input for year in ["2020", "2021", "2022", "2023", "2024"]):
            self.requirements.pop("period", None)
        if "ticker" in user_lower or "stock" in user_lower:
            self.requirements.pop("ticker", None)
        if "capital" in user_lower or "$" in user_input or "money" in user_lower:
            self.requirements.pop("capital", None)
        if "strategy" in user_lower:
            self.requirements.pop("strategy", None)
        
        # Now re-process with cleared requirements
        return "I see you want to change the requirements. Let me update that.\n\n" + self._phase1_understanding(user_input)
```

### Fix 2: Update `_phase1_understanding()` to acknowledge new info

```python
def _phase1_understanding(self, user_input: str) -> str:
    # Track what we had before
    before = set(self.requirements.keys())
    
    # Extract from this message
    self._update_requirements_from_conversation(user_input)
    
    # Track what's new
    after = set(self.requirements.keys())
    newly_added = after - before
    
    # Build context for LLM
    context = ""
    if newly_added:
        context = f"NEW INFO THIS TURN: {', '.join(newly_added)}\n"
    
    prompt = f"""...
{context}
CURRENT REQUIREMENTS:
{self._format_requirements()}

INSTRUCTIONS:
- If new info was extracted this turn, acknowledge it positively
- If all 4 requirements are now complete, output STATUS: READY
- Otherwise, ask for what's still missing
..."""
```

### Fix 3: Better "no" handling

```python
if user_lower == "no":
    return """I understand you're not ready to proceed yet. 
    
What would you like to do?
• Type "change [requirement]" to modify something
• Type "explain" for more details
• Or tell me what's wrong and I'll help!"""
```

---

## Implementation Priority

1. **HIGH**: Fix Bug #1 (change after STATUS:READY) - user explicitly reported this
2. **MEDIUM**: Fix Bug #2 (progressive disclosure) - makes conversation feel more natural
3. **LOW**: Fix Bug #3 (better "no" handling) - nice-to-have UX improvement

---

## Related Files
- `src/nlbt/reflection.py` - `_handle_implementation_confirmation()`, `_phase1_understanding()`
- Test script: `/tmp/test_workflows.py`

