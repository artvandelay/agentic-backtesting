from nlbt.reflection import ReflectionEngine

engine = ReflectionEngine()
test_cases = [
    (["Date", "Equity", "Portfolio", "Cash"], "equity"),
    (["timestamp", "account_value", "balance"], "equity"),
    (["time", "portfolio_value", "holdings"], "equity"), 
    (["index", "value", "total"], "equity"),
]

print("Testing column detection:\n")
for columns, target in test_cases:
    best_col = engine._find_best_column(columns, target)
    print(f"Columns: {columns}")
    print(f"Best {target} column: {best_col}\n")
