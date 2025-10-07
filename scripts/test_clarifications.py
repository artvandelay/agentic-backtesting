from nlbt.reflection import ReflectionEngine

engine = ReflectionEngine()

test_cases = [
    # Should continue - only 2 basic questions
    ["What ticker?", "What period?"],
    
    # Should stop - comprehensive coverage
    ["What ticker symbol?", "What time period?", "What initial capital?", "What trading strategy?", "What risk tolerance?"],
    
    # Should continue - missing key info
    ["What color is your favorite?", "How old are you?", "What's the weather?"],
    
    # Should stop - good coverage but getting repetitive  
    ["What stock ticker?", "What time period (year)?", "What initial capital amount?", "What trading strategy rules?", "What stop loss percentage?", "What take profit target?", "What position sizing method?"]
]

print("Testing clarification stopping logic:\n")
for i, clarifications in enumerate(test_cases, 1):
    should_stop = engine._should_stop_clarifications(clarifications)
    print(f"Test {i} ({len(clarifications)} clarifications): {'STOP' if should_stop else 'CONTINUE'}")
    print(f"  Questions: {clarifications[:3]}{'...' if len(clarifications) > 3 else ''}")
    print()
