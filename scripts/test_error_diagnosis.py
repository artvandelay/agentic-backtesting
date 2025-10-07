from nlbt.reflection import ReflectionEngine

engine = ReflectionEngine()
engine.requirements = {"ticker": "AAPL", "period": "2024", "capital": "$10000", "strategy": "buy and hold"}

# Test different types of errors
test_errors = [
    # Import error
    ("ModuleNotFoundError: No module named 'pandas_ta'", "import pandas_ta\nrsi = pandas_ta.rsi(data.Close)"),
    
    # Syntax error  
    ("SyntaxError: invalid syntax", "def next(self):\n    if self.rsi[-1] < 30\n        self.buy()"),
    
    # Data error
    ("KeyError: 'AAPL'", "data = yf.download('AAPL', start='2024-01-01')\nbt = Backtest(data, Strategy, cash='$10000')"),
    
    # Type error
    ("TypeError: unsupported operand type(s) for -: 'str' and 'int'", "cash = '$10000'\nbt = Backtest(data, Strategy, cash=cash - 1000)")
]

print("Testing error diagnosis:\n")
for i, (error, code) in enumerate(test_errors, 1):
    print(f"=== Test {i}: {error.split(':')[0]} ===")
    fix_prompt = engine._generate_error_fix_prompt(error, code)
    print(f"Generated fix prompt: {fix_prompt[:200]}...")
    print()
