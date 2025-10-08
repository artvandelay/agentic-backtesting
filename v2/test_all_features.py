#!/usr/bin/env python3
"""Test script to demonstrate all v2 features."""

import subprocess
import time
import os

def run_test(name: str, input_text: str):
    """Run a test case and report results."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Input: {input_text}")
    print(f"{'='*60}")
    
    # Run the CLI with input
    process = subprocess.Popen(
        ['python', 'cli.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send input and get output
    stdout, stderr = process.communicate(input=input_text + "\nexit\n")
    
    # Print results
    print("Output:")
    print(stdout)
    
    if stderr:
        print("Errors:")
        print(stderr)
    
    # Check for generated reports
    print("\nGenerated files:")
    if "Full report:" in stdout:
        # Extract report path
        for line in stdout.split('\n'):
            if "Full report:" in line:
                report_path = line.split("Full report:")[-1].strip()
                if os.path.exists(report_path):
                    report_dir = os.path.dirname(report_path)
                    for file in os.listdir(report_dir):
                        file_path = os.path.join(report_dir, file)
                        size = os.path.getsize(file_path)
                        print(f"  - {file} ({size:,} bytes)")
    
    time.sleep(2)  # Pause between tests

def main():
    """Run all test cases."""
    print("🚀 v2 Feature Test Suite")
    print("=" * 60)
    
    # Test 1: Simple buy and hold
    run_test(
        "Simple Buy & Hold",
        "Buy and hold AAPL in 2024 with $10,000"
    )
    
    # Test 2: Complex RSI strategy
    run_test(
        "RSI Technical Strategy", 
        "Test RSI strategy on SPY: buy when RSI < 30, sell when RSI > 70, use 2023 data with $20K"
    )
    
    # Test 3: Vague strategy (triggers clarification)
    run_test(
        "Vague Strategy (Clarification)",
        "Buy SPY on dips in 2024 with $50k"
    )
    
    # Test 4: Multi-asset attempt (rejected)
    run_test(
        "Multi-Asset (Validation)",
        "Rotate between GLD and SPY based on momentum, 2023-2024, $100k"
    )
    
    # Test 5: Indian ticker
    run_test(
        "International Ticker",
        "Buy and hold RELIANCE.NS in 2023 with ₹10,00,000"
    )
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
