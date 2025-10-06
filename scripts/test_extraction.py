from nlbt.reflection import ReflectionEngine

engine = ReflectionEngine()
test_cases = [
    "Buy AAPL in 2024 with $10,000",
    "NVDA RSI strategy: buy < 30, sell > 70, 2023, ₹50000, lang Spanish", 
    "Test RELIANCE moving average crossover, period 2023, capital INR 100000",
    "SPY buy and hold strategy for 2020-2024 with $25K",
    "I want to backtest TSLA momentum strategy in 2023 using $5000",
]

print("Testing LLM requirement extraction:\n")
for msg in test_cases:
    extracted = engine._extract_requirements_llm(msg)
    print(f"'{msg}'")
    print(f"  -> {extracted}\n")
