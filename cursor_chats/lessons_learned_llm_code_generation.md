# Lessons Learned: LLM Code Generation

## Date: 2025-10-02

## Problem: Indicator-based backtesting strategies failing inconsistently

### Initial Symptoms
- SMA crossover: ❌ Failed
- RSI strategies: ❌ Failed  
- MACD strategies: ❌ Failed
- Bollinger Bands: ❌ Failed
- Simple buy-and-hold: ✅ Worked

### Root Cause Chain

#### 1. PRIMARY: Abstract prompts instead of concrete templates

**What we did wrong:**
```
❌ "Use ta library (ta.momentum, ta.trend) for indicators"
❌ "Calculate RSI with RSIIndicator from ta.momentum"
❌ "Integrate indicators via self.I with backtesting.py"
```

**Why it failed:**
- LLM had to **guess** the exact API: `RSIIndicator(close=...).rsi()` vs `RSI(...)` vs `ta.rsi(...)`
- Different attempts = different interpretations = inconsistent code
- Sometimes tried `from backtesting.test import RSI` (doesn't exist)
- Sometimes tried `pandas_ta` (not installed)
- Sometimes tried to use `.rolling()` directly on `backtesting._Array` (causes AttributeError)

**The fix:**
```python
✅ Provide EXACT working code to copy:

def rsi(values, n=14):
    import pandas as pd
    import numpy as np
    delta = pd.Series(values).diff()
    gain = (delta.where(delta > 0, 0)).rolling(n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(n).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).to_numpy()

self.rsi = self.I(rsi, self.data.Close, 14)
```

#### 2. SECONDARY: The `backtesting.py` + `ta` integration gotcha

**Non-obvious API constraint:**
- `self.data.Close` in `backtesting.Strategy` is a special `_Array` type
- It's **not** a pandas Series, so `.rolling()`, `.ewm()`, etc. don't work directly
- Must wrap in `self.I(helper_function, data)` where helper converts to Series first
- This is **library-specific knowledge** the LLM doesn't inherently have

**The pattern that works:**
```python
def indicator(values, n):
    import pandas as pd
    # Convert backtesting._Array → pd.Series → compute → numpy
    return pd.Series(values).rolling(n).mean().to_numpy()

self.my_indicator = self.I(indicator, self.data.Close, 20)
```

#### 3. TERTIARY: Ticker extraction regex bug

**What broke:**
```python
re.search(r'\b([A-Z]{2,5})\b', "Test NVDA with RSI", re.IGNORECASE)
# Matched "Test" first (uppercased to "TEST")
# "TEST" not in whitelist → ticker never extracted
```

**The fix:**
```python
matches = re.findall(r'\b([A-Z]{2,5})\b', user_input)  # No IGNORECASE
for ticker in matches:
    if ticker in VALID_TICKERS:
        use_this_ticker()
```

### Key Insight: LLMs as Code Copiers vs. API Explorers

**LLMs are EXCELLENT at:**
- ✅ Pattern matching and copying working code
- ✅ Making small modifications to templates
- ✅ Following explicit structural rules

**LLMs are INCONSISTENT at:**
- ❌ Figuring out non-obvious library APIs from documentation
- ❌ Understanding library-specific type constraints (like `backtesting._Array`)
- ❌ Remembering exact method names across retries
- ❌ Inferring the "right way" when multiple approaches exist

### The Solution Pattern

**WRONG approach:**
```
Prompt: "Use ta library for SMA. Calculate 50-day and 200-day moving averages.
         Integrate them with backtesting.py Strategy class."
```

**RIGHT approach:**
```
Prompt: "Copy this EXACT pattern:

def sma(values, n):
    import pandas as pd
    return pd.Series(values).rolling(n).mean().to_numpy()

self.sma50 = self.I(sma, self.data.Close, 50)
self.sma200 = self.I(sma, self.data.Close, 200)

YOUR TASK: Use this pattern and modify n=50/200 for your needs."
```

### Implementation Changes Made

1. **Replaced abstract instructions with bulletproof templates** in `src/nlbt/reflection.py`:
   - SMA template
   - RSI template  
   - MACD template
   - EMA template
   - Bollinger Bands template
   - Crossover detection (without imports)

2. **Fixed ticker extraction** to only match all-caps words

3. **Relaxed Critic** to accept 0-trade results (valid when strategy doesn't trigger)

4. **Added date warmup guidance** for long-window indicators (200-day SMA needs historical data)

### Results

**Before fix:** 0/4 indicator strategies passed
**After fix:** 5/5 strategies passed (100%)

### Takeaway for Future

**When asking LLM to generate code with external libraries:**

1. ✅ **Provide working templates**, not abstract requirements
2. ✅ **Show the exact pattern** for library-specific gotchas
3. ✅ **Include imports and data conversions** in the template
4. ✅ **Test with edge cases** (0 trades, long warmup periods, etc.)
5. ❌ **Don't assume the LLM "knows" the API** from package names alone
6. ❌ **Don't rely on retry loops** to discover the right pattern

**Remember:** LLMs are **pattern matchers**, not API explorers. Give them the pattern to match.

---

## Related Files
- `src/nlbt/reflection.py` - Phase 2 implementation with templates
- `EXAMPLES.md` - Test cases that now pass
- `reports/backtest_*.md` - Generated reports showing success


