from nlbt.reflection import ReflectionEngine

engine = ReflectionEngine()
test_cases = [
    ("trades", "English"),
    ("equity_curve", "English"),
    ("trades", "Spanish"),
    ("equity_curve", "Hindi"),
]

print("Testing section name generation:\n")
for section_type, lang in test_cases:
    heading = engine._generate_section_name(section_type, lang)
    print(f"{section_type} ({lang}): {heading}")

