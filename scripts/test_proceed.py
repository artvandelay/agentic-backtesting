from nlbt.reflection import ReflectionEngine

engine = ReflectionEngine()
test_cases = [
    ("yes", True),
    ("go", True),
    ("proceed", True),
    ("ok let's do it", True),
    ("sure", True),
    ("no", False),
    ("wait", False),
    ("change ticker to NVDA", False),
    ("explain first", False),
    ("can you explain the strategy?", False),
    ("yes but change the period", False),
]

print("Testing proceed detection:\n")
for user_input, expected in test_cases:
    result = engine._should_proceed(user_input)
    status = "✓" if result == expected else "✗"
    print(f"{status} '{user_input}' -> {result} (expected {expected})")

