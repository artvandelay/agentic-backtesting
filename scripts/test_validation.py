from nlbt.reflection import ReflectionEngine

engine = ReflectionEngine()
engine.requirements = {"ticker": "AAPL", "period": "2024", "capital": "$10000", "strategy": "buy and hold"}
engine.code = """
# Mock backtest code
bt = Backtest(data, Strategy, cash=10000, commission=.002)
stats = bt.run()
print(stats)
"""

# Test successful result
good_result = {
    "output": """
Start                     2024-01-01 00:00:00
End                       2024-12-31 00:00:00
Duration                    365 days 00:00:00
Exposure Time [%]                     100.0
Equity Final [$]                   12500.50
Equity Peak [$]                    13000.00
Return [%]                            25.01
Buy & Hold Return [%]                 25.01
Return (Ann.) [%]                     25.01
Volatility (Ann.) [%]                 18.50
Sharpe Ratio                          1.35
Sortino Ratio                         2.10
Calmar Ratio                          0.95
Max. Drawdown [%]                     -8.20
Avg. Drawdown [%]                     -2.10
Max. Drawdown Duration      45 days 00:00:00
Avg. Drawdown Duration      12 days 00:00:00
# Trades                                 5
Win Rate [%]                         80.00
Best Trade [%]                        8.50
Worst Trade [%]                      -3.20
Avg. Trade [%]                        4.20
Max. Trade Duration         89 days 00:00:00
Avg. Trade Duration         45 days 00:00:00
Profit Factor                         3.25
Expectancy [%]                        4.50
SQN                                   1.85
"""
}

# Test problematic result  
bad_result = {
    "output": "Error: ticker not found\nTraceback: KeyError: 'AAPL'"
}

print("Testing result validation:\n")
print("Original method - Good result:")
validation = engine._critique_results(good_result)
print(f"  Proceed: {validation['proceed']}")
print(f"  Reason: {validation['critique'][:100]}...")

print("\nLLM method - Good result:")
validation = engine._critique_results_llm(good_result)
print(f"  Proceed: {validation['proceed']}")
print(f"  Reason: {validation['critique']}")

print("\nLLM method - Bad result:")
validation = engine._critique_results_llm(bad_result)
print(f"  Proceed: {validation['proceed']}")
print(f"  Reason: {validation['critique']}")
