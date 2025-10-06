from nlbt.reflection import ReflectionEngine

engine = ReflectionEngine()
test_cases = [
    {"ticker": "AAPL", "period": "2024", "strategy": "buy and hold", "lang": "English"},
    {"ticker": "NVDA", "period": "2023", "strategy": "RSI < 30 buy, > 70 sell", "lang": "Spanish"},
    {"ticker": "RELIANCE.NS", "period": "2023", "strategy": "SMA crossover", "lang": "Hindi"},
]

for tc in test_cases:
    engine.requirements = tc
    print(f"{tc} -> {engine._generate_title()}")

